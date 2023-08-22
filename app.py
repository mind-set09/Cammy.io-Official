import os
import disnake
import requests
from disnake.ext import commands
from disnake.ui import Button, View

# Database models
from .models import Trainer, Pokemon

bot = commands.Bot(command_prefix='/')

@bot.slash_command()
async def start(ctx):

    # Display starter select screen
    await select_starter(ctx)
    
    # Wait for starter selection 
    starter_pokemon = await get_starter_selection(ctx)
    
    # Create trainer
    trainer = Trainer(id=ctx.author.id, name=ctx.author.name, starter=starter_pokemon)
    
    # Save trainer to DB
    await trainer.save()
    
    # Display confirmation message
    await display_confirmation(ctx, trainer)

async def select_starter(ctx):

    # Create view with starter buttons
    view = View()
    for pokemon in ['Bulbasaur', 'Charmander', 'Squirtle']:
        button = Button(label=pokemon)
        view.add_item(button)

    # Display starter selection embed    
    embed = disnake.Embed(title='Pick a Starter', color=0x00FF00)
    await ctx.respond(embed=embed, view=view)

async def get_starter_selection(ctx):
    
    # Wait for button click
    button_ctx = await bot.wait_for('button_click')

    # Fetch Pokemon data from PokeAPI v2
    pokemon_name = button_ctx.component[0].label.lower()
    pokemon_info = fetch_pokemon_info(pokemon_name)

    # Create Pokemon object
    pokemon = Pokemon(name=pokemon_info['name'], description=pokemon_info['description'], sprite_url=pokemon_info['sprite_url'])

    return pokemon

async def display_confirmation(ctx, trainer):

    # Create embed
    embed = disnake.Embed(title='You chose:', color=0x00FF00)
    embed.add_field(name=trainer.starter.name, value=trainer.starter.description)
    embed.set_thumbnail(url=trainer.starter.sprite_url) 

    await ctx.send(embed=embed)

def fetch_pokemon_info(pokemon_name):
    api_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
    response = requests.get(api_url)
    data = response.json()

    # Extract relevant information
    description = "No description available."
    if data['species']['url']:
        species_info = requests.get(data['species']['url']).json()
        for entry in species_info['flavor_text_entries']:
            if entry['language']['name'] == 'en':
                description = entry['flavor_text']
                break

    sprite_url = data['sprites']['front_default']

    return {'name': pokemon_name.capitalize(), 'description': description, 'sprite_url': sprite_url}

bot.run(os.environ['TOKEN'])
