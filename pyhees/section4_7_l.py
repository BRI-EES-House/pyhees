# ============================================================================
# 付録 L 温水床暖房
# ============================================================================

import numpy as np
from math import floor


# ※敷設面積については、当該住戸に設置される温水床暖房の値を用いるのではなく、
#  本付録 により求まる値を使用するものとする。 

# ============================================================================
# L.2 熱損失
# ============================================================================

def get_Q_loss_rad(Q_T_H_rad, r_up):
    """ 放熱器の熱損失 (1)

    :param Q_T_H_rad: 1時間当たりの放熱器の処理暖房負荷 (MJ/h)
    :type Q_T_H_rad: ndarray
    :param r_up: 温水床暖房の定免法熱率 (-)
    :type r_up: float
    :return: 放熱器の熱損失 (MJ/h)
    :rtype: ndarray
    """
    return Q_T_H_rad * (1 - r_up) / r_up


# ============================================================================
# L.3 温水供給運転率
# ============================================================================

def get_r_WS_rad(Q_T_H_rad, Q_max_H_rad):
    """ 温水供給運転率 (2)

    :param Q_T_H_rad: 1時間当たりの放熱器の処理暖房負荷 (MJ/h)
    :type Q_T_H_rad: ndarray
    :param Q_max_H_rad: 1時間当たりの放熱器の最大暖房出力 (MJ/h)
    :type Q_max_H_rad: ndarray
    :return: 温水供給運転率 (-)
    :rtype: ndarray
    """
    return Q_T_H_rad / Q_max_H_rad


# ============================================================================
# L.4 最大暖房出力
# ============================================================================

def get_Q_max_H_rad(Theta_SW, A_f):
    """  放熱器の最大暖房出力 (3)

    :param Theta_SW: 往き温水温度 (℃)
    :type Theta_SW: ndarray
    :param A_f: 温水床暖房の敷設面積 (m2)
    :type A_f: float
    :return: 放熱器の最大暖房出力
    :rtype: ndarray
    """
    # 温水床暖房の単位面積当たりの上面最大放熱能力 (W/m2)
    q_max_fh = get_q_max_fh()

    Q_max_H_rad = np.ones(24*365) * q_max_fh * A_f * (Theta_SW - 20) / (60 - 20) * 3600 * 10 ** (-6)

    return Q_max_H_rad


def get_q_max_fh():
    """ 温水床暖房の単位面積当たりの上面最大放熱能力 (W/m2)

    :return: 温水床暖房の単位面積当たりの上面最大放熱能力
    :rtype: float
    """
    return 162


# ============================================================================
# L.5 敷設面積
# ============================================================================

#
def get_A_f(A_HCZ, r_Af):
    """ 温水床暖房の敷設面積 (4)

    :param A_HCZ: 暖冷房区画の床面積
    :type A_HCZ: float
    :param r_Af: 当該住戸における温水床暖房の敷設率 (-)
    :type r_Af: flloat
    :return: 温水床暖房の敷設面積
    :rtype: float
    """
    return A_HCZ * r_Af


def get_r_f(A_f, A_HCZ):
    """ 温水床暖房の敷設率 (5)

    :param A_f: 温水床暖房の敷設面積 (m2)
    :type A_f: float
    :param A_HCZ: 暖冷房区画の床面積
    :type A_HCZ: float
    :return: 温水床暖房の敷設率
    :rtype: float
    """
    r_f = A_f / A_HCZ

    # 1000分の1未満の端数を切り下げた小数第三位までの値とする
    r_f = floor(r_f * 1000) / 1000

    return r_f


# ============================================================================
# L.6 上面放熱率
# ============================================================================

def get_r_up(is_domayuka):
    """ 上面放熱率 (6) ※参照なし

    :param is_domayuka: 土間床に設置
    :type is_domayuka: bool
    :return: 上面放熱率
    :rtype: float
    """
    # 土間床に設置された温水床暖房の上面放熱率は0.90とすｒ
    if is_domayuka:
        return 0.90

    else:
        # R_si + R_U
        R_si_plus_R_U = get_R_si_plus_R_U()

        # (6)
        r_up = 1 - H * R_si_plus_R_U * R_U

        # 100 分の 1 未満の端数を切り捨てした小数点第 二位までの値
        return floor(r_up * 100) / 100


def get_R_si_plus_R_U():
    """ 1) 床暖房パネルの床上側表面熱伝達抵抗と床暖房パネル内の配管から床仕上げ材上側表面までの熱抵抗の合計

    :return: 床暖房パネルの床上側表面熱伝達抵抗と床暖房パネル内の配管から床仕上げ材上側表面までの熱抵抗の合計
    :rtype: float
    """
    return 0.269


def get_H(region, is_adjacent_not_insulated):
    """ 2) 温度差係数U ※参照なし

    :param region: 省エネルギー地域区分
    :type region: int
    :param is_adjacent_not_insulated: 当該住戸の床暖房を設置する床の隣接空間が断熱区画外の場合
    :type is_adjacent_not_insulated: bool
    :return: 温度差係数U
    :rtype: 温度差係数U
    """
    # TODO: 第3章第2節への参照
    if is_adjacent_not_insulated:
        raise NotImplementedError()
    else:
        if region in [1, 2, 3]:
            return 0.05
        elif region in [4, 5, 6, 7]:
            return 0.15
        else:
            raise NotImplementedError()
