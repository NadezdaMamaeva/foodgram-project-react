from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (ComponentViewSet, ComponentUnitViewSet,
                       PrescriptorViewSet, TagViewSet,)
from api.users.views import CustomUserViewSet

router = DefaultRouter()

router.register('ingredients', ComponentViewSet, basename='ingredients')
router.register('componentunits', ComponentUnitViewSet,
                basename='componentunits')
router.register('recipes', PrescriptorViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('users', CustomUserViewSet, basename='users')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
