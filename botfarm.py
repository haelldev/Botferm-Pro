# botfarm.py
import os
import mysql.connector
from discord.ext import commands

# -------------------------
# Conexão com o banco de dados
# -------------------------

host = os.getenv("MYSQLHOST")
if not host:
    raise ValueError("MYSQLHOST não configurado. Defina a variável de ambiente.")

conexao = mysql.connector.connect(
    host=host,
    user=os.getenv("MYSQLUSER"),
    password=os.getenv("MYSQLPASSWORD"),
    database=os.getenv("MYSQL_DATABASE"),
    port=int(os.getenv("MYSQLPORT", 3306))
)
print("Conexão MySQL bem-sucedida!")


cursor = conn.cursor()

# -------------------------
# Configuração do bot
# -------------------------
bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

# -------------------------
# Comandos do bot
# -------------------------

# Adicionar item
@bot.command()
async def add_item(ctx, item: str, quantity: int):
    cursor.execute(
        "INSERT INTO farm_data (user_id, item, quantity) VALUES (%s, %s, %s) "
        "ON DUPLICATE KEY UPDATE quantity = quantity + %s",
        (ctx.author.id, item, quantity, quantity)
    )
    conn.commit()
    await ctx.send(f"{quantity}x {item} adicionados ao seu inventário!")

# Remover item
@bot.command()
async def remove_item(ctx, item: str, quantity: int):
    cursor.execute(
        "SELECT quantity FROM farm_data WHERE user_id=%s AND item=%s",
        (ctx.author.id, item)
    )
    row = cursor.fetchone()
    if not row:
        await ctx.send("Você não tem esse item.")
        return
    new_quantity = row[0] - quantity
    if new_quantity <= 0:
        cursor.execute(
            "DELETE FROM farm_data WHERE user_id=%s AND item=%s",
            (ctx.author.id, item)
        )
    else:
        cursor.execute(
            "UPDATE farm_data SET quantity=%s WHERE user_id=%s AND item=%s",
            (new_quantity, ctx.author.id, item)
        )
    conn.commit()
    await ctx.send(f"{quantity}x {item} removidos do seu inventário!")

# Listar itens
@bot.command()
async def list_items(ctx):
    cursor.execute(
        "SELECT item, quantity FROM farm_data WHERE user_id=%s",
        (ctx.author.id,)
    )
    rows = cursor.fetchall()
    if not rows:
        await ctx.send("Você não tem itens no inventário.")
    else:
        message = "Seus itens:\n"
        for item, quantity in rows:
            message += f"- {item}: {quantity}\n"
        await ctx.send(message)

# Editar quantidade de um item
@bot.command()
async def edit_item(ctx, item: str, quantity: int):
    cursor.execute(
        "SELECT quantity FROM farm_data WHERE user_id=%s AND item=%s",
        (ctx.author.id, item)
    )
    row = cursor.fetchone()
    if not row:
        await ctx.send("Você não tem esse item.")
        return
    cursor.execute(
        "UPDATE farm_data SET quantity=%s WHERE user_id=%s AND item=%s",
        (quantity, ctx.author.id, item)
    )
    conn.commit()
    await ctx.send(f"Quantidade de {item} alterada para {quantity}.")

# Total de itens
@bot.command()
async def total_items(ctx):
    cursor.execute(
        "SELECT SUM(quantity) FROM farm_data WHERE user_id=%s",
        (ctx.author.id,)
    )
    total = cursor.fetchone()[0]
    total = total if total else 0
    await ctx.send(f"Você tem um total de {total} itens no inventário.")

# -------------------------
# Rodando o bot
# -------------------------
bot.run(os.getenv("TOKEN"))
