import sys
sys.path.append('./')
sys.path.append('../')

from adapter import *
import json

sentence = 'As an admin, I can delete / deactivate Users.'

output = analyze(sentence)

print(json.dumps(output, sort_keys=True, indent=2))

