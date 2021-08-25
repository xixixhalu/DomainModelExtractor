import sys
sys.path.append('./')
sys.path.append('../')

from adapter import *
import json

sentence = 'Admin can send an Email to User.'
# sentence = 'Admin can send users an email.'

output = analyze(sentence)

print(json.dumps(output, sort_keys=True, indent=2))

