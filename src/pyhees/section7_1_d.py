# ============================================================================
# 付録 D 石油給湯機及び石油給湯温水暖房機の給湯部
# ============================================================================

import numpy as np


# ============================================================================
# D.2 消費電力量
# ============================================================================

def calc_E_E_hs_d_t(W_dash_k_d_t, W_dash_s_d_t, W_dash_w_d_t, W_dash_b1_d_t, W_dash_ba1_d_t, W_dash_b2_d_t,
                    theta_ex_d_Ave_d, L_dashdash_ba2_d_t):
    """1時間当たりの給湯機の消費電力量 (1)

    Args:
      W_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯量 (L/h)
      W_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯量 (L/h)
      W_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯量 (L/h)
      W_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/h)
      W_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯量 (L/h)
      W_dash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯量 (L/h)
      theta_ex_d_Ave_d: 日平均外気温度 (℃)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの給湯機の消費電力量 (kWh/h)

    """
    # 待機時及び水栓給湯時の補機による消費電力量 (2)
    E_E_hs_aux1_d_t = get_E_E_hs_aux1_d_t(W_dash_k_d_t, W_dash_s_d_t, W_dash_w_d_t, W_dash_b1_d_t, W_dash_ba1_d_t,
                                          theta_ex_d_Ave_d)

    # 湯はり時の補機による消費電力量 (3)
    E_E_hs_aux2_d_t = calc_E_E_hs_aux2_d_t(W_dash_b2_d_t)

    # 保温時の補機による消費電力量 (4)
    E_E_hs_aux3_d_t = calc_E_E_hs_aux3_d_t(L_dashdash_ba2_d_t)

    # 1日当たりの給湯機の消費電力量 (1)
    E_E_hs_d_t = E_E_hs_aux1_d_t + E_E_hs_aux2_d_t + E_E_hs_aux3_d_t

    return E_E_hs_d_t


def get_E_E_hs_aux1_d_t(W_dash_k_d_t, W_dash_s_d_t, W_dash_w_d_t, W_dash_b1_d_t, W_dash_ba1_d_t, theta_ex_d_Ave_d):
    """1時間当たりの給湯機の待機時及び水栓給湯時の補機による消費電力量 (2)

    Args:
      W_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯量 (L/h)
      W_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯量 (L/h)
      W_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯量 (L/h)
      W_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/h)
      W_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯量 (L/h)
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)

    Returns:
      ndarray: 1時間当たりの給湯機の待機時及び水栓給湯時の補機による消費電力量 (kWh/h)

    """
    # 1時間当たりの給湯機の待機時及び水栓給湯時の補機による消費電力量 (2)
    E_E_hs_aux1_d_t = ((-0.00235 * np.repeat(theta_ex_d_Ave_d, 24) + 0.3388) / 24
                       + 0.000780 * (
                               W_dash_k_d_t + W_dash_s_d_t + W_dash_w_d_t + W_dash_b1_d_t + W_dash_ba1_d_t)) * 10 ** 3 / 3600

    return E_E_hs_aux1_d_t


def calc_E_E_hs_aux2_d_t(W_dash_b2_d_t):
    """1時間当たりの給湯機の湯はり時の補機による消費電力量 (3)

    Args:
      W_dash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯量 (L/h)

    Returns:
      ndarray: 1時間当たりの給湯機の湯はり時の補機による消費電力量 (kWh/h)

    """
    E_E_hs_aux2_d_t = np.zeros(24 * 365)

    # 1日ごとにまとめる
    W_dash_b2_d = get_W_dash_b2_d(W_dash_b2_d_t)
    W_dash_b2_d = np.repeat(W_dash_b2_d, 24)

    # W_dash_b2_d > 0 の場合
    f = W_dash_b2_d > 0
    E_E_hs_aux2_d_t[f] = (0.07 * 10 ** 3 / 3600) * W_dash_b2_d_t[f] / W_dash_b2_d[f]

    return E_E_hs_aux2_d_t


def calc_E_E_hs_aux3_d_t(L_dashdash_ba2_d_t):
    """1時間当たりの給湯機の保温時の補機による消費電力量 (4)

    Args:
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 1日当たりの給湯機の保温時の補機による消費電力量 (kWh/d)

    """
    E_E_hs_aux3 = np.zeros(24 * 365)

    L_dashdash_ba2_d = get_L_dashdash_ba2_d(L_dashdash_ba2_d_t)
    L_dashdash_ba2_d = np.repeat(L_dashdash_ba2_d, 24)

    f = (L_dashdash_ba2_d > 0)
    E_E_hs_aux3[f] = (0.02102 * L_dashdash_ba2_d[f] + 0.12852) * 10 ** 3 / 3600 \
                     * L_dashdash_ba2_d_t[f] / L_dashdash_ba2_d[f]

    return E_E_hs_aux3


# ============================================================================
# D.3 ガス消費量
# ============================================================================

def get_E_G_hs_d_t():
    """1日当たりの給湯機のガス消費量

    Args:

    Returns:
      ndarray: 1日当たりの給湯機のガス消費量

    """
    # 1日当たりの給湯機のガス消費量は0とする
    return np.zeros(24 * 365)


# ============================================================================
# D.4 灯油消費量
# ============================================================================

def calc_E_K_hs_d_t(hw_type, e_rtd, e_dash_rtd, bath_function, theta_ex_d_Ave_d, L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t,
                    L_dashdash_b1_d_t, L_dashdash_b2_d_t, L_dashdash_ba1_d_t, L_dashdash_ba2_d_t):
    """灯油消費量 (5)

    Args:
      hw_type(str): 給湯機／給湯温水暖房機の種類
      e_rtd(float): 当該給湯機の効率
      e_dash_rtd(float): エネルギーの使用の合理化に関する法律」に基づく「特定機器の性能の向上に関する製造事業者等の 判断の基準等」（ガス温水機器）に定義される「エネルギー消費効率」
      bath_function(str): ふろ機能の種類
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dashdash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/h)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの給湯機の灯油消費量 (MJ/h)

    """
    # 効率の決定
    if e_rtd == None:
        if e_dash_rtd == None:
            e_rtd = get_e_rtd_default(hw_type)
        else:
            e_rtd = get_e_rtd(e_dash_rtd)

    # 1日当たりの太陽熱補正給湯熱負荷
    L_dashdash_k_d = get_L_dashdash_k_d(L_dashdash_k_d_t)
    L_dashdash_s_d = get_L_dashdash_s_d(L_dashdash_s_d_t)
    L_dashdash_w_d = get_L_dashdash_w_d(L_dashdash_w_d_t)
    L_dashdash_b1_d = get_L_dashdash_b1_d(L_dashdash_b1_d_t)
    L_dashdash_b2_d = get_L_dashdash_b2_d(L_dashdash_b2_d_t)
    L_dashdash_ba1_d = get_L_dashdash_ba1_d(L_dashdash_ba1_d_t)
    L_dashdash_ba2_d = get_L_dashdash_ba2_d(L_dashdash_ba2_d_t)

    # 日平均給湯機効率
    e_k_d = get_e_k_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_w_d)
    e_s_d = get_e_s_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_s_d)
    e_w_d = get_e_w_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_w_d)
    e_b1_d = get_e_b1_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_b1_d)
    e_b2_d = get_e_b2_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_b2_d)
    e_ba1_d = get_e_ba1_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_ba1_d)
    e_ba2_d = get_e_ba2_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_ba2_d)

    e_k_d = np.repeat(e_k_d, 24)
    e_s_d = np.repeat(e_s_d, 24)
    e_w_d = np.repeat(e_w_d, 24)
    e_b1_d = np.repeat(e_b1_d, 24)
    e_b2_d = np.repeat(e_b2_d, 24)
    e_ba1_d = np.repeat(e_ba1_d, 24)
    e_ba2_d = np.repeat(e_ba2_d, 24)

    if bath_function == '給湯単機能':
        # (5a)
        return L_dashdash_k_d_t / e_k_d \
               + L_dashdash_s_d_t / e_s_d \
               + L_dashdash_w_d_t / e_w_d \
               + L_dashdash_b1_d_t / e_b1_d \
               + L_dashdash_ba1_d_t / e_ba1_d
    elif bath_function == 'ふろ給湯機(追焚なし)':
        # (5b)
        return L_dashdash_k_d_t / e_k_d \
               + L_dashdash_s_d_t / e_s_d \
               + L_dashdash_w_d_t / e_w_d \
               + L_dashdash_b2_d_t / e_b2_d \
               + L_dashdash_ba1_d_t / e_ba1_d
    elif bath_function == 'ふろ給湯機(追焚あり)':
        # (5c)
        return L_dashdash_k_d_t / e_k_d \
               + L_dashdash_s_d_t / e_s_d \
               + L_dashdash_w_d_t / e_w_d \
               + L_dashdash_b2_d_t / e_b2_d \
               + L_dashdash_ba2_d_t / e_ba2_d
    else:
        raise ValueError(bath_function)


def get_e_k_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_w_d):
    """台所水栓の給湯使用時における日平均給湯機効率 (6a)

    Args:
      e_rtd(float): 当該給湯機の効率
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_k_d(ndarray): 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_w_d(ndarray): 1日当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 台所水栓の給湯使用時における日平均給湯機効率

    """
    # 当該給湯機に対する効率の補正係数
    f_hs = get_f_hs(e_rtd)

    # 石油給湯機効率の回帰係数
    a_std_k = get_table_d_3()[0][0]
    b_std_k = get_table_d_3()[1][0]
    c_std_k = get_table_d_3()[2][0]
    a_k = a_std_k * f_hs  # (7a)
    b_k = b_std_k * f_hs  # (7b)
    c_k = c_std_k * f_hs  # (7c)

    e_k = a_k * theta_ex_d_Ave_d + b_k * (L_dashdash_k_d + L_dashdash_w_d) + c_k

    return np.clip(e_k, 0.0, 1.0)


def get_e_s_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_s_d):
    """浴室シャワー水栓の給湯使用時における日平均給湯機効率 (6b)

    Args:
      e_rtd(float): 当該給湯機の効率
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_s_d(ndarray): 1日当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 浴室シャワー水栓における日平均給湯機効率

    """
    # 当該給湯機に対する効率の補正係数
    f_hs = get_f_hs(e_rtd)

    # 石油給湯機効率の回帰係数
    a_std_s = get_table_d_3()[0][1]
    b_std_s = get_table_d_3()[1][1]
    c_std_s = get_table_d_3()[2][1]
    a_s = a_std_s * f_hs  # (7a)
    b_s = b_std_s * f_hs  # (7b)
    c_s = c_std_s * f_hs  # (7c)

    e_s = a_s * theta_ex_d_Ave_d + b_s * L_dashdash_s_d + c_s

    return np.clip(e_s, 0.0, 1.0)


def get_e_w_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_w_d):
    """洗面水栓の給湯使用時における日平均給湯機効率 (6c)

    Args:
      e_rtd(float): 当該給湯機の効率
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_k_d(ndarray): 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_w_d(ndarray): 1日当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 洗面水栓の給湯使用時における日平均給湯機効率

    """
    # 当該給湯機に対する効率の補正係数
    f_hs = get_f_hs(e_rtd)

    # 石油給湯機効率の回帰係数
    a_std_w = get_table_d_3()[0][2]
    b_std_w = get_table_d_3()[1][2]
    c_std_w = get_table_d_3()[2][2]
    a_w = a_std_w * f_hs  # (7a)
    b_w = b_std_w * f_hs  # (7b)
    c_w = c_std_w * f_hs  # (7c)

    e_w = a_w * theta_ex_d_Ave_d + b_w * (L_dashdash_k_d + L_dashdash_w_d) + c_w

    return np.clip(e_w, 0.0, 1.0)


def get_e_b1_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_b1_d):
    """浴槽水栓湯はり時における日平均給湯機効率 (6d)

    Args:
      e_rtd(float): 当該給湯機の効率
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_b1_d(ndarray): 1日当たりの浴槽水栓湯はり時における太陽熱補正給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 浴槽水栓湯はり時における日平均給湯機効率

    """
    # 当該給湯機に対する効率の補正係数
    f_hs = get_f_hs(e_rtd)

    # 石油給湯機効率の回帰係数
    a_std_b1 = get_table_d_3()[0][3]
    b_std_b1 = get_table_d_3()[1][3]
    c_std_b1 = get_table_d_3()[2][3]
    a_b1 = a_std_b1 * f_hs  # (7a)
    b_b1 = b_std_b1 * f_hs  # (7b)
    c_b1 = c_std_b1 * f_hs  # (7c)

    e_b1 = a_b1 * theta_ex_d_Ave_d + b_b1 * L_dashdash_b1_d + c_b1

    return np.clip(e_b1, 0.0, 1.0)


def get_e_b2_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_b2_d):
    """浴槽自動湯はり時における日平均給湯機効率 (6e)

    Args:
      e_rtd(float): 当該給湯機の効率
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_b2_d(ndarray): 1日当たりの浴槽自動湯はり時における太陽熱補正給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 浴槽自動湯はり時における日平均給湯機効率

    """
    # 当該給湯機に対する効率の補正係数
    f_hs = get_f_hs(e_rtd)

    # 石油給湯機効率の回帰係数
    a_std_b2 = get_table_d_3()[0][4]
    b_std_b2 = get_table_d_3()[1][4]
    c_std_b2 = get_table_d_3()[2][4]
    a_b2 = a_std_b2 * f_hs  # (7a)
    b_b2 = b_std_b2 * f_hs  # (7b)
    c_b2 = c_std_b2 * f_hs  # (7c)

    e_b2 = a_b2 * theta_ex_d_Ave_d + b_b2 * L_dashdash_b2_d + c_b2

    return np.clip(e_b2, 0.0, 1.0)


def get_e_ba1_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_ba1_d):
    """浴槽水さし時における日平均給湯機効率 (6f)

    Args:
      e_rtd(float): 当該給湯機の効率
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_ba1_d(ndarray): 1日当たりの浴槽水栓さし湯時における太陽熱補正給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 浴槽水さし時における日平均給湯機効率

    """
    # 当該給湯機に対する効率の補正係数
    f_hs = get_f_hs(e_rtd)

    # 石油給湯機効率の回帰係数
    a_std_ba1 = get_table_d_3()[0][5]
    b_std_ba1 = get_table_d_3()[1][5]
    c_std_ba1 = get_table_d_3()[2][5]
    a_ba1 = a_std_ba1 * f_hs  # (7a)
    b_ba1 = b_std_ba1 * f_hs  # (7b)
    c_ba1 = c_std_ba1 * f_hs  # (7c)

    e_ba1 = a_ba1 * theta_ex_d_Ave_d + b_ba1 * L_dashdash_ba1_d + c_ba1

    return np.clip(e_ba1, 0.0, 1.0)


def get_e_ba2_d(e_rtd, theta_ex_d_Ave_d, L_dashdash_ba2_d):
    """浴槽追焚時における日平均給湯機効率 (6g)

    Args:
      e_rtd(float): 当該給湯機の効率
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_ba2_d(ndarray): 1日当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 浴槽追焚時における日平均給湯機効率

    """
    # 当該給湯機に対する効率の補正係数
    f_hs = get_f_hs(e_rtd)

    # 石油給湯機効率の回帰係数
    a_std_ba2 = get_table_d_3()[0][6]
    b_std_ba2 = get_table_d_3()[1][6]
    c_std_ba2 = get_table_d_3()[2][6]
    a_ba2 = a_std_ba2 * f_hs  # (7a)
    b_ba2 = b_std_ba2 * f_hs  # (7b)
    c_ba2 = c_std_ba2 * f_hs  # (7c)

    e_ba2 = a_ba2 * theta_ex_d_Ave_d + b_ba2 * L_dashdash_ba2_d + c_ba2

    return np.clip(e_ba2, 0.0, 1.0)


def get_table_d_3():
    """表 D.3 石油給湯機効率の回帰係

    Args:

    Returns:
      list: 石油給湯機効率の回帰係

    """
    table_d_3 = [
        (0.0005, 0.0024, 0.0005, 0.0000, 0.0000, 0.0000, 0.0062),
        (0.0028, 0.0021, 0.0028, -0.0027, -0.0024, -0.0027, 0.0462),
        (0.6818, 0.7560, 0.6818, 0.9026, 0.8885, 0.9026, 0.4001)
    ]
    return table_d_3

def get_f_hs(e_rtd):
    """当該給湯機に対する効率の補正係数 (8)

    Args:
      e_rtd(float): 当該給湯機の効率

    Returns:
      float: 当該給湯機に対する効率の補正係数

    """
    return (0.8669 * e_rtd + 0.091) / 0.796


def get_e_rtd_default(hw_type):
    """当該給湯機の効率

    Args:
      hw_type(str): 給湯機／給湯温水暖房機の種類

    Returns:
      float: 当該給湯機の効率

    """
    if hw_type in ['石油潜熱回収型給湯機', '石油潜熱回収型給湯温水暖房機']:
        return 0.819
    elif hw_type in ['石油従来型給湯機', '石油従来型給湯温水暖房機']:
        return 0.779
    else:
        raise ValueError(hw_type)



def get_e_rtd(e_dash_rtd):
    """「エネルギーの使用の合理化に関する法律」に基づく「特定機器の性能の向上に関する製造事業者等の 判断の基準等」（ガス温水機器）
       # に定義される「エネルギー消費効率」 から 当該給湯器の効率を取得

    Args:
      e_dash_rtd(float): エネルギーの使用の合理化に関する法律」に基づく「特定機器の性能の向上に関する製造事業者等の 判断の基準等」（ガス温水機器）に定義される「エネルギー消費効率」

    Returns:
      float: 換算された当該給湯器の効率

    """
    return e_dash_rtd - 0.081


# ============================================================================
# D.5 1日当たりの太陽熱補正給湯熱負荷
# ============================================================================

def get_L_dashdash_k_d(L_dashdash_k_d_t):
    """1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)

    Args:
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)

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

def get_W_dash_b2_d(W_dash_b2_d_t):
    """1日当たりの浴槽追焚時における節湯補正給湯量 (L/h)

    Args:
      W_dash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯量 (L/h)

    Returns:
      ndarray: 1日当たりの浴槽追焚時における節湯補正給湯量 (L/h)

    """
    return np.sum(W_dash_b2_d_t.reshape(365, 24), axis=1)