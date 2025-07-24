from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout,login, authenticate
from .db_utils import *
from django.db import connection
import re
import os
from datetime import datetime, timedelta
from django.conf import settings
# Create your views here.

def get_users(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, username, password FROM auth_user")
        row = cursor.fetchall()

        return JsonResponse(row, safe=False)

def home(request):
    param = {}
    timestamp = getTimestamp().strftime('%Y-%m-%d %H:%M:%S')

    # Active items
    param['itemData'] = runQuery(f'''SELECT item.id, item.name, item.category, item.min_bid_amt, organization.name, 
                   item.bid_start_time, item.bid_end_time, item.description, bidInfo.amount,
                   TIMEDIFF(item.bid_end_time, '{timestamp}') AS time_remaining, item.filename
                   FROM item 
                   JOIN organization 
                   ON item.organization_id = organization.reg_no 
                   LEFT JOIN (SELECT highest_bid.item_id, bid.amount 
                   FROM highest_bid join bid ON 
                   highest_bid.bid_id = bid.id) AS bidInfo 
                   ON item.id = bidInfo.item_id 
                   WHERE item.bid_start_time <= '{timestamp}' and item.bid_end_time > '{timestamp}' limit 5''')

    

    return render(request,"Auction/index.html", param)

def search(request):
    
    data = runQuery("SELECT * from organization")

    return JsonResponse(data, safe=False)


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

def category(request):
    param = {}
    timestamp = getTimestamp()
    timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    param['activeItemData'] = runQuery(f'''SELECT item.id, item.name, item.min_bid_amt, bidInfo.amount,
                   TIMEDIFF(item.bid_end_time, '{timestamp}') AS time_remaining, item.filename
                   FROM item 
                   LEFT JOIN (SELECT highest_bid.item_id, bid.amount 
                   FROM highest_bid join bid ON 
                   highest_bid.bid_id = bid.id) AS bidInfo 
                   ON item.id = bidInfo.item_id 
                   WHERE item.bid_start_time <= '{timestamp}' and item.bid_end_time > '{timestamp}' order by time_remaining limit 18''')
    # Upcoming items
    param['upcomingItemData'] = runQuery(f'''SELECT item.id, item.name, item.min_bid_amt, 
                   item.bid_start_time, item.filename
                   FROM item
                   WHERE item.bid_start_time > '{timestamp}'  order by item.bid_start_time limit 6''')
    # Closed items
    param['endedItemData'] = runQuery(f'''SELECT item.id, item.name, 
                   item.bid_end_time, bidInfo.amount, item.filename, item.min_bid_amt
                   FROM item 
                   LEFT JOIN (SELECT highest_bid.item_id, bid.amount 
                   FROM highest_bid join bid ON 
                   highest_bid.bid_id = bid.id) AS bidInfo 
                   ON item.id = bidInfo.item_id 
                   WHERE item.bid_end_time <= '{timestamp}' order by item.bid_end_time desc limit 6''')

    return render(request, "Auction/category.html", param)

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
        filename = image.name

        filename = filename.split(".")
        filename = filename[0][:19] + str(datetime.now())+"." + filename[-1]
        filename = filename.replace("-",'')
        filename = filename.replace(":",'')
        filename = filename.replace(" ",'')
        file_path = os.path.join(save_dir, filename)
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
        


        data = runQuery(f"SELECT 1 FROM item WHERE name = '{name}' and organization_id = {request.user.username}", )
        if data:
            messages.error(request, "Item already exists")
            return redirect('addItem')
        
        start_time_str = start_time_str.replace("T"," ")+":00"
        end_time_str = end_time_str.replace("T"," ")+":00"
        runQuery(f'''INSERT INTO item(name, category, description, min_bid_amt,
                       organization_id, bid_start_time, bid_end_time, filename) 
                       VALUES('{name}','{category}','{description}',{min_bid_amt},
                       {request.user.username},'{start_time_str}','{end_time_str}', '{filename}')''')
        

        messages.success(request, "Item was added successfully.")
        return redirect('addItem')

    else:
        messages.error(request, "Invalid request")
        return redirect('/')   

def item(request, itemID):
    param = {}
    timestamp = getTimestamp()    
    timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    param['item'] = runQuery(f'''SELECT item.id, item.name, item.category, item.min_bid_amt, organization.name, 
                   item.bid_start_time, item.bid_end_time, item.description, bidInfo.amount,
                   TIMEDIFF(item.bid_end_time, '{timestamp}') AS time_remaining, item.filename
                   FROM item 
                   JOIN organization 
                   ON item.organization_id = organization.reg_no 
                   LEFT JOIN (SELECT highest_bid.item_id, bid.amount 
                   FROM highest_bid join bid ON 
                   highest_bid.bid_id = bid.id) AS bidInfo 
                   ON item.id = bidInfo.item_id 
                   WHERE item.id = {itemID}''')[0]
    
    return render(request, "Auction/itemDetails.html", param) 


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

        if user_type=="Organization":
            messages.success(request, "Registration successful. Please use registration number as username for log in .")
            runQuery(f"INSERT INTO organization VALUES({username},'{name}','{address}',{contact})")
        else:
            messages.success(request,"Registration successful. Please use citizenship number as username for log in .")
            runQuery(f"INSERT INTO bidder VALUES({username},'{name}','{address}',{contact})")
        
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

