import os

ROBOT_TOKEN = os.environ.get('DINGDING_TOKEN', None)
ROBOT_SECRET = os.environ.get('DINGDING_SECRET', None)

TEMPLATE_PATH = os.path.abspath(os.path.dirname(__file__))