import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

PREFIX_FILE = "prefix.txt"

def get_prefix():
    if os.path.exists(PREFIX_FILE):
        with open(PREFIX_FILE, "r") as f:
            return f.read().strip()
    return "?"

def set_prefix(new_prefix):
    with open(PREFIX_FILE, "w") as f:
        f.write(new_prefix)

intents = discord.Intents.default()
intents.members = True

warns = {}

class ModerationBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} slash commands.")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

bot = ModerationBot()

@bot.hybrid_command(description="Warn a user")
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    guild_id = ctx.guild.id
    warns.setdefault(guild_id, {})
    warns[guild_id].setdefault(member.id, [])
    warns[guild_id][member.id].append(reason or "No reason provided.")
    await ctx.send(f"{member.mention} has been warned. Total warns: {len(warns[guild_id][member.id])}")

@bot.hybrid_command(description="Kick a user")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    try:
        await member.kick(reason=reason)
        await ctx.send(f'User {member} has been kicked.')
    except Exception as e:
        await ctx.send(f'Failed to kick {member}: {e}')

@bot.hybrid_command(description="Ban a user")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    try:
        await member.ban(reason=reason)
        await ctx.send(f'User {member} has been banned.')
    except Exception as e:
        await ctx.send(f'Failed to ban {member}: {e}')

@bot.hybrid_command(description="Mute a user")
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, duration: int = 10, *, reason=None):
    try:
        await member.edit(timeout=discord.utils.utcnow() + discord.timedelta(minutes=duration), reason=reason)
        await ctx.send(f'User {member} has been muted for {duration} minutes.')
    except Exception as e:
        await ctx.send(f'Failed to mute {member}: {e}')

@bot.tree.command(name="setprefix", description="Change the bot's prefix")
@app_commands.describe(prefix="The new prefix to use")
@commands.has_permissions(administrator=True)
async def setprefix(interaction: discord.Interaction, prefix: str):
    set_prefix(prefix)
    bot.command_prefix = get_prefix
    await interaction.response.send_message(f"Prefix changed to `{prefix}`. Please use the new prefix for commands.", ephemeral=True)

@warn.error
@kick.error
@ban.error
@mute.error
async def mod_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Couldn't find that user.")
    else:
        await ctx.send(f"An error occurred: {error}")

bot.run('MTQxNzkxNzMxMjI2MTk1MTQ5OA.GSi4AZ.ECRiD-yktIM-HRG49tiEjkjsPCfyHM8-4TMoac') 
