
# Python installation procedure

## Windows

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

### Install languages
```
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
```


### Install additional Python requirements

Download ffmpeg binaries 
https://www.gyan.dev/ffmpeg/builds/
https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

And put the bin directory into the PATH.



## Linux

### Install Pyenv

https://github.com/pyenv/pyenv

https://github.com/pyenv/pyenv?tab=readme-ov-file#unixmacos

Open a terminal then run:
```
curl https://pyenv.run | bash 
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
source env/bin/activate 
```

### Install requirements
```
pip install -r requirements.txt
```

### Install languages
```
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
```


### Install additional Python requirements

Download ffmpeg binaries:
```
sudo apt install ffmpeg
```



