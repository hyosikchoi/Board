from django.contrib.auth.views import LoginView
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path, include
from .views import SignupView, LoginViewSet, PostCreateAPIView, PostUpdateAPIView, PostDeleteAPIView, PostAPIView, \
    CommentAPIView, PostListViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = DefaultRouter()

# basename='posts' 을 정의할지 말지는 선택.
# 정의할 시 viewSet에서 query_set 을 지정 안해줘도 괜찮음.
router.register(r'posts', PostListViewSet, basename='posts')
router.register(r'login', LoginViewSet, basename='login')

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),

    path('', include(router.urls)),  # 게시글 리스트

    path('posts/<int:pk>/', PostAPIView.as_view(), name='post-detail'),  # 게시글 디테일

    path('posts/create/', PostCreateAPIView.as_view(), name='post-create'),  # 게시글 생성
    path('posts/<int:pk>/update/', PostUpdateAPIView.as_view(), name='post-update'),  # 게시글 수정
    path('posts/<int:pk>/delete/', PostDeleteAPIView.as_view(), name='post-delete'),  # 게시글 삭제

    path('posts/<int:pk>/comment/', CommentAPIView.as_view(), name='comment-create'),

    path('posts/<int:pk>/comment/<int:comment_id>', CommentAPIView.as_view(), name='comment-ud'),

    # YOUR PATTERNS
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]
