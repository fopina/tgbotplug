from tgbot import plugintest
from tgbot.botapi import Update
from test_plugin import TestPlugin


class TestPluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.plugin = TestPlugin()
        self.bot = self.fake_bot(
            '',
            plugins=[self.plugin],
        )
        self.received_id = 1

    def test_user_update(self):
        """Test for issue #22"""
        sender = {
            'id': 1,
            'first_name': 'John',
            'last_name': 'Doe',
        }
        self.receive_message('test', sender=sender)
        self.assertEqual(self.bot.models.User.get(self.bot.models.User.id == 1).first_name, 'John')

        self.receive_message('test', sender=sender)

        sender['first_name'] = 'Paul'
        self.receive_message('test', sender=sender)
        self.assertEqual(self.bot.models.User.get(self.bot.models.User.id == 1).first_name, 'Paul')

    def receive_message(self, text, sender=None, chat=None, reply_to_message_id=None):
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

        self.bot.process_update(
            Update.from_dict({
                'update_id': self.received_id,
                'message': {
                    'message_id': self.received_id,
                    'text': text,
                    'chat': chat,
                    'from': sender,
                    'reply_to_message': reply_to_message,
                }
            })
        )

        self.received_id += 1
