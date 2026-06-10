"""Repository layer foundation for RSA CMS / Mini-CRM.

Repositories isolate data access from service/business logic.
For now, these repositories are in-memory/DynamoDB-ready skeletons.
Later batches can replace their internals with boto3/DynamoDB calls while
keeping routes and services stable.
"""
