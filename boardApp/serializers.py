from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Post, Comment


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

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            data['user'] = user
            return data

        raise serializers.ValidationError('Invalid email or password')

class UserTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)


class CommentSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author_email = serializers.EmailField(source='author.email', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_email','content','created_at', 'updated_at']


class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author_email = serializers.EmailField(source='author.email', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True) # serializer 에서 read_only 로 설정 해줘야함.
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'author_email', 'comments', 'created_at', 'updated_at']



class UserPostsSerializer(serializers.Serializer):
    name = serializers.CharField()
    post_count = serializers.IntegerField()


class StatisticsSerializer(serializers.Serializer):
    today_posts = serializers.IntegerField()
    today_post_avg = serializers.FloatField()
    # serializers.ListSerializer(child=UserPostsSerializer()) 이 방법과
    # UserPostsSerializer(many = true) 방법이 있다.
    user_posts = serializers.ListSerializer(child=UserPostsSerializer())
    total_count = serializers.IntegerField()
