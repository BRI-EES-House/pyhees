import numpy as np


def get_Q_T_H_d_t_i(Q_max_H_d_t_i, L_H_d_t_i):
    """ 暖房設備機器等の処理暖房負荷（MJ/h）(6a)を計算する

    :param Q_max_H_d_t_i: 暖房設備機器の最大暖房出力
    :type Q_max_H_d_t_i: ndarray
    :param L_H_d_t_i: 暖房負荷
    :type L_H_d_t_i: ndarray
    :return: 暖房設備機器等の処理暖房負荷（MJ/h）
    :rtype: ndarray
    """
    assert len(Q_max_H_d_t_i.shape) == 1
    assert len(L_H_d_t_i.shape) == 1
    return np.min([Q_max_H_d_t_i, L_H_d_t_i], axis=0)


def get_Q_T_CS_d_t_i(Q_max_CS_d_t_i, L_CS_d_t_i):
    """ 冷房設備機器の処理冷房顕熱負荷（MJ/h）(19a)を計算する

    :param Q_max_CS_d_t_i: 最大冷房顕熱出力
    :type Q_max_CS_d_t_i: ndarray
    :param L_CS_d_t_i: 冷房顕熱負荷
    :type L_CS_d_t_i: ndarray
    :return: 冷房設備機器の処理冷房顕熱負荷（MJ/h）
    :rtype: ndarray
    """
    return np.min([Q_max_CS_d_t_i, L_CS_d_t_i], axis=0)


def get_Q_UT_CS_d_t_i(L_CS_d_t_i, Q_T_CS_d_t_i):
    """ 冷房設備機器の未処理冷房顕熱負荷（MJ/h）(19b)を計算する

    :param Q_T_CS_d_t_i: 最大冷房潜熱出力
    :type Q_T_CS_d_t_i: ndarray
    :param L_CS_d_t_i: 冷房顕熱負荷
    :type L_CS_d_t_i: ndarray
    :return: 冷房設備機器の未処理冷房顕熱負荷（MJ/h）
    :rtype: ndarray
    """
    return L_CS_d_t_i - Q_T_CS_d_t_i


def get_Q_T_CL_d_t_i(Q_max_CL_d_t_i, L_CL_d_t_i):
    """ 冷房設備機器の処理冷房潜熱負荷（MJ/h）(20a)を計算する

    :param Q_max_CL_d_t_i: 最大冷房潜熱出力
    :type Q_max_CL_d_t_i: ndarray
    :param L_CL_d_t_i: 冷房潜熱負荷
    :type L_CL_d_t_i: ndarray
    :return: 冷房設備機器の処理冷房潜熱負荷（MJ/h）
    :rtype: ndarray
    """
    return np.min([Q_max_CL_d_t_i, L_CL_d_t_i], axis=0)


def get_Q_UT_CL_d_t_i(L_CL_d_t_i, Q_T_CL_d_t_i):
    """ 冷房設備機器の未処理冷房潜熱負荷（MJ/h）(20b)を計算する

    :param Q_max_CL_d_t_i: 最大冷房潜熱出力
    :type Q_max_CL_d_t_i: ndarray
    :param L_CL_d_t_i: 冷房潜熱負荷
    :type L_CL_d_t_i: ndarray
    :return: 冷房設備機器の未処理冷房潜熱負荷（MJ/h）
    :rtype: ndarray
    """
    return L_CL_d_t_i - Q_T_CL_d_t_i
