from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import logout,login, authenticate
from django.contrib.auth.hashers import make_password
from .utils import *
from django.db import connection
import re
import os
from datetime import datetime, timedelta
from django.conf import settings
from .templatetags.custom_filters import auctionStatus
import cloudinary.uploader
# Create your views here.

def profile(request, id, profile_type):
    params = {}
    if profile_type == "organization":
        params['profile'] = runQuery('''SELECT * from organization
                WHERE reg_no = %s''',[id])
    elif profile_type == "bidder":
        params['profile'] = runQuery('''SELECT * from bidder
                WHERE citizenship_no = %s''',[id])
    else:
        return redirect("/")
    
    if not params['profile']:
        messages.error(request, "❌ Profile not found")
        return redirect("/")
    params['type'] = profile_type
    return render(request,"Auction/profile.html", params)
    

def editProfile(request):
    if request.user.is_authenticated and request.method == 'GET':
        user = request.user
        params = {}

        if user.user_type == "Organization":
            profile = runQuery("SELECT reg_no, name, address, contact FROM organization WHERE reg_no =",[user.id])
        else:
            profile = runQuery("SELECT citizenship_no, name, address, contact FROM bidder WHERE citizenship_no = ", [user.id])

        if not profile:
            messages.error(request, "❌Profile not found.")
            return redirect('/')

        params['profile'] = profile
        return render(request, 'Auction/editProfile.html', params)
    messages.success(request, "✅Profile updated successfully.")
    return redirect('/')   

def home(request):
    param = {}
    timestamp = getTimestamp().strftime('%Y-%m-%d %H:%M:%S')
    # Active items
    param['itemData'] = runQuery('''SELECT item.id, item.name, item.category, item.min_bid_amt, organization.name, 
                   item.bid_start_time, item.bid_end_time, item.description, bidInfo.amount,
                   EXTRACT(EPOCH FROM (item.bid_end_time - %s::timestamp))::int AS time_remaining, item.fileurl,organization.reg_no 
                   FROM item 
                   JOIN organization 
                   ON item.organization_id = organization.reg_no 
                   LEFT JOIN (SELECT highest_bid.item_id, bid.amount 
                   FROM highest_bid join bid ON 
                   highest_bid.bid_id = bid.id) AS bidInfo 
                   ON item.id = bidInfo.item_id 
                   WHERE item.bid_start_time <= %s and item.bid_end_time > %s ORDER BY time_remaining limit 5''',
                   [timestamp, timestamp, timestamp])
    
    param['winner'] = runQuery(''' SELECT highest_bid.item_id, item.name, bid.bidder_id FROM highest_bid 
                               JOIN item ON item.id = highest_bid.item_id
                               JOIN bid ON highest_bid.bid_id = bid.id
                               ORDER BY bid.created_at DESC
                               LIMIT 18 ''')
    return render(request,"Auction/index.html", param)

def search(request):
    searchTerm = request.GET.get('search')
    params = {}
    params['searchResults'] = runQuery('''SELECT item.id, item.name, item.min_bid_amt, 
                   item.bid_start_time, item.fileurl
                   FROM item
                   where item.name like '%%s%' or item.category like '%%s%' limit 20 ''', [searchTerm,searchTerm])


    return render(request,"Auction/search.html", params)

def showBids(request):    
    if request.user.is_authenticated and request.user.user_type == "Bidder":
        params = {}
        timestamp = getTimestamp()
        params['itemData'] = runQuery('''SELECT DISTINCT item.id, item.name, item.min_bid_amt, 
                    item.bid_start_time, item.fileurl, item.bid_end_time, bidInfo.amount,
                    EXTRACT(EPOCH FROM (item.bid_end_time - %s::timestamp))::int AS time_remaining, bidInfo.bidder_id, bids.amount
                   FROM item 
                   JOIN (SELECT DISTINCT ON (bid.item_id) bid.item_id, bid.amount, bid.bidder_id 
                FROM bid WHERE bidder_id = %s ORDER BY bid.item_id, bid.amount DESC) as bids
                   ON item.id = bids.item_id
                   LEFT JOIN (SELECT highest_bid.item_id, bid.bidder_id, bid.amount 
                   FROM highest_bid join bid ON 
                   highest_bid.bid_id = bid.id) AS bidInfo 
                   ON item.id = bidInfo.item_id ORDER BY item.bid_end_time DESC
                   ''', [timestamp, request.user.id])
        return render(request,"Auction/myBids.html", params)    
        
    messages.error(request, "❌Invalid request")
    return redirect("/")

def showItems(request):
    if request.user.is_authenticated and request.user.user_type == "Organization":
        params = {}
        timestamp = getTimestamp()
        params['itemData'] = runQuery('''SELECT item.id, item.name, item.min_bid_amt, 
                    item.bid_start_time, item.fileurl, item.bid_end_time, bidInfo.amount,
                    EXTRACT(EPOCH FROM (item.bid_end_time - %s::timestamp))::int AS time_remaining
                   FROM item 
                   JOIN organization 
                   ON item.organization_id = organization.reg_no 
                   LEFT JOIN (SELECT highest_bid.item_id, bid.amount 
                   FROM highest_bid join bid ON 
                   highest_bid.bid_id = bid.id) AS bidInfo 
                   ON item.id = bidInfo.item_id 
                   WHERE item.organization_id = %s
                   ORDER BY item.bid_end_time DESC''', [timestamp, request.user.id])
        
        return render(request,"Auction/showItems.html", params)    
    messages.error(request, "❌Invalid request")
    return redirect("/")

def bid(request):
    if request.method == 'POST':
        try:
            bid_amount = int(request.POST.get('bid_amount'))
            item_id = int(request.POST.get('item_id'))
        except:
            messages.error(request, "❌Invalid bid amount.")
            return redirect('item',itemID = item_id)
        highest = runQuery("SELECT * FROM highest_bid WHERE item_id = %s", [item_id])
        if highest:
            bid_id = highest[0][1]
            current_bid = runQuery("SELECT amount FROM bid WHERE id = %s",[bid_id])[0][0]

        else:
             current_bid = runQuery("SELECT min_bid_amt FROM item WHERE id = %s", [item_id])[0][0]
        
        if bid_amount <= current_bid:
            messages.error(request, "❌Bid amount must be higher than current bid amount.")
            return redirect('item',itemID = item_id)
        
        timestamp = getTimestamp().strftime('%Y-%m-%d %H:%M:%S')
        runQuery(''' INSERT INTO bid (created_at, item_id, bidder_id, amount)
            VALUES (%s, %s, %s, %s)''',
            [timestamp, item_id, request.user.id, bid_amount])
        
        bid_id = runQuery("SELECT id FROM bid WHERE item_id = %s ORDER BY amount DESC LIMIT 1", [item_id])[0][0]
        
        if highest:
            runQuery("UPDATE highest_bid SET bid_id =%s WHERE item_id =%s",[bid_id, item_id] )

        else:
            runQuery("INSERT INTO highest_bid VALUES(%s,%s)",[item_id, bid_id] )
        
        messages.success(request, "✅Bid placed successfully.")
        return redirect('item',itemID = item_id)

    return render(request, "Auction/bid.html", {'item': item})

def createTables(request): 
    create_tables()
    messages.success(request, "✅Tables created successfully")
    return redirect('home')

def addItem(request): 
    if request.user.is_authenticated and request.user.user_type == "Organization":
        return render(request,"Auction/add_item.html")
    
    messages.error(request, "❌Invalid request")
    if not request.user.is_authenticated:
        return redirect('/#login')

    return redirect('/')

def category(request):
    param = {}
    timestamp = getTimestamp()
    timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    param['activeItemData'] = runQuery('''SELECT item.id, item.name, item.min_bid_amt, bidInfo.amount,
                   EXTRACT(EPOCH FROM (item.bid_end_time - %s::timestamp))::int AS time_remaining, item.fileurl
                   FROM item 
                   LEFT JOIN (SELECT highest_bid.item_id, bid.amount 
                   FROM highest_bid join bid ON 
                   highest_bid.bid_id = bid.id) AS bidInfo 
                   ON item.id = bidInfo.item_id 
                   WHERE item.bid_start_time <= %s and item.bid_end_time > %s order by time_remaining''',
                   [timestamp, timestamp, timestamp])
    # Upcoming items
    param['upcomingItemData'] = runQuery('''SELECT item.id, item.name, item.min_bid_amt, 
                   item.bid_start_time, item.fileurl
                   FROM item
                   WHERE item.bid_start_time > %s order by item.bid_start_time limit 6''', [timestamp])
    # Closed items
    param['endedItemData'] = runQuery('''SELECT item.id, item.name, 
                   item.bid_end_time, bidInfo.amount, item.fileurl, item.min_bid_amt
                   FROM item 
                   LEFT JOIN (SELECT highest_bid.item_id, bid.amount 
                   FROM highest_bid join bid ON 
                   highest_bid.bid_id = bid.id) AS bidInfo 
                   ON item.id = bidInfo.item_id 
                   WHERE item.bid_end_time <= %s order by item.bid_end_time desc limit 6''',[timestamp])

    return render(request, "Auction/category.html", param)

def saveItem(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.user_type == "Organization":
        # Extract fields from POST
        name = request.POST.get('name')[:100]
        min_bid_amt = request.POST.get('min_bid_amount')
        category = request.POST.get('category')[:50]
        description = request.POST.get('description')[:500]
        start_time_str = request.POST.get('start_time')  
        end_time_str = request.POST.get('end_time')
        image = request.FILES.get('item_image')
        filename = image.name

        filename = filename.split(".")
        if(filename[-1] not in ['jpg','jpeg', 'png']):
            messages.error(request, "❌Unsupported image file type. You can only upload jpg, jped or png images")
            return redirect('addItem')
        filename = filename[0][:19] + str(datetime.now())
        filename = filename.replace("-",'')
        filename = filename.replace(":",'')
        filename = filename.replace(" ",'')
        filename = filename.replace(".",'')
        result = cloudinary.uploader.upload(
            image,
            folder='item_images/',
            public_id = filename,
            overwrite=True,
            resource_type="image"
        )
        image_url = result['secure_url']
        public_id = result['public_id']

        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M")

        min_end_time = start_time + timedelta(minutes=60)

        if end_time < min_end_time:
            messages.error(request, "❌Start and end time must be at least 60 minutes apart")
            return redirect('addItem')


        if not all([name, min_bid_amt, category, start_time_str, end_time_str]):
            messages.error(request, "❌Please fill all required fields.")
            return redirect('addItem')
        


        data = runQuery("SELECT 1 FROM item WHERE name = %s and organization_id = %s", [name, request.user.id])
        if data:
            messages.error(request, "❌Item already exists")
            return redirect('addItem')
        
        start_time_str = start_time_str.replace("T"," ")+":00"
        end_time_str = end_time_str.replace("T"," ")+":00"
        runQuery('''INSERT INTO item(name, category, description, min_bid_amt,
                       organization_id, bid_start_time, bid_end_time, fileurl, fileid) 
                       VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s)''',[name,category,description,min_bid_amt,
                       request.user.id,start_time_str,end_time_str, image_url,public_id])
        

        messages.success(request, "✅Item was added successfully.")
        return redirect('addItem')

    else:
        messages.error(request, "❌Invalid request")
        return redirect('/')   
    
def updateItem(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.user_type == "Organization":
        # Extract fields from POST
        name = request.POST.get('name')[:100]
        item_id = request.POST.get('item_id')
        min_bid_amt = request.POST.get('min_bid_amount')
        category = request.POST.get('category')[:50]
        description = request.POST.get('description')[:500]
        start_time_str = request.POST.get('start_time')  
        end_time_str = request.POST.get('end_time')
        image = request.FILES.get('item_image')
        
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M")

        min_end_time = start_time + timedelta(minutes=60)

        if not item_id:
            messages.error(request, "❌Invalid Request.")
            return redirect('home')

        if end_time < min_end_time:
            messages.error(request, "❌Start and end time must be at least 60 minutes apart")
            return redirect('item',itemID = item_id)


        data = runQuery("SELECT * FROM item WHERE id = %s and organization_id = %s",[item_id, request.user.id])[0]
        if not data:
            messages.error(request, "❌Item doesn't exist")
            return redirect('item',itemID = str(item_id).strip())
        
        name = name or data[1]
        min_bid_amt = min_bid_amt or data[4]
        category = category or data[2]
        description = description or data[3]
        start_time = start_time or data[7]
        end_time = end_time or data[8]

        if image:
            filename = image.name
            filename = filename.split(".")
            if(filename[-1] not in ['jpg','jpeg', 'png']):
                messages.error(request, "❌Unsupported image file type. You can only upload jpg, jped or png images")
                return redirect('item',itemID = str(item_id).strip())
            filename = filename[0][:19] + str(datetime.now())
            filename = filename.replace("-",'')
            filename = filename.replace(":",'')
            filename = filename.replace(" ",'')
            filename = filename.replace(".",'')
            result = cloudinary.uploader.upload(
                image,
                folder='item_images/',
                public_id = filename,
                overwrite=True,
                resource_type="image"
            )
            image_url = result['secure_url']
            public_id = result['public_id']
            try:
                result = cloudinary.uploader.destroy(data[9], invalidate=True)
                print(result)
            except Exception as e:
                pass      
        
        else:
            image_url = data[6]
            public_id = data[9]
        
        start_time_str = start_time_str.replace("T"," ")+":00"
        end_time_str = end_time_str.replace("T"," ")+":00"
        runQuery('''UPDATE item set name=%s, category=%s, description=%s, 
                 min_bid_amt=%s,organization_id=%s, bid_start_time=%s, 
                 bid_end_time=%s, fileurl=%s, fileid=%s WHERE id=%s''',
                 [name, category, description, min_bid_amt, request.user.id,start_time_str,end_time_str,image_url, public_id, item_id])
        

        messages.success(request, "✅Item was updated successfully.")
        return redirect('item',itemID = str(item_id).strip())

    else:
        messages.error(request, "❌Invalid request")
        return redirect('/')   

def item(request, itemID):
    params = {}
    timestamp = getTimestamp()    
    timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    params['item'] = runQuery('''SELECT item.id, item.name, item.category, item.min_bid_amt, organization.name, 
                   item.bid_start_time, item.bid_end_time, item.description, bidInfo.amount,
                   EXTRACT(EPOCH FROM (item.bid_end_time - %s::timestamp))::int AS time_remaining, item.fileurl, organization.reg_no, bidInfo.bidder_id
                   FROM item 
                   JOIN organization 
                   ON item.organization_id = organization.reg_no 
                   LEFT JOIN (SELECT highest_bid.item_id, bid.amount, bid.bidder_id 
                   FROM highest_bid join bid ON 
                   highest_bid.bid_id = bid.id) AS bidInfo 
                   ON item.id = bidInfo.item_id 
                   WHERE item.id = %s''', [timestamp, itemID])[0]
    params['bid'] = runQuery("SELECT bid.amount, bid.bidder_id FROM bid where item_id = %s ORDER BY created_at DESC LIMIT 1", [itemID])
    params['status'] = auctionStatus(params['item'][5],params['item'][6])
    return render(request, "Auction/itemDetails.html", params) 

def deleteItem(request):
    if request.user.is_authenticated and request.user.user_type == "Organization" and request.method =='POST':
        itemID = request.POST.get('item_id')
        data = runQuery('''SELECT id, bid_start_time, bid_end_time, organization_id, fileid
                    FROM item
                    WHERE id = %s''',[itemID])[0]
                
        if request.user.id == data[3]:
            if auctionStatus(data[1], data[2]) == "Upcoming":
                if  runQuery("SELECT * from highest_bid where item_id=%s",[itemID]):
                    messages.error(request, "❌Item which already have bids cannot be deleted")   
                    return redirect('home')
                try:
                    cloudinary.uploader.destroy(data[4])
                except Exception as e:
                    pass
                
                runQuery('''DELETE FROM item where id=%s''',[itemID])
                messages.success(request, "✅Deletion Successfull")
            else:
                messages.error(request, "❌Only items with auction status 'upcoming' can be deleted")
        else:
            messages.error(request, "❌Invalid Request!!!")
        return redirect('home')
    messages.error(request, "❌Invalid Request!!!")
    return redirect('home')

def edit(request):
    if request.user.is_authenticated and request.user.user_type == "Organization" and request.method =='POST':
        itemID = request.POST.get('item_id')
        params = {}
        timestamp = getTimestamp()    
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        params['item'] = runQuery('''SELECT item.id, item.name, item.category, item.min_bid_amt, 
                    item.bid_start_time, item.bid_end_time, item.description, bidInfo.amount,
                    EXTRACT(EPOCH FROM (item.bid_end_time - %s::timestamp))::int AS time_remaining, item.fileurl, organization.reg_no
                    FROM item 
                    JOIN organization 
                    ON item.organization_id = organization.reg_no 
                    LEFT JOIN (SELECT highest_bid.item_id, bid.amount 
                    FROM highest_bid join bid ON 
                    highest_bid.bid_id = bid.id) AS bidInfo 
                    ON item.id = bidInfo.item_id 
                    WHERE item.id = %s''', [timestamp, itemID])[0]
        if request.user.id == params['item'][10]:
            return render(request, "Auction/editItem.html", params) 
        else:
            messages.error(request, "❌Invalid Request!!!")
            return redirect('/')
    messages.error(request, "❌Invalid Request!!!")
    return redirect('/')

def logout_user(request):
    if request.method == 'POST':
        logout(request)
        request.session.pop('user_id', None)
        request.session.pop('user_type', None)
        messages.success(request, "✅Log out successful.")
    else:
        messages.error(request, "❌Invalid Request.")
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')[:100]
        contact = re.sub(r'\D', '',request.POST.get('contact'))
        address = request.POST.get('address')[:100]
        user_type = request.POST.get('userType')
        username = re.sub(r'\D', '', request.POST.get('usernameInput'))
        password = request.POST.get('password')

        if not all([username, password, name, contact, address]):
            messages.error(request, "❌Please fill all required fields.")
            return redirect('/')

        with connection.cursor() as cursor:
            if user_type=="Organization":
                cursor.execute("SELECT reg_no FROM organization WHERE reg_no = %s", [username])
            else:
                cursor.execute("SELECT citizenship_no FROM bidder WHERE citizenship_no = %s", [username])
            
            if cursor.fetchone():
                messages.error(request, "❌Username already exists.")
                return redirect('/')

            hashed_password = make_password(password)

            if user_type=="Organization":
                messages.success(request, "✅Registration successful. Please use registration number as username for log in.")
                runQuery("INSERT INTO organization VALUES(%s,%s, %s, %s, %s)",
                         [username, name, address, contact, hashed_password])
            else:
                messages.success(request,"✅Registration successful. Please use citizenship number as username for log in.")
                runQuery("INSERT INTO bidder VALUES(%s,%s, %s, %s, %s)",
                         [username, name, address, contact, hashed_password])
        
        return redirect('/')

    else:
        messages.error(request, "❌Invalid request")
        return redirect('/')

def login_user(request):
    if request.method == "POST":
        username = re.sub(r'\D', '', request.POST.get('username'))
        password = request.POST.get('password')
        user_type = request.POST.get('userType')

        if not username or not password or not user_type or (user_type!="Organization" and user_type != "Bidder"):
            messages.error(request, "❌Invalid credentials.")
            return redirect('/#login')

        user = authenticate(request, username=username, password=password, user_type=user_type)

        if user:
            login(request, user, backend='your_app.auth_backend.RawSQLAuthBackend')
            request.session['user_id'] = user.id
            request.session['user_type'] = user_type
            request.session.modified = True
            messages.success(request, "✅Log in successful.")
            return redirect('home')
        else:
            messages.error(request, "❌Invalid credentials.")
            return redirect('home')
    messages.error(request, "❌Only POST requests are allowed.")
    return redirect('home')

def updateProfile(request):
    if request.method == 'POST' and request.user.is_authenticated:
        name = request.POST.get('name')[:100]
        contact = re.sub(r'\D', '', request.POST.get('contact'))
        address = request.POST.get('address')[:100]
        password = request.POST.get('password')

        if request.user.user_type == "Organization":
            data = runQuery("SELECT * FROM organization WHERE reg_no = %s",[request.user.id])
        else:
            data = runQuery("SELECT * FROM bidder WHERE citizenship_no = %s",[request.user.id])

        if not data:
            messages.error(request, "❌Unauthorized Request.")
            return redirect('home')

        data = data[0] 

        name = name or data[1]
        address = address or data[2]
        contact = contact or data[3]
        if password:
            hashed_pw = make_password(password)
        else:
            hashed_pw = data[4]
        

        if request.user.user_type == 'Bidder':
            runQuery("""UPDATE bidder SET name = %s, address = %s, 
                     contact %s, password = %s WHERE 
                     citizenship_no = %s""",
                     [name, address, contact, hashed_pw, request.user.id])
        elif request.user.user_type == 'Organization':
            runQuery("""UPDATE organization SET name = %s, address = %s, 
                     contact = %s, password = %s WHERE 
                     reg_no = %s""",
                     [name, address, contact, hashed_pw, request.user.id])

        messages.success(request, "✅Profile updated successfully.")
        return redirect(f'profile/{request.user.user_type.lower()}/{request.user.id}')
    messages.error(request, "❌Unauthorized Request.")
    return redirect('/')

