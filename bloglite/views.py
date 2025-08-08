from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Authorization"])
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API для получения JWT-токена
    """

    pass


@extend_schema(tags=["Authorization"])
class CustomTokenRefreshView(TokenRefreshView):
    """
    API для обновления JWT-токена
    """

    pass
