import discord
from discord import app_commands
from discord.ext import commands
from cogs.base_cog import Base_Cog
import logging
from utils.portal import Portal

class About_Command(Base_Cog):
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        super().__init__(logging.getLogger("cmds.about"))

    @app_commands.command(name = "about", description = "Provides general information about the bot")
    async def about(self, ctx: discord.Interaction):
        portal:Portal = Portal.instance()
        embed = discord.Embed(title=f"POST IT - `{portal.PROGRAM_VERSION}`",
                      description="### Übersicht der Befehle\n- `/post` Veröffentlicht einen Post einer anderen Plattform, mit beliebigen Bildern als Anhang\n- `/help` Zeigt diese Übersicht an\n- `/settings` Persönliche Einstellungen für das verhalten des Bots\n- `/stats` Zeigt persönliche und globale Statistiken\n- `/debug` Erweiterte Informationen zum Betriebszustandes des Bots",
                      colour=0x5a5a5a)

        embed.add_field(name="Status des Bots",
                        value="Fehlerfrei :green_circle:",
                        inline=True)
        embed.add_field(name="Besitzer der Bot Instanz",
                        value=f"<@{portal.bot_config['DISCORD']['OWNER_ID']}>",
                        inline=True)

        await ctx.response.send_message(embed = embed, ephemeral = True)

async def setup(bot:commands.Bot):
    await bot.add_cog(About_Command(bot))

# class AddCog(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @app_commands.command(name="add", description="Füge ein neues Wort zur Liste hinzu")
#     async def add(self, interaction: discord.Interaction, new_word: str):
#         if new_word.lower() not in self.bot.known_words:
#             self.bot.known_words.append(new_word.lower())
#             await interaction.response.send_message(f"Wort '{new_word}' wurde zur Liste hinzugefügt.")
#         else:
#             await interaction.response.send_message(f"Wort '{new_word}' existiert bereits.")

# async def setup(bot):
#     await bot.add_cog(AddCog(bot))
