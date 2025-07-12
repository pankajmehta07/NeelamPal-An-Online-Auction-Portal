import mysql.connector
from django.conf import settings

def get_connection():
    return mysql.connector.connect(
        host=settings.DATABASE['default']['HOST'],
        user=settings.DATABASE['default']['USER'],
        password=settings.DATABASE['default']['PASSWORD'],
        database=settings.DATABASE['default']['NAME'],
        port=settings.DATABASE['default']['PORT'],
    )

def create_tables():
    conn = get_connection()
    cursor = conn.cursor() 

    cursor.execute("CREATE TABLE IF NOT EXISTS organization(reg_no INT PRIMARY KEY, name VARCHAR(100), address VARCHAR(100),contact INT NOT NULL)") 
    cursor.execute("CREATE TABLE IF NOT EXISTS bidder(citizenship_no INT PRIMARY KEY, name VARCHAR(100), address VARCHAR(100), contact INT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS item(id INT AUTO_INCREMENT PRIMARY KEY, category VARCHAR(50), min_bid_amt INT CHECK(min_bid_amt >0), organization_id INT, FOREIGN KEY(organization_id) REFERENCES organization(reg_no),bid_start_time TIMESTAMP, bid_end_time TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS bid(id INT AUTO_INCREMENT PRIMARY KEY, created_at TIMESTAMP,item_id INT,FOREIGN KEY(item_id) REFERENCES item(id), bidder_id INT, FOREIGN KEY(bidder_id) REFERENCES bidder(citizenship_no), amount INT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS highest_bid(item_id INT, bid_id INT, FOREIGN KEY(item_id) REFERENCES item(id),FOREIGN KEY(bid_id) REFERENCES bid(id))")
  
    cursor.close()
    conn.close()

