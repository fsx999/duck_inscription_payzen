# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_xworkflows.models


class Migration(migrations.Migration):

    dependencies = [
        ('duck_inscription', '0002_auto_20150603_1252'),
    ]

    operations = [
        migrations.CreateModel(
            name='MoyenPaiementModel',
            fields=[
                ('type', models.CharField(max_length=3, serialize=False, verbose_name='type paiement', primary_key=True)),
                ('label', models.CharField(max_length=60, verbose_name='label')),
            ],
        ),
        migrations.CreateModel(
            name='PaiementAllModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', django_xworkflows.models.StateField(max_length=16, workflow=django_xworkflows.models._SerializedWorkflow(states=[b'droit_univ', b'choix_demi_annee', b'nb_paiement', b'recapitulatif'], initial_state=b'droit_univ', name=b'PaiementState'))),
                ('nb_paiement_frais', models.IntegerField(default=1, verbose_name='Nombre de paiements pour les frais p\xe9dagogiques')),
                ('etape', models.CharField(default='droit_univ', max_length=20)),
                ('demi_annee', models.BooleanField(default=False)),
                ('moyen_paiement', models.ForeignKey(verbose_name='Votre moyen de paiement :', to='duck_inscription_payzen.MoyenPaiementModel', help_text='Veuillez choisir un moyen de paiement', null=True)),
                ('wish', models.OneToOneField(to='duck_inscription.Wish')),
            ],
            bases=(django_xworkflows.models.WorkflowEnabled, models.Model),
        ),
        migrations.CreateModel(
            name='PaiementStateLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transition', models.CharField(max_length=255, verbose_name='transition', db_index=True)),
                ('from_state', models.CharField(max_length=255, verbose_name='from state', db_index=True)),
                ('to_state', models.CharField(max_length=255, verbose_name='to state', db_index=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='performed at', db_index=True)),
                ('paiement', models.ForeignKey(related_name='log_paiement', to='duck_inscription_payzen.PaiementAllModel')),
            ],
            options={
                'ordering': ('-timestamp', 'transition'),
                'abstract': False,
                'verbose_name': 'XWorkflow transition log',
                'verbose_name_plural': 'XWorkflow transition logs',
            },
        ),
        migrations.CreateModel(
            name='TypePaiementModel',
            fields=[
                ('type', models.CharField(max_length=5, serialize=False, verbose_name='type de frais', primary_key=True)),
                ('label', models.CharField(max_length=40, verbose_name='label')),
            ],
        ),
    ]
