
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

### Install Visual Studio C++ Build Tools

https://visualstudio.microsoft.com/fr/visual-cpp-build-tools/

```
vs_buildtools__370953915.1537938681.exe --quiet --add Microsoft.VisualStudio.Workload.VCTools
```

```
$env:Path = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.16.27023\bin\HostX64\x64;" + $env:Path
```

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
python -m venv karaoke
```

### Activate the virtual env
```
 .\karaoke\Scripts\Activate.ps1
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


```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
jiwer 3.1.0 requires click>=8.1.8, but you have click 7.1.2 which is incompatible.
nemo-toolkit 2.2.1 requires protobuf==3.20.3, but you have protobuf 3.19.6 which is incompatible.
onnx 1.17.0 requires protobuf>=3.20.2, but you have protobuf 3.19.6 which is incompatible.
pyannote-database 5.1.3 requires typer>=0.12.1, but you have typer 0.3.2 which is incompatible.

```

``` 
    rank_termination_signal: signal.Signals = signal.SIGKILL
        SIGKILL => SIGILL
    karaoke\karaoke\Lib\site-packages\nemo\utils\exp_manager.py
```

````
https://dev.to/methane/python-use-utf-8-mode-on-windows-212i
align with PYTHONUTF8=1 
````