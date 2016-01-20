from tgbot import plugintest
from tgbot.botapi import Update
from test_plugin import TestPlugin


class IssuesTest(plugintest.PluginTestCase):
    def setUp(self):
        self.plugin = TestPlugin()
        self.bot = self.fake_bot(
            '',
            plugins=[self.plugin],
        )
        self.received_id = 1

    def test_user_update(self):
        """Update user information (issue #22)"""
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

    def test_group_update(self):
        """Update group information (bonus for issue #22)"""
        chat = {
            'id': -1,
            'title': 'Test Group',
            'type': 'group'
        }
        self.receive_message('test', chat=chat)
        self.assertEqual(self.bot.models.User.get(self.bot.models.User.id == 1).first_name, 'John')
        self.assertEqual(self.bot.models.GroupChat.get(self.bot.models.GroupChat.id == -1).title, 'Test Group')

        chat['title'] = 'Test Crew'
        self.receive_message('test', chat=chat)
        self.assertEqual(self.bot.models.User.get(self.bot.models.User.id == 1).first_name, 'John')
        self.assertEqual(self.bot.models.GroupChat.get(self.bot.models.GroupChat.id == -1).title, 'Test Crew')

    def test_group_delete_with_message(self):
        """Delete GroupChat with pending messages (issue #24)"""
        chat = {
            'id': -1,
            'title': 'Test Group',
            'type': 'group'
        }
        self.receive_message('test', chat=chat)
        self.assertEqual(self.bot.models.User.get(self.bot.models.User.id == 1).first_name, 'John')
        self.assertEqual(self.bot.models.GroupChat.get(self.bot.models.GroupChat.id == -1).title, 'Test Group')
        self.assertEqual(self.bot.models.Message.select().count(), 0)

        # trigger need_reply
        self.receive_message('/echo', chat=chat)
        self.assertEqual(self.bot.models.Message.select().first().group_chat.id, -1)

        self.receive_message('', chat=chat, left_chat_participant=self.bot._bot_user.__dict__)
        self.assertEqual(self.bot.models.Message.select().count(), 0)

    def test_need_reply_twice(self):
        """Test need_reply for the duplicate incoming message (issue #23)"""
        # trigger first need_reply
        self.receive_message('/echo')
        self.assertEqual(self.bot.models.Message.select().count(), 1)

        # trigger second need_reply with same id
        self.received_id -= 1
        self.receive_message('/echo')
        self.assertEqual(self.bot.models.Message.select().count(), 1)

    def receive_message(self, text, sender=None, chat=None, reply_to_message_id=None, left_chat_participant=None):
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
                    'left_chat_participant': left_chat_participant,
                }
            })
        )

        self.received_id += 1
