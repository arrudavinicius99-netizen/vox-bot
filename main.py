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
CANAL_BOAS_VINDAS = 1504298479957053460
CANAL_REGRAS = 1504301990983897253
CANAL_INSCRICAO = 1504305510097358888
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

@bot.event
async def on_message(message):
    try:
        if message.author.bot or not message.guild:
            return
        user_id = str(message.author.id)
        if user_id not in db["users"]:
            db["users"][user_id] = {"xp": 0, "level": 1, "coins": 0, "daily": 0}
        db["users"][user_id]["xp"] += random.randint(5, 15)
        xp = db["users"][user_id]["xp"]
        level = db["users"][user_id]["level"]
        if xp >= level * 100:
            db["users"][user_id]["level"] += 1
            db["users"][user_id]["xp"] = 0
            db["users"][user_id]["coins"] += level * 50
            embed = discord.Embed(title="LEVEL UP!", description=f"{message.author.mention} subiu para nivel {level + 1}!", color=0x00ff00)
            await message.channel.send(embed=embed)
        save_db(db)
        msg = message.content.lower()
        if bot.user.mentioned_in(message):
            if "como entrar" in msg or "recrutar" in msg:
                await message.channel.send(f"{message.author.mention} Usa /recrutar!")
                return
            if "treino" in msg or "horario" in msg:
                await message.channel.send(f"{message.author.mention} Agenda no /eventos!")
                return
            await message.channel.send(random.choice([f"Salve {message.author.mention}! /ajuda", f"Fala {message.author.mention}! /ping"]))
        if "bom dia" in msg:
            await message.channel.send(f"Bom dia {message.author.mention}!")
        if "boa noite" in msg:
            await message.channel.send(f"Boa noite {message.author.mention}!")
        if "boa tarde" in msg:
            await message.channel.send(f"Boa tarde {message.author.mention}!")
        if "vortex" in msg:
            await message.channel.send("**VORTEX ESP** - Disciplina | Estrategia | Evolucao")
        if "ff" in msg or "free fire" in msg:
            await message.channel.send("FREE FIRE E VIDA! /membros")
        if any(p in msg for p in ["fdp", "krl", "porra", "vsf", "caralho"]):
            await message.delete()
            if user_id not in db["warns"]:
                db["warns"][user_id] = 0
            db["warns"][user_id] += 1
            save_db(db)
            await message.channel.send(f"{message.author.mention} Sem palavrão! Avisos: {db['warns'][user_id]}/3", delete_after=5)
            if db["warns"][user_id] >= 3:
                await message.author.timeout(timedelta(minutes=10))
    except Exception as e:
        print(f"ERRO on_message: {e}")
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    canal = bot.get_channel(CANAL_BOAS_VINDAS)
    if canal:
        embed = discord.Embed(title="BEM-VINDO A VORTEX ESP", description=f"E ai {member.mention}! Membro #{member.guild.member_count}", color=0x00ff00)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="REGRAS", value=f"<#{CANAL_REGRAS}>", inline=False)
        embed.add_field(name="INSCRICAO", value=f"<#{CANAL_INSCRICAO}>", inline=False)
        await canal.send(embed=embed)

@bot.tree.command(name="ping", description="Mostra a latencia do bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")

@bot.tree.command(name="ajuda", description="Lista todos os comandos")
async def ajuda(interaction: discord.Interaction):
    embed = discord.Embed(title="VOX BOT - COMANDOS", color=0x00ffff)
    embed.add_field(name="INFO", value="`/ping` `/serverinfo` `/userinfo` `/avatar`", inline=False)
    embed.add_field(name="GUILDA", value="`/regras` `/recrutar` `/eventos` `/membros`", inline=False)
    embed.add_field(name="RANK", value="`/rank` `/daily` `/coins` `/top`", inline=False)
    embed.add_field(name="STAFF", value="`/aviso` `/mutar` `/kick` `/ban` `/limpar` `/warn`", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="serverinfo", description="Informacoes do servidor")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=guild.name, color=0x3498db)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Membros", value=guild.member_count, inline=True)
    embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
    embed.add_field(name="Criado em", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rank", description="Mostra seu rank")
async def rank(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if uid not in db["users"]:
        db["users"][uid] = {"xp": 0, "level": 1, "coins": 0, "daily": 0}
    level = db["users"][uid]["level"]
    xp = db["users"][uid]["xp"]
    coins = db["users"][uid]["coins"]
    embed = discord.Embed(title=f"RANK {interaction.user.name}", color=0xFFD700)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="XP", value=f"{xp}/{level * 100}", inline=True)
    embed.add_field(name="Coins", value=coins, inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daily", description="Resgata coins diarios")
async def daily(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if uid not in db["users"]:
        db["users"][uid] = {"xp": 0, "level": 1, "coins": 0, "daily": 0}
    agora = datetime.now().timestamp()
    if agora - db["users"][uid].get("daily", 0) < 86400:
        tempo = 86400 - (agora - db["users"][uid]["daily"])
        await interaction.response.send_message(f"Volte em {int(tempo // 3600)}h {int(tempo % 3600 // 60)}m", ephemeral=True)
        return
    recompensa = random.randint(100, 500)
    db["users"][uid]["coins"] += recompensa
    db["users"][uid]["daily"] = agora
    save_db(db)
    embed = discord.Embed(title="DAILY RESGATADO!", description=f"+{recompensa} coins! Saldo: {db['users'][uid]['coins']}", color=0x00ff00)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="coins", description="Ve quantas coins voce tem")
async def coins(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    if uid not in db["users"]:
        db["users"][uid] = {"xp": 0, "level": 1, "coins": 0, "daily": 0}
    await interaction.response.send_message(f"{interaction.user.mention} tem {db['users'][uid]['coins']} coins")

@bot.tree.command(name="top", description="Top 10 membros por level")
async def top(interaction: discord.Interaction):
    top_users = sorted(db["users"].items(), key=lambda x: x[1]["level"], reverse=True)[:10]
    embed = discord.Embed(title="TOP 10 LEVELS", color=0xFFD700)
    texto = ""
    for pos, (uid, data) in enumerate(top_users, 1):
        try:
            user = await interaction.guild.fetch_member(int(uid))
            texto += f"{pos}. {user.display_name} - Level {data['level']}\n"
        except:
            pass
    embed.description = texto or "Ninguem no rank ainda"
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="limpar", description="Deleta mensagens do canal")
async def limpar(interaction: discord.Interaction, quantidade: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Voce nao tem permissao", ephemeral=True)
        return
    if quantidade > 100:
        await interaction.response.send_message("Maximo 100", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deletadas = await interaction.channel.purge(limit=quantidade)
    await interaction.followup.send(f"Deletei {len(deletadas)} mensagens", ephemeral=True)

from flask import Flask
import threading

app = Flask('')
@app.route('/')
def home():
    return "Bot online"

def run():
    app.run(host='0.0.0.0', port=10000)

t = threading.Thread(target=run)
t.start()

if __name__ == "__main__":
    bot.run(TOKEN)
