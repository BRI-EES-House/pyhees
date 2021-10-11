import numpy as np


def get_Q_T_H_d_t_i(Q_max_H_d_t_i, L_H_d_t_i):
    """暖房設備機器等の処理暖房負荷（MJ/h）(6a)を計算する

    Args:
      Q_max_H_d_t_i(ndarray): 暖房設備機器の最大暖房出力
      L_H_d_t_i(ndarray): 暖房負荷

    Returns:
      ndarray: 暖房設備機器等の処理暖房負荷（MJ/h）

    """
    assert len(Q_max_H_d_t_i.shape) == 1
    assert len(L_H_d_t_i.shape) == 1
    return np.min([Q_max_H_d_t_i, L_H_d_t_i], axis=0)


def get_Q_T_CS_d_t_i(Q_max_CS_d_t_i, L_CS_d_t_i):
    """冷房設備機器の処理冷房顕熱負荷（MJ/h）(19a)を計算する

    Args:
      Q_max_CS_d_t_i(ndarray): 最大冷房顕熱出力
      L_CS_d_t_i(ndarray): 冷房顕熱負荷

    Returns:
      ndarray: 冷房設備機器の処理冷房顕熱負荷（MJ/h）

    """
    return np.min([Q_max_CS_d_t_i, L_CS_d_t_i], axis=0)


def get_Q_UT_CS_d_t_i(L_CS_d_t_i, Q_T_CS_d_t_i):
    """冷房設備機器の未処理冷房顕熱負荷（MJ/h）(19b)を計算する

    Args:
      Q_T_CS_d_t_i(ndarray): 最大冷房潜熱出力
      L_CS_d_t_i(ndarray): 冷房顕熱負荷

    Returns:
      ndarray: 冷房設備機器の未処理冷房顕熱負荷（MJ/h）

    """
    return L_CS_d_t_i - Q_T_CS_d_t_i


def get_Q_T_CL_d_t_i(Q_max_CL_d_t_i, L_CL_d_t_i):
    """冷房設備機器の処理冷房潜熱負荷（MJ/h）(20a)を計算する

    Args:
      Q_max_CL_d_t_i(ndarray): 最大冷房潜熱出力
      L_CL_d_t_i(ndarray): 冷房潜熱負荷

    Returns:
      ndarray: 冷房設備機器の処理冷房潜熱負荷（MJ/h）

    """
    return np.min([Q_max_CL_d_t_i, L_CL_d_t_i], axis=0)


def get_Q_UT_CL_d_t_i(L_CL_d_t_i, Q_T_CL_d_t_i):
    """冷房設備機器の未処理冷房潜熱負荷（MJ/h）(20b)を計算する

    Args:
      Q_max_CL_d_t_i(ndarray): 最大冷房潜熱出力
      L_CL_d_t_i(ndarray): 冷房潜熱負荷
      Q_T_CL_d_t_i: returns: 冷房設備機器の未処理冷房潜熱負荷（MJ/h）

    Returns:
      ndarray: 冷房設備機器の未処理冷房潜熱負荷（MJ/h）

    """
    return L_CL_d_t_i - Q_T_CL_d_t_i
