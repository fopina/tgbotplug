from tgbot import plugintest
from plugin_examples.random_photo import RandomPhotoPlugin


class RandomPhotoPluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.bot = self.fake_bot('', plugins=[RandomPhotoPlugin()])

    def test_photo(self):
        self.receive_message('/photo')
        self.assertIn('Cool', self.pop_reply()[1]['caption'])
