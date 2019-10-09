
import sqlite3
import warnings
import pandas as pd
from datetime import datetime


class RecommendModel:

   def __init__(self,userID,dbPath,pos):
      # input: user ID and DB path
      self.userID = userID
      self.dbPath = dbPath
      self.pos = pos
      self.hyper_param()

   def hyper_param(self):
      self.preferThresh = 4

   def open_connect(self):
      # build connection
      self.conn = sqlite3.connect(self.dbPath)

   def close_connect(self):
      # close connection
      self.conn.close()

   def locate_restrict(self):
      return(self.pos)

   def time_restrict(self,hour):
      curWeekday = datetime.today().strftime('%A')
      resWeekday = hour.get(curWeekday)

      # Current Weekday is Open
      if resWeekday != None:
         resHour = [datetime.strptime(x,"%H:%M").time() for x in resWeekday.split("-")]

         # Current Hour is Open
         if resHour[0] < datetime.now().time() < resHour[1]:
            return True

      # All Other Situations are Closed
      return False

   def read_user(self):
      # input: user_id already loaded from class __init__.
      # return: information list.

      cursor = None
      try:
         cursor = self.conn.execute("SELECT * FROM USER WHERE user_id = ? ", (self.userID,))

      finally:
         if cursor is None:
            print("No Such User Query")
            return

         if cursor is not None:
            descript = [x[0] for x in cursor.description]
            row = cursor.fetchall()

            if len(row) > 1:
               # SAFETY CONCERN: Multiple Lines Under Same user_id Warning
               warnings.warn("Multiple Logs For One Same user_id", category=None, stacklevel=1, source=None)

            df = pd.DataFrame(row, columns=descript)
            return df

   def read_review(self,user=True, resID=None):
      cursor = None
      try:
         if user:
            cursor = self.conn.execute("SELECT * FROM REVIEW WHERE user_id = ? ", (self.userID,))
         else:
            cursor = self.conn.execute("SELECT * FROM REVIEW WHERE business_id = ? ", (resID,))

      finally:
         if cursor is None:
            print("No Such Review Query")
            return

         if cursor is not None:
            descript = [x[0] for x in cursor.description]
            row = cursor.fetchall()
            df = pd.DataFrame(row, columns=descript)
            return df

   def read_business(self, boolTime, boolLocate):

      pos = self.locate_restrict() if boolLocate else [-90,90,-180,180]
      cursor = None
      try:
         cursor = self.conn.execute("SELECT * FROM BUSINESS WHERE (latitude BETWEEN ? AND ?)"
                                    "AND (longitude BETWEEN ? AND ?)",(tuple(pos)))
      finally:
         if cursor is None:
            print("No Such Res Query")
            return

         if cursor is not None:
            descript = [x[0] for x in cursor.description]
            row = cursor.fetchall()
            df = pd.DataFrame(row, columns=descript)
            if not boolTime:
               return df
            else:
               openIndex = []
               for i in df.index:
                  hour = df.loc[i]["hours"]
                  if eval(hour) != None:
                     if self.time_restrict(eval(hour)):
                        openIndex.append(i)
               return df.loc[openIndex]

   def test(self):
      self.open_connect()

      self.define_user()


      #df_user=self.read_user()
      #df_review=self.read_review()
      #print(df_user["review_count"])
      #print(df_review["stars"])
      self.close_connect()

   def define_user(self):
      self.open_connect()
      userInfo=self.read_user()
      registDays=(datetime.now()-datetime.strptime(userInfo["yelping_since"].values[0],"%Y-%m-%d %H:%M:%S")).days

      # new user
      if registDays <= 10 and userInfo["review_count"].values[0] <= 2:
         print("New User")
         self.content_filter(userInfo)

      # old user
      else:
         print("Old User")
         self.user_filter(userInfo)

      self.close_connect()
      return

   def user_filter(self, userInfo):
      # user based

      other=[]

      resInfo = self.read_business(False, True)
      userReviewInfo = self.read_review(user=True)
      noReviewRes = resInfo[~resInfo['business_id'].isin(userReviewInfo.get("business_id").values)]

      for noReviewResID in noReviewRes["business_id"].values:
         print(noReviewResID)
         resReviewInfo = self.read_review(user=False,resID=noReviewResID)
         other.append(resReviewInfo["user_id"].values)

      print(len(other))

      if self.prefer(userReviewInfo):
         return
      return


   def prefer(self, reviewInfo):
      # Now we using a simple comparison: stars v.s. threshold
      ## Need Update later, use a weighted avg of #(cool, useful, funny).
      ## Threshold value also need to be calculated based on other restaurant distributions.
      if reviewInfo.get("stars").values[0] > self.preferThresh:
         return True
      return False

   def content_filter(self,userInfo):
      # content based: cold start

      return

   def hybrid_filter(self):
      # hybrid
      return

   def hottag_filter(self):
      ### update later
      return


