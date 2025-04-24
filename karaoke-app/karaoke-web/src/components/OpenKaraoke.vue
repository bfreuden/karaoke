
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
        Lequel ?
      </h2>
    </template>

    <template #text>
      <v-select
        v-model="projectName"
        :items="karaokes"
      ></v-select>
    </template>
    <template #actions>
      <v-spacer></v-spacer>
      <v-btn variant="flat" color="primary" @click="openKaraoke">
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
    projectName: null,
    karaokes: [],
  }),
  async beforeMount() {
    const response = await api.get('/karaokes')
    this.karaokes = response.data.map(({project_name, artist, title}) => ({value :project_name, title: `${artist} - ${title}`}))
  },
  methods: {
    async openKaraoke() {
      await api.post(`/open-karaoke?project_name=${this.projectName}`)
      this.$emit('open-karaoke', this.projectName)
    }
  }
}
</script>
