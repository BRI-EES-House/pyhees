# ============================================================================
# 第四章 暖冷房設備
# 第三節 ルームエアコンディショナー
# Ver.03（エネルギー消費性能計算プログラム（住宅版）Ver.02～）
# ============================================================================

import numpy as np
from math import floor

from pyhees.section4_1_Q import \
    get_Q_T_H_d_t_i, \
    get_Q_T_CS_d_t_i, \
    get_Q_T_CL_d_t_i

from pyhees.section4_3_a import \
    get_q_max_H, \
    get_q_rtd_C, \
    get_q_max_C

from pyhees.section11_1 import \
    load_outdoor, \
    get_Theta_ex, \
    get_X_ex, \
    calc_h_ex


# ============================================================================
# 5 最大暖房出力
# ============================================================================

# 最大暖房出力 (1)
def calc_Q_max_H_d_t(Q_r_max_H_d_t, q_rtd_H, Theta_ex, h_ex):
    """最大暖房出力 (1)

    Args:
      Q_r_max_H_d_t(ndarray): 最大暖房出力比
      q_rtd_H(float): 定格暖房能力
      Theta_ex(ndarray): 外気温度
      h_ex(ndarray): 外気相対湿度

    Returns:
      ndarray: 最大暖房出力

    """
    # 室内機吹き出し風量に関する暖房時の能力補正係
    C_af_H = get_C_af_H()

    # デフロストに関する暖房出力補正係数
    C_df_H_d_t = get_C_df_H(Theta_ex, h_ex)

    return Q_r_max_H_d_t * q_rtd_H * C_af_H * C_df_H_d_t * 3600 * 10 ** (-6)


# 最大暖房出力比 (2)
def calc_Q_r_max_H_d_t(q_rtd_C, q_r_max_H, Theta_ex_d_t):
    """最大暖房出力比

    Args:
      q_rtd_C(float): 定格冷房能力
      q_r_max_H(float): 最大暖房能力比
      Theta_ex_d_t(ndarray): 外気温度

    Returns:
      ndarray: 最大暖房出力比

    """
    # 係数a2及びa2,a0
    a2, a1, a0 = calc_a_eq3(q_r_max_H, q_rtd_C)

    return a2 * (Theta_ex_d_t - 7) ** 2 + a1 * (Theta_ex_d_t - 7) + a0


# 係数a2及びa1,a0 (3a)
def calc_a_eq3(q_r_max_H, q_rtd_C):
    """係数a2及びa1,a0 (3a)

    Args:
      q_r_max_H(float): 最大暖房能力比
      q_rtd_C(float): 定格冷房能力

    Returns:
      tuple: 係数a2及びa1,a0 (3a)

    """
    b2, b1, b0 = get_b_eq3(q_rtd_C)
    c2, c1, c0 = get_c_eq3(q_rtd_C)
    a2 = b2 * q_r_max_H + c2
    a1 = b1 * q_r_max_H + c1
    a0 = b0 * q_r_max_H + c0
    return a2, a1, a0


# 係数b2及びb1,b0 (3b)
def get_b_eq3(q_rtd_C):
    """係数b2及びb1,b0 (3b)

    Args:
      q_rtd_C(float): 定格冷房能力

    Returns:
      tuple: 係数b2及びb1,b0

    """
    q_rtd_C = min(5600, q_rtd_C)
    b2 = 0.000181 * q_rtd_C * 10 ** (-3) - 0.000184
    b1 = 0.002322 * q_rtd_C * 10 ** (-3) + 0.013904
    b0 = 0.003556 * q_rtd_C * 10 ** (-3) + 0.993431
    return b2, b1, b0


# 係数c2及びc1,c0 (3b)
def get_c_eq3(q_rtd_C):
    """係数c2及びc1,c0 (3b)

    Args:
      q_rtd_C(float): 定格冷房能力

    Returns:
      tuple: 係数c2及びc1,c0

    """
    q_rtd_C = min(5600, q_rtd_C)
    c2 = -0.000173 * q_rtd_C * 10 ** (-3) + 0.000367
    c1 = -0.003980 * q_rtd_C * 10 ** (-3) + 0.003983
    c0 = -0.002870 * q_rtd_C * 10 ** (-3) + 0.006376
    return c2, c1, c0


# 最大暖房能力比 (4)
def get_q_r_max_H(q_max_H, q_rtd_H):
    """最大暖房能力比 (4)

    Args:
      q_max_H(float): 最大暖房能力
      q_rtd_H(float): 定格暖房能力

    Returns:
      float: 最大暖房能力比

    """
    q_r_max_H = q_max_H / q_rtd_H
    return q_r_max_H


# 室内機吹き出し風量に関する暖房時の能力補正係
def get_C_af_H():
    """室内機吹き出し風量に関する暖房時の能力補正係数

    Args:

    Returns:
      float: 室内機吹き出し風量に関する暖房時の能力補正係

    """
    return 0.8


# デフロストに関する暖房出力補正係数
def get_C_df_H(Theta_ex, h_ex):
    """デフロストに関する暖房出力補正係数

    Args:
      Theta_ex(ndarray): 外気温度
      h_ex(ndarray): 外気相対湿度

    Returns:
      ndarray: デフロストに関する暖房出力補正係数

    """
    C_df_H = np.ones(24 * 365)
    C_df_H[(Theta_ex < 5.0) * (h_ex >= 80.0)] = 0.77
    return C_df_H


# ============================================================================
# 6. 暖房エネルギー消費量
# ============================================================================

# ============================================================================
# 6.1 消費電力量
# ============================================================================

# 消費電力量 (5)
# dualcompressor: 容量可変型コンプレッサー搭載
def calc_E_E_H_d_t(region, q_rtd_C, q_rtd_H, e_rtd_H, dualcompressor, L_H_d_t):
    """消費電力量 (5)

    Args:
      region(int): 省エネルギー地域区分
      q_rtd_C(float): 定格冷房能力
      q_rtd_H(float): 定格暖房能力
      e_rtd_H(float): 定格暖房エネルギー消費効率
      dualcompressor(bool): 容量可変型コンプレッサー搭載
      L_H_d_t(ndarray): 暖冷房区画݅の１時間当たりの暖房負荷

    Returns:
      ndarray: 消費電力量

    """
    # 外気条件
    outdoor = load_outdoor()
    Theta_ex = get_Theta_ex(region, outdoor)
    X_ex = get_X_ex(region, outdoor)
    h_ex = calc_h_ex(X_ex, Theta_ex)

    # 最大暖房能力
    q_max_C = get_q_max_C(q_rtd_C)
    q_max_H = get_q_max_H(q_rtd_H, q_max_C)

    # 最大暖房能力比
    q_r_max_H = get_q_r_max_H(q_max_H, q_rtd_H)

    # 最大暖房出力比
    Q_r_max_H_d_t = calc_Q_r_max_H_d_t(q_rtd_C, q_r_max_H, Theta_ex)

    # 最大暖房出力
    Q_max_H_d_t = calc_Q_max_H_d_t(Q_r_max_H_d_t, q_rtd_H, Theta_ex, h_ex)

    # 処理暖房負荷
    Q_T_H_d_t = get_Q_T_H_d_t_i(Q_max_H_d_t_i=Q_max_H_d_t, L_H_d_t_i=L_H_d_t)

    # 補正処理暖房負荷
    Q_dash_T_H_d_t = calc_Q_dash_T_H_d_t(Q_T_H_d_t, Theta_ex, h_ex)

    # 消費電力量
    E_E_H_d_t = calc_f_H_Theta(Q_dash_T_H_d_t / (q_max_H * 3600 * 10 ** (-6)), q_rtd_C, dualcompressor, Theta_ex) \
                / calc_f_H_Theta(1.0 / q_r_max_H, q_rtd_C, dualcompressor, np.ones(24 * 365) * 7.0) \
                * (q_rtd_H / e_rtd_H) * 10 ** (-3)
    E_E_H_d_t[Q_dash_T_H_d_t == 0.0] = 0.0  # 補正処理暖房負荷が0の場合は0

    return E_E_H_d_t


def calc_Q_UT_H_d_t(region, q_rtd_C, q_rtd_H, e_rtd_H, L_H_d_t):
    """未処理負荷

    Args:
      region(int): 省エネルギー地域区分
      q_rtd_C(float): 定格冷房能力
      q_rtd_H(float): 定格暖房能力
      e_rtd_H(float): 定格暖房エネルギー消費効率
      L_H_d_t(ndarray): 暖冷房区画݅の１時間当たりの暖房負荷

    Returns:
      ndarray: 未処理負荷

    """
    # 外気条件
    outdoor = load_outdoor()
    Theta_ex = get_Theta_ex(region, outdoor)
    X_ex = get_X_ex(region, outdoor)
    h_ex = calc_h_ex(X_ex, Theta_ex)

    # 最大暖房能力
    q_max_C = get_q_max_C(q_rtd_C)
    q_max_H = get_q_max_H(q_rtd_H, q_max_C)

    # 最大暖房能力比
    q_r_max_H = get_q_r_max_H(q_max_H, q_rtd_H)

    # 最大暖房出力比
    Q_r_max_H_d_t = calc_Q_r_max_H_d_t(q_rtd_C, q_r_max_H, Theta_ex)

    # 最大暖房出力
    Q_max_H_d_t = calc_Q_max_H_d_t(Q_r_max_H_d_t, q_rtd_H, Theta_ex, h_ex)

    # 処理暖房負荷
    Q_T_H_d_t = get_Q_T_H_d_t_i(Q_max_H_d_t_i=Q_max_H_d_t, L_H_d_t_i=L_H_d_t)

    return L_H_d_t - Q_T_H_d_t


# 基準入出力関数 (6)
# dualcompressor: 容量可変型コンプレッサー搭載
def calc_f_H_Theta(x, q_rtd_C, dualcompressor, Theta_ex):
    """基準入出力関数 (6)

    Args:
      x(float): 入力
      q_rtd_C(float): 定格冷房能力
      dualcompressor(bool): 容量可変型コンプレッサー搭載
      Theta_ex(ndarray): 外気温度

    Returns:
      float: 基準入出力関数

    """
    # 係数a0-a4
    a0, a1, a2, a3, a4 = calc_a_eq7(q_rtd_C, dualcompressor, Theta_ex)
    return a4 * x ** 4 + a3 * x ** 3 + a2 * x ** 2 + a1 * x + a0


# 係数a0～a4 (7)
# dualcompressor: 容量可変型コンプレッサー搭載
def calc_a_eq7(q_rtd_C, dualcompressor, Theta_ex):
    """係数a0～a4

    Args:
      q_rtd_C(float): 定格冷房能力
      dualcompressor(bool): 容量可変型コンプレッサー搭載
      Theta_ex(ndarray): 外気気温

    Returns:
      tuple: 係数a0～a4

    """
    if dualcompressor == False:
        # 容量可変型コンプレッサー搭載ルームエアコンディショナーでないルームエアコンディショナー
        calc_p_i = calc_p_i_eq8
    else:
        # 容量可変型コンプレッサー搭載ルームエアコンディショナー
        calc_p_i = calc_p_i_eq9

    # 係数p_i
    p_42 = calc_p_i(42, q_rtd_C)
    p_41 = calc_p_i(41, q_rtd_C)
    p_40 = calc_p_i(40, q_rtd_C)
    p_32 = calc_p_i(32, q_rtd_C)
    p_31 = calc_p_i(31, q_rtd_C)
    p_30 = calc_p_i(30, q_rtd_C)
    p_22 = calc_p_i(22, q_rtd_C)
    p_21 = calc_p_i(21, q_rtd_C)
    p_20 = calc_p_i(20, q_rtd_C)
    p_12 = calc_p_i(12, q_rtd_C)
    p_11 = calc_p_i(11, q_rtd_C)
    p_10 = calc_p_i(10, q_rtd_C)
    p_02 = calc_p_i(2, q_rtd_C)
    p_01 = calc_p_i(1, q_rtd_C)
    p_00 = calc_p_i(0, q_rtd_C)

    a4 = p_42 * Theta_ex ** 2 + p_41 * Theta_ex + p_40 * 1
    a3 = p_32 * Theta_ex ** 2 + p_31 * Theta_ex + p_30 * 1
    a2 = p_22 * Theta_ex ** 2 + p_21 * Theta_ex + p_20 * 1
    a1 = p_12 * Theta_ex ** 2 + p_11 * Theta_ex + p_10 * 1
    a0 = p_02 * Theta_ex ** 2 + p_01 * Theta_ex + p_00 * 1

    return a0, a1, a2, a3, a4


# 係数p_i (8) (i=0,1,2,10..42)
# (容量可変型コンプレッサー搭載ルームエアコンディショナーでないルームエアコンディショナー)
def calc_p_i_eq8(i, q_rtd_C):
    """係数p_i

    Args:
      i(int): description]
      q_rtd_C(float): 定格冷房能力

    Returns:
      float: 係数p_i

    """
    q_rtd_C = min(5600, q_rtd_C)
    # 係数 s_i, t_i
    s_i = calc_s_i_eq8(i)
    t_i = calc_t_i_eq8(i)
    return s_i * q_rtd_C * 10 ** (-3) + t_i


# 係数s_i (i=0,1,2,10..42)
def calc_s_i_eq8(i):
    """係数s_i (i=0,1,2,10..42)

    Args:
      i(int): description]

    Returns:
      float: 係数s_i (i=0,1,2,10..42)

    """
    table_3 = get_table_3()    
    return table_3[4 - floor(i / 10)][(2 - (i % 10)) * 2]


# 係数t_i (i=0,1,2,10..42)
def calc_t_i_eq8(i):
    """係数t_i (i=0,1,2,10..42)

    Args:
      i(int): description]

    Returns:
      float: 係数t_i (i=0,1,2,10..42)

    """
    table_3 = get_table_3()
    return table_3[4 - floor(i / 10)][(2 - (i % 10)) * 2 + 1]


def get_table_3():
    """表3 係数s_i及びt_i

    Args:

    Returns:
      list: 表3 係数s_i及びt_i

    """
    # 表3 係数s_i及びt_i
    table_3 = [
        (-0.00236, 0.01324, 0.08418, -0.47143, -1.16944, 6.54886),
        (0.00427, -0.02392, -0.19226, 0.94213, 2.58632, -12.85618),
        (-0.00275, 0.01542, 0.14947, -0.68303, -2.03594, 10.60561),
        (0.00063, -0.00351, -0.02865, 0.10522, 0.37336, -1.09499),
        (-0.00005, 0.00028, 0.00184, -0.01090, -0.09609, 0.59229)
    ]
    return table_3


# 係数p_i (9)
# (容量可変型コンプレッサー搭載ルームエアコンディショナー)
def calc_p_i_eq9(i, q_rtd_C):
    """係数p_i (9)

    Args:
      i(int): description]
      q_rtd_C(float): 定格冷房能力

    Returns:
      float: 係数p_i (9)

    Raises:
      ValueError: q_rtd_Cが数値でない場合発生する

    """
    if q_rtd_C <= 2200:
        # (9a)
        return calc_p_i_A(i)
    elif 2200 < q_rtd_C and q_rtd_C <= 4000:
        # (9b)
        p_i_A = calc_p_i_A(i)
        p_i_B = calc_p_i_B(i)
        return p_i_A * ((4000 - q_rtd_C) / (4000 - 2200)) \
               + p_i_B * ((q_rtd_C - 2200) / (4000 - 2200))
    elif 4000 < q_rtd_C and q_rtd_C < 7100:
        # (9c)
        p_i_B = calc_p_i_B(i)
        p_i_C = calc_p_i_C(i)
        return p_i_B * ((7100 - q_rtd_C) / (7100 - 4000)) \
               + p_i_C * ((q_rtd_C - 4000) / (7100 - 4000))
    elif 7100 <= q_rtd_C:
        return calc_p_i_C(i)
    else:
        raise ValueError(q_rtd_C)


# 係数P_i_A (i=0,1,2,10..42)
def calc_p_i_A(i):
    """係数P_i_A (i=0,1,2,10..42)

    Args:
      i(int): description]

    Returns:
      float: 係数P_i_A (i=0,1,2,10..42)

    """
    table_4_A = get_table_4_A()
    return table_4_A[4 - floor(i / 10)][(2 - (i % 10))]


def calc_p_i_B(i):
    """係数P_i_B

    Args:
      i(int): description]

    Returns:
      float: 係数P_i_B

    """
    table_4_B = get_table_4_B()
    return table_4_B[4 - floor(i / 10)][(2 - (i % 10))]


def calc_p_i_C(i):
    """係数P_i_C

    Args:
      i(int): description]

    Returns:
      float: 係数P_i_C

    """
    table_4_C = get_table_4_C()
    return table_4_C[4 - floor(i / 10)][(2 - (i % 10))]

def get_table_4_A():
    """表4(A) 係数 p_i_A

    Args:

    Returns:
      list: 表4(A) 係数 p_i_A

    """
    # 表4(A) 係数 p_i_A
    table_4_A = [
        (-0.000056, 0.000786, 0.071625),
        (-0.000145, 0.003337, -0.143643),
        (-0.000240, -0.029471, 1.954343),
        (-0.000035, -0.050909, 1.389751),
        (0.0, 0.0, 0.076800)
    ]
    return table_4_A

def get_table_4_B():
    """表4(B) 係数 p_i_B

    Args:

    Returns:
      list: 表4(B) 係数 p_i_B

    """
    # 表4(B) 係数 p_i_B
    table_4_B = [
        (0.000108, -0.035658, 3.063873),
        (-0.000017, 0.062546, -5.471556),
        (-0.000245, -0.025126, 4.057590),
        (0.000323, -0.021166, 0.575459),
        (0.0, 0.000330, 0.047500)
    ]
    return table_4_B

def get_table_4_C():
    """表4(C) 係数 p_i_C

    Args:

    Returns:
      list: 表4(C) 係数 p_i_C

    """
    # 表4(C) 係数 p_i_C
    table_4_C = [
        (-0.001465, -0.030500, 1.920431),
        (0.002824, 0.041081, -1.835302),
        (-0.001929, -0.009738, 1.582898),
        (0.000616, -0.014239, 0.546204),
        (0.0, -0.000110, 0.023100)
    ]
    return table_4_C


# 補正処理暖房負荷 (10)
def calc_Q_dash_T_H_d_t(Q_T_H_d_t, Theta_ex, h_ex):
    """補正処理暖房負荷 (10)

    Args:
      Q_T_H_d_t(ndarray): 処理負荷
      Theta_ex(ndarray): 外気温度
      h_ex(ndarray): 外気相対温度

    Returns:
      ndarray: 補正処理暖房負荷 (10)

    """
    ##室内機吹き出し風量に関する暖房時の能力補正係
    C_af_H = get_C_af_H()

    ##デフロストに関する暖房出力補正係数
    C_d_f = get_C_df_H(Theta_ex, h_ex)

    Q_dash_T_H_d_t = Q_T_H_d_t * (1.0 / (C_af_H * C_d_f))

    return Q_dash_T_H_d_t


# ============================================================================
# 6.2 ガス消費量
# ============================================================================

# ガス消費量
def get_E_G_H_d_t():
    """ガス消費量

    Args:

    Returns:
      ndarray: ガス消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# 6.3 灯油消費量
# ============================================================================

# 灯油消費量
def get_E_K_H_d_t():
    """灯油消費量

    Args:

    Returns:
      ndarray: 灯油消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# 6.4 その他の燃料による一次エネルギー消費量
# ============================================================================

# その他の燃料による一次エネルギー消費量
def get_E_M_H_d_t():
    """その他の燃料による一次エネルギー消費量

    Args:

    Returns:
      ndarray: その他の燃料による一次エネルギー消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# 7. 最大冷房出力
# ============================================================================

# ============================================================================
# 7.1 最大冷房出力
# ============================================================================

# 最大冷房出力 (11)
def calc_Q_max_C_d_t(Q_r_max_C_d_t, q_rtd_C):
    """最大冷房出力 (11)

    Args:
      Q_r_max_C_d_t(ndarray): 最大冷房出力比
      q_rtd_C(float): 定格冷房能力

    Returns:
      ndarray: 最大冷房出力

    """
    # 室内機吸い込み湿度に関する冷房出力補正係数
    C_hm_C = get_C_hm_C()

    # 室内機吹き出し風量に関する冷房出力係数
    C_af_C = get_C_af_C()

    return Q_r_max_C_d_t * q_rtd_C * C_af_C * C_hm_C * 3600 * 10 ** (-6)


# 最大冷房出力比 (12)
def calc_Q_r_max_C_d_t(q_r_max_C, q_rtd_C, Theta_ex_d_t):
    """最大冷房出力比 (12)

    Args:
      q_r_max_C(float): 最大冷房能力比
      q_rtd_C(float): 定格冷房能力
      Theta_ex_d_t(ndarray): 1時間当たりの外気温度

    Returns:
      ndarray: 最大冷房出力比

    """
    a2, a1, a0 = calc_a_eq13(q_r_max_C, q_rtd_C)
    return a2 * (Theta_ex_d_t - 35) ** 2 + a1 * (Theta_ex_d_t - 35) + a0


# 係数a2及びa1,a0 (13a)
def calc_a_eq13(q_r_max_C, q_rtd_C):
    """係数a2及びa1,a0 (13a)

    Args:
      q_r_max_C(float): 最大冷房能力比
      q_rtd_C(float): 定格冷房能力

    Returns:
      tuple: 係数a2及びa1,a0

    """
    b2, b1, b0 = get_b_eq13(q_rtd_C)
    c2, c1, c0 = get_c_eq13(q_rtd_C)
    a2 = b2 * q_r_max_C + c2
    a1 = b1 * q_r_max_C + c1
    a0 = b0 * q_r_max_C + c0
    return a2, a1, a0


# 係数b2,b1,b0 (13b)
def get_b_eq13(q_rtd_C):
    """係数b2,b1,b0 (13b)

    Args:
      q_rtd_C(float): 定格冷房能力

    Returns:
      tuple: 係数b2,b1,b0

    """
    q_rtd_C = min(5600, q_rtd_C)
    b2 = 0.000812 * q_rtd_C * 10 ** (-3) - 0.001480
    b1 = 0.003527 * q_rtd_C * 10 ** (-3) - 0.023000
    b0 = -0.011490 * q_rtd_C * 10 ** (-3) + 1.024328
    return b2, b1, b0


# 係数c2,c1,c0 (13c)
def get_c_eq13(q_rtd_C):
    """係数c2,c1,c0 (13c)

    Args:
      q_rtd_C(float): 定格冷房能力

    Returns:
      tuple: 係数c2,c1,c0

    """
    q_rtd_C = min(5600, q_rtd_C)
    c2 = -0.000350 * q_rtd_C * 10 ** (-3) + 0.000800
    c1 = -0.001280 * q_rtd_C * 10 ** (-3) + 0.003621
    c0 = 0.004772 * q_rtd_C * 10 ** (-3) - 0.011170
    return c2, c1, c0


# 最大冷房能力比 (14)
def get_q_r_max_C(q_max_C, q_rtd_C):
    """最大冷房能力比 (14)

    Args:
      q_max_C(float): 最大冷房能力
      q_rtd_C(float): 定格冷房能力

    Returns:
      float: 最大冷房能力比

    """
    return q_max_C / q_rtd_C


# 室内機吹き出し風量に関する冷房時の能力補正係数 C_af_C
def get_C_af_C():
    """室内機吹き出し風量に関する冷房時の能力補正係数 C_af_C

    Args:

    Returns:
      float: 室内機吹き出し風量に関する冷房時の能力補正係数

    """
    return 0.85


# 室内機吸い込み湿度に関する冷房能力補正係 C_hm_C
def get_C_hm_C():
    """室内機吸い込み湿度に関する冷房能力補正係数 C_hm_C

    Args:

    Returns:
      float: 室内機吸い込み湿度に関する冷房能力補正係数

    """
    return 1.15


# ============================================================================
# 7.2 最大冷房顕熱出力及び最大冷房潜熱出力の計算
# ============================================================================

# 最大冷房顕熱出力 (15a)
def get_Q_max_CS_d_t(Q_max_C_d_t, SHF_dash_d_t):
    """最大冷房顕熱出力 (15a)

    Args:
      Q_max_C_d_t(ndarray): 最大冷房出力
      SHF_dash_d_t(ndarray): 冷房負荷補正顕熱比

    Returns:
      ndarray: 最大冷房顕熱出力

    """
    return Q_max_C_d_t * SHF_dash_d_t


# 最大冷房潜熱出力 (15b)
def get_Q_max_CL_d_t(Q_max_C_d_t, SHF_dash_d_t, L_dash_CL_d_t):
    """最大冷房潜熱出力 (15b)

    Args:
      Q_max_C_d_t(ndarray): 最大冷房出力
      SHF_dash_d_t(ndarray): 冷房負荷補正顕熱比
      L_dash_CL_d_t(ndarray): 1時間当たりの補正冷房潜熱負荷

    Returns:
      ndarray: 最大冷房潜熱出力

    """
    return np.clip(Q_max_C_d_t * (1.0 - SHF_dash_d_t), 0, L_dash_CL_d_t)


# 冷房負荷補正顕熱比 (16)
def get_SHF_dash_d_t(L_CS_d_t, L_dash_C_d_t):
    """冷房負荷補正顕熱比 (16)

    Args:
      L_CS_d_t(ndarray): 暖冷房区画の 1 時間当たりの冷房顕熱負荷
      L_dash_CL_d_t(ndarray): 1時間当たりの補正冷房潜熱負荷
      L_dash_C_d_t: returns: 冷房負荷補正顕熱比

    Returns:
      float: 冷房負荷補正顕熱比

    """
    SHF_dash_d_t = np.zeros(24*365)
    f1 = L_dash_C_d_t > 0
    SHF_dash_d_t[f1] = L_CS_d_t[f1] / L_dash_C_d_t[f1]
    return SHF_dash_d_t


# 補正冷房負荷 (17)
def get_L_dash_C_d_t(L_CS_d_t, L_dash_CL_d_t):
    """補正冷房負荷 (17)

    Args:
      L_CS_d_t(ndarray): 暖冷房区画の 1 時間当たりの冷房顕熱負荷
      L_dash_CL_d_t(ndarray): 1時間当たりの補正冷房潜熱負荷

    Returns:
      ndarray: 補正冷房負荷

    """
    return L_CS_d_t + L_dash_CL_d_t


# 補正冷房潜熱負荷 (18)
def get_L_dash_CL_d_t(L_max_CL_d_t, L_CL_d_t):
    """補正冷房潜熱負荷 (18)

    Args:
      L_max_CL_d_t(ndarray): 1時間当たりの最大冷房潜熱負荷
      L_CL_d_t(ndarray): 暖冷房区画の 1 時間当たりの冷房潜熱負荷

    Returns:
      ndarray: 補正冷房潜熱負荷

    """
    return np.clip(L_CL_d_t, 0, L_max_CL_d_t)


# 最大冷房潜熱負荷 (19)
def get_L_max_CL_d_t(L_CS_d_t, SHF_L_min_c):
    """最大冷房潜熱負荷 (19)

    Args:
      L_CS_d_t(ndarray): 暖冷房区画の 1 時間当たりの冷房顕熱負荷
      SHF_L_min_c(float): 冷房負荷最小顕熱比率

    Returns:
      ndarray: 最大冷房潜熱負荷

    """
    return L_CS_d_t * ((1.0 - SHF_L_min_c) / SHF_L_min_c)


# 冷房負荷最小顕熱比
def get_SHF_L_min_c():
    """冷房負荷最小顕熱比

    Args:

    Returns:
      float: 冷房負荷最小顕熱比率

    """
    return 0.4


# ============================================================================
# 8. 冷房エネルギー消費量
# ============================================================================

# ============================================================================
# 8.1 消費電力量
# ============================================================================

# 消費電力量 (20)
def calc_E_E_C_d_t(region, q_rtd_C, e_rtd_C, dualcompressor, L_CS_d_t, L_CL_d_t):
    """消費電力量 (20)

    Args:
      region(int): 省エネルギー地域区分
      q_rtd_C(float): 定格冷房能力
      e_rtd_C(float): 定格冷房エネルギー消費効率
      dualcompressor(bool): 容量可変型コンプレッサー搭載
      L_CS_d_t(ndarray): 暖冷房区画の 1 時間当たりの冷房顕熱負荷
      L_CL_d_t(ndarray): 暖冷房区画の 1 時間当たりの冷房潜熱負荷

    Returns:
      ndarray: 消費電力量

    """
    # 外気条件
    outdoor = load_outdoor()
    Theta_ex = get_Theta_ex(region, outdoor)
    X_ex = get_X_ex(region, outdoor)
    h_ex = calc_h_ex(X_ex, Theta_ex)

    # 最大冷房能力
    q_max_C = get_q_max_C(q_rtd_C)

    # 最大冷房能力比
    q_r_max_C = get_q_r_max_C(q_max_C, q_rtd_C)

    # 最大冷房出力比
    Q_r_max_C_d_t = calc_Q_r_max_C_d_t(q_r_max_C, q_rtd_C, Theta_ex)

    # 最大冷房出力
    Q_max_C_d_t = calc_Q_max_C_d_t(Q_r_max_C_d_t, q_rtd_C)

    # 冷房負荷最小顕熱比
    SHF_L_min_c = get_SHF_L_min_c()

    # 最大冷房潜熱負荷
    L_max_CL_d_t = get_L_max_CL_d_t(L_CS_d_t, SHF_L_min_c)

    # 補正冷房潜熱負荷
    L_dash_CL_d_t = get_L_dash_CL_d_t(L_max_CL_d_t, L_CL_d_t)
    L_dash_C_d_t = get_L_dash_C_d_t(L_CS_d_t, L_dash_CL_d_t)

    # 冷房負荷補正顕熱比
    SHF_dash_d_t = get_SHF_dash_d_t(L_CS_d_t, L_dash_C_d_t)

    # 最大冷房顕熱出力, 最大冷房潜熱出力
    Q_max_CS_d_t = get_Q_max_CS_d_t(Q_max_C_d_t, SHF_dash_d_t)
    Q_max_CL_d_t = get_Q_max_CL_d_t(Q_max_C_d_t, SHF_dash_d_t, L_dash_CL_d_t)

    # 処理冷房負荷
    Q_T_CS_d_t = get_Q_T_CS_d_t_i(Q_max_CS_d_t_i=Q_max_CS_d_t, L_CS_d_t_i=L_CS_d_t)
    Q_T_CL_d_t = get_Q_T_CL_d_t_i(Q_max_CL_d_t_i=Q_max_CL_d_t, L_CL_d_t_i=L_CL_d_t)

    # 補正処理冷房負荷
    Q_dash_T_C_d_t = calc_Q_dash_T_C_d_t(Q_T_CS_d_t, Q_T_CL_d_t)

    # 消費電力量
    E_E_C_d_t = calc_f_C_Theta(Q_dash_T_C_d_t / (q_max_C * 3600 * 10 ** (-6)), Theta_ex, q_rtd_C, dualcompressor) \
                / calc_f_C_Theta(1.0 / q_r_max_C, np.ones(24 * 365) * 35.0, q_rtd_C, dualcompressor) \
                * (q_rtd_C / e_rtd_C) * 10 ** (-3)
    E_E_C_d_t[Q_dash_T_C_d_t == 0.0] = 0.0

    return E_E_C_d_t


# 基準入出力関数 (21)
def calc_f_C_Theta(x, Theta_ex, q_rtd_C, dualcompressor=False):
    """基準入出力関数 (21)

    Args:
      x(float): 入力
      Theta_ex(ndarray): 外気気温
      q_rtd_C(float): 定格冷房能力
      dualcompressor(bool, optional, optional): 容量可変型コンプレッサー搭載, defaults to False

    Returns:
      float: 基準入出力関数の入力xに対する出力

    """
    # 係数a0-a4
    a0, a1, a2, a3, a4 = calc_a_eq22(Theta_ex, q_rtd_C, dualcompressor=dualcompressor)

    return a4 * x ** 4 + a3 * x ** 3 + a2 * x ** 2 + a1 * x + a0


# 係数a0-a4
def calc_a_eq22(Theta_ex, q_rtd_C, dualcompressor=False):
    """係数a0-a4

    Args:
      Theta_ex(ndarray): 外気気温
      q_rtd_C(float): 定格冷房能力
      dualcompressor(bool, optional, optional): 容量可変型コンプレッサー搭載, defaults to False

    Returns:
      tuple: 係数a0-a4

    """
    if dualcompressor == False:
        # 容量可変型コンプレッサー搭載ルームエアコンディショナーでないルームエアコンディショナー
        calc_p_i = calc_p_i_eq23
    else:
        # 容量可変型コンプレッサー搭載ルームエアコンディショナー
        calc_p_i = calc_p_i_eq24

    # 係数p_i
    p42 = calc_p_i(42, q_rtd_C)
    p41 = calc_p_i(41, q_rtd_C)
    p40 = calc_p_i(40, q_rtd_C)
    p32 = calc_p_i(32, q_rtd_C)
    p31 = calc_p_i(31, q_rtd_C)
    p30 = calc_p_i(30, q_rtd_C)
    p22 = calc_p_i(22, q_rtd_C)
    p21 = calc_p_i(21, q_rtd_C)
    p20 = calc_p_i(20, q_rtd_C)
    p12 = calc_p_i(12, q_rtd_C)
    p11 = calc_p_i(11, q_rtd_C)
    p10 = calc_p_i(10, q_rtd_C)
    p02 = calc_p_i(2, q_rtd_C)
    p01 = calc_p_i(1, q_rtd_C)
    p00 = calc_p_i(0, q_rtd_C)

    a4 = p42 * Theta_ex ** 2 + p41 * Theta_ex + p40 * 1
    a3 = p32 * Theta_ex ** 2 + p31 * Theta_ex + p30 * 1
    a2 = p22 * Theta_ex ** 2 + p21 * Theta_ex + p20 * 1
    a1 = p12 * Theta_ex ** 2 + p11 * Theta_ex + p10 * 1
    a0 = p02 * Theta_ex ** 2 + p01 * Theta_ex + p00 * 1

    return a0, a1, a2, a3, a4


# 係数p_i (23)
def calc_p_i_eq23(i, q_rtd_C):
    """係数p_i (23)

    Args:
      i(int): description]
      q_rtd_C(float): 定格冷房能力

    Returns:
      float: 係数p_i

    """
    q_rtd_C = min(5600, q_rtd_C)
    s_i = calc_s_i_eq23(i)
    t_i = calc_t_i_eq23(i)
    return s_i * q_rtd_C * 10 ** (-3) + t_i


# 係数s_i (i=0,1,2,10..42)
def calc_s_i_eq23(i):
    """係数s_i (i=0,1,2,10..42)

    Args:
      i(int): description]

    Returns:
      float: 係数s_i

    """
    table_5 = get_table_5()
    return table_5[4 - floor(i / 10)][(2 - (i % 10)) * 2]


# 係数t_i (i=0,1,2,10..42)
def calc_t_i_eq23(i):
    """

    Args:
      i: 

    Returns:

    """
    table_5 = get_table_5()
    return table_5[4 - floor(i / 10)][(2 - (i % 10)) * 2 + 1]


def get_table_5():
    """表5 係数s_i及びt_i

    Args:

    Returns:
      float: 表5 係数s_i及びt_i

    """
    # 表5 係数s_i及びt_i
    table_5 = [
        (0.00000, 0.00000, 0.00000, 0.00000, 0.00000, 0.00000),
        (0.00000, 0.00000, -0.00036, 0.05080, -0.20346, 0.47765),
        (0.00000, 0.00000, 0.00227, -0.03952, 0.04115, 0.23099),
        (0.00000, 0.00000, -0.00911, 0.07102, 0.14950, -1.07335),
        (0.00000, 0.00000, 0.00044, -0.00214, -0.06250, 0.35150)
    ]
    return table_5


# 係数p_i (21)
# (容量可変型コンプレッサー搭載ルームエアコンディショナー)
def calc_p_i_eq24(i, q_rtd_C):
    """係数p_i (21)

    Args:
      i(int): description]
      q_rtd_C(float): 定格冷房能力

    Returns:
      float: 係数p_i

    Raises:
      ValueError: q_rtd_Cが数値でない場合発生する

    """
    if q_rtd_C <= 2200:
        # (9a)
        return calc_p_i_A_eq24(i)
    elif 2200 < q_rtd_C and q_rtd_C <= 4000:
        # (9b)
        p_i_A = calc_p_i_A_eq24(i)
        p_i_B = calc_p_i_B_eq24(i)
        return p_i_A * ((4000 - q_rtd_C) / (4000 - 2200)) \
               + p_i_B * ((q_rtd_C - 2200) / (4000 - 2200))
    elif 4000 <= q_rtd_C and q_rtd_C < 7100:
        # (9c)
        p_i_B = calc_p_i_B_eq24(i)
        p_i_C = calc_p_i_C_eq24(i)
        return p_i_B * ((7100 - q_rtd_C) / (7100 - 4000)) \
               + p_i_C * ((q_rtd_C - 4000) / (7100 - 4000))
    elif 7100 <= q_rtd_C:
        return calc_p_i_C_eq24(i)
    else:
        raise ValueError(q_rtd_C)


# 係数P_i_A (i=0,1,2,10..42)
def calc_p_i_A_eq24(i):
    """係数P_i_A (i=0,1,2,10..42)

    Args:
      i(int): description]

    Returns:
      float: 係数P_i_A

    """
    table_6_A = get_table_6_A()
    return table_6_A[4 - floor(i / 10)][(2 - (i % 10))]


def calc_p_i_B_eq24(i):
    """係数P_i_B

    Args:
      i(int): description]

    Returns:
      float: 係数P_i_B

    """
    table_6_B = get_table_6_B()
    return table_6_B[4 - floor(i / 10)][(2 - (i % 10))]


def calc_p_i_C_eq24(i):
    """係数P_i_C

    Args:
      i(int): description]

    Returns:
      float: 係数P_i_C

    """
    table_6_C = get_table_6_C()
    return table_6_C[4 - floor(i / 10)][(2 - (i % 10))]


def get_table_6_A():
    """表6(A) 係数 p_i_a

    Args:

    Returns:
      list: 表6(A) 係数 p_i_a

    """
    # 表6(A) 係数 p_i_A
    table_6_A = [
        (-0.0004078, 0.01035, -0.03248),
        (0.0, 0.04099, -0.818809),
        (0.0, -0.04615, 2.10666),
        (0.0013382, -0.01179, -0.41778),
        (0.0000000, -0.00102, 0.09270)
    ]
    return table_6_A

def get_table_6_B():
    """表6(B) 係数 p_i_b

    Args:

    Returns:
      list: 表6(B) 係数 p_i_b

    """
    # 表6(B) 係数 p_i_B
    table_6_B = [
        (-0.000056, -0.003539, -0.430566),
        (0.0, 0.015237, 1.188850),
        (0.0, 0.000527, -0.304645),
        (-0.000179, 0.020543, 0.130373),
        (0.0, 0.000240, 0.013500)
    ]
    return table_6_B

def get_table_6_C():
    """表6(C) 係数 p_i_C

    Args:

    Returns:
      list: 表6(C) 係数 p_i_C

    """
    # 表6(C) 係数 p_i_C
    table_6_C = [
        (-0.0001598, 0.004848, 0.047097),
        (0.0, 0.016675, 0.362141),
        (0.0, -0.008134, -0.023535),
        (-0.0000772, 0.012558, 0.056185),
        (0.0, -0.000110, 0.010300)
    ]
    return table_6_C


# 補正処理冷房負荷 (25)
def calc_Q_dash_T_C_d_t(Q_T_CS_d_t, Q_T_CL_d_t):
    """補正処理冷房負荷 (25)

    Args:
      Q_T_CS_d_t(ndarray): 冷房区画の処理冷房顕熱負荷
      Q_T_CL_d_t(ndarray): 冷房区画の処理冷房潜熱負荷

    Returns:
      ndarray: 補正処理冷房負荷

    """
    # 室内機吸い込み湿度に関する冷房出力補正係数
    C_hm_C = get_C_hm_C()

    # 室内機吹き出し風量に関する冷房出力係数
    C_af_C = get_C_af_C()

    return (Q_T_CS_d_t + Q_T_CL_d_t) * (1.0 / (C_hm_C * C_af_C))


# ============================================================================
# 8.2 ガス消費量
# ============================================================================

# ガス消費量
def get_E_G_C_d_t():
    """ガス消費量

    Args:

    Returns:
      ndarray: ガス消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# 8.3 灯油消費量
# ============================================================================

# 灯油消費量
def get_E_K_C_d_t():
    """灯油消費量

    Args:

    Returns:
      ndarray: 灯油消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# 8.4 その他の燃料による一次エネルギー消費量
# ============================================================================

# その他の燃料による一次エネルギー消費量
def get_E_M_C_d_t():
    """その他の燃料による一次エネルギー消費量

    Args:

    Returns:
      ndarray: その他の燃料による一次エネルギー消費量

    """
    return np.zeros(24 * 365)


if __name__ == '__main__':
    from section11_1 import load_outdoor

    outdoor = load_outdoor()

    # ダミー負荷
    L_H_d_t = np.ones(24 * 365) * 12
    L_CS_d_t = np.ones(24 * 365) * 12
    L_CL_d_t = np.ones(24 * 365) * 12

    # エアコン暖房
    E_E_H_d_t = calc_E_E_H_d_t(
        region=7,
        outdoor=outdoor,
        q_rtd_C=4066.6500,
        q_rtd_H=4066.6500,
        e_rtd_H=1.3420,
        L_H_d_t=L_H_d_t
    )
    E_G_H_d_t = get_E_G_H_d_t()
    E_K_H_d_t = get_E_K_H_d_t()
    E_M_H_d_t = get_E_M_H_d_t()
    print('E_E_H = {} '.format(np.sum(E_E_H_d_t)))
    print('E_G_H = {} '.format(np.sum(E_G_H_d_t)))
    print('E_K_H = {} '.format(np.sum(E_K_H_d_t)))
    print('E_M_H = {} '.format(np.sum(E_M_H_d_t)))

    # エアコン冷房
    E_E_C_d_t = calc_E_E_C_d_t(
        region=7,
        outdoor=outdoor,
        q_rtd_C=4066.6500,
        e_rtd_C=1.3420,
        L_CS_d_t=L_CS_d_t,
        L_CL_d_t=L_CL_d_t
    )
    E_G_C_d_t = get_E_G_C_d_t()
    E_K_C_d_t = get_E_K_C_d_t()
    E_M_C_d_t = get_E_M_C_d_t()
    print('E_E_C = {} '.format(np.sum(E_E_C_d_t)))
    print('E_G_C = {} '.format(np.sum(E_G_C_d_t)))
    print('E_K_C = {} '.format(np.sum(E_K_C_d_t)))
    print('E_M_C = {} '.format(np.sum(E_M_C_d_t)))
