# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-11-04 15:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting_tools', '0002_auto_20201104_1311-4'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashbook',
            name='name',
            field=models.CharField(default=b'---', max_length=255, verbose_name='Titre du journal de caisse'),
        ),
        migrations.AlterField(
            model_name='expenseclaim',
            name='name',
            field=models.CharField(default=b'---', max_length=255, verbose_name='Titre de la note de frais'),
        ),
        migrations.AlterField(
            model_name='financialprovider',
            name='name',
            field=models.CharField(default=b'---', max_length=255, verbose_name='Nom du fournisseur'),
        ),
        migrations.AlterField(
            model_name='internaltransfer',
            name='name',
            field=models.CharField(default=b'---', max_length=255, verbose_name='Raison du transfert'),
        ),
        migrations.AlterField(
            model_name='providerinvoice',
            name='name',
            field=models.CharField(default=b'---', max_length=255, verbose_name='Titre de la facture fournisseur'),
        ),
        migrations.AlterField(
            model_name='subvention',
            name='name',
            field=models.CharField(default=b'---', max_length=255, verbose_name='Nom du projet'),
        ),
        migrations.AlterField(
            model_name='subventionline',
            name='name',
            field=models.CharField(default=b'---', max_length=255, verbose_name="Nom de l'\xe9v\xe8nement"),
        ),
        migrations.AlterField(
            model_name='withdrawal',
            name='name',
            field=models.CharField(default=b'---', max_length=255, verbose_name='Raison du retrait'),
        ),
    ]