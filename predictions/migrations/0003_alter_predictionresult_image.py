# Generated by Django 5.1.3 on 2024-12-05 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictions', '0002_predictionresult_diagnosis_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='predictionresult',
            name='image',
            field=models.ImageField(upload_to='media/analyzed_images/'),
        ),
    ]
