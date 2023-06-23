from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import ComponentViewSet, ComponentUnitViewSet, TagViewSet


router = DefaultRouter()

router.register('components', ComponentViewSet, basename='components')
router.register('componentunits', ComponentUnitViewSet, basename='componentunits')
router.register('tags', TagViewSet, basename='tags')


urlpatterns = [
    path('admin/', admin.site.urls),    
    path('api/', include(router.urls)),
]
