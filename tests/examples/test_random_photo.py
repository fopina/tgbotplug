from tgbot import plugintest
from plugin_examples.random_photo import RandomPhotoPlugin


class RandomPhotoPluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.bot = self.fake_bot('', plugins=[RandomPhotoPlugin()])

    def test_photo(self):
        self.receive_message('/photo')
        r = self.pop_reply()
        self.assertEqual(r[0], 'sendPhoto')
        self.assertIn('Cool', r[1]['caption'])
        self.assertIsNotNone(r[2])
        self.assertTrue(r[2][0].file_info.file_name.endswith('.jpg'))
