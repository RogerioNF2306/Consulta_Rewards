import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from modulo_links.utils import load_xbox_selectors
except ImportError:
    from config.utils import load_xbox_selectors


def load_config():
    return load_xbox_selectors()
