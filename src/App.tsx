import { BrowserRouter, Route, Routes } from "react-router"
import HomePage from "./pages/HomePage"
import AppLayout from "./components/AppLayout"

function App() {

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<HomePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
