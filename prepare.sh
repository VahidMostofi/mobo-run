#!/bin/bash
sudo apt-get update
sudo apt-get install -y python3-pip
sudo apt-get install -y git
sudo add-apt-repository ppa:ubuntu-lxc/lxd-stable
sudo apt-get update
sudo apt-get install -y golang
pip3 install sklearn tqdm numpy matplotlib deap pandas scipy
pip3 install git+https://github.com/ppgaluzio/MOBOpt
