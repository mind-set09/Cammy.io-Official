import disnake
from disnake.ext import commands
from disnake.ext.commands import Context, Option
import random
import aiohttp

intents = disnake.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.slash_command(name="start", description="Begin your Pokémon adventure!")
async def start(ctx: Context):
    try:
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        # Initial embed: Name prompt
        name_prompt = disnake.Embed(title="Welcome to the Pokémon RPG!", description="Hi there! What's your name?", color=0x3498db)
        await ctx.send(embed=name_prompt)

        user_response = await bot.wait_for("message", check=check, timeout=60)
        user_name = user_response.content

        # Starter Pokemon selection
        starter_options = [
            disnake.OptionChoice(name="Bulbasaur", value="bulbasaur"),
            disnake.OptionChoice(name="Charmander", value="charmander"),
            disnake.OptionChoice(name="Squirtle", value="squirtle")
        ]
        starter_selection = disnake.Embed(title=f"Nice to meet you, {user_name}!", description="Let's choose your starter Pokémon.", color=0x27ae60)
        starter_selection.set_footer(text="Choose wisely!")
        await ctx.send(embed=starter_selection, options=[Option(name="starter", description="Select your starter Pokémon:", type=disnake.OptionType.STRING, choices=starter_options)])

        # Wait for the user's choice
        interaction = await bot.wait_for("slash_command", check=lambda i: i.interaction.user == ctx.author)
        chosen_starter = interaction.data["options"][0]["value"]

        # Fetch starter Pokémon details from PokeAPI
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pokeapi.co/api/v2/pokemon/{chosen_starter}/') as response:
                data = await response.json()

                name = data['name']
                types = [t['type']['name'] for t in data['types']]
                base_stats = [f"{stat['stat']['name']}: {stat['base_stat']}" for stat in data['stats']]

                # Starter Pokemon details embed
                starter_embed = disnake.Embed(title=f"Your starter Pokémon is {name}!", color=0x00ff00)
                starter_embed.add_field(name="Types", value=', '.join(types), inline=False)
                starter_embed.add_field(name="Base Stats", value='\n'.join(base_stats), inline=False)
                starter_embed.set_thumbnail(url=data['sprites']['front_default'])

                await ctx.send(embed=starter_embed)

    except asyncio.TimeoutError:
        await ctx.send("Sorry, you took too long to respond.")

bot.run(os.environ['TOKEN'])
