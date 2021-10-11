# ============================================================================
# 付録 H 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機
#        （給湯熱源：ガス瞬間式、暖房熱源：電気ヒートポンプ・ガス瞬間式併用）
# ============================================================================

import numpy as np

import pyhees.section7_1_c as gas


def get_E_E_hs(W_dash_k_d_t, W_dash_s_d_t, W_dash_w_d_t, W_dash_b1_d_t, W_dash_b2_d_t, W_dash_ba1_d_t, theta_ex_d_Ave_d, L_dashdash_ba2_d_t):
    """# 1日当たりの給湯機の消費電力量

    Args:
      W_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯量 (L/d)
      W_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯量 (L/d)
      W_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯量 (L/d)
      W_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/d)
      W_dash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯量 (L/d)
      W_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯量 (L/d)
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 1日当たりの給湯機の消費電力量 (kWh/d)

    """
    return gas.calc_E_E_hs_d_t(
        W_dash_k_d_t=W_dash_k_d_t,
        W_dash_s_d_t=W_dash_s_d_t,
        W_dash_w_d_t=W_dash_w_d_t,
        W_dash_b1_d_t=W_dash_b1_d_t,
        W_dash_b2_d_t=W_dash_b2_d_t,
        W_dash_ba1_d_t=W_dash_ba1_d_t,
        theta_ex_d_Ave_d=theta_ex_d_Ave_d,
        L_dashdash_ba2_d_t=L_dashdash_ba2_d_t
    )


def get_E_G_hs(Theta_ex_Ave, L_dashdash_k, L_dashdash_s, L_dashdash_w, L_dashdash_b1, L_dashdash_b2,
               L_dashdash_ba1, L_dashdash_ba2, bath_function):
    """1時間当たりの給湯機のガス消費量

    Args:
      Theta_ex_Ave(ndarray): 日平均外気温度 (℃)
      L_dashdash_k(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dashdash_s(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dashdash_w(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dashdash_b1(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/d)
      L_dashdash_b2(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/d)
      L_dashdash_ba1(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/d)
      L_dashdash_ba2(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/d)
      bath_function(str): ふろ機能の種類

    Returns:
      ndarray: 1時間当たりの給湯機のガス消費量 (MJ/d)

    """
    return gas.calc_E_G_hs_d_t(
        hw_type=None,
        theta_ex_d_Ave_d=Theta_ex_Ave,
        L_dashdash_k_d_t=L_dashdash_k,
        L_dashdash_s_d_t=L_dashdash_s,
        L_dashdash_w_d_t=L_dashdash_w,
        L_dashdash_b1_d_t=L_dashdash_b1,
        L_dashdash_b2_d_t=L_dashdash_b2,
        L_dashdash_ba1_d_t=L_dashdash_ba1,
        L_dashdash_ba2_d_t=L_dashdash_ba2,
        bath_function=bath_function,
        e_rtd=0.866
    )


def get_E_K_hs():
    """1日当たりの給湯機の灯油消費量

    Args:

    Returns:
      ndarray: 1日当たりの給湯機の灯油消費量

    """
    # 1日当たりの給湯機の灯油消費量は0とする
    return gas.get_E_K_hs_d_t()

if __name__ == '__main__':
    # ダミー負荷
    W_dash_k = np.ones(24 * 365)
    W_dash_s = np.ones(24 * 365)
    W_dash_w = np.ones(24 * 365)
    W_dash_b1 = np.ones(24 * 365)
    W_dash_b2 = np.ones(24 * 365)
    W_dash_ba1 = np.ones(24 * 365)
    W_dash_ba2 = np.ones(24 * 365)
    Theta_ex_Ave = np.ones(24 * 365) * 20
    L_dashdash_k = np.ones(24 * 365)
    L_dashdash_s = np.ones(24 * 365)
    L_dashdash_w = np.ones(24 * 365)
    L_dashdash_b1 = np.ones(24 * 365)
    L_dashdash_b2 = np.ones(24 * 365)
    L_dashdash_ba1 = np.ones(24 * 365)
    L_dashdash_ba2 = np.ones(24 * 365)

    bath_function = 'ふろ給湯機(追焚あり)'

    E_E_hs = get_E_E_hs(
        W_dash_k_d_t=W_dash_k,
        W_dash_s_d_t=W_dash_s,
        W_dash_w_d_t=W_dash_w,
        W_dash_b1_d_t=W_dash_b1,
        W_dash_b2_d_t=W_dash_b2,
        W_dash_ba1_d_t=W_dash_ba1,
        theta_ex_d_Ave_d=Theta_ex_Ave,
        L_dashdash_ba2_d_t=L_dashdash_ba2
        )
    E_G_hs = get_E_G_hs(
        e_rtd=0.75,
        Theta_ex_Ave=Theta_ex_Ave,
        L_dashdash_k=L_dashdash_k,
        L_dashdash_s=L_dashdash_s,
        L_dashdash_w=L_dashdash_w,
        L_dashdash_b1=L_dashdash_b1,
        L_dashdash_b2=L_dashdash_b2,
        L_dashdash_ba1=L_dashdash_ba1,
        L_dashdash_ba2=L_dashdash_ba2,
        bath_function=bath_function
        )
    E_K_hs = get_E_K_hs()
    print('E_E_hs = {}', np.sum(E_E_hs))
    print('E_G_hs = {}', np.sum(E_G_hs))
    print('E_K_hs = {}', np.sum(E_K_hs))
