# ============================================================================
# 付録D バックアップボイラーの給湯部(ガス熱源)
# ============================================================================

import numpy as np


# ============================================================================
# D.2 ガス消費量
# ============================================================================

def calc_E_G_BB_DHW_d_t(bath_function,
                        L_BB_DHW_k_d_t, L_BB_DHW_s_d_t, L_BB_DHW_w_d_t,
                        L_BB_DHW_b1_d_t, L_BB_DHW_b2_d_t, L_BB_DHW_ba1_d_t, L_BB_DHW_ba2_d_t,
                        e_rtd_DHW_BB, Theta_ex_Ave):
    """1時間当たりの給湯時のバックアップボイラーの燃料消費量 (MJ/h)

    Args:
      bath_function(str): ふろ機能の種類
      L_BB_DHW_k_d_t(ndarray): 1時間当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_w_d_t(ndarray): 1時間当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はりにおけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はりにおけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      e_rtd_DHW_BB(float): バックアップボイラー(給湯)の給湯機の効率
      Theta_ex_Ave(ndarray): 外気温度 (℃)

    Returns:
      ndarray: 1時間当たりの給湯時のバックアップボイラーの燃料消費量 (MJ/h)

    """
    # 1日当たりの太陽熱補正給湯熱負荷 (7)
    L_BB_DHW_k_d = get_L_BB_DHW_k_d(L_BB_DHW_k_d_t)
    L_BB_DHW_s_d = get_L_BB_DHW_k_d(L_BB_DHW_s_d_t)
    L_BB_DHW_w_d = get_L_BB_DHW_k_d(L_BB_DHW_w_d_t)
    L_BB_DHW_b1_d = get_L_BB_DHW_k_d(L_BB_DHW_b1_d_t)
    L_BB_DHW_b2_d = get_L_BB_DHW_k_d(L_BB_DHW_b2_d_t)
    L_BB_DHW_ba1_d = get_L_BB_DHW_k_d(L_BB_DHW_ba1_d_t)
    L_BB_DHW_ba2_d = get_L_BB_DHW_k_d(L_BB_DHW_ba2_d_t)

    # 1時間当たりのバックアップボイラーの保温時の補機による消費電力量 (kWh/h) (6)
    E_E_BB_aux_ba2_d_t = get_E_E_BB_aux_ba2_d_t(L_BB_DHW_ba2_d_t)

    # 各用途における日平均バックアップボイラー効率 (-) (2)
    e_k_d, e_w_d, e_s_d, e_b1_d, e_b2_d, e_ba1_d, e_ba2_d = calc_e_x_d(e_rtd_DHW_BB, Theta_ex_Ave,
                                                                       L_BB_DHW_k_d, L_BB_DHW_w_d, L_BB_DHW_s_d,
                                                                       L_BB_DHW_b1_d, L_BB_DHW_b2_d,
                                                                       L_BB_DHW_ba1_d, L_BB_DHW_ba2_d)

    # 1時間当たりの浴槽追焚時のバックアップボイラーのガス消費量 (MJ/d) (3)
    E_G_BB_DHW_ba2_d_t = get_E_G_BB_DHW_ba2_d_t(L_BB_DHW_ba2_d_t, e_ba2_d)

    # 1時間当たりの給湯時のバックアップボイラーの燃料消費量 (MJ/h) (1)
    E_G_BB_DHW_d_t = get_E_G_BB_DHW_d_t(bath_function, L_BB_DHW_k_d_t, L_BB_DHW_s_d_t, L_BB_DHW_w_d_t,
                                        L_BB_DHW_b1_d_t, L_BB_DHW_b2_d_t, L_BB_DHW_ba1_d_t, L_BB_DHW_ba2_d_t,
                                        e_k_d, e_s_d, e_w_d,
                                        e_b1_d, e_b2_d, e_ba1_d, e_ba2_d)

    print('L_BB_DHW_k = {} [MJ/yr]'.format(np.sum(L_BB_DHW_k_d_t)))
    print('L_BB_DHW_s = {} [MJ/yr]'.format(np.sum(L_BB_DHW_s_d_t)))
    print('L_BB_DHW_w = {} [MJ/yr]'.format(np.sum(L_BB_DHW_w_d_t)))
    print('L_BB_DHW_b1 = {} [MJ/yr]'.format(np.sum(L_BB_DHW_b1_d_t)))
    print('L_BB_DHW_b2 = {} [MJ/yr]'.format(np.sum(L_BB_DHW_b2_d_t)))
    print('L_BB_DHW_ba1 = {} [MJ/yr]'.format(np.sum(L_BB_DHW_ba1_d_t)))
    print('L_BB_DHW_ba2 = {} [MJ/yr]'.format(np.sum(L_BB_DHW_ba2_d_t)))
    print('sum(e_k_d) = {} [-]'.format(np.sum(e_k_d)))
    print('sum(e_s_d) = {} [-]'.format(np.sum(e_s_d)))
    print('sum(e_w_d) = {} [-]'.format(np.sum(e_w_d)))
    print('sum(e_b1_d) = {} [-]'.format(np.sum(e_b1_d)))
    print('sum(e_b2_d) = {} [-]'.format(np.sum(e_b2_d)))
    print('sum(e_ba1_d) = {} [-]'.format(np.sum(e_ba1_d)))
    print('sum(e_ba2_d) = {} [-]'.format(np.sum(e_ba2_d)))

    return E_G_BB_DHW_d_t, E_G_BB_DHW_ba2_d_t


def get_E_G_BB_DHW_d_t(bath_function,
                       L_BB_DHW_k_d_t, L_BB_DHW_s_d_t, L_BB_DHW_w_d_t,
                       L_BB_DHW_b1_d_t, L_BB_DHW_b2_d_t, L_BB_DHW_ba1_d_t, L_BB_DHW_ba2_d_t,
                       e_k_d, e_s_d, e_w_d,
                       e_b1_d, e_b2_d, e_ba1_d, e_ba2_d):
    """1時間当たりの給湯時のバックアップボイラーの燃料消費量 (MJ/h) (1)

    Args:
      bath_function(str): ふろ機能の種類
      L_BB_DHW_k_d_t(ndarray): 1時間当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_w_d_t(ndarray): 1時間当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はりにおけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はりにおけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      e_k_d(ndarray): 台所水栓における日平均バックアップボイラー効率 (-)
      e_s_d(ndarray): シャワー水栓における日平均バックアップボイラー効率 (-)
      e_w_d(ndarray): 洗面水栓における日平均バックアップボイラー効率 (-)
      e_b1_d(ndarray): 浴槽水栓湯はりにおける日平均バックアップボイラー効率 (-)
      e_b2_d(ndarray): 浴槽自動湯はりにおける日平均バックアップボイラー効率 (-)
      e_ba1_d(ndarray): 浴槽水栓さし湯における日平均バックアップボイラー効率 (-)
      e_ba2_d(ndarray): 浴槽追焚における日平均バックアップボイラー効率 (-)

    Returns:
      ndarray: 1時間当たりの給湯時のバックアップボイラーの燃料消費量

    """
    e_k_d = np.repeat(e_k_d, 24)
    e_s_d = np.repeat(e_s_d, 24)
    e_w_d = np.repeat(e_w_d, 24)
    e_b1_d = np.repeat(e_b1_d, 24)
    e_b2_d = np.repeat(e_b2_d, 24)
    e_ba1_d = np.repeat(e_ba1_d, 24)
    e_ba2_d = np.repeat(e_ba2_d, 24)

    if bath_function == '給湯単機能':
        # 給湯単機能の場合 (1a)
        E_G_BB_DHW_d_t = (L_BB_DHW_k_d_t / e_k_d
                          + L_BB_DHW_s_d_t / e_s_d
                          + L_BB_DHW_w_d_t / e_w_d
                          + L_BB_DHW_b1_d_t / e_b1_d
                          + L_BB_DHW_ba1_d_t / e_ba1_d)
    elif bath_function == 'ふろ給湯機(追焚なし)':
        # ふろ給湯機(追焚なし)の場合 (1b)
        E_G_BB_DHW_d_t = (L_BB_DHW_k_d_t / e_k_d
                          + L_BB_DHW_s_d_t / e_s_d
                          + L_BB_DHW_w_d_t / e_w_d
                          + L_BB_DHW_b2_d_t / e_b2_d
                          + L_BB_DHW_ba1_d_t / e_ba1_d)
    elif bath_function == 'ふろ給湯機(追焚あり)':
        # ふろ給湯機(追焚あり)の場合 (1c)
        E_G_BB_DHW_d_t = (L_BB_DHW_k_d_t / e_k_d
                          + L_BB_DHW_s_d_t / e_s_d
                          + L_BB_DHW_w_d_t / e_w_d
                          + L_BB_DHW_b2_d_t / e_b2_d
                          + L_BB_DHW_ba2_d_t / e_ba2_d)
    else:
        raise ValueError(bath_function)

    return E_G_BB_DHW_d_t


def get_E_G_BB_DHW_ba2_d_t(L_BB_DHW_ba2_d_t, e_ba2_d):
    """1時間当たりの浴槽追焚時のバックアップボイラーのガス消費量 (MJ/d) (2)

    Args:
      L_BB_DHW_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時のバックアップボイラーのガス消費量 (MJ/h)
      e_ba2_d(ndarray): 浴槽追焚時におけるバックアップボイラーの給湯部の日平均効率 (-)

    Returns:
      ndarray: 1時間当たりの浴槽追焚時のバックアップボイラーのガス消費量 (MJ/d)

    """
    E_G_BB_DHW_ba2_d_t = L_BB_DHW_ba2_d_t / np.repeat(e_ba2_d, 24)
    return E_G_BB_DHW_ba2_d_t


def calc_e_x_d(e_rtd_DHW_BB, Theta_ex_Ave,
               L_BB_DHW_k_d, L_BB_DHW_w_d, L_BB_DHW_s_d,
               L_BB_DHW_b1_d, L_BB_DHW_b2_d,
               L_BB_DHW_ba1_d, L_BB_DHW_ba2_d):
    """各用途における日平均バックアップボイラー効率 (-) (3)

    Args:
      e_rtd_DHW_BB(float): バックアップボイラーの給湯機の効率
      Theta_ex_Ave(ndarray): 日平均外気温度 (℃)
      L_BB_DHW_k_d(ndarray): 1日当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_w_d(ndarray_): 1日当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_s_d(ndarray): 1日当たりの浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_b1_d(ndarray): 1日当たりの浴槽水栓湯はりにおけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_b2_d(ndarray): 1日当たりの浴槽自動湯はりにおけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_ba1_d(ndarray): 1日当たりの浴槽水栓さし湯におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      L_BB_DHW_ba2_d(ndarray): 1日当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)

    Returns:
      tuple: 台所水栓・洗面水栓・浴室シャワー水栓・浴槽水栓湯はり・浴槽自動湯はり・浴槽水栓さし巣・浴槽追焚ににおける日平均バックアップボイラー効率 e_BB_k_d, e_BB_w_d, e_BB_s_d, e_BB_b1_d, e_BB_b2_d, e_BB_ba1_d, e_BB_ba2_d

    """
    f_hs = get_f_hs(e_rtd_DHW_BB)
    e_k_d = get_e_k(Theta_ex_Ave, L_BB_DHW_k_d, L_BB_DHW_w_d, f_hs)
    e_w_d = get_e_w(Theta_ex_Ave, L_BB_DHW_k_d, L_BB_DHW_w_d, f_hs)
    e_s_d = get_e_s(Theta_ex_Ave, L_BB_DHW_s_d, f_hs)
    e_b1_d = get_e_b1(Theta_ex_Ave, L_BB_DHW_b1_d, f_hs)
    e_b2_d = get_e_b2(Theta_ex_Ave, L_BB_DHW_b2_d, f_hs)
    e_ba1_d = get_e_ba1(Theta_ex_Ave, L_BB_DHW_ba1_d, f_hs)
    e_ba2_d = calc_e_ba2(Theta_ex_Ave, L_BB_DHW_ba2_d, f_hs)

    return e_k_d, e_w_d, e_s_d, e_b1_d, e_b2_d, e_ba1_d, e_ba2_d


def get_e_k(Theta_ex_Ave, L_BB_DHW_k, L_BB_DHW_w, f_hs):
    """台所水栓の給湯使用時における日平均給湯機効率 (3a)

    Args:
      Theta_ex_Ave(ndarray): 日平均外気温度 (℃)
      L_BB_DHW_k(ndarray): 1日当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷
      L_BB_DHW_w(ndarray): 1日当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷
      f_hs(float): 当該給湯機に対する効率の補正係数

    Returns:
      ndarray: 台所水栓の給湯使用時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    std_k = get_std_u('k')
    a_k, b_k, c_k = get_rcoeff(std_k, f_hs)

    e_k = np.clip(a_k * Theta_ex_Ave + b_k * (L_BB_DHW_k + L_BB_DHW_w) + c_k, 0, 1)

    return e_k


def get_e_s(Theta_ex_Ave, L_BB_DHW_s, f_hs):
    """浴室シャワー水栓の給湯使用時における日平均給湯機効率 (3b)

    Args:
      Theta_ex_Ave: 日平均外気温度 (℃)
      L_BB_DHW_s(ndarray): 浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷
      f_hs(float): 当該給湯機に対する効率の補正係数

    Returns:
      ndarray: 浴室シャワー水栓の給湯使用時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    std_s = get_std_u('s')
    a_s, b_s, c_s = get_rcoeff(std_s, f_hs)

    e_s = np.clip(a_s * Theta_ex_Ave + b_s * L_BB_DHW_s + c_s, 0, 1)

    return e_s


def get_e_w(Theta_ex_Ave, L_BB_DHW_k, L_dashdash_w, f_hs):
    """洗面水栓の給湯使用時における日平均給湯機効率 (3c)

    Args:
      Theta_ex_Ave(ndarray): 日平均外気温度 (℃)
      L_BB_DHW_k(ndarray): 1日当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷
      L_dashdash_w(ndarray): 1日当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷
      f_hs(float): 当該給湯機に対する効率の補正係数

    Returns:
      ndarray: 洗面水栓の給湯使用時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    std_w = get_std_u('w')
    a_w, b_w, c_w = get_rcoeff(std_w, f_hs)

    e_w = np.clip(a_w * Theta_ex_Ave + b_w * (L_BB_DHW_k + L_dashdash_w) + c_w, 0, 1)

    return e_w


def get_e_b1(Theta_ex_Ave, L_BB_DHW_b1, f_hs):
    """浴槽水栓湯はり時における日平均給湯機効率 (3d)

    Args:
      Theta_ex_Ave(ndarray): 日平均外気温度 (℃)
      L_BB_DHW_b1(ndarray): 1日当たりの浴槽水栓湯はり時におけるバックアップボイラーが分担する給湯熱負荷
      f_hs(float): 当該給湯機に対する効率の補正係数

    Returns:
      ndarray: 浴槽水栓湯はり時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    std_b1 = get_std_u('b1')
    a_b1, b_b1, c_b1 = get_rcoeff(std_b1, f_hs)

    e_b1 = np.clip(a_b1 * Theta_ex_Ave + b_b1 * L_BB_DHW_b1 + c_b1, 0, 1)

    return e_b1


def get_e_b2(Theta_ex_Ave, L_BB_DHW_b2, f_hs):
    """浴槽自動湯はり時における日平均給湯機効率 (3e)

    Args:
      Theta_ex_Ave(ndarray): 日平均外気温度 (℃)
      L_BB_DHW_b2(ndarray): 1日当たりの浴槽水栓湯はり時におけるバックアップボイラーが分担する給湯熱負荷
      f_hs(float): 当該給湯機に対する効率の補正係数

    Returns:
      ndarray: 浴槽自動湯はり時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    std_b2 = get_std_u('b2')
    a_b2, b_b2, c_b2 = get_rcoeff(std_b2, f_hs)

    e_b2 = np.clip(a_b2 * Theta_ex_Ave + b_b2 * L_BB_DHW_b2 + c_b2, 0, 1)

    return e_b2


def get_e_ba1(Theta_ex_Ave, L_BB_DHW_ba1, f_hs):
    """浴槽水栓さし湯時における日平均給湯機効率 (3f)

    Args:
      Theta_ex_Ave(ndarray): 日平均外気温度 (℃)
      L_BB_DHW_ba1(ndarray): 1日当たりの浴槽水栓さし湯時におけるバックアップボイラーが分担する給湯熱負荷
      f_hs: 当該給湯機に対する効率の補正係数

    Returns:
      浴槽水栓さし湯時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    std_ba1 = get_std_u('ba1')
    a_ba1, b_ba1, c_ba1 = get_rcoeff(std_ba1, f_hs)

    e_ba1 = np.clip(a_ba1 * Theta_ex_Ave + b_ba1 * L_BB_DHW_ba1 + c_ba1, 0, 1)

    return e_ba1


def calc_e_ba2(Theta_ex_Ave, L_BB_DHW_ba2, f_hs):
    """浴槽追追焚時における日平均給湯機効率 (3g)

    Args:
      Theta_ex_Ave(ndarray): 日平均外気温度 (℃)
      L_BB_DHW_ba2(ndarray): 1日当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
      f_hs(float): 当該給湯機に対する効率の補正係数

    Returns:
      ndarray: 浴槽追追焚時における日平均給湯機効率

    """
    # 日平均給湯機効率を計算するための回帰係数
    std_ba2 = get_std_u('ba2')
    a_ba2, b_ba2, c_ba2 = get_rcoeff(std_ba2, f_hs)

    e_ba2 = np.clip(a_ba2 * Theta_ex_Ave + b_ba2 * L_BB_DHW_ba2 + c_ba2, 0, 1)

    return e_ba2


def get_rcoeff(std_u, f_hs):
    """a_u, b_u, c_uの取得 (4a)(4b)(4c)

    Args:
      std_u(param f_hs: バックアップボイラーの給湯部に対する効率の補正係数 (-)): 表D.3により求まる係数 (-)
      f_hs: バックアップボイラーの給湯部に対する効率の補正係数 (-)

    Returns:
      日平均給湯機効率を計算するための回帰係数 a_u, b_u, c_u

    """
    a_u = std_u[0] * f_hs
    b_u = std_u[1] * f_hs
    c_u = std_u[2] * f_hs
    return a_u, b_u, c_u


def get_std_u(u):
    """バックアップボイラーの給湯部の効率の回帰係数a_std_u, b_std_u, c_std_u

    Args:
      u(str): 用途を表す添え字(k,s,w,b1,b2,ba1,ba2)

    Returns:
      tuple: バックアップボイラーの給湯部の効率の回帰係数a_std_u, b_std_u, c_std_u

    """
    # 表C.3 バックアップボイラーの給湯部の効率の回帰係数a_std_u, b_std_u, c_std_u
    table_d_3 = [
        (0.0019, 0.0006, 0.0019, 0.0000, 0.0000, 0.0000, 0.0033),
        (0.0013, 0.0005, 0.0013, 0.0002, -0.0005, 0.0002, 0.0194),
        (0.6533, 0.7414, 0.6533, 0.7839, 0.7828, 0.7839, 0.5776)
    ]
    i = {'k': 0, 's': 1, 'w': 2, 'b1': 3, 'b2': 4, 'ba1': 5, 'ba2': 6}[u]
    return table_d_3[0][i], table_d_3[1][i], table_d_3[2][i]


def get_f_hs(e_rtd):
    """バックアップボイラーの給湯部に対する効率の補正係数 f_hs (5)

    Args:
      e_rtd(float): 当該バックアップボイラーの給湯部の効率 (-)

    Returns:
      float: バックアップボイラーの給湯部に対する効率の補正係数 (-)

    """
    return (0.8754 * e_rtd + 0.060) / 0.745


# ============================================================================
# D.3 バックアップボイラーの保温時の補機による消費電力量
# ============================================================================

def get_E_E_BB_aux_ba2_d_t(L_BB_DHW_ba2_d_t):
    """1時間当たりのバックアップボイラーの保温時の補機による消費電力量 (kWh/h) (6)

    Args:
      L_BB_DHW_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりのバックアップボイラーの保温時の補機による消費電力量 (kWh/h)

    """
    E_E_BB_aux_ba2_d_t = np.zeros(24 * 365)

    L_BB_DHW_ba2_d = np.repeat(get_L_BB_DHW_ba2_d(L_BB_DHW_ba2_d_t), 24)

    # L_BB_DHW_ba2_d > 0 の場合
    f1 = L_BB_DHW_ba2_d > 0
    E_E_BB_aux_ba2_d_t[f1] = (0.01723 * L_BB_DHW_ba2_d[f1] + 0.06099) * 10 ** 3 / 3600 \
                             * (L_BB_DHW_ba2_d_t[f1] / L_BB_DHW_ba2_d[f1])

    # L_BB_DHW_ba2_d == 0 の場合
    f2 = L_BB_DHW_ba2_d == 0
    E_E_BB_aux_ba2_d_t[f2] = 0

    return E_E_BB_aux_ba2_d_t


# ============================================================================
# D.4 1日当たりの太陽熱補正給湯熱負荷
# ============================================================================

def get_L_BB_DHW_k_d(L_BB_DHW_k_d_t):
    """1日当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d) (7a)

    Args:
      L_BB_DHW_k_d_t(ndarray): 1時間当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)

    """
    return np.sum(L_BB_DHW_k_d_t.reshape(365, 24), axis=1)


def get_L_BB_DHW_s_d(L_BB_DHW_s_d_t):
    """1日当たりの浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d) (7b)

    Args:
      L_BB_DHW_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)

    """
    return np.sum(L_BB_DHW_s_d_t.reshape(365, 24), axis=1)


def get_L_BB_DHW_w_d(L_BB_DHW_w_d_t):
    """1日当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d) (7c)

    Args:
      L_BB_DHW_w_d_t(ndarray): 1時間当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)

    """
    return np.sum(L_BB_DHW_w_d_t.reshape(365, 24), axis=1)


def get_L_BB_DHW_b1_d(L_BB_DHW_b1_d_t):
    """1日当たりの浴槽水栓湯はり時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d) (7d)

    Args:
      L_BB_DHW_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽水栓湯はり時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)

    """
    return np.sum(L_BB_DHW_b1_d_t.reshape(365, 24), axis=1)


def get_L_BB_DHW_b2_d(L_BB_DHW_b2_d_t):
    """1日当たりの浴槽自動湯はり時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d) (7e)

    Args:
      L_BB_DHW_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽自動湯はり時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)

    """
    return np.sum(L_BB_DHW_b2_d_t.reshape(365, 24), axis=1)


def get_L_BB_DHW_ba1_d(L_BB_DHW_ba1_d_t):
    """1日当たりの浴槽水栓さし湯時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d) (7f)

    Args:
      L_BB_DHW_ba1_d_t: 1時間当たりの浴槽水栓さし湯時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽水栓さし湯時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)

    """
    return np.sum(L_BB_DHW_ba1_d_t.reshape(365, 24), axis=1)


def get_L_BB_DHW_ba2_d(L_BB_DHW_ba2_d_t):
    """1日当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d) (7g)

    Args:
      L_BB_DHW_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)

    """
    return np.sum(L_BB_DHW_ba2_d_t.reshape(365, 24), axis=1)
