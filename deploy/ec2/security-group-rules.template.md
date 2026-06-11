# RSA CMS / Mini-CRM Security Group Rule Template

Security group name suggestion:

```text
rsa-cms-ec2-demo-sg
```

Description:

```text
RSA CMS EC2 demo security group - temporary public IP testing
```

## Initial inbound rules

Replace `<YOUR_PUBLIC_IP>/32`.

| Type | Protocol | Port | Source | Notes |
|---|---|---:|---|---|
| SSH | TCP | 22 | `<YOUR_PUBLIC_IP>/32` | Required for server setup |
| Custom TCP | TCP | 8000 | `<YOUR_PUBLIC_IP>/32` | Temporary FastAPI smoke test only |

## Initial outbound rules

Default outbound is acceptable for first setup:

| Type | Protocol | Port | Destination | Notes |
|---|---|---:|---|---|
| All traffic | All | All | `0.0.0.0/0` | Allows package updates and AWS API calls |

## Do not add

```text
SSH 22 from 0.0.0.0/0
RDP 3389 from 0.0.0.0/0
FastAPI 8000 from 0.0.0.0/0
Large open port ranges
```

## After nginx/hardening

Port 8000 should normally be closed from public internet and reached only through local reverse proxy.

Future inbound public rules may be:

| Type | Protocol | Port | Source | Notes |
|---|---|---:|---|---|
| HTTP | TCP | 80 | `0.0.0.0/0` | Only after public web test approval |
| HTTPS | TCP | 443 | `0.0.0.0/0` | Only after SSL/domain path approval |
