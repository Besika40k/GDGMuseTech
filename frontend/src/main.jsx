import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";
import Layout from "./components/Layout.jsx";
import LandingPage from "./pages/LandingPage/LadningPage.jsx";
import HomePage from "./pages/HomePage.jsx";
import { LanguageProvider } from "./contexts/languageContext.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <LanguageProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/interview" element={<HomePage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </LanguageProvider>
  </StrictMode>
);
