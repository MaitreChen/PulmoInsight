# Import necessary modules from Django
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.conf import settings
from django.utils import timezone

# Import forms and models from the current app
from .forms import (
    ImageUploadForm,
    PatientBasicInfoForm,
    DoctorBasicInfoForm,
    PatientMedicalHistoryForm,
    PatientPostForm,
    PatientCommentForm,
    DoctorPostForm,
    DoctorCommentForm
)
from .models import (
    UploadedImage,
    Doctor,
    Patient,
    MedicalRecord,
    DiagnosisRecord,
    PatientPost,
    PatientComment,
    DoctorPost,
    DoctorComment
)

# Import os module for operating system related functionalities
import os

# Import custom module for ONNX model inference
from .onnx_inference import inference_resnet18sam

# Import necessary modules for image processing
from PIL import Image
import numpy as np
import cv2 as cv


def index(request):
    return render(request, 'index.html')


def login_view(request):
    """
     Handles user login.
     """
    # Check if the request method is POST
    if request.method == 'POST':
        # Create an instance of AuthenticationForm with the POST data
        form = AuthenticationForm(request, request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Extract username, password, and role from the form data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = request.POST.get('role')

            # Authenticate the user with the provided username and password
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # If user authentication is successful
                login(request, user)

                # Redirect based on the user's role
                if role == 'doctor' and user.is_doctor:
                    # Redirect to doctor's home page if the user is a doctor
                    return redirect('doctor_home')
                elif role == 'patient' and not user.is_doctor:
                    # Redirect to patient's home page if the user is a patient
                    return redirect('patient_home')

                # If the selected role does not match, display an error message
                messages.error(request, 'Invalid role selected.')
            else:
                # If user authentication fails, display an error message
                messages.error(request, 'Invalid username or password.')

        else:
            # If form validation fails, display an error message
            messages.error(request, 'Invalid form submission. Please check your input.')

    return render(request, 'login.html', {'form': AuthenticationForm()})


def register_view(request):
    """
    Handles user registration.
    """
    # Import necessary modules
    from .models import CustomUser
    from django.contrib.auth.hashers import make_password

    if request.method == 'POST':
        # Extract data from POST request
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        identity = request.POST.get('identity')

        # Check if passwords match
        if password1 != password2:
            return render(request, 'register.html', {'error': 'Passwords do not match. Please try again!'})
        elif 'hospital' not in email and identity == 'doctor':
            return render(request, 'register.html', {'error': 'Incorrect identity. Please try again!'})

        # Check if username already exists
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists. Please try again!'})
        else:
            # Create user
            user = CustomUser(username=username, email=email)
            user.password = make_password(password1)  # Hash the password using make_password
            user.is_doctor = 'hospital' in email and identity == 'doctor'  # Set user role based on email and identity
            user.save()

            # Log in the user after registration
            login(request, user)

            # Display success message
            messages.success(request, 'Registration successful!')

            # Redirect to login page
            return redirect('login')

    return render(request, 'register.html')


def password_reset_view(request):
    """
    Handles password reset requests.
    """
    error_message = None

    if request.method == 'POST':
        # Extract data from POST request
        username = request.POST.get('username')
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        # Check if new passwords match
        if new_password != confirm_new_password:
            error_message = 'Entered passwords do not match. Please enter them again.'
        else:
            # Get the user model and manager
            User = get_user_model()
            user_manager = User.objects

            # Filter users by username and email
            users = user_manager.filter(username=username, email=email)

            if not users.exists():
                error_message = 'Username or email does not match. Please check your input.'
            else:
                # Get the first user
                user = users.first()

                # Reset the user's password
                user.set_password(new_password)
                user.save()

                # Update user session to maintain login state after password change
                update_session_auth_hash(request, user)

                # Display success message and redirect to login page
                messages.success(request, 'Password successfully reset!')
                return redirect('login')

    return render(request, 'password_reset.html', {'error_message': error_message})


def upload(request):
    """
    Handles file upload requests.
    """
    if request.method == 'POST' and request.FILES.get('file'):
        # If request method is POST and a file is uploaded
        uploaded_file = request.FILES['file']

        # Handle file logic, simply save the file to the 'media' directory
        with open('media/' + uploaded_file.name, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Return success response if file upload is successful
        return JsonResponse({'status': 'success'})
    else:
        # Return error response if no file is received
        return JsonResponse({'status': 'error', 'message': 'File not received.'})


@login_required
def doctor_home(request):
    """
    Renders the doctor's home page.
    """
    user = request.user  # Get the current user

    # Get diagnosis records with diagnosis status 'No'
    no_diagnosis_records = DiagnosisRecord.objects.filter(diagnosis_status='No')

    print(f"no diagnosis patients:{no_diagnosis_records}")  # Print number of patients without diagnosis

    # Count the number of patients without diagnosis
    patients_with_no_diagnosis = len([record.patient for record in no_diagnosis_records])

    return render(request, 'doctor/doctor_home.html', {'user': user, 'num_patients': patients_with_no_diagnosis})


# Display each medical record uploaded by patients
def doctor_records(request):
    """
    Renders the doctor's records page, displaying medical records uploaded by patients.
    """
    # Get search criteria
    search_diagnosis_result = request.GET.get('search_diagnosis_result', 'All')
    search_diagnosis_status = request.GET.get('search_diagnosis_status', 'None')
    search_controversy_status = request.GET.get('search_controversy_status', 'None')

    # Print search criteria
    print(f"Search keyword for diagnosis_result: {search_diagnosis_result}")
    print(f"Search keyword for diagnosis_status: {search_diagnosis_status}")
    print(f"Search keyword for controversy_status: {search_controversy_status}")

    # Get patient and diagnosis record information
    patients = Patient.objects.all()
    diagnosis_records = DiagnosisRecord.objects.select_related('patient').all()

    # Print patient information
    # patients_to_delete = Patient.objects.filter(name='TestDoctorUser1')
    # patients_to_delete.delete()
    print(f"Patients information: {patients}")

    # Merge data
    merged_data = []
    for patient in patients:
        medical_record = patient.medical_records.first()

        # Check if diagnosis record exists
        diagnosis_record = diagnosis_records.filter(patient=patient).first()

        diagnosis_status = 'No'
        diagnosis_result = None
        diagnosis_time = None
        diagnostician = None
        controversy_status = None

        # Create diagnosis record if it doesn't exist
        if not diagnosis_record:
            diagnosis_record = DiagnosisRecord(patient=patient, diagnosis_status='No',
                                               diagnosis_result=None, diagnosis_time=None,
                                               diagnostician=None, controversy_status=None)
            diagnosis_record.save()
        else:
            if diagnosis_record.diagnosis_status == 'Yes':
                diagnosis_status = 'Yes'
                diagnosis_result = diagnosis_record.diagnosis_result
                diagnosis_time = diagnosis_record.diagnosis_time
                diagnostician = diagnosis_record.diagnostician
                controversy_status = diagnosis_record.controversy_status

        # Append merged data
        merged_data.append(
            {'patient': patient, 'medical_record': medical_record, 'diagnosis_status': diagnosis_status,
             'diagnosis_result': diagnosis_result, 'diagnosis_time': diagnosis_time, 'diagnostician': diagnostician,
             'controversy_status': controversy_status})

    # Filter data based on diagnosis result search criteria
    if search_diagnosis_result in ['Normal', 'Pneumonia']:
        filtered_data = [data for data in merged_data if data['diagnosis_result'] == search_diagnosis_result]
    else:
        filtered_data = merged_data

    # Filter data based on diagnosis status search criteria
    if search_diagnosis_status != 'None':
        filtered_data = [data for data in filtered_data if data['diagnosis_status'] == search_diagnosis_status]

    # Filter data based on controversy status search criteria
    if search_controversy_status != 'None':
        filtered_data = [data for data in filtered_data if str(data['controversy_status']) == search_controversy_status]

    return render(request, 'doctor/doctor_records.html', {'merged_data': filtered_data})


def diagnose_patient(request, patient_id, record_id):
    """
    Renders the page to diagnose a patient based on their medical record.
    """
    # Get the patient, medical record, and diagnosis record
    patient = get_object_or_404(Patient, id=patient_id)
    medical_record = MedicalRecord.objects.filter(patient=patient)
    diagnosis_record = DiagnosisRecord.objects.filter(patient=patient)

    print("Patient's medical record information retrieved!")

    # Get the current medical record
    current_medical_record = get_object_or_404(MedicalRecord, id=record_id)

    if current_medical_record:
        image_path = current_medical_record.pulmonary_image.path
        # Open the original image
        original_image = np.array(Image.open(image_path))

        # Convert to grayscale if necessary
        if len(original_image.shape) == 3:
            original_image = cv.cvtColor(original_image, cv.COLOR_RGB2GRAY)

        # Perform inference using the model
        inference_time, inference_result, inference_probabilities = inference_resnet18sam(original_image)

        # Control button visibility
        upload_success = True

        # Add inference time and result to the context dictionary
        context = {
            'inference_time': inference_time,
            'inference_result': inference_result,
            'upload_success': upload_success,
            'inference_probabilities': inference_probabilities,
        }

        # Render the page with patient, medical record, diagnosis record, and inference results
        return render(request, 'doctor/diagnose_patient.html', {
            'patient': patient,
            'current_medical_record': current_medical_record,
            'diagnosis_record': diagnosis_record,
            'context': context,
        })


def save_diagnosis(request, patient_id, record_id):
    """
    Saves the diagnosis information provided by the doctor.
    """
    if request.method == 'POST':
        # Get the patient
        patient = get_object_or_404(Patient, id=patient_id)

        # Get the diagnosis record for the patient
        diagnosis_record = DiagnosisRecord.objects.filter(patient=patient).first()
        print(f'diagnosis_record:{diagnosis_record}')

        # Update diagnosis record information
        diagnosis_record.diagnosis_status = 'Yes'
        diagnosis_record.diagnosis_result = request.POST.get('diagnosis_result')
        diagnosis_record.detailed_diagnosis = request.POST.get('detailed_diagnosis')
        diagnosis_record.diagnosis_suggestion = request.POST.get('diagnosis_suggestion')
        diagnosis_record.diagnosis_time = timezone.now()
        diagnosis_record.diagnostician = request.user.username

        # Determine the controversy status of the diagnosis record
        controversy_value = request.POST.get('controversy', 'no')
        diagnosis_record.controversy_status = controversy_value == 'yes'
        diagnosis_record.controversy_reason = request.POST.get('controversy_reason')

        # Save the updated diagnosis record
        diagnosis_record.save()

        # Redirect to the doctor's records page after saving diagnosis
        return redirect('doctor_records')

    # If it's not a POST request, handle other logic such as displaying error messages
    return HttpResponse('An error occurred')


def delete_diagnosis_record(request, record_id):
    """
    Deletes the diagnosis record identified by the given record_id.
    """
    print("Deleting DiagnosisRecord with record_id:", record_id)

    # Get the diagnosis record by its ID
    diagnosis_record = get_object_or_404(DiagnosisRecord, id=record_id)

    # Delete the diagnosis record
    diagnosis_record.delete()

    # Redirect to the doctor's records page after deletion
    return redirect('doctor_records')


def doctor_analyze(request):
    """
    Handles image analysis by the doctor.
    """
    if request.method == 'POST':
        # If request method is POST, process the form data
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form data
            form.save()

            # Query the latest uploaded image
            latest_image = UploadedImage.objects.filter(image__isnull=False).order_by('-id').first()
            # print("image name:", latest_image.image.name)
            if latest_image:
                # Open the original image
                original_image = np.array(Image.open(latest_image.image.path))

                # Convert to grayscale if necessary
                if len(original_image.shape) == 3:
                    original_image = cv.cvtColor(original_image, cv.COLOR_RGB2GRAY)

                # Perform inference using the model
                inference_time, inference_result, inference_probabilities = inference_resnet18sam(original_image)
                # print(inference_probabilities)

                # Control button visibility
                upload_success = True

                # Add image name, inference time, and result to the context dictionary
                context = {
                    'image_name': latest_image.image.name.split("/")[1],
                    'latest_image': latest_image,
                    'inference_time': inference_time,
                    'inference_result': inference_result,
                    'upload_success': upload_success,
                    'inference_probabilities': inference_probabilities,
                }

                # Render the page with image analysis results
                return render(request, 'doctor/doctor_analyze.html', context)
    else:
        # If request method is not POST, display the form
        form = ImageUploadForm()

    return render(request, 'doctor/doctor_analyze.html', {'form': form})


@login_required
def doctor_community(request):
    """
    Renders the doctor's community page.
    """
    # Get the username of the currently logged-in user
    username = request.user.username

    # Check if the current user has filled out basic information; if not, display a warning to complete the profile
    try:
        # Get doctor instance for the logged-in user
        doctor = Doctor.objects.get(name=username)
        # print(f"Get doctor information: {doctor}")
    except Doctor.DoesNotExist:
        # If the doctor instance does not exist, return a message prompting to complete personal information
        return HttpResponse('Please complete your personal information!')

    # Get all posts in the community, ordered by creation time
    posts = DoctorPost.objects.all().order_by('-created_at')

    # Handle the form for posting new messages in the community
    if request.method == 'POST':
        post_form = DoctorPostForm(request.POST)
        if post_form.is_valid():
            # Save the new post
            new_post = post_form.save(commit=False)
            new_post.doctor = doctor
            new_post.save()
            return redirect('doctor_community')
    else:
        post_form = DoctorPostForm()

    # Render the doctor's community page with posts and post form
    return render(request, 'doctor/doctor_community.html',
                  {'posts': posts, 'doctor': doctor, 'post_form': post_form})


def doctor_help(request):
    """
    Renders the doctor's help page. Needs improvement.
    """
    return render(request, 'doctor/doctor_help.html')


def patient_home(request):
    """
    Renders the patient's home page with basic information and diagnosis records related to the user.
    """
    # Get the current logged-in user
    user = request.user

    # Retrieve diagnosis records related to the current user
    diagnosis_records = DiagnosisRecord.objects.filter(patient__name=user.username)

    # Initialize diagnosis status variable
    diagnosis_status = None

    # print(diagnosis_status)

    return render(request, 'patient/patient_home.html', {'user': user, 'diagnosis_status': diagnosis_status})


def patient_basic_info_upload(request):
    """
    Handles the uploading of basic information of a patient.
    """
    if request.method == 'POST':
        form = PatientBasicInfoForm(request.POST)
        if form.is_valid():
            # Extract data from the form
            patient_name = form.cleaned_data['name']

            # Check if patient exists, otherwise create a new patient object
            try:
                patient = Patient.objects.get(name=patient_name)
            except Patient.DoesNotExist:
                patient = Patient(name=patient_name)

            # Update patient object fields with form data
            patient.gender = form.cleaned_data['gender']
            patient.age = form.cleaned_data['age']
            patient.marital_status = form.cleaned_data['marital_status']
            patient.occupation = form.cleaned_data['occupation']
            patient.phone_number = form.cleaned_data['phone_number']
            patient.address = form.cleaned_data['address']

            # Save patient object to the database
            patient.save()

            # Store patient's basic information ID in session
            request.session['patient_basic_info_id'] = patient.id

    else:
        form = PatientBasicInfoForm()

    return render(request, 'patient/patient_basic_info_upload.html', {'form': form})


def patient_profile(request):
    """
    Renders the patient's profile page.
    """
    return render(request, 'patient/patient_basic_info_upload.html')


# Renders the page for uploading doctor basic information.
def doctor_basic_info_upload(request):
    """
    Renders the page for uploading doctor basic information.
    """
    if request.method == 'POST':
        # Get form data
        form = DoctorBasicInfoForm(request.POST)
        if form.is_valid():
            doctor_name = form.cleaned_data['name']
            try:
                doctor = Doctor.objects.get(name=doctor_name)
            except Doctor.DoesNotExist:
                doctor = Doctor(name=doctor_name)

            # Update doctor object fields
            doctor.gender = form.cleaned_data['gender']
            doctor.age = form.cleaned_data['age']
            doctor.marital_status = form.cleaned_data['marital_status']
            doctor.phone_number = form.cleaned_data['phone_number']
            doctor.address = form.cleaned_data['address']

            # Save doctor object to the database
            doctor.save()

            # Store the doctor's basic information ID in the session
            request.session['doctor_basic_info_id'] = doctor.id

    else:
        form = DoctorBasicInfoForm()

    return render(request, 'doctor/doctor_basic_info_upload.html', {'form': form})


def doctor_profile(request):
    """
    Renders the doctor's profile page.
    """
    return render(request, 'doctor/doctor_basic_info_upload.html')


# Renders the page for uploading patient medical history.
def patient_medical_history_upload(request):
    """
    Renders the page for uploading patient medical history.
    """
    # Get the username of the current logged-in user
    username = request.user.username

    try:
        # Get the patient instance if the user has completed personal information
        patient_instance = Patient.objects.get(name=username)
    except Patient.DoesNotExist:
        return HttpResponse('Please complete your personal information!')

    if request.method == 'POST':
        # Get form data
        image_file = request.FILES.get('image')
        medical_history = request.POST.get('medical_history')
        symptoms = request.POST.get('symptoms')
        other = request.POST.get('other')

        # Create forms
        image_form = ImageUploadForm(request.POST, request.FILES)
        medical_form = PatientMedicalHistoryForm(request.POST)

        # Check if both forms exist
        if image_file and medical_history and symptoms and other:
            # Create a new medical record
            new_medical_record = MedicalRecord(patient=patient_instance)

            if image_form.is_valid() and medical_form.is_valid():
                new_medical_record.pulmonary_image = image_form.cleaned_data['image']
                new_medical_record.medical_history = medical_form.cleaned_data['medical_history']
                new_medical_record.symptoms = medical_form.cleaned_data['symptoms']
                new_medical_record.other = medical_form.cleaned_data['other']
                # Save the patient instance to the database
                new_medical_record.save()
                return HttpResponse("Success")

    else:
        # Handle GET request
        image_form = ImageUploadForm()
        medical_form = PatientMedicalHistoryForm()

    return render(request, 'patient/patient_medical_history_upload.html',
                  {'image_form': image_form, 'form': medical_form})


# Renders the patient history page where medical records are displayed.
def patient_history(request):
    """
    Renders the patient history page displaying medical records.

    Args:
        request: HttpRequest object representing the request made to the server.

    Returns:
        Rendered HttpResponse object representing the patient's history page.
    """
    # Get the username of the current logged-in user
    username = request.user.username

    try:
        # Query the basic and diagnosis records of the patient
        patient_basic_records = MedicalRecord.objects.filter(patient__name=username)
        patient_diagnosis_records = DiagnosisRecord.objects.filter(patient__name=username)

        # Check if there are any diagnosis records
        if patient_diagnosis_records.first() is not None:
            # Try to get the diagnosis status
            try:
                patient_diagnosis_status = patient_diagnosis_records.first().diagnosis_status
            except AttributeError:
                # Set diagnosis status to None if there's an exception (NoneType has no attribute 'diagnosis_status')
                patient_diagnosis_status = None
        else:
            # Set diagnosis status to None if there are no diagnosis records
            patient_diagnosis_status = None

        # Compile the records
        records = {'patient_basic_records': patient_basic_records,
                   'patient_diagnosis_status': patient_diagnosis_status}

        # Pass the records to the frontend
        return render(request, 'patient/patient_history.html', records)
    except MedicalRecord.DoesNotExist:
        return HttpResponse('No medical records found for you.')


# Downloads an image file.
def download_image(request, filename):
    """
    Downloads an image file.
    """
    # Build the file path
    file_path = os.path.join(settings.MEDIA_ROOT, 'pulmonary_images', filename)

    # Open the file and create an HttpResponse object
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(),
                                content_type='image/png')  # Adjust content_type according to the actual file type

    # Set the file name and add download headers
    response['Content-Disposition'] = f'attachment; filename={filename}'

    return response


# Handles the deletion of medical records.
def delete_record(request, record_id):
    """
    Deletes a medical record.
    """
    try:
        # Delete the record corresponding to record_id
        record = MedicalRecord.objects.get(id=record_id)
        record.delete()

        # Also delete associated patient and diagnosis records
        patient_record = Patient.objects.get(name=request.user.username)
        patient_record.delete()

        diagnose_record = DiagnosisRecord.objects.get(patient__name=request.user.username)
        diagnose_record.delete()

        return JsonResponse({'success': True})
    except MedicalRecord.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Record not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Displays detailed information of a patient's medical records.
def patient_detailed_info(request):
    """
    Renders the detailed information page of a patient's medical records.
    """
    username = request.user.username
    patient = get_object_or_404(Patient, name=username)
    basic_records = MedicalRecord.objects.filter(patient__name=username).order_by('-upload_time')[:1]
    diagnosis_records = DiagnosisRecord.objects.filter(patient__name=username)

    return render(request, 'patient/patient_detailed_info.html',
                  {'patient': patient, 'basic_records': basic_records, 'diagnosis_records': diagnosis_records})


# Displays the patient community page.
@login_required
def patient_community(request):
    """
    Renders the patient community page.
    """
    # Get the username of the current logged-in user
    username = request.user.username

    # Check if the current user has filled in their basic information, display warning if not
    try:
        # Get the patient instance
        patient = Patient.objects.get(name=username)
    except Patient.DoesNotExist:
        return HttpResponse('Please complete your personal information!')

    # Get all posts in the patient community
    posts = PatientPost.objects.all().order_by('-created_at')

    # Handle form for submitting new posts
    if request.method == 'POST':
        post_form = PatientPostForm(request.POST)
        if post_form.is_valid():
            # Save the new post
            new_post = post_form.save(commit=False)
            new_post.patient = patient
            new_post.save()
            return redirect('patient_community')
    else:
        post_form = PatientPostForm()

    return render(request, 'patient/patient_community.html',
                  {'posts': posts, 'patient': patient, 'post_form': post_form})


# Deletes a post from the patient community.
def delete_patient_post(request, post_id):
    """
    Handles the deletion of a post from the patient community.
    """
    post = get_object_or_404(PatientPost, id=post_id)

    # Check user permissions to ensure only the author can delete the post
    if request.user.username == post.patient.name:
        post.delete()

    # Redirect to the patient community page or other appropriate page
    return redirect('patient_community')


# Deletes a post from the doctor community.
def delete_doctor_post(request, post_id):
    """
    Handles the deletion of a post from the doctor community.
    """
    post = get_object_or_404(DoctorPost, id=post_id)

    # Check user permissions to ensure only the author can delete the post
    if request.user.username == post.doctor.name:
        post.delete()

    # Redirect to the community page or other appropriate page
    return redirect('doctor_community')


# Displays comments for a patient post in the patient community.
@login_required
def view_patient_comments(request, post_id):
    """
    Renders the view for patient post comments in the patient community.
    """
    # Get the post object
    post = get_object_or_404(PatientPost, id=post_id)

    # Get the patient object corresponding to the current logged-in user
    patient = Patient.objects.get(name=request.user)

    # Get all comments for the post
    comments = PatientComment.objects.filter(post=post).order_by('-created_at')

    # Handle comment submission form
    if request.method == 'POST':
        comment_form = PatientCommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.patient = patient
            new_comment.save()
            return redirect('view_patient_comments', post_id=post_id)
    else:
        comment_form = PatientCommentForm()

    return render(request, 'patient/patient_view_comments.html',
                  {'post': post, 'comments': comments, 'comment_form': comment_form})


# Deletes the comment corresponding to a patient post.
def delete_patient_comment(request, comment_id, post_id):
    """
    Handles the deletion of a comment associated with a patient post.
    """
    # Get the comment object to be deleted, returns 404 if it doesn't exist
    comment = get_object_or_404(PatientComment, id=comment_id)

    # In a real-world project, there might be permission checks to ensure only the comment author or administrators can delete comments
    if request.user.username == comment.patient.name:
        # Perform the deletion operation
        comment.delete()

    return redirect('view_patient_comments', post_id=post_id)


# Displays comments for a doctor post in the doctor community.
@login_required
def view_doctor_comments(request, post_id):
    """
    Renders the view for doctor post comments in the doctor community.
    """
    # Get the post object
    post = get_object_or_404(DoctorPost, id=post_id)

    # Get the patient object corresponding to the current logged-in user
    doctor = Doctor.objects.get(name=request.user)

    # Get all comments for the post
    comments = DoctorComment.objects.filter(post=post).order_by('-created_at')

    # Handle comment submission form
    if request.method == 'POST':
        comment_form = DoctorCommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.patient = doctor
            new_comment.save()
            return redirect('view_doctor_comments', post_id=post_id)
    else:
        comment_form = DoctorCommentForm()

    return render(request, 'doctor/doctor_view_comments.html',
                  {'post': post, 'comments': comments, 'comment_form': comment_form})


# Deletes the comment corresponding to a doctor post.
def delete_doctor_comment(request, comment_id, post_id):
    """
    Handles the deletion of a comment associated with a doctor post.
    """
    # Get the comment object to be deleted, returns 404 if it doesn't exist
    comment = get_object_or_404(DoctorComment, id=comment_id)

    # In a real-world project, there might be permission checks to ensure only the comment author or administrators can delete comments
    if request.user.username == comment.doctor.name:
        # Perform the deletion operation
        comment.delete()

    return redirect('view_doctor_comments', post_id=post_id)


def patient_help(request):
    """
    Renders the patient's help page. Needs improvement.
    """
    return render(request, 'patient/patient_help.html')
