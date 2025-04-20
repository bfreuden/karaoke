
<template>
<!--  image="https://cdn.vuetifyjs.com/docs/images/one/create/feature.png"-->
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
        Copier le lien <a href="https://genius.com/" target="_blank">Genius</a> des paroles (ou directement les paroles)
      </h2>
    </template>

    <template #text>

      <v-text-field
        variant="solo-inverted"
        v-model="geniusURL"
      ></v-text-field>
      <v-textarea
        variant="solo-inverted"
        v-model="lyrics"
      ></v-textarea>
    </template>

    <template #actions>
      <v-spacer></v-spacer>
      <v-btn
        v-if="lyrics"
        variant="flat"
        color="primary"
        @click="saveLyrics"
      >
        C'est bien ça !
      </v-btn>
      <v-spacer></v-spacer>
    </template>

  </v-card>

</template>

<script>

import {api} from "@/api.js"
import debounce from 'debounce';

export default {
  props: ['projectName', 'artist', 'title'],
  data:() => ({
    geniusURL: null,
    lyrics: null,
  }),
  async mounted() {
    this.getGeniusLyrics = debounce(this.getGeniusLyricsInternal, 500)
    try {
      const response = await api.post("/search-genius-lyrics",{artist: this.artist, title: this.title})
      this.geniusURL = response.data.url
    } catch (error) {
      console.log(error)
    }
  },
  watch: {
    geniusURL(value) {
      if (value)
        this.getGeniusLyrics()
    }
  },
  methods: {
    async getGeniusLyricsInternal() {
      const response = await api.post("/get-genius-lyrics",{url: this.geniusURL})
      this.lyrics = response.data.lyrics;
    },
    async saveLyrics() {
      const data = {genius_url: this.geniusURL, lyrics: this.lyrics}
      await api.patch(`/karaoke/${this.projectName}`, data)
      this.$emit("lyrics-selected");
    }
  }
}
</script>

<style scoped>
.center {
  text-align: center;
}
</style>
