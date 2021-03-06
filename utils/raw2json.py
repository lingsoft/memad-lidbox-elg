import pandas as pd
import json
import os
from os.path import dirname as up


def str2ts(x):
    return int(x) * 1.0 / 1000


def utt2label2lang(path):
    df = pd.read_csv(path, sep=' ', names=['name', 'lang'])

    df['start'] = df['name'].map(lambda x: str2ts(x.split('_')[3]))
    df['end'] = df['name'].map(lambda x: str2ts(x.split('_')[4]))
    return df


utt2label_path = os.sys.argv[1]
# eg: audios/yle_1/part2/audio/MEDIA_2014_00868316.utt2label
wav_fname = utt2label_path.split('/')[-1].split('.')[0]
audio_base_dir = up(up(utt2label_path))
anno_diar_path = audio_base_dir + '/anno/' + wav_fname + '-diar.json'

df = utt2label2lang(utt2label_path)

res = []
for index, row in df.iterrows():
    name = row['lang']
    start = str(row['start'])
    end = str(row['end'])
    res.append({'id': name, 'start': start, 'end': end})

print(res)

with open(anno_diar_path, 'w') as f:
    json.dump(res, f)
