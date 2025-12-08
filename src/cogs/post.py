"""Contains the implementation for the /post command"""

from .base import BaseCog
import logging
from discord import app_commands, Interaction
from discord.ext import commands

class PostCommand(BaseCog):
    def __init__(self, bot):
        logger = logging.getLogger("cmds.post")
        super().__init__(bot, logger)

    @app_commands.command(name = "post", description = "Post an embed in the Current Channel with a link to the content")
    @app_commands.describe(url = "URL to the post", custom_note = "Describe the post with your own note", use_title = "Display the title of the post", quality = "Specifies the quality of the converted image, closer to 100 is better")
    @app_commands.choices(quality = [
        app_commands.Choice(name = "Poor (60)", value = 60),
        app_commands.Choice(name = "Fair (70)", value = 70),
        app_commands.Choice(name = "Good (80)", value = 80),
        app_commands.Choice(name = "Very Good (85)", value = 85),
        app_commands.Choice(name = "Excellent (90)", value = 90),
        app_commands.Choice(name = "Superior (95)", value = 95),
        app_commands.Choice(name = "Perfect (100)", value = 100)
    ])
    async def post(self, ctx:Interaction, url:str, custom_note:str = None, use_title:bool = True, quality:app_commands.Choice[int] = 95):
        print("Hallo")

async def setup(bot:commands.Bot):
    await bot.add_cog(PostCommand(bot))