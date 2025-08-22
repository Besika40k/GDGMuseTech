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
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

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


client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
)

latest_ai_response = {"message": "No response yet"}

@app.post("/api/submitForm")
async def submit_form(data: dict, response: Response):
    # Save to cookie
    response.set_cookie(
        key="userForm",
        value=str(data),  # could JSON.stringify but keep short here
        httponly=False,   # allow frontend to read it too if needed
        max_age=60*60*24*7
    )
    return {"message": "Data stored", "data": data}

@app.get("/context")
async def get_context(request: Request):
    user_data = request.cookies.get("userForm")
    if user_data:
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
        user_data = request.cookies.get("userForm")  # stored cookie
        print("Cookieaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa data:", user_data)
    
        # Parse JSON categories
        categories_dict = json.loads(categories)

        # Log received data
        print("Received request")
        print(f"Text: {text}")
        print(f"PDF: {pdf.filename if pdf else 'No PDF'}")
        print(f"Categories: {categories_dict}")
        # Decompose Dict data
        dashlili = ""
        for i in categories_dict.items():
            if i[0] != i[1]:
                dashlili += f"{i[0]}: {i[1]}\n"
        if dashlili != "":
            dashlili = f"დამატებითი ინფორმაცია: {dashlili}"
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

        if not OPENAI_API_KEY:
            return JSONResponse(content={"status": "error", "message": "OPENAI_API_KEY is not set"}, status_code=400)
        # Send user input to AI model
    
        # response = client.responses.create(
        #     model="gpt-4o-mini",
        #     input= f"do something man",
        #     store=True,
        # )
        # დაამუშავე შემდეგი მოთხოვნა:\n\ტექსტი: {text}\n {dashlili} {pdf_text}
        # Store AI response globally
        global latest_ai_response
        # latest_ai_response = {"message": response.choices[0].message.content} 
        latest_ai_response = {"message": "some text"} 
        return {"status": "success", "message": latest_ai_response}

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=400)
    


# Add this to test if server is running
# @app.get("/")
# async def root():
#     return {"message": "Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)