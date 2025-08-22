import { useState } from "react";
import Nav from "../components/Nav";
import "./HomePage.css";
import Categories from "../components/Categories";
import InputArea from "../components/InputArea";
import ReactMarkdown from "react-markdown";

import categoryOptions from "../utils/categoryOptions";

function HomePage() {
  // Declare states
  const [message, setMessage] = useState("");
  const [file, setFile] = useState(null);
  const [aiResponse, setAiResponse] = useState(
    "ხელოვნური ინტელექტის პასუხი მოვა აქ..."
  );
  const [categoryChoices, setCategoryChoices] = useState(
    categoryOptions.reduce((acc, category) => {
      acc[category.name] = category.options[0]; // Default to first option
      return acc;
    }, {})
  );

  const handleCategorySelect = (categoryName, selectedValue) => {
    setCategoryChoices((prev) => ({
      ...prev,
      [categoryName]: selectedValue,
    }));
  };

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile && uploadedFile.type === "HomePagelication/pdf") {
      setFile(uploadedFile);
    } else {
      alert("Please upload a PDF file");
    }
  };

  const handleChatSubmit = async () => {
    const formData = new FormData();

    if (file) formData.append("pdf", file);

    // Create JSON payload
    formData.append("text", message);
    formData.append("categories", JSON.stringify(categoryChoices));

    console.log("Sending data:", {
      pdf: file,
      text: message,
      categories: categoryChoices,
    });

    try {
      console.log("Sending data:", {
        pdf: file,
        text: message,
        categories: categoryChoices,
      });
      console.log("Sending request to: http://localhost:8000/api/submit");
      const response = await fetch("http://localhost:8000/api/submit", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      console.log("Raw response:", response);
      console.log("Response status:", response.status);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          `Submission failed: ${data.message || response.statusText}`
        );
      }
      console.log(data.message);
      console.log(data.message.message);
      console.log(typeof data.message.message);
      setAiResponse(data.message.message);
      console.log("Success:", data);
    } catch (error) {
      console.error("Detailed error:", error);
    }
  };

  return (
    <div className="HomePage">
      <div className="content-div">
        {/* <Categories
          categoryChoices={categoryChoices}
          onSelect={handleCategorySelect}
        /> */}

        <div className="main-content">
          <div className="output-container">
            <div className="output-text">
              <ReactMarkdown>{aiResponse}</ReactMarkdown>
            </div>
          </div>
          <div className="outer-input-container">
            <InputArea
              message={message}
              setMessage={setMessage}
              handleFileUpload={handleFileUpload}
            />
            <button className="submit-button" onClick={handleChatSubmit}>
              <svg
                style={{
                  minWidth: "20px",
                  minHeight: "20px",
                  flexShrink: 0,
                  maxWidth: "50px",
                  maxHeight: "50px",
                }}
                width="100"
                height="100"
                viewBox="0 0 68 68"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <g clipPath="url(#clip0_4_114)">
                  <path
                    d="M62.2106 34.5488L31.1053 33.8715M62.2106 34.5488L23.6357 52.098L31.1053 33.8715M62.2106 34.5488L24.4362 15.3372L31.1053 33.8715"
                    stroke="currentColor"
                    strokeWidth="4"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </g>
                <defs>
                  <clipPath id="clip0_4_114">
                    <rect
                      width="48"
                      height="48"
                      fill="white"
                      transform="translate(34.672) rotate(46.2474)"
                    />
                  </clipPath>
                </defs>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
