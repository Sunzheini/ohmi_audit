from django import forms
from ohmi_audit.main_app.models import *

__all__ = ['AuditForm']


class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['date'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['description'].widget = forms.Textarea(attrs={'rows': 3})
