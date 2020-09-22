import requests
import random
import string
import os

from bs4 import BeautifulSoup

readme_save_local_address = "/Users/qinhaojun/Desktop/testSpi"
source_user = "Bolvvv"

#生成随机文件名称
def generate_file_name():
    salt = ''.join(random.sample(string.ascii_letters + string.digits, 6))
    return salt

#返回对应仓库的json字段
def download_readme(link):
    #生成readme的md格式下载地址
    download_address = "https://raw.githubusercontent.com"+link+"/master/README.md"
    urlpage = requests.get(download_address)
    if urlpage.status_code != 200:
        return None
    else:
        save_address = readme_save_local_address+"/"+generate_file_name()+".md"
        ff = open(save_address,'w')
        ff.writelines(urlpage.text)
        ff.close()
        return save_address

#获取用户仓库信息
def get_repositories_info(user_name):
    repositories_url = "https://github.com/"+user_name+"?tab=repositories"
    repositories_page_resp = requests.get(repositories_url)
    repositories_page_soup = BeautifulSoup(repositories_page_resp.content, features="html.parser")
    respositories_list = repositories_page_soup.find(id='user-repositories-list').find_all("li")
    #获取仓库信息
    respositories_json = []
    for i in respositories_list:
        temp_json = {
            "name":None,
            "link":None,
            "readme_local_address":None
        }
        temp_json['name'] = i.a.string.lstrip()
        temp_json['link'] = i.a['href']
        temp_json['readme_local_address'] = download_readme(i.a['href'])
        respositories_json.append(temp_json)
    print(respositories_json)

get_repositories_info(source_user)

# following_url = "https://github.com/"+source_user+"?tab=following"
