import {createRouter, createWebHistory} from 'vue-router'
import CameraCV from "@/components/CameraCV";
import LocationTable from "@/components/LocationTable";
import MainStand from "@/components/StandApp/MainStand";
import EventsTable from "@/components/EventsTable";

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
        component: LocationTable,
        meta:{
            layout: "admin-layout"
        }
    },
    {
        path: '/events',
        name: 'events',
        component: EventsTable,
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