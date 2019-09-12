import sys
sys.path.append('./')
sys.path.append('../')

from adapter import *
import json

sentence = 'As a user, I can redeem usable WAT points so that I can receive a gift card.'

output = analyze(sentence)

print json.dumps(output, sort_keys=True, indent=2)

