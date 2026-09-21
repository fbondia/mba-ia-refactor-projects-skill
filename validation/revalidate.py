"""Reproduce tests, syntax checks and localhost boot with temporary databases."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ('code-smells-project', 'ecommerce-api-legacy', 'task-manager-api')


def run(command, cwd, env):
    result = subprocess.run(command, cwd=cwd, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    return result.returncode, '$ ' + ' '.join(map(str, command)) + '\n' + result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', default=shutil.which('node'))
    args = parser.parse_args()
    if not args.node:
        parser.error('Node.js 18–22 is required')
    node = str(Path(args.node).resolve())
    version = subprocess.check_output([node, '--version'], text=True).strip()
    if not 18 <= int(version.split('.')[0][1:]) < 23:
        parser.error('Use --node with Node.js >=18 <23, as declared in package.json')
    env = {**os.environ, 'SECRET_KEY': 'test-secret-not-for-production',
           'ADMIN_TOKEN': 'test-admin-token', 'FLASK_DEBUG': 'false'}
    stamp = datetime.now(timezone.utc).isoformat()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    header = f'Validation UTC: {stamp}\nBase commit: {revision}; working tree under review\n'
    for index, project in enumerate(PROJECTS, 1):
        folder = ROOT / project
        if index == 2:
            commands = [[node, '--version'], [node, '--test', 'tests/checkout.test.js']]
            commands += [[node, '--check', str(p.relative_to(folder))]
                         for area in ('src', 'tests') for p in sorted((folder / area).rglob('*.js'))]
        else:
            python = str(folder / '.venv/bin/python')
            commands = [[python, '--version'],
                        [python, '-W', 'error::DeprecationWarning', '-m', 'unittest',
                         'discover', '-s', 'tests', '-v']]
            files = [str(p.relative_to(folder)) for p in folder.rglob('*.py')
                     if not any(part.startswith('.') for part in p.relative_to(folder).parts)]
            commands.append([python, '-m', 'compileall', '-q', *sorted(files)])
        output = header
        for command in commands:
            code, result = run(command, folder, env)
            output += '\n' + result + f'Exit code: {code}\n'
            (ROOT / 'validation' / f'project-{index}-tests.log').write_text(output)
            if code:
                raise RuntimeError(f'{project}: validation failed; see log')
        print(f'{project}: tests and syntax PASS', flush=True)

    smoke = header
    for index, project in enumerate(PROJECTS, 1):
        folder = ROOT / project
        with tempfile.TemporaryDirectory(prefix='refactor-validation-') as temporary:
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            boot_env = {**env, 'HOST': '127.0.0.1', 'PORT': str(port),
                        'DATABASE_PATH': str(Path(temporary) / 'app.db'),
                        'DATABASE_URL': 'sqlite:///' + str(Path(temporary) / 'tasks.db')}
            command = [node, 'src/app.js'] if index == 2 else [str(folder / '.venv/bin/python'), 'app.py']
            with open(Path(temporary) / 'boot.log', 'w+') as log:
                process = subprocess.Popen(command, cwd=folder, env=boot_env, stdout=log, stderr=log)
                try:
                    path = '/api/admin/financial-report' if index == 2 else '/health'
                    request = urllib.request.Request(f'http://127.0.0.1:{port}{path}',
                                                     headers={'Authorization': 'Bearer test-admin-token'})
                    for attempt in range(100):
                        try:
                            with urllib.request.urlopen(request, timeout=1) as response:
                                status = response.status
                                assert status == 200
                                break
                        except OSError:
                            if process.poll() is not None:
                                raise RuntimeError(f'{project}: boot failed')
                            time.sleep(.1)
                    else:
                        raise RuntimeError(f'{project}: boot timed out')
                    smoke += f'\n{project}: boot PASS; GET {path} -> {status}\n'
                    print(f'{project}: boot/HTTP PASS', flush=True)
                finally:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    log.seek(0)
                    smoke += log.read()
                    (ROOT / 'validation/boot-smoke.log').write_text(smoke)


if __name__ == '__main__':
    main()
