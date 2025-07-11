# Generated by Django 5.2.4 on 2025-07-06 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detection', '0002_userprofile_points_alter_userprofile_langue_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imageupload',
            name='avg_b',
        ),
        migrations.RemoveField(
            model_name='imageupload',
            name='avg_g',
        ),
        migrations.RemoveField(
            model_name='imageupload',
            name='avg_r',
        ),
        migrations.RemoveField(
            model_name='imageupload',
            name='contours',
        ),
        migrations.RemoveField(
            model_name='imageupload',
            name='contrast',
        ),
        migrations.RemoveField(
            model_name='imageupload',
            name='file_size_kb',
        ),
        migrations.RemoveField(
            model_name='imageupload',
            name='height',
        ),
        migrations.RemoveField(
            model_name='imageupload',
            name='width',
        ),
        migrations.AddField(
            model_name='imageupload',
            name='chemin',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='imageupload',
            name='date_csv',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='imageupload',
            name='hauteur',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='imageupload',
            name='largeur',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='imageupload',
            name='pixels',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='imageupload',
            name='taille',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='imageupload',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
