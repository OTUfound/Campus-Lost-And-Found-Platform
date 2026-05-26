#from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def homepage(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')

