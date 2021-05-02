import asyncio
import discord
import time
import datetime
from discord.ext import commands

from events import *




bot = commands.Bot(command_prefix = '+')

queue = EventQueue()


# Bot functions
@bot.event
async def on_ready():
    print(bot.user, " Has Logged In")




@bot.command(name = "eyes")
async def eyes(ctx):
    queue.add(EyesCommand(datetime.datetime.now(),datetime.timedelta(), ctx.author))



async def run_queue():
    #while not queue.is_empty():
        # print("-")
       # if queue.is_ready():
    event = queue.pop()
    message = event.run_event(queue)
        # user = await client.fetch_user(event.user_id)
    user = event.user_id
    if message is not None:
        await user.send(message)



# Reads in the token
with open('token.txt') as file:
    token = file.readline()

bot.run(token) # Launches the bot 
