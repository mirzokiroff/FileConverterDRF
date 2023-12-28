import io
import os

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
        # Call the parent perform_create method to save the instance
        instance = serializer.save()

        # Get the uploaded JPG file
        original_file_path = instance.original_file.path

        # Extract the name of the original file without the extension
        original_file_name = os.path.splitext(os.path.basename(original_file_path))[0]

        # Generate the path for the converted PDF file without accessing it
        converted_file_name = f"{original_file_name}.pdf"

        try:
            # Convert JPG to PDF using PIL
            img = Image.open(original_file_path)
            pdf_buffer = io.BytesIO()
            img.save(pdf_buffer, format='PDF', resolution=100.0)

            # Save the converted PDF to the 'converted/' directory
            instance.converted_file.save(converted_file_name, ContentFile(pdf_buffer.getvalue()))
            instance.target_format = "pdf"
            instance.save()

            # Return the response with the converted file
            return Response({"message": "File converted successfully", "converted_file": instance.converted_file.url},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            # If an error occurs during conversion, delete the instance and return an error response
            instance.delete()
            return Response({"error": f"Conversion failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class DownloadFileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, file_id):
        try:
            converted_file = ConvertedFile.objects.get(id=file_id)
            file_path = converted_file.converted_file.path

            # Check if the file exists before attempting to open it
            if not os.path.exists(file_path):
                return HttpResponseNotFound("File not found")

            # Create a FileResponse with the content type 'application/pdf'
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{converted_file.converted_file.name}"'
                return response
        except ConvertedFile.DoesNotExist:
            return HttpResponseNotFound("File not found")
