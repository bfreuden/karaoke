
# 1 demi-ton en plus = frequence * 1,059463035
# 1 ton en plus = frequence * 1,059463035 ^ 2
# 1.5 ton en plus = frequence * 1,059463035 ^ 3

# 1.5 ton en moins = frequence *0,840896557 0.840896557

# ffmpeg -i accompaniment.wav -af asetrate=44100*0.840896557,aresample=44100,atempo=1/0.840896557 accompaniment-1.5.wav