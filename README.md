
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

### Install pytorch

#### GPU install 
Warning: it really depends on:
- your nvidia driver version
- your GPU compute capability: https://developer.nvidia.com/cuda-gpus
- cudnn support matrix: https://docs.nvidia.com/deeplearning/cudnn/backend/latest/reference/support-matrix.html

For GTX 1050 Ti and nvidia driver version 535
```
pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121
```

#### CPU install

``` 
pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cpu
```

### Install NVIDIA NeMo

```
pip install nemo_toolkit['asr']==2.2.1
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



