from django.contrib.auth import get_user_model  
from django.core.management.base import BaseCommand  

User = get_user_model()  

class Command(BaseCommand):  
    def handle(self, *args, **options):  
        username = 'admin'  
        email = 'admin@example.com'  
        try:  
            u = None
            if not User.objects.filter(username=username).exists() and not User.objects.filter(is_superuser=True).exists():  
                print("admin user not found, creating one")  
                password = "admin"
                u = User.objects.create_superuser(username=username, email=email, password=password)  
                print(f"===================================")  
                print(f"A superuser '{username}' was created with email '{email}' and password '{password}'")  
                print(f"===================================")  
            else:  
                print("admin user found. Skipping super user creation")  
            print(u)  
        except Exception as e:  
            print(f"There was an error: {e}")