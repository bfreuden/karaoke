# pyenv

https://github.com/pyenv-win/pyenv-win

## Installation

https://github.com/pyenv-win/pyenv-win/blob/master/docs/installation.md#powershell

Open a Powershell prompt in Administrator then run:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine 
```
And and run:
``` 
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

## Install Python 3.10

```
pyenv install 3.10
```

## Create a virtual env for karaoke

```
cd karaoke
pyenv local 3.10.11
python venv env
```

## Activate virtual env for karaoke
```
 .\env\Scripts\Activate.ps1
```

## Install requirements
```
pip install -r requirements.txt
```

## Install Python requirements

Download ffmpeg binaries 
https://www.gyan.dev/ffmpeg/builds/
https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

And put the bin directory into the PATH.


