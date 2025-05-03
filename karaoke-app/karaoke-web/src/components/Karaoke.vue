<template>
  <v-container class="fill-height" :max-width="width" >
    <v-fab
      absolute
      app
      location="top right"
      color="primary"
      icon
      @click="closeKaraoke"
    >
      <v-icon>mdi-reload</v-icon>
    </v-fab>
    <v-row v-if="initialized">
      <v-col
        v-if="freshKaraoke && freshKaraokeAction === null"
        cols="12"
        style="width: 900px"
      >
        <NewOrExistingKaraoke
          @new-karaoke="freshKaraokeAction = 'create'"
          @open-karaoke="freshKaraokeAction = 'open'"
        ></NewOrExistingKaraoke>
      </v-col>
      <v-col
        v-if="freshKaraoke && freshKaraokeAction === 'open'"
        cols="12"
        style="width: 900px"
      >
        <OpenKaraoke
          @open-karaoke="karaokeSelected"
        ></OpenKaraoke>
      </v-col>
      <v-col
        v-if="freshKaraoke && freshKaraokeAction === 'create'"
        cols="12"
      >
        <NewKaraoke
          @karaoke-created="karaokeSelected"
        ></NewKaraoke>
      </v-col>
      <v-col
        v-if="projectName && !projectData.youtube_url"
        cols="12"
      >
        <SelectVideo
          :project-name="projectName"
          @video-selected="getKaraokeData"
        ></SelectVideo>
      </v-col>
      <v-col
        v-if="projectName && projectData.youtube_url && (!projectData.lyrics || !projectData.language)"
        cols="12"
      >
        <SelectLyrics
          :project-name="projectName"
          :artist="projectData.artist"
          :title="projectData.title"
          @lyrics-selected="getKaraokeData"
        ></SelectLyrics>
      </v-col>
      <v-col
        v-if="projectName && projectData.lyrics && projectData.language && !projectData.video_accompaniment_mp4"
        cols="12"
      >
        <GenerateKaraoke
          :project-name="projectName"
          @karaoke-generated="getKaraokeData"
        ></GenerateKaraoke>
      </v-col>
      <v-col
        v-if="projectName && projectData.video_accompaniment_mp4 && projectData.alignment_correction === null"
        cols="12"
      >
        <KaraokeResult
          version="preview"
          :project-name="projectName"
          :project-data="projectData"
          @correct-alignment="getKaraokeData"
        ></KaraokeResult>
      </v-col>
      <v-col
        v-if="projectName && projectData.video_accompaniment_mp4 && projectData.alignment_correction === true"
        cols="12"
      >
        <CorrectSegmentAlignment
          :width="width"
          :project-name="projectName"
          :project-data="projectData"
          @alignment-corrected="getKaraokeData"
        ></CorrectSegmentAlignment>
      </v-col>
      <v-col
        v-if="projectName && projectData.video_accompaniment_mp4 && projectData.alignment_correction === false && !projectData.realignment_ready"
        cols="12"
      >
        <RealignWords
          :project-name="projectName"
          @words-realigned="getKaraokeData"
        ></RealignWords>
      </v-col>
      <v-col
        v-if="projectName && projectData.video_accompaniment_mp4 && projectData.alignment_correction === false && projectData.realignment_ready"
        cols="12"
      >
        <KaraokeResult
          version="realigned"
          :project-name="projectName"
          :project-data="projectData"
          @correct-alignment="getKaraokeData"
        ></KaraokeResult>
      </v-col>

    </v-row>
  </v-container>
</template>

<script>
import NewOrExistingKaraoke from "@/components/NewOrExistingKaraoke.vue";
import NewKaraoke from "@/components/NewKaraoke.vue";
import OpenKaraoke from "@/components/OpenKaraoke.vue";
import WaveSurferExample from "@/components/WaveSurferExample.vue";
import WaveSurferExampleNative from "@/components/WaveSurferExampleNative.vue";
import {api} from "@/api.js"
import SelectVideo from "@/components/SelectVideo.vue";
import SelectLyrics from "@/components/SelectLyrics.vue";
import GenerateKaraoke from "@/components/GenerateKaraoke.vue";
import KaraokeResult from "@/components/KaraokeResult.vue";
import CorrectSegmentAlignment from "@/components/CorrectSegmentAlignment.vue";
import RealignWords from "@/components/RealignWords.vue";

export default {
  components: {
    RealignWords,
    KaraokeResult,
    CorrectSegmentAlignment,
    GenerateKaraoke,
    OpenKaraoke,
    SelectLyrics, SelectVideo, WaveSurferExampleNative, WaveSurferExample, NewOrExistingKaraoke, NewKaraoke},
  data: () => ({
    initialized: false,
    projectName: null,
    projectData: {},
    freshKaraokeAction: null,
    width: "1366px",
  }),
  async beforeMount() {
    try {
      const response = await api.get('/check-session')
      this.projectName = response.data.project_name
    } catch (error) {
      if (error.response && error.response.status === 403) {
        const response = await api.get('/create-session')
        this.projectName = response.data.project_name
      } else {
        console.error(error)
      }
    }
    if (this.projectName)
      await this.getKaraokeData()
    this.initialized = true
  },
  computed: {
    freshKaraoke() {
      return !this.projectName
    }
  },
  methods: {
    async closeKaraoke(projectName) {
      this.projectName = null
      this.projectData = {}
      await api.post("/close-karaoke")
    },
    async karaokeSelected(projectName) {
      this.projectName = projectName
      await this.getKaraokeData()
    },
    async getKaraokeData() {
      try {
        const response = await api.get(`/karaoke/${this.projectName}`)
        this.projectData = response.data
      } catch (error) {
        this.projectName = null
        this.projectData = {}
      }
    },
  }
}

</script>
