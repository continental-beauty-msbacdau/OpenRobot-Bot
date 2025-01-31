import discord
import config
import asyncpg
import mystbin
import boto3
import aioredis
import aiospotify
import aiohttp
from .ping import Ping
from .error import Error
from .driver import Driver
from .context import Context
from discord.ext import commands
from openrobot.api_wrapper import AsyncClient
from openrobot import discord_activities as discord_activity


class Bot(commands.Bot):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)

        self.running_commands = {}

        # Some other attrs that can be used
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.spotify: aiospotify.Client = aiospotify.Client(
            **config.AIOSPOTIFY_CRIDENTIALS, session=self.session
        )
        self.color: discord.Colour = None
        self.config = config
        self.mystbin: mystbin.Client = mystbin.Client(session=self.session)
        self.api: AsyncClient = AsyncClient(
            config.API_TOKEN, ignore_warning=True, session=self.session
        )
        self.ping: Ping = Ping(self)
        self.error: Error = Error(self)
        self.discord_activity: discord_activity.DiscordActivity = (
            discord_activity.DiscordActivity(config.TOKEN)
        )
        self.driver = Driver
        self.cdn = boto3.client("s3", **config.AWS_CRIDENTIALS)

        # Databases
        self.pool: asyncpg.Pool = None
        self.redis: aioredis.Redis = None
        self.spotify_pool: asyncpg.Pool = None
        self.spotify_redis: aioredis.Redis = None
        self.tb_pool: asyncpg.Pool = None

    async def get_context(
        self, message: discord.Message, *, cls: Context = Context
    ) -> Context:
        return await super().get_context(message, cls=cls)

    async def __invoke(self, ctx, **kwargs) -> None:
        if ctx.command is not None:
            self.dispatch("command", ctx)
            run_in_task = kwargs.pop("task", True)
            try:
                if await self.can_run(ctx, call_once=True):
                    if run_in_task:
                        task = await self.loop.create_task(ctx.command.invoke(ctx))
                        self.running_commands[ctx.message] = {"ctx": ctx, "task": task}
                    else:
                        await ctx.command.invoke(ctx)
                else:
                    raise commands.CheckFailure(
                        "The global check once functions failed."
                    )
            except commands.CommandError as exc:
                await ctx.command.dispatch_error(ctx, exc)
            else:
                self.dispatch("command_completion", ctx)
        elif ctx.invoked_with:
            exc = commands.CommandNotFound(
                'Command "{}" is not found'.format(ctx.invoked_with)
            )
            self.dispatch("command_error", ctx, exc)
