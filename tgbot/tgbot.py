from twx.botapi import TelegramBot, Error
from . import models
from .pluginbase import TGPluginBase
from playhouse.db_url import connect


class TGBot(object):
    def __init__(self, token, plugins=[], no_command=None, db_url=None):
        self._token = token
        self.tg = TelegramBot(token)
        self._last_id = None
        self.cmds = {}
        self._no_cmd = no_command
        self._msgs = {}
        self._plugins = plugins

        if no_command is not None:
            if not isinstance(no_command, TGPluginBase):
                raise NotImplementedError('%s does not subclass tgbot.TGPluginBase' % type(no_command).__name__)

        for p in self._plugins:

            if not isinstance(p, TGPluginBase):
                raise NotImplementedError('%s does not subclass tgbot.TGPluginBase' % type(p).__name__)

            for cmd in p.list_commands():
                if cmd[0] in self.cmds:
                    raise Exception(
                        'Duplicate command %s: both in %s and %s' % (
                            cmd[0],
                            type(p).__name__,
                            self.cmds[cmd[0]][2],
                        )
                    )
                self.cmds[cmd[0]] = (cmd[1], cmd[2], type(p).__name__)

        if db_url is None:
            self.db = connect('sqlite:///:memory:')
            models.database_proxy.initialize(self.db)
            self.setup_db()
        else:
            self.db = connect(db_url)
            models.database_proxy.initialize(self.db)

    def process_update(self, update):
        if update.message.text:
            if update.message.text.startswith('/'):
                spl = update.message.text.find(' ')
                if spl < 0:
                    self.process(update.message.text[1:], '', update.message)
                else:
                    self.process(update.message.text[1:spl], update.message.text[spl + 1:], update.message)
            else:
                was_expected = False
                for p in self._plugins:
                    was_expected = p.is_expected(self, update.message)
                    if was_expected:
                        break

                if self._no_cmd is not None and not was_expected:
                    self._no_cmd.chat(self, update.message, update.message.text)

    def setup_db(self):
        models.create_tables(self.db)

    def run(self, polling_time=2):
        from time import sleep
        # make sure all webhooks are disabled
        self.tg.set_webhook().wait()

        while True:
            ups = self.tg.get_updates(offset=self._last_id).wait()
            if isinstance(ups, Error):
                print 'Error: ', ups
            else:
                for up in ups:
                    self.process_update(up)
                    self._last_id = up.update_id + 1

            sleep(polling_time)

    def run_web(self, hook_url, **kwargs):
        from . import webserver
        url = hook_url
        if url[-1] != '/':
            url += '/'
        self.tg.set_webhook(url + 'update/' + self._token)
        webserver.run_server(self, **kwargs)

    def list_commands(self):
        out = []
        for ck in self.cmds:
            if self.cmds[ck][1]:
                out.append((ck, self.cmds[ck][1]))
        return out

    def print_commands(self):
        '''
        utility method to print commands and descriptions
        for @BotFather
        '''
        cmds = self.list_commands()
        for ck in cmds:
            print '%s - %s' % ck

    def process(self, cmd, text, message):
        spl = cmd.find('@')
        if spl > 0:
            cmd = cmd[:spl]
        if cmd in self.cmds:
            try:
                self.cmds[cmd][0](self, message, text)
            except:
                import traceback
                traceback.print_exc()
                self.tg.send_message(message.chat.id, 'some error occurred... (logged and reported)', reply_to_message_id=message.message_id)
