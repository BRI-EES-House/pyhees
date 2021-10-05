# ============================================================================
# 付録 I 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機
#    （給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：電気ヒートポンプ・ガス瞬間式併用）
# ============================================================================


import numpy as np


# ============================================================================
# I.2 消費電力量
# ============================================================================


def calc_E_E_hs_d_t(L_HWH, hybrid_category, theta_ex_d_Ave_d, L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t,
                    L_dashdash_b2_d_t,
                    L_dashdash_ba2_d_t):
    """# 1時間当たりの給湯機の消費電力量 (1)

    Args:
      L_HWH(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの給湯機の消費電力量 (kWh/h)

    """
    # 1日当たりの太陽熱補正給湯熱負荷
    L_dashdash_k_d = get_L_dashdash_k_d(L_dashdash_k_d_t)
    L_dashdash_s_d = get_L_dashdash_s_d(L_dashdash_s_d_t)
    L_dashdash_w_d = get_L_dashdash_w_d(L_dashdash_w_d_t)
    L_dashdash_b2_d = get_L_dashdash_b2_d(L_dashdash_b2_d_t)
    L_dashdash_ba2_d = get_L_dashdash_ba2_d(L_dashdash_ba2_d_t)

    E_E_hs_d = calc_E_E_hs_d(L_HWH, hybrid_category, theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d,
                             L_dashdash_b2_d, L_dashdash_ba2_d)

    # 1日当たりの太陽熱補正給湯熱負荷、給湯機の消費電力量の配列要素を1時間ごとに引き延ばす(合計値は24倍になることに注意)
    E_E_hs_d = np.repeat(E_E_hs_d, 24)
    L_dashdash_k_d = np.repeat(L_dashdash_k_d, 24)
    L_dashdash_s_d = np.repeat(L_dashdash_s_d, 24)
    L_dashdash_w_d = np.repeat(L_dashdash_w_d, 24)
    L_dashdash_b2_d = np.repeat(L_dashdash_b2_d, 24)
    L_dashdash_ba2_d = np.repeat(L_dashdash_ba2_d, 24)

    E_E_hs_d_t = np.zeros(24 * 365)

    # (1-1) 太陽熱補正給湯熱負荷が発生しない日 => 24時間で単純分割
    f1 = (L_dashdash_k_d + L_dashdash_s_d + L_dashdash_w_d + L_dashdash_b2_d + L_dashdash_ba2_d == 0)
    E_E_hs_d_t[f1] = E_E_hs_d[f1] / 24

    # (1-2) 太陽熱補正給湯熱負荷が発生する日 => 負荷で按分
    f2 = (L_dashdash_k_d + L_dashdash_s_d + L_dashdash_w_d + L_dashdash_b2_d + L_dashdash_ba2_d > 0)
    E_E_hs_d_t[f2] = E_E_hs_d[f2] * (
            L_dashdash_k_d_t[f2] + L_dashdash_s_d_t[f2] + L_dashdash_w_d_t[f2] + L_dashdash_b2_d_t[f2] +
            L_dashdash_ba2_d_t[f2]) / (
                             L_dashdash_k_d[f2] + L_dashdash_s_d[f2] + L_dashdash_w_d[f2] + L_dashdash_b2_d[f2] +
                             L_dashdash_ba2_d[f2])

    return E_E_hs_d_t


def calc_E_E_hs_d(L_HWH, hybrid_category, theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d,
                  L_dashdash_b2_d,
                  L_dashdash_ba2_d):
    """# 1日当たりの給湯機の消費電力量 (2)

    Args:
      L_HWH(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_k_d(ndarray): 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_s_d(ndarray): 1日当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_w_d(ndarray): 1日当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_b2_d(ndarray): 1日当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_ba2_d(ndarray): 1日当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 1日当たりの給湯機の消費電力量 (kWh/d)

    """
    # 係数
    a_1, a_2, a_3, a_4 = get_coeff_a(L_HWH, hybrid_category)

    # デフロスト係数
    C_E_def_d = get_C_E_def_d(theta_ex_d_Ave_d)

    E_E_hs_d = ((a_1 * theta_ex_d_Ave_d + a_2 * (
            L_dashdash_k_d + L_dashdash_s_d + L_dashdash_w_d + L_dashdash_b2_d) + a_3 * L_HWH + a_4) * C_E_def_d
                + (0.01723 * L_dashdash_ba2_d + 0.06099)) * 10 ** 3 / 3600

    return E_E_hs_d


def get_coeff_a(L_HWH, hybrid_category):
    """# 係数a_1, a_2, a_3, a_4

    Args:
      L_HWH(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分

    Returns:
      tuple: 係数a_1, a_2, a_3, a_4

    """

    a_1 = np.zeros(365)
    a_2 = np.zeros(365)
    a_3 = np.zeros(365)
    a_4 = np.zeros(365)
    if hybrid_category == '区分1':
        a_1[L_HWH > 0] = get_table_i_3()[0][0]
        a_1[L_HWH == 0] = get_table_i_3()[0][2]
        a_2[L_HWH > 0] = get_table_i_3()[1][0]
        a_2[L_HWH == 0] = get_table_i_3()[1][2]
        a_3[L_HWH > 0] = get_table_i_3()[2][0]
        a_3[L_HWH == 0] = get_table_i_3()[2][2]
        a_4[L_HWH > 0] = get_table_i_3()[3][0]
        a_4[L_HWH == 0] = get_table_i_3()[3][2]
    elif hybrid_category == '区分2':
        a_1[L_HWH > 0] = get_table_i_3()[0][1]
        a_1[L_HWH == 0] = get_table_i_3()[0][3]
        a_2[L_HWH > 0] = get_table_i_3()[1][1]
        a_2[L_HWH == 0] = get_table_i_3()[1][3]
        a_3[L_HWH > 0] = get_table_i_3()[2][1]
        a_3[L_HWH == 0] = get_table_i_3()[2][3]
        a_4[L_HWH > 0] = get_table_i_3()[3][1]
        a_4[L_HWH == 0] = get_table_i_3()[3][3]
    else:
        raise ValueError(hybrid_category)
    return a_1, a_2, a_3, a_4

def get_table_i_3():
    """表I.3 式(1)における係数

    Args:

    Returns:
      list: 表I.3 式(1)における係数

    """
    # 表I.3 式(1)における係数
    table_i_3 = [
        (-0.51375, -0.57722, -0.18114, -0.30429),
        (-0.01782, 0.03865, 0.10483, 0.08497),
        (0.27640, 0.18173, 0.0, 0.0),
        (9.40671, 15.30711, 5.85285, 10.66158)
    ]
    return table_i_3

def get_C_E_def_d(theta_ex_d_Ave_d):
    """1日当たりのデフロスト運転による消費電力量の補正係数 (3)

    Args:
      theta_ex_d_Ave_d: 日平均外気温度 (℃)

    Returns:
      ndarray: 1日当たりのデフロスト運転による消費電力量の補正係数 (3)

    """
    C_E_def_d = np.ones(365)

    f = theta_ex_d_Ave_d < 7
    C_E_def_d[f] = 1 + (7 - theta_ex_d_Ave_d[f]) * 0.0091

    return C_E_def_d


# ============================================================================
# I.3 ガス消費量
# ============================================================================


def calc_E_G_hs_d_t(L_HWH, hybrid_category, Theta_ex_Ave, L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t, L_dashdash_b2_d_t,
                   L_dashdash_ba2_d_t):
    """# 1時間当たりの給湯機のガス消費量 (4)

    Args:
      L_HWH(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分
      Theta_ex_Nave: 夜間平均外気温 (℃)
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/hd)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/hd)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
      Theta_ex_Ave: returns: 1時間当たりの給湯機のガス消費量  (MJ/h)

    Returns:
      ndarray: 1時間当たりの給湯機のガス消費量  (MJ/h)

    """

    # 1日当たりの太陽熱補正給湯熱負荷
    L_dashdash_k_d = get_L_dashdash_k_d(L_dashdash_k_d_t)
    L_dashdash_s_d = get_L_dashdash_s_d(L_dashdash_s_d_t)
    L_dashdash_w_d = get_L_dashdash_w_d(L_dashdash_w_d_t)
    L_dashdash_b2_d = get_L_dashdash_b2_d(L_dashdash_b2_d_t)
    L_dashdash_ba2_d = get_L_dashdash_ba2_d(L_dashdash_ba2_d_t)

    # 1日当たりの給湯機のガス消費量 (5)
    E_G_hs_d = calc_E_G_hs_d(L_HWH, hybrid_category, Theta_ex_Ave, L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d, L_dashdash_b2_d,
               L_dashdash_ba2_d)

    # 1日当たりの太陽熱補正給湯熱負荷、給湯機のガス消費量の配列要素を1時間ごとに引き延ばす(合計値は24倍になることに注意)
    E_G_hs_d = np.repeat(E_G_hs_d, 24)
    L_dashdash_k_d = np.repeat(L_dashdash_k_d, 24)
    L_dashdash_s_d = np.repeat(L_dashdash_s_d, 24)
    L_dashdash_w_d = np.repeat(L_dashdash_w_d, 24)
    L_dashdash_b2_d = np.repeat(L_dashdash_b2_d, 24)
    L_dashdash_ba2_d = np.repeat(L_dashdash_ba2_d, 24)

    E_G_hs_d_t = np.zeros(24 * 365)

    # (4-1) 太陽熱補正給湯熱負荷が発生しない日 => 24時間で単純分割
    f1 = (L_dashdash_k_d + L_dashdash_s_d + L_dashdash_w_d + L_dashdash_b2_d + L_dashdash_ba2_d == 0)
    E_G_hs_d_t[f1] = E_G_hs_d[f1] / 24

    # (4-2) 太陽熱補正給湯熱負荷が発生する日 => 負荷で按分
    f2 = (L_dashdash_k_d + L_dashdash_s_d + L_dashdash_w_d + L_dashdash_b2_d + L_dashdash_ba2_d > 0)
    E_G_hs_d_t[f2] = E_G_hs_d[f2] * (
            L_dashdash_k_d_t[f2] + L_dashdash_s_d_t[f2] + L_dashdash_w_d_t[f2] + L_dashdash_b2_d_t[f2] +
            L_dashdash_ba2_d_t[f2]) / (
                             L_dashdash_k_d[f2] + L_dashdash_s_d[f2] + L_dashdash_w_d[f2] + L_dashdash_b2_d[f2] +
                             L_dashdash_ba2_d[f2])

    return E_G_hs_d_t

def calc_E_G_hs_d(L_HWH, hybrid_category, Theta_ex_Ave, L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d, L_dashdash_b2_d,
               L_dashdash_ba2_d):
    """# 1日当たりの給湯機のガス消費量 (5)

    Args:
      L_HWH(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分
      Theta_ex_Ave(ndarray): 夜間平均外気温 (℃)
      L_dashdash_k_d(ndarray): 1日当たりの台所水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dashdash_s_d(ndarray): 1日当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dashdash_w_d(ndarray): 1日当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dashdash_b2_d(ndarray): 1日当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/d)
      L_dashdash_ba2_d(ndarray): 1日当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 1日当たりの給湯機のガス消費量  (MJ/d)

    """
    # 係数
    b_1, b_2, b_3, b_4 = get_coeff_b(L_HWH, hybrid_category)

    # デフロスト係数
    C_G_def_d = get_C_G_def_d(Theta_ex_Ave)

    # 浴槽追焚時における日平均給湯機効率
    e_ba2 = get_e_ba2_d(Theta_ex_Ave, L_dashdash_ba2_d)

    return ((b_1 * Theta_ex_Ave + b_2 * (
            L_dashdash_k_d + L_dashdash_s_d + L_dashdash_w_d + L_dashdash_b2_d) + b_3 * L_HWH + b_4) * C_G_def_d + (
                    L_dashdash_ba2_d / e_ba2))


def get_coeff_b(L_HWH, hybrid_category):
    """# 係数b_1, b_2, b_3, b_4

    Args:
      L_HWH(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分

    Returns:
      tuple: 係数b_1, b_2, b_3, b_4

    """

    b_1 = np.zeros(365)
    b_2 = np.zeros(365)
    b_3 = np.zeros(365)
    b_4 = np.zeros(365)
    if hybrid_category == '区分1':
        b_1[L_HWH > 0] = get_table_i_4()[0][0]
        b_1[L_HWH == 0] = get_table_i_4()[0][2]
        b_2[L_HWH > 0] = get_table_i_4()[1][0]
        b_2[L_HWH == 0] = get_table_i_4()[1][2]
        b_3[L_HWH > 0] = get_table_i_4()[2][0]
        b_3[L_HWH == 0] = get_table_i_4()[2][2]
        b_4[L_HWH > 0] = get_table_i_4()[3][0]
        b_4[L_HWH == 0] = get_table_i_4()[3][2]
    elif hybrid_category == '区分2':
        b_1[L_HWH > 0] = get_table_i_4()[0][1]
        b_1[L_HWH == 0] = get_table_i_4()[0][3]
        b_2[L_HWH > 0] = get_table_i_4()[1][1]
        b_2[L_HWH == 0] = get_table_i_4()[1][3]
        b_3[L_HWH > 0] = get_table_i_4()[2][1]
        b_3[L_HWH == 0] = get_table_i_4()[2][3]
        b_4[L_HWH > 0] = get_table_i_4()[3][1]
        b_4[L_HWH == 0] = get_table_i_4()[3][3]
    else:
        raise ValueError(hybrid_category)
    return b_1, b_2, b_3, b_4

def get_table_i_4():
    """表I.4 係数

    Args:

    Returns:
      list: 表I.4 係数

    """
    # 表I.4 係数
    table_i_4 = [
        (-0.19841, -0.5782, -0.05770, 0.14061),
        (1.10632, 0.75066, 0.47525, 0.3227),
        (0.19307, 0.46244, 0.0, 0.0),
        (-10.36669, -12.55999, -6.34593, -13.43567)
    ]
    return table_i_4

def get_e_ba2_d(theta_ex_d_Ave_d, L_dashdash_ba2_d):
    """# 浴槽追焚時における日平均給湯機効率 (6)

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_ba2_d(ndarray): 1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)

    Returns:
      ndarray: 浴槽追焚時における日平均給湯機効率 (6)

    """
    # 係数
    c_1, c_2, c_3 = get_coeff_c()

    e_ba2_d = c_1 * theta_ex_d_Ave_d + c_2 * L_dashdash_ba2_d + c_3

    # 効率が1.0を超えない範囲で
    e_ba2_d = np.clip(e_ba2_d, None, 1)

    return e_ba2_d


def get_coeff_c():
    """表I.5 係数

    Args:

    Returns:
      tuple: 表I.5 係数

    """
    # 表I.5 係数
    table_i_5 = (0.0048, 0.0060, 0.7544)
    return table_i_5


def get_C_G_def_d(theta_ex_d_Ave_d):
    """# 1日当たりのデフロスト運転によるガス消費量の補正係数 (7)

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)

    Returns:
      ndarray: 1日当たりのデフロスト運転によるガス消費量の補正係数 (7)

    """
    C_G_def = np.ones(365)

    f = theta_ex_d_Ave_d < 7
    C_G_def[f] = 1 + (7 - theta_ex_d_Ave_d[f]) * 0.0205

    return C_G_def


# ============================================================================
# I.4 灯油消費量
# ============================================================================


def get_E_K_hs_d_t():
    """# 1時間当たりの給湯機の灯油消費量

    Args:

    Returns:
      ndarray: 1時間当たりの給湯機の灯油消費量

    """
    # 1日当たりの給湯機の灯油消費量は0とする
    return np.zeros(24*365)


# ============================================================================
# I.5 温水暖房における熱源機の往き温水温度の候補
# ============================================================================


def get_hotwater_temp_list():
    """# 温水暖房における熱源機の往き温水温度の候補

    Args:

    Returns:
      温水暖房における熱源機の往き温水温度の候補

    """
    return [60, 40]


def get_L_dashdash_k_d(L_dashdash_k_d_t):
    """# 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)

    Args:
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)

    """
    return np.sum(L_dashdash_k_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_s_d(L_dashdash_s_d_t):
    """# 1日当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/d)

    Args:
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_s_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_w_d(L_dashdash_w_d_t):
    """# 1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)

    Args:
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_w_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_b1_d(L_dashdash_b1_d_t):
    """# 1日当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/d)

    Args:
      L_dashdash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_b1_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_b2_d(L_dashdash_b2_d_t):
    """# 1日当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/d)

    Args:
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_b2_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_ba1_d(L_dashdash_ba1_d_t):
    """# 1日当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/d)

    Args:
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_ba1_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_ba2_d(L_dashdash_ba2_d_t):
    """# 1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)

    Args:
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_ba2_d_t.reshape((365, 24)), axis=1)
