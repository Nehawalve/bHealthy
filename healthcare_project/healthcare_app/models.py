from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)
    bio = models.TextField()

    def __str__(self):
        return self.user.get_full_name() or self.user.username


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
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField()
    queue_number = models.IntegerField(null=True, blank=True)
    checkup_done = models.BooleanField(default=False) 

    def save(self, *args, **kwargs):
        # First, save the current instance
        super().save(*args, **kwargs)
        
         # Recalculate queue numbers for all pending (non-completed) appointments
        # for the same doctor on the same day, sorted by appointment_date.
        pending_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date__date=self.appointment_date.date(),
            checkup_done=False
        ).order_by('appointment_date')

        for idx, appointment in enumerate(pending_appointments, start=1):
            # Update the queue_number only if it differs from the calculated value.
            if appointment.queue_number != idx:
                Appointment.objects.filter(pk=appointment.pk).update(queue_number=idx)

    def __str__(self):
        return f"Appointment for {self.patient} on {self.appointment_date}"


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    bio = models.TextField()

    def __str__(self):
        return self.name
    

class LabTest(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class HealthArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateField()
    trending = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class MedicineOrder(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} by {self.patient}"

