# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_xworkflows.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('django_payzen', '0004_auto_20141221_2140'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('duck_inscription_payzen', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DuckInscriptionPaymentRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vads_cust_address', models.CharField(max_length=255, null=True, blank=True)),
                ('vads_cust_address_number', models.CharField(max_length=5, null=True, blank=True)),
                ('vads_cust_country', models.CharField(max_length=2, null=True, blank=True)),
                ('vads_cust_email', models.EmailField(max_length=254, null=True, blank=True)),
                ('vads_cust_id', models.CharField(max_length=63, null=True, blank=True)),
                ('vads_cust_name', models.CharField(max_length=127, null=True, blank=True)),
                ('vads_cust_last_name', models.CharField(max_length=63, null=True, blank=True)),
                ('vads_cust_first_name', models.CharField(max_length=63, null=True, blank=True)),
                ('vads_cust_cell_phone', models.CharField(max_length=32, null=True, blank=True)),
                ('vads_cust_phone', models.CharField(max_length=32, null=True, blank=True)),
                ('vads_cust_title', models.CharField(max_length=63, null=True, blank=True)),
                ('vads_cust_city', models.CharField(max_length=63, null=True, blank=True)),
                ('vads_cust_status', models.CharField(max_length=63, null=True, blank=True)),
                ('vads_cust_state', models.CharField(max_length=63, null=True, blank=True)),
                ('vads_cust_zip', models.CharField(max_length=63, null=True, blank=True)),
                ('vads_language', models.CharField(max_length=2, null=True, blank=True)),
                ('vads_order_id', models.CharField(max_length=32, null=True, blank=True)),
                ('vads_order_info', models.CharField(max_length=255, null=True, blank=True)),
                ('vads_order_info2', models.CharField(max_length=255, null=True, blank=True)),
                ('vads_order_info3', models.CharField(max_length=255, null=True, blank=True)),
                ('vads_ship_to_name', models.CharField(max_length=127, null=True, blank=True)),
                ('vads_ship_to_first_name', models.CharField(max_length=63, null=True, blank=True)),
                ('vads_ship_to_last_name', models.CharField(max_length=63, null=True, blank=True)),
                ('vads_ship_to_street_number', models.CharField(max_length=5, null=True, blank=True)),
                ('vads_ship_to_street', models.CharField(max_length=255, null=True, blank=True)),
                ('vads_ship_to_street2', models.CharField(max_length=255, null=True, blank=True)),
                ('vads_ship_to_zip', models.CharField(max_length=63, null=True, blank=True)),
                ('vads_ship_to_city', models.CharField(max_length=63, null=True, blank=True)),
                ('vads_ship_to_country', models.CharField(max_length=2, null=True, blank=True)),
                ('vads_ship_to_phone_num', models.CharField(max_length=32, null=True, blank=True)),
                ('vads_ship_to_state', models.CharField(max_length=255, null=True, blank=True)),
                ('vads_action_mode', models.CharField(default=None, max_length=11, choices=[(b'INTERACTIVE', b'INTERACTIVE'), (b'SILENT', b'SILENT')])),
                ('vads_amount', models.PositiveIntegerField()),
                ('vads_currency', models.CharField(default=None, max_length=3, choices=[(b'036', b'Australian dollar'), (b'124', b'Canadian dollar'), (b'156', b'Chinese Yuan'), (b'208', b'Danish Krone'), (b'392', b'Japanese Yen'), (b'578', b'Norwegian Krone'), (b'752', b'Swedish Krona'), (b'756', b'Swiss franc'), (b'826', b'Pound sterling'), (b'840', b'American dollar'), (b'953', b'Franc Pacifique (CFP)'), (b'978', b'Euro')])),
                ('vads_ctx_mode', models.CharField(default=b'TEST', max_length=10, choices=[(b'TEST', b'TEST'), (b'PRODUCTION', b'PRODUCTION')])),
                ('vads_page_action', models.CharField(default=b'PAYMENT', max_length=7)),
                ('vads_payment_config', models.TextField()),
                ('vads_site_id', models.PositiveIntegerField(default=58163425)),
                ('vads_trans_date', models.CharField(max_length=14)),
                ('vads_trans_id', models.CharField(max_length=6)),
                ('vads_version', models.CharField(default=b'V2', max_length=2)),
                ('signature', models.CharField(max_length=40)),
                ('vads_capture_delay', models.PositiveIntegerField(null=True, blank=True)),
                ('vads_contrib', models.CharField(default=b'django-payzen v1.0', max_length=255, null=True, blank=True)),
                ('vads_payment_cards', models.CharField(max_length=127, null=True, blank=True)),
                ('vads_return_mode', models.CharField(blank=True, max_length=12, null=True, choices=[(b'AMEX', b'American Express'), (b'AURORE-MULTI', b'AURORE (multi brand)'), (b'BUYSTER', b'BUYSTER'), (b'CB', b'CB'), (b'COFINOGA', b'COFINOGA'), (b'E-CARTEBLEUE', b'e blue card'), (b'MASTERCARD', b'Eurocard / MasterCard'), (b'JCB', b'JCB'), (b'MAESTRO', b'Maestro'), (b'ONEY', b'ONEY'), (b'ONEY_SANDBOX', b'ONEY SANDBOX mode'), (b'PAYPAL', b'PAYPAL'), (b'PAYPAL_SB', b'PAYPAL SANDBOX mode'), (b'PAYSAFECARD', b'PAYSAFECARD'), (b'VISA', b'Visa'), (b'VISA_ELECTRON', b'Visa Electron'), (b'COF3XCB', b'3x CB Cofinoga'), (b'COF3XCB_SB', b'3x CB Cofinoga SANDBOX')])),
                ('vads_theme_config', models.CharField(max_length=255, null=True, blank=True)),
                ('vads_validation_mode', models.CharField(blank=True, max_length=1, null=True, choices=[(b'', b'Default shop configuration (using payzen admin)'), (b'0', b'Automatic validation'), (b'1', b'Manual validation')])),
                ('vads_url_success', models.URLField(null=True, blank=True)),
                ('vads_url_referral', models.URLField(null=True, blank=True)),
                ('vads_url_refused', models.URLField(null=True, blank=True)),
                ('vads_url_cancel', models.URLField(null=True, blank=True)),
                ('vads_url_error', models.URLField(null=True, blank=True)),
                ('vads_url_return', models.URLField(null=True, blank=True)),
                ('vads_user_info', models.CharField(max_length=255, null=True, blank=True)),
                ('vads_shop_name', models.CharField(max_length=255, null=True, blank=True)),
                ('vads_redirect_success_timeout', models.PositiveIntegerField(null=True, blank=True)),
                ('vads_redirect_success_message', models.CharField(max_length=255, null=True, blank=True)),
                ('vads_redirect_error_timeout', models.PositiveIntegerField(null=True, blank=True)),
                ('vads_redirect_error_message', models.CharField(max_length=255, null=True, blank=True)),
                ('custom_payment_config', models.ManyToManyField(to='django_payzen.CustomPaymentConfig')),
            ],
            options={
                'verbose_name': 'Request',
            },
        ),
        migrations.RemoveField(
            model_name='paiementallmodel',
            name='etape',
        ),
        migrations.AlterField(
            model_name='paiementallmodel',
            name='state',
            field=django_xworkflows.models.StateField(max_length=16, workflow=django_xworkflows.models._SerializedWorkflow(states=[b'droit_univ', b'choix_demi_annee', b'nb_paiement', b'recapitulatif', b'paiement', b'done'], initial_state=b'droit_univ', name=b'PaiementState')),
        ),
        migrations.AddField(
            model_name='duckinscriptionpaymentrequest',
            name='paiement',
            field=models.ForeignKey(to='duck_inscription_payzen.PaiementAllModel'),
        ),
        migrations.AddField(
            model_name='duckinscriptionpaymentrequest',
            name='payment_config',
            field=models.ForeignKey(blank=True, to='django_payzen.MultiPaymentConfig', null=True),
        ),
        migrations.AddField(
            model_name='duckinscriptionpaymentrequest',
            name='theme',
            field=models.ForeignKey(blank=True, to='django_payzen.ThemeConfig', null=True),
        ),
        migrations.AddField(
            model_name='duckinscriptionpaymentrequest',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='duckinscriptionpaymentrequest',
            unique_together=set([('vads_trans_id', 'vads_site_id', 'vads_trans_date')]),
        ),
    ]
