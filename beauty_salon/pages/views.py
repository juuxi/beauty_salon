from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_not_required


@login_not_required
def register_view(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            if user is not None:
                login(request, user)
                return redirect('pages:index')
    return render(request, 'registration/register.html', {'form': form})
