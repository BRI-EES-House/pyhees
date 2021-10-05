# ============================================================================
# 第三章 暖冷房負荷と外皮性能
# 第四節 日射熱取得率
# Ver.11（住宅・住戸の外皮性能の計算プログラム Ver.03～2021.4）
# ----------------------------------------------------------------------------
# 付録B 大部分がガラスで構成されている窓等の開口部における取得日射熱補正係数
# ----------------------------------------------------------------------------
# B.1.1 開口部の上部に日除けが設置されている場合
# ============================================================================

import os
import pandas as pd
import numpy as np
from functools import lru_cache


def calc_f_H_1(region, glass_spec_category, direction, y1, y2, z):
    """ 開口部の暖房期の取得日射熱補正係数(面する方位に応じない求め方) 式(1)

    :param region: 省エネルギー地域区分
    :type region: int
    :param glass_spec_category: ガラスの仕様の区分
    :type glass_spec_category: str
    :param direction: 外皮の部位の方位
    :type direction: str
    :param y1: 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
    :type y1: float
    :param y2: 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm)
    :type y2: float
    :param z: 壁面からの日除けの張り出し寸法（軒等の出寸法は壁表面から先端までの寸法とする）(mm)
    :type z: float
    :return: 開口部の暖房期の取得日射熱補正係数(面する方位に応じない求め方) 式(1)
    :rtype: float
    """
    l1 = get_l1(y1, z)
    l2 = get_l2(y1, y2, z)
    f1 = get_glass_f(region, glass_spec_category, l1, 'H', direction)
    f2 = get_glass_f(region, glass_spec_category, l2, 'H', direction)
    f = get_f(f1, f2, y1, y2)
    return f


def calc_f_C_1(region, glass_spec_category, direction, y1, y2, z):
    """ 開口部の冷房期の取得日射熱補正係数(面する方位に応じない求め方) 式(1)

    :param region: 省エネルギー地域区分
    :type region: int
    :param glass_spec_category: ガラスの仕様の区分
    :type glass_spec_category: str
    :param direction: 外皮の部位の方位
    :type direction: str
    :param y1: 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
    :type y1: float
    :param y2: 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm)
    :type y2: float
    :param z: 壁面からの日除けの張り出し寸法（軒等の出寸法は壁表面から先端までの寸法とする）(mm)
    :type z: float
    :return: 開口部の冷房期の取得日射熱補正係数(面する方位に応じない求め方) 式(1)
    :rtype: float
    """
    l1 = get_l1(y1, z)
    l2 = get_l2(y1, y2, z)
    f1 = get_glass_f(region, glass_spec_category, l1, 'C', direction)
    f2 = get_glass_f(region, glass_spec_category, l2, 'C', direction)
    f = get_f(f1, f2, y1, y2)
    return f


def get_glass_f(region, glass_spec_category, l, H_or_C, direction):
    """ lをパラメーターとして地域の区分及びガラスの仕様の区分に応じ、データ「取得日射熱補正係数」より算出した値

    :param region: 省エネルギー地域区分
    :type region: int
    :param glass_spec_category: ガラスの仕様の区分
    :type glass_spec_category: str
    :param l: パラメータ
    :type l: float
    :param H_or_CS: 計算対象
    :type H_or_CS: str
    :param direction: 外皮の部位の方位
    :type direction: str
    :return: 取得日射熱補正係数
    :rtype: float
    """
    glass_index = (glass_spec_category - 1) * 44
    if H_or_C == 'C':
        HC_index = 0
    elif H_or_C == 'H':
        HC_index = 22
    else:
        raise ValueError(H_or_C)

    dir_dic = {
        '北': 0, '北東': 1, '東': 2, '南東': 3, '南': 4, '南西': 5, '西': 6, '北西': 7
    }
    dir_index = dir_dic[direction]

    index_base = glass_index + HC_index

    region_index = 3 + (region - 1) * 8

    df = get_glass_f_table()
    f_cd = df[2][index_base:index_base + 22].values
    index = np.argwhere(f_cd == l)

    if len(index) == 1:
        # 按分不要の場合
        f = float(df[region_index + dir_index][index_base + index[0]])
    else:
        # 按分が必要な場合
        index_a = np.min(np.argwhere(f_cd > l)) - 1
        index_b = np.max(np.argwhere(f_cd < l)) + 1
        la = float(df[2][index_base + index_a])
        lb = float(df[2][index_base + index_b])
        fa = float(df[region_index + dir_index][index_base + index_a])
        fb = float(df[region_index + dir_index][index_base + index_b])

        f = fa + (fb - fa) / (lb - la) * (l - la)

    return f


@lru_cache()
def get_glass_f_table():
    """ データ「取得日射熱補正係数」

    :return: データ「取得日射熱補正係数」
    :rtype: DataFrame
    """
    path = os.path.join(os.path.dirname(__file__), 'data', 'glass_f.csv')
    df = pd.read_csv(path, header=None, skiprows=2)
    return df


def get_f(f1, f2, y1=0, y2=None):
    """ 開口部の取得日射熱補正係数(面する方位に応じない求め方) 式(1)

    :param f1: l1をパラメーターとして地域の区分及びガラスの仕様の区分に応じ、データ「取得日射熱補正係数」より算出した値
    :type f1: float
    :param f2: l２をパラメーターとして地域の区分及びガラスの仕様の区分に応じ、データ「取得日射熱補正係数」より算出した値
    :type f2: float
    :param y1: 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
    :type y1: float
    :param y2: 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm)
    :type y2: float
    :return: 開口部の取得日射熱補正係数(面する方位に応じない求め方) 式(1)
    :rtype: float
    """
    if y1 == 0:
        f = f2
    else:
        f = (f2 * (y1 + y2) - f1 * y1) / y2
    return f


def get_f_H_2(region, direction, y1, y2, z):
    """　開口部の暖房期の取得日射熱補正係数(面する方位に応じた求め方) (2)

    :param region: 省エネルギー地域区分
    :type region: int
    :param direction: 外皮の部位の方位
    :type direction: str
    :param y1: 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
    :type y1: float
    :param y2: 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm)
    :type y2: float
    :param z: 壁面からの日除けの張り出し寸法（軒等の出寸法は壁表面から先端までの寸法とする）(mm)
    :type z: float
    :return: 開口部の暖房期の取得日射熱補正係数
    :rtype:  float
    """
    if region in [1, 2, 3, 4, 5, 6, 7]:
        if direction in ['南東', '南', '南西']:
            # 暖房期における1地域から7地域までの南東面・南面・南西面 (2a)
            f_H = min(0.01 * (5 + 20 * (3 * y1 + y2) / z), 0.72)
        else:
            # 暖房期における1地域から7地域までの南東面・南面・南西面以外 (2b)
            f_H = min(0.01 * (10 + 15 * (2 * y1 + y2) / z), 0.72)
    elif region in [8]:
        return None
    else:
        raise ValueError(region)

    return f_H


def get_f_C_2(region, direction, y1, y2, z):
    """ 開口部の冷房期の取得日射熱補正係数(面する方位に応じた求め方) (3)

    :param region: 省エネルギー地域区分
    :type region: int
    :param direction: 外皮の部位の方位
    :type direction: str
    :param y1: 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
    :type y1: float
    :param y2: 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm)
    :type y2: float
    :param z: 壁面からの日除けの張り出し寸法（軒等の出寸法は壁表面から先端までの寸法とする）(mm)
    :type z: float
    :return: 開口部の冷房期の取得日射熱補正係数
    :rtype: float
    """
    if region in [1, 2, 3, 4, 5, 6, 7]:
        if direction in ['南東', '南', '南西']:
            # 冷房期における1地域から7地域までの南東面・南面・南西面 (3a)
            f_C = min(0.01 * (24 + 9 * (3 * y1 + y2) / z), 0.93)
        else:
            # 冷房期における1地域から7地域までの南東面・南面・南西面以外 (3b)
            f_C = min(0.01 * (16 + 24 * (2 * y1 + y2) / z), 0.93)
    elif region in [8]:
        if direction in ['南東', '南', '南西']:
            # 冷房期における8地域の南東面・南面・南西面 (3c)
            f_C = min(0.01 * (16 + 19 * (2 * y1 + y2) / z), 0.93)
        else:
            return None
    else:
        raise ValueError(region)

    return f_C


def get_l1(y1, z):
    """ 式 (4a)

    :param y1: 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
    :type y1: float
    :param z: 壁面からの日除けの張り出し寸法（ひさし等のオーバーハング型日除けの出寸法は壁表面から先端までの寸法とする）(mm)
    :type z: float
    :return: 式 (4a)
    :rtype: float
    """
    return y1 / z


def get_l2(y1, y2, z):
    """ 式 (4b)

    :param y1: 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
    :type y1: float
    :param y2: 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm)
    :type y2: float
    :param z: 壁面からの日除けの張り出し寸法（軒等の出寸法は壁表面から先端までの寸法とする）(mm)
    :type z: float
    :return: 式 (4b)
    :rtype: float
    """
    return (y1 + y2) / z
