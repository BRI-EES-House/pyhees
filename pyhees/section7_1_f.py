# ============================================================================
# 付録 F 電気ヒーター給湯機及び電気ヒーター給湯温水暖房機の給湯部
# ============================================================================

import numpy as np


# ============================================================================
# F.2 消費電力量
# ============================================================================

def calc_E_E_hs_d_t(L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t, L_dashdash_b1_d_t, L_dashdash_b2_d_t,
                    L_dashdash_ba1_d_t, L_dashdash_ba2_d_t,
                    theta_ex_d_Ave_d):
    """1時間当たりの給湯機の消費電力量 (1)

    Args:
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h)
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)

    Returns:
      ndarray: 1時間当たりの給湯機の消費電力量 (kWh/h)

    """
    # 表F.2 係数
    a, b, c = (
        -0.13801,
        0.975853,
        13.7426
    )

    # 1日当たりの太陽熱補正給湯熱負荷
    L_dashdash_k_d = get_L_dashdash_k_d(L_dashdash_k_d_t)
    L_dashdash_s_d = get_L_dashdash_s_d(L_dashdash_s_d_t)
    L_dashdash_w_d = get_L_dashdash_w_d(L_dashdash_w_d_t)
    L_dashdash_b1_d = get_L_dashdash_b1_d(L_dashdash_b1_d_t)
    L_dashdash_b2_d = get_L_dashdash_b2_d(L_dashdash_b2_d_t)
    L_dashdash_ba1_d = get_L_dashdash_ba1_d(L_dashdash_ba1_d_t)
    L_dashdash_ba2_d = get_L_dashdash_ba2_d(L_dashdash_ba2_d_t)
    L_dashdash_d = get_L_dashdash_d(L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d, L_dashdash_b1_d,
                                    L_dashdash_b2_d, L_dashdash_ba1_d,
                                    L_dashdash_ba2_d)

    Theta_ex_Ave_d_t = np.repeat(theta_ex_d_Ave_d, 24)
    Theta_ex_Ave_d_t_p1 = np.roll(Theta_ex_Ave_d_t, -24)
    L_dashdash_d = np.repeat(L_dashdash_d, 24)

    E_E_hs_d_t = np.zeros(24 * 365)
    t_wh = 8

    # (1) t == 0 - 6
    f1 = np.tile(np.arange(24) <= 6, 365)
    E_E_hs_d_t[f1] = (a * Theta_ex_Ave_d_t[f1] + b * L_dashdash_d[f1] + c) / 3.6 / t_wh

    # (2) t == 7-22
    f2 = np.tile(np.logical_and(7 <= np.arange(24), np.arange(24) <= 22), 365)
    E_E_hs_d_t[f2] = 0

    # (3) t == 23
    f3 = np.tile(np.arange(24) == 23, 365)
    E_E_hs_d_t[f3] = (a * Theta_ex_Ave_d_t_p1[f3] + b * L_dashdash_d[f3] + c) / 3.6 / t_wh

    return E_E_hs_d_t


# ============================================================================
# F.3 ガス消費量
# ============================================================================

def get_E_G_hs():
    """1日当たりの給湯機のガス消費量

    Args:

    Returns:
      ndarray: 1日当たりの給湯機のガス消費量

    """
    # 1日当たりの給湯機のガス消費量は0とする
    return np.zeros(24 * 365)


# ============================================================================
# F.4 灯油消費量
# ============================================================================

def get_E_K_hs():
    """# 1日当たりの給湯機の灯油消費量

    Args:

    Returns:
      ndarray: 1日当たりの給湯機の灯油消費量

    """
    # 1日当たりの給湯機の灯油消費量は0とする
    return np.zeros(24 * 365)


# ============================================================================
# F.5 1日当たりの太陽熱補正給湯熱負荷
# ============================================================================


def get_L_dashdash_d(L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d, L_dashdash_b1_d, L_dashdash_b2_d, L_dashdash_ba1_d,
                     L_dashdash_ba2_d):
    """1日当たりの太陽熱補正給湯熱負荷 (2)

    Args:
      L_dashdash_k_d(ndarray): 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_s_d(ndarray): 1日当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/d)
      L_dashdash_w_d(ndarray): 1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)
      L_dashdash_b1_d(ndarray): 1日当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/d)
      L_dashdash_b2_d(ndarray): 1日当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/d)
      L_dashdash_ba1_d(ndarray): 1日当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/d)
      L_dashdash_ba2_d(ndarray): 1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)

    Returns:
      ndarray: 1日当たりの太陽熱補正給湯熱負荷 (MJ/d)

    """
    return (L_dashdash_k_d
            + L_dashdash_s_d
            + L_dashdash_w_d
            + L_dashdash_b1_d
            + L_dashdash_b2_d
            + L_dashdash_ba1_d
            + L_dashdash_ba2_d)


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
