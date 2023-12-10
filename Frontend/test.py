from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 设置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search")
async def search_papers(request: Request):
    # 解析请求体为 JSON
    data = await request.json()
    print("收到的搜索请求数据:", data)

    # 返回一个简单的测试响应
    return JSONResponse(content={"message": "测试成功", "receivedData": data})

@app.get("/test")
async def test_endpoint():
    # 一个简单的 GET 请求测试端点
    return {"message": "GET 请求测试成功"}
