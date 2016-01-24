# coding=utf-8
from tgbot import plugintest
from plugin_examples.bold import BoldPlugin


class AdminPluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.bot = self.fake_bot('', inline_query=BoldPlugin())

    def test_inline(self):
        self.receive_inline(u'hello')
        results = self.pop_reply()[1]['results']
        self.assertEqual(results[0]['title'], 'Bold')
        self.assertEqual(results[0]['message_text'], '*hello*')
        self.assertEqual(results[1]['title'], 'Italic')
        self.assertEqual(results[1]['message_text'], '_hello_')
        self.assertEqual(results[2]['title'], 'Fixedsys')
        self.assertEqual(results[2]['message_text'], '`hello`')
        self.assertEqual(results[3]['title'], 'Pre-Rendered')
        self.assertEqual(results[3]['message_text'], 'hello')
