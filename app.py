import disnake
from disnake.ext import commands
from pokepy import V2Client
from pymongo import MongoClient

# Bot 
intents = disnake.Intents.default()
bot = commands.Bot(intents=intents)

# MongoDB
cluster = MongoClient("mongo_uri")
db = cluster["pokemon"]
trainers = db["trainers"]

# PokeAPI
poke_client = V2Client()

# Embed helpers
async def get_name_embed():
  embed = disnake.Embed(title="What is your name?")
  return embed

async def get_starter_embed(starters):
  embed = disnake.Embed(title="Choose a starter:")
  for starter in starters:
    embed.add_field(name=starter.name, value="\n".join(starter.types))
  return embed

async def get_confirm_embed(trainer, starter):
  embed = disnake.Embed(title="Let's go!")
  embed.set_thumbnail(url=starter.sprite_url)
  embed.add_field(name="Trainer", value=trainer.name)
  embed.add_field(name="Starter", value=starter.name)
  return embed

@bot.slash_command()
async def start(ctx):

  # Get name
  name_embed = await get_name_embed()
  await ctx.send(embed=name_embed)

  name_msg = await bot.wait_for('message')
  name = name_msg.content

  # Get starters
  starters = await fetch_starters()
  starter_embed = await get_starter_embed(starters)

  await ctx.send(embed=starter_embed)

  res = await bot.wait_for('click')
  starter_name = res.component.label
  
  # Initialize trainer
  for starter in starters:
    if starter.name == starter_name:
      break

  trainer = Trainer(id=ctx.author.id, name=name, starter=starter)

  # Confirmation
  confirm_embed = await get_confirm_embed(trainer, starter)
  await ctx.send(embed=confirm_embed)

  # Save trainer
  result = await save_trainer(trainer)
  if result.acknowledged:
    await ctx.send("Trainer saved!")
  else:
    await ctx.send("Error saving trainer!")

# Trainer model
class Trainer:
  def __init__(self, id, name, starter):
    self.id = id
    self.name = name
    self.starter = starter

# Pokemon model
class Pokemon:
  def __init__(self, name, types, sprite):
    self.name = name
    self.types = types
    self.sprite_url = sprite

# Get starter data  
async def fetch_starters():
  url = "https://pokeapi.co/api/v2/pokemon?limit=3"
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
      data = await resp.json()

  return [Pokemon(p['name'], p['types'], p['sprites']['front_default']) for p in data['results']]

# Save trainer
async def save_trainer(trainer):
  trainer_data = {
    "_id": trainer.id,
    "name": trainer.name, 
    "starter": trainer.starter
  }

  trainers.insert_one(trainer_data)
  return True

bot.run(os.getenv("TOKEN"))
