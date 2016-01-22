from tgbot import plugintest
from plugin_examples.random_choice import RandomPlugin


class RandomPluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.bot = self.fake_bot('', plugins=[RandomPlugin()])

    def test_need_reply(self):
        self.receive_message('/random')
        self.assertReplied('What are the options? (space separated)')

        self.receive_message('foo bar')

        self.assertIn(
            self.last_reply(),
            [
                'foo',
                'bar',
            ]
        )

    def test_reply(self):
        self.receive_message('/random foo bar')

        self.assertIn(
            self.last_reply(),
            [
                'foo',
                'bar',
            ]
        )
