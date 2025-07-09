from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    return HttpResponse("This is home page.")

def search(request):
    return HttpResponse("This is search page.")

def login(request):
    return HttpResponse("This is login page.")

def signup(request):
    return HttpResponse("This is signup page.")