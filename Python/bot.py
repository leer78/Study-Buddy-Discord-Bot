import discord
import time
import datetime


client = discord.Client()


@client.event
async def on_ready():   
    print(client.user , " Has Logged In")


@client.event
async def on_message(message):    
    msg = message.content
    msg_content = msg.split()

    if msg.startswith("+add "):
        schedule_add = open('Database\\{message.author}.txt'.format(message=message),"a")
        schedule_add.write(formatted_event(msg) + "\n")
        schedule_add.close()
        await message.channel.send("Event Has Been Added")
        time.sleep(get_time(msg_content[2]))
        await message.author.send("REMINDER: {event}".format(event = msg_content[1]))
    if msg.startswith("+read"):
        schedule_read = open('Database\\names.txt',"r")


def formatted_event(msg):
    event = msg.split()
    return event[1] + ": " + event[2] 





client.run('') # DELETE BEFORE PUSHING DISCORD DOES NOT LIKE WHEN WE SHARE TOKEN ONLINE