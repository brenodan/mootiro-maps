# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from markitup.widgets import MarkItUpWidget
from ajax_select.fields import AutoCompleteSelectMultipleField

from crispy_forms.helper import FormHelper
from main.utils import MooHelper
from main.widgets import Tagsinput
from organization.models import (Organization, OrganizationBranch,
                OrganizationCategory, OrganizationCategoryTranslation)
from need.models import TargetAudience
from fileupload.forms import FileuploadField
from fileupload.models import UploadedFile

if settings.LANGUAGE_CODE == 'en-us':
    CATEGORIES = [(cat.id, cat.name) \
                    for cat in OrganizationCategory.objects.all()]
else:
    CATEGORIES = [(cat.category_id, cat.name)\
                    for cat in OrganizationCategoryTranslation.objects.filter(
                        lang=settings.LANGUAGE_CODE)]


class FormOrganizationNew(forms.ModelForm):
    description = forms.CharField(required=False, widget=MarkItUpWidget())
    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)
    contact = forms.CharField(required=False, widget=MarkItUpWidget())
    target_audiences = forms.Field(required=False,
        widget=Tagsinput(
            TargetAudience,
            autocomplete_url="/need/target_audience_search")
    )
    # categories = AutoCompleteSelectMultipleField('organizationcategory',
    #     help_text='', required=False)
    categories = forms.MultipleChoiceField(required=False, choices=CATEGORIES,
        widget=forms.CheckboxSelectMultiple(
                    attrs={'class': 'org-widget-categories'}))
    files = FileuploadField(required=False)

    class Meta:
        model = Organization
        fields = ['description', 'community', 'link', 'contact',
        'target_audiences', 'categories', 'files']

    _field_labels = {
        'description': _('Description'),
        'community': _('Community'),
        'contact': _('Contact'),
        'target_audiences': _('Target Audience'),
        'categories': _('Categories'),
        'files': _(' ')
    }

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False

        post = args[0] if args and len(args) > 0 else None
        if post:
            self.org_name = post.get('org_name_text')

        org = super(FormOrganizationNew, self).__init__(*args, **kwargs)

        for field, label in self._field_labels.iteritems():
            self.fields[field].label = label

        return org

    def save(self, user=None, *args, **kwargs):
        org = Organization()
        org.description = self.cleaned_data['description']
        org.contact = self.cleaned_data['contact']
        org.link = self.cleaned_data['link']
        org.name = self.org_name
        if user and not user.is_anonymous():
            org.creator_id = user.id
        org.save()

        for com in self.cleaned_data['community']:
            org.community.add(com)

        for target_aud in self.cleaned_data['target_audiences']:
            org.target_audiences.add(target_aud)

        for c in self.cleaned_data['categories']:
            org.categories.add(c)

        files_id_list = self.cleaned_data.get('files', '').split('|')
        UploadedFile.bind_files(files_id_list, org)

        return org


class FormOrganizationEdit(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    description = forms.CharField(required=False, widget=MarkItUpWidget())
    community = AutoCompleteSelectMultipleField('community', help_text='',
        required=False)
    contact = forms.CharField(required=False, widget=MarkItUpWidget())
    target_audiences = forms.Field(required=False,
        widget=Tagsinput(
            TargetAudience,
            autocomplete_url="/need/target_audience_search")
    )
    # categories = AutoCompleteSelectMultipleField('organizationcategory',
    #     help_text='', required=False)
    categories = forms.MultipleChoiceField(required=False, choices=CATEGORIES,
        widget=forms.CheckboxSelectMultiple(
                    attrs={'class': 'org-widget-categories'}))
    files = FileuploadField(required=False)

    class Meta:
        model = Organization
        fields = ['name', 'description', 'community', 'link', 'contact',
                  'target_audiences', 'categories', 'id']

    _field_labels = {
        'name': _('Name'),
        'description': _('Description'),
        'community': _('Community'),
        'contact': _('Contact'),
        'target_audiences': _('Target Audiences'),
        'categories': _('Categories'),
        'files': _(' ')
    }

    def __init__(self, *args, **kwargs):
        self.helper = MooHelper()
        self.helper.form_id = 'form_organization'

        org = super(FormOrganizationEdit, self).__init__(*args, **kwargs)
        for field, label in self._field_labels.iteritems():
            self.fields[field].label = label

        return org

    def save(self, user=None, *args, **kwargs):
        org = super(FormOrganizationEdit, self).save(*args, **kwargs)

        if user and not user.is_anonymous():
            org.creator_id = user.id
            org.save()

        files_id_list = self.cleaned_data.get('files', '').split('|')
        UploadedFile.bind_files(files_id_list, org)

        return org


class FormBranchNew(forms.Form):
    branch_name = forms.CharField()
    geometry = forms.CharField(required=False, widget=forms.HiddenInput())
    branch_info = forms.CharField(required=False, widget=MarkItUpWidget())

    _field_labels = {
        'branch_name': _('Branch Name'),
        'branch_info': _('Info'),
    }

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False

        b = super(FormBranchNew, self).__init__(*args, **kwargs)

        for field, label in self._field_labels.iteritems():
            self.fields[field].label = label

        return b

    def save(self, user=None, organization=None, *args, **kwargs):
        branch = OrganizationBranch()
        if 'geometry' in self.fields:
            branch.geometry = self.cleaned_data.get('geometry', '')
        branch.info = self.cleaned_data.get('branch_info', None)
        branch.name = self.cleaned_data.get('branch_name', None)
        if user and not user.is_anonymous():
            branch.creator_id = user.id
        branch.organization = organization
        branch.save()
        return branch
