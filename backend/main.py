from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import openai
from typing import Optional
import json
from pypdf import PdfReader
app = FastAPI()

# Configure CORS with exact frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5173/",  # Include both with and without trailing slash
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5173/",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8000/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



client = openai.OpenAI(
    api_key="sk-ENIRLVIVfmBfzXtVfOQhVw",
    base_url="https://api.ailab.ge"
)

latest_ai_response = {"message": "No response yet"}

@app.get("/api/response")
async def get_ai_response():
    print(latest_ai_response)
    return latest_ai_response

@app.post("/api/submit")
async def handle_submission(
    pdf: Optional[UploadFile] = File(None),
    text: str = Form(...),
    categories: str = Form(...)
):
    try:
        # Parse JSON categories
        categories_dict = json.loads(categories)

        # Log received data
        print("Received request")
        print(f"Text: {text}")
        print(f"PDF: {pdf.filename if pdf else 'No PDF'}")
        print(f"Categories: {categories_dict}")
        print(categories_dict)
        # Decompose Dict data
        dashlili = ""
        for i in categories_dict.items():
            if i[0] != i[1]:
                dashlili += f"{i[0]}: {i[1]}\n"
        
        # Read PDF file
        if pdf:
            reader = PdfReader(pdf.file)
            number_of_pages = len(reader.pages)
            page = reader.pages[0]
            pdf_text = page.extract_text()
            for i in range(number_of_pages):
                if len(pdf_text) > 10000:
                    break
                page = reader.pages[i]
                pdf_text += page.extract_text()
        else:
            pdf_text = ""
        # Send user input to AI model
        response = client.chat.completions.create(
            model="kona",
            messages=[
                {"role": "user", "content": f"დაამუშავე შემდეგი მოთხოვნა:\n\ტექსტი: {text}\n კატეგორიები: {dashlili} ამ pdf ის ტექსტის გათვალისწინებით: {pdf_text}"}
            ]
        )
        # Store AI response globally
        latest_ai_response = {"message": response.choices[0].message.content} 
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