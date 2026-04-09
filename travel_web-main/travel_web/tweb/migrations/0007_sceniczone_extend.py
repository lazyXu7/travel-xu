# Generated migration for ScenicZone extended fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweb', '0006_remove_hotel_tel_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='sceniczone',
            name='SZ_duration',
            field=models.IntegerField(default=3),
        ),
        migrations.AddField(
            model_name='sceniczone',
            name='SZ_latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sceniczone',
            name='SZ_longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sceniczone',
            name='SZ_tags',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
