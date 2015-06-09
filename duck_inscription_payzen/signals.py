__author__ = 'paulguichon'
from django.dispatch import receiver
from django_payzen.signals import payment_success, payment_failure, response_error
from duck_inscription_payzen import models as dip_mod

@receiver(payment_success)
def inscription_payment_success(sender, **kwargs):
    response = kwargs['response']
    paiement = dip_mod.PaiementAllModel.objects.get(pk=response.vads_order_id)
    paiement.done()
    paiement.wish.inscription()


@receiver(response_error)
def inscription_response_error(sender, **kwargs):
    response = kwargs['response']
    paiement = dip_mod.PaiementAllModel.objects.get(pk=response.vads_order_id)
    paiement.error()


@receiver(payment_failure)
def inscription_payment_failure(sender, **kwargs):
    response = kwargs['response']
    paiement = dip_mod.PaiementAllModel.objects.get(pk=response.vads_order_id)
    paiement.failure()