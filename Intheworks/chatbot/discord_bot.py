#https://discordpy.readthedocs.io/en/stable/faq.html
# https://realpython.com/how-to-make-a-discord-bot-python/
import discord      #!pip3 install --user discord
from finance_info import FinanceInfo
from stocksignal_info import StocksignalInfo
import os

__MY_TOKEN__ = os.environ.get('DISCORD_KEY')
assert __MY_TOKEN__ is not None, ""

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

      try:
        item = FinanceInfo(message.content[1:],page=PAGE)
        item.get_stochastic()
        fn = item.get_filename()
        with open(fn, 'rb') as fp:
          await channel.send(file=discord.File(fp, fn))
      except:
        msg = '종목을 찾을 수 없습니다.'
        await channel.send(msg)
      return None

    if message.content[0] == '#':
      if message.content[1:] == '매수상위':
        channel = message.channel
        msg = '매수상위종목'
        await channel.send(msg)
        msg = 'Please wait about 10s ...'
        await channel.send(msg)
      
        try:
          item = StocksignalInfo()
          item.run()
          fn = item.get_filename()
          with open(fn, 'rb') as fp:
            await channel.send(file=discord.File(fp, fn))
        except:
          msg = 'URL: 404 Error'
          await channel.send(msg)
          return None

if __name__ == '__main__':
  print('%d\n'%PAGE)
  client = chatbot()
  client.run(__MY_TOKEN__)

 
