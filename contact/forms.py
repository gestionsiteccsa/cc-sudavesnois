from django import forms

from .models import ContactEmail

# from .models import Contact


class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Email")
    phone = forms.CharField(max_length=15, required=False, label="Téléphone")
    message = forms.CharField(widget=forms.Textarea, required=True, label="Message")
    rgpd = forms.BooleanField(required=True, label="J'accepte les conditions RGPD")

    def clean_message(self):
        message = self.cleaned_data.get("message")
        if len(message) < 10:
            raise forms.ValidationError("Le message doit contenir au moins 10 caractères.")
        return message

    def clean_phone(self):
        """
        Vérifie si le numéro de téléphone est valide.
        """
        phone = self.cleaned_data.get("phone")
        if phone:
            if not phone.isdigit():
                raise forms.ValidationError(
                    "Le numéro de téléphone doit \
                                            contenir uniquement des chiffres."
                )
            if len(phone) < 10:
                raise forms.ValidationError(
                    "Le numéro de téléphone doit \
                                            contenir au moins 10 chiffres."
                )
        return phone


class ContactEmailForm(forms.ModelForm):
    """Formulaire pour gérer les emails de contact."""

    class Meta:
        model = ContactEmail
        fields = ["email", "is_active"]
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "Entrez votre email"}),
            "is_active": forms.CheckboxInput(),
        }

        def clean_email(self):
            email = self.cleaned_data.get("email")
            if not email:
                raise forms.ValidationError("L'email est requis.")
            return email
