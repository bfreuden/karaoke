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
        Voilà ce que ça donne
      </h2>
    </template>

    <template #text>
      <v-row class="mt-5">
        <v-col cols="4" class="my-0 py-0">
          <v-switch density="compact" color="primary" v-model="withVoice" label="Avec la voix"></v-switch>
        </v-col>
        <v-col cols="4" class="my-0 pt-3 pb-0">
          <a :href="withVoice ? projectData.lyrics_video_mp4 : projectData.karaoke_video_mp4" download>Télécharger la vidéo</a>
        </v-col>
        <v-col cols="3" class="my-0 pt-3 pb-0">
          <a :href="withVoice ? projectData.lyrics_subtitles_ass : projectData.karaoke_subtitles_ass" download>Télécharger les sous-titres</a>
        </v-col>
      </v-row>
      <v-row v-if="withVoice" class="mt-5">
        <v-col cols="12">
          <VideoWithSubtitles
            :video-url="projectData.video_mp4"
            :subtitles-url="projectData.subtitles_segments_ass"
          ></VideoWithSubtitles>
        </v-col>
      </v-row>
      <v-row v-else class="mt-5">
        <v-col cols="12">
          <VideoWithSubtitles
            :video-url="projectData.video_accompaniment_mp4"
            :subtitles-url="projectData.subtitles_segments_ass"
          ></VideoWithSubtitles>
        </v-col>
      </v-row>

    </template>
    <template #actions>
      <v-spacer></v-spacer>
      <v-btn variant="flat" color="primary" @click="correctAlignment">
        Corriger l'alignement des paroles
      </v-btn>
      <v-spacer></v-spacer>
    </template>
  </v-card>

</template>

<script>
import ASS from 'ass-html5'
import VideoWithSubtitles from "@/components/VideoWithSubtitles.vue";
import {api} from "@/api.js";
// import videojs from "video.js"

export default {
  components: {VideoWithSubtitles},
  props: ['projectName', 'projectData'],
  data: () => ({
    withVoice: false,
  }),
  methods: {
    async correctAlignment() {
      const data = {alignment_correction: true}
      await api.patch(`/karaoke/${this.projectName}`, data)
      this.$emit('correct-alignment');
    }
  }
}

</script>

