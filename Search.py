import pymysql
import json
import textwrap
from elasticsearch import Elasticsearch
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
es = Elasticsearch(timeout = 3600)
print(es.ping())
conn = pymysql.connect(host = '10.242.202.17',
port = 3306, user='root', password='abc',charset = 'utf8', database = "catmap")
cursor = conn.cursor(pymysql.cursors.DictCursor)
cursor.execute("SELECT * FROM 100pdf")
res = cursor.fetchall()
thisid = 1
print(res[0])

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
                "type": "integer"  # 年份字段
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

# 创建索引（替换YOUR_INDEX_NAME为您想要的索引名称）

act = []
len = len(res)
for i in range(0,len):

    act.append({"index": {"_index": "paper", '_id': i+1}})
    newAuthor = []
    thisAuthor = json.loads(res[i]["author"])
    for name, affiliation in zip(thisAuthor["name"], thisAuthor["affiliation"]):
        newAuthor.append({"name": name, "affiliation": affiliation})
    res[i]["author"] = newAuthor
    res[i]["conference"] = False
    act.append(res[i])
print(act[0])
if es.indices.exists(index = "paper"):
    es.indices.delete(index="paper")
r = es.indices.create(index ='paper',body =mapping)
es.bulk(body = act)


app = FastAPI()

@app.post("/search")

async def search_papers(request:Request):
    data = await request.json()
    print(data)
    query = data['query']
    criteria = data['criteria']
    es.indices.refresh(index = "paper")
    search_body = {
        "query": {
            "multi_match": {  # 多字段匹配查询
                "query": query,
                "fields": criteria  # 指定要搜索的字段
            }
        }
    }
    res = es.search(index="paper", body=search_body)
    print(res)
    return res

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(r"C:\Users\86188\Desktop\study\DianGongDao\Large Project\index.html", 'r',encoding='utf-8') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

