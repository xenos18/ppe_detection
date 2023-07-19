import {createRouter, createWebHistory} from 'vue-router'
import CameraCV from "@/components/CameraCV";
import TableJournal from "@/components/TableJournal";
import MainStand from "@/components/StandApp/MainStand";

const routes = [
    {
        path: '/',
        name: 'app',
        component: MainStand,
    },
    {
        path: '/application',
        name: 'camera',
        component: CameraCV,
        meta: {
            layout: "admin-layout"
        }
    },
    {
        path: '/table',
        name: 'table',
        component: TableJournal,
        meta:{
            layout: "admin-layout"
        }
    }
]
const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})
export default router