# ============================================================================
# 付録 A 機器の性能を表す仕様の決定方法
# ============================================================================

from pyhees.section4_1_Q import \
    get_Q_T_CL_d_t_i
#    get_Q_T_H_A_d_t

from pyhees.section4_2 import \
    get_season_array_d_t, \
    calc_Q_UT_A

from pyhees.section4_2_b import \
    get_q_hs_rtd_H, \
    get_q_hs_mid_H, \
    get_q_hs_min_H, \
    get_P_hs_rtd_H, \
    get_q_hs_rtd_C, \
    get_q_hs_mid_C, \
    get_q_hs_min_C, \
    get_P_hs_rtd_C, \
    get_V_fan_rtd_H, \
    get_V_fan_mid_H, \
    get_V_fan_rtd_C, \
    get_V_fan_mid_C, \
    get_P_fan_rtd_H,\
    get_P_fan_mid_H, \
    get_P_fan_rtd_C,\
    get_P_fan_mid_C, \
    get_V_fan_dsgn_H, \
    get_V_fan_dsgn_C


from pyhees.section4_8_a import \
    calc_e_ref_H_th

from pyhees.section11_1 import \
    load_outdoor, \
    get_T_ex, \
    get_Theta_ex, \
    get_X_ex, \
    calc_h_ex

import numpy as np

from scipy import optimize

# ============================================================================
# A.2 消費電力量
# ============================================================================

# ============================================================================
# A.2.1 消費電力量
# ============================================================================

# 日付dの時刻tにおける1時間当たりの暖房時の消費電力量（kWh/h）(1)
def calc_E_E_H_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, V_hs_supply_d_t, V_hs_vent_d_t, C_df_H_d_t,
           q_hs_rtd_H, V_hs_dsgn_H, P_hs_mid_H, P_hs_rtd_H, P_fan_rtd_H, P_fan_mid_H, q_hs_min_H, q_hs_mid_H,
           V_fan_rtd_H, V_fan_mid_H, EquipmentSpec, region):

    # 外気条件
    outdoor = load_outdoor()
    Theta_ex_d_t = get_Theta_ex(region, outdoor)

    # (3)
    q_hs_H_d_t = get_q_hs_H_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, V_hs_supply_d_t, C_df_H_d_t, region)

    # (37)
    E_E_fan_H_d_t = get_E_E_fan_H_d_t(P_fan_rtd_H, V_hs_vent_d_t, V_hs_supply_d_t, V_hs_dsgn_H, q_hs_H_d_t)

    # (20)
    e_th_mid_H = calc_e_th_mid_H(V_fan_mid_H, q_hs_mid_H)

    # (19)
    e_th_rtd_H = calc_e_th_rtd_H(V_fan_rtd_H, q_hs_rtd_H)

    # (17)
    e_th_H_d_t = calc_e_th_H_d_t(Theta_ex_d_t, Theta_hs_in_d_t, Theta_hs_out_d_t, V_hs_supply_d_t)

    # (11)
    e_r_rtd_H = get_e_r_rtd_H(e_th_rtd_H, q_hs_rtd_H, P_hs_rtd_H, P_fan_rtd_H)

    # (15)
    e_r_min_H = get_e_r_min_H(e_r_rtd_H)

    # (13)
    e_r_mid_H = get_e_r_mid_H(e_r_rtd_H, e_th_mid_H, q_hs_mid_H, P_hs_mid_H, P_fan_mid_H, EquipmentSpec)

    # (9)
    e_r_H_d_t = get_e_r_H_d_t(q_hs_H_d_t, q_hs_rtd_H, q_hs_min_H, q_hs_mid_H, e_r_mid_H, e_r_min_H, e_r_rtd_H)

    # (7)
    e_hs_H_d_t = get_e_hs_H_d_t(e_th_H_d_t, e_r_H_d_t)

    # (5)
    E_E_comp_H_d_t = get_E_E_comp_H_d_t(q_hs_H_d_t, e_hs_H_d_t)

    # (1)
    E_E_H_d_t = E_E_comp_H_d_t + E_E_fan_H_d_t

    return E_E_H_d_t


# 日付dの時刻tにおける1時間当たりの冷房時の消費電力量（kWh/h）(2)
def get_E_E_C_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t,  X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, V_hs_vent_d_t,
                  q_hs_rtd_C, V_hs_dsgn_C, q_hs_mid_C, q_hs_min_C,
                  P_fan_rtd_C, P_fan_mid_C, P_hs_rtd_C, P_hs_mid_C, V_fan_rtd_C, V_fan_mid_C, EquipmentSpec, region):

    # 外気条件
    outdoor = load_outdoor()
    Theta_ex_d_t = get_Theta_ex(region, outdoor)

    # (4)
    q_hs_C_d_t = get_q_hs_C_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, X_hs_out_d_t, X_hs_in_d_t, V_hs_supply_d_t, region)

    # (38)
    E_E_fan_C_d_t = get_E_E_fan_C_d_t(P_fan_rtd_C, V_hs_vent_d_t, V_hs_supply_d_t, V_hs_dsgn_C, q_hs_C_d_t)

    # (22)
    e_th_mid_C = calc_e_th_mid_C(V_fan_mid_C, q_hs_mid_C)

    # (21)
    e_th_rtd_C = calc_e_th_rtd_C(V_fan_rtd_C, q_hs_rtd_C)

    # (18)
    e_th_C_d_t = calc_e_th_C_d_t(Theta_ex_d_t, Theta_hs_in_d_t, X_hs_in_d_t, Theta_hs_out_d_t, V_hs_supply_d_t)

    # (12)
    e_r_rtd_C = get_e_r_rtd_C(e_th_rtd_C, q_hs_rtd_C, P_hs_rtd_C, P_fan_rtd_C)

    # (16)
    e_r_min_C = get_e_r_min_C(e_r_rtd_C)

    # (14)
    e_r_mid_C = get_e_r_mid_C(e_r_rtd_C, e_th_mid_C, q_hs_mid_C, P_hs_mid_C, P_fan_mid_C, EquipmentSpec)

    # (10)
    e_r_C_d_t = get_e_r_C_d_t(q_hs_C_d_t, q_hs_rtd_C, q_hs_min_C, q_hs_mid_C, e_r_mid_C, e_r_min_C, e_r_rtd_C)

    # (8)
    e_hs_C_d_t = get_e_hs_C_d_t(e_th_C_d_t, e_r_C_d_t)

    # (6)
    E_E_comp_C_d_t = get_E_E_comp_C_d_t(q_hs_C_d_t, e_hs_C_d_t)

    # (2)
    E_E_C_d_t = E_E_comp_C_d_t + E_E_fan_C_d_t

    return E_E_C_d_t


# ============================================================================
# A.3 熱源機の平均暖房能力・平均冷房能力
# ============================================================================

def get_q_hs_H_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, V_hs_supply_d_t, C_df_H_d_t, region):
    """(3-1)(3-2)(3-3)

    :param Theta_hs_out_d_t:日付dの時刻tにおける熱源機の出口における空気温度（℃）
    :param Theta_hs_in_d_t:日付dの時刻tにおける熱源機の入口における空気温度（℃）
    :param V_hs_supply_d_t:日付dの時刻tにおける熱源機の風量（m3/h）
    :param C_df_H_d_t:日付dの時刻tにおけるデフロストに関する暖房出力補正係数（-）
    :param region:地域区分
    :return:日付dの時刻tにおける1時間当たりの熱源機の平均暖房能力（-）
    """
    H, C, M = get_season_array_d_t(region)
    c_p_air = get_c_p_air()
    rho_air = get_rho_air()

    q_hs_H_d_t = np.zeros(24 * 365)

    # 暖房期 (3-1)
    q_hs_H_d_t[H] = np.clip(c_p_air * rho_air * (Theta_hs_out_d_t[H] - Theta_hs_in_d_t[H]) \
                    * (V_hs_supply_d_t[H] / 3600) * (1 / C_df_H_d_t[H]), 0, None)

    # 冷房期 (3-2)
    q_hs_H_d_t[C] = 0

    # 中間期 (3-3)
    q_hs_H_d_t[M] = 0

    return q_hs_H_d_t


def get_q_hs_C_d_t(Theta_hs_out_d_t, Theta_hs_in_d_t, X_hs_out_d_t, X_hs_in_d_t,V_hs_supply_d_t, region):
    """(4a-1)(4b-1)(4c-1)(4a-2)(4b-2)(4c-2)(4a-3)(4b-3)(4c-3)

    :param Theta_hs_out_d_t:日付dの時刻tにおける熱源機の出口における空気温度（℃）
    :param Theta_hs_in_d_t:日付dの時刻tにおける熱源機の入口における空気温度（℃）
    :param X_hs_out_d_t:日付dの時刻tにおける熱源機の出口における絶対湿度（kg/kg(DA)）
    :param X_hs_in_d_t:日付dの時刻tにおける熱源機の入口における絶対湿度（kg/kg(DA)）
    :param V_hs_supply_d_t:日付dの時刻tにおける熱源機の風量（m3/h）
    :param region:地域区分
    :return:日付dの時刻tにおける1時間当たりの熱源機の平均冷房能力（-）
    """
    H, C, M = get_season_array_d_t(region)
    c_p_air = get_c_p_air()
    rho_air = get_rho_air()
    L_wtr = get_L_wtr()

    # 暖房期および中間期 (4a-1)(4b-1)(4c-1)(4a-3)(4b-3)(4c-3)
    q_hs_C_d_t = np.zeros(24 * 365)
    q_hs_CS_d_t = np.zeros(24 * 365)
    q_hs_CL_d_t = np.zeros(24 * 365)

    # 冷房期 (4a-2)(4b-2)(4c-2)
    q_hs_CS_d_t[C] = np.clip(c_p_air * rho_air * (Theta_hs_in_d_t[C] - Theta_hs_out_d_t[C]) * (V_hs_supply_d_t[C] / 3600), 0, None)

    Cf = np.logical_and(C, q_hs_CS_d_t > 0)

    q_hs_CL_d_t[Cf] = np.clip(L_wtr * rho_air * (X_hs_in_d_t[Cf] - X_hs_out_d_t[Cf]) * (V_hs_supply_d_t[Cf] / 3600) * 10 ** 3, 0, None)

    q_hs_C_d_t = q_hs_CS_d_t + q_hs_CL_d_t

    return q_hs_C_d_t


# ============================================================================
# A.4 圧縮機
# ============================================================================

# ============================================================================
# A.4.1 消費電力量
# ============================================================================

def get_E_E_comp_H_d_t(q_hs_H_d_t, e_hs_H_d_t):
    """(5)

    :param q_hs_H_d_t:日付dの時刻tにおける1時間当たりの熱源機の平均暖房能力（-）
    :param e_hs_H_d_t:日付dの時刻tにおける暖房時の熱源機の効率（-）
    :return:日付dの時刻tにおける1時間当たりの暖房時の圧縮機の消費電力量（kWh/h）
    """
    E_E_comp_H_d_t = np.zeros(24 * 365)

    f = q_hs_H_d_t > 0

    E_E_comp_H_d_t[f] = (q_hs_H_d_t[f] / e_hs_H_d_t[f]) * 10 ** (-3)

    return E_E_comp_H_d_t


def get_E_E_comp_C_d_t(q_hs_C_d_t, e_hs_C_d_t):
    """(6)

    :param q_hs_C_d_t:日付dの時刻tにおける1時間当たりの熱源機の平均冷房能力（-）
    :param e_hs_C_d_t:日付dの時刻tにおける冷房時の熱源機の効率（-）
    :return:日付dの時刻tにおける1時間当たりの冷房時の圧縮機の消費電力量（kWh/h）
    """
    E_E_comp_C_d_t = np.zeros(24 * 365)

    f = q_hs_C_d_t > 0

    E_E_comp_C_d_t[f] = (q_hs_C_d_t[f] / e_hs_C_d_t[f]) * 10 ** (-3)

    return E_E_comp_C_d_t


def get_e_hs_H_d_t(e_th_H_d_t, e_r_H_d_t):
    """(7)

    :param e_th_H_d_t:日付dの時刻tにおける暖房時のヒートポンプサイクルの理論効率（-）
    :param e_r_H_d_t:日付dの時刻tにおける暖房時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    :return:日付dの時刻tにおける暖房時の熱源機の効率（-）
    """
    return e_th_H_d_t * e_r_H_d_t


def get_e_hs_C_d_t(e_th_C_d_t, e_r_C_d_t):
    """(8)

    :param e_th_C_d_t:日付dの時刻tにおける冷房時のヒートポンプサイクルの理論効率（-）
    :param e_r_C_d_t:日付dの時刻tにおける冷房時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    :return:日付dの時刻tにおける冷房時の熱源機の効率（-）
    """
    return e_th_C_d_t * e_r_C_d_t


# ============================================================================
# A.4.3 ヒートポンプサイクルの理論効率に対する熱源機の効率の比
# ============================================================================

# ==============================================================================================
# A.4.3.1 エネルギー消費量の算定におけるヒートポンプサイクルの理論効率に対する熱源機の効率の比
# ==============================================================================================

def get_e_r_H_d_t(q_hs_H_d_t, q_hs_rtd_H, q_hs_min_H, q_hs_mid_H, e_r_mid_H, e_r_min_H, e_r_rtd_H):
    """(9-1)(9-2)(9-3)(9-4)

    :param q_hs_H_d_t: 日付dの時刻tにおける1時間当たりの熱源機の平均暖房能力（-）
    :param q_hs_rtd_H: 熱源機の定格暖房能力（-）
    :param q_hs_min_H: 熱源機の最小暖房能力（-）
    :param q_hs_mid_H: 熱源機の中間暖房能力（-）
    :param e_r_mid_H: 中間暖房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    :param e_r_min_H: 最小暖房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    :param e_r_rtd_H: 定格暖房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    :return: 日付dの時刻tにおける暖房時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    """
    f1 = q_hs_H_d_t <= q_hs_min_H
    f2 = (q_hs_min_H < q_hs_H_d_t) & (q_hs_H_d_t <= q_hs_mid_H)
    f3 = (q_hs_mid_H < q_hs_H_d_t) & (q_hs_H_d_t <= q_hs_rtd_H)
    f4 = q_hs_rtd_H < q_hs_H_d_t

    e_r_H_d_t = np.zeros(24 * 365)

    # (9-1)
    e_r_H_d_t[f1] = e_r_min_H - (q_hs_min_H - q_hs_H_d_t[f1]) * (e_r_min_H / q_hs_min_H)

    # (9-2)
    e_r_H_d_t[f2] = e_r_mid_H - (q_hs_mid_H - q_hs_H_d_t[f2]) \
                    * ((e_r_mid_H - e_r_min_H) / (q_hs_mid_H - q_hs_min_H))

    # (9-3)
    e_r_H_d_t[f3] = e_r_rtd_H - (q_hs_rtd_H - q_hs_H_d_t[f3]) \
                    * ((e_r_rtd_H - e_r_mid_H) / (q_hs_rtd_H - q_hs_mid_H))

    # (9-4)
    f5 = np.logical_and(f4, e_r_rtd_H > 0.4)
    f6 = np.logical_and(f4, e_r_rtd_H <= 0.4)

    e_r_H_d_t[f5] = np.clip(e_r_rtd_H - (q_hs_H_d_t[f5] - q_hs_rtd_H) * (e_r_rtd_H / q_hs_rtd_H), 0.4, None)

    e_r_H_d_t[f6] = e_r_rtd_H

    return e_r_H_d_t


def get_e_r_C_d_t(q_hs_C_d_t, q_hs_rtd_C, q_hs_min_C, q_hs_mid_C, e_r_mid_C, e_r_min_C, e_r_rtd_C):
    """(10-1)(10-2)(10-3)(10-4)

    :param q_hs_C_d_t: 日付dの時刻tにおける1時間当たりの熱源機の平均冷房能力（-）
    :param q_hs_rtd_C: 熱源機の定格冷房能力（-）
    :param q_hs_min_C: 熱源機の最小冷房能力（-）
    :param q_hs_mid_C: 熱源機の中間冷房能力（-）
    :param e_r_mid_C: 中間冷房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    :param e_r_min_C: 最小冷房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    :param e_r_rtd_C: 定格冷房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    :return: 日付dの時刻tにおける冷房時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    """
    f1 = q_hs_C_d_t <= q_hs_min_C
    f2 = (q_hs_min_C < q_hs_C_d_t) & (q_hs_C_d_t <= q_hs_mid_C)
    f3 = (q_hs_mid_C < q_hs_C_d_t) & (q_hs_C_d_t <= q_hs_rtd_C)
    f4 = q_hs_rtd_C < q_hs_C_d_t

    e_r_C_d_t = np.zeros(24 * 365)

    # (10-1)
    e_r_C_d_t[f1] = e_r_min_C - (q_hs_min_C - q_hs_C_d_t[f1]) * (e_r_min_C / q_hs_min_C)

    # (10-2)
    e_r_C_d_t[f2] = e_r_mid_C - (q_hs_mid_C - q_hs_C_d_t[f2]) \
                    * ((e_r_mid_C - e_r_min_C) / (q_hs_mid_C - q_hs_min_C))

    # (10-3)
    e_r_C_d_t[f3] = e_r_rtd_C - (q_hs_rtd_C - q_hs_C_d_t[f3]) \
                    * ((e_r_rtd_C - e_r_mid_C) / (q_hs_rtd_C - q_hs_mid_C))

    # (10-4)
    f5 = np.logical_and(f4, e_r_rtd_C > 0.4)
    f6 = np.logical_and(f4, e_r_rtd_C <= 0.4)

    e_r_C_d_t[f5] = np.clip(e_r_rtd_C - (q_hs_C_d_t[f5] - q_hs_rtd_C) * (e_r_rtd_C / q_hs_rtd_C), 0.4, None)

    e_r_C_d_t[f6] = e_r_rtd_C

    return e_r_C_d_t


# ===============================================================================
# A.4.3.2 JIS試験におけるヒートポンプサイクルの理論効率に対する熱源機の効率の比
# ===============================================================================

def get_e_r_rtd_H(e_th_rtd_H, q_hs_rtd_H, P_hs_rtd_H, P_fan_rtd_H):
    """(11a)(11b)

    :param e_th_rtd_H: 定格暖房能力運転時のヒートポンプサイクルの理論効率（-）
    :param q_hs_rtd_H: 熱源機の定格暖房能力（-）
    :param P_hs_rtd_H: 熱源機の定格暖房消費電力（W）
    :param P_fan_rtd_H: 定格暖房能力運転時の送風機の消費電力（W）
    :return: 定格暖房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    """
    # 定格暖房能力運転時の熱源機の効率（-）(11b)
    if P_hs_rtd_H <= P_fan_rtd_H:
        raise ValueError(P_fan_rtd_H)

    e_hs_rtd_H = q_hs_rtd_H / (P_hs_rtd_H - P_fan_rtd_H)

    # (11a)
    e_r_rtd_H = e_hs_rtd_H / e_th_rtd_H

    e_r_rtd_H = np.clip(e_r_rtd_H, 0, 1.0)

    return e_r_rtd_H


def get_e_r_rtd_C(e_th_rtd_C, q_hs_rtd_C, P_hs_rtd_C, P_fan_rtd_C):
    """(12a)(12b)

    :param e_th_rtd_C: 定格冷房能力運転時のヒートポンプサイクルの理論効率（-）
    :param q_hs_rtd_C: 熱源機の定格冷房能力（-）
    :param P_hs_rtd_C: 熱源機の定格冷房消費電力（W）
    :param P_fan_rtd_C: 定格冷房能力運転時の送風機の消費電力（W）
    :return: 定格冷房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    """
    # 定格暖房能力運転時の熱源機の効率（-）(12b)
    if P_hs_rtd_C <= P_fan_rtd_C:
        raise ValueError(P_hs_rtd_C)

    e_hs_rtd_C = q_hs_rtd_C / (P_hs_rtd_C - P_fan_rtd_C)

    # (12a)
    e_r_rtd_C = e_hs_rtd_C / e_th_rtd_C

    e_r_rtd_C = np.clip(e_r_rtd_C, 0, 1.0)

    return e_r_rtd_C


def get_e_r_mid_H(e_r_rtd_H, e_th_mid_H, q_hs_mid_H, P_hs_mid_H, P_fan_mid_H, EquipmentSpec):
    """(13a-1)(13b)(13a-2)

    :param e_r_rtd_H:定格暖房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    :param e_th_mid_H:中間暖房能力運転時のヒートポンプサイクルの理論効率（-）
    :param q_hs_mid_H:中間暖房能力（-）※ 付録B
    :param P_hs_mid_H:熱源機の中間暖房消費電力（W）※ 付録B
    :param P_fan_mid_H:中間暖房能力運転時の送風機の消費電力（W）※ 付録B
    :param EquipmentSpec:機器の仕様
    :return:中間暖房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    """
    # (13a-2)
    if EquipmentSpec == '入力しない' or EquipmentSpec == '定格能力試験の値を入力する':

        e_r_mid_H = e_r_rtd_H * 0.95

    # (13a-1)(13b)
    elif EquipmentSpec == '定格能力試験と中間能力試験の値を入力する':

        # 中間暖房能力運転時の熱源機の効率（-）
        if P_hs_mid_H <= P_fan_mid_H:
            raise ValueError(P_fan_mid_H)

        e_hs_mid_H = q_hs_mid_H / (P_hs_mid_H - P_fan_mid_H)

        e_r_mid_H = e_hs_mid_H / e_th_mid_H

    else:
        raise ValueError(EquipmentSpec)

    e_r_mid_H = np.clip(e_r_mid_H, 0, 1.0)

    return e_r_mid_H


def get_e_r_mid_C(e_r_rtd_C, e_th_mid_C, q_hs_mid_C, P_hs_mid_C, P_fan_mid_C, EquipmentSpec):
    """(14a-1)(14b)(14a-2)

    :param e_r_rtd_C:定格冷房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    :param e_th_mid_C:中間冷房能力運転時のヒートポンプサイクルの理論効率（-）
    :param q_hs_mid_C:中間冷房能力（-）※付録B
    :param P_hs_mid_C:熱源機の中間冷房消費電力（W）※付録B
    :param P_fan_mid_C:中間冷房能力運転時の送風機の消費電力（W）※付録B
    :param EquipmentSpec:機器の仕様
    :return:中間冷房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    """
    # (14a-2)
    if EquipmentSpec == '入力しない' or EquipmentSpec == '定格能力試験の値を入力する':

        e_r_mid_C = e_r_rtd_C * 0.95

    # (14a-1)(14b)
    elif EquipmentSpec == '定格能力試験と中間能力試験の値を入力する':

        # 中間暖房能力運転時の熱源機の効率（-）
        if P_hs_mid_C <= P_fan_mid_C:
            raise ValueError(P_hs_mid_C)

        e_hs_mid_C = q_hs_mid_C / (P_hs_mid_C - P_fan_mid_C)

        e_r_mid_C = e_hs_mid_C / e_th_mid_C

    else:
        raise ValueError(EquipmentSpec)

    e_r_mid_C = np.clip(e_r_mid_C, 0, 1.0)

    return e_r_mid_C


def get_e_r_min_H(e_r_rtd_H):
    """(15)

    :param e_r_rtd_H:定格暖房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    :return:最小暖房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    """
    return e_r_rtd_H * 0.65


def get_e_r_min_C(e_r_rtd_C):
    """(16)

    :param e_r_rtd_C:定格冷房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    :return:最小冷房能力運転時のヒートポンプサイクルの理論効率に対する熱源機の効率の比（-）
    """
    return e_r_rtd_C * 0.65


# ============================================================================
# A.4.4 ヒートポンプサイクルの理論効率
# ============================================================================

# ============================================================================
# A.4.4.1 エネルギー消費量の算定におけるヒートポンプサイクルの理論効率
# ============================================================================

def calc_e_th_H_d_t(Theta_ex_d_t, Theta_hs_in_d_t, Theta_hs_out_d_t, V_hs_supply_d_t):
    """(17)

    :param Theta_ex_d_t: 日付dの時刻tにおける外気温
    :param Theta_hs_in_d_t: 日付dの時刻tにおける熱源機の入口における空気温度
    :param Theta_hs_out_d_t: 日付dの時刻tにおける熱源機の出口における空気温度
    :param V_hs_supply_d_t: 日付dの時刻tにおける熱源機の風量
    :param alpha_c_hex_H: 暖房時の室内熱交換器表面の顕熱伝達率（W/(m2・K)）
    :return: 日付dの時刻tにおける暖房時のヒートポンプサイクルの理論効率（-）
    """
    e_dash_th_d_t = np.zeros(24 * 365)
    for i in range(24 * 365):
        # (35)
        alpha_c_hex_H = get_alpha_c_hex_H(V_hs_supply_d_t[i])

        # (31)
        Theta_sur_f_hex_H = get_Theta_sur_f_hex_H_calc(Theta_hs_in_d_t[i], Theta_hs_out_d_t[i], V_hs_supply_d_t[i],
                                                       alpha_c_hex_H)

        # (23)
        Theta_ref_cnd_H = get_Theta_ref_cnd_H(Theta_sur_f_hex_H)

        # (24)
        Theta_ref_evp_H = get_Theta_ref_evp_H(Theta_ex_d_t[i], Theta_ref_cnd_H)

        # (25)
        Theta_ref_SC_H = get_Theta_ref_SC_H(Theta_ref_cnd_H)

        # (26)
        Theta_ref_SH_H = get_Theta_ref_SH_H(Theta_ref_cnd_H)

        # 4_8_a (1) ヒートポンプサイクルの理論暖房効率
        e_dash_th_d_t[i] = calc_e_ref_H_th(Theta_ref_evp_H, Theta_ref_cnd_H, Theta_ref_SC_H, Theta_ref_SH_H)

    # (17)
    return e_dash_th_d_t


def calc_e_th_C_d_t(Theta_ex_d_t, Theta_hs_in_d_t, X_hs_in_d_t, Theta_hs_out_d_t, V_hs_supply_d_t):
    """(18)

    :param Theta_ex_d_t: 日付dの時刻tにおける外気温
    :param Theta_hs_in_d_t: 日付dの時刻tにおける熱源機の入口における空気温度
    :param X_hs_in_d_t: 日付dの時刻tにおける熱源機の入口における絶対湿度
    :param Theta_hs_out_d_t: 日付dの時刻tにおける熱源機の出口における空気温度
    :param V_hs_supply_d_t: 日付dの時刻tにおける熱源機の風量
    :param alpha_c_hex_C: 冷房時の室内熱交換器表面の顕熱伝達率（W/(m2・K)）
    :return: 日付dの時刻tにおける暖房時のヒートポンプサイクルの理論効率（-）
    """
    e_dash_th_d_t = np.zeros(24 * 365)
    Theta_sur_f_hex_C = np.zeros(24 * 365)
    for i in range(24 * 365):
        # (36)
        alpha_c_hex_C, alpha_dash_c_hex_C = get_alpha_c_hex_C(V_hs_supply_d_t[i], X_hs_in_d_t[i])

        # (32)
        Theta_sur_f_hex_C[i] = get_Theta_sur_f_hex_C_calc(Theta_hs_in_d_t[i], Theta_hs_out_d_t[i], V_hs_supply_d_t[i],
                                                       alpha_c_hex_C)

        # (28)
        Theta_ref_evp_C = get_Theta_ref_evp_C(Theta_sur_f_hex_C[i])

        # (27)
        Theta_ref_cnd_C = get_Theta_ref_cnd_C(Theta_ex_d_t[i], Theta_ref_evp_C)

        # (29)
        Theta_ref_SC_C = get_Theta_ref_SC_C(Theta_ref_cnd_C)

        # (30)
        Theta_ref_SH_C = get_Theta_ref_SH_C(Theta_ref_cnd_C)

        # 4_8_a (1) ヒートポンプサイクルの理論暖房効率
        e_dash_th_d_t[i] = calc_e_ref_H_th(Theta_ref_evp_C, Theta_ref_cnd_C, Theta_ref_SC_C, Theta_ref_SH_C)

    # (18)
    return e_dash_th_d_t - 1


# ============================================================================
# A.4.4.2 JIS試験におけるヒートポンプサイクルの理論効率
# ============================================================================

def calc_e_th_rtd_H(V_fan_rtd_H, q_hs_rtd_H):
    """(19)

    :param V_fan_rtd_H: 定格暖房能力運転時の送風機の風量（m3/h）
    :param q_hs_rtd_H: 定格暖房能力（W）
    :param alpha_c_hex_H: 暖房時の室内熱交換器表面の顕熱伝達率（W/(m2・K)）
    :return: 定格暖房能力運転時のヒートポンプサイクルサイクルの理論効率（-）
    """
    # (35)
    alpha_c_hex_H = get_alpha_c_hex_H(V_fan_rtd_H)

    # (33)
    Theta_sur_f_hex_H = get_Theta_sur_f_hex_H_JIS(V_fan_rtd_H, q_hs_rtd_H, alpha_c_hex_H)

    # (23)
    Theta_ref_cnd_H = get_Theta_ref_cnd_H(Theta_sur_f_hex_H)

    # (24)
    Theta_ref_evp_H = get_Theta_ref_evp_H(7, Theta_ref_cnd_H)

     # (25)
    Theta_ref_SC_H = get_Theta_ref_SC_H(Theta_ref_cnd_H)

    # (26)
    Theta_ref_SH_H = get_Theta_ref_SH_H(Theta_ref_cnd_H)

    # 4_8_a (1) ヒートポンプサイクルの理論暖房効率
    e_dash_th_rtd_H = calc_e_ref_H_th(Theta_ref_evp_H, Theta_ref_cnd_H, Theta_ref_SC_H, Theta_ref_SH_H)

    # (19)
    return e_dash_th_rtd_H


def calc_e_th_mid_H(V_fan_mid_H, q_hs_mid_H):
    """(20)

    :param V_fan_mid_H: 中間暖房能力運転時の送風機の風量（m3/h）
    :param q_hs_mid_H: 熱源機の中間暖房能力（W）
    :param alpha_c_hex_H: 暖房時の室内熱交換器表面の顕熱伝達率（W/(m2・K)）
    :return: 中間暖房能力運転時のヒートポンプサイクルサイクルの理論効率（-）
    """
    # (35)
    alpha_c_hex_H = get_alpha_c_hex_H(V_fan_mid_H)

    # (33)
    Theta_sur_f_hex_H = get_Theta_sur_f_hex_H_JIS(V_fan_mid_H, q_hs_mid_H, alpha_c_hex_H)

    # (23)
    Theta_ref_cnd_H = get_Theta_ref_cnd_H(Theta_sur_f_hex_H)

    # (24)
    Theta_ref_evp_H = get_Theta_ref_evp_H(7, Theta_ref_cnd_H)

     # (25)
    Theta_ref_SC_H = get_Theta_ref_SC_H(Theta_ref_cnd_H)

    # (26)
    Theta_ref_SH_H = get_Theta_ref_SH_H(Theta_ref_cnd_H)

    # 4_8_a (1) ヒートポンプサイクルの理論暖房効率
    e_dash_th_mid_H = calc_e_ref_H_th(Theta_ref_evp_H, Theta_ref_cnd_H, Theta_ref_SC_H, Theta_ref_SH_H)

    # (20)
    return e_dash_th_mid_H


def calc_e_th_rtd_C(V_fan_rtd_C, q_hs_rtd_C):
    """(21)

    :param V_fan_rtd_H: 定格冷房能力運転時の送風機の風量（m3/h）
    :param q_hs_rtd_H: 定格冷房能力（W）
    :return: 定格冷房能力運転時のヒートポンプサイクルサイクルの理論効率（-）
    """
    # 表5より
    X_hs_in = 0.010376
    # (36)
    alpha_c_hex_C, alpha_dash_c_hex_C = get_alpha_c_hex_C(V_fan_rtd_C, X_hs_in)

    # (34)
    def func(x):
        # 表5より
        q_hs_C = q_hs_rtd_C

        # 連立方程式を解くために(34a)の左辺を移項し、左辺を0にしておく
        return calc_Theta_sur_f_hex_C_JIS(x, V_fan_rtd_C, alpha_c_hex_C, alpha_dash_c_hex_C) - q_hs_C

    # x = fsolve(fun,x0) は、点 x0 を開始点として方程式 fun(x) = 0 (ゼロの配列) の解を求めようとする
    Theta_sur_f_hex_C = optimize.bisect(func, -273.15, 99.96)

    # (28)
    Theta_ref_evp_C = get_Theta_ref_evp_C(Theta_sur_f_hex_C)

    # (27)
    Theta_ref_cnd_C = get_Theta_ref_cnd_C(35, Theta_ref_evp_C)

    # (29)
    Theta_ref_SC_C = get_Theta_ref_SC_C(Theta_ref_cnd_C)

    # (30)
    Theta_ref_SH_C = get_Theta_ref_SH_C(Theta_ref_cnd_C)

    # 4_8_a (1) ヒートポンプサイクルの理論暖房効率
    e_dash_th_rtd_C = calc_e_ref_H_th(Theta_ref_evp_C, Theta_ref_cnd_C, Theta_ref_SC_C, Theta_ref_SH_C)

    # (21)
    return e_dash_th_rtd_C - 1


def calc_e_th_mid_C(V_fan_mid_C, q_hs_mid_C):
    """(22)

    :param V_fan_rtd_H: 定格冷房能力運転時の送風機の風量（m3/h）
    :param q_hs_rtd_H: 定格冷房能力（W）
    :return: 定格冷房能力運転時のヒートポンプサイクルサイクルの理論効率（-）
    """
    # 表5より
    X_hs_in = 0.010376
    # (36)
    alpha_c_hex_C, alpha_dash_c_hex_C = get_alpha_c_hex_C(V_fan_mid_C, X_hs_in)

    # (34)
    def func(x):
        # 表5より
        q_hs_C = q_hs_mid_C

        # 連立方程式を解くために(34a)の左辺を移項し、左辺を0にしておく
        return calc_Theta_sur_f_hex_C_JIS(x, V_fan_mid_C, alpha_c_hex_C, alpha_dash_c_hex_C) - q_hs_C

    # x = fsolve(fun,x0) は、点 x0 を開始点として方程式 fun(x) = 0 (ゼロの配列) の解を求めようとする
    Theta_sur_f_hex_C = optimize.bisect(func, -273.15, 99.96)

    # (28)
    Theta_ref_evp_C = get_Theta_ref_evp_C(Theta_sur_f_hex_C)

    # (27)
    Theta_ref_cnd_C = get_Theta_ref_cnd_C(35, Theta_ref_evp_C)

    # (29)
    Theta_ref_SC_C = get_Theta_ref_SC_C(Theta_ref_cnd_C)

    # (30)
    Theta_ref_SH_C = get_Theta_ref_SH_C(Theta_ref_cnd_C)

    # 4_8_a (1) ヒートポンプサイクルの理論暖房効率
    e_dash_th_mid_C = calc_e_ref_H_th(Theta_ref_evp_C, Theta_ref_cnd_C, Theta_ref_SC_C, Theta_ref_SH_C)

    # (22)
    return e_dash_th_mid_C - 1


# ============================================================================
# A.4.5 冷媒温度
# ============================================================================

def get_Theta_ref_cnd_H(Theta_sur_f_hex_H):
    """(23)

    :param Theta_sur_f_hex_H: 暖房時の室内機熱交換器の表面温度（℃）
    :return: 暖房時の冷媒の凝縮温度（℃）
    """
    Theta_ref_cnd_H = Theta_sur_f_hex_H

    if Theta_ref_cnd_H > 65:
        Theta_ref_cnd_H = 65

    return Theta_ref_cnd_H


def get_Theta_ref_evp_H(Theta_ex, Theta_ref_cnd_H):
    """(24)

    :param Theta_ex:外気温度（℃）
    :param Theta_ref_cnd_H:暖房時の冷媒の凝縮温度（℃）
    :return:暖房時の冷媒の蒸発温度（℃）
    """
    Theta_ref_evp_H = Theta_ex - (0.100 * Theta_ref_cnd_H + 2.95)

    if Theta_ref_evp_H < -50:
        Theta_ref_evp_H = -50

    if Theta_ref_evp_H > Theta_ref_cnd_H - 5.0:
        Theta_ref_evp_H = Theta_ref_cnd_H - 5.0

    return Theta_ref_evp_H


def get_Theta_ref_SC_H(Theta_ref_cnd_H):
    """(25)

    :param Theta_ref_cnd_H: 暖房時の冷媒の凝縮温度（℃）
    :return: 暖房時の冷媒の過冷却度（℃）
    """
    return 0.245 * Theta_ref_cnd_H - 1.72


def get_Theta_ref_SH_H(Theta_ref_cnd_H):
    """(26)

    :param Theta_ref_cnd_H: 暖房時の冷媒の凝縮温度（℃）
    :return: 暖房時の冷媒の過熱度（℃）
    """
    return 4.49 - 0.036 * Theta_ref_cnd_H


def get_Theta_ref_cnd_C(Theta_ex, Theta_ref_evp_C):
    """(27)

    :param Theta_ref_evp_C: 冷房時の冷媒の蒸発温度（℃）
    :return: 冷房時の冷媒の凝縮温度（℃）
    """
    Theta_ref_cnd_C = np.maximum(Theta_ex + 27.4 - 1.35 * Theta_ref_evp_C, Theta_ex)

    if Theta_ref_cnd_C > 65:
        Theta_ref_cnd_C = 65

    if Theta_ref_cnd_C < Theta_ref_evp_C + 5.0:
        Theta_ref_cnd_C = Theta_ref_evp_C + 5.0

    return Theta_ref_cnd_C


def get_Theta_ref_evp_C(Theta_sur_f_hex_C):
    """(28)

    :param Theta_sur_f_hex_C:冷房時の室内機熱交換器の表面温度（℃）
    :return:冷房時の冷媒の蒸発温度（℃）
    """
    Theta_ref_evp_C = Theta_sur_f_hex_C

    if Theta_ref_evp_C < -50:
        Theta_ref_evp_C = -50

    return Theta_ref_evp_C


def get_Theta_ref_SC_C(Theta_ref_cnd_C):
    """(29)

    :param Theta_ref_cnd_H: 暖房時の冷媒の凝縮温度（℃）
    :return: 冷房時の冷媒の過冷却度（℃）
    """
    return np.maximum(0.772 * Theta_ref_cnd_C - 25.6, 0)


def get_Theta_ref_SH_C(Theta_ref_cnd_C):
    """(30)

    :param Theta_ref_cnd_H: 暖房時の冷媒の凝縮温度（℃）
    :return: 冷房時の冷媒の過熱度（℃）
    """
    return np.maximum(0.194 * Theta_ref_cnd_C - 3.86, 0)


# ============================================================================
# A.5 室内機熱交換器
# ============================================================================

# ============================================================================
# A.5.1 熱交換器の表面温度
# ============================================================================

# ============================================================================
# A.5.1.1 エネルギー消費量の算定における熱交換器の表面温度
# ============================================================================

def get_Theta_sur_f_hex_H_calc(Theta_hs_in, Theta_hs_out, V_hs_supply, alpha_c_hex_H):
    """(31)

    :param Theta_hs_in: 熱源機の入口における空気温度（℃）
    :param Theta_hs_out: 熱源機の出口における空気温度（℃）
    :param V_hs_supply: 熱源機の風量（m3/h）
    :param alpha_c_hex_H: 暖房時の室内熱交換器表面の顕熱伝達率（W/(m2・K)）
    :return: エネルギー消費量の算定における熱交換器の表面温度を算定する場合の暖房時の室内機熱交換器の表面温度（℃）
    """
    c_p_air = get_c_p_air()
    rho_air = get_rho_air()
    A_e_hex = get_A_e_hex()

    Theta_sur_f_hex_H = ((Theta_hs_in + Theta_hs_out) / 2) \
                        + (c_p_air * rho_air * V_hs_supply * (Theta_hs_out - Theta_hs_in) / 3600) / (A_e_hex * alpha_c_hex_H)

    return Theta_sur_f_hex_H


def get_Theta_sur_f_hex_C_calc(Theta_hs_in, Theta_hs_out, V_hs_supply, alpha_c_hex_C):
    """(32)

    :param Theta_hs_in: 熱源機の入口における空気温度（℃）
    :param Theta_hs_out: 熱源機の出口における空気温度（℃）
    :param V_hs_supply: 熱源機の風量（m3/h）
    :param alpha_c_hex_C: 冷房時の室内熱交換器表面の顕熱伝達率（W/(m2・K)）
    :return: エネルギー消費量の算定における熱交換器の表面温度を算定する場合の冷房時の室内機熱交換器の表面温度（℃）
    """
    c_p_air = get_c_p_air()
    rho_air = get_rho_air()
    A_e_hex = get_A_e_hex()

    Theta_sur_f_hex_C = ((Theta_hs_in + Theta_hs_out) / 2) \
                        - (c_p_air * rho_air * V_hs_supply * (Theta_hs_in - Theta_hs_out) / 3600) / (A_e_hex * alpha_c_hex_C)

    return Theta_sur_f_hex_C


# ============================================================================
# A.5.1.2 JIS試験における熱交換器の表面温度
# ============================================================================

def get_Theta_sur_f_hex_H_JIS(V_fan_x_H, q_hs_X_H, alpha_c_hex_H):
    """(33)

    :param V_fan_x_H: 熱源機の風量（m3/h）※式(19)を算定する場合はV_fan_rtd_H、式(20)を算定する場合はV_fan_mid_H
    :param q_hs_X_H: 熱源機の暖房能力（W）※式(19)を算定する場合はq_hs_rtd_H、式(20)を算定する場合はq_hs_mid_H
    :param alpha_c_hex_H: 暖房時の室内機熱交換器の表面温度（℃）
    :return: JIS試験における熱交換器の表面温度を算定する場合の暖房時の室内機熱交換器の表面温度（℃）
    """
    # 表5より
    Theta_hs_in = 20
    V_hs_supply = V_fan_x_H
    q_hs_H = q_hs_X_H

    c_p_air = get_c_p_air()
    rho_air = get_rho_air()
    A_e_hex = get_A_e_hex()

    Theta_sur_f_hex_H_JIS = Theta_hs_in + (q_hs_H / (2 * c_p_air * rho_air * V_hs_supply)) * 3600 \
                            + (q_hs_H / (A_e_hex * alpha_c_hex_H))

    return Theta_sur_f_hex_H_JIS


def calc_Theta_sur_f_hex_C_JIS(Theta_surf_hex_C, V_fan_x_C, alpha_c_hex_C, alpha_dash_c_hex_C):
    """(34a)

    :param Theta_surf_hex_C:冷房時の室内機熱交換器の表面温度（℃）
    :param V_fan_x_C:熱源機の風量（m3/h）
    :param alpha_c_hex_C:冷房時の室内熱交換器表面の顕熱伝達率（W/(m2・K)）
    :param alpha_dash_c_hex_C:冷房時の室内熱交換器表面の潜熱伝達率（kg/(m2・s)）
    :return:冷房時の室内機熱交換器の表面温度（℃） ※連立方程式の解
    """
    # (34b)
    q_hs_CS = get_q_hs_CS(Theta_surf_hex_C, V_fan_x_C, alpha_c_hex_C)

    # (34c)
    q_hs_CL = get_q_hs_CL(Theta_surf_hex_C, V_fan_x_C, alpha_dash_c_hex_C)

    # (34a)
    return q_hs_CS + q_hs_CL


def get_q_hs_CS(Theta_surf_hex_C, V_fan_x_C, alpha_c_hex_C):
    """(34b)

    :param Theta_surf_hex_C: 冷房時の室内機熱交換器の表面温度（℃）
    :param V_fan_x_C: 熱源機の風量（m3/h）
    :param alpha_c_hex_C: 冷房時の室内熱交換器表面の顕熱伝達率（W/(m2・K)）
    :return: 熱源機の冷房顕熱能力（W）
    """
    # 表5より
    Theta_hs_in = 27
    V_hs_supply = V_fan_x_C

    c_p_air = get_c_p_air()
    rho_air = get_rho_air()
    A_e_hex = get_A_e_hex()

    return (Theta_hs_in - Theta_surf_hex_C) / (3600 / (2 * c_p_air * rho_air * V_hs_supply) + 1 / (A_e_hex * alpha_c_hex_C))


def get_q_hs_CL(Theta_surf_hex_C, V_fan_x_C, alpha_dash_c_hex_C):
    """(34c)

    :param Theta_surf_hex_C: 冷房時の室内機熱交換器の表面温度（℃）
    :param V_fan_x_C: 熱源機の風量（m3/h）
    :param alpha_dash_c_hex_C: 冷房時の室内熱交換器表面の潜熱伝達率（kg/(m2・s)）
    :return: 熱源機の冷房潜熱能力（W）
    """
    # 表5より
    X_hs_in = 0.010376
    V_hs_supply = V_fan_x_C

    L_wtr = get_L_wtr()
    rho_air = get_rho_air()
    A_e_hex = get_A_e_hex()

    # ------ここから第11章5節------

    Theta = Theta_surf_hex_C

    # 大気圧（Pa）
    F = 101325

    # 絶対温度（K）
    T = Theta + 273.16 #(6)

    # 表1 式(5b)における係数の値
    a1 = -6096.9385
    a2 = 21.2409642
    a3 = -0.02711193
    a4 = 0.00001673952
    a5 = 2.433502
    b1 = -6024.5282
    b2 = 29.32707
    b3 = 0.010613863
    b4 = -0.000013198825
    b5 = -0.49382577

    #(5b)
    if Theta > 0:
        k = a1 / T + a2 + a3 * T + a4 * T ** 2 + a5 * np.log(T)
    else:
        k = b1 / T + b2 + b3 * T + b4 * T ** 2 + b5 * np.log(T)

    # 飽和水蒸気圧（Pa）
    P_vs = np.exp(k) #(5a)

    # 飽和空気の絶対湿度（kg/kg(DA)）
    X_s = 0.622 * (P_vs / (F - P_vs)) #(3)

    # ------ここまで第11章5節------

    X_surf_hex_C = X_s

    # (34c)
    a = (X_hs_in - X_surf_hex_C) / (3600 / (2 * L_wtr * rho_air * V_hs_supply * 10 ** 3) \
                                    + 1 / (L_wtr * A_e_hex * alpha_dash_c_hex_C * 10 ** 3))
    return np.maximum(a, 0)


# ============================================================================
# A.5.2 熱交換器表面の顕熱伝達率
# ============================================================================

def get_alpha_c_hex_H(V_fan_x_H):
    """(35)

    :param V_fan_x_H:熱源機の風量（m3/h）
    :return:暖房時の室内熱交換器表面の顕熱伝達率（W/(m2・K)）
    """
    # 表5より
    V_hs_supply = V_fan_x_H

    A_f_hex = get_A_f_hex()

    alpha_c_hex_H = (-0.0017 * ((V_hs_supply / 3600) / A_f_hex) ** 2 \
                     + 0.044 * ((V_hs_supply / 3600) / A_f_hex) + 0.0271) * 10 ** 3

    return alpha_c_hex_H


def get_alpha_c_hex_C(V_fan_x_C, X_hs_in):
    """(36)

    :param V_fan_x_C:熱源機の風量（m3/h）
    :param X_hs_in:冷房時の熱源機の入口における絶対湿度（kg/kg(DA)）
    :return:冷房時の室内熱交換器表面の顕熱伝達率（W/(m2・K)）および 冷房時の室内熱交換器表面の潜熱伝達率（kg/(m2・s)）
    """
    # 表5より
    V_hs_supply = V_fan_x_C

    A_f_hex = get_A_f_hex()
    c_p_air = get_c_p_air()
    c_p_w = get_c_p_w()

    a = np.clip(V_hs_supply, 400, None)

    # (36b)
    alpha_dash_c_hex_C = 0.050 * np.log((a / 3600) / A_f_hex) + 0.073

    # (36a)
    alpha_c_hex_C = alpha_dash_c_hex_C * (c_p_air + c_p_w * X_hs_in)

    return alpha_c_hex_C, alpha_dash_c_hex_C


# ============================================================================
# A.5.3 熱交換器の表面積
# ============================================================================

# 室内機熱交換器の全面面積のうち熱交換に有効な面積 (m2)
def get_A_f_hex():
    return 0.23559


# 室内機熱交換器の表面積のうち熱交換に有効な面積 (m2)
def get_A_e_hex():
    return 6.396


# ============================================================================
# A.6 送風機
# ============================================================================

# ============================================================================
# A.6 送風機
# ============================================================================

def get_E_E_fan_H_d_t(P_fan_rtd_H, V_hs_vent_d_t, V_hs_supply_d_t, V_hs_dsgn_H, q_hs_H_d_t):
    """(37)

    :param P_fan_rtd_H:定格暖房能力運転時の送風機の消費電力（W）
    :param V_hs_vent_d_t:日付dの時刻tにおける熱源機の風量のうちの全般換気分（m3/h）
    :param V_hs_supply_d_t:
    :param V_hs_dsgn_H:暖房時の設計風量（m3/h）
    :param q_hs_H_d_t:日付dの時刻tにおける1時間当たりの熱源機の平均暖房能力（-）
    :return:日付dの時刻tにおける1時間当たりの送風機の消費電力量のうちの暖房設備への付加分（kWh/h）
    """
    f_SFP = get_f_SFP()
    E_E_fan_H_d_t = np.zeros(24 * 365)

    a = (P_fan_rtd_H - f_SFP * V_hs_vent_d_t) \
        * ((V_hs_supply_d_t - V_hs_vent_d_t) / (V_hs_dsgn_H - V_hs_vent_d_t)) * 10 ** (-3)

    E_E_fan_H_d_t[q_hs_H_d_t > 0] = np.clip(a[q_hs_H_d_t > 0], 0, None)

    return E_E_fan_H_d_t

def get_e_rtd_H():
    """定格暖房エネルギー消費効率
    
    :return: 定格暖房エネルギー消費効率
    :rtype: float
    """
    # 定格暖房エネルギー消費効率
    e_rtd_H = 3.76
    return e_rtd_H

def get_e_rtd_C():
    """定格冷房エネルギー消費効率
    
    :return: 定格冷房エネルギー消費効率
    :rtype: float
    """
    # 定格冷房エネルギー消費効率
    e_rtd_C = 3.17
    return e_rtd_C

def get_E_E_fan_C_d_t(P_fan_rtd_C, V_hs_vent_d_t, V_hs_supply_d_t, V_hs_dsgn_C, q_hs_C_d_t):
    """(38)

    :param P_fan_rtd_C:定格冷房能力運転時の送風機の消費電力（W）
    :param V_hs_vent_d_t:日付dの時刻tにおける熱源機の風量のうちの全般換気分（m3/h）
    :param V_hs_supply_d_t:
    :param V_hs_dsgn_C:冷房時の設計風量（m3/h）
    :param q_hs_C_d_t:日付dの時刻tにおける1時間当たりの熱源機の平均冷房能力（-）
    :return:日付dの時刻tにおける1時間当たりの送風機の消費電力量のうちの暖房設備への付加分（kWh/h）
    """
    f_SFP = get_f_SFP()
    E_E_fan_C_d_t = np.zeros(24 * 365)

    a = (P_fan_rtd_C - f_SFP * V_hs_vent_d_t) \
        * ((V_hs_supply_d_t - V_hs_vent_d_t) / (V_hs_dsgn_C - V_hs_vent_d_t)) * 10 ** (-3)

    E_E_fan_C_d_t[q_hs_C_d_t > 0] = np.clip(a[q_hs_C_d_t > 0], 0, None)

    return E_E_fan_C_d_t


# 全般換気設備の比消費電力（W/(m3/h)）
def get_f_SFP():
    return 0.4 * 0.36

# ============================================================================
# A.7 熱源機および送風機の仕様
# ============================================================================

# 付録Bで定義


# ============================================================================
# A.8 空気・水蒸気・水の物性値
# ============================================================================

# 空気の比熱 (J/Kg・K)
def get_c_p_air():
    return 1006.0


# 空気の密度 (kg/m3)
def get_rho_air():
    return 1.2


# 水蒸気の定圧比熱  (J/Kg・K)
def get_c_p_w():
    return 1.846


# 水の蒸発潜熱 (kJ/kg) (39)
def get_L_wtr():
    Theta = get_Theta()
    return 2500.8 - 2.3668 * Theta


# 冷房時を仮定した温度 (℃)
def get_Theta():
    return 27
