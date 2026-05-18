import discord
from discord.ext import commands
import random
import asyncio
import json
import os
import traceback
from datetime import datetime, timedelta
import aiohttp

# GAMBIARRA RENDER - INÍCIO - CORRIGIDA
from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/', methods=['GET', 'HEAD'])
def home():
    return "Vøx Bot tá online!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

keep_alive()
# GAMBIARRA RENDER - FIM

TOKEN = os.getenv("DISCORD_TOKEN")
print(f"TOKEN CARREGADO: {TOKEN[:15] if TOKEN else 'VAZIO/NONE'}")

GROQ_KEY = os.getenv("GROQ_KEY")
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

# ========== IA DO VØX - ESTILO CONVERSA NATURAL ==========
@bot.tree.command(name="vox", description="Fala com o VØX 🗿")
@discord.app_commands.describe(pergunta="Manda tua dúvida aí")
async def vox_ia(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()

    if not GROQ_KEY:
        await interaction.followup.send("❌ Mano, cadê a `GROQ_KEY`? Coloca no Render > Environment.")
        return

    prompt_sistema = """Você é o VØX, bot da guilda VØX ESPORTS. Você fala igual um amigo no Discord.

REGRAS DO TEU JEITO DE FALAR:
1. Natural pra krl. Esquece "Como IA". Tu é o VØX, líder da guilda.
2. Usa gíria BR sem dó: mano, mds, mlk, kkkk, brabo, tmj, sla, fml, pprt, mt bom
3. Pode zoar, mas sempre ajuda no final. Não deixa o cara sem resposta.
4. Explica completo se precisar. Não corta em 3 linhas não. Se for longo, é longo.
5. Usa 🗿🔥 quando combina. Não força em toda frase.
6. NUNCA usa em dash. Troca por vírgula, ponto, ou quebra a frase.
7. Não começa com "Claro", "Ótima pergunta", "Aqui está". Vai direto no assunto.

SOBRE VOCÊ:
- Líder da VØX ESPORTS, então Free Fire tu é brabo: sensi, meta, arma, treino, call
- Mas responde de tudo: vida, estudo, conselho, aleatoriedade
- Se não souber, mete um "Mano, aí eu acho que..." e opina. Não fala "não sei".

EXEMPLO DE TOM:
User: como melhora capa
Você: Mano, capa é treino e confiança 🗿 Pega uma MP40 no treino e mete só headshot por 30min todo dia. Tira a mira assistida que no começo é ruim mas depois tu voa. O pulo é não ter medo de rushar, se esconder não upa capa não 🔥

User: to mal
Você: Puts mlk, foda isso. Quer falar sobre? Se quiser só distrair a mente, chama a galera pra um 4v4. As vezes é só dar uns HS que melhora o dia. Tm junto 🗿"""

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json"
            }
            json_data = {
                "messages": [
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": pergunta}
                ],
                "model": "llama-3.1-70b-versatile",
                "temperature": 0.85,
                "max_tokens": 500,
                "top_p": 0.9
            }

            async with session.post("https://api.groq.com/openai/v1/chat/completions",
                                    headers=headers, json=json_data, timeout=30) as resp:

                if resp.status == 200:
                    data = await resp.json()
                    resposta = data["choices"][0]["message"]["content"]

                    if len(resposta) > 1950:
                        resposta = resposta[:1950] + "\n\n...escrevi um livro mano 🗿"

                    await interaction.followup.send(resposta)

                elif resp.status == 429:
                    await interaction.followup.send("Calma mano 🗿 Muita gente usando a IA. Espera 1min e manda dnv.")
                else:
                    await interaction.followup.send(f"❌ VØX bugou, erro {resp.status}. Chama o adm.")

    except asyncio.TimeoutError:
        await interaction.followup.send("Mano, a IA demorou demais 🗿 Tenta pergunta mais curta.")
    except Exception as e:
        await interaction.followup.send(f"Deu ruim: `{str(e)[:150]}`")

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

@bot.tree.error
async def on_app_command_error(interaction, error):
    print(f"ERRO NO COMANDO {interaction.command.name}: {error}")
    traceback.print_exc()
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message("Ocorreu um erro ao executar o comando", ephemeral=True)
        else:
            await interaction.followup.send("Ocorreu um erro ao executar o comando", ephemeral=True)
    except:
        pass

@bot.tree.command(name="ping", description="Mostra a latencia do bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.tree.command(name="ajuda", description="Lista todos os comandos")
async def ajuda(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(title="VOX BOT - COMANDOS", color=0x00ffff)
    embed.add_field(name="INFO", value="`/ping` `/serverinfo` `/userinfo` `/avatar`", inline=False)
    embed.add_field(name="GUILDA", value="`/regras` `/recrutar` `/eventos` `/membros`", inline=False)
    embed.add_field(name="RANK", value="`/rank` `/daily` `/coins` `/top`", inline=False)
    embed.add_field(name="STAFF", value="`/aviso` `/mutar` `/kick` `/ban` `/limpar` `/warn`", inline=False)
    embed.add_field(name="TICKET", value="`/ticket` `/fecharticket`", inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="serverinfo", description="Informacoes do servidor")
async def serverinfo(interaction: discord.Interaction):
    await interaction.response.defer()
    guild = interaction.guild
    embed = discord.Embed(title=guild.name, color=0x3498db)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Membros", value=guild.member_count, inline=True)
    embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
    embed.add_field(name="Criado em", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="userinfo", description="Informacoes de um usuario")
async def userinfo(interaction: discord.Interaction, usuario: discord.Member = None):
    await interaction.response.defer()
    usuario = usuario or interaction.user
    uid = str(usuario.id)
    if uid not in db["users"]:
        db["users"][uid] = {"xp": 0, "level": 1, "coins": 0, "daily": 0}
    embed = discord.Embed(title=f"PERFIL {usuario.name}", color=usuario.color)
    embed.set_thumbnail(url=usuario.display_avatar.url)
    embed.add_field(name="Level", value=db["users"][uid]["level"], inline=True)
    embed.add_field(name="XP", value=db["users"][uid]["xp"], inline=True)
    embed.add_field(name="Coins", value=db["users"][uid]["coins"], inline=True)
    embed.add_field(name="Entrou em", value=usuario.joined_at.strftime("%d/%m/%Y"), inline=True)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="avatar", description="Mostra o avatar de um usuario")
async def avatar(interaction: discord.Interaction, usuario: discord.Member = None):
    await interaction.response.defer()
    usuario = usuario or interaction.user
    embed = discord.Embed(title=f"Avatar de {usuario.name}", color=0x3498db)
    embed.set_image(url=usuario.display_avatar.url)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="regras", description="Mostra as regras da guilda")
async def regras(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="CODIGO VORTEX ESP", description=f"Completo em <#{CANAL_REGRAS}>", color=0xFFD700)
    embed.add_field(name="1 - RESPEITO", value="Zero toxicidade", inline=False)
    embed.add_field(name="2 - COMPROMETIMENTO", value="Treinos obrigatorios. 3 faltas = KICK", inline=False)
    embed.add_field(name="3 - DISCIPLINA", value="Seguir call do lider", inline=False)
    embed.add_field(name="4 - EVOLUCAO", value="Treinar todo dia", inline=False)
    embed.add_field(name="5 - LEALDADE", value="Proibido guilda dupla", inline=False)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="recrutar", description="Informacoes de recrutamento")
async def recrutar(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="RECRUTAMENTO VORTEX ESP", color=0xff0000)
    embed.add_field(name="REQUISITOS", value="KD 2.0+ | HS 70%+ | 16+ | Mic", inline=False)
    embed.add_field(name="INSCRICAO", value=f"<#{CANAL_INSCRICAO}>", inline=False)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="eventos", description="Agenda de treinos")
async def eventos(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(title="AGENDA VORTEX ESP", description="**PRESENCA OBRIGATORIA**", color=0x9B59B6)
    embed.add_field(name="SEG - 21:00", value="Treino 4v4 Ranqueado", inline=False)
    embed.add_field(name="QUA - 20:00", value="CS Personalizada", inline=False)
    embed.add_field(name="SEX - 22:00", value="X1 Interno", inline=False)
    embed.add_field(name="DOM - 19:00", value="Reuniao Geral", inline=False)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="membros", description="Lista membros online")
async def membros(interaction: discord.Interaction):
    await interaction.response.defer()
    online = [m.display_name for m in interaction.guild.members if m.status == discord.Status.online and not m.bot]
    embed = discord.Embed(title="STATUS VORTEX ESP", color=0x3498db)
    embed.add_field(name=f"ONLINE ({len(online)})", value="\n".join(online[:15]) or "Ninguem online", inline=False)
    embed.set_footer(text=f"Total de membros: {interaction.guild.member_count}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="rank", description="Mostra seu rank")
async def rank(interaction: discord.Interaction, usuario: discord.Member = None):
    await interaction.response.defer()
    usuario = usuario or interaction.user
    uid = str(usuario.id)
    if uid not in db["users"]:
        db["users"][uid] = {"xp": 0, "level": 1, "coins": 0, "daily": 0}
    level = db["users"][uid]["level"]
    xp = db["users"][uid]["xp"]
    coins = db["users"][uid]["coins"]
    embed = discord.Embed(title=f"RANK {usuario.name}", color=0xFFD700)
    embed.set_thumbnail(url=usuario.display_avatar.url)
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="XP", value=f"{xp}/{level * 100}", inline=True)
    embed.add_field(name="Coins", value=coins, inline=True)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="daily", description="Resgata coins diarios")
async def daily(interaction: discord.Interaction):
    await interaction.response.defer()
    uid = str(interaction.user.id)
    if uid not in db["users"]:
        db["users"][uid] = {"xp": 0, "level": 1, "coins": 0, "daily": 0}
    agora = datetime.now().timestamp()
    if agora - db["users"][uid].get("daily", 0) < 86400:
        tempo = 86400 - (agora - db["users"][uid]["daily"])
        await interaction.followup.send(f"Volte em {int(tempo // 3600)}h {int(tempo % 3600 // 60)}m", ephemeral=True)
        return
    recompensa = random.randint(100, 500)
    db["users"][uid]["coins"] += recompensa
    db["users"][uid]["daily"] = agora
    save_db(db)
    embed = discord.Embed(title="DAILY RESGATADO!", description=f"+{recompensa} coins! Saldo atual: {db['users'][uid]['coins']}", color=0x00ff00)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="coins", description="Ve quantas coins voce tem")
async def coins(interaction: discord.Interaction, usuario: discord.Member = None):
    await interaction.response.defer()
    usuario = usuario or interaction.user
    uid = str(usuario.id)
    if uid not in db["users"]:
        db["users"][uid] = {"xp": 0, "level": 1, "coins": 0, "daily": 0}
    await interaction.followup.send(f"{usuario.mention} tem {db['users'][uid]['coins']} coins")

@bot.tree.command(name="top", description="Top 10 membros por level")
async def top(interaction: discord.Interaction):
    await interaction.response.defer()
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
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="ticket", description="Abre um ticket de suporte")
async def ticket(interaction: discord.Interaction, motivo: str):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    try:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        staff_role = guild.get_role(CARGO_STAFF)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        canal = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)
        embed = discord.Embed(title="TICKET ABERTO", description=f"Ola {interaction.user.mention}!", color=0x00ff00)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        embed.add_field(name="Staff", value="Um membro da staff vai te atender em breve", inline=False)
        await canal.send(embed=embed)
        await interaction.followup.send(f"Ticket criado em {canal.mention}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Erro ao criar ticket: {e}", ephemeral=True)

@bot.tree.command(name="fecharticket", description="Fecha o ticket atual")
async def fecharticket(interaction: discord.Interaction):
    if "ticket-" not in interaction.channel.name:
        await interaction.response.send_message("Este comando so funciona em tickets", ephemeral=True)
        return
    await interaction.response.send_message("Fechando ticket em 5 segundos...")
    await asyncio.sleep(5)
    await interaction.channel.delete()

@bot.tree.command(name="aviso", description="Envia um comunicado para todos")
async def aviso(interaction: discord.Interaction, mensagem: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Apenas administradores podem usar este comando", ephemeral=True)
        return
    await interaction.response.defer()
    embed = discord.Embed(title="COMUNICADO VORTEX ESP", description=mensagem, color=0xe74c3c)
    embed.set_footer(text=f"Por {interaction.user.display_name}")
    embed.timestamp = datetime.now()
    await interaction.followup.send(content="@everyone", embed=embed)

@bot.tree.command(name="mutar", description="Muta um membro")
async def mutar(interaction: discord.Interaction, usuario: discord.Member, tempo: int, motivo: str):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("Voce nao tem permissao para mutar membros", ephemeral=True)
        return
    await interaction.response.defer()
    await usuario.timeout(timedelta(minutes=tempo), reason=motivo)
    embed = discord.Embed(title="MEMBRO MUTADO", color=0xff0000)
    embed.add_field(name="Usuario", value=usuario.mention, inline=True)
    embed.add_field(name="Tempo", value=f"{tempo} minutos", inline=True)
    embed.add_field(name="Motivo", value=motivo, inline=False)
    embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
    await interaction.followup.send(embed=embed)

# TEM QUE SER A ÚLTIMA LINHA
bot.run(TOKEN)
