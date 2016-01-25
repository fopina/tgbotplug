from tgbot import plugintest, TGBot
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

    def test_need_reply_outside_sender(self):
        """
        this is impossible(?)...
        there cannot be a sender.id different than chat.id in a private chat...
        but gotta cover that line!
        TODO: revisit that code to make sure new chat.type's are covered...
        """
        self.bot = self.fake_bot('', plugins=[TestPlugin()])

        chat = {
            'id': 2,
            'type': 'private',
            'first_name': 'Ghost'
        }
        with self.assertRaisesRegexp(RuntimeError, 'Unexpected chat id 2'):
            self.receive_message('/echo', chat=chat)

    def test_prepare_bot(self):
        self.bot = TGBot('123')
        self.prepare_bot()
        self.assertEqual(self.bot.username, 'test_bot')

    def test_no_replies(self):
        self.bot = self.fake_bot('')
        with self.assertRaisesRegexp(AssertionError, 'No replies'):
            self.last_reply()
        with self.assertRaisesRegexp(AssertionError, 'No replies'):
            self.pop_reply()
