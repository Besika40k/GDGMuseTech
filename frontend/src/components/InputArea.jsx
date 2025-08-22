import { FaFileUpload } from "react-icons/fa";
import "./InputArea.css";
import { useContext } from "react";
import { LanguageContext } from "../contexts/languageContext";

const InputArea = ({ message, setMessage, handleFileUpload }) => {
  const { language, setLanguage } = useContext(LanguageContext);
  const input_message = {
    English: "Enter your answer here",
    Georgian: "შეიყვანეთ თქვენი პასუხი აქ",
    Russian: "Введите ваш ответ здесь",
  };

  return (
    <div className="input-area">
      <div className="input-container">
        <label htmlFor="pdf-upload" className="upload-button">
          <svg
            width="30"
            height="30"
            viewBox="0 0 48 48"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <g clipPath="url(#clip0_3_449)">
              <path
                d="M32 32L24 24M24 24L16 32M24 24V42M40.78 36.78C42.7307 35.7166 44.2716 34.0338 45.1597 31.9973C46.0478 29.9608 46.2324 27.6865 45.6844 25.5334C45.1364 23.3803 43.887 21.4711 42.1333 20.1069C40.3797 18.7428 38.2217 18.0015 36 18H33.48C32.8746 15.6585 31.7463 13.4847 30.1799 11.642C28.6135 9.79933 26.6497 8.33573 24.4362 7.36124C22.2227 6.38676 19.8171 5.92675 17.4002 6.01579C14.9833 6.10484 12.6181 6.74063 10.4823 7.87536C8.34655 9.01009 6.4958 10.6142 5.06923 12.5672C3.64265 14.5202 2.67736 16.7711 2.24594 19.1508C1.81452 21.5305 1.92819 23.9771 2.57841 26.3065C3.22862 28.636 4.39847 30.7878 5.99998 32.6"
                stroke="currentColor"
                strokeWidth="4"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </g>
            <defs>
              <clipPath id="clip0_3_449">
                <rect width="48" height="48" fill="white" />
              </clipPath>
            </defs>
          </svg>
        </label>

        <input
          id="pdf-upload"
          type="file"
          accept=".pdf"
          onChange={handleFileUpload}
          style={{ display: "none" }}
        />

        <textarea
          className="text-input"
          placeholder={input_message[language]}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
      </div>
    </div>
  );
};

export default InputArea;
