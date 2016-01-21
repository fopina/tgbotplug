from tgbot import plugintest
from tgbot.botapi import Update, User


class DBTrackTest(plugintest.PluginTestCase):
    def setUp(self):
        self.bot = self.fake_bot('')

    def test_track(self):
        chat1 = {
            'id': 1,
            'title': 'test chat',
            'type': 'group',
        }
        sender2 = {
            'id': 2,
            'first_name': 'John',
            'last_name': 'Doe',
        }

        # empty DB
        self.assertEqual(self.bot.models.User.select().count(), 0)
        self.assertEqual(self.bot.models.GroupChat.select().count(), 0)

        # user message, no chat created
        self.receive_message('one')
        self.assertEqual(self.bot.models.User.select().count(), 1)
        self.assertEqual(self.bot.models.GroupChat.select().count(), 0)

        # group chat message
        self.receive_message('two', chat=chat1)
        self.assertEqual(self.bot.models.User.select().count(), 1)
        self.assertEqual(self.bot.models.GroupChat.select().count(), 1)

        # different user, same chat
        self.receive_message('two', sender=sender2, chat=chat1)
        self.assertEqual(self.bot.models.User.select().count(), 2)
        self.assertEqual(self.bot.models.GroupChat.select().count(), 1)

        # kicked out of group
        self.receive_message(chat=chat1, left_chat_participant=dict(self.bot._bot_user.__dict__))
        self.assertEqual(self.bot.models.GroupChat.select().count(), 0)
