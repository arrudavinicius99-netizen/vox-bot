              import discord
import os
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import json
import traceback
from datetime import datetime, timedelta

TOKEN = os.getenv("TOKEN")
GUILD_ID = 1504180595511791616
CANAL_BOAS_VINDAS = 1504301990983897253
CANAL_REGRAS = 1504305510097358888
CANAL_INSCRICAO = 1504307560920997889
CARGO_STAFF = 1504298479957053462

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.moderation = True
bot = commands.Bot(command_prefix="!", intents=intents)

def load_db():
    if not os.path.exists("database.json"):
        with open("database.json", "w") as f:
            json.dump({"users": {}, "warns": {}}, f)
    with open("database.json", "r") as f:
        return json.load(f)

def save_db(data):
    with open("database.json", "w") as f:
        json.dump(data, f)

db = load_db()

@bot.event
async def on_ready():
    print(f"BOT ONLINE: {bot.user}")
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"COMANDOS SINCRONIZADOS: {len(synced)}")
    except Exception as e:
        print(f"ERRO SYNC: {e}")
        traceback.print_exc()

@bot.tree.command(name="ping", description="Mostra a latencia do bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")

if __name__ == "__main__":
    bot.run(TOKEN)
