from fastapi import FastAPI, File, Form, UploadFile, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import openai
from typing import Optional
import json
from pypdf import PdfReader
import os
from dotenv import load_dotenv, find_dotenv
from typing import Union

load_dotenv(find_dotenv())
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

app = FastAPI()

# Configure CORS with exact frontend URL
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",
#         "http://localhost:5173/",
#         "http://127.0.0.1:62655",
#         "http://127.0.0.1:62655/",
#         "http://0.0.0.0:8000",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# OpenAI client configuration for Gemini
client = openai.OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta"
)

latest_ai_response = {"message": "No response yet"}

# Store conversation history for each user session
conversation_history = {}

@app.post("/api/submitForm")
async def submit_form(data: dict, response: Response):
    # Log the received data for debugging
    print("Received form data:", data)
    print("Cookiaaaaae data being stored:", data)
    
    # Validate the expected fields
    expected_fields = ["selectedLanguage", "interviewLanguage", "position", "selectedCompanyUrl"]
    received_fields = list(data.keys())
    
    print(f"Expected fields: {expected_fields}")
    print(f"Received fields: {received_fields}")
    
    # Save to cookie with proper JSON serialization
    response.set_cookie(
        key="userForm",
        value=json.dumps(data),  # Use proper JSON serialization
        httponly=False,   # allow frontend to read it too if needed
        max_age=60*60*24*7
    )
    
    return {"message": "Data stored", "data": data}

@app.get("/context")
async def get_context(request: Request):
    user_data = request.cookies.get("userForm")
    if user_data:
        try:
            # Parse the JSON data from cookie
            parsed_data = json.loads(user_data)
            return {"context": parsed_data}
        except json.JSONDecodeError:
            # Fallback for old format
            return {"context": user_data}
    return {"context": "No data stored"}


@app.get("/api/response")
async def get_ai_response():
    return latest_ai_response

@app.post("/api/submit")
async def handle_submission(
    request: Request,  # add this
    text: str = Form(...),
    categories: str = Form(...),
    pdf: Union[UploadFile, None] = File(default=None),
):
    try:
        user_data_raw = request.cookies.get("userForm")  # stored cookie
        print("Cookie data:", user_data_raw)
        
        # Parse user data from cookie
        user_data = {}
        if user_data_raw:
            try:
                user_data = json.loads(user_data_raw)
            except json.JSONDecodeError:
                print("Failed to parse user data from cookie")
                user_data = {}
    
        # Parse JSON categories
        categories_dict = json.loads(categories)

        # Log received data
        print("Received request")
        print(f"Text: {text}")
        print(f"PDF: {pdf.filename if pdf else 'No PDF'}")
        print(f"Categories: {categories_dict}")
        
        # Create a unique session ID based on user data
        session_id = f"{user_data.get('selectedLanguage', 'unknown')}_{user_data.get('position', 'unknown')}_{user_data.get('selectedCompanyUrl', 'unknown')}"
        
        # Initialize conversation history for this session if it doesn't exist
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Add user's response to history
        conversation_history[session_id].append({
            "role": "user",
            "content": text,
            "timestamp": "now"
        })
        
        # Read PDF file (robust against None text)
        if pdf:
            try:
                reader = PdfReader(pdf.file)
                number_of_pages = len(reader.pages)
                pdf_text = ""
                for i in range(number_of_pages):
                    if len(pdf_text) > 10000:
                        break
                    page = reader.pages[i]
                    page_text = page.extract_text() or ""
                    pdf_text += page_text
                if pdf_text:
                    pdf_text = f"ამ pdf ის ტექსტის გათვალისწინებით: {pdf_text}"
            except Exception as pdf_err:
                print(f"PDF parsing error: {str(pdf_err)}")
                pdf_text = ""
        else:
            pdf_text = ""

        if not GEMINI_API_KEY:
            return JSONResponse(content={"status": "error", "message": "GEMINI_API_KEY is not set"}, status_code=400)
        
        # Build conversation history for context
        history_context = ""
        if len(conversation_history[session_id]) > 1:
            history_context = "\n\nPrevious conversation:\n"
            for i, msg in enumerate(conversation_history[session_id][:-1]):  # Exclude the current message
                if msg["role"] == "user":
                    history_context += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    history_context += f"Assistant: {msg['content']}\n"
        
        # Prepare the prompt for Gemini
        prompt = f"""You are an AI interview coach. Generate ONE specific interview question based on the context provided.

User Context:
- Programming Language: {user_data.get('selectedLanguage', 'Not specified') if user_data else 'Not specified'}
- Interview Language: {user_data.get('interviewLanguage', 'Not specified') if user_data else 'Not specified'}
- Position: {user_data.get('position', 'Not specified') if user_data else 'Not specified'}
- Company: {user_data.get('selectedCompanyUrl', 'Not specified') if user_data else 'Not specified'}

Current User Input: {text}

{history_context}

PDF Content: {pdf_text}

Instructions:
1. Generate ONLY ONE specific interview question
2. Make it relevant to the programming language and position
3. Consider the conversation history to avoid repetition
4. Make the question challenging but appropriate for the level
5. Focus on technical skills, problem-solving, or behavioral aspects
6. don't return anything other than the interview question
Generate your response in this format:
Question: [Your single question here]

Additional Context: [Brief explanation or hint if needed]"""
        
        try:
            # Use OpenAI SDK to call Gemini
            response = client.chat.completions.create(
                model="models/gemini-2.0-flash",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            # Extract the response content
            ai_content = response.choices[0].message.content
            
            # Add AI response to conversation history
            conversation_history[session_id].append({
                "role": "assistant",
                "content": ai_content,
                "timestamp": "now"
            })
            
            # Store AI response globally
            global latest_ai_response
            latest_ai_response = {"message": ai_content}
            
            print("Cookiaaaaae data:", user_data)
            print(f"Conversation history for session {session_id}: {len(conversation_history[session_id])} messages")
            return {"status": "success", "message": latest_ai_response}
            
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            return JSONResponse(content={"status": "error", "message": f"Gemini API error: {str(e)}"}, status_code=500)

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=400)
    


# Add this to test if server is running
@app.get("/")
async def root():
    return {"message": "Server is running", "status": "healthy"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Backend API is running"}

@app.get("/api/conversation-history")
async def get_conversation_history():
    return {"conversation_history": conversation_history}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)