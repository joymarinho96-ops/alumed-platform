import os
import sys

# Ensure root directory is on python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alumed.wsgi import app
