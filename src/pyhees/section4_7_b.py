# ============================================================================
# 付録 B ガス温水暖房機及びガス給湯温水暖房機
# ============================================================================

import numpy as np
import pyhees.section4_7_h as appendix_H


# ============================================================================
# B.2 エネルギー消費量
# ============================================================================

# ============================================================================
# B.2.1 ガス消費量
# ============================================================================

def calc_E_G_hs(e_rtd, q_rtd_hs, Q_out_H_hs, hs_type, Theta_SW_hs):
    """1時間当たりの温水床暖房用熱源機のガス消費量 (1)

    Args:
      e_rtd(float): 当該給湯機の効率
      q_rtd_hs(float): 温水暖房用熱源機の定格能力 (W)
      Q_out_H_hs(ndarray): 1時間当たりの温水暖房用熱源機の暖房出力 (MJ/h)
      hs_type(str): 温水暖房用熱源機の種類
      Theta_SW_hs(ndarray): 温水暖房用熱源機の往き温水温度 (℃)

    Returns:
      ndarray: 1時間当たりの温水床暖房用熱源機のガス消費量

    """
    # 1時間当たりの温水暖房用熱源機の筐体放熱損失 (MJ/h) (2)
    Q_body = get_Q_body(hs_type, Theta_SW_hs)

    # 熱交換効率
    e_ex = calc_e_ex(e_rtd, Q_body, hs_type, Theta_SW_hs, q_rtd_hs)

    # 1時間当たりの温水床暖房用熱源機のガス消費量 (1)
    E_G_hs = (Q_out_H_hs + Q_body) / e_ex
    E_G_hs[Q_out_H_hs == 0] = 0

    return E_G_hs


def get_Q_body(hs_type, Theta_SW_hs):
    """1時間当たりの温水暖房用熱源機の筐体放熱損失 (2)

    Args:
      hs_type(str): 温水暖房用熱源機の種類
      Theta_SW_hs(ndarray): 温水暖房用熱源機の往き温水温度 (℃)

    Returns:
      ndarray: 1時間当たりの温水暖房用熱源機の筐体放熱損失

    """
    if hs_type in ['ガス従来型温水暖房機', 'ガス従来型給湯温水暖房機', 'ガス従来型'] or hs_type == '不明':
        # (2a)
        Q_body = np.ones(24*365) * 240.96 * 3600 * 10 ** (-6)
        return Q_body
    elif hs_type in ['ガス潜熱回収型温水暖房機', 'ガス潜熱回収型給湯温水暖房機', 'ガス潜熱回収型']:
        Q_body = np.zeros(24*365)

        # (2b)
        Q_body[Theta_SW_hs == 60] = 225.26 * 3600 * 10 ** (-6)
        Q_body[Theta_SW_hs == 40] = 123.74 * 3600 * 10 ** (-6)

        return Q_body
    else:
        raise ValueError(hs_type)


def calc_e_ex(e_rtd, Q_body, hs_type, Theta_SW_hs, q_rtd_hs):
    """1時間平均の温水暖房用熱源機の熱交換効率 (3)

    Args:
      e_rtd(float): 当該給湯機の効率
      Q_body(ndarray): 1時間当たりの温水暖房用熱源機の筐体放熱損失
      hs_type(str): 温水暖房用熱源機の種類
      Theta_SW_hs(ndarray): 温水暖房用熱源機の往き温水温度 (℃)
      q_rtd_hs(float): 温水暖房用熱源機の定格能力 (W)

    Returns:
      ndarray: 1時間平均の温水暖房用熱源機の熱交換効率

    """
    # 定格効率を補正する係数
    f_rtd = get_f_rtd(hs_type, Theta_SW_hs)

    return e_rtd * f_rtd * (q_rtd_hs * 3600 * 10 ** (-6) + Q_body) / (q_rtd_hs * 3600 * 10 ** (-6))


def get_f_rtd(hs_type, Theta_SW_hs):
    """定格効率を補正する係数

    Args:
      hs_type(str): 温水暖房用熱源機の種類
      Theta_SW_hs(ndarray): 温水暖房用熱源機の往き温水温度 (℃)

    Returns:
      ndarray: 定格効率を補正する係数

    """
    if hs_type in ['ガス従来型温水暖房機', 'ガス従来型給湯温水暖房機', 'ガス従来型']:
        return np.ones(24*365) * 0.985
    elif hs_type in ['ガス潜熱回収型温水暖房機', 'ガス潜熱回収型給湯温水暖房機', 'ガス潜熱回収型']:
        f_rtd = np.zeros(24*365)
        f_rtd[Theta_SW_hs == 60] = 1.038
        f_rtd[Theta_SW_hs == 40] = 1.064
        return f_rtd
    else:
        raise ValueError(hs_type)


def get_e_rtd_default(hs_type):
    """定格効率(規定値)

    Args:
      hs_type(str): 温水暖房用熱源機の種類

    Returns:
      float: 定格効率(規定値)

    """
    if hs_type in ['ガス従来型温水暖房機', 'ガス従来型給湯温水暖房機']:
        return 0.81
    elif hs_type in ['ガス潜熱回収型温水暖房機', 'ガス潜熱回収型給湯温水暖房機']:
        return 0.87
    else:
        raise ValueError(hs_type)


def calc_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh):
    """温水暖房用熱源機の定格能力

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      has_MR_hwh(bool): 温水暖房の放熱器を主たる居室に設置する場合はTrue
      has_OR_hwh(bool): 温水暖房の放熱器をその他の居室に設置する場合はTrue

    Returns:
      float: 温水暖房用熱源機の定格能力

    """
    # 付録Hに定める温水暖房用熱源機の最大能力 q_max_hs に等しい
    return appendix_H.calc_q_max_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)


# ============================================================================
# B.2.2 消費電力量
# ============================================================================

def calc_E_E_hs(r_WS_hs, E_G_hs):
    """消費電力量 (5)

    Args:
      r_WS_hs(ndarray): 1時間平均の温水暖房用熱源機の温水供給運転率
      E_G_hs(ndarray): 1時間当たりの温水暖房用熱源機のガス消費量（MJ/h）

    Returns:
      ndarray: 消費電力量 (5)

    """
    # 送水ポンプの消費電力量
    E_E_hs_pmp = calc_E_E_hs_pmp(r_WS_hs)

    # 排気ファンの消費電力量
    E_E_hs_fan = get_E_E_hs_fan(E_G_hs)

    return E_E_hs_pmp + E_E_hs_fan


def calc_E_E_hs_pmp(r_WS_hs):
    """送水ポンプの消費電力量 (6)

    Args:
      r_WS_hs(ndarray): 1時間平均の温水暖房用熱源機の温水供給運転率

    Returns:
      ndarray: 送水ポンプの消費電力量 (6)

    """
    # 送水ポンプの消費電力
    P_hs_pmp = get_P_hs_pmp()

    return P_hs_pmp * r_WS_hs * 10 ** (-3)


def get_P_hs_pmp():
    """送水ポンプの消費電力

    Args:

    Returns:
      float: 送水ポンプの消費電力

    """
    return 73


def get_E_E_hs_fan(E_G_hs):
    """排気ファンの消費電力量 (7)

    Args:
      E_G_hs(ndarray): 1時間当たりの温水暖房用熱源機のガス消費量（MJ/h）

    Returns:
      ndarray: 排気ファンの消費電力量

    """
    # 排気ファンの効率
    gamma = get_gamma()

    return E_G_hs * gamma * 10 ** 3 / 3600


def get_gamma():
    """排気ファンの効率

    Args:

    Returns:
      float: 排気ファンの効率

    """
    return 0.003


# ============================================================================
# B.2.3 灯油消費量
# ============================================================================

def get_E_K_hs():
    """1時間当たりの温水暖房用熱源機の灯油消費量

    Args:

    Returns:
      ndarray: 1時間当たりの温水暖房用熱源機の灯油消費量

    """
    # 1時間当たりの温水暖房用熱源機の灯油消費量は0とする
    return np.zeros(24 * 365)


# ============================================================================
# B.2.4 その他の一次エネルギー消費量
# ============================================================================

def get_E_M_hs():
    """1時間当たりの温水暖房用熱源機のその他の一次エネルギー消費量

    Args:

    Returns:
      ndarray: 1時間当たりの温水暖房用熱源機のその他の一次エネルギー消費量

    """
    # 1時間当たりの温水暖房用熱源機のその他の一次エネルギー消費量は0とする
    return np.zeros(24 * 365)


# ============================================================================
# B.3 最大暖房出力
# ============================================================================

def get_Q_max_H_hs(q_rtd_hs):
    """1時間当たりの温水暖房用熱源機の最大暖房出力 (8)

    Args:
      q_rtd_hs(float): 温水暖房用熱源機の定格能力 (W)

    Returns:
      ndarray: 1時間当たりの温水暖房用熱源機の最大暖房出力 (MJ/h)

    """
    return np.ones(24*365) * q_rtd_hs * 3600 / (10 ** 6)
