from rest_framework.serializers import ModelSerializer

from .models import ConvertedFile


class ConvertedFileSerializer(ModelSerializer):

    class Meta:
        model = ConvertedFile
        fields = '__all__'
        read_only_fields = ('id', 'converted_file')
