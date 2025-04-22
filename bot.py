import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # untuk mendapatkan info member, termasuk DM

bot = commands.Bot(command_prefix='!', intents=intents)

# Ganti dengan daftar ID role yang diizinkan
ALLOWED_ROLE_IDS = ["460202943178866698", "460202416336535573", "1348354692782100612"]

# Ganti dengan ID role admin yang ingin disebutkan
ADMIN_ROLE_ID = 1356871379005341746

# Ganti dengan ID channel admin
ADMIN_CHANNEL_ID = 1355979573686173696

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} berhasil online!')
    # Set status Competing
    activity = discord.Activity(type=discord.ActivityType.competing, name="🔴24/7 Live | #DifferentLevel🤪 #TDCO")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        admin_role = discord.utils.get(message.guild.roles, id=ADMIN_ROLE_ID)
        admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)

        message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"

        embed = discord.Embed(
            title="📌 Notifikasi Bot Disebut",
            description=f"**{message.author.mention}** menyebut bot di {message.channel.mention}",
            color=discord.Color.orange()
        )
        embed.add_field(name="Isi Pesan", value=message.content, inline=False)
        embed.add_field(name="🔗 Link Pesan", value=f"[Klik di sini untuk lihat pesan]({message_link})", inline=False)
        embed.set_footer(text=f"Server: {message.guild.name}")

        if admin_channel:
            if admin_role:
                await admin_channel.send(f"{admin_role.mention}", embed=embed)
            else:
                await admin_channel.send(embed=embed)

        for member in message.guild.members:
            if admin_role in member.roles:
                try:
                    await member.send(embed=embed)
                except discord.Forbidden:
                    print(f"Gagal kirim DM ke {member.name} karena privasi.")
                except discord.HTTPException as e:
                    print(f"Gagal kirim DM ke {member.name}: {e}")

    await bot.process_commands(message)

@bot.command()
async def say(ctx, channel: discord.TextChannel, *, message):
    member = ctx.author
    allowed_roles = [role.id for role in member.roles if role.id in map(int, ALLOWED_ROLE_IDS)]
    
    if allowed_roles:
        await channel.send(content=message, allowed_mentions=discord.AllowedMentions(everyone=True))
        await ctx.send(f"✅ Pesan sudah dikirim ke {channel.mention}")
    else:
        await ctx.send("❌ Anda tidak memiliki izin untuk menggunakan command ini.")

@bot.command()
async def join(ctx):
    """Perintah untuk bot bergabung dengan channel voice tempat pengguna berada dan mute mic-nya"""
    # Cek apakah pengguna berada di channel voice
    if ctx.author.voice:
        channel = ctx.author.voice.channel  # Dapatkan channel voice yang sedang ditempati oleh pengguna
        if ctx.voice_client:
            return await ctx.voice_client.move_to(channel)  # Jika bot sudah ada di voice channel yang lain, pindahkan ke channel yang sama
        
        # Bergabung ke voice channel dan mute bot
        voice_client = await channel.connect()
        await voice_client.edit(mute=True)  # Mematikan mikrofon bot
        
        await ctx.send(f'✅ Bot telah bergabung dengan channel {channel.name} dan mute mic-nya.')
    else:
        await ctx.send("❌ Anda harus berada di channel voice terlebih dahulu untuk menggunakan perintah ini.")

@bot.command()
async def leave(ctx):
    """Perintah untuk bot meninggalkan channel voice"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('✅ Bot telah meninggalkan channel voice.')
    else:
        await ctx.send('❌ Bot tidak berada di channel voice.')

bot.run(TOKEN)
