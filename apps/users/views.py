from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.http import Http404
from django.utils.text import slugify
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from conf import settings
from users.models import UserProfile
from users.serializers import UserProfileRetrieveSerializer, RegisterSerializer, EmailVerySerializer, LoginSerializer
from .tasks import send_to_gmail


class IsAuthenticatedAndOwner(BasePermission):
    message = 'You must be the owner of this object.'

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class UserProfileRetrieveView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileRetrieveSerializer
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny, IsAuthenticatedAndOwner]
    http_method_names = ('get', 'patch')

    def get_object(self):
        user = self.request.user
        if user.is_authenticated:
            return user

        username_slug = slugify(self.kwargs['username'])
        try:
            user = UserProfile.objects.get(username=username_slug)
            return user
        except UserProfile.DoesNotExist:
            raise Http404("User does not exist")


class RegisterView(CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if UserProfile.objects.filter(email=data['email']).exists():
            return Response({"ERROR": "This email already exists"}, status.HTTP_400_BAD_REQUEST)

        data['password'] = make_password(data['password'])
        data['confirm_password'] = make_password(data['confirm_password'])

        user = UserProfile(**data)
        send_to_gmail.delay(user.email)
        cache.set(f'user:{user.email}', user, timeout=settings.CACHE_TTL)
        return Response({"status": True, 'user': user.email}, status=201)

    def perform_create(self, serializer):
        instance = serializer.save()
        hashed_password = make_password(instance.password)
        instance.password = hashed_password
        instance.save()


class LoginView(CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny, ]

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        user = authenticate(username=username, password=password, confirm_password=confirm_password)

        if user in UserProfile.objects.all():
            if password == confirm_password:
                refresh_token = RefreshToken.for_user(user)
                return Response({"refresh": str(refresh_token), "access": str(refresh_token.access_token)})  # noqa
            return Response({"ERROR": "The passwords do not match"}, status.HTTP_400_BAD_REQUEST)
        return Response({"ERROR": "Invalid credentials"}, status.HTTP_401_UNAUTHORIZED)


class EmailSignUpView(CreateAPIView):
    serializer_class = EmailVerySerializer

    def post(self, request, *args, **kwargs):
        serializer = EmailVerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.data.get('code')
        if code and (email := cache.get(f'{settings.CACHE_KEY_PREFIX}:{code}')):
            if user := cache.get(f'user:{email}'):
                cache.delete(f'{settings.CACHE_KEY_PREFIX}:{code}')
                cache.delete(f'user:{email}')
                user.save()
                return Response({"message": 'User is successfully activated'})
        return Response({"message": 'Code is expired or invalid'})
