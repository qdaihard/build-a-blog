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
import webapp2
import os
import jinja2
import cgi

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self,template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blogpost(db.Model):
    title = db.StringProperty(required = True)
    blogpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class NewPost(Handler):
    def render_add(self, title="", blogpost="", error=""):
        self.render("addpage.html", title=title, blogpost=blogpost, error=error)

    def get(self):
        self.render_add()

    def post(self):
        title = self.request.get('title')
        blogpost = self.request.get('post')

        if title and blogpost:
            entry = Blogpost(title = title, blogpost = blogpost)
            entry.put()
            self.redirect("/blog")
        else:
            error = "Please enter BOTH a title and the content of your blogpost!"
            self.render_add(title, blogpost, error)

class MainPage(Handler):
    def render_front(self, error=""):
        entries = db.GqlQuery("SELECT * FROM Blogpost ORDER BY created DESC LIMIT 5")
        error = self.request.get("error")

        self.render("front-page.html", entries_templates = entries)

    def get(self):
        self.render_front()

class ViewPostHandler(Handler):
    def get(self, id):
        entry = db.GqlQuery("SELECT * FROM Blogpost WHERE ID = 'id'")
        if entry:
            self.render("blogpost.html", blogpost = Blogpost.get_by_id(int(id)))
        else:
            error = "This blogpost does not exist"
            self.redirect("/blog/?error=" + cgi.escape(error))


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
