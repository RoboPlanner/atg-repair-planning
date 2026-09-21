"""Run archive verification and current implementation/source-check regressions."""
from pathlib import Path
import subprocess, sys
from verify_archive import verify

ROOT = Path(__file__).resolve().parents[1]
verify()
for directory, args in [
    (ROOT/'reproduction/implementation_v7_70', ['discover', '-s', 'tests', '-v']),
    (ROOT/'reproduction', ['test_external_reference', '-v']),
]:
    subprocess.run([sys.executable, '-X', 'utf8', '-m', 'unittest', *args], cwd=directory, check=True)
print('PASS: current implementation and independent public-source checker tests.')
