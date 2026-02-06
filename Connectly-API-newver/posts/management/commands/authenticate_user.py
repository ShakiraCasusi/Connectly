from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate

class Command(BaseCommand):

    help = 'Authenticate a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username to authenticate')
        parser.add_argument('password', type=str, help='The password to authenticate')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        password = kwargs['password']
        
        user = authenticate(username=username, password=password)
        if user is not None:
            self.stdout.write(self.style.SUCCESS("Authentication successful!"))
        else:
            self.stdout.write(self.style.ERROR("Invalid credentials."))
