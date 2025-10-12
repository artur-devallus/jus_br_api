import {RouterProvider} from 'react-router-dom';
import {router} from "./routes/router.tsx";
import {AuthProvider} from "./providers/auth/AuthProvider.tsx";
import {Toaster} from "sonner";

const App = () => {
  return (
    <AuthProvider>
      <RouterProvider router={router}/>
      <Toaster richColors position="bottom-center"/>
    </AuthProvider>
  );
};

export default App;
