import discord
from discord.ext import commands
from discord import app_commands
import os

# GAMBIARRA RENDER - INÍCIO
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Vøx Bot tá online!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

keep_alive()
# GAMBIARRA RENDER - FIM

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'BOT ONLINE: {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'COMANDOS SINCRONIZADOS: {len(synced)}')
    except Exception as e:
        print(e)

# COLOCA SEUS COMANDOS AQUI EMBAIXO
# Exemplo:
@bot.tree.command(name="ping", description="Testa se o bot tá on")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓")

# NÃO APAGA ISSO AQUI DE BAIXO
if __name__ == "__main__":
    bot.run(TOKEN)
