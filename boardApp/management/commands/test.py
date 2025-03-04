
from django.core.management import BaseCommand
from rest_framework.generics import get_object_or_404

from boardApp.models import User, Post


class Command(BaseCommand):
    def handle(self, *args, **options):
        posts = Post.objects.select_related('author').prefetch_related('comments').all().order_by('-created_at')
        print(posts)