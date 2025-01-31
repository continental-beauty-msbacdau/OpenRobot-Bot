import time
import asyncpg
import aiohttp
from discord.ext import commands


class DatabasePing:
    def __init__(self, ping):
        self._ping = ping

    async def postgresql(
        self, format: str = "seconds", spotify: bool = False
    ) -> int | float | None:
        try:
            start = time.perf_counter()

            for _ in range(5):
                try:
                    if spotify:
                        await self._ping.bot.spotify_pool.execute("SELECT 1")
                    else:
                        await self._ping.bot.pool.execute("SELECT 1")
                except asyncpg.exceptions._base.InterfaceError:
                    pass
                else:
                    break

            result = time.perf_counter() - start

            if format.lower() in ["ms", "milliseconds", "millisecond"]:
                return result * 1000
            else:
                return result
        except:
            return None

    async def redis(
        self, format: str = "seconds", spotify: bool = False
    ) -> int | float | None:
        try:
            start = time.perf_counter()

            if spotify:
                await self._ping.bot.spotify_redis.ping()
            else:
                await self._ping.bot.redis.ping()

            result = time.perf_counter() - start

            if format.lower() in ["ms", "milliseconds", "millisecond"]:
                return result * 1000
            else:
                return result
        except:
            return None


class Ping:
    EMOJIS = {
        "postgresql": "<:postgresql:903286241066385458>",
        "redis": "<:redis:903286716058710117>",
        "bot": "\U0001f916",
        "discord": "<:BlueDiscord:842701102381269022>",
        "typing": "<a:typing:597589448607399949>",
        "openrobot-api": "<:OpenRobotLogo:901132699241168937>",
    }

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @property
    def database(self) -> DatabasePing:
        return DatabasePing(self)

    @property
    def db(self) -> DatabasePing:
        return self.database

    def bot_latency(self, format: str = "seconds") -> int | float:
        if format.lower() in ["ms", "milliseconds", "millisecond"]:
            return self.bot.latency * 1000
        else:
            return self.bot.latency

    async def discord_web_ping(self, format: str = "seconds") -> int | float:
        url = "https://discordapp.com/"

        start = time.perf_counter()
        async with self.bot.session.get(url) as resp:
            end = time.perf_counter()

            if format.lower() in ["ms", "milliseconds", "millisecond"]:
                return (end - start) * 1000
            else:
                return end - start

    async def typing_latency(self, format: str = "seconds") -> int | float:
        chan = self.bot.get_channel(903282453735678035)  # Typing Channel ping test

        start = time.perf_counter()
        await chan.trigger_typing()
        end = time.perf_counter()

        if format.lower() in ["ms", "milliseconds", "millisecond"]:
            return (end - start) * 1000
        else:
            return end - start

    async def api(self, format: str = "seconds") -> int | float:
        url = "https://api.openrobot.xyz/_internal/available"  # API ping test, fastest endpoint to test as it just returns a static JSON.

        start = time.perf_counter()
        async with self.bot.session.get(url) as resp:
            end = time.perf_counter()

            if format.lower() in ["ms", "milliseconds", "millisecond"]:
                return (end - start) * 1000
            else:
                return end - start
