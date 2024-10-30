import discord
from discord.ext import commands
from discord import app_commands
from cogs.base_cog import Base_Cog

import logging


class Maintenance_Command(Base_Cog):
    def __init__(self, bot):
        self.__bot = bot
        self.__maintenance_mode_enabled = False
        super().__init__(logging.getLogger("cmds.maintenance"))

    def enable_global_maintenance(self):
        self.__maintenance_mode_enabled = True

    def disable_gloabal_maintenance(self):
        self.__maintenance_mode_enabled = False

    @staticmethod
    async def handle_check(ctx: discord.Integration):
        """Check function called for every command"""
        instance = ctx.client.get_cog("Maintenance_Command")
        if instance and instance.__maintenance_mode_enabled:
            await instance.startup(ctx)
            return False
        return True

    async def startup(self, ctx: discord.Interaction):
        """Returns an message, explaining that the bot is still starting up"""
        embed = discord.Embed(
            title = ":construction: Bot is still starting up! :construction:", 
            description = "While the bot is starting, all commands are locked and unable to be executed",
            color = 0xED4337)
        await ctx.response.send_message(embed = embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, app_commands.CheckFailure):
            # Suppress the traceback and inform the user about maintenance mode
            return  # Already handled in the `startup` method

    cmds_group = app_commands.Group(name="maintenance", description="Put the bot into maintenance mode and control its alternative behaviour")
    @cmds_group.command(name = "enable", description = "Enables the maintenance mode globally")
    async def maintenance_enable(self, ctx: discord.Interaction):
        if self.__maintenance_mode_enabled:
            await ctx.response.send_message("Maintenance mode was allready enabled", ephemeral = True)
        else:
            await ctx.response.send_message("Maintenance mode is now enabled", ephemeral = True)
        self.__maintenance_mode_enabled = True
    
    async def maintenance_disable(self, ctx: discord.Interaction):
        if self.__maintenance_mode_enabled:
            await ctx.response.send_message("Maintenance mode is now disabled", ephemeral = True)
        else:
            await ctx.response.send_message("Maintenance mode was allready disabled", ephemeral = True)
        self.__maintenance_mode_enabled = False

async def setup(bot:commands.Bot):
    await bot.add_cog(Maintenance_Command(bot))