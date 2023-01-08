import os
import random
from time import sleep
import discord
import openai
from discord import app_commands
from googletrans import Translator
from threading import Thread
from spinhandlerselenium import spin_text
from pygrammalecte import grammalecte_text
from spinhandlerseleniumv2 import spin_text as spin_text_v2

##
from revChatGPT.ChatGPT import Chatbot
chatbot = Chatbot({
        "session_token": 	"eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..vuU2jvz-0ZftTUld.MP7EVq-KSbF9zk1bgnOCFNJLlx6zg"
    }, conversation_id=None, parent_id=None)

def get_error_message():
    error_messages = [
        "Nous avons rencontré une erreur inattendue lors de notre tentative de récupération de la réponse du chatbot.",
        "Notre chatbot nous a causé un problème lorsque nous avons essayé de récupérer sa réponse.",
        "Une erreur s'est glissée entre nous et la réponse de notre chatbot lors de notre tentative de récupération.",
        "Notre chatbot nous a donné du fil à retordre en nous refusant sa réponse lors de notre tentative de récupération.",
        "Nous avons été confrontés à une erreur déroutante lorsque nous avons essayé de récupérer une réponse de notre chatbot."
    ]
    return random.choice(error_messages)


def chatbot_response(input_text, session_id):
    try:
        response = chatbot.ask(input_text, conversation_id=None, parent_id=None) 
        return response["message"], response["conversation_id"]
    except:
        return get_error_message(), "404"

# {
#   "message": message,
#   "conversation_id": self.conversation_id,
#   "parent_id": self.parent_id,
# }







# SCOPE = https://discord.com/api/oauth2/authorize?client_id=1060269212301533394&permissions=11328&scope=bot

guildid = 639822603728453632

images_path = "/home/goupil/Documents/DiscordRobotImages/"

translator = Translator()


def get_random_img(): 
    return discord.File(
        f"{images_path}{random.choice(os.listdir(images_path))}",
        filename="consciousness.png"
    )


def translate_fr_en(lang,data):
    translated = translator.translate(text=data,dest='en').text
    print("+\n\n"+translated)
    spinned,xs = spin_text(lang,translated);xs.quit()
    retranslate = translator.translate(text=spinned,dest='fr').text
    print("+\n\n"+retranslate)
    return(retranslate)
        

def translate_fr_en_v2(lang, data):
    translated = translator.translate(text=data, dest='en').text
    print("+\n\n" + translated)
    spinned, xs = spin_text_v2(lang, translated)
    xs.quit()
    retranslate = translator.translate(text=spinned, dest='fr').text
    print("+\n\n" + retranslate)
    return retranslate


class Aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = True


client = Aclient()
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guildid))





@tree.command(name="spin", description="Je refais ta paragraphe en mieux !", guild= discord.Object(id=guildid))
async def spin(interaction: discord.Interaction, paragraphe: str):
    await interaction.response.defer()
    
    spinned_text = translate_fr_en("English", paragraphe)

    embed = create_embed(paragraphe, spinned_text, interaction.user)
    xs = await interaction.followup.send(embed=embed)

    await xs.add_reaction("✅")
    await xs.add_reaction("❌")
    await xs.add_reaction("🔄")

@tree.command(name="correct", description="Je corrige ton grammaire !", guild= discord.Object(id=guildid))
async def correct(interaction: discord.Interaction, paragraphe: str):
    await interaction.response.defer()
    
    spinned_text = grammalecte_text(paragraphe)

    embed = create_embed(paragraphe, spinned_text, interaction.user)
    xs = await interaction.followup.send(embed=embed)

    await xs.add_reaction("✅")
    await xs.add_reaction("❌")
    await xs.add_reaction("🔄")







async def temp_workingedit(msg, x1, user):
    firstcut = str.split(x1,"**Nouvelle version**")
    secondcut = str.split(firstcut[0],"""**Texte d'origine**
> """)[-1].strip()

    embed = create_embed(
        secondcut,
        "Je prévois d'écrire un nouveau paragraphe en fonction du contexte que vous m'avez fournis ⏳ ..\nAttendez quelques petites secondes, s'il vous plaît 🤖 👽",
        user
    )


    spinned_text = translate_fr_en("English", secondcut)
    embed = create_embed(secondcut, spinned_text, user)
    await msg.edit(embed=embed)
    await msg.clear_reactions()
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    await msg.add_reaction("🔄")
    await msg.edit(embed=embed)









@client.event
async def on_raw_reaction_add(payload):
    user = await client.fetch_user(payload.user_id)
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    emoji = str(payload.emoji)

    # Return if the user reacting is a bot
    if user.bot:
        return

    # Check if the user reacting is the original message author or the bot owner
    if payload.member.name != message.embeds[0].author.name and payload.member.id != 1054681455307018251:
        print("Access denied")
        await message.remove_reaction(payload.emoji, user)
        return

    if emoji == "🔙" and "🔙" == message.reactions[0].emoji:
        await message.clear_reactions()
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        await message.add_reaction("🔄")
        return

    if emoji == "⭐" and "⭐" == message.reactions[-1].emoji:
        return

    # Remove reaction if it is not a valid reaction
    if emoji != "✅" and emoji != "❌" and emoji != "🔄":
        await message.remove_reaction(emoji, user)
        return

    if emoji == "❌":
        await message.delete()
        return

    if emoji == "✅":
        await message.clear_reactions()
        await message.add_reaction("🔙")
        await message.add_reaction("⭐")
        return

    if emoji == "🔄" and user.id != client.user.id:
        await message.clear_reactions()
        await message.add_reaction("📝")
        await message.add_reaction("⏳")
        origintext = message.embeds[0].description
        await temp_workingedit(message, origintext, user)
        return

    if emoji == "⭐":
        await message.add_reaction("⭐")
        await message.add_reaction("🔙")
        await message.remove_reaction("✅", client.user)
        await message.remove_reaction("❌", client.user)
        await message.remove_reaction("🔄", client.user)
        return









def create_embed(original_text: str, new_text: str, user: discord.User):
    """Create and return an Embed object for the spin command."""
    embed = discord.Embed(
        title="✍️ ・ Skritur",
        description=
        "*Améliorez votre plume, avec l'intelligence artificielle !*\n\n**Texte d'origine**\n> " +
        original_text +
        "\n\n**Nouvelle version**\n> " +
        new_text +
        "\n\n**Skritur as-t-il fait un bon boulot ? Votre avis l'aide a s'améliorer**\nSi le rendu vous deplai, cliquez sur ``🔄 Relancer``\n──・─__─────__─__────__─__───__─__──__────────────"
    )
    embed.set_footer(text="Hollved ・ Skritur", icon_url="https://cdn.discordapp.com/attachments/1045358677089062963/1060899624489078794/Fichier_7.png")
    embed.set_author(name=user.name, icon_url=user.display_avatar)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1045358677089062963/1060589734331699321/Ligne_invisible_hollved.png")
    return embed








##### CHAT GPT







openai.api_key = "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"


def generate_response(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    return message


"""
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
"""


async def chatgpt_embed(response,user,c_id):
    """Create and return an Embed object for the spin command."""
    embed = discord.Embed(
        title="✍️ ・ Skritur・ChatGPT-3",
        description=("**ChatGPT**\nL'intilligence artificielle la plus intelligente au monde !\n\n**Réponse**\n" +
  "> " + response + "\n\n" +
  "──・─__─────__─__────__─__───__─__──__────────────\n\n" +
    "*Cette fonctionnalité est exclusivement réservée a l'équipe*\n<@&1044610134502023249>\n" +

  "**Chat ID:** *" + str.split(c_id,'-')[-1] + "*"))
    embed.set_footer(text="Hollved ・ Skritur・ChatGPT", icon_url="https://cdn.discordapp.com/attachments/1045358677089062963/1060899624489078794/Fichier_7.png")
    embed.set_author(name=user.name, icon_url=user.display_avatar)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1045358677089062963/1060589734331699321/Ligne_invisible_hollved.png")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1061358792790515742/1061369811743023174/chatgpt.png")
    if c_id=="404":
        embed.color.brand_red()
    return embed


@client.event
async def on_message(message):
  if message.author.bot:
    return
  # define the role IDs that are allowed
  allowed_role_ids = [1044610134502023249]
  # check if the user has one of the allowed role IDs
  if message.content.startswith('<@1060269212301533394>') and any(role.id in allowed_role_ids for role in message.author.roles):
    prompt = message.content.split(' ')
    prompt = ' '.join(prompt[1:])
    
    try:
        response, sessid = chatbot_response(prompt, message.author.id)
        await message.channel.send(embed=await chatgpt_embed(response,message.author,sessid),reference=message)
    except:
        x = await message.channel.send(embed=await chatgpt_embed(get_error_message(),message,"404"),reference=message)
    # create and start a new thread to delete the message after 30 seconds
        async def delete_msg(msg,usermsg):
            print("delprocess")
            await usermsg.add_reaction("⁉️")
            sleep(30)
            await msg.delete()
            print("delprocess")

        thread = Thread(target=await delete_msg(x))
        thread.start()

  if message.content.startswith("!kill") and any(role.id in allowed_role_ids for role in message.author.roles):
    pass




    """
    allowed_ids = [662012101560369182, 1054681455307018251, 759357876246151199]
    print("msgauthorid: "+str(message.author.id))
    if (
        message.content.startswith('<@1060269212301533394>')
        and message.author.id in allowed_ids
    ):
        prompt = message.content.split(' ', 1)[1]
        response = generate_response(prompt)
        await message.channel.send(response, reference=message)
        """








##### CHAT GPT

















client.run('MTAx')