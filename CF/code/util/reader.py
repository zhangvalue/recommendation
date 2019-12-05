# *===================================*
# -*- coding: utf-8 -*-
# * Time : 2019-12-05 15:25
# * Author : zhangsf
# *===================================*
import os


def get_user_click(rating_file):
    """
    get user click list
    Args:
        rating_fiel: input file
    Return:
        dict, key: userid, value:[itemid1, itemid2]
    """
    # 判断该文件是否存在
    if not os.path.exists(rating_file):
        return {}, {}
    fp = open(rating_file)
    num = 0
    # 返回的数据结构
    user_click = {}
    user_click_time = {}
    for line in fp:
        if num == 0:
            num += 1
            continue
        item = line.strip().split(',')
        if len(item) < 4:
            continue
        [userid, itemid, rating, timestamp] = item
        if userid + '_' + itemid not in user_click_time:
            user_click_time[userid + '_' + itemid] = int(timestamp)
        if float(rating) < 3.0:
            continue
        if userid not in user_click:
            user_click[userid] = []
        user_click[userid].append(itemid)
    fp.close()
    return user_click, user_click_time


# 第二个函数得到item的info
def get_item_info(item_file):
    """
    get item info[title, genres]
    Args:
        item_file:input iteminfo file
    return:
        a dict, key itemid, value: [title, genres]
    """
    # 判断item_file是否存在
    if not os.path.exists(item_file):
        return {}
    num = 0
    fp = open(item_file)
    item_info = {}
    for line in fp:
        if num == 0:
            num += 1
            continue
        item = line.strip().split(',')
        if len(item) < 3:
            continue
        if len(item) == 3:
            [itemid, title, genres] = item
        elif len(item) > 3:
            itemid = item[0]
            genres = item[-1]
            title = ','.join(item[1:-1])
        if itemid not in item_info:
            item_info[itemid] = [title, genres]
    fp.close()
    return item_info


if __name__ == '__main__':
    user_click, user_click_time = get_user_click("../../data/ratings.csv")
    # 查看有多少用户
    print(len(user_click))
    # 打印第一个用户的点击序列
    print(user_click["1"])

    item_info=get_item_info("../../data/movies.csv")
    print(len(item_info))
    print(item_info["11"])
