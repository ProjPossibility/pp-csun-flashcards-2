import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.database
import tornado.web
import os.path


from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="blog database host")
define("mysql_database", default="ss12", help="blog database name")
define("mysql_user", default="root", help="blog database user")
define("mysql_password", default="", help="blog database password")

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
	       self.render("home.html")

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    
class DecksListHandler(BaseHandler):
    def get(self):
        entries = self.db.query("SELECT * FROM DECK")
        self.render("deckslist.html", entries=entries)
        
class CardsInDeckListHandler(BaseHandler):
    def get(self):
        deckid = self.get_argument("deckid")
        entries = self.db.query("SELECT * FROM CARDS WHERE DECKID=%s", deckid)
        self.render("cardsindecklist.html", entries=entries, deckid=deckid)
    def post(self):
        deckid = self.get_argument("deckid")
        self.redirect("newcard",deckid)
        
        
        
class DeckHandler(tornado.web.RequestHandler):
    def get(self):
	       self.render("deck.html")
           


class NewDeckHandler(BaseHandler):
    	def get(self):
	       self.render("newdeck.html")

	def post(self):
		name = self.get_argument("name", None)
		if name:
		    entry = self.db.get("SELECT * FROM DECK WHERE name = %s", str(name))
		    if entry: raise tornado.web.HTTPError(404) #duplicate
		self.db.execute(
		"INSERT INTO DECK (userid,name) VALUES (%s,%s)",
		1, name)	

class NewCardHandler(BaseHandler):
    def get(self):
        deckid = self.get_argument("deckid")
        self.render("newcard.html",deckid=deckid)
    def post(self):
            question = self.get_argument("cardquestion", None)
            answer = self.get_argument("cardanswer", None)
            deckid = self.get_argument("deckid")
            if question:
                entry = self.db.get("SELECT * FROM CARDS WHERE QUESTION = %s", str(question))
            if entry: raise tornado.web.HTTPError(404) #duplicate<input type="hidden" value="{{deckid.value}}" name="deckid" id="deckid" />

            self.db.execute(
                            "INSERT INTO CARDS (DECKID,QUESTION,ANSWER) VALUES (%s,%s,%s)",
                            deckid, question, answer)	


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
        (r"/cardsindecklist", CardsInDeckListHandler),
		(r"/viewcard", ViewCardHandler),
		(r"/newcard", NewCardHandler),
        (r"/deckslist", DecksListHandler)]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
		    debug=True, static_path=os.path.join(os.path.dirname(__file__), "css"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)
    
        self.db = tornado.database.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()


