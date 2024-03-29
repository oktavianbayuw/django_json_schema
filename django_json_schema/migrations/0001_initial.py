# Generated by Django 4.2.9 on 2024-01-03 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JsonValidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_path', models.CharField(max_length=200)),
                ('json_string', models.JSONField()),
                ('json_schema', models.TextField()),
                ('dt_insert', models.DateTimeField(auto_now_add=True)),
                ('dt_modified', models.DateTimeField(auto_now_add=True)),
                ('status', models.SmallIntegerField()),
            ],
        ),
    ]
