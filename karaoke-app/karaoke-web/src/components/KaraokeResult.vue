<template>
  <video :src="projectData.video_accompaniment_mp4" id="video" controls width="1024" height="768"></video>
<!--  <video id="my-video" class="video-js" controls preload="auto"width="640" height="264" data-setup='{}'>-->
<!--    <source :src="projectData.video_accompaniment_mp4" type="video/mp4" />-->
<!--  </video>-->
</template>

<script>
import ASS from 'ass-html5'
// import videojs from "video.js"

export default {
  props: ['projectData'],
  async mounted() {
    const res = await fetch(this.projectData.subtitles_segments_ass);
    // const res = await fetch(this.projectData.subtitles_segments_ass);
    let assSubs = await res.text();
    console.log(assSubs)
    const ass = new ASS({
      assText: assSubs,
      video: document.getElementById('video')
    });
    await ass.render();
    // document.addEventListener('DOMContentLoaded', async () => {
    //   const res = await fetch(this.projectData.subtitles_segments_ass);
    //   const assSubs = await res.text();
    //   const player = videojs('my-video');
    //
    //   player.ready(async () => {
    //     // Get the video element from the player
    //     const videoElement = player.el().getElementsByTagName('video')[0];
    //     const ass = new ASS.default({
    //       assText: assSubs,
    //       video: videoElement
    //     });
    //     await ass.render();
    //   });
    // });
  }
}

</script>

