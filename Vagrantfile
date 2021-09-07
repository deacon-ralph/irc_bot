Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.synced_folder ".", "/irc_bot"
  config.disksize.size = '12GB'
  config.vm.customize ["modifyvm", :id, "--memory", 1024]
  config.vm.customize ["modifyvm", :id, "--cpus", 2]
end
