import traceback
import aiohttp
from discord.ext import commands

class Gif(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def __exit__(self):
        self.session.close()


    async def _url_valid(self, url):
        try:
            async with self.session.get(url, timeout=1) as resp:
                if resp.status < 400:
                    return True
        except:
            traceback.print_exc()
        return False

    async def _get_url(self, text):
        async with self.session.post(
                'https://rightgif.com/search/web',
                data={'text': text},
                timeout=5,
        ) as resp:
            data = await resp.json()
            return data['url']

    @commands.command(no_pm=True, pass_context=True)
    async def gif(self, ctx):
        """.gif query - Gives you a random gif."""
        async with ctx.message.channel.typing():
            text = ctx.message.content.split(' ', 1)[1]
            url = await self._get_url(text)
            await ctx.message.channel.send(f'**{text}**: {url}')


def setup(bot):
    bot.add_cog(Gif(bot))
