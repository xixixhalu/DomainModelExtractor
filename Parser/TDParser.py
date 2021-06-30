import json

def TypeDep(data):
    tdjson = data['sentences'][0]['enhancedDependencies']

    result1 = {}
    result2 = {}

    for dep in tdjson:
        for key in dep:
            if key == 'dep':
                result1[dep.get(key)] = []

    for dep in tdjson:
        case = dep.get('dep')
        gover = dep.get('governor')
        depe = dep.get('dependent')
        tup = (gover, depe)

        result1[case].append(tup)  # TD type as key; e.g. 'det': [(3,2), (5,4)]
        result2[tup] = case  # Index tuple as key; e.g. (3,2): 'det'

    return result2

def TypeDep1(data):
    tdjson = data['sentences'][0]['basicDependencies']

    result1 = {}
    result2 = {}

    for dep in tdjson:
        for key in dep:
            if key == 'dep':
                result1[dep.get(key)] = []

    for dep in tdjson:
        case = dep.get('dep')
        gover = dep.get('governor')
        depe = dep.get('dependent')
        tup = (gover, depe)

        result1[case].append(tup)  # TD type as key; e.g. 'det': [(3,2), (5,4)]
        result2[tup] = case  # Index tuple as key; e.g. (3,2): 'det'

    return result1


def pure_enhancedTD(data):
    tdjson = data['sentences'][0]['enhancedDependencies']

    result1 = {}
    # result2 = {}

    for dep in tdjson:
        for key in dep:
            if key == 'dep':
                result1[dep.get(key)] = []

    for dep in tdjson:
        case = dep.get('dep')
        gover = dep.get('governor')
        depe = dep.get('dependent')
        tup = (gover, depe)

        result1[case].append(tup)  # TD type as key; e.g. 'det': [(3,2), (5,4)]
        # result2[tup] = case  # Index tuple as key; e.g. (3,2): 'det'

    return result1


def enhancedTD(data):
    tdjson = data['sentences'][0]['enhancedDependencies']

    result1 = {}
    # result2 = {}

    for dep in tdjson:
        for key in dep:
            if key == 'dep':
                case = dep.get(key)
                cut_index = case.find(":")
                if cut_index >= 0:
                    case = case[:cut_index]
                result1[case] = []

    for dep in tdjson:
        case = dep.get('dep')
        gover = dep.get('governor')
        depe = dep.get('dependent')
        tup = (gover, depe)

        cut_index = case.find(":")
        if cut_index >= 0:
            case = case[:cut_index]
        result1[case].append(tup)  # TD type as key; e.g. 'det': [(3,2), (5,4)]
        # result2[tup] = case  # Index tuple as key; e.g. (3,2): 'det'

    return result1

def getType(result, ind1, ind2):  # Retrieve the TD type of two words with the given indexes
    for record in result:
        if record == (ind1, ind2):  # or record == (ind2, ind1):
            return result[record]


if __name__ == '__main__':
    data = json.load(open('3.json'))
    result = TypeDep(data)
    print(result)
    TD = getType(result, 3, 2)
    print(TD)

