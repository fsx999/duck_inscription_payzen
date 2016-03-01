# coding=utf-8
from __future__ import unicode_literals
import hashlib
from django.conf import settings
from django.core.urlresolvers import reverse
from django_payzen.models import PaymentRequest, ThemeConfig, MultiPaymentConfig, CustomPaymentConfig, PaymentResponse, \
    RequestDetails, CustomerDetails, ShippingDetails, OrderDetails, auth_user_model
from duck_inscription.models import Wish, CentreGestionModel
from django_payzen import constants, app_settings, tools
from django_xworkflows import models as xwf_models
from xworkflows import before_transition, on_enter_state
import datetime
from suds.client import Client
from suds.sax.element import Element
import uuid
import hmac
import base64
from django.utils.timezone import utc
import xworkflows

__author__ = 'paulguichon'

from django.db import models

class MoyenPaiementModel(models.Model):
    """
    chéque virement etc
    """
    type = models.CharField('type paiement', primary_key=True, max_length=3)
    label = models.CharField('label', max_length=60)

    def __unicode__(self):
        return unicode(self.label)


class TypePaiementModel(models.Model):
    """
    Droit univ ou frais péda
    """
    type = models.CharField('type de frais', primary_key=True, max_length=5)
    label = models.CharField('label', max_length=40)


    def __unicode__(self):
        return unicode(self.label)


PRECEDENT = 0
TITLE = 1
NEXT = 2
class PaiementState(xwf_models.Workflow):
    log_model = 'duck_inscription_payzen.PaiementStateLog'
    states = (
        ('choix_ied_fp', 'Choix centre'),
        ('droit_univ', 'Droit universitaire'),
        ('choix_demi_annee', 'Inscription à un semestre ou à l\'année'),
        ('nb_paiement', "Choisir le nombre de paiements"),
        ('recapitulatif', "Récapitulatif"),
        ('paiement', 'Paiement CB'),
        ('error', 'Erreur'),
        ('failure', 'Failure'),
        ('done', 'Effectué'),

    )
    initial_state = 'choix_ied_fp'

    transitions = (
        ('droit_univ', ('failure', 'error', 'choix_demi_annee', 'nb_paiement', 'choix_ied_fp'), 'droit_univ'),
        ('choix_demi_annee', ('droit_univ', 'nb_paiement'), 'choix_demi_annee'),
        ('nb_paiement', ('droit_univ', 'choix_demi_annee', 'recapitulatif'),'nb_paiement'),
        ('recapitulatif', 'nb_paiement', 'recapitulatif'),
        ('paiement', ('failure', 'error', 'recapitulatif'), 'paiement'),
        ('error', 'paiement', 'error'),
        ('failure', 'paiement', 'failure'),
        ('done', ('paiement', 'failure'), 'done')
    )

class PaiementStateLog(xwf_models.BaseTransitionLog):
    paiement = models.ForeignKey('PaiementAllModel', related_name='log_paiement')
    MODIFIED_OBJECT_FIELD = 'paiement'


class PaiementAllModel(xwf_models.WorkflowEnabled, models.Model):
    state = xwf_models.StateField(PaiementState)
    wish = models.OneToOneField(Wish)
    moyen_paiement = models.ForeignKey(MoyenPaiementModel, verbose_name=u'Votre moyen de paiement :',
                                       help_text=u"Veuillez choisir un moyen de paiement", null=True)
    nb_paiement_frais = models.IntegerField(verbose_name=u"Nombre de paiements pour les frais pédagogiques", default=1)
    demi_annee = models.BooleanField(default=False)

    @before_transition('droit_univ')
    def before_transition_droit_univ(self):
        wish = self.wish
        wish.valide_liste()
        if not wish.centre_gestion:
            wish.centre_gestion = CentreGestionModel.objects.get(centre_gestion='ied')

        if not wish.is_ok and not wish.is_reins_formation() and not wish.centre_gestion.centre_gestion == 'fp':
            try:
                wish.liste_attente_inscription()
            except xworkflows.InvalidTransitionError:
                pass


    @on_enter_state('paiement')
    def on_enter_state_paiement(self, res, *arg, **kwargs):
        if not self.moyen_paiement.type == 'CB':
            self.done()
            self.wish.inscription()

    @before_transition('choix_demi_annee')
    def on_enter_state_choix_demi_annee(self, *args, **kwargs):
        if not self.wish.can_demi_annee():
            if self.state.is_droit_univ:
                self.nb_paiement()
            elif self.state.is_nb_paiement:
                self.droit_univ()
            raise xwf_models.AbortTransition
    @property
    def num_transaction(self):
        pk = str(self.pk)
        return (6-len(pk))*'0'+pk

    def liste_motif(self):
        a = []
        for x in range(self.nb_paiement_frais):
            chaine = u'IED  %s %s %s %s' % (
            self.wish.etape.cod_etp, self.wish.individu.code_opi, self.wish.individu.last_name, str(x + 1))
            a.append(chaine)
        return a

    def range(self):
        a = []
        for x in range(self.nb_paiement_frais):
            a.append((x, self.moment_paiement[x]))
        return a


    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.demi_annee and not self.wish.demi_annee:
            self.wish.demi_annee = True
            self.wish.save()
        super(PaiementAllModel, self).save(force_insert, force_update, using, update_fields)

    def previous_step(self):
        index = self.state.workflow.states._order.index(self.state)-1
        if index >= 0:
            prev = self.state.workflow.states._order[self.state.workflow.states._order.index(self.state)-1]
            try:
                getattr(self, prev)()
            except xwf_models.AbortTransition:
                pass
            except AttributeError:
                return False
            return True
        else:
            return False

    def recap(self):
        return not self.liste_etapes[self.etape][NEXT]

    def prev(self):
        index = self.state.workflow.states._order.index(self.state)-1
        if index >= 0:
            return True
        else:
            return False

    def template_name(self):
        return 'duck_inscription_payzen/%s.html' % self.state

    @property
    def droit_total(self):
        """
        Api public: à implementer
        :return: les droits universitaire + secu + frais medicaux
        """
        return self.wish.droit_total()

    @property
    def frais_peda(self):
        """
        Api public: à implementer
        :return:
        """
        return self.wish.frais_peda()

    def title(self):
        return self.state.title

    def next_step(self):
        index = self.state.workflow.states._order.index(self.state)+1
        if index < len(self.state.workflow.states._order):

            next = self.state.workflow.states._order[index]
            try:
                getattr(self, next)()
            except xwf_models.AbortTransition:
                pass
            self.etape = str(self.state)
            self.save()
            return True
        else:
            return False

    def get_absolute_url(self):
        return reverse(self.state.name, kwargs={'pk':str(self.wish.pk)})

    @property
    def total(self):
        total = self.droit_total + self.frais_peda
        return str(int(total*100))
    @property
    def memsualite(self):
        return float(self.total_euro - self.first_paiement_euro)/float(self.nb_paiement_frais-1)
    @property
    def total_euro(self):
        total = self.droit_total + self.frais_peda
        return float(total)

    @property
    def first_paiement(self):
        return str(int((self.wish.droit_total() + (self.wish.frais_peda()/self.nb_paiement_frais))*100))

    @property
    def first_paiement_euro(self):
        return float((self.wish.droit_total() + (self.wish.frais_peda()/self.nb_paiement_frais)))
    @property
    def echeancier(self):
        date = datetime.datetime.strptime(self.paiement_request.vads_trans_date,  "%Y%m%d%H%M%S").strftime("%d/%m/%Y")
        if self.nb_paiement_frais == 1:
            return [[date, self.total_euro]]
        else:

            result = [[date, self.first_paiement_euro]]
            for x in range(self.nb_paiement_frais-1):
                result.append(['+{} jours'.format(str(30*(self.nb_paiement_frais-1))), self.memsualite])
            return result
    def get_context(self):
        return {'paiement': self}
    @property
    def range_paiement(self):
        return range(self.nb_paiement_frais)
    @property
    def echeancier_frais_peda(self):
        return float(self.frais_peda)/float(self.nb_paiement_frais)

    def get_templates(self):
        template = []
        if self.wish.centre_gestion.centre_gestion == 'fp':
            return template
        if self.moyen_paiement.type == 'CB':
            template.extend([{'name': 'duck_inscription_payzen/formulaire_paiement_cb.html'}])
        else:
            template.extend([{'name': "duck_inscription_payzen/formulaire_paiement_droit.html"},
         {'name': "duck_inscription_payzen/formulaire_paiement_frais.html"}])
        if self.moyen_paiement.type == 'V':
            template.extend([ {'name': 'duck_inscription_payzen/ordre_virement.html'}])
        return template

class DuckInscriptionPaymentRequest(RequestDetails, CustomerDetails,
                     OrderDetails, ShippingDetails):
    """Model that contains all Payzen parameters to initiate a payment."""
    user = models.ForeignKey(auth_user_model, blank=True, null=True)
    paiement = models.OneToOneField(PaiementAllModel, related_name='paiement_request')

    vads_capture_delay = models.PositiveIntegerField(blank=True, null=True)
    vads_contrib = models.CharField(
        max_length=255, blank=True, null=True,
        default=app_settings.VADS_CONTRIB)
    vads_payment_cards = models.CharField(
        max_length=127, blank=True, null=True)
    vads_return_mode = models.CharField(
        max_length=12, choices=constants.VADS_RETURN_MODE_CHOICES,
        blank=True, null=True)
    vads_theme_config = models.CharField(
        max_length=255, blank=True, null=True)
    vads_validation_mode = models.CharField(
        choices=constants.VADS_VALIDATION_MODE_CHOICES,
        max_length=1, blank=True, null=True)
    vads_url_success = models.URLField(blank=True, null=True)
    vads_url_referral = models.URLField(blank=True, null=True)
    vads_url_refused = models.URLField(blank=True, null=True)
    vads_url_cancel = models.URLField(blank=True, null=True)
    vads_url_error = models.URLField(blank=True, null=True)
    vads_url_return = models.URLField(blank=True, null=True)
    vads_user_info = models.CharField(max_length=255, blank=True, null=True)
    vads_shop_name = models.CharField(max_length=255, blank=True, null=True)
    vads_redirect_success_timeout = models.PositiveIntegerField(
        blank=True, null=True)
    vads_redirect_success_message = models.CharField(
        max_length=255, blank=True, null=True)
    vads_redirect_error_timeout = models.PositiveIntegerField(
        blank=True, null=True)
    vads_redirect_error_message = models.CharField(
        max_length=255, blank=True, null=True)

    # Relations
    theme = models.ForeignKey(ThemeConfig, blank=True, null=True)
    payment_config = models.ForeignKey(
        MultiPaymentConfig, blank=True, null=True)
    custom_payment_config = models.ManyToManyField(CustomPaymentConfig)

    class Meta:
        verbose_name = "Request"
        unique_together = ("vads_trans_id", "vads_site_id", "vads_trans_date")

    def set_vads_payment_config(self):
        """
        vads_payment_config can be set only after object saving.

        A custom payment config can be set once PaymentRequest saved
        (adding elements to the m2m relationship). As a consequence
        we set vads_payment_config just before sending data elements
        to payzen."""
        if self.paiement.nb_paiement_frais == 1:
            self.vads_payment_config = 'SINGLE'
        else:
            self.vads_payment_config = 'MULTI:first={};count={};period=30'.format(self.paiement.first_paiement, self.paiement.nb_paiement_frais)

    def set_signature(self):
        self.signature = tools.get_signature(self)

    @property
    def response(self):
        try:
            return PaymentResponse.objects.get(
                vads_trans_id=self.vads_trans_id,
                vads_trans_date=self.vads_trans_date,
                vads_site_id=self.vads_site_id)
        except PaymentResponse.DoesNotExist:
            return PaymentResponse.objects.none()

    @property
    def payment_successful(self):
        return self.response and self.response.payment_successful

    def save(self, **kwargs):
        """
        We set up vads_trans_id and theme according to payzen format.

        If fields values are explicitely set by user, we do not override
        their values.
        :param **kwargs:
        """
        if not self.vads_trans_date:
            self.vads_trans_date = datetime.datetime.utcnow().replace(
                tzinfo=utc).strftime("%Y%m%d%H%M%S")
        if not self.vads_trans_id:
            self.vads_trans_id = tools.get_vads_trans_id(
                self.vads_site_id, self.vads_trans_date)
        if self.theme and not self.vads_theme_config:
            self.vads_theme_config = str(self.theme)
        if not self.pk:
            super(DuckInscriptionPaymentRequest, self).save()

        self.set_vads_payment_config()
        self.set_signature()
        super(DuckInscriptionPaymentRequest, self).save()

    def update(self):
        if not self.pk:
            # Prevent bug on filtering m2m relationship
            self.save()
        if not self.vads_trans_date:
            self.vads_trans_date = datetime.datetime.utcnow().replace(
                tzinfo=utc).strftime("%Y%m%d%H%M%S")
        self.set_vads_payment_config()
        self.set_signature()
        self.save()

    def copy_wish(self, wish):
        self.vads_cust_email = wish.individu.user.email
        self.vads_cust_address = wish.individu.get_adresse_annuelle_simple()
        self.vads_cust_id = wish.individu.code_opi
        self.save()

    def _get_soap_headers(self):
        certif = settings.VADS_CERTIFICATE
        date = datetime.datetime.utcnow().replace(tzinfo=utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        rid = str(uuid.uuid1())
        id_ = rid + date
        token = hmac.new(bytes(certif).encode("utf-8"), bytes(id_).encode("utf-8"), hashlib.sha256).digest()
        token = base64.b64encode(token)

        # Create Header of request
        # Creates Element <shopId> id </shopId>
        shopId = Element('shopId').setText(settings.VADS_SITE_ID)
        timestamp = Element('timestamp').setText(date)
        requestId = Element('requestId').setText(rid)
        mode = Element('mode').setText(settings.VADS_CTX_MODE)
        # mode = Element('mode').setText('PRODUCTION')
        authToken = Element('authToken').setText(token)
        return shopId, requestId, timestamp, mode, authToken

    def status_paiement(self):
        # Create request
        url = 'https://secure.payzen.eu/vads-ws/v5?wsdl'
        client = Client(url)
        client.set_options(soapheaders=self._get_soap_headers())

        # Create body of request
        p = client.factory.create('queryRequest')
        p.orderId = self.vads_order_id
        result = client.service.findPayments(p)
        return result

    def payment_details(self, uuid_):
        # Create request
        url = 'https://secure.payzen.eu/vads-ws/v5?wsdl'
        client = Client(url)
        client.set_options(soapheaders=self._get_soap_headers())

        # Create body of request
        p = client.factory.create('queryRequest')
        p.uuid = uuid_
        result = client.service.getPaymentDetails(p)
        return result
