from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import logout,login, authenticate
from django.contrib.auth.hashers import make_password
from .db_utils import *
from django.db import connection
import re
import os
from datetime import datetime, timedelta
from django.conf import settings
# Create your views here.

def profile(request):
    if request.user.is_authenticated:
        params = {}
        if request.user.user_type == "Organization":
            params['profile'] = runQuery(f'''SELECT * from organization
                    WHERE reg_no = {request.user.id}''')
        else:
            params['profile'] = runQuery(f'''SELECT * from bidder
                    WHERE citizenship_no = {request.user.id}''')

        return render(request,"Auction/profile.html", params)
    
    messages.error(request, "Invalid request")
    return redirect("/")

def home(request):
    param = {}
    timestamp = getTimestamp().strftime('%Y-%m-%d %H:%M:%S')

    # Active items
    param['itemData'] = runQuery(f'''SELECT item.id, item.name, item.category, item.min_bid_amt, organization.name, 
                   item.bid_start_time, item.bid_end_time, item.description, bidInfo.amount,
                   TIMESTAMPDIFF(SECOND,'{timestamp}',item.bid_end_time) AS time_remaining, item.filename
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
    searchTerm = request.GET.get('search')
    params = {}
    params['searchResults'] = runQuery(f'''SELECT item.id, item.name, item.min_bid_amt, 
                   item.bid_start_time, item.filename
                   FROM item
                   where item.name like '%{searchTerm}%' or item.category like '%{searchTerm}%' limit 20 ''')


    return render(request,"Auction/search.html", params)

def showItems(request):    
    if request.user.is_authenticated and request.user.user_type == "Organization":
        params = {}
        params['itemData'] = runQuery(f'''SELECT item.id, item.name, item.category, item.min_bid_amt, 
                    organization.name, item.bid_start_time, item.bid_end_time, item.description, 
                    bidInfo.amount, item.filename
                   FROM item 
                   JOIN organization 
                   ON item.organization_id = organization.reg_no 
                   LEFT JOIN (SELECT highest_bid.item_id, bid.amount 
                   FROM highest_bid join bid ON 
                   highest_bid.bid_id = bid.id) AS bidInfo 
                   ON item.id = bidInfo.item_id 
                   WHERE item.organization_id = {request.user.id}''')

        return render(request,"Auction/showItems.html", params)
    
    messages.error(request, "Invalid request")
    return redirect("/")
def bid(request):
    if request.method == 'POST':
        try:
            bid_amount = int(request.POST.get('bid_amount'))
            item_id = int(request.POST.get('item_id'))
        except:
            messages.error(request, "Invalid bid amount.")
            return redirect('item',itemID = item_id)
        highest = runQuery(f"SELECT * FROM highest_bid WHERE item_id = {item_id} ")
        if highest:
            bid_id = highest[0][1]
            current_bid = runQuery(f"SELECT amount FROM bid WHERE id = {bid_id}")[0][0]

        else:
             current_bid = runQuery(f"SELECT min_bid_amt FROM item WHERE id = {item_id}")[0][0]
        
        print(current_bid)
        if bid_amount <= current_bid:
            messages.error(request, "Bid amount must be higher than current bid amount.")
            return redirect('item',itemID = item_id)
        
        timestamp = getTimestamp().strftime('%Y-%m-%d %H:%M:%S')
        runQuery(f''' INSERT INTO bid (created_at, item_id, bidder_id, amount)
            VALUES ('{timestamp}', {item_id}, {request.user.id}, {bid_amount})''')
        
        bid_id = runQuery(f"SELECT id FROM bid WHERE item_id = {item_id} ORDER BY amount DESC LIMIT 1")[0][0]
        print("Highest Bid:",bid_id)
        
        if highest:
            runQuery(f"UPDATE highest_bid SET bid_id ={bid_id} WHERE item_id ={item_id}" )

        else:
            runQuery(f"INSERT INTO highest_bid VALUES({item_id},{bid_id})" )
        
        messages.success(request, "Bid placed successfully.")
        return redirect('item',itemID = item_id)

    return render(request, "Auction/bid.html", {'item': item})

def createTables(request): 
    create_tables()
    messages.success(request, "Tables created successfully")
    return redirect('home')

def addItem(request): 
    if request.user.is_authenticated and request.user.user_type == "Organization":
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
                   TIMESTAMPDIFF(SECOND,'{timestamp}',item.bid_end_time) AS time_remaining, item.filename
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
    if request.method == 'POST' and request.user.is_authenticated and request.user.user_type == "Organization":
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
        


        data = runQuery(f"SELECT 1 FROM item WHERE name = '{name}' and organization_id = {request.user.id}", )
        if data:
            messages.error(request, "Item already exists")
            return redirect('addItem')
        
        start_time_str = start_time_str.replace("T"," ")+":00"
        end_time_str = end_time_str.replace("T"," ")+":00"
        runQuery(f'''INSERT INTO item(name, category, description, min_bid_amt,
                       organization_id, bid_start_time, bid_end_time, filename) 
                       VALUES('{name}','{category}','{description}',{min_bid_amt},
                       {request.user.id},'{start_time_str}','{end_time_str}', '{filename}')''')
        

        messages.success(request, "Item was added successfully.")
        return redirect('addItem')

    else:
        messages.error(request, "Invalid request")
        return redirect('/')   

def item(request, itemID):
    params = {}
    timestamp = getTimestamp()    
    timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    params['item'] = runQuery(f'''SELECT item.id, item.name, item.category, item.min_bid_amt, organization.name, 
                   item.bid_start_time, item.bid_end_time, item.description, bidInfo.amount,
                   TIMESTAMPDIFF(SECOND,'{timestamp}',item.bid_end_time) AS time_remaining, item.filename
                   FROM item 
                   JOIN organization 
                   ON item.organization_id = organization.reg_no 
                   LEFT JOIN (SELECT highest_bid.item_id, bid.amount 
                   FROM highest_bid join bid ON 
                   highest_bid.bid_id = bid.id) AS bidInfo 
                   ON item.id = bidInfo.item_id 
                   WHERE item.id = {itemID}''')[0]
    
    return render(request, "Auction/itemDetails.html", params) 


def logout_user(request):
    if request.method == 'POST':
        logout(request)
        request.session.pop('user_id', None)
        request.session.pop('user_type', None)
        messages.success(request, "Log out successful.")
    else:
        messages.error(request, "Invalid Request.")
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact = re.sub(r'\D', '',request.POST.get('contact'))
        address = request.POST.get('address')
        user_type = request.POST.get('userType')  
        username = re.sub(r'\D', '', request.POST.get('usernameInput'))
        password = request.POST.get('password')

        if not all([username, password, name, contact, address]):
            messages.error(request, "Please fill all required fields.")
            return redirect('/')

        with connection.cursor() as cursor:
            if user_type=="Organization":
                cursor.execute("SELECT reg_no FROM organization WHERE reg_no = %s", [username])
            else:
                cursor.execute("SELECT citizenship_no FROM bidder WHERE citizenship_no = %s", [username])
            
            if cursor.fetchone():
                messages.error(request, "Username already exists.")
                return redirect('/')

            hashed_password = make_password(password)

            if user_type=="Organization":
                messages.success(request, "Registration successful. Please use registration number as username for log in .")
                runQuery(f"INSERT INTO organization VALUES({username},'{name}','{address}',{contact}, '{hashed_password}')")
            else:
                messages.success(request,"Registration successful. Please use citizenship number as username for log in .")
                runQuery(f"INSERT INTO bidder VALUES({username},'{name}','{address}',{contact}, '{hashed_password}')")
        
        return redirect('/')

    else:
        messages.error(request, "Invalid request")
        return redirect('/')

def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('userType')

        if not username or not password or not user_type or (user_type!="Organization" and user_type != "Bidder"):
            messages.error(request, "Invalid credentials.")
            return redirect('/#login')

        user = authenticate(request, username=username, password=password, user_type=user_type)

        if user:
            login(request, user, backend='your_app.auth_backend.RawSQLAuthBackend')
            request.session['user_id'] = user.id
            request.session['user_type'] = user_type
            request.session.modified = True
            messages.success(request, "Log in successful.")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('home')
    messages.error(request, "Only POST requests are allowed.")
    return redirect('home')

