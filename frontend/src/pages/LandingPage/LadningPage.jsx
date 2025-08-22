import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./LandingPage.css";
import Cookies from "js-cookie";
import companyData from "../../utils/companyData.json";

const LandingPage = () => {
  const navigate = useNavigate();
  const [selectedLanguage, setSelectedLanguage] = useState("");
  const [interviewLanguage, setInterviewLanguage] = useState("");
  const [position, setPosition] = useState("");
  const [company, setCompany] = useState("");
  const [selectedCompanyUrl, setSelectedCompanyUrl] = useState("");

  const programmingLanguages = ["JavaScript", "Python", "Java", "C++", "C#"];

  const interviewLanguages = ["English", "Georgian", "Polish"];

  const developmentPositions = [
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Software Engineer",
    "Senior Software Engineer",
    "Lead Developer",
    "DevOps Engineer",
    "Site Reliability Engineer (SRE)",
    "Data Scientist",
    "Data Engineer",
    "Machine Learning Engineer",
    "AI Engineer",
    "Mobile Developer (iOS)",
    "Mobile Developer (Android)",
    "React Developer",
    "Vue.js Developer",
    "Angular Developer",
    "Node.js Developer",
    "Python Developer",
    "Java Developer",
    "C# Developer",
    ".NET Developer",
    "PHP Developer",
    "Ruby Developer",
    "Go Developer",
    "Rust Developer",
    "Systems Engineer",
    "Cloud Engineer",
    "Security Engineer",
    "QA Engineer",
    "Test Automation Engineer",
    "UI/UX Developer",
    "Game Developer",
    "Embedded Systems Engineer",
    "Blockchain Developer",
    "Technical Lead",
    "Architecture Engineer",
    "Database Administrator",
    "Database Developer",
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = {
      selectedLanguage,
      interviewLanguage,
      position,
      selectedCompanyUrl,
    };
    // Save to cookies
    Cookies.set("userForm", JSON.stringify(formData), { expires: 7 });
    console.log(formData, "aaaaaaaaaaaaaaa");
    // Send to backend
    const res = await fetch("http://localhost:8000/api/submitForm", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify(formData),
    });

    const data = await res.json();
    console.log("Response from backend:", data);

    if (res.ok && data.message === "Data stored") {
      // Navigate to HomePage on success
      navigate("/interview");
    } else {
      console.error("Submission failed:", data.message);
      // You can add error handling here (show error message to user)
    }
  };

  return (
    <div className="landing-page">
      <div className="landing-container">
        <header className="landing-header">
          <h1>Interview Preparation Assistant</h1>
          <p>Get ready for your technical interview with AI-powered practice</p>
        </header>

        <form className="landing-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="language-select">Programming Language *</label>
            <select
              id="language-select"
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              required
              className="form-select"
            >
              <option value="">Select a programming language</option>
              {programmingLanguages.map((lang) => (
                <option key={lang} value={lang}>
                  {lang}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="interview-language">Interview Language *</label>
            <select
              id="interview-language"
              value={interviewLanguage}
              onChange={(e) => setInterviewLanguage(e.target.value)}
              required
              className="form-select"
            >
              <option value="">Select interview language</option>
              {interviewLanguages.map((lang) => (
                <option key={lang} value={lang}>
                  {lang}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="position">Position/Role *</label>
            <select
              id="position"
              value={position}
              onChange={(e) => setPosition(e.target.value)}
              required
              className="form-select"
            >
              <option value="">Select a position/role</option>
              {developmentPositions.map((pos) => (
                <option key={pos} value={pos}>
                  {pos}
                </option>
              ))}
            </select>
          </div>

          {position && (
            <div className="form-group">
              <label>Select Company (Optional)</label>
              <div className="company-scroll-container">
                <div className="company-scroll">
                  {companyData[position] ? (
                    companyData[position].map((company, index) => (
                      <div
                        key={index}
                        className={`company-logo ${
                          selectedCompanyUrl === company[1] ? "selected" : ""
                        }`}
                        onClick={() => {
                          setCompany(company[1]);
                          setSelectedCompanyUrl(company[1]);
                        }}
                        title={company[1]}
                      >
                        <img
                          src={company[0]}
                          alt="Company logo"
                          onError={(e) => {
                            e.target.style.display = "none";
                          }}
                        />
                      </div>
                    ))
                  ) : (
                    <div className="no-companies">
                      <p>No companies available for this position</p>
                    </div>
                  )}
                </div>
              </div>
              {selectedCompanyUrl && (
                <div className="selected-company">
                  <p>
                    Selected:{" "}
                    <a
                      href={selectedCompanyUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {selectedCompanyUrl}
                    </a>
                  </p>
                </div>
              )}
            </div>
          )}

          <button type="submit" className="submit-btn">
            Start Interview Practice
          </button>
        </form>
      </div>
    </div>
  );
};

export default LandingPage;
