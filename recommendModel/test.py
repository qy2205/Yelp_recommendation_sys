

import sqlite3
conn = sqlite3.connect('/home/gehua/Desktop/yelp.db/yelp.db')

cursor = conn.execute("SELECT * FROM USER ")

for row in cursor:
    print(row[20])