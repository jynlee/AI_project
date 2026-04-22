# %%
# pip install fastapi uvicorn ollama openai python-multipart python-dotenv nest-asyncio

import os
import base64
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import nest_asyncio
from openai import OpenAI
import ollama

# .env 파일의 환경 변수를 로드합니다.
load_dotenv()

app = FastAPI()

# 모든 Origin/Method/Header 허용 (CORS 설정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def getGptVisionResponse(imageBytes, userQuestion):
    """
    OpenAI GPT-4o 모델을 사용하여 이미지 분석 및 질문에 답변합니다.
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        base64Image = base64.b64encode(imageBytes).decode('utf-8')
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": userQuestion},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64Image}"}
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

def getOllamaVisionResponse(imageBytes, userQuestion):
    """
    Ollama 로컬 모델을 사용하여 이미지 분석 및 질문에 답변합니다.
    """
    try:
        # gemma4:e2b 모델은 텍스트 전용일 수 있으므로, 이미지 분석을 위해 llava 등 호환 모델 사용 권장
        # 여기서는 요청된 gemma4:e2b를 사용하여 구조를 유지합니다.
        modelName = os.getenv("OLLAMA_MODEL", "gemma4:e2b")
        
        response = ollama.chat(
            model=modelName,
            messages=[{
                'role': 'user',
                'content': userQuestion,
                'images': [imageBytes]
            }]
        )
        return response['message']['content']
    except Exception as e:
        return str(e)

@app.post("/analyze")
async def analyzeImage(file: UploadFile = File(...), question: str = Form(...)):
    """
    업로드된 이미지를 분석하고 텍스트를 추출하여 질문에 답합니다.
    """
    try:
        imageContent = await file.read()
        useModel = os.getenv("USE_MODEL", "OLLAMA")
        
        finalResult = ""
        
        if useModel == "GPT":
            finalResult = getGptVisionResponse(imageContent, question)
        elif useModel == "OLLAMA":
            finalResult = getOllamaVisionResponse(imageContent, question)
        else:
            return {"success": False, "message": "설정된 모델이 유효하지 않습니다."}
            
        return {"success": True, "data": finalResult}
        
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/")
def readRoot():
    """ 
    기본 루트 엔드포인트입니다.
    """
    try:
        currentModel = os.getenv("USE_MODEL", "OLLAMA")
        return {"success": True, "message": f"현재 {currentModel} 모드로 분석 서버가 작동 중입니다."}
    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    nest_asyncio.apply()
    uvicorn.run(app, host="0.0.0.0", port=8000)


