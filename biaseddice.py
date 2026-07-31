import argparse
import csv
import random
from collections import Counter


parser = argparse.ArgumentParser(
                    prog='Biased dice generation'
)
parser.add_argument('filename')           # positional argument
# parser.add_argument('-v', '--season', type=int, default=1)
# parser.add_argument('-m', '--multipart', action='store_true')      # option that takes a value
args = parser.parse_args()

setup = {
    '1a': {'n': 36, 'bias': 0.3},
    '1b': {'n': 36, 'bias': 0.7},
    '1c': {'n': 36, 'bias': 0.6},
    '1d': {'n': 36, 'bias': 0.4},
    '1e': {'n': 36, 'bias': 0},
    '1f': {'n': 36, 'bias': 0.5},
    '1g': {'n': 36, 'bias': 0.2},
    '1h': {'n': 36, 'bias': 0},
    '1i': {'n': 36, 'bias': 0},
    '1j': {'n': 36, 'bias': 0.1},
    '2a': {'n': 120, 'bias': 0.1},
    '2b': {'n': 120, 'bias': 0},
    '2c': {'n': 120, 'bias': 0.2},
    '2d': {'n': 120, 'bias': 0.7},
    '2e': {'n': 120, 'bias': 0.3},
    '2f': {'n': 120, 'bias': 0.6},
    '2g': {'n': 120, 'bias': 0.5},
    '2h': {'n': 120, 'bias': 0},
    '2i': {'n': 120, 'bias': 0.4},
    '2j': {'n': 120, 'bias': 0},
    '3a': {'n': 480, 'bias': 0.5},
    '3b': {'n': 480, 'bias': 0},
    '3c': {'n': 480, 'bias': 0.2},
    '3d': {'n': 480, 'bias': 0.1},
    '3e': {'n': 480, 'bias': 0.3},
    '3f': {'n': 480, 'bias': 0.4},
    '3g': {'n': 480, 'bias': 0.6},
    '3h': {'n': 480, 'bias': 0},
    '3i': {'n': 480, 'bias': 0.7},
    '3j': {'n': 480, 'bias': 0},
    '4a': {'n': 1992, 'bias': 0.1},
    '4b': {'n': 1992, 'bias': 0.6},
    '4c': {'n': 1992, 'bias': 0.7},
    '4d': {'n': 1992, 'bias': 0.4},
    '4e': {'n': 1992, 'bias': 0.3},
    '4f': {'n': 1992, 'bias': 0.2},
    '4g': {'n': 1992, 'bias': 0},
    '4h': {'n': 1992, 'bias': 0.5},
    '4i': {'n': 1992, 'bias': 0},
    '4j': {'n': 1992, 'bias': 0},
}
DIETYPE = 12
NUMWEIGHTED = 3
csvcolumns = {}



def selectWeighted(dietype=12, numweighted =3):
    diefaces = list(range(1,dietype+1))
    upweights = []
    downweights = []

    for i in range(numweighted):
        up = random.choice(diefaces)
        down = 13- up
        upweights.append(up)
        downweights.append(down)

        diefaces.remove(up)
        diefaces.remove(down)

        print('selectweighted', upweights, downweights)

    return upweights, downweights

def genWeights(dietype=12, numweighted=3, weight=0.1):
    upweight, downweight = selectWeighted(dietype, numweighted)

    faces = []
    weights = []

    for d in range(1,dietype+1):
        faces.append(d)
        if d in upweight:
            weights.append(1+weight)
        elif d in downweight:
            weights.append(1-weight)
        else:
            weights.append(1.0)
    print('genWeights', faces, weights)
    return faces, weights

def rollWeightedDice(dietype=12, numweighted=3, weight=0.1, rolls=100):
    faces, weights = genWeights(dietype, numweighted, weight)

    return random.choices(faces, weights, k=rolls)

for key, spec in setup.items():



    rolls = rollWeightedDice(DIETYPE, NUMWEIGHTED, spec['bias'], spec['n'])
    counts = Counter(rolls)
    if len(counts)<DIETYPE:
        for i in range(1,DIETYPE+1):
            if i not in counts:
                counts[i]=0
    print(counts)
    print(list(dict(sorted(counts.items())).values()))

    csvcolumns[key] = list(dict(sorted(counts.items())).values())

with open(args.filename, "w") as outfile:
    out = csv.DictWriter(outfile, fieldnames=['roll']+list(csvcolumns.keys()))
    out.writeheader()
    for i in range(DIETYPE):
        outrow = {'roll':i+1}
        for k,v in csvcolumns.items():
            try:
                outrow[k]=v[i]
            except:
                print(i, k, v)
                raise

        out.writerow(outrow)











#
#

#
#
# multipartRegexes = [r'(\d+)4$']
# episodeRegex = [r'ep(\d+) ']
# junkStrings = ['english','eng','sub','downsub','com','down','｜','⧸','ตอนจบ']
#
