from uuid import uuid4

from django.core.validators import FileExtensionValidator
from django.db.models import Model, FileField, CharField, ForeignKey, CASCADE
from django.db.models.signals import pre_save
from django.dispatch import receiver

from conf import settings


class ConvertedFile(Model):
    id = CharField(max_length=111, primary_key=True)
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='converter_user')
    original_file = FileField(upload_to='uploads/', validators=[
        FileExtensionValidator(
            ['mp4', 'avi', 'mkv', 'mov', '3gp', 'mpg', 'flv', 'ts', 'wmv', 'webm', 'gif', 'jpg', 'heic'])])
    converted_file = FileField(upload_to='converted/')
    target_format = CharField(max_length=50)


@receiver(pre_save, sender=ConvertedFile)
def generate_unique_id(sender, instance, *args, **kwargs):
    if not instance.id:
        instance.id = str(uuid4()).split('-')[-1]
