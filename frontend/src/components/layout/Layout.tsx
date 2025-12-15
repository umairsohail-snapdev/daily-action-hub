import { Outlet } from "react-router-dom";
import { Header } from "./Header";

export function Layout() {
  return (
    <div className="h-screen w-screen flex flex-col bg-background text-foreground">
      <Header />
      <main className="flex-grow overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}