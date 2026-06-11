# Batch 21 — Admin CMS management pages/actions

Adds admin CMS pages and safe create/update actions for:

- About Us
- Project Gallery
- Services
- Contact Us / Contact Persons / Social Media

Still not included:

- Delete actions
- Image upload
- Cognito/admin login protection
- Final UI polish

## Local test

Backend:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\frontend"
python -m http.server 5500
```

Open:

- http://127.0.0.1:5500/admin/about.html
- http://127.0.0.1:5500/admin/project-gallery.html
- http://127.0.0.1:5500/admin/services.html
- http://127.0.0.1:5500/admin/contact-us.html

Optional backend smoke test:

```powershell
python scripts\test_admin_cms_crud_smoke.py
python scripts\test_admin_cms_crud_smoke.py --execute --confirm-write-test
```
