import os
import time
import static.python.db_modules as mod
import queue

from dotenv import load_dotenv
from twitchio.ext import commands
from twitchio.client import Client
from static.python.utils import json
from random import choices

load_dotenv(os.path.abspath('.env'))

PREFIX = os.environ.get('BOT_PREFIX')
TOKEN = os.environ.get('TOKEN')
BOT_NICK = os.environ.get('BOT_NICK')
gifter = []


client = Client(
    token=TOKEN,
    heartbeat=30.0
)

q = queue.Queue()


def start_queue(item, delay):
    q.put(item)
    while not q.empty():
        time.sleep(delay)
        item = q.get()
    return item


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            prefix=PREFIX,
            token=TOKEN,
            initial_channels=['emerok1'],
            heartbeat=20.0
        )

    async def event_ready(self):
        print(f'Iniciando como | {self.nick}')
        print(f'Id de usuário é | {self.user_id}')

    async def event_raw_usernotice(self, channel, tags):
        prizes = json.loadprizes(channel.name)
        cores = prizes.pop('99')
        prize = []
        weight = []
        for i in prizes:
            prize.append(prizes[f'{i}']['prize'])
            weight.append(prizes[f'{i}']['weight'])
        resultado = choices(prize, weights=weight)[0]
        if tags['msg-id'] == 'sub' or tags['msg-id'] == 'resub':
            ganhador = tags['display-name']
            mod.add_prize(ganhador, resultado, channel.name)
            print('sub', tags['display-name'],
                  tags['msg-param-cumulative-months'])
            for i in prizes:
                if resultado == prizes[i]['prize']:
                    desc = prizes[i]['desc']
                    item = start_queue(desc, 14)
                    await channel.send(f'/me {ganhador}, você ganhou....... {item}')
                    try:
                        points = prizes[i]['points']
                        await channel.send(f'!addpoints {ganhador} {points}')
                    except KeyError:
                        pass
                    try:
                        price = prizes[i]['price']
                        bank = cores['weight']
                        new = bank - price
                        json.editweight(channel.name, '99', new)
                        if new < prizes[i]['price']:
                            json.editweight(channel.name, i, 0)
                    except KeyError:
                        pass
        elif tags['msg-id'] == 'submysterygift':
            print('massgift', tags['login'], tags['msg-param-mass-gift-count'])
            gifter.append([tags['login'], tags['msg-param-mass-gift-count']])
        elif tags['msg-id'] == 'subgift':
            for i in range(len(gifter)):
                if tags['login'] == gifter[i][0]:
                    gifter[i][1] = int(gifter[i][1]) - 1
                    ganhador = tags['msg-param-recipient-display-name']
                    mod.add_prize(ganhador, resultado, channel.name)
                    for i in prizes:
                        if resultado == prizes[i]['prize']:
                            desc = prizes[i]['desc']
                            item = start_queue(desc, 3)
                            await channel.send(f'/me {ganhador}, você ganhou....... {item}')
                            try:
                                points = prizes[i]['points']
                                await channel.send(f'!addpoints {ganhador} {points}')
                            except KeyError:
                                pass
                            try:
                                price = prizes[i]['price']
                                bank = cores['weight']
                                new = bank - price
                                json.editweight(channel.name, '99', new)
                                if new < prizes[i]['price']:
                                    json.editweight(channel.name, i, 0)
                            except KeyError:
                                pass

                    if gifter[i][1] == 0:
                        gifter.remove(gifter[i])
                else:
                    print(
                        'gift', tags['msg-param-recipient-display-name'], tags['msg-param-months'])
                    ganhador = tags['msg-param-recipient-display-name']
                    mod.add_prize(ganhador, resultado, channel.name)
                    for i in prizes:
                        if resultado == prizes[i]['prize']:
                            desc = prizes[i]['desc']
                            item = start_queue(desc)
                            await channel.send(f'/me {ganhador}, você ganhou....... {item}')
                            try:
                                points = prizes[i]['points']
                                await channel.send(f'!addpoints {ganhador} {points}')
                            except KeyError:
                                pass
                            try:
                                price = prizes[i]['price']
                                bank = cores['weight']
                                new = bank - price
                                json.editweight(channel.name, '99', new)
                                if new < prizes[i]['price']:
                                    json.editweight(channel.name, i, 0)
                            except KeyError:
                                pass

    async def event_message(self, message):

        if message.echo:
            return

        autor = message.author.name
        canal = message.channel.name
        content = message.content
        hora = message.timestamp.strftime('%H:%M:%S')
        print(f'#{canal} {hora} {autor}: {content}')

        await self.handle_commands(message)

    @commands.command(name='sortear')
    async def sortear(self, ctx: commands.Context):
        if ctx.author.is_mod:
            prizes = json.loadprizes(ctx.channel.name)
            cores = prizes.pop('99')
            prize = []
            weight = []
            ganhador = ctx.message.content.split()[1]
            for i in prizes:
                prize.append(prizes[f'{i}']['prize'])
                weight.append(prizes[f'{i}']['weight'])
            resultado = choices(prize, weights=weight)[0]
            mod.add_prize(ganhador, resultado, ctx.channel.name)
            for i in prizes:
                if resultado == prizes[i]['prize']:
                    desc = prizes[i]['desc']
                    await ctx.send(f'/me {ganhador}, você ganhou....... {desc}')
                    try:
                        points = prizes[i]['points']
                        await ctx.send(f'!addpoints {ganhador} {points}')
                    except KeyError:
                        pass
                    try:
                        price = prizes[i]['price']
                        bank = cores['weight']
                        new = bank - price
                        json.editweight(ctx.channel.name, '99', new)
                        if new < prizes[i]['price']:
                            json.editweight(ctx.channel.name, i, 0)
                    except KeyError:
                        pass


bot = Bot()
