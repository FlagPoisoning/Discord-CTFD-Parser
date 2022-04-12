FILE=discord.zip
ROOTPASS=DiscordSuperBot
USER=discordbot
DOMAIN=bot

HTTP_PORT=80
HTTPS_PORT=443

DOCUMENT_ROOT=/var/www/$DOMAIN

echo "Installing ..."

apt-get -y -qq update;
apt-get install -y -qq build-essential;
apt-get -y -qq install systemctl bash ffmpeg libsndfile1 pip tar file sox nano git unzip sudo wget curl zip ssldump exiftool pngcheck binwalk rubygems ssh stegsnow sox tshark chaosreader strace ltrace checksec binutils-multiarch;
unzip /var/www/$DOMAIN/$FILE
python3 -m pip install -r requirements.txt
wget https://gist.githubusercontent.com/dhondta/feaf4f5fb3ed8d1eb7515abe8cde4880/raw/stegopvd.py && chmod +x stegopvd.py && sudo mv stegopvd.py /usr/bin/stegopvd
stegoveritas_install_deps
mv ./analysis/tools/identify /usr/bin/identify
git clone https://github.com/ribt/dtmf-decoder.git
cd dtmf-decoder/
sudo python3 -m pip install -r requirement.txt --upgrade
chmod +x dtmf.py
sudo cp dtmf.py /usr/local/bin/dtmf
wget -O /usr/bin/jsteg https://github.com/lukechampine/jsteg/releases/download/v0.1.0/jsteg-linux-amd64
chmod +x /usr/bin/jsteg
wget -O /usr/bin/slink https://github.com/lukechampine/jsteg/releases/download/v0.2.0/slink-linux-amd64
chmod +x /usr/bin/slink

wget http://www.openssl.org/source/openssl-1.0.1g.tar.gz
tar -xvzf openssl-1.0.1g.tar.gz
cd openssl-1.0.1g
./config --prefix=/usr/local/openssl --openssldir=/usr/local/openssl
make
make install
git clone https://github.com/radareorg/radare2
cd radare2 ; sys/install.sh
echo "cd $DOCUMENT_ROOT" >> /root/.bashrc;
useradd -m -s /bin/bash $USER;
echo $USER:$USER | chpasswd;
echo root:$ROOTPASS | chpasswd;
#rm /var/www/$DOMAIN/$FILE;

echo "Finish !"