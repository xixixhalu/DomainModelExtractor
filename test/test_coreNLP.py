import sys
sys.path.append('./')
sys.path.append('../')

from adapter import *
import json

sentence = 'By sending an email to the user if they forget the password or otherwise can change in the profile instead.'

output = analyze(sentence)

print(json.dumps(output, sort_keys=True, indent=2))

