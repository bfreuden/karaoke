
# Python installation procedure

## Linux

### Install Docker

See: https://docs.docker.com/engine/install/

### Install Pyenv dependencies

See: https://github.com/pyenv/pyenv/wiki#suggested-build-environment


Ubuntu/Debian:
```
sudo apt update; sudo apt install build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl git \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev 
```

CentOS/Fedora 21 and below:
``` 
yum install gcc make patch zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel
```

Fedora 22 and above:
``` 
dnf install make gcc patch zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel libuuid-devel gdbm-libs libnsl2
```

### Install Pyenv

https://github.com/pyenv/pyenv

https://github.com/pyenv/pyenv?tab=readme-ov-file#unixmacos

Open a terminal then run:
```
curl https://pyenv.run | bash 
```

### Install Python 3.10

```
pyenv install 3.10.12
```

### Create a virtual env 

```
pyenv virtualenv 3.10.12 karaoke
```

### Activate the virtual env

```
pyenv shell karaoke
```

### Install requirements
```
pip install -r requirements.txt
```

### Install additional Python requirements

Download ffmpeg binaries:
```
sudo apt install ffmpeg
```




## Windows

TODO!!

### Install Pyenv

https://github.com/pyenv-win/pyenv-win

https://github.com/pyenv-win/pyenv-win/blob/master/docs/installation.md#powershell

Open a Powershell prompt in Administrator then run:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine 
```
And and run:
``` 
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

### Install Python 3.10

```
pyenv install 3.10.11
```

### Create a virtual env 

```
cd karaoke
pyenv local 3.10.11
python -m venv env
```

### Activate the virtual env
```
 .\env\Scripts\Activate.ps1
```

### Install requirements
```
pip install -r requirements.txt
```


### Install additional Python requirements

Download ffmpeg binaries 
https://www.gyan.dev/ffmpeg/builds/
https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

And put the bin directory into the PATH.


