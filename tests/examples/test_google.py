# coding=utf-8
from tgbot import plugintest
from plugin_examples.google import GooglePlugin


class GooglePluginTest(plugintest.PluginTestCase):
    def setUp(self):
        self.bot = self.fake_bot('', plugins=[GooglePlugin()])

    def test_not_found(self):
        self.receive_message('/g site:www.android.com "iphone is awesome"')
        self.assertReplied('Sorry, nothing found...')

    def test_reply(self):
        self.receive_message('/g site:skmobi.com TimeIsMoney')
        self.assertReplied(u'''\
skmobi - TimeIsMoney

Time is Money! So, "time" your money with this app. TimeIsMoney uses the \n\
interface you're used to from Clock.app stopwatch, but instead of showing time, ...

http://skmobi.com/timeismoney/''')

    def test_need_reply(self):
        self.receive_message('/g')
        self.assertReplied('Google for what?')

        self.receive_message('site:skmobi.com TimeIsMoney')
        self.assertReplied(u'''\
skmobi - TimeIsMoney

Time is Money! So, "time" your money with this app. TimeIsMoney uses the \n\
interface you're used to from Clock.app stopwatch, but instead of showing time, ...

http://skmobi.com/timeismoney/''')
