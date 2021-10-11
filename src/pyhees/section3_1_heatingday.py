import numpy as np


# ============================================================================
# 10. 暖房日
# ============================================================================


def get_heating_flag_d(L_dash_H_R_d_t_i):
    """暖房日 = 暖房使用が発生することが見込まれる日

    Args:
      L_dash_H_R_d_t_i(ndarray): 標準住戸の負荷補正前の暖房負荷 (MJ/h)

    Returns:
      ndarray: 暖房使用が発生することが見込まれる日

    """
    L_dash_H_R_d_t = np.sum(L_dash_H_R_d_t_i, axis=0)
    L_dash_H_R_d = np.sum(L_dash_H_R_d_t.reshape(365, 24), axis=1)

    heating_flag_d = np.ones(365)
    heating_flag_d[1:] = L_dash_H_R_d[0:364] > 0

    return heating_flag_d
