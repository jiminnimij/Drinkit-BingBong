from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.validators import UniqueValidator
from .models import Mypage, Timer


User = get_user_model()

# 회원가입 시리얼라이저
class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password": "비밀번호가 일치하지 않습니다."}
            )
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user

# 로그인 시리얼라이저
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if user:
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        raise serializers.ValidationError(
            {"error": "일치하는 회원 정보가 없습니다."}
        )

# 마이페이지 시리얼라이저
class MypageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mypage
        fields = ("nickname", "image", "friends")

# 비밀번호 변경 시리얼라이저
class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password": "새 비밀번호가 일치하지 않습니다."})
        return data
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class TimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timer
        fields = ['time_left', 'is_running', 'start_time']