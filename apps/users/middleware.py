from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

# достаёт access-токен из cookie и подкладывает в Authorization header
# если access истёк — автоматически обновляет через refresh и пишет новый в cookie
class JWTCookieMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        new_access_token = None
        should_clear = False

        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if access_token:
            try:
                AccessToken(access_token)
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            except TokenError:
                if refresh_token:
                    try:
                        refresh = RefreshToken(refresh_token)
                        new_access_token = str(refresh.access_token)
                        request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_access_token}'
                        request._new_access_token = new_access_token
                    except TokenError:
                        should_clear = True
                else:
                    should_clear = True

        response = self.get_response(request)

        # обновлённый access кладется в cookie
        if new_access_token:
            response.set_cookie(
                'access_token', new_access_token,
                httponly=True, secure=False, samesite='Lax',
                max_age=15 * 60,
            )

        if should_clear:
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

        return response