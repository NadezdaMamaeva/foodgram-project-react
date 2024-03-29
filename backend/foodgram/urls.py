from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.recipes.views import (ComponentViewSet, ComponentUnitViewSet,
                               RecipeViewSet, TagViewSet,)
from api.users.views import CustomUserViewSet, UserSubscribeViewSet

router = DefaultRouter()

router.register('ingredients', ComponentViewSet, basename='ingredients')
router.register('componentunits', ComponentUnitViewSet,
                basename='componentunits')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('users', CustomUserViewSet, basename='users')

router_subscribe = DefaultRouter()

router_subscribe.register('', UserSubscribeViewSet, basename='subscribe')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/users/<int:pk>/subscribe/', include(router_subscribe.urls)),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
