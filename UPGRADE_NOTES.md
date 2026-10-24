# Malitinne upgrade notes

## Put the upgrade on the live server (VPS 102.202.192.45)

Double-click **deploy_to_vps.bat** in this folder (or run it in cmd from here). It will:

1. pack the new code and upload it to the VPS (you type the VPS password; it may ask twice),
2. back up the live database, code and .env to ~/malitinne_backups/<date-time>/ on the VPS,
3. copy the new code in (the server's .env, media and database are never replaced),
4. switch email to hello@malitinne.co.za and set DEBUG=False. It asks for the hello@ mailbox
   password on the server; nothing shows while you type, and it is only stored in the server's .env,
5. install requirements, migrate, collect static files, restart gunicorn/nginx (or Docker),
6. send a test email to hello@malitinne.co.za and check that the main pages load,
7. offer to approve learners who were already enrolled and email them their login link.

Safe to run again (for example after fixing a wrong mailbox password). Every run makes a new backup.
To undo, the script prints the exact rollback command at the end.

## On this PC
- Your local .env still needs the real hello@ mailbox password in EMAIL_HOST_PASSWORD
  (only matters if you send email from this PC).
- python manage.py migrate      (adds approvals, programmes, enquiries, gallery + seeds them)
- python manage.py test core    (74 tests)

## Using the new features
- Approvals: /admin-dashboard/approvals/ (also Django admin > Users > action)
- Gallery: /gallery/ - add or hide photos in Django admin > Gallery photos.
  Tick "Show on home" for the 6 photos on the home page. Only post photos of people who agreed.
- Programmes, map locations and enquiries: Django admin.
- Put a face-to-face programme online: open a course > Manage > "Import learner guide", or
  python manage.py import_learner_guide KM01_Learner_Guide.docx --course "Project Manager"
      --module "KM-01 Introductory studies for Project Managers" --assessment KM-01-Learner_Assessment.docx
