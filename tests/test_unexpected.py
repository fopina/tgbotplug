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

    def test_need_reply_null_handler(self):
        self.bot = self.fake_bot('', plugins=[TestPlugin()])

        msg = self.receive_message('/echo')
        self.assertReplied('echo what?')
        m = self.bot.models.Message.get(id=msg.message.message_id)
        m.reply_method = 'echo_invalid'
        m.save()
        self.receive_message('hello')
        self.assertNoReplies()
