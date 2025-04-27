<template>
  <v-card
    class="py-4"
    color="surface-variant"
    prepend-icon="mdi-rocket-launch-outline"
    rounded="lg"
    variant="tonal"
  >
    <!--    <template #image>-->
    <!--      <v-img position="top right"/>-->
    <!--    </template>-->

    <template #title>
      <h2 class="text-h5 font-weight-bold">
        Corriger l'alignement des paroles
      </h2>
    </template>

    <template #text>
      <v-row  class="mt-5">
        <v-col v-if="loading" cols="12">
          <v-progress-circular indeterminate></v-progress-circular>
        </v-col>
        <v-col v-else cols="12">
          <h2 class="text-h5 font-weight-bold">
            {{ currentSegment.text }}
          </h2>
        </v-col>
        <v-col v-if="!loading" cols="12">
          <span class="mr-5">Déplacer le début du segment au</span><v-btn class="mr-5">Silence précédent</v-btn><v-btn>Silence suivant</v-btn>
        </v-col>
        <v-col v-if="!loading" cols="12">
          <span class="mr-5">Déplacer la fin du segment au</span><v-btn class="mr-5">Silence précédent</v-btn><v-btn>Silence suivant</v-btn>
        </v-col>
        <v-col cols="12" style="width: 1024px">
          <div id="waveform-audio" style="display:none;"></div>
          <div id="waveform-vocals" :style="loading ? 'display:none;' : ''"></div>
        </v-col>
      </v-row>

    </template>
    <template #actions>
      <v-spacer></v-spacer>
      <v-btn variant="flat" color="primary" @click="alignmentCorrected">
        C'est OK !
      </v-btn>
      <v-spacer></v-spacer>
    </template>
  </v-card>

</template>

<script>
import ASS from 'ass-html5'
// import VideoWithSubtitles from "@/components/VideoWithSubtitles.vue";
import {api} from "@/api.js";
// import SegmentAdjuster  from "@/components/SegmentAdjuster.vue";
import WaveSurfer from 'wavesurfer.js'
import RegionsPlugin from 'wavesurfer.js/dist/plugins/regions.esm.js'

export default {
  //components: {VideoWithSubtitles, SegmentAdjuster},
  props: ['projectName', 'projectData'],
  data: () => ({
    loading: true,
    currentSegment: {
      text: '',
      start: 0,
      end: 0
    },
    time: 0,
  }),
  async mounted() {
    const self = this;
    const response = await api.get(`/karaoke/${this.projectName}/segments_adjustment`)
    const segmentsAdjustment = response.data
    const response2 = await api.get(`/karaoke/${this.projectName}/non_silence_segments`)
    const nonSilenceSegments = response.data

    const [audioSurfer, audioRegions] = await this.createWaveSurfer(this.projectData.audio_wav, "#waveform-audio")
    this.$audioSurfer = audioSurfer
    this.$audioRegions = audioRegions
    const [vocalsSurfer, vocalsRegions] = await this.createWaveSurfer(this.projectData.vocals_wav, "#waveform-vocals")
    this.$vocalsSurfer = vocalsSurfer
    this.$vocalsRegions = vocalsRegions

// Give regions a random color when they are created
//     const random = (min, max) => Math.random() * (max - min) + min
//     const randomColor = () => `rgba(${random(0, 255)}, ${random(0, 255)}, ${random(0, 255)}, 0.5)`

// Create some regions at specific time ranges
    this.$vocalsSurfer.on('play', () => {
      this.$audioSurfer.play()
    })
    this.$vocalsSurfer.on('pause', () => {
      this.$audioSurfer.pause()
    })
    this.$vocalsSurfer.on('seeking', (value) => {
      this.$audioSurfer.seekTo(value / segmentsAdjustment.audio_duration)
    })
    this.$vocalsSurfer.on('timeupdate', (time) => {
      self.time = time
    })
    this.$vocalsSurfer.setMuted(true)
    // this.$vocalsSurfer.seekTo(segmentsAdjustment.initial_start / segmentsAdjustment.audio_duration)
    // this.$audioSurfer.seekTo(segmentsAdjustment.initial_start / segmentsAdjustment.audio_duration)

    for (const segment of segmentsAdjustment.corrected_segments) {
      this.$vocalsRegions.addRegion({
        start: segment.start,
        end: segment.end,
        content: segment.text,
        color: `rgba(0, 200, 200, 0.3)`,
        drag: false,
        resize: false,
      })
    }
    for (const segment of segmentsAdjustment.next_suggested_segments) {
      const region = this.$vocalsRegions.addRegion({
        start: segment.start,
        end: segment.end,
        content: segment.text,
        color: `rgba(200, 200, 0, 0.3)`,
        drag: false,
        resize: true,
      })
      region.$lyrics = segment.text
    }

    this.$vocalsRegions.on('region-in', (region) => {
      console.log('region-in', region)
      self.$currentRegion = region
      self.currentSegment.text = region.$lyrics
      self.currentSegment.start = region.start
      self.currentSegment.end = region.end
    })
    this.$vocalsRegions.on('region-out', (region) => {
      console.log('region-out', region)
      self.$lastRegion = region
      self.$currentRegion = region
      self.currentSegment.text = region.$lyrics
      self.currentSegment.start = region.start
      self.currentSegment.end = region.end
    })


    if (segmentsAdjustment.corrected_segments.length > 0) {
      this.$vocalsSurfer.setTime(segmentsAdjustment[segmentsAdjustment.length - 1].end)
      this.$audioSurfer.setTime(segmentsAdjustment[segmentsAdjustment.length - 1].end)
    } else {
      this.$vocalsSurfer.setTime(segmentsAdjustment.initial_start)
      this.$audioSurfer.setTime(segmentsAdjustment.initial_start)
    }
    this.loading = false

    // this.$vocalsSurfer.setScroll(100)

    // regions.enableDragSelection({
    //   color: 'rgba(255, 0, 0, 0.1)',
    // })
    //
    this.$vocalsRegions.on('region-updated', (region) => {
      console.log('Updated region', region)
    })

  // // Loop a region on click
  //   let loop = true
  // // Toggle looping with a checkbox
  //   document.querySelector('input[type="checkbox"]').onclick = (e) => {
  //     loop = e.target.checked
  //   }
  //
  //   {
  //     let activeRegion = null
  //     regions.on('region-clicked', (region, e) => {
  //       e.stopPropagation() // prevent triggering a click on the waveform
  //       activeRegion = region
  //       region.play(true)
  //       region.setOptions({color: randomColor()})
  //     })
  //     // Reset the active region when the user clicks anywhere in the waveform
  //     this.$vocalsSurfer.on('interaction', () => {
  //       activeRegion = null
  //     })
  //   }

    // Update the zoom level on slider change
    this.$vocalsSurfer.once('decode', () => {
      document.querySelector('input[type="range"]').oninput = (e) => {
        const minPxPerSec = Number(e.target.value)
        this.$vocalsSurfer.zoom(minPxPerSec)
      }
    })
  },
  methods: {
    async createWaveSurfer(url, container, options) {
      return new Promise((resolve, reject) => {
        try {
          const regions = RegionsPlugin.create()
          const surfer = WaveSurfer.create({
            barGap: 5,
            mediaControls: true,
            autoCenter: true,
            barWidth: 5,
            barRadius: 8,
            duration: 80,
            barHeight: 3,
            minPxPerSec: 100,
            height: 300,
            hideScrollbar: false,
            waveColor: 'rgb(200, 0, 200)',
            progressColor: 'rgb(100, 0, 100)',
            plugins: [regions],
            url,
            container,
            ...options,
          })
          surfer.on('ready', () => {
            resolve([surfer, regions])
          })
          } catch (error) {
          reject(error)
        }
      });
    },
    // async alignmentCorrected() {
    //   const data = { alignment_correction: (this.projectData.alignment_correction + 1)}
    //   await api.patch(`/karaoke/${this.projectName}`, data)
    //   this.$emit('correct-alignment');
    // }
  }
}

</script>

