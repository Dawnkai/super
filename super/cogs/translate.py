from discord.ext import commands
from aiogoogletrans import Translator
from aiogoogletrans.constants import LANGUAGES
from super import utils

import aiogoogletrans


class Translate:
    def __init__(self, bot):
        self.bot = bot


    @staticmethod
    def _is_language(text):
        return text in LANGUAGES.keys()

    @commands.command(no_pm=False, pass_context=True, name='t')
    async def t(self, ctx):
        """.t [from lang] [to lang] <sentence>. Auto detects by default."""
        words = ctx.message.content.split(' ')[1:]
        if not len(words):
            return

        config = {'from': 'auto', 'to': 'en'}
        for _ in range(2):
            if len(words) < 3:
                continue
            setting, value = words[0], words[1]
            if words[0] not in ('from', 'to') or not self._is_language(value):
                continue

            config[setting] = value
            del words[0:2]

        utils.send_typing(self, ctx.message.channel)
        out = await Translator().translate(
            text=' '.join(words),
            src=config['from'],
            dest=config['to'],
        )
        await self.bot.say(f'**{out.src}**→**{out.dest}** - {out.text}')


def setup(bot):
    bot.add_cog(Translate(bot))
