import asyncio
import discord
import time
import datetime
from staying_alive import staying_alive

from events import *


client = discord.Client()  # Creates the bot object
queue = EventQueue()


# Bot functions
@client.event
async def on_ready():
    print(client.user, " Has Logged In")


@client.event
async def on_message(message: discord.message.Message):
    msg = message.content
    start_message = "Invalid Command"

    # Adds eye strain command to the queue of events
    if (msg.startswith("+eyes")):
        queue.add(EyesCommand(datetime.datetime.now(),datetime.timedelta(), message.author))
        start_message = "Eye Strain Reduction Session Has Begun! Type +eyes To End It."

    # Adds pomodor studying technique session to the queue of events (refer to website for )
    if(msg.startswith("+pomodoro")):
        #queue.add(PomodoroCommand(datetime.datetime.now(),datetime.timedelta(), message.author))
        start_message = "Pomodoro Session Has Begun! Type +pomodoro To End It."


    

    await message.author.send(start_message)
    await run_queue()

    if msg.startswith("+add "):
        schedule_add = open('Database\\{message.author}.txt'.format(message=message),"a")
        schedule_add.write(formatted_event(msg) + "\n")
        schedule_add.close()
        await message.channel.send("Event Has Been Added")
    



async def run_queue():
    while not queue.is_empty():
        # print("-")
        if queue.is_ready():
            event = queue.pop()
            message = event.run_event(queue)
        # user = await client.fetch_user(event.user_id)
            user = event.user_id
            print(type(event))
            if message is not None:
                await user.send(message)


# Reads in the token
with open('token.txt') as file:
    token = file.readline()

staying_alive()
client.run(token) # Launches the bot 
