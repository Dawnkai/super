import os
from discord.ext import commands
from cobe.brain import Brain
from super import settings, utils
from super.utils import R
import random
import asyncio
import re

class markov:
    def __init__(self, bot):
        self.bot = bot
        os.makedirs('/data/cobe/', exist_ok=True)

    def _get_brain(self, server):
        return Brain(f'/data/cobe/{server}')

    def _get_slug(self, channel):
        return R.slug_to_str(['markov_replyrate', channel])

    async def _get_replyrate(self, channel):
        slug = self._get_slug(channel)

        replyrate = await R.read(slug)
        if not replyrate:
            return False
        else:
            return int(replyrate)

    async def should_reply(self, channel):
        rr = await self._get_replyrate(channel)
        if not rr:
            return False

        if random.randint(0, 100) < rr:
            return True

        return False

    def sanitize_out(self, message):
        replacements = {
            '@here': '**@**here',
            '@everyone': '**@**everyone',
        }
        for k, v in replacements.items():
            message = message.replace(k, v)
        return message

    async def on_message(self, message):
        if message.author.bot:  # Ignore bots
            return
        if message.content.startswith(settings.SUPER_PREFIX): # Ignore commands
            return
        brain = self._get_brain(message.author.server.id)

        mention = r'<@!?' + self.bot.user.id + '>'

        mentioned = any(self.bot.user.id == m.id for m in message.mentions)

        learned_message = re.sub(mention, 'Super', message.content).strip()
        brain.learn(learned_message)

        if mentioned or await self.should_reply(message.channel.id):
            reply = self.sanitize_out(brain.reply(message.content))
            await self.bot.send_message(message.channel, reply)


    @commands.command(no_pm=True, pass_context=True)
    async def chat(self, ctx):
        utils.send_typing(self, ctx.message.channel)
        brain = self._get_brain(ctx.message.author.server.id)
        about = ctx.message.content.split(' ', 1)[1]
        await self.bot.say(brain.reply(about))

    @commands.command(no_pm=True, pass_context=True)
    async def replyrate(self, ctx):
        if ctx.message.author.id not in settings.SUPER_ADMINS:
            return await self.bot.say('You cannot configure this.')
        message = ctx.message.content.split(' ')
        rr = int(message[1])

        if not 0 <= rr <= 100:
            return await self.bot.say('0-100')

        await R.write(self._get_slug(ctx.message.channel.id), rr)
        return await self.bot.say(f'Reply rate set to {rr}%')

def setup(bot):
    bot.add_cog(markov(bot))
