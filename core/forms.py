import json
import re

from django import forms
from django.core.validators import RegexValidator

from .locations import REGION_CITY_COMMUNE_MAP, get_city_choices, get_commune_choices, get_region_choices
from .models import ContactRequest


class ContactRequestForm(forms.ModelForm):
    phone_validator = RegexValidator(
        regex=r"^[0-9+\s()\-]{8,20}$",
        message="Ingresa un teléfono válido, solo con números y caracteres habituales.",
    )

    region = forms.ChoiceField(
        label="Región",
        choices=[],
        required=True,
        error_messages={
            "required": "Selecciona una región.",
            "invalid_choice": "Selecciona una región válida.",
        },
    )
    city = forms.ChoiceField(
        label="Ciudad",
        choices=[],
        required=True,
        error_messages={
            "required": "Selecciona una ciudad.",
            "invalid_choice": "Selecciona una ciudad válida.",
        },
    )
    commune = forms.ChoiceField(
        label="Comuna",
        choices=[],
        required=True,
        error_messages={
            "required": "Selecciona una comuna.",
            "invalid_choice": "Selecciona una comuna válida para la ciudad indicada.",
        },
    )

    class Meta:
        model = ContactRequest
        fields = [
            "full_name",
            "company",
            "email",
            "phone",
            "service",
            "message",
        ]
        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "placeholder": "Nombre y apellido",
                    "autocomplete": "name",
                    "maxlength": "120",
                }
            ),
            "company": forms.TextInput(
                attrs={
                    "placeholder": "Empresa, edificio o proyecto",
                    "autocomplete": "organization",
                    "maxlength": "140",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "contacto@maxservicesspa.cl",
                    "autocomplete": "email",
                    "inputmode": "email",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "22 559 01 08",
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "maxlength": "20",
                }
            ),
            "service": forms.Select(),
            "message": forms.Textarea(
                attrs={
                    "rows": 5,
                    "minlength": "20",
                    "placeholder": (
                        "Cuéntanos el tipo de recinto, el trabajo requerido y "
                        "si necesitas visita técnica, instalación o mantención."
                    ),
                }
            ),
        }
        labels = {
            "full_name": "Nombre",
            "company": "Empresa o proyecto",
            "email": "Correo electrónico",
            "phone": "Teléfono",
            "service": "Servicio requerido",
            "message": "Detalle del requerimiento",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].required = False
        self.fields["phone"].required = True
        self.fields["phone"].validators.append(self.phone_validator)
        self.fields["full_name"].error_messages["required"] = "Ingresa tu nombre y apellido."
        self.fields["email"].error_messages["required"] = "Ingresa un correo electrónico válido."
        self.fields["phone"].error_messages["required"] = "Ingresa un teléfono de contacto."
        self.fields["service"].error_messages["required"] = "Selecciona un servicio requerido."
        self.fields["message"].error_messages["required"] = "Describe el requerimiento para poder revisarlo."
        self.fields["region"].choices = get_region_choices()
        self.fields["region"].widget.attrs["class"] = "form-select site-input"
        self.fields["city"].choices = get_city_choices("")
        self.fields["city"].widget.attrs["class"] = "form-select site-input"
        self.fields["commune"].widget.attrs["class"] = "form-select site-input"

        if self.data.get("region") or self.data.get("city"):
            initial_region = self.data.get("region", "")
            initial_city = self.data.get("city")
            initial_commune = self.data.get("commune", "")
        else:
            initial_region, initial_city, initial_commune = self._parse_location(
                getattr(self.instance, "location", "")
            )

        self.fields["region"].initial = initial_region
        self.fields["city"].initial = initial_city
        self.fields["city"].choices = get_city_choices(initial_region)
        self.fields["commune"].choices = get_commune_choices(initial_region, initial_city)
        self.fields["commune"].initial = initial_commune
        self.fields["region"].widget.attrs["data-cities-endpoint"] = "/api/locations/cities/"
        self.fields["city"].widget.attrs["data-communes-endpoint"] = "/api/locations/communes/"

        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select site-input"
            else:
                field.widget.attrs["class"] = "form-control site-input"

    def clean_full_name(self):
        full_name = " ".join((self.cleaned_data.get("full_name") or "").split())
        if len(full_name) < 6:
            raise forms.ValidationError("Ingresa nombre y apellido completos.")
        if len(full_name.split()) < 2:
            raise forms.ValidationError("Ingresa al menos nombre y apellido.")
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'.-]+", full_name):
            raise forms.ValidationError("Ingresa un nombre válido, sin símbolos extraños.")
        return full_name

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        return email

    def clean_phone(self):
        phone = " ".join((self.cleaned_data.get("phone") or "").split())
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 8:
            raise forms.ValidationError("Ingresa un teléfono válido con al menos 8 dígitos.")
        return phone

    def clean_company(self):
        company = " ".join((self.cleaned_data.get("company") or "").split())
        return company

    def clean_message(self):
        message = " ".join((self.cleaned_data.get("message") or "").split())
        if len(message) < 20:
            raise forms.ValidationError("Entrega un poco más de detalle para poder evaluar el requerimiento.")
        return message

    @property
    def location_map_json(self):
        return json.dumps(REGION_CITY_COMMUNE_MAP, ensure_ascii=False)

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get("region", "").strip()
        city = cleaned_data.get("city", "").strip()
        commune = cleaned_data.get("commune", "").strip()

        if not region:
            self.add_error("region", "Selecciona una región.")

        if not city:
            self.add_error("city", "Selecciona una ciudad.")

        if region and city:
            valid_cities = [value for value, _label in get_city_choices(region) if value]
            if city not in valid_cities:
                self.add_error("city", "Selecciona una ciudad válida para la región indicada.")

        if city and not commune:
            self.add_error("commune", "Selecciona una comuna.")

        valid_communes = [value for value, _label in get_commune_choices(region, city) if value]
        if region and city and commune and commune not in valid_communes:
            self.add_error("commune", "Selecciona una comuna válida para la ciudad indicada.")

        cleaned_data["location"] = self._compose_location(region, city, commune)
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.location = self.cleaned_data.get("location", "")
        if commit:
            instance.save()
        return instance

    def _parse_location(self, location_value):
        if not location_value:
            return "", "", ""

        parts = [part.strip() for part in location_value.split(",") if part.strip()]
        if len(parts) >= 3:
            commune, city, region = parts[0], parts[1], ", ".join(parts[2:])
            return region, city, commune
        if len(parts) == 2:
            commune, city = parts
            return "", city, commune
        return "", "", ""

    def _compose_location(self, region, city, commune):
        if region and city and commune:
            return f"{commune}, {city}, {region}"
        if city and commune:
            return f"{commune}, {city}"
        return region or city or commune
