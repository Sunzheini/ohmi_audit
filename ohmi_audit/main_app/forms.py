from django import forms

from common.common_forms_data import *
from ohmi_audit.main_app.models import *

__all__ = ['AuditForm']


class AuditForm(forms.ModelForm, ChangeLabelsMixin, FormWidgetStylesMixin):
    class Meta:
        model = Audit
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_widget_styles()
