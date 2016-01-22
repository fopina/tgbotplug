from tgbot import plugintest
from plugin_examples.echo import EchoPlugin


class EchoPluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.bot = self.fake_bot('', plugins=[EchoPlugin()])

    def test_reply(self):
        self.receive_message('/echo test')
        self.assertReplied('test')

    def test_need_reply(self):
        self.receive_message('/echo')
        self.assertReplied('echo what?')

        self.receive_message('test')
        self.assertReplied('test')
