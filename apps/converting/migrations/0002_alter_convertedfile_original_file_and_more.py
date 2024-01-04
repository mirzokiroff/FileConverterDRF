# Generated by Django 5.0 on 2024-01-04 11:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('converting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='convertedfile',
            name='original_file',
            field=models.FileField(upload_to='uploads/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'pdf', 'png'])]),
        ),
        migrations.AlterField(
            model_name='convertedfile',
            name='target_format',
            field=models.CharField(choices=[('jpg', 'JPG'), ('pdf', 'PDF'), ('png', 'PNG'), ('jpeg', 'JPEG')], max_length=50),
        ),
    ]