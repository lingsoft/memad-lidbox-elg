import os
import json
from sys import exit
import requests
from elg.model import Failure
from elg.model.base import StandardMessages

def send_request(url, audio, anno=''):

    if anno:
        with open(anno) as json_file:
            anno_lst = json.load(json_file)
        
        try:
            for anno_ in anno_lst:
                anno_["features"] = {"label": anno_.pop("id") if "id" in anno_ else "x-nolang"}
                anno_["start"] = float(anno_["start"])
                anno_["end"] = float(anno_["end"])
                anno_ = json.dumps(anno_)
        except Exception:
            err_msg = StandardMessages.generate_elg_request_invalid(
                        detail={"request": "Annotation JSON must contain starting and ending times of speech fragments."})
            print(Failure(errors=[err_msg]))
            exit()
            
        annots = {"segments": anno_lst}
        payload = {
            "type": "audio",
            "format": "LINEAR16",
            "sampleRate": 16000,
            "annotations": annots
        }
    else:
        payload = {"type": "audio", "format": "LINEAR16", "sampleRate": 16000}

    with open(audio, 'rb') as f:
        files = {
            'request': (None, json.dumps(payload), 'application/json'),
            'content': (os.path.basename(audio), f.read(), 'audio/x-wav')
        }

    r = requests.post(url, files=files)
    print(json.dumps(r.json(), indent=2))


print('Sending request with annotation')
send_request(url='http://localhost:8000/process',
             audio='test_samples/memad_test.wav',
             anno='test_samples/memad_test_anno.json')
