import {createBrowserRouter} from "react-router-dom";
import {NotLoggedRoute} from "./not-logged.route.tsx";
import LandingPage from "@/pages/LandingPage.tsx";
import LoginPage from "@/pages/LoginPage.tsx";
import MaintenancePage from "@/pages/Maintenance.tsx";
import NotFoundPage from "@/pages/NotFoundPage.tsx";
import Layout from "@/components/layout/layout";
import ConsultasPage from "@/pages/ConsultasPage.tsx";


export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage/>,
  },
  {
    path: "/auth/login",
    element: <NotLoggedRoute element={<LoginPage/>}/>,
  },
  {
    path: "/app",
    element: <Layout/>, // layout com sidebar + outlet
    children: [
      {
        index: true,
        path: "",
        element: <ConsultasPage/>
      },
    ]
  },
  {
    path: "maintenance",
    element: <MaintenancePage/>,
  },
  {
    path: "*",
    element: <NotFoundPage/>,
  },
]);