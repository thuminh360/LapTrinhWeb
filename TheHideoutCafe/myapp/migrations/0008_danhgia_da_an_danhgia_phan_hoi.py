# Generated by Django 4.2.8 on 2025-05-22 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_donhang_nguoi_dung_alter_donhang_trang_thai'),
    ]

    operations = [
        migrations.AddField(
            model_name='danhgia',
            name='da_an',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='danhgia',
            name='phan_hoi',
            field=models.TextField(blank=True, null=True),
        ),
    ]
