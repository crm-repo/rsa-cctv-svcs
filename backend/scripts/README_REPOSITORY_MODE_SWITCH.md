# Batch 8 — Environment-Based Repository Mode Switch

Batch 8 adds a controlled repository mode switch for the CRM/lead repositories while keeping local development safe.

## Safe default

The default is still mock/in-memory mode:

```powershell
python scripts\check_repository_mode.py
```

Expected:

```text
Repository mode: mock
AWS calls made: False
customers: CustomerRepository
bookings: BookingRepository
inquiries: InquiryRepository
id_counters: IdCounterRepository
```

Public APIs should continue to work locally without AWS credentials:

```powershell
uvicorn app.main:app --reload
```

## Preferred environment variable

Use this going forward:

```powershell
$env:RSA_REPOSITORY_MODE="mock"
```

Later, after DynamoDB tables exist and seed data is loaded:

```powershell
$env:RSA_REPOSITORY_MODE="dynamodb"
```

Older aliases still work for backward compatibility:

```powershell
$env:RSA_DATA_BACKEND="mock"
$env:DATA_BACKEND="mock"
```

## What switches in Batch 8

Batch 8 prepares the repository switch for these CRM/lead repositories:

```text
customers
bookings
inquiries
id_counters
```

Mock mode classes:

```text
CustomerRepository
BookingRepository
InquiryRepository
IdCounterRepository
```

DynamoDB mode classes:

```text
DynamoDBCustomerRepository
DynamoDBBookingRepository
DynamoDBInquiryRepository
DynamoDBIdCounterRepository
```

## Important safety rule

Do not run the public API in DynamoDB mode yet unless all of these are true:

```text
1. DynamoDB tables have been created.
2. Table check passes.
3. JSON seed loader has been executed.
4. DynamoDB write/read/delete smoke test passes.
5. AWS credentials and region are confirmed.
```

Until then, keep:

```powershell
$env:RSA_REPOSITORY_MODE="mock"
```

## Dry-run checks

No AWS calls:

```powershell
python scripts\check_repository_mode.py
python scripts\check_dynamodb_connection.py
```

Read-only AWS checks later, after credentials are configured:

```powershell
python scripts\check_dynamodb_connection.py --execute
python scripts\check_dynamodb_connection.py --execute --check-tables
```

Write/read/delete smoke test later, after tables exist:

```powershell
python scripts\test_dynamodb_repository_smoke.py --execute --confirm-write-test
```
