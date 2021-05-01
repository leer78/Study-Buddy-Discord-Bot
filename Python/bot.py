import discord
import time
import datetime


client = discord.Client() # Creates the bot object


# Bot functions
@client.event
async def on_ready():   
    print(client.user , " Has Logged In")


@client.event
async def on_message(message: discord.message.Message):
    msg = message.content
    msg_content = msg.split()


    if msg.startswith("+add "):
        schedule_add = open('Database\\{message.author}.txt'.format(message=message),"a")
        schedule_add.write(formatted_event(msg) + "\n")
        schedule_add.close()
        await message.channel.send("Event Has Been Added")
    if msg.startswith("+read"):
        schedule_read = open('Database\\names.txt',"r")



def formatted_event(msg):
    event = msg.split()
    return event[1] + ": " + event[2] 


# Reads in the token 
with open('token.txt') as file:
    token = file.readline()

client.run(token) # Launches the bot 