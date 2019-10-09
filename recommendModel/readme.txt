###

10.9.2019 -- Gehua

###

RUN main.py for test

###

model.py

1. function explain:
    () __init__: class input: user_id, dababasePath, location (list of 4 elements [min lati, max lati, min longi, max longi])
    () hyper_param: setup model hyper parameters here
    () open_connect: open connection to DB
    () closeConn: close connection to DB
    () locateRestrict：restrict location
    () timeRestrict: If "hours" == None, skip.
    () read_user: no input required, take self.user_info as default input. Return all user information in DB.
    () read_review: no input required, take self.user_info as default input. Return all user reviews in DB.
    () read_business: two bool input, boolTime == True: restrict time, boolLocate == True: restrict location. Returns all restaurant information based on condition selected.
    () define_user: define if it's new user or not. If register date <=10 and review Number <=2: regard as new user. Then run corresponding models.
    () user_filter: for old users.
    () content_filter: for new users.
    () hybrid_filter:
    () hottag_filter:
    () contentFilter:
    () similarity: Calculate similarity.

2. Need to update:
    () similarity: now only use people's average stars to meaure.
    () similarity: now use 1-D distance, ie, X-Y to measure. (maybe quantile?)
    () similarity: now use min-max normalize to [0,1]. Maybe other methods
    () define user: how to define a new user?

3. Speeeeeed up:

    () Only select useful columns instead of all information?

