# ============================================================================
# 第四章 暖冷房設備
# 第八節 ルームエアコンディショナー付温水床暖房
# Ver.06（エネルギー消費性能計算プログラム（住宅版）Ver.02.01～）
# ============================================================================

import numpy as np
from math import sqrt

from pyhees.section4_1_Q import get_Q_T_H_d_t_i

# エアーコンディショナー
import pyhees.section4_3 as rac
import pyhees.section4_3_a as rac_spec

# 温水床暖房
import pyhees.section4_7_l as hwfloor

# R410A におけるヒートポンプサイクルの理論効率の計算方法
from pyhees.section4_8_a import calc_e_ref_H_th

# 地域の区分と外気条件
from pyhees.section11_1 import load_outdoor, get_Theta_ex, get_X_ex, calc_h_ex


# ============================================================================
# 5. 最大暖房能力
# ============================================================================

# 最大暖房出力 (1)
def calc_Q_max_H_d_t(region, Theta_SW_d_t, A_HCZ, r_Af):
    """最大暖房出力 (1)
    
    :param region: 省エネルギー地域区分
    :type region: int
    :param Theta_SW_d_t: 往き温水温度 (℃)
    :type Theta_SW_d_t: ndarray
    :param A_HCZ: ルームエアコンディショナー付温水床暖房を設置する暖冷房区画の面積 (m2)
    :type A_HCZ: float
    :param r_Af: 当該住戸における温水床暖房の敷設率 (-)
    :type r_Af: flloat
    :return: 最大暖房出力 (MJ/h)
    :rtype: ndarray
    """
    # 温水床暖房の最大暖房出力 (MJ/h)
    Q_max_H_floor_d_t = calc_Q_max_H_floor_d_t(Theta_SW_d_t, A_HCZ, r_Af)

    # ルームエアコンディショナーの最大暖房出力 (MJ/h)
    Q_max_H_RAC_d_t = calc_Q_max_H_RAC_d_t(region, A_HCZ)

    # ルームエアコンディショナー付温水床暖房の最大暖房出力 (MJ/h)
    Q_max_H_d_t = Q_max_H_floor_d_t + Q_max_H_RAC_d_t

    return Q_max_H_d_t


# 温水床暖房の最大暖房出力
def calc_Q_max_H_floor_d_t(Theta_SW_d_t, A_HCZ, r_Af):
    """温水床暖房の最大暖房出力
    
    :param Theta_SW_d_t: 往き温水温度 (℃)
    :type Theta_SW_d_t: ndarray
    :param A_HCZ: ルームエアコンディショナー付温水床暖房を設置する暖冷房区画の面積 (m2)
    :type A_HCZ: float
    :param r_Af: 当該住戸における温水床暖房の敷設率 (-)
    :type r_Af: float
    :return: 温水床暖房の最大暖房出力 (MJ/h)
    :rtype: ndarray
    """
    
    # 温水床暖房の敷設面積 (m2)
    A_f = hwfloor.get_A_f(A_HCZ, r_Af)

    # 温水床暖房の最大暖房出力 (MJ/h)
    Q_max_H_floor_d_t = hwfloor.get_Q_max_H_rad(Theta_SW_d_t, A_f)

    return Q_max_H_floor_d_t


# ルームエアコンディショナーの最大暖房出力
def calc_Q_max_H_RAC_d_t(region, A_HCZ):
    """ルームエアコンディショナーの最大暖房出力
    
    :param region: 省エネルギー地域区分
    :type region: int
    :param A_HCZ: ルームエアコンディショナー付温水床暖房を設置する暖冷房区画の面積 (m2)
    :type A_HCZ: float
    :return: ルームエアコンディショナーの最大暖房出力
    :rtype: ndarray
    """
    # 外気温度・湿度の取得
    outdoor = load_outdoor()
    Theta_ex_d_t = get_Theta_ex(region, outdoor)
    X_ex = get_X_ex(region, outdoor)
    h_ex = calc_h_ex(X_ex, Theta_ex_d_t)

    # 定格冷房能力
    q_rtd_C = rac_spec.get_q_rtd_C(A_HCZ)

    # 定格暖房能力
    q_rtd_H = rac_spec.get_q_rtd_H(q_rtd_C)

    # 最大冷房能力
    q_max_C = rac_spec.get_q_max_C(q_rtd_C)

    # 最大暖房能力
    q_max_H = rac_spec.get_q_max_H(q_rtd_H, q_max_C)

    # 最大暖房能力比
    q_r_max_H = rac.get_q_r_max_H(q_max_H, q_rtd_H)

    # 最大暖房出力比
    Q_r_max_H_d_t = rac.calc_Q_r_max_H_d_t(q_rtd_C, q_r_max_H, Theta_ex_d_t)

    # 最大暖房出力
    Q_max_H_RAC_d_t = rac.calc_Q_max_H_d_t(Q_r_max_H_d_t, q_rtd_H, Theta_ex_d_t, h_ex)

    return Q_max_H_RAC_d_t


# ============================================================================
# 6 暖房エネルギー消費量
# ============================================================================

# ============================================================================
# 6.1 消費電力量
# ============================================================================

# 1時間当たりの消費電力量 (2)
def calc_E_E_d_t(region, A_A_act, i, A_HCZ, r_Af, r_up, pipe_insulation, L_H_d_t):
    """1時間当たりの消費電力量 (2)

    :param region: 省エネルギー地域区分
    :type region: int
    :param A_A_act: 当該住戸における床面積の合計 (m2)
    :type A_A_act: float
    :param i: 暖冷房区画の番号
    :type i: int
    :param A_HCZ: ルームエアコンディショナー付温水床暖房を設置する暖冷房区画の面積 (m2)
    :type A_HCZ: float
    :param r_Af: 当該住戸における温水床暖房の敷設率 (-)
    :type r_Af: float
    :param r_up:  当該住戸の温水床暖房の上面放熱率
    :type r_up: float
    :param pipe_insulation: 配管断熱の有無
    :type pipe_insulation: bool
    :param L_H_d_t: 暖冷房区画݅の１時間当たりの暖房負荷
    :type L_H_d_t: ndarray
    :return: 1時間当たりの消費電力量
    :rtype: ndarray
    """
    # 往き温水温度
    Theta_SW_d_t = get_Theta_SW_d_t()

    # 最大暖房出力
    Q_max_H_d_t = calc_Q_max_H_d_t(region, Theta_SW_d_t, A_HCZ, r_Af)

    # 処理暖房負荷
    Q_T_H_d_t = get_Q_T_H_d_t_i(Q_max_H_d_t, L_H_d_t)

    # 1時間当たりの熱源機の消費電力量
    E_E_hs_d_t = calc_E_E_hs_d_t(region, A_A_act, i, A_HCZ, r_Af, r_up, pipe_insulation, Theta_SW_d_t, Q_T_H_d_t)

    return E_E_hs_d_t


def calc_Q_UT_H_d_t(region, A_HCZ, r_Af, L_H_d_t):
    """未処理暖房負荷
    
    :param region: 省エネルギー地域区分
    :type region: int
    :param A_HCZ: ルームエアコンディショナー付温水床暖房を設置する暖冷房区画の面積 (m2)
    :type A_HCZ: float
    :param r_Af: 当該住戸における温水床暖房の敷設率 (-)
    :type r_Af: float
    :param L_H_d_t: 暖冷房区画݅の１時間当たりの暖房負荷
    :type L_H_d_t: ndarray
    :return: 未処理暖房負荷
    :rtype: ndarray
    """
    # 往き温水温度
    Theta_SW_d_t = get_Theta_SW_d_t()

    # 最大暖房出力
    Q_max_H_d_t = calc_Q_max_H_d_t(region, Theta_SW_d_t, A_HCZ, r_Af)

    # 処理暖房負荷
    Q_T_H_d_t = get_Q_T_H_d_t_i(Q_max_H_d_t, L_H_d_t)

    return L_H_d_t - Q_T_H_d_t


# ============================================================================
# 6.2 ガス消費量
# ============================================================================

# 1時間当たりのガス消費量
def get_E_G_d_t():
    """1時間当たりのガス消費量
    
    :return: 1時間当たりのガス消費量
    :rtype: ndarray
    """
    # 1時間当たりのガス消費量は0とする
    return np.zeros(24 * 365)


# ============================================================================
# 6.3 灯油消費量
# ============================================================================

# 1時間当たりの灯油消費量
def get_E_K_d_t():
    """1時間当たりの灯油消費量
    
    :return: 1時間当たりの灯油消費量
    :rtype: ndarray
    """
    # 1時間当たりの灯油消費量は0とする
    return np.zeros(24 * 365)


# ============================================================================
# 6.4 その他の燃料による一次エネルギー消費量
# ============================================================================

# その他の燃料による一次エネルギー消費量
def get_E_M_d_t():
    """その他の燃料による一次エネルギー消費量
    
    :return: その他の燃料による一次エネルギー消費量
    :rtype: ndarray
    """
    # 1時間当たりのその他の燃料による一次エネルギー消費量は0とする
    return np.zeros(24 * 365)


# ============================================================================
# 7 熱源機
# ============================================================================

# ============================================================================
# 7.1 熱源機の消費電力量
# ============================================================================

# 1時間当たりの熱源機の消費電力量 (3)
def calc_E_E_hs_d_t(region, A_A_act, i, A_HCZ, r_Af, r_up, pipe_insulation, Theta_SW_d_t, Q_T_H_d_t):
    """熱源機の消費電力量
    
    :param region: 省エネルギー地域区分
    :type region: int
    :param A_A_act: 当該住戸における床面積の合計 (m2)
    :type A_A_act: float
    :param i: 暖冷房区画の番号
    :type i: int
    :param A_HCZ: ルームエアコンディショナー付温水床暖房を設置する暖冷房区画の面積 (m2)
    :type A_HCZ: float
    :param r_Af: 当該住戸における温水床暖房の敷設率 (-)
    :type r_Af: float
    :param r_up: 当該住戸の温水床暖房の上面放熱率
    :type r_up: float
    :param pipe_insulation: 配管断熱の有無
    :type pipe_insulation: bool
    :param Theta_SW_d_t: 往き温水温度(℃)
    :type Theta_SW_d_t: ndarray
    :param Q_T_H_d_t: 1時間当たりの処理暖房負荷 (MJ/h)
    :type Q_T_H_d_t: ndarray
    :return: 1時間当たりの熱源機の消費電力量 [kWh/h]
    :rtype: ndarray
    """
    # 未使用変数
    #:param Theta_ex_d_t: 外気温度(℃)
    #:param h_ex_d_t: 外気相対湿度

    # 外気温度湿度
    outdoor = load_outdoor()
    Theta_ex_d_t = get_Theta_ex(region, outdoor)
    X_ex = get_X_ex(region, outdoor)
    h_ex_d_t = calc_h_ex(X_ex, Theta_ex_d_t)

    # 温水床暖房の最大暖房出力
    Q_max_H_floor_d_t = calc_Q_max_H_floor_d_t(Theta_SW_d_t, A_HCZ, r_Af)

    # 温水床暖房の処理暖房負荷 (22)
    Q_T_H_FH_d_t = get_Q_T_H_FH_d_t(Q_T_H_d_t, Q_max_H_floor_d_t)

    # 1時間当たりの熱源機の温水床暖房の熱需要 (18)
    Q_dmd_H_hs_FH_d_t = calc_Q_dmd_H_hs_FH_d_t(i, A_A_act, r_up, pipe_insulation, Theta_SW_d_t, Theta_ex_d_t, Q_max_H_floor_d_t,
                                              Q_T_H_d_t)

    # 熱源機の最大暖房能力 (16)
    R_type = '主たる居室' if i == 1 else 'その他の居室'
    q_max_H_hs = calc_q_max_H_hs(region, A_HCZ, R_type)

    # 1時間当たりの熱源機のルームエアコンディショナー部の熱需要 (21)
    Q_dmd_H_hs_RAC_d_t = calc_Q_dmd_H_hs_RAC_d_t(Q_T_H_d_t, Q_T_H_FH_d_t)

    # 1時間当たりの熱源機の熱需要 (17)
    Q_dmd_H_hs_d_t = get_Q_dmd_H_hs_d_t(Q_dmd_H_hs_FH_d_t, Q_dmd_H_hs_RAC_d_t)

    # 1時間当たりの圧縮機の消費電力量 (4)
    E_comp_hs_d_t = calc_E_comp_hs_d_t(region, A_HCZ, r_Af, Theta_SW_d_t, q_max_H_hs, Q_dmd_H_hs_d_t, Q_T_H_d_t)

    # 熱源機の最大暖房出力 (15)
    Q_max_H_hs_d_t = get_Q_max_H_hs_d_t(Theta_ex_d_t, Theta_SW_d_t, q_max_H_hs, h_ex_d_t)

    # 1時間当たりの熱源機暖房出力 (14)
    Q_out_H_hs_d_t = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

    # 熱源機の平均暖房出力 (12)
    q_out_H_hs_d_t = get_q_out_H_hs_d_t(Q_out_H_hs_d_t)

    # 温水床暖房の最大暖房出力
    Q_max_H_floor_d_t = calc_Q_max_H_floor_d_t(Theta_SW_d_t, A_HCZ, r_Af)

    # 温水床暖房の処理暖房負荷 (22)
    Q_T_H_FH_d_t = get_Q_T_H_FH_d_t(Q_T_H_d_t, Q_max_H_floor_d_t)

    # 熱源機のルームエアコンディショナー部の熱需要 (21)
    Q_dmd_H_hs_RAC_d_t = calc_Q_dmd_H_hs_RAC_d_t(Q_T_H_d_t, Q_T_H_FH_d_t)

    # 1時間当たりの補器の消費電力量 (11)
    E_aux_hs_d_t = get_E_aux_hs_d_t(q_out_H_hs_d_t, Q_dmd_H_hs_RAC_d_t)

    # 1時間当たりの熱源機の未処理暖房負荷
    Q_UT_H_hs_d_t = get_Q_UT_H_hs_d_t(Q_dmd_H_hs_d_t, Q_out_H_hs_d_t)

    # 1時間当たりの熱源機の消費電力量 (3)
    E_E_hs_d_t = E_comp_hs_d_t + E_aux_hs_d_t + Q_UT_H_hs_d_t / 3600 * 1000

    # 熱源機の平均暖房出力が0に等しい場合は0
    E_E_hs_d_t[q_out_H_hs_d_t == 0] = 0

    return E_E_hs_d_t


# ============================================================================
# 7.2 圧縮機の消費電力量
# ============================================================================

# 1時間当たりの圧縮機の消費電力量 (4)
def calc_E_comp_hs_d_t(region, A_HCZ, r_Af, Theta_SW_d_t, q_max_H_hs, Q_dmd_H_hs_d_t, Q_T_H_d_t):
    """[summary]
    
    :param region: 省エネルギー地域区分
    :type region: int
    :param A_HCZ: ルームエアコンディショナー付温水床暖房を設置する暖冷房区画の面積 (m2)
    :type A_HCZ: float
    :param r_Af: 当該住戸における温水床暖房の敷設率 (-)
    :type r_Af: float
    :param Theta_SW_d_t: 往き温水温度(℃)
    :type Theta_SW_d_t: ndarray
    :param q_max_H_hs: 熱源機の最大暖房能力 (W/m2)
    :type q_max_H_hs: float
    :param Q_dmd_H_hs_d_t: 1時間当たりの熱源機の熱需要 (MJ/h)
    :type Q_dmd_H_hs_d_t: ndarray
    :param Q_T_H_d_t: 1時間当たりの処理暖房負荷 (MJ/h)
    :type Q_T_H_d_t: ndarray
    :return: 1時間当たりの圧縮機の消費電力量
    :rtype: ndarray
    """
    # 外気温度湿度を取得
    outdoor = load_outdoor()
    Theta_ex_d_t = get_Theta_ex(region, outdoor)
    X_ex = get_X_ex(region, outdoor)
    h_ex_d_t = calc_h_ex(X_ex, Theta_ex_d_t)

    # 熱源機の最大暖房出力 (15)
    Q_max_H_hs_d_t = get_Q_max_H_hs_d_t(Theta_ex_d_t, Theta_SW_d_t, q_max_H_hs, h_ex_d_t)

    # 1時間当たりの熱源機暖房出力 (14)
    Q_out_H_hs_d_t = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

    # 熱源機の平均暖房出力 (12)
    q_out_H_hs_d_t = get_q_out_H_hs_d_t(Q_out_H_hs_d_t)

    # 温水床暖房の最大暖房出力
    Q_max_H_floor_d_t = calc_Q_max_H_floor_d_t(Theta_SW_d_t, A_HCZ, r_Af)

    # 温水床暖房の処理暖房負荷 (22)
    Q_T_H_FH_d_t = get_Q_T_H_FH_d_t(Q_T_H_d_t, Q_max_H_floor_d_t)

    # 熱源機のルームエアコンディショナー部の熱需要 (21)
    Q_dmd_H_hs_RAC_d_t = calc_Q_dmd_H_hs_RAC_d_t(Q_T_H_d_t, Q_T_H_FH_d_t)

    # 熱源機内の平均放熱温度 (10)
    q_loss_H_hs_d_t = get_q_loss_H_hs_d_t(Theta_SW_d_t, Theta_ex_d_t, Q_dmd_H_hs_RAC_d_t)

    # ヒートポンプサイクルの過熱度 (9)
    Theta_ref_SH_d_t = get_Theta_ref_SH_d_t(q_out_H_hs_d_t, Theta_ex_d_t)

    # ヒートポンプサイクルの過冷温度 (8)
    Theta_ref_SC_d_t = get_Theta_ref_SC_d_t(Theta_SW_d_t, q_out_H_hs_d_t)

    # ヒートポンプサイクルの凝縮温度 (7)
    Theta_ref_cnd_d_t = get_Theta_ref_cnd_d_t(Theta_SW_d_t, q_out_H_hs_d_t)

    # ヒートポンプサイクルの蒸発温度 (6)
    Theta_ref_evp_d_t = get_Theta_ref_evp_d_t(q_out_H_hs_d_t, Theta_ex_d_t, h_ex_d_t)

    # 圧縮機の圧縮効率 (5)
    etr_d_t = get_etr_d_t(q_out_H_hs_d_t, q_max_H_hs)

    # ヒートポンプサイクルの理論暖房効率 付録A (1)
    e_ref_H_th_d_t = calc_e_ref_H_th(Theta_ref_evp_d_t, Theta_ref_cnd_d_t, Theta_ref_SC_d_t, Theta_ref_SH_d_t)

    # ただし、10を超える場合は10
    e_ref_H_th_d_t[e_ref_H_th_d_t > 10] = 10

    # 1時間当たりの圧縮機の消費電力量 (4)
    C_df_H_d_t = get_C_df_H_d_t(Theta_ex_d_t, h_ex_d_t)
    E_com_hs_d_t = (q_out_H_hs_d_t + q_loss_H_hs_d_t) / (etr_d_t * C_df_H_d_t * e_ref_H_th_d_t)

    # ヒートポンプサイクルの蒸発温度が凝縮温度以上の場合は0
    E_com_hs_d_t[Theta_ref_evp_d_t >= Theta_ref_cnd_d_t] = 0

    return E_com_hs_d_t


# デフロストに関する暖房出力補正係数
def get_C_df_H_d_t(Theta_ex_d_t, h_ex_d_t):
    """デフロストに関する暖房出力補正係数
    
    :param Theta_ex_d_t: 外気温度(℃)
    :type Theta_ex_d_t: ndarray
    :param h_ex_d_t: 外気相対湿度
    :type h_ex_d_t: ndarray
    :return: デフロストに関する暖房出力補正係数
    :rtype: ndarray
    """
    C_df_H_d_t = np.ones(24 * 365)
    C_df_H_d_t[(Theta_ex_d_t < 5.0) * (h_ex_d_t >= 80.0)] = 0.85
    return C_df_H_d_t


# 圧縮機の圧縮効率 (5)
def get_etr_d_t(q_out_H_hs_d_t, q_max_H_hs):
    """圧縮機の圧縮効率 (5)
    
    :param q_out_H_hs_d_t: 熱源機の平均暖房出力 (kW)
    :type q_out_H_hs_d_t: ndarray
    :param q_max_H_hs: 熱源機の最大暖房出力 (W)
    :type q_max_H_hs: float
    :return: 圧縮機の圧縮効率
    :rtype: float
    """
    tmp = (q_out_H_hs_d_t * 1000 / q_max_H_hs)
    return -0.9645 * tmp * tmp \
           + 1.245 * tmp \
           + 0.347


# ヒートポンプサイクルの蒸発温度 (6)
def get_Theta_ref_evp_d_t(q_out_H_hs_d_t, Theta_ex_d_t, h_ex_d_t):
    """ヒートポンプサイクルの蒸発温度 (6)
    
    :param q_out_H_hs_d_t: 熱源機の平均暖房出力 (kW)
    :type q_out_H_hs_d_t: ndarray
    :param Theta_ex_d_t: 外気温度(℃)
    :type Theta_ex_d_t: ndarray
    :param h_ex_d_t: 外気相対湿度
    :type h_ex_d_t: ndarray
    :return: ヒートポンプサイクルの蒸発温度
    :rtype: ndarray
    """
    Theta_ref_evp_d_t = -1.043 * q_out_H_hs_d_t + 1.008 * Theta_ex_d_t + 0.032 * h_ex_d_t - 4.309

    # Theta_ref_evp_d_t < -50 のときは Theta_ref_evp_d_t = -50 とする
    return np.clip(Theta_ref_evp_d_t, -50, None)


# ヒートポンプサイクルの凝縮温度 (7)
def get_Theta_ref_cnd_d_t(Theta_SW_d_t, q_out_H_hs_d_t):
    """ヒートポンプサイクルの凝縮温度 (7)
    
    :param Theta_SW_d_t: 往き温水温度(℃)
    :type Theta_SW_d_t: ndarray
    :param q_out_H_hs_d_t: 熱源機の平均暖房出力 (kW)
    :type q_out_H_hs_d_t: ndarray
    :return: ヒートポンプサイクルの凝縮温度
    :rtype: ndarray
    """
    Theta_ref_cnd_d_t = 0.961 * Theta_SW_d_t + 0.409 * q_out_H_hs_d_t + 3.301

    # Theta_ref_cnd_d_t > 65 のときは Theta_ref_cnd_d_t = 65 とする
    ## C#に合わせて 60上限とする
    return np.clip(Theta_ref_cnd_d_t, None, 60)


# ヒートポンプサイクルの過冷温度 (8)
def get_Theta_ref_SC_d_t(Theta_SW_d_t, q_out_H_hs_d_t):
    """ヒートポンプサイクルの過冷温度 (8)
    
    :param Theta_SW_d_t:  往き温水温度(℃)
    :type Theta_SW_d_t: ndarray
    :param q_out_H_hs_d_t: 熱源機の平均暖房出力 (kW)
    :type q_out_H_hs_d_t: ndarray
    :return: ヒートポンプサイクルの過冷温度
    :rtype: ndarray
    """
    Theta_ref_SC_d_t = -0.101 * Theta_SW_d_t - 0.180 * q_out_H_hs_d_t + 7.162

    # Theta_ref_SC_d_t < 0 のときは Theta_ref_SC_d_t = 0 とする
    return np.clip(Theta_ref_SC_d_t, 0, None)


# ヒートポンプサイクルの過熱度 (9)
def get_Theta_ref_SH_d_t(q_out_H_hs_d_t, Theta_ex_d_t):
    """ヒートポンプサイクルの過熱度 (9)
    
    :param q_out_H_hs_d_t: 熱源機の平均暖房出力 (kW)
    :type q_out_H_hs_d_t: ndarray
    :param Theta_ex_d_t: 外気温度(℃)
    :type Theta_ex_d_t: ndarray
    :return: ヒートポンプサイクルの過熱度
    :rtype: ndarray
    """
    Theta_ref_SH_d_t = -0.187 * q_out_H_hs_d_t + 0.142 * Theta_ex_d_t + 1.873

    # Theta_ref_SH_d_t < 0 のときは Theta_ref_SH_d_t = 0 とする
    return np.clip(Theta_ref_SH_d_t, 0, None)


# 熱源機内の平均放熱温度 (10)
def get_q_loss_H_hs_d_t(Theta_SW_d_t, Theta_ex_d_t, Q_dmd_H_hs_RAC_d_t):
    """ 熱源機内の平均放熱温度 (10)
    
    :param Theta_SW_d_t: 往き温水温度(℃)
    :type Theta_SW_d_t: ndarray
    :param Theta_ex_d_t: 外気温度(℃)
    :type Theta_ex_d_t: ndarray
    :param Q_dmd_H_hs_RAC_d_t: 1時間当たりの熱源機のルームエアコンディショナー部の熱需要 (MJ/h)
    :type Q_dmd_H_hs_RAC_d_t: ndarray
    :return:  熱源機内の平均放熱温度
    :rtype: ndarray
    """
    # q_loss_H_hs_d_t が0を下回る場合は 0
    q_loss_H_hs_d_t = np.zeros(24 * 365)

    # Q_dmd_H_hs_RAC_d_t = 0 の場合
    f1 = Q_dmd_H_hs_RAC_d_t == 0
    q_loss_H_hs_d_t[f1] = 0.004 * (Theta_SW_d_t[f1] - Theta_ex_d_t[f1])

    # Q_dmd_H_hs_RAC_d_t > 0 の場合
    f2 = Q_dmd_H_hs_RAC_d_t > 0
    q_loss_H_hs_d_t[f2] = 0.010 * (Theta_SW_d_t[f2] - Theta_ex_d_t[f2])

    return q_loss_H_hs_d_t


# ============================================================================
# 7.3 補機の消費電力量 (11)
# ============================================================================

# 1時間当たりの補機の消費電力量 (11)
def get_E_aux_hs_d_t(q_out_H_hs_d_t, Q_dmd_H_hs_RAC_d_t):
    """1時間当たりの補機の消費電力量 (11)
    
    :param q_out_H_hs_d_t:  熱源機の平均暖房出力 (kW)
    :type q_out_H_hs_d_t: ndarray
    :param Q_dmd_H_hs_RAC_d_t: 1時間当たりの熱源機のルームエアコンディショナー部の熱需要 (MJ/h)
    :type Q_dmd_H_hs_RAC_d_t: ndarray
    :return: 1時間当たりの補機の消費電力量 (kWh/h)
    :rtype: ndarray
    """
    E_aux_hs_d_t = np.zeros(24 * 365)

    # Q_dmd_H_hs_RAC_d_t = 0 の場合
    f1 = Q_dmd_H_hs_RAC_d_t == 0
    E_aux_hs_d_t[f1] = 0.034 * q_out_H_hs_d_t[f1] + 0.123

    # Q_dmd_H_hs_RAC_d_t > 0 の場合
    f2 = Q_dmd_H_hs_RAC_d_t > 0
    E_aux_hs_d_t[f2] = 0.020 * q_out_H_hs_d_t[f2] + 0.132

    return E_aux_hs_d_t


# ============================================================================
# 7.4 熱源機の暖房出力と未処理暖房負荷
# ============================================================================

# 熱源機の平均暖房出力 (12)
def get_q_out_H_hs_d_t(Q_out_H_hs_d_t):
    """熱源機の平均暖房出力 (12)
    
    :param Q_out_H_hs_d_t: 1時間当たりの熱源機暖房出力 (MJ/h)
    :type Q_out_H_hs_d_t: ndarray
    :return: 熱源機の平均暖房出力 (kW)
    :rtype: ndarray
    """
    return Q_out_H_hs_d_t / 3600 * 10 ** 3


# 1時間当たりの熱源機の未処理暖房負荷 (13)
def get_Q_UT_H_hs_d_t(Q_dmd_H_hs_d_t, Q_out_H_hs_d_t):
    """1時間当たりの熱源機の未処理暖房負荷 (13)
    
    :param Q_dmd_H_hs_d_t:  1時間当たりの熱源機の熱需要 (MJ/h)
    :type Q_dmd_H_hs_d_t: ndarray
    :param Q_out_H_hs_d_t: 1時間当たりの熱源機暖房出力 (MJ/h)
    :type Q_out_H_hs_d_t: ndarray
    :return: 1時間当たりの熱源機の未処理暖房負荷 (MJ/h)
    :rtype: ndarray
    """
    return Q_dmd_H_hs_d_t - Q_out_H_hs_d_t


# 1時間当たりの熱源機暖房出力 (14)
def get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t):
    """1時間当たりの熱源機暖房出力 (14)
    
    :param Q_dmd_H_hs_d_t: 1時間当たりの熱源機の熱需要 (MJ/h)
    :type Q_dmd_H_hs_d_t: ndarray
    :param Q_max_H_hs_d_t: 1時間当たりの熱源機の最大暖房出力 (MJ/h)
    :type Q_max_H_hs_d_t: ndarray
    :return: 1時間当たりの熱源機暖房出力 (MJ/h)
    :rtype: ndarray
    """
    Q_out_H_hs_d_t = np.zeros(24 * 365)

    # Q_dmd_H_hs_dt <= Q_max_H_hs_d_t の場合
    f1 = Q_dmd_H_hs_d_t <= Q_max_H_hs_d_t
    Q_out_H_hs_d_t[f1] = Q_dmd_H_hs_d_t[f1]

    # Q_dmd_H_hs_dt > Q_max_H_hs_d_t の場合
    f2 = Q_dmd_H_hs_d_t > Q_max_H_hs_d_t
    Q_out_H_hs_d_t[f2] = Q_max_H_hs_d_t[f2]

    return Q_out_H_hs_d_t


# 熱源機の最大暖房出力 (15)
def get_Q_max_H_hs_d_t(Theta_ex_d_t, Theta_SW_d_t, q_max_H_hs, h_ex_d_t):
    """熱源機の最大暖房出力 (15)
    
    :param Theta_ex_d_t: 外気温度 (℃)
    :type Theta_ex_d_t: ndarray
    :param Theta_SW_d_t: 往き温水温度 (℃)
    :type Theta_SW_d_t: ndarray
    :param q_max_H_hs: 熱源機の最大暖房出力 (W)
    :type q_max_H_hs: float
    :param h_ex_d_t: 外気相対湿度
    :type h_ex_d_t: ndarray
    :return: 熱源機の最大暖房出力 (MJ/h)
    :rtype: ndarray
    """
    # デフロストに関する暖房出力補正係数
    # ※ (15)式の直下に書かれており、(4)式のそれと被るため、あえてここに記述します。
    C_df_H_d_t = np.ones(24 * 365)
    C_df_H_d_t[np.logical_and(Theta_ex_d_t < 5, h_ex_d_t >= 80.0)] = 0.85

    # 熱源機の最大暖房出力
    Q_max_H_hs_d_t = (11.62 + 0.2781 * Theta_ex_d_t - 0.00113 * Theta_ex_d_t ** 2 - 0.1271 * Theta_SW_d_t
                      - 0.00363 * Theta_ex_d_t * Theta_SW_d_t) * (q_max_H_hs * 0.8 / 6) * \
                     (C_df_H_d_t / 0.85) * 3600 / 10 ** 6

    return Q_max_H_hs_d_t


# 熱源機の最大暖房能力 (16)
def calc_q_max_H_hs(region, A_HCZ, R_type):
    """熱源機の最大暖房能力 (16)
    
    :param region: 省エネルギー地域区分
    :type region: int
    :param A_HCZ: 暖冷房区画の床面積 (m2)
    :type A_HCZ: float
    :param R_type: 暖冷房区画の種類
    :type R_type: string
    :return: 熱源機の最大暖房能力 (W/m2)
    :rtype: float
    """
    # 単位面積当たりの必要暖房能力 (W/m2)
    q_rq_H = calc_q_rq_H(region, R_type)

    # 外気温度能力補正係数
    f_cT = get_f_cT()

    # 間歇運転能力補正係数
    f_cI = get_f_cI(R_type)

    return q_rq_H * A_HCZ * f_cT * f_cI


# 単位面積当たりの必要暖房能力
def calc_q_rq_H(region, R_type):
    """単位面積当たりの必要暖房能力
    :param region: 省エネルギー地域区分
    :type region: int
    :param R_type: 暖冷房区画の種類
    :type R_type: string
    :raises ValueError: R_type が '主たる居室' または 'その他の居室' 以外の場合に発生する
    :return: 単位面積当たりの必要暖房能力
    :rtype: float
    """
    table_3 = get_table_3()
    if R_type == '主たる居室':
        return table_3[region - 1][0]
    elif R_type == 'その他の居室':
        return table_3[region - 1][1]
    else:
        raise ValueError(R_type)


# 外気温度能力補正係数
def get_f_cT():
    """外気温度能力補正係数
    
    :return: 外気温度能力補正係数
    :rtype: float
    """
    return 1.05


# 間歇運転能力補正係数
def get_f_cI(R_type):
    """[summary]
    
    :param R_type: 暖冷房区画の種類
    :type R_type: string
    :raises NotImplementedError:  R_type が '主たる居室' または 'その他の居室' 以外の場合に発生する
    :return: 間歇運転能力補正係数
    :rtype: float
    """
    if R_type == '主たる居室':
        return 3.03
    elif R_type == 'その他の居室':
        return 1.62
    else:
        raise NotImplementedError()


# 表3 単位面積当たりの必要暖房能力 (W/m2)
def get_table_3():
    """表3 単位面積当たりの必要暖房能力 (W/m2)
    
    :return: 表3 単位面積当たりの必要暖房能力 (W/m2)
    :rtype: list
    """
    table_3 = [
        (139.26, 62.28),
        (120.65, 53.26),
        (111.32, 53.81),
        (118.98, 55.41),
        (126.56, 59.43),
        (106.48, 49.93),
        (112.91, 53.48),
        (None, None)
    ]
    return table_3


# ============================================================================
# 7.5 熱源機の熱需要
# ============================================================================

# ============================================================================
# 7.5.1 熱源機の熱需要
# ============================================================================

# 1時間当たりの熱源機の熱需要 (17)
def get_Q_dmd_H_hs_d_t(Q_dmd_H_hs_FH_d_t, Q_dmd_H_hs_RAC_d_t):
    """[summary]
    
    :param Q_dmd_H_hs_FH_d_t: 1時間当たりの熱源機の温水床暖房部の熱需要
    :type Q_dmd_H_hs_FH_d_t: ndarray
    :param Q_dmd_H_hs_RAC_d_t: 1時間当たりの熱源機のルームエアコンディショナー部の熱需要 (MJ/h)
    :type Q_dmd_H_hs_RAC_d_t: ndarray
    :return: 1時間当たりの熱源機の熱需要 (17)
    :rtype: ndarray
    """
    # 1時間当たりの熱源機の熱需要
    Q_dmd_H_hs_d_t = Q_dmd_H_hs_FH_d_t + Q_dmd_H_hs_RAC_d_t

    return Q_dmd_H_hs_d_t


# ============================================================================
# 7.5.2 熱源機の温水床暖房部の熱需要
# ============================================================================

# 1時間当たりの熱源機の温水床暖房部の熱需要 (18)
def calc_Q_dmd_H_hs_FH_d_t(i, A_A_act, r_up, has_pipe, Theta_SW_d_t, Theta_ex_d_t, Q_max_H_floor_d_t,
                          Q_T_H_d_t):
    """1時間当たりの熱源機の温水床暖房部の熱需要 (18)
    
    :param i: 暖冷房区画の番号
    :type i: int
    :param A_A_act: 当該住戸における床面積の合計 (m2)
    :type A_A_act: float
    :param r_up: 当該住戸の温水床暖房の上面放熱率
    :type r_up: float
    :param has_pipe: 配管断熱の有無
    :type has_pipe: bool
    :param Theta_SW_d_t: 往き温水温度(℃)
    :type Theta_SW_d_t: ndarray
    :param Theta_ex_d_t: 外気温度(℃)
    :type Theta_ex_d_t: ndarray
    :param Q_max_H_floor_d_t: 1時間当たりの温水床暖房の最大暖房出力 (MJ/h)
    :type Q_max_H_floor_d_t: ndarray
    :param Q_T_H_d_t: 1時間当たりの処理暖房負荷 (MJ/h)
    :type Q_T_H_d_t: ndarray
    :return: 1時間当たりの熱源機の温水床暖房部の熱需要 (MJ/h)
    :rtype: ndarray
    """
    L_pp_ex = calc_L_pp_ex(i, A_A_act)

    # 配管の断熱区間内における長さ (20b)
    L_pp_in = calc_L_pp_in(i, A_A_act)

    # 1時間当たりの温水床暖房の処理暖房負荷
    Q_T_H_FH_d_t = get_Q_T_H_FH_d_t(Q_T_H_d_t, Q_max_H_floor_d_t)

    # 温水床暖房の温水供給運転率
    r_WS_rad_d_t = calc_r_WS_rad_d_t(Q_T_H_FH_d_t, Q_max_H_floor_d_t)

    # 1時間当たりの配管の放熱損失 (19)
    Q_loss_pp_d_t = calc_Q_loss_pp_d_t(Theta_SW_d_t, Theta_ex_d_t, L_pp_ex, L_pp_in, has_pipe, r_WS_rad_d_t)

    # 1時間当たりの温水床暖房の放熱損失
    Q_loss_FH_d_t = calc_Q_loss_FH_d_t(Q_T_H_FH_d_t, r_up)

    # 1時間当たりの熱源機の温水床暖房部の熱需要 (18)
    Q_dmd_H_hs_FH_d_t = Q_T_H_FH_d_t + Q_loss_FH_d_t + Q_loss_pp_d_t

    return Q_dmd_H_hs_FH_d_t


# 配管の熱損失 (19)
def calc_Q_loss_pp_d_t(Theta_SW_d_t, Theta_ex_d_t, L_pp_ex, L_pp_in, has_pipe, r_WS_rad_d_t):
    """配管の熱損失 (19)
    
    :param Theta_SW_d_t: 往き温水温度(℃)
    :type Theta_SW_d_t: ndarray
    :param Theta_ex_d_t: 外気温度(℃)
    :type Theta_ex_d_t: ndarray
    :param L_pp_ex: 配管の断熱区間外における長さ(m)
    :type L_pp_ex: float
    :param L_pp_in: 配管の断熱区間内における長さ(m)
    :type L_pp_in: float
    :param has_pipe: 配管断熱の有無
    :type has_pipe: bool
    :param r_WS_rad_d_t: 温水床暖房の温水供給運転率
    :type r_WS_rad_d_t: ndarray
    :return: 1時間当たりの配管の放熱損失
    :rtype: ndarray
    """
    # 配管の線熱損失係数 (W/mK)
    K_loss_pp = get_K_loss_pp(has_pipe)

    return ((Theta_SW_d_t - (Theta_ex_d_t * 0.7 + 20 * 0.3)) * L_pp_ex + (
            Theta_SW_d_t - 20) * L_pp_in) * K_loss_pp * r_WS_rad_d_t * 3600 / 1000000


# 配管の断熱区画外における長さ (20a)
def calc_L_pp_ex(i, A_A_act):
    """配管の断熱区画外における長さ (20a)
    
    :param i: 暖冷房区画の番号
    :type i: int
    :param A_A_act: 当該住戸における床面積の合計(m2)
    :type A_A_act: float
    :return: 配管の断熱区画外における長さ(m)
    :rtype: float
    """

    # 暖冷房区画ごとに表4に表される係数
    L_pp_ex_R = get_L_pp_ex_R(i)

    # 標準住戸における床面積の合計
    A_A_R = get_A_A_R()

    # 配管の断熱区画外における長さ
    L_pp_ex = L_pp_ex_R * sqrt(A_A_act / A_A_R)

    return L_pp_ex


# 配管の断熱区間内における長さ (20b)
def calc_L_pp_in(i, A_A_act):
    """配管の断熱区間内における長さ (20b)
    
    :param i: 暖冷房区画の番号
    :type i: int
    :param A_A_act: 当該住戸における床面積の合計(m2)
    :type A_A_act: float
    :return: 配管の断熱区画内における長さ(m)
    :rtype: float
    """

    # 暖冷房区画ごとに表4に表される係数
    L_pp_in_R = get_L_pp_in_R(i)

    # 標準住戸における床面積の合計
    A_A_R = get_A_A_R()

    # 配管の断熱区画内における長さ
    L_pp_in = L_pp_in_R * sqrt(A_A_act / A_A_R)

    return L_pp_in


# 暖冷房区画ごとに表4に表される係数 L_pp_ex_R
def get_L_pp_ex_R(i):
    """暖冷房区画ごとに表4に表される係数 L_pp_ex_R
    
    :param i: 暖冷房区画の番号
    :type i: int
    :return: 暖冷房区画ごとに表4に表される係数
    :rtype: float
    """
    table_4 = get_table_4()
    if i == 1:
        return table_4[0][0]
    elif i in [3, 4, 5]:
        return table_4[0][i - 2]
    else:
        ValueError(i)


# 暖冷房区画ごとに表4に表される係数 L_pp_in_R
def get_L_pp_in_R(i):
    """暖冷房区画ごとに表4に表される係数 L_pp_in_R
    
    :param i: 暖冷房区画の番号
    :type i: int
    :return: 暖冷房区画ごとに表4に表される係数
    :rtype: float
    """
    table_4 = get_table_4()
    if i == 1:
        return table_4[1][0]
    elif i in [3, 4, 5]:
        return table_4[1][i - 2]
    else:
        ValueError(i)


# 標準住戸における床面積の合計
def get_A_A_R():
    """標準住戸における床面積の合計
    
    :return: 標準住戸における床面積の合計(m2)
    :rtype: float
    """
    return 120.08


def get_table_4():
    """表4 係数L_pp_ex_R及びL_pp_in_R
    
    :return: 表4 係数L_pp_ex_R及びL_pp_in_R
    :rtype: list
    """
    # 表4 係数L_pp_ex_R及びL_pp_in_R
    table_4 = [
        (27.86, 0.00, 0.00, 0.00),
        (0.00, 16.54, 12.90, 20.30)
    ]
    return table_4


# 配管の線熱損失係数
def get_K_loss_pp(has_pipe):
    """配管の線熱損失係数
    
    :param has_pipe: 配管の断熱の有無
    :type has_pipe: bool
    :return: 配管の線熱損失係数 (W/mK)
    :rtype: float
    """
    if has_pipe:
        return 0.15
    else:
        return 0.21


# 温水床暖房の温水供給運転率
def calc_r_WS_rad_d_t(Q_T_H_FH_d_t, Q_max_H_floor_d_t):
    """温水床暖房の温水供給運転率
    
    :param Q_T_H_FH_d_t: 温水床暖房の処理暖房負荷 [MJ/h]
    :type Q_T_H_FH_d_t: ndarray
    :param Q_max_H_floor_d_t: 温水床暖房の最大暖房出力
    :type Q_max_H_floor_d_t: ndarray
    :return: 温水床暖房の温水供給運転率
    :rtype: ndarray
    """
    return hwfloor.get_r_WS_rad(
        Q_T_H_rad=Q_T_H_FH_d_t,
        Q_max_H_rad=Q_max_H_floor_d_t
    )


# 温水床暖房の放熱損失
def calc_Q_loss_FH_d_t(Q_T_H_FH_d_t, r_up):
    """温水床暖房の放熱損失
    
    :param Q_T_H_FH_d_t: 温水暖房の処理暖房負荷 [MJ/h]
    :type Q_T_H_FH_d_t: ndarray
    :param r_up: 当該住戸の温水床暖房の上面放熱率 [-]
    :type r_up: ndarray
    :return: 温水床暖房の放熱損失
    :rtype: ndarray
    """
    return hwfloor.get_Q_loss_rad(Q_T_H_rad=Q_T_H_FH_d_t, r_up=r_up)


# ============================================================================
# 7.5.3 熱源機のルームエアコンディショナー部の熱需要
# ============================================================================

# 熱源機のルームエアコンディショナー部の熱需要 (21)
def calc_Q_dmd_H_hs_RAC_d_t(Q_T_H_d_t, Q_T_H_FH_d_t):
    """熱源機のルームエアコンディショナー部の熱需要 (21)

    :param Q_T_H_d_t: 1時間当たりの処理暖房負荷 (MJ/h)
    :type Q_T_H_d_t: ndarray    
    :param Q_T_H_FH_d_t: 1時間当たりの温水床暖房の処理暖房負荷 (MJ/h)
    :type Q_T_H_FH_d_t: ndarray
    :return: 熱源機のルームエアコンディショナー部の熱需要 (MJ/h)
    :rtype: ndarray
    """
    return get_Q_T_H_RAC_d_t(Q_T_H_d_t, Q_T_H_FH_d_t)


# ============================================================================
# 7.6 処理暖房負荷
# ============================================================================

# 
def get_Q_T_H_FH_d_t(Q_T_H_d_t, Q_max_H_floor_d_t):
    """温水床暖房の処理暖房負荷 (22)
    
    :param Q_T_H_d_t: 1時間当たりの処理暖房負荷 (MJ/h)
    :type Q_T_H_d_t: ndarray
    :param Q_max_H_floor_d_t: 1時間当たりの温水床暖房の最大暖房出力 (MJ/h)
    :type Q_max_H_floor_d_t: ndarray
    :return: 温水床暖房の処理暖房負荷 (MJ/h)
    :rtype: ndarray
    """

    Q_T_H_FH_d_t = np.zeros(24*365)

    f1 = Q_T_H_d_t <= Q_max_H_floor_d_t
    Q_T_H_FH_d_t[f1] = Q_T_H_d_t[f1]

    f2 = Q_T_H_d_t > Q_max_H_floor_d_t
    Q_T_H_FH_d_t[f2] = Q_max_H_floor_d_t[f2]

    return Q_T_H_FH_d_t



# ルームエアコンディショナーの処理暖房負荷 (23)
def get_Q_T_H_RAC_d_t(Q_T_H_d_t, Q_T_H_FH_d_t):
    """ルームエアコンディショナーの処理暖房負荷 (23)
    
    :param Q_T_H_d_t: 1時間当たりの処理暖房負荷 (MJ/h)
    :type Q_T_H_d_t: ndarray
    :param Q_T_H_FH_d_t: 1時間当たりの温水床暖房の処理暖房負荷 (MJ/h)
    :type Q_T_H_FH_d_t: ndarray
    :return: 1時間当たりのルームエアコンディショナーの処理暖房負荷 (MJ/h)
    :rtype: ndarray
    """
    return Q_T_H_d_t - Q_T_H_FH_d_t


# ============================================================================
# 7.7 往き温水温度
# ============================================================================

# 往き温水温度 (℃)
def get_Theta_SW_d_t():
    """往き温水温度 (℃)
    
    :return: 往き温水温度 (℃)
    :rtype: ndarray
    """
    return 36.0 * np.ones(24 * 365)


# ============================================================================
# 8 冷房
# ============================================================================

# ルームエアコンディショナー付温水床暖房における冷房時のエネルギー所肥料及び最大冷房出力については、
# ルームエアコンディショナーの冷房と同じ。

# 消費電力量
def calc_E_E_C_d_t(region, outdoor, q_rtd_C, e_rtd_C, L_CS_d_t, L_CL_d_t):
    """消費電力量
    ルームエアコンディショナー付温水床暖房における冷房時のエネルギー所肥料及び最大冷房出力については、
    ルームエアコンディショナーの冷房と同じ。
    
    :param region: 省エネルギー地域区分
    :type region: int
    :param outdoor: 気温[℃],絶湿[g/kg']
    :type outdoor: DataFrame
    :param q_rtd_C: 定格冷房能力
    :type q_rtd_C: float
    :param e_rtd_C: 定格冷房エネルギー消費効率
    :type e_rtd_C: float
    :param L_CS_d_t: 暖冷房区画の 1 時間当たりの冷房顕熱負荷
    :type L_CS_d_t: ndarray
    :param L_CL_d_t: 暖冷房区画の 1 時間当たりの冷房潜熱負荷
    :type L_CL_d_t: ndarray
    :return: 消費電力量
    :rtype: ndarray
    """
    return rac.calc_E_E_C_d_t(region, outdoor, q_rtd_C, e_rtd_C, L_CS_d_t, L_CL_d_t)
