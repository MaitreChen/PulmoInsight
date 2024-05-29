from django.db import models
from django.contrib.auth.models import AbstractUser

from django.utils import timezone
from os.path import basename


class UploadedImage(models.Model):
    """
    Image Upload Class

    Note:
    This class defines a model for storing uploaded images.
    """
    image = models.ImageField(upload_to='images/')


class CustomUser(AbstractUser):
    """
    Custom User Class

    Note:
    This class extends Django's built-in User model by adding an 'is_doctor' field
    for identity verification.
    """
    is_doctor = models.BooleanField(default=False)


class Patient(models.Model):
    """
    Patient Information Class
    """

    # Basic Information
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    marital_status = models.CharField(max_length=20, blank=True, null=True)
    occupation = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

    # Medical Records
    medical_history = models.TextField(blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    other = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Doctor(models.Model):
    """
    Medical Information Class
    """

    # Basic Information
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    marital_status = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class MedicalRecord(models.Model):
    """
    Medical Record Class

    Note:
    The model is linked to the Patient model through a foreign key relationship.
    Whenever a patient uploads medical information, a new MedicalRecord entry
    is created instead of updating the existing patient record.
    """

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    image_name = models.CharField(max_length=255, blank=True, null=False, default='')  # 图像名称
    pulmonary_image = models.ImageField(upload_to='pulmonary_images/', blank=True, null=False, default='')
    medical_history = models.TextField(blank=True, null=False, default='')
    symptoms = models.TextField(blank=True, null=False, default='')
    other = models.TextField(blank=True, null=False, default='')
    upload_time = models.DateTimeField(default=timezone.now, null=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def get_patient_age(self):
        return self.patient.age

    def get_patient_name(self):
        return self.patient.name

    def get_patient_gender(self):
        return self.patient.gender

    def get_patient_marital_status(self):
        return self.patient.marital_status

    def get_patient_medical_image_name(self):
        return basename(self.pulmonary_image.name)


class DiagnosisRecord(models.Model):
    """
    Diagnosis Record Class
    """

    # link to patient
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    # Diagnosis Information
    diagnosis_status = models.CharField(max_length=20)
    diagnosis_result = models.TextField(null=True, blank=True)
    detailed_diagnosis = models.TextField(blank=True, null=True)
    diagnosis_suggestion = models.TextField(blank=True, null=True)
    diagnosis_time = models.DateTimeField(null=True, blank=True)
    diagnostician = models.CharField(max_length=255, null=True, blank=True)

    # decide whether disputed
    controversy_status = models.BooleanField(default=False, null=True, blank=True)
    controversy_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnosis for {self.patient.name} - {self.diagnosis_status}"

    class Meta:
        ordering = ['-created_at']  #


class PatientPost(models.Model):
    """
    Patient Post Class
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.patient.name} - {self.created_at}'


class PatientComment(models.Model):
    """
    Patient Comment Class
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(PatientPost, on_delete=models.CASCADE, related_name='comments', null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.patient.name} - {self.created_at}'


class DoctorPost(models.Model):
    """
    Doctor Post Class
    """
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.doctor.name} - {self.created_at}'


class DoctorComment(models.Model):
    """
    Doctor Comment Class
    """
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(DoctorPost, on_delete=models.CASCADE, related_name='comments', null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.doctor.name} - {self.created_at}'
