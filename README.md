# ELG API for Memad lidbox language identification pipeline

This git repository contains [ELG compatible](https://european-language-grid.readthedocs.io/en/stable/all/A3_API/LTInternalAPI.html) Flask based REST API for [MeMAD](https://memad.eu) language identification project.


The ELG API was developed based on the project [memad-lid-pipeline](https://github.com/MeMAD-project/memad-lid-pipeline), the author of the pipeline is [LimeCraft](https://www.limecraft.com/team/) while the tool [lidbox](https://github.com/py-lidbox/lidbox) is developed by Matias Lindgren with MIT license. The API is in EU's CEF project: [Microservices at your service](https://www.lingsoft.fi/en/microservices-at-your-service-bridging-gap-between-nlp-research-and-industry).


## Use cases
The API can identify these languages: fi, sv, fr, de, en, and x-nolang (denotes no language detected).
The pipeline works in two scenarios:
- if there is an audio file in the request, the API splits the input audio into 2 seconds chunks and predicts corresponding spoken languages.
- if there is an audio file and corresponding annotation/diarization json text in the request, the API returns prediction results and reports the classification metrics. This works like testing the lidbox tool. 

## General setup for local use
The pipeline needs:
- python3.7+
- lidbox
- [plda](https://github.com/RaviSoji/plda): 
- transformer
- memad lid [models](https://zenodo.org/record/4486873#.YaXpQi0Rr0o)


Install dependencies

```
python3 -m venv venv && source venv/bin/activate
pip install -r requiremets.txt
```

Install Lidbox

```
pip install lidbox -e git+https://github.com/py-lidbox/lidbox.git@e60d5ad2ff4d6076f9afaa780972c0301ee71ac8#egg=lidbox
```

Install plda

```
cd plda_bkp
pip install .
```

Install tensorflow

```
pip install tensorflow
```

## Yle Data evaluation example
The Yle dataset with an experimental license is available upon request [here](https://developer.yle.fi/en/data/avdata/index.html). Dataset 1 contains Audio files (12.7 hours of media), subtitles and ground truth transcripts, speaker diarizations, and NER annotations of 16 factual programs in Finnish and Swedish.

The Yle dataset 1 will have the following structure

```
audios/yle_1/part2
????????? audio
???   ????????? MEDIA_2014_00868316.utt2label
???   ????????? MEDIA_2014_00868316.wav
????????? readme_and_licence.txt
```

There is a `raw2json` script to convert utt2label format into json format of diarization that memad needs

```
python3 utils/raw2json.py audios/yle_1/part2/audio/MEDIA_2014_00868316.utt2label 
```

After the conversion, the previous directory tree now looks like

```
audios/yle_1/part2
????????? anno
???   ????????? MEDIA_2014_00868316-diar.json
????????? audio
???   ????????? MEDIA_2014_00868316
???   ????????? MEDIA_2014_00868316.utt2label
???   ????????? MEDIA_2014_00868316.wav
????????? readme_and_licence.txt
```

Then use the `predict_n_test_yle1.sh` bash script to predict and report the classification results of the Yle dataset 1.

```
sh predict_scripts/predict_n_test_yle1.sh audios/yle_1/part2/audio/MEDIA_2014_00868316.wav audios/yle_1/part2/anno/MEDIA_2014_00868316-diar.json
```

Results should be under `report.txt` file.

```
audios/yle_1/part2/audio/MEDIA_2014_00868316/report
????????? report.txt
```

Content of report.txt

```
Out of 56 annotations, there are 31 annotations correctly predicted by memad
There are 0 correct de annotations
There are 0 correct en annotations
There are 23 correct fi annotations
There are 6 correct sv annotations
There are 2 correct x-nolang annotations
              precision    recall  f1-score   support

          de       0.00      0.00      0.00         0
          en       0.00      0.00      0.00         0
          fi       0.77      0.79      0.78        29
          sv       0.75      0.32      0.44        19
    x-nolang       0.67      0.25      0.36         8

    accuracy                           0.55        56
   macro avg       0.44      0.27      0.32        56
weighted avg       0.75      0.55      0.61        56
```

## VOX dev data evaluation
VOX [dev](http://bark.phon.ioc.ee/voxlingua107/dev.zip) dataset contains 1609 speech segments from 33 languages, validated by at least two volunteers. It includes 5 languages that memad lid pipeline supports.
For example, with VOX data structured as follow:
```
audios/VOX
????????? dev
    ????????? de
    ????????? en
    ????????? fi
    ????????? fr
    ????????? sv
```
where each subdir contains audios of that language, the directory name is also the label of all audios file inside it.

Run the evaluation on VOX dataset

```
sh predict_scripts/predict_n_test.sh audios/VOX
```

Example result of the Swedish language case

```
--lang sv
Total audios:  100
Accuracy: 0.49
Classification report:
              precision    recall  f1-score   support

          sv       1.00      0.49      0.66       100

   micro avg       1.00      0.49      0.66       100
   macro avg       1.00      0.49      0.66       100
weighted avg       1.00      0.49      0.66       100
```

## Local development

Start the local development app
```
FLASK_ENV=development flask run --host 0.0.0.0 --port 8000
```

## Building the docker image

```
docker build -t memad-lidbox .
```

Or pull directly ready-made image `docker pull lingsoft/memad-lidbox:tagname`. (currently unavailable)

## Deploying the service

```
docker run -d -p <port>:8000 --init --memory="2g" --restart always memad-lidbox
```

## REST API
The ELG Audio service accepts POST requests of Content-Type: multipart/form-data with two parts, the first part with name `request` has type: `application/json`, and the second part with name `content` will be audio/x-wav type which contains the actual audio data file.

### Call pattern

#### URL

```
http://<host>:<port>/process
```

place `<host>` and `<port>` with the hostname and port where the 
service is running.

#### HEADERS

```
Content-type : multipart/form-data
```

#### BODY

Part 1 with the name `request`

```
{
  "type":"audio",
  "format":"string",
  "sampleRate":number,
  "annotations": "object",
}
```

The property `format` is required and `LINEAR16` value is expected while the property `sampleRate` and `annotations` are optional. For the second use case (see section [use-case](#use-cases), `annotations` is required and should contain annotation data as shown in `multi_form_req.py`

Part 2 with the name `content`
- read in the audio file content
- maximum file size support: 100MB
- `WAV`format only, with an expected 16khz sample rate and a 16-bit sample size.


#### RESPONSE

```
{
   "response":{
      "type":"annotations",
      "annotations":{
         "spoken_language_identification":[
            {
               "start":number,
               "end":number,
               "features":{
                  "lang":str,
                  "true_label":str
               }
            },
         ]
      }
   }
}     
```

### Response structure

- `start` and `end` (float)
  - the time indices of the recognized language parts (in second). If use case 1, each start and end pair has a time interval of 2 seconds.
- `lang` (str)
  - the corresponding identified language. Only one language returns
- `true_label` (str)
   - the corresponding true label of language. One of these labels: 'de', 'en', 'fi', 'fr', 'sv', and 'x-nolang'. The property presents only when the corresponding annotation/diarization json text in the request is sent.

### Example call

The script `multi_form_req.py` sends multipart/form-data POST request with the audio file under `test_samples/memad_test.wav`
`memad_test.wav` is a concatenated audio of five short independent samples in 'de', 'en', 'fi', 'fr', 'sv' languages taken from the VOX dev dataset. Here are the following sample files that were concatenated (in order):
   - -7hqy7xahkM__U__S106---0752.680-0761.950.wav (de)
   - _EHGqmRh9Es__U__S130---0840.140-0846.350.wav (en)
   - 1WCI1U2iEGQ__U__S122---1453.730-1472.010.wav (fi)
   - 0A42eBNqp2Q__U__S0---0753.910-0762.010.wav (fr)
   - _8h3f0QoF5Q__U__S109---0347.590-0361.420.wav (sv)

The true lables of `memad_test.wav` (see `test_samples/memad_test_anno.json`) were manually annotated using Audacity software.

```
python3 multi_form_req.py
```

### Response should be


```
{
  "response": {
    "type": "annotations",
    "annotations": {
      "spoken_language_identification": [
        {
          "start": 2.297,
          "end": 4.613,
          "features": {
            "lang": "de",
            "true_label": "de"
          }
        },
        {
          "start": 4.765,
          "end": 9.278,
          "features": {
            "lang": "en",
            "true_label": "x-nolang"
          }
        },
        {
          "start": 9.297,
          "end": 15.18,
          "features": {
            "lang": "en",
            "true_label": "en"
          }
        },
        {
          "start": 15.958,
          "end": 33.572,
          "features": {
            "lang": "fi",
            "true_label": "fi"
          }
        },
        {
          "start": 34.57,
          "end": 41.602,
          "features": {
            "lang": "fr",
            "true_label": "fr"
          }
        },
        {
          "start": 42.058,
          "end": 55.345,
          "features": {
            "lang": "sv",
            "true_label": "sv"
          }
        }
      ]
    }
  }
}
```

## Test the service
`test_samples` directory contains two audio files: `memad_test.wav` and `olen_kehitt??j??.mp3` for testing purpose `olen_kehitt??j??.mp3` file was captured from Google translation text to speech fo the phrase "Olen kehitt??j??" and used for testing wrong audio format purpose.

To run test

```
python -m unittest test -v
```
