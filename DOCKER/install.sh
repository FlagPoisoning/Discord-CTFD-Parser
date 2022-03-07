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
apt-get -y -qq install systemctl bash libsndfile1 pip tar file sox nano unzip sudo wget curl zip ssh;
unzip /var/www/$DOMAIN/$FILE
python3 -m pip install -r requirements.txt
echo "cd $DOCUMENT_ROOT" >> /root/.bashrc;
useradd -m -s /bin/bash $USER;
echo $USER:$USER | chpasswd;
echo root:$ROOTPASS | chpasswd;

echo "Finish !"