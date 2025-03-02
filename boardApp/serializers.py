from rest_framework import serializers
from .models import User

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # 비밀번호는 응답에서 제외

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'role']

    def create(self, validated_data):
        """회원가입 시 비밀번호 해싱 후 저장"""
        user = User(
            email=validated_data['email'],
            name=validated_data['name'],
            role=validated_data.get('role', 'user')
        )
        user.set_password(validated_data['password'])  # 비밀번호 해싱 후 저장
        return user
