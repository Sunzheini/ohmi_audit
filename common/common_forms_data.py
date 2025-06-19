from django import forms
from django.utils import translation


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
