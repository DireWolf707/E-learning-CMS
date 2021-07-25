from django import forms
from .models import Course, Module


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ('instructor', 'slug', 'created', 'students')


ModuleFormSet = forms.inlineformset_factory(
    Course, Module, fields=('title', 'description',), extra=3, can_delete=True
)
