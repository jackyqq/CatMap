import pymysql
import json
import textwrap
from typing import Optional
from elasticsearch import Elasticsearch
from fastapi import FastAPI, Body
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

def mappingMake():   
    # 定义mapping
    mapping = {
        "mappings": {
            "properties": {
                "date": {
                    "type": "date"  # 日期字段
                },
                "keywords": {
                    "type": "text",  # 关键词字段
                    "fields": {
                        "keyword": {
                            "type": "keyword"  # 关键词的子字段，用于精确匹配和聚合
                        }
                    }
                },
                "year": {
                    "type": "text"  # 年份字段
                },
                "author": {
                    "type": "nested",  # 作者字段
                    "properties": {
                        "name": {"type": "text"},  # 作者名
                        "affiliation": {"type": "text"}  # 作者隶属机构
                        }
                    },

                "title": {
                    "type": "text"  # 标题字段
                },
                "journal": {
                    "type": "text",  # 期刊字段
                    "fields": {
                        "keyword": {
                            "type": "keyword"  # 期刊的子字段，用于精确匹配和聚合
                        }
                    }
                },
                "publisher": {
                    "type": "text",  # 出版社字段
                    "fields": {
                        "keyword": {
                            "type": "keyword"  # 出版社的子字段，用于精确匹配和聚合
                        }
                    }
                },
                "abstract": {
                    "type": "text"  # 摘要字段
                },
                "link":{
                "type" : "keyword"
                },
                "issn":{
                "type" : "keyword"
                },
                "doi" : {
                "type" : "keyword"
                }
            }},

        "settings" : {
        "analysis": {
            "analyzer": {
                "whitespace_analyzer": {
                    "type": "custom",
                    "tokenizer": "whitespace",
                    "filter": ["lowercase"]
                }
            }
        }
    }
    }
    return mapping

# 创建索引
def indexCreate():
    es = Elasticsearch(["http://localhost:9200"], timeout=3600)
    print(es.ping())
    conn = pymysql.connect(host='10.242.202.17', port=3306, user='root', password='abc', charset='utf8', database="catmap")
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM 100pdf")
    res = cursor.fetchall()
    act = []
    length = len(res)
    for i in range(0,length):

        act.append({"index": {"_index": "paper", '_id': i+1}})
        newAuthor = []
        thisAuthor = json.loads(res[i]["author"])
        if isinstance(thisAuthor, list):
            for name in thisAuthor:
                newAuthor.append({"name": name, "affiliation": " "})
        elif isinstance(thisAuthor, dict):
            for name, affiliation in zip(thisAuthor["name"], thisAuthor["affiliation"]):
                newAuthor.append({"name": name, "affiliation": affiliation})
        res[i]["author"] = newAuthor
        res[i]["conference"] = False
        act.append(res[i])
    if es.indices.exists(index="paper"):
        es.indices.delete(index="paper")
    mapping = mappingMake()
    r = es.indices.create(index='paper', body=mapping)
    es.bulk(body=act)
    return es

def process_search_results(res):
    # 初始化结果字典
    processed_results = {
        "awei": [],
        "yt": {"years": [], "counts": []}
    }

    # 用于存储每个年份的出现次数
    year_counts = {}

    # 遍历搜索结果
    for hit in res['hits']['hits']:
        # 获取每一条搜索结果的年份、标题、作者和摘要
        id = hit['_id']
        year = hit['_source']['year']
        title = hit['_source']['title']
        authors = hit['_source']['author']
        abstract = hit['_source']['abstract']
        
        # 构建awei列表的元素，只包含title, author, abstract
        processed_results['awei'].append({
            'id' : id,
            'title': title,
            'author': authors,
            'abstract': abstract
        })

        # 统计年份出现的次数
        if year in year_counts:
             year_counts[year] += 1
        else:
            year_counts[year] = 1
    for year, count in sorted(year_counts.items()):
        processed_results["yt"]["years"].append(year)
        processed_results["yt"]["counts"].append(count)

    return processed_results



app = FastAPI()

# 设置 CORS 以允许跨域请求，特别是来自前端应用的请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    term: str
    selected_option: Optional[str] = None

@app.post("/search")

async def search(request: SearchRequest = Body(...)):
    term = request.term
    selected_option = request.selected_option
    print(term)
    print(selected_option)
    es = indexCreate()
    # 获取查询参数
    #配置查询参数

    
    criteria = []
    if (selected_option == "all fields" or selected_option == ""):
        criteria = ["keywords", "author", "title", "year", "journal", "abstract"]
    else:
        if (selected_option == "author or affiliation"):
            criteria = "author"
        else:
            criteria = selected_option
    es.indices.refresh(index="paper")
    nested_fields = ["author.name", "author.affiliation"]
    
    main_query = {"bool": {"should": []}}

    if criteria == "author":
        nested_query = {
            "nested": {
                "path": "author",
                "query": {
                    "multi_match": {
                        "query": term,
                        "fields": nested_fields
                    }
                }
            }
        }
        main_query["bool"]["should"].append(nested_query)
        

    else:  # 如果还有其它字段
        main_query["bool"]["should"].append({
            "multi_match": {
                "query": term,
                "fields": criteria
            }
        })
    #开始查询
    res = es.search(index="paper", body={"query": main_query})
    realRes = process_search_results(res)
    print(realRes)
    return realRes

if __name__ == "__main__":
    import uvicorn 
    uvicorn.run("main:app",host = '127.0.0.1',port = 8000,reload=True ,debug = True,workers=1)
