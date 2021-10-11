# 付録A 一般部位及び大部分がガラスで構成されていないドア等の開口部における日除けの効果係数

import os
import pandas as pd
import numpy as np
from functools import lru_cache

def get_gamma_H_i_default():
    """暖房期の日除けの効果係数

    Args:

    Returns:
      float: 暖房期の日除けの効果係数

    """
    return 1.0


def get_gamma_C_i_default():
    """冷房期の日除けの効果係数

    Args:

    Returns:
      float: 冷房期の日除けの効果係数

    """
    return 1.0


def get_gamma(y1, y2, gamma1, gamma2):
    """一般部位及び大部分がガラスで構成されていないドア等の開口部における日除けの効果係数 (-)

    Args:
      y1(float): 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
      y2(float): 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm)
      gamma1(float): データ「日除けの効果係数」より算出した値
      gamma2(float): データ「日除けの効果係数」より算出した値

    Returns:
      float: 一般部位及び大部分がガラスで構成されていないドア等の開口部における日除けの効果係数

    """
    gamma = (gamma2 * (y1 + y2) - gamma1 * y1) / y2
    return gamma


def get_l1(y1, z):
    """l1 (2a)

    Args:
      y1(float): 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
      z(float): 壁面からの日除けの張り出し寸法（軒等の出寸法は壁表面から先端までの寸法とする）(mm)

    Returns:
      float: l1

    """
    l1 = y1 / z
    return l1


def get_l2(y1, y2, z):
    """l2 (2b)

    Args:
      y1(float): 日除け下端から一般部及び大部分がガラスで構成されていないドア等の開口部の上端までの垂直方向距離 (mm)
      y2(float): 一般部及び大部分がガラスで構成されていないドア等の開口部の高さ寸法 (mm)
      z(float): 壁面からの日除けの張り出し寸法（軒等の出寸法は壁表面から先端までの寸法とする）(mm)

    Returns:
      float: l2

    """
    return (y1 + y2) / z




def get_blind_gamma_f(region, l, H_or_C, direction):
    """lをパラメーターとして地域の区分及びガラスの仕様の区分に応じ、データ「日除けの効果係数」より算出した値

    Args:
      region(int): 省エネルギー地域区分
      l(float): パラメータ
      H_or_CS(str): 計算対象
      direction(str): 外皮の部位の方位
      H_or_C: returns: 日除けの効果係数

    Returns:
      float: 日除けの効果係数

    """
    
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

    index_base = HC_index

    region_index = 2 + (region - 1) * 8

    df = get_blind_gamma_table()
    f_cd = df[1][index_base:index_base + 22].to_numpy()
    index = np.argwhere(f_cd == l)

    
    if len(index) == 1:
        # 按分不要の場合
        f = float(df[region_index + dir_index][index_base + index[0]])
    else:
        # 按分が必要な場合
        index_a = np.min(np.argwhere(f_cd > l)) - 1
        index_b = np.max(np.argwhere(f_cd < l)) + 1
        la = float(df[1][index_base + index_a])
        lb = float(df[1][index_base + index_b])
        fa = float(df[region_index + dir_index][index_base + index_a])
        fb = float(df[region_index + dir_index][index_base + index_b])

        f = fa + (fb - fa) / (lb - la) * (l - la)

    return f
    


@lru_cache()
def get_blind_gamma_table():
    """データ「日除けの効果係数」

    Args:

    Returns:
      DataFrame: データ「日除けの効果係数」

    """
    path = os.path.join(os.path.dirname(__file__), 'data', '3-blind_gamma')
    df = pd.read_csv(path, header=None, skiprows=2)
    return df
