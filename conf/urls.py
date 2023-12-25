from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="File Converter DRF 🅐🅟🅘 𝐦.𝐦𝐢𝐫𝐳𝐨𝐤𝐢𝐫𝐨𝐟𝐟",
        default_version='𝟽𝟽𝟽',
        description="File Converter - it helps you to convert your file from any format to any type of format",
    ),
    public=True,
    permission_classes=[AllowAny],
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.urls')),
]

if settings.DEBUG:
    urlpatterns += ([
            path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                     document_root=settings.MEDIA_ROOT))
