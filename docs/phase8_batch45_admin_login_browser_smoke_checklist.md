# Batch 45 Admin Login Browser Smoke Checklist

## EC2

- [ ] EC2 instance is running only while testing.
- [ ] Current public IP has been confirmed.
- [ ] Port 80 is reachable from tester IP.
- [ ] Direct port 8000 remains blocked publicly.

## Public/admin exposure

- [ ] Public homepage loads.
- [ ] `/admin/login.html` loads.
- [ ] `/api/admin/auth/config` returns Cognito config.
- [ ] `/api/admin/auth/status` returns anonymous/authenticated=false before login.

## Browser login

- [ ] Login was tested in a private/incognito browser.
- [ ] Admin email used: `jhannbernas@gmail.com`.
- [ ] Password was not pasted into chat.
- [ ] Password was not committed to Git.
- [ ] If Cognito forced a password change, a permanent password was set.
- [ ] No SMS verification was required.
- [ ] No phone number was required.
- [ ] Admin session/token was established.

## Locked-down surfaces

- [ ] `/api/admin/products` remains 403.
- [ ] `/api/customers` remains 403.
- [ ] `/api/bookings` remains 403.
- [ ] `/api/inquiries` remains 403.
- [ ] `/docs` remains 403.
- [ ] `/openapi.json` remains 403.

## End of batch

- [ ] Batch 45 script/checklist files committed and pushed.
- [ ] EC2 stopped if not continuing immediately.
