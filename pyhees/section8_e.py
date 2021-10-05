# ============================================================================
# 付録E バックアップボイラーの温水暖房部(ガス熱源)
# ============================================================================

import numpy as np


# ============================================================================
# E.2 ガス消費量
# ============================================================================

def calc_E_G_BB_HWH_d_t(BB_type, e_rtd, q_rtd, L_BB_HWH_d_t, p_hs):
    """1時間当たりの温水暖房時のバックアップボイラーのガス消費量 (MJ/h)

    :param BB_type: 当該バックアップボイラーの温水暖房部の種類
    :type BB_type: str
    :param e_rtd: バックアップボイラーの温水暖房部の定格効率 (-)
    :type e_rtd: float
    :param q_rtd: バックアップボイラーの温水暖房の定格能力 (W)
    :type q_rtd: int
    :param L_BB_HWH_d_t: 1時間当たりのバックアップボイラーが分担する温水暖房熱負荷 (MJ/h)
    :type L_BB_HWH_d_t: ndarray
    :param p_hs: 温水暖房用熱源機の往き温水温度の区分
    :type p_hs: ndarray
    :return: 1時間当たりの温水暖房時のバックアップボイラーのガス消費量 (MJ/h)
    :rtype: ndarray
    """
    # 1時間当たりの温水暖房時のバックアップボイラーの最大暖房出力 (MJ/h) (9)
    Q_max_BB_HWH = get_Q_max_BB_HWH(q_rtd)

    # 1時間当たりのバックアップボイラーの温水暖房部の温水暖房出力 (MJ/h) (8)
    Q_out_BB_HWH_d_t = get_Q_out_BB_HWH_d_t(L_BB_HWH_d_t, Q_max_BB_HWH)

    # 1時間平均の定格効率を補正する係数 (-) (4)
    f_rtd_d_t = get_f_rtd_d_t(BB_type, p_hs)

    # 1時間当たりのバックアップボイラーの温水暖房部の筐体熱損失 (MJ/h) (3)
    Q_body_d_t = get_Q_body_d_t(BB_type, p_hs)

    # 1時間平均のバックアップボイラーの温水暖房部の熱交換効率 (-) (2)
    e_ex_d_t = get_e_ex_d_t(e_rtd, f_rtd_d_t, q_rtd, Q_body_d_t)

    # 1時間当たりの温水暖房時のバックアップボイラーのガス消費量 (MJ/h) (1)
    E_G_BB_HWH_d_t = get_E_G_BB_HWH_d_t(Q_out_BB_HWH_d_t, Q_body_d_t, e_ex_d_t)

    print('Q_body = {} [MJ/yr]'.format(np.sum(Q_body_d_t)))
    print('sum(e_ex_d_t) = {} [-]'.format(np.sum(e_ex_d_t)))
    print('L_BB_HWH = {} [MJ/yr]'.format(np.sum(L_BB_HWH_d_t)))
    print('Q_out_BB_HWH = {} [MJ/yr]'.format(np.sum(Q_out_BB_HWH_d_t)))
    print('E_G_BB_HWH = {} [MJ/yr]'.format(np.sum(E_G_BB_HWH_d_t)))

    return E_G_BB_HWH_d_t


def get_E_G_BB_HWH_d_t(Q_out_BB_HWH_d_t, Q_body_d_t, e_ex_d_t):
    """1時間当たりの温水暖房時のバックアップボイラーのガス消費量 (MJ/h) (1)

    :param Q_out_BB_HWH_d_t: 1時間当たりのバックアップボイラーの温水暖房部の温水暖房出力 (MJ/h)
    :type Q_out_BB_HWH_d_t: ndarray
    :param Q_body_d_t: 1時間当たりのバックアップボイラーの温水暖房部の共闘放熱損失 (MJ/h)
    :type Q_body_d_t: ndarray
    :param e_ex_d_t: 1時間平均のバックアップボイラーの温水暖房部の熱交換効率 (-)
    :type e_ex_d_t: ndarray
    :return: 1時間当たりの温水暖房時のバックアップボイラーのガス消費量 (MJ/h)
    :rtype: ndarray
    """
    E_G_BB_HWH_d_t = np.zeros(24 * 365)

    # Q_out_BB_HWH_d_t = 0 の場合
    f1 = Q_out_BB_HWH_d_t == 0
    E_G_BB_HWH_d_t[f1] = 0

    # Q_out_BB_HWH_d_t > 0 の場合
    f2 = Q_out_BB_HWH_d_t > 0
    E_G_BB_HWH_d_t[f2] = (Q_out_BB_HWH_d_t[f2] + Q_body_d_t[f2]) / e_ex_d_t[f2]

    return E_G_BB_HWH_d_t


def get_e_ex_d_t(e_rtd, f_rtd_d_t, q_rtd, Q_body_d_t):
    """1時間平均のバックアップボイラーの温水暖房部の熱交換効率 (-) (2)

    :param e_rtd: バックアップボイラーの温水暖房部の定格効率 (-)
    :type e_rtd: float
    :param f_rtd_d_t: 1時間平均の定格効率を補正する係数 (-)
    :type f_rtd_d_t: ndarray
    :param q_rtd: バックアップボイラーの温水暖房部の定格能力 (W)
    :type q_rtd: int
    :param Q_body_d_t: 1時間当たりのバックアップボイラーの温水暖房部の筐体放熱損失 (MJ/h)
    :type Q_body_d_t: ndarray
    :return: 1時間平均のバックアップボイラーの温水暖房部の熱交換効率 (-)
    :rtype: ndarray
    """
    e_ex_d_t = e_rtd * f_rtd_d_t * (q_rtd * 3600 * 10 ** (-6) + Q_body_d_t) / (q_rtd * 3600 * 10 ** (-6))
    return e_ex_d_t


def get_Q_body_d_t(BB_type, p_hs=None):
    """1時間当たりのバックアップボイラーの温水暖房部の筐体熱損失 (MJ/h) (3)

    :param BB_type: 当該バックアップボイラーの温水暖房部の種類
    :type BB_type: str
    :param p_hs: 送水温度の区分
    :type p_hs: ndarray
    :return: 1時間当たりのバックアップボイラーの温水暖房部の筐体熱損失 (MJ/h)
    :rtype: ndarray
    """
    Q_body_d_t = np.zeros(24 * 365)

    if BB_type in ['ガス従来型', 'G_NEJ']:
        Q_body_d_t[:] = 240.96 * 3600 * 10 ** (-6)
    elif BB_type in ['ガス潜熱回収型', 'G_EJ']:
        # 送水温度の区分p_hsが1(送水温度60℃)の場合
        f1 = (p_hs == 1)
        Q_body_d_t[f1] = 225.26 * 3600 * 10 ** (-6)

        # 送水温度の区分p_hsが2(送水温度40℃)の場合
        f2 = (p_hs == 2)
        Q_body_d_t[f2] = 123.74 * 3600 * 10 ** (-6)
    else:
        raise ValueError(BB_type)

    return Q_body_d_t


def get_f_rtd_d_t(BB_type, p_hs):
    """1時間平均の定格効率を補正する係数 (-) (4)

    :param BB_type: 当該バックアップボイラーの温水暖房部の種類
    :type BB_type: str
    :param p_hs: 送水温度の区分
    :type p_hs: ndarray
    :return: 1時間平均の定格効率を補正する係数 (-)
    :rtype: ndarray
    """
    f_rtd_d_t = np.zeros(24 * 365)
    if BB_type in ['ガス従来型', 'G_NEJ']:
        f_rtd_d_t[:] = 0.985
    elif BB_type in ['ガス潜熱回収型', 'G_EJ']:
        # 送水温度の区分p_hsが1(送水温度60℃)の場合
        f1 = (p_hs == 1)
        f_rtd_d_t[f1] = 1.038

        # 送水温度の区分p_hsが2(送水温度40℃)の場合
        f2 = (p_hs == 2)
        f_rtd_d_t[f2] = 1.064
    else:
        raise ValueError(BB_type)

    return f_rtd_d_t


# ============================================================================
# E.3 温水暖房出力
# ============================================================================

def get_Q_out_BB_HWH_d_t(L_BB_HWH_d_t, Q_max_BB_HWH):
    """1時間当たりのバックアップボイラーの温水暖房部の温水暖房出力 (MJ/h) (5)

    :param L_BB_HWH_d_t: 1時間当たりのバックアップボイラーが分担する温水暖房熱負荷 (MJ/h)
    :type L_BB_HWH_d_t: ndarray
    :param Q_max_BB_HWH: 1時間当たりの温水暖房時のバックアップボイラーの最大暖房出力 (MJ/h)
    :type Q_max_BB_HWH: float
    :return: 1時間当たりのバックアップボイラーの温水暖房部の温水暖房出力 (MJ/h)
    :rtype: ndarray
    """
    Q_out_BB_HWH_d_t = np.clip(L_BB_HWH_d_t, None, Q_max_BB_HWH)
    return Q_out_BB_HWH_d_t


def get_Q_max_BB_HWH(q_rtd_BB_HWH):
    """1時間当たりの温水暖房時のバックアップボイラーの最大暖房出力 (MJ/h) (6)

    :param q_rtd_BB_HWH: バックアップボイラーの温水暖房の定格能力 (W)
    :type q_rtd_BB_HWH: float
    :return: 1時間当たりの温水暖房時のバックアップボイラーの最大暖房出力 (MJ/h)
    :rtype: float
    """
    Q_max_BB_HWH = q_rtd_BB_HWH * 3600 / (10 ** 6)

    return Q_max_BB_HWH
