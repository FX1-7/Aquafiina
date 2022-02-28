from discord.ext import commands
import discord
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
WELCOME_IMAGE_ID = 866987484318400512
SERVER_ID = 866970151873806366

WELCOMEBG = "./aqua.jpg"
LEAVEBG = "./aqua.jpg"
# FONT = ""
# FONTSIZE = 16
# FONT = ImageFont.truetype(FONT, FONTSIZE)

def draw_text(y, font, text, draw, width):
    """
    Draw text on an image
    y is the y pos the image will be placed under
    font is the TrueType font
    text is the text to be drawn
    draw is the ImageDraw object
    width is the width of the image to be drawn on - the text will be centered in this width
    """
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)
    textWidth = font.getsize(text)[0]
    x = (width - textWidth) / 2
    for y_p in range(-1, 2):
        for x_p in range(-1, 2):
            draw.text((x + x_p, y + y_p), text, font=font, fill=shadowcolor)
    draw.text((x, y), text, font=font, fill=fillcolor)
    return draw

def num_suffix(n):
    """
    Format a number into a string and prepend "nd" "st" "rd" etc
    """
    return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

def mask_circle_transparent(pil_img, offset=0):
    """
    Crop an image to a circle shape
    """
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)

    result = pil_img.copy()
    result.putalpha(mask)

    return result

def make_welcome(pfp: BytesIO, member: discord.Member):
    tag = str(member)  # username#1234
    joinpos = member.guild.member_count

    bg = Image.open(WELCOMEBG)  # open the welcome background
    bg = bg.resize((1024, 500))  # resize

    pfp = Image.open(pfp)  # make the pfp a PIL Image
    pfp = mask_circle_transparent(pfp)  # crop pfp to circle
    pfp = pfp.resize((265, 265))  # make pfp 265x265

    # hardcode values since the images are resized to a hardcoded value
    bg.paste(pfp, (380, 45, 645, 310), pfp)  # paste pfp onto image

    draw = ImageDraw.Draw(bg)  # Start a draw canvas using the background

    # draw all text
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 60)
    draw = draw_text(325, font, "Welcome", draw, bg.size[0])
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
    draw = draw_text(395, font, tag, draw, bg.size[0])
    draw = draw_text(440, font, f"You are our {num_suffix(joinpos)} member", draw, bg.size[0])

    return bg  # changes are saved to the bg so return that

def make_leave(pfp: BytesIO, member: discord.Member):
    tag = str(member)  # username#1234
    joinpos = member.guild.member_count

    bg = Image.open(WELCOMEBG)  # open the welcome background
    bg = bg.resize((1024, 500))  # resize

    pfp = Image.open(pfp)  # make the pfp a PIL Image
    pfp = mask_circle_transparent(pfp)  # crop pfp to circle
    pfp = pfp.resize((265, 265))  # make pfp 265x265

    # hardcode values since the images are resized to a hardcoded value
    bg.paste(pfp, (380, 45, 645, 310), pfp)  # paste pfp onto image

    draw = ImageDraw.Draw(bg)  # Start a draw canvas using the background

    draw = ImageDraw.Draw(bg)

    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 60)
    draw = draw_text(325, font, "Goodbye", draw, bg.size[0])
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
    draw = draw_text(395, font, tag, draw, bg.size[0])
    draw = draw_text(440, font, f"They were our {num_suffix(joinpos)} member", draw, bg.size[0])
    # STUFF HERE

    return bg  # changes are saved to the bg so return that


class WelcomeImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(WELCOME_IMAGE_ID)

    async def get_pfp(self, member: discord.Member):
        """
        Downloads profile picture as a PNG into a bytes object
        """
        img = member.display_avatar
        img = await img.read()
        return img

    async def send_image(self, image, filename="image.png"):
        channel = self.bot.get_channel(WELCOME_IMAGE_ID)
        """
        Convert the image object to a bytes stream and sends it to the needed channel
        """
        image_b = BytesIO()
        image.save(image_b, format='png')
        image_b.seek(0)
        await channel.send(file=discord.File(image_b, filename=filename))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(WELCOME_IMAGE_ID)
        if member.guild.id != SERVER_ID:
            return
        image = await self.get_pfp(member)
        image = make_welcome(BytesIO(image), member)
        await self.send_image(image)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(WELCOME_IMAGE_ID)
        if member.guild.id != SERVER_ID:
            return
        image = await self.get_pfp(member)
        image = make_leave(BytesIO(image), member)
        await self.send_image(image)


def setup(bot):
    bot.add_cog(WelcomeImage(bot))
