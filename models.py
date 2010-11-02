from google.appengine.ext import db

class User(db.Model):
	fbid = db.StringProperty(required=True)
	guser = db.UserProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	updated = db.DateTimeProperty(auto_now=True)
	name = db.StringProperty(required=True)
	profile_url = db.StringProperty(required=True)
	access_token = db.StringProperty(required=True)

class Likes(db.Expando):
	user = db.ReferenceProperty(User,required=True)
	source = db.StringProperty(choices=set([u"facebook",u"twitter",u"youtube"]))
	name = db.StringProperty()
	category = db.StringProperty()
	likeid = db.StringProperty()
	link = db.StringProperty() # Url reference if applicable

