$install = <<-SCRIPT
sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.9 -y
sudo apt install python3.9-distutils -y
curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
python3.9 /tmp/get-pip.py
python3.9 -m pip install --upgrade setuptools
python3.9 -m pip install -r /irc_bot/requirements.txt
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.synced_folder ".", "/irc_bot"
  config.vm.provision "shell", inline: $install
end
