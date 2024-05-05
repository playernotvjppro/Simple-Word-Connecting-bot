import discord
from discord.ext import commands
from discord import app_commands
import re


bot = commands.Bot(command_prefix='??', intents=discord.Intents.all())


#Define

current_word = ''
last_word_id = ""
admin_role_name = "ADMINISTRATOR"
used_words = []


def load_words(filename):
    with open(filename, 'r') as file:
        words = [line.strip().lower() for line in file]
    return words

def save_channel_id(channel_id, filename):
    with open(filename, 'w') as file:
        file.write(str(channel_id))


def load_channel_id(filename):
    with open(filename, 'r') as file:
        channel_id = int(file.readline().strip())
    return channel_id

def remove_channel_id(channel_id, filename):
    with open(filename, 'r') as file:
        channel_ids = [line.strip() for line in file if line.strip() != str(channel_id)]

    with open(filename, 'w') as file:
        file.write('\n'.join(channel_ids))
        
def save_used_words(used_word, filename):
    with open(filename, 'w') as file:
        for word in used_word:
            file.write(word + '\n')

def load_used_words(filename):
    loaded_words = []
    with open(filename, 'r') as file:
        for line in file:
            loaded_words.append(line.strip())
    return loaded_words
def clear_used_words(filename):
    with open(filename, 'w') as file:
        file.write('')
        
def save_last_id(last_id,filename):
    with open(filename,"w") as file:
        file.write(str(last_id))

def load_last_id(filename):
    lastid = ""
    with open(filename,"r") as file:
        for line in file:
            lastid = int(line.strip())
    return lastid
def clear_last_id(filename):
    with open(filename, 'w') as file:
        file.write('')
        
def save_connect(connect,filename):
    with open(filename,"w") as file:
        file.write(str(connect))

def load_connect(filename):
    connect = ""
    with open(filename,"r") as file:
        for line in file:
            connect = line.strip()
    return connect

english_words = load_words('words.txt')
word_channel_filename = 'word_channel_id.txt'
used_words_filename = "used words.txt"
word_channel_id = load_channel_id(word_channel_filename)
last_word_id_filename = "last word id.txt"
used_words = load_used_words(used_words_filename)
last_word_id = load_last_id(last_word_id_filename)
connect_filename = "toggle connect.txt"
connectable = load_connect(connect_filename)

#procedure

@bot.command()
async def set_channel(ctx):
    global word_channel_id
    if ctx.author.guild_permissions.administrator:
        word_channel_id = ctx.channel.id
        save_channel_id(word_channel_id, word_channel_filename)
        await ctx.send(f"This channel is now set as the word connect channel.")
    else:
        await ctx.send("You need to be an administrator to set the word connect channel.")


@bot.command()
async def reset_game(ctx):
    global current_word
    global used_words
    global last_word_id
    global connectable

    if ctx.author.guild_permissions.administrator:
        current_word = ''
        used_words = []
        clear_used_words(used_words_filename)
        last_word_id = ""
        clear_last_id(last_word_id_filename)
        connectable = False
        save_connect(connectable,connect_filename)
        await ctx.send("Game has been reset.")
    else:
        await ctx.send("You need to be an administrator to reset the game.")
        
@bot.command()
async def remove_channel(ctx):
    global word_channel_filename
    
    if ctx.author.guild_permissions.administrator:
        remove_channel_id(ctx.channel.id,word_channel_filename)
        await ctx.send("This word connect channel has been removed!")
    else:
        await ctx.send("You need to be an administrator to reset the channel!")
        
@bot.command()
async def toggle_connect(ctx):
    global connectable
    
    if ctx.author.guild_permissions.administrator:
        if str(connectable) == "False":
            connectable = True
            save_connect(connectable,connect_filename)
            await ctx.send("Player can connect twice or more times in a row now!")
        elif str(connectable) == "True":
            connectable = False
            save_connect(connectable,connect_filename)
            await ctx.send("Player can't connect twice or more times in a row now!")
    else:
        await ctx.send("You need to be an administrator to toggle connect!")
        
#Main gameplay        

@bot.event
async def on_message(message):
    global current_word
    global used_words
    global last_word_id

    if message.author == bot.user:
        return

    if current_word == '' and message.channel.id == word_channel_id and len(used_words) == 0:
        word = message.content.lower().strip()
        
        if re.match("^[a-zA-Z]+$", word):
            
            if word in english_words:
                current_word = word
                used_words.append(word)
                await message.channel.send(f"Word connecting game started with the word: `{current_word}`")
                await message.add_reaction('✅')
                save_used_words(used_words,used_words_filename)
                last_word_id = message.author.id
                save_last_id(last_word_id,last_word_id_filename)
            else:
                await message.add_reaction('❌')
                await message.channel.send(f"The word `{word}` is not in the dictionary.")
    elif message.channel.id == word_channel_id:
        word = message.content.lower().strip()
        current_word = used_words[-1]
        
        if re.match("^[a-zA-Z]+$", word):
            
            if last_word_id == message.author.id and not connectable:
                await message.add_reaction('❌')
                await message.channel.send("You have just connected word!")
            
            elif word in english_words:
                
                if word.startswith(current_word[-1]) and word not in used_words:
                    
                    if word not in used_words:
                        used_words.append(word)
                        save_used_words(used_words,used_words_filename)
                        last_word_id = message.author.id
                        save_last_id(last_word_id,last_word_id_filename)
                        await message.add_reaction('✅')
                        current_word = word
                elif word in used_words:
                    await message.add_reaction('❌')
                    await message.channel.send(f"The word `{word}` has been used!")
                else:
                    await message.add_reaction('❌')
                    await message.channel.send(f"The word `{word}` doesn't connect with `{current_word[-1]}`!")
            else:
                await message.add_reaction('❌')
                await message.channel.send(f"The word `{word}` is not in the dictionary!")
        else:
            pass

    await bot.process_commands(message)

#Slash Command

@bot.event
async def on_ready():
    print("This bot is usable now")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    
@bot.tree.command(name="help",description="Cảm thấy khó dùng...?")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message("Ko bé oi")

@bot.tree.command(name="say",description="say something...")
@app_commands.describe(thing_to_say = "lmao")
async def say(interaciton: discord.Interaction, thing_to_say: str):
    await interaciton.response.send_message(f"{thing_to_say}")

@bot.tree.command(name="set_channel", description="Đặt channel nối từ")
async def set_channel(interaction: discord.Interaction):
    global word_channel_id
    if interaction.user.guild_permissions.administrator:
        word_channel_id = interaction.channel_id
        save_channel_id(word_channel_id, word_channel_filename)
        await interaction.response.send_message(content="This channel is now set as the word connect channel.")
    else:
        await interaction.response.send_message(content="You need to be an administrator to set the word connect channel.", ephemeral=True)
        
@bot.tree.command(name="reset_game",description="Reset các từ đã nối")
async def reset_game(interaction:discord.Interaction):
    global current_word
    global used_words
    global last_word_id
    global connectable

    if interaction.user.guild_permissions.administrator:
        current_word = ''
        used_words = []
        clear_used_words(used_words_filename)
        last_word_id = ""
        clear_last_id(last_word_id_filename)
        connectable = False
        save_connect(connectable,connect_filename)
        await interaction.response.send_message("Game has been reset.")
    else:
        await interaction.response.send_message("You need to be an administrator to reset the game.",ephemeral=True)
        
@bot.tree.command(name="remove_channel",description="Reset channel nối từ")
async def remove_channel(interaction:discord.Interaction):
    global word_channel_filename
    
    if interaction.user.guild_permissions.administrator:
        remove_channel_id(interaction.channel.id,word_channel_filename)
        await interaction.response.send_message("This word connect channel has been removed!")
    else:
        await interaction.response.send_message("You need to be an administrator to reset the channel!",ephemeral=True)

@bot.tree.command(name="toggle_connect",description="Bật hoặc tắt nối từ liên tiếp")
async def toggle_connect(interaction:discord.Interaction):
    global connectable
    
    if interaction.user.guild_permissions.administrator:
        if str(connectable) == "False":
            connectable = True
            save_connect(connectable,connect_filename)
            await interaction.response.send_message("Player can connect twice or more times in a row now!")
        elif str(connectable) == "True":
            connectable = False
            save_connect(connectable,connect_filename)
            await interaction.response.send_message("Player can't connect twice or more times in a row now!")
    else:
        await interaction.response.send_message("You need to be an administrator to toggle connect!")
        


#Run

bot.run('Your bot token')
