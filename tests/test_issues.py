from tgbot import plugintest, pluginbase
from tgbot.botapi import Message
from sample_plugin import TestPlugin

import threading
import time


class IssuesTest(plugintest.PluginTestCase):
    def setUp(self):
        self.plugin = TestPlugin()
        self.bot = self.fake_bot('', plugins=[self.plugin])

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
        self.receive_message('/echo', message_id=1)
        self.assertEqual(self.bot.models.Message.select().count(), 1)

    def test_need_reply_validation(self):
        """Test need_reply validation (issue #27)"""
        import mock
        with mock.patch('logging.Logger._log') as m:
            self.plugin.need_reply(None, 'str')
            m.assert_called_with(40, 'in_message must be instance of Message, discarded: %s', ('str',))
            self.plugin.need_reply(None, Message.from_result({}), out_message='str')
            m.assert_called_with(40, 'out_message must be instance of Message, discarded: %s', ('str',))

    def test_atomic_operation(self):
        """Test atomic operation (issue #31)"""
        import tempfile
        import os
        _, v = tempfile.mkstemp()
        self.plugin = AtomicTestPlugin()
        self.bot = self.fake_bot(
            '', plugins=[self.plugin],
            # TODO: fix this for shared in-memory - it seems to always be creating the file even with mode=memory...
            db_url='sqlite:///%s?mode=memory&cache=shared' % v
        )
        self.bot.setup_db()

        self.receive_message('/atomic_fail')
        self.receive_message('/atomic_fail')
        time.sleep(0.05)
        # second one should fail or return 2, not 1...
        self.assertReplied('Value: 1')
        self.assertReplied('Value: 1')

        # try the proper one
        self.receive_message('/atomic_good')
        self.receive_message('/atomic_good')
        time.sleep(0.05)
        # second call failed to update atomically
        # replies will not be ordered due to threading...
        r = [self.last_reply(), self.last_reply()]
        self.assertIn('Value: 2', r)
        self.assertIn('Failed update', r)
        os.unlink(v)


class AtomicTestPlugin(TestPlugin):
    def list_commands(self):
        return [
            pluginbase.TGCommandBase('atomic_fail', self.atomic_fail, ''),
            pluginbase.TGCommandBase('atomic_good', self.atomic_good, '')
        ]

    def _update(self, chat_id):
        x = self.read_data(chat_id)
        if not x:
            x = 0
        x += 1
        time.sleep(0.01)
        self.save_data(chat_id, obj=x)
        self.bot.send_message(chat_id, 'Value: %d' % x)

    def _atomic_update(self, chat_id):
        try:
            with self.bot.db.atomic():
                x = self.read_data(chat_id)
                if not x:
                    x = 0
                x += 1
                time.sleep(0.01)
                self.save_data(chat_id, obj=x)
                self.bot.send_message(chat_id, 'Value: %d' % x)
        except:
            self.bot.send_message(chat_id, 'Failed update')

    def atomic_fail(self, message, text):
        threading.Thread(target=self._update, args=(message.chat.id,)).start()

    def atomic_good(self, message, text):
        threading.Thread(target=self._atomic_update, args=(message.chat.id,)).start()
