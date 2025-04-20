
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
        On chante quoi ?
      </h2>
    </template>

    <template #text>
      <v-row class="mt-5">
        <v-col cols="6">
          <v-text-field
            variant="solo-inverted"
            label="Artiste"
            v-model="artist"
          ></v-text-field>
        </v-col>
        <v-col cols="6">
          <v-text-field
            variant="solo-inverted"
            label="Titre"
            v-model="title"
          ></v-text-field>
        </v-col>
      </v-row>
    </template>
    <template #actions>
      <v-spacer></v-spacer>
      <v-btn variant="flat" color="primary" @click="createKaraoke">
        C'est parti
      </v-btn>
      <v-spacer></v-spacer>
    </template>
  </v-card>

</template>

<script>
import {api} from '@/api'
export default {
  data: () => ({
    artist: "",
    title: "",
  }),
  methods: {
    async createKaraoke() {
      const response = await api.post('/create-karaoke', {artist: this.artist, title: this.title})
      const projectName = response.data.project_name
      this.$emit('karaoke-created', projectName)
    }
  }
}
</script>
