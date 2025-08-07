import mysql.connector
from django.conf import settings
import platform
from datetime import datetime, timedelta
from django.db import connection

def create_tables():
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS organization(reg_no BIGINT PRIMARY KEY, name VARCHAR(100), address VARCHAR(100),contact BIGINT NOT NULL, password VARCHAR(128) NOT NULL)") 
            cursor.execute("CREATE TABLE IF NOT EXISTS bidder(citizenship_no BIGINT PRIMARY KEY, name VARCHAR(100), address VARCHAR(100), contact BIGINT NOT NULL, password VARCHAR(128) NOT NULL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS item(id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), category VARCHAR(50),description varchar(500), min_bid_amt INT CHECK(min_bid_amt >0), organization_id BIGINT, filename VARCHAR(50), FOREIGN KEY(organization_id) REFERENCES organization(reg_no),bid_start_time TIMESTAMP, bid_end_time TIMESTAMP)")
            cursor.execute("CREATE TABLE IF NOT EXISTS bid(id INT AUTO_INCREMENT PRIMARY KEY, created_at TIMESTAMP,item_id INT,FOREIGN KEY(item_id) REFERENCES item(id), bidder_id BIGINT, FOREIGN KEY(bidder_id) REFERENCES bidder(citizenship_no), amount INT NOT NULL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS highest_bid(item_id INT, bid_id INT, FOREIGN KEY(item_id) REFERENCES item(id),FOREIGN KEY(bid_id) REFERENCES bid(id))")
    except Exception as e:
        return


def getTimestamp():
    if platform.system()=="Linux":
        return datetime.now() + timedelta(hours=5, minutes=45)
    else:
        return datetime.now()

def runQuery(query):
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
            return data
    except Exception as e:
        return

def filter(words):
    words = words.replace("\\", "\\\\")
    words = words.replace("'", "\\'")
    words = words.replace('"', '\\"')
    return words