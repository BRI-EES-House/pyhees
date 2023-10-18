# ============================================================================
# 第十一章 その他
# 第一節 地域の区分と外気条件
# Ver.04（エネルギー消費性能計算プログラム（住宅版）Ver.02.00～）
# ============================================================================

import os
import numpy as np
import pandas as pd
from functools import lru_cache
from pyhees.section11_5 import \
    calc_h_ex

# ============================================================================
# 4. 外気条件
# ============================================================================


@lru_cache()
def load_climate(region):
    """

    Args:
      region: 

    Returns:

    """
    csvpath =  os.path.join(os.path.dirname(__file__), 'data', 'climate', 'climateData_{}.csv'.format(region))
    return pd.read_csv(csvpath, nrows=24 * 365, encoding="SHIFT-JIS")


def get_Theta_ex(climate):
    """外気温度[℃]

    Args:
      climate(DateFrame): 外気条件

    Returns:
      ndarray: 1時間ごとの外気温度[℃]

    """
    return climate["外気温[℃]"].values


def get_X_ex(climate):
    """外気絶対湿度 [kg/kgDA]

    Args:
      climate(DateFrame): 外気条件

    Returns:
      ndarray: 1時間ごとの外気絶対湿度 [kg/kgDA]

    """
    return climate["外気絶対湿度 [kg/kgDA]"].values


def get_climate_df(climate):
    """

    Args:
      climate(DateFrame): 外気条件

    Returns:
      climate(DataFrame): 11_2のcalc_I_s_d_tで使用するDataFrame（法線面直達日射量、水平面全天日射量、太陽高度、太陽方位角）
    
    
    """
    df = pd.DataFrame({
            'I_DN': climate["法線面直達日射量 [W/m2]"].values,
            'I_Sky': climate["水平面天空日射量 [W/m2]"].values,
            'h': climate["太陽高度角[度]"].values,
            'A': climate["太陽方位角[度]"].values
        })
    
    return df


# ============================================================================
# 付録 A 外気相対湿度の計算方法
# ============================================================================

# ============================================================================
# A.2 外気相対湿度の計算方法
# ============================================================================

@lru_cache()
def load_outdoor():
    """気温[℃],絶湿[g/kg']

    Args:

    Returns:
      DateFrame: 気温[℃],絶湿[g/kg']

    """
    csvpath =  os.path.join(os.path.dirname(__file__), 'data', 'outdoor.csv')
    return pd.read_csv(csvpath, skiprows=4, nrows=24 * 365, names=(
    'day', 'hour', 'holiday', 'Theta_ex_1', 'X_ex_1', 'Theta_ex_2', 'X_ex_2', 'Theta_ex_3', 'X_ex_3', 'Theta_ex_4',
    'X_ex_4', 'Theta_ex_5', 'X_ex_5', 'Theta_ex_6', 'X_ex_6', 'Theta_ex_7', 'X_ex_7', 'Theta_ex_8', 'X_ex_8'))


# ============================================================================
# 付録 B 平均外気温度の計算方法
# ============================================================================

# ============================================================================
# B.2 年平均外気温度
# ============================================================================


def get_Theta_ex_a_Ave(Theta_ex_d_t):
    """年平均外気温度[℃] (1)

    Args:
      Theta_ex_d_t(ndarray): 外気絶対温度[K]

    Returns:
      ndarray: 年平均外気温度[℃]

    """
    return np.sum(Theta_ex_d_t) / 8760

# ============================================================================
# B.3 日平均外気温度
# ============================================================================


def get_Theta_ex_d_Ave_d(Theta_ex_d_t):
    """日付dにおける日平均外気温度[℃] (2)

    Args:
      Theta_ex_d_t(ndarray): 外気絶対温度[K]

    Returns:
      ndarray: 日付dにおける日平均外気温度

    """

    # 1次元配列を2次元配列に形状変換する
    Theta_ex_d_t = np.reshape(Theta_ex_d_t, (365, 24))

    # 時間軸を合計し、365日分の配列を返す
    return np.sum(Theta_ex_d_t, axis=1) / 24

# ============================================================================
# B.4 暖房期における期間平均外気温度
# ============================================================================


def get_Theta_ex_H_Ave(Theta_ex_d_t, L_H_x_t_i):
    """暖房期における期間平均外気温度[℃] (3a)

    Args:
      Theta_ex_d_t(ndarray): 外気絶対温度[K]
      L_H_x_t_i(ndarray): 暖冷房区画iの1時間当たりの暖房負荷

    Returns:
      ndarray: 暖房期における期間平均外気温度[℃]

    """

    # 暖房負荷が発生する日付の集合[-]
    D = get_D(L_H_x_t_i)

    # 1次元配列を2次元配列に形状変換する
    Theta_ex_d_t = np.reshape(Theta_ex_d_t, (365, 24))

    # 時間軸合算
    Theta_ex_d = np.sum(Theta_ex_d_t, axis=1)

    # 暖房期以外の外気温度を0とする
    Theta_ex_d[D == False] = 0

    # 暖房期における期間平均外気温度[℃]
    Theta_ex_H_Ave = np.sum(Theta_ex_d) / (24 * np.count_nonzero(D))

    return Theta_ex_H_Ave


def get_D(L_H_x_t_i):
    """暖房負荷が発生する日付の集合[-] (3b)

    Args:
      L_H_x_t_i(ndarray): 暖冷房区画iの1時間当たりの暖房負荷

    Returns:
      ndarray: 暖房負荷が発生する日付の集合

    """

    # L_H_x_t_iは暖冷房区画毎に365日×24時間分の負荷を持った2次元配列
    # 暖冷房区画軸合算(暖冷房区画の次元をなくす)
    L_H_x_t = np.sum(L_H_x_t_i, axis=0)

    # 1次元配列を2次元配列に形状変換する
    L_H_x_t = np.reshape(L_H_x_t, (365, 24))

    # 時間軸合算
    L_H_x = np.sum(L_H_x_t, axis=1)

    # 暖房日の判定（暖房負荷がある日はtrue、ない日はfalse）
    D = 0 < L_H_x

    # 暖房日の判定を行った365日分の配列を返す
    return D


if __name__ == '__main__':
    import numpy as np

    df = load_outdoor()

    for region in range(1, 9):
        # 外気温
        climate = load_climate(region)
        Theta_ex = get_Theta_ex(climate)

        # 絶対湿度
        X_ex = get_X_ex(climate)

        # 相対湿度
        h_ex = calc_h_ex(X_ex, Theta_ex)

        print('** 地域区分{0} **'.format(region))
        print('平均気温: {0} [K]'.format(np.average(Theta_ex)))
        print('平均絶対湿度: {0} [g/kg\']'.format(np.average(X_ex)))
        print('外気相対湿度: {0} [%]'.format(np.average(h_ex)))