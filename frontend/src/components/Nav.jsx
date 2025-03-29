import './NavStyle.css';
import { useState } from 'react';
import { FaMoon, FaSun, FaUser } from 'react-icons/fa';

const Nav = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <nav className="navbar">
      <div className="logo">
        {/* Replace with your logo */}
        <span>MuseTech</span>
      </div>
      
      <div className="right-section">
        <button 
          className="icon-button"
          onClick={toggleDarkMode}
        >
          {isDarkMode ? <FaSun size={20} /> : <FaMoon size={20} />}
        </button>
        
        <button 
          className="icon-button"
        >
          <FaUser size={20} />
        </button>
      </div>
    </nav>
  );
};

export default Nav;