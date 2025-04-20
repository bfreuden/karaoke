
<template>
<!--  image="https://cdn.vuetifyjs.com/docs/images/one/create/feature.png"-->
  <div>

  </div>
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
        Créer un nouveau karaoké ou sélectionner un karaoké existant
      </h2>
    </template>

    <template #text>
    </template>

    <template #actions>
      <v-spacer></v-spacer>
      <v-btn variant="flat" color="primary" @click="$emit('new-karaoke')">
        Créer
      </v-btn>
      <v-btn variant="flat" color="primary" @click="$emit('existing-karaoke')">
        Sélectionner
      </v-btn>
      <v-spacer></v-spacer>
    </template>
  </v-card>

</template>

