from django.urls import path, include
from rest_framework.routers import DefaultRouter


router_v1 = DefaultRouter()

urlpatterns = [
    path('', include(router_v1.urls)),
    # Djoser создаст набор необходимых эндпоинтов.
    # базовые, для управления пользователями в Django:
    # path('auth/', include('djoser.urls')),
    # JWT-эндпоинты, для управления JWT-токенами:
    # path('v1/', include('djoser.urls.jwt')),
]
