# ============================================================================
# 付録 C ガス給湯機及びガス給湯温水暖房機の給湯部
# ============================================================================

import numpy as np


# ============================================================================
# C.2 消費電力量
# ============================================================================

def calc_E_E_hs_d_t(W_dash_k_d_t, W_dash_s_d_t, W_dash_w_d_t, W_dash_b1_d_t, W_dash_b2_d_t, W_dash_ba1_d_t,
                    theta_ex_d_Ave_d,
                    L_dashdash_ba2_d_t):
    """1時間当たりの給湯機の消費電力量 (kWh/h) (1)

    Args:
      W_dash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯負荷 (MJ/h)
      W_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/h)
      W_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/h)
      W_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/h)
      W_dash_b2_d_t(ndarray): 1時間当たりの自動湯はり時における太陽熱補正給湯負荷 (MJ/h)
      W_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの給湯機の消費電力量 (kWh/d)

    """
    # 給湯機の待機時及び水栓給湯時の補機による消費電力 (2)
    E_E_hs_aux1_d_t = get_E_E_hs_aux1_d_t(W_dash_k_d_t, W_dash_s_d_t, W_dash_w_d_t, W_dash_b1_d_t, W_dash_ba1_d_t,
                                          theta_ex_d_Ave_d)

    # 給湯機の湯はり時の補機による消費電力量 (3)
    E_E_hs_aux2_d_t = get_E_E_hs_aux2_d_t(W_dash_b2_d_t)

    # 給湯機の保温時の補機による消費電力量 (4)
    E_E_hs_aux3_d_t = calc_E_E_hs_aux3_d_t(L_dashdash_ba2_d_t)

    print('E_E_hs_aux1 = {}'.format(np.sum(E_E_hs_aux1_d_t)))
    print('E_E_hs_aux2 = {}'.format(np.sum(E_E_hs_aux2_d_t)))
    print('E_E_hs_aux3 = {}'.format(np.sum(E_E_hs_aux3_d_t)))

    return E_E_hs_aux1_d_t + E_E_hs_aux2_d_t + E_E_hs_aux3_d_t


def get_E_E_hs_aux1_d_t(W_dash_k_d_t, W_dash_s_d_t, W_dash_w_d_t, W_dash_b1_d_t, W_dash_ba1_d_t, theta_ex_d_Ave_d):
    """1時間当たりの給湯機の待機時及び水栓給湯時の補機による消費電力 (2)

    Args:
      W_dash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯負荷 (MJ/h)
      W_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/h)
      W_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/h)
      W_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/h)
      W_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)

    Returns:
      ndarray: 1時間当たりの給湯機の待機時及び水栓給湯時の補機による消費電力量 (kWh/h)

    """
    return ((-0.00172 * np.repeat(theta_ex_d_Ave_d, 24) + 0.2822) / 24
            + 0.000393 * (W_dash_k_d_t + W_dash_s_d_t + W_dash_w_d_t + W_dash_b1_d_t + W_dash_ba1_d_t)) * 10 ** 3 / 3600



def get_E_E_hs_aux2_d_t(W_dash_b2_d_t):
    """1時間当たりの給湯機の湯はり時の補機による消費電力量 (3)

    Args:
      W_dash_b2_d_t(ndarray): 1時間当たりの自動湯はり時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの給湯機の湯はり時の補機による消費電力量

    """
    E_E_hs_aux2_d_t = np.zeros(24 * 365)

    # 1日ごとにまとめる
    W_dash_b2_d = np.repeat(np.sum(W_dash_b2_d_t.reshape(365, 24), axis=1), 24)

    # W_dash_b2_d > 0 の場合
    f = W_dash_b2_d > 0
    E_E_hs_aux2_d_t[f] = (0.07 * 10 ** 3 / 3600) * W_dash_b2_d_t[f] / W_dash_b2_d[f]

    return E_E_hs_aux2_d_t


def calc_E_E_hs_aux3_d_t(L_dashdash_ba2_d_t):
    """1時間当たりの給湯機の保温時の補機による消費電力量 (4)

    Args:
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの給湯機の保温時の補機による消費電力量

    """
    E_E_hs_aux3_d_t = np.zeros(24 * 365)
    L_dashdash_ba2_d = get_L_dashdash_ba2_d(L_dashdash_ba2_d_t)
    L_dashdash_ba2_d = np.repeat(L_dashdash_ba2_d, 24)

    # L_dashdash_ba2_d > 0 の場合
    f = L_dashdash_ba2_d > 0
    E_E_hs_aux3_d_t[f] = (0.01723 * L_dashdash_ba2_d[f] + 0.06099) * 10 ** 3 / 3600 \
                         * L_dashdash_ba2_d_t[f] / L_dashdash_ba2_d[f]

    return E_E_hs_aux3_d_t


# ============================================================================
# C.3 ガス消費量
# ============================================================================

def calc_E_G_hs_d_t(theta_ex_d_Ave_d, L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t, L_dashdash_b1_d_t,
                    L_dashdash_b2_d_t,
                    L_dashdash_ba1_d_t, L_dashdash_ba2_d_t, bath_function, hw_type=None, e_rtd=None, e_dash_rtd=None):
    """1時間当たりの給湯機のガス消費量 (5)

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温 (℃)
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h)
      bath_function(str): ふろ機能の種類
      hw_type(str, optional): 給湯機の種類 (Default value = None)
      e_rtd(float, optional): 当該給湯機の効率 (Default value = None)
      e_dash_rtd(float, optional): エネルギーの使用の合理化に関する法律」に基づく「特定機器の性能の向上に関する製造事業者等の 判断の基準等」（ガス温水機器）に定義される「エネルギー消費効率」 (Default value = None)

    Returns:
      ndarray: 1時間当たりの給湯機のガス消費量 (MJ/h)

    """
    # 効率の決定
    if e_rtd is None:
        if e_dash_rtd is None:
            e_rtd = get_e_rtd_default(hw_type)
        else:
            e_rtd = get_e_rtd(e_dash_rtd, bath_function)

    # 当該給湯機に対する効率の補正係数
    f_hs = get_f_hs(e_rtd)

    # 1日当たりの太陽熱補正給湯熱負荷
    L_dashdash_k_d = get_L_dashdash_k_d(L_dashdash_k_d_t)
    L_dashdash_s_d = get_L_dashdash_s_d(L_dashdash_s_d_t)
    L_dashdash_w_d = get_L_dashdash_w_d(L_dashdash_w_d_t)
    L_dashdash_b1_d = get_L_dashdash_b1_d(L_dashdash_b1_d_t)
    L_dashdash_b2_d = get_L_dashdash_b2_d(L_dashdash_b2_d_t)
    L_dashdash_ba1_d = get_L_dashdash_ba1_d(L_dashdash_ba1_d_t)
    L_dashdash_ba2_d = get_L_dashdash_ba2_d(L_dashdash_ba2_d_t)

    # 日平均給湯機効率
    e_k_d = get_e_k_d(theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_w_d, f_hs)
    e_s_d = get_e_s_d(theta_ex_d_Ave_d, L_dashdash_s_d, f_hs)
    e_w_d = get_e_w_d(theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_w_d, f_hs)

    if bath_function == '給湯単機能':

        # 日平均給湯機効率
        e_b1_d = get_e_b1_d(theta_ex_d_Ave_d, L_dashdash_b1_d, f_hs)
        e_ba1_d = get_e_ba1_d(theta_ex_d_Ave_d, L_dashdash_ba1_d, f_hs)

        # (5a)
        return L_dashdash_k_d_t / np.repeat(e_k_d, 24) \
               + L_dashdash_s_d_t / np.repeat(e_s_d, 24) \
               + L_dashdash_w_d_t / np.repeat(e_w_d, 24) \
               + L_dashdash_b1_d_t / np.repeat(e_b1_d, 24) \
               + L_dashdash_ba1_d_t / np.repeat(e_ba1_d, 24)
    elif bath_function == 'ふろ給湯機(追焚なし)':

        # 日平均給湯機効率
        e_b2_d = get_e_b2_d(theta_ex_d_Ave_d, L_dashdash_b2_d, f_hs)
        e_ba1_d = get_e_ba1_d(theta_ex_d_Ave_d, L_dashdash_ba1_d, f_hs)

        # (5b)
        return L_dashdash_k_d_t / np.repeat(e_k_d, 24) \
               + L_dashdash_s_d_t / np.repeat(e_s_d, 24) \
               + L_dashdash_w_d_t / np.repeat(e_w_d, 24) \
               + L_dashdash_b2_d_t / np.repeat(e_b2_d, 24) \
               + L_dashdash_ba1_d_t / np.repeat(e_ba1_d, 24)
    elif bath_function == 'ふろ給湯機(追焚あり)':

        # 日平均給湯機効率
        e_b2_d = get_e_b2_d(theta_ex_d_Ave_d, L_dashdash_b2_d, f_hs)
        e_ba2_d = get_e_ba2_d(theta_ex_d_Ave_d, L_dashdash_ba2_d, f_hs)

        # (5c)
        return L_dashdash_k_d_t / np.repeat(e_k_d, 24) \
               + L_dashdash_s_d_t / np.repeat(e_s_d, 24) \
               + L_dashdash_w_d_t / np.repeat(e_w_d, 24) \
               + L_dashdash_b2_d_t / np.repeat(e_b2_d, 24) \
               + L_dashdash_ba2_d_t / np.repeat(e_ba2_d, 24)
    else:
        raise ValueError(bath_function)


def get_e_k_d(theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_w_d, f_hs):
    """台所水栓の給湯使用時における日平均給湯機効率 (6a)

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_k_d(ndarray): 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_w_d(ndarray): 1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)
      f_hs(float): 当該給湯機に対する効率の補正係数

    Returns:
      ndarray: 台所水栓の給湯使用時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    a_std_k = get_table_c_3()[0][0]
    b_std_k = get_table_c_3()[1][0]
    c_std_k = get_table_c_3()[2][0]
    a_k = a_std_k * f_hs
    b_k = b_std_k * f_hs
    c_k = c_std_k * f_hs

    e_k = np.clip(a_k * theta_ex_d_Ave_d + b_k * (L_dashdash_k_d + L_dashdash_w_d) + c_k, 0, 1)

    return e_k


def get_e_s_d(theta_ex_d_Ave_d, L_dashdash_s_d, f_hs):
    """浴室シャワー水栓の給湯使用時における日平均給湯機効率 (6b)

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_s_d(ndarray): 浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/d)
      f_hs(float): 当該給湯機に対する効率の補正係数

    Returns:
      ndarray: 浴室シャワー水栓の給湯使用時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    a_std_s = get_table_c_3()[0][1]
    b_std_s = get_table_c_3()[1][1]
    c_std_s = get_table_c_3()[2][1]
    a_s = a_std_s * f_hs
    b_s = b_std_s * f_hs
    c_s = c_std_s * f_hs

    e_s = np.clip(a_s * theta_ex_d_Ave_d + b_s * L_dashdash_s_d + c_s, 0, 1)

    return e_s


def get_e_w_d(theta_ex_d_Ave_d, L_dashdash_k_d, L_dashdash_w_d, f_hs):
    """洗面水栓の給湯使用時における日平均給湯機効率 (6c)

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_k_d(ndaray): 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_w_d(ndarray): 1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)
      f_hs(float): 当該給湯機に対する効率の補正係数

    Returns:
      ndarray: 洗面水栓の給湯使用時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    a_std_w = get_table_c_3()[0][2]
    b_std_w = get_table_c_3()[1][2]
    c_std_w = get_table_c_3()[2][2]
    a_w = a_std_w * f_hs
    b_w = b_std_w * f_hs
    c_w = c_std_w * f_hs

    e_w = np.clip(a_w * theta_ex_d_Ave_d + b_w * (L_dashdash_k_d + L_dashdash_w_d) + c_w, 0, 1)

    return e_w


def get_e_b1_d(theta_ex_d_Ave_d, L_dashdash_b1_d, f_hs):
    """浴槽水栓湯はり時における日平均給湯機効率 (6d)

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_b1_d(ndarray): 1日当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/d)
      f_hs(float): 当該給湯機に対する効率の補正係数

    Returns:
      ndarray: 浴槽水栓湯はり時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    a_std_b1 = get_table_c_3()[0][3]
    b_std_b1 = get_table_c_3()[1][3]
    c_std_b1 = get_table_c_3()[2][3]
    a_b1 = a_std_b1 * f_hs
    b_b1 = b_std_b1 * f_hs
    c_b1 = c_std_b1 * f_hs

    e_b1 = np.clip(a_b1 * theta_ex_d_Ave_d + b_b1 * L_dashdash_b1_d + c_b1, 0, 1)

    return e_b1


def get_e_b2_d(theta_ex_d_Ave_d, L_dashdash_b2_d, f_hs):
    """浴槽自動湯はり時における日平均給湯機効率 (6e)

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_b2_d(ndarray): 1日当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/d)
      f_hs(float): 当該給湯機に対する効率の補正係数

    Returns:
      ndarray: 浴槽自動湯はり時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    a_std_b2 = get_table_c_3()[0][4]
    b_std_b2 = get_table_c_3()[1][4]
    c_std_b2 = get_table_c_3()[2][4]
    a_b2 = a_std_b2 * f_hs
    b_b2 = b_std_b2 * f_hs
    c_b2 = c_std_b2 * f_hs

    e_b2 = np.clip(a_b2 * theta_ex_d_Ave_d + b_b2 * L_dashdash_b2_d + c_b2, 0, 1)

    return e_b2


def get_e_ba1_d(theta_ex_d_Ave_d, L_dashdash_ba1_d, f_hs):
    """浴槽水栓さし湯時における日平均給湯機効率 (6f)

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_ba1_d(ndarray): 1日当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/d)
      f_hs(floatr): 当該給湯機に対する効率の補正係数

    Returns:
      ndarray: 浴槽水栓さし湯時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    a_std_ba1 = get_table_c_3()[0][5]
    b_std_ba1 = get_table_c_3()[1][5]
    c_std_ba1 = get_table_c_3()[2][5]
    a_ba1 = a_std_ba1 * f_hs
    b_ba1 = b_std_ba1 * f_hs
    c_ba1 = c_std_ba1 * f_hs

    e_ba1 = np.clip(a_ba1 * theta_ex_d_Ave_d + b_ba1 * L_dashdash_ba1_d + c_ba1, 0, 1)

    return e_ba1


def get_e_ba2_d(theta_ex_d_Ave_d, L_dashdash_ba2_d, f_hs):
    """浴槽追追焚時における日平均給湯機効率 (6g)

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_ba2_d(ndarray): 1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)
      f_hs(float): 当該給湯機に対する効率の補正係数

    Returns:
      ndarray: 浴槽追追焚時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    a_std_ba2 = get_table_c_3()[0][6]
    b_std_ba2 = get_table_c_3()[1][6]
    c_std_ba2 = get_table_c_3()[2][6]
    a_ba2 = a_std_ba2 * f_hs
    b_ba2 = b_std_ba2 * f_hs
    c_ba2 = c_std_ba2 * f_hs

    e_ba2 = np.clip(a_ba2 * theta_ex_d_Ave_d + b_ba2 * L_dashdash_ba2_d + c_ba2, 0, 1)

    return e_ba2


def get_table_c_3():
    """表C.3 ガス給湯機効率の回帰係数a_std_u, b_std_u, c_std_u

    Args:

    Returns:
      list: ガス給湯機効率の回帰係数a_std_u, b_std_u, c_std_u

    """
    table_c_3 = [
        (0.0019, 0.0006, 0.0019, 0.0000, 0.0000, 0.0000, 0.0033),
        (0.0013, 0.0005, 0.0013, 0.0002, -0.0005, 0.0002, 0.0194),
        (0.6533, 0.7414, 0.6533, 0.7839, 0.7828, 0.7839, 0.5776)
    ]
    return table_c_3

def get_f_hs(e_rtd):
    """当該給湯機に対する効率の補正係数 f_hs (8)

    Args:
      e_rtd(float): 当該給湯機の効率

    Returns:
      float: 当該給湯機に対する効率の補正係数

    """
    return (0.8754 * e_rtd + 0.060) / 0.745


def get_e_rtd_default(hw_type):
    """当該給湯機の効率

    Args:
      hw_type(str): 給湯機／給湯温水暖房機の種類

    Returns:
      float: 当該給湯機の効率

    """
    if hw_type in ['ガス潜熱回収型給湯機', 'ガス潜熱回収型給湯温水暖房機']:
        return 0.836
    elif hw_type in ['ガス従来型給湯機', 'ガス従来型給湯温水暖房機']:
        return 0.704
    else:
        raise ValueError(hw_type)


def get_e_rtd(e_dash_rtd, bath_function):
    """「エネルギーの使用の合理化に関する法律」に基づく「特定機器の性能の向上に関する製造事業者等の 判断の基準等」（ガス温水機器）
       に定義される「エネルギー消費効率」 から 当該給湯器の効率を取得 (9)

    Args:
      e_dash_rtd(float): エネルギーの使用の合理化に関する法律」に基づく「特定機器の性能の向上に関する製造事業者等の 判断の基準等」（ガス温水機器）に定義される「エネルギー消費効率」
      bath_function(str): ふろ機能の種類

    Returns:
      float: 換算された当該給湯器の効率

    """
    if bath_function == '給湯単機能' or bath_function == 'ふろ給湯機(追焚なし)':
        return e_dash_rtd - 0.046  # (9a)
    elif bath_function == 'ふろ給湯機(追焚あり)':
        return e_dash_rtd - 0.064  # (9b)
    else:
        raise ValueError()


# ============================================================================
# C.4 灯油消費量
# ============================================================================

def get_E_K_hs_d_t():
    """1日当たりの給湯機の灯油消費量

    Args:

    Returns:
      ndarray: 1日当たりの給湯機の灯油消費量

    """
    # 1日当たりの給湯機の灯油消費量は0とする
    return np.zeros(24 * 365)


# ============================================================================
# C.5 1日当たりの太陽熱補正給湯熱負荷
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
