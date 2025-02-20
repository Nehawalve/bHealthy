from django.shortcuts import get_object_or_404,render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import AppointmentForm
from .models import LabTest, HealthArticle, MedicineOrder, Appointment, DoctorProfile, Patient
from .forms import PatientForm
from .forms import DoctorRegistrationForm
from django.http import HttpResponse



def home(request):
    return render(request, 'healthcare_app/index.html')

def index(request):
    return render(request, 'healthcare_app/index.html')

def lab_tests(request):
    tests = LabTest.objects.all().order_by('name')
    return render(request, 'healthcare_app/lab_tests.html', {'tests': tests})

@login_required
def book_lab_test(request, test_id):
    test = get_object_or_404(LabTest, id=test_id)
    # Here you would implement booking logic.
    return render(request, 'healthcare_app/book_lab_test.html', {'test': test})

def buy_medicine(request):
    # Placeholder view for buying medicine.
    return render(request, 'healthcare_app/buy_medicine.html')

def health_articles(request):
    articles = HealthArticle.objects.filter(trending=True).order_by('-published_date')
    return render(request, 'healthcare_app/health_articles.html', {'articles': articles})

def article_detail(request, article_id):
    article = get_object_or_404(HealthArticle, id=article_id)
    return render(request, 'healthcare_app/article_detail.html', {'article': article})

@login_required
def order_details(request):
    orders = MedicineOrder.objects.filter(patient__user=request.user).order_by('-order_date')
    return render(request, 'healthcare_app/order_details.html', {'orders': orders})

def doctor_list(request):
    genre = request.GET.get('genre', None)
    if genre and genre != 'all':
        doctors = DoctorProfile.objects.filter(specialty__icontains=genre)
    else:
        doctors = DoctorProfile.objects.all()
    return render(request, 'healthcare_app/doctor_list.html', {'doctors': doctors, 'genre': genre})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the new user to the database
            # Optionally, you can log the user in automatically here
            return redirect('login')  # Redirect to login page after registration
        else:
            print(form.errors)  # For debugging: check errors in the console
    else:
        form = UserCreationForm()
    return render(request, 'healthcare_app/register.html', {'form': form})

@login_required    
def book_appointment(request):
    # Use request.user only if authenticated; otherwise, use None.
    current_user = request.user if getattr(request.user, 'is_authenticated', False) else None

    if request.method == "POST":
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm(user=request.user)
    return render(request, 'healthcare_app/appointment.html', {'form': form})


@login_required  
def appointment_list(request):
        appointments = Appointment.objects.filter(patient__user=request.user)
        return render(request, 'healthcare_app/appointment_list.html', {'appointments': appointments})

@login_required  
def appointment_list(request):
    if getattr(request.user, 'is_authenticated', False):
        # For logged-in users, show appointments only for patients associated with them.
        appointments = Appointment.objects.filter(patient__user=request.user)
    else:
        # For anonymous users, show all appointments (or change to Appointment.objects.none() if desired)
        appointments = Appointment.objects.all()
    
    return render(request, 'healthcare_app/appointment_list.html', {'appointments': appointments})


def about(request):
    return render(request, 'healthcare_app/about.html')

@login_required
def patient_list(request):
    # Show only the patients belonging to the logged-in user
    patients = Patient.objects.filter(user=request.user)
    return render(request, 'healthcare_app/patient_list.html', {'patients': patients})

@login_required
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.user = request.user  # Associate with the logged-in user
            patient.save()
            return redirect('patient_list')
        else:
            # Optional: print or log form.errors for debugging
            print(form.errors)
    else:
        form = PatientForm()

    return render(request, 'healthcare_app/patient_create.html', {'form': form})


def doctor_register(request):
    if request.method == "POST":
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('doctor_login')
    else:
        form = DoctorRegistrationForm()
    return render(request, 'healthcare_app/doctor_register.html', {'form': form})


@login_required
def doctor_dashboard(request):
    try:
        doctor_profile = request.user.doctorprofile
    except DoctorProfile.DoesNotExist:
        return redirect('doctor_register')
    
    hide_completed = request.GET.get('hide_completed') == '1'
    
    # Fetch appointments for this doctor, ordered by time
    appointments = Appointment.objects.filter(doctor=doctor_profile).order_by('appointment_date')
    if hide_completed:
        appointments = appointments.filter(checkup_done=False)
    
    context = {
        'appointments': appointments,
        'hide_completed': hide_completed,
    }
    return render(request, 'healthcare_app/doctor_dashboard.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Ensure the appointment belongs to the logged-in user (assuming patient appointments)
    if appointment.patient.user == request.user:
        appointment.delete()
    # Optionally, add messages.success(request, "Appointment cancelled successfully.")
    return redirect('appointment_list')


@login_required
def mark_checkup_done(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Ensure that only the assigned doctor can mark the appointment as done.
    if appointment.doctor.user == request.user:
        appointment.checkup_done = True
        appointment.save()
    # Optionally, add a success message here.
    return redirect('doctor_dashboard')


@login_required
def clear_completed_checkups(request):
    # Ensure that the logged-in user has a doctor profile.
    try:
        doctor_profile = request.user.doctorprofile
    except Exception:
        return redirect('doctor_register')
    
    if request.method == "POST":
        # Delete all completed appointments for this doctor
        Appointment.objects.filter(doctor=doctor_profile, checkup_done=True).delete()
        # Optionally, add a message to indicate success.
    
    return redirect('doctor_dashboard')