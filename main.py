#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class MainPage(Handler):

    def render_front(self, title="", body="", error=""):
        #blogposts = db.GqlQuery("SELECT * FROM BlogPost")
        self.render("front.html", title=title, body=body, error=error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            b = BlogPost(title=title, body=body)
            b.put()
            self.redirect("/blog")

        else:
            error = "We need both a title and a body."
            self.render_front(title, body, error)

class BlogPage(Handler):

    def get(self):
        #title= some way to get the titles of the blog entries from the database
        blogposts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
        self.render("bloglist.html", posts=blogposts)

class ViewPostHandler(Handler):
    def get(self, id):
        post_to_display = BlogPost.get_by_id(int(id))
        if not post_to_display:
            self.response.write("No post found. Try another!")
        else:
            self.render("viewpost.html", title=post_to_display.title, body=post_to_display.body)

app = webapp2.WSGIApplication([
    ('/newpost', MainPage),
    ('/blog', BlogPage), webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
