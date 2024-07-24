from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as DjangoUser
from .models import UserProfile, predict_sleep_disorder, predict_obesity, predict_stress, get_user_by_id, update_Last_Prediction_text, update_user_profile
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
        update_user_profile(sender=DjangoUser, instance=user, created=True)        

        
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
            update_user_profile(sender=DjangoUser, instance=request.user, created=False)
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



@login_required
def predict_sleep_disorder_view(request):
    user_id = request.user.id
   
    prediction = predict_sleep_disorder(user_id)
    prediction_obs = predict_obesity(user_id)
    prediction_stress = predict_stress(user_id)


    user_data = get_user_by_id(user_id)
    # convert user_data to a dictionary
    user_data = user_data.__dict__
    user_data.pop('_state')
    
    print(user_data)
    sleep_disorder_message = sleep_disorder_messages[prediction]
    obesity_status_message = obesity_status_messages[prediction_obs]
    stress_status_message = stress_status_messages[prediction_stress]

    recommendations = provide_detailed_recommendations_obesity(user_data)
    recommendations += provide_detailed_recommendations_stress(user_data)
    recommendations += provide_detailed_recommendations_nutrition(user_data)

    
    # trasnfrom the recommendations into a one string
    recommendations = '\n'.join(recommendations)


    context = {
        'sleep_disorder_message': sleep_disorder_message,
        'obesity_status_message': obesity_status_message,
        'stress_status_message': stress_status_message,
        'recommendations': recommendations
    }

    update_Last_Prediction_text(user_id, recommendations, sleep_disorder_message, obesity_status_message, stress_status_message)
    return render(request, 'prediction_result.html', context)

sleep_disorder_messages = {
    0: "Vous ne semblez pas avoir de troubles du sommeil. Continuez à maintenir un mode de vie sain.",
    1: "Vous pourriez souffrir d'apnée du sommeil. Il est important de consulter un professionnel de la santé pour une évaluation et un traitement approprié.",
    2: "Vous pourriez souffrir d'insomnie. Considérez des techniques de relaxation et consultez un professionnel de la santé si nécessaire.",
    -1: "Aucun trouble du sommeil détecté."
}
obesity_status_messages = {
    0: "Vous êtes en insuffisance pondérale. Essayez d'ajuster légèrement votre mode de vie pour atteindre un poids optimal.",
    1: "Vous avez un poids normal ! Félicitations pour maintenir un mode de vie sain.",
    2: "Vous êtes légèrement en surpoids. Essayez d'ajuster légèrement votre mode de vie pour atteindre un poids optimal.",
    3: "Vous êtes modérément en surpoids. Essayez d'ajuster légèrement votre mode de vie pour atteindre un poids optimal.",
    4: "Vous êtes sévèrement en surpoids. Il est recommandé de consulter un professionnel de la santé pour vous aider à ajuster votre mode de vie.",
    5: "Vous êtes très en surpoids. Il est recommandé de consulter un professionnel de la santé pour vous aider à ajuster votre mode de vie.",
    6: "Vous êtes obèse morbide. Il est crucial de consulter un spécialiste pour un soutien approprié."
}
stress_status_messages = {
    0: "Vous ne semblez pas éprouver de stress croissant. Continuez à maintenir un mode de vie équilibré et sain.",
    1: "Vous ressentez du stress croissant. Il est important de prendre des mesures pour gérer votre stress et consulter un professionnel si nécessaire.",
    2: "Vous pourriez ressentir du stress croissant. Évaluez vos habitudes et considérez des techniques de gestion du stress."
}


def provide_detailed_recommendations_obesity(user_data):
    recommendations = []
    # calculate BMI avec height et weight
    user_data['BMI Category'] = user_data['weight'] / (user_data['height'] / 100) ** 2


    if user_data['BMI Category'] == 'Underweight':
        recommendations.append("Votre IMC indique que vous êtes en sous-poids. Envisagez de consulter un nutritionniste pour un régime équilibré.")
    elif user_data['BMI Category'] == 'Overweight':
        recommendations.append("Votre IMC indique que vous êtes en surpoids. Une activité physique régulière et une alimentation saine peuvent aider.")
    elif user_data['BMI Category'] == 'Obese':
        recommendations.append("Votre IMC indique que vous êtes obèse. Il est important de consulter un professionnel de la santé pour un plan de gestion de poids.")
    if user_data['steps'] < 5000:
        recommendations.append("Votre nombre de pas quotidien est faible. Essayez d'augmenter votre activité quotidienne pour améliorer votre sommeil.")
    elif user_data['steps'] <= 10000:
        recommendations.append("Votre nombre de pas quotidien est modéré. Continuez à maintenir cette activité pour un bon sommeil.")
    else:
        recommendations.append("Votre nombre de pas quotidien est élevé. Assurez-vous de bien vous reposer pour éviter le surentraînement.")

    if user_data['physical_activity'] < 30:
        recommendations.append("Votre niveau d'activité physique est faible. Essayez d'augmenter votre activité quotidienne pour améliorer votre sommeil.")
    elif user_data['physical_activity'] <= 60:
        recommendations.append("Votre niveau d'activité physique est modéré. Continuez à maintenir une activité régulière pour un bon sommeil.")
    else:
        recommendations.append("Votre niveau d'activité physique est élevé. Assurez-vous de bien vous reposer pour éviter le surentraînement.")

    if user_data['age'] < 30:
        recommendations.append("À votre âge, il est important de maintenir une activité physique régulière et une alimentation saine.")
    elif user_data['age'] >= 30 and user_data['age'] <= 45:
        recommendations.append("À votre âge, essayez de trouver un équilibre entre travail, activité physique et repos.")
    else:
        recommendations.append("À votre âge, une attention particulière à la gestion du stress et une alimentation équilibrée sont importantes.")
    return recommendations



def provide_detailed_recommendations_nutrition(user_data):
    recommendations = []
    if user_data['fcvc'] == 1:
        recommendations.append("Tu indiques ne jamais consommer de légumes ?! Pour prévenir tout risque de surpoids, c'est important de consommer environ 5 fruits et légumes par jour. Essaye petit à petit d'inclure des fruits et des légumes dans ton alimentation. Tu n'en seras que satisfait je te le promet ! ;)")
    if user_data['fcvc'] == 2:
        recommendations.append("Tu indiques consommer de temps en temps des légumes. C'est un bon début ! Si tu veux être vraiment en mode 'perfect', augmente ta consommation à 5 fruits et légumes par jour. Tu ne le regretteras pas, ton corps te le rendra, promis !")
    if user_data['fcvc'] == 3:
        recommendations.append("Tu consommes très souvent des fruits et des légumes ! Félicitations ! Continues comme ça !")
    if user_data['ch2o'] == 1:
        recommendations.append("Tu bois moins d'un litre d'eau par jour ? C'est insuffisant pour rester bien hydraté. Essaye d'augmenter ta consommation d'eau à au moins 1,5 litres par jour.")
    if user_data['ch2o'] == 2:
        recommendations.append("Tu consommes environ deux litres d'eau par jour, ce qui est un bon niveau d'hydratation. Continues sur cette voie pour garder une bonne santé.")
    if user_data['ch2o'] == 3:
        recommendations.append("Super ! Tu bois plus de deux litres d'eau par jour. C'est excellent pour ta santé et ton métabolisme.")
    if user_data['ncp'] == 1:
        recommendations.append("Tu prends moins que le nombre recommandé de repas principaux, ce qui peut affecter ton métabolisme. Essaye de manger régulièrement 3 repas par jour.")
    elif user_data['ncp'] == 2:
        recommendations.append("Deux repas principaux par jour peuvent suffire si tu manges à ta faim, mais assures-toi d'intégrer suffisamment de nutriments.")
    elif user_data['ncp'] == 3:
        recommendations.append("Trois repas par jour est un bon rythme, assures-toi qu'ils sont bien équilibrés.")
    elif user_data['ncp'] == 4:
        recommendations.append("Prendre quatre repas principaux par jour est parfait si tu répartis bien ton apport calorique tout au long de la journée.")
    return recommendations


def provide_detailed_recommendations_stress(user_data):
    recommendations = []
    
    # Temps passé à l'intérieur
    if user_data['Days_Indoors'] == "1-14":
        recommendations.append("Vous indiquez passer entre 1 et 14 jours à l'intérieur. Essayez de sortir plus souvent pour profiter de l'air frais et de la lumière naturelle.")
    if user_data['Days_Indoors'] == "15-30":
        recommendations.append("Vous passez beaucoup de temps à l'intérieur. Essayez de trouver un équilibre en sortant pour des activités extérieures.")
    if user_data['Days_Indoors'] == "31-60":
        recommendations.append("Vous passez entre 31 et 60 jours à l'intérieur. Cela peut affecter votre santé mentale. Augmentez vos activités en plein air.")
    if user_data['Days_Indoors'] == "More than 60":
        recommendations.append("Vous passez plus de 60 jours à l'intérieur. Il est crucial pour votre santé mentale de sortir plus souvent.")

    # Changements d'habitudes
    if user_data['Changes_Habits'] == "Yes":
        recommendations.append("Vous avez récemment changé vos habitudes. Essayez de maintenir ces changements positifs et de vous adapter lentement.")
    elif user_data['Changes_Habits'] == "No":
        recommendations.append("Vous n'avez pas changé vos habitudes récemment. Peut-être envisager de nouvelles habitudes saines pourrait être bénéfique.")
    elif user_data['Changes_Habits'] == "Maybe":
        recommendations.append("Vous n'êtes pas sûr des changements d'habitudes. Prenez le temps d'évaluer vos habitudes actuelles et d'envisager des ajustements positifs.")

    # Intérêt pour le travail
    if user_data['Work_Interest'] == "Yes":
        recommendations.append("Vous êtes intéressé par votre travail. Continuez à trouver des aspects positifs dans votre travail pour maintenir votre intérêt.")
    elif user_data['Work_Interest'] == "No":
        recommendations.append("Vous n'êtes pas intéressé par votre travail actuellement. Peut-être essayer de trouver des projets ou des tâches qui suscitent votre intérêt.")

    # Faiblesses sociales
    if user_data['Social_Weakness'] == "Yes":
        recommendations.append("Vous ressentez des faiblesses sociales. Essayer de participer à des activités sociales ou de rejoindre des groupes peut aider.")
    elif user_data['Social_Weakness'] == "No":
        recommendations.append("Vous ne ressentez pas de faiblesses sociales. Continuez à interagir socialement pour maintenir votre bien-être.")
    elif user_data['Social_Weakness'] == "Maybe":
        recommendations.append("Vous n'êtes pas sûr des faiblesses sociales. Essayez d'évaluer vos interactions sociales et d'envisager des moyens de les améliorer.")

    # Historique de santé mentale
    if user_data['Mental_Health_History'] == "Yes":
        recommendations.append("Vous avez des antécédents de problèmes de santé mentale. Il est important de continuer à surveiller votre bien-être mental et de chercher de l'aide si nécessaire.")
    elif user_data['Mental_Health_History'] == "No":
        recommendations.append("Vous n'avez pas d'antécédents de problèmes de santé mentale. Continuez à prendre soin de votre santé mentale pour prévenir tout problème futur.")
    elif user_data['Mental_Health_History'] == "Maybe":
        recommendations.append("Vous n'êtes pas sûr de votre historique de santé mentale. Il peut être utile de parler à un professionnel pour clarifier cela.")

    return recommendations