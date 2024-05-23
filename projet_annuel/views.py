from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import User
from django.http import HttpResponse
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.contrib.auth import logout

def connection(request):
    if request.method == 'POST':
        mail = request.POST.get('email')
        password = request.POST.get('password')
        user = User.user_login(mail, password)
        if user is not None:
            login(request, user)
            return redirect('user_profile')
        else:
            print("Erreur lors de la connexion !")
    return render(request, 'signin.html')

def inscription(request):
    if request.method == 'POST':
        username = request.POST.get('pseudo')
        mail = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user = User.create_user( mail, password, first_name, last_name, username)
        if user:
            pass
        else:
            pass
    return render(request, 'signup.html')

@login_required
def user_profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserChangeForm(instance=request.user)

    context = {
        'user': request.user,
        'form': form
    }
    return render(request, 'profile.html', context)

class UserProfileUpdateForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(max_length=255, required=False)
    age = forms.IntegerField(required=False)
    sexe = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')], required=False)

def update_profile(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.email = form.cleaned_data.get('email')
            user.age = form.cleaned_data.get('age')
            user.sexe = form.cleaned_data.get('sexe')
            user.save()
            User.update_user(user.email, user.password, user.first_name, user.last_name, user.username, user.age, user.sexe)
            return redirect('update_profile')
        
    else:
        form = UserProfileUpdateForm()

    context = {
        'form': form
    }
    return render(request, 'update_profile.html', context)

def logout_view(request):
    logout(request)
    return redirect('hello_world')

def hello_world(request):
    return render(request, 'index.html')

