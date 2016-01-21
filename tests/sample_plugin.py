from tgbot import TGPluginBase, TGCommandBase
from tgbot.botapi import ForceReply


class TestPlugin(TGPluginBase):
    def chat(self, bot, message, text):
        pass

    def list_commands(self):
        return [
            TGCommandBase('echo', self.echo, 'right back at ya'),
            TGCommandBase('echo2', self.echo_selective, 'right back at ya'),
            TGCommandBase('save', self.save, 'save a note'),
            TGCommandBase('read', self.read, 'read a note'),
            TGCommandBase('savegroup', self.savegroup, 'save a group note'),
            TGCommandBase('readgroup', self.readgroup, 'read a group note'),
            TGCommandBase('prefixcmd', self.prefixcmd, 'prefix cmd', prefix=True, printable=False),
        ]

    def echo_selective(self, message, text):
        if text:
            self.bot.send_message(message.chat.id, text, reply_to_message_id=message.message_id)
        else:
            m = self.bot.send_message(
                message.chat.id,
                'echo what?',
                reply_to_message_id=message.message_id,
                reply_markup=ForceReply.create(
                    selective=True
                )
            ).wait()
            self.need_reply(self.echo_selective, message, out_message=m, selective=True)

    def echo(self, message, text):
        if text:
            self.bot.send_message(message.chat.id, text, reply_to_message_id=message.message_id)
        else:
            m = self.bot.send_message(
                message.chat.id,
                'echo what?',
                reply_to_message_id=message.message_id,
                reply_markup=ForceReply.create(
                    selective=False
                )
            ).wait()
            self.need_reply(self.echo, message, out_message=m, selective=False)

    def save(self, message, text):
        if not text:
            self.bot.send_message(message.chat.id, 'Use it like: /save my note', reply_to_message_id=message.message_id)
        else:
            # complexify note for test purposes
            self.save_data(message.chat.id, key2=message.sender.id, obj={
                'note': text
            })
            self.bot.send_message(message.chat.id, 'saved', reply_to_message_id=message.message_id)

    def read(self, message, text):
        note = self.read_data(message.chat.id, key2=message.sender.id)
        if note is None:
            self.bot.send_message(message.chat.id, 'no note saved', reply_to_message_id=message.message_id)
        else:
            self.bot.send_message(message.chat.id, 'your note: ' + note['note'], reply_to_message_id=message.message_id)

    def savegroup(self, message, text):
        if not text:
            self.bot.send_message(message.chat.id, 'Use it like: /savegroup my note', reply_to_message_id=message.message_id)
        else:
            self.save_data(message.chat.id, obj=text)
            self.bot.send_message(message.chat.id, 'saved', reply_to_message_id=message.message_id)

    def readgroup(self, message, text):
        note = self.read_data(message.chat.id)
        if note is None:
            self.bot.send_message(message.chat.id, 'no note saved', reply_to_message_id=message.message_id)
        else:
            self.bot.send_message(message.chat.id, 'this group note: ' + note, reply_to_message_id=message.message_id)

    def prefixcmd(self, message, text):
        self.bot.send_message(message.chat.id, text)
