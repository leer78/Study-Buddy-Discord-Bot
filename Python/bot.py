import asyncio
import discord
import time
import datetime
from discord.ext import tasks, commands

from pomodoro_events import *
from events import *
from to_do_events import *
from gaming_events import *
from water_events import *
from music_events import *


bot = commands.Bot(command_prefix='+')

queue = EventQueue()


# Bot functions
@bot.event
async def on_ready():
    print(bot.user, " Is Alive :)")


@bot.command(name="eyes")
async def eyes(ctx):
    queue.add(EyesCommand(datetime.datetime.now(), datetime.timedelta(), ctx.author))


@bot.command(name="pomodoro")
async def pomodoro(ctx):
    queue.add(PomodoroCommand(datetime.datetime.now(), datetime.timedelta(), ctx.author))


@bot.command(name="todoAdd")
async def to_do_add(ctx, *args):
    task = ''
    for arg in args:
        task += arg.strip('\n') + ' '
    queue.add(CreateToDoCommand(datetime.datetime.now(), datetime.timedelta(), ctx.author, task))


@bot.command(name="todoDelete")
async def to_do_delete(ctx, num):
    queue.add(DeleteToDoCommand(datetime.datetime.now(), datetime.timedelta(), ctx.author, num))


@bot.command(name="todoView")
async def to_do_view(ctx):
    queue.add(ViewToDoCommand(datetime.datetime.now(), datetime.timedelta(), ctx.author))


@bot.command(name="gaming")
async def gaming(ctx):
    queue.add(GamingCommand(datetime.datetime.now(), datetime.timedelta(), ctx.author))


@bot.command(name="water")
async def water(ctx):
    queue.add(WaterCommand(datetime.datetime.now(), datetime.timedelta(), ctx.author))


@bot.command(name="bottle")
async def bottle(ctx):
    queue.add(BottleCommand(datetime.datetime.now(), datetime.timedelta(), ctx.author))


@bot.command(name="studying?")
async def studying(ctx, user: discord.User):
    queue.add(CheckStudyingCommand(datetime.datetime.now(), datetime.timedelta(), ctx.author, user))


@bot.command(name='music')
async def music(ctx):
    queue.add(MusicReqCommand(datetime.datetime.now(), datetime.timedelta(), ctx.author))


@tasks.loop(seconds=1)
async def run_queue():
    if not queue.is_empty():
        if queue.is_ready():
            event = queue.pop()
            message = event.run_event(queue)
            user = event.user_id
            if message is not None:
                await user.send(message)


run_queue.start()
# Reads in the token
with open('../token.txt') as file:
    token = file.readline()

bot.run(token)  # Launches the bot
