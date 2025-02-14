from django.db import models
from django.conf import settings

class Patient(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True,blank=True)
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    dob        = models.DateField(verbose_name="Date of Birth")
    email      = models.EmailField()
    phone      = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Appointment(models.Model):
    patient          = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    doctor_name      = models.CharField(max_length=100)
    reason           = models.TextField()

    def __str__(self):
        return f"Appointment for {self.patient} on {self.appointment_date}"



class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    bio = models.TextField()

    def __str__(self):
        return self.name
