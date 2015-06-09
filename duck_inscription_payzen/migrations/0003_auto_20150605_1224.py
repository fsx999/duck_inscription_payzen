# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('duck_inscription_payzen', '0002_auto_20150604_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='duckinscriptionpaymentrequest',
            name='paiement',
            field=models.OneToOneField(related_name='paiement_request', to='duck_inscription_payzen.PaiementAllModel'),
        ),
    ]
