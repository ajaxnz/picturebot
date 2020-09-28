say -r 125 Hi Vivek -v Daniel -o Daniel.aiff
say -r 125 Hi Vivek -v Xander -o Xander.aiff
say -r 125 Hi Vivek -v Karen -o Karen.aiff
say -r 125 Hi Vivek -v Moira -o Moira.aiff
say -r 125 Hi Vivek -v Rishi -o Rishi.aiff
say -r 125 Hi Vivek -v Samantha -o Samantha.aiff
say -r 125 Hi Vivek -v Tessa -o Tessa.aiff
say -r 125 Hi Vivek -v Veena -o Veena.aiff
say -r 125 Hi Vivek -v Victoria -o Victoria.aiff
say -r 100 Hi Vivek -v Daniel -o Daniel.2.aiff
say -r 150 Hi Vivek -v Daniel -o Daniel.3.aiff
say -r 100 Hi Vivek -v Xander -o Xander.2.aiff
say -r 100 Hi Vivek -v Rishi -o Rishi.2.aiff
ffmpeg -i Daniel.aiff \
 -i Xander.aiff \
 -i Karen.aiff \
 -i Moira.aiff \
 -i Rishi.aiff \
 -i Samantha.aiff \
 -i Tessa.aiff \
 -i Veena.aiff \
 -i Victoria.aiff \
 -i Daniel.2.aiff \
 -i Daniel.3.aiff \
 -i Xander.2.aiff \
 -i Rishi.2.aiff \
 -filter_complex amix=inputs=13:duration=longest:dropout_transition=0,volume=10.0 -ac 2 -ar 48000 hivivek.wav
