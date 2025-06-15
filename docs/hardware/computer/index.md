# Computer
Our computer is based on the NVidia Jetson Orin Development Kit.

# Links
- Main Nvidia Jetson Orin page: https://developer.nvidia.com/embedded/learn/jetson-agx-orin-devkit-user-guide/developer_kit_layout.html
- Datasheets for NVidia Jetson Orin: https://developer.nvidia.com/embedded/downloads
TODO link here to datasheets in the repo itself

# Data
## Power
- Power consumption: 
- Voltage range:
- Power connectors: USB-C, barrel TODO something, 5.5mm maybe + add inner diameter

## Specs
TODO

# Notes
## How to install Anydesk in Nvidia Jetson Orin
```bash
wget -qO - https://keys.anydesk.com/repos/DEB-GPG-KEY | sudo apt-key add -
echo 'deb http://deb.anydesk.com/ all main' | sudo tee /etc/apt/sources.list.d/anydesk.list                                                                                           
sudo apt update                                                                                                                                                                       
sudo apt install -y anydesk 
```


