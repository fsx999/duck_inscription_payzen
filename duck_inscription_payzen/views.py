# coding=utf-8
from __future__ import unicode_literals
from django.core.urlresolvers import reverse, NoReverseMatch
__author__ = 'paulguichon'
from django.conf import settings
from django.views import generic
from django.shortcuts import redirect
from django.views.generic import TemplateView, UpdateView
from duck_inscription.models import CentreGestionModel
from duck_inscription_payzen.models import PaiementAllModel, DuckInscriptionPaymentRequest
from duck_inscription.views import WishIndividuMixin
import xworkflows
from duck_inscription_payzen.forms import ChoixPaiementDroitForm, DemiAnneeForm, NbPaiementPedaForm, \
    ValidationPaiementForm


class DispatchView(generic.View, WishIndividuMixin):

    def get(self, request, *args, **kwargs):
        try:
            return redirect(self.wish.paiementallmodel.get_absolute_url())
        except NoReverseMatch:
            return redirect(self.wish.get_absolute_url())


class ChoixIedFpView(TemplateView):
    template_name = "duck_inscription_payzen/choix_ied_fp.html"

    def get(self, request, *args, **kwargs):
        centre = self.request.GET.get('centre', None)
        if centre in ['ied', 'fp']:
            wish = self.request.user.individu.wishes.get(pk=self.kwargs['pk'])
            wish.centre_gestion = CentreGestionModel.objects.get(centre_gestion=centre)
            try:
                if centre == 'fp':
                    wish.inscription()
                    return redirect(wish.get_absolute_url())
                else:
                    wish.paiementallmodel.droit_univ()
            except xworkflows.InvalidTransitionError:
                pass
            return redirect(wish.paiementallmodel.get_absolute_url())
        return super(ChoixIedFpView, self).get(request, *args, **kwargs)


class DroitView(UpdateView, WishIndividuMixin):
    model = PaiementAllModel
    template_name = "duck_inscription/individu/dossier_inscription/base_formulaire.html"
    forms = {
        'droit_univ': ChoixPaiementDroitForm,
        'choix_demi_annee': DemiAnneeForm,
        'nb_paiement': NbPaiementPedaForm,
        "recapitulatif": ValidationPaiementForm
    }

    def get_template_names(self):
        if self.object.state == "recapitulatif":
            return "duck_inscription_payzen/recapitulatif.html"
        return self.template_name

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.state.is_done :
            return redirect(self.object.wish.get_absolute_url())
        if self.object.state.is_paiement or self.object.state.is_error or self.object.state.is_failure:
            return redirect(self.object.get_absolute_url())
        return super(DroitView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.get('precedent', None):
            self.object = self.get_object()
            if self.object.previous_step():
                return redirect(self.object.get_absolute_url())
        return super(DroitView, self).post(request, *args, **kwargs)


    def get_success_url(self):
        if self.object.next_step() and not self.object.state.is_done:
            return self.object.get_absolute_url()
        else:
            wish = self.wish
            return wish.get_absolute_url()

    def get_form_class(self):
        return self.forms[self.object.state]

    def get_object(self, queryset=None):
        wish = self.wish
        return PaiementAllModel.objects.get_or_create(wish=wish)[0]


class PaiementView(TemplateView, WishIndividuMixin):
    template_name = 'duck_inscription_payzen/test_paiement.html'

    def get_template_names(self):
        return super(PaiementView, self).get_template_names()

    def get(self, request, *args, **kwargs):
        p = self.wish.paiementallmodel
        if self.request.GET.get('res') == 'cancel':
            p.failure()
            return redirect(p.wish.get_absolute_url())
        if not p.state.is_paiement:
            return redirect(p.wish.get_absolute_url())
        return super(PaiementView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        p = self.wish.paiementallmodel
        url = reverse('paiement', kwargs={'pk': p.wish.pk})
        url_pattern = '{host}{url}?res={get}'
        try:
            payment_request = p.paiement_request
        except DuckInscriptionPaymentRequest.DoesNotExist:
            payment_request = DuckInscriptionPaymentRequest(
            paiement=p,

        )
        if settings.DEBUG:
            host = 'http://preins:8081'
        else:
            host = 'https://preins.iedparis8.net'

        payment_request.vads_trans_date = None
        payment_request.vads_trans_id = None
        payment_request.vads_amount=p.total
        payment_request.vads_url_success=url_pattern.format(host=host, url=url, get='success')
        payment_request.vads_url_refused=url_pattern.format(host=host, url=url, get='refused')
        payment_request.vads_url_cancel=url_pattern.format(host=host, url=url, get='cancel')
        payment_request.vads_order_info=self.wish.code_dossier
        payment_request.vads_order_info2="{} {}".format(self.wish.code_dossier, self.wish.individu.code_opi)
        payment_request.vads_order_id=p.pk
        payment_request.save()
        payment_request.copy_wish(self.wish)
        context= super(PaiementView, self).get_context_data(**kwargs)
        context['object'] = payment_request
        return context


class PaiementFailureView(TemplateView, WishIndividuMixin):
    template_name = "duck_inscription_payzen/failure.html"

    def get(self, request, *args, **kwargs):
        action = self.request.GET.get('action', None)
        if action:
            getattr(self.wish.paiementallmodel,action)()
            return redirect(self.wish.paiementallmodel.get_absolute_url())
        return super(PaiementFailureView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PaiementFailureView, self).get_context_data(**kwargs)
        context['wish'] = self.wish
        return context
