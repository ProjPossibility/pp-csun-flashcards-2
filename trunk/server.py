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

class MathParser(tornado.web.RequestHandler):


	def parseMathXL(self, inString):

		def parse(x):
			if x == '0':
				return 'zero '
			elif x == '1':
				return 'one '
			elif x == '2':
				return 'two '
			elif x == '3':
				return 'three '
			elif x == '4':
				return 'four '
			elif x == '5':
				return 'five '
			elif x == '6':
				return 'six '
			elif x == '7':
				return 'seven '
			elif x == '8':
				return 'eight '
			elif x == '9':
				return 'nine '
			elif x == '-':
				return 'minus '
			elif x == '*':
				return 'times '
			elif x == '/':
				return 'divided by '
			elif x == '(':
				return 'open paranthesis '
			elif x == ')':
				return 'close paranthesis '
			elif x == '^':
				return 'to the power of '
			else:
				return x + " "

		outString = ""

		for i in range(len(inString)):
			outString += parse(inString[i])

		return outString

	def get(self):
		text = self.get_argument("text")
		self.write('<textarea>'+self.parseMathXL(text)+'</textarea>')  



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
        self.redirect("newcard?deckid="+deckid)
        
        
        
class CardHandler(BaseHandler):
    def get(self):
        deckid = self.get_argument("deckid")
        cardid = self.get_argument("cardid")
        cardindex = 0
        entries = self.db.query("SELECT * FROM CARDS WHERE DECKID=%s", deckid)
        for i in range(0,len(entries)):
            if str(entries[i].ID) == str(cardid):
                cardindex = i
        self.render("card.html", entries=entries, cardid=cardid, cardindex=cardindex)
           


class NewDeckHandler(BaseHandler):
   	def get(self):
		self.render("newdeck.html")
	def post(self):
		name = self.get_argument("name", None)
		if name:
		    entry = self.db.get("SELECT * FROM DECK WHERE name = %s", str(name))
		    if entry: raise tornado.web.HTTPError(404) #duplicate
		self.db.execute("INSERT INTO DECK (userid,name) VALUES (%s,%s)",1, name)
		entries = self.db.query("SELECT * FROM DECK")
		self.redirect("newcard?deckid="+str(entries[len(entries)-1]))



class CardHandlerNew(BaseHandler):
    def get(self):
        deckid = self.get_argument("deckid", None)
        self.render("newcard.html",deckid=deckid)
    def post(self):
            question = self.get_argument("cardquestion", None)
            answer = self.get_argument("cardanswer", None)
            deckid = self.get_argument("deckid", None)
            print "%s %s %s", question, answer, deckid
            if question:
                entry = self.db.get("SELECT * FROM CARDS WHERE QUESTION = %s", str(question))
            if entry: raise tornado.web.HTTPError(404) #duplicate<input type="hidden" value="{{deckid.value}}" name="deckid" id="deckid" />

            self.db.execute(
                            "INSERT INTO CARDS (DECKID,QUESTION,ANSWER) VALUES (%s,%s,%s)",
                            deckid, question, answer)
            self.redirect("cardsindecklist?deckid="+deckid)

class ModifyCardHandler(BaseHandler):
	def get(self):
		deckid = self.get_argument("deckid", None)
		cardid = self.get_argument("cardid", None)
		entries = self.db.query("SELECT * FROM CARDS WHERE ID=%s",cardid)
		print len(entries)
		entry = entries[0]
		self.render("modcard.html", entry=entry)
		
	def post(self):
		deckid = self.get_argument("deckid", None)
		cardid = self.get_argument("cardid", None)
		question = self.get_argument("cardquestion", None)
		answer = self.get_argument("cardanswer", None)
		self.db.execute("UPDATE CARDS SET QUESTION=%s, ANSWER=%s WHERE ID=%s", question, answer, cardid)
		self.redirect("cardsindecklist?deckid="+deckid)
	

class DeleteDeckHandler(BaseHandler):
    def get(self):
        deckid = self.get_argument("deckid")
        self.db.execute("DELETE FROM CARDS WHERE DECKID=%s", deckid)
        self.db.execute("DELETE FROM DECK WHERE ID=%s", deckid)
        self.redirect("deckslist")

class DeleteCardHandler(BaseHandler):
    def get(self):
        cardid = self.get_argument("cardid")
        deckid = self.get_argument("deckid")
        self.db.execute("DELETE FROM CARDS WHERE ID=%s",cardid)
        self.redirect("/cardsindecklist?deckid="+deckid)
        
class ConfirmDeleteHandler(BaseHandler):
	def get(self):
		deckid = self.get_argument("deckid", None)
		cardid = self.get_argument("selfid", None)
		self.render("confirmdelete.html", cardid=cardid, deckid=deckid)

class ViewDeckHandler(tornado.web.RequestHandler):
    def get(self):
	       self.render("viewdeck.html")

class NewCardHandler(tornado.web.RequestHandler):
    def get(self):
	       self.render("newcard.html")

class ViewCardHandler(tornado.web.RequestHandler):
    def get(self):
	       self.render("viewcard.html")

class MathHandler(tornado.web.RequestHandler):
    def get(self):
	       self.render("math.html")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
		(r"/", HomeHandler),
		(r"/card", CardHandler),
		(r"/newdeck", NewDeckHandler),
		(r"/viewdeck", ViewDeckHandler),
		(r"/newcard", CardHandlerNew),
        (r"/deldeck", DeleteDeckHandler),
        (r"/confirmdelete", ConfirmDeleteHandler),
        (r"/delcard", DeleteCardHandler),
        (r"/modcard", ModifyCardHandler),
        (r"/cardsindecklist", CardsInDeckListHandler),
		(r"/viewcard", ViewCardHandler),
        (r"/deckslist", DecksListHandler),
		(r"/math", MathHandler),
		(r"/mathparse", MathParser)]


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


