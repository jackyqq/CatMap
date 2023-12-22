from fastapi import FastAPI,Request,Query,APIRouter,Response,Body
from pydantic import BaseModel,Field
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional,List
from fastapi.responses import FileResponse,StreamingResponse
import httpx
import database

app = FastAPI(
    title="Catmap_api",
    docs_url='/api/v1/docs',
    redoc_url='/api/v1/redoc',
    openapi_url='/api/v1/openapi.json'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

class Item(BaseModel):
    All_Fields : Optional[str] = None
    Title : Optional[int] = None
    Author_Affiliation : Optional[str] = None
    Keywords : Optional[str] = None
    Year : Optional[str] = None
    Journal : Optional[str] = None
    Abstract : Optional[str] = None



#简单搜索
@app.get('/api/search_easy')
async def search_papers(request : Request):
    data = await request.json()
    papers = Search(data)
    #print(papers)
    return papers

#复杂搜索
@app.post("/search_difficult")
async def search_papers(item : Item = Body(..., title="search_body",description="a string of content", example="Carlson")):
    papers = Search(item)
    #print(papers)
    return papers

@app.get("/years/", response_model=List[int])
async def get_years():
    # 这里，我们假设年份范围是2000到当前年份
    current_year = 2023  # 通常，这里可以用datetime模块动态获取当前年份
    years = list(range(2000, current_year + 1))
    return years

@app.get("/download-pdf/")
async def download_pdf():
    file_path = "path/to/your/pdf-file.pdf"  # 将这里的路径替换为你的 PDF 文件的实际路径
    return FileResponse(path=file_path, media_type='application/pdf', filename="downloaded_file.pdf")


async def download_pdf():
    pdf_url = "http://example.com/path/to/your/pdf"  # 替换为实际的 PDF 文件 URL

    async with httpx.AsyncClient() as client:
        response = await client.get(pdf_url, follow_redirects=True)
        response.raise_for_status()

        return StreamingResponse(response.iter_bytes(), media_type=response.headers['Content-Type'])

@app.get("/api/papers/details")
async def get_paper_detail(id : str = Query(..., title = "get_details", description="from the id to details", example = "1")):
    papers = Search(id)
    #Search函数内部已经连接好数据库，并能实现对id的搜索
    return papers
    # eg_papers = {"author":"xmm", "abstract" : "xmmwd", "pdf_url" : "http://example.com/123"}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run:app", host = '127.0.0.1', port = 8000, reload = True, workers = 1)
