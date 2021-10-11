# ============================================================================
# 第九章 自然エネルギー利用設備
# 第三節 空気集熱式太陽熱利用設備
# Ver.02（エネルギー消費性能計算プログラム（住宅版）Ver.02.05～）
# ============================================================================

import numpy as np

from pyhees.section3_1_heatingday import get_heating_flag_d

import pyhees.section3_1_e as algo

from pyhees.section11_2 import calc_I_s_d_t, get_Theta_ex


# ============================================================================
# 5. 暖房負荷削減量
# ============================================================================

def calc_delta_L_dash_H_ass_d_t_i(i, supply_target, L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i, region, sol_region, A_HCZ_i,
                                  A_A, A_MR, A_OR, Q,
                                  hotwater_use, Theta_ex_d_t, P_alpha, P_beta,
                                  A_col, V_fan_P0, m_fan_test, d0, d1, ufv_insulation, r_A_ufvnt):
    """空気集熱式太陽熱利用設備による暖房負荷削減量 (MJ/h)

    Args:
      i(int): 暖冷房区画の番号
      supply_target(str): 集熱後の空気を供給する先
      L_dash_H_R_d_t_i(ndarray): 空気集熱式太陽熱利用設備による暖房負荷削減量 (MJ/h)
      L_dash_CS_R_d_t_i(ndarray): 標準住戸の負荷補正前の冷房顕熱負荷 （MJ/h）
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      A_HCZ_i(float): 暖冷房区画iの床面積 (m2)
      A_A(float): 床面積の合計(m2)
      A_MR(float): 主たる居室の床面積(m2)
      A_OR(float): その他の拠出の床面積(m2)
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      hotwater_use(bool): 空気集熱式太陽熱利用設備が給湯部を有する場合はTrue
      Theta_ex_d_t(ndarray): 外気温度 (℃)
      P_alpha(float): 方位角 (°)
      P_beta(float): 傾斜角 (°)
      A_col(tuple): 集熱器群の面積 (m2)
      V_fan_P0(float): 空気搬送ファンの送風機特性曲線において機外静圧をゼロとしたときの空気搬送ファンの風量 (m3/h)
      m_fan_test(tuple): 集熱器群を構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2))
      d0(tuple): 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の切片 (-)
      d1(tuple): 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K))
      ufv_insulation(bool): 床下空間が断熱空間内である場合はTrue
      r_A_ufvnt(float): 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)

    Returns:
      ndarray: 空気集熱式太陽熱利用設備による暖房負荷削減量

    """
    # ----- 10 集熱部 -----

    # 空気搬送ファン停止時および稼働時の集熱部の出口における空気温度 (℃)
    Theta_col_nonopg_d_t, Theta_col_opg_d_t = calc_Theta_col(A_col=A_col, P_alpha=P_alpha, P_beta=P_beta,
                                                             V_fan_P0=V_fan_P0, d0=d0, d1=d1, m_fan_test=m_fan_test,
                                                             region=region, sol_region=sol_region,
                                                             Theta_ex_d_t=Theta_ex_d_t)

    # ----- 9. 空気搬送部 -----

    # 1時間当たりの空気搬送ファンの稼働時間 (h/h) (12)
    t_fan_d_t = get_t_fan_d_t(Theta_col_nonopg_d_t, Theta_col_opg_d_t)

    # 1時間当たりの空気搬送ファンの風量 (m3/h) (13)
    V_fan_d_t = get_V_fan_d_t(t_fan_d_t, V_fan_P0)

    # 暖房日
    heating_flag_d = get_heating_flag_d(L_dash_H_R_d_t_i)

    # 1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (17)
    r_sa_d_t = get_r_sa_d_t(t_fan_d_t, heating_flag_d)

    # 床下空間または居室へ供給する1時間当たりの空気の風量の合計 (m3/h) (16)
    V_sa_d_t_A = get_V_sa_d_t_A(V_fan_d_t, r_sa_d_t)

    # 1時間当たりの床下空間または居室へ供給する空気の風量 (15)
    V_sa_d_t_i = get_V_sa_d_t_i(i, A_HCZ_i, A_MR, A_OR, V_sa_d_t_A)

    # ----- 5. 暖房負荷削減量 -----

    # 当該住戸の暖冷房区画iの外気を導入する床下空間に接する床の面積
    if supply_target == '床下':
        A_s_ufvnt_i = algo.calc_A_s_ufvnt_i(i, r_A_ufvnt, A_A, A_MR, A_OR)
    else:
        A_s_ufvnt_i = None

    # 暖冷房負荷計算時に想定した床の熱貫流率 (W/m2K)
    U_s_vert = algo.get_U_s_vert(region, Q)

    # 1時間当たりの集熱部における集熱量 (MJ/h) (19)
    Q_col_d_t = get_Q_col_d_t(V_fan_d_t, Theta_col_opg_d_t, Theta_ex_d_t)

    # 1時間当たりの循環ポンプの稼働時間 (h/h) (6)
    t_cp_d_t = get_t_cp_d_t(hotwater_use, t_fan_d_t, heating_flag_d)

    # 1時間当たりの集熱部における集熱量のうちの給湯利用分 (MJ/h) (11)
    Q_col_W_d_t = get_Q_col_w_d_t(Q_col_d_t, t_cp_d_t)

    # 床下空間または居室へ供給する空気の温度 (℃) (18)
    Theta_sa_d_t = get_Theta_sa_d_t(V_fan_d_t, Theta_col_opg_d_t, Q_col_W_d_t)

    # 床下温度及び地盤またはそれを覆う基礎の表面温度 (℃)
    if supply_target == '床下':
        Theta_uf_d_t, Theta_g_surf_d_t = algo.calc_Theta(
            region=region,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            Q=Q,
            H_OR_C='H',
            # 床下の設定
            r_A_ufvnt=r_A_ufvnt,
            underfloor_insulation=ufv_insulation,
            V_sa_d_t_A=V_sa_d_t_A,
            # 温度・負荷
            Theta_sa_d_t=Theta_sa_d_t,
            Theta_ex_d_t=Theta_ex_d_t,
            L_dash_H_R_d_t=L_dash_H_R_d_t_i,
            L_dash_CS_R_d_t=L_dash_CS_R_d_t_i
        )
    else:
        Theta_uf_d_t, Theta_g_surf_d_t = None, None

    # 暖房設定温度 (℃)
    Theta_prst_H = get_Theta_prst_H()

    # 室内温度 (℃)
    Theta_in_d_t = get_Theta_in_d_t(Theta_prst_H)

    # 空気集熱式太陽熱利用設備による暖房負荷削減量 (1)
    delta_L_dash_H_ass_d_t_i = get_delta_L_dash_H_ass_d_t_i(
        # 床下の設定
        supply_target=supply_target,
        A_s_ufvnt_i=A_s_ufvnt_i,
        U_s_vert=U_s_vert,
        V_sa_d_t_i=V_sa_d_t_i,
        r_sa_d_t=r_sa_d_t,
        # 温度・負荷
        Theta_in_d_t=Theta_in_d_t,
        Theta_uf_d_t=Theta_uf_d_t,
        Theta_ex_d_t=Theta_ex_d_t,
        Theta_sa_d_t=Theta_sa_d_t,
        L_dash_H_R_d_t_i=L_dash_H_R_d_t_i[i - 1],
    )

    return delta_L_dash_H_ass_d_t_i


def get_delta_L_dash_H_ass_d_t_i(A_s_ufvnt_i, L_dash_H_R_d_t_i, Theta_in_d_t, Theta_ex_d_t, Theta_sa_d_t, Theta_uf_d_t,
                                 U_s_vert, V_sa_d_t_i, r_sa_d_t, supply_target):
    """空気集熱式太陽熱利用設備による暖房負荷削減量 (1)

    Args:
      A_s_ufvnt_i(float): 暖冷房区画iの空気を供給する床下空間に接する床の面積 (m2)
      L_dash_H_R_d_t_i(ndarray): 標準住戸の暖冷房区画iの負荷補正前の暖房負荷 (MJ/h)
      Theta_in_d_t(ndarray): 室内温度 (℃)
      Theta_ex_d_t(ndarray): 外気温度 (℃)
      Theta_sa_d_t(ndarray): 床下空間または居室へ供給する空気の温度 (℃)
      Theta_uf_d_t(ndarray): 当該住戸の床下温度 (℃)
      U_s_vert(float): 暖冷房負荷計算時に想定した床の熱貫流率 (W/m2K)
      V_sa_d_t_i(ndarray): 1時間当たりの床下空間または居室へ供給する空気の風量 (m3/h)
      r_sa_d_t(ndarray): 1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (-)
      supply_target(str): 集熱後の空気を供給する先

    Returns:
      ndarray: 空気集熱式太陽熱利用設備による暖房負荷削減量 (MJ/h)

    """

    # 床の温度差係数( -)
    H_floor = get_H_floor()

    # 空気の密度[kg/m3]
    ro_air = get_ro_air()

    # 空気の比熱[kJ/(kgK)]
    c_p_air = get_c_p_air()

    # 床下の熱貫流率[W/m2K]
    U_s = get_U_s()

    if supply_target == '床下':
        # 集熱後の空気を床下空間へ供給する場合

        # (1-2a)
        delta_L_dash_H_ass_d_t_i = (ro_air * c_p_air * V_sa_d_t_i * (Theta_uf_d_t - Theta_in_d_t) * 10 ** (-3)
                                    - U_s * A_s_ufvnt_i * (Theta_in_d_t - Theta_uf_d_t) * 3.6 * 10 ** (-3)
                                    + U_s_vert * A_s_ufvnt_i * (Theta_in_d_t - Theta_ex_d_t) * H_floor * 3.6 * 10 ** (-3))

        # (1-1a)
        delta_L_dash_H_ass_d_t_i[np.logical_or(L_dash_H_R_d_t_i <= 0, r_sa_d_t == 0)] = 0.0

    elif supply_target == '居室':
        # 集熱後の空気を居室へ直接供給する場合

        # (1-2b)
        delta_L_dash_H_ass_d_t_i = ro_air * c_p_air * V_sa_d_t_i * (Theta_sa_d_t - Theta_in_d_t) * 10 ** (-3)

        # (1-2a)
        delta_L_dash_H_ass_d_t_i[np.logical_or(L_dash_H_R_d_t_i <= 0, r_sa_d_t == 0)] = 0.0

    else:
        raise ValueError(supply_target)

    return delta_L_dash_H_ass_d_t_i


def get_delta_L_dash_H_uf_d_t_i():
    """集熱後の空気を供給する空間及び標準住戸の負荷補正前の暖房負荷が0以下かつ、当該時刻において集熱した熱を暖房に利用しない場合

    Args:

    Returns:
      ndarray: 空気集熱式太陽熱利用設備による暖房負荷削減量 (MJ/h)

    """
    return np.zeros(24 * 365)


def get_delta_L_dash_CS_uf_d_t_i():
    """

    Args:

    Returns:
      ndarray: 空気集熱式太陽熱利用設備による暖房負荷削減量 (MJ/h)

    """
    return np.zeros(24 * 365)


def get_H_floor():
    """床の温度差係数 (-)

    Args:

    Returns:
      float: 床の温度差係数 (-)

    """
    return 0.7


def get_Theta_prst_H():
    """暖房設定温度 (℃)

    Args:

    Returns:
      float: 暖房設定温度 (℃)

    """
    return 20.0


def get_Theta_in_d_t(Theta_prst_H):
    """室内温度 (℃)

    Args:
      Theta_prst_H: 暖房設定温度 (℃)

    Returns:
      ndarray: 1時間当たりの室内温度 (℃)

    """
    return np.repeat(Theta_prst_H, 24 * 365)


def get_ro_air():
    """空気の密度 (kg/m3)

    Args:

    Returns:
      float: 空気の密度 (kg/m3)

    """
    return 1.20


def get_c_p_air():
    """空気の比熱 (kJ/(kgK))

    Args:

    Returns:
      float: 空気の比熱 (kJ/(kgK))

    """
    return 1.006


def get_U_s():
    """床下の熱貫流率 (W/m2K)

    Args:

    Returns:
      float: 床下の熱貫流率 (W/m2K)

    """
    return 2.223


# ============================================================================
# 6. 補正集熱量
# ============================================================================

def calc_L_sun_ass_d_t(L_tnk_d, L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t):
    """1時間当たりの空気集熱式太陽熱利用設備における補正集熱量 (MJ/d) (2)

    Args:
      L_tnk_d(ndarray): 1日当たりの給湯部におけるタンク蓄熱量の上限による補正集熱量 (MJ/d)
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における節湯補正給湯熱負荷 (MJ/h)
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの空気集熱式太陽熱利用設備における補正集熱量 (MJ/h)

    """
    # 1日あたりの節湯補正給湯熱負荷 (MJ/d)
    L_dash_k_d = np.sum(L_dash_k_d_t.reshape(365, 24), axis=1)
    L_dash_s_d = np.sum(L_dash_s_d_t.reshape(365, 24), axis=1)
    L_dash_w_d = np.sum(L_dash_w_d_t.reshape(365, 24), axis=1)
    L_dash_b1_d = np.sum(L_dash_b1_d_t.reshape(365, 24), axis=1)
    L_dash_b2_d = np.sum(L_dash_b2_d_t.reshape(365, 24), axis=1)
    L_dash_ba1_d = np.sum(L_dash_ba1_d_t.reshape(365, 24), axis=1)

    # 1日当たりの空気集熱式太陽熱利用設備における補正集熱量 (MJ/d) (3)
    L_sun_ass_d = calc_L_sun_ass_d(L_tnk_d, L_dash_k_d, L_dash_s_d, L_dash_w_d, L_dash_b1_d, L_dash_b2_d, L_dash_ba1_d)
    L_sun_ass_d = np.repeat(L_sun_ass_d, 24)

    # 1日当たりの空気集熱式太陽熱利用設備における補正集熱量 (MJ/d)
    L_sun_ass_d_t = np.zeros(24 * 365)

    # 24時間化
    L_dash_k_d = np.repeat(L_dash_k_d, 24)
    L_dash_s_d = np.repeat(L_dash_s_d, 24)
    L_dash_w_d = np.repeat(L_dash_w_d, 24)
    L_dash_b1_d = np.repeat(L_dash_b1_d, 24)
    L_dash_b2_d = np.repeat(L_dash_b2_d, 24)
    L_dash_ba1_d = np.repeat(L_dash_ba1_d, 24)

    # 1) 1日あたりの節湯補正給湯熱負荷 = 0 の場合
    f1 = (L_dash_k_d + L_dash_s_d + L_dash_w_d + L_dash_b1_d + L_dash_b2_d + L_dash_ba1_d) == 0
    L_sun_ass_d_t[f1] = 0

    # 2) 1日あたりの節湯補正給湯熱負荷 > 0 の場合
    f2 = (L_dash_k_d + L_dash_s_d + L_dash_w_d + L_dash_b1_d + L_dash_b2_d + L_dash_ba1_d) > 0
    L_dash_d = L_dash_k_d + L_dash_s_d + L_dash_w_d + L_dash_b1_d + L_dash_b2_d + L_dash_ba1_d
    L_dash_d_t = L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t
    L_sun_ass_d_t[f2] = L_sun_ass_d[f2] * L_dash_d_t[f2] / L_dash_d[f2]

    return L_sun_ass_d_t


def calc_L_sun_ass_d(L_tnk_d, L_dash_k_d, L_dash_s_d, L_dash_w_d, L_dash_b1_d, L_dash_b2_d, L_dash_ba1_d):
    """1日当たりの空気集熱式太陽熱利用設備における補正集熱量 (MJ/d) (3)

    Args:
      L_tnk_d(ndarray): 1日当たりの給湯部におけるタンク蓄熱量の上限による補正集熱量 (MJ/d)
      L_dash_k_d(ndarray): 1日当たりの台所水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dash_s_d(ndarray): 1日当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dash_w_d(ndarray): 1日当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dash_b1_d(ndarray): 1日当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/d)
      L_dash_b2_d(ndarray): 1日当たりの浴槽自動湯はり時における節湯補正給湯熱負荷 (MJ/d)
      L_dash_ba1_d(ndarray): 1日当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 1日当たりの空気集熱式太陽熱利用設備における補正集熱量 (MJ/d)

    """
    # 給湯部の分担率上限値
    f_sr_uplim = get_f_sr_uplim()

    # 1日当たりの空気集熱式太陽熱利用設備における補正集熱量 (MJ/d)
    L_sun_ass_d = np.clip(
        L_tnk_d,
        None,
        (L_dash_k_d + L_dash_s_d + L_dash_w_d + L_dash_b1_d + L_dash_b2_d + L_dash_ba1_d) * f_sr_uplim
    )

    return L_sun_ass_d


def get_f_sr_uplim():
    """給湯部の分担率上限値 (-)

    Args:

    Returns:
      float: 給湯部の分担率上限値 (-)

    """
    return 0.9


# ============================================================================
# 7. 補機の消費電力量
# ============================================================================

def calc_E_E_W_aux_ass_d_t(hotwater_use, heating_flag_d, region, sol_region, P_alpha, P_beta,
                           A_col, V_fan_P0, m_fan_test, d0, d1, fan_sso, fan_type, pump_sso):
    """1時間当たりの補機の消費電力量のうちの給湯設備への付加分 (kWh/h)

    Args:
      hotwater_use(bool): 空気集熱式太陽熱利用設備が給湯部を有する場合はTrue
      heating_flag_d(ndarray): 暖房日
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      P_alpha(float): 方位角 (°)
      P_beta(tuple): 傾斜角 (°)
      A_col(tuple): 集熱器群の面積 (m2)
      V_fan_P0(float): 空気搬送ファンの送風機特性曲線において機外静圧をゼロとしたときの空気搬送ファンの風量 (m3/h)
      d0(tuple): 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の切片 (-)
      d1(tuple): 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K))
      m_fan_test(tuple): 集熱器群を構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2))
      fan_sso(bool): 空気搬送ファンの自立運転用太陽光発電装置を採用する場合はTrue
      fan_type(str): ファンの種別
      pump_sso(bool): 循環ポンプの自立運転用太陽光発電装置を採用する場合はTrue

    Returns:
      ndarray: 1時間当たりの補機の消費電力量のうちの給湯設備への付加分 (kWh/h)

    """

    from pyhees.section11_1 import load_outdoor, get_Theta_ex
    outdoor = load_outdoor()
    Theta_ex_d_t = get_Theta_ex(region, outdoor)

    # ----- 10 集熱部 -----

    # 空気搬送ファン停止時および稼働時の集熱部の出口における空気温度 (℃)
    Theta_col_nonopg_d_t, Theta_col_opg_d_t = calc_Theta_col(A_col=A_col, P_alpha=P_alpha, P_beta=P_beta,
                                                             V_fan_P0=V_fan_P0, d0=d0, d1=d1, m_fan_test=m_fan_test,
                                                             region=region, sol_region=sol_region,
                                                             Theta_ex_d_t=Theta_ex_d_t)

    # ----- 9. 空気搬送部 -----

    # 1時間当たりの空気搬送ファンの稼働時間 (h/h) (12)
    t_fan_d_t = get_t_fan_d_t(Theta_col_nonopg_d_t, Theta_col_opg_d_t)

    # 1時間当たりの空気搬送ファンの風量 (m3/h) (13)
    V_fan_d_t = get_V_fan_d_t(t_fan_d_t, V_fan_P0)

    # 1時間当たりの空気搬送ファンの消費電力量 (kWh/h) (14)
    E_E_fan_d_t = calc_E_E_fan_d_t(fan_sso, fan_type, V_fan_d_t, t_fan_d_t)

    # 1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (17)
    r_sa_d_t = get_r_sa_d_t(t_fan_d_t, heating_flag_d)

    # ----- 8. 給湯部 -----

    # 1時間当たりの循環ポンプの稼働時間 (h/h) (6)
    t_cp_d_t = get_t_cp_d_t(hotwater_use, t_fan_d_t, heating_flag_d)

    # 1時間当たりの循環ポンプの消費電力量 (kWh/h) (7)
    E_E_cp_d_t = get_E_E_cp_d_t(pump_sso, t_cp_d_t)

    # ----- 7. 補機の消費電力量 -----

    # 1時間当たりの補機の消費電力量のうち暖房設備への付加分 (kWh/h) (4)
    E_E_W_aux_ass_d_t = get_E_E_W_aux_ass_d_t(r_sa_d_t, t_cp_d_t, E_E_fan_d_t, E_E_cp_d_t)

    return E_E_W_aux_ass_d_t


def calc_E_E_H_aux_ass_d_t(hotwater_use, heating_flag_d, region, sol_region, P_alpha, P_beta,
                           A_col, V_fan_P0, m_fan_test, d0, d1, fan_sso, fan_type):
    """1時間当たりの補機の消費電力量のうち暖房設備への付加分 (kWh/h) (4)

    Args:
      hotwater_use(bool): 空気集熱式太陽熱利用設備が給湯部を有する場合はTrue
      heating_flag_d(ndarray): 暖房日
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      P_alpha(float): 方位角 (°)
      P_beta(float): 傾斜角 (°)
      A_col(tuple): 集熱器群の面積 (m2)
      V_fan_P0(float): 空気搬送ファンの送風機特性曲線において機外静圧をゼロとしたときの空気搬送ファンの風量 (m3/h)
      d0(tuple): 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の切片 (-)
      d1(tuple): 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K))
      m_fan_test(tuple): 集熱器群を構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2))
      fan_sso: param fan_type:
      fan_type: 

    Returns:
      ndarray: 1時間当たりの補機の消費電力量のうち暖房設備への付加分 (kWh/h)

    """
    from pyhees.section11_1 import load_outdoor, get_Theta_ex
    outdoor = load_outdoor()
    Theta_ex_d_t = get_Theta_ex(region, outdoor)

    # ----- 10 集熱部 -----

    # 空気搬送ファン停止時および稼働時の集熱部の出口における空気温度 (℃)
    Theta_col_nonopg_d_t, Theta_col_opg_d_t = calc_Theta_col(A_col=A_col, P_alpha=P_alpha, P_beta=P_beta,
                                                             V_fan_P0=V_fan_P0, d0=d0, d1=d1, m_fan_test=m_fan_test,
                                                             region=region, sol_region=sol_region,
                                                             Theta_ex_d_t=Theta_ex_d_t)

    # ----- 9. 空気搬送部 -----

    # 1時間当たりの空気搬送ファンの稼働時間 (h/h) (12)
    t_fan_d_t = get_t_fan_d_t(Theta_col_nonopg_d_t, Theta_col_opg_d_t)

    # 1時間当たりの空気搬送ファンの風量 (m3/h) (13)
    V_fan_d_t = get_V_fan_d_t(t_fan_d_t, V_fan_P0)

    # 1時間当たりの空気搬送ファンの消費電力量 (kWh/h) (14)
    E_E_fan_d_t = calc_E_E_fan_d_t(fan_sso, fan_type, V_fan_d_t, t_fan_d_t)

    # 1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (17)
    r_sa_d_t = get_r_sa_d_t(t_fan_d_t, heating_flag_d)

    # ----- 8. 給湯部 -----

    # 1時間当たりの循環ポンプの稼働時間 (h/h) (6)
    t_cp_d_t = get_t_cp_d_t(hotwater_use, t_fan_d_t, heating_flag_d)

    # ----- 7. 補機の消費電力量 -----

    # 1時間当たりの補機の消費電力量のうち暖房設備への付加分 (kWh/h) (4)
    E_E_H_aux_ass_d_t = get_E_E_H_aux_ass_d_t(r_sa_d_t, t_cp_d_t, E_E_fan_d_t)

    return E_E_H_aux_ass_d_t


def get_E_E_H_aux_ass_d_t(r_sa_d_t, t_cp_d_t, E_E_fan_d_t):
    """1時間当たりの補機の消費電力量のうち暖房設備への付加分 (kWh/h) (4)

    Args:
      r_sa_d_t(ndarray): 1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (-)
      t_cp_d_t(ndarray): 1時間当たりの循環ポンプの稼働時間 (h/h)
      E_E_fan_d_t(ndarray): 1時間当たりの空気搬送ファンの消費電力量 (kWh/h)

    Returns:
      ndarray: 1時間当たりの補機の消費電力量のうち暖房設備への付加分 (kWh/h)

    """

    E_E_H_aux_ass_d_t = np.zeros(24 * 365)

    # (4)
    f = np.logical_and(0 < r_sa_d_t, t_cp_d_t == 0)
    E_E_H_aux_ass_d_t[f] = E_E_fan_d_t[f]

    return E_E_H_aux_ass_d_t


def get_E_E_W_aux_ass_d_t(r_sa_d_t, t_cp_d_t, E_E_fan_d_t, E_E_cp_d_t):
    """1時間当たりの補機の消費電力量のうち給湯設備への付加分 (kWh/h)

    Args:
      r_sa_d_t(ndarray): 1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (-)
      t_cp_d_t(ndarray): 1時間当たりの循環ポンプの稼働時間 (h/h)
      E_E_fan_d_t(ndarray): 1時間当たりの空気搬送ファンの消費電力量 (kWh/h)
      E_E_cp_d_t(ndarray): 1時間当たりの循環ポンプの消費電力量 (kWh/h)

    Returns:
      ndarray: 1時間当たりの補機の消費電力量のうち給湯設備への付加分 (kWh/h)

    """
    E_E_W_aux_ass_d_t = np.zeros(24 * 365)

    # (5)
    f = np.logical_and(r_sa_d_t == 0, 0 < t_cp_d_t)
    E_E_W_aux_ass_d_t[f] = E_E_fan_d_t[f] + E_E_cp_d_t[f]

    return E_E_W_aux_ass_d_t


# ============================================================================
# 8. 給湯部
# ============================================================================

# ============================================================================
# 8.1 循環ポンプの稼働時間
# ============================================================================

def get_t_cp_d_t(hotwater_use, t_fan_d_t, heating_flag_d):
    """1時間当たりの循環ポンプの稼働時間 (h/h) (6)

    Args:
      hotwater_use(bool): 空気集熱式太陽熱利用設備が給湯部を有する場合はTrue
      t_fan_d_t(ndarray): 1時間当たりの空気搬送ファンの稼働時間 (h/h)
      heating_flag_d(bool): 暖房日であればTrue

    Returns:
      ndarray: 1時間当たりの循環ポンプの稼働時間 (h/h)

    """
    t_cp_d_t = np.zeros(24 * 365)

    if hotwater_use == False:
        # (6-1) 集熱した熱を給湯に使用しない場合は循環ポンプは稼働しない
        pass
    else:
        # 暖房日を時間ごとの配列へ展開 365->24*365
        heating_flag_d_t = np.repeat(heating_flag_d, 24)

        # (6-2) 空気搬送ファンが稼働しているが非暖房日の場合は循環ポンプは稼働する
        f = np.logical_and(0 < t_fan_d_t, heating_flag_d_t == False)
        t_cp_d_t[f] = 1.0

    return t_cp_d_t


# ============================================================================
# 8.2 循環ポンプの消費電力量
# ============================================================================

def get_E_E_cp_d_t(pump_sso, t_cp_d_t):
    """1時間当たりの循環ポンプの消費電力量 (kWh/h) (7)

    Args:
      pump_sso(bool): 循環ポンプの自立運転用太陽光発電装置を採用する場合はTrue
      t_cp_d_t(ndarray): 1時間当たりの空気搬送ファンの稼働時間 (h/h)

    Returns:
      ndarray: 1時間当たりの循環ポンプの消費電力量 (kWh/h)

    """
    if pump_sso == True:
        # 循環ポンプの自立運転用太陽光発電装置を採用する場合は、循環ポンプの消費電力を計上しない
        E_E_cp_d_t = np.zeros(24 * 365)
    else:
        # 循環ポンプの消費電力[W]
        P_cp = get_P_cp()

        # 1時間当たりの循環ポンプの消費電力量 (kWh/h)
        E_E_cp_d_t = P_cp * t_cp_d_t * 10 ** (-3)

    return E_E_cp_d_t


def get_P_cp():
    """循環ポンプの消費電力[W]

    Args:

    Returns:
      float: 循環ポンプの消費電力[W]

    """
    return 80.0


# ============================================================================
# 8.3 タンク蓄熱量の上限による補正集熱量
# ============================================================================

def calc_L_tnk_d(Q_d, W_tnk, Theta_wtr_d):
    """1日当たりの給湯部におけるタンク蓄熱量の上限による補正集熱量 (MJ/d) (8)

    Args:
      Q_d(ndarray): 1日当たりの基準集熱量 (MJ/d)
      W_tnk(float): 給湯部のタンク容量 (L)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: 1日当たりの給湯部におけるタンク蓄熱量の上限による補正集熱量 (MJ/d)

    """
    # 給湯部のタンク蓄熱量の上限 (MJ/d) (9)
    HC_tnk_d = get_HC_tnk_d(W_tnk, Theta_wtr_d)

    # 給湯部のタンク有効利用率
    alpha_tnk_d = get_alpha_tnk_d()

    # 1日当たりの給湯部におけるタンク蓄熱量の上限による補正集熱量 (MJ/d) (8)
    L_tnk_d = np.clip(
        Q_d,
        None,
        HC_tnk_d * alpha_tnk_d
    )

    return L_tnk_d


def get_alpha_tnk_d():
    """給湯部のタンク有効利用率 [1/d]

    Args:

    Returns:
      ndarray: 給湯部のタンク有効利用率 [1/d]

    """
    # 給湯タンク有効利用率は1.0固定とする
    return np.ones(365)


def get_HC_tnk_d(W_tnk, Theta_wtr_d):
    """給湯部のタンク蓄熱量の上限 (MJ/d) (9)

    Args:
      W_tnk(float): 給湯部のタンク容量 (L)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: 給湯部のタンク蓄熱量の上限 (MJ/d)

    """
    # 給湯部のタンク内温度 (℃)
    Theta_tnk = 65.0

    # 給湯部のタンク蓄熱量の上限 (MJ/d)
    HC_tnk_d = (Theta_tnk - Theta_wtr_d) * W_tnk * 4.186 * 10 ** (-3)

    return HC_tnk_d


# ============================================================================
# 8.4 基準集熱量
# ============================================================================

def calc_Q_d(Q_col_d_t, t_cp_d_t):
    """1日当たりの基準集熱量 (MJ/d) (10)

    Args:
      Q_col_d_t(ndarray): 1時間当たりの集熱部における集熱量 (MJ/d)
      t_cp_d_t(ndarray): 1時間当たりの循環ポンプの稼働時間 (h/h)

    Returns:
      ndarray: 1日当たりの基準集熱量 (MJ/d)

    """
    # 1時間当たりの集熱部における集熱量のうちの給湯利用分 (11)
    Q_col_w_d_t = get_Q_col_w_d_t(Q_col_d_t, t_cp_d_t)

    # 給湯部のシステム効率
    f_s = 0.85

    # 1日当たりの基準集熱量 (MJ/d) (10)
    tmp = Q_col_w_d_t * f_s
    Q_d = np.sum(tmp.reshape(365, 24), axis=1)

    return Q_d


def get_Q_col_w_d_t(Q_col_d_t, t_cp_d_t):
    """1時間当たりの集熱部における集熱量のうちの給湯利用分 (MJ/h) (11)

    Args:
      Q_col_d_t(ndarray): 1時間当たりの集熱部における集熱量 (MJ/d)
      t_cp_d_t(ndarray): 1時間当たりの循環ポンプの稼働時間 (h/h)

    Returns:
      ndarray: 1時間当たりの集熱部における集熱量のうちの給湯利用分 (MJ/h)

    """
    # 給湯部の熱交換効率
    f_hx = 0.25

    # 1時間当たりの集熱部における集熱量のうちの給湯利用分 (MJ/h) (11)
    Q_col_w_d_t = Q_col_d_t * f_hx * t_cp_d_t

    return Q_col_w_d_t


# ============================================================================
# 9. 空気搬送部
# ============================================================================

# ============================================================================
# 9.1 空気搬送ファンの稼働時間
# ============================================================================

def get_t_fan_d_t(Theta_col_nonopg_d_t, Theta_col_opg_d_t):
    """1時間当たりの空気搬送ファンの稼働時間 (h/h) (12)

    Args:
      Theta_col_nonopg_d_t(ndarray): 空気搬送ファン停止時の集熱部の出口における空気温度 (℃)
      Theta_col_opg_d_t(ndarray): 空気搬送ファン稼働時の集熱部の出口における空気温度 (℃)

    Returns:
      ndarray: 1時間当たりの空気搬送ファンの稼働時間 (h/h)

    """
    # 空気搬送ファン稼働時の集熱部の出口における空気温度が25度より大、かつ
    # 空気搬送ファン停止時の集熱部の出口における空気温度が30度以上の場合に稼働する
    t_fan_d_t = np.zeros(24 * 365)
    f = np.logical_and(30 <= Theta_col_nonopg_d_t, 25 < Theta_col_opg_d_t)
    t_fan_d_t[f] = 1

    return t_fan_d_t


# ============================================================================
# 9.2 空気搬送ファンの風量
# ============================================================================

def get_V_fan_d_t(t_fan_d_t, V_fan_P0):
    """1時間当たりの空気搬送ファンの風量 (m3/h) (13)

    Args:
      t_fan_d_t(ndarray): 1時間当たりの空気搬送ファンの稼働時間 (h/h)
      V_fan_P0(float): 空気搬送ファンの送風機特性曲線において機外静圧をゼロとした時の空気搬送ファンの風量 (m3/h)

    Returns:
      ndarray: 1時間当たりの空気搬送ファンの風量 (m3/h)

    """
    V_fan_d_t = V_fan_P0 * t_fan_d_t
    return V_fan_d_t


# ============================================================================
# 9.3 空気搬送ファンの消費電力量
# ============================================================================

def calc_E_E_fan_d_t(fan_sso, fan_type, V_fan_d_t, t_fan_d_t):
    """1時間当たりの空気搬送ファンの消費電力量 (kWh/h) (14)

    Args:
      fan_sso(bool): 空気搬送ファンの自立運転用太陽光発電装置を採用する場合はTrue
      fan_type(str): ファンの種別
      V_fan_d_t(ndarray): 1時間当たりの空気搬送ファンの風量 (m3/h)
      t_fan_d_t(ndarray): 1時間当たりの空気搬送ファンの稼働時間 (h/h)

    Returns:
      ndarray: 1時間当たりの空気搬送ファンの消費電力量 (kWh/h)

    """
    if fan_sso == True:
        # 空気搬送ファンの自立運転用太陽光発電装置を採用する場合は、空気搬送ファンの消費電力を計上しない
        E_E_fan_d_t = np.zeros(24 * 365)
    else:
        # 空気搬送ファンの比消費電力 (W/(m3/h))
        f_SFP = get_f_SFP(fan_type)

        # 1時間当たりの空気搬送ファンの消費電力量 (kWh/h) (14)
        E_E_fan_d_t = f_SFP * V_fan_d_t * t_fan_d_t * 10 ** (-3)

    return E_E_fan_d_t


def get_f_SFP(fan_type):
    """空気搬送ファンの比消費電力 (W/(m3/h))

    Args:
      fan_type(str): ファンの種別

    Returns:
      float: 空気搬送ファンの比消費電力 (W/(m3/h))

    """
    if fan_type == 'AC':
        return get_table_1()[0]
    elif fan_type == 'DC':
        return get_table_1()[1]
    else:
        raise ValueError(fan_type)


def get_table_1():
    """表1 空気搬送ファンの比消費電力 f_SFP

    Args:

    Returns:
      list: 表1 空気搬送ファンの比消費電力 f_SFP

    """
    table_1 = (0.4, 0.2)
    return table_1


# ============================================================================
# 9.4 床下空間または居室へ供給する空気の風量
# ============================================================================

def get_V_sa_d_t_i(i, A_HCZ_i, A_MR, A_OR, V_sa_d_t_A):
    """1時間当たりの床下空間または居室へ供給する空気の風量 (m3/h) (15)

    Args:
      i(int): 暖冷房区画の番号
      A_HCZ_i(float): 暖冷房区画iの床面積 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      V_sa_d_t_A(ndarray): 床下空間または居室へ供給する1時間当たりの空気の風量の合計

    Returns:
      ndarray: 1時間当たりの床下空間または居室へ供給する空気の風量 (m3/h)

    """
    if i in [1, 2, 3, 4, 5]:
        return V_sa_d_t_A * A_HCZ_i / (A_MR + A_OR)

    elif i in [6, 7, 8, 9, 10, 11, 12]:
        return np.zeros(24 * 365)

    else:
        raise ValueError(i)


def get_V_sa_d_t_A(V_fan_d_t, r_sa_d_t):
    """床下空間または居室へ供給する1時間当たりの空気の風量の合計 (m3/h) (16)

    Args:
      V_fan_d_t(ndarray): 1時間当たりの空気搬送ファンの風量 (m3/h)
      r_sa_d_t(ndarray): 1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (-)

    Returns:
      ndarray: 床下空間または居室へ供給する1時間当たりの空気の風量の合計 (m3/h)

    """
    V_sa_d_t_A = V_fan_d_t * r_sa_d_t

    return V_sa_d_t_A


def get_r_sa_d_t(t_fan_d_t, heating_flag_d):
    """1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (17)

    Args:
      t_fan_d_t(ndarray): 1時間当たりの空気搬送ファンの稼働時間 (h/h)
      heating_flag_d(ndarray): 暖房日であればTrue

    Returns:
      ndarray: 1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (-)

    """
    # 暖房日を時間ごとの配列へ展開 365->24*365
    heating_flag_d_t = np.repeat(heating_flag_d, 24)

    # 空気搬送ファンの風量が0より多きい、かつ、暖房日である
    r_sa_d_t = np.zeros(24 * 365)
    f = np.logical_and(0.0 < t_fan_d_t, heating_flag_d_t == True)
    r_sa_d_t[f] = 1.0

    return r_sa_d_t


# ============================================================================
# 9.5 床下空間または居室へ供給する空気の温度
# ============================================================================

def get_Theta_sa_d_t(V_fan_d_t, Theta_col_opg_d_t, Q_col_W_d_t):
    """床下空間または居室へ供給する空気の温度 (℃) (18)

    Args:
      V_fan_d_t(ndarray): 1時間当たりの空気搬送ファンの風量 (m3/h)
      Theta_col_opg_d_t(ndarray): 空気搬送ファンの稼働時の集熱部の出口における空気温度 (℃)
      Q_col_W_d_t(ndarray): 1時間当たりの集熱部における集熱量のうちの給湯利用分 (MJ/h)

    Returns:
      ndarray: 床下空間または居室へ供給する空気の温度 (℃)

    """
    # 空気の密度 [kg/m3]
    ro_air = 1.20

    # 空気の比熱 [kJ/(kgK)]
    c_p_air = 1.006

    # 床下空間または居室へ供給する空気の温度 (℃) (18)
    Theta_sa_d_t = np.copy(Theta_col_opg_d_t)
    f = V_fan_d_t > 0
    Theta_sa_d_t[f] = Theta_col_opg_d_t[f] - (Q_col_W_d_t[f] / (ro_air * c_p_air * V_fan_d_t[f]))

    return Theta_sa_d_t


# ============================================================================
# 10. 集熱部
# ============================================================================

def calc_Theta_col(A_col, P_alpha, P_beta, V_fan_P0, d0, d1, m_fan_test, region, sol_region, Theta_ex_d_t):
    """空気搬送ファン停止時および稼働時の集熱部の出口における空気温度 (℃)

    Args:
      A_col(tuple): 集熱器群の面積 (m2)
      P_alpha(float): 方位角 (°)
      P_beta(tuple): 傾斜角 (°)
      V_fan_P0(float): 空気搬送ファンの送風機特性曲線において機外静圧をゼロとしたときの空気搬送ファンの風量 (m3/h)
      d0(tuple): 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の切片 (-)
      d1(tuple): 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K))
      m_fan_test(tuple): 集熱器群を構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2))
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      Theta_ex_d_t(ndarray): 外気温度 (℃)

    Returns:
      tuple: 空気搬送ファン停止時および稼働時の集熱部の出口における空気温度 (℃)

    """
    # 集熱器群の数
    n = len(A_col)

    # 作業領域の確保
    V_col_j_d_t = np.zeros((n, 24 * 365))
    Theta_col_nonopg_j_d_t = np.zeros((n, 24 * 365))
    Theta_col_opg_j_d_t = np.zeros((n, 24 * 365))

    for j in range(1, n + 1):
        # 空気搬送ファン稼働時に集熱器群jを流れる空気の体積流量 (m3/h) (24)
        V_col_j_d_t[j - 1, :] = get_V_col_j_d_t(V_fan_P0, A_col[j - 1], A_col)

        # 空気搬送ファン停止時の集熱器群jの出口における空気温度 (℃) (22)
        Theta_col_nonopg_j_d_t[j - 1, :] = calc_Theta_col_nonopg_j_d_t(
            P_alpha_j=P_alpha,
            P_beta_j=P_beta[j - 1],
            region=region,
            sol_region=sol_region,
            Theta_ex_d_t=Theta_ex_d_t,
            d0_j=d0[j - 1],
            d1_j=d1[j - 1]
        )

        # 集熱器群jを構成する集熱器の総合熱損失係数 (25)
        U_c_j = get_U_c_j(m_fan_test[j - 1], d1[j - 1])

        # 空気搬送ファン稼働時に集熱器群jを流れる空気の体積流量 (24)
        V_col_j_d_t[j - 1, :] = get_V_col_j_d_t(V_fan_P0, A_col[j - 1], A_col)

        # 空気搬送ファン稼働時の集熱器群jの出口における空気温度 (℃) (23)
        Theta_col_opg_j_d_t[j - 1, :] = get_Theta_col_opg_j_d_t(
            V_col_j_d_t=V_col_j_d_t[j - 1],
            A_col_j=A_col[j - 1],
            U_c_j=U_c_j,
            Theta_col_nonopg_j_d_t=Theta_col_nonopg_j_d_t[j - 1],
            Theta_ex_d_t=Theta_ex_d_t
        )
    # 空気搬送ファン稼働時の集熱部の出口における空気温度 (℃) (21)
    Theta_col_opg_d_t = get_Theta_col_opg_d_t(Theta_col_opg_j_d_t, V_col_j_d_t)

    # 空気搬送ファン停止時の集熱部の出口における空気温度 (℃) (20)
    Theta_col_nonopg_d_t = get_Theta_col_nonopg_d_t(Theta_col_nonopg_j_d_t, V_col_j_d_t)

    return Theta_col_nonopg_d_t, Theta_col_opg_d_t


# ============================================================================
# 10.1 集熱量
# ============================================================================

def get_Q_col_d_t(V_fan_d_t, Theta_col_opg_d_t, Theta_ex_d_t):
    """1時間当たりの集熱部における集熱量 (MJ/h) (19)

    Args:
      V_fan_d_t(ndarray): 1時間当たりの空気搬送ファンの風量 (m3/h)
      Theta_col_opg_d_t(ndarray): 空気搬送ファン稼働時の集熱部の出口における空気温度 (℃)
      Theta_ex_d_t(ndarray): 外気温度 (℃)

    Returns:
      ndarray: 1時間当たりの集熱部における集熱量 (MJ/h)

    """
    # 空気の密度 [kg/m3]
    ro_air = 1.20

    # 空気の比熱 [kJ/(kgK)]
    c_p_air = 1.006

    # 1時間当たりの集熱部における集熱量 (MJ/h) (19)
    Q_col_d_t = ro_air * c_p_air * V_fan_d_t * (Theta_col_opg_d_t - Theta_ex_d_t) * 10 ** (-3)

    return Q_col_d_t


# ============================================================================
# 10.2 空気搬送ファン停止時の集熱部の出口における空気温度
# ============================================================================

def get_Theta_col_nonopg_d_t(Theta_col_nonopg_j_d_t, V_col_j_d_t):
    """空気搬送ファン停止時の集熱部の出口における空気温度 (℃) (20)

    Args:
      Theta_col_nonopg_j_d_t(ndarray): 空気搬送ファン停止時の集熱器群ごとの出口における空気温度 (℃)
      V_col_j_d_t(ndarray): 空気搬送ファン稼働時に集熱器群ごとに流れる空気の体積流量 (m3/h)

    Returns:
      ndarray: 空気搬送ファン停止時の集熱部の出口における空気温度 (℃)

    """
    # 集熱器群の数 (-)
    n = Theta_col_nonopg_j_d_t.shape[0]

    # 空気搬送ファン停止時の集熱部の出口における空気温度 (℃)
    Theta_col_nonopg_d_t = (np.sum([Theta_col_nonopg_j_d_t[j] * V_col_j_d_t[j] for j in range(n)], axis=0)
                            / np.sum([V_col_j_d_t[j] for j in range(n)], axis=0))

    return Theta_col_nonopg_d_t


# ============================================================================
# 10.3 空気搬送ファン稼働時の集熱部の出口における空気温度
# ============================================================================

def get_Theta_col_opg_d_t(Theta_col_opg_j_d_t, V_col_j_d_t):
    """空気搬送ファン稼働時の集熱部の出口における空気温度 (℃) (21)

    Args:
      Theta_col_opg_j_d_t(ndarray): 空気搬送ファン稼働時の集熱器群ごとの出口における空気温度 (℃)
      V_col_j_d_t(ndarray): 空気搬送ファン稼働時に集熱器群ごとの空気の体積流量 (m3/h)

    Returns:
      ndarray: 空気搬送ファン稼働時の集熱部の出口における空気温度 (℃)

    """
    # 集熱器群の数 (-)
    n = Theta_col_opg_j_d_t.shape[0]

    # 空気搬送ファン稼働時の集熱部の出口における空気温度 (℃) (21)
    Theta_col_opg_d_t = (np.sum([Theta_col_opg_j_d_t[j] * V_col_j_d_t[j] for j in range(n)], axis=0)
                         / np.sum([V_col_j_d_t[j] for j in range(n)], axis=0))

    return Theta_col_opg_d_t


# ============================================================================
# 10.4 空気搬送ファン停止時の集熱器群の出口における空気温度
# ============================================================================

def calc_Theta_col_nonopg_j_d_t(P_alpha_j, P_beta_j, region, sol_region, Theta_ex_d_t, d0_j=None, d1_j=None):
    """空気搬送ファン停止時の集熱器群jの出口における空気温度 (℃) (22)

    Args:
      P_alpha_j(float): 方位角 (°)
      P_beta_j(float): 傾斜角 (°)
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      Theta_ex_d_t(ndarray): 外気温度 (℃)
      d0_j(float, optional): 集熱器群jを構成する集熱器の集熱効率特性線図一次近似式の切片 (-) (Default value = None)
      d1_j(float, optional): 集熱器群jを構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K)) (Default value = None)

    Returns:
      ndarray: 空気搬送ファン停止時の集熱器群jの出口における空気温度 (℃)

    """
    # 日射量データの読み込み
    from pyhees.section11_2 import load_solrad, get_Theta_ex
    solrad = load_solrad(region, sol_region)

    # 単位面積当たりの平均日射量[W/m2]
    I_s_j_d_t = calc_I_s_d_t(P_alpha_j, P_beta_j, solrad)

    # 集熱効率特性線図一次近似式の切片および傾きの解決
    if d0_j is None:
        d0_j = get_d0_default()
    if d1_j is None:
        d1_j = get_d1_default()

    # 空気搬送ファン停止時の集熱器群jの出口における空気温度(℃)
    Theta_col_nonopg_j_d_t = d0_j / d1_j * I_s_j_d_t + Theta_ex_d_t

    return Theta_col_nonopg_j_d_t


def get_d0_default():
    """集熱効率特性線図一次近似式の切片(規定値)[-]

    Args:

    Returns:
      float: 集熱効率特性線図一次近似式の切片(規定値)[-]

    """
    return 0.1


def get_d1_default():
    """集熱効率特性線図一次近似式の傾き(規定値)[m2K]

    Args:

    Returns:
      float: 集熱効率特性線図一次近似式の傾き(規定値)[m2K]

    """
    return 2.0


# ============================================================================
# 10.5 空気搬送ファン稼働時の集熱器群の出口における空気温度
# ============================================================================

def get_Theta_col_opg_j_d_t(V_col_j_d_t, A_col_j, U_c_j, Theta_col_nonopg_j_d_t, Theta_ex_d_t):
    """空気搬送ファン稼働時の集熱器群jの出口における空気温度 (℃) (23)

    Args:
      V_col_j_d_t(ndarray): 空気搬送ファン稼働時に集熱器群jを流れる空気の体積流量
      A_col_j(float): 集熱器群jの面積 (m2)
      U_c_j(float): 集熱器群jを構成する集熱器の総合熱損失係数
      Theta_col_nonopg_j_d_t(ndarray): 空気搬送ファン停止時の集熱器群jの出口における空気温度 (℃)
      Theta_ex_d_t(ndarray): 外気温度 (℃)

    Returns:
      ndarray: 空気搬送ファン稼働時の集熱器群jの出口における空気温度 (℃)

    """
    # 空気の密度 [kg/m3]
    ro_air = 1.20

    # 空気の比熱 [kJ/(kgK)]
    c_p_air = 1.006

    # 空気搬送ファン稼働時の集熱器群jの出口における空気温度 (℃) (23)
    Theta_col_opg_j_d_t = (Theta_col_nonopg_j_d_t + (Theta_ex_d_t - Theta_col_nonopg_j_d_t)
                           * np.exp(- (U_c_j * A_col_j) / (c_p_air * ro_air * V_col_j_d_t / 3600 * 10 ** 3)))

    return Theta_col_opg_j_d_t


def get_V_col_j_d_t(V_fan_P0_j, A_col_j, A_col):
    """空気搬送ファン稼働時に集熱器群jを流れる空気の体積流量 (m3/h) (24)

    Args:
      V_fan_P0_j(float): 空気搬送ファンの送風機特性曲線において機外静圧をゼロとしたときの空気搬送ファンの風量 (m3/h)
      A_col_j(float): 集熱器群jの面積 (m2)
      A_col(tuple): 集熱器群の面積 (m2)

    Returns:
      float: 空気搬送ファン稼働時に集熱器群jを流れる空気の体積流量 (m3/h)

    """
    V_col_j_d_t = V_fan_P0_j * A_col_j / sum(A_col)
    return V_col_j_d_t


def get_U_c_j(m_fan_test_j=None, d1_j=None):
    """集熱器群jを構成する集熱器の総合熱損失係数 (25)

    Args:
      m_fan_test_j(float, optional): 集熱器群jを構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2)) (Default value = None)
      d1_j(float, optional): 集熱器群jを構成する集熱器の集熱効率特性線図一次近似式の傾き (W/m2K) (Default value = None)

    Returns:
      float: 集熱器群jを構成する集熱器の総合熱損失係数

    """
    # 空気の比熱 [kJ/(kgK)]
    c_p_air = 1.006

    if m_fan_test_j is None:
        m_fan_test_j = 0.0107
    if d1_j is None:
        d1_j = 2.0

    # 集熱器群jを構成する集熱器の総合熱損失係数 (25)
    U_c_j = - c_p_air * m_fan_test_j * 10 ** 3 * np.log(1 - 1 / (c_p_air * m_fan_test_j * 10 ** 3) * d1_j)

    return U_c_j


if __name__ == '__main__':
    spec = {

        # 空気搬送ファンの自立運転用太陽光発電装置の採用
        'pump_sso': False,

        # 空気搬送ファンの種別
        'fan_type': 'DC',

        # 機外静圧をゼロとした時の空気搬送ファンの風量[m3/h]
        'V_fan_P0': 2.0,

        # 集熱した熱の給湯への利用
        'use_hotwater': True,

        # 集熱後の空気を供給する空間
        'supply_target': '床下',

        # 集熱器群
        'collectors': [

            # 集熱器群その1
            {
                # 集熱器群1の面積[m2]
                'A_col': 1.0,
                'P_alpha': 0.1,
                'P_beta': 0.2,
                'd0': 0.1,
                'd1': 2.0,
                'm_fan_test': 0.0107
            }
        ]
    }
