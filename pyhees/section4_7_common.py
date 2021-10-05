import numpy as np

def get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t):
    """温水暖房用熱源機の暖房出力 (5)

    Args:
      Q_dmd_H_hs_d_t(ndarray): 1時間当たりの熱源機の熱需要 (MJ/h)
      Q_max_H_hs_d_t(ndarray): 1時間当たりの熱源機の最大暖房出力 (MJ/h)

    Returns:
      ndarray: 温水暖房用熱源機の暖房出力 (5)

    """
    return np.clip(Q_dmd_H_hs_d_t, None, Q_max_H_hs_d_t)
