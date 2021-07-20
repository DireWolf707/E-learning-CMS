from django.shortcuts import render
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from django.shortcuts import redirect
from django.contrib.auth import login


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return redirect('courses:home')
