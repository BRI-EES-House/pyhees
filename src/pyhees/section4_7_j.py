# ============================================================================
# 付録 J パネルラジエーター
# ============================================================================

import numpy as np
import pyhees.section4_7_m as appendix_M


# ============================================================================
# J.2 温水供給運転率
# ============================================================================

def calc_r_WS_rad(region, mode, A_HCZ, R_type, Theta_SW, Q_T_H_rad):
    """1時間平均の放熱器の温水供給運転率 (1)

    Args:
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      A_HCZ(float): 暖冷房区画の床面積
      R_type(string): 居室の形式
      Theta_SW(ndarray): 往き温水温度 (℃)
      Q_T_H_rad(ndarray): 放熱器の処理暖房負荷

    Returns:
      ndarray: 1時間平均の放熱器の温水供給運転率 (1)

    """
    # 放熱器の最大能力
    q_max_rad = calc_q_max_rad(region, mode, A_HCZ, R_type)

    # 最大暖房出力
    Q_max_H_rad = get_Q_max_H_rad(Theta_SW, q_max_rad)

    return Q_T_H_rad / Q_max_H_rad


# ============================================================================
# J.3 最大暖房出力
# ============================================================================

def get_Q_max_H_rad(Theta_SW, q_max_rad):
    """最大暖房出力 (2)

    Args:
      Theta_SW(ndarray): 往き温水温度 (℃)
      q_max_rad(ndarray): 放熱器の最大能力 （W）

    Returns:
      ndarray: 最大暖房出力 (2)

    """
    return np.ones(24*365) *  q_max_rad * (Theta_SW - 20) / (60 - 20) * 3600 / (10 ** 6)


def calc_q_max_rad(region, mode, A_HCZ, R_type):
    """放熱器の最大能力

    Args:
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      A_HCZ(float): 暖冷房区画の床面積
      R_type(string): 居室の形式

    Returns:
      ndarray: 放熱器の最大能力

    """
    # 付録Mに定める放熱器の最大能力 q_max_rad に等しいものとする。
    return appendix_M.calc_q_max_rad(region, mode, A_HCZ, R_type)
