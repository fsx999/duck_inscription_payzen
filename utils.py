# coding=utf-8
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.decorators import available_attrs
from six import wraps

__author__ = 'paulguichon'

def paiement_passes_test(test_func):
    """
    decorateur copier de django et modifié
    """
    from duck_inscription.models import Wish

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_anonymous():
                return redirect('/')
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            if test_func(request.user) and request.user.individu.get_absolute_url() == reverse('accueil', kwargs={'pk': request.user.individu.pk}):  # l'individu est bien authentifié et il a fini
                try:  # si l'étudiant à un voeu
                    wish = request.user.individu.wishes.get(pk=kwargs['pk'])
                    if wish.get_absolute_url() == reverse('dispatch', kwargs={'pk': wish.pk}) and request.path_info == wish.paiementallmodel.get_absolute_url():  # c'est la bonne url
                        return view_func(request, *args, **kwargs)
                    else:
                        return redirect(wish.get_absolute_url())
                except (Wish.DoesNotExist, KeyError), e:  # il n'a pas de voeux
                    if request.path_info != reverse("new_wish", kwargs={'pk': request.user.individu.pk}):
                        return redirect(reverse('accueil', kwargs={'pk': request.user.individu.pk}))
                return view_func(request, *args, **kwargs)


            return redirect(reverse('accueil'), kwargs={'pk': request.user.individu.pk})

        return _wrapped_view

    return decorator


def paiement_verif_etape_and_login(function=None):
    actual_decorator = paiement_passes_test(
        lambda u: u.is_authenticated()

    )
    if function:
        return actual_decorator(function)
    return actual_decorator
