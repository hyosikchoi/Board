
from django.core.management import BaseCommand
from django.db.models import F, Subquery, Count, Sum, Q
from django.views.decorators.http import condition
from rest_framework.generics import get_object_or_404

from boardApp.models import User, Post, Comment


class Command(BaseCommand):
    def handle(self, *args, **options):
        # query = Comment.objects.select_related('author').order_by('-created_at')
        query2 = Post.objects.prefetch_related('comments', 'comments__author').order_by('-created_at')
        print(query2)
        # posts = Post.objects.select_related('author').prefetch_related('comments').all().order_by('-created_at')
        # posts = Post.objects.select_related("comment").filter(start__lt=today()).aggregate(_sum=Sum(F("comment__price"))).
        #
        # condition = Q(title="aaa")
        # condition &= Q(content='bbb')
        #
        # condition_2 = Q(title="ccc")
        # if ddd
        #     condition_2 &= Q(content='ddd')
        # else
        #     condition_2 &= Q(content='xxx')
        #
        # condition |= condition_2
        #
        #
        # queryset = Post.objects.exclude(title="aaa", content='bbb', content='bbb', content='bbb')
        #
        # a = queryset.exclude(content='bbb')
        #
        #
        #
        # return {"_sum": Sum("comment__price")}.get("_sum", 0)
