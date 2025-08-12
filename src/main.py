import asyncio
from datetime import datetime
from utils.logger.custom_logging import Custom_Logger
import logging
from pathlib import Path
import sys, signal
import os
import dotenv
from bot import PostIt_Bot
from utils.datetime_tools import get_elapsed_time_milliseconds, get_elapsed_time_big
import discord

async def main(event_loop:asyncio.AbstractEventLoop, close_event:asyncio.Event):
    PROGRAM_VERSION = "1.0"
    print("      ____  ____  ___________    __________")
    print("     / __ \/ __ \/ ___/_  __/   /  _/_  __/")
    print("    / /_/ / / / /\__ \ / /_____ / /  / /   ")
    print("   / ____/ /_/ /___/ // /_____// /  / /    ")
    print(f"  /_/    \____//____//_/     /___/ /_/ v{PROGRAM_VERSION}")
    print("  Copyright (c) 2024-2025 Lars Winzer")
    print()
    print("  Source: https://github.com/official-Cromatin/Post-It")
    print("  Report an Issue: https://github.com/official-Cromatin/Post-It/issues/new?assignees=&labels=bug&projects=&template=issue_report.yml")
    print("\n")

    # Get timestamp for begin of actual execution
    startup_time = datetime.now().timestamp()

    # Initialize the logger
    Custom_Logger.initialize()
    app_logger = logging.getLogger("app")
    app_startup_logger = logging.getLogger("app.startup")
    app_startup_logger.info(f"Starting Post-It v{PROGRAM_VERSION} ...")

    # Detect entrypoint
    source_path = Path(__file__).resolve()
    base_path = source_path.parents[1]
    app_startup_logger.info(f"Using the following path as entrypoint: '{base_path}'")

    # Detect operating system and attach
    shutdown_event = asyncio.Event()
    def signal_handler(*args):
        app_logger.info("Shutdown signal recieved, shutting down")
        event_loop.call_soon_threadsafe(shutdown_event.set)
        close_event.set()

    match sys.platform:
        case "linux":
            app_startup_logger.info("Detected platform: Linux")
            event_loop.add_signal_handler(signal.SIGINT, signal_handler)
            event_loop.add_signal_handler(signal.SIGTERM, signal_handler)

        case "darwin:":
            app_startup_logger.info("Detected platform: MacOS (Darwin)")
            event_loop.add_signal_handler(signal.SIGINT, signal_handler)
            event_loop.add_signal_handler(signal.SIGTERM, signal_handler)

        case "win32":
            app_startup_logger.info("Detected platform: Windows (Win32)")
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        
        case _:
            app_startup_logger.fatal(f"Detected unsupported platform: {sys.platform}")
            quit(1)

    # Load environment variables
    if (os.getenv("skip_dotenv", False)):
        app_startup_logger.warning("Skipped import of dotenv file")
    else:
        dotenv.load_dotenv(base_path / ".env")
        app_startup_logger.warning("Imported dotenv file")

        # Check if required environment variables are present
        check_ok = True
        required_variables = [
            "DISCORD_TOKEN",
        ]

        for variable_name in required_variables:
            if os.getenv(variable_name) is None:
                app_startup_logger.error(f"Environment variable '{variable_name}' is missing")
                check_ok = False

        if not check_ok:
            app_startup_logger.critical("Multiple required variables are missing. Aborting startup")
            quit(1)

    # Create bot instance and start bot
    app_startup_logger.info(f"Preperations complete after {get_elapsed_time_milliseconds(datetime.now().timestamp() - startup_time)}, launching bot")
    try:
        bot_instance = PostIt_Bot(startup_time, PROGRAM_VERSION, app_logger)

        bot_task = event_loop.create_task(bot_instance.start(os.getenv("DISCORD_TOKEN")))
        shutdown_task = event_loop.create_task(shutdown_event.wait())

        # Wait if either the bot disconnects or the shutdown event is detected
        finished_task, _ = await asyncio.wait(
            [shutdown_task, bot_task],
            return_when = asyncio.FIRST_COMPLETED
        )

        if shutdown_task in finished_task:
            await bot_instance.close()
            app_logger.info("Bot closed connection successfully")
    
    except discord.errors.LoginFailure:
        app_logger.critical("Improper token has been passed. Aborting startup")
        quit(1)

    finally:
        close_event.set()
        app_logger.info(f"Exiting. Application ran for {get_elapsed_time_big(datetime.now().timestamp() - startup_time)}")

# Entry point for execution
if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    asyncio.set_event_loop(event_loop)
    close_event = asyncio.Event()

    event_loop.run_until_complete(main(event_loop, close_event))

    # Wait until program is ready to close
    event_loop.run_until_complete(close_event.wait())
    event_loop.close()
