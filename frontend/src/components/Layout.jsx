import Header from "./Header.jsx";
import Sidebar from "./Sidebar.jsx";

export default function Layout({ children }) {
  return (
    <div className="app-shell">
      <Header />
      <div className="app-body">
        <Sidebar />
        <main className="page">{children}</main>
      </div>
    </div>
  );
}
