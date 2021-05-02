import asyncio
import discord
import time
import datetime
from discord.ext import tasks, commands

from events import *




bot = commands.Bot(command_prefix = '+')

queue = EventQueue()


# Bot functions
@bot.event
async def on_ready():
    print(bot.user, " Is Alive :)")


@bot.command(name = "eyes")
async def eyes(ctx):
    queue.add(EyesCommand(datetime.datetime.now(),datetime.timedelta(), ctx.author))



@tasks.loop(minutes=0.1)
async def run_queue():   
    if not queue.is_empty():
        print(queue.view())
        event = queue.pop()  
        print("MADE IT BEFORE MESSAGE:" )
        message = event.run_event(queue)
        print("AFTER MESSAGE:" )
        # user = await client.fetch_user(event.user_id)
        user = event.user_id
        if message is not None:
            await user.send(message)




run_queue.start()
# Reads in the token
with open('token.txt') as file:
    token = file.readline()

bot.run(token) # Launches the bot 
