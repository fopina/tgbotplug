from tgbot import plugintest, TGPluginBase, TGCommandBase
from tgbot.botapi import Update, ForceReply
from webtest import TestApp
from webtest.app import AppError


class WebserverTest(plugintest.PluginTestCase):
    def setUp(self):
        from test_plugin import TestPlugin
        from tgbot.webserver import wsgi_app
        self.bot = self.fake_bot('123', plugins=[TestPlugin()])
        self.received_id = 1
        self.webapp = TestApp(wsgi_app([self.bot]))

    def test_ping(self):
        print self.bot.token
        self.bot.token = '321'
        print self.bot.token
        self.assertEqual(self.webapp.get('/ping/').text, '<b>Pong!</b>')

    def test_update_invalid_method(self):
        # invalid method (only POST allowed)
        with self.assertRaisesRegexp(AppError, 'Bad response: 405 Method Not Allowed'):
            self.webapp.get('/update/123')

    def test_update_invalid_token(self):
        with self.assertRaisesRegexp(AppError, 'Bad response: 404 Not Found'):
            self.webapp.post_json('/update/invalid', params=self.build_update('hello'))

    def test_update(self):
        self.webapp.post_json('/update/123', params=self.build_update('hello'))
        self.assertRaises(AssertionError, self.last_reply, self.bot)

        self.webapp.post_json('/update/123', params=self.build_update('/echo test'))
        self.assertReplied(self.bot, 'test')

    def build_update(self, text, sender=None, chat=None, reply_to_message_id=None):
        if sender is None:
            sender = {
                'id': 1,
                'first_name': 'John',
                'last_name': 'Doe',
            }

        if chat is None:
            chat = {'type': 'private'}
            chat.update(sender)

        reply_to_message = None

        if reply_to_message_id is not None:
            reply_to_message = {
                'message_id': reply_to_message_id,
                'chat': chat,
            }

        update = {
            'update_id': self.received_id,
            'message': {
                'message_id': self.received_id,
                'text': text,
                'chat': chat,
                'from': sender,
                'reply_to_message': reply_to_message,
            }
        }

        self.received_id += 1

        return update
