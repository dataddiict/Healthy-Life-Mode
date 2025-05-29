from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User as DjangoUser
from .models import UserProfile, FollowDataUser, update_user_profile, predict_sleep_disorder, predict_obesity, predict_stress, get_user_by_id, update_Last_Prediction_text
import json

# 🔒 API d'inscription
@csrf_exempt
def inscription(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('pseudo')
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')

            user = DjangoUser.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            update_user_profile(sender=DjangoUser, instance=user, created=True)

            return JsonResponse({'success': True, 'message': 'Utilisateur créé avec succès'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

# 🔒 API de connexion
@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            user = DjangoUser.objects.filter(email=email).first()
            if user:
                auth_user = authenticate(request, username=user.username, password=password)
                if auth_user:
                    login(request, auth_user)
                    return JsonResponse({'success': True, 'message': 'Connexion réussie !'})
            return JsonResponse({'success': False, 'error': 'Email ou mot de passe incorrect.'}, status=401)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

# 🔒 API de déconnexion
@csrf_exempt
def api_logout(request):
    logout(request)
    return JsonResponse({'success': True, 'message': 'Déconnexion réussie !'})

# 🔒 API user profile (JSON)
@csrf_exempt
@login_required
def api_user_profile(request):
    try:
        user = request.user
        profile = UserProfile.objects.get(user=user)
        profile_data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'age': profile.age,
            'sexe': profile.sexe,
            'height': profile.height,
            'weight': profile.weight,
            'steps': profile.steps,
            'sleep_quality': profile.sleep_quality,
            'sleep_duration': profile.sleep_duration,
            'physical_activity': profile.physical_activity,
            'stress_level': profile.stress_level,
            'fcvc': profile.fcvc,
            'ncp': profile.ncp,
            'ch2o': profile.ch2o,
            'Days_Indoors': profile.Days_Indoors,
            'Changes_Habits': profile.Changes_Habits,
            'Work_Interest': profile.Work_Interest,
            'Social_Weakness': profile.Social_Weakness,
            'Mental_Health_History': profile.Mental_Health_History,
            'Last_sleep_prediction': profile.Last_sleep_prediction,
            'Last_obesity_prediction': profile.Last_obesity_prediction,
            'Last_stress_prediction': profile.Last_stress_prediction,
            'Last_Prediction_text': profile.Last_Prediction_text,
        }
        return JsonResponse({'success': True, 'profile': profile_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# 🔒 API user count
@csrf_exempt
def api_user_count(request):
    count = DjangoUser.objects.count()
    return JsonResponse({'user_count': count})

# 🔒 Page profil (HTML)
@login_required
def user_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    history = FollowDataUser.objects.filter(user=request.user).order_by('updated_at')
    return render(request, 'profile.html', {'profile': user_profile, 'history': history, 'user': request.user})
