import threading
import discord
from discord.ext import commands
from discord.ext.commands.core import has_permissions
from discord import *
import os,json
import time as times
import requests

#MODIFY DATA
PREFIX="YOUR PREFIX HERE"
TOKEN="YOUR TOKEN HERE"

intents=discord.Intents.all()
client=commands.Bot(command_prefix=PREFIX,intents=intents)
client.token=TOKEN
client.api="https://discord.com/api/v8"

if not os.path.isfile("scheduledmute.json"):
    with open("scheduledmute.json","w") as f:
        json.dump({"mutes":[],"roles":[]},f,indent=4)

@client.event
async def on_ready():
    print(f"Online als {client.user}")
    
def check_events():
    while True:
        with open("scheduledmute.json","r") as f:
            xd=json.load(f)
        for a in xd["mutes"]:
            if int(a[1]) <= times.time():
                xd.pop(xd.index(a))
                with open("scheduledmute.json","w") as f:
                    json.dump(xd,f,indent=4)
                if a[0] == "unmute":
                    headers={
                        "authorization":f"Bot {client.token}"
                    }
                    for a in xd["roles"]:
                        requests.delete(f"{client.api}/guilds/920739361304244264/members/{a[2]}/roles/{a}",headers=headers)
        times.sleep(1)

def convert(time):
    pos = ["s","m","h","d","w"]

    time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24, "w": 3600*24*7}

    unit = time[-1].lower()

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]

@client.event
async def on_command_error(ctx,error):
    if not isinstance(error,commands.CommandNotFound):
        embed=discord.Embed(description=str(error).capitalize(),color=discord.Colour.red())
        await ctx.send(embed=embed)

@client.event
async def on_message(message):
    if message.author.bot:
        return
    await client.process_commands(message)

@client.command()
@has_permissions(kick_members=True)
async def mute(ctx,member:discord.Member,*,time):
    time=convert(time)
    if not time in [-1,-2]:
        pass
    elif time==-1:
        raise commands.BadArgument("Possible Declarations: `s` second `m` minute `h` hour `d` day `w` week\nPlease separate the individual declarations with a /")
    else:
        raise commands.BadArgument("Please separate the individual declarations with a /")
    with open("scheduledmute.json","r") as f:
        xd=json.load(f)
    added=False
    for a in xd["roles"]:
        try:
            role=ctx.guild.get_role(a)
            await member.add_roles(role)
        except:
            pass
        else:
            added=True
    if added==False:
        return await ctx.send(embed=discord.Embed(description=f"There is no Muted Role, you can create one `{PREFIX}create_mute_role`",color=discord.Colour.red()))
    list=["unmute",times.time()+time,member.id]
    with open("scheduledmute.json","r") as f:
        xd=json.load(f)
    xd["mutes"].append(list)
    with open("scheduledmute.json","w") as f:
        json.dump(xd,f,indent=4)
    embed=discord.Embed(description=f"{member.mention} was muted for {time} seconds.",color=discord.Colour.green())
    await ctx.send(embed=embed)

@client.command()
@has_permissions(kick_members=True)
async def unmute(ctx,member:discord.Member):
    with open("scheduledmute.json","r") as f:
        xd=json.load(f)
    for a in xd["mutes"]:
        if a[0]=="unmute" and a[2]==member.id:
            xd[xd.index(a)][1]=times.time()
    with open("scheduledmute.json","w") as f:
        json.dump(xd,f,indent=4)
    embed=discord.Embed(description=f"{member.mention} was unmuted.",color=discord.Colour.green())
    await ctx.send(embed=embed)

@client.command()
@has_permissions(manage_guild=True)
async def create_mute_role(ctx):
    role=await ctx.guild.create_role("Muted")
    for channel in ctx.guild.channels:
        if isinstance(channel,discord.TextChannel):
            await channel.set_permissions(role,send_messages=False)
        elif isinstance(channel,discord.VoiceChannel):
            await channel.set_permissions(role,connect=False)
    with open("scheduledmute.json","r") as f:
        xd=json.load(f)
    xd["roles"].append(role.id)
    with open("scheduledmute.json","w") as f:
        json.dump(xd,f,indent=4)

t1=threading.Thread(target=check_events)
t1.start()
client.run(client.token)
