# ============================================================================
# 付録 G ヒートポンプ・ガス瞬間式併用型給湯温水暖房機
#       （給湯熱源：ヒートポンプ・ガス併瞬間式用、暖房熱源：ヒートポンプ・ガス瞬間式併用)
# ============================================================================

import numpy as np


# 給湯機とみなすので、暖房機としての消費エネルギーは計上しない
# ref: section7_1_i

def get_E_E_hs():
    """消費電力量

    Args:

    Returns:
      ndarray: 消費電力量

    """
    return np.zeros(24 * 365)


def get_E_G_hs():
    """ガス消費量

    Args:

    Returns:
      ndarray: ガス消費量

    """
    return np.zeros(24 * 365)


def get_E_K_hs():
    """灯油消費量

    Args:

    Returns:
      ndarray: 灯油消費量

    """

    return np.zeros(24 * 365)


def get_E_M_hs():
    """その他の一次エネルギー消費量

    Args:

    Returns:
      ndarray: その他の一次エネルギー消費量

    """
    return np.zeros(24 * 365)
