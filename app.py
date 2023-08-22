import os
import disnake
from disnake.ext import commands
from disnake.ui import Button, View
from pokedex import pokedex

# Database models
from models import Trainer, Pokemon

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

    # Lookup pokemon
    pokemon = Pokemon.get(name=button_ctx.component[0].label)

    return pokemon

async def display_confirmation(ctx, trainer):

    # Lookup pokemon info
    pokemon = pokedex[trainer.starter.name]
    
    # Create embed        
    embed = disnake.Embed(title='You chose:', color=0x00FF00)
    embed.add_field(name=trainer.starter.name, value=pokemon['description'])
    embed.set_thumbnail(url=pokemon['sprite_url']) 

    await ctx.send(embed=embed)
    
bot.run(os.environ['TOKEN'])
