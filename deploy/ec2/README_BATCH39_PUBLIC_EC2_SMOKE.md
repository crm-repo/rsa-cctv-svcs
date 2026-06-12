# Batch 39 — Public EC2 Smoke Regression

This batch is local-machine verification only. It does not need a new server-side install step.

Run from local PowerShell:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\check_ec2_public_site_smoke.py --base-url http://<PUBLIC_IPV4>
```

Optional write check:

```powershell
python scripts\check_ec2_public_site_smoke.py --base-url http://<PUBLIC_IPV4> --execute --confirm-write-test
```

Do not expose direct backend port 8000 publicly. Public traffic should go through Nginx on port 80.
