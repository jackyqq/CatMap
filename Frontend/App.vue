import pymysql
import json
import textwrap
from elasticsearch import Elasticsearch
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

es = Elasticsearch(timeout=3600)
print(es.ping())
conn = pymysql.connect(host='10.242.202.17', port=3306, user='root', password='abc', charset='utf8', database="catmap")
cursor = conn.cursor(pymysql.cursors.DictCursor)
cursor.execute("SELECT * FROM 100pdf")
res = cursor.fetchall()
thisid = 1
print(res[len(res)-1])

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

# 创建索引（替换YOUR_INDEX_NAME为您想要的索引名称）

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
len1 = len(act)
if es.indices.exists(index="paper"):
    es.indices.delete(index="paper")
r = es.indices.create(index='paper',body =mapping)
es.bulk(body=act)


app = FastAPI()

# 设置 CORS 以允许跨域请求，特别是来自前端应用的请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],  #URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search")

async def search_papers(request:Request):
    data = await request.json()
    print(data)
    query = data['query']
    criteria = data['criteria']
    es.indices.refresh(index="paper")
    nested_fields = ["author.name", "author.affiliation"]
    normal_fields = [field for field in criteria if field != "author"]
    highlight_fields = {field: {} for field in normal_fields}
    main_query = {"bool": {"must": []}}

    if "author" in criteria:
        nested_query = {
            "nested": {
                "path": "author",
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": nested_fields
                    }
                }
            }
        }
        main_query["bool"]["must"].append(nested_query)
        criteria.remove("author")

    if criteria:  # 如果还有其它字段
        main_query["bool"]["must"].append({
            "multi_match": {
                "query": query,
                "fields": criteria
            }
        })
    print(main_query)
    res = es.search(index="paper", body={"query": main_query, "highlight": {
            "fields":highlight_fields,  # 对所有搜索字段应用高亮

            "pre_tags": ["<em>"],  # 高亮文本的开始标签
            "post_tags": ["</em>"],  # 高亮文本的结束标签
        }})
    print(res)
    return res



@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(r"C:\Users\86188\Desktop\study\DianGongDao\Large Project\index.html", 'r',encoding='utf-8') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

