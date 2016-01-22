from tgbot.pluginbase import TGPluginBase, TGCommandBase
from tgbot.botapi import ReplyKeyboardMarkup, ReplyKeyboardHide
from random import random


class GuessPlugin(TGPluginBase):
    def list_commands(self):
        return (
            TGCommandBase('guess_start', self.guess_start, 'start the (number) guess game!'),
            TGCommandBase('guess_stop', self.guess_stop, u'stop the (number) guess game (why? \U0001F622)')
        )

    def guess_start(self, message, text):
        number = int(random() * 10)
        self.save_data(message.chat.id, obj=number)

        m = self.bot.send_message(
            message.chat.id,
            "I'm going to think of a number between 0 and 9 and you have to guess it! What's your guess?",
            reply_to_message_id=message.message_id,
            reply_markup=ReplyKeyboardMarkup.create(
                keyboard=[
                    ['0', '1', '2'],
                    ['3', '4', '5'],
                    ['6', '7', '8'],
                    ['9'],
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
            )
        ).wait()
        self.need_reply(self.guess_try, message, out_message=m, selective=True)

    def guess_try(self, message, text):
        number = self.read_data(message.chat.id)

        done = False

        try:
            guess = int(text)
            if guess == number:
                reply = 'Congratz, you nailed it %s' % message.sender.first_name
                done = True
            elif guess < number:
                reply = "I'm thinking higher..."
            else:
                reply = "I'm thinking lower..."
        except ValueError:
            reply = "Invalid guess!"

        if done:
            self.save_data(message.chat.id)
            self.clear_chat_replies(message.chat)
            self.bot.send_message(
                message.chat.id,
                reply,
                reply_to_message_id=message.message_id,
                reply_markup=ReplyKeyboardHide.create()
            )
        else:
            m = self.bot.send_message(
                message.chat.id,
                reply,
                reply_to_message_id=message.message_id,
                reply_markup=ReplyKeyboardMarkup.create(
                    keyboard=[
                        ['0', '1', '2'],
                        ['3', '4', '5'],
                        ['6', '7', '8'],
                        ['9'],
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=True,
                )
            ).wait()
            self.need_reply(self.guess_try, message, out_message=m, selective=True)

    def guess_stop(self, message, text):
        self.save_data(message.chat.id)
        self.clear_chat_replies(message.chat)

        self.bot.send_message(
            message.chat.id,
            'Ok :(',
            reply_to_message_id=message.message_id,
            reply_markup=ReplyKeyboardHide.create()
        )
