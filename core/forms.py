from django import forms
from .models import *

class LectorRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = Lector
        fields = ['name', 'surname', 'email', 'lector_id']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()         #patara asoebit emailis sheyvana
        if Lector.objects.filter(email=email).exists():           
            raise forms.ValidationError("Email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        lector = super().save(commit=False)
        lector.set_password(self.cleaned_data['password'])  # hashed password
        if commit:
            lector.save()
        return lector

    

class StudentRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = Student
        fields = ['name', 'surname', 'email', 'student_id']

    def clean_email(self):
        email=self.cleaned_data['email'].lower() #lower shrift to not duplicate email with higher shrift
        if Student.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        lector = super().save(commit=False)
        lector.set_password(self.cleaned_data['password'])  # hashed password
        if commit:
            lector.save()
        return lector
    
class AddStudentForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        label="Select a student",
        widget=forms.Select(attrs={
            'class': 'form-control student-select',  # Add class for JS
            'style': 'width: 100%;'
        })
    )


class GroupForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Group
        fields = ['name', 'students']   

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'image', 'file']        

class PointForm(forms.ModelForm):
    class Meta:
        model = Point
        fields = ['student', 'value', 'point_type']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control student-select'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
            'point_type': forms.Select(attrs={'class': 'form-control'}),
        }

class StudentImageForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['profile_image']