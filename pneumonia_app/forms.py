from django import forms
from .models import UploadedImage

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Patient, DoctorPost, DoctorComment, PatientPost, PatientComment


# Medical Record Image Upload Form
class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']
        labels = {
            'image': 'Choose File:'
        }


# Registration Form
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('is_doctor',)


# Login Form
class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser


# Patient Basic Information Form
class PatientBasicInfoForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'gender', 'age', 'marital_status', 'occupation', 'phone_number', 'address']


# Doctor Basic Information Form
class DoctorBasicInfoForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'gender', 'age', 'marital_status', 'phone_number', 'address']


# Patient Medical Record Text Upload Form
class PatientMedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['medical_history', 'symptoms', 'other']


# Patient Post Upload Form
class PatientPostForm(forms.ModelForm):
    class Meta:
        model = PatientPost
        fields = ['content']


# Patient Post Comment Upload Form
class PatientCommentForm(forms.ModelForm):
    class Meta:
        model = PatientComment
        fields = ['comment']


# Doctor Post Upload Form
class DoctorPostForm(forms.ModelForm):
    class Meta:
        model = DoctorPost
        fields = ['content']


# Doctor Post Comment Upload Form
class DoctorCommentForm(forms.ModelForm):
    class Meta:
        model = DoctorComment
        fields = ['comment']
