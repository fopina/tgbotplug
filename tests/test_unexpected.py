from tgbot import plugintest
from sample_plugin import TestPlugin


class TestPluginTest(plugintest.PluginTestCase):
    def test_need_reply_no_text(self):
        self.bot = self.fake_bot('', plugins=[TestPlugin()])
        msg = self.receive_message('/echo')
        self.assertReplied('echo what?')
        self.bot.models.Message.get(id=msg.message.message_id)

        msg = self.receive_message(None)
        self.assertReplied('echo what?')
        with self.assertRaises(self.bot.models.Message.DoesNotExist):
            self.bot.models.Message.get(id=msg.message.message_id)
