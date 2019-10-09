
import sqlite3
import warnings
import pandas as pd
import numpy as np
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
      self.regisThresh = 10
      self.reviewNumThresh = 2

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

   def read_review(self):
      cursor = None
      try:
         cursor = self.conn.execute("SELECT * FROM REVIEW WHERE user_id = ? ", (self.userID,))

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

   def define_user(self):
      self.open_connect()
      userInfo=self.read_user()
      registDays=(datetime.now()-datetime.strptime(userInfo["yelping_since"].values[0],"%Y-%m-%d %H:%M:%S")).days

      # new user
      if registDays <= self.regisThresh and userInfo["review_count"].values[0] <= self.reviewNumThresh:
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

      otherUserID=[]

      resInfo = self.read_business(False, True)
      userReviewInfo = self.read_review()
      noReviewRes = resInfo[~resInfo['business_id'].isin(userReviewInfo.get("business_id").values)]
      noReviewResID = noReviewRes["business_id"].values

      cursor = self.conn.execute("SELECT user_id FROM REVIEW WHERE business_id IN {} ".format(tuple(noReviewResID)))
      for row in cursor:
         otherUserID.append(row[0])

      # filter out multiple users
      otherUserID=list(set(otherUserID))

      print('Not Reviewed Restaurant Count In This Location: '+str(len(noReviewResID)))
      print('Number of Other People Who Reviewed Those Restaurant: '+str(len(otherUserID)))

      # Prepare this users' similarity w.r.t other users
      dfSimilar = self.similarity(otherUserID, userInfo)

      # Prepare other users' preference on rest of the restaurant
      cursor = self.conn.execute("SELECT stars,user_id,business_id FROM REVIEW WHERE (business_id IN {}) AND (user_id IN {}) ".format(tuple(noReviewResID),tuple(otherUserID)))
      descript = [x[0] for x in cursor.description]
      dfTmp= pd.DataFrame(cursor,columns=descript)
      dfTmp.drop_duplicates(subset="user_id",inplace=True)
      dfPrefer = dfTmp.pivot(index="user_id", columns="business_id", values="stars")
      dfPrefer.fillna(0,inplace=True)
      dfPrefer.sort_index(inplace=True)

      # Matrix multiply to get score
      arrScore=np.dot(np.transpose(dfSimilar.to_numpy()),dfPrefer.to_numpy())
      dfScore=pd.DataFrame(arrScore,columns=dfPrefer.columns,index=["score"])
      print(dfScore.sort_values(by="score", axis=1,ascending=False))


   def similarity(self,otherUserID, userInfo):

      # Need Update Later
      ## Here we use the simplest way:
      ### If people have similar avg_stars, they tend to have similar preference
      cursor = self.conn.execute("SELECT average_stars,user_id FROM USER WHERE user_id IN {} ".format(tuple(otherUserID)))
      descript = [x[0] for x in cursor.description]
      row = cursor.fetchall()
      df = pd.DataFrame(row,columns=descript)
      df.set_index("user_id",inplace=True)
      del df.index.name

      # 1-Dimension distance to measure similarity
      ## Need update later
      starDiff=np.array([x-userInfo["average_stars"].values[0] for x in df["average_stars"].values])

      # min-max normalize to [0,1] then use 1-x use as similarity: the bigger the similar
      similarScore=1-(abs(starDiff-np.min(starDiff)))/(np.max(starDiff)-np.min(starDiff))
      similarDF = pd.DataFrame(similarScore,index=df.index,columns=["similarity"])
      similarDF.sort_index(inplace=True)
      return similarDF

   '''
   def prefer(self, reviewInfo):
      # Now we using a simple comparison: stars v.s. threshold
      ## Need Update later, use a weighted avg of #(cool, useful, funny).
      ## Threshold value also need to be calculated based on other restaurant distributions.
      if reviewInfo.get("stars").values[0] > self.preferThresh:
         return True
      return False
   '''

   def content_filter(self,userInfo):
      # content based: cold start

      return

   def hybrid_filter(self):
      # hybrid
      return

   def hottag_filter(self):
      ### update later
      return

   def test(self):
      self.open_connect()

      self.define_user()


      #df_user=self.read_user()
      #df_review=self.read_review()
      #print(df_user["review_count"])
      #print(df_review["stars"])
      self.close_connect()

