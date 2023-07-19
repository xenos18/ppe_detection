<template>
   <component :is="layout">
          <router-view/>
    </component>
</template>

<script>


export default {
  name: 'App',
  computed: {
    //Это самое вычисляемое свойство
    layout() {
      //Вернем имя шаблона из роута или дефолтное значение
      //(шаблон для страниц, для которых мы не указали шаблон)
      return this.$route.meta.layout || "default-layout"
    }
  }
}
</script>

<style>
@import "@/assets/css/main.css";
@import "@/assets/css/lineicons.css";
@import "@/assets/css/materialdesignicons.min.css";
@import "@/assets/css/bootstrap.min.css";

</style>
