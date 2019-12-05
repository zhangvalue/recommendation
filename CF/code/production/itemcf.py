# *===================================*
# -*- coding: utf-8 -*-
# * Time : 2019-12-05 15:48
# * Author : zhangsf
# *===================================*
# import sys
# sys.path.append("../util")
# import util.reader as reader
from CF.code.util import reader
import math
import operator

user_click, user_click_time = reader.get_user_click("../../data/ratings.csv")


def transfer_user_click(user):
    """
    将用户的点击转化成item被用户点击
    Args:
        user_click: key userid, value: [itemid1, itemid2]
    Return:
        dict, key itemid, value:[userid1,userid2]
    """
    item_click_by_user = {}
    for user in user_click:
        item_list = user_click[user]
        for itemid in item_list:
            item_click_by_user.setdefault(itemid, [])
            item_click_by_user[itemid].append(user)
    return item_click_by_user


def usercf_base_contribution_score():
    """
    基础的用户贡献权重
    """
    return 1


def usercf_update_contribution_score(item_user_click_count):
    """
    usercf contribution score update V1
    Args:
        item_user_click_count: how many user have clicked this item
    Return：
        contribution score
    """
    return 1 / math.log10(1 + item_user_click_count)


def usercf_update_two_contribution_score(click_time_one, click_time_two):
    """
    usercf contribution score update V2
    Args:
        different user action time to the same item, click_time_one, click_time_two
    return:
        Contribution score
    """
    delta_time = abs(click_time_two - click_time_one)
    # 将时间转化为以天为单位
    norm_num = 60 * 60 * 24
    delta_time = delta_time / norm_num
    return 1 / (1 + delta_time)


usercf_contribution_type = 2


def cal_user_sim(item_click_by_user, user_click_time):
    """
    计算用户相似度
    Args:
        item_click_by_user: dict, key:itemid, value:[userid1, userid2]
    Return:
        dict, key itemid, value:dict, value_key:itemid_j, value_value:sim_score
    """
    co_appear = {}
    user_click_count = {}
    for itemid, user_list in item_click_by_user.items():
        for index_i in range(0, len(user_list)):
            user_i = user_list[index_i]
            user_click_count.setdefault(user_i, 0)
            user_click_count[user_i] += 1
            if user_i + "_" + itemid not in user_click_time:
                click_time_one = 0
            else:
                click_time_one = user_click_time[user_i + "_" + itemid]
            for index_j in range(index_i + 1, len(user_list)):
                user_j = user_list[index_j]
                if user_j + "_" + itemid not in user_click_time:
                    click_time_two = 0
                else:
                    click_time_two = user_click_time[user_j + '_' + itemid]
                co_appear.setdefault(user_i, {})
                co_appear[user_i].setdefault(user_j, 0)
                co_appear.setdefault(user_j, {})
                co_appear[user_j].setdefault(user_i, 0)

                # 基础用户贡献权重
                if usercf_contribution_type == 0:
                    co_appear[user_i][user_j] += usercf_base_contribution_score()
                    co_appear[user_j][user_i] += usercf_base_contribution_score()
                # 惩罚行为频繁用户的贡献权重
                elif usercf_contribution_type == 1:
                    co_appear[user_i][user_j] += usercf_update_contribution_score(len(user_list))
                    co_appear[user_j][user_i] += usercf_update_contribution_score(len(user_list))
                # 惩罚时间间隔太长的用户贡献权重
                elif usercf_contribution_type == 2:
                    co_appear[user_i][user_j] += usercf_update_two_contribution_score(click_time_one, click_time_two)
                    co_appear[user_j][user_i] += usercf_update_two_contribution_score(click_time_one, click_time_two)
    user_sim_info = {}
    user_sim_info_sorted = {}
    for user_i, relate_user in co_appear.items():
        user_sim_info.setdefault(user_i, {})
        for user_j, cotime in relate_user.items():
            user_sim_info[user_i].setdefault(user_j, 0)
            user_sim_info[user_i][user_j] = cotime / math.sqrt(user_click_count[user_i] * user_click_count[user_j])
    # 将相似度用户排序
    for user in user_sim_info:
        user_sim_info_sorted[user] = sorted(user_sim_info[user].items(), key=operator.itemgetter(1), reverse=True)
    return user_sim_info_sorted


def cal_recom_result_using_usercf(user_click, user_sim):
    """
    利用usercf产生推荐结果
    Args:
        user_clik: dict, key userid, value: [itemid1, itemid2]
        user_sim: key: userid value: [(useridj, score1),(useridk, score2)]
    Return:
        dict, key userid, value: dict value_key:itemid, value_value:recom_score
    """

    recom_result = {}
    topk_user = 3
    item_num = 5
    for user, item_list in user_click.items():
        tmp_dict = {}
        for itemid in item_list:
            tmp_dict.setdefault(itemid, 1)
        recom_result.setdefault(user, {})
        for zuhe in user_sim[user][:topk_user]:
            userid_j, sim_score = zuhe
            if userid_j not in user_click:
                continue

            for itemid_j in user_click[userid_j][:item_num]:
                recom_result[user].setdefault(itemid_j, sim_score)
    return recom_result


def debug_user_sim(user_sim):
    """
    测试用户间相似度
    Args：
        user_sim: key: userid vale:[(userid1, score1), (userid2,score2)]
    """
    fixed_user = 212
    topk = 5
    if fixed_user not in user_sim:
        print("Invalid user")
        return
    for zuhe in user_sim[fixed_user][:topk]:
        userid, score = zuhe
        print("fix_user" + "\t sim_user" + userid + "\t" + str(score))


def debug_recom_result_using_usercf(item_info, recom_result):
    """
    Args:
        item_info: key itemid value:[title, genres]
        recom_result: key userid, value dict, value key: itemid value_value: recom_score
    """
    fix_user = '1'
    if fix_user not in recom_result:
        print("invalid user for recoming result.")
        return
    for itemid in recom_result["1"]:
        if itemid not in item_info:
            continue
        recom_score = recom_result["1"][itemid]
        print("recom result: " + ",".join(item_info[itemid]) + "\t" + str(recom_score))


def main_flow():
    user_click, user_click_time = reader.get_user_click("../../data/ratings.csv")
    item_click_by_user = transfer_user_click(user_click)
    user_sim = cal_user_sim(item_click_by_user, user_click_time)
    recom_result = cal_recom_result_using_usercf(user_click, user_sim)
    # 打印出针对userid为1的推荐结果
    # print(recom_result["1"])
    # 前面是item的id 后面是推荐得分
    # '296': 0.0031744794848567043
    # print((user_sim["1"]))
    debug_user_sim(user_sim)
    item_info = reader.get_item_info("../../data/movies.csv")
    debug_recom_result_using_usercf(item_info, recom_result)


if __name__ == '__main__':
    main_flow()
