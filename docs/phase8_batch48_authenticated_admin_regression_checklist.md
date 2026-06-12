# Batch 48 Checklist

- [ ] EC2 instance is running only for the test session.
- [ ] Current EC2 public IPv4 is confirmed.
- [ ] Public pages return HTTP 200.
- [ ] Public read APIs return HTTP 200.
- [ ] Admin login page returns HTTP 200.
- [ ] Anonymous admin/CRM APIs return HTTP 401.
- [ ] `/docs`, `/redoc`, and `/openapi.json` return HTTP 403.
- [ ] Direct public `:8000` is blocked/unreachable.
- [ ] Manual browser login succeeds with Cognito admin user.
- [ ] Authenticated script check passes.
- [ ] Optional write regression is run only if live test records are acceptable.
- [ ] Batch files are committed and pushed.
- [ ] EC2 is stopped if no immediate next batch is planned.
