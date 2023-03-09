import os
import argparse
import string
import re
from pymkv import MKVFile
from pymkv import MKVTrack


'''
firefox plugin for video download is crap quality, but works
movies better quality: https://y2down.cc/en/
subs: https://downsub.com/
'''
parser = argparse.ArgumentParser(
                    prog='Movie name fixer for plex',
                    description='What the program does',
                    epilog='Text at the bottom of help')
parser.add_argument('folder')           # positional argument
parser.add_argument('-v', '--season', type=int, default=1)
parser.add_argument('-l','--language', default='jpn')
parser.add_argument('-r', '--rename', action='store_true')
parser.add_argument('-e','--encode', action='store_true')
parser.add_argument('-m', '--multipart', action='store_true')      # option that takes a value
args = parser.parse_args()


multipartRegexes = [(r'(\d+)4$', r'part\1')]
episodeRegex = [(r'ep(\d+) ', r'S01E\1 ')]
junkStrings = ['english','eng','sub','downsub','com','down','｜','⧸']


def main(args):
    files = os.listdir(args.folder)
    filepairs = linkFilePairs(files)

    # tidyup names
    for key, details in filepairs.items():
        tidyFileNames(key, details)

        applyFileChanges(args, details)

    return


def tidyFileNames(key, details):
    mov = details['mov']
    sub = details.get('sub')
    newkey = key
    for rule in episodeRegex:
        newkey, subs = re.subn(rule[0], rule[1], key)
        if subs:
            episode = re.findall(rule[0], key)[0]
            details['episode'] = episode
            break
    key = newkey
    for rule in multipartRegexes:
        newkey, subs = re.subn(rule[0], rule[1], key)
        if subs:
            part = re.findall(rule[0], key)[0]
            details['part'] = part
            break
    details['newkey'] = newkey
    dir, file, ext = splitFile(mov)
    details['outmov'] = joinFile(dir, newkey, ext)
    if sub:
        dir, file, ext = splitFile(sub)
        details['outsub'] = joinFile(dir, newkey, ext)


def applyFileChanges(args, details):
    print(f"{details['newkey']}: Episode {details.get('episode')} Part {details.get('part')}")
    print(f"     mov {details['mov']} sub {details.get('sub')}")

    newkey = details['newkey']
    if args.encode:
        dir, file, ext = splitFile(details['mov'])
        newfilename = joinFile(os.path.join(dir, 'new'), newkey, ".mkv")
        details['outmkv'] = newfilename
        newmkv = MKVFile(title=newkey)
        newmkv.add_track(MKVTrack(details['mov'], language='zxx', track_id=0))
        newmkv.add_track(MKVTrack(details['mov'], language=args.language, track_id=1))
        if 'sub' in details:
            newmkv.add_track(MKVTrack(details['sub'], language='eng'))
        newmkv.mux(newfilename, silent=True)
        print(f"     encoded to  {details['outmkv']}")
    elif args.rename:
        os.rename(details['mov'], details['outmov'])
        if 'sub' in details:
            os.rename(details['sub'], details['outsub'])
            print(f"     renamed to {details['outmov']}")


def linkFilePairs(files):
    subs = set()
    movs = set()
    for f in files:
        dir, file, ext = splitFile(f)
        if ext == '.py':
            continue
        if ext in ('.srt', '.sub'):
            subs.add(f)
        elif ext in ('.mp4', '.mkv'):
            movs.add(f)
    subLookup = {stripPuncF(f): f for f in subs}
    filepairs = {}  # key : {
    for f in movs:
        key = stripPuncF(f)
        if key in subLookup:
            filepairs[key] = {'mov': f,
                              'sub': subLookup[key]}
        else:
            filepairs[key] = {'mov': f}
    return filepairs



def stripPunc(s):
    s=s.translate(str.maketrans('', '', string.punctuation))
    s = s.lower()
    for j in junkStrings:
        s = s.replace(j,'')
    s = s.strip()
    s = s.replace('  ',' ')
    s = s.replace('  ',' ')
    s = s.replace('  ',' ')
    s = s.replace('  ',' ')
    return s

def stripPuncF(f):
    dir, file, ext = splitFile(f)
    stripFile = stripPunc(file)
    return stripFile


def splitFile(f):
    dir = os.path.dirname(f)
    file, ext = os.path.splitext(os.path.basename(f))
    return dir, file, ext
def joinFile(dir, file, ext):
    if not ext.startswith("."):
        ext = '.'+ext
    path = os.path.join(dir, file+ext)
    return path



main(args)


'''
add subs
/Applications/MKVToolNix-74.0.0.app/Contents/MacOS/mkvmerge --ui-language en_US --priority lower --output '/Volumes/Inbox/midnight museum/midnight museum พิพิธภัณฑ์รัตติกาล S01E1 part1.mkv' --language 0:und --language 1:und '(' '/Volumes/Inbox/midnight museum/midnight museum พิพิธภัณฑ์รัตติกาล S01E1 part1.mp4' ')' --language 0:und '(' '/Volumes/Inbox/midnight museum/midnight museum พิพิธภัณฑ์รัตติกาล S01E1 part1.srt' ')' --track-order 0:0,0:1,1:0


concatenate 4 with sub
/Applications/MKVToolNix-74.0.0.app/Contents/MacOS/mkvmerge --ui-language en_US --priority lower --output '/Volumes/Inbox/midnight museum/midnight museum พิพิธภัณฑ์รัตติกาล S01E1 part1 (1).mkv' --language 0:zxx --display-dimensions 0:1280x720 --language 1:th --sub-charset 2:UTF-8 --language 2:en '(' '/Volumes/Inbox/midnight museum/midnight museum พิพิธภัณฑ์รัตติกาล S01E1 part1.mkv' ')' --sub-charset 2:UTF-8 + '(' '/Volumes/Inbox/midnight museum/midnight museum พิพิธภัณฑ์รัตติกาล S01E1 part2.mkv' ')' --sub-charset 2:UTF-8 + '(' '/Volumes/Inbox/midnight museum/midnight museum พิพิธภัณฑ์รัตติกาล S01E1 part3.mkv' ')' --sub-charset 2:UTF-8 + '(' '/Volumes/Inbox/midnight museum/midnight museum พิพิธภัณฑ์รัตติกาล S01E1 part4.mkv' ')' --track-order 0:0,0:1,0:2 --append-to 1:0:0:0,2:0:1:0,3:0:2:0,1:1:0:1,2:1:1:1,3:1:2:1,1:2:0:2,2:2:1:2,3:2:2:2





'''