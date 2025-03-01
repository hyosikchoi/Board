from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.all()
        print(user)
