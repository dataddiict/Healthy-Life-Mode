from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as DjangoUser
from .models import UserProfile, predict_sleep_disorder, predict_obesity, predict_stress
from django import forms
from .models import User_User, getunbr_user, UserUpdateForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.contrib import messages
from .models import UserProfile, FollowDataUser

def connection(request):
    if request.method == 'POST':
        mail = request.POST.get('email')
        password = request.POST.get('password')
        user = User_User.user_login(mail, password)
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
    users = request.user
    history = FollowDataUser.objects.filter(user=users).order_by('updated_at')
    context = {
        'user': request.user,
        'profile': user_profile,
        'history': history
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

        

from django import forms
from .models import UserProfile

class UserProfileUpdateForm(forms.ModelForm):
    DAYS_INDOORS_CHOICES = [
        ('1-14 days', '1-14 days'), 
        ('15-30 days', '15-30 days'), 
        ('31-60 days', '31-60 days'), 
        ('More than 60 days', 'More than 60 days')
    ]
    YES_NO_MAYBE_CHOICES = [
        ('Yes', 'Yes'), 
        ('No', 'No'), 
        ('Maybe', 'Maybe')
    ]
    YES_NO_CHOICES = [
        ('Yes', 'Yes'), 
        ('No', 'No')
    ]

    Days_Indoors = forms.ChoiceField(choices=DAYS_INDOORS_CHOICES)
    Changes_Habits = forms.ChoiceField(choices=YES_NO_MAYBE_CHOICES)
    Work_Interest = forms.ChoiceField(choices=YES_NO_CHOICES)
    Social_Weakness = forms.ChoiceField(choices=YES_NO_MAYBE_CHOICES)
    Mental_Health_History = forms.ChoiceField(choices=YES_NO_MAYBE_CHOICES)

    class Meta:
        model = UserProfile
        fields = ['age', 'sexe',
                  'height', 'weight',
                  'steps', 'sleep_quality',
                  'sleep_duration', 'physical_activity',
                  'stress_level',
                  'ch2o','fcvc','ncp','Days_Indoors', 'Changes_Habits', 'Work_Interest', 'Social_Weakness', 'Mental_Health_History'
                ]

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
    prediction_obs = predict_obesity(user_id)
    prediction_stress = predict_stress(user_id)

    result_sleep = ''
    message_sleep = ''
    result_obesity = ''
    message_obesity = ''
    result_stress = ''
    message_stress = ''

    if prediction == 0:
        result_sleep = 'Pas de trouble du sommeil'
        message_sleep = 'Félicitations ! Vous n\'avez pas de troubles du sommeil. Continuez à maintenir une bonne hygiène de sommeil.'
    elif prediction == 1:
        result_sleep = 'Apnée du sommeil'
        message_sleep = 'Nous avons détecté des signes d\'apnée du sommeil. Il est recommandé de consulter un professionnel de la santé.'
    elif prediction == 2:
        result_sleep = 'Insomnie'
        message_sleep = 'Les résultats indiquent que vous pourriez souffrir d\'insomnie. Essayez de suivre des routines de sommeil régulières et évitez les écrans avant de dormir.'

    if prediction_obs == 0:
        result_obesity = "Sous-poids"
        message_obesity = "Vous êtes en insuffisance pondérale. Essayez d'ajuster légèrement votre mode de vie pour atteindre un poids optimal."
    elif prediction_obs == 1:
        result_obesity = 'Poids normal'
        message_obesity = "Vous avez un poids normal ! Félicitations pour maintenir un mode de vie sain."
    elif prediction_obs == 5:
        result_obesity = "Surpoids léger"
        message_obesity = "Vous êtes légèrement en surpoids. Essayez d'ajuster légèrement votre mode de vie pour atteindre un poids optimal."
    elif prediction_obs == 6:
        result_obesity = "Surpoids modéré"
        message_obesity = "Vous êtes modérément en surpoids. Essayez d'ajuster légèrement votre mode de vie pour atteindre un poids optimal."
    elif prediction_obs == 2:
        result_obesity = "Obésité de type I"
        message_obesity = "Vous êtes sévèrement en surpoids. Il est recommandé de consulter un professionnel de la santé pour vous aider à ajuster votre mode de vie."
    elif prediction_obs == 3:
        result_obesity = "Obésité de type II"
        message_obesity = "Vous êtes très en surpoids. Il est recommandé de consulter un professionnel de la santé pour vous aider à ajuster votre mode de vie."
    elif prediction_obs == 4:
        result_obesity = "Obésité de type III"
        message_obesity = "Vous êtes obèse morbide. Il est crucial de consulter un spécialiste pour un soutien approprié."

    if prediction_stress == 0:
        result_stress = 'Pas de stress'
        message_stress = 'Félicitations ! Vous n\'êtes pas stressé. Continuez à maintenir une bonne hygiène de vie.'
    elif prediction_stress == 1:
        result_stress = 'Stress modéré'
        message_stress = 'Vous êtes modérément stressé. Essayez de pratiquer des activités relaxantes pour réduire votre niveau de stress.'
    elif prediction_stress == 2:
        result_stress = 'Stress élevé'
        message_stress = 'Vous êtes très stressé. Il est recommandé de pratiquer des activités relaxantes et de consulter un professionnel de la santé.'

    context = {
        'result_sleep': result_sleep,
        'message_sleep': message_sleep,
        'result_obesity': result_obesity,
        'message_obesity': message_obesity,
        'result_stress': result_stress,
        'message_stress': message_stress
    }
    return render(request, 'prediction_result.html', context)

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

