from django.conf import settings
import json

def run():
    print("STATICFILES_DIRS:", settings.STATICFILES_DIRS)
    print("STATIC_ROOT:", settings.STATIC_ROOT)
    print("TEMPLATES DIRS:", settings.TEMPLATES[0]['DIRS'])
    print("INSTALLED_APPS:", settings.INSTALLED_APPS)

run()
