# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _


import datetime


from generic.models import GenericModel, GenericStateModel, FalseFK, GenericContactableModel, GenericGroupsModel, GenericExternalUnitAllowed, GenericModelWithLines, ModelUsedAsLine, GenericModelWithFiles, GenericTaggableObject
from rights.utils import UnitExternalEditableModel, UnitEditableModel
from accounting_core.utils import AccountingYearLinked, CostCenterLinked
from app.utils import get_current_year, get_current_unit


class _Subvention(GenericModel, GenericModelWithFiles, GenericModelWithLines, AccountingYearLinked, GenericStateModel, GenericGroupsModel, UnitExternalEditableModel, GenericExternalUnitAllowed, GenericContactableModel):

    SUBVENTION_TYPE = (
        ('subvention', _(u'Subvention')),
        ('sponsorship', _(u'Sponsoring')),
    )

    class MetaRightsUnit(UnitExternalEditableModel.MetaRightsUnit):
        access = 'TRESORERIE'
        world_ro_access = False

    name = models.CharField(_(u'Nom du projet'), max_length=255)
    amount_asked = models.SmallIntegerField(_(u'Montant demandé'))
    amount_given = models.SmallIntegerField(_(u'Montant attribué'), blank=True, null=True)
    mobility_asked = models.SmallIntegerField(_(u'Montant mobilité demandé'), blank=True, null=True)
    mobility_given = models.SmallIntegerField(_(u'Montant mobilité attribué'), blank=True, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    comment_root = models.TextField(_('Commentaire AGEPoly'), blank=True, null=True)
    kind = models.CharField(_(u'Type de soutien'), max_length=15, choices=SUBVENTION_TYPE, blank=True, null=True)

    class Meta:
        abstract = True
        unique_together = (("unit", "unit_blank_name", "accounting_year"),)

    class MetaEdit:
        files_title = _(u'Fichiers')
        files_help = _(u'Envoie les fichiers nécessaires pour ta demande de subvention.')

    class MetaData:
        list_display = [
            ('name', _(u'Projet')),
            ('get_unit_name', _(u'Association / Commission')),
            ('amount_asked', _(u'Montant demandé')),
            ('mobility_asked', _(u'Montant mobilité demandé')),
        ]

        default_sort = "[2, 'asc']"  # unit
        filter_fields = ('name', 'kind', 'unit')

        details_display = list_display + [('description', _(u'Description')), ('accounting_year', _(u'Année comptable'))]
        extra_right_display = {'comment_root': lambda (obj, user): obj.rights_can('LIST', user)}

        files_title = _(u'Fichiers')
        base_title = _(u'Subvention')
        list_title = _(u'Liste des demandes de subvention')
        base_icon = 'fa fa-list'
        elem_icon = 'fa fa-smile-o'

        menu_id = 'menu-compta-subventions'
        not_sortable_colums = ['get_unit_name']
        safe_fields = ['get_unit_name']

        has_unit = True

        help_list = _(u"""Les demandes de subvention peuvent être faites par toutes les commissions ou association auprès de l'AGEPoly.""")

    class MetaAccounting:
        copiable = False

    class MetaLines:
        lines_objects = [
            {
                'title': _(u'Evènements'),
                'class': 'accounting_tools.models.SubventionLine',
                'form': 'accounting_tools.forms.SubventionLineForm',
                'related_name': 'events',
                'field': 'subvention',
                'sortable': True,
                'date_fields': ['start_date', 'end_date'],
                'show_list': [
                    ('name', _(u'Titre')),
                    ('start_date', _(u'Du')),
                    ('end_date', _(u'Au')),
                    ('place', _(u'Lieu')),
                    ('nb_spec', _(u'Nb personnes attendues')),
                ]
            },
        ]

    class MetaState:

        states = {
            '0_draft': _(u'Brouillon'),
            '1_submited': _(u'Demande soumise'),
            '2_treated': _(u'Demande traitée'),
        }

        default = '0_draft'

        states_texts = {
            '0_draft': _(u'La demande est en cours de création et n\'est pas publique.'),
            '1_submited': _(u'La demande a été soumise.'),
            '2_treated': _(u'La demande a été traitée.'),
        }

        states_links = {
            '0_draft': ['1_submited'],
            '1_submited': ['2_treated'],
            '2_treated': [],
        }

        states_colors = {
            '0_draft': 'primary',
            '1_submited': 'default',
            '2_treated': 'success',
        }

        states_icons = {
            '0_draft': '',
            '1_submited': '',
            '2_treated': '',
            '3_archived': '',
        }

        list_quick_switch = {
            '0_draft': [('1_submited', 'fa fa-check', _(u'Soumettre la demande')), ],
            '1_submited': [('2_treated', 'fa fa-check', _(u'Marquer la demande comme traitée')), ],
            '2_treated': [],
        }

        states_default_filter = '0_draft,1_submited,2_treated'
        states_default_filter_related = '0_draft,1_submited,2_treated'
        status_col_id = 3

    def __init__(self, *args, **kwargs):
        super(_Subvention, self).__init__(*args, **kwargs)

        self.MetaRights = type("MetaRights", (self.MetaRights,), {})
        self.MetaRights.rights_update({
            'EXPORT': _(u'Peut exporter les éléments'),
        })

    def may_switch_to(self, user, dest_state):

        return self.rights_can('EDIT', user)

    def can_switch_to(self, user, dest_state):

        if self.status == '2_treated' and not user.is_superuser:
            return (False, _(u'Seul un super utilisateur peut sortir cet élément de l\'état traité'))

        if int(dest_state[0]) - int(self.status[0]) != 1 and not user.is_superuser:
            return (False, _(u'Seul un super utilisateur peut sauter des étapes ou revenir en arrière.'))

        if self.status == '1_submited' and not self.rights_in_root_unit(user, self.MetaRightsUnit.access):
            return (False, _(u'Seul un membre du Comité de Direction peut marquer la demande comme traitée.'))

        if not self.rights_can('EDIT', user):
            return (False, _('Pas les droits.'))

        return super(_Subvention, self).can_switch_to(user, dest_state)

    def __unicode__(self):
        return u"{} {}".format(self.unit, self.accounting_year)

    def genericFormExtraClean(self, data, form):
        """Check that unique_together is fulfiled"""
        from accounting_tools.models import Subvention

        if Subvention.objects.exclude(pk=self.pk).filter(accounting_year=get_current_year(form.truffe_request), unit=get_current_unit(form.truffe_request), unit_blank_name=data['unit_blank_name']).count():
            raise forms.ValidationError(_(u'Une demande de subvention pour cette unité existe déjà pour cette année comptable.'))  # Potentiellement parmi les supprimées

    def genericFormExtraInit(self, form, current_user, *args, **kwargs):
        """Remove fields that should be edited by CDD only."""

        if not self.rights_in_root_unit(current_user, self.MetaRightsUnit.access):
            for key in ['amount_given', 'mobility_given', 'comment_root']:
                del form.fields[key]
            form.fields['kind'].widget = forms.HiddenInput()

    def rights_can_EXPORT(self, user):
        return self.rights_in_root_unit(user)

    def get_real_unit_name(self):
        return self.unit_blank_name or self.unit.name

    def total_people(self):
        """Return the total number of expected people among all events"""
        total = 0
        for line in self.events.all():
            total += line.nb_spec
        return total


class SubventionLine(ModelUsedAsLine):
    name = models.CharField(_(u'Nom de l\'évènement'), max_length=255)
    start_date = models.DateField(_(u'Début de l\'évènement'))
    end_date = models.DateField(_(u'Fin de l\'évènement'))
    place = models.CharField(_(u'Lieu de l\'évènement'), max_length=100)
    nb_spec = models.SmallIntegerField(_(u'Nombre de personnes attendues'))

    subvention = models.ForeignKey('Subvention', related_name="events", verbose_name=_(u'Subvention/sponsoring'))

    def __unicode__(self):
        return u"{}:{}".format(self.subvention.name, self.name)


class _Invoice(GenericModel, GenericTaggableObject, CostCenterLinked, GenericModelWithLines, AccountingYearLinked, UnitEditableModel):

    class MetaRightsUnit(UnitEditableModel.MetaRightsUnit):
        access = 'TRESORERIE'

    title = models.CharField(max_length=255)
    unit = FalseFK('units.models.Unit')

    custom_bvr_number = models.CharField(_(u'Numéro de BVR manuel'), help_text=_(u'Ne PAS utiliser un numéro alléatoire, mais utiliser un VRAI et UNIQUE numéro de BVR. Seulement pour des BVR physiques. Si pas renseigné, un numéro sera généré automatiquement. Il est possible de demander des BVR à Marianne.'), max_length=59, blank=True, null=True)

    address = models.TextField(_('Adresse'), help_text=_(u'Exemple: \'Monsieur Poney - Rue Des Canard 19 - 1015 Lausanne\''), blank=True, null=True)
    date_and_place = models.CharField(_(u'Lieu et date'), max_length=512, blank=True, null=True)
    preface = models.TextField(_(u'Introduction'), help_text=_(u'Texte affiché avant la liste. Exemple: \'Pour l\'achat du Yearbook 2014\' ou \'Chère Madame, - Par la présente, je me permets de vous remettre notre facture pour le financement de nos activités associatives pour l\'année académique 2014-2015.\''), blank=True, null=True)
    ending = models.CharField(_(u'Conclusion'), help_text=_(u'Affiché après la liste, avant les moyens de payements'), max_length=1024, default='', blank=True, null=True)
    display_bvr = models.BooleanField(_(u'Afficher payement via BVR'), help_text=_(u'Génère un BVR (il est possible d\'obtenir un \'vrai\' BVR via Marianne) et le texte corespondant'), default=True)
    display_account = models.BooleanField(_(u'Afficher payement via compte'), help_text=_(u'Affiche le texte pour le payement via le compte de l\'AGEPoly.'), default=True)
    greetins = models.CharField(_(u'Salutations'), default='', max_length=1024, blank=True, null=True)
    sign = models.CharField(_(u'Signature'), max_length=512, help_text=_(u'Titre de la zone de signature'), blank=True, null=True)
    annex = models.BooleanField(_(u'Annexes'), help_text=_(u'Affiche \'Annexe(s): ment.\' en bas de la facture'), default=False)

    # TODO: Statut (Draft, Sent, TramisMarianne, Reçu)

    class MetaData:
        list_display = [
            ('title', _('Titre')),
            ('costcenter', _(u'Centre de coût')),
            ('get_reference', _(u'Référence')),
        ]
        details_display = list_display + [
            ('get_bvr_number', _(u'Numéro de BVR')),
            ('address', _('Adresse')),
            ('date_and_place', _(u'Lieu et date')),
            ('preface', _(u'Introduction')),
            ('ending', _(u'Conclusion')),
            ('display_bvr', _(u'Afficher payement via BVR')),
            ('display_account', _(u'Afficher payement via compte')),
            ('greetins', _(u'Salutations')),
            ('sign', _(u'Signature')),
            ('annex', _(u'Annexes')),

        ]
        filter_fields = ('title', )

        base_title = _(u'Facture')
        list_title = _(u'Liste de toutes les factures')
        base_icon = 'fa fa-list'
        elem_icon = 'fa fa-money'

        default_sort = "[1, 'asc']"  # title

        menu_id = 'menu-compta-invoice'

        has_unit = True

        help_list = _(u"""Factures.""")

        not_sortable_colums = ['get_reference',]
        yes_or_no_fields = ['display_bvr', 'display_account', 'annex']

    class MetaEdit:

        @staticmethod
        def set_extra_defaults(obj, request):
            obj.sign = '{} {}'.format(request.user.first_name, request.user.last_name)
            obj.date_and_place = 'Lausanne, le {}'.format(datetime.datetime.now().strftime('%d %B %Y'))

    class MetaLines:
        lines_objects = [
            {
                'title': _(u'Lignes'),
                'class': 'accounting_tools.models.InvoiceLine',
                'form': 'accounting_tools.forms.InvoiceLineForm',
                'related_name': 'lines',
                'field': 'invoice',
                'sortable': True,
                'tva_fields': ['tva'],
                'show_list': [
                    ('label', _(u'Titre')),
                    ('quantity', _(u'Quantité')),
                    ('value', _(u'Montant (HT)')),
                    ('get_tva', _(u'TVA')),
                    ('total', _(u'Montant (TTC)')),
                ]},
        ]

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title

    def get_reference(self):
        return 'T2-{}-{}'.format(self.costcenter.account_number, self.pk)

    def get_bvr_number(self):
        return self.custom_bvr_number or \
            '94 42100 08402 {0:05d} {1:05d} {2:05d}'.format(int(self.costcenter.account_number), int(self.pk / 100000), self.pk % 100000)  # Note: 84=T => 04202~T2~Truffe2

    def get_lines(self):
        return self.lines.order_by('order').all()

    def get_total(self):
        return sum([line.total() for line in self.get_lines()])


class InvoiceLine(ModelUsedAsLine):

    invoice = models.ForeignKey('Invoice', related_name="lines")

    label = models.CharField(_(u'Titre'), max_length=255)
    quantity = models.DecimalField(_(u'Quantité'), max_digits=20, decimal_places=0, default=1)
    value = models.DecimalField(_('Montant unitaire (HT)'), max_digits=20, decimal_places=2)
    tva = models.DecimalField(_('TVA'), max_digits=20, decimal_places=2)

    def __unicode__(self):
        return u'%s: %s * %s + %s%%' % (self.label, self.quantity, self.value, self.tva)

    def total(self):
        return float(self.quantity) * float(self.value) * (1 + float(self.tva) / 100.0)

    def get_tva(self):
        from accounting_core.models import TVA
        return TVA.tva_format(self.tva)
