from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer


# хелпер для установки куки
def set_jwt_cookies(response, user):
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    access_lifetime = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
    refresh_lifetime = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())

    # False при DEBUG = True, чтобы работало по http
    secure = not settings.DEBUG

    response.set_cookie(
        'access_token', str(access),
        httponly=True, secure=secure, samesite='Lax',
        max_age=access_lifetime,
    )
    response.set_cookie(
        'refresh_token', str(refresh),
        httponly=True, secure=secure, samesite='Lax',
        max_age=refresh_lifetime,
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        response = Response(
            {'id': user.id, 'username': user.username, 'email': user.email},
            status=status.HTTP_201_CREATED,
        )
        # сразу логин при успешной регистрации
        set_jwt_cookies(response, user)
        return response


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'detail': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response(
            {'detail': 'Login successful.', 'username': user.username},
            status=status.HTTP_200_OK,
        )
        set_jwt_cookies(response, user)
        return response


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token not found.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
        except TokenError:
            return Response(
                {'detail': 'Invalid or expired refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access = str(refresh.access_token)
        access_lifetime = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())

        response = Response({'detail': 'Token refreshed.'}, status=status.HTTP_200_OK)
        response.set_cookie(
            'access_token', access,
            httponly=True, secure=not settings.DEBUG, samesite='Lax',
            max_age=access_lifetime,
        )

        # Если включена ротация — вернём новый refresh и заблэклистим старый
        if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS'):
            try:
                refresh.blacklist()
                new_refresh = RefreshToken.for_user(refresh.user)
                refresh_lifetime = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
                response.set_cookie(
                    'refresh_token', str(new_refresh),
                    httponly=True, secure=not settings.DEBUG, samesite='Lax',
                    max_age=refresh_lifetime,
                )
            except Exception:
                # старый refresh уже в blacklist или user удалён — не критично
                pass

        return response


# ---------- Logout ----------

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass   # уже в blacklist или невалидный — не важно

        response = Response({'detail': 'Logged out.'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response