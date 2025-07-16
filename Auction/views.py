from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout,login, authenticate
from types import SimpleNamespace
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from .db_utils import get_connection,create_tables
from django.db import connection

# Create your views here.

def get_users(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, username, password FROM auth_user")
        row = cursor.fetchall()
        # cursor = conn.cursor(dictionary=True)  # so you get dict results

        # cursor.execute("SELECT id, name FROM users")
        # rows = cursor.fetchall()

        # cursor.close()
        # conn.close()

        return JsonResponse(row, safe=False)

def home(request):
    param = {'names':['PKMMC', 'Gay', 'Aradhya Dhungel']}
    return render(request,"Auction/index.html", param)

def search(request):
    return HttpResponse("This is search page.")


def signup(request): 
    create_tables()
    return HttpResponse("This is signup page.")

def add_item(request): 
    return render(request,"Auction/add_item.html")


@csrf_exempt
def logout_user(request):
    logout(request)

    messages.success(request, "Log out successful.")
    # For 0 ORM
    # try:
    #     del request.session['_auth_user_id']
    #     del request.session['_auth_user_backend']
    #     if '_manual_auth' in request.session:
    #         del request.session['_manual_auth']
    # except KeyError:
    #     pass

    # return JsonResponse({'message': 'Logout successful'}, status=200)
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        # Extract fields from POST
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        user_type = request.POST.get('userType')  
        
        username = request.POST.get('usernameInput') 
        password = request.POST.get('password')
        print(username, password, name, contact, address, user_type)

        if not all([username, password, name, contact, address]):
            messages.error(request, "Please fill all required fields.")
            return redirect('/')


        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('/')

        # Create user
        user = User.objects.create_user(username=username, password=password)
        user.first_name = name
        user.save()

        if user_type=="Organization":
            msg = "Registration successful. Please use registration number as username for log in ."
        else:
            msg = "Registration successful. Please use citizenship number as username for log in ."

        messages.success(request, msg)
        return redirect('/')

    else:
        messages.error(request, "Invalid request")
        return redirect('/')

    # # Without Using ORM
    # with connection.cursor() as cursor:
    #     # Check if username exists
    #     cursor.execute("SELECT 1 FROM auth_user WHERE username = %s", [username])
    #     if cursor.fetchone():
    #         return JsonResponse({'error': 'User already exists'}, status=400)

    #     # Create user (default values for required fields)
    #     hashed_pw = make_password(password)
    #     cursor.execute("""
    #         INSERT INTO auth_user 
    #         (username, password, is_superuser, is_staff, is_active, date_joined, first_name, last_name, email)
    #         VALUES (%s, %s, 0, 0, 1, CURRENT_TIMESTAMP, '', '', '')
    #     """, [username, hashed_pw])

    # # return JsonResponse({'message': 'User registered successfully'}, status=201)
    # return redirect('home')

def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Log in successful.")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('home')
    messages.error(request, "Only POST requests are allowed.")
    return redirect('home')
        
        # Without Using ORM
        # with connection.cursor() as cursor:
        #     cursor.execute("SELECT id, password FROM auth_user WHERE username = %s", [username])
        #     row = cursor.fetchone()

        # if not row:
        #     return JsonResponse({'error': 'Invalid credentials'}, status=401)

        # user_id, hashed_pw = row
        # if check_password(password, hashed_pw):
        #     # user = User.objects.get(pk=user_id)
        #     # login(request, user)

        #     # For 0 ORM
        #     # ✅ Manually set session values
        #     request.session['_auth_user_id'] = user_id
        #     request.session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
        #     request.session['_manual_auth'] = True  # optional, to mark custom login

        #     return JsonResponse({'message': 'Login successful'}, status=200)
        # else:
        #     return JsonResponse({'error': 'Invalid credentials'}, status=401)