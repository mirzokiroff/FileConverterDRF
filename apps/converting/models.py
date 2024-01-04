from uuid import uuid4

from django.core.validators import FileExtensionValidator
from django.db.models import Model, FileField, CharField
from django.db.models.signals import pre_save
from django.dispatch import receiver


class ConvertedFile(Model):
    id = CharField(max_length=111, primary_key=True)
    original_file = FileField(upload_to='uploads/', validators=[
        FileExtensionValidator(
            ['jpg', 'jpeg', 'pdf', 'png'])
    ])
    converted_file = FileField(upload_to='converted/')
    target_format = CharField(max_length=50, choices=[
        ('jpg', 'JPG'), ('pdf', 'PDF'), ('png', 'PNG'), ('jpeg', 'JPEG')])


@receiver(pre_save, sender=ConvertedFile)
def generate_unique_id(sender, instance, *args, **kwargs):
    if not instance.id:
        instance.id = str(uuid4()).split('-')[-1]
