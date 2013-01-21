# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import sockjs.tornado


class IndexHandler(tornado.web.RequestHandler):

    def post(self):
        event_type = self.get_argument('event', 'message')
        event_data = self.get_argument('data', None)
        uniq_id = self.get_argument('uniq_id')
        try:
            data = json.loads(event_data)
        except:
            data = event_data
        to_send = {
            "event": event_type,
            "data": data
        }
        for p in ChatConnection.participants:
            if p.uniq_id != uniq_id:
                p.send(to_send)
        self.finish()


class ChatConnection(sockjs.tornado.SockJSConnection):
    """Chat connection implementation"""
    # Class level variable
    participants = set()

    def on_open(self, info):
        print 'client connected'
        # Add client to the clients list
        self.uniq_id = info.path
        self.participants.add(self)
        self.send({'event': 'init', 'uniq_id': self.uniq_id})

    def on_close(self):
        print 'client disconnected'
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)


if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    # 1. Create chat router
    ChatRouter = sockjs.tornado.SockJSRouter(ChatConnection, '/sockjs')

    # 2. Create Tornado application
    app = tornado.web.Application(
            [(r"/", IndexHandler)] + ChatRouter.urls
    )

    # 3. Make Tornado app listen on port 8001
    app.listen(8001)

    # 4. Start IOLoop
    tornado.ioloop.IOLoop.instance().start()
