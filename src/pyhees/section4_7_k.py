# ============================================================================
# 付録K ファンコンベクター
# ============================================================================


import numpy as np
import pyhees.section4_7_m as appendix_M


# ============================================================================
# K.2 消費電力量
# ============================================================================

def calc_E_E_rad(region, mode, A_HCZ, R_type, Theta_SW, Q_T_H_rad):
    """放熱器の消費電力量 (1)

    Args:
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      A_HCZ(float): 暖冷房区画の床面積
      R_type(string): 居室の形式
      Theta_SW(ndarray): 往き温水温度 (℃)
      Q_T_H_rad(ndarray): 放熱器の処理暖房負荷

    Returns:
      ndarray: 放熱器の消費電力量 (1)

    """
    # ファンコンベクターの最大能力及び最小能力
    q_max_FC = calc_q_max_FC(region, mode, A_HCZ, R_type)
    q_min_FC = get_q_min_FC(q_max_FC)

    # ファンコンベクターの最大暖房出力及び最小暖房出力
    Q_max_H_FC = get_Q_max_H_FC(Theta_SW, q_max_FC)
    Q_min_H_FC = get_Q_min_H_FC(Theta_SW, q_min_FC)

    # ファンコンベクターの最大消費電力及び最小消費電力
    P_max_FC = get_P_max_FC(q_max_FC)
    P_min_FC = get_P_min_FC(q_min_FC)

    # (1a)
    tmp_1a = P_min_FC * (Q_T_H_rad / Q_min_H_FC) * 10 ** (-3)
    tmp_1a[np.logical_not(Q_T_H_rad <= Q_min_H_FC)] = 0

    # (1b)
    tmp_1b = (P_min_FC * (Q_max_H_FC - Q_T_H_rad) / (Q_max_H_FC - Q_min_H_FC) + P_max_FC * (Q_T_H_rad - Q_min_H_FC) / (
                Q_max_H_FC - Q_min_H_FC)) * 10 ** (-3)
    tmp_1b[np.logical_not(np.logical_and(Q_min_H_FC < Q_T_H_rad, Q_T_H_rad < Q_max_H_FC))] = 0

    # (1c)
    tmp_1c = P_max_FC * 10 ** (-3) * np.ones_like(Q_T_H_rad)
    tmp_1c[np.logical_not(Q_max_H_FC <= Q_T_H_rad)] = 0

    E_E_rad = tmp_1a + tmp_1b + tmp_1c
    return E_E_rad


# ============================================================================
# K.3 温水供給運転率
# ============================================================================

def get_r_WS_rad(Q_T_H_rad, Q_min_H_FC):
    """温水供給運転率 (2)

    Args:
      Q_T_H_rad(ndarray): 1時間当たりの放熱器の処理暖房負荷 （MJ/h）
      Q_min_H_FC(ndarray): 1時間当たりのファンコンベクターの最小暖房出力 （MJ/h）

    Returns:
      ndarray: 温水供給運転率

    """
    return Q_T_H_rad / Q_min_H_FC


# ============================================================================
# K.4 最大暖房出力
# ============================================================================

def calc_Q_max_H_rad(Theta_SW, q_max_FC):
    """最大暖房出力

    Args:
      Theta_SW(ndarray): 往き温水温度 (℃)
      q_max_FC(ndarray): ファンコンベクターの最大能力 （W）

    Returns:
      ndarray: 最大暖房出力

    """
    return get_Q_max_H_FC(Theta_SW, q_max_FC)


# ============================================================================
# K.5 ファンコンベクターの最大暖房出力及び最小暖房出力
# ============================================================================

def get_Q_max_H_FC(Theta_SW, q_max_FC):
    """ファンコンベクターの最大暖房出力 (3a)

    Args:
      Theta_SW(ndarray): 往き温水温度 (℃)
      q_max_FC(ndarray): ファンコンベクターの最大能力（W）

    Returns:
      ndarray: ファンコンベクターの最大暖房出力 (3a)

    """

    return q_max_FC * (Theta_SW - 20) / (60 - 20) * 3600 * 10 ** (-6)


def get_Q_min_H_FC(Theta_SW, q_min_FC):
    """ファンコンベクターの最小暖房出力 (3b)

    Args:
      Theta_SW(ndarray): 往き温水温度 (℃)
      q_min_FC(ndarray): ファンコンベクターの最小能力 （W）

    Returns:
      ndarray: ファンコンベクターの最小暖房出力 (3b)

    """
    return q_min_FC * (Theta_SW - 20) / (60 - 20) * 3600 * 10 ** (-6)


def calc_q_max_FC(region, mode, A_HCZ, R_type):
    """ファンコンベクターの最大能力

    Args:
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      A_HCZ(float): 暖冷房区画の床面積
      R_type(string): 居室の形式

    Returns:
      ndarray: ファンコンベクターの最大能力

    """
    # 付録Mに定める放熱器の最大能力 q_max_rad に等しいものとする
    return appendix_M.calc_q_max_rad(region, mode, A_HCZ, R_type)


def get_q_min_FC(q_max_FC):
    """ファンコンベクターの最小能力 (4)

    Args:
      q_max_FC(ndarray): ファンコンベクターの最大能力 （W）

    Returns:
      ndarray: ファンコンベクターの最小能力

    """
    return 0.4859 * q_max_FC


# ============================================================================
# K.6 ファンコンベクターの最大消費電力及び最小消費電力
# ============================================================================

def get_P_max_FC(q_max_FC):
    """ファンコンベクターの最大消費電力 (5a)

    Args:
      q_max_FC(ndarray): ファンコンベクターの最大能力 （W）

    Returns:
      ndarray: ァンコンベクターの最大消費電力

    """
    return 7.564 * 10 ** (-3) * q_max_FC


def get_P_min_FC(q_min_FC):
    """ファンコンベクターの最小消費電力 (5b)

    Args:
      q_min_FC(ndarray): ファンコンベクターの最小能力 （W）

    Returns:
      ndarray: ファンコンベクターの最小消費電力

    """
    return 7.783 * 10 ** (-3) * q_min_FC
