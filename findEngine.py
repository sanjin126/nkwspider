import os

from appConfig import AppConfig


def find_by_keyword(filename, k):
    filename = AppConfig.data_dir + os.sep + filename
    l = []
    with open(filename, "r", encoding="utf8") as f:
        lines = f.readlines()
        for line in lines:
            if k.lower() in line.lower():
                l.append(str.strip(line))
    return l


if __name__ == '__main__':
    appConfig = AppConfig()
    with open(appConfig.article_filename_set, "r", encoding="utf8") as f:
        files = f.readlines()
    while True:
        keyword = input("输入查询关键字：")
        if keyword == "exit":
            break
        res = []
        for file in files:
            res.extend(find_by_keyword(str.strip(file), keyword))
        print('查询到的个数为：', len(res))
        ifShow = input("Do you want to see the results? (y/n): ")
        if ifShow == "y":
            for i in res:
                print(i)
