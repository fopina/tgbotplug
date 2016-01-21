from tgbot import plugintest
from sample_plugin import TestPlugin


class TestPluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.plugin = TestPlugin()
        self.bot = self.fake_bot(
            '',
            plugins=[self.plugin],
        )

    def test_print_commands(self):
        from cStringIO import StringIO
        out = StringIO()
        self.bot.print_commands(out=out)
        self.assertEqual(out.getvalue(), '''\
echo - right back at ya
echo2 - right back at ya
save - save a note
read - read a note
savegroup - save a group note
readgroup - read a group note
''')

    def test_reply(self):
        self.receive_message('/echo test')
        self.assertReplied('test')
        self.receive_message('/echo sound 1 2 3')
        self.assertReplied('sound 1 2 3')

    def test_need_reply_user(self):
        self.receive_message('test')
        self.assertNoReplies()

        self.receive_message('/echo')
        self.assertReplied('echo what?')

        self.receive_message('test')
        self.assertReplied('test')

        self.receive_message('sound')
        self.assertNoReplies()

    def test_need_reply_by_message_id(self):
        self.receive_message('/echo')
        self.assertReplied('echo what?')

        self.clear_queues()

        # wrong reply id, should be ignored
        self.receive_message('test', reply_to_message=3)
        self.assertNoReplies()

        # correct reply id
        self.receive_message('test', reply_to_message=2)
        self.assertReplied('test')

    def test_need_reply_group(self):
        chat = {
            'id': 1,
            'title': 'test group',
            'type': 'group',
        }
        self.receive_message('/echo', chat=chat)
        self.assertReplied('echo what?')

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
        self.assertReplied('test')

    def test_need_reply_selective_group(self):
        chat = {
            'id': 1,
            'title': 'test group',
            'type': 'group',
        }

        self.receive_message('/echo2', chat=chat)
        self.assertReplied('echo what?')

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
        self.assertNoReplies()

        self.receive_message(
            'test',
            chat=chat,
        )
        self.assertReplied('test')

    def test_plugin_data_single(self):
        self.receive_message('/save test 123')
        self.assertReplied('saved')

        self.receive_message('/read', sender={
            'id': 2,
            'first_name': 'Jane',
            'last_name': 'Doe',
        })
        self.assertReplied('no note saved')

        self.receive_message('/read')
        self.assertReplied('your note: test 123')

        self.receive_message('/save test 321')
        self.assertReplied('saved')

        self.receive_message('/read')
        self.assertReplied('your note: test 321')

    def test_plugin_data_group(self):
        chat = {
            'id': 99,
            'title': 'test group',
        }

        self.receive_message('/savegroup test 123', chat=chat)
        self.assertReplied('saved')

        self.receive_message('/readgroup')
        self.assertReplied('no note saved')

        self.receive_message('/readgroup', chat=chat)
        self.assertReplied('this group note: test 123')

        self.receive_message('/readgroup', chat=chat, sender={
            'id': 2,
            'first_name': 'Jane',
            'last_name': 'Doe',
        })
        self.assertReplied('this group note: test 123')

    def test_prefix_cmd(self):
        self.receive_message('/prefixcmd1')
        self.assertReplied('1')

        self.receive_message('/prefixcmd12@test_bot')
        self.assertReplied('12')

        self.receive_message('/prefixcmd@test_bot 123')
        self.assertReplied('123')

    def test_list_keys(self):
        sender2 = {
            'id': 2,
            'first_name': 'Jane',
            'last_name': 'Doe',
        }
        chat1 = {
            'id': 3,
            'title': 'test chat',
        }

        self.receive_message('/save note1')  # 1 1
        self.receive_message('/save note2', sender=sender2)  # 2 2
        self.receive_message('/save note3', chat=chat1)  # 3 1
        self.receive_message('/save note4', sender=sender2, chat=chat1)  # 3 2

        self.assertEqual(
            list(self.plugin.iter_data_keys()),
            ['1', '2', '3'],
        )
        self.assertEqual(
            list(self.plugin.iter_data_key_keys()),
            [],
        )
        self.assertEqual(
            list(self.plugin.iter_data_key_keys('1')),
            ['1'],
        )
        self.assertEqual(
            list(self.plugin.iter_data_key_keys('2')),
            ['2'],
        )
        self.assertEqual(
            list(self.plugin.iter_data_key_keys('3')),
            ['1', '2'],
        )

        self.plugin.save_data(3, key2=2)
        self.assertEqual(
            list(self.plugin.iter_data_key_keys('3')),
            ['1'],
        )
