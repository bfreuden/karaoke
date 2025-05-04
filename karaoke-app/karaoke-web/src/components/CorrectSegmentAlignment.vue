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
        <v-col v-if="!loading" cols="4">
          <span class="mr-5">Déplacer la lecture peu avant la frontière</span>
        </v-col>
        <v-col v-if="!loading" cols="4">
          <v-btn color="primary" class="mr-5" @click="seekPreviousBoundary">précédente (S)</v-btn><v-btn color="primary" @click="seekNextBoundary">suivante (Z)</v-btn>
        </v-col>
        <v-col v-if="!loading" cols="4">
          <v-checkbox v-model="shiftSegments">Pousser les segments à droite</v-checkbox>
        </v-col>
        <v-col v-if="!loading" cols="4">
          <span class="mr-5">Déplacer le début du segment à la frontière</span>
        </v-col>
        <v-col v-if="!loading" cols="4">
          <v-btn color="primary" class="mr-5" @click="moveRegionStartToPreviousBoundary">précédente (Q)</v-btn><v-btn color="primary" @click="moveRegionStartToNextBoundary">suivante (A)</v-btn>
        </v-col>
        <v-col v-if="!loading" cols="4">
        </v-col>
        <v-col v-if="!loading" cols="4">
          <span class="mr-5">Déplacer la fin du segment à la frontière</span>
        </v-col>
        <v-col v-if="!loading" cols="4">
          <v-btn color="primary" class="mr-5" @click="moveRegionEndToPreviousBoundary">précédente (D)</v-btn><v-btn color="primary" @click="moveRegionEndToNextBoundary">suivante (E)</v-btn>
        </v-col>
        <v-col v-if="!loading" cols="4">
        </v-col>
        <v-col v-if="!loading" cols="4">
          <v-switch v-model="autoValidation" label="Validation automatique en sortie de segment"></v-switch>
        </v-col>
        <v-col v-if="!loading" cols="4">
          <v-btn color="primary" v-if="!autoValidation" @click="toggleValidation" :disabled="!currentSegment.text">Changer la validation de la ligne courante</v-btn>
<!--          <v-btn color="primary" v-if="!autoValidation" @click="validateCurrentRegion" :disabled="!currentSegment.text">Valider la ligne courante</v-btn>-->
          <v-btn color="primary" v-if="autoValidation" @click="cancelPreviousValidation" :disabled="!validationPending">Annuler la précédente validation</v-btn>
        </v-col>
        <v-col v-if="!loading" cols="4">
          <v-btn color="primary" @click="playCurrentSegment" :disabled="!currentSegment.text">Jouer le segment</v-btn>
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

const VALIDATED_COLOR = `rgba(0, 200, 200, 0.3)`
const UNVALIDATED_COLOR = `rgba(200, 200, 0, 0.3)`
const SILENCE_BOUNDARY_COLOR = `rgba(255, 0, 0, 0.8)`

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
    shiftSegments: false,
  }),
  unmounted() {
    window.removeEventListener("keydown", this.keyPressed)
  },
  async mounted() {
    window.addEventListener("keydown", this.keyPressed);
    this.$currentRegion = null
    this.$stopOnRegionOut = null
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
      console.log(value)
      const currentRegion = this.$vocalsRegions.regions.find(it => it.start <= value && value <= it.end)
      this.$currentRegion = currentRegion
      this.currentSegment.text = this.$currentRegion ? this.$currentRegion.$lyrics : ""
    })
    this.$vocalsSurfer.on('interaction', (value) => {
      this.$audioSurfer.setTime(value)
      console.log(value)
      const currentRegion = this.$vocalsRegions.regions.find(it => it.start <= value && value <= it.end)
      this.$currentRegion = currentRegion
      this.currentSegment.text = this.$currentRegion ? this.$currentRegion.$lyrics : ""
    })
    this.$vocalsSurfer.on('timeupdate', (time) => {
      self.time = time
    })
    this.$vocalsSurfer.setMuted(true)

    for (const segment of segmentsAdjustment.segments) {
      const color = segment.validated ? VALIDATED_COLOR : UNVALIDATED_COLOR
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
      region.$id = segment.id
      region.$validated = segment.validated
    }
    for (const silenceBoundary of this.$silenceBoundaries) {
      this.$vocalsRegions.addRegion({
        start: silenceBoundary,
        color: SILENCE_BOUNDARY_COLOR,
        drag: false,
        resize: false,
      })
    }
    this.computeSortedRegions()

    this.$vocalsRegions.on('region-in', (region) => {
      const stopOnRegionOut = this.$stopOnRegionOut
      if (region.start !== region.end && stopOnRegionOut === null) {
        console.log('region-in', region)
        self.$currentRegion = region
        self.currentSegment.text = region.$lyrics
      }
    })
    this.$vocalsRegions.on('region-out', (region) => {
      const stopOnRegionOut = this.$stopOnRegionOut
      if (stopOnRegionOut && region.$id === stopOnRegionOut.$id) {
        this.$audioSurfer.pause()
        this.$vocalsSurfer.pause()
        this.$stopOnRegionOut = null
      }
      if (region.start !== region.end) {
        console.log('region-out', region)
        self.currentSegment.text = ""
        if (self.autoValidation) {
          self.validationPending = true
          self.$validationTimeout = setTimeout(() => {
            console.log("validating region", region.$id)
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

    this.$vocalsRegions.on('region-updated', async (region) => {

      region.setOptions({
        color: UNVALIDATED_COLOR
      })
      const update = {start: region.start, end: region.end, id: region.$id, validated: region.$validated};
      await api.post(`/karaoke/${this.projectName}/_adjust_segment`, update)
      await self.maybeRightShiftOtherRegions(region)
    })

    // Update the zoom level on slider change
    this.$vocalsSurfer.once('decode', () => {
      document.querySelector('input[type="range"]').oninput = (e) => {
        const minPxPerSec = Number(e.target.value)
        this.$vocalsSurfer.zoom(minPxPerSec)
      }
    })
  },
  methods: {
    playCurrentSegment() {
      this.$stopOnRegionOut = this.$currentRegion
      this.$vocalsSurfer.setTime(this.$currentRegion.start+0.01)
      this.$audioSurfer.setTime(this.$currentRegion.start+0.01)
      this.$vocalsSurfer.play()
      this.$audioSurfer.play()
    },
    computeSortedRegions() {
      this.$sortedRegionsAscending = this.$vocalsRegions.regions.sort((a, b) => a.start - b.start).filter(it => it.end !== it.start).map(it => ({"$id": it.$id, "start": it.start, "end": it.end, "$lyrics": it.$lyrics}))
    },
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
        region.$validated = true
        region.setOptions({
          color: VALIDATED_COLOR
        })
        await this.updateRegion(region)
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
          this.setTime(Math.max(0, boundary-0.7))
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
        this.setTime(Math.max(0, boundary-0.7))
     },
    findNextBoundary() {
      const time = this.time
      for (const boundary of this.$silenceBoundaries)
        if (boundary > time)
          return boundary
      return null
    },
    async moveRegionStartToPreviousBoundary() {
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
        await this.updateRegion(region)
        await this.maybeRightShiftOtherRegions(region)
      }
    },
    async toggleValidation() {
      this.$currentRegion.setOptions({
        color: this.$currentRegion.$validated ? UNVALIDATED_COLOR : VALIDATED_COLOR
      })
      this.$currentRegion.$validated = !this.$currentRegion.$validated
      const validation = {start: this.$currentRegion.start, end: this.$currentRegion.end, id: this.$currentRegion.$id, validated: !this.$currentRegion.$validated};
      await api.post(`/karaoke/${this.projectName}/_adjust_segment`, validation)
    },
    async updateRegion(region) {
      const validation = {start: region.start, end: region.end, id: region.$id, validated: true};
      await api.post(`/karaoke/${this.projectName}/_adjust_segment`, validation)
    },
    async moveRegionStartToNextBoundary() {
      const region = this.$currentRegion
      if (!region)
        return
      // const end = region.end
      // const content = region.$lyrics
      // const color = region.$color
      const boundary = this.findNextBoundary()
      if (boundary !== null) {
        console.log("update start", boundary)
        let end = region.end
        if (boundary >= end) {
          end = boundary + 0.5
        }
        region.setOptions({
          start: boundary,
          end,
        })
        await this.updateRegion(region)
        await this.maybeRightShiftOtherRegions(region)
      }

    },
    async maybeRightShiftOtherRegions(region) {
      if (!this.shiftSegments)
        return
      const updates = []
      let currentRegionFound = false
      let previousRegionEnd = false
      for (const otherRegion of this.$sortedRegionsAscending) {
        if (!currentRegionFound) {
          currentRegionFound = region.$id === otherRegion.$id
          if (currentRegionFound) {
            previousRegionEnd = region.end
          }
          continue
        }
        if (otherRegion.$validated)
          continue
        if (otherRegion.start < previousRegionEnd) {
          const shift = previousRegionEnd - otherRegion.start
          const newStart = otherRegion.start + shift
          let newEnd = otherRegion.end + shift
          if (newEnd <= (newStart + 0.5))
            newEnd = newStart + 0.5
          previousRegionEnd = newEnd
          const otherRealRegion = this.$vocalsRegions.regions.find(it => it.$id === otherRegion.$id)
          otherRealRegion.setOptions({
            start: newStart,
            end: newEnd,
          })
          updates.push({id: otherRealRegion.$id, start: otherRealRegion.start, end: otherRealRegion.end, validated: false})

        } else {
          break
        }
      }
      this.computeSortedRegions()
      await api.post(`/karaoke/${this.projectName}/_adjust_segments`, updates)
    },
    async moveRegionEndToPreviousBoundary() {
      const region = this.$currentRegion
      if (!region)
        return
      // const start = region.start
      // const content = region.$lyrics
      // const color = region.$color
      const boundary = this.findPreviousBoundary()
      if (boundary !== null) {
        console.log("update end", boundary)
        let start = region.start
        if (boundary <= start) {
          start = boundary - 0.5
        }
        region.setOptions({
          start: start,
          end: boundary
        })
        await this.updateRegion(region)
        await this.maybeRightShiftOtherRegions(region)
      }
    },
    async moveRegionEndToNextBoundary() {
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
        await this.updateRegion(region)
        await this.maybeRightShiftOtherRegions(region)
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
    async alignmentCorrected() {
      const data = { alignment_correction: false}
      await api.patch(`/karaoke/${this.projectName}`, data)
      this.$emit('alignment-corrected');
    }
  }
}

</script>

