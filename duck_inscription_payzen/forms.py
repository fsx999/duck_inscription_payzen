# coding=utf-8
from __future__ import unicode_literals
from duck_inscription_payzen.models import PaiementAllModel

__author__ = 'paulguichon'
import floppyforms.__future__ as forms

class ChoixPaiementDroitForm(forms.ModelForm):

    class Meta:
        model = PaiementAllModel
        fields = ('moyen_paiement',)


class DemiAnneeForm(forms.ModelForm):
    demi_annee = forms.BooleanField(widget=forms.Select(choices=(('', '----'),
                                                                 ('1', "Je m'inscris à un semestre"),
                                                                 ('0', "Je m'inscris à une année entière")),),
                                    required=False)

    class Meta:
        model = PaiementAllModel
        fields = ('demi_annee',)


class NbPaiementPedaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NbPaiementPedaForm, self).__init__(*args, **kwargs)
        choices = [('', '-----')] + [(x + 1, x + 1) for x in range(self.instance.wish.etape.nb_paiement)]
        self.fields['nb_paiement_frais'] = forms.ChoiceField(choices=choices, label=u"Nombre de paiements")

    class Meta:
        model = PaiementAllModel
        fields = ('nb_paiement_frais',)

class ValidationPaiementForm(forms.ModelForm):
    valider = forms.CharField()

    class Meta:
        model = PaiementAllModel
        fields = ('id',)

