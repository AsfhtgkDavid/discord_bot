import MySQLdb
import discord
from discord.ext import commands, tasks
from discord.utils import get
import os

async def mute(channel, member:discord.Member, time_min:int, reason:str):
    conn = MySQLdb.connect('sql4.freemysqlhosting.net', 'sql4409115', 'UamctGqrPZ', 'sql4409115')
    role = member.guild.get_role(610742364797141002)
    emb = discord.Embed(description=f'Я выдал тебе мут {member.mention} за **"{reason}"**')
    conn.autocommit(on=True)
    cursor = conn.cursor()
    await member.add_roles(role, reason=reason)
    cursor.execute(f'INSERT INTO mutes VALUES({member.id},{time_min})')
    await channel.send(embed= emb)


async def warn(user:discord.Member, channel):
    conn = MySQLdb.connect('sql4.freemysqlhosting.net', 'sql4409115', 'UamctGqrPZ', 'sql4409115')
    conn.autocommit(on=True)
    cursor = conn.cursor()
    cursor.execute(f'SELECT count FROM warns WHERE user = {user.id}')
    db = cursor.fetchall()
    if db == ():
        cursor.execute(f'INSERT INTO warns(user, count) VALUES ({user.id},{1})')
    elif db[0][0] == 3:
        cursor.execute(f'UPDATE warns SET count = 0 WHERE user = {user.id}')
        await mute(channel, user, 4, "Получил 3 варна!")
    else:
        cursor.execute(f'UPDATE warns SET count = count + 1 WHERE user = {user.id}')
    conn.close()



bot = commands.Bot(command_prefix='-', intents=discord.Intents.all())
@bot.event
async def on_message(ctx):

    author = ctx.author
    emb = discord.Embed(description=f'Я выдал тебе предупреждение <@!{author.id}> за **"Использование команд в не предназначеном месте"**')
    content = ctx.content
    if ctx.channel.category_id != 836615446538092585 and (content.startswith('!') or content.startswith('=')) and 554332699691712512 not in [role.id for role in author.roles]:
        await ctx.channel.send(embed = emb)
        await warn(author, ctx.channel)
    await bot.process_commands(ctx)
@bot.event
async def on_ready():
    print('i online')
    mute_check.start()

@tasks.loop(seconds=60.0)
async def mute_check():
    conn = MySQLdb.connect('sql4.freemysqlhosting.net', 'sql4409115', 'UamctGqrPZ', 'sql4409115')
    guild = bot.get_guild(554314886562185217)
    role = guild.get_role(610742364797141002)
    conn.autocommit(on=True)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mutes')
    for i in cursor.fetchall():
        print(i)
        user = guild.get_member(i[0])
        mute_min = i[1]
        if user:
            if mute_min <= 0:
                print(1)
                await user.remove_roles(role)
                cursor.execute(f'DELETE FROM mutes WHERE user = {user.id}')
            else:
                print(2)
                cursor.execute(f'UPDATE mutes SET time_min = time_min - 1 WHERE user = {user.id}')
    conn.close()


@bot.command()
async def ping(ctx):
    jh = ctx.message.author
    await ctx.send(f'pong! {jh.mention}')
@bot.command()
@commands.has_permissions(administrator = True)
async def say(ctx):

    o = True
    jh = ctx.message.content
    await ctx.channel.purge(limit=1)
    gh = ''
    for i in jh:
        gh += i
        if i == ' ' and o:
            gh = ''
            o = False
    await ctx.send(gh)
@bot.command()
async def dell(ctx):
    await ctx.channel.purge()
@bot.command()
async def connect(ctx):
    global voices
    chan = ctx.message.author.voice.channel
    voices = get(bot.voice_clients, guild = ctx.guild)
    if voices and voices.is_connected():
        await voices.move_to(chan)
    else:
        voices = await chan.connect()
@bot.command()
async def disconnect(ctx):
    global voices
    chan = ctx.message.author.voice.channel
    voices = get(bot.voice_clients, guild = ctx.guild)
    if voices and voices.is_connected():
        await voices.disconnect()
    else:
        voices = await chan.connect()
token = os.environ.get('token')
bot.run(token)