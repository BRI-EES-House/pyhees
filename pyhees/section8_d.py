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
    """ 1時間当たりの給湯時のバックアップボイラーの燃料消費量 (MJ/h)

    :param bath_function: ふろ機能の種類
    :type bath_function: str
    :param L_BB_DHW_k_d_t: 1時間当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_k_d_t: ndarray
    :param L_BB_DHW_s_d_t: 1時間当たりの浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_s_d_t: ndarray
    :param L_BB_DHW_w_d_t: 1時間当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_w_d_t: ndarray
    :param L_BB_DHW_b1_d_t: 1時間当たりの浴槽水栓湯はりにおけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_b1_d_t: ndarray
    :param L_BB_DHW_b2_d_t: 1時間当たりの浴槽自動湯はりにおけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_b2_d_t: ndarray
    :param L_BB_DHW_ba1_d_t: 1時間当たりの浴槽水栓さし湯におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_ba1_d_t: ndarray
    :param L_BB_DHW_ba2_d_t: 1時間当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_ba2_d_t: ndarray
    :param e_rtd_DHW_BB: バックアップボイラー(給湯)の給湯機の効率
    :type e_rtd_DHW_BB: float
    :param Theta_ex_Ave: 外気温度 (℃)
    :type Theta_ex_Ave: ndarray
    :return: 1時間当たりの給湯時のバックアップボイラーの燃料消費量 (MJ/h)
    :rtype: ndarray
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
    """ 1時間当たりの給湯時のバックアップボイラーの燃料消費量 (MJ/h) (1)

    :param bath_function: ふろ機能の種類
    :type bath_function: str
    :param L_BB_DHW_k_d_t: 1時間当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_k_d_t: ndarray
    :param L_BB_DHW_s_d_t: 1時間当たりの浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_s_d_t: ndarray
    :param L_BB_DHW_w_d_t: 1時間当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_w_d_t: ndarray
    :param L_BB_DHW_b1_d_t: 1時間当たりの浴槽水栓湯はりにおけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_b1_d_t: ndarray
    :param L_BB_DHW_b2_d_t: 1時間当たりの浴槽自動湯はりにおけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_b2_d_t: ndarray
    :param L_BB_DHW_ba1_d_t: 1時間当たりの浴槽水栓さし湯におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_ba1_d_t: ndarray
    :param L_BB_DHW_ba2_d_t: 1時間当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_ba2_d_t: ndarray
    :param e_k_d: 台所水栓における日平均バックアップボイラー効率 (-)
    :type e_k_d: ndarray
    :param e_s_d: シャワー水栓における日平均バックアップボイラー効率 (-)
    :type e_s_d: ndarray
    :param e_w_d: 洗面水栓における日平均バックアップボイラー効率 (-)
    :type e_w_d: ndarray
    :param e_b1_d: 浴槽水栓湯はりにおける日平均バックアップボイラー効率 (-)
    :type e_b1_d: ndarray
    :param e_b2_d: 浴槽自動湯はりにおける日平均バックアップボイラー効率 (-)
    :type e_b2_d: ndarray
    :param e_ba1_d: 浴槽水栓さし湯における日平均バックアップボイラー効率 (-)
    :type e_ba1_d: ndarray
    :param e_ba2_d: 浴槽追焚における日平均バックアップボイラー効率 (-)
    :type e_ba2_d: ndarray
    :return: 1時間当たりの給湯時のバックアップボイラーの燃料消費量
    :rtype: ndarray
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

    :param L_BB_DHW_ba2_d_t: 1時間当たりの浴槽追焚時のバックアップボイラーのガス消費量 (MJ/h)
    :type L_BB_DHW_ba2_d_t: ndarray
    :param e_ba2_d: 浴槽追焚時におけるバックアップボイラーの給湯部の日平均効率 (-)
    :type e_ba2_d: ndarray
    :return: 1時間当たりの浴槽追焚時のバックアップボイラーのガス消費量 (MJ/d)
    :rtype: ndarray
    """
    E_G_BB_DHW_ba2_d_t = L_BB_DHW_ba2_d_t / np.repeat(e_ba2_d, 24)
    return E_G_BB_DHW_ba2_d_t


def calc_e_x_d(e_rtd_DHW_BB, Theta_ex_Ave,
               L_BB_DHW_k_d, L_BB_DHW_w_d, L_BB_DHW_s_d,
               L_BB_DHW_b1_d, L_BB_DHW_b2_d,
               L_BB_DHW_ba1_d, L_BB_DHW_ba2_d):
    """各用途における日平均バックアップボイラー効率 (-) (3)

    :param e_rtd_DHW_BB: バックアップボイラーの給湯機の効率
    :type e_rtd_DHW_BB: float
    :param Theta_ex_Ave: 日平均外気温度 (℃)
    :type Theta_ex_Ave: ndarray
    :param L_BB_DHW_k_d: 1日当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_k_d: ndarray
    :param L_BB_DHW_w_d: 1日当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_w_d: ndarray_
    :param L_BB_DHW_s_d: 1日当たりの浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_s_d: ndarray
    :param L_BB_DHW_b1_d: 1日当たりの浴槽水栓湯はりにおけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_b1_d: ndarray
    :param L_BB_DHW_b2_d: 1日当たりの浴槽自動湯はりにおけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_b2_d: ndarray
    :param L_BB_DHW_ba1_d: 1日当たりの浴槽水栓さし湯におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_ba1_d: ndarray
    :param L_BB_DHW_ba2_d: 1日当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_ba2_d: ndarray
    :return: 台所水栓・洗面水栓・浴室シャワー水栓・浴槽水栓湯はり・浴槽自動湯はり・浴槽水栓さし巣・浴槽追焚ににおける日平均バックアップボイラー効率 e_BB_k_d, e_BB_w_d, e_BB_s_d, e_BB_b1_d, e_BB_b2_d, e_BB_ba1_d, e_BB_ba2_d
    :rtype: tuple
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

    :param Theta_ex_Ave: 日平均外気温度 (℃)
    :type Theta_ex_Ave: ndarray
    :param L_BB_DHW_k: 1日当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷
    :type L_BB_DHW_k: ndarray
    :param L_BB_DHW_w: 1日当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷
    :type L_BB_DHW_w: ndarray
    :param f_hs: 当該給湯機に対する効率の補正係数
    :type f_hs: float
    :return: 台所水栓の給湯使用時における日平均給湯機効率
    :rtype: ndarray
    """
    # 日平均給湯機効率を計算するための回帰係数
    std_k = get_std_u('k')
    a_k, b_k, c_k = get_rcoeff(std_k, f_hs)

    e_k = np.clip(a_k * Theta_ex_Ave + b_k * (L_BB_DHW_k + L_BB_DHW_w) + c_k, 0, 1)

    return e_k


def get_e_s(Theta_ex_Ave, L_BB_DHW_s, f_hs):
    """浴室シャワー水栓の給湯使用時における日平均給湯機効率 (3b)

    :param Theta_ex_Ave: 日平均外気温度 (℃)
    :type: ndarray
    :param L_BB_DHW_s: 浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷
    :type L_BB_DHW_s: ndarray
    :param f_hs: 当該給湯機に対する効率の補正係数
    :type f_hs: float
    :return: 浴室シャワー水栓の給湯使用時における日平均給湯機効率
    :rtype: ndarray
    """
    # 日平均給湯機効率を計算するための回帰係数
    std_s = get_std_u('s')
    a_s, b_s, c_s = get_rcoeff(std_s, f_hs)

    e_s = np.clip(a_s * Theta_ex_Ave + b_s * L_BB_DHW_s + c_s, 0, 1)

    return e_s


def get_e_w(Theta_ex_Ave, L_BB_DHW_k, L_dashdash_w, f_hs):
    """洗面水栓の給湯使用時における日平均給湯機効率 (3c)

    :param Theta_ex_Ave: 日平均外気温度 (℃)
    :type Theta_ex_Ave: ndarray
    :param L_BB_DHW_k: 1日当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷
    :type L_BB_DHW_k: ndarray
    :param L_dashdash_w: 1日当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷
    :type L_dashdash_w: ndarray
    :param f_hs: 当該給湯機に対する効率の補正係数
    :type f_hs: float
    :return: 洗面水栓の給湯使用時における日平均給湯機効率
    :rtype: ndarray
    """
    # 日平均給湯機効率を計算するための回帰係数
    std_w = get_std_u('w')
    a_w, b_w, c_w = get_rcoeff(std_w, f_hs)

    e_w = np.clip(a_w * Theta_ex_Ave + b_w * (L_BB_DHW_k + L_dashdash_w) + c_w, 0, 1)

    return e_w


def get_e_b1(Theta_ex_Ave, L_BB_DHW_b1, f_hs):
    """浴槽水栓湯はり時における日平均給湯機効率 (3d)

    :param Theta_ex_Ave: 日平均外気温度 (℃)
    :type Theta_ex_Ave: ndarray
    :param L_BB_DHW_b1: 1日当たりの浴槽水栓湯はり時におけるバックアップボイラーが分担する給湯熱負荷
    :type L_BB_DHW_b1: ndarray
    :param f_hs: 当該給湯機に対する効率の補正係数
    :type f_hs: float
    :return: 浴槽水栓湯はり時における日平均給湯機効率
    :rtype: ndarray
    """
    # 日平均給湯機効率を計算するための回帰係数
    std_b1 = get_std_u('b1')
    a_b1, b_b1, c_b1 = get_rcoeff(std_b1, f_hs)

    e_b1 = np.clip(a_b1 * Theta_ex_Ave + b_b1 * L_BB_DHW_b1 + c_b1, 0, 1)

    return e_b1


def get_e_b2(Theta_ex_Ave, L_BB_DHW_b2, f_hs):
    """浴槽自動湯はり時における日平均給湯機効率 (3e)

    :param Theta_ex_Ave: 日平均外気温度 (℃)
    :type Theta_ex_Ave: ndarray
    :param L_BB_DHW_b2: 1日当たりの浴槽水栓湯はり時におけるバックアップボイラーが分担する給湯熱負荷
    :type L_BB_DHW_b2: ndarray
    :param f_hs: 当該給湯機に対する効率の補正係数
    :type f_hs: float
    :return: 浴槽自動湯はり時における日平均給湯機効率
    :rtype: ndarray
    """
    # 日平均給湯機効率を計算するための回帰係数
    std_b2 = get_std_u('b2')
    a_b2, b_b2, c_b2 = get_rcoeff(std_b2, f_hs)

    e_b2 = np.clip(a_b2 * Theta_ex_Ave + b_b2 * L_BB_DHW_b2 + c_b2, 0, 1)

    return e_b2


def get_e_ba1(Theta_ex_Ave, L_BB_DHW_ba1, f_hs):
    """浴槽水栓さし湯時における日平均給湯機効率 (3f)

    :param Theta_ex_Ave: 日平均外気温度 (℃)
    :type Theta_ex_Ave: ndarray
    :param L_BB_DHW_ba1: 1日当たりの浴槽水栓さし湯時におけるバックアップボイラーが分担する給湯熱負荷
    :type L_BB_DHW_ba1: ndarray
    :param f_hs: 当該給湯機に対する効率の補正係数
    :return: 浴槽水栓さし湯時における日平均給湯機効率
    """
    # 日平均給湯機効率を計算するための回帰係数
    std_ba1 = get_std_u('ba1')
    a_ba1, b_ba1, c_ba1 = get_rcoeff(std_ba1, f_hs)

    e_ba1 = np.clip(a_ba1 * Theta_ex_Ave + b_ba1 * L_BB_DHW_ba1 + c_ba1, 0, 1)

    return e_ba1


def calc_e_ba2(Theta_ex_Ave, L_BB_DHW_ba2, f_hs):
    """浴槽追追焚時における日平均給湯機効率 (3g)

    :param Theta_ex_Ave: 日平均外気温度 (℃)
    :type Theta_ex_Ave: ndarray
    :param L_BB_DHW_ba2: 1日当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :type L_BB_DHW_ba2: ndarray
    :param f_hs: 当該給湯機に対する効率の補正係数
    :type f_hs: float
    :return: 浴槽追追焚時における日平均給湯機効率
    :rtype: ndarray
    """
    # 日平均給湯機効率を計算するための回帰係数
    std_ba2 = get_std_u('ba2')
    a_ba2, b_ba2, c_ba2 = get_rcoeff(std_ba2, f_hs)

    e_ba2 = np.clip(a_ba2 * Theta_ex_Ave + b_ba2 * L_BB_DHW_ba2 + c_ba2, 0, 1)

    return e_ba2


def get_rcoeff(std_u, f_hs):
    """a_u, b_u, c_uの取得 (4a)(4b)(4c)

    :param std_u: 表D.3により求まる係数 (-)
    :type std_u:
    :param f_hs: バックアップボイラーの給湯部に対する効率の補正係数 (-)
    :return: 日平均給湯機効率を計算するための回帰係数 a_u, b_u, c_u
    """
    a_u = std_u[0] * f_hs
    b_u = std_u[1] * f_hs
    c_u = std_u[2] * f_hs
    return a_u, b_u, c_u


def get_std_u(u):
    """バックアップボイラーの給湯部の効率の回帰係数a_std_u, b_std_u, c_std_u

    :param u: 用途を表す添え字(k,s,w,b1,b2,ba1,ba2)
    :type u: str
    :return: バックアップボイラーの給湯部の効率の回帰係数a_std_u, b_std_u, c_std_u
    :rtype: tuple
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

    :param e_rtd: 当該バックアップボイラーの給湯部の効率 (-)
    :type e_rtd: float
    :return: バックアップボイラーの給湯部に対する効率の補正係数 (-)
    :rtype: float
    """
    return (0.8754 * e_rtd + 0.060) / 0.745


# ============================================================================
# D.3 バックアップボイラーの保温時の補機による消費電力量
# ============================================================================

def get_E_E_BB_aux_ba2_d_t(L_BB_DHW_ba2_d_t):
    """1時間当たりのバックアップボイラーの保温時の補機による消費電力量 (kWh/h) (6)

    :param L_BB_DHW_ba2_d_t: 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_BB_DHW_ba2_d_t: ndarray
    :return: 1時間当たりのバックアップボイラーの保温時の補機による消費電力量 (kWh/h)
    :rtype: ndarray
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

    :param L_BB_DHW_k_d_t: 1時間当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)
    :type L_BB_DHW_k_d_t: ndarray
    :return: 1日当たりの台所水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :rtype: ndarray
    """
    return np.sum(L_BB_DHW_k_d_t.reshape(365, 24), axis=1)


def get_L_BB_DHW_s_d(L_BB_DHW_s_d_t):
    """1日当たりの浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d) (7b)

    :param L_BB_DHW_s_d_t: 1時間当たりの浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)
    :type L_BB_DHW_s_d_t: ndarray
    :return: 1日当たりの浴室シャワー水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :rtype: ndarray
    """
    return np.sum(L_BB_DHW_s_d_t.reshape(365, 24), axis=1)


def get_L_BB_DHW_w_d(L_BB_DHW_w_d_t):
    """1日当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d) (7c)

    :param L_BB_DHW_w_d_t: 1時間当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)
    :type L_BB_DHW_w_d_t: ndarray
    :return: 1日当たりの洗面水栓におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :rtype: ndarray
    """
    return np.sum(L_BB_DHW_w_d_t.reshape(365, 24), axis=1)


def get_L_BB_DHW_b1_d(L_BB_DHW_b1_d_t):
    """1日当たりの浴槽水栓湯はり時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d) (7d)

    :param L_BB_DHW_b1_d_t: 1時間当たりの浴槽水栓湯はり時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)
    :type L_BB_DHW_b1_d_t: ndarray
    :return: 1日当たりの浴槽水栓湯はり時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :rtype: ndarray
    """
    return np.sum(L_BB_DHW_b1_d_t.reshape(365, 24), axis=1)


def get_L_BB_DHW_b2_d(L_BB_DHW_b2_d_t):
    """1日当たりの浴槽自動湯はり時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d) (7e)

    :param L_BB_DHW_b2_d_t: 1時間当たりの浴槽自動湯はり時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)
    :type L_BB_DHW_b2_d_t: ndarray
    :return: 1日当たりの浴槽自動湯はり時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :rtype: ndarray
    """
    return np.sum(L_BB_DHW_b2_d_t.reshape(365, 24), axis=1)


def get_L_BB_DHW_ba1_d(L_BB_DHW_ba1_d_t):
    """1日当たりの浴槽水栓さし湯時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d) (7f)

    :param L_BB_DHW_ba1_d_t: 1時間当たりの浴槽水栓さし湯時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)
    :type: ndarray
    :return: 1日当たりの浴槽水栓さし湯時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :rtype: ndarray
    """
    return np.sum(L_BB_DHW_ba1_d_t.reshape(365, 24), axis=1)


def get_L_BB_DHW_ba2_d(L_BB_DHW_ba2_d_t):
    """1日当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d) (7g)

    :param L_BB_DHW_ba2_d_t: 1時間当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)
    :type L_BB_DHW_ba2_d_t: ndarray
    :return: 1日当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/d)
    :rtype: ndarray
    """
    return np.sum(L_BB_DHW_ba2_d_t.reshape(365, 24), axis=1)
