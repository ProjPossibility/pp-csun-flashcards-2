import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os.path


from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
	self.render("home.html")

class DeckHandler(tornado.web.RequestHandler):
    def get(self):
	self.render("deck.html")

class NewDeckHandler(tornado.web.RequestHandler):
    def get(self):
	self.render("newdeck.html")

class ViewDeckHandler(tornado.web.RequestHandler):
    def get(self):
	self.render("viewdeck.html")

class NewCardHandler(tornado.web.RequestHandler):
    def get(self):
	self.render("newcard.html")

class ViewCardHandler(tornado.web.RequestHandler):
    def get(self):
	self.render("viewcard.html")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
		(r"/", HomeHandler),
		(r"/deck", DeckHandler),
		(r"/newdeck", NewDeckHandler),
		(r"/viewdeck", ViewDeckHandler),
		(r"/newcard", NewCardHandler),
		(r"/viewcard", ViewCardHandler),
	]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
		debug = True
        )
	tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()


