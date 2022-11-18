import os

DEBUG = False

if DEBUG:
    os.environ['DINGDING_TOKEN'] = '11eebb3f55367d4e7a5deb61603906414b2ce841dd976cd0754e798437d1bb22'
    os.environ['DINGDING_SECRET'] = '1232add7289aa9a2b5049e4bd428be0085b88456209fb8d70be7569e5589b51aa12'
    

ROBOT_TOKEN = os.environ.get('DINGDING_TOKEN', None)
ROBOT_SECRET = os.environ.get('DINGDING_SECRET', None)

TEMPLATE_PATH = os.path.abspath(os.path.dirname(__file__))