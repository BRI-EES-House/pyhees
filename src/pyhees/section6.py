# ============================================================================
# 第六章 照明設備
# Ver.08（エネルギー消費性能計算プログラム（住宅版）Ver.02.02～）
# ============================================================================

import numpy as np
from functools import lru_cache

from pyhees.section11_3 import load_schedule, get_schedule_l


# ============================================================================
# 5. 照明設備の消費電力量
# ============================================================================


def calc_E_E_L_d_t(n_p, A_A, A_MR, A_OR, L):
    """1 時間当たりの照明設備の消費電力量（kWh/h）

    Args:
      n_p(float): 仮想居住人数
      A_A(float): 床面積の合計[m^2]
      A_MR(float): 主たる居室の床面積[m^2]
      A_OR(float): その他の居室の床面積[m^2]
      L(dict): 照明設備仕様辞書

    Returns:
      ndarray: E_E_L_d_t 日付dの時刻tにおける 1 時間当たりの照明設備の消費電力量[kWh/h]

    """

    if L is None:
        return np.zeros(24*365)

    def get_value(key):
        """

        Args:
          key: 

        Returns:

        """
        return L[key] if key in L else None

    # 1時間当たりの居住人数がp人における主たる居室の照明設備の消費電力量
    E_E_L_MR_d_t = calc_E_E_L_MR_d_t(
        n_p=n_p,
        A_A=A_A,
        A_MR=A_MR,
        A_OR=A_OR,
        MR_installed=get_value('MR_installed'),
        MR_power=get_value('MR_power'),
        MR_multi=get_value('MR_multi'),
        MR_dimming=get_value('MR_dimming')
    )

    # 1時間当たりの居住人数がp人におけるその他の居室の照明設備の消費電力量
    if L['has_OR']:
        E_E_L_OR_d_t = calc_E_E_L_OR_d_t(
            n_p=n_p,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            OR_installed=get_value('OR_installed'),
            OR_power=get_value('OR_power'),
            OR_dimming=get_value('OR_dimming')
        )
    else:
        E_E_L_OR_d_t = np.zeros(24 * 365)

    # 1時間当たりの居住人数がp人における非居室の照明設備の消費電力量
    if L['has_NO']:
        E_E_L_NO_d_t = calc_E_E_L_NO_d_t(
            n_p=n_p,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            NO_installed=get_value('NO_installed'),
            NO_power=get_value('NO_power'),
            NO_sensor=get_value('NO_sensor')
        )
    else:
        E_E_L_NO_d_t = np.zeros(24 * 365)

    return E_E_L_MR_d_t + E_E_L_OR_d_t + E_E_L_NO_d_t  # (1)


# ============================================================================
# 5.1 主たる居室
# ============================================================================

def calc_E_E_L_MR_d_t(n_p, A_A, A_MR, A_OR, MR_installed, MR_power=None, MR_multi=None, MR_dimming=None):
    """1 時間当たりの居住人数がp人における主たる居室の照明設備の消費電力量（kWh/h）

    Args:
      n_p(float): 仮想居住人数
      A_A(float): 床面積の合計[m^2]
      A_MR(float): 主たる居室の床面積[m^2]
      A_OR(float): その他の居室の床面積[m^2]
      MR_installed(str): 主たる居室の設置
      MR_power(str, optional): 主たる居室の照明器具の種類 (Default value = None)
      MR_multi(str, optional): 主たる居室の多灯分散照明方式の採用 (Default value = None)
      MR_dimming(str, optional): 主たる居室の調光が可能な制御の採用 (Default value = None)

    Returns:
      ndarray: E_E_L_MR_d_t: 日付dの時刻tにおける 1 時間当たりの居住人数がp人における主たる居室の照明設備の消費電力量[kWh/h]

    """
    # (2)
    if 1 <= n_p and n_p <= 2:
        E_E_L_MR_1_d_t = calc_E_E_L_MR_p_d_t(1, A_A, A_MR, A_OR, MR_installed, MR_power, MR_multi, MR_dimming)
        E_E_L_MR_2_d_t = calc_E_E_L_MR_p_d_t(2, A_A, A_MR, A_OR, MR_installed, MR_power, MR_multi, MR_dimming)
        return E_E_L_MR_1_d_t * (2 - n_p) / (2 - 1) + E_E_L_MR_2_d_t * (n_p - 1) / (2 - 1)
    elif 2 <= n_p and n_p <= 3:
        E_E_L_MR_2_d_t = calc_E_E_L_MR_p_d_t(2, A_A, A_MR, A_OR, MR_installed, MR_power, MR_multi, MR_dimming)
        E_E_L_MR_3_d_t = calc_E_E_L_MR_p_d_t(3, A_A, A_MR, A_OR, MR_installed, MR_power, MR_multi, MR_dimming)
        return E_E_L_MR_2_d_t * (3 - n_p) / (3 - 2) + E_E_L_MR_3_d_t * (n_p - 2) / (3 - 2)
    elif 3 <= n_p and n_p <= 4:
        E_E_L_MR_3_d_t = calc_E_E_L_MR_p_d_t(3, A_A, A_MR, A_OR, MR_installed, MR_power, MR_multi, MR_dimming)
        E_E_L_MR_4_d_t = calc_E_E_L_MR_p_d_t(4, A_A, A_MR, A_OR, MR_installed, MR_power, MR_multi, MR_dimming)
        return E_E_L_MR_3_d_t * (4 - n_p) / (4 - 3) + E_E_L_MR_4_d_t * (n_p - 3) / (4 - 3)


def calc_E_E_L_MR_p_d_t(p, A_A, A_MR, A_OR, MR_installed, MR_power, MR_multi, MR_dimming):
    """1 時間当たりの居住人数がp人における主たる居室の照明設備の消費電力量（kWh/h）

    Args:
      p(int): 居住人数
      A_A(float): 床面積の合計[m^2]
      A_MR(float): 主たる居室の床面積[m^2]
      A_OR(float): その他の居室の床面積[m^2]
      MR_installed(str): 主たる居室の設置
      MR_power(str): 主たる居室の照明器具の種類
      MR_multi(str): 主たる居室の多灯分散照明方式の採用
      MR_dimming(str): 主たる居室の調光が可能な制御の採用

    Returns:
      ndarray: E_E_L_MR_p_d_t 日付dの時刻tにおける 1 時間当たりの居住人数がp人における主たる居室の照明設備の消費電力量[kWh/h]

    """
    E_E_L_i_p_d_t = np.zeros((3, 24 * 365))
    for i in range(1, 4):
        E_E_L_i_p_d_t[i - 1] = calc_E_E_L_i_p_d_t(i, p, A_A, A_MR, A_OR, MR_installed, MR_power,
                                                  MR_multi, MR_dimming)
    # (3)
    E_E_L_MR_p_d_t = np.sum(E_E_L_i_p_d_t, axis=0)

    return E_E_L_MR_p_d_t


# ============================================================================
# 5.2 その他の居室
# ============================================================================

def calc_E_E_L_OR_d_t(n_p, A_A, A_MR, A_OR, OR_installed, OR_power, OR_dimming):
    """1 時間当たりの居住人数がp人におけるその他の居室の照明設備の消費電力量（kWh/h）

    Args:
      n_p(float): 仮想居住人数
      A_A(float): 床面積の合計[m^2]
      A_MR(float): 主たる居室の床面積[m^2]
      A_OR(float): その他の居室の床面積[m^2]
      OR_installed(str): その他の居室の設置
      OR_power(str): その他の居室の照明器具の種類
      OR_dimming(str): その他の居室の調光が可能な制御の採用

    Returns:
      ndarray: E_E_L_OR_d_t 日付dの時刻ｔにおける 1 時間当たりのその他の居室の照明設備の消費電力量[kWh/h]

    """
    # (4)
    if 1 <= n_p and n_p <= 2:
        E_E_L_OR_1_d_t = calc_E_E_L_OR_p_d_t(1, A_A, A_MR, A_OR, OR_installed, OR_power, OR_dimming)
        E_E_L_OR_2_d_t = calc_E_E_L_OR_p_d_t(2, A_A, A_MR, A_OR, OR_installed, OR_power, OR_dimming)
        return E_E_L_OR_1_d_t * (2 - n_p) / (2 - 1) + E_E_L_OR_2_d_t * (n_p - 1) / (2 - 1)
    elif 2 <= n_p and n_p <= 3:
        E_E_L_OR_2_d_t = calc_E_E_L_OR_p_d_t(2, A_A, A_MR, A_OR, OR_installed, OR_power, OR_dimming)
        E_E_L_OR_3_d_t = calc_E_E_L_OR_p_d_t(3, A_A, A_MR, A_OR, OR_installed, OR_power, OR_dimming)
        return E_E_L_OR_2_d_t * (3 - n_p) / (3 - 2) + E_E_L_OR_3_d_t * (n_p - 2) / (3 - 2)
    elif 3 <= n_p and n_p <= 4:
        E_E_L_OR_3_d_t = calc_E_E_L_OR_p_d_t(3, A_A, A_MR, A_OR, OR_installed, OR_power, OR_dimming)
        E_E_L_OR_4_d_t = calc_E_E_L_OR_p_d_t(4, A_A, A_MR, A_OR, OR_installed, OR_power, OR_dimming)
        return E_E_L_OR_3_d_t * (4 - n_p) / (4 - 3) + E_E_L_OR_4_d_t * (n_p - 3) / (4 - 3)


def calc_E_E_L_OR_p_d_t(p, A_A, A_MR, A_OR, OR_installed, OR_power, OR_dimming):
    """1 時間当たりの居住人数がp人におけるその他の居室の照明設備の消費電力量（kWh/h）

    Args:
      p(int): 居住人巣
      A_A(float): 床面積の合計[m^2]
      A_MR(float): 主たる居室の床面積[m^2]
      A_OR(float): その他の居室の床面積[m^2]
      OR_installed(str): その他の居室の設置
      OR_power(str): その他の居室の照明器具の種類
      OR_dimming(str): その他の居室の調光が可能な制御の採用

    Returns:
      ndarray: E_E_L_OR_p_d_t 日付dの時刻tにおける 1 時間当たりの居住人数がp人におけるその他の居室の照明設備の消費電力量[kWh/h]

    """
    E_E_L_i_p_d_t = np.zeros((4, 24 * 365))
    for i in range(4, 8):
        E_E_L_i_p_d_t[i - 4] = calc_E_E_L_i_p_d_t(i, p, A_A, A_MR, A_OR, OR_installed=OR_installed, OR_power=OR_power,
                                                  OR_dimming=OR_dimming)

    # (5)
    E_E_L_OR_p_d_t = np.sum(E_E_L_i_p_d_t, axis=0)

    return E_E_L_OR_p_d_t


# ============================================================================
# 5.3 非居室
# ============================================================================

def calc_E_E_L_NO_d_t(n_p, A_A, A_MR, A_OR, NO_installed, NO_power, NO_sensor):
    """1 時間当たりの非居室の照明設備の消費電力量（kWh/h）

    Args:
      n_p(float): 仮想居住人数
      A_A(float): 床面積の合計[m^2]
      A_MR(float): 主たる居室の床面積[m^2]
      A_OR(float): その他の居室の床面積[m^2]
      NO_installed(str): 非居室の設置
      NO_power(str): 非居室の照明器具の種類
      NO_sensor(str): 非居室の人感センサーの採用

    Returns:
      ndarray: E_E_L_NO_d_t 日付dの時刻tにおける 1 時間当たりの非居室の照明設備の消費電力量[kWh/h]

    """
    # (6)
    if 1 <= n_p and n_p <= 2:
        E_E_L_NO_1_d_t = calc_E_E_L_NO_p_d_t(1, A_A, A_MR, A_OR, NO_installed, NO_power, NO_sensor)
        E_E_L_NO_2_d_t = calc_E_E_L_NO_p_d_t(2, A_A, A_MR, A_OR, NO_installed, NO_power, NO_sensor)
        return E_E_L_NO_1_d_t * (2 - n_p) / (2 - 1) + E_E_L_NO_2_d_t * (n_p - 1) / (2 - 1)
    elif 2 <= n_p and n_p <= 3:
        E_E_L_NO_2_d_t = calc_E_E_L_NO_p_d_t(2, A_A, A_MR, A_OR, NO_installed, NO_power, NO_sensor)
        E_E_L_NO_3_d_t = calc_E_E_L_NO_p_d_t(3, A_A, A_MR, A_OR, NO_installed, NO_power, NO_sensor)
        return E_E_L_NO_2_d_t * (3 - n_p) / (3 - 2) + E_E_L_NO_3_d_t * (n_p - 2) / (3 - 2)
    elif 3 <= n_p and n_p <= 4:
        E_E_L_NO_3_d_t = calc_E_E_L_NO_p_d_t(3, A_A, A_MR, A_OR, NO_installed, NO_power, NO_sensor)
        E_E_L_NO_4_d_t = calc_E_E_L_NO_p_d_t(4, A_A, A_MR, A_OR, NO_installed, NO_power, NO_sensor)
        return E_E_L_NO_3_d_t * (4 - n_p) / (4 - 3) + E_E_L_NO_4_d_t * (n_p - 3) / (4 - 3)


def calc_E_E_L_NO_p_d_t(p, A_A, A_MR, A_OR, NO_installed, NO_power=None, NO_sensor=None):
    """1 時間当たりの居住人数がp人における非居室の照明設備の消費電力量（kWh/h）

    Args:
      p(int): 居住人数
      A_A(float): 床面積の合計[m^2]
      A_MR(float): 主たる居室の床面積[m^2]
      A_OR(float): その他の居室の床面積[m^2]
      NO_installed(str): 非居室の設置
      NO_power(str, optional): 非居室の照明器具の種類 (Default value = None)
      NO_sensor(str, optional): 非居室の人感センサーの採用 (Default value = None)

    Returns:
      ndarray: E_E_L_NO_p_d_t 日付dの時刻tにおける 1 時間当たりの居住人数がp人における非居室の照明設備の消費電力量[kWh/h]

    """
    E_E_L_i_p_d_t = np.zeros((11, 24 * 365))
    for i in range(8, 19):
        E_E_L_i_p_d_t[i - 8] = calc_E_E_L_i_p_d_t(i, p, A_A, A_MR, A_OR, NO_installed=NO_installed, NO_power=NO_power,
                                                  NO_sensor=NO_sensor)

    E_E_L_port_p_d_t = calc_E_E_L_port_p_d_t(p, NO_installed, NO_power, NO_sensor)
    # (7)
    E_E_L_NO_p_d_t = np.sum(E_E_L_i_p_d_t, axis=0) + E_E_L_port_p_d_t
    return E_E_L_NO_p_d_t


# ============================================================================
# 6. 照明区画に設置された照明設備
# ============================================================================

# ============================================================================
# 6.1 消費電力量
# ============================================================================

def calc_E_E_L_i_p_d_t(i, p, A_A, A_MR, A_OR, MR_installed=None, MR_power=None,
                       MR_multi=None, MR_dimming=None, OR_installed=None, OR_power=None, OR_dimming=None,
                       NO_installed=None, NO_power=None, NO_sensor=None):
    """1 時間当たりの居住人数がp人における照明区画݅に設置された照明設備の消費電力量（kWh/h）

    Args:
      i(int): 照明区画
      p(int): 居住人数
      A_A(float): 床面積の合計[m^2]
      A_MR(float): 主たる居室の床面積[m^2]
      A_OR(float): その他の居室の床面積[m^2]
      MR_installed(str, optional): 主たる居室の設置 (Default value = None)
      MR_power(str, optional): 主たる居室の照明器具の種類 (Default value = None)
      MR_multi(str, optional): 主たる居室の多灯分散照明方式の採用 (Default value = None)
      MR_dimming(str, optional): 主たる居室の調光が可能な制御の採用 (Default value = None)
      OR_installed(str, optional): その他の居室の設置 (Default value = None)
      OR_power(str, optional): その他の居室の照明器具の種類 (Default value = None)
      OR_dimming(str, optional): その他の居室の調光が可能な制御の採用 (Default value = None)
      NO_installed(str, optional): 非居室の設置 (Default value = None)
      NO_power(str, optional): 非居室の照明器具の種類 (Default value = None)
      NO_sensor(str, optional): 非居室の人感センサーの採用 (Default value = None)

    Returns:
      ndarray: E_E_L_i_p_d_t 日付dの時刻tにおける 1 時間当たりの居住人数がp人における照明区画iに設置された照明設備の消費電[kWh/h]

    """
    # 室内光束
    F_i = calc_F_i(i, A_A, A_MR, A_OR)

    # 平均総合効率, 特殊条件による補正係数....
    if i in [1, 2, 3]:
        Le_i = get_Le_MR(i, MR_installed, MR_power)
        Ce_i = get_Ce(i)
        Cd_i = get_Cd_MR(i, MR_installed, MR_dimming)
        Cs_i = get_Cs_MR()
        Cm_i = get_Cm_MR(i, MR_installed, MR_power, MR_multi)
        Ci_i = 1.0
    elif i in [4, 5, 6, 7]:
        Le_i = get_Le_OR(i, OR_installed, OR_power)
        Ce_i = get_Ce(i)
        Cd_i = get_Cd_OR(i, OR_installed, OR_dimming)
        Cs_i = get_Cs_OR()
        Cm_i = get_Cm_OR()
        Ci_i = 1.0
    elif i in [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]:
        Le_i = get_Le_NO(i, NO_installed, NO_power)
        Ce_i = get_Ce(i)
        Cd_i = get_Cd_NO()
        Cs_i = get_Cs_NO(i, NO_installed, NO_sensor)
        Cm_i = get_Cm_NO()
        Ci_i = 1.0
    else:
        raise ValueError(i)

    # 照明区画݅iに設置された照明設備の使用時間率
    r_i_p_d_t = get_r_i_p_d_t(i, p)

    return (F_i / Le_i * Ce_i) * Cd_i * Cs_i * Cm_i * Ci_i / 1000 * r_i_p_d_t  # (8)


# ============================================================================
# 6.2 室内光束
# ============================================================================

def calc_F_i(i, A_A, A_MR, A_OR):
    """室内光束の取得(9)

    Args:
      i(int): 照明区画
      A_A(float): 床面積の合計[m^2]
      A_MR(float): 主たる居室の床面積[m^2]
      A_OR(float): その他の居室の床面積[m^2]

    Returns:
      float: 照明区画iにおける室内光束

    """
    # 照明区画iの床面積
    A_LZ_i = get_A_LZ_i(i, A_A_act=A_A, A_MR_act=A_MR, A_OR_act=A_OR)

    # 照明区画iに設置される照明器具の種類, 設計照度
    lighting_device_type, E_i = get_table_3()[i - 1]


    if lighting_device_type == '拡散配光器具':
        return (232 * (A_LZ_i / 1.65) + 817) * (E_i / 50)  # (9a)
    elif lighting_device_type == '広照配光器具':
        return (177 * (A_LZ_i / 1.65) + 369) * (E_i / 50)  # (9b)
    else:
        raise ValueError(lighting_device_type)

def get_table_3() :
    """表3. 照明器具の種類及び設計照度

    Args:

    Returns:
      list: 表3. 照明器具の種類及び設計照度

    """
    table_3 = [
        ('拡散配光器具', 100),
        ('拡散配光器具', 100),
        ('拡散配光器具', 100),
        ('拡散配光器具', 100),
        ('拡散配光器具', 100),
        ('拡散配光器具', 100),
        ('拡散配光器具', 100),
        ('拡散配光器具', 100),
        ('拡散配光器具', 50),
        ('広照配光器具', 50),
        ('拡散配光器具', 50),
        ('広照配光器具', 50),
        ('拡散配光器具', 50),
        ('拡散配光器具', 50),
        ('広照配光器具', 50),
        ('広照配光器具', 100),
        ('広照配光器具', 50),
        ('拡散配光器具', 50)
    ]
    return table_3


# ============================================================================
# 6.3 平均総合効率
# ============================================================================

# ============================================================================
# 6.3.1 主たる居室
# ============================================================================

def get_Le_MR(i, MR_installed, MR_power=None):
    """主たる居室の照明区画iに設置された照明設備の平均総合効率の取得

    Args:
      i(int): 照明区画
      MR_installed(str): 主たる居室の設置
      MR_power(str, optional): 主たる居室の照明器具の種類 (Default value = None)

    Returns:
      float: Le_MR 主たる居室の照明区画iに設置された照明設備の平均総合効率

    """
    if MR_installed == '設置しない':
        return get_table_4()[i - 1][0]
    elif MR_installed == '設置する':
        if MR_power == 'すべての機器においてLEDを使用している':
            return get_table_4()[i - 1][0]
        elif MR_power == 'すべての機器において白熱灯以外を使用している':
            return get_table_4()[i - 1][1]
        elif MR_power == 'いずれかの機器において白熱灯を使用している':
            return get_table_4()[i - 1][2]
        else:
            raise ValueError(MR_power)
    else:
        raise ValueError(MR_installed)

def get_table_4():
    """表 4 主たる居室の照明区画݅に設置された照明設備の平均総合効率

    Args:

    Returns:
      list: 表 4 主たる居室の照明区画݅に設置された照明設備の平均総合効率

    """
    table_4 = [
        (90.0, 70.0, 42.5),
        (90.0, 70.0, 15.0),
        (90.0, 70.0, 42.5)
    ]
    return table_4


# ============================================================================
# 6.3.2 その他の居室
# ============================================================================

def get_Le_OR(i, OR_installed, OR_power=None):
    """その他の居室の照明区画iに設置された照明設備の平均総合効率の取得

    Args:
      i(int): 照明区画
      OR_installed(str): その他の居室の設置
      OR_power(str, optional): その他の居室の照明器具の種類 (Default value = None)

    Returns:
      float: Le_OR その他の居室の照明区画iに設置された照明設備の平均総合効率

    """
    if OR_installed == '設置しない':
        return get_table_5()[i - 4][0]
    elif OR_installed == '設置する':
        if OR_power == 'すべての機器においてLEDを使用している':
            return get_table_5()[i - 4][0]
        elif OR_power == 'すべての機器において白熱灯以外を使用している':
            return get_table_5()[i - 4][1]
        elif OR_power == 'いずれかの機器において白熱灯を使用している':
            return get_table_5()[i - 4][2]
        else:
            raise ValueError(OR_power)
    else:
        raise ValueError(OR_installed)


def get_table_5():
    """表 5 その他の居室の照明区画݅に設置された照明設備の平均総合効率

    Args:

    Returns:
      list: 表 5 その他の居室の照明区画݅に設置された照明設備の平均総合効率

    """
    table_5 = [
        (90.0, 70.0, 42.5),
        (90.0, 70.0, 42.5),
        (90.0, 70.0, 42.5),
        (90.0, 70.0, 42.5)
    ]
    return table_5


# ============================================================================
# 6.3.3 非居室
# ============================================================================

def get_Le_NO(i, NO_installed, NO_power=None):
    """非居室の照明区画iに設置された照明設備の平均総合効率

    Args:
      i(int): 照明区画
      NO_installed(str): 非居室の設置
      NO_power(str, optional): 非居室の照明器具の種類 (Default value = None)

    Returns:
      float: Le_NO 非居室の照明区画iに設置された照明設備の平均総合効率

    """
    if NO_installed == '設置しない':
        return get_table_6()[i - 8][0]
    elif NO_installed == '設置する':
        if NO_power == 'すべての機器においてLEDを使用している':
            return get_table_6()[i - 8][0]
        elif NO_power == 'すべての機器において白熱灯以外を使用している':
            return get_table_6()[i - 8][1]
        elif NO_power == 'いずれかの機器において白熱灯を使用している':
            return get_table_6()[i - 8][2]
        else:
            raise ValueError(NO_power)
    else:
        raise ValueError(NO_installed)

def get_table_6():
    """表 6 非居室の照明区画݅に設置された照明設備の平均総合効率

    Args:

    Returns:
      list: 表 6 非居室の照明区画݅に設置された照明設備の平均総合効率

    """
    table_6 = [
        (90.0, 70.0, 70.0),
        (90.0, 70.0, 15.0),
        (90.0, 70.0, 15.0),
        (90.0, 70.0, 15.0),
        (90.0, 70.0, 15.0),
        (90.0, 70.0, 15.0),
        (90.0, 70.0, 15.0),
        (90.0, 70.0, 15.0),
        (90.0, 70.0, 70.0),
        (90.0, 70.0, 15.0),
        (90.0, 70.0, 15.0),
    ]
    return table_6



# ============================================================================
# 6.4 特殊条件による補正係数
# ============================================================================

def get_Ce(i):
    """照明区画iに設置された照明設備の特殊条件による補正係数

    Args:
      i(int): 照明区画

    Returns:
      float: Ce 照明区画iに設置された照明設備の特殊条件による補正係数

    """
    return get_table_7()[i - 1]

def get_table_7():
    """表 7 照明区画݅に設置された照明設備の特殊条件による補正係数

    Args:

    Returns:
      list: 表 7 照明区画݅に設置された照明設備の特殊条件による補正係数

    """
    table_7 = [
        1.0,
        0.5,
        1.0,
        1.0,
        0.8,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        0.5,
        1.0,
        1.0,
        1.0,
        1.0,
        0.5,
        1.0
    ]
    return table_7



# ============================================================================
# 6.5 調光による補正係数
# ============================================================================

# ============================================================================
# 6.5.1 主たる居室
# ============================================================================

def get_Cd_MR(i, MR_installed, MR_dimming=None):
    """主たる居室の照明区画iに設置された照明設備の調光による補正係数

    Args:
      i(int): 照明区画
      MR_installed(str): 主たる居室の設置
      MR_dimming(str, optional): 主たる居室の調光が可能な制御の採用 (Default value = None)

    Returns:
      float: Cd_MR 主たる居室の照明区画iに設置された照明設備の調光による補正係数

    """
    if MR_installed == '設置しない':
        return get_table_8()[i - 1][1]
    elif MR_installed == '設置する':
        if MR_dimming == '採用する':
            return get_table_8()[i - 1][0]
        elif MR_dimming == '採用しない':
            return get_table_8()[i - 1][1]
        else:
            raise ValueError(MR_dimming)
    else:
        raise ValueError(MR_installed)


def get_table_8():
    """表 8 主たる居室の照明区画݅に設置された照明設備の調光による補正係数

    Args:

    Returns:
      list: 表 8 主たる居室の照明区画݅に設置された照明設備の調光による補正係数

    """
    table_8 = [
        (0.9, 1.0),
        (0.9, 1.0),
        (1.0, 1.0)
    ]
    return table_8


# ============================================================================
# 6.5.2 その他の居室
# ============================================================================

def get_Cd_OR(i, OR_installed, OR_dimming=None):
    """その他の居室の照明区画iに設置された照明設備の調光による補正係数

    Args:
      i(int): 照明区画
      OR_installed: type OR_installed:
      OR_dimming: type OR_dimming: (Default value = None)

    Returns:
      float: Cd_OR その他の居室の照明区画iに設置された照明設備の調光による補正係数

    """
    if OR_installed == '設置しない':
        return get_table_9()[i - 4][1]
    elif OR_installed == '設置する':
        if OR_dimming == '採用する':
            return get_table_9()[i - 4][0]
        elif OR_dimming == '採用しない':
            return get_table_9()[i - 4][1]
        else:
            raise ValueError(OR_dimming)
    else:
        raise ValueError(OR_installed)


def get_table_9():
    """表 9 その他の居室の照明区画݅に設置された照明設備の調光による補正係数

    Args:

    Returns:
      list: 表 9 その他の居室の照明区画݅に設置された照明設備の調光による補正係数

    """
    table_9 = [
        (0.9, 1.0),
        (0.9, 1.0),
        (0.9, 1.0),
        (0.9, 1.0)
    ]
    return table_9


# ============================================================================
# 6.5.3 非居室
# ============================================================================

def get_Cd_NO():
    """非居室の照明区画iに設置された照明設備の調光による補正係数

    Args:

    Returns:
      float: Cd_NO 非居室の照明区画iに設置された照明設備の調光による補正係数

    """
    return 1.0


# ============================================================================
# 6.6 人感センサーによる補正係数
# ============================================================================

# ============================================================================
# 6.6.1 主たる居室
# ============================================================================

def get_Cs_MR():
    """主たる居室の照明区画iに設置された照明設備の人感センサーによる補正係数

    Args:

    Returns:
      float: Cs_MR 主たる居室の照明区画iに設置された照明設備の人感センサーによる補正係数

    """
    return 1.0


# ============================================================================
# 6.6.2 その他の居室
# ============================================================================

def get_Cs_OR():
    """その他の居室の照明区画iに設置された照明設備の人感センサーによる補正係数

    Args:

    Returns:
      float: Cs_OR その他の居室の照明区画iに設置された照明設備の人感センサーによる補正係数

    """
    return 1.0


# ============================================================================
# 6.6.3 非居室
# ============================================================================

def get_Cs_NO(i, NO_installed, NO_sensor=None):
    """非居室の照明区画iに設置された照明設備の人感センサーによる補正係数

    Args:
      i(int): 照明区画
      NO_installed(str): 非居室の設置
      NO_sensor(str, optional): 非居室の人感センサーの採用 (Default value = None)

    Returns:
      float: 非居室の照明区画iに設置された照明設備の人感センサーによる補正係数

    """
    if NO_installed == '設置しない':
        return get_table_10()[i - 8][1]
    elif NO_installed == '設置する':
        if NO_sensor == '採用する':
            return get_table_10()[i - 8][0]
        elif NO_sensor == '採用しない':
            return get_table_10()[i - 8][1]
        else:
            raise ValueError(NO_sensor)
    else:
        raise ValueError(NO_installed)


def get_table_10():
    """表 10 非居室の照明区画݅に設置された照明設備の人感センサーによる補正係数

    Args:

    Returns:
      list: 表 10 非居室の照明区画݅に設置された照明設備の人感センサーによる補正係数

    """
    table_10 = [
        (1.0, 1.0),
        (1.0, 1.0),
        (0.9, 1.0),
        (0.9, 1.0),
        (0.9, 1.0),
        (0.9, 1.0),
        (0.9, 1.0),
        (0.9, 1.0),
        (1.0, 1.0),
        (0.9, 1.0),
        (0.9, 1.0)
    ]
    return  table_10


# ============================================================================
# 6.7 多灯分散照明方式による補正係数
# ============================================================================

# ============================================================================
# 6.7.1 主たる居室
# ============================================================================

def get_Cm_MR(i, MR_installed, MR_power=None, MR_multi=None):
    """主たる居室の照明区画iに設置された照明設備の多灯分散照明方式による補正係数

    Args:
      i(int): 照明区画
      MR_installed(str): 主たる居室の設置
      MR_power(str, optional): 主たる居室の照明器具の種類 (Default value = None)
      MR_multi(str, optional): 主たる居室の多灯分散照明方式の採用 (Default value = None)

    Returns:
      float: Cm_MR 主たる居室の照明区画iに設置された照明設備の多灯分散照明方式による補正係数

    """
    if MR_installed == '設置する' \
            and (MR_power == 'すべての機器においてLEDを使用している' or MR_power == 'すべての機器において白熱灯以外を使用している') \
            and MR_multi == '採用する':
        return get_table_11()[i - 1][0]
    else:
        return get_table_11()[i - 1][1]


def get_table_11():
    """表 11 主たる居室の照明区画݅に設置された照明設備の多灯分散照明方式による補正係数

    Args:

    Returns:
      list: 表 11 主たる居室の照明区画݅に設置された照明設備の多灯分散照明方式による補正係数

    """
    table_11 = [
        (0.8, 1.0),
        (1.0, 1.0),
        (1.0, 1.0)
    ]
    return table_11

# 照明設備の多灯分散照明方式の適用条件

# ============================================================================
# 6.7.2 その他の居室
# ============================================================================

def get_Cm_OR():
    """その他の居室の照明区画iに設置された照明設備の多灯分散照明方式による補正係数

    Args:

    Returns:
      float: Cm_OR その他の居室の照明区画iに設置された照明設備の多灯分散照明方式による補正係数

    """
    return 1.0


# ============================================================================
# 6.7.3 非居室
# ============================================================================

def get_Cm_NO():
    """非居室の照明区画iに設置された照明設備の多灯分散照明方式による補正係数

    Args:

    Returns:
      float: Cm_NO 非居室の照明区画iに設置された照明設備の多灯分散照明方式による補正係数

    """
    return 1.0


# ============================================================================
# 6.8 初期照度補正制御による補正係数
# ============================================================================

def get_Ci():
    """照明区画iに設置された照明設備の初期照度補正制御による補正係数

    Args:

    Returns:
      float: Ci 照明区画iに設置された照明設備の初期照度補正制御による補正係数

    """
    return 1.0


# ============================================================================
# 6.9 照明設備の使用時間率
# ============================================================================

# ============================================================================
# 7. 玄関ポーチに設置された照明設備
# ============================================================================

def calc_E_E_L_port_p_d_t(p, NO_installed, NO_power=None, NO_sensor=None):
    """1 時間当たりの居住人数がp人における玄関ポーチに設置された照明設備の消費電力量

    Args:
      p(int): 居住人数
      NO_installed(str): 非居室の設置
      NO_power(str, optional): 非居室の照明器具の種類 (Default value = None)
      NO_sensor(str, optional): 非居室の人感センサーの採用 (Default value = None)

    Returns:
      ndarray: E_E_L_port_p_d_t 日付dの時刻tにおける1時間当たりの居住人数がp人における玄関ポーチに設置された照明設備の消費電力量

    """
    # 玄関ポーチに設置された照明設備の消費電力
    P_port = get_P_port(NO_installed, NO_power)

    # 玄関ポーチに設置された照明設備の人感センサーによる補正係数
    Cs_port = get_Cs_port(NO_installed, NO_sensor)

    # 玄関ポーチに設置された照明設備の初期照度補正制御による補正係数
    Ci_port = 1.0

    # 玄関ポーチに設置された照明設備の使用時間率
    r_port_p_d_t = get_r_port_p_d_t(p)

    return P_port * Cs_port * Ci_port / 1000 * r_port_p_d_t  # (11)


def get_P_port(NO_installed, NO_power=None):
    """玄関ポーチに設置された照明設備の消費電力

    Args:
      NO_installed(str): 非居室の設置
      NO_power(str, optional): 非居室の照明器具の種類 (Default value = None)

    Returns:
      float: P_port 玄関ポーチに設置された照明設備の消費電力

    """
    if NO_installed == '設置しない':
        return get_table_12()[0]
    elif NO_installed == '設置する':
        if NO_power == 'すべての機器においてLEDを使用している':
            return get_table_12()[0]
        elif NO_power == 'すべての機器において白熱灯以外を使用している':
            return get_table_12()[1]
        elif NO_power == 'いずれかの機器において白熱灯を使用している':
            return get_table_12()[2]
        else:
            raise ValueError(NO_power)
    else:
        raise ValueError(NO_installed)


def get_table_12():
    """表 12 玄関ポーチに設置された照明設備の消費電力

    Args:

    Returns:
      list: 表 12 玄関ポーチに設置された照明設備の消費電力

    """
    table_12 = (10.0, 12.0, 54.0)
    return table_12


def get_Cs_port(NO_installed, NO_sensor):
    """玄関ポーチに設置された照明設備の人感センサーによる補正係数

    Args:
      NO_installed(str): 非居室の設置
      NO_sensor(str): 非居室の人感センサーの採用

    Returns:
      float: Cs_port 玄関ポーチに設置された照明設備の人感センサーによる補正係数

    """
    if NO_installed == '設置しない':
        return get_table_13()[1]
    elif NO_installed == '設置する':
        if NO_sensor == '採用する':
            return get_table_13()[0]
        elif NO_sensor == '採用しない':
            return get_table_13()[1]
        else:
            raise ValueError(NO_sensor)
    else:
        raise ValueError(NO_installed)


def get_table_13():
    """表 13 玄関ポーチに設置された照明設備の人感センサーによる補正係数

    Args:

    Returns:
      list: 表 13 玄関ポーチに設置された照明設備の人感センサーによる補正係数

    """
    table_13 = (0.9, 1.0)
    return table_13


# ============================================================================
# 付録 A 照明区画の床面積
# ============================================================================

def get_A_LZ_i(i, A_A_act, A_MR_act, A_OR_act):
    """照明区画iの床面積

    Args:
      i(int): 照明区画
      A_A_act(float): 当該住戸の床面積の合計[m^2]
      A_MR_act(float): 当該住戸の主たる居室の床面積[m^2]
      A_OR_act(float): 当該住戸のその他の居室の床面積[m^2]

    Returns:
      float: A_LZ_i 照明区画iの床面積

    """
    # 標準住戸における照明区画iの床面積
    A_LZ_R_i = get_A_LZ_R_i(i)

    # (1)
    if 1 <= i and i <= 3:
        return A_LZ_R_i * A_MR_act / 29.81
    elif 4 <= i and i <= 7:
        return A_LZ_R_i * A_OR_act / 51.34
    elif 8 <= i and i <= 18:
        return A_LZ_R_i * (A_A_act - A_MR_act - A_OR_act) / 38.93


def get_A_LZ_R_i(i):
    """標準住戸における照明区画iの床面積

    Args:
      i(int): 照明区画

    Returns:
      float: A_LZ_R_i 標準住戸における照明区画iの床面積

    """
    return get_table_a_1()[i - 1]


def get_table_a_1():
    """表 A.1 標準住戸における照明区画݅の床面積

    Args:

    Returns:
      list: 表 A.1 標準住戸における照明区画݅の床面積

    """
    table_a_1 = [
        13.031,
        7.929,
        7.194,
        13.031,
        12.816,
        10.587,
        10.373,
        3.094,
        3.097,
        1.601,
        4.699,
        5.168,
        1.242,
        3.301,
        1.496,
        0.773,
        6.800,
        4.699
    ]
    return table_a_1


# ============================================================================
# 付録 B 使用時間率
# ============================================================================

@lru_cache()
def get_r_i_p_d_t(i, p):
    """照明区画݅に設置された照明設備の使用時間率

    Args:
      i(int): 照明区画
      p(int): 居住人数

    Returns:
      ndarray: r_i_p_d_t 日付dの時刻tにおける居住人数がp人の場合の照明区画iに設置された照明設備の使用時間率

    """
    schedule = load_schedule()
    schedule_l = get_schedule_l(schedule)

    if p == 3:
        return (get_r_i_p_d_t(i, 2) + get_r_i_p_d_t(i, 4)) / 2
    else:
        if p == 4:
            table_a = get_table_b_1_a()
            table_b = get_table_b_1_b()
            table_c = get_table_b_1_c()
        elif p == 2:
            table_a = get_table_b_2_a()
            table_b = get_table_b_2_b()
            table_c = get_table_b_2_c()
        elif p == 1:
            table_a = get_table_b_3_a()
            table_b = get_table_b_3_b()
            table_c = get_table_b_3_c()
        else:
            raise ValueError(p)

        # 全日平日とみなした24時間365日の消費電力量
        tmp_a = np.tile([table_a[h][i - 1] for h in range(24)], 365)

        # 休日在宅とみなした24時間365日の消費電力量
        tmp_b = np.tile([table_b[h][i - 1] for h in range(24)], 365)

        # 休日外出とみなした24時間365日の消費電力量
        tmp_c = np.tile([table_c[h][i - 1] for h in range(24)], 365)

        # 時間単位に展開した生活パターン
        schedule_extend = np.repeat(schedule_l, 24)

        r_i_p_d_t = (tmp_a * (schedule_extend == '平日')
                    + tmp_b * (schedule_extend == '休日在')
                    + tmp_c * (schedule_extend == '休日外'))

        return r_i_p_d_t


def get_r_port_p_d_t(p):
    """玄関ポーチに設置された照明設備の使用時間率

    Args:
      p(int): 居住人数

    Returns:
      ndarray: r_port_p_d_t 日付dの時刻tにおける居住人数がp人の場合の玄関ポーチに設置された照明設備の使用時間率

    """
    return get_r_i_p_d_t(19, p)


def get_table_b_1_a():
    """表 B.1 居住人数 4 人における照明設備の使用時間率 (a) 平日

    Args:

    Returns:
      list: 表 B.1 居住人数 4 人における照明設備の使用時間率 (a) 平日

    """
    table_b_1_a = [
        (0.00, 0.00, 0.00, 0.00, 0.25, 0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.25, 0.25, 0.25, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (0.25, 0.50, 0.50, 0.00, 0.00, 0.25, 0.25, 0.50, 0.00, 0.50, 0.25, 0.50, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
        (0.75, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.50, 0.00, 0.50, 0.50, 0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.00),
        (0.75, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.25, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.25, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.25, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.25, 0.25, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.00, 0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25),
        (1.00, 0.00, 1.00, 0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25),
        (0.25, 0.75, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.25, 0.00, 0.00, 0.75, 0.25, 0.25, 0.50, 0.25, 0.00, 0.75, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.50, 1.00, 0.50, 0.50, 0.50, 0.00, 1.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 1.00, 0.75, 0.25, 0.50, 0.25, 0.00, 0.75, 0.00, 0.00, 0.25, 0.25, 0.25, 0.00, 0.00),
    ]
    return table_b_1_a


def get_table_b_1_b():
    """表 B.1 居住人数 4 人における照明設備の使用時間率 (b) 休日在宅

    Args:

    Returns:
      list: 表 B.1 居住人数 4 人における照明設備の使用時間率 (b) 休日在宅

    """
    table_b_1_b = [
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.25, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (0.25, 0.25, 0.25, 0.00, 0.25, 0.25, 0.25, 1.00, 0.00, 0.50, 0.00, 1.00, 0.00, 0.50, 0.00, 0.00, 0.50, 0.25, 0.00),
        (1.00, 0.50, 0.50, 0.25, 0.25, 0.25, 0.75, 0.75, 0.00, 0.25, 0.00, 0.75, 0.00, 0.50, 0.00, 0.00, 0.50, 0.25, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 1.00, 1.00, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 1.00, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.75, 0.25, 0.25, 0.00, 0.00, 0.50, 0.75, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.50, 0.00, 0.00, 0.50, 0.00, 0.00),
        (0.50, 0.25, 0.50, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.50, 0.00, 0.00, 0.50, 0.00, 0.00, 0.50, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.00, 0.00, 0.00, 0.00, 0.50, 0.00, 0.00, 0.50, 0.00, 0.25, 0.50, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 1.00, 0.00, 0.25, 0.25, 0.25, 0.25, 0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25),
        (1.00, 0.00, 1.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
        (1.00, 0.00, 0.50, 0.00, 0.00, 0.50, 0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.75, 1.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.50, 1.00, 0.50, 0.50, 0.50, 0.00, 1.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
        (0.50, 0.00, 0.00, 0.00, 0.50, 0.50, 0.50, 0.25, 0.50, 0.25, 0.00, 0.75, 0.00, 0.50, 0.25, 0.25, 0.50, 0.00, 0.00),
    ]
    return table_b_1_b


def get_table_b_1_c():
    """表 B.1 居住人数 4 人における照明設備の使用時間率 (c) 休日外出

    Args:

    Returns:
      list: 表 B.1 居住人数 4 人における照明設備の使用時間率 (c) 休日外出

    """
    table_b_1_c = [
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (0.75, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.25, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.75, 0.00, 0.50, 0.00, 0.25, 0.25, 0.25, 0.75, 0.00, 0.50, 0.00, 0.75, 0.00, 0.75, 0.00, 0.00, 0.75, 0.25, 0.00),
        (0.25, 0.25, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.25, 0.50, 0.25, 0.00, 0.75, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.50, 1.00, 0.50, 0.50, 0.50, 0.00, 1.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
        (0.50, 0.00, 0.00, 0.00, 0.50, 0.50, 0.50, 0.25, 0.50, 0.25, 0.00, 0.75, 0.00, 0.50, 0.25, 0.25, 0.75, 0.00, 0.00),
    ]
    return table_b_1_c


# 表 B.2 居住人数 2 人における照明設備の使用時間率
def get_table_b_2_a():
    """表 B.2 居住人数 2 人における照明設備の使用時間率 (a) 平日

    Args:

    Returns:
      list: 表 B.2 居住人数 2 人における照明設備の使用時間率 (a) 平日

    """
    table_b_2_a = [
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.25, 0.00, 0.50, 0.00, 0.00, 0.50, 0.00, 0.50, 0.00, 0.50, 0.00, 0.50, 0.00, 0.00, 0.50, 0.50, 0.00),
        (0.25, 0.50, 0.25, 0.00, 0.00, 0.00, 0.00, 0.50, 0.00, 0.00, 0.25, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.25, 0.25, 0.00, 0.25, 0.00, 0.00, 0.50, 0.25, 0.25, 0.25, 0.50, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.50, 0.00, 0.25, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.25, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.25, 0.00, 0.75, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.75, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25),
        (1.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.50, 0.25, 0.00, 0.75, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.75, 0.00, 0.00, 0.00, 0.50, 0.00, 0.00, 0.25, 0.25, 0.25, 0.00, 0.50, 0.00, 0.50, 0.00, 0.00, 0.50, 0.00, 0.00),
    ]
    return table_b_2_a


def get_table_b_2_b():
    """表 B.2 居住人数 2 人における照明設備の使用時間率 (b) 休日在宅

    Args:

    Returns:
      list: 表 B.2 居住人数 2 人における照明設備の使用時間率 (b) 休日在宅

    """
    table_b_2_b = [
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.25, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.50, 0.00, 0.25, 0.00, 0.50, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (0.50, 0.25, 0.50, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.25, 0.00, 0.25, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (0.75, 0.25, 0.25, 0.00, 0.25, 0.00, 0.00, 0.75, 0.25, 0.25, 0.25, 0.25, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.50, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.25, 0.25, 0.25, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.25, 0.25, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25),
        (1.00, 0.00, 0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.50, 0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.75, 0.25, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.50, 0.25, 0.00, 0.75, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.25, 0.00, 0.50, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
    ]
    return table_b_2_b


def get_table_b_2_c():
    """表 B.2 居住人数 2 人における照明設備の使用時間率 (c) 休日外出

    Args:

    Returns:
      list: 表 B.2 居住人数 2 人における照明設備の使用時間率 (c) 休日外出

    """
    table_b_2_c = [
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.75, 0.00, 0.25, 0.00, 0.25, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (0.25, 0.25, 0.50, 0.00, 0.25, 0.00, 0.00, 0.50, 0.00, 0.25, 0.00, 0.50, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (0.75, 0.25, 0.25, 0.00, 0.25, 0.00, 0.00, 0.75, 0.25, 0.50, 0.25, 0.75, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.50, 0.25, 0.00, 0.75, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.25, 0.00, 0.50, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
    ]
    return table_b_2_c


def get_table_b_3_a():
    """表 B.3 居住人数 1 人における照明設備の使用時間率 (a) 平日

    Args:

    Returns:
      list: 表 B.3 居住人数 1 人における照明設備の使用時間率 (a) 平日

    """
    table_b_3_a = [
        (0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.25, 0.00, 0.50, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.25, 0.25, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.25, 0.00, 0.25, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25),
        (0.50, 0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
    ]
    return table_b_3_a


def get_table_b_3_b():
    """表 B.3 居住人数 1 人における照明設備の使用時間率 (b) 休日在宅

    Args:

    Returns:
      list: 表 B.3 居住人数 1 人における照明設備の使用時間率 (b) 休日在宅

    """
    table_b_3_b = [
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.25, 0.25, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.25, 0.00, 0.25, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (0.25, 0.25, 0.50, 0.00, 0.25, 0.00, 0.00, 0.50, 0.00, 0.00, 0.00, 0.50, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.50, 0.25, 0.50, 0.50, 0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.25, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.25, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.75, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.75, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.25, 0.00, 0.50, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
    ]
    return table_b_3_b


def get_table_b_3_c():
    """表 B.3 居住人数 1 人における照明設備の使用時間率 (c) 休日外出

    Args:

    Returns:
      list: 表 B.3 居住人数 1 人における照明設備の使用時間率 (c) 休日外出

    """
    table_b_3_c = [
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.25, 0.25, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.25, 0.00, 0.25, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (0.25, 0.25, 0.50, 0.00, 0.25, 0.00, 0.00, 0.50, 0.00, 0.00, 0.00, 0.50, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.50, 0.25, 0.50, 0.50, 0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.25),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.00, 0.00, 0.25, 0.00, 0.00, 0.25, 0.25, 0.25, 0.00, 0.50, 0.00, 0.25, 0.00, 0.00, 0.25, 0.00, 0.00),
    ]
    return table_b_3_c
