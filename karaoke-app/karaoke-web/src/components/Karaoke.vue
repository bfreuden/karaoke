<template>
  <v-container class="fill-height" width="900" max-width="900" >

    <v-row v-if="initialized">
      <v-col
        v-if="freshKaraoke && freshKaraokeAction === null"
        cols="12"
        style="width: 900px"
      >
<!--        <WaveSurferExampleNative></WaveSurferExampleNative>-->
        <NewOrExistingKaraoke
          @new-karaoke="freshKaraokeAction = 'create'"
        ></NewOrExistingKaraoke>
      </v-col>
      <v-col
        v-if="freshKaraoke && freshKaraokeAction === 'create'"
        cols="12"
      >
        <NewKaraoke
          @karaoke-created="karaokeCreated"
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
        v-if="projectName && projectData.youtube_url && !projectData.lyrics"
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
        v-if="projectName && projectData.lyrics && !projectData.video"
        cols="12"
      >
        <CreateKaraoke
          :project-name="projectName"
        ></CreateKaraoke>
      </v-col>

    </v-row>
  </v-container>
</template>

<script>
import NewOrExistingKaraoke from "@/components/NewOrExistingKaraoke.vue";
import NewKaraoke from "@/components/NewKaraoke.vue";
import WaveSurferExample from "@/components/WaveSurferExample.vue";
import WaveSurferExampleNative from "@/components/WaveSurferExampleNative.vue";
import {api} from "@/api.js"
import SelectVideo from "@/components/SelectVideo.vue";
import SelectLyrics from "@/components/SelectLyrics.vue";
import CreateKaraoke from "@/components/CreateKaraoke.vue";

export default {
  components: {
    CreateKaraoke,
    SelectLyrics, SelectVideo, WaveSurferExampleNative, WaveSurferExample, NewOrExistingKaraoke, NewKaraoke},
  data: () => ({
    initialized: false,
    projectName: null,
    projectData: {},
    freshKaraokeAction: null,
  }),
  async beforeMount() {
    try {
      const response = await api.get('/check-session')
      this.projectName = response.data.project_name
    } catch (error) {
      if (error.response.status === 403) {
        const response = await api.get('/create-session')
        this.projectName = response.data.project_name
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
    async karaokeCreated(projectName) {
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
