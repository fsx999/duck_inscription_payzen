# coding=utf-8
from duck_inscription_payzen.models import PaiementAllModel

__author__ = 'paulguichon'
from django.dispatch import receiver
from django_payzen.signals import payment_success, payment_failure, response_error
from duck_inscription_payzen import models as dip_mod
from duck_inscription.signals import paiement_dispatch
from django.db.models import ObjectDoesNotExist

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

@receiver(paiement_dispatch)
def create_paiement_inscription(sender, **kwargs):
    wish = kwargs['wish']
    PaiementAllModel.objects.get_or_create(wish=wish)
