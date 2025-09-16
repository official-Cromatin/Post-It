import discord
from discord import app_commands
from discord.ext import commands
from cogs.base_cog import Base_Cog

import logging
from urllib.parse import urlparse
from asyncpraw.models import Submission
from utils.portal import Portal
import aiohttp
from PIL import Image
from io import BytesIO
from datetime import datetime
from utils.datetime_tools import get_elapsed_time_milliseconds

class NoMediaFound(Exception): 
    pass

class Post_Command(Base_Cog):
    def __init__(self, bot:commands.Bot):
        self.__bot = bot
        super().__init__(logging.getLogger("cmds.post"))

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
    async def post(self, ctx:discord.Interaction, url:str, custom_note:str = None, use_title:bool = True, quality:app_commands.Choice[int] = 95):
        try:
            domain_info = urlparse(url)
            portal = Portal.instance()
            toplevel_domain = '.'.join(domain_info.netloc.split('.')[-2:])
            begin_process = datetime.now().timestamp()
            match toplevel_domain:
                case "reddit.com":
                    self._logger.debug(f"Recieved command by {ctx.user} ({ctx.user.id}) for reddit ({url})")

                    subm:Submission = await portal.reddit_adapter.fetch(url)
                    image_urls = []
                    # Check if submission has a gallery
                    if hasattr(subm, "media_metadata"):
                        for media_id, media in subm.media_metadata.items():
                            file_extension = media["m"].split("/")[1]
                            if file_extension not in ("jpg", "jpeg", "png", "webp", "heic", "heif"):
                                continue
                            image_urls.append(f"https://i.redd.it/{media_id}.{file_extension}")
                    else:
                        image_urls.append(subm.url)
                    image_count = len(image_urls)
                    if image_count == 0:
                        raise NoMediaFound
                    self._logger.debug(f"Found {image_count} image urls for the post")

                    progress_title = f"`{image_count}` images are going to be converted, it may take a while."
                    progress_temp = progress_title + f"\n`0` of `{image_count}` have already been loaded"
                    await ctx.response.send_message(progress_temp, ephemeral = True)

                    if isinstance(quality, app_commands.Choice):
                        quality_value = quality.value
                    else:
                        quality_value = quality

                    # Download and convert each image
                    image_files:list[discord.File] = []
                    begin_conversion = datetime.now().timestamp()
                    async with aiohttp.ClientSession() as session:
                        index = 0
                        for image_url in image_urls:
                            async with session.get(image_url) as response:
                                response.raise_for_status()
                                image_data = await response.read()

                            original_image = Image.open(BytesIO(image_data))
                            webp_buffer = BytesIO()
                            original_image.save(webp_buffer, format = "WEBP", quality = quality_value)
                            webp_buffer.seek(0)
                            image_file = discord.File(webp_buffer, filename = f"image_{index}.webp")
                            image_files.append(image_file)
                            index += 1

                            progress_temp = progress_title + f"\n`{index}` of `{image_count}` have already been loaded"
                            await ctx.edit_original_response(content = progress_temp)
                        
                    self._logger.debug(f"Downloaded and converted {len(image_files)} images in {get_elapsed_time_milliseconds(datetime.now().timestamp() - begin_conversion)}")
                    
                    author = subm.author.name if subm.author else "Author not found"
                    content = f":copyright: [{author}]({url})"
                    if use_title:
                        content += f"\n# {subm.title}"

                    if custom_note:
                        content += f"\n> {custom_note}"
                    
                    await ctx.delete_original_response()
                    message = await ctx.followup.send(
                        content = content,
                        suppress_embeds = True,
                        files = image_files
                    )

                    self._logger.info(f"Successfully processed the command executed by {ctx.user.name} ({ctx.user.id}) after {get_elapsed_time_milliseconds(datetime.now().timestamp() - begin_process)} (ID of message: {message.id})")
                
                # No domain for seperation found
                case _:
                    if toplevel_domain == "":
                        toplevel_domain = "not_found"
                        
                    embed = discord.Embed(
                        title = "Domain not found",
                        description = f"The requested domain `{toplevel_domain}` is currently not supported\nOpen [an issue](https://github.com/official-Cromatin/Post-It/issues/new?assignees=&labels=feature-request&projects=&template=feature_request.yml) to request support for it.\n\nCurrently supported plattforms:\n- Reddit",
                        color = 0xED4337)

                    await ctx.response.send_message(embed = embed, ephemeral = True)

        except NoMediaFound:
            self._logger.error(f"Aborted issued command by {ctx.user.name} ({ctx.user.id}). Post had no media attatched")

            # Delete the original response, if existing
            try:
                await ctx.delete_original_response()
            except discord.NotFound:
                pass
            embed = discord.Embed(
                title = "No media found",
                description = "The post had no media attatched, or was in an unsupported format\nVideos are not supported! (yet)",
                color = 0xED4337
            )
            embed.set_footer(text = "Supported image formats: jpg, jpeg, png, webp, heic, heif")

        except discord.errors.HTTPException as error:
            self._logger.error(f"Could not complete command by {ctx.user.name} ({ctx.user.id})")
            self._logger.exception(error, stack_info = True)

            match error.code:
                case 40005:
                    self._logger.error("Failed to upload images, payload too large")

                    embed = discord.Embed(
                        title = "Error while processing",
                        description = "The attachments exceed the upload limit of Discord,\nchoose a different quality level via the argument `quality`",
                        color = 0xED4337
                    )

                    if ctx.response.is_done():
                        await ctx.followup.send(embed = embed, ephemeral = True)
                    else:
                        await ctx.response.send_message(embed = embed)

        except Exception as error:
            self._logger.error(f"Could not complete command by {ctx.user.name} ({ctx.user.id})")
            self._logger.exception(error, stack_info = True)

            # Delete the original response, if existing
            try:
                await ctx.delete_original_response()
            except discord.NotFound:
                pass

            # Explain to the user what the error was
            embed = discord.Embed(
                title = "Error while processing",
                description = f"While we processed your request, the following exception occured: `{error}`",
                color = 0xED4337
            )
            if ctx.response.is_done():
                await ctx.followup.send(embed = embed, ephemeral = True)
            else:
                await ctx.response.send_message(embed = embed)


async def setup(bot:commands.Bot):
    await bot.add_cog(Post_Command(bot))