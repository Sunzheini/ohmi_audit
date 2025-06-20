from django import forms
from django.utils import translation

__all__ = ['ChangeLabelsMixin', 'FormWidgetStylesMixin']


class ChangeLabelsMixin:
    def change_to_given_labels(self, labels: dict = None):
        """
        Change the labels of the form fields to Bulgarian if the current language is Bulgarian.
        :param lang: The language code to check against. If 'bg', it will change the labels to Bulgarian.
        :param labels: A dictionary containing the labels for the fields. If None, it will use the default labels.
        example: {
            'type': 'Тип',
            'number': 'Номер',
            'name': 'Име',
            'parent_process': 'Родителски процес',
            'documents': 'Документи',
            'description': 'Описание',
            'responsible': 'Отговорник',
        }
        :return: None
        """
        if labels is None:
            raise ValueError("Labels dictionary must be provided for language change.")
        for field_name, label in labels.items():
            if field_name in self.fields:
                self.fields[field_name].label = label


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
