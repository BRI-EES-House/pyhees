# ============================================================================
# 付録K ファンコンベクター
# ============================================================================


import numpy as np
import pyhees.section4_7_m as appendix_M


# ============================================================================
# K.2 消費電力量
# ============================================================================

def calc_E_E_rad(region, mode, A_HCZ, R_type, Theta_SW, Q_T_H_rad):
    """ 放熱器の消費電力量 (1)

    :param region: 省エネルギー地域区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は'
    :type mode: str
    :param A_HCZ: 暖冷房区画の床面積
    :type A_HCZ: float
    :param R_type: 居室の形式
    :type R_type: string
    :param Theta_SW: 往き温水温度 (℃)
    :type Theta_SW: ndarray
    :param Q_T_H_rad: 放熱器の処理暖房負荷
    :type Q_T_H_rad: ndarray
    :return: 放熱器の消費電力量 (1)
    :rtype: ndarray
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
    """ 温水供給運転率 (2)

    :param Q_T_H_rad: 1時間当たりの放熱器の処理暖房負荷 （MJ/h）
    :type Q_T_H_rad: ndarray
    :param Q_min_H_FC: 1時間当たりのファンコンベクターの最小暖房出力 （MJ/h）
    :type Q_min_H_FC: ndarray
    :return: 温水供給運転率
    :rtype: ndarray
    """
    return Q_T_H_rad / Q_min_H_FC


# ============================================================================
# K.4 最大暖房出力
# ============================================================================

def calc_Q_max_H_rad(Theta_SW, q_max_FC):
    """ 最大暖房出力

    :param Theta_SW: 往き温水温度 (℃)
    :type Theta_SW: ndarray
    :param q_max_FC: ファンコンベクターの最大能力 （W）
    :type q_max_FC: ndarray
    :return: 最大暖房出力
    :rtype: ndarray
    """
    return get_Q_max_H_FC(Theta_SW, q_max_FC)


# ============================================================================
# K.5 ファンコンベクターの最大暖房出力及び最小暖房出力
# ============================================================================

def get_Q_max_H_FC(Theta_SW, q_max_FC):
    """ ファンコンベクターの最大暖房出力 (3a)

    :param Theta_SW: 往き温水温度 (℃)
    :type Theta_SW: ndarray
    :param q_max_FC: ファンコンベクターの最大能力（W）
    :type q_max_FC: ndarray
    :return: ファンコンベクターの最大暖房出力 (3a)
    :rtype: ndarray
    """

    return q_max_FC * (Theta_SW - 20) / (60 - 20) * 3600 * 10 ** (-6)


def get_Q_min_H_FC(Theta_SW, q_min_FC):
    """ ファンコンベクターの最小暖房出力 (3b)

    :param Theta_SW: 往き温水温度 (℃)
    :type Theta_SW: ndarray
    :param q_min_FC: ファンコンベクターの最小能力 （W）
    :type q_min_FC: ndarray
    :return: ファンコンベクターの最小暖房出力 (3b)
    :rtype: ndarray
    """
    return q_min_FC * (Theta_SW - 20) / (60 - 20) * 3600 * 10 ** (-6)


def calc_q_max_FC(region, mode, A_HCZ, R_type):
    """ ファンコンベクターの最大能力

    :param region: 省エネルギー地域区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は'
    :type mode: str
    :param A_HCZ: 暖冷房区画の床面積
    :type A_HCZ: float
    :param R_type: 居室の形式
    :type R_type: string
    :return: ファンコンベクターの最大能力
    :rtype: ndarray
    """
    # 付録Mに定める放熱器の最大能力 q_max_rad に等しいものとする
    return appendix_M.calc_q_max_rad(region, mode, A_HCZ, R_type)


def get_q_min_FC(q_max_FC):
    """ ファンコンベクターの最小能力 (4)

    :param q_max_FC: ファンコンベクターの最大能力 （W）
    :type q_max_FC: ndarray
    :return: ファンコンベクターの最小能力
    :rtype: ndarray
    """
    return 0.4859 * q_max_FC


# ============================================================================
# K.6 ファンコンベクターの最大消費電力及び最小消費電力
# ============================================================================

def get_P_max_FC(q_max_FC):
    """ ファンコンベクターの最大消費電力 (5a)

    :param q_max_FC: ファンコンベクターの最大能力 （W）
    :type q_max_FC: ndarray
    :return: ァンコンベクターの最大消費電力
    :rtype: ndarray
    """
    return 7.564 * 10 ** (-3) * q_max_FC


def get_P_min_FC(q_min_FC):
    """ ファンコンベクターの最小消費電力 (5b)

    :param q_min_FC: ファンコンベクターの最小能力 （W）
    :type q_min_FC: ndarray
    :return: ファンコンベクターの最小消費電力
    :rtype: ndarray
    """
    return 7.783 * 10 ** (-3) * q_min_FC
