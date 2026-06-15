cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"

.\venv\Scripts\activate

$env:RSA_REPOSITORY_MODE="dynamodb"
$env:AWS_DEFAULT_REGION="ap-southeast-1"
$env:AWS_REGION="ap-southeast-1"

$env:RSA_ADMIN_AUTH_MODE="cognito"
$env:RSA_COGNITO_REGION="ap-southeast-1"
$env:RSA_COGNITO_USER_POOL_ID="ap-southeast-1_BNvYFNmw9"
$env:RSA_COGNITO_CLIENT_ID="3r13vplp8agjigm3e52ficsm1e"

$env:RSA_MEDIA_STORAGE_MODE="local"
$env:RSA_MEDIA_MAX_UPLOAD_MB="5"

Write-Host "RSA CMS local backend starting..."
Write-Host "Repository mode: DynamoDB"
Write-Host "Admin auth mode: Cognito"
Write-Host "Media mode: local"
Write-Host "Backend URL: http://127.0.0.1:8000"

uvicorn app.main:app --reload
