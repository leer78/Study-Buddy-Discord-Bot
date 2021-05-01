import discord

client = discord.Client()


@client.event
async def on_ready():
    print(client.user , " Has Logged In")


@client.event
async def on_message(message):
    msg = message.content

    if msg.startswith("+add "):
        schedule_add = open('Database\\{message.author}.txt'.format(message=message),"a")
        schedule_add.write(formatted_event(msg) + "\n")
        schedule_add.close()
        await message.channel.send("Event Has Been Added")

    if msg.startswith("+read"):
        schedule_read = open('Database\\names.txt',"r")


def formatted_event(msg):
    event = msg.split()
    return event[1] + ": " + event[2] +"-" +event[3]


    

client.run('ODM3ODMxODk2MTQ2NzcxOTk4.YIyRwg.sFEwy8sipdy1_Sngyt48GaOx9rU')