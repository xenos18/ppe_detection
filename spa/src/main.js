import {createApp} from 'vue'
import App from './App.vue'
import router from "@/router";

import AdminLayout from "@/layouts/AdminLayout";
import StandLayout from "@/layouts/StandLayout";

const app = createApp(App)
app.component('admin-layout', AdminLayout)
app.component('default-layout', StandLayout)
app.use(router)
app.mount('#app')
