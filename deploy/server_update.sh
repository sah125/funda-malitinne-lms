#!/usr/bin/env bash
# =============================================================================
#  Malitinne / Funda Malitinne LMS: one-step server update
#
#  Run by deploy_to_vps.bat (on your Windows PC), or by hand on the VPS:
#      sudo bash /tmp/malitinne_upgrade/deploy/server_update.sh /tmp/malitinne_upgrade
#  Or, after "git pull" in the live project folder on the VPS:
#      sudo bash deploy/server_update.sh --in-place
#
#  What it does, in order (it stops at the first real error):
#    1. Finds the live project folder (or use APP_DIR=/path).
#    2. Detects Docker (docker compose) or a normal gunicorn/systemd setup.
#    3. Backs up the database, the current code and .env.
#    4. Copies the new code in (your .env, media and database are never replaced).
#    5. Switches email to hello@malitinne.co.za and asks for the mailbox password
#       (typed on the server, never shown, never stored anywhere except .env).
#    6. Installs requirements, migrates, collects static files.
#    7. Sends a test email, restarts the site and checks that pages load.
#    8. Optionally approves learners who were already enrolled.
#
#  Optional settings (environment variables):
#    APP_DIR=/opt/lms           project folder on the server
#    MAIL_PASSWORD=...          skip the password prompt (automation)
#    ASSUME_YES=1               answer "yes" to questions (automation)
#    SKIP_RESTART=1             do not restart services (testing)
# =============================================================================
set -Eeuo pipefail

IN_PLACE=""
if [ "${1:-}" = "--in-place" ]; then
    IN_PLACE=1
    APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # the folder you just git-pulled
    STAGE="$APP_DIR"
else
    STAGE="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
fi
NEW_FILES=(core lms templates static manage.py requirements.txt gunicorn_config.py deploy)
MAILBOX="hello@malitinne.co.za"
TS="$(date +%Y%m%d-%H%M%S)"

c_ok=$'\e[32m'; c_warn=$'\e[33m'; c_err=$'\e[31m'; c_b=$'\e[1m'; c_0=$'\e[0m'
step() { echo; echo "${c_b}==> $*${c_0}"; }
ok()   { echo "${c_ok}  ✓ $*${c_0}"; }
warn() { echo "${c_warn}  ! $*${c_0}"; }
die()  { echo "${c_err}  ✗ $*${c_0}"; echo; echo "Nothing after this point was changed."; [ -n "${BACKUP_DIR:-}" ] && echo "Backup: $BACKUP_DIR"; exit 1; }
trap 'echo "${c_err}  ✗ Failed on line $LINENO: $BASH_COMMAND${c_0}" >&2; [ -n "${CODE_COPIED:-}" ] && { echo; echo "To roll back the code:  cd $APP_DIR && tar -xzf $BACKUP_DIR/code.tar.gz && cp $BACKUP_DIR/env.bak .env"; } >&2' ERR

ask_yes() {  # ask_yes "Question?"  -> 0 for yes
    [ "${ASSUME_YES:-}" = "1" ] && return 0
    local a; read -r -p "  $1 [y/N] " a </dev/tty || a=""; [[ "$a" =~ ^[Yy] ]]
}

# ---------------------------------------------------------------- 0. sanity
[ -f "$STAGE/manage.py" ] && [ -f "$STAGE/core/models.py" ] || die "Upgrade files not found in $STAGE"

# ---------------------------------------------------------------- 1. project folder
step "Finding the live project folder"
is_project() { [ -f "$1/manage.py" ] && [ -f "$1/lms/settings.py" ]; }
if [ -z "${APP_DIR:-}" ]; then
    # (a) Which folder is the RUNNING site using? Look at gunicorn/uwsgi/runserver processes,
    #     systemd WorkingDirectory=, and Docker containers that mount a host folder at /app.
    LIVE_RAW=""
    SERVER_RE='^([^ ]*/)?(gunicorn|uwsgi|daphne|uvicorn)( |:|$)|^([^ ]*/)?python[0-9.]* +(-[^ ]+ +)*([^ ]*/)?(gunicorn|uwsgi|daphne|uvicorn|manage\.py +runserver)( |$)'
    for pid in $(ps -eo pid=,args= 2>/dev/null | sed -E 's/^ *//' | awk '{pid=$1; $1=""; sub(/^ /,""); print pid "\t" $0}' \
                 | grep -P "\t" | awk -F'\t' -v re="$SERVER_RE" '$2 ~ re {print $1}' || true); do
        cwd="$(readlink -f "/proc/$pid/cwd" 2>/dev/null || true)"
        if [ -n "$cwd" ] && is_project "$cwd"; then LIVE_RAW+="$cwd"$'\n'; fi
    done
    if command -v systemctl >/dev/null 2>&1; then
        for u in $(systemctl list-units --type=service --state=running --no-legend --plain 2>/dev/null | awk '{print $1}' | grep -Ei 'gunicorn|malitinne|funda|lms|django|uwsgi' || true); do
            wd="$(systemctl show -p WorkingDirectory --value "$u" 2>/dev/null || true)"
            if [ -n "$wd" ] && is_project "$wd"; then LIVE_RAW+="$(readlink -f "$wd")"$'\n'; fi
        done
    fi
    if command -v docker >/dev/null 2>&1; then
        for c in $(docker ps -q 2>/dev/null || true); do
            src="$(docker inspect --format '{{range .Mounts}}{{if eq .Destination "/app"}}{{.Source}}{{end}}{{end}}' "$c" 2>/dev/null || true)"
            if [ -n "$src" ] && is_project "$src"; then LIVE_RAW+="$(readlink -f "$src")"$'\n'; fi
        done
    fi
    mapfile -t LIVE < <(printf '%s' "$LIVE_RAW" | grep . | sort -u || true)

    # (b) Every copy of the project on disk.
    mapfile -t CANDIDATES < <(find /opt /srv /var/www /home /root /app -maxdepth 4 -name manage.py 2>/dev/null \
        | while read -r m; do d="$(readlink -f "$(dirname "$m")")"; if is_project "$d" && [[ "$d" != /tmp/* ]]; then echo "$d"; fi; done | sort -u || true)

    if [ "${#LIVE[@]}" -eq 1 ]; then
        APP_DIR="${LIVE[0]}"
        ok "The running site is served from $APP_DIR"
    elif [ "${#CANDIDATES[@]}" -eq 0 ]; then
        die "Could not find the project (a folder with manage.py and lms/settings.py). Run again and type the folder when asked"
    elif [ "${#CANDIDATES[@]}" -eq 1 ]; then
        APP_DIR="${CANDIDATES[0]}"
    else
        echo "  Found more than one copy of the project:"
        i=1
        for d in "${CANDIDATES[@]}"; do
            tag=""
            for l in "${LIVE[@]}"; do [ "$l" = "$d" ] && tag="  <-- RUNNING NOW"; done
            [[ "$d" == *backup* ]] && tag="$tag  (looks like a backup)"
            db="no db.sqlite3"; [ -f "$d/db.sqlite3" ] && db="database last written $(date -r "$d/db.sqlite3" '+%F %H:%M' 2>/dev/null || echo '?')"
            code="code changed $(date -r "$d/manage.py" +%F 2>/dev/null || echo '?')"
            echo "    $i) $d   [$db · $code]$tag"
            i=$((i+1))
        done
        echo "  Tip: the live site is usually the one whose database was written most recently."
        n=""
        while ! [[ "$n" =~ ^[0-9]+$ ]] || [ "$n" -lt 1 ] || [ "$n" -gt "${#CANDIDATES[@]}" ]; do
            read -r -p "  Which one is the LIVE site? [1-${#CANDIDATES[@]}] " n </dev/tty || die "No answer given"
        done
        APP_DIR="${CANDIDATES[$((n-1))]}"
    fi
fi
[ -f "$APP_DIR/manage.py" ] || die "$APP_DIR does not contain manage.py"
ENV_FILE="$APP_DIR/.env"
[ -f "$ENV_FILE" ] || die "$ENV_FILE is missing. The server needs its .env (database password etc.) before updating"
[ -z "$IN_PLACE" ] && [ "$(cd "$APP_DIR" && pwd -P)" = "$(cd "$STAGE" && pwd -P)" ] && die "The upgrade folder and the live project are the same folder ($APP_DIR)"
ok "Project: $APP_DIR"

envget() { { grep -E "^[[:space:]]*$1=" "$ENV_FILE" || true; } | tail -1 | cut -d= -f2- | sed -E "s/^['\"]//; s/['\"][[:space:]]*\$//; s/\r\$//"; }

# ---------------------------------------------------------------- 2. how is it running?
step "Detecting how the site runs"
MODE="systemd"; DC=""
if command -v docker >/dev/null 2>&1 && [ -f "$APP_DIR/docker-compose.yml" ]; then
    if docker compose version >/dev/null 2>&1; then DC="docker compose"; elif command -v docker-compose >/dev/null 2>&1; then DC="docker-compose"; fi
    if [ -n "$DC" ] && (cd "$APP_DIR" && $DC ps --services --filter status=running 2>/dev/null | grep -qx web); then MODE="docker"; fi
fi

SERVICES=()
SETTINGS_MODULE=""
if [ "$MODE" = "systemd" ]; then
    if command -v systemctl >/dev/null 2>&1; then
        mapfile -t SERVICES < <(systemctl list-units --type=service --all --no-legend --plain 2>/dev/null \
            | awk '{print $1}' | grep -Ei 'gunicorn|malitinne|funda|lms|django|celery|uvicorn' || true)
        for s in "${SERVICES[@]}"; do
            m="$(systemctl cat "$s" 2>/dev/null | grep -oE 'DJANGO_SETTINGS_MODULE=[A-Za-z0-9_.]+' | head -1 | cut -d= -f2 || true)"
            [ -n "$m" ] && SETTINGS_MODULE="$m" && break
        done
    fi
    PY=""
    for v in venv .venv env new.venv; do [ -x "$APP_DIR/$v/bin/python" ] && PY="$APP_DIR/$v/bin/python" && break; done
    if [ -z "$PY" ] && [ "${#SERVICES[@]}" -gt 0 ]; then
        g="$(systemctl cat "${SERVICES[@]}" 2>/dev/null | grep -oE '/[^ ]*/bin/gunicorn' | head -1 || true)"
        [ -n "$g" ] && [ -x "$(dirname "$g")/python" ] && PY="$(dirname "$g")/python"
    fi
    [ -z "$PY" ] && PY="$(command -v python3)" && warn "No virtualenv found, using $PY"
    SETTINGS_MODULE="${SETTINGS_MODULE:-lms.settings}"
    ok "Mode: gunicorn/systemd · Python: $PY · Settings: $SETTINGS_MODULE"
    [ "${#SERVICES[@]}" -gt 0 ] && ok "Services to restart: ${SERVICES[*]}" || warn "No gunicorn/LMS service found; you may need to restart the app yourself"
else
    SETTINGS_MODULE="lms.settings_production"
    ok "Mode: Docker ($DC) · Settings: $SETTINGS_MODULE"
fi

manage() {
    if [ "$MODE" = "docker" ]; then (cd "$APP_DIR" && $DC exec -T web python manage.py "$@" --settings="$SETTINGS_MODULE")
    else (cd "$APP_DIR" && DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE" "$PY" manage.py "$@"); fi
}

# ---------------------------------------------------------------- 3. backup
step "Backing up (database, code, .env)"
BACKUP_DIR="${BACKUP_ROOT:-$HOME/malitinne_backups}/$TS"
mkdir -p "$BACKUP_DIR"; chmod 700 "$BACKUP_DIR"
cp -p "$ENV_FILE" "$BACKUP_DIR/env.bak"
(cd "$APP_DIR" && tar -czf "$BACKUP_DIR/code.tar.gz" --exclude='__pycache__' --exclude='*.pyc' \
    $(for f in "${NEW_FILES[@]}"; do if [ -e "$f" ]; then echo "$f"; fi; done))
# Ask Django which database the LIVE site really uses (the .env text can be misleading:
# DB_ENGINE=django.db.backends.postgresql still means SQLite under lms.settings).
DBINFO="$(manage shell -v 0 -c "from django.db import connection as c; d=c.settings_dict; print('DBINFO|'+c.vendor+'|'+str(d['NAME'])+'|'+str(d.get('USER') or '')+'|'+str(d.get('HOST') or '')+'|'+str(d.get('PORT') or ''))" 2>/dev/null | grep '^DBINFO|' | tail -1 || true)"
if [ -n "$DBINFO" ]; then
    IFS='|' read -r _ DB_VENDOR DB_NAME DB_USER DB_HOST DB_PORT <<< "$DBINFO"
else
    warn "Could not ask Django which database is in use; guessing from .env"
    DB_NAME="$(envget DB_NAME)"; DB_USER="$(envget DB_USER)"; DB_HOST="$(envget DB_HOST)"; DB_PORT="$(envget DB_PORT)"
    if [ "$(envget DB_ENGINE)" = "postgresql" ] || [ "$MODE" = "docker" ]; then DB_VENDOR=postgresql; else DB_VENDOR=sqlite; DB_NAME="$APP_DIR/db.sqlite3"; fi
fi
DB_PASS="$(envget DB_PASSWORD)"
ok "Live database: $DB_VENDOR ($DB_NAME)"
DB_DONE=""
if [ "$DB_VENDOR" = "postgresql" ]; then
    DB_NAME="${DB_NAME:-funda_malitinne_lms}"; DB_USER="${DB_USER:-postgres}"
    if [ "$MODE" = "docker" ]; then
        (cd "$APP_DIR" && $DC exec -T db pg_dump -U "$DB_USER" "$DB_NAME") > "$BACKUP_DIR/database.sql" && DB_DONE=1
    else
        PGPASSWORD="$DB_PASS" pg_dump -h "${DB_HOST:-localhost}" -p "${DB_PORT:-5432}" -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/database.sql" 2>/dev/null && DB_DONE=1 \
          || { command -v sudo >/dev/null && sudo -u postgres pg_dump "$DB_NAME" > "$BACKUP_DIR/database.sql" 2>/dev/null && DB_DONE=1; } || true
    fi
else
    SQLITE="${DB_NAME:-$APP_DIR/db.sqlite3}"; [[ "$SQLITE" != /* ]] && SQLITE="$APP_DIR/$SQLITE"
    [ -f "$SQLITE" ] && python3 -c "import sqlite3,sys; s=sqlite3.connect(sys.argv[1]); d=sqlite3.connect(sys.argv[2]); s.backup(d); d.close()" "$SQLITE" "$BACKUP_DIR/db.sqlite3" && DB_DONE=1
fi
if [ -n "$DB_DONE" ] && { [ -s "$BACKUP_DIR/database.sql" ] || [ -s "$BACKUP_DIR/db.sqlite3" ]; }; then
    chmod 600 "$BACKUP_DIR"/*; ok "Backup saved in $BACKUP_DIR"
else
    rm -f "$BACKUP_DIR/database.sql"
    warn "Could not back up the database automatically."
    ask_yes "Continue WITHOUT a database backup?" || die "Stopped so you can back up the database first"
fi

# ---------------------------------------------------------------- 4. copy new code
if [ -n "$IN_PLACE" ]; then
step "Using the code you just pulled with git"
ok "In-place mode: $APP_DIR (undo with: git -C $APP_DIR reset --hard ORIG_HEAD)"
else
step "Installing the new code"
for f in "${NEW_FILES[@]}"; do
    [ -e "$STAGE/$f" ] || continue
    if [ -d "$STAGE/$f" ]; then mkdir -p "$APP_DIR/$f" && cp -a "$STAGE/$f/." "$APP_DIR/$f/"; else cp -a "$STAGE/$f" "$APP_DIR/$f"; fi
done
find "$APP_DIR/core" "$APP_DIR/lms" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
CODE_COPIED=1
ok "Code copied (your .env, media/ and database were not touched)"
fi

# ---------------------------------------------------------------- 5. email settings
step "Switching email to $MAILBOX"
CUR_PW="$(envget EMAIL_HOST_PASSWORD)"; CUR_USER="$(envget EMAIL_HOST_USER)"
PW="${MAIL_PASSWORD:-}"
if [ -z "$PW" ]; then
    if [ "$CUR_USER" = "$MAILBOX" ] && [ -n "$CUR_PW" ] && [[ "$CUR_PW" != PUT-THE-* ]]; then
        ok "Server already has a password for $MAILBOX"
        ask_yes "Type a new mailbox password anyway?" && read -r -s -p "  Password for $MAILBOX: " PW </dev/tty && echo
    else
        echo "  Type the password of the $MAILBOX mailbox (cPanel > Email Accounts)."
        echo "  Nothing will show while you type. Press Enter when done."
        while [ -z "$PW" ]; do read -r -s -p "  Password for $MAILBOX: " PW </dev/tty; echo; done
    fi
fi
SITE_HOST="$(envget ALLOWED_HOSTS | cut -d, -f1)"
PW="$PW" SITE_HOST="${SITE_HOST:-malitinne.co.za}" "$(command -v python3)" - "$ENV_FILE" <<'PY'
import os, sys
path = sys.argv[1]
pw = os.environ.get('PW', '')
updates = {
    'DEBUG': 'False',
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'mail.malitinne.co.za',
    'EMAIL_PORT': '465',
    'EMAIL_USE_SSL': 'True',
    'EMAIL_USE_TLS': 'False',
    'EMAIL_HOST_USER': 'hello@malitinne.co.za',
    'DEFAULT_FROM_EMAIL': 'Malitinne <hello@malitinne.co.za>',
    'CONTACT_EMAIL': 'hello@malitinne.co.za',
    'REGISTRATION_NOTIFY_EMAILS': 'hello@malitinne.co.za',
    'ADMIN_EMAIL': 'hello@malitinne.co.za',
    'SITE_URL': 'https://malitinne.co.za',
}
if pw:
    if "'" not in pw:
        updates['EMAIL_HOST_PASSWORD'] = "'" + pw + "'"      # quoted: keeps # and spaces literal
    elif '#' not in pw and pw == pw.strip():
        updates['EMAIL_HOST_PASSWORD'] = pw
    else:
        sys.exit("This password has both ' and # in it, which .env files cannot store safely. "
                 "Change the mailbox password in cPanel and run this again.")
with open(path, encoding='utf-8') as fh:
    lines = fh.read().splitlines()
out, seen = [], set()
for line in lines:
    stripped = line.strip()
    key = stripped.split('=', 1)[0].strip() if ('=' in stripped and not stripped.startswith('#')) else None
    if key in updates:
        if key not in seen:
            out.append(f'{key}={updates[key]}'); seen.add(key)
        continue
    if 'sah.sakhile@gmail.com' in line:
        continue          # remove the old personal Gmail address everywhere
    out.append(line)
missing = [k for k in updates if k not in seen]
if missing:
    out.append('')
    out.append('# ---- Malitinne email (hello@malitinne.co.za) ----')
    out += [f'{k}={updates[k]}' for k in missing]
tmp = path + '.new'
with open(tmp, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(out) + '\n')
os.chmod(tmp, 0o600)
os.replace(tmp, path)
PY
unset PW MAIL_PASSWORD
chmod 600 "$ENV_FILE"
grep -q 'sah.sakhile' "$ENV_FILE" && die ".env still mentions the old Gmail address"
ok ".env updated: DEBUG=False, email via $MAILBOX, old Gmail removed"

# ---------------------------------------------------------------- 6. install, migrate, static
step "Installing requirements, updating the database, collecting static files"
if [ "$MODE" = "docker" ]; then
    (cd "$APP_DIR" && $DC build web && $DC up -d) || die "Docker build/start failed"
    sleep 5
else
    "$PY" -m pip install -q -r "$APP_DIR/requirements.txt" || die "pip install failed (see above)"
fi
manage check --fail-level ERROR >/dev/null || { manage check; die "Django check failed"; }
manage migrate --noinput
manage collectstatic --noinput -v 0
ok "Database migrated and static files collected"

# ---------------------------------------------------------------- 7. restart + test
step "Restarting the site"
if [ "${SKIP_RESTART:-}" = "1" ]; then
    warn "SKIP_RESTART=1, not restarting"
elif [ "$MODE" = "docker" ]; then
    (cd "$APP_DIR" && $DC up -d --force-recreate web celery celery_beat 2>/dev/null || $DC up -d --force-recreate web)
    ok "Containers recreated"
else
    for s in "${SERVICES[@]}"; do systemctl restart "$s" && ok "Restarted $s" || warn "Could not restart $s"; done
    if command -v nginx >/dev/null 2>&1; then nginx -t >/dev/null 2>&1 && systemctl reload nginx && ok "nginx reloaded" || warn "nginx config test failed; nginx left as it was"; fi
fi

step "Scheduling the daily tender & grant scan (06:00)"
mkdir -p "$APP_DIR/logs"
if [ "$MODE" = "docker" ]; then
    JOB="cd $APP_DIR && $DC exec -T web python manage.py staff_daily --settings=$SETTINGS_MODULE"
else
    JOB="cd $APP_DIR && DJANGO_SETTINGS_MODULE=$SETTINGS_MODULE $PY manage.py staff_daily"
fi
if [ -d /etc/cron.d ] && [ "$(id -u)" -eq 0 ]; then
    cat > /etc/cron.d/malitinne-staff-daily <<CRON
# Malitinne staff portal: scan eTenders + SETA/NYDA/NSF pages, notify staff, remind about expiring bid documents
SHELL=/bin/bash
CRON_TZ=Africa/Johannesburg
0 6 * * * root $JOB >> $APP_DIR/logs/staff_daily.log 2>&1
CRON
    chmod 644 /etc/cron.d/malitinne-staff-daily
    ok "Daily scan scheduled (log: $APP_DIR/logs/staff_daily.log)"
else
    warn "Could not install the daily schedule automatically. Add this line with 'crontab -e':"
    echo "    0 4 * * * $JOB >> $APP_DIR/logs/staff_daily.log 2>&1   (04:00 UTC = 06:00 SAST)"
fi
if [ "${SKIP_RESTART:-}" != "1" ]; then
    (eval "$JOB --scan-only" >> "$APP_DIR/logs/staff_daily.log" 2>&1 &)
    ok "First scan started in the background; tenders appear on the staff portal within a few minutes"
fi

step "Sending a test email to $MAILBOX"
EMAIL_OK=""
if MAIL_OUT="$(manage sendtestemail "$MAILBOX" 2>&1)"; then EMAIL_OK=1; ok "Test email sent; check the $MAILBOX inbox"
else
    warn "The test email FAILED: $(echo "$MAIL_OUT" | grep -v '^[[:space:]]' | tail -1)"
    warn "Usually a wrong mailbox password (or the VPS cannot reach mail.malitinne.co.za on port 465). Fix it, then run the update again and retype the password when asked."
fi

step "Checking the site responds"
sleep 3
for path in / /programmes/ /gallery/ /login/ /staff-portal/; do
    code="$(curl -s -o /dev/null -w '%{http_code}' -H "Host: ${SITE_HOST:-malitinne.co.za}" -H 'X-Forwarded-Proto: https' "http://127.0.0.1:8000$path" 2>/dev/null || true)"
    [ "$code" = "000" ] && code="$(curl -sk -o /dev/null -w '%{http_code}' "https://127.0.0.1$path" -H "Host: ${SITE_HOST:-malitinne.co.za}" 2>/dev/null || true)"
    case "$code" in 200|301|302) ok "$path → $code";; *) warn "$path → $code (check: journalctl -u ${SERVICES[0]:-gunicorn} -n 50)";; esac
done
if [ "$SETTINGS_MODULE" = "lms.settings_production" ] && ! (ss -ltn 2>/dev/null | grep -q ':443 '); then
    warn "Production settings force HTTPS but nothing listens on port 443."
    warn "Get a certificate:  certbot --nginx -d malitinne.co.za -d www.malitinne.co.za"
fi

# ---------------------------------------------------------------- 8. existing learners
step "Learners who registered before approvals existed"
manage approve_existing_students --list || true
if [ -z "$EMAIL_OK" ]; then
    warn "Skipped: email is not working yet, so they would not receive their login link. Fix email, then run again."
elif ask_yes "Approve the learners above who are already enrolled in a course, and email them a login link?"; then
    manage approve_existing_students --enrolled-only --notify
else
    echo "  Skipped. Approve them later at https://malitinne.co.za/admin-dashboard/approvals/"
fi

trap - ERR
echo
echo "${c_ok}${c_b}All done.${c_0}  Backup: $BACKUP_DIR"
echo "To undo the code change:  cd $APP_DIR && tar -xzf $BACKUP_DIR/code.tar.gz && cp $BACKUP_DIR/env.bak .env  (then restart)"
case "$STAGE" in /tmp/malitinne_upgrade*) rm -rf "$STAGE" /tmp/malitinne_upgrade.tar.gz 2>/dev/null || true;; esac
