import discord
from discord import app_commands
from wonderwords import RandomWord
from novelai_api import NovelAIAPI
from novelai_api.ImagePreset import ImageModel, ImageResolution, UCPreset, ImagePreset
from logging import Logger, StreamHandler
from aiohttp import ClientSession

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    async def on_ready(self):
        await tree.sync(guild= discord.Object(id = 'GUILD ID'))
        print("bot online")

client = MyClient(intents=discord.Intents().all())
tree = app_commands.CommandTree(client)


@tree.command(name = "girl", description = "Default - 1girl,highres. Currated is 'good basis/expected subject' ('chainsaw man' will give Makima)", guild= discord.Object(id = 'GUILD ID'))
async def girl(interaction: discord.Interaction, currated_model: bool = False, override_default_tags: bool = False, post_tags: bool = False, seed: int = 0, tags: str = None):
    await interaction.response.defer()
    if not tags and not override_default_tags:
        tags = "1girl, highres"
    elif not override_default_tags:
        tags = "1girl, highres, " + tags

    await genimage(interaction,currated_model,post_tags,tags,seed,1)
   
  
@tree.command(name = "boy", description = "Default - 1boy,highres. Currated is 'good basis/expected subject' ('chainsaw man' will give Makima)", guild= discord.Object(id = 'GUILD ID'))
async def boy(interaction: discord.Interaction, currated_model: bool = False, override_default_tags: bool = False, post_tags: bool = False, seed: int = 0, tags: str = None):
    await interaction.response.defer()
    if not tags and not override_default_tags:
        tags = "1boy, highres"
    elif not override_default_tags:
        tags = "1boy, highres, " + tags 
        
    await genimage(interaction,currated_model,post_tags,tags,seed,2)
    
tree.command(name= "random", description = "Generate a random image", guild= discord.Object(id = 'GUILD ID'))
async def randomimg(interaction: discord.Interaction):
    await interaction.response.defer()
    
    startlistrandum = random.randint(1,100)
    finalstr = ""
     
    if startlistrandum <= 5:
        finalstr = '{{abstract}}, {{{{{no humans}}}}}, hires'
    elif startlistrandum <= 10:
        finalstr = '{{object focus}}, {{{{{no humans}}}}}, hires'
    elif startlistrandum <= 45:
        finalstr = "1girl, hires"
    else:
        finalstr = "1boy, hires"

    wordlist = []
    for i in range(8):
        wrd = r.word()
        if random.randint(0,100) < 25:
            numsquids = range(random.randint(1,5))
            for i in numsquids:
                wrd = '{' + wrd + '}'       
        wordlist.append(wrd)

    for i in wordlist:
        finalstr = finalstr + ", " + i
        
    await genimage(interaction,False,True,finalstr,0,3)    
    
async def genimage(interaction,currated_model,post_tags,tags,seed,imgnum):
    
    imgstr = f"image_{imgnum}.png"
    
    logger = Logger("NovelAI")
    logger.addHandler(StreamHandler())
    api = NovelAIAPI(logger = logger)
    session = ClientSession()
    await session.__aenter__()
    api.attach_session(session)
    await api.high_level.login('EMAIL', 'PASSWORD')
                
    preset = ImagePreset()
    preset["uc"] = ", bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet"
    imgmdl = ImageModel.Anime_Full
    if currated_model:
        imgmdl = ImageModel.Anime_Curated
    if seed != 0:
        preset["seed"] = seed    
    async for img in api.high_level.generate_image(tags, imgmdl, preset):
        with open(imgstr, "wb") as f:
             f.write(img)
    await interaction.followup.send(file=discord.File(imgstr))
    if post_tags:
        im = Image.open(imgstr)   
        im.load()
        metadata = json.loads(im.info['Comment'])
        seed = metadata["seed"]        
        await interaction.followup.send(tags + " - Seed: " + str(seed))
    await session.close()
    
client.start('TOKEN')
