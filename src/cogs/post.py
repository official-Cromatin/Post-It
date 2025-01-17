import discord
from discord import app_commands
from discord.ext import commands
from cogs.base_cog import Base_Cog

import logging
from urllib.parse import urlparse
from praw.models import Submission, Subreddit
from utils.portal import Portal
import aiohttp
from PIL import Image
from io import BytesIO
from datetime import datetime
from utils.datetime_tools import get_elapsed_time_milliseconds

class Post_Command(Base_Cog):
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        super().__init__(logging.getLogger("cmds.post"))

    @app_commands.command(name = "post", description = "Post an embed in the Current Channel with a link to the content")
    async def post(self, ctx:discord.Interaction, url:str, custom_note:str = None):
        domain_info = urlparse(url)
        portal = Portal.instance()
        toplevel_domain = '.'.join(domain_info.netloc.split('.')[-2:])
        match toplevel_domain:
            case "reddit.com":
                await ctx.response.defer()

                subm:Submission = portal.reddit_adapter.fetch(url)
                embeds = []

                image_urls = []
                # Check if submission has a gallery
                if hasattr(subm, "media_metadata"):
                    for media_id, media in subm.media_metadata.items():
                        file_extension = media["m"].split("/")[1]
                        image_urls.append(f"https://i.redd.it/{media_id}.{file_extension}")
                else:
                    image_urls.append(subm.url)
                self._logger.debug(f"Found {len(image_urls)} image urls for the post")

                # Download and convert each image
                image_files:list[discord.File] = []
                begin_conversion = datetime.now().timestamp()
                async with aiohttp.ClientSession() as session:
                    index = 0
                    for image_url in image_urls:
                        async with session.get(image_url) as response:
                            response.raise_for_status()  # Fehlerbehandlung für HTTP-Status
                            image_data = await response.read()  # Bilddaten im RAM laden

                        original_image = Image.open(BytesIO(image_data))  # Originalbild laden
                        webp_buffer = BytesIO()  # Puffer für WebP-Bild
                        original_image.save(webp_buffer, format="WEBP", lossless=True)  # WebP speichern
                        webp_buffer.seek(0)
                        image_file = discord.File(webp_buffer, filename = f"image_{index}.webp")
                        image_files.append(image_file)

                        index += 1
                    
                self._logger.debug(f"Downloaded and converted {len(image_files)} images in {get_elapsed_time_milliseconds(datetime.now().timestamp() - begin_conversion)}")
                
                author = subm.author.name if subm.author else "Author not found"
                content = f":copyright: [{author}]({url})"
                if custom_note:
                    content += f"\n> {custom_note}"
                
                await ctx.followup.send(
                    content = content,
                    suppress_embeds = True,
                    files = image_files
                )

                # embed = discord.Embed(url = "https://discord.com/humans.txt", color = int(portal.platforms_config["REDDIT"]["embed_color"], 16))
                # embed.set_author(name = subm.title)
                # embeds.append(embed)

                # embed.add_field(
                #     name = "Author",
                #     value = f"[u/{subm.author}](https://www.reddit.com/user/{subm.author})",
                #     inline = True)
                # embed.add_field(
                #     name = "Subreddit",
                #     value = f"[r/{subm.subreddit.display_name}]({url})",
                #     inline = True)
                # if subm.selftext:
                #     embed.add_field(
                #         name = "Discription",
                #         value = subm.selftext,
                #         inline = False)
                
                # for image_url in image_urls:
                #     embed = discord.Embed(url = "https://discord.com/humans.txt")
                #     embed.set_image(url = image_url)
                #     embeds.append(embed)
            
            # No domain for seperation found
            case _:
                embed = discord.Embed(
                    title = "Domain not found",
                    description = f"The requested domain `{toplevel_domain}` is currently not supported\nOpen [an issue](https://github.com/official-Cromatin/Post-It/issues/new?assignees=&labels=feature-request&projects=&template=feature_request.yml) to request support for it.\n\nSee an list of supported platforms with the `/platforms` command",
                    color = 0xED4337)

                await ctx.response.send_message(embed = embed)


async def setup(bot:commands.Bot):
    await bot.add_cog(Post_Command(bot))