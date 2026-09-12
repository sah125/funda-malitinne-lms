## Stabilization Pass - 2026-09-12

- Fixed duplicate AI-count and discussion view definitions in `eeb2c48`.
- Consolidated learner-hub imports in `19bdadd`.
- Aligned discussion models, views, routes, templates, likes, nested replies, and migration in `fda4b47`; migration application remains blocked by local PostgreSQL credentials.
- Centralized shared role permission helpers in `b77d154`; full inline-check migration remains deferred.
- Moved expired-opportunity cleanup from the public GET handler to a daily 00:05 Celery task in `51657ee`.
- Restored CSRF protection on administrative bulk uploads in `af7344b`.
- Replaced the tender crawl stub with an explicit 501 response and removed its dashboard button in `f4445da`.
- Added registration regression coverage for all custom `User` fields in `b0d0956`.
- Added the Makefile and pytest configuration for the verification loop in `84cdbb8`.
- Deferred the views package extraction, media lockdown, email task migration, high-risk test suite, and dead-code routing audit pending the database/deployment prerequisites and a dedicated refactor pass.
