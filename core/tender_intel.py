"""Tender & grant intelligence for the staff portal.

Three jobs, all deterministic and explainable (every score comes with reasons):

1. find      - pull open tenders from National Treasury's eTenders open-data API (OCDS)
               and scan watched web pages (SETA / NYDA / NSF funding windows) for grants.
2. score     - rate each opportunity 0-100 against Malitinne's BidProfile
               (services, provinces, exclusions) -> verdict strong / possible / low.
3. qualify   - read the requirements out of the tender text (CSD, tax, B-BBEE, CIDB,
               accreditation, briefing session ...) and check them against the documents
               in the Shared Drive vault, including expiry dates -> eligibility checklist.

Run daily by `python manage.py staff_daily` (cron) or from the "Scan now" button.
"""
from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

USER_AGENT = 'MalitinneTenderBot/1.0 (+https://malitinne.co.za; hello@malitinne.co.za)'
OCDS_URL = 'https://ocds-api.etenders.gov.za/api/OCDSReleases'
PROVINCES = ['Eastern Cape', 'Free State', 'Gauteng', 'KwaZulu-Natal', 'Limpopo', 'Mpumalanga',
             'North West', 'Northern Cape', 'Western Cape']
_PROVINCE_ALIASES = {'kzn': 'KwaZulu-Natal', 'kwazulu natal': 'KwaZulu-Natal', 'kwa-zulu natal': 'KwaZulu-Natal',
                     'gp': 'Gauteng', 'wc': 'Western Cape', 'ec': 'Eastern Cape', 'nw': 'North West',
                     'durban': 'KwaZulu-Natal', 'ethekwini': 'KwaZulu-Natal', 'pietermaritzburg': 'KwaZulu-Natal',
                     'msunduzi': 'KwaZulu-Natal', 'richards bay': 'KwaZulu-Natal', 'umhlathuze': 'KwaZulu-Natal',
                     'johannesburg': 'Gauteng', 'pretoria': 'Gauteng', 'tshwane': 'Gauteng', 'ekurhuleni': 'Gauteng',
                     'cape town': 'Western Cape', 'polokwane': 'Limpopo', 'mbombela': 'Mpumalanga',
                     'bloemfontein': 'Free State', 'mangaung': 'Free State', 'kimberley': 'Northern Cape',
                     'gqeberha': 'Eastern Cape', 'east london': 'Eastern Cape', 'buffalo city': 'Eastern Cape',
                     'mahikeng': 'North West', 'rustenburg': 'North West'}


# --------------------------------------------------------------------------- requirements
@dataclass(frozen=True)
class Requirement:
    key: str
    label: str
    pattern: str
    doc_type: str | None          # Shared Drive document that proves it (None = profile check)
    baseline: bool = False        # required by every SA government bid even if not mentioned


REQUIREMENTS = [
    Requirement('csd', 'Registered on the Central Supplier Database (CSD)', r'\bcsd\b|central supplier database', 'csd_report', True),
    Requirement('tax', 'SARS tax compliance status (TCS PIN)', r'tax (clearance|compliance)|\btcs\b|sars pin|tax status', 'tax_compliance', True),
    Requirement('cipc', 'Company registration (CIPC)', r'\bcipc\b|company registration|cor ?14|registration certificate', 'cipc_registration'),
    Requirement('bbbee', 'B-BBEE certificate or sworn affidavit', r'b-?bbee|\bbee\b (certificate|status|level)|sworn affidavit|preference points', 'bbbee'),
    Requirement('coida', 'COIDA letter of good standing', r'coida|letter of good standing|compensation fund|workmen', 'coida'),
    Requirement('bank', 'Bank confirmation letter', r'bank (confirmation|letter|rating)|stamped bank', 'bank_letter'),
    Requirement('accreditation', 'Accreditation (QCTO / SETA)', r'accredit|\bseta\b|\bqcto\b|training provider', 'accreditation_letter'),
    Requirement('cidb', 'CIDB grading', r'\bcidb\b|\b\d\s?(ce|gb|ge|ee|me|sq)\b', None),
]
META_PREFIXES = ('Bid number:', 'Method:', 'Category:', 'Contact:')
_BRIEFING = re.compile(r'(compulsory|mandatory)\s+(site\s+)?(briefing|meeting|clarification)', re.I)
_CIDB_GRADE = re.compile(r'\b(\d)\s?(ce|gb|ge|ee|me|sq)\b', re.I)


def _norm(text):
    return re.sub(r'\s+', ' ', (text or '')).strip()


def _keyword_hit(keyword, text_lower):
    keyword = keyword.lower().strip()
    if not keyword:
        return False
    if len(keyword) <= 4:  # short words (EPWP, SMME, NQF) must be whole words
        return re.search(r'\b' + re.escape(keyword) + r'\b', text_lower) is not None
    return keyword in text_lower


def detect_province(*texts):
    blob = ' '.join(t for t in texts if t).lower()
    for prov in PROVINCES:
        if prov.lower() in blob or prov.lower().replace('-', ' ') in blob:
            return prov
    for alias, prov in _PROVINCE_ALIASES.items():
        if re.search(r'\b' + re.escape(alias) + r'\b', blob):
            return prov
    return ''


# --------------------------------------------------------------------------- vault
def document_vault():
    """{doc_type: newest current SharedDocument} for every vault type we hold."""
    from .models import SharedDocument
    vault = {}
    for doc in SharedDocument.objects.filter(is_current=True).exclude(doc_type='other').order_by('doc_type', '-uploaded_at'):
        vault.setdefault(doc.doc_type, doc)
    return vault


# --------------------------------------------------------------------------- scoring
@dataclass
class Assessment:
    score: int
    verdict: str
    reasons: list = field(default_factory=list)
    checklist: list = field(default_factory=list)
    eligibility: str = 'unknown'
    relevant: bool = False      # any core/related keyword matched


def assess(opp, profile, vault=None, today=None):
    """Score one TenderOpportunity (not saved). Pure function of opp + profile + vault."""
    today = today or timezone.localdate()
    vault = document_vault() if vault is None else vault
    # Metadata lines we add while importing (eTenders categories are unreliable) do not count as scope
    scope = '\n'.join(line for line in (opp.description or '').splitlines() if not line.startswith(META_PREFIXES))
    text = _norm(' '.join([opp.title or '', scope, opp.department or '', opp.location or '']))
    low = text.lower()
    reasons, score = [], 0

    core = [k for k in profile._lines(profile.core_keywords) if _keyword_hit(k, low)]
    related = [k for k in profile._lines(profile.related_keywords) if _keyword_hit(k, low) and k not in core]
    excluded = [k for k in profile._lines(profile.exclude_keywords) if _keyword_hit(k, low)]

    relevance = min(65, 20 * len(core) + 8 * len(related))
    if opp.kind == 'grant' and relevance:
        relevance = min(65, relevance + 10)        # funding windows aimed at providers are rarely noise
    score += relevance
    if core:
        reasons.append('Core service match: ' + ', '.join(core[:6]))
    if related:
        reasons.append('Related work: ' + ', '.join(related[:6]))
    if not core and not related:
        reasons.append('No match with our services')

    province = opp.province or detect_province(text)
    targets = [p.lower() for p in profile._lines(profile.target_provinces)]
    if province and province == profile.home_province:
        score += 20
        reasons.append(f'{province} is our home province')
    elif province and province.lower() in targets:
        score += 12
        reasons.append(f'{province} is a province we deliver in')
    elif province:
        score += 4
        reasons.append(f'{province} is outside our usual area')
    else:
        score += 8
        reasons.append('Province not stated')

    if excluded:
        penalty = min(45, 20 * len(excluded)) if not core else min(25, 10 * len(excluded))
        score -= penalty
        reasons.append('Outside our scope: ' + ', '.join(excluded[:5]))

    # ---- eligibility checklist
    checklist = []
    blocking, missing = False, False
    for req in REQUIREMENTS:
        mentioned = re.search(req.pattern, low, re.I) is not None
        if not (mentioned or req.baseline):
            continue
        if req.key == 'cidb':
            grade = _CIDB_GRADE.search(low)
            if profile.cidb_grade:
                checklist.append(_item(req.label, 'ok', f'We hold CIDB {profile.cidb_grade}'))
            else:
                blocking = True
                checklist.append(_item(req.label, 'fail', f'Requires CIDB {grade.group(0).upper() if grade else "grading"}; we are not CIDB registered'))
            continue
        if req.key == 'accreditation' and not mentioned:
            continue
        doc = vault.get(req.doc_type)
        source = 'Mentioned in the tender' if mentioned else 'Standard for government bids'
        if not doc:
            missing = True
            checklist.append(_item(req.label, 'missing', f'{source}. Upload it to the Shared Drive vault.', req.doc_type))
        elif doc.expiry_date and doc.expiry_date < today:
            missing = True
            checklist.append(_item(req.label, 'missing', f'Our copy expired on {doc.expiry_date:%d %b %Y}. Renew it.', req.doc_type, doc.pk))
        elif doc.expiry_date and opp.closing_date and doc.expiry_date < opp.closing_date:
            checklist.append(_item(req.label, 'warn', f'Valid now, but expires {doc.expiry_date:%d %b %Y} before the tender closes.', req.doc_type, doc.pk))
        else:
            until = f' (valid until {doc.expiry_date:%d %b %Y})' if doc.expiry_date else ''
            checklist.append(_item(req.label, 'ok', f'On file{until}', req.doc_type, doc.pk))

    if profile.bbbee_level and re.search(r'b-?bbee|preference points', low):
        checklist.append(_item('B-BBEE level', 'info', f'We are level {profile.bbbee_level}; check the preference-point table'))

    if opp.briefing_at:
        when = timezone.localtime(opp.briefing_at) if timezone.is_aware(opp.briefing_at) else opp.briefing_at
        if when.date() < today and opp.briefing_compulsory:
            blocking = True
            checklist.append(_item('Compulsory briefing session', 'fail', f'Was on {when:%d %b %Y}; we could not have attended'))
        else:
            label = 'Compulsory briefing session' if opp.briefing_compulsory else 'Briefing session'
            checklist.append(_item(label, 'warn' if opp.briefing_compulsory else 'info',
                                   f'{when:%a %d %b %Y, %H:%M}' + (f' at {opp.briefing_venue}' if opp.briefing_venue else '')))
    elif _BRIEFING.search(low):
        checklist.append(_item('Compulsory briefing session', 'warn', 'Mentioned in the tender; confirm the date and attend'))

    if opp.closing_date:
        days = (opp.closing_date - today).days
        if days < 0:
            blocking = True
            checklist.append(_item('Time to prepare', 'fail', 'Closing date has passed'))
        elif days < profile.min_days_to_prepare:
            checklist.append(_item('Time to prepare', 'warn', f'Only {days} day(s) left to prepare'))
        else:
            checklist.append(_item('Time to prepare', 'ok', f'{days} days until closing'))
    else:
        checklist.append(_item('Closing date', 'info', 'Not announced yet; watch the source page'))

    required = [c for c in checklist if c['status'] in ('ok', 'missing', 'warn') and c.get('doc_type')]
    if required:
        ready = sum(1 for c in required if c['status'] in ('ok', 'warn'))
        score += round(15 * ready / len(required))
        reasons.append(f'Compliance documents ready: {ready} of {len(required)}')
    else:
        score += 8

    score = max(0, min(100, int(score)))
    if blocking:
        eligibility = 'not_eligible'
    elif missing:
        eligibility = 'missing_docs'
    elif required:
        eligibility = 'eligible'
    else:
        eligibility = 'unknown'

    if blocking or (excluded and not core):
        verdict = 'low'
    elif score >= 70 and core:
        verdict = 'strong'
    elif score >= 45 and (core or related):
        verdict = 'possible'
    else:
        verdict = 'low'
    return Assessment(score, verdict, reasons, checklist, eligibility, bool(core or (related and not excluded)))


def _item(label, status, detail, doc_type=None, doc_id=None):
    item = {'label': label, 'status': status, 'detail': detail}
    if doc_type:
        item['doc_type'] = doc_type
    if doc_id:
        item['doc_id'] = doc_id
    return item


def apply_assessment(opp, result):
    opp.ai_relevance_score = result.score
    opp.ai_confidence = 1.0
    opp.fit_verdict = result.verdict
    opp.ai_match_reasons = '\n'.join(result.reasons)
    opp.eligibility = result.checklist
    opp.eligibility_status = result.eligibility
    opp.scored_at = timezone.now()
    if not opp.province:
        opp.province = detect_province(opp.title, opp.description, opp.department, opp.location)


def rescore_all(only_open=True):
    """Re-run scoring, e.g. after the bid profile or a vault document changed."""
    from .models import BidProfile, TenderOpportunity
    profile, vault, count = BidProfile.load(), document_vault(), 0
    qs = TenderOpportunity.objects.all()
    if only_open:
        qs = qs.exclude(status__in=['won', 'lost', 'declined', 'expired'])
    for opp in qs.iterator():
        apply_assessment(opp, assess(opp, profile, vault))
        opp.save(update_fields=['ai_relevance_score', 'ai_confidence', 'fit_verdict', 'ai_match_reasons',
                                'eligibility', 'eligibility_status', 'scored_at', 'province'])
        count += 1
    return count


# --------------------------------------------------------------------------- parsing helpers
def _parse_dt(value):
    """ISO-8601 text -> aware datetime (UTC 'Z' respected, naive = Johannesburg)."""
    if not value:
        return None
    text = str(value).strip().replace('Z', '+00:00')
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        try:
            dt = datetime.strptime(text[:10], '%Y-%m-%d')
        except ValueError:
            return None
    return dt if timezone.is_aware(dt) else timezone.make_aware(dt)


_MONTHS = {m: i for i, m in enumerate(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                       'september', 'october', 'november', 'december'], 1)}
_DATE_PATTERNS = [
    (re.compile(r'\b(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(20\d\d)\b', re.I),
     lambda m: date(int(m[3]), _MONTHS[m[2].lower()], int(m[1]))),
    (re.compile(r'\b(20\d\d)[-/](\d{1,2})[-/](\d{1,2})\b'), lambda m: date(int(m[1]), int(m[2]), int(m[3]))),
    (re.compile(r'\b(\d{1,2})[/.](\d{1,2})[/.](20\d\d)\b'), lambda m: date(int(m[3]), int(m[2]), int(m[1]))),
]


def find_closing_date(text, today=None):
    """Best-effort closing date from free text: prefers a date near 'closing'/'deadline'."""
    today = today or timezone.localdate()
    text = text or ''
    found = []
    for pattern, build in _DATE_PATTERNS:
        for m in pattern.finditer(text):
            try:
                d = build(m)
            except ValueError:
                continue
            window = text[max(0, m.start() - 60):m.start()].lower()
            near = any(w in window for w in ('clos', 'deadline', 'due', 'submi', 'until', 'before', 'by '))
            found.append((not near, d))
    future = [f for f in found if f[1] >= today]
    return sorted(future)[0][1] if future else None


def _clean_money(value):
    try:
        amount = Decimal(str(value))
        return amount if amount > 0 else None
    except (InvalidOperation, TypeError, ValueError):
        return None


_REF_LIKE = re.compile(r'^[A-Z0-9][A-Z0-9 /._:-]{0,40}$')


def parse_ocds_release(rel):
    """Map one OCDS release to TenderOpportunity field values (or None if unusable)."""
    tender = rel.get('tender') or {}
    title = _norm(tender.get('title'))
    desc = _norm(tender.get('description'))
    reference = ''
    if title and _REF_LIKE.match(title) and desc:
        reference, title = title, desc          # eTenders puts the bid number in "title"
    title = title or desc
    if not title:
        return None
    period = tender.get('tenderPeriod') or {}
    closing = _parse_dt(period.get('endDate'))
    published = _parse_dt(period.get('startDate')) or _parse_dt(rel.get('date'))
    buyer = (rel.get('buyer') or {}).get('name') or (tender.get('procuringEntity') or {}).get('name') or ''
    docs = [d for d in tender.get('documents') or [] if d.get('url')]
    address = tender.get('deliveryAddress') or {}
    province_raw = tender.get('province') or address.get('region') or tender.get('deliveryLocation') or ''
    briefing = tender.get('briefingSession') or {}
    briefing_at = _parse_dt(briefing.get('date')) if isinstance(briefing, dict) else None
    contact = tender.get('contactPerson') or {}
    categories = [tender.get('mainProcurementCategory') or ''] + list(tender.get('additionalProcurementCategories') or [])
    extra = []
    if reference:
        extra.append(f'Bid number: {reference}')
    if tender.get('procurementMethodDetails'):
        extra.append(f"Method: {tender['procurementMethodDetails']}")
    names = {'consultingServices': 'Consulting services', 'goods': 'Goods', 'works': 'Works', 'services': 'Services'}
    if [c for c in categories if c]:
        extra.append('Category: ' + ', '.join(dict.fromkeys(names.get(c, c) for c in categories if c)))
    if isinstance(contact, dict) and (contact.get('name') or contact.get('email')):
        extra.append('Contact: ' + ' '.join(str(contact.get(k) or '') for k in ('name', 'email', 'telephoneNumber')).strip())
    if docs:
        extra.append('Documents: ' + '; '.join(_norm(d.get('title')) or 'document' for d in docs[:6]))
    method = (tender.get('procurementMethodDetails') or '').lower()
    return {
        'ocid': rel.get('ocid', '')[:80],
        'tender_id': (rel.get('ocid') or tender.get('id') or reference)[:100],
        'reference': reference[:120],
        'kind': 'rfq' if 'quotation' in method or 'rfq' in method else 'tender',
        'title': title[:500],
        'description': '\n'.join([desc] + extra) if desc != title else '\n'.join(extra),
        'department': buyer[:300],
        'published_date': published.date() if published else None,
        'closing_date': timezone.localtime(closing).date() if closing else None,
        'closing_time': timezone.localtime(closing).time() if closing else None,
        'value_amount': _clean_money((tender.get('value') or {}).get('amount')),
        'document_url': docs[0]['url'][:200] if docs and len(docs[0]['url']) <= 200 else '',
        'source_url': f"https://www.etenders.gov.za/Home/opportunities?id={tender.get('id')}" if tender.get('id') else '',
        'province': detect_province(str(province_raw)) or detect_province(buyer),
        'location': _norm(' '.join(str(address.get(k) or '') for k in ('streetAddress', 'locality')))[:200],
        'briefing_at': briefing_at,
        'briefing_venue': _norm(str(briefing.get('venue') or ''))[:300] if isinstance(briefing, dict) else '',
        'briefing_compulsory': bool(briefing.get('compulsory')) if isinstance(briefing, dict) else False,
        'category': 'training',
    }


# --------------------------------------------------------------------------- fetchers
def _session():
    import requests
    s = requests.Session()
    s.headers.update({'User-Agent': USER_AGENT, 'Accept': 'application/json, text/html;q=0.9'})
    return s


def fetch_ocds(days_back=7, page_size=100, max_pages=25, session=None, today=None):
    """Yield OCDS releases published in the last `days_back` days."""
    today = today or timezone.localdate()
    session = session or _session()
    seen = set()
    for page in range(1, max_pages + 1):
        resp = session.get(OCDS_URL, params={'PageNumber': page, 'PageSize': page_size,
                                             'dateFrom': (today - timedelta(days=days_back)).isoformat(),
                                             'dateTo': today.isoformat()}, timeout=40)
        resp.raise_for_status()
        releases = (resp.json() or {}).get('releases') or []
        if not releases:
            break
        for rel in releases:
            key = rel.get('ocid')
            if key in seen:
                continue
            seen.add(key)
            yield rel
        if len(releases) < page_size:
            break


GRANT_WORDS = re.compile(r'discretionary grant|\bdg\b|funding window|call for (proposals|applications)|'
                         r'grant (window|funding|application)|bursar|learnership (funding|grant)|skills programme funding|'
                         r'request for proposals|applications (are )?(now )?open|expression of interest|\beoi\b|'
                         r'mandatory grant|pivotal|special projects|funding opportunit', re.I)


def scan_watch_page(url, session=None, today=None):
    """Return grant/funding leads (dicts) found on one web page."""
    import lxml.html
    session = session or _session()
    resp = session.get(url, timeout=40)
    resp.raise_for_status()
    doc = lxml.html.fromstring(resp.content)
    doc.make_links_absolute(resp.url)
    host = urlparse(resp.url).netloc
    leads, seen = [], set()
    for a in doc.iter('a'):
        href = (a.get('href') or '').split('#')[0]
        if not href.startswith('http') or href in seen:
            continue
        text = _norm(a.text_content())
        parent = a.getparent()
        context = _norm(parent.text_content()) if parent is not None else text
        context = context[:500]
        if len(text) < 12 or not GRANT_WORDS.search(text + ' ' + context):
            continue
        if urlparse(href).netloc not in (host, '') and not href.lower().endswith('.pdf'):
            continue
        seen.add(href)
        leads.append({
            'tender_id': 'web-' + hashlib.sha1(href.encode()).hexdigest()[:32],
            'title': text[:500],
            'description': context if context != text else '',
            'source_url': href[:500],
            'document_url': href[:200] if href.lower().endswith('.pdf') and len(href) <= 200 else '',
            'closing_date': find_closing_date(text + ' ' + context, today),
            'category': 'training',
        })
    return leads[:40]


# --------------------------------------------------------------------------- orchestration
@dataclass
class ScanResult:
    found: int = 0
    created: int = 0
    updated: int = 0
    errors: list = field(default_factory=list)

    def summary(self):
        text = f'{self.created} new, {self.updated} updated from {self.found} relevant'
        return text + (f'; {len(self.errors)} source error(s)' if self.errors else '')


def _upsert(source, values, profile, vault, result, today, require_relevance=True):
    from .models import TenderOpportunity
    values = dict(values)
    tender_id = values.pop('tender_id')
    existing = TenderOpportunity.objects.filter(source=source, tender_id=tender_id).first()
    opp = existing or TenderOpportunity(source=source, tender_id=tender_id, kind=source.default_kind or 'tender')
    protected = {'status', 'internal_notes', 'assigned_to', 'follow_up_date', 'follow_up_notes'}
    for key, val in values.items():
        if key in protected:
            continue
        if existing and val in (None, '') and getattr(opp, key, None):
            continue  # never wipe data a person typed in
        setattr(opp, key, val)
    outcome = assess(opp, profile, vault, today)
    if require_relevance and not existing and not outcome.relevant:
        return
    if not existing and opp.closing_date and opp.closing_date < today:
        return
    apply_assessment(opp, outcome)
    result.found += 1
    with transaction.atomic():
        opp.save()
    if existing:
        result.updated += 1
    else:
        result.created += 1


def run_scan(sources=None, days_back=7, today=None, session=None):
    """Scan every active source. Never raises: errors are logged per source."""
    from .models import BidProfile, CrawlLog, TenderOpportunity, TenderSource
    today = today or timezone.localdate()
    profile, vault = BidProfile.load(), document_vault()
    sources = sources if sources is not None else TenderSource.objects.filter(is_active=True, source_type__in=['ocds', 'watch_page'])
    total = ScanResult()
    session = session or _session()
    for source in sources:
        log = CrawlLog.objects.create(source=source, status='in_progress')
        result = ScanResult()
        try:
            if source.source_type == 'ocds':
                for rel in fetch_ocds(days_back=days_back, session=session, today=today):
                    values = parse_ocds_release(rel)
                    if values:
                        _upsert(source, values, profile, vault, result, today)
            else:
                for lead in scan_watch_page(source.base_url, session=session, today=today):
                    _upsert(source, lead, profile, vault, result, today)
            log.status = 'success'
        except Exception as exc:  # network, JSON, HTML - one bad source must not stop the others
            logger.warning('Tender source %s failed: %s', source.name, exc)
            result.errors.append(f'{source.name}: {exc}')
            log.status = 'failed'
            log.error_message = str(exc)[:2000]
        log.completed_at = timezone.now()
        log.opportunities_found = result.found
        log.opportunities_new = result.created
        log.save()
        source.last_crawled = timezone.now()
        source.last_result = (result.summary() if log.status == 'success' else f'Failed: {result.errors[-1]}')[:300]
        source.save(update_fields=['last_crawled', 'last_result'])
        for attr in ('found', 'created', 'updated'):
            setattr(total, attr, getattr(total, attr) + getattr(result, attr))
        total.errors += result.errors

    # housekeeping: anything still "new" after closing is marked expired
    TenderOpportunity.objects.filter(status__in=['new', 'viewed'], closing_date__lt=today).update(status='expired')
    return total


# --------------------------------------------------------------------------- vault definition
# The documents every bid asks for. Shown as the "Bid-ready documents" panel in the Shared Drive.
VAULT_TYPES = [
    # doc_type, label, icon, needs_expiry, hint
    ('cipc_registration', 'CIPC registration', 'fa-building-columns', False, 'CoR14.3 / company registration certificate'),
    ('tax_compliance', 'Tax compliance (TCS PIN)', 'fa-receipt', True, 'Download a fresh status from SARS eFiling'),
    ('csd_report', 'CSD registration report', 'fa-id-card', True, 'Re-download from csd.gov.za at least every 3 months'),
    ('bbbee', 'B-BBEE certificate / affidavit', 'fa-scale-balanced', True, 'Valid for 12 months from issue'),
    ('coida', 'COIDA letter of good standing', 'fa-helmet-safety', True, 'Compensation Fund letter, renewed yearly'),
    ('bank_letter', 'Bank confirmation letter', 'fa-landmark', True, 'Most buyers want one dated within 3 months'),
    ('accreditation_letter', 'Accreditation letters', 'fa-award', True, 'QCTO / SETA accreditation and scope'),
    ('company_profile', 'Company profile', 'fa-book-open', False, 'Latest signed-off version'),
    ('vat', 'VAT registration', 'fa-percent', False, 'VAT103 / registration notice'),
    ('director_id', "Directors' IDs", 'fa-user-shield', False, 'Personal information: management only'),
]
VAULT_TYPE_KEYS = [v[0] for v in VAULT_TYPES]
