# bot_farm.py
import os
import discord
from discord.ext import commands
import mysql.connector

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv("TOKEN")  # Token do bot no Discord
PREFIX = "!"

# Conexão com o banco de dados
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT"))
)
cursor = db.cursor()

# Criar tabela caso não exista
cursor.execute("""
CREATE TABLE IF NOT EXISTS farm_data (
    user_id BIGINT NOT NULL,
    item VARCHAR(255) NOT NULL,
    quantidade INT DEFAULT 0,
    PRIMARY KEY(user_id, item)
)
""")
db.commit()

# Inicializando bot
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

# --- FUNÇÕES ---
def salvar_item(user_id, item, quantidade):
    """Adiciona ou atualiza quantidade de itens do usuário"""
    sql = """
    INSERT INTO farm_data (user_id, item, quantidade)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE quantidade = quantidade + %s
    """
    valores = (user_id, item, quantidade, quantidade)
    cursor.execute(sql, valores)
    db.commit()

def pegar_itens(user_id):
    """Retorna todos os itens do usuário"""
    cursor.execute("SELECT item, quantidade FROM farm_data WHERE user_id = %s", (user_id,))
    return cursor.fetchall()  # lista de tuplas (item, quantidade)

# --- COMANDOS ---
@bot.command()
async def coletar(ctx, item: str, quantidade: int):
    salvar_item(ctx.author.id, item, quantidade)
    await ctx.send(f"{ctx.author.name} coletou {quantidade}x {item}!")

@bot.command()
async def inventario(ctx):
    itens = pegar_itens(ctx.author.id)
    if itens:
        resposta = "\n".join([f"{item}: {qtd}" for item, qtd in itens])
    else:
        resposta = "Seu inventário está vazio!"
    await ctx.send(f"**Inventário de {ctx.author.name}:**\n{resposta}")

# --- EVENTOS ---
@bot.event
async def on_ready():
    print(f"{bot.user} está online!")

# --- RODAR BOT ---
bot.run(TOKEN)
