
from django.core.management import BaseCommand
from rest_framework.generics import get_object_or_404

from boardApp.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = get_object_or_404(User, email='test@example.com')
        print(user.id)
        print(user.name)
