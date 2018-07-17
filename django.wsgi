import os
import time
import traceback
import signal
import sys

os.environ['PYTHON_EGG_CACHE'] = '/tmp'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crits.settings')

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
from django.core.wsgi import get_wsgi_application
try:
    application = get_wsgi_application()
except Exception:
    if 'mod_wsgi' in sys.modules:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)
