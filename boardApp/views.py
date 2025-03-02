from django.shortcuts import render
from django.utils import timezone

# Create your views here.
from rest_framework.views import APIView
from .serializers import UserSignupSerializer
from django.shortcuts import get_object_or_404
from .models import User

from rest_framework.response import Response
from rest_framework import status
from .models import Post
from .serializers import PostSerializer


class SignupView(APIView):
    """회원가입 API"""

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save() # 이 시점에서 serializer 의 create 메서드 호출
            return Response({"message": "회원가입 성공", "user_id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """로그인 API"""
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = get_object_or_404(User, email=email)  # 이메일로 사용자 찾기
        if not user.check_password(password):  # 비밀번호 검증
            return Response({"error": "이메일 또는 비밀번호가 올바르지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"message": "로그인 성공", "User": user.id}, status=status.HTTP_200_OK)

class PostListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # 모든 게시글 조회
        posts = Post.objects.all().order_by('-created_at')
        # 게시글 목록을 직렬화
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostAPIView(APIView):
    def get(self, request, pk, *args, **kwargs):

        try:
            # 게시글 조회
            post = Post.objects.get(pk=pk)
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class PostCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')  # 요청 본문에서 user_id를 가져옴
        try:
            user = User.objects.get(id=user_id)  # user_id로 User 객체를 찾음
            # Post 객체를 생성하는 serializer 생성
            serializer = PostSerializer(
                data={
                    'title': request.data.get('title'),
                    'content': request.data.get('content'),
                    'author': user.id,
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()  # 게시글 생성 시 author를 설정
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid user_id'}, status=status.HTTP_400_BAD_REQUEST)


def get_post_or_403(pk, user_id):
    """Post 객체를 가져오고, user_id가 author인지 검증"""
    post = get_object_or_404(Post, pk=pk)

    if not user_id:
        return Response({'detail': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if post.author_id != user_id:
        return Response({'detail': 'Invalid user_id'}, status=status.HTTP_400_BAD_REQUEST)

    return post  # 검증된 Post 객체 반환

class PostUpdateAPIView(APIView):
    def put(self, request, pk=None, *args, **kwargs):
        try:
            user_id = request.data.get('user_id')
            post_or_response = get_post_or_403(pk=pk, user_id=user_id)

            if isinstance(post_or_response, Response):
                return post_or_response # 에러 응답 반환

            post = post_or_response

            update_title = request.data.get('title')
            update_content = request.data.get('content')

            post.title = update_title
            post.content = update_content
            post.updated_at = timezone.now()
            # 기존 Post 객체를 업데이트할 serializer 생성
            serializer = PostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)


class PostDeleteAPIView(APIView):
    def delete(self, request, pk=None, *args, **kwargs):
        try:
            user_id = request.data.get('user_id')
            post_or_response = get_post_or_403(pk=pk, user_id=user_id)
            if isinstance(post_or_response, Response):
                return post_or_response
            post_or_response.delete()  # 게시글 삭제
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
