"""Offline workflow and optional Windows signing regressions."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import re
import runpy
import shlex
import shutil
import subprocess
import sys
from types import ModuleType
from typing import Any
import xml.etree.ElementTree as ET

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
POWERSHELL = shutil.which('pwsh')
SIGN_SCRIPT = ROOT / 'scripts' / 'sign_windows.ps1'


def workflow(name: str) -> dict[str, Any]:
    """Read workflow mappings without YAML 1.1 coercing the `on` key."""
    path = ROOT / '.github' / 'workflows' / name
    return yaml.load(path.read_text(encoding='utf-8'), Loader=yaml.BaseLoader)


def test_signing_secrets_do_not_enter_conditions_or_script_source() -> None:
    """Secrets must reach PowerShell as data rather than expression source."""
    steps = workflow('windows_installer.yml')['jobs']['build-msi']['steps']
    for step in steps:
        assert 'secrets.' not in step.get('if', '')
        assert 'secrets.' not in step.get('run', '')
    signing = next(step for step in steps if step.get('name') ==
                   'Code sign (optional)')
    assert signing['env']['WINDOWS_CERT_PFX'] == (
        '${{ secrets.WINDOWS_CERT_PFX }}'
    )
    assert signing['env']['WINDOWS_CERT_PWD'] == (
        '${{ secrets.WINDOWS_CERT_PWD }}'
    )


@pytest.mark.parametrize('name', ['ci.yml', 'windows_installer.yml'])
def test_packaging_uses_absolute_import_entry_and_module_resources(
    name: str,
) -> None:
    """Bundle the real launcher and data beside the frozen api_gui package."""
    jobs = workflow(name)['jobs']
    steps = [step for job in jobs.values() for step in job['steps']]
    command = next(step['run'] for step in steps
                   if 'pyinstaller ' in step.get('run', ''))
    arguments = shlex.split(command)
    assert arguments[-1] == 'run.py'
    assert (ROOT / arguments[-1]).is_file()
    assert arguments[arguments.index('--paths') + 1] == 'src'
    source, destination = arguments[
        arguments.index('--add-data') + 1
    ].split(':')
    assert destination == 'api_gui'
    assert (ROOT / source / 'providers').is_dir()
    assert (ROOT / source / 'schemas').is_dir()
    assert (ROOT / source / 'export').is_dir()


def test_msi_keeps_executable_and_artifact_names() -> None:
    """The repaired pipeline must still upload the MSI for pro-ref.exe."""
    steps = workflow('windows_installer.yml')['jobs']['build-msi']['steps']
    build = next(step for step in steps if step.get('name') ==
                 'Build MSI with WiX')
    xml = re.search(r'<Wix\b.*?</Wix>', build['run'], re.DOTALL)
    assert xml is not None
    product = ET.fromstring(xml.group())
    file = product.find('.//{http://schemas.microsoft.com/wix/2006/wi}File')
    assert file is not None
    assert file.attrib['Source'] == r'dist\pro-ref.exe'
    upload = next(step for step in steps if step.get('name') == 'Upload MSI')
    assert upload['with']['name'] == 'pro-ref-msi'
    assert upload['with']['path'] == 'pro-ref.msi'


def test_launcher_calls_application_with_absolute_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Run the packaging launcher without creating a GUI or user settings."""
    called: list[str] = []
    application = ModuleType('api_gui.gui.app')
    setattr(application, 'main', lambda: called.append('main'))
    monkeypatch.setitem(sys.modules, 'api_gui.gui.app', application)
    runpy.run_path(str(ROOT / 'run.py'), run_name='__main__')
    assert called == ['main']


@pytest.mark.skipif(POWERSHELL is None, reason='PowerShell is unavailable')
def test_installer_powershell_parses(tmp_path: Path) -> None:
    """Parse every Windows run block and the signing helper natively."""
    steps = workflow('windows_installer.yml')['jobs']['build-msi']['steps']
    sources = [step['run'] for step in steps if 'run' in step]
    sources.append(SIGN_SCRIPT.read_text(encoding='utf-8'))
    for index, source in enumerate(sources):
        path = tmp_path / f'block-{index}.ps1'
        path.write_text(source, encoding='utf-8')
        command = (
            '$tokens=$null; $errors=$null; '
            '[System.Management.Automation.Language.Parser]::ParseFile('
            '$env:SCRIPT_TO_PARSE,[ref]$tokens,[ref]$errors) > $null; '
            'if ($errors.Count) { $errors | ForEach-Object { '
            'Write-Error $_.Message }; exit 1 }'
        )
        result = subprocess.run(
            [str(POWERSHELL), '-NoProfile', '-Command', command],
            env={**os.environ, 'SCRIPT_TO_PARSE': str(path)},
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr


@pytest.mark.skipif(POWERSHELL is None, reason='PowerShell is unavailable')
def test_absent_certificate_skips_before_signer_or_file_access(
    tmp_path: Path,
) -> None:
    """An unsigned run succeeds without touching a signer or certificate."""
    result = subprocess.run(
        [str(POWERSHELL), '-NoProfile', '-File', str(SIGN_SCRIPT),
         '-SignToolPath', str(tmp_path / 'missing-signer.exe')],
        env={**os.environ, 'WINDOWS_CERT_PFX': '',
             'WINDOWS_CERT_PWD': '', 'RUNNER_TEMP': str(tmp_path)},
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert not list(tmp_path.iterdir())


@pytest.mark.skipif(POWERSHELL is None, reason='PowerShell is unavailable')
@pytest.mark.parametrize('signer_exit', [0, 23])
def test_signer_receives_literal_password_and_certificate_is_cleaned(
    tmp_path: Path, signer_exit: int,
) -> None:
    """Both successful and failed signing retain arguments and remove PFX."""
    signer = tmp_path / 'fake signer.ps1'
    trace = tmp_path / 'trace.json'
    signer.write_text(
        '[ordered]@{ arguments=@($args); '
        'certificate=[Convert]::ToBase64String('
        '[IO.File]::ReadAllBytes($args[2])) } | ConvertTo-Json -Depth 3 | '
        'Set-Content -LiteralPath $env:SYNTHETIC_SIGN_TRACE; '
        'exit ([int]$env:SYNTHETIC_SIGN_EXIT)',
        encoding='utf-8',
    )
    certificate = base64.b64encode(b'synthetic certificate').decode('ascii')
    password = 'literal quote\' $(throw "must remain data")'
    result = subprocess.run(
        [str(POWERSHELL), '-NoProfile', '-File', str(SIGN_SCRIPT),
         '-ArtifactPath', 'artifact with spaces.msi',
         '-SignToolPath', str(signer)],
        env={**os.environ, 'WINDOWS_CERT_PFX': certificate,
             'WINDOWS_CERT_PWD': password, 'RUNNER_TEMP': str(tmp_path),
             'SYNTHETIC_SIGN_TRACE': str(trace),
             'SYNTHETIC_SIGN_EXIT': str(signer_exit)},
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert (result.returncode == 0) == (signer_exit == 0), result.stderr
    recorded = json.loads(trace.read_text(encoding='utf-8-sig'))
    assert recorded['certificate'] == certificate
    assert recorded['arguments'][4] == password
    assert recorded['arguments'][-1] == 'artifact with spaces.msi'
    assert not list(tmp_path.glob('*.pfx'))
