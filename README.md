# picturebot
Discord bot for the world famous PictureDice TTRPG system



run with
- `python3 picturebot.py`

build docker image with
- `docker image build --tag picturebot .`
- save with `docker image save picturebot -o ../picturebot.tar.gz`
- or run `docker run picturebot`

setup sound
- `say Excuse me, take a break. A timeout card has been used. -v fiona -o tcard.aiff`
- convert using Music (horrid) or use ffmpeg, has to be 48khz stereo
- `ffmpeg -i tcard.aiff -ac 2 -ar 48000 tcard.wav`

install 
- `https://discord.com/api/oauth2/authorize?client_id=734818153292628058&permissions=271821840&scope=bot`
- discord permissions
 - connect,speak
 - send,manage,attach,read history,mention
 - view channels,  possibly manage channels&roles
