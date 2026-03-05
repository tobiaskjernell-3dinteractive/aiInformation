import { BrowserRouter, Route, Routes } from "react-router"
import HomePage from "./pages/HomePage"
import AppLayout from "./components/AppLayout"
import Unity from "./pages/Unity"

function App() {

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path='/unity' element={<Unity />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
