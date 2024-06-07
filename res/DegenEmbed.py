import discord


class DegenEmbed:
    def __init__(self, title, description, logo=None, color=0x1f6e9e):
        self.embed_title = title
        self.embed_description = description
        self.embed_logo = logo
        self.embed_color = color
        self.embed = discord.Embed(title=self.embed_title, url="https://www.seattledegens.wtf", description=self.embed_description,
                                   color=self.embed_color)

# Need to_dict for some embed internals.
    def to_dict(self):
        return self.embed.to_dict()

    def create(self):
        self.embed.set_author(name=f"Get Fucked", icon_url=self.embed_logo)
        self.embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/1737241?v=4")
        self.embed.set_footer(text="Made by ur mum")

    def add_field(self, name, value, inline=True):
        self.embed.add_field(name=name, value=value, inline=inline)