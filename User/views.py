from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # loguea al usuario automáticamente
            return redirect('index')  # redirige al inicio
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

