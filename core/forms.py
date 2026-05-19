from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from core.models import User, Course, Lesson, Quiz, QuizQuestion, Assignment, Announcement

class UserRegistrationForm(UserCreationForm):
    """Extended user registration form with additional fields"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email address'
    }))
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First name'
    }))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last name'
    }))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone number'
    }))
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'date_of_birth', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ('password1', 'password2'):
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class CourseForm(forms.ModelForm):
    """Form for creating and editing courses"""
    class Meta:
        model = Course
        fields = ('title', 'description', 'short_description', 'level', 'price', 'featured_image', 'status')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class LessonForm(forms.ModelForm):
    """Form for creating and editing lessons"""
    class Meta:
        model = Lesson
        fields = ('title', 'description', 'content', 'video_url', 'document', 'order')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class QuizForm(forms.ModelForm):
    """Form for creating quizzes"""
    class Meta:
        model = Quiz
        fields = ('title', 'description', 'passing_score', 'attempts_allowed')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'attempts_allowed': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class QuizQuestionForm(forms.ModelForm):
    """Form for creating quiz questions"""
    class Meta:
        model = QuizQuestion
        fields = ('question_text', 'question_type', 'correct_answer', 'points', 'order')
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'correct_answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AssignmentForm(forms.ModelForm):
    """Form for creating assignments"""
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'instructions', 'due_date', 'max_score')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class AnnouncementForm(forms.ModelForm):
    """Form for creating announcements"""
    class Meta:
        model = Announcement
        fields = ('title', 'content', 'is_pinned')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
