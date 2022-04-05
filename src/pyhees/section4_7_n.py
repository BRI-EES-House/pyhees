# ============================================================================
# 付録 N 地中熱ヒートポンプ温水暖房機
# ============================================================================

import numpy as np
from pyhees.section4_7_common import get_Q_out_H_hs_d_t
from pyhees.section4_8_a import calc_e_ref_H_th
import pyhees.section4_7_h as appendix_H
from pyhees.section4_7_o import get_virtual_HeatExchangerType


# ============================================================================
# N3. 暖房エネルギー消費量
# ============================================================================


# ============================================================================
# N.3.1 消費電力量
# ============================================================================


def calc_E_E_hs_d_t(Q_dmd_H_hs_d_t, Theta_ex_a_Ave, Theta_ex_d_Ave_d, Theta_ex_H_Ave, Theta_SW_d_t, q_max_hs, L_H_x_t_i, L_CS_x_t_i, L_CL_x_t_i, HeatExchangerType):
    """日付dの時刻tにおける1時間当たりの温水暖房用熱源機の消費電力量 (1)

    Args:
      Q_dmd_H_hs_d_t(ndarray): 1時間当たりの熱源機の熱需要 (MJ/h)
      Theta_ex_a_Ave(float): 年平均外気温度 (℃)
      Theta_ex_d_Ave_d(ndarray): 日付dにおける日平均外気温度 (℃)
      Theta_ex_H_Ave(float): 暖房期における期間平均外気温度（℃）
      Theta_SW_d_t(ndarray): 往き温水温度 (℃)
      q_max_hs(float): 熱源機の最大暖房能力 ⒲
      L_H_x_t_i(ndarray): 暖冷房区画iの1時間当たりの暖房負荷
      L_CS_x_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの冷房顕熱負荷 (MJ/h)
      L_CL_x_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの冷房潜熱負荷 (MJ/h)
      HeatExchangerType(str): 熱交換器タイプ (-)

    Returns:
      ndarray: 1時間当たりの熱源機の消費電力量 (kWh/h)

    """
    # ---------- 地中熱交換器からの戻り熱源水の日平均温度 ----------

    # 1日当たりの冷房全熱負荷の年間最大値（MJ/d）(20c)
    L_max_C = get_L_max_C(L_CS_x_t_i, L_CL_x_t_i)

    # 1日当たりの暖房負荷の年間最大値（MJ/d）(20b)
    L_max_H = get_L_max_H(L_H_x_t_i)

    # 1日当たりの暖房負荷の年間最大値と1日当たりの冷房負荷の年間最大値の和に対する、これらの差の比（-）(20a)
    R_L_max = get_R_L_max(L_max_H, L_max_C)

    # 付録Oによる熱交換器タイプの決定
    virtual_HeatExchangerType = get_virtual_HeatExchangerType(HeatExchangerType)

    # 地中熱交換器からの戻り熱源水温度を求める式の係数（-）(19)
    K_gsRW_H = calc_K_gsRW_H(R_L_max, virtual_HeatExchangerType)

    # 暖房期における地中熱交換器からの戻り熱源水の期間平均温度と年平均外気温度との差（℃）(18)
    Delta_Theta_gsRW_H = calc_Delta_Theta_gsRW_H(R_L_max, virtual_HeatExchangerType)

    # 日付dにおける地中熱交換器からの戻り熱源水の日平均温度（℃）(17)
    Theta_gsRW_d_ave_d = get_Theta_gsRW_d_ave_d(K_gsRW_H, Theta_ex_d_Ave_d, Theta_ex_H_Ave, Theta_ex_a_Ave, Delta_Theta_gsRW_H)

    # ---------- 地中からの戻り熱源水温度および送水温度による補正後の最大暖房能力 ----------

    # 日付dの時刻tにおける1時間当たりの温水暖房用熱源機の最大暖房出力（MJ/h）(16)
    q_max_H_hs_JRA = calc_q_max_H_hs_JRA(q_max_hs)

    # ---------- 温水暖房用熱源機内の平均放熱損失 ----------

    # 日付dの時刻tにおける温水暖房用の熱源機内部の平均放熱損失 (kw) (N.9)
    q_loss_H_hs_d_t = get_q_loss_H_hs_d_t()

    # ---------- 温水暖房用熱源機の平均暖房出力 ----------

    # 日付dの時刻tにおける1時間当たりの温水暖房用熱源機の最大暖房出力（MJ/h）(15)
    Q_max_H_hs_d_t = calc_Q_max_H_hs_d_t(Theta_SW_d_t, Theta_ex_d_Ave_d, Theta_ex_H_Ave, Theta_ex_a_Ave, q_max_hs, L_H_x_t_i, L_CS_x_t_i, L_CL_x_t_i, HeatExchangerType)

    # 日付dの時刻tにおける1時間当たりの温水暖房用熱源機の暖房出力（MJ/h）(14)
    Q_out_H_hs_d_t = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

    # 日付dの時刻tにおける温水暖房用熱源機の平均暖房出力(kW) (13)
    q_out_H_hs_d_t = get_q_out_H_hs_d_t(Q_out_H_hs_d_t)

    # ---------- 温水暖房用熱源機の最大暖房能力に対する平均負荷率 ----------

    # 日付dの時刻tにおける温水暖房用熱源機の最大暖房能力に対する平均負荷率(-) (12)
    qr_out_H_hs_d_t = get_qr_out_H_hs_d_t(q_out_H_hs_d_t, q_max_H_hs_JRA)

    # ---------- 補機の消費電力量 ----------

    # 日付dの時刻tにおける1時間当たりの補機の消費電力量(kWh/h) (11a)
    E_aux_hs_d_t = calc_E_aux_hs_d_t(qr_out_H_hs_d_t)

    # ---------- ポンプの消費電力量 ----------

    # 日付dの時刻tにおける1時間当たりの熱源水ポンプの消費電力量 (kWh/h) (10a)
    E_pump_gsRW_d_t = calc_E_pump_gsRW_d_t(qr_out_H_hs_d_t)

    # 日付dの時刻tにおける1時間当たりの送水ポンプの消費電力量 (kWh/h) (9a)
    E_pump_SW_d_t = calc_E_pump_SW_d_t(qr_out_H_hs_d_t)

    # 日付dの時刻tにおける1時間当たりのポンプの消費電力量 (kWh/h) (8)
    E_pump_hs_d_t = get_E_pump_hs_d_t(E_pump_SW_d_t, E_pump_gsRW_d_t)

    # ---------- 圧縮機の消費電力量 ----------

    # 日付dの時刻tにおけるヒートポンプサイクルの凝縮温度（℃）(7a)
    Theta_ref_SH_d_t = calc_Theta_ref_SH_d_t(qr_out_H_hs_d_t, Theta_gsRW_d_ave_d)

    # 日付dの時刻tにおけるヒートポンプサイクルの蒸発温度（℃）(6a)
    Theta_ref_SC_d_t = calc_Theta_ref_SC_d_t(qr_out_H_hs_d_t, Theta_SW_d_t)

    # 日付dの時刻tにおけるヒートポンプサイクルの凝縮温度（℃）(5a)
    Theta_ref_cnd_d_t = calc_Theta_ref_cnd_d_t(qr_out_H_hs_d_t, Theta_SW_d_t)

    # 日付dの時刻tにおけるヒートポンプサイクルの蒸発温度（℃）(4a)
    Theta_ref_evp_d_t = calc_Theta_ref_evp_d_t(qr_out_H_hs_d_t, Theta_gsRW_d_ave_d)

    # 日付dの時刻tにおける1時間当たりの圧縮機の圧縮効率 (-) (3a)
    Mu_d_t = calc_Mu_d_t(Theta_ref_evp_d_t, Theta_ref_cnd_d_t, Theta_ref_SC_d_t, Theta_ref_SH_d_t)

    # 日付dの時刻tにおける1時間当たりの圧縮機の消費電力量 (kWh/h) (2)
    E_comp_hs_d_t, _ = get_E_comp_hs_d_t(qr_out_H_hs_d_t, q_out_H_hs_d_t, q_loss_H_hs_d_t, Mu_d_t, Theta_ref_evp_d_t, Theta_ref_cnd_d_t)

    # ---------- 熱源機の消費電力量 ----------

    # 1時間当たりの熱源機の消費電力量 (kWh/h) (1)
    E_E_hs_d_t = E_comp_hs_d_t + E_pump_hs_d_t + E_aux_hs_d_t
    E_E_hs_d_t[q_out_H_hs_d_t == 0] = 0

    return E_E_hs_d_t


# ============================================================================
# N.3.2 ガス消費量
# ============================================================================


def get_E_G_hs_d_t():
    """熱源機のガス消費量

    Args:

    Returns:
      ndarray: 熱源機のガス消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# N.3.3 灯油消費量
# ============================================================================


def get_E_K_hs_d_t():
    """熱源機の灯油消費量

    Args:

    Returns:
      ndarray: 熱源機の灯油消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# N.3.4 その他の一次エネルギー消費量
# ============================================================================


def get_E_M_hs_d_t():
    """熱源機のその他の燃料の一次エネルギー消費量

    Args:

    Returns:
      ndarray: 熱源機のその他の燃料の一次エネルギー消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# N.4 圧縮機の消費電力量
# ============================================================================


def get_E_comp_hs_d_t(qr_out_H_hs_d_t, q_out_H_hs_d_t, q_loss_H_hs_d_t, Mu_d_t, Theta_ref_evp_d_t, Theta_ref_cnd_d_t):
    """日付dの時刻tにおける1時間当たりの圧縮機の消費電力量 (2)

    Args:
      qr_out_H_hs_d_t(ndarray): 日付dの時刻tにおける温水暖房用熱源機の最大暖房能力に対する平均負荷率(-)
      q_out_H_hs_d_t(ndarray): 1時間平均のヒートポンプユニットの断続運転率
      q_loss_H_hs_d_t(ndarray): 1時間平均のヒートポンプユニットの断続運転率
      Mu_d_t(ndarray): 1時間平均のヒートポンプユニットの断続運転率
      Theta_ref_evp_d_t(ndarray): 1時間平均のヒートポンプユニットの断続運転率
      Theta_ref_cnd_d_t(ndarray): 1時間平均のヒートポンプユニットの断続運転率

    Returns:
      ndarray: 日付dの時刻tにおける1時間当たりの圧縮機の消費電力量

    """
    # 圧縮機の消費電力に対する補正係数を計算する式の係数(-) (2c)
    k_comp_a = -0.7309
    k_comp_b = 0.67
    k_comp_c = 1.0319

    # 日付𝑑の時刻𝑡における圧縮機の消費電力に対する補正係数(-) (2b)
    f_comp_act_d_t = np.clip(k_comp_a * qr_out_H_hs_d_t + (1 - k_comp_a * k_comp_b), 1, None) * k_comp_c

    # 日付dの時刻tにおける1時間当たりの圧縮機の消費電力量 (2a)
    E_comp_hs_d_t = f_comp_act_d_t * ((q_out_H_hs_d_t + q_loss_H_hs_d_t) / Mu_d_t)
    E_comp_hs_d_t[Theta_ref_evp_d_t >= Theta_ref_cnd_d_t] = 0

    return E_comp_hs_d_t, f_comp_act_d_t


def calc_Mu_d_t(Theta_ref_evp_d_t, Theta_ref_cnd_d_t, Theta_ref_SC_d_t, Theta_ref_SH_d_t):
    """日付dの時刻tにおける圧縮機の圧縮効率 (3a)

    Args:
      Theta_ref_evp_d_t(ndarray): 1時間平均のヒートポンプユニットの断続運転率
      Theta_ref_cnd_d_t(ndarray): 1時間平均のヒートポンプユニットの断続運転率
      Theta_ref_SC_d_t(ndarray): ヒートポンプサイクルの過冷却度（℃）
      Theta_ref_SH_d_t(ndarray): ヒートポンプサイクルの過熱度（℃）

    Returns:
      ndarray: 日付dの時刻tにおける圧縮機の圧縮効率 (3a)

    """
    # Kμh0：圧縮機の圧縮効率を求める式の係数 (-) (3b)
    K_Mu_h_0 = get_K_Mu_h_0()

    # Kμh1：圧縮機の圧縮効率を求める式の係数 (-) (3b)
    K_Mu_h_1 = get_K_Mu_h_1()

    # Kμh2：圧縮機の圧縮効率を求める式の係数 (-) (3b)
    K_Mu_h_2 = get_K_Mu_h_2()

    # 日付dの時刻tにおけるヒートポンプサイクルの理論暖房効率(-) 4章8節付録A(1)
    e_ref_H_th_d_t = calc_e_ref_H_th(Theta_ref_evp_d_t, Theta_ref_cnd_d_t, Theta_ref_SC_d_t, Theta_ref_SH_d_t)

    # 日付dの時刻tにおける圧縮機の圧縮効率 (3a)
    Mu_d_t = K_Mu_h_2 * (e_ref_H_th_d_t ** 2) + K_Mu_h_1 * e_ref_H_th_d_t + K_Mu_h_0
    Mu_d_t[e_ref_H_th_d_t > 10] = K_Mu_h_2 * (10 ** 2) + K_Mu_h_1 * 10 + K_Mu_h_0

    return Mu_d_t


def get_K_Mu_h_0():
    """Kμh0：圧縮機の圧縮効率を求める式の係数 (-) (3b)

    Args:

    Returns:
      float: Kμh0：圧縮機の圧縮効率を求める式の係数 (-) (3b)

    """
    return -0.430363368361459


def get_K_Mu_h_1():
    """Kμh1：圧縮機の圧縮効率を求める式の係数 (-) (3b)

    Args:

    Returns:
      float: Kμh1：圧縮機の圧縮効率を求める式の係数 (-) (3b)

    """
    return 0.698531770387591


def get_K_Mu_h_2():
    """Kμh2：圧縮機の圧縮効率を求める式の係数 (-) (3b)

    Args:

    Returns:
      float: Kμh2：圧縮機の圧縮効率を求める式の係数 (-) (3b)

    """
    return 0.0100164335768507


def calc_Theta_ref_evp_d_t(qr_out_H_hs_d_t, Theta_gsRW_d_ave_d):
    """日付dの時刻tにおけるヒートポンプサイクルの蒸発温度（℃） (4a)

    Args:
      qr_out_H_hs_d_t(ndarray): 日付dの時刻tにおける温水暖房用熱源機の最大暖房能力に対する平均負荷率(-)
      Theta_gsRW_d_ave_d(ndarray): 日付dにおける地中熱交換器からの戻り熱源水の日平均温度（℃）

    Returns:
      日付dの時刻tにおけるヒートポンプサイクルの蒸発温度（℃） (4a)

    """
    # Kevph0：蒸発温度を計算する式の係数 (-) (4b)
    K_evp_h_0 = get_K_evp_h_0()

    # Kevph1：蒸発温度を計算する式の係数 (-) (4b)
    K_evp_h_1 = get_K_evp_h_1()

    # Kevph2：蒸発温度を計算する式の係数 (-) (4b)
    K_evp_h_2 = get_K_evp_h_2()

    # Kevph12：蒸発温度を計算する式の係数 (-) (4b)
    K_evp_h_12 = get_K_evp_h_12()

    # 日付dの時刻tにおけるヒートポンプサイクルの蒸発温度（℃） (4a)
    Theta_ref_evp_d_t = np.clip(K_evp_h_0 + K_evp_h_1 * np.repeat(Theta_gsRW_d_ave_d, 24)
                                + K_evp_h_2 * qr_out_H_hs_d_t
                                + K_evp_h_12 * np.repeat(Theta_gsRW_d_ave_d, 24) * qr_out_H_hs_d_t, -50, None)

    return Theta_ref_evp_d_t


def get_K_evp_h_0():
    """Kevph0：蒸発温度を計算する式の係数 (-) (4b)

    Args:

    Returns:
      float: Kevph0：蒸発温度を計算する式の係数

    """

    return -2.95315205817646


def get_K_evp_h_1():
    """Kevph1：蒸発温度を計算する式の係数 (-) (4b)

    Args:

    Returns:
      float: Kevph1：蒸発温度を計算する式の係数

    """
    return 0.915893610614308


def get_K_evp_h_2():
    """Kevph2：蒸発温度を計算する式の係数 (-) (4b)

    Args:

    Returns:
      float: Kevph2：蒸発温度を計算する式の係数

    """
    return -11.8319776584846


def get_K_evp_h_12():
    """Kevph12：蒸発温度を計算する式の係数 (-) (4b)

    Args:

    Returns:
      float: Kevph12：蒸発温度を計算する式の係数

    """
    return 0.29704275467947


def calc_Theta_ref_cnd_d_t(qr_out_H_hs_d_t, Theta_SW_d_t):
    """日付dの時刻tにおけるヒートポンプサイクルの凝縮温度（℃）(5a)

    Args:
      qr_out_H_hs_d_t(param Theta_SW_d_t: 日付dの時刻tにおける往き温水温度（℃）): 日付dの時刻tにおける温水暖房用熱源機の最大暖房能力に対する平均負荷率(-)
      Theta_SW_d_t(ndarray): 日付dの時刻tにおける往き温水温度（℃）

    Returns:
      ndarray: 日付dの時刻tにおけるヒートポンプサイクルの凝縮温度（℃）

    """
    # Kcndh0：凝縮温度を計算する式の係数 (-) (5b)
    K_cnd_h_0 = get_K_cnd_h_0()

    # Kcndh1：凝縮温度を計算する式の係数 (-) (5b)
    K_cnd_h_1 = get_K_cnd_h_1()

    # Kcndh2：凝縮温度を計算する式の係数 (-) (5b)
    K_cnd_h_2 = get_K_cnd_h_2()

    # Kcndh12：凝縮温度を計算する式の係数 (-) (5b)
    K_cnd_h_12 = get_K_cnd_h_12()

    # 日付dの時刻tにおけるヒートポンプサイクルの蒸発温度（℃） (5a)
    Theta_ref_cnd_d_t = np.clip(K_cnd_h_0 + K_cnd_h_1 * Theta_SW_d_t
                                + K_cnd_h_2 * qr_out_H_hs_d_t
                                + K_cnd_h_12 * Theta_SW_d_t * qr_out_H_hs_d_t, None, 65)

    return Theta_ref_cnd_d_t


def get_K_cnd_h_0():
    """Kcndh0：凝縮温度を計算する式の係数 (-) (5b)

    Args:

    Returns:
      float: Kcndh0：凝縮温度を計算する式の係数

    """
    return 3.6105623002886


def get_K_cnd_h_1():
    """Kcndh1：凝縮温度を計算する式の係数 (-) (5b)

    Args:

    Returns:
      float: Kcndh1：凝縮温度を計算する式の係数

    """
    return 0.930136847064537


def get_K_cnd_h_2():
    """Kcndh2：凝縮温度を計算する式の係数 (-) (5b)

    Args:

    Returns:
      float: Kcndh2：凝縮温度を計算する式の係数

    """
    return 0.494024927234563


def get_K_cnd_h_12():
    """Kcndh12：凝縮温度を計算する式の係数 (-) (5b)

    Args:

    Returns:
      ndarray: Kcndh12：凝縮温度を計算する式の係数

    """
    return 0.00770898511188855


def calc_Theta_ref_SC_d_t(qr_out_H_hs_d_t, Theta_SW_d_t):
    """日付dの時刻tにおけるヒートポンプサイクルの過冷却度（℃）(6a)

    Args:
      qr_out_H_hs_d_t(ndarray): 日付dの時刻tにおける温水暖房用熱源機の最大暖房能力に対する平均負荷率(-)
      Theta_SW_d_t(ndarray): 往き温水温度 (℃)

    Returns:
      ndarray: 日付dの時刻tにおけるヒートポンプサイクルの過冷却度（℃）

    """
    # Ksch0：過冷却度を計算する式の係数 (-) (6b)
    K_sc_h_0 = get_K_sc_h_0()

    # Ksch1：過冷却度を計算する式の係数 (-) (6b)
    K_sc_h_1 = get_K_sc_h_1()

    # Ksch2：過冷却度を計算する式の係数 (-) (6b)
    K_sc_h_2 = get_K_sc_h_2()

    # 日付dの時刻tにおけるヒートポンプサイクルの過冷却度（℃） (6a)
    Theta_ref_SC_d_t = np.clip(K_sc_h_0 + K_sc_h_1 * Theta_SW_d_t + K_sc_h_2 * qr_out_H_hs_d_t, 0, None)

    return Theta_ref_SC_d_t


def get_K_sc_h_0():
    """Ksch0：過冷却度を計算する式の係数(-) (6b)

    Args:

    Returns:
      float: Ksch0：過冷却度を計算する式の係数(-) (6b)

    """
    return -4.02655782981397


def get_K_sc_h_1():
    """Ksch1：過冷却度を計算する式の係数 (-) (6b)

    Args:

    Returns:
      float: Ksch1：過冷却度を計算する式の係数

    """
    return 0.0894330494418674


def get_K_sc_h_2():
    """Ksch2：過冷却度を計算する式の係数 (-) (6b)

    Args:

    Returns:
      float: Ksch2：過冷却度を計算する式の係数

    """
    return 14.3457831669162


def calc_Theta_ref_SH_d_t(qr_out_H_hs_d_t, Theta_gsRW_d_ave_d):
    """日付dの時刻tにおけるヒートポンプサイクルの過熱度（℃）(7a)

    Args:
      qr_out_H_hs_d_t(ndarray): 日付dの時刻tにおける温水暖房用熱源機の最大暖房能力に対する平均負荷率(-)
      Theta_gsRW_d_ave_d(ndarray): 日付dにおける地中熱交換器からの戻り熱源水の日平均温度（℃）

    Returns:
      ndarray: 日付dの時刻tにおけるヒートポンプサイクルの過熱度（℃）

    """
    # Kshh0：過熱度を計算する式の係数 (-) (7b)
    K_sh_h_0 = get_K_sh_h_0()

    # Kshh1：過熱度を計算する式の係数 (-) (7b)
    K_sh_h_1 = get_K_sh_h_1()

    # Kshh2：過熱度を計算する式の係数 (-) (7b)
    K_sh_h_2 = get_K_sh_h_2()

    # 日付dの時刻tにおけるヒートポンプサイクルの過熱度（℃） (7a)
    Theta_ref_SC_d_t = np.clip(K_sh_h_0 + K_sh_h_1 * qr_out_H_hs_d_t + K_sh_h_2 * np.repeat(Theta_gsRW_d_ave_d, 24), 0, None)

    return Theta_ref_SC_d_t


def get_K_sh_h_0():
    """Kshh0：過熱度を計算する式の係数(-) (7b)

    Args:

    Returns:
      float: Kshh0：過熱度を計算する式の係数

    """
    return 0.819643791668597


def get_K_sh_h_1():
    """Kshh1：過熱度を計算する式の係数 (-) (7b)

    Args:

    Returns:
      float: Kshh1：過熱度を計算する式の係数 (-)

    """
    return 2.99282570323758


def get_K_sh_h_2():
    """Kshh2：過熱度を計算する式の係数 (-) (7b)

    Args:

    Returns:
      Kshh2：過熱度を計算する式の係数 (-)

    """
    return -0.0762659183765636


# ============================================================================
# N.5 ポンプの消費電力量
# ============================================================================


def get_E_pump_hs_d_t(E_pump_SW_d_t, E_pump_gsRW_d_t):
    """日付dの時刻tにおける1時間当たりのポンプの消費電力量 (8)

    Args:
      E_pump_SW_d_t(ndarray): 日付dの時刻tにおける1時間当たりの送水ポンプの消費電力量（kWh/h）
      E_pump_gsRW_d_t(ndarray): 日付dの時刻tにおける1時間当たりの熱源水ポンプの消費電力量（kWh/h）

    Returns:
      ndarray: 日付dの時刻tにおける1時間当たりのポンプの消費電力量（kWh/h）

    """

    # 日付dの時刻tにおける1時間当たりのポンプの消費電力量 (8)
    E_pump_hs_d_t = E_pump_SW_d_t + E_pump_gsRW_d_t

    return E_pump_hs_d_t


def calc_E_pump_SW_d_t(qr_out_H_hs_d_t):
    """日付dの時刻tにおける1時間当たりの送水ポンプの消費電力量（kWh/h） (9a)

    Args:
      qr_out_H_hs_d_t(ndarray): 日付dの時刻tにおける温水暖房用熱源機の最大暖房能力に対する平均負荷率(-)

    Returns:
      ndarray: 日付dの時刻tにおける1時間当たりの送水ポンプの消費電力量（kWh/h）

    """
    # apump,SW：送水ポンプの消費電力量を計算する式の係数 (-) (9b)
    a_pump_SW = get_a_pump_SW()

    # bpump,SW：送水ポンプの消費電力量を計算する式の係数 (-) (9b)
    b_pump_SW = get_b_pump_SW()

    # 日付dの時刻tにおける1時間当たりの送水ポンプの消費電力量（kWh/h） (9a)
    E_pump_SW_d_t = a_pump_SW * qr_out_H_hs_d_t + b_pump_SW * (qr_out_H_hs_d_t ** 2)

    return E_pump_SW_d_t


def get_a_pump_SW():
    """apump,SW：送水ポンプの消費電力量を計算する式の係数 (-) (9b)

    Args:

    Returns:
      float: apump,SW：送水ポンプの消費電力量を計算する式の係数 (-)

    """
    return 0.041972403


def get_b_pump_SW():
    """bpump,SW：送水ポンプの消費電力量を計算する式の係数 (-) (9b)

    Args:

    Returns:
      float: bpump,SW：送水ポンプの消費電力量を計算する式の係数 (-)

    """
    return 0.104478967


def calc_E_pump_gsRW_d_t(qr_out_H_hs_d_t):
    """日付dの時刻tにおける1時間当たりの熱源水ポンプの消費電力量（kWh/h） (10a)

    Args:
      qr_out_H_hs_d_t(ndarray): 日付dの時刻tにおける温水暖房用熱源機の最大暖房能力に対する平均負荷率(-)

    Returns:
      ndarray: 日付dの時刻tにおける1時間当たりの熱源水ポンプの消費電力量（kWh/h）

    """
    # apump,gsRW：熱源水ポンプの消費電力量を計算する式の係数 (-) (10b)
    a_pump_gsRW = get_a_pump_gsRW()

    # bpump,gsRW：熱源水ポンプの消費電力量を計算する式の係数 (-) (10b)
    b_pump_gsRW = get_b_pump_gsRW()

    # 日付dの時刻tにおける1時間当たりの熱源水ポンプの消費電力量（kWh/h） (10a)
    E_pump_gsRW_d_t = a_pump_gsRW * qr_out_H_hs_d_t + b_pump_gsRW * (qr_out_H_hs_d_t ** 2)

    return E_pump_gsRW_d_t


def get_a_pump_gsRW():
    """apump,gsRW：熱源水ポンプの消費電力量を計算する式の係数 (-) (10b)

    Args:

    Returns:
      float: apump,gsRW：熱源水ポンプの消費電力量を計算する式の係数 (-)

    """
    return 0.062196275


def get_b_pump_gsRW():
    """bpump,gsRW：熱源水ポンプの消費電力量を計算する式の係数 (-) (10b)

    Args:

    Returns:
      bpump,gsRW：熱源水ポンプの消費電力量を計算する式の係数 (-)

    """
    return 0.071756474


# ============================================================================
# N.6 補機の消費電力量
# ============================================================================


def calc_E_aux_hs_d_t(qr_out_H_hs_d_t):
    """日付dの時刻tにおける1時間当たりの補機の消費電力量（kWh/h） (11a)

    Args:
      qr_out_H_hs_d_t(ndarray): 日付dの時刻tにおける温水暖房用熱源機の最大暖房能力に対する平均負荷率(-)

    Returns:
      ndarray: 日付dの時刻tにおける1時間当たりの補機の消費電力量（kWh/h）

    """
    # kauxh0：補機の消費電力量を計算する式の係数 (-) (11b)
    kauxh0 = get_kauxh0()

    # kauxh1：補機の消費電力量を計算する式の係数 (-) (11b)
    kauxh1 = get_kauxh1()

    # 日付dの時刻tにおける1時間当たりの熱源水ポンプの消費電力量（kWh/h） (11a)
    E_aux_hs_d_t = kauxh1 * qr_out_H_hs_d_t + kauxh0

    return E_aux_hs_d_t


def get_kauxh0():
    """kauxh0：補機の消費電力量を計算する式の係数 (-) (11b)

    Args:

    Returns:
      float: kauxh0：補機の消費電力量を計算する式の係数 (-)

    """
    return 0.0433205551083371


def get_kauxh1():
    """kauxh1：補機の消費電力量を計算する式の係数 (-) (11b)

    Args:

    Returns:
      float: kauxh1：補機の消費電力量を計算する式の係数 (-)

    """
    return 0.0173758330059922


# ============================================================================
# N.7 温水暖房用熱源機の最大暖房能力に対する平均負荷率
# ============================================================================


def get_qr_out_H_hs_d_t(q_out_H_hs_d_t, q_max_H_hs_JRA):
    """日付dの時刻tにおける温水暖房用熱源機の最大暖房能力に対する平均負荷率（-） (12)

    Args:
      q_out_H_hs_d_t(ndarray): 日付dの時刻tにおける温水暖房用熱源機の最大暖房能力に対する平均負荷率(-)
      q_max_H_hs_JRA(ndarray): 地中からの戻り熱源水温度および送水温度による補正後の最大暖房能力(W)

    Returns:
      ndarray: 日付dの時刻tにおける温水暖房用熱源機の最大暖房能力に対する平均負荷率（-）

    """
    # 日付dの時刻tにおける温水暖房用熱源機の最大暖房能力に対する平均負荷率（-） (12)
    qr_out_H_hs_d_t = (q_out_H_hs_d_t * 10 ** 3) / q_max_H_hs_JRA

    return qr_out_H_hs_d_t


# ============================================================================
# N.8 温水暖房用熱源機の平均暖房出力
# ============================================================================


def get_q_out_H_hs_d_t(Q_out_H_hs_d_t):
    """日付dの時刻tにおける温水暖房用熱源機の平均暖房出力（kW） (13)

    Args:
      Q_out_H_hs_d_t(ndarray): 日付dの時刻tにおける1時間当たりの温水暖房用熱源機の暖房出力(MJ/h)

    Returns:
      ndarray: 日付dの時刻tにおける温水暖房用熱源機の平均暖房出力（kW）

    """
    # 日付dの時刻tにおける温水暖房用熱源機の平均暖房出力（kW）(13)
    q_out_H_hs_d_t = Q_out_H_hs_d_t / 3600 * 10 ** 3

    return q_out_H_hs_d_t

def get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t):
    """日付dの時刻tにおける1時間当たりの温水暖房用熱源機の暖房出力（MJ/h）(14)

    Args:
      Q_dmd_H_hs_d_t(ndarray): 日付dの時刻tにおける1時間当たりの温水暖房用熱源機の温水熱需要(MJ/h)
      Q_max_H_hs_d_t(ndarray): 日付dの時刻tにおける1時間当たりの温水暖房用熱源機の最大暖房出力(MJ/h)

    Returns:
      ndarray: 日付dの時刻tにおける1時間当たりの温水暖房用熱源機の暖房出力（MJ/h）

    """
    # 日付dの時刻tにおける温水暖房用熱源機の平均暖房出力（kW）(14)
    return np.min([Q_dmd_H_hs_d_t, Q_max_H_hs_d_t], axis=0)


def calc_Q_max_H_hs_d_t(Theta_SW_d_t, Theta_ex_d_Ave_d, Theta_ex_H_Ave, Theta_ex_a_Ave, q_max_hs, L_H_x_t_i, L_CS_x_t_i, L_CL_x_t_i, HeatExchangerType):
    """日付dの時刻tにおける1時間当たりの温水暖房用熱源機の最大暖房出力(MJ/h) (15)

    Args:
      Theta_SW_d_t(ndarray): 往き温水温度 (℃)
      Theta_ex_d_Ave_d(ndarray): 日付dにおける日平均外気温度 (℃)
      Theta_ex_H_Ave(float): 暖房期における期間平均外気温度（℃）
      Theta_ex_a_Ave(float): 年平均外気温度 (℃)
      q_max_hs(float): 熱源機の最大暖房能力 ⒲
      L_H_x_t_i(ndarray): 暖冷房区画iの1時間当たりの暖房負荷
      L_CS_x_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの冷房顕熱負荷 (MJ/h)
      L_CL_x_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの冷房潜熱負荷 (MJ/h)
      HeatExchangerType(str): 熱交換器タイプ (-)

    Returns:
      ndarray: 日付dの時刻tにおける1時間当たりの温水暖房用熱源機の最大暖房出力(MJ/h)

    """
    # ---------- 地中熱交換器からの戻り熱源水の日平均温度 ----------

    # 1日当たりの冷房全熱負荷の年間最大値（MJ/d）(20c)
    L_max_C = get_L_max_C(L_CS_x_t_i, L_CL_x_t_i)

    # 1日当たりの暖房負荷の年間最大値（MJ/d）(20b)
    L_max_H = get_L_max_H(L_H_x_t_i)

    # 1日当たりの暖房負荷の年間最大値と1日当たりの冷房負荷の年間最大値の和に対する、これらの差の比（-）(20a)
    R_L_max = get_R_L_max(L_max_H, L_max_C)

    # 付録Oによる熱交換器タイプの決定
    virtual_HeatExchangerType = get_virtual_HeatExchangerType(HeatExchangerType)

    # 地中熱交換器からの戻り熱源水温度を求める式の係数（-）(19)
    K_gsRW_H = calc_K_gsRW_H(R_L_max, virtual_HeatExchangerType)

    # 暖房期における地中熱交換器からの戻り熱源水の期間平均温度と年平均外気温度との差（℃）(18)
    Delta_Theta_gsRW_H = calc_Delta_Theta_gsRW_H(R_L_max, virtual_HeatExchangerType)

    # 日付dにおける地中熱交換器からの戻り熱源水の日平均温度（℃）(17)
    Theta_gsRW_d_ave_d = get_Theta_gsRW_d_ave_d(K_gsRW_H, Theta_ex_d_Ave_d, Theta_ex_H_Ave, Theta_ex_a_Ave,
                                                Delta_Theta_gsRW_H)

    # ---------- 地中からの戻り熱源水温度および送水温度による補正後の最大暖房能力(W) (16) ----------
    q_max_H_hs_JRA = calc_q_max_H_hs_JRA(q_max_hs)

    # ---------- 日付dの時刻tにおける1時間当たりの温水暖房用熱源機の最大暖房出力(MJ/h)(15) ----------
    Q_max_H_hs_d_t = (-0.005635139785329 * Theta_SW_d_t
                      + 0.0258983299329793 * np.clip(np.repeat(Theta_gsRW_d_ave_d, 24), 0, 20) + 0.836930642418471) * q_max_H_hs_JRA * 3600 * 10 ** (-6)

    return Q_max_H_hs_d_t


# ============================================================================
# N.9 温水暖房用熱源機内の平均放熱損失
# ============================================================================


def get_q_loss_H_hs_d_t():
    """日付dの時刻tにおける温水暖房用熱源機内の平均放熱損失（kW）

    Args:

    Returns:
      float: 日付dの時刻tにおける温水暖房用熱源機内の平均放熱損失（kW）

    """
    return 0


# ============================================================================
# N.10 地中からの戻り熱源水温度および送水温度による補正後の最大暖房能力
# ============================================================================


def calc_q_max_H_hs_JRA(q_max_hs):
    """地中からの戻り熱源水温度および送水温度による補正後の最大暖房能力(W) (16)

    Args:
      q_max_hs(return: 地中からの戻り熱源水温度および送水温度による補正後の最大暖房能力(W)): 熱源機の最大暖房能力 ⒲

    Returns:
      地中からの戻り熱源水温度および送水温度による補正後の最大暖房能力(W)

    """
    # 地中からの戻り熱源水温度および送水温度に関する最大暖房能力の補正係数(-)
    f_crated = get_f_crated()

    # 地中からの戻り熱源水温度および送水温度による補正後の最大暖房能力(W)(16)
    q_max_H_hs_JRA = q_max_hs * f_crated

    return q_max_H_hs_JRA


def calc_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh):
    """温水暖房用熱源機の定格能力

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      has_MR_hwh(bool): 温水暖房の放熱器を主たる居室に設置する場合はTrue
      has_OR_hwh(bool): 温水暖房の放熱器をその他の居室に設置する場合はTrue

    Returns:
      float: 温水暖房用熱源機の定格能力

    """
    # 付録Hに定める温水暖房用熱源機の最大能力 q_max_hs に等しい
    return appendix_H.calc_q_max_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)


def get_f_crated():
    """地中からの戻り熱源水温度および送水温度に関する最大暖房能力の補正係数(-)

    Args:

    Returns:
      float: 地中からの戻り熱源水温度および送水温度に関する最大暖房能力の補正係数(-)

    """
    return 1.35


# ============================================================================
# N.11 地中熱交換器からの戻り熱源水の日平均温度
# ============================================================================


def get_Theta_gsRW_d_ave_d(K_gsRW_H, Theta_ex_d_Ave_d, Theta_ex_H_Ave, Theta_ex_a_Ave, Delta_Theta_gsRW_H):
    """日付dにおける地中熱交換器からの戻り熱源水の日平均温度(℃) (17)

    Args:
      K_gsRW_H(float): K_gsRW_H: 地中熱交換器からの戻り熱源水温度を求める式の係数(-)
      Theta_ex_d_Ave_d(ndarray): 日付dにおける日平均外気温度 (℃)
      Theta_ex_H_Ave(float): 暖房期における期間平均外気温度（℃）
      Theta_ex_a_Ave(float): 年平均外気温度 (℃)
      Delta_Theta_gsRW_H(float): 暖房期における地中熱交換器からの戻り熱源水の期間平均温度と年平均外気温度との差（℃）

    Returns:
      ndarray: 日付dにおける地中熱交換器からの戻り熱源水の日平均温度(℃)

    """
    # 日付dにおける地中熱交換器からの戻り熱源水の日平均温度(℃) (17)
    Theta_gsRW_d_ave_d = K_gsRW_H * (Theta_ex_d_Ave_d - Theta_ex_H_Ave) + Theta_ex_a_Ave + Delta_Theta_gsRW_H

    return Theta_gsRW_d_ave_d


def calc_Delta_Theta_gsRW_H(R_L_max, HeatExchangerType):
    """暖房期における地中熱交換器からの戻り熱源水の期間平均温度と年平均外気温度との差（℃）(18)

    Args:
      R_L_max(float): 1日当たりの暖房負荷の年間最大値と1日当たりの冷房負荷の年間最大値の和に対する、これらの差の比（-）
      HeatExchangerType(str): 地中熱交換器タイプ

    Returns:
      float: 暖房期における地中熱交換器からの戻り熱源水の期間平均温度と年平均外気温度との差（℃）

    """
    # 熱交換器タイプに応じた係数取得
    a_gsRW_H = get_a_gsRW_H(HeatExchangerType)
    b_gsRW_H = get_b_gsRW_H(HeatExchangerType)

    # 暖房期における地中熱交換器からの戻り熱源水の期間平均温度と年平均外気温度との差（℃）(18)
    Delta_Theta_gsRW_H = a_gsRW_H * R_L_max + b_gsRW_H

    return Delta_Theta_gsRW_H


def calc_K_gsRW_H(R_L_max, HeatExchangerType):
    """地中熱交換器からの戻り熱源水温度を求める式の係数（-）(19)

    Args:
      R_L_max(float): 1日当たりの暖房負荷の年間最大値と1日当たりの冷房負荷の年間最大値の和に対する、これらの差の比（-）
      HeatExchangerType(str): 熱交換器タイプ (-)

    Returns:
      float: 地中熱交換器からの戻り熱源水温度を求める式の係数（-）(19)

    """
    # 熱交換器タイプに応じた係数取得
    c_gsRW_H = get_c_gsRW_H(HeatExchangerType)
    d_gsRW_H = get_d_gsRW_H(HeatExchangerType)

    # 地中熱交換器からの戻り熱源水温度を求める式の係数（-）(19)
    K_gsRW_H = c_gsRW_H * R_L_max + d_gsRW_H

    return K_gsRW_H


def get_a_gsRW_H(HeatExchangerType):
    """熱交換器タイプに応じた係数a_gsRW_Hの取得

    Args:
      HeatExchangerType(str): 熱交換器タイプ (-)

    Returns:
      float: 熱交換器タイプに応じた係数a_gsRW_Hの取得

    """

    if HeatExchangerType == '1':
        return get_table_n_3()[0][0]
    elif HeatExchangerType == '2':
        return get_table_n_3()[1][0]
    elif HeatExchangerType == '3':
        return get_table_n_3()[2][0]
    elif HeatExchangerType == '4':
        return get_table_n_3()[3][0]
    elif HeatExchangerType == '5':
        return get_table_n_3()[4][0]
    else:
        raise ValueError(HeatExchangerType)


def get_b_gsRW_H(HeatExchangerType):
    """熱交換器タイプに応じた係数b_gsRW_Hの取得

    Args:
      HeatExchangerType(str): 熱交換器タイプ (-)

    Returns:
      float: 熱交換器タイプに応じた係数b_gsRW_Hの取得

    """
    if HeatExchangerType == '1':
        return get_table_n_3()[0][1]
    elif HeatExchangerType == '2':
        return get_table_n_3()[1][1]
    elif HeatExchangerType == '3':
        return get_table_n_3()[2][1]
    elif HeatExchangerType == '4':
        return get_table_n_3()[3][1]
    elif HeatExchangerType == '5':
        return get_table_n_3()[4][1]
    else:
        raise ValueError(HeatExchangerType)


def get_c_gsRW_H(HeatExchangerType):
    """熱交換器タイプに応じた係数a_gsRW_Hの取得

    Args:
      HeatExchangerType(str): 熱交換器タイプ (-)

    Returns:
      float: 熱交換器タイプに応じた係数a_gsRW_Hの取得

    """
    if HeatExchangerType == '1':
        return get_table_n_3()[0][2]
    elif HeatExchangerType == '2':
        return get_table_n_3()[1][2]
    elif HeatExchangerType == '3':
        return get_table_n_3()[2][2]
    elif HeatExchangerType == '4':
        return get_table_n_3()[3][2]
    elif HeatExchangerType == '5':
        return get_table_n_3()[4][2]
    else:
        raise ValueError(HeatExchangerType)


def get_d_gsRW_H(HeatExchangerType):
    """熱交換器タイプに応じた係数b_gsRW_Hの取得

    Args:
      HeatExchangerType(str): 熱交換器タイプ (-)

    Returns:
      float: 熱交換器タイプに応じた係数b_gsRW_Hの取得

    """
    if HeatExchangerType == '1':
        return get_table_n_3()[0][3]
    elif HeatExchangerType == '2':
        return get_table_n_3()[1][3]
    elif HeatExchangerType == '3':
        return get_table_n_3()[2][3]
    elif HeatExchangerType == '4':
        return get_table_n_3()[3][3]
    elif HeatExchangerType == '5':
        return get_table_n_3()[4][3]
    else:
        raise ValueError(HeatExchangerType)


def get_table_n_3():
    """表N.3 係数

    Args:

    Returns:
      list: 表N.3 係数

    """
    table_n_3 = [
        (3.1672, -0.4273, -0.0444, 0.0442),
        (5.9793, -1.0687, -0.1613, 0.1047),
        (8.3652, -1.5946, -0.2486, 0.1546),
        (9.9065, -2.1827, -0.3454, 0.2072),
        (10.2898, -2.8727, -0.3270, 0.2700)
    ]
    return table_n_3


def get_R_L_max(L_max_H, L_max_C):
    """1日当たりの暖房負荷の年間最大値と1日当たりの冷房負荷の年間最大値の和に対する、これらの差の比（-）(20a)

    Args:
      L_max_H(float): 1日当たりの暖房負荷の年間最大値（MJ/d）
      L_max_C(float): 1日当たりの冷房全熱負荷の年間最大値（MJ/d）

    Returns:
      float: 1日当たりの暖房負荷の年間最大値と1日当たりの冷房負荷の年間最大値の和に対する、これらの差の比（-）(20a)

    """
    # 1日当たりの暖房負荷の年間最大値と1日当たりの冷房負荷の年間最大値の和に対する、これらの差の比（-）(20a)
    R_L_max = (L_max_C - L_max_H) / (L_max_C + L_max_H)

    return R_L_max


def get_L_max_H(L_H_x_t_i):
    """1日当たりの暖房負荷の年間最大値（MJ/d）(20b)

    Args:
      L_H_x_t_i(ndarray): 暖冷房区画iの1時間当たりの暖房負荷

    Returns:
      float: 1日当たりの暖房負荷の年間最大値（MJ/d）

    """
    # L_H_x_t_iは暖冷房区画毎に365日×24時間分の負荷を持った2次元配列
    # 暖冷房区画軸合算(暖冷房区画の次元をなくす)
    L_H_x_t = np.sum(L_H_x_t_i, axis=0)

    # 1次元配列を2次元配列に形状変換する
    L_H_x_t = np.reshape(L_H_x_t, (365, 24))

    # 時間軸合算
    L_H_x = np.sum(L_H_x_t, axis=1)

    # 1日当たりの暖房負荷の年間最大値（MJ/d）(20b)
    L_max_H = np.max(L_H_x)

    return L_max_H


def get_L_max_C(L_CS_x_t_i, L_CL_x_t_i):
    """1日当たりの冷房全熱負荷の年間最大値（MJ/d）(20c)

    Args:
      L_CS_x_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの冷房顕熱負荷 (MJ/h)
      L_CL_x_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの冷房潜熱負荷 (MJ/h)

    Returns:
      float: 1日当たりの冷房全熱負荷の年間最大値（MJ/d）

    """
    # 暖冷房区画軸合算(暖冷房区画の次元をなくす)
    L_CS_x_t = np.sum(L_CS_x_t_i, axis=0)
    L_CL_x_t = np.sum(L_CL_x_t_i, axis=0)

    # L_CS_x_tとL_CL_x_tの要素同士を足す
    L_C_x_t = L_CS_x_t + L_CL_x_t

    # 1次元配列を2次元配列に形状変換する
    L_C_x_t = np.reshape(L_C_x_t, (365, 24))

    # 時間軸合算
    L_C_x = np.sum(L_C_x_t, axis=1)

    # 1日当たりの冷房全熱負荷の年間最大値（MJ/d）(20c)
    L_max_C = np.max(L_C_x)

    return L_max_C
