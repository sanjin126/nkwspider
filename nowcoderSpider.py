# -*- coding = UTF-8 #-*-
# @Time : 2023/2/6 13:25
# @Author : 李宇博
# @File : nowcoderSpider.py
# @SoftWare : PyCharm
import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def getJson(page, jobId):
    headers = {
        'authority': 'gw-c.nowcoder.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.nowcoder.com',
        'referer': 'https://www.nowcoder.com/',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    json_data = {
        'companyList': [],
        'jobId': jobId,
        'level': 3,
        'order': 3,
        'page': page,
        'isNewJob': True,
    }

    response = requests.post(
        'https://gw-c.nowcoder.com/api/sparta/job-experience/experience/job/list',
        headers=headers,
        json=json_data,
    )
    content = json.dumps(response.json(), indent=4, ensure_ascii=False)
    content = json.loads(content)
    return content


# 获取代号
def getId():
    jobId = int(input("请输入你要爬取的jobId:\n"))
    # 获取返回内容
    content = getJson(1, jobId)
    # print("共有{}条记录".format(content['data']['total']))
    groupNum = int(input("请输入你要爬取的面经组数(20个为一组):\n"))
    for i in range(1, groupNum + 1):
        res = getJson(i, jobId)
        with open('textId.txt', 'a') as f:
            for i in range(20):
                try:
                    f.write(str(res['data']['records'][i]['contentData']['entityId']) + "\n")
                except KeyError:
                    f.write(str(res['data']['records'][i]['momentData']['id']) + "\n")
                except IndexError:
                    print("没有这么多面经，请重试！")
                    os.remove('textId.txt')
                    exit(0)
    print("获取文章代号完毕，已写入textId.txt")
    return jobId


def getContent():
    sigNum = 0
    cnt = 1
    result = ""
    with open("textId.txt", "r") as f:
        content = f.read().splitlines()
    for i in content:
        url = "https://www.nowcoder.com/discuss/" + str(i)
        print(cnt, url)
        r = getHtml(url)
        title = re.findall('<title>(.*?)</title>', r.text)[0].replace("_笔经面经_牛客网", '')
        # time = re.findall('<span class ="time-text" data-v-bb417982="" >(.*?)</span>', r.text, re.S)[0].replace("\n", "").replace("  ", "")
        try:
            bs = BeautifulSoup(r.text, 'html.parser')
            res = bs.find_all(name='span', attrs={'class': 'time-text'})
            bs2 = BeautifulSoup(str(res[0]), 'html.parser')
            time = bs2.get_text()
            bs = BeautifulSoup(r.text, 'html.parser')
            res = bs.find_all(name='div', attrs={'class': 'nc-slate-editor-content'})
            bs2 = BeautifulSoup(str(res[0]), 'html.parser')
            content = bs2.get_text()
            print('类型1')
            sigNum = sigNum + 1
        except IndexError:
            try:
                print('类型2')
                bs = BeautifulSoup(r.text, 'html.parser')
                res = bs.find_all(name='span', attrs={'class': 'time-text'})
                bs2 = BeautifulSoup(str(res[0]), 'html.parser')
                time = bs2.get_text()
                bs = BeautifulSoup(r.text, 'html.parser')
                res = bs.find_all(name='div', attrs={'class': 'nc-post-content'})
                bs2 = BeautifulSoup(str(res[0]), 'html.parser')
                content = bs2.get_text()
                sigNum = sigNum + 1
            except IndexError:
                print('IP被封')
                time = "无"
                title = "IP被封，未获取到，请重试"
                content = "IP被封，未获取到，请重试"
        result += content
        with open("final.txt", "a") as f:
            f.write("第" + str(cnt) + "篇面经" + "\n" + "链接:" + str(url) + "\n" + "标题:" + str(
                title) + "\n" + "时间:" + str(
                time) + "\n" + "内容:" + str(result) + "liyubo")
        # print("链接:" + url, "标题:" + title, "时间:" + time, sep="\t")
        cnt = cnt + 1
        result = ""
    print("内容爬取完毕，共有{}条有效数据，已写入final.txt文件".format(sigNum))


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def getHtml(url):
    # ....
    retry_count = 5
    proxy = get_proxy().get("proxy")
    headers = {'User-Agent': str(UserAgent().random)}
    while retry_count > 0:
        try:
            # 使用代理访问
            # print(proxy)
            # 代理搭建好后可使用这个
            # html = requests.get(url, proxies={"http": "http://{}".format(proxy)}, headers=headers)
            # 没搭建好代理用这个
            html = requests.get(url, headers=headers)
            return html
        except Exception:
            retry_count -= 1
            # 删除代理池中代理
            delete_proxy(proxy)
    return None


def clearBlankLine(id):
    file1 = open('final.txt', 'r', encoding='utf-8')  # 要去掉空行的文件
    file2 = open(str(id) + ".txt", 'w', encoding='utf-8')  # 生成没有空行的文件
    try:
        for line in file1.readlines():
            if line == '\n':
                line = line.strip("\n")
            elif line.__contains__("liyubo"):
                line = line.replace("liyubo", "\n\n\n\n")
            file2.write(line)
    finally:
        file1.close()
        file2.close()
        print("空行去除完毕，完成！")


def formatting():
    try:
        os.remove("final.txt")
        os.remove("textId.txt")
    except:
        print("出现异常")


def save_to_file(content: str, file_name="final.txt"):
    with open(file_name, "a", encoding='utf8') as f:
        f.write(content)


def get_experience_list(job_id, page, save: callable):
    url = "https://gw-c.nowcoder.com/api/sparta/job-experience/experience/job/list?_=" + "1734871561374"
    headers = {'User-Agent': str(UserAgent().random), "content-type": "application/json"}
    page = int(page)
    data = {"companyList": [], "jobId": int(job_id), "level": 3, "order": 3, "page": page, "isNewJob": "true"}
    r = requests.post(url=url,
                      headers=headers,
                      data=json.dumps(data))
    content: dict = json.loads(r.text)['data']
    current_page = content['current']
    size = content['size']
    total_page = content['totalPage']
    records: list = content['records']
    first_time = 0
    print("第{}页".format(current_page))

    try:
        first_time = records[0]['momentData']['showTime']
    except KeyError:
        first_time = records[0]['contentData']['createTime']

    save_content = ''
    for i, record in enumerate(records):
        parse, err = parse_experience_record(record, lambda title, aid: print(i, title, aid))
        if not err:
            print("**")
            continue
        save_content += parse
        save_content += '\n\n'
    f_name = "experience-" + time.strftime("%Y-%m-%d", time.localtime(first_time / 1000.0)) + ".txt"
    try:
        # save(save_content, f_name)
        pass
    except Exception as e:
        print(e)
        raise IOError("save content to file failed")
    print("第{}页保存完毕->{}".format(current_page, f_name))
    return total_page, f_name


def parse_experience_record(record: dict, print_title):
    try:
        content_id: int = record['contentId']
        print(content_id)
        if not save_article_id(content_id):
            return '', False

        content_type: int = record['contentType']
        if content_type == 74:
            user_brief: dict = record['userBrief']
            moment_ata: dict = record['momentData']

            user_name = user_brief['nickname']
            education_info = user_brief['educationInfo'] or ''
            auth_display_info = user_brief['authDisplayInfo'] or ''
            title: str = moment_ata['title']

            print_title(title, content_id)

            interview_exp: str = moment_ata['content']
            create_time: int = moment_ata['showTime']
            parse: str = ''
            parse += title + '\n'
            parse += (user_name + ' ' + education_info + ' ' + auth_display_info +
                      time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(create_time / 1000.0)) + '\n')
            parse += interview_exp + '\n'
            return parse, True
        elif content_type == 250:
            user_brief: dict = record['userBrief']
            content_data: dict = record['contentData']

            user_name = user_brief['nickname']
            education_info = user_brief['educationInfo'] or ''
            auth_display_info = user_brief['authDisplayInfo'] or ''
            title: str = content_data['title']
            print_title(title)
            interview_exp: str = content_data['content']
            create_time: int = content_data['createTime']
            parse: str = ''
            parse += title + '\n'
            parse += (user_name + ' ' + education_info + ' ' + auth_display_info +
                      time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(create_time / 1000.0)) + '\n')
            parse += interview_exp + '\n'
            return parse, True
    except KeyError as e:
        print(e)
        return '', False
    except Exception as e:
        print(e)
        return '', False


articleIds = set()


def init():
    # load article id from file
    # not exist, create one
    if not os.path.exists("articleId.txt"):
        with open("articleId.txt", "w") as f:
            pass
    with open("articleId.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            articleIds.add(int(line.strip()))


def save_article_id(article_id):
    print(article_id)
    if int(article_id) not in articleIds:
        print('hit')
        print(articleIds)
        print( article_id not in articleIds )
        articleIds.add(article_id)
        return True
    else:
        return False


def store_article_id():
    with open("articleId.txt", "a") as f:
        for article_id in articleIds:
            f.write(str(article_id) + "\n")


if __name__ == '__main__':
    init()
    # # 获取文章代号
    # jobId = getId()
    # # 获取内容并写入文件
    # getContent()
    # # 格式化处理
    # clearBlankLine(jobId)
    # formatting()
    # print(save_article_id(2507643))

    file_name_set = []

    total_page, file_name = get_experience_list(11002, 1, save_to_file)
    file_name_set.append(file_name)

    for i in range(24, 50):
        try:
            _, file_name = get_experience_list(11002, i, save_to_file)
            file_name_set.append(file_name)
        except IOError as e:
            print(e)
            pass
        finally:
            time.sleep(1)
    # 写入文件
    with open("filename.txt", "a", encoding="utf8") as f:
        for file_name in file_name_set:
            f.write(file_name + "\n")
    store_article_id()
