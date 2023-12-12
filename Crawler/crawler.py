import json
import requests
from lxml import etree
import pymysql

config = {
    'host': '10.242.202.17',
    'port': 3306,  # MySQL默认端口
    'user': 'root',  # mysql默认用户名
    'password': 'abc',
    'db': 'catmap',  # 数据库
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}


#接受来自arxiv网页论文的url，如：https://arxiv.org/abs/2312.05488，返回一个记录论文内容评的字典
def fetch_inf(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Error fetching the page")
        return []
    tree = etree.HTML(response.content)
    title = tree.xpath("//meta[@name='citation_title']/@content")[0]
    authors  =  tree.xpath("//div[@class='authors']/a/text()")
    abstract = tree.xpath("//meta[@name='citation_abstract']/@content")[0]
    date = tree.xpath("//meta[@name='citation_date']/@content")[0]
    pdf_link = tree.xpath("//meta[@name='citation_pdf_url']/@content")[0]
    arvix_id = tree.xpath("//meta[@name='citation_arxiv_id']/@content")[0]
    esy = {"arvix_id":arvix_id,"title":title,"authors":authors,"abstract":abstract,"date":date,"pdf_link":pdf_link}
    return esy
    

    #接受一个爬取出的字典文件，放入数据库
def update_to_db(esy):
    con = pymysql.connect(**config)
    cursor = con.cursor()
    insert_stmt = (
        "INSERT INTO `100pdf` (date, author, link, abstract, title, paper_id) "
        "VALUES (%s, %s, %s, %s, %s, %s)"
    )
    
    #author_str = ', '.join(esy["authors"])
    au = json.dumps(esy["authors"])
    insert_data = (esy["date"],au,esy["pdf_link"],esy["abstract"],esy["title"],esy["arvix_id"])
    # cursor.execute(insert_stmt,insert_data)
    # con.commit()
   
    try:
        cursor.execute(insert_stmt, insert_data)
        con.commit()
    except pymysql.Error as e:
        print(f"Error inserting data: {e}")
    cursor.close()
    con.close()


esy = fetch_inf("https://arxiv.org/abs/2312.02858")

update_to_db(esy)



