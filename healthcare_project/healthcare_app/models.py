from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)
    bio = models.TextField()
    checkup_fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_lab_tester = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Patient(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True,blank=True)
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    dob        = models.DateField(verbose_name="Date of Birth")
    email      = models.EmailField()
    phone      = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

class Appointment(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    doctor = models.ForeignKey('DoctorProfile', on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField()
    queue_number = models.IntegerField(null=True, blank=True)
    checkup_done = models.BooleanField(default=False)
    is_lab_test = models.BooleanField(default=False)  # Flag for lab test appointments

    def save(self, *args, **kwargs):
        # Save first
        super().save(*args, **kwargs)
        # Recalculate queue numbers only for pending non-completed appointments on the same day.
        # For lab test appointments, you might choose to recalc separately if needed.
        if not self.is_lab_test:
            appointments = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date__date=self.appointment_date.date(),
                checkup_done=False,
                is_lab_test=False
            ).order_by('appointment_date')
        else:
            # For lab test appointments, recalc queue numbers for all lab test appointments on that day.
            appointments = Appointment.objects.filter(
                is_lab_test=True,
                appointment_date__date=self.appointment_date.date(),
                checkup_done=False
            ).order_by('appointment_date')
        for idx, appointment in enumerate(appointments, start=1):
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

class Medicine(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    # Optionally include stock, expiry, etc.

    def __str__(self):
        return self.name

class MedicineOrder(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='Pending')  # e.g. Pending, Confirmed, Delivered, Cancelled
    order_number = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Save the order first so that order_date is set.
        super().save(*args, **kwargs)
        # Recalculate order numbers for all orders for this patient,
        # ordered by order_date (oldest first)
        orders = MedicineOrder.objects.filter(patient=self.patient).order_by('order_date')
        for idx, order in enumerate(orders, start=1):
            if order.order_number != idx:
                # Use update() to avoid recursive calls to save()
                MedicineOrder.objects.filter(pk=order.pk).update(order_number=idx)

    def __str__(self):
        # Show the order number if available, otherwise fallback to primary key.
        return f"Order {self.order_number or self.id} by {self.patient}"

    
