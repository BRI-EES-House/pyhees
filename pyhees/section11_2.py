# ============================================================================
# 第十一章 その他
# 第二節 日射に関する地域区分と日射量
# Ver.04（エネルギー消費性能計算プログラム（住宅版）Ver.02～）
# ============================================================================

import os
import numpy as np
import pandas as pd
from functools import lru_cache


# ============================================================================
# 付録 A 傾斜面における単位面積当たりの平均日射量
# ============================================================================

# ============================================================================
# A.2 傾斜面における単位面積当たりの平均日射量の計算方法
# ============================================================================

@lru_cache()
def load_solrad(region, sol_region):
    """日射量データの読み込み

    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :return: 日射量データ
    :rtype: DateFrame
    """
    posnum = get_position_num(region, sol_region)
    csvpath =  os.path.join(os.path.dirname(__file__), 'data', 'solar', '%s.csv' % posnum)
    return pd.read_csv(csvpath, skiprows=2, nrows=24 * 365,
                       names=('T_ex', 'I_DN', 'I_Sky', 'h', 'A'))


def get_position_num(region, sol_region):
    """地域区分、日射地域区分から地域番号

    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :return: 地域区分、日射地域区分から地域番号
    :rtype: str
    """
    nums = [
        ['7', '117', '124', '-', '-'],
        ['49', '63', '59', '2A4', '2A5'],
        ['190', '230', '426', '403', '412'],
        ['286', '186', '292', '423', '401'],
        ['593', '542', '495', '473', '420'],
        ['-', '569', '551', '480', '438'],
        ['819-A1', '819-A2', '819', '798', '797'],
        ['-', '-', '826', '836', '842']
    ]
    return nums[region - 1][sol_region - 1]


def get_Theta_ex(df):
    """外気温度

    :param df: 気温[℃],絶湿[g/kg']
    :type df: DataFrame
    :return: 外気温度
    :rtype: ndarray
    """
    return df['T_ex'].values


def calc_I_s_d_t(P_alpha, P_beta, df):
    """傾斜面の単位面積当たりの平均日射量

    :param P_alpha: 方位角 (°)
    :type P_alpha: float
    :param P_beta: 傾斜角 (°)
    :type P_beta: float
    :param df: load_solrad の返り値
    :type df: DateFrame
    :return: 傾斜面の単位面積当たりの平均日射量
    :rtype: ndarray
    """
    I_DN_d_t = df['I_DN'].values / 3.6 * 1000
    I_Sky_d_t = df['I_Sky'].values / 3.6 * 1000
    h_d_t = np.radians(df['h'].values)
    A_d_t = np.radians(df['A'].values * (df['A'].values >= 0) + (df['A'].values + 360.0) * (df['A'].values < 0))

    I_D_d_t = get_I_D_d_t(I_DN_d_t, h_d_t, P_alpha, P_beta, A_d_t)
    I_d_d_t = get_I_d_d_t(I_Sky_d_t, P_beta)

    return I_D_d_t * (I_D_d_t >= 0) + I_d_d_t


def get_I_D_d_t(I_DN_d_t, h_d_t, P_alpha, P_beta, A_d_t):
    """傾斜面の単位面積当たりの直達日射量

    :param I_DN_d_t: 法線面直達日射量
    :type I_DN_d_t: ndarray
    :param h_d_t: 太陽高度
    :type h_d_t: ndarray
    :param P_alpha: 方位角 (°)
    :type P_alpha: float
    :param P_beta: 傾斜角 (°)
    :type P_beta: float
    :param A_d_t: 太陽方位角 (°)
    :type A_d_t: ndarray
    :return: 傾斜面の単位面積当たりの直達日射量
    :rtype: ndarray
    """
    return I_DN_d_t * (np.sin(h_d_t) * np.cos(P_beta) + np.cos(h_d_t) * np.sin(P_beta) * np.cos(P_alpha - A_d_t))


def get_I_d_d_t(I_Sky_d_t, P_beta):
    """傾斜面の単位面積当たりの天空放射量

    :param I_Sky_d_t: 水平面天空日射量
    :type I_Sky_d_t: ndarray
    :param P_beta: 傾斜角 (°)
    :type P_beta: float
    :return: 傾斜面の単位面積当たりの天空放射量
    :rtype: ndarray
    """
    return I_Sky_d_t * ((1.0 + np.cos(P_beta)) / 2.0)


if __name__ == "__main__":
    df = load_solrad(5, 3)
    print(np.average(get_Theta_ex(df)))
    print(calc_I_s_d_t(1, 0.5, df).sum())
