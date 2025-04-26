from django.urls import path
from .views import redirect_to_recipe


urlpatterns = [
    path("s/<slug:urn>/", redirect_to_recipe, name="shortlink-redirect"),
]
