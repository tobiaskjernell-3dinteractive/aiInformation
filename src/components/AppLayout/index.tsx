import { Outlet } from "react-router";
import NavigationBar from "../NavigationBar";

const AppLayout = () => {
    return (
        <div className="flex flex-col h-screen w-auto">
            <NavigationBar />
            <main className="flex-1 bg-zinc-800 flex pt-20 justify-center text-zinc-50">
                <Outlet />
            </main>
        </div>
    )
}

export default AppLayout;