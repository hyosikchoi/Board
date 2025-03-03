from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path, include
from .views import SignupView, LoginView, PostCreateAPIView, PostUpdateAPIView, PostDeleteAPIView, PostListAPIView, \
    PostAPIView, CommentAPIView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),

    path('posts/', PostListAPIView.as_view(), name='post-list'),  # 게시글 리스트

    path('posts/<int:pk>/', PostAPIView.as_view(), name='post-detail'),  # 게시글 디테일

    path('posts/create/', PostCreateAPIView.as_view(), name='post-create'),  # 게시글 생성
    path('posts/<int:pk>/update/', PostUpdateAPIView.as_view(), name='post-update'),  # 게시글 수정
    path('posts/<int:pk>/delete/', PostDeleteAPIView.as_view(), name='post-delete'),  # 게시글 삭제

    path('posts/<int:pk>/comment/', CommentAPIView.as_view(), name='comment-create'),

    path('posts/<int:pk>/comment/<int:comment_id>', CommentAPIView.as_view(), name='comment-ud')

]
