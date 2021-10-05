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
    """開口部の暖房期の取得日射熱補正係数(面する方位に応じない求め方) 式(1)

    Args:
      region(int): 省エネルギー地域区分
      glass_spec_category(str): ガラスの仕様の区分
      direction(str): 外皮の部位の方位
      y1(float): 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
      y2(float): 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm)
      z(float): 壁面からの日除けの張り出し寸法（軒等の出寸法は壁表面から先端までの寸法とする）(mm)

    Returns:
      float: 開口部の暖房期の取得日射熱補正係数(面する方位に応じない求め方) 式(1)

    """
    l1 = get_l1(y1, z)
    l2 = get_l2(y1, y2, z)
    f1 = get_glass_f(region, glass_spec_category, l1, 'H', direction)
    f2 = get_glass_f(region, glass_spec_category, l2, 'H', direction)
    f = get_f(f1, f2, y1, y2)
    return f


def calc_f_C_1(region, glass_spec_category, direction, y1, y2, z):
    """開口部の冷房期の取得日射熱補正係数(面する方位に応じない求め方) 式(1)

    Args:
      region(int): 省エネルギー地域区分
      glass_spec_category(str): ガラスの仕様の区分
      direction(str): 外皮の部位の方位
      y1(float): 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
      y2(float): 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm)
      z(float): 壁面からの日除けの張り出し寸法（軒等の出寸法は壁表面から先端までの寸法とする）(mm)

    Returns:
      float: 開口部の冷房期の取得日射熱補正係数(面する方位に応じない求め方) 式(1)

    """
    l1 = get_l1(y1, z)
    l2 = get_l2(y1, y2, z)
    f1 = get_glass_f(region, glass_spec_category, l1, 'C', direction)
    f2 = get_glass_f(region, glass_spec_category, l2, 'C', direction)
    f = get_f(f1, f2, y1, y2)
    return f


def get_glass_f(region, glass_spec_category, l, H_or_C, direction):
    """lをパラメーターとして地域の区分及びガラスの仕様の区分に応じ、データ「取得日射熱補正係数」より算出した値

    Args:
      region(int): 省エネルギー地域区分
      glass_spec_category(str): ガラスの仕様の区分
      l(float): パラメータ
      H_or_CS(str): 計算対象
      direction(str): 外皮の部位の方位
      H_or_C: returns: 取得日射熱補正係数

    Returns:
      float: 取得日射熱補正係数

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
    """データ「取得日射熱補正係数」

    Args:

    Returns:
      DataFrame: データ「取得日射熱補正係数」

    """
    path = os.path.join(os.path.dirname(__file__), 'data', 'glass_f.csv')
    df = pd.read_csv(path, header=None, skiprows=2)
    return df


def get_f(f1, f2, y1=0, y2=None):
    """開口部の取得日射熱補正係数(面する方位に応じない求め方) 式(1)

    Args:
      f1(float): l1をパラメーターとして地域の区分及びガラスの仕様の区分に応じ、データ「取得日射熱補正係数」より算出した値
      f2(float): l２をパラメーターとして地域の区分及びガラスの仕様の区分に応じ、データ「取得日射熱補正係数」より算出した値
      y1(float, optional): 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm) (Default value = 0)
      y2(float, optional): 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm) (Default value = None)

    Returns:
      float: 開口部の取得日射熱補正係数(面する方位に応じない求め方) 式(1)

    """
    if y1 == 0:
        f = f2
    else:
        f = (f2 * (y1 + y2) - f1 * y1) / y2
    return f


def get_f_H_2(region, direction, y1, y2, z):
    """開口部の暖房期の取得日射熱補正係数(面する方位に応じた求め方) (2)

    Args:
      region(int): 省エネルギー地域区分
      direction(str): 外皮の部位の方位
      y1(float): 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
      y2(float): 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm)
      z(float): 壁面からの日除けの張り出し寸法（軒等の出寸法は壁表面から先端までの寸法とする）(mm)

    Returns:
      float: 開口部の暖房期の取得日射熱補正係数

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
    """開口部の冷房期の取得日射熱補正係数(面する方位に応じた求め方) (3)

    Args:
      region(int): 省エネルギー地域区分
      direction(str): 外皮の部位の方位
      y1(float): 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
      y2(float): 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm)
      z(float): 壁面からの日除けの張り出し寸法（軒等の出寸法は壁表面から先端までの寸法とする）(mm)

    Returns:
      float: 開口部の冷房期の取得日射熱補正係数

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
    """式 (4a)

    Args:
      y1(float): 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
      z(float): 壁面からの日除けの張り出し寸法（ひさし等のオーバーハング型日除けの出寸法は壁表面から先端までの寸法とする）(mm)

    Returns:
      float: 式 (4a)

    """
    return y1 / z


def get_l2(y1, y2, z):
    """式 (4b)

    Args:
      y1(float): 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
      y2(float): 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm)
      z(float): 壁面からの日除けの張り出し寸法（軒等の出寸法は壁表面から先端までの寸法とする）(mm)

    Returns:
      float: 式 (4b)

    """
    return (y1 + y2) / z
