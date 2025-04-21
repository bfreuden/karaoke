
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
      <v-select
        v-model="language"
        :items="languages"
      ></v-select>
    </template>

    <template #actions>
      <v-spacer></v-spacer>
      <v-btn
        v-if="lyrics"
        variant="flat"
        color="primary"
        @click="saveLyrics"
        :disabled="!lyrics || !language"
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
    language: null,
    languages: [],
  }),
  async mounted() {
    await this.getSupportedLanguages()
    this.guessLyricsLanguageDebounced = debounce(this.guessLyricsLanguage, 500)
    this.getGeniusLyricsDebounced = debounce(this.getGeniusLyrics, 500)
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
        this.getGeniusLyricsDebounced()
    },
    lyrics(value) {
      if (value)
        this.guessLyricsLanguageDebounced()
    }
  },
  methods: {
    async getSupportedLanguages() {
      const response = await api.get(`/languages`)
      const translations = {
        "en": "Anglais",
        "fr": "Français",
        "ja": "Japonais (rōmaji)",
      }
      this.languages = response.data.map(it => ({value: it, title: translations[it]}) )
    },
    async guessLyricsLanguage() {
      const response = await api.post(`/_guess_language`, this.lyrics, {
          headers: {
            'Content-Type': 'text/plain'
          }
        }
      )
      this.language = response.data.language
    },
    async getGeniusLyrics() {
      const response = await api.post("/get-genius-lyrics",{url: this.geniusURL})
      this.lyrics = response.data.lyrics;
    },
    async saveLyrics() {
      const data = {genius_url: this.geniusURL, lyrics: this.lyrics, language: this.language}
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
