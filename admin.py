__author__ = 'paulguichon'
from django.contrib import admin
from duck_inscription_payzen import models as dip_models

admin.site.register(dip_models.MoyenPaiementModel)