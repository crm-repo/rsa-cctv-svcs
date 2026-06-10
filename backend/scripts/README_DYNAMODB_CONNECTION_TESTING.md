# Batch 7 — DynamoDB Connection Testing and Repository Switch Preparation

This batch prepares safe DynamoDB connection checks and a generic repository helper.
It does **not** switch the public APIs to DynamoDB yet.

## Current default behavior

The backend still uses mock/in-memory repositories by default:

```powershell
uvicorn app.main:app --reload
```

The public APIs should continue to work without AWS credentials.

## Repository mode flag

Repository mode defaults to:

```text
mock
```

Later, when the DynamoDB-backed repositories are fully wired, the mode can be changed with:

```powershell
$env:RSA_DATA_BACKEND="dynamodb"
```

For now, keep it unset or set to mock:

```powershell
$env:RSA_DATA_BACKEND="mock"
```

## Dry-run connection preview

Run this any time. It does not call AWS:

```powershell
python scripts\check_dynamodb_connection.py
```

Expected:

```text
Mode: DRY RUN
Dry run only. No AWS calls were made.
```

## Read-only AWS connection check

Run this later only after AWS credentials are configured:

```powershell
python scripts\check_dynamodb_connection.py --execute
```

This checks:

```text
AWS credentials via STS get_caller_identity
DynamoDB connectivity via list_tables
```

It does not create, update, or delete anything.

## Read-only Phase 8 table check

After DynamoDB tables are created in a later controlled step, run:

```powershell
python scripts\check_dynamodb_connection.py --execute --check-tables
```

This confirms the approved 12 tables and 5 GSIs are visible.

## Optional write/read/delete smoke test

Do not run this until tables exist and you intentionally want to test one temporary DynamoDB write.

```powershell
python scripts\test_dynamodb_repository_smoke.py --execute --confirm-write-test
```

Default target:

```text
rsa_id_counters
```

The smoke test writes one temporary item, reads it, then deletes it.

## Batch 7 safety rules

- No AWS resources are created by this batch.
- No public API behavior is changed.
- DynamoDB repository helpers are prepared but not used by default.
- Use `mock` repository mode until the DynamoDB tables are created, seeded, and verified.
