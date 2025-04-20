
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
        Copier le lien d'une vidéo <a href="https://www.youtube.com/" target="_blank">YouTube</a>
      </h2>
    </template>

    <template #text>

      <v-text-field
        variant="solo-inverted"
        v-model="youTubeURL"
      ></v-text-field>
      <div
        v-if="embeddedYouTubeURL"
        class="center"
      >
        <iframe width="560" height="315" :src="embeddedYouTubeURL" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
      </div>
    </template>
    <template #actions>
      <v-spacer></v-spacer>
      <v-btn
        v-if="embeddedYouTubeURL"
        variant="flat"
        color="primary"
        @click="saveYoutubeURL"
      >
        C'est bien celle-là !
      </v-btn>
      <v-spacer></v-spacer>
    </template>

  </v-card>

</template>

<script>

import {api} from "@/api.js"

export default {
  props: ['projectName'],
  data:() => ({
    youTubeURL: "",
  }),
  computed: {
    embeddedYouTubeURL() {
      if (!this.youTubeURL)
        return null;
      let marker = "watch?v=";
      const markerIndex = this.youTubeURL.indexOf(marker)
      if (markerIndex === -1)
        return null
      return `https://www.youtube.com/embed/${this.youTubeURL.substring(markerIndex + marker.length)}`;
    }
  },
  methods: {
    async saveYoutubeURL() {
      await api.patch(`/karaoke/${this.projectName}`, {youtube_url: this.youTubeURL})
      this.$emit("video-selected");
    }
  }
}
</script>

<style scoped>
.center {
  text-align: center;
}
</style>
