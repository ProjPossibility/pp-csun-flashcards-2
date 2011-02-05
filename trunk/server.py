import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os.path


from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #self.write("Hello, world")
	self.render("home.html")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
		(r"/", MainHandler),
	]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
        )
	tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()


