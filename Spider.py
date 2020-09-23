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

#生成仓库信息
def generate_repositories_info(respositories_list):
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
    return respositories_json

#获取用户仓库信息
def get_repositories_info(user_name):
    repositories_url = "https://github.com/"+user_name+"?tab=repositories"
    next_page_button_flag = True
    final_json = []
    while next_page_button_flag:
        page_resp = requests.get(repositories_url)
        soup = BeautifulSoup(page_resp.content, features="html.parser")
        block = soup.find(id='user-repositories-list')
        #判断仓库页是否有具体仓库
        if block.find("ul") == None:
            break
        #获取当页数据
        respositories_list = block.find_all("li")
        final_json = final_json + generate_repositories_info(respositories_list)
        #判断是否有下一页
        jump_bar_nav = block.find('ul').next_sibling.next_sibling
        if jump_bar_nav == None:
            next_page_button_flag = False
        else:
            #判断“下一页”按钮是否有效
            for next_button in list(jump_bar_nav.children)[1]:
                continue
            if(next_button.name == "button"):
                next_page_button_flag = False
            else:
                repositories_url = next_button["href"]

get_repositories_info("chanchann")
# #获取用户关注列表
# def get_user_following(user_name):
#     following_url = "https://github.com/"+user_name+"?tab=following"

