import { BrowserRouter, Routes, Route, NavLink, Link } from "react-router-dom";
import "./index.css";
import { HomePage } from "./pages/HomePage";
import { BrowsePage } from "./pages/BrowsePage";
import { ThemeSwitcher } from "./components/ThemeSwitcher";
import { LanguageSwitcher } from "./components/LanguageSwitcher";
import { useI18n } from "./i18n/context";
import styles from "./App.module.css";

export default function App() {
  const { t } = useI18n();

  return (
    <BrowserRouter>
      <div className={styles.app}>
        <header className={styles.header}>
          <Link to="/" className={styles.brand}>Paper Scout</Link>
          <nav className={styles.nav}>
            <NavLink
              to="/"
              end
              className={({ isActive }) => isActive ? styles.navActive : styles.navLink}
            >
              {t("nav.search")}
            </NavLink>
            <NavLink
              to="/browse"
              className={({ isActive }) => isActive ? styles.navActive : styles.navLink}
            >
              {t("nav.browse")}
            </NavLink>
          </nav>
          <div className={styles.headerEnd}>
            <LanguageSwitcher />
            <ThemeSwitcher />
          </div>
        </header>
        <main className={styles.main}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/browse" element={<BrowsePage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
