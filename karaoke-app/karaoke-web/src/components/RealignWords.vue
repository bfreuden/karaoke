
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
        Réalignement des mots en cours...
      </h2>
    </template>

    <template #text>
      <div>{{ message }}</div>
      <v-progress-linear v-model="step" :max="steps"></v-progress-linear>
    </template>
    <template #actions>
      <v-spacer></v-spacer>
      <v-spacer></v-spacer>
    </template>

  </v-card>

</template>

<script>

import {api} from "@/api.js"

export default {
  props: ['projectName'],
  data: () => ({
    steps: 0,
    step: 0,
    message: "",
  }),
  mounted() {
    const socket = new WebSocket(`ws://${window.location.host}/ws/realign`);
    const self = this
    socket.addEventListener("message", (event) => {
      console.log("Message from server ", event.data);
      const notification = JSON.parse(event.data);
      if (!notification.ping) {
        self.step = notification.step
        self.steps = notification.steps
        self.message = notification.message
        if (self.steps !== 0 && self.step === self.steps) {
          console.log("closing websocket");
          socket.close()
          const data = { realignment_ready: true}
          api.patch(`/karaoke/${this.projectName}`, data).then(res => {
            this.$emit("words-realigned")
          })
        }
      }
    });
    socket.addEventListener("open", (event) => {
      console.log("websocket open");
      api.post(`/karaoke/${this.projectName}/_realign`)
    });
  },
}
</script>

