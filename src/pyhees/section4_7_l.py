# ============================================================================
# 付録 L 温水床暖房
# ============================================================================

import numpy as np
from math import floor

import pyhees.section4_7_q as sc4_7_q


# ※敷設面積については、当該住戸に設置される温水床暖房の値を用いるのではなく、
#  本付録 により求まる値を使用するものとする。 

# ============================================================================
# L.2 熱損失
# ============================================================================

def get_Q_loss_rad(Q_T_H_rad, r_up):
    """放熱器の熱損失 (1)

    Args:
      Q_T_H_rad(ndarray): 1時間当たりの放熱器の処理暖房負荷 (MJ/h)
      r_up(float): 温水床暖房の定免法熱率 (-)

    Returns:
      ndarray: 放熱器の熱損失 (MJ/h)

    """
    return Q_T_H_rad * (1 - r_up) / r_up


# ============================================================================
# L.3 温水供給運転率
# ============================================================================

def get_r_WS_rad(Q_T_H_rad, Q_max_H_rad, racfh_combed=False):
    """温水供給運転率 (2)

    Args:
      Q_T_H_rad(ndarray): 1時間当たりの放熱器の処理暖房負荷 (MJ/h)
      Q_max_H_rad(ndarray): 1時間当たりの放熱器の最大暖房出力 (MJ/h)
      racfh_combed (bool, optional): 主たる居室で温水床暖房とエアコンを併用する場合か否か Defaults to False

    Returns:
      ndarray: 温水供給運転率 (-)

    """
    # 最大暖房出力となる時の運転率 (-)
    r_WS_rad_max = get_r_WS_rad_max(racfh_combed)

    return (Q_T_H_rad / Q_max_H_rad) * r_WS_rad_max


# ============================================================================
# L.4 最大暖房出力
# ============================================================================

def get_Q_max_H_rad(Theta_SW, A_f, racfh_combed=False):
    """放熱器の最大暖房出力 (3)

    Args:
      Theta_SW(ndarray): 往き温水温度 (℃)
      A_f(float): 温水床暖房の敷設面積 (m2)
      racfh_combed (bool, optional): 主たる居室で温水床暖房とエアコンを併用する場合か否か Defaults to False

    Returns:
      ndarray: 放熱器の最大暖房出力

    """
    # 温水床暖房の単位面積当たりの上面最大放熱能力 (W/m2)
    q_max_fh = get_q_max_fh()

    # 最大暖房出力となる時の運転率 (-)
    r_WS_rad_max = get_r_WS_rad_max(racfh_combed)

    Q_max_H_rad = np.ones(24*365) * (q_max_fh * A_f * (Theta_SW - 20) / (60 - 20) * 3600 * 10 ** (-6)) * r_WS_rad_max

    return Q_max_H_rad


def get_q_max_fh():
    """温水床暖房の単位面積当たりの上面最大放熱能力 (W/m2)

    Args:

    Returns:
      float: 温水床暖房の単位面積当たりの上面最大放熱能力

    """
    return 162


def get_r_WS_rad_max(racfh_combed):
    """最大暖房出力となる時の運転率 (-)

    Args:
        racfh_combed (bool): 主たる居室で温水床暖房とエアコンを併用する場合か否か

    Returns:
        float: 最大暖房出力となる時の運転率 (-)
    """
    if racfh_combed:
        return sc4_7_q.get_r_WS_rad_max()
    else:
        return 1.0


# ============================================================================
# L.5 敷設面積
# ============================================================================

def get_A_f(A_HCZ, r_Af):
    """温水床暖房の敷設面積 (4)

    Args:
      A_HCZ(float): 暖冷房区画の床面積
      r_Af(float): 当該住戸における温水床暖房の敷設率 (-)

    Returns:
      float: 温水床暖房の敷設面積

    """
    if r_Af is None:
        r_Af = 0.4

    return A_HCZ * r_Af


def get_r_f(A_f, A_HCZ):
    """温水床暖房の敷設率 (5)

    Args:
      A_f(float): 温水床暖房の敷設面積 (m2)
      A_HCZ(float): 暖冷房区画の床面積

    Returns:
      float: 温水床暖房の敷設率

    """
    r_f = A_f / A_HCZ

    # 1000分の1未満の端数を切り下げた小数第三位までの値とする
    r_f = floor(r_f * 1000) / 1000

    return r_f


# ============================================================================
# L.6 上面放熱率
# ============================================================================

def get_r_up(is_domayuka):
    """上面放熱率 (6) ※参照なし

    Args:
      is_domayuka(bool): 土間床に設置

    Returns:
      float: 上面放熱率

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
    """1) 床暖房パネルの床上側表面熱伝達抵抗と床暖房パネル内の配管から床仕上げ材上側表面までの熱抵抗の合計

    Args:

    Returns:
      float: 床暖房パネルの床上側表面熱伝達抵抗と床暖房パネル内の配管から床仕上げ材上側表面までの熱抵抗の合計

    """
    return 0.269


def get_H(region, is_adjacent_not_insulated):
    """2) 温度差係数U ※参照なし

    Args:
      region(int): 省エネルギー地域区分
      is_adjacent_not_insulated(bool): 当該住戸の床暖房を設置する床の隣接空間が断熱区画外の場合

    Returns:
      温度差係数U: 温度差係数U

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
