#from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def homepage(request):
    return render(request, 'home.html')


@login_required
def about(request):
    #return HttpResponse("This is the about page.")
    return render(request, 'about.html')
