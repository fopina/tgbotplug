from tgbot.pluginbase import TGPluginBase, TGCommandBase
from random import choice
from tgbot.botapi import ForceReply


class RandomPlugin(TGPluginBase):
    def list_commands(self):
        return (
            TGCommandBase('random', self.random, 'pick a random value from provided list'),
        )

    def random(self, message, text):
        if not text:
            m = self.bot.send_message(
                message.chat.id,
                'What are the options? (space separated)',
                reply_to_message_id=message.message_id,
                reply_markup=ForceReply.create(selective=True)
            ).wait()
            self.need_reply(self.random, message, out_message=m, selective=True)
        else:
            pars = text.split()  # split on any whitespace
            reply = choice(pars)
            self.bot.send_message(message.chat.id, reply, reply_to_message_id=message.message_id)
