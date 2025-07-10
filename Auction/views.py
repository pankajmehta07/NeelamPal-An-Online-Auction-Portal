from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .db_utils import get_connection
# Create your views here.

def get_users(request):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # so you get dict results

    cursor.execute("SELECT id, name FROM users")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return JsonResponse(rows, safe=False)

def home(request):
    return HttpResponse("This is home page.")

def search(request):
    return HttpResponse("This is search page.")

def login(request):
    return HttpResponse("This is login page.")

def signup(request):
    return HttpResponse("This is signup page.")