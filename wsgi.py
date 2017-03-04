import os, sys

sys.path.append('/usr/share/familytree')
sys.path.append('/usr/share/familytree-virtualenv/lib/python3.5/site-packages')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
