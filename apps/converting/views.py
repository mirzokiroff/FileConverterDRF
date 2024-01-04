import io
import os

import fitz
import cv2
import numpy as np
import pyheif
from PIL import Image
from django.core.files.base import ContentFile
from django.http import HttpResponseNotFound, HttpResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from converting.models import ConvertedFile
from converting.serializers import ConvertedFileSerializer


class ConvertFileView(CreateAPIView):
    queryset = ConvertedFile.objects.all()
    serializer_class = ConvertedFileSerializer
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()

        original_file_path = instance.original_file.path
        original_file_name, original_file_extension = os.path.splitext(os.path.basename(original_file_path))
        converted_file_name = f"{original_file_name}.{instance.target_format.lower()}"
        original_format = instance.original_file.name.split('.')[-1].lower()

        try:
            if instance.target_format in ['jpg', 'jpeg'] and original_format in ['jpeg', 'jpg']:
                # JPG yoki JPEG formatidan JPEG yoki JPG formatiga o'tkazish
                # Convert JPG or JPEG to JPEG or JPG
                img = Image.open(original_file_path)
                jpg_buffer = io.BytesIO()
                img.save(jpg_buffer, format='jpeg', resolution=100.0)
                instance.converted_file.save(converted_file_name, ContentFile(jpg_buffer.getvalue()))
            elif instance.target_format in ['jpg', 'jpeg', 'png'] and original_format == 'png':
                # PNG formatida JPG yoki JPEG formatiga o'tkazish
                # Convert PNG to JPG or JPEG

                png_image = Image.open(original_file_path)

                jpg_buffer = io.BytesIO()
                png_image.convert("RGB").save(jpg_buffer, format="JPEG", quality=100)
                instance.converted_file.save(converted_file_name, ContentFile(jpg_buffer.getvalue()))
            elif instance.target_format == 'png' and original_format in ['jpg', 'jpeg', 'png']:
                # JPG va JPEG formatidan PNG formatiga o'tkazish
                # Convert JPG or JPEG to PNG
                image = Image.open(original_file_path)
                png_buffer = io.BytesIO()
                image.save(png_buffer, format='PNG', resolution=100.0)
                instance.converted_file.save(converted_file_name, ContentFile(png_buffer.getvalue()))
            elif instance.target_format in ['jpg', 'jpeg', 'png', 'pdf'] and original_format == 'pdf':
                # PDF formatidan JPG yoki JPEG yoki PNG formatiga o'tkazish
                # Convert PDF to JPG or JPEG or PNG
                pdf_document = fitz.open(instance.original_file.path)  # noqa
                pdf_page = pdf_document[0]

                pdf_image = pdf_page.get_pixmap()

                pil_image = Image.frombytes("RGB", [pdf_image.width, pdf_image.height], pdf_image.samples)  # noqa

                jpg_buffer = io.BytesIO()
                pil_image.save(jpg_buffer, format="JPEG", quality=100)

                instance.converted_file.save(converted_file_name, ContentFile(jpg_buffer.getvalue()))
            elif instance.target_format == 'pdf' and original_format in ['jpg', 'jpeg', 'png', 'pdf']:
                # JPG yoki JPEG yoki PNG formatidan PDF formatiga o'tkazish
                # Convert JPG or JPEG or PNG to PDF
                image = Image.open(original_file_path)

                pdf_buffer = io.BytesIO()
                image.save(pdf_buffer, format='PDF', resolution=100.0)
                instance.converted_file.save(converted_file_name, ContentFile(pdf_buffer.getvalue()))

                instance.save()
            return Response({"message": "File converted successfully", "converted_file": instance.converted_file.url},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            instance.delete()
            return Response({"error": f"Conversion failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class DownloadFileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, file_id):  # noqa
        try:
            converted_file = ConvertedFile.objects.get(id=file_id)
            file_path = converted_file.converted_file.path

            if not os.path.exists(file_path):
                return HttpResponseNotFound("File not found")

            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{converted_file.converted_file.name}"'
                return response
        except ConvertedFile.DoesNotExist:
            return HttpResponseNotFound("File not found")
