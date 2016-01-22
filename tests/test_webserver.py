from tgbot import plugintest
from webtest import TestApp
from webtest.app import AppError


class WebserverTest(plugintest.PluginTestCase):
    def setUp(self):
        from sample_plugin import TestPlugin
        from tgbot.webserver import wsgi_app
        self.bot = self.fake_bot('123', plugins=[TestPlugin()])
        self.webapp = TestApp(wsgi_app([self.bot]))

    def test_ping(self):
        self.assertEqual(self.webapp.get('/ping/').text, '<b>Pong!</b>')

    def test_update_invalid_method(self):
        # invalid method (only POST allowed)
        with self.assertRaisesRegexp(AppError, 'Bad response: 405 Method Not Allowed'):
            self.webapp.get('/update/123')

    def test_update_invalid_token(self):
        with self.assertRaisesRegexp(AppError, 'Bad response: 404 Not Found'):
            self.webapp.post_json('/update/invalid', params=self.build_message('hello'))

    def test_update(self):
        self.webapp.post_json('/update/123', params=self.build_message('hello'))
        self.assertNoReplies()

        self.webapp.post_json('/update/123', params=self.build_message('/echo test'))
        self.assertReplied('test')
