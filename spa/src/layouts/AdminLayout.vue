<template>
  <layout-slider/>
  <main class="main-wrapper">
    <MainHeader/>
    <slot/>
  </main>
</template>

<script>
import MainHeader from "@/components/MainHeader";
import LayoutSlider from "@/components/LayoutSlider";

export default {
  name: "AdminLayout",
   components: {
    MainHeader,
    LayoutSlider,

  },
}
</script>

<style scoped>

</style>