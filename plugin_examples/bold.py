from tgbot.pluginbase import TGPluginBase
from tgbot.botapi import InlineQueryResultArticle


class BoldPlugin(TGPluginBase):
    """A plugin to do something like the official @bold inline bot"""
    def list_commands(self):
        return ()

    def inline_query(self, inline_query):
        if inline_query.query:
            # limit is 510 - thought not documented at the moment...
            txt = inline_query.query[:500]
            results = [
                self._inline_result('Bold', '*%s*' % txt),
                self._inline_result('Italic', '_%s_' % txt),
                self._inline_result('Fixedsys', '`%s`' % txt),
                self._inline_result('Pre-Rendered', txt)
            ]
            self.bot.answer_inline_query(inline_query.id, results, cache_time=3600)

    def _inline_result(self, title, text):
        return InlineQueryResultArticle(
            title, title,
            text, description=text,
            parse_mode='Markdown'
        )
