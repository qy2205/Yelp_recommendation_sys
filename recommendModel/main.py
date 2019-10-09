from model import RecommendModel


pos=[40,40.4,-80.01,-80]
user_id="JFU_qJxMzQXejQZVB-SLng"
DBpath='/home/gehua/Desktop/yelp.db/yelp.db'



a=RecommendModel(user_id,DBpath,pos)
a.define_user()

'''
"mD3B_TGV8TviCXhdx_9GnA"
"tVB0qWCyCfPySt3f237Zpw'
"JIch-659IMD1RfsSmXcn8A'
'mdg2rTZi2sgXg-KWIltm2Q'
'W6ifB2bf8zwt2Q5A389rgA'
'ZXMWoORiIklpH637hGWvyA'
'JFU_qJxMzQXejQZVB-SLng'
'''