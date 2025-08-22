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


terminationMessage = {
    "English": "Please wait, your answers are being processed.",
    "Georgian": "გთხოვთ, მოითმინოთ, თქვენი პასუხები მუშავდება.",
    "Russian": "Пожалуйста, подождите, ваши ответы обрабатываются."
}



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

global latest_ai_response
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

        if len(conversation_history[session_id]) >= 20:
            print("checkpoint")
            lang = user_data.get("interviewLanguage", "English").lower()
            message = terminationMessage.get(lang, terminationMessage["English"])
            latest_ai_response = {"message": message}
            return {"status": "success", "message": latest_ai_response}


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
the word "question" in {user_data.get('interviewLanguage', 'Not specified') if user_data else 'Not specified'} [the numer of question]: [Your single question here]
"""
        
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
            latest_ai_response = {"message": ai_content}

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



# ... (existing imports and FastAPI setup) ...

# This will store the final evaluation message for the front end to fetch.
final_evaluation_response = {"message": "Final evaluation not yet available."}

@app.get("/api/finalEvaluation")
async def get_final_evaluation(request: Request):
    """
    Evaluates the user's performance based on the conversation history
    and provides tips for improvement.
    """
    try:
        user_data_raw = request.cookies.get("userForm")
        if not user_data_raw:
            return JSONResponse(content={"status": "error", "message": "User data not found in cookie."}, status_code=400)
        
        user_data = json.loads(user_data_raw)
        session_id = f"{user_data.get('selectedLanguage', 'unknown')}_{user_data.get('position', 'unknown')}_{user_data.get('selectedCompanyUrl', 'unknown')}"
        
        # Check if conversation history exists for the session
        if session_id not in conversation_history or not conversation_history[session_id]:
            return JSONResponse(content={"status": "error", "message": "No conversation history found for this session."}, status_code=404)

        # Build the full conversation history string for the prompt
        full_history_prompt = "User and Assistant Conversation History:\n"
        for msg in conversation_history[session_id]:
            if msg["role"] == "user":
                full_history_prompt += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant":
                full_history_prompt += f"Assistant: {msg['content']}\n"
        
        # Define the prompt for the final evaluation
        final_prompt = f"""You are an experienced and senior interviewer. Your task is to provide a comprehensive evaluation of the user's performance in the mock interview.

Interview Context:
- Programming Language: {user_data.get('selectedLanguage', 'Not specified')}
- Position: {user_data.get('position', 'Not specified')}
- Company: {user_data.get('selectedCompanyUrl', 'Not specified')}

{full_history_prompt}

Instructions for Evaluation:
1.  **Evaluate Performance**: Provide a professional assessment of the user's strengths and weaknesses based on the entire conversation.
2.  **Provide Tips**: Offer actionable advice and tips on how the user can improve their answers, communication style, or technical knowledge.
3.  **Give Tricks**: Share "tricks" or advanced strategies for handling similar interview questions in the future.
4.  **Be Comprehensive**: Your response should be a well-structured text, not just a single sentence. Use markdown for formatting (e.g., headings, bullet points, bold text) to make it easy to read.
5.  **Language**: The evaluation must be in the interview language specified by the user: {user_data.get('interviewLanguage', 'English')}.
6.  **Do not ask any questions. Provide the evaluation and nothing else.**
"""
        
        # Call the Gemini API for the final evaluation
        final_response_from_gemini = client.chat.completions.create(
            model="models/gemini-2.0-flash",
            messages=[
                {
                    "role": "user",
                    "content": final_prompt
                }
            ],
            max_tokens=2000,
            temperature=0.7
        )

        ai_evaluation = final_response_from_gemini.choices[0].message.content
        
        # Update the global response variable to be fetched by the frontend
        global latest_ai_response
        latest_ai_response = {"message": ai_evaluation}
        
        # Clear the conversation history for the current session to start fresh
        del conversation_history[session_id]

        return {"status": "success", "message": {"message": ai_evaluation}}

    except Exception as e:
        print(f"Error during final evaluation: {str(e)}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)