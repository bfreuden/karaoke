
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
        C'est parti !
      </h2>
    </template>

    <template #text>

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
  mounted() {
    const socket = new WebSocket(`ws://${window.location.host}/ws/create`);

    socket.addEventListener("message", (event) => {
      console.log("Message from server ", event.data);
    });
    socket.addEventListener("open", (event) => {
      console.log("websocket open");
      api.post(`/karaoke/${this.projectName}/_generate`)
    });
    setTimeout(() => {
      socket.close();
    }, 5)
  },
}
</script>

