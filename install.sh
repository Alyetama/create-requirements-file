#!/bin/sh

pip3 install -r requirements.txt
rm /usr/local/bin/genreq > /dev/null 2>&1
cp main.py /usr/local/bin/genreq
chmod +x /usr/local/bin/genreq

echo '-------------------- Installed successfully! --------------------\n'
genreq --help
