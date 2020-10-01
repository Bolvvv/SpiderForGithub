import requests
import random
import string
import os
import logging
import click

from bs4 import BeautifulSoup

readme_save_local_address = "./readme_file"
name_list_file = "./log/name_list.txt"
log_file_name = "./log/log.log"


#日志配置
logging.basicConfig(
        level=logging.DEBUG,  # 定义输出到文件的log级别，大于此级别的都被输出
        format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
        datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
        filename=log_file_name,  # log文件名
        filemode='w+')  # 写入模式“w”或“a”

#返回对应仓库的json字段
def download_readme(link):
    #生成readme的md格式下载地址
    download_address = "https://raw.githubusercontent.com"+link+"/master/README.md"
    urlpage = requests.get(download_address)
    if urlpage.status_code != 200:
        return None
    else:
        save_address = readme_save_local_address+"/"+link.strip('/').replace('/','_')+".md"
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
        logging.debug(temp_json['link'])
    return respositories_json

#获取用户仓库信息
def get_repositories_info(user_name):
    repositories_url = "https://github.com/"+user_name+"?tab=repositories"
    next_page_button_flag = True
    final_json = []
    while next_page_button_flag:
        page_resp = requests.get(repositories_url)
        #在这一步需要注意设置bs4使用的默认解析器，有html.parser,lxml和html5lib。使用html.parser容易造成解析不完全的问题，故更换为lxml
        soup = BeautifulSoup(page_resp.content, 'lxml')
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
    return final_json

# 获取用户关注列表与被关注列表
def get_user_follow(user_name):
    following_url = "https://github.com/"+user_name+"?tab=following"
    next_page_button_flag = True
    final_json = []
    while next_page_button_flag:
        page_resp = requests.get(following_url)
        soup = BeautifulSoup(page_resp.content, features="lxml")
        #获取对应关注列表块
        follow_list = list(list(list(list(list(soup.main)[3])[1])[3])[3])[3]
        list_a = follow_list.find_all('a', class_='d-inline-block no-underline mb-1')
        #判断是否有关注好友
        if list_a == []:
            break
        #获取当页关注列表
        for i in list_a:
            final_json.append(i['href'].strip('/'))
        #判断是否有下一页按钮
        button_nav = follow_list.find('div', class_ = "pagination")
        if button_nav == None:
            next_page_button_flag = False
        else:
            #判断下一页按钮是否有效
            next_button = list(button_nav)[1]
            if next_button.name != 'a':
                next_page_button_flag = False
            else:
                following_url = next_button['href']
    return final_json

# 赋值
@click.command()
@click.option('--retry', is_flag=True)#设置retry参数，当命令行不设置retry参数时，retry==fales,不进行重试操作
def spider(retry):
    number = 2000
    save_json = []
    name_list = ["Bolvvv"]
    stop_flag = False
    name_set = set()
    temp_list = []
    index = 0
    if retry == True:
        name_set_file = open(name_list_file, 'r')
        s = name_set_file.readlines()
        for i in s:
            name_set.add(i.replace('\n',''))
        name_set_file.close()
    try:
        while stop_flag==False:
            for index in range(len(name_list)):
                if len(save_json) > number:
                    stop_flag=True
                    break
                #获取当前用户的关注列表，并将其加入临时关注列表中
                temp_list = temp_list + get_user_follow(name_list[index])
                if index == len(name_list)-1:
                    index = 0
                    name_list = temp_list[:]
                    temp_list.clear()
                if name_list[index] in name_set:
                    continue
                else:
                    name_set.add(name_list[index])
                    save_json = save_json + get_repositories_info(name_list[index])
    except:
        logging.debug("网络出现问题")
        ff = open(name_list_file,'w+')
        for i in name_set:
            ff.writelines(i)
            ff.writelines('\n')
        ff.close()

if __name__ == "__main__":
    spider()