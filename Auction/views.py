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
import re
import os
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.conf import settings

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
    param = {}
    conn = get_connection()
    cursor = conn.cursor() 

    cursor.execute("SELECT * from organization") 
    param['organizationData'] = cursor.fetchall()
    cursor.execute("SELECT * from bidder") 
    param['bidderData'] = cursor.fetchall()

    cursor.close()
    conn.close()

    return render(request,"Auction/index.html", param)

def search(request):
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * from organization")
    row = cursor.fetchall()

    cursor.close()
    conn.close()

    return JsonResponse(row, safe=False)


def createTables(request): 
    create_tables()
    messages.success(request, "Tables created successfully")
    return redirect('home')

def addItem(request): 
    if request.user.is_authenticated and request.user.first_name == "Organization":
        return render(request,"Auction/add_item.html")
    
    messages.error(request, "Invalid request")
    if not request.user.is_authenticated:
        return redirect('/#login')

    return redirect('/')

def saveItem(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.first_name == "Organization":
        # Extract fields from POST
        name = request.POST.get('name')
        min_bid_amt = request.POST.get('min_bid_amount')
        category = request.POST.get('category')
        description = request.POST.get('description')
        start_time_str = request.POST.get('start_time')  
        end_time_str = request.POST.get('end_time')
        image = request.FILES.get('item_image')

        save_dir = os.path.join(settings.BASE_DIR,'Auction', 'static', 'Auction', 'images','item_images')   
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, image.name)
        with open(file_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)


        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M")

        min_end_time = start_time + timedelta(minutes=60)

        if end_time < min_end_time:
            messages.error(request, "Start and end time must be at least 60 minutes apart")
            return redirect('addItem')


        if not all([name, min_bid_amt, category, start_time_str, end_time_str]):
            messages.error(request, "Please fill all required fields.")
            return redirect('addItem')
        

        conn = get_connection()
        cursor = conn.cursor() 

        cursor.execute(f"SELECT 1 FROM item WHERE name = '{name}' and organization_id = {request.user.username}", )
        if cursor.fetchone():
            messages.error(request, "Item already exists")
            return redirect('addItem')
        
        start_time_str = start_time_str.replace("T"," ")+":00"
        end_time_str = end_time_str.replace("T"," ")+":00"
        cursor.execute(f"INSERT INTO item(name,category,description,min_bid_amt,organization_id,bid_start_time,bid_end_time) VALUES('{name}','{category}','{description}',{min_bid_amt},{request.user.username},'{start_time_str}','{end_time_str}')")
        
        conn.commit()
        cursor.close()
        conn.close()

        messages.success(request, "Item was added successfully.")
        return redirect('addItem')

    else:
        messages.error(request, "Invalid request")
        return redirect('/')   

def logout_user(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Log out successful.")
    else:
        messages.error(request, "Invalid Request.")

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
        contact = re.sub(r'\D', '',request.POST.get('contact'))
        address = request.POST.get('address')
        user_type = request.POST.get('userType')  
        username = re.sub(r'\D', '', request.POST.get('usernameInput'))
        password = request.POST.get('password')

        if not all([username, password, name, contact, address]):
            messages.error(request, "Please fill all required fields.")
            return redirect('/')


        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('/')

        # Create user
        user = User.objects.create_user(username=username, password=password)
        user.first_name = user_type
        user.save()


        conn = get_connection()
        cursor = conn.cursor() 

        if user_type=="Organization":
            messages.success(request, "Registration successful. Please use registration number as username for log in .")
            cursor.execute(f"INSERT INTO organization VALUES({username},'{name}','{address}',{contact})")
        else:
            messages.success(request,"Registration successful. Please use citizenship number as username for log in .")
            cursor.execute(f"INSERT INTO bidder VALUES({username},'{name}','{address}',{contact})")
        
        conn.commit()
        cursor.close()
        conn.close()
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

