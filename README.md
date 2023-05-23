# telebotgptchat
First step you should do is to download latest_silero_models.yml to your main folder.
You can do this using this piece of code:

import torch
from pprint import pprint
from omegaconf import OmegaConf
torch.hub.download_url_to_file('https://raw.githubusercontent.com/snakers4/silero-models/master/models.yml',
                               'latest_silero_models.yml',
                               progress=False)
                               
this .yml must be put in the same folder with main.py in order to work properly
also, do not forget to download all used libraries.
