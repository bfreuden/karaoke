


<template>
  <h1>WaveSurferPlayer Using Components </h1>

  <div>
    <WaveSurferPlayer :options="options" @timeupdate="(time: number) => timeUpdateHandler(time)"
                      @ready="(duration: number) => readyHandler(duration)"
                      @waveSurfer="(ws: WaveSurfer) => readyWaveSurferHandler(ws)"/>

  </div>
  <p> currentTime: {{ currentTime }}</p>
  <p>totalDuration:{{ totalDuration }}</p>
  <button @click="waveSurfer?.playPause()" :style="{ minWidth: '5em' }">
    Play
  </button>
</template>


<script setup lang="ts">
  import {ref} from 'vue'
  import type WaveSurfer from 'wavesurfer.js'
  import {WaveSurferPlayer} from '@meersagor/wavesurfer-vue'
  import Minimap from 'wavesurfer.js/dist/plugins/minimap.esm.js'
  // import Spectrogram from 'wavesurfer.js/dist/plugins/spectrogram.esm.js'

  const options = ref({
  height: 48,
  waveColor: 'gray',
  progressColor: 'red',
  barGap: 5,
  barWidth: 5,
  barRadius: 8,
  duration: 80,
  barHeight: 2,
  minPxPerSec: 100,
  height: 300,
  hideScrollbar: false,
  autoCenter: false,
  // url: "https://revews-bucket.s3.ap-southeast-1.amazonaws.com/a06mmMU3sgnzuUkH4OiHvyuUgCFdLSnJaDLBao7y.webm",
  url: "/static/op2op/vocals.wav",
  plugins: [
      // Register the plugin
      Minimap.create({
      height: 20,
      waveColor: '#ddd',
      progressColor: '#999',
      // the Minimap takes all the same options as the WaveSurfer itself
    }),
    // Spectrogram.create({
    //   labels: true,
    //   height: 200,
    //   splitChannels: true,
    //   scale: 'mel', // or 'linear', 'logarithmic', 'bark', 'erb'
    //   frequencyMax: 8000,
    //   frequencyMin: 0,
    //   fftSamples: 1024,
    //   labelsBackground: 'rgba(0, 0, 0, 0.1)',
    // }),
  ],
})

  const currentTime = ref<string>('00:00')
  const totalDuration = ref<string>('00:00')
  const waveSurfer = ref<WaveSurfer | null>(null)

  const formatTime = (seconds: number): string => [seconds / 60, seconds % 60].map((v) => `0${Math.floor(v)}`.slice(-2)).join(':')

  const timeUpdateHandler = (time: number) => {
    currentTime.value = formatTime(time)
  }
  const readyHandler = (duration: any) => {
    totalDuration.value = formatTime(duration)
  }
  const readyWaveSurferHandler = (ws: WaveSurfer) => {
    waveSurfer.value = ws
    waveSurfer.setTime(8.0)
  }
</script>
<style scoped>

</style>
