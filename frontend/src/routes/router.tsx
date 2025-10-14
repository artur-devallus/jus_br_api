import {createBrowserRouter} from "react-router-dom";
import {NotLoggedRoute} from "./not-logged.route.tsx";
import LandingPage from "@/pages/landing-page";
import LoginPage from "@/pages/login-page";
import MaintenancePage from "@/pages/maintenance-page";
import NotFoundPage from "@/pages/not-found-page";
import Layout from "@/components/layout/layout";
import ConsultasPage from "@/pages/consultas-page.tsx";
import ImportFilePage from "@/pages/import-file-page.tsx";
import QueriesListPage from "@/pages/queries-list-page.tsx";


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
      {
        path: "import-file",
        element: <ImportFilePage/>
      },
      {
        path: "queries-list",
        element: <QueriesListPage/>
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