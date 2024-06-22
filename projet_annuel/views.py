from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as DjangoUser
from .models import UserProfile, predict_sleep_disorder
from django import forms
from .models import User, getunbr_user, UserUpdateForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.contrib import messages


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
        user = DjangoUser.objects.create_user(username=username, email=mail, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return redirect('signin')
    return render(request, 'signup.html')

@login_required
def user_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    context = {
        'user': request.user,
        'profile': user_profile
    }
    return render(request, 'profile.html', context)


@login_required
def update_user(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('user_profile')
    else:
        form = UserUpdateForm(instance=request.user)
    context = {
        'form': form
    }
    return render(request, 'update_user.html', context)

        

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age', 'sexe', 'height', 'weight', 'steps', 'sleep_quality', 'sleep_duration', 'physical_activity', 'stress_level']

@login_required
def update_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserProfileUpdateForm(instance=user_profile)
    context = {
        'form': form
    }
    return render(request, 'update_profile.html', context)

@login_required
def predict_sleep_disorder_view(request):
    user_id = request.user.id
    prediction = predict_sleep_disorder(user_id)
    
    result = ''
    if prediction == 0:
        result = 'Pas de trouble du sommeil'
    elif prediction == 1:
        result = 'Apnée du sommeil'
    elif prediction == 2:
        result = 'Insomnie'
    
    return render(request, 'prediction_result.html', {'result': result})

def logout_view(request):
    logout(request)
    return redirect('hello_world')

def hello_world(request):
    user_count = getunbr_user()
    return render(request, 'index.html', {'user_count': user_count})

from django.shortcuts import render
from .models import Image, Service

def home(request):
    images = Image.objects.all()
    services = Service.objects.all()
    return render(request, 'index.html', {'images': images, 'services': services})

