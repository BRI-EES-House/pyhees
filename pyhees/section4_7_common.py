import numpy as np

def get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t):
    """ 温水暖房用熱源機の暖房出力 (5)

    :param Q_dmd_H_hs_d_t: 1時間当たりの熱源機の熱需要 (MJ/h)
    :type Q_dmd_H_hs_d_t: ndarray
    :param Q_max_H_hs_d_t: 1時間当たりの熱源機の最大暖房出力 (MJ/h)
    :type Q_max_H_hs_d_t: ndarray
    :return: 温水暖房用熱源機の暖房出力 (5)
    :rtype: ndarray
    """
    return np.clip(Q_dmd_H_hs_d_t, None, Q_max_H_hs_d_t)
