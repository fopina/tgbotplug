# coding=utf-8
from tgbot import plugintest
from plugin_examples.admin import AdminPlugin


class AdminPluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.bot = self.fake_bot(
            '',
            plugins=[AdminPlugin()],
        )

    def test_users(self):
        self.receive_message('/users')
        self.assertNoReplies()

        self.receive_message('/auth changeme')
        self.assertReplied(u'Welcome \U0001F60F')

        self.receive_message('/users')
        self.assertReplied('/msg1 - John Doe\n')

        self.receive_message('hey', sender={
            'id': 2,
            'first_name': 'Jane',
            'last_name': 'Doe',
        })

        self.receive_message('/users')
        self.assertReplied('''\
/msg1 - John Doe
/msg2 - Jane Doe
''')

    def test_groups(self):
        self.receive_message('/chats')
        self.assertNoReplies()

        self.receive_message('/auth changeme')
        self.assertReplied(u'Welcome \U0001F60F')

        self.receive_message('/chats')
        self.assertReplied('Zero...')

        self.receive_message(
            'hey',
            chat={
                'id': 1,
                'title': 'chat 1',
                'type': 'group',
            }
        )

        self.receive_message('/chats')
        self.assertReplied('/msg1 - chat 1\n')

        self.receive_message(
            'hey',
            chat={
                'id': 2,
                'title': 'chat 2',
                'type': 'group',
            }
        )

        self.receive_message('/chats')
        self.assertReplied('''\
/msg1 - chat 1
/msg2 - chat 2
''')

        self.receive_message(
            chat={
                'id': 1,
                'title': 'chat 1',
                'type': 'group',
            },
            sender=self.bot._bot_user.__dict__,
            left_chat_participant=self.bot._bot_user.__dict__
        )
        self.receive_message('/chats')
        self.assertReplied('/msg2 - chat 2\n')

    def test_more_users(self):
        self.receive_message('/more')
        self.assertNoReplies()

        self.receive_message('/auth changeme')
        self.assertReplied(u'Welcome \U0001F60F')

        self.receive_message('/more')
        self.assertReplied('No pending query...')

        self.receive_message('/users')
        self.assertReplied('/msg1 - John Doe\n')

        for i in xrange(2, 11):
            self.receive_message('hey', sender={
                'id': i,
                'first_name': 'Jane',
                'last_name': str(i),
            })
        self.receive_message('hey', sender={
            'id': -1,
            'first_name': 'Jane',
            'last_name': '-1',
        })

        self.receive_message('/users')
        self.assertReplied('''\
/msgN1 - Jane -1
/msg1 - John Doe
/msg2 - Jane 2
/msg3 - Jane 3
/msg4 - Jane 4
/msg5 - Jane 5
/msg6 - Jane 6
/msg7 - Jane 7
/msg8 - Jane 8
/msg9 - Jane 9
There are more, type /more to list 10 more results''')

        self.receive_message('/more')
        self.assertReplied('/msg10 - Jane 10\n')
        self.receive_message('/more')
        self.assertReplied('No pending query...')

    def test_more_chats(self):
        self.receive_message('/more')
        self.assertNoReplies()

        self.receive_message('/auth changeme')
        self.assertReplied(u'Welcome \U0001F60F')

        self.receive_message('/more')
        self.assertReplied('No pending query...')

        self.receive_message('/chats')
        self.assertReplied('Zero...')

        for i in xrange(-1, 20):
            self.receive_message('hey', chat={
                'id': i,
                'title': 'chat %d' % i,
                'type': 'group',
            })

        self.receive_message('/chats')
        self.assertReplied('''\
/msgN1 - chat -1
/msg0 - chat 0
/msg1 - chat 1
/msg2 - chat 2
/msg3 - chat 3
/msg4 - chat 4
/msg5 - chat 5
/msg6 - chat 6
/msg7 - chat 7
/msg8 - chat 8
There are more, type /more to list 10 more results''')

        self.receive_message('/more')
        self.receive_message('/more')
        self.assertReplied('/msg19 - chat 19\n')

        self.receive_message('/more')
        self.assertReplied('No pending query...')

    def test_change_password(self):
        self.receive_message('/newpass')
        self.assertNoReplies()

        self.receive_message('/auth changeme')
        self.assertReplied(u'Welcome \U0001F60F')

        self.receive_message('/newpass otherpassword')
        self.assertReplied('''\
Password updated to:
otherpassword''')

        self.receive_message('/auth changeme')
        self.assertReplied('You are already admin')

        sender = {
            'id': 2,
            'first_name': 'Jane',
            'last_name': 'Doe',
        }
        self.receive_message('/auth changeme', sender=sender)
        self.assertNoReplies()

        self.receive_message('/auth otherpassword', sender=sender)
        self.assertReplied(u'Welcome \U0001F60F')

    def test_message(self):
        self.receive_message('/auth changeme')
        self.assertReplied(u'Welcome \U0001F60F')

        self.receive_message('/msg1 hello')
        self.assertReplied("'hello' sent to 1")

        self.receive_message('/msg 1 bye')
        self.assertReplied("'bye' sent to 1")

        self.receive_message('/msg1')
        self.assertReplied("And say what?")

        self.receive_message('hey again')
        self.assertReplied("'hey again' sent to 1")
