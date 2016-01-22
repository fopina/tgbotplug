from tgbot.pluginbase import TGPluginBase, TGCommandBase
from tgbot.tgbot import InputFileInfo, InputFile, send_photo
import re
import requests
from cStringIO import StringIO
import mimetypes


class RandomPhotoPlugin(TGPluginBase):
    def list_commands(self):
        return (
            TGCommandBase('photo', self.photo, 'get a random photo from http://photo.net/'),
        )

    def photo(self, message, text):
        r = requests.get(
            'http://photo.net/photodb/random-photo',
            headers={'User-Agent': 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0'}
        )
        if r.status_code != 200:
            self.bot.send_message(message.chat.id, 'photodb is down at the moment...')
            return

        pic_url = re.search('src="(http://gallery.photo.net/photo/.*?)"', r.content).group(1)
        fp = StringIO(requests.get(pic_url).content)
        file_info = InputFileInfo(pic_url.split('/')[-1], fp, mimetypes.guess_type(pic_url)[0])
        return send_photo(chat_id=message.chat.id, caption='Cool', photo=InputFile('photo', file_info), token=self.bot.token)
        #self.bot.send_photo(chat_id=message.chat.id, caption='Cool', photo=InputFile('photo', file_info))
