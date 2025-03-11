from datetime import datetime

import jwt
from django.db.migrations import serializer
from django.db.models import Prefetch, Count, F, Value, Subquery, Sum
from django.forms.models import model_to_dict
from django.shortcuts import render
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_serializer
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import AllowAny

# Create your views here.
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .serializers import UserSignupSerializer, CommentSerializer, StatisticsSerializer, UserLoginSerializer, \
    UserTokenSerializer
from django.shortcuts import get_object_or_404
from .models import User, Comment

from rest_framework.response import Response
from rest_framework import status, mixins, viewsets, permissions
from .models import Post
from .serializers import PostSerializer


# 회원 가입
class SignupView(APIView):
    """회원가입 API"""

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # 이 시점에서 serializer 의 create 메서드 호출
            return Response({"message": "회원가입 성공", "user_id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 로그인
class LoginViewSet(viewsets.GenericViewSet):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserLoginSerializer,
        responses={201: UserTokenSerializer},
        methods=["POST"]
    )
    def create(self, request):
        login_serializer = UserLoginSerializer(data=request.data)
        if login_serializer.is_valid():
            user = login_serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            token_serializer = UserTokenSerializer(
                instance={
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh)
                }
            )

            return Response(token_serializer.data, status=status.HTTP_200_OK)

        return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 게시글 관련
class PostListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = PostSerializer
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self):
        if self.action in ['update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        comment_prefetch = Prefetch(
            'comments',
            queryset=Comment.objects.select_related('author').order_by('-created_at'),
        )

        return Post.objects.select_related('author').prefetch_related(comment_prefetch).all().order_by('-created_at')

    @extend_schema_serializer(
        exclude_fields=('comments',)
    )
    def update(self, request, *args, **kwargs):
        # auth_header = request.headers.get('Authorization')
        # if not auth_header or not auth_header.startswith('Bearer'):
        #     return Response(status=status.HTTP_401_UNAUTHORIZED)
        #
        # token = auth_header.split(' ')[1]  # Bearer 토큰 가져오기
        # decoded_token = AccessToken(token)  # access token 파싱하기
        #
        # exp_timestamp = decoded_token['exp']  # 만료기간
        #
        # if datetime.now().timestamp() > exp_timestamp:
        #     return Response(data={'detail': 'Token expired'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = request.user.id
        pk = self.kwargs['pk']
        post = get_object_or_raise(model=Post, pk=pk, user_id=user_id)
        update_title = request.data.get('title')
        update_content = request.data.get('content')

        post.title = update_title
        post.content = update_content
        post.updated_at = timezone.now()

        # 기존 Post 객체를 업데이트할 serializer 생성
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            # auth_header = request.headers.get('Authorization')
            # if not auth_header or not auth_header.startswith('Bearer'):
            #     return Response(status=status.HTTP_401_UNAUTHORIZED)
            #
            # token = auth_header.split(' ')[1]  # Bearer 토큰 가져오기
            # decoded_token = AccessToken(token)  # access token 파싱하기
            #
            # exp_timestamp = decoded_token['exp']  # 만료기간
            #
            # if datetime.now().timestamp() > exp_timestamp:
            #     return Response(data={'detail': 'Token expired'}, status=status.HTTP_401_UNAUTHORIZED)

            user_id = request.user.id
            pk = self.kwargs['pk']  # pathvariable 에서 게시글 번호 가져오기
            post = get_object_or_raise(model=Post, pk=pk, user_id=user_id)
            post.delete()  # 게시글 삭제
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Post.DoesNotExist:
            return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    # filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    # def get(self, request, *args, **kwargs):
    #     # 모든 게시글 조회
    #     # prefetch 에서 comment 를 단 author 를 표기해야 하므로 comments__author 로 설정한다.
    #     posts = Post.objects.select_related('author').prefetch_related('comments', 'comments__author').all().order_by('-created_at', '-comments__created_at')
    #     # 게시글 목록을 직렬화
    #     serializer = PostSerializer(posts, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path="statistics")
    def get_counts(self, request, pk=None):

        today = timezone.localdate()

        today_post_count = Post.objects.filter(created_at__date=today).order_by('-created_at').all().count()

        today_post_avg = (float(User.objects.all().count()) / float(today_post_count)) if today_post_count > 0 else 0.0

        # values 는 object 를 반환하는게 아닌 원하는 필드만 dictionary 형태로 반환하게 해준다!
        each_user_post = User.objects.annotate(post_count=Count('posts')).values('name', 'post_count').order_by(
            '-post_count').all()

        total_count = Post.objects.aggregate(posts=Sum('id')).get("posts", 0)

        statistics_serializer = StatisticsSerializer(
            instance={
                'today_posts': today_post_count,
                'today_post_avg': today_post_avg,
                'user_posts': each_user_post,
                'total_count': total_count,
            }
        )

        return Response(statistics_serializer.data, status=status.HTTP_200_OK)

    # 수요일
    # drf-spectacular 붙이기
    # 로그인 기능 붙이기 Authorization: Bearer xxxxx
    # delete -> DELETE / update -> PUT 구현 -> 작성자만 가능 /게시글 id/
    # Optional:
    # - 관리자는 모든 글 삭제 수정 가능
    # - 통계기능은 관리가만 조회 가능 (get_count)
    # 테스트 만들어보기


class PostAPIView(APIView):
    def get(self, request, pk, *args, **kwargs):
        try:
            # 게시글 조회
            post = Post.objects.select_related('author').prefetch_related('comments').get(pk=pk)
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class PostCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = PostSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()  # 게시글 생성 시 author를 설정
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid user_id'}, status=status.HTTP_400_BAD_REQUEST)


# def get_post_or_403(pk, user_id):
#     """Post 객체를 가져오고, user_id가 author인지 검증"""
#     post = get_object_or_404(Post, pk=pk)
#
#     if not user_id:
#         return Response({'detail': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
#     if post.author_id != user_id:
#         return Response({'detail': 'Invalid user_id'}, status=status.HTTP_400_BAD_REQUEST)
#
#     return post  # 검증된 Post 객체 반환


def get_object_or_raise(model, pk, user_id, author_field='author_id'):
    """임의의 모델 객체를 가져오고, user_id가 author인지 검증"""
    obj = get_object_or_404(model, pk=pk)

    if not user_id:
        raise ValidationError({'detail': 'user_id is required.'})

    if getattr(obj, author_field) != user_id:
        raise ValidationError({'detail': 'Invalid user_id'})

    return obj  # 검증된 객체 반환


# 댓글 관련
class CommentAPIView(APIView):
    def post(self, request, pk=None, *args, **kwargs):
        user_id = request.data.get('user_id')
        comment = request.data.get('comment')

        user = get_object_or_404(User, pk=user_id)

        serializer = CommentSerializer(data={
            'content': comment,
            'author': user.id,
            'author_email': user.email,
            'post': pk,
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None, comment_id=None, *args, **kwargs):

        try:
            # RestFul 하게 사용하고 싶었지만... user_id 를 header 에 넣을 수가 없음 ㅜㅜ
            user_id = request.data.get('user_id')

            # 현재 로그인한 유저 id 값과 댓글의 author id 값 비교
            comment = get_object_or_raise(model=Comment, pk=comment_id, user_id=user_id)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({'detail': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk=None, comment_id=None, *args, **kwargs):

        try:
            user_id = request.data.get('user_id')

            comment = get_object_or_raise(model=Comment, pk=comment_id, user_id=user_id)

            comment.content = request.data.get('content')
            serializer = CommentSerializer(comment, data=model_to_dict(comment), partial=True)

            if serializer.is_valid():
                serializer.save(updated_at=timezone.now())
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({'detail': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
