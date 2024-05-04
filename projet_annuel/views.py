from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import User
from django.http import HttpResponse
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.decorators import login_required

def connection(request):
    if request.method == 'POST':
        mail = request.POST.get('email')
        password = request.POST.get('password')

        # Vérifier les informations de connexion en utilisant la méthode user_login de la classe User
        user = User.user_login(mail, password)

        if user is not None:
            # Connexion réussie, créer une session pour l'utilisateur
            login(request, user)
            return redirect('user_profile')  # Rediriger vers la page de profil utilisateur
        else:
            # Erreur de connexion, afficher un message d'erreur
            print("Erreur lors de la connexion !")

    return render(request, 'signin.html')


def inscription(request):
    if request.method == 'POST':
        pseudo = request.POST.get('pseudo')
        mail = request.POST.get('email')
        password = request.POST.get('password')
        user = User.create_user(pseudo, mail, password)

        if user:
            # Inscription réussie, rediriger ou afficher un message de succès
            pass
        else:
            # Erreur lors de la création de l'utilisateur, afficher un message d'erreur
            pass
    return render(request, 'signup.html')

@login_required
def user_profile(request):
    # Vérifier si l'utilisateur est connecté
    if request.user.is_authenticated:
        # Récupérer l'utilisateur connecté
        user = request.user

        # Passer l'utilisateur au modèle
        context = {
            'user': user
        }

        # Rendre la page de profil utilisateur
        return render(request, 'profile.html', context)
    else:
        # Si l'utilisateur n'est pas connecté, rediriger vers la page de connexion
        return redirect_to_login(next='user_profile')
    
def hello_world(request):
    return render(request, 'index.html')