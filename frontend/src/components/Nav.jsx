import "./NavStyle.css";
import { useEffect, useState } from "react";
import { FaMoon, FaSun, FaUser } from "react-icons/fa";

const Nav = () => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const stored =
      typeof window !== "undefined" ? localStorage.getItem("theme") : null;
    if (stored === "dark") return true;
    if (stored === "light") return false;
    // Fallback to prefers-color-scheme
    if (typeof window !== "undefined" && window.matchMedia) {
      return window.matchMedia("(prefers-color-scheme: dark)").matches;
    }
    return false;
  });

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  useEffect(() => {
    const theme = isDarkMode ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [isDarkMode]);

  return (
    <nav className="navbar">
      <div className="logo">
        {/* Replace with your logo */}
        <span>MuseTech</span>
      </div>

      <div className="right-section">
        <button className="icon-button" onClick={toggleDarkMode}>
          {isDarkMode ? <FaSun size={20} /> : <FaMoon size={20} />}
        </button>
        <button className="icon-button">
          <FaUser size={20} />
        </button>
      </div>
    </nav>
  );
};

export default Nav;
