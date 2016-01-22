# coding=utf-8
from tgbot import plugintest
from plugin_examples.simsimi import SimsimiPlugin
import os

from requests.packages import urllib3
urllib3.disable_warnings()


class SimsimiPluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self._key = os.environ.get('SIMSIMI_KEY', '')
        self.bot = self.fake_bot('', plugins=[], no_command=SimsimiPlugin(self._key))

    def test_reply(self):
        # if no key configured, use mock
        if not self._key:
            import mock

            def fget(*args, **kwargs):
                r = type('Test', (object,), {})()
                r.json = lambda: {'result': 100, 'response': 'hello'}
                return r

            with mock.patch('requests.get', fget):
                self.receive_message('hello')
        else:
            self.receive_message('hello')

        # any reply will do except the error reply
        self.assertNotEqual(self.last_reply(), 'Sorry, sleeping at the moment...')

    def test_no_reply(self):
        self.receive_message('')
        # any reply will do...
        self.assertNoReplies()
