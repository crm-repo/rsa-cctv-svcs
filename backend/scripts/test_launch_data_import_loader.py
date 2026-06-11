from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = BACKEND_ROOT / 'scripts' / 'import_launch_data_to_dynamodb.py'


def run_case(args: list[str]) -> None:
    command = [sys.executable, str(SCRIPT), *args]
    print('Running:', ' '.join(args))
    completed = subprocess.run(command, cwd=str(BACKEND_ROOT), text=True, capture_output=True)
    print(completed.stdout)
    if completed.stderr:
        print(completed.stderr)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    print('RSA CMS / Mini-CRM Batch 26 Launch Data Import Loader Smoke Test')
    print('Dry-run validation only. No DynamoDB writes are made by this smoke test.')
    print('')
    run_case(['--all'])
    run_case(['--table', 'products'])
    run_case(['--table', 'contact_us'])
    print('Batch 26 launch data import loader dry-run smoke test PASSED.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
