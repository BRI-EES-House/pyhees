# ============================================================================
# 付録 C 電気ヒーター温水暖房機及び電気ヒーター給湯温水暖房機
# ============================================================================

import numpy as np
import pyhees.section4_7_h as appendix_H


# ============================================================================
# C.2 エネルギー消費量
# ============================================================================

# ============================================================================
# C.2.1 消費電力量
# ============================================================================

def calc_E_E_hs(Q_out_H_hs, r_WS_hs):
    """ 消費電力量 (1)

    :param Q_out_H_hs: 1時間当たりの熱源機暖房出力 (MJ/h)
    :type Q_out_H_hs: ndarray
    :param r_WS_hs: 1時間平均の温水暖房用熱源機の温水供給運転率
    :type r_WS_hs: ndarray
    :return: 消費電力量
    :rtype: ndarray
    """
    # 電気ヒーターの消費電力量
    E_E_hs_htr = get_E_E_hs_htr(Q_out_H_hs)

    # 送水ポンプの消費電力量
    E_E_hs_pmp = calc_E_E_hs_pmp(r_WS_hs)

    return E_E_hs_htr + E_E_hs_pmp


def get_E_E_hs_htr(Q_out_H_hs):
    """ 電気ヒーターの消費電力量 (2)

    :param Q_out_H_hs: 1時間当たりの熱源機暖房出力 (MJ/h)
    :type Q_out_H_hs: ndarray
    :return: 電気ヒーターの消費電力量 (2)
    :rtype: ndarray
    """
    return Q_out_H_hs * 10 ** 3 / 3600


def calc_E_E_hs_pmp(r_WS_hs):
    """ 送水ポンプの消費電力量 (3)

    :param r_WS_hs: 1時間平均の温水暖房用熱源機の温水供給運転率
    :type r_WS_hs: ndarray
    :return: 送水ポンプの消費電力量
    :rtype: ndarray
    """
    # 送水ポンプの消費電力
    P_hs_pmp = get_P_hs_pmp()

    return P_hs_pmp * r_WS_hs * 10 ** (-3)


def get_P_hs_pmp():
    """ 送水ポンプの消費電力

    :return: 送水ポンプの消費電力
    :rtype: float
    """
    return 90


# ============================================================================
# C.2.2 ガス消費量
# ============================================================================

def get_E_G_hs():
    """ ガス消費量

    :return: ガス消費量
    :rtype: ndarray
    """
    return np.zeros(24 * 365)


# ============================================================================
# C.2.3 灯油消費量
# ============================================================================

def get_E_K_hs():
    """ 灯油消費量

    :return: 灯油消費量
    :rtype: ndarray
    """
    return np.zeros(24 * 365)


# ============================================================================
# C.2.4 その他の一次エネルギー消費量
# ============================================================================

def get_E_M_hs():
    """ その他の一次エネルギー消費量

    :return: その他の一次エネルギー消費量
    :rtype: ndarray
    """
    return np.zeros(24 * 365)


# ============================================================================
# C.3 最大暖房出力
# ============================================================================

def calc_Q_max_H_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh):
    """ 最大暖房出力 (4)

    :param region: 省エネルギー地域区分
    :type region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param mode_MR: 主たる居室の運転モード 'い', 'ろ', 'は'
    :type mode_MR: str
    :param mode_OR: その他の居室の運転モード 'い', 'ろ', 'は'
    :type mode_OR: str
    :param has_MR_hwh: 温水暖房の放熱器を主たる居室に設置する場合はTrue
    :type has_MR_hwh: bool
    :param has_OR_hwh: 温水暖房の放熱器をその他の居室に設置する場合はTrue
    :type has_OR_hwh: bool
    :return: 最大暖房出力
    :rtype: ndarray
    """
    # 定格能力
    q_rtd_hs = get_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

    return np.ones(24*365) * q_rtd_hs * 3600 / (10 ** 6)


def get_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh):
    """ 温水暖房用熱源機の定格能力

    :param region: 省エネルギー地域区分
    :type region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param mode_MR: 主たる居室の運転モード 'い', 'ろ', 'は'
    :type mode_MR: str
    :param mode_OR: その他の居室の運転モード 'い', 'ろ', 'は'
    :type mode_OR: str
    :param has_MR_hwh: 温水暖房の放熱器を主たる居室に設置する場合はTrue
    :type has_MR_hwh: bool
    :param has_OR_hwh: 温水暖房の放熱器をその他の居室に設置する場合はTrue
    :type has_OR_hwh: bool
    :return: 温水暖房用熱源機の定格能力
    :rtype: float
    """
    # 付録Hに定める温水暖房用熱源機の最大能力 q_max_hs に等しい
    return appendix_H.calc_q_max_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)
