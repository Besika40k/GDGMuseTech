import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./LandingPage.css";
import Cookies from "js-cookie";

const LandingPage = () => {
  const navigate = useNavigate();
  const [selectedLanguage, setSelectedLanguage] = useState("");
  const [interviewLanguage, setInterviewLanguage] = useState("");
  const [position, setPosition] = useState("");
  const [company, setCompany] = useState("");

  const programmingLanguages = ["JavaScript", "Python", "Java", "C++", "C#"];

  const interviewLanguages = ["English", "Georgian", "Polish"];

  //   const handleSubmit = (e) => {
  //     e.preventDefault();
  //     console.log("Form submitted:", {
  //       selectedLanguage,
  //       interviewLanguage,
  //       position,
  //       company,
  //     });
  //     // Handle form submission logic here
  //   };
  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = {
      selectedLanguage,
      interviewLanguage,
      position,
      company,
    };
    // Save to cookies
    Cookies.set("userForm", JSON.stringify(formData), { expires: 7 });

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
            <input
              type="text"
              id="position"
              value={position}
              onChange={(e) => setPosition(e.target.value)}
              placeholder="e.g., Frontend Developer, Data Scientist, DevOps Engineer"
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="company">Company (Optional)</label>
            <input
              type="text"
              id="company"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g., Google, Microsoft, Startup XYZ"
              className="form-input"
            />
          </div>

          <button type="submit" className="submit-btn">
            Start Interview Practice
          </button>
        </form>
      </div>
    </div>
  );
};

export default LandingPage;
