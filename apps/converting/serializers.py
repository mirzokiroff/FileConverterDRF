from rest_framework.fields import HiddenField, CurrentUserDefault, CharField
from rest_framework.serializers import ModelSerializer

from .models import ConvertedFile


class ConvertedFileSerializer(ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = ConvertedFile
        fields = '__all__'
        read_only_fields = ('id', 'converted_file', 'target_format')
