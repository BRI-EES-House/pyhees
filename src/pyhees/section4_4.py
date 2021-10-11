# ============================================================================
# 第四章 暖冷房設備
# 第四節 FF 暖房機
# Ver.03（エネルギー消費性能計算プログラム（住宅版）Ver.02～）
# ============================================================================

import numpy as np
from pyhees.section4_1_Q import get_Q_T_H_d_t_i


# ============================================================================
# 5. 最大暖房出力
# ============================================================================

def get_Q_max_H_d_t(q_max_H):
    """最大暖房出力

    Args:
      q_max_H(float): 最大暖房能力

    Returns:
      ndarray: 最大暖房出力

    """
    return np.ones(24 * 365) * q_max_H * 3600 * 10 ** (-6)  # (1)


# ============================================================================
# 6. 暖房エネルギー消費量
# ============================================================================

# ============================================================================
# 6.1 消費電力量
# ============================================================================

def calc_E_E_H_d_t(q_max_H, q_min_H, P_rtd_H, P_itm_H, L_H_d_t):
    """消費電力量

    Args:
      q_max_H(float): 最大暖房能力
      q_min_H(float): 連続運転時最小能力
      P_rtd_H(float): 定格暖房消費電力
      P_itm_H(float): 断続時消費電力
      L_H_d_t(ndarray): 暖冷房区画の１時間当たりの暖房負荷

    Returns:
      ndarray: 消費電力量

    """
    # 最大暖房出力
    Q_max_H_d_t = get_Q_max_H_d_t(q_max_H)

    # 処理暖房負荷
    Q_T_H_d_t = get_Q_T_H_d_t_i(Q_max_H_d_t, L_H_d_t)

    # 消費電力量
    tmp1 = P_rtd_H * Q_T_H_d_t / Q_max_H_d_t * 10 ** (-3)
    tmp1[Q_T_H_d_t < q_min_H * 3600 * 10 ** (-6)] = 0.0

    tmp2 = (P_rtd_H * Q_T_H_d_t / Q_max_H_d_t + P_itm_H) * 10 ** (-3)
    tmp2[Q_T_H_d_t >= q_min_H * 3600 * 10 ** (-6)] = 0.0

    E_E_H_d_t = tmp1 + tmp2

    # ただし、Q_T_H_d_tが0の場合は0
    E_E_H_d_t[Q_T_H_d_t == 0] = 0

    return E_E_H_d_t


# ============================================================================
# 6.2 ガス消費量
# ============================================================================

def calc_E_G_H_d_t(fuel, q_max_H, e_rtd_H, L_H_d_t):
    """ガス消費量

    Args:
      fuel(string): G'か'K'の値をとる
      q_max_H(float): 最大暖房能力
      e_rtd_H(float): 定格暖房エネルギー消費効率
      L_H_d_t(ndarray): 暖冷房区画の１時間当たりの暖房負荷

    Returns:
      ndarray: ガス消費量

    Raises:
      ValueError: fuel が 'G'か'K' 以外の場合に発生する

    """
    if fuel == 'G':
        return calc_E_F_H_d_t(q_max_H, e_rtd_H, L_H_d_t)
    elif fuel == 'K':
        return np.zeros(24 * 365)
    else:
        raise ValueError(fuel)


# ============================================================================
# 6.3 灯油消費量
# ============================================================================

def calc_E_K_H_d_t(fuel, q_max_H, e_rtd_H, L_H_d_t):
    """灯油消費量

    Args:
      fuel(string): G'か'K'の値をとる
      q_max_H(float): 最大暖房能力
      e_rtd_H(float): 定格暖房エネルギー消費効率
      L_H_d_t(ndarray): 暖冷房区画の１時間当たりの暖房負荷

    Returns:
      ndarray: 灯油消費量

    Raises:
      ValueError: fuel が 'G'か'K' 以外の場合に発生する

    """
    if fuel == 'K':
        return calc_E_F_H_d_t(q_max_H, e_rtd_H, L_H_d_t)
    elif fuel == 'G':
        return np.zeros(24 * 365)
    else:
        raise ValueError(fuel)


# ============================================================================
# 6.4 その他の燃料による一次エネルギー消費量
# ============================================================================

def get_E_M_H_d_t():
    """その他の燃料による一次エネルギー消費量

    Args:

    Returns:
      ndarray: その他の燃料による一次エネルギー消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# 7.燃料消費量
# ============================================================================

def calc_E_F_H_d_t(q_max_H, e_rtd_H, L_H_d_t):
    """燃料消費量

    Args:
      q_max_H(float): 最大暖房能力
      e_rtd_H(float): 定格暖房エネルギー消費効率
      L_H_d_t(ndarray): 暖冷房区画の１時間当たりの暖房負荷

    Returns:
      ndarray: 燃料消費量

    """
    # 最大暖房出力
    Q_max_H_d_t = get_Q_max_H_d_t(q_max_H)

    # 処理暖房負荷
    Q_T_H_d_t = get_Q_T_H_d_t_i(Q_max_H_d_t, L_H_d_t)

    E_F_H_d_t = Q_T_H_d_t / e_rtd_H  # (3)

    return E_F_H_d_t


def calc_Q_UT_H_d_t(q_max_H, L_H_d_t):
    """未処理暖房負荷

    Args:
      q_max_H(float): 最大暖房能力
      L_H_d_t(ndarray): 暖冷房区画の１時間当たりの暖房負荷

    Returns:
      ndarray: 未処理暖房負荷

    """
    # 最大暖房出力
    Q_max_H_d_t = get_Q_max_H_d_t(q_max_H)

    # 処理暖房負荷
    Q_T_H_d_t = get_Q_T_H_d_t_i(Q_max_H_d_t, L_H_d_t)

    # 未処理暖房負荷
    Q_UT_H_d_t = L_H_d_t - Q_T_H_d_t

    return Q_UT_H_d_t


if __name__ == '__main__':
    # ダミー負荷
    L_H_d_t = np.ones(24 * 365) * 12

    # 設定値
    q_max_H = 2585.8770
    q_min_H = 580.6191
    e_rtd_H = 0.860
    P_rtd_H = 8.0938
    P_itm_H = 40
    fuel = 'G'

    # FF暖房
    E_E_H_d_t = calc_E_E_H_d_t(
        q_max_H=q_max_H,
        q_min_H=q_min_H,
        P_rtd_H=P_rtd_H,
        P_itm_H=P_itm_H,
        L_H_d_t=L_H_d_t
        )
    E_G_H_d_t = calc_E_G_H_d_t(fuel, q_max_H, e_rtd_H, L_H_d_t)
    E_K_H_d_t = calc_E_K_H_d_t(fuel, q_max_H, e_rtd_H, L_H_d_t)
    E_M_H_d_t = get_E_M_H_d_t()
    print('E_E_H = {} '.format(np.sum(E_E_H_d_t)))
    print('E_G_H = {} '.format(np.sum(E_G_H_d_t)))
    print('E_K_H = {} '.format(np.sum(E_K_H_d_t)))
    print('E_M_H = {} '.format(np.sum(E_M_H_d_t)))
