<template>
  <video :src="videoUrl" id="the-video" controls width="1024" height="768"></video>
</template>

<script>
import ASS from "ass-html5";

export default {
  props: ["videoUrl", "subtitlesUrl"],
  async mounted() {
    const res = await fetch(this.subtitlesUrl);
    let assSubs = await res.text();
    const ass = new ASS({
      assText: assSubs,
      video: document.getElementById('the-video')
    });
    await ass.render();
  }

}

</script>


