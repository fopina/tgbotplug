import tgbot
from tgbot.botapi import ChatAction
import requests


class SimsimiPlugin(tgbot.TGPluginBase):
    def __init__(self, key, trial_key=True):
        super(SimsimiPlugin, self).__init__()
        self._key = key
        self._trial_key = trial_key
        self._url = 'http://sandbox.api.simsimi.com/request.p' if trial_key else 'http://api.simsimi.com/request.p'

    def simsimi(self, message, text):
        self.bot.send_chat_action(message.chat.id, ChatAction.TEXT)

        res = requests.get(self._url, params={
            'key': self._key,
            'lc': 'en',
            'ft': '1.0',
            'text': text,
        }).json()

        if res['result'] == 100:
            self.bot.send_message(message.chat.id, res['response'])
        else:
            self.bot.send_message(message.chat.id, 'Sorry, sleeping at the moment...')

    def chat(self, message, text):
        if not text:
            return
        self.simsimi(message, text)
