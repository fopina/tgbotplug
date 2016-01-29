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

        import mock
        with mock.patch('logging.Logger._log') as m:
            self.receive_message('/echo', chat=chat)
            m.assert_called_with(40, 'Unexpected chat id %s (not a GroupChat nor sender)', (2,))

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

    def test_unprepared_bot(self):
        self.bot = TGBot('', plugins=[TestPlugin()])
        with self.assertRaisesRegexp(Exception, 'Did you forget to apply PluginTestCase.prepare_bot to your bot instance?'):
            self.receive_message('/echo 123')
        with self.assertRaisesRegexp(Exception, 'Did you forget to apply PluginTestCase.prepare_bot to your bot instance?'):
            self.build_inline('some query')
        with self.assertRaisesRegexp(Exception, 'Did you forget to apply PluginTestCase.prepare_bot to your bot instance?'):
            self.bot.send_message('123', 1)

    def test_sqlite_file_db(self):
        import tempfile
        import os
        _, v = tempfile.mkstemp()
        self.bot = self.fake_bot('', db_url='sqlite:///%s' % v)
        self.bot.setup_db()
        # TODO: find some assert for this
        # self.assertEqual(os.path.getsize(v), 12288)
        os.unlink(v)

    def test_update_bot_info(self):
        """
        Test automatic update_bot_info

        bot._bot_user is usually set by default in a test bot instance
        remove it and then test update_bot_info by triggering it with an update
        """
        self.bot = self.fake_bot('')
        self.bot._bot_user = None
        self.assertIsNone(self.bot.username)

        self.push_fake_result(dict(
            id=9999999,
            first_name='Test',
            last_name='Bot',
            username='test_bot'
        ))
        self.receive_message('niente')
        self.assertEqual(self.bot.username, 'test_bot')

    def test_run_web(self):
        self.bot = self.fake_bot('megaToken')
        # HACK ALERT: use invalid port to stop server immediately
        with self.assertRaisesRegexp(Exception, 'getsockaddrarg: port must be 0-65535'):
            self.bot.run_web('http://localhost', quiet=True, port=99999)
        r = self.pop_reply()
        self.assertEqual(r[0], 'setWebhook')
        self.assertEqual(r[1]['url'], 'http://localhost/update/megaToken')

    def test_get_updates_error(self):
        self.bot = self.fake_bot('megaToken')

        self.push_fake_result('API Error', status_code=400)  # push an error for testing
        self.push_fake_result(True)  # push result for setWebhook

        # HACK ALERT: use invalid polling_time to only loop once...
        with self.assertRaisesRegexp(IOError, '\[Errno 22\] Invalid argument'):
            self.bot.run(polling_time=-1)

        # TODO: assert Error was logged once logging is implemented
        r = self.pop_reply()
        self.assertEqual(r[0], 'getUpdates')
        self.assertEqual(r[1], {})

        r = self.pop_reply()
        self.assertEqual(r[0], 'setWebhook')
        self.assertEqual(r[1], {})

    def test_get_updates_good(self):
        self.bot = self.fake_bot('megaToken', plugins=[TestPlugin()])

        # insert fake results in reverse order (push pop)
        # push a list of updates for getUpdate call
        self.push_fake_result([
            self.build_message('/echo'),
            self.build_message('test')
        ])
        # push result for setWebhook call
        self.push_fake_result(True)

        # HACK ALERT: use invalid polling_time to only loop once...
        with self.assertRaisesRegexp(IOError, '\[Errno 22\] Invalid argument'):
            self.bot.run(polling_time=-1)

        # assert replies in reverse order (last to first)
        self.assertReplied('test')  # reply to "test" message

        self.assertReplied('echo what?')  # reply to "/echo" message

        r = self.pop_reply()
        self.assertEqual(r[0], 'getUpdates')
        self.assertEqual(r[1], {})

        r = self.pop_reply()
        self.assertEqual(r[0], 'setWebhook')
        self.assertEqual(r[1], {})
