from tgbot.pluginbase import TGPluginBase, TGCommandBase
from tgbot.botapi import ForceReply, ChatAction
import re
import HTMLParser
import requests


class GooglePlugin(TGPluginBase):
    TAG_RE = re.compile(r'<[^>]+>')

    def __init__(self):
        super(GooglePlugin, self).__init__()
        self.unescaper = HTMLParser.HTMLParser()

    def list_commands(self):
        return (
            TGCommandBase('g', self.google, 'Google it'),
        )

    def google(self, message, text):
        if not text:
            m = self.bot.send_message(
                message.chat.id,
                'Google for what?',
                reply_to_message_id=message.message_id,
                reply_markup=ForceReply.create(selective=True)
            ).wait()
            self.need_reply(self.google, message, out_message=m, selective=True)
        else:
            self.bot.send_chat_action(message.chat.id, ChatAction.TEXT)

            res = requests.get('http://ajax.googleapis.com/ajax/services/search/web', params={
                'v': 1.0,
                'q': text,
            }).json()

            if res['responseStatus'] == 200:
                try:
                    res = res['responseData']['results'][0]
                    res['content'] = self.unescaper.unescape(GooglePlugin.TAG_RE.sub('', res['content']))
                    res['titleNoFormatting'] = self.unescaper.unescape(res['titleNoFormatting'])
                    reply = '%(titleNoFormatting)s\n\n%(content)s\n\n%(url)s' % res
                except IndexError:
                    reply = 'Sorry, nothing found...'
            else:  # pragma: no cover
                reply = 'It seems I\'m googling too much lately, I need to rest a little...'

            self.bot.send_message(message.chat.id, reply, reply_to_message_id=message.message_id, disable_web_page_preview=True)
