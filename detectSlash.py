import stanfordnlp
import re


def detectSlash(sentences):
    # sentences is a list!
        temp = set()
        for i in sentences:
            if '/' in i:
                match = re.search('(([a-zA-Z]+)/[a-zA-Z]+)',i).group(0)
                spl = match.split('/')
                temp.add(i.replace(match,spl[0]))
                temp.add(i.replace(match,spl[1]))
            else:
                return sentences
        return detectSlash(temp)
# This is the basic logic. Need to add something about tags to get more accuracy.


text = ['As a general manger, I can monitor real-time twitter/facebook/instagram feeds/reaction from key sources in a continuous manner and/or on demand.']
print(detectSlash(text))