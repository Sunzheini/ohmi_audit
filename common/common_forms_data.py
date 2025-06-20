from django import forms
from django.utils import translation

__all__ = ['ChangeLabelsMixin', 'FormWidgetStylesMixin']


ALL_LABELS_BG = {
    # all fields of model Audit
    'name': 'име',
    'description': 'описание',
    'date': 'дата',
    'is_active': 'активен',
    'category': 'категория',

    # all fields of model Test
    'some_other_field': 'друго поле',
    'type': 'тип',
    'number': 'номер',
}


class ChangeLabelsMixin:
    def change_to_current_labels(self):
        # language_code = translation.get_language()
        language_code = 'bg'  # For testing purposes, we set it to Bulgarian directly

        if language_code == 'bg':
            for field_name, field in self.fields.items():
                if field_name in ALL_LABELS_BG:
                    field.label = ALL_LABELS_BG[field_name]
                else:
                    # Fallback to default label if not found
                    field.label = field.label or field_name.replace('_', ' ').capitalize()


class FormWidgetStylesMixin:
    def set_widget_styles(self):
        """
        Applies consistent Bootstrap styling to all form fields.
        - Date fields get HTML5 date picker
        - Boolean fields get proper checkbox styling
        - Choice fields get select styling
        - Text fields get appropriate controls
        """
        for field_name, field in self.fields.items():
            # Skip already processed fields
            if hasattr(field, '_widget_processed'):
                continue

            # DateField (override widget completely)
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(attrs={
                    'type': 'date',
                    'class': 'form-control'
                })
                field._widget_processed = True
                continue  # Skip remaining checks for this field

            # BooleanField (checkboxes)
            elif isinstance(field, forms.BooleanField):
                field.widget = forms.CheckboxInput(attrs={
                    'class': 'form-check-input'
                })
                field._widget_processed = True
                continue

            # Choice fields (Select/SelectMultiple)
            elif isinstance(field, (forms.ChoiceField, forms.ModelChoiceField, forms.ModelMultipleChoiceField)):
                field.widget.attrs.update({'class': 'form-select'})
                field._widget_processed = True
                continue

            # CharField
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label
                })

            # CharField with choices (Select)
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': 'form-select',
                    'placeholder': field.label
                })

            # TextField
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': field.label
                })

            # FileField
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.update({
                    'class': 'form-control-file',
                    'placeholder': field.label
                })

            # EmailField
            elif isinstance(field.widget, forms.EmailInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label
                })

            # URLField
            elif isinstance(field.widget, forms.URLInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label
                })

            # NumberField
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label
                })

            # Other fields (default to form-control)
            else:
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label
                })

            # Mark widget as processed to avoid reapplying styles
            field._widget_processed = True
