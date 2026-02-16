from django import forms

from .models import BackupSettings


class BackupSettingsForm(forms.ModelForm):
    """Formulaire pour modifier les paramètres de backup."""
    
    class Meta:
        model = BackupSettings
        fields = ['notification_email']
        widgets = {
            'notification_email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'ex: email@exemple.com'
            })
        }
        labels = {
            'notification_email': 'Email de notification'
        }
