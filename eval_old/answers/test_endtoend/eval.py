import sys
import os
import re

from pathlib import Path

base_path = Path().resolve()
sys.path.append(str(base_path))

import decompose_yaml 
import scoring

decompose_yaml.run()
scoring.run()