# coding=utf-8
from django.conf.urls import url
from duck_inscription.utils import wish_verif_etape_and_login
from duck_inscription_payzen import views

__author__ = 'paulguichon'

urlpatterns = [

    url(r'^dispatch/(?P<pk>\d+)/$', wish_verif_etape_and_login(views.DispatchView.as_view()),
        name="dispatch"),
    url(r'^choix_ied_fp/(?P<pk>\d+)/$', wish_verif_etape_and_login(views.ChoixIedFpView.as_view()),
        name="choix_ied_fp"),
    url(r'^droit_univ/(?P<pk>\d+)/$', wish_verif_etape_and_login(views.DroitView.as_view()), name="droit_univ"),
    url(r'^droit_univ/(?P<pk>\d+)/$', wish_verif_etape_and_login(views.DroitView.as_view()), name="choix_demi_annee"),
    url(r'^droit_univ/(?P<pk>\d+)/$', wish_verif_etape_and_login(views.DroitView.as_view()), name="nb_paiement"),
    url(r'^droit_univ/(?P<pk>\d+)/$', wish_verif_etape_and_login(views.DroitView.as_view()), name="recapitulatif"),
    url(r'^paiement/(?P<pk>\d+)/$', views.PaiementView.as_view(), name='paiement'),
    url(r'^error/(?P<pk>\d+)/$', views.PaiementFailureView.as_view(), name='error'),
    url(r'^faillure/(?P<pk>\d+)/$', views.PaiementFailureView.as_view(), name='failure'),


]
