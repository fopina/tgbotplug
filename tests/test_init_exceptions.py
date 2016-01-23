from tgbot import plugintest
from sample_plugin import TestPlugin


class TestPluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.plugin = TestPlugin()
        self.bot = self.fake_bot('', plugins=[self.plugin])

    def test_reattach(self):
        with self.assertRaisesRegexp(Exception, 'This instance of TestPlugin is already attached to other bot'):
            self.fake_bot('', plugins=[self.plugin])
        with self.assertRaisesRegexp(Exception, 'This instance of TestPlugin is already attached to other bot'):
            self.fake_bot('', no_command=self.plugin)
        with self.assertRaisesRegexp(Exception, 'This instance of TestPlugin is already attached to other bot'):
            self.fake_bot('', inline_query=self.plugin)

    def test_duplicate_command(self):
        class OtherPlugin(TestPlugin):
            pass
        with self.assertRaisesRegexp(Exception, 'Duplicate command echo: both in TestPlugin and OtherPlugin'):
            self.fake_bot('', plugins=[OtherPlugin(), TestPlugin()])
