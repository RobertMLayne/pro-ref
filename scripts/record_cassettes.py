#!/usr/bin/env python
from __future__ import annotations

import os
import subprocess
import sys


os.environ.setdefault("VCR_MODE", "all")

try:
    subprocess.run([sys.executable, "-m", "pytest", "-q"], check=True)
except subprocess.CalledProcessError as exc:
    sys.exit(exc.returncode)
