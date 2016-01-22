from bottle import Bottle, request, response, abort
from botapi import Update, TelegramBotRPCRequest


def wsgi_app(bots):
    app = Bottle()

    bots_dict = {}
    for bot in bots:
        bots_dict[bot.token] = bot

    @app.route('/ping/')
    def ping():
        return '<b>Pong!</b>'

    @app.route('/update/<token>', method='POST')
    def update(token):
        if token not in bots_dict:
            abort(404, 'Not found: \'/update/%s\'' % token)
        x = bots_dict[token].process_update(Update.from_dict(request.json))
        if isinstance(x, TelegramBotRPCRequest):
            if x.thread.is_alive():
                return None
            x.params['method'] = x.api_method
            print 'webhook response'
            x = x._get_request()
            # print x.headers
            response.content_type = x.headers['Content-Type']
            # print x.body
            return x.body
        else:
            return None

    return app


def run_server(bots, **kwargs):  # pragma: no cover
    wsgi_app(bots).run(**kwargs)
