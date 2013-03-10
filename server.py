# -*- coding: utf-8 -*-
import json
import tornado.ioloop
import tornado.web
import sockjs.tornado
import logging

class IndexHandler(tornado.web.RequestHandler):

    def post(self):
        event_type = self.get_argument('event')
        event_data = self.get_argument('data', None)
        session_id = self.get_argument('session_id')
        user = self.get_argument('user')
        to_send = {
            "event": event_type,
            "data": event_data,
            'user': user
        }
        for p in ChatConnection.participants:
            if p.session_id == session_id:
                p.send(to_send)
        self.finish()


class ChatConnection(sockjs.tornado.SockJSConnection):
    """Chat connection implementation"""
    # Class level variable
    participants = set()

    def on_open(self, info):
        print 'client connected'
        # Add client to the clients list
        self.participants.add(self)

    def on_message(self, message):
        data = json.loads(message)
        self.session_id = data.get('session_id')

    def on_close(self):
        print 'client disconnected'
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)

logging.getLogger().setLevel(logging.DEBUG)

# 1. Create chat router
ChatRouter = sockjs.tornado.SockJSRouter(ChatConnection, '/sockjs')

# 2. Create Tornado application
app = tornado.web.Application(
        [(r"/", IndexHandler)] + ChatRouter.urls
)

if __name__ == "__main__":
    # 3. Make Tornado app listen on port 8001
    app.listen(8001)

    # 4. Start IOLoop
    tornado.ioloop.IOLoop.instance().start()
	
