from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ConvertFileView, DownloadFileView

router = DefaultRouter()
# router.register('converting', ConvertFileToPdfView, basename='converting'),

urlpatterns = [
    # path('', include(router.urls)),
    path('convert/', ConvertFileView.as_view(), name='file-converter'),
    path('api/v1/user/download/<str:file_id>/', DownloadFileView.as_view(), name='download_file'),
]
