import asyncio
import discord
import time
import datetime
from discord.ext import commands

from events import *


client = discord.Client() # Creates the bot object
queue = EventQueue()


# Bot functions
@client.event
async def on_ready():       
    print(client.user , " Has Logged In")


@client.event
async def on_message(message: discord.message.Message):
    msg = message.content

    # Adds eye strain command to the queue of events
    if (msg.startswith("+eyes")):
        queue.add(EyesCommand(datetime.datetime.now(), datetime.timedelta(), message.author))
        
    await run_queue()

    
async def run_queue():
   
    while not queue.is_empty():  
        #print("-") 
        if queue.is_ready():   
            queue.view()
            print("IM READY") 
            event = queue.pop()
            message = event.run_event(queue)
        #user = await client.fetch_user(event.user_id)
            user = event.user_id
            if message is not None:
                await user.send(message)
            await user.send("hello")
    print("IM OUT")



# Reads in the token 
with open('token.txt') as file:
    token = file.readline()

client.run(token) # Launches the bot 