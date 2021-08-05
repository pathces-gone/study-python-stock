#https://discordpy.readthedocs.io/en/stable/faq.html
# https://realpython.com/how-to-make-a-discord-bot-python/
import discord      #!pip3 install --user discord
from finance_info import FinanceInfo

__MY_TOKEN__ = ''
PAGE = 10

class chatbot(discord.Client):
  async def on_ready(self):
    game = discord.Game('내용')
    await client.change_presence(status=discord.Status.online, activity=game)
    print('READY')

  async def on_message(self, message):
    global PAGE
    if message.author.bot:
      return None

    if message.content[0:len('@setpage=')] == '@setpage=':
      channel = message.channel
      try:
        print(message.content[len('@setpage='):len('@setpage=')+2])
        PAGE = int(message.content[len('@setpage='):len('@setpage=')+2])
      except:
        PAGE = 10
  
      msg = 'set page: %d'%(PAGE)
      await channel.send(msg)

    if message.content[0] == '!':
      channel = message.channel
      msg = '%s stochastic.'%(message.content[1:])
      await channel.send(msg)
      msg = 'Please wait about 10s ...'
      await channel.send(msg)

      item = FinanceInfo(message.content[1:],page=PAGE)
      item.get_stochastic()
      with open(item.get_filename(), 'rb') as fp:
        await channel.send(file=discord.File(fp, 'new_filename.png'))

      return None

if __name__ == '__main__':
  print('%d\n'%PAGE)
  client = chatbot()
  client.run(__MY_TOKEN__)

 