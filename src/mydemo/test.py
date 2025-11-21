import os
from pathlib import Path
getcwd = os.getcwd()
print(f"getcwd: {getcwd}")
parent = Path(getcwd).parent
print(f"parent: {parent}")

join = os.path.join(parent, "libs/stealth.min.js")
print(f"join: {join}")