# Generated by Django 5.1.5 on 2025-02-05 02:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WEB', '0003_vigenciaplan'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comuna',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Provincia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='registroempresas',
            name='comuna',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='WEB.comuna'),
        ),
        migrations.AddField(
            model_name='comuna',
            name='provincia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='WEB.provincia'),
        ),
        migrations.AlterField(
            model_name='registroempresas',
            name='provincia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='WEB.provincia'),
        ),
        migrations.AddField(
            model_name='provincia',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='WEB.region'),
        ),
        migrations.AlterField(
            model_name='registroempresas',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='WEB.region'),
        ),
    ]
