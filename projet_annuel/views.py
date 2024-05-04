from django.shortcuts import render
from django.http import HttpResponse
from .models import User


def hello_world(request):
    return render(request, 'index.html')

def connection(request):
    return render(request, 'signin.html')

def inscription(request):
    if request.method == 'POST':
        pseudo = request.POST.get('pseudo')
        mail = request.POST.get('email')
        password = request.POST.get('password')

        # Créer un nouvel utilisateur en utilisant la méthode du modèle
        user = User.create_user(pseudo, mail, password)

        if user:
            # Inscription réussie, rediriger ou afficher un message de succès
            pass
        else:
            # Erreur lors de la création de l'utilisateur, afficher un message d'erreur
            pass
    return render(request, 'signup.html')