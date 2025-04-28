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
        <v-col v-if="!loading" cols="4">
          <span class="mr-5">Déplacer la lecture peu avant la frontière</span>
        </v-col>
        <v-col v-if="!loading" cols="4">
          <v-btn color="primary" class="mr-5" @click="seekPreviousBoundary">précédente (S)</v-btn><v-btn color="primary" @click="seekNextBoundary">suivante (Z)</v-btn>
        </v-col>
        <v-col v-if="!loading" cols="4">
        </v-col>
        <v-col v-if="!loading" cols="4">
          <span class="mr-5">Déplacer le début du segment à la frontière</span>
        </v-col>
        <v-col v-if="!loading" cols="4">
          <v-btn color="primary" class="mr-5" @click="moveRegionStartToPreviousBoundary">précédente (Q)</v-btn><v-btn color="primary" @click="moveRegionStartToNextBoundary">suivante (A)</v-btn>
        </v-col>
        <v-col v-if="!loading" cols="4">
          <v-switch v-model="autoValidation" label="Validation automatique en sortie de ligne"></v-switch>
        </v-col>
        <v-col v-if="!loading" cols="4">
          <span class="mr-5">Déplacer la fin du segment à la frontière</span>
        </v-col>
        <v-col v-if="!loading" cols="4">
          <v-btn color="primary" class="mr-5" @click="moveRegionEndToPreviousBoundary">précédente (D)</v-btn><v-btn color="primary" @click="moveRegionEndToNextBoundary">suivante (E)</v-btn>
        </v-col>
        <v-col v-if="!loading" cols="4">
          <v-btn color="primary" v-if="!autoValidation" @click="validateCurrentRegion" :disabled="!currentSegment.text">Valider la ligne courante</v-btn>
          <v-btn color="primary" v-if="autoValidation" @click="cancelPreviousValidation" :disabled="!validationPending">Annuler la précédente validation</v-btn>/
        </v-col>
        <v-col cols="12" :style="`width: ${width}`">
          <div id="waveform-vocals" :style="loading ? 'display:none;' : ''"></div>
          <div id="waveform-audio" :style="loading ? 'display:none;' : ''"></div>
        </v-col>
      </v-row>

    </template>
    <template #actions>
      <v-spacer></v-spacer>
      <v-btn color="primary" variant="flat" @click="alignmentCorrected">
        C'est OK !
      </v-btn>
      <v-spacer></v-spacer>
    </template>
  </v-card>

</template>

<script>
import {api} from "@/api.js";
import WaveSurfer from 'wavesurfer.js'
import RegionsPlugin from 'wavesurfer.js/dist/plugins/regions.esm.js'

export default {
  //components: {VideoWithSubtitles, SegmentAdjuster},
  props: ['width', 'projectName', 'projectData'],
  data: () => ({
    loading: true,
    autoValidation: true,
    validationPending: false,
    currentSegment: {
      text: '',
      start: 0,
      end: 0
    },
    time: 0,
  }),
  unmounted() {
    window.removeEventListener("keydown", this.keyPressed)
  },
  async mounted() {
    window.addEventListener("keydown", this.keyPressed);
    this.$currentRegion = null
    const self = this;
    const response = await api.get(`/karaoke/${this.projectName}/segments-adjustment`)
    const segmentsAdjustment = response.data
    let initialStart = 0.0
    for (const segment of segmentsAdjustment.segments) {
      if (segment.validated)
        continue
      initialStart = Math.max(0, segment.start - 0.5)
      break
    }
    const response2 = await api.get(`/karaoke/${this.projectName}/silence-boundaries`)
    this.$silenceBoundaries = response2.data.boundaries
    this.$reversedSilenceBoundaries = [...response2.data.boundaries].reverse()
    // this.loading = false
    // return
    const [audioSurfer, audioRegions] = await this.createWaveSurfer(this.projectData.audio_wav, "#waveform-audio", {height: 0})
    this.$audioSurfer = audioSurfer
    this.$audioRegions = audioRegions
    const [vocalsSurfer, vocalsRegions] = await this.createWaveSurfer(this.projectData.vocals_wav, "#waveform-vocals", {mediaControls: false})
    this.$vocalsSurfer = vocalsSurfer
    this.$vocalsRegions = vocalsRegions

// Give regions a random color when they are created
//     const random = (min, max) => Math.random() * (max - min) + min
//     const randomColor = () => `rgba(${random(0, 255)}, ${random(0, 255)}, ${random(0, 255)}, 0.5)`

// Create some regions at specific time ranges
    this.$audioSurfer.on('play', () => {
      this.$vocalsSurfer.play()
    })
    this.$audioSurfer.on('pause', () => {
      this.$vocalsSurfer.pause()
    })
    this.$vocalsSurfer.on('seeking', (value) => {
      this.$audioSurfer.setTime(value)
    })
    this.$vocalsSurfer.on('interaction', (value) => {
      this.$audioSurfer.setTime(value)
    })
    this.$vocalsSurfer.on('timeupdate', (time) => {
      self.time = time
    })
    this.$vocalsSurfer.setMuted(true)

    for (const segment of segmentsAdjustment.segments) {
      const color = segment.validated ? `rgba(0, 200, 200, 0.3)` : `rgba(200, 200, 0, 0.3)`
      const region = this.$vocalsRegions.addRegion({
        start: segment.start,
        end: segment.end,
        content: segment.text,
        color,
        drag: false,
        resize: true,
      })
      region.$lyrics = segment.text
      region.$color = color
      region.$segmentId = segment.id
    }
    for (const silenceBoundary of this.$silenceBoundaries) {
      this.$vocalsRegions.addRegion({
        start: silenceBoundary,
        color: `rgba(255, 0, 0, 0.8)`,
        drag: false,
        resize: false,
      })
    }

    this.$vocalsRegions.on('region-in', (region) => {
      if (region.start !== region.end) {
        console.log('region-in', region)
        self.$currentRegion = region
        self.currentSegment.text = region.$lyrics
      }
    })
    this.$vocalsRegions.on('region-out', (region) => {
      if (region.start !== region.end) {
        console.log('region-out', region)
        self.$currentRegion = region
        self.currentSegment.text = ""
        if (self.autoValidation) {
          self.validationPending = true
          self.$validationTimeout = setTimeout(() => {
            console.log("validating region", region.$segmentId)
            self.validationPending = false
            self.$validationTimeout = null
            self.validateRegion(region)
          }, 1500)
        }
      }
    })

    this.setTime(initialStart)
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
    async validateCurrentRegion() {
      if (this.$currentRegion !== null)
        await this.validateRegion(this.$currentRegion)
    },
    cancelPreviousValidation() {
      this.validationPending = false
      if (this.$validationTimeout) {
        clearTimeout(this.$validationTimeout)
      }
    },
    async validateRegion(region) {
      try {
        const start = region.start
        const end = region.end
        const id = region.$segmentId
        const validation = {start, end, id};
        await api.post(`/karaoke/${this.projectName}/_validate_segment`, validation)
        region.setOptions({
          color: `rgba(0, 200, 200, 0.3)`
        })
      } catch (error) {
        console.error(error)
      }
    },
    // togglePlay() {
    //   this.$audioSurfer.playPause()
    // },
    keyPressed(event) {
      switch (event.keyCode) {
        case 90: return this.seekNextBoundary()// Z
        case 83: return this.seekPreviousBoundary()// S
        case 65: return this.moveRegionStartToNextBoundary()// A
        case 81: return this.moveRegionStartToPreviousBoundary()// Q
        case 69: return this.moveRegionEndToNextBoundary()// E
        case 68: return this.moveRegionEndToPreviousBoundary()// D
        // case 32: return this.togglePlay()// Space
      }
    },
    setTime(time) {
      this.$vocalsSurfer.setTime(time)
      this.$audioSurfer.setTime(time)
    },
    seekPreviousBoundary() {
      const boundary = this.findPreviousBoundary()
      if (boundary !== null)
          this.setTime(boundary)
    },
    findPreviousBoundary() {
      const time = this.time
      for (const boundary of this.$reversedSilenceBoundaries)
        if (boundary < time)
          return boundary
      return null
    },
    seekNextBoundary() {
      const boundary = this.findNextBoundary()
      if (boundary !== null)
        this.setTime(boundary)
    },
    findNextBoundary() {
      const time = this.time
      for (const boundary of this.$silenceBoundaries)
        if (boundary > time)
          return boundary
      return null
    },
    moveRegionStartToPreviousBoundary() {
      const region = this.$currentRegion
      if (!region)
        return
      // const end = region.end
      // const content = region.$lyrics
      // const color = region.$color
      const boundary = this.findPreviousBoundary()
      if (boundary !== null) {
        console.log("update start", boundary)
        region.setOptions({
          start: boundary
        })
        // region.remove()
        // const regionDesc = { start: boundary, end, content, color, drag: false, resize: true }
        // console.log(regionDesc)
        // const newRegion = this.$vocalsRegions.addRegion(regionDesc)
        // this.$currentRegion = newRegion
        // newRegion.$lyrics = content
        // newRegion.$color = color
      }
    },
    moveRegionStartToNextBoundary() {
      const region = this.$currentRegion
      if (!region)
        return
      // const end = region.end
      // const content = region.$lyrics
      // const color = region.$color
      const boundary = this.findNextBoundary()
      if (boundary !== null) {
        console.log("update start", boundary)
        region.setOptions({
          start: boundary
        })

        // region.remove()
        // const regionDesc = { start: boundary, end, content, color, drag: false, resize: true }
        // console.log(regionDesc)
        // const newRegion = this.$vocalsRegions.addRegion(regionDesc)
        // this.$currentRegion = newRegion
        // newRegion.$lyrics = content
        // newRegion.$color = color
      }

    },
    moveRegionEndToPreviousBoundary() {
      const region = this.$currentRegion
      if (!region)
        return
      // const start = region.start
      // const content = region.$lyrics
      // const color = region.$color
      const boundary = this.findPreviousBoundary()
      if (boundary !== null) {
        console.log("update end", boundary)
        region.setOptions({
          end: boundary
        })
        // region.remove()
        // const regionDesc = { start, end: boundary, content, color, drag: false, resize: true }
        // console.log(regionDesc)
        // const newRegion = this.$vocalsRegions.addRegion(regionDesc)
        // this.$currentRegion = newRegion
        // newRegion.$lyrics = content
        // newRegion.$color = color
      }
    },
    moveRegionEndToNextBoundary() {
      const region = this.$currentRegion
      if (!region)
        return
      // const start = region.start
      // const content = region.$lyrics
      // const color = region.$color
      const boundary = this.findNextBoundary()
      if (boundary !== null) {
        console.log("update end", boundary)
        region.setOptions({
          end: boundary
        })
        // region.remove()
        // const regionDesc = { start, end: boundary, content, color, drag: false, resize: true }
        // console.log(regionDesc)
        // const newRegion = this.$vocalsRegions.addRegion(regionDesc)
        // this.$currentRegion = newRegion
        // newRegion.$lyrics = content
        // newRegion.$color = color
      }

    },
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

