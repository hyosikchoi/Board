from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSignupSerializer
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from .models import User

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
