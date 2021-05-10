import sys
sys.path.append('./')
sys.path.append('../')

from adapter import *
import json

sentence = 'GM can both extracts and visualizes PlayerLibraries so that GM can build Roster for the next Season and make informed Decisions affecting the bottom-line .'

output = analyze(sentence)

print(json.dumps(output, sort_keys=True, indent=2))

