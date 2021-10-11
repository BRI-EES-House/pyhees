# ============================================================================
# 付録 A 石油温水暖房機及び石油給湯温水暖房機
# ============================================================================


import numpy as np
import pyhees.section4_7_h as appendix_H


# ============================================================================
# A.2 エネルギー消費量
# ============================================================================


# ============================================================================
# A.2.1 灯油消費量
# ============================================================================


def calc_E_K_hs(Q_out_H_hs, e_rtd, hs_type, Theta_SW_hs, Theta_RW_hs, region, A_A, A_MR, A_OR, mode_MR, mode_OR,
                has_MR_hwh, has_OR_hwh):
    """温水暖房用熱源機の灯油消費量 (1)

    Args:
      Q_out_H_hs(ndarray): 熱源機暖房出力 (MJ/h)
      e_rtd(float): 当該給湯機の効率
      hs_type(str): 温水暖房用熱源機の種類
      Theta_SW_hs(ndarray): 温水暖房用熱源機の往き温水温度
      Theta_RW_hs(ndarray): 1時間平均の熱源機の戻り温水温度 (℃)
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      has_MR_hwh(bool): 温水暖房の放熱器を主たる居室に設置する場合はTrue
      has_OR_hwh(bool): 温水暖房の放熱器をその他の居室に設置する場合はTrue

    Returns:
      ndarray: 温水暖房用熱源機の灯油消費量

    """
    # 定格試験時の温水暖房用熱源機の筐体放熱損失 (4)
    Q_body_rtd = get_Q_body_rtd(hs_type)

    # 温水暖房熱源機の定格能力
    q_rtd_hs = calc_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

    # 1時間平均の温水暖房用熱源機の熱交換効率 (3)
    e_ex = calc_e_ex(e_rtd, hs_type, Theta_RW_hs, q_rtd_hs, Q_body_rtd)

    # 温水暖房用熱源機の筐体放熱損失 (2)
    Q_body = get_Q_body(hs_type, Theta_SW_hs)

    # 温水暖房用熱源機の灯油消費量 (1)
    E_K_hs = (Q_out_H_hs + Q_body) / e_ex
    E_K_hs[Q_out_H_hs == 0] = 0

    return E_K_hs


def get_Q_body(hs_type, Theta_SW_hs):
    """温水暖房用熱源機の筐体放熱損失 (2)

    Args:
      hs_type(str): 温水暖房用熱源機の種類
      Theta_SW_hs(ndarray): 温水暖房用熱源機の往き温水温度

    Returns:
      ndarray: 温水暖房用熱源機の筐体放熱損失

    """
    if hs_type in ['石油従来型暖房機', '石油従来型温水暖房機', '石油従来型給湯温水暖房機', '不明']:
        # (2a)
        return [234 * 3600 * 10 ** (-6)] * 24 * 365
    elif hs_type in ['石油潜熱回収型暖房機', '石油潜熱回収型温水暖房機', '石油潜熱回収型給湯温水暖房機']:
        # (2b)
        return (5.3928 * Theta_SW_hs - 71.903) * 3600 * 10 ** (-6)
    else:
        raise ValueError(hs_type)


def calc_e_ex(e_rtd, hs_type, Theta_RW_hs, q_rtd_hs, Q_body_rtd):
    """1時間平均の温水暖房用熱源機の熱交換効率 (3)

    Args:
      e_rtd(float): 当該給湯機の効率
      hs_type(str): 温水暖房用熱源機の種類
      Theta_RW_hs(ndarray): 1時間平均の熱源機の戻り温水温度 (℃)
      q_rtd_hs(float): 温水暖房用熱源機の定格能力 (W)
      Q_body_rtd(ndarray): 1時間当たりの定格試験時の温水暖房用熱源機の筐体放熱損失（MJ/h）

    Returns:
      ndarray: 1時間平均の温水暖房用熱源機の熱交換効率 (3)

    """
    # 1時間平均の定格効率を補正する係数
    f_rtd = get_f_rtd(hs_type, Theta_RW_hs)

    return e_rtd * f_rtd * (q_rtd_hs * 3600 * 10 ** (-6) + Q_body_rtd) / (q_rtd_hs * 3600 * 10 ** (-6))


def get_Q_body_rtd(hs_type):
    """定格試験時の温水暖房用熱源機の筐体放熱損失 (4)

    Args:
      hs_type(str): 温水暖房用熱源機の種類

    Returns:
      ndarray: 定格試験時の温水暖房用熱源機の筐体放熱損失 (4)

    """
    if hs_type in ['石油従来型暖房機', '石油従来型温水暖房機', '石油従来型給湯温水暖房機']:
        # (4a)
        return 234 * 3600 * 10 ** (-6) * np.ones(24*365)
    elif hs_type in ['石油潜熱回収型暖房機', '石油潜熱回収型温水暖房機', '石油潜熱回収型給湯温水暖房機']:

        # 温水暖房用熱源機の定格試験時の往き温水温度
        Theta_SW_hs_rtd = get_Theta_SW_hs_rtd()

        # (4b)
        return (5.3928 * Theta_SW_hs_rtd - 71.903) * 3600 * 10 ** (-6)
    else:
        raise ValueError(hs_type)


def get_f_rtd(hs_type, Theta_RW_hs):
    """1時間平均の定格効率を補正する係数 (5)

    Args:
      hs_type(str): 温水暖房用熱源機の種類
      Theta_RW_hs(ndarray): 1時間平均の熱源機の戻り温水温度 (℃)

    Returns:
      ndarray: 1時間平均の定格効率を補正する係数 (5)

    """
    f_rtd = np.zeros(24 * 365)

    if hs_type in ['石油従来型暖房機', '石油従来型温水暖房機', '石油従来型給湯温水暖房機']:
        # (5a)
        f_rtd[:] = 0.946
    elif hs_type in ['石油潜熱回収型暖房機', '石油潜熱回収型温水暖房機', '石油潜熱回収型給湯温水暖房機']:
        # (5b)

        Theta_RW_hs_rtd = get_Theta_RW_hs_rtd()

        # 条件1
        f1 = np.logical_and(Theta_RW_hs >= 46.5, Theta_RW_hs_rtd >= 46.5)
        f_rtd[f1] = 0.9768

        # 条件2
        f2 = np.logical_and(Theta_RW_hs < 46.5, Theta_RW_hs_rtd >= 46.5)
        f_rtd[f2] = (-0.0023 * Theta_RW_hs[f2] + 1.014) / 0.907 * 0.9768

        # 条件3
        f3 = np.logical_and(Theta_RW_hs >= 46.5, Theta_RW_hs_rtd < 46.5)
        f_rtd[f3] = 0.907 / (-0.0023 * Theta_RW_hs[f3] + 1.014) * 0.9768

        # 条件4
        f4 = np.logical_and(Theta_RW_hs < 46.5, Theta_RW_hs_rtd < 46.5)
        f_rtd[f4] = (-0.0023 * Theta_RW_hs[f4] + 1.014) / (-0.0023 * Theta_RW_hs_rtd + 1.014) * 0.9768

    else:
        raise ValueError(hs_type)

    return f_rtd


def get_e_rtd_default(hs_type):
    """定格効率(規定値)

    Args:
      hs_type(str): 温水暖房用熱源機の種類

    Returns:
      float: 定格効率(規定値)

    """
    if hs_type in ['石油従来型暖房機', '石油従来型温水暖房機', '石油従来型給湯温水暖房機']:
        return 0.82
    elif hs_type in ['石油潜熱回収型暖房機', '石油潜熱回収型温水暖房機', '石油潜熱回収型給湯温水暖房機']:
        return 0.91
    else:
        raise ValueError(hs_type)


def get_Theta_SW_hs_rtd():
    """温水暖房用熱源機の定格試験時の往き温水温度

    Args:

    Returns:
      float: 温水暖房用熱源機の定格試験時の往き温水温度

    """
    return 70


def get_Theta_RW_hs_rtd():
    """温水暖房熱源機の定格試験時の戻り温水温度

    Args:

    Returns:
      float: 温水暖房熱源機の定格試験時の戻り温水温度

    """
    return 50


def calc_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh):
    """温水暖房熱源機の定格能力

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
      float: 温水暖房熱源機の定格能力

    """
    # 付録Hに定める温水暖房用熱源機の最大能力 q_max_hs に等しい
    return appendix_H.calc_q_max_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)


# ============================================================================
# A.2.2 消費電力量
# ============================================================================


def calc_E_E_hs(hs_type, r_WS_hs, E_K_hs):
    """温水暖房用熱源機の消費電力量 (6)

    Args:
      hs_type(str): 温水暖房用熱源機の種類
      r_WS_hs(ndarray): 1時間平均の温水暖房用熱源機の温水供給運転率
      E_K_hs(ndarray): 1時間当たりの温水暖房用熱源機の灯油消費量（MJ/h）

    Returns:
      ndarray: 温水暖房用熱源機の消費電力量

    """
    # 温水暖房用熱源機の送水ポンプの消費電力量
    E_E_hs_pump = calc_E_E_hs_pmp(hs_type, r_WS_hs)

    # 温水暖房用の熱源機の排気ファンの消費電力量
    E_E_hs_fan = calc_E_E_hs_fan(E_K_hs)

    return E_E_hs_pump + E_E_hs_fan


def calc_E_E_hs_pmp(hs_type, r_WS_hs):
    """温水暖房用熱源機の送水ポンプの消費電力量 (7)

    Args:
      hs_type(str): 温水暖房用熱源機の種類
      r_WS_hs(ndarray): 1時間平均の温水暖房用熱源機の温水供給運転率

    Returns:
      ndarray: 温水暖房用熱源機の送水ポンプの消費電力量

    """
    # 温水暖房用熱源機の送水ポンプの消費電力
    P_hs_pmp = get_P_hs_pmp(hs_type)

    return P_hs_pmp * r_WS_hs * 10 ** (-3)


def get_P_hs_pmp(hs_type):
    """温水暖房用熱源機の送水ポンプの消費電力

    Args:
      hs_type(str): 温水暖房用熱源機の種類

    Returns:
      float: 温水暖房用熱源機の送水ポンプの消費電力

    """
    if hs_type in ['石油従来型暖房機', '石油従来型温水暖房機', '石油従来型給湯温水暖房機']:
        return 90
    elif hs_type in ['石油潜熱回収型暖房機', '石油潜熱回収型温水暖房機', '石油潜熱回収型給湯温水暖房機']:
        return 70
    else:
        raise ValueError(hs_type)


def calc_E_E_hs_fan(E_K_hs):
    """温水暖房用の熱源機の排気ファンの消費電力量 (8)

    Args:
      E_K_hs(ndarray): 1時間当たりの温水暖房用熱源機の灯油消費量（MJ/h）

    Returns:
      ndarray: 温水暖房用の熱源機の排気ファンの消費電力量 (8)

    """
    # 排気ファンの効率
    gamma = get_gamma()

    return E_K_hs * gamma * 10 ** 3 / 3600


def get_gamma():
    """排気ファンの効率

    Args:

    Returns:
      float: 排気ファンの効率

    """
    return 0.003


# ============================================================================
# A.2.3 ガス消費量
# ============================================================================


def get_E_G_hs():
    """ガス消費量

    Args:

    Returns:
      ndarray: ガス消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# A.2.4 その他の燃料による一次エネルギー消費量
# ============================================================================


def get_E_M_hs():
    """その他の燃料による一次エネルギー消費量

    Args:

    Returns:
      ndarray: その他の燃料による一次エネルギー消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# A.3 最大暖房出力
# ============================================================================


def get_Q_max_H_hs(q_rtd_hs):
    """最大暖房出力 (9)

    Args:
      q_rtd_hs(float): 温水暖房用熱源機の定格能力 (W)

    Returns:
      ndarray: 最大暖房出力

    """
    return np.ones(24*365) * q_rtd_hs * 3600 / (10 ** 6)
