import json
from util import unicode_2str


with open('./index.json') as fh:
    index = unicode_2str(json.load(fh))
