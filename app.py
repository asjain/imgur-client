import imgurpython
import webbrowser
import cherrypy
import threading
import time

CLIENT_ID = 'Enter Your Client ID'
CLIENT_SECRET = 'ENTER Your Client Secret'
USER_NAME = 'Enter your username'

class App:
    def __init__(self, client_id, secret):
        self.client = imgurpython.ImgurClient(client_id, secret)
        self.redirect_srv = Redirect()
        self.auth_code = None
        self.credentials = None
        
    def __launch_server(self):
        self.redirect_srv.start()

    def __get_auth_code(self, response_type='code'):
        auth_url = self.client.get_auth_url(response_type)
        webbrowser.open(auth_url)
        while self.auth_code == None:
            time.sleep(2)
            self.auth_code = self.redirect_srv.get_access_code()
        self.redirect_srv.shutdown()

    def connect(self):
        self.__launch_server()
        self.__get_auth_code()
        credentials = self.client.authorize(self.auth_code, 'authorization_code')
        self.client.set_user_auth(credentials['access_token'], credentials['refresh_token'])
        print 'client authorized'

    
# https://api.imgur.com/sgadia_callback?code=60137aa376632be290ae645904971b52a763b222
class Redirect(threading.Thread):
    def __init__(self):
        self.access_code = None
        threading.Thread.__init__(self)

    def run(self):
        print 'starting redirect uri server'
        cherrypy.quickstart(self)
        print 'server shutdown!!'

    def shutdown(self):
        cherrypy.engine.exit()

    def get_access_code(self):
        return self.access_code

    @cherrypy.expose
    def index(self):
        return 'Redirect Root page'

    @cherrypy.expose
    def redirect_uri(self, code):
        self.access_code = code


if __name__ == "__main__":
    app = App(CLIENT_ID, CLIENT_SECRET)
    app.connect()
    acc = app.client.get_account_settings(USER_NAME)
    print acc.email, ' is Authenticated.'
