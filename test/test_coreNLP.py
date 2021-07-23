import sys
sys.path.append('./')
sys.path.append('../')

from adapter import *
import json

sentence = 'SporTechB.IContractor can update the PlayerData as the Season progresses .'

output = analyze(sentence)

print(json.dumps(output, sort_keys=True, indent=2))

