# ============================================================================
# 付録 G 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機
#        （給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式）
# ============================================================================

import numpy as np


# ============================================================================
# G.2.3 消費電力量
# ============================================================================

def calc_E_E_hs_d_t(hybrid_category, theta_ex_d_Ave_d, L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t,
                    L_dashdash_b2_d_t, L_dashdash_ba2_d_t):
    """1時間当たりの給湯機の消費電力量 (1)

    Args:
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における対応熱補正給湯負荷 (MJ/hd)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における対応熱補正給湯負荷 (MJ/h)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における対応熱補正給湯負荷 (MJ/h)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における対応熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの給湯機の消費電力量 (kWh/h)

    """
    # 1日当たりの太陽熱補正給湯熱負荷
    L_dashdash_k_d = get_L_dashdash_k_d(L_dashdash_k_d_t)
    L_dashdash_s_d = get_L_dashdash_s_d(L_dashdash_s_d_t)
    L_dashdash_w_d = get_L_dashdash_w_d(L_dashdash_w_d_t)
    L_dashdash_b2_d = get_L_dashdash_b2_d(L_dashdash_b2_d_t)
    L_dashdash_ba2_d = get_L_dashdash_ba2_d(L_dashdash_ba2_d_t)

    # 1日当たりの給湯機の消費電力量 (2)
    E_E_hs_d = calc_E_E_hs_d(hybrid_category, theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d,
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


def calc_E_E_hs_d(hybrid_category, theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d,
                  L_dashdash_b2_d, L_dashdash_ba2_d):
    """1日当たりの給湯機の消費電力量 (2)

    Args:
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_k_d(ndarray): 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_s_d(ndarray): 1日当たりの浴室シャワー水栓における対応熱補正給湯負荷 (MJ/d)
      L_dashdash_w_d(ndarray): 1日当たりの洗面水栓における対応熱補正給湯負荷 (MJ/d)
      L_dashdash_b2_d(ndarray): 1日当たりの浴槽自動湯はり時における対応熱補正給湯負荷 (MJ/d)
      L_dashdash_ba2_d(ndarray): 1日当たりの浴槽追焚時における対応熱補正給湯負荷 (MJ/d)

    Returns:
      ndarray: 1日当たりの給湯機の消費電力量 (kWh/d)

    """
    # 係数a,b,c
    a, b, c = get_coeff_eq1(hybrid_category)

    # デフロスト運転による消費電力量の補正係数 (3)
    C_E_def = get_C_E_def_d(theta_ex_d_Ave_d)

    # 1日当たりの給湯機の消費電力量 (2)
    E_E_hs_d = ((a * theta_ex_d_Ave_d + b * (
            L_dashdash_k_d + L_dashdash_s_d + L_dashdash_w_d + L_dashdash_b2_d) + c) * C_E_def
                + (0.01723 * L_dashdash_ba2_d + 0.06099)) * 10 ** 3 / 3600
    E_E_hs_d = np.clip(E_E_hs_d, 0, None)

    return E_E_hs_d


def get_coeff_eq1(hybrid_category):
    """係数a,b,c

    Args:
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分

    Returns:
      tuple: 式(1)における係数 a, b, c

    """
    if hybrid_category == '区分1':
        return get_table_g_2()[0][0], get_table_g_2()[1][0], get_table_g_2()[2][0]
    elif hybrid_category == '区分2':
        return get_table_g_2()[0][1], get_table_g_2()[1][1], get_table_g_2()[2][1]
    elif hybrid_category == '区分3':
        return get_table_g_2()[0][2], get_table_g_2()[1][2], get_table_g_2()[2][2]
    else:
        raise ValueError(hybrid_category)


def get_table_g_2():
    """表G.2 係数

    Args:

    Returns:
      list: 表G.2 係数

    """
    # 表G.2 係数
    table_g_2 = [
        (-0.18441, -0.18114, -0.18441),
        (0.18530, 0.10483, 0.18530),
        (3.51058, 5.85285, 3.51058)
    ]
    return table_g_2

def get_C_E_def_d(theta_ex_d_Ave_d):
    """1日当たりのデフロスト運転による消費電力量の補正係数 (3)

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)

    Returns:
      ndarray: 1日当たりのデフロスト運転による消費電力量の補正係数 (-)

    """
    C_E_def_d = np.ones(365)

    # theta_ex_d_Ave_d < 7 の場合
    f = theta_ex_d_Ave_d < 7
    C_E_def_d[f] = 1.0 + (7 - theta_ex_d_Ave_d[f]) * 0.0091

    return C_E_def_d


# ============================================================================
# G.2 ガス消費量
# ============================================================================

def calc_E_G_hs_d_t(hybrid_category, theta_ex_d_Ave_d, L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t,
                    L_dashdash_b2_d_t, L_dashdash_ba2_d_t):
    """1時間当たりの給湯機のガス消費量 (4)

    Args:
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における対応熱補正給湯負荷 (MJ/hd)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における対応熱補正給湯負荷 (MJ/h)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における対応熱補正給湯負荷 (MJ/h)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における対応熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの給湯機のガス消費量 (MJ/h)

    """
    # 1日当たりの太陽熱補正給湯熱負荷
    L_dashdash_k_d = get_L_dashdash_k_d(L_dashdash_k_d_t)
    L_dashdash_s_d = get_L_dashdash_s_d(L_dashdash_s_d_t)
    L_dashdash_w_d = get_L_dashdash_w_d(L_dashdash_w_d_t)
    L_dashdash_b2_d = get_L_dashdash_b2_d(L_dashdash_b2_d_t)
    L_dashdash_ba2_d = get_L_dashdash_ba2_d(L_dashdash_ba2_d_t)

    # 1日当たりの給湯機のガス消費量 (4)
    E_G_hs_d = calc_E_G_hs_d(hybrid_category, theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d,
                             L_dashdash_b2_d, L_dashdash_ba2_d)

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


def calc_E_G_hs_d(hybrid_category, theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d, L_dashdash_b2_d,
                  L_dashdash_ba2_d):
    """1日当たりの給湯機のガス消費量 (5)

    Args:
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_k_d(ndarray): 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_s_d(ndarray): 1日当たりの浴室シャワー水栓における対応熱補正給湯負荷 (MJ/d)
      L_dashdash_w_d(ndarray): 1日当たりの洗面水栓における対応熱補正給湯負荷 (MJ/d)
      L_dashdash_b2_d(ndarray): 1日当たりの浴槽自動湯はり時における対応熱補正給湯負荷 (MJ/d)
      L_dashdash_ba2_d(ndarray): 1日当たりの浴槽追焚時における対応熱補正給湯負荷 (MJ/d)

    Returns:
      ndarray: 1日当たりの給湯機のガス消費量 (MJ/d)

    """
    # 係数d,e,f
    d, e, f = get_coeff_eq3(hybrid_category)

    # デフロスト係数
    C_G_def_d = get_C_G_def_d(theta_ex_d_Ave_d)

    # 浴槽追焚時における日平均給湯機効率
    e_ba2 = get_e_ba2_d(theta_ex_d_Ave_d, L_dashdash_ba2_d)

    # 1日当たりの給湯機のガス消費量 (3)
    E_G_hs = (d * theta_ex_d_Ave_d + e * (
            L_dashdash_k_d + L_dashdash_s_d + L_dashdash_w_d + L_dashdash_b2_d) + f) * C_G_def_d + (
                         L_dashdash_ba2_d / e_ba2)
    E_G_hs = np.clip(E_G_hs, 0, None)

    return E_G_hs


def get_coeff_eq3(hybrid_category):
    """係数d,e,f

    Args:
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分

    Returns:
      tuple: 式(3)における係数 d,e,f

    """
    if hybrid_category == '区分1':
        return get_table_g_3()[0][0], get_table_g_3()[1][0], get_table_g_3()[2][0]
    elif hybrid_category == '区分2':
        return get_table_g_3()[0][1], get_table_g_3()[1][1], get_table_g_3()[2][1]
    elif hybrid_category == '区分3':
        return get_table_g_3()[0][2], get_table_g_3()[1][2], get_table_g_3()[2][2]
    else:
        raise ValueError(hybrid_category)

def get_table_g_3():
    """表G.3 係数

    Args:

    Returns:
      list: 表G.3 係数

    """
    # 表G.3 係数
    table_g_3 = [
        (-0.52617, -0.05770, -0.52617),
        (0.15061, 0.47525, 0.15061),
        (15.18195, -6.34593, 15.18195)
    ]
    return table_g_3


def get_e_ba2_d(theta_ex_d_Ave_d, L_dashdash_ba2_d):
    """浴槽追焚時における日平均給湯機効率 (6)

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_ba2_d(ndarray): 1日当たりの浴槽追焚時における対応熱補正給湯負荷 (MJ/d)

    Returns:
      ndarray: 浴槽追焚時における日平均給湯機効率 (-)

    """
    # 係数g,h,i
    g, h, i = get_coeff_eq4()

    e_ba2 = g * theta_ex_d_Ave_d + h * L_dashdash_ba2_d + i

    # 効率が1.0を超えない範囲
    e_ba2 = np.clip(e_ba2, None, 1)

    return e_ba2


def get_coeff_eq4():
    """係数 g, h, i

    Args:

    Returns:
      tuple: 式(4)における係数 g,h,i

    """
    # 表G.4 係数
    table_g_4 = (0.0048, 0.0060, 0.7544)

    return table_g_4


def get_C_G_def_d(theta_ex_d_Ave_d):
    """1日当たりのデフロスト運転によるガス消費量の補正係数 (7)

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)

    Returns:
      ndarray: 1日当たりのデフロスト運転によるガス消費量の補正係数 (-)

    """
    C_G_def_d = np.ones(365)

    # theta_ex_d_Ave_d < 7 の場合
    f = (theta_ex_d_Ave_d < 7)
    C_G_def_d[f] = 1.0 + (7 - theta_ex_d_Ave_d[f]) * 0.0205

    return C_G_def_d


# ============================================================================
# G.2.5 灯油消費量
# ============================================================================

def get_E_K_hs_d_t():
    """1時間当たりの給湯機の灯油消費量

    Args:

    Returns:
      ndarray: 1時間当たりの給湯機の灯油消費量

    """
    # 1日当たりの給湯機の灯油消費量は0とする
    return np.zeros(24 * 365)


def get_L_dashdash_k_d(L_dashdash_k_d_t):
    """1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)

    Args:
      L_dashdash_k_d_t(ndarra): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)

    """
    return np.sum(L_dashdash_k_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_s_d(L_dashdash_s_d_t):
    """1日当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/d)

    Args:
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_s_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_w_d(L_dashdash_w_d_t):
    """1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)

    Args:
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_w_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_b1_d(L_dashdash_b1_d_t):
    """1日当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/d)

    Args:
      L_dashdash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_b1_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_b2_d(L_dashdash_b2_d_t):
    """1日当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/d)

    Args:
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_b2_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_ba1_d(L_dashdash_ba1_d_t):
    """1日当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/d)

    Args:
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_ba1_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_ba2_d(L_dashdash_ba2_d_t):
    """1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)

    Args:
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_ba2_d_t.reshape((365, 24)), axis=1)
