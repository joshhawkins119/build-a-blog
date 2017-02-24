import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


class MainHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(MainHandler):
    def render_main(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")

        self.render("main.html", blogs=blogs)

    def get(self):
        self.render_main()

class NewPost(MainHandler):
    def render_front(self, title="", blog="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")

        self.render("new_post.html", title=title, blog=blog, error=error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            b = Blog(title = title, blog = blog)
            b.put()
            self.redirect("/blog/" + str(b.key().id()))

        else:
            error = "we need both a title and an entry!"
            self.render_front(title, blog, error)


class ViewPostHandler(MainHandler, webapp2.RequestHandler, Blog):
    def get(self, id):
        id = int(id)
        post = Blog.get_by_id(id)
        if post:
            self.render("post.html", post=post)
        else:
            error = "That blog does not exist!"
            self.redirect("/blog")


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/newpost', NewPost),
    (webapp2.Route('/blog/<id:\d+>', ViewPostHandler))
], debug=True)
