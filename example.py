#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A barebones AppEngine application that uses Facebook for login."""

import facebook
import logging
import os.path
import wsgiref.handlers

from google.appengine import api

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

from models import Likes
from models import User

# Find a JSON parser
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        # For Google AppEngine
        from django.utils import simplejson as json
_parse_json = lambda s: json.loads(s)

try:
	# This is the resource dictionary
	import res
except:
	pass

FACEBOOK_APP_ID = res.keys['fbappid'] if res else ""
FACEBOOK_APP_SECRET = res.keys['fbsecret'] if res else ""

class BaseHandler(webapp.RequestHandler):
	"""Provides access to the active Facebook user in self.current_user

	The property is lazy-loaded on first access, using the cookie saved
	by the Facebook JavaScript SDK to determine the user ID of the active
	user. See http://developers.facebook.com/docs/authentication/ for
	more information.
	"""
	@property
	def current_user(self):
		if not hasattr(self, "_current_user"):
			self._current_user = None
			cookie = facebook.get_user_from_cookie(
				self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
			if cookie:
				# Store a local instance of the user data so we don't need
				# a round-trip to Facebook on every request
				user = User.get_by_key_name(cookie["uid"])
				if not user:
					graph = facebook.GraphAPI(cookie["access_token"])
					profile = graph.get_object("me")
					# Change the user type's key to be a unique key (maybe openid)
					user = User(key_name=str(profile["id"]),
					#user = User(key_name=str(api.users.get_current_user().email()),
								guser=api.users.get_current_user(),
								fbid=str(profile["id"]),
								name=profile["name"],
								profile_url=profile["link"],
								access_token=cookie["access_token"])
					user.put()
				elif user.access_token != cookie["access_token"]:
					user.access_token = cookie["access_token"]
					user.put()
				self._current_user = user
		return self._current_user
		
	@property
	def graph(self):
		if not hasattr(self, "_graph") and self.current_user:
			self._graph = None
			tok = self.current_user.access_token
			self._graph = facebook.GraphAPI(tok)
		else:
			self._graph = facebook.GraphAPI()
		logging.debug("graph: %s" % str(self._graph))
		return self._graph
	
	def render(self, path, **kwargs):
		args = dict(current_user=self.current_user,
				facebook_app_id=FACEBOOK_APP_ID)
		args.update(kwargs)
		path = os.path.join(os.path.dirname(__file__), "templates/example.html")
		self.response.out.write(template.render(path, args))


class HomeHandler(BaseHandler):
	def get(self):
		like_list = {u'data' : []}
		if self.current_user:	
			like_list = self.graph.request("me/likes",
				{"access_token":self.current_user.access_token})
		
		logging.debug("like_list: %s"%str(like_list))
		
		map(self.add_like, like_list[u'data'])
		#map(lambda x: self.add_like(x,'twitter'), like_list[u'data'])
		#map(lambda x: self.add_like(x,'youtube'), like_list[u'data'])
		
		args = dict(current_user = self.current_user,
					likes = like_list,
					facebook_app_id = FACEBOOK_APP_ID)
		self.render("example.html", likes=like_list)


	def add_like(self, thelike, type=u'facebook'):
		""" Adds the like to the current user. """
		if self.current_user:
			logging.info("add_like: %s %s"%(str(self.current_user),str(thelike)))
			new_like = Likes(user=self.current_user,
				source=u'facebook',
				category=thelike[u'category'],
				name=thelike[u'name'],
				likeid=thelike[u'id'])
			# Check for duplicates
			if db.GqlQuery("SELECT __key__ FROM Likes WHERE user = :1 AND name = :2",
				new_like.user, new_like.name).count(1) == 0:
				new_like.put() # Does not exist so put it in the data store
		else:
			return


def main():
	util.run_wsgi_app(webapp.WSGIApplication([(r"/example", HomeHandler)]))


if __name__ == "__main__":
	main()
