import os
import json


def loadprizes(canal):
    with open(os.path.abspath('resources')+f'/{canal}/prizes.json', encoding='utf8') as json_file:
        prizes = json.load(json_file)
        return prizes


def editweight(canal, id, weight):
    with open(os.path.abspath('resources')+f'/{canal}/prizes.json', encoding='utf8') as json_file:
        prizes = json.load(json_file)
        prizes[f'{id}']['weight'] = float(weight)
    with open(os.path.abspath('resources')+f'/{canal}/prizes.json', 'w', encoding='utf-8') as json_file:
        json.dump(prizes, json_file, indent=2, ensure_ascii=False)
