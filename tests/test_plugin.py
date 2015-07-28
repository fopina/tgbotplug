from tgbot import plugintest, TGPluginBase
from twx.botapi import Update, ForceReply


class TestPlugin(TGPluginBase):
    def chat(self, bot, message, text):
        pass

    def list_commands(self):
        return [
            ('echo', self.echo, 'right back at ya'),
            ('echo2', self.echo_selective, 'right back at ya'),
            ('save', self.save, 'save a note'),
            ('read', self.read, 'read a note'),
            ('savegroup', self.savegroup, 'save a group note'),
            ('readgroup', self.readgroup, 'read a group note'),
        ]

    def echo_selective(self, bot, message, text):
        if text:
            bot.tg.send_message(message.chat.id, text, reply_to_message_id=message.message_id)
        else:
            m = bot.tg.send_message(
                message.chat.id,
                'echo what?',
                reply_to_message_id=message.message_id,
                reply_markup=ForceReply.create(
                    selective=True
                )
            ).wait()
            self.need_reply(self.echo_selective, message, out_message=m, selective=True)

    def echo(self, bot, message, text):
        if text:
            bot.tg.send_message(message.chat.id, text, reply_to_message_id=message.message_id)
        else:
            m = bot.tg.send_message(
                message.chat.id,
                'echo what?',
                reply_to_message_id=message.message_id,
                reply_markup=ForceReply.create(
                    selective=True
                )
            ).wait()
            self.need_reply(self.echo, message, out_message=m, selective=False)

    def save(self, bot, message, text):
        if not text:
            bot.tg.send_message(message.chat.id, 'Use it like: /save my note', reply_to_message_id=message.message_id)
        else:
            # complexify note for test purposes
            self.save_data(message.chat.id, key2=message.sender.id, obj={
                'note': text
            })
            bot.tg.send_message(message.chat.id, 'saved', reply_to_message_id=message.message_id)

    def read(self, bot, message, text):
        note = self.read_data(message.chat.id, key2=message.sender.id)
        if note is None:
            bot.tg.send_message(message.chat.id, 'no note saved', reply_to_message_id=message.message_id)
        else:
            bot.tg.send_message(message.chat.id, 'your note: ' + note['note'], reply_to_message_id=message.message_id)

    def savegroup(self, bot, message, text):
        if not text:
            bot.tg.send_message(message.chat.id, 'Use it like: /savegroup my note', reply_to_message_id=message.message_id)
        else:
            self.save_data(message.chat.id, obj=text)
            bot.tg.send_message(message.chat.id, 'saved', reply_to_message_id=message.message_id)

    def readgroup(self, bot, message, text):
        note = self.read_data(message.chat.id)
        if note is None:
            bot.tg.send_message(message.chat.id, 'no note saved', reply_to_message_id=message.message_id)
        else:
            bot.tg.send_message(message.chat.id, 'this group note: ' + note, reply_to_message_id=message.message_id)


class TestPluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.bot = self.fake_bot(
            '',
            plugins=[TestPlugin()],
        )
        self.received_id = 1

    def receive_message(self, text, sender=None, chat=None, reply_to_message_id=None):
        if sender is None:
            sender = {
                'id': 1,
                'first_name': 'John',
                'last_name': 'Doe',
            }

        if chat is None:
            chat = sender

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

    def test_reply(self):
        self.receive_message('/echo test')
        self.assertReplied(self.bot, 'test')
        self.receive_message('/echo sound 1 2 3')
        self.assertReplied(self.bot, 'sound 1 2 3')

    def test_need_reply_user(self):
        self.receive_message('test')
        self.assertRaises(AssertionError, self.last_reply, self.bot)

        self.receive_message('/echo')
        self.assertReplied(self.bot, 'echo what?')

        self.receive_message('test')
        self.assertReplied(self.bot, 'test')

        self.clear_replies(self.bot)
        self.receive_message('sound')
        self.assertRaises(AssertionError, self.last_reply, self.bot)

    def test_need_reply_by_message_id(self):
        self.receive_message('/echo')
        self.assertReplied(self.bot, 'echo what?')

        self.clear_replies(self.bot)
        # wrong reply id, should be ignored
        self.receive_message('test', reply_to_message_id=2)
        self.assertRaises(AssertionError, self.last_reply, self.bot)

        # correct reply id
        self.receive_message('test', reply_to_message_id=1)
        self.assertReplied(self.bot, 'test')

    def test_need_reply_group(self):
        chat = {
            'id': 1,
            'title': 'test group',
        }
        self.receive_message('/echo', chat=chat)
        self.assertReplied(self.bot, 'echo what?')

        # non-selective need_reply, should accept from any user
        self.receive_message(
            'test',
            chat=chat,
            sender={
                'id': 2,
                'first_name': 'Jane',
                'last_name': 'Doe',
            }
        )
        self.assertReplied(self.bot, 'test')

    def test_need_reply_selective_group(self):
        chat = {
            'id': 1,
            'title': 'test group',
        }

        self.receive_message('/echo2', chat=chat)
        self.assertReplied(self.bot, 'echo what?')

        self.clear_replies(self.bot)
        # selective need_reply, should ignore other user
        self.receive_message(
            'test',
            chat=chat,
            sender={
                'id': 2,
                'first_name': 'Jane',
                'last_name': 'Doe',
            }
        )
        self.assertRaises(AssertionError, self.last_reply, self.bot)

        self.receive_message(
            'test',
            chat=chat,
        )
        self.assertReplied(self.bot, 'test')

    def test_plugin_data_single(self):
        self.receive_message('/save test 123')
        self.assertReplied(self.bot, 'saved')

        self.receive_message('/read', sender={
            'id': 2,
            'first_name': 'Jane',
            'last_name': 'Doe',
        })
        self.assertReplied(self.bot, 'no note saved')

        self.receive_message('/read')
        self.assertReplied(self.bot, 'your note: test 123')

        self.receive_message('/save test 321')
        self.assertReplied(self.bot, 'saved')

        self.receive_message('/read')
        self.assertReplied(self.bot, 'your note: test 321')

    def test_plugin_data_group(self):
        chat = {
            'id': 99,
            'title': 'test group',
        }

        self.receive_message('/savegroup test 123', chat=chat)
        self.assertReplied(self.bot, 'saved')

        self.receive_message('/readgroup')
        self.assertReplied(self.bot, 'no note saved')

        self.receive_message('/readgroup', chat=chat)
        self.assertReplied(self.bot, 'this group note: test 123')

        self.receive_message('/readgroup', chat=chat, sender={
            'id': 2,
            'first_name': 'Jane',
            'last_name': 'Doe',
        })
        self.assertReplied(self.bot, 'this group note: test 123')
