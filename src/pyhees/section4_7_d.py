# ============================================================================
# 付録 D 電気ヒートポンプ温水暖房機（フロン系）
# ============================================================================

import pyhees.section4_7_h as appendix_H

import numpy as np


# ============================================================================
# D.2 エネルギー消費量
# ============================================================================

# ============================================================================
# D.2.1 消費電力量
# ============================================================================

def calc_E_E_hs(Q_out_H_hs, Q_max_H_hs, Q_dmd_H_hs_d_t, Theta_SW_hs, Theta_ex, q_rtd_hs):
    """1時間当たりの消費電力量 (1)

    Args:
      Q_out_H_hs(ndarray): 1時間当たりの温水暖房用熱源機の暖房出力 (MJ/h)
      Q_max_H_hs(ndarray): 熱源機の最大暖房出力 (MJ/h)
      Q_dmd_H_hs_d_t(ndarray): 1時間当たりの熱源機の熱需要 (MJ/h)
      Theta_SW_hs(ndarray): 温水暖房用熱源機の往き温水温度
      Theta_ex(ndarray): 外気温度
      q_rtd_hs(float): 温水暖房用熱源機の定格能力 (W)

    Returns:
      ndarray: 1時間当たりの消費電力量

    """
    # 定格効率
    e_rtd = get_e_rtd()

    # 定格消費電力
    P_rtd_hs = get_P_rtd_hs(q_rtd_hs, e_rtd)

    # 1 時間平均の温水暖房用熱源機の効率
    e_hs = calc_e_hs(Q_max_H_hs, Theta_SW_hs, Theta_ex, Q_out_H_hs, P_rtd_hs)

    # 消費電力量
    E_E_hs = Q_out_H_hs / e_hs * 10 ** 3 / 3600
    E_E_hs[Q_dmd_H_hs_d_t == 0] = 0

    return E_E_hs


def calc_e_hs(Q_max_H_hs, Theta_SW_hs, Theta_ex, Q_out_H_hs, P_rtd_hs):
    """1時間平均の温水暖房用熱源機の効率 (2)

    Args:
      Q_max_H_hs(ndarray): 熱源機の最大暖房出力 (MJ/h)
      Theta_SW_hs(ndarray): 温水暖房用熱源機の往き温水温度
      Theta_ex(ndarray): 外気温度
      Q_out_H_hs(ndarray): 1時間当たりの温水暖房用熱源機の暖房出力 (MJ/h)
      P_rtd_hs(float): 温水暖房用熱源機の定格消費電力 (W)

    Returns:
      ndarray: 1時間平均の温水暖房用熱源機の効率

    """

    # 1時間平均の効率比
    e_r_hs = get_e_r_hs(Theta_SW_hs, Theta_ex, Q_out_H_hs, Q_max_H_hs)

    # 最大消費電力
    P_max_hs = get_P_max_hs(P_rtd_hs)

    return (Q_max_H_hs * 10 ** 6 / 3600) / P_max_hs * e_r_hs


def get_P_max_hs(P_rtd_hs):
    """最大消費電力 (3)

    Args:
      P_rtd_hs(float): 温水暖房用熱源機の定格消費電力 (W)

    Returns:
      float: 最大消費電力

    """
    return P_rtd_hs / 0.6


def get_P_rtd_hs(q_rtd_hs, e_rtd):
    """定格消費電力 (4)

    Args:
      q_rtd_hs(float): 温水暖房用熱源機の定格能力 (W)
      e_rtd(float): 当該給湯機の効率

    Returns:
      float: 定格消費電力

    """
    return q_rtd_hs / e_rtd


def get_e_rtd():
    """定格効率

    Args:

    Returns:
      float: 定格効率

    """
    return 4.05


def calc_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh):
    """定格能力 (5)

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
      float: 定格能力 (5)

    """
    # 最大能力
    q_max_hs = appendix_H.calc_q_max_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

    return q_max_hs * 0.8


def get_e_r_hs(Theta_SW_hs, Theta_ex, Q_out_H_hs, Q_max_H_hs):
    """1時間平均の効率比 (6)

    Args:
      Theta_SW_hs(ndarray): 温水暖房用熱源機の往き温水温度
      Theta_ex(ndarray): 外気温度
      Q_out_H_hs(ndarray): 1時間当たりの温水暖房用熱源機の暖房出力 (MJ/h)
      Q_max_H_hs(ndarray): 熱源機の最大暖房出力 (MJ/h)

    Returns:
      ndarray: 1時間平均の効率比 (6)

    """
    return (1.120656 - 0.03703 * (Theta_SW_hs - Theta_ex)) * (1 - Q_out_H_hs / Q_max_H_hs) ** 2 \
           + (-0.36786 + 0.012152 * (Theta_SW_hs - Theta_ex)) * (1 - Q_out_H_hs / Q_max_H_hs) \
           + 1


# ============================================================================
# D.2.2 ガス消費量
# ============================================================================

def get_E_G_hs():
    """ガス消費量

    Args:

    Returns:
      ndarray: ガス消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# D.2.3 灯油消費量
# ============================================================================

def get_E_K_hs():
    """灯油消費量

    Args:

    Returns:
      ndarray: 灯油消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# D.2.4 その他の一次エネルギー消費量
# ============================================================================

def get_E_M_hs():
    """

    Args:

    Returns:
      ndarray: その他の一次エネルギー消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# D.3 最大暖房出力
# ============================================================================

def calc_Q_max_H_hs(q_rtd_hs, Theta_SW_hs, Theta_ex, h_ex):
    """最大暖房出力 (7)

    Args:
      q_rtd_hs(float): 温水暖房用熱源機の定格能力 (W)
      Theta_SW_hs(ndarray): 温水暖房用熱源機の往き温水温度
      Theta_ex(ndarray): 外気温度
      h_ex(ndarray): 外気相対湿度

    Returns:
      最大暖房出力 (7)

    """
    # デフロスト補正係数
    C_def = get_C_def(Theta_ex, h_ex)

    return (11.62 + 0.2781 * Theta_ex - 0.00113 * Theta_ex ** 2 - 0.1271 * Theta_SW_hs - 0.00363 * Theta_ex * Theta_SW_hs) \
           * (q_rtd_hs / 6) * (C_def / 0.85) * 3600 * 10 ** (-6)


def get_C_def(Theta_ex, h_ex):
    """デフロスト補正係数

    Args:
      Theta_ex(ndarray): 外気温度
      h_ex(ndarray): 外気相対湿度

    Returns:
      ndarray: デフロスト補正係数

    """
    C_def = np.zeros(24 * 365)
    C_def[:] = 1
    C_def[(Theta_ex < 5) * (h_ex >= 80)] = 0.85
    return C_def
