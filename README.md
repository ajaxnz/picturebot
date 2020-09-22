# picturebot
Discord bot for the world famous PictureDice TTRPG system



run with
- `python3 picturebot.py`

build docker image with
- `docker image build --tag picturebot .`
- `docker image save picturebot -o picturebot.tar.gz`

setup sound
- `say Excuse me, take a break. A timeout card has been used. -v fiona -o tcard.aiff`
- convert using Music (horrid) or use ffmpeg, has to be 48khz stereo
- `ffmpeg -i tcard.aiff -ac 2 -ar 48000 tcard.wav`