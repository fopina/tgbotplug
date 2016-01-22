from tgbot import plugintest
from plugin_examples.guess import GuessPlugin


class GuessPluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.plugin = GuessPlugin()
        self.bot = self.fake_bot('', plugins=[self.plugin])

    def test_play(self):
        self.receive_message('/guess_start')
        self.assertReplied("I'm going to think of a number between 0 and 9 and you have to guess it! What's your guess?")

        number = self.plugin.read_data(1)
        self.assertIsNotNone(number)
        self.assertGreaterEqual(number, 0)
        self.assertLessEqual(number, 9)

        # force number for testing
        self.plugin.save_data(1, obj=5)

        self.receive_message('1')
        self.assertReplied("I'm thinking higher...")

        self.receive_message('6')
        self.assertReplied("I'm thinking lower...")

        self.receive_message('gief error')
        self.assertReplied('Invalid guess!')

        self.receive_message('5')
        self.assertReplied('Congratz, you nailed it John')

    def test_stop(self):
        self.receive_message('/guess_start')
        self.assertReplied("I'm going to think of a number between 0 and 9 and you have to guess it! What's your guess?")
        self.assertIsNotNone(self.plugin.read_data(1))

        self.receive_message('/guess_stop')
        self.assertReplied('Ok :(')
        self.assertIsNone(self.plugin.read_data(1))
