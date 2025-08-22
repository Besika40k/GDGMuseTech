import React from "react";
import Nav from "./Nav";
import "./Layout.css";
const Layout = ({ children }) => {
  return (
    <div className="layout">
      <Nav />
      <main className="main-content">{children}</main>
    </div>
  );
};

export default Layout;
