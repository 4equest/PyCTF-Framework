from .workspace import *
from .manager import *

import os

WORKSPACE_DIR = "workspace"

if not os.path.isdir(WORKSPACE_DIR):
    os.mkdir(WORKSPACE_DIR)