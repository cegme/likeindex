import facebook
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import models
try:
	import res
except:
	pass

_fbsecret = res.keys['fbsecret'] if res else ""
_fbappid = res.keys['fbappid'] if res else ""

class MainHandler(webapp.RequestHandler):
	def get(self):
		fbuser = facebook.get_user_from_cookie(self.request.cookies,
				_fbappid, _fbsecret)
		
		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = u'Logout'
			
			if fbuser:
				graph = facebook.GraphAPI(user["oauth_access_token"])
				profile = graph.get_object("me")
				friends = graph.get_connections("me", "friends")
			
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = u'Login'

		template_values = {
				'url': url,
				'url_linktext': url_linktext,
				}
		path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
		self.response.out.write(template.render(path, template_values))

def main():
	application = webapp.WSGIApplication(
				[(r'/', MainHandler)],
				debug=True)
	run_wsgi_app(application)

if __name__ == '__main__':
	main()
