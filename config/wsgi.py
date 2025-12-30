import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ops_system.settings')

application = get_wsgi_application()

# 🚨 DEBUG PRINT
print("🔥 WSGI LOADED")

if os.getenv("CREATE_ADMIN") == "1":
    print("🔥 CREATE_ADMIN detected")
    from django.core.management import call_command
    call_command("create_admin")
