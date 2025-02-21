# healthcare_app/forms.py
from django import forms
from django.core.validators import RegexValidator
from .models import Appointment, Patient
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import DoctorProfile


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'appointment_date', 'doctor', 'reason']
        labels = {
            'patient': 'Select Patient',
            'appointment_date': 'Date & Time',
            'doctor': 'Doctor Name',
            'reason': 'Reason for Appointment',
        }
        help_texts = {
            'appointment_date': 'Choose a suitable date and time.',
            'reason': 'Describe the reason or symptoms for this appointment.',
        }
        widgets = {
            'patient': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'appointment_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'placeholder': 'YYYY-MM-DD HH:MM',
                }
            ),
            'doctor': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'reason': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Briefly describe your reason or symptoms',
                }
            ),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # We’ll pass 'user' from the view
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = DoctorProfile.objects.filter(is_lab_tester=False)


class PatientForm(forms.ModelForm):
    # Example phone regex validator
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    # Override the phone field to include validation
    phone = forms.CharField(
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. +1234567890'
        })
    )

    # Override the dob (Date of Birth) field to use an HTML5 date picker
    dob = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',         # HTML5 date input
                'class': 'form-control'
            }
        ),
        label="Date of Birth"
    )

    # Override the email field to use HTML5 email input
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com'
        })
    )

    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'dob', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            # We already overrode `dob`, `email`, and `phone` above
        }

SPECIALTY_CHOICES = [
    ('neurologist', 'Neurologist'),
    ('surgeon', 'Surgeon'),
    ('gynecologist', 'Gynecologist'),
    ('cardiologist', 'Cardiologist'),
    ('dentist', 'Dentist'),
    ('dietician', 'Dietician'),
    ('orthopedist', 'Orthopedist'),
    ('dermatologist', 'Dermatologist'),
    ('psychiatrist', 'Psychiatrist'),
    ('pediatrician', 'Pediatrician'),
    ('ent', 'ENT'),
]


class DoctorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    specialty = forms.ChoiceField(choices=SPECIALTY_CHOICES)
    bio = forms.CharField(widget=forms.Textarea, required=True)
    checkup_fee = forms.DecimalField(
        max_digits=8, decimal_places=2, required=True,
        help_text="Enter your consultation fee in INR."
    )
    is_lab_tester = forms.BooleanField(
        required=False, 
        label="Register as Lab Tester (For Lab Test Appointments Only)"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'specialty', 'bio', 'checkup_fee', 'is_lab_tester', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit)
        specialty = self.cleaned_data['specialty']
        bio = self.cleaned_data['bio']
        fee = self.cleaned_data['checkup_fee']
        lab_tester = self.cleaned_data.get('is_lab_tester', False)
        # Create the DoctorProfile with the provided details.
        DoctorProfile.objects.create(
            user=user, 
            specialty=specialty, 
            bio=bio, 
            checkup_fee=fee,
            is_lab_tester=lab_tester
        )
        return user