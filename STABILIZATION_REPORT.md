# Stabilization Report

## Stabilization Pass - 2026-09-12

| Issue | Status | Commit | Files touched | Verification |
|---|---|---|---|---|
| 1. Split views package | Blocked | - | None | Deferred: physical extraction of 3,700-line views module requires a dedicated refactor pass to preserve imports and behavior safely. |
| 2. Duplicate functions | Fixed | `eeb2c48` | `core/views.py` | Exactly one `ai_query_count_api` and one `discussions_list`; `manage.py check` and tests pass. |
| 3. Mid-file imports | Fixed | `19bdadd` | `core/views.py` | Duplicate pandas/import block removed; Workbook moved to module scope; checks and tests pass. |
| 4. Permission consolidation | Deferred | `b77d154` | `core/permissions.py`, `core/views.py` | Shared predicates/decorators centralized and imported by views. Endpoint-by-endpoint inline authorization replacement remains deferred to avoid response changes without the expanded test suite. |
| 5. Forum mismatch | Blocked | `fda4b47` | `core/models.py`, `core/views.py`, `core/migrations/0002_forumpost_liked_by_forumtopic_is_closed_and_more.py`, `lms/urls.py`, `templates/lesson_detail.html` | Model/view/template contracts align; checks and tests pass. Applying the migration is blocked by PostgreSQL authentication failure for local user `postgres`. |
| 6. Expired opportunities | Fixed | `51657ee` | `core/views.py`, `core/tasks.py`, `lms/celery.py`, `lms/__init__.py` | GET write removed; task registered at 00:05 daily; task registry and schedule inspected; checks and tests pass. |
| 7. Media lockdown | Deferred | - | None | Not changed. Requires a verified Nginx/media deployment and ownership matrix for every file model. |
| 8. Email tasks | Deferred | - | None | Existing inline sends remain. Requires task package design and email-template regression tests. |
| 9. CSRF exemptions | Fixed | `af7344b` | `core/views.py` | Both `csrf_exempt` decorators removed. No frontend fetch caller for these endpoints exists; existing HTML upload form includes a CSRF token. Checks and tests pass. |
| 10. Tender crawl stub | Fixed | `f4445da` | `core/views.py`, `templates/tender_dashboard.html` | Endpoint returns JSON 501 and dashboard control removed. Checks and tests pass. |
| 11. Registration fields | Fixed | `b0d0956` | `core/tests.py` | Confirmed all requested fields exist on `User`; direct POST regression test verifies assignments. Checks and tests pass. |
| 12. High-risk tests | Deferred | - | None | Only existing health and registration tests are present. Coverage is 43% overall and 16% for `core/views.py`; 60% target is not met. |
| 13. Dead code/routing | Deferred | - | None | Full route/dead-code inventory requires the views package split and template inventory. |
| 14. Makefile loop | Fixed | `84cdbb8` | `Makefile`, `pytest.ini` | `coverage run -m pytest` collected 2 tests and passed; coverage report generated; Django checks/tests pass. |

## Behavior Changes

- `/tender-crawl/` now returns `{"error": "not_implemented"}` with HTTP 501 for admins instead of redirecting with a flash message. The dashboard crawl button was removed.
- The legacy discussion `toggle-close` route now uses the consolidated lock handler and returns both `is_locked` and `is_closed` keys.
- Expired opportunities are no longer updated during a public GET request; the update is performed by the scheduled Celery task.
- Administrative bulk-upload endpoints now require normal CSRF validation.
- Forum routes gained the authenticated lesson discussion list route and model-backed pin/close/view/like behavior.

## Test Coverage

Current coverage run:

- Total: 43%
- `core/views.py`: 16%
- `core/permissions.py`: 34%
- Tests collected: 2
- Tests passed: 2

The requested 60% view/permission coverage target is not met.

## Blockers

- Local PostgreSQL authentication fails for user `postgres`, so migration application and database-backed tests cannot be verified against the configured database.
- Nginx is not running/reachable in this environment, so media lockdown cannot be safely validated end to end.
- The repository currently has an unrelated modified `core/ai_assistant.py` file that was not changed by this pass.

## Next Three Recommended Steps

1. Restore a disposable PostgreSQL test database with valid credentials and apply migration `core.0002`.
2. Complete the media authorization design and verify it through Nginx before exposing learner documents or evidence.
3. Extract `core/views.py` into the requested package, then add the high-risk test suites until the 60% coverage target is met.
