from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import AppointmentForm
from .models import Appointment, Doctor, Patient
from .forms import PatientForm



def home(request):
    return render(request, 'healthcare_app/index.html')


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

#@login_required    just remove this when login is required to access this page
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


#@login_required   just remove this when login is required to access this page
#def appointment_list(request):
    # Filter appointments by checking the user of the patient
 #   appointments = Appointment.objects.filter(patient__user=request.user)
  #  return render(request, 'healthcare_app/appointment_list.html', {'appointments': appointments})

def appointment_list(request):
    if getattr(request.user, 'is_authenticated', False):
        # For logged-in users, show appointments only for patients associated with them.
        appointments = Appointment.objects.filter(patient__user=request.user)
    else:
        # For anonymous users, show all appointments (or change to Appointment.objects.none() if desired)
        appointments = Appointment.objects.all()
    
    return render(request, 'healthcare_app/appointment_list.html', {'appointments': appointments})



def doctor_list(request):
    query = request.GET.get('q')
    if query:
        doctors = Doctor.objects.filter(name__icontains=query) | Doctor.objects.filter(specialty__icontains=query)
    else:
        doctors = Doctor.objects.all()
    return render(request, 'healthcare_app/doctor_list.html', {'doctors': doctors})

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