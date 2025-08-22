import { createContext, useState } from "react";

// 1. Create the context
export const LanguageContext = createContext();

// 2. Create the provider component
export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState("English"); // Default language is English

  return (
    <LanguageContext.Provider value={{ language, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};
