# ============================================================================
# 付録E バックアップボイラーの温水暖房部(ガス熱源)
# ============================================================================

import numpy as np


# ============================================================================
# E.2 ガス消費量
# ============================================================================

def calc_E_G_BB_HWH_d_t(BB_type, e_rtd, q_rtd, L_BB_HWH_d_t, Theta_SW_BB_HWH):
    """1時間当たりの温水暖房時のバックアップボイラーのガス消費量 (MJ/h)

    Args:
      BB_type(str): 当該バックアップボイラーの温水暖房部の種類
      e_rtd(float): バックアップボイラーの温水暖房部の定格効率 (-)
      q_rtd(int): バックアップボイラーの温水暖房の定格能力 (W)
      L_BB_HWH_d_t(ndarray): 1時間当たりのバックアップボイラーが分担する温水暖房熱負荷 (MJ/h)
      Theta_SW_BB_WHW(ndarray): バックアップボイラーの温水暖房部の往き温水温度 (℃)

    Returns:
      ndarray: 1時間当たりの温水暖房時のバックアップボイラーのガス消費量 (MJ/h)

    """
    # 1時間当たりの温水暖房時のバックアップボイラーの最大暖房出力 (MJ/h) (9)
    Q_max_BB_HWH = get_Q_max_BB_HWH(q_rtd)

    # 1時間当たりのバックアップボイラーの温水暖房部の温水暖房出力 (MJ/h) (8)
    Q_out_BB_HWH_d_t = get_Q_out_BB_HWH_d_t(L_BB_HWH_d_t, Q_max_BB_HWH)

    # 1時間平均の定格効率を補正する係数 (-) (4)
    f_rtd_d_t = get_f_rtd_d_t(BB_type, Theta_SW_BB_HWH)

    # 1時間当たりのバックアップボイラーの温水暖房部の筐体熱損失 (MJ/h) (3)
    Q_body_d_t = get_Q_body_d_t(BB_type, Theta_SW_BB_HWH)

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

    Args:
      Q_out_BB_HWH_d_t(ndarray): 1時間当たりのバックアップボイラーの温水暖房部の温水暖房出力 (MJ/h)
      Q_body_d_t(ndarray): 1時間当たりのバックアップボイラーの温水暖房部の共闘放熱損失 (MJ/h)
      e_ex_d_t(ndarray): 1時間平均のバックアップボイラーの温水暖房部の熱交換効率 (-)

    Returns:
      ndarray: 1時間当たりの温水暖房時のバックアップボイラーのガス消費量 (MJ/h)

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

    Args:
      e_rtd(float): バックアップボイラーの温水暖房部の定格効率 (-)
      f_rtd_d_t(ndarray): 1時間平均の定格効率を補正する係数 (-)
      q_rtd(int): バックアップボイラーの温水暖房部の定格能力 (W)
      Q_body_d_t(ndarray): 1時間当たりのバックアップボイラーの温水暖房部の筐体放熱損失 (MJ/h)

    Returns:
      ndarray: 1時間平均のバックアップボイラーの温水暖房部の熱交換効率 (-)

    """
    e_ex_d_t = e_rtd * f_rtd_d_t * (q_rtd * 3600 * 10 ** (-6) + Q_body_d_t) / (q_rtd * 3600 * 10 ** (-6))
    return e_ex_d_t


def get_Q_body_d_t(BB_type, Theta_SW_BB_WHW):
    """1時間当たりのバックアップボイラーの温水暖房部の筐体熱損失 (MJ/h) (3)

    Args:
      BB_type(str): 当該バックアップボイラーの温水暖房部の種類
      Theta_SW_BB_WHW(ndarray): バックアップボイラーの温水暖房部の往き温水温度 (℃)

    Returns:
      ndarray: 1時間当たりのバックアップボイラーの温水暖房部の筐体熱損失 (MJ/h)

    """
    Q_body_d_t = np.zeros(24 * 365)

    if BB_type in ['ガス従来型', 'G_NEJ']:
        Q_body_d_t[:] = 240.96 * 3600 * 10 ** (-6)
    elif BB_type in ['ガス潜熱回収型', 'G_EJ']:
        f1 = (Theta_SW_BB_WHW == 60)
        Q_body_d_t[f1] = 225.26 * 3600 * 10 ** (-6)

        f2 = (Theta_SW_BB_WHW == 40)
        Q_body_d_t[f2] = 123.74 * 3600 * 10 ** (-6)
    else:
        raise ValueError(BB_type)

    return Q_body_d_t


def get_f_rtd_d_t(BB_type, Theta_SW_BB_WHW):
    """1時間平均の定格効率を補正する係数 (-) (4)

    Args:
      BB_type(str): 当該バックアップボイラーの温水暖房部の種類
      Theta_SW_BB_WHW(ndarray): バックアップボイラーの温水暖房部の往き温水温度 (℃)

    Returns:
      ndarray: 1時間平均の定格効率を補正する係数 (-)

    """
    f_rtd_d_t = np.zeros(24 * 365)
    if BB_type in ['ガス従来型', 'G_NEJ']:
        f_rtd_d_t[:] = 0.985
    elif BB_type in ['ガス潜熱回収型', 'G_EJ']:
        f1 = (Theta_SW_BB_WHW == 60)
        f_rtd_d_t[f1] = 1.038

        f2 = (Theta_SW_BB_WHW == 40)
        f_rtd_d_t[f2] = 1.064
    else:
        raise ValueError(BB_type)

    return f_rtd_d_t


# ============================================================================
# E.3 温水暖房出力
# ============================================================================

def get_Q_out_BB_HWH_d_t(L_BB_HWH_d_t, Q_max_BB_HWH):
    """1時間当たりのバックアップボイラーの温水暖房部の温水暖房出力 (MJ/h) (5)

    Args:
      L_BB_HWH_d_t(ndarray): 1時間当たりのバックアップボイラーが分担する温水暖房熱負荷 (MJ/h)
      Q_max_BB_HWH(float): 1時間当たりの温水暖房時のバックアップボイラーの最大暖房出力 (MJ/h)

    Returns:
      ndarray: 1時間当たりのバックアップボイラーの温水暖房部の温水暖房出力 (MJ/h)

    """
    Q_out_BB_HWH_d_t = np.clip(L_BB_HWH_d_t, None, Q_max_BB_HWH)
    return Q_out_BB_HWH_d_t


def get_Q_max_BB_HWH(q_rtd_BB_HWH):
    """1時間当たりの温水暖房時のバックアップボイラーの最大暖房出力 (MJ/h) (6)

    Args:
      q_rtd_BB_HWH(float): バックアップボイラーの温水暖房の定格能力 (W)

    Returns:
      float: 1時間当たりの温水暖房時のバックアップボイラーの最大暖房出力 (MJ/h)

    """
    Q_max_BB_HWH = q_rtd_BB_HWH * 3600 / (10 ** 6)

    return Q_max_BB_HWH
