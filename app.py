import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
from discord.commands import default_permissions

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
INVITES_FILE = os.getenv("INVITES_FILE", "invites.json")

intents = discord.Intents.default()
intents.members = True
intents.invites = True

bot = commands.Bot(command_prefix="!", intents=intents)


def load_invites():
    try:
        with open(INVITES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_invites(data):
    with open(INVITES_FILE, "w") as f:
        json.dump(data, f, indent=4)


invite_tracker = load_invites()


@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user}")
    await bot.sync_commands()

    for guild in bot.guilds:
        # Initialize guild if not exists while preserving existing data
        if str(guild.id) not in invite_tracker:
            invite_tracker[str(guild.id)] = {}

        current_invites = await guild.invites()

        # Update only invite uses count and creator, preserve other data
        for invite in current_invites:
            if invite.code not in invite_tracker[str(guild.id)]:
                # New invite found, initialize it
                invite_tracker[str(guild.id)][invite.code] = {
                    "uses": invite.uses,
                    "creator": invite.inviter.id if invite.inviter else None,
                    "invited_users": [],
                }
            else:
                # Update only the uses count, preserve invited_users
                existing_data = invite_tracker[str(guild.id)][invite.code]
                existing_data["uses"] = invite.uses
                # Update creator only if it was None
                if existing_data.get("creator") is None:
                    existing_data["creator"] = (
                        invite.inviter.id if invite.inviter else None
                    )
                # Ensure invited_users list exists
                if "invited_users" not in existing_data:
                    existing_data["invited_users"] = []

        # Remove invites that no longer exist while preserving data structure
        stored_codes = set(invite_tracker[str(guild.id)].keys())
        current_codes = {invite.code for invite in current_invites}
        for removed_code in stored_codes - current_codes:
            # Only remove if it has no invited users
            if not invite_tracker[str(guild.id)][removed_code].get("invited_users"):
                del invite_tracker[str(guild.id)][removed_code]

        save_invites(invite_tracker)


@bot.slash_command(
    name="createinvite",
    description="Create an invite link for a user",
    default_permissions=discord.Permissions(
        create_instant_invite=True, manage_guild=True
    ),
)
async def create_invite(ctx, user: discord.Member, channel: discord.TextChannel = None):
    target_channel = channel or ctx.channel

    try:
        invite = await target_channel.create_invite(
            max_age=0, max_uses=0, reason=f"Tracked invite for {user.name}"
        )

        if str(ctx.guild.id) not in invite_tracker:
            invite_tracker[str(ctx.guild.id)] = {}

        invite_tracker[str(ctx.guild.id)][invite.code] = {
            "uses": 0,
            "creator": user.id,
        }
        save_invites(invite_tracker)

        embed = discord.Embed(
            title="🎫 New Invite Created", color=discord.Color.green()
        )
        embed.add_field(name="Created For", value=user.mention, inline=True)
        embed.add_field(name="Channel", value=target_channel.mention, inline=True)
        embed.add_field(name="Invite Link", value=invite.url, inline=False)
        embed.set_footer(
            text=f"Created by {ctx.author.name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
        )

        await ctx.respond(embed=embed)

    except discord.Forbidden:
        error_embed = discord.Embed(
            title="❌ Error",
            description="I don't have permission to create invites in that channel.",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=error_embed, ephemeral=True)


@bot.slash_command(
    name="invites",
    description="Show invite statistics for a user",
    default_member_permissions=discord.Permissions(manage_guild=True),
)
async def invites(ctx, user: discord.Member = None):
    member = user or ctx.author

    total_invites = 0
    guild_invites = invite_tracker.get(str(ctx.guild.id), {})
    active_invites = []

    for invite_code, invite_data in guild_invites.items():
        if invite_data["creator"] == member.id:
            total_invites += invite_data["uses"]
            try:
                invite = await discord.utils.get(
                    await ctx.guild.invites(), code=invite_code
                )
                if invite:
                    active_invites.append(
                        f"discord.gg/{invite_code} ({invite_data['uses']} uses)"
                    )
            except:
                continue

    embed = discord.Embed(title="📊 Invite Statistics", color=discord.Color.blue())

    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="Total Invites", value=str(total_invites), inline=True)

    if active_invites:
        embed.add_field(
            name="Active Invite Links",
            value="\n".join(active_invites[:5])
            + ("\n..." if len(active_invites) > 5 else ""),
            inline=False,
        )

    embed.set_thumbnail(
        url=member.avatar.url if member.avatar else member.default_avatar.url
    )
    embed.set_footer(
        text=f"Requested by {ctx.author.name}",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
    )

    await ctx.respond(embed=embed)


@bot.event
async def on_member_join(member):
    guild = member.guild
    current_invites = await guild.invites()

    for invite in current_invites:
        stored_invite = invite_tracker[str(guild.id)].get(invite.code)
        if stored_invite and invite.uses > stored_invite["uses"]:
            invite_tracker[str(guild.id)][invite.code]["uses"] = invite.uses

            if "invited_users" not in invite_tracker[str(guild.id)][invite.code]:
                invite_tracker[str(guild.id)][invite.code]["invited_users"] = []

            invite_tracker[str(guild.id)][invite.code]["invited_users"].append(
                {
                    "id": member.id,
                    "name": member.name,
                    "joined_at": (
                        member.joined_at.isoformat() if member.joined_at else None
                    ),
                }
            )

            save_invites(invite_tracker)

            # # Welcome message code commented out
            # try:
            #     inviter = guild.get_member(stored_invite["creator"])
            #     welcome_embed = discord.Embed(
            #         title="👋 Welcome!",
            #         description=f"Welcome {member.mention} to the server!",
            #         color=discord.Color.green()
            #     )
            #     welcome_embed.add_field(
            #         name="Invited By",
            #         value=inviter.mention if inviter else "Unknown",
            #         inline=True
            #     )
            #     welcome_embed.set_thumbnail(
            #         url=member.avatar.url if member.avatar else member.default_avatar.url
            #     )

            #     # Try to find system channel or first text channel
            #     channel = guild.system_channel or next(
            #         (channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages),
            #         None
            #     )
            #     if channel:
            #         await channel.send(embed=welcome_embed)
            # except:
            #     pass
            break


@bot.slash_command(
    name="detailed-invites",
    description="Show detailed invite statistics including invited users",
    default_member_permissions=discord.Permissions(manage_guild=True),
)
async def detailed_invites(ctx, user: discord.Member = None, show_all: bool = False):
    member = user or ctx.author
    guild_invites = invite_tracker.get(str(ctx.guild.id), {})

    total_invites = 0
    invited_users = []
    active_links = []

    for invite_code, invite_data in guild_invites.items():
        if invite_data["creator"] == member.id:
            total_invites += invite_data["uses"]
            if "invited_users" in invite_data:
                invited_users.extend(invite_data["invited_users"])
            try:
                invite = await discord.utils.get(
                    await ctx.guild.invites(), code=invite_code
                )
                if invite:
                    active_links.append(
                        f"discord.gg/{invite_code} ({invite_data['uses']} uses)"
                    )
            except:
                continue

    embed = discord.Embed(
        title="📊 Detailed Invite Statistics", color=discord.Color.blue()
    )

    embed.add_field(name="Inviter", value=member.mention, inline=True)
    embed.add_field(name="Total Invites", value=str(total_invites), inline=True)

    if active_links:
        embed.add_field(
            name="Active Invite Links",
            value="\n".join(active_links[:5])
            + ("\n..." if len(active_links) > 5 else ""),
            inline=False,
        )

    if invited_users:
        invited_users.sort(key=lambda x: x["joined_at"], reverse=True)

        display_users = invited_users if show_all else invited_users[:10]

        users_list = []
        for user in display_users:
            member_obj = ctx.guild.get_member(user["id"])
            if member_obj:
                joined_date = discord.utils.format_dt(
                    discord.utils.parse_time(user["joined_at"]), style="R"
                )
                users_list.append(f"{member_obj.mention} (joined {joined_date})")

        if users_list:
            embed.add_field(
                name=f"Invited Users ({len(invited_users)} total)",
                value="\n".join(users_list)
                + ("\n..." if not show_all and len(invited_users) > 10 else ""),
                inline=False,
            )

    embed.set_thumbnail(
        url=member.avatar.url if member.avatar else member.default_avatar.url
    )
    embed.set_footer(
        text=f"Requested by {ctx.author.name}",
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
    )

    await ctx.respond(embed=embed)


if __name__ == "__main__":
    bot.run(TOKEN)
