import subprocess
import sys

from daemon.daemon import DaemonContext


daemon = DaemonContext(stderr=sys.stderr)
daemon.open()
subprocess.call([
    'python3', '-c',
    'import sys; import os; print(os.stat(1), file=sys.stderr)',
])
