import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from appConfig import AppConfig


def req_one_pge(job_id, page):
    url = "https://gw-c.nowcoder.com/api/sparta/job-experience/experience/job/list?_=" + "1734871561374"
    headers = {'User-Agent': str(UserAgent().random), "content-type": "application/json"}
    page = int(page)
    data = {"companyList": [], "jobId": int(job_id), "level": 3, "order": 3, "page": page, "isNewJob": "true"}
    r = requests.post(url=url,
                      headers=headers,
                      data=json.dumps(data))
    if r.status_code != 200:
        raise IOError("request failed")
    return r


def special_for_250(article_id):
    article = ''
    try:
        resp = requests.get("https://www.nowcoder.com/discuss/{}".format(article_id))
        soup = BeautifulSoup(resp.text, "html.parser")
        # find by class
        case1 = soup.find_all(class_='nc-slate-editor-content')
        case2 = soup.find_all(class_='feed-content-text')
        case3 = soup.find_all(class_='nc-post-content')

        if len(case1) > 0:
            items = case1[0]
            all_children = items.children  # 或使用 target_node.children（返回的是生成器）

            # 提取子节点的文本内容
            for child in all_children:
                if child.name:  # 如果是一个标签
                    if child.get_text(strip=True) == '':
                        continue
                    article += child.get_text(strip=True) + '\n'
                else:  # 如果是一个文本节点
                    if child.strip() == '':
                        continue
                    article += child.strip() + '\n'
        elif len(case2) > 0:
            items = case2[0]
            all_children = items.children  # 或使用 target_node.children（返回的是生成器）

            # 提取子节点的文本内容
            for child in all_children:
                if child.name:  # 如果是一个标签
                    if child.get_text(strip=True) == '':
                        continue
                    article += child.get_text(strip=True) + '\n'
                else:  # 如果是一个文本节点
                    if child.strip() == '':
                        continue
                    article += child.strip() + '\n'
        elif len(case3) > 0:
            # recursive case3 node every child
            items = case3[0]
            all_children = items.children  # 或使用 target_node.children（返回的是生成器）

            # 提取子节点的文本内容
            for child in all_children:
                if child.name:  # 如果是一个标签
                    if child.get_text(strip=True) == '':
                        continue
                    article += child.get_text(strip=True) + '\n'
                else:  # 如果是一个文本节点
                    if child.strip() == '':
                        continue
                    article += child.strip() + '\n'
        else :
            print("no content id:{}".format(article_id))
            exit(1)
        return article
    except Exception as e:
        print("exception" + e)
        raise e


def parse_record_2_article(record: dict, title_printer: callable):
    try:
        content_id: int = record['contentId']
        if not save_article_id(content_id):
            return '', False

        content_type: int = record['contentType']

        if content_type == 74:
            user_brief: dict = record['userBrief']
            content_data: dict = record['momentData']
            create_time: int = content_data['showTime']
            interview_exp: str = content_data['content']
        elif content_type == 250:
            user_brief: dict = record['userBrief']
            content_data: dict = record['contentData']
            create_time: int = content_data['createTime']
            interview_exp: str = special_for_250(content_id)
        else:
            return '', False
        user_name = user_brief['nickname']
        education_info = user_brief['educationInfo'] or ''
        auth_display_info = user_brief['authDisplayInfo'] or ''
        title: str = content_data['title']
        title_printer(title)

        article: str = ''
        article += title + '\n'
        article += (user_name + ' ' + education_info + ' ' + auth_display_info + ' ' + str(content_id) + ' ' +
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(create_time / 1000.0)) + '\n')
        article += interview_exp + '\n'
        return article, True
    except KeyError as e:
        print('KeyError' + e)
        return '', False
    except Exception as e:
        print('Exception' + e)
        return '', False


def get_experience_list(job_id, page, file_saver: callable):
    try:
        resp = req_one_pge(job_id, page)
    except Exception as e:
        print(e)
        raise IOError("request failed")

    pageContent: dict = json.loads(resp.text)['data']
    current_page = pageContent['current']
    size = pageContent['size']
    total_page = pageContent['totalPage']
    records: list = pageContent['records']
    try:
        first_time = records[0]['momentData']['showTime']
    except KeyError:
        first_time = records[0]['contentData']['createTime']

    print("开始保存第{}页".format(current_page))

    each_article = []
    for i, record in enumerate(records):
        article, success = parse_record_2_article(record, lambda title: print(i, title))
        if not success:
            print("**无**")
            continue
        each_article.append(article)
        each_article.append("\n")

    try:
        f_name = ("experience-" +
                  time.strftime("%Y-%m-%d", time.localtime(first_time / 1000.0))
                  + ".txt")
        file_saver(each_article, f_name)
    except Exception as e:
        print(e)
        raise IOError("保存到文件中失败了")
    print("第{}页保存完毕->{}".format(current_page, f_name))
    return total_page, f_name


def init():
    if not os.path.exists(appConfig.data_dir):
        os.mkdir(appConfig.data_dir)
    ais_file = appConfig.article_id_set

    if not os.path.exists(ais_file):
        with open(ais_file, "w") as f:
            pass
    with open(ais_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            articleIds.add(str(line.strip()))
    # load file name from file
    # not exist, create one
    if not os.path.exists(appConfig.article_filename_set):
        with open(appConfig.article_filename_set, "w") as f:
            pass
    with open(appConfig.article_filename_set, "r") as f:
        lines = f.readlines()
        for line in lines:
            file_name_set.add(str(line.strip()))


def save_article_id(article_id):
    article_id = str(article_id)
    if article_id not in articleIds:
        articleIds.add(article_id)
        return True
    else:
        return False


def save_file_name(file_name):
    file_name = str(file_name)
    if file_name not in file_name_set:
        file_name_set.add(file_name)
        return True
    else:
        return False


def store_article_id():
    with open(appConfig.article_id_set, "a") as f:
        for article_id in articleIds:
            f.write(str(article_id) + "\n")


def store_file_name():
    with open(appConfig.article_filename_set, "a", encoding="utf8") as f:
        for file_name in file_name_set:
            f.write(file_name + "\n")


def save_article_to_file(content: list, file_name):
    with open(appConfig.data_dir + os.sep + file_name, "a", encoding='utf8') as f:
        for line in content:
            f.write(line)


file_name_set = set()
articleIds = set()
appConfig = AppConfig()
if __name__ == '__main__':
    ## for test
    # article_id = '693110685621833728'
    # print(special_for_250(article_id))
    # exit(1)
    ##
    init()

    for i in range(1, 21):
        try:
            total_page, file_name = get_experience_list(11002, i, save_article_to_file)
            save_file_name(file_name)
            if i == total_page:
                break
        except IOError as e:
            print(e)
            pass
        finally:
            time.sleep(0.1)

    # 写入文件
    store_file_name()
    store_article_id()
