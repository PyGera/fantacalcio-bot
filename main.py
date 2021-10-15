
"""

Fantacalcio Discord Bot

made with 💘 by Federico Gerardi


"""


import discord
from discord.ext import commands, tasks
import requests
import datetime
from dotenv import load_dotenv
import os
from commands.fantacalcio.live import live
from commands.presentation.invite import invite
from commands.presentation.help import help_function
from commands.results.matches import matches_function as matches, match_back, match_forward, match_now
from commands.results.standings import standings, standings_now
from pymongo import MongoClient
from bson.objectid import ObjectId

load_dotenv()

FOOTBALL_API_HEADERS = {"apikey": os.environ['FOOTBALL_API_KEY']}

# Initializing the bot
client = commands.Bot(command_prefix="f!")
client.remove_command("help")
db_client = MongoClient(f"mongodb+srv://root:{os.environ['DB_PASSWORD']}@stats.bibxu.mongodb.net/?retryWrites=true&w=majority")
db = db_client.stats

@tasks.loop()
async def sendData():
    guild = client.get_guild(886727465026854912)

    # requests.post('http://localhost:8080/api/sendData', data={'servers': len(client.guilds), 'users': guild.member_count})
    db.data.update_one({"_id": ObjectId("6169bf78386bbf78ac0e18f1")},{"$set": {'servers': len(client.guilds), 'users': guild.member_count}}, upsert=False)


@client.event
async def on_ready():
    # Log in bot
    await client.change_presence(status=discord.Status.idle, activity=discord.Game('f!help'))
    print('Logged on as 🧙⚽🤖#2397')
    sendData.start()


@client.event
async def on_message(message):
    # Bot messagges processing
    print(f'Message from {message.author}: {message.content}')  
    await client.process_commands(message)

@client.event
async def on_reaction_add(reaction, user):

    # Reaction Manager
    if user.id != client.user.id:
        emojis = ["⬅️", "➡️", "🔄", "🕙", "🔁"]
        
        # f!matches command

        # Going Back
        if str(reaction.emoji) == emojis[0]:
            await reaction.message.remove_reaction("⬅️", user)
            await reaction.message.remove_reaction("⬅️", client.user)
            await reaction.message.remove_reaction("➡️", client.user)
            await reaction.message.remove_reaction("🔄", client.user)
            await match_back(reaction.message, client, FOOTBALL_API_HEADERS)
            
        # Going ahead
        elif str(reaction.emoji) == emojis[1]:
            await reaction.message.remove_reaction("➡️", user)
            await reaction.message.remove_reaction("⬅️", client.user)
            await reaction.message.remove_reaction("➡️", client.user)
            await reaction.message.remove_reaction("🔄", client.user)
            await match_forward(reaction.message, client, FOOTBALL_API_HEADERS)

        # Updating result
        elif str(reaction.emoji) == emojis[2]:
            await reaction.message.remove_reaction("🔄", user)
            await match_now(reaction.message, client, FOOTBALL_API_HEADERS)
        
        # Back home
        elif str(reaction.emoji) == emojis[3]:
            await reaction.message.remove_reaction("🕙", user)
            await reaction.message.remove_reaction("🕙", client.user)
            await match_now(reaction.message, client, FOOTBALL_API_HEADERS)
        
        # f!standings command

        # Update standing
        elif str(reaction.emoji) == emojis[4]:
            await reaction.message.remove_reaction("🔁", user)
            await standings_now(reaction.message, client, FOOTBALL_API_HEADERS)

@client.command(name='live')
async def _live(ctx, squadra):
    await live(ctx, squadra, FOOTBALL_API_HEADERS)

@client.command(name='matches')
async def _matches(ctx):
    await matches(ctx, client, FOOTBALL_API_HEADERS)

@client.command(name='standings')
async def _standings(ctx):
    await standings(ctx, client, FOOTBALL_API_HEADERS)

@client.command(name='invite')
async def _invite(ctx):
    await invite(ctx)


@client.command(name='help')
async def _help(ctx):
    await help_function(ctx)



client.run(os.environ['PRODUCTION_TOKEN']) # Production 
# client.run(os.environ['TEST_BOT_TOKEN']) # Test
