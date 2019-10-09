

model.py

1. function explain:
    1) closeConn: close connection to DB
    2) readData： query specified columns (DB column name) based on user_id
    3）locateRestrict：restrict location
    4) timeRestrict: If "hours" == None, skip.



    3) contentFilter: determine cold start: by registeration date and review_count： registDays <=10 and reviewNumber <=2: regard as new user.
