import json

def parsePosTag(data):
    tokens = data['sentences'][0]['tokens']
    parse_str = data['sentences'][0]['parse']

    result = {}
    stack = []

    i = 0
    index = 1
    while True:
        if parse_str[i] == '(':
            tag = ''
            i += 1
            while parse_str[i] != '\n' and parse_str[i] != ' ':
                tag += parse_str[i]
                i += 1
            stack.append((tag, index))
        elif parse_str[i] == ')':
            tag = stack[-1][0]
            start = stack[-1][1]
            if tag not in result:
                result[tag] = []
            result[tag].append((start, index - 1))
            stack.pop()
            i += 1
        else:
            while parse_str[i] != '\n' and parse_str[i] != ' ' and parse_str[i] != ')':
                i += 1
            index += 1
        while i < len(parse_str) and (parse_str[i] == '\n' or parse_str[i] == ' '):
            i += 1
        if i == len(parse_str):
            break

    for tag, lst in result.items():
        result[tag] = sorted(lst, key=lambda x: x[0])
    return result


if __name__ == '__main__':
    data = json.load(open('3.json'))
    result = parsePosTag(data)
    print(result)