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

    :param i: 暖冷房区画の番号
    :type i: int
    :param supply_target: 集熱後の空気を供給する先
    :type supply_target: str
    :param L_dash_H_R_d_t_i: 空気集熱式太陽熱利用設備による暖房負荷削減量 (MJ/h)
    :type L_dash_H_R_d_t_i: ndarray
    :param L_dash_CS_R_d_t_i: 標準住戸の負荷補正前の冷房顕熱負荷 （MJ/h）
    :type L_dash_CS_R_d_t_i: ndarray
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param A_HCZ_i: 暖冷房区画iの床面積 (m2)
    :type A_HCZ_i: float
    :param A_A: 床面積の合計(m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積(m2)
    :type A_MR: float
    :param A_OR: その他の拠出の床面積(m2)
    :type A_OR: float
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param hotwater_use: 空気集熱式太陽熱利用設備が給湯部を有する場合はTrue
    :type hotwater_use: bool
    :param Theta_ex_d_t: 外気温度 (℃)
    :type Theta_ex_d_t: ndarray
    :param P_alpha: 方位角 (°)
    :type P_alpha: float
    :param P_beta: 傾斜角 (°)
    :type P_beta: float
    :param A_col: 集熱器群の面積 (m2)
    :type A_col: tuple
    :param V_fan_P0: 空気搬送ファンの送風機特性曲線において機外静圧をゼロとしたときの空気搬送ファンの風量 (m3/h)
    :type V_fan_P0: float
    :param m_fan_test: 集熱器群を構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2))
    :type m_fan_test: tuple
    :param d0: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の切片 (-)
    :type d0: tuple
    :param d1: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K))
    :type d1: tuple
    :param ufv_insulation: 床下空間が断熱空間内である場合はTrue
    :type ufv_insulation: bool
    :param r_A_ufvnt: 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
    :type r_A_ufvnt: float
    :return: 空気集熱式太陽熱利用設備による暖房負荷削減量
    :rtype: ndarray
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

    :param A_s_ufvnt_i: 暖冷房区画iの空気を供給する床下空間に接する床の面積 (m2)
    :type A_s_ufvnt_i: float
    :param L_dash_H_R_d_t_i: 標準住戸の暖冷房区画iの負荷補正前の暖房負荷 (MJ/h)
    :type L_dash_H_R_d_t_i: ndarray
    :param Theta_in_d_t: 室内温度 (℃)
    :type Theta_in_d_t: ndarray
    :param Theta_ex_d_t: 外気温度 (℃)
    :type Theta_ex_d_t: ndarray
    :param Theta_sa_d_t: 床下空間または居室へ供給する空気の温度 (℃)
    :type Theta_sa_d_t: ndarray
    :param Theta_uf_d_t: 当該住戸の床下温度 (℃)
    :type Theta_uf_d_t: ndarray
    :param U_s_vert: 暖冷房負荷計算時に想定した床の熱貫流率 (W/m2K)
    :type U_s_vert: float
    :param V_sa_d_t_i: 1時間当たりの床下空間または居室へ供給する空気の風量 (m3/h)
    :type V_sa_d_t_i: ndarray
    :param r_sa_d_t: 1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (-)
    :type r_sa_d_t: ndarray
    :param supply_target: 集熱後の空気を供給する先
    :type supply_target: str
    :return: 空気集熱式太陽熱利用設備による暖房負荷削減量 (MJ/h)
    :rtype: ndarray
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

    :return:　空気集熱式太陽熱利用設備による暖房負荷削減量 (MJ/h)
    :rtype: ndarray
    """
    return np.zeros(24 * 365)


def get_delta_L_dash_CS_uf_d_t_i():
    """

    :return:
    :rtype:
    """
    return np.zeros(24 * 365)


def get_H_floor():
    """床の温度差係数 (-)

    :return: 床の温度差係数 (-)
    :rtype: float
    """
    return 0.7


def get_Theta_prst_H():
    """暖房設定温度 (℃)

    :return: 暖房設定温度 (℃)
    :rtype: float
    """
    return 20.0


def get_Theta_in_d_t(Theta_prst_H):
    """室内温度 (℃)

    :param Theta_prst_H: 暖房設定温度 (℃)
    :type: float
    :return: 1時間当たりの室内温度 (℃)
    :rtype: ndarray
    """
    return np.repeat(Theta_prst_H, 24 * 365)


def get_ro_air():
    """空気の密度 (kg/m3)

    :return: 空気の密度 (kg/m3)
    :rtype: float
    """
    return 1.20


def get_c_p_air():
    """空気の比熱 (kJ/(kgK))

    :return: 空気の比熱 (kJ/(kgK))
    :rtype: float
    """
    return 1.006


def get_U_s():
    """ 床下の熱貫流率 (W/m2K)

    :return: 床下の熱貫流率 (W/m2K)
    :rtype: float
    """
    return 2.223


# ============================================================================
# 6. 補正集熱量
# ============================================================================

def calc_L_sun_ass_d_t(L_tnk_d, L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t):
    """1時間当たりの空気集熱式太陽熱利用設備における補正集熱量 (MJ/d) (2)

    :param L_tnk_d: 1日当たりの給湯部におけるタンク蓄熱量の上限による補正集熱量 (MJ/d)
    :type L_tnk_d: ndarray
    :param L_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_k_d_t: ndarray
    :param L_dash_s_d_t: 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_s_d_t: ndarray
    :param L_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_w_d_t: ndarray
    :param L_dash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b1_d_t: ndarray
    :param L_dash_b2_d_t: 1時間当たりの浴槽自動湯はり時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b2_d_t: ndarray
    :param L_dash_ba1_d_t: 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_ba1_d_t: ndarray
    :return: 1時間当たりの空気集熱式太陽熱利用設備における補正集熱量 (MJ/h)
    :rtype: ndarray
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

    :param L_tnk_d: 1日当たりの給湯部におけるタンク蓄熱量の上限による補正集熱量 (MJ/d)
    :type L_tnk_d: ndarray
    :param L_dash_k_d: 1日当たりの台所水栓における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_k_d: ndarray
    :param L_dash_s_d: 1日当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_s_d: ndarray
    :param L_dash_w_d: 1日当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_w_d: ndarray
    :param L_dash_b1_d: 1日当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_b1_d: ndarray
    :param L_dash_b2_d: 1日当たりの浴槽自動湯はり時における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_b2_d: ndarray
    :param L_dash_ba1_d: 1日当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_ba1_d: ndarray
    :return: 1日当たりの空気集熱式太陽熱利用設備における補正集熱量 (MJ/d)
    :rtype: ndarray
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

    :return: 給湯部の分担率上限値 (-)
    :rtype: float
    """
    return 0.9


# ============================================================================
# 7. 補機の消費電力量
# ============================================================================

def calc_E_E_W_aux_ass_d_t(hotwater_use, heating_flag_d, region, sol_region, P_alpha, P_beta,
                           A_col, V_fan_P0, m_fan_test, d0, d1, fan_sso, fan_type, pump_sso):
    """1時間当たりの補機の消費電力量のうちの給湯設備への付加分 (kWh/h)

    :param hotwater_use: 空気集熱式太陽熱利用設備が給湯部を有する場合はTrue
    :type hotwater_use: bool
    :param heating_flag_d: 暖房日
    :type heating_flag_d: ndarray
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param P_alpha: 方位角 (°)
    :type P_alpha: float
    :param P_beta: 傾斜角 (°)
    :type P_beta: tuple
    :param A_col: 集熱器群の面積 (m2)
    :type A_col: tuple
    :param V_fan_P0: 空気搬送ファンの送風機特性曲線において機外静圧をゼロとしたときの空気搬送ファンの風量 (m3/h)
    :type V_fan_P0: float
    :param d0: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の切片 (-)
    :type d0: tuple
    :param d1: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K))
    :type d1: tuple
    :param m_fan_test: 集熱器群を構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2))
    :type m_fan_test: tuple
    :param fan_sso: 空気搬送ファンの自立運転用太陽光発電装置を採用する場合はTrue
    :type fan_sso: bool
    :param fan_type: ファンの種別
    :type fan_type: str
    :param pump_sso: 循環ポンプの自立運転用太陽光発電装置を採用する場合はTrue
    :type pump_sso: bool
    :return: 1時間当たりの補機の消費電力量のうちの給湯設備への付加分 (kWh/h)
    :rtype: ndarray
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

    :param hotwater_use: 空気集熱式太陽熱利用設備が給湯部を有する場合はTrue
    :type hotwater_use: bool
    :param heating_flag_d: 暖房日
    :type heating_flag_d: ndarray
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param P_alpha: 方位角 (°)
    :type P_alpha: float
    :param P_beta: 傾斜角 (°)
    :type P_beta: float
    :param A_col: 集熱器群の面積 (m2)
    :type A_col: tuple
    :param V_fan_P0: 空気搬送ファンの送風機特性曲線において機外静圧をゼロとしたときの空気搬送ファンの風量 (m3/h)
    :type V_fan_P0: float
    :param d0: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の切片 (-)
    :type d0: tuple
    :param d1: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K))
    :type d1: tuple
    :param m_fan_test: 集熱器群を構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2))
    :type m_fan_test: tuple
    :return: 1時間当たりの補機の消費電力量のうち暖房設備への付加分 (kWh/h)
    :rtype: ndarray
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

    :param r_sa_d_t: 1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (-)
    :type r_sa_d_t: ndarray
    :param t_cp_d_t: 1時間当たりの循環ポンプの稼働時間 (h/h)
    :type t_cp_d_t: ndarray
    :param E_E_fan_d_t: 1時間当たりの空気搬送ファンの消費電力量 (kWh/h)
    :type E_E_fan_d_t: ndarray
    :return: 1時間当たりの補機の消費電力量のうち暖房設備への付加分 (kWh/h)
    :rtype: ndarray
    """

    E_E_H_aux_ass_d_t = np.zeros(24 * 365)

    # (4)
    f = np.logical_and(0 < r_sa_d_t, t_cp_d_t == 0)
    E_E_H_aux_ass_d_t[f] = E_E_fan_d_t[f]

    return E_E_H_aux_ass_d_t


def get_E_E_W_aux_ass_d_t(r_sa_d_t, t_cp_d_t, E_E_fan_d_t, E_E_cp_d_t):
    """1時間当たりの補機の消費電力量のうち給湯設備への付加分 (kWh/h)

    :param r_sa_d_t: 1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (-)
    :type r_sa_d_t: ndarray
    :param t_cp_d_t: 1時間当たりの循環ポンプの稼働時間 (h/h)
    :type t_cp_d_t: ndarray
    :param E_E_fan_d_t: 1時間当たりの空気搬送ファンの消費電力量 (kWh/h)
    :type E_E_fan_d_t: ndarray
    :param E_E_cp_d_t: 1時間当たりの循環ポンプの消費電力量 (kWh/h)
    :type E_E_cp_d_t: ndarray
    :return: 1時間当たりの補機の消費電力量のうち給湯設備への付加分 (kWh/h)
    :rtype: ndarray
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

    :param hotwater_use: 空気集熱式太陽熱利用設備が給湯部を有する場合はTrue
    :type hotwater_use: bool
    :param t_fan_d_t: 1時間当たりの空気搬送ファンの稼働時間 (h/h)
    :type t_fan_d_t: ndarray
    :param heating_flag_d: 暖房日であればTrue
    :type heating_flag_d: bool
    :return: 1時間当たりの循環ポンプの稼働時間 (h/h)
    :rtype: ndarray
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

    :param pump_sso: 循環ポンプの自立運転用太陽光発電装置を採用する場合はTrue
    :type pump_sso: bool
    :param t_cp_d_t: 1時間当たりの空気搬送ファンの稼働時間 (h/h)
    :type t_cp_d_t: ndarray
    :return: 1時間当たりの循環ポンプの消費電力量 (kWh/h)
    :rtype: ndarray
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

    :return:循環ポンプの消費電力[W]
    :rtype: float
    """
    return 80.0


# ============================================================================
# 8.3 タンク蓄熱量の上限による補正集熱量
# ============================================================================

def calc_L_tnk_d(Q_d, W_tnk, Theta_wtr_d):
    """1日当たりの給湯部におけるタンク蓄熱量の上限による補正集熱量 (MJ/d) (8)

    :param Q_d: 1日当たりの基準集熱量 (MJ/d)
    :type Q_d: ndarray
    :param W_tnk: 給湯部のタンク容量 (L)
    :type W_tnk: float
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :return: 1日当たりの給湯部におけるタンク蓄熱量の上限による補正集熱量 (MJ/d)
    :rtype: ndarray
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

    :return: 給湯部のタンク有効利用率 [1/d]
    :rtype: ndarray
    """
    # 給湯タンク有効利用率は1.0固定とする
    return np.ones(365)


def get_HC_tnk_d(W_tnk, Theta_wtr_d):
    """給湯部のタンク蓄熱量の上限 (MJ/d) (9)

    :param W_tnk: 給湯部のタンク容量 (L)
    :type W_tnk: float
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :return: 給湯部のタンク蓄熱量の上限 (MJ/d)
    :rtype: ndarray
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

    :param Q_col_d_t: 1時間当たりの集熱部における集熱量 (MJ/d)
    :type Q_col_d_t: ndarray
    :param t_cp_d_t: 1時間当たりの循環ポンプの稼働時間 (h/h)
    :type t_cp_d_t: ndarray
    :return: 1日当たりの基準集熱量 (MJ/d)
    :rtype: ndarray
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

    :param Q_col_d_t: 1時間当たりの集熱部における集熱量 (MJ/d)
    :type Q_col_d_t: ndarray
    :param t_cp_d_t: 1時間当たりの循環ポンプの稼働時間 (h/h)
    :type t_cp_d_t: ndarray
    :return: 1時間当たりの集熱部における集熱量のうちの給湯利用分 (MJ/h)
    :rtype: ndarray
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

    :param Theta_col_nonopg_d_t: 空気搬送ファン停止時の集熱部の出口における空気温度 (℃)
    :type Theta_col_nonopg_d_t: ndarray
    :param Theta_col_opg_d_t:  空気搬送ファン稼働時の集熱部の出口における空気温度 (℃)
    :type Theta_col_opg_d_t: ndarray
    :return: 1時間当たりの空気搬送ファンの稼働時間 (h/h)
    :rtype: ndarray
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

    :param t_fan_d_t: 1時間当たりの空気搬送ファンの稼働時間 (h/h)
    :type t_fan_d_t: ndarray
    :param V_fan_P0: 空気搬送ファンの送風機特性曲線において機外静圧をゼロとした時の空気搬送ファンの風量 (m3/h)
    :type V_fan_P0: float
    :return: 1時間当たりの空気搬送ファンの風量 (m3/h)
    :rtype: ndarray
    """
    V_fan_d_t = V_fan_P0 * t_fan_d_t
    return V_fan_d_t


# ============================================================================
# 9.3 空気搬送ファンの消費電力量
# ============================================================================

def calc_E_E_fan_d_t(fan_sso, fan_type, V_fan_d_t, t_fan_d_t):
    """1時間当たりの空気搬送ファンの消費電力量 (kWh/h) (14)

    :param fan_sso: 空気搬送ファンの自立運転用太陽光発電装置を採用する場合はTrue
    :type fan_sso: bool
    :param fan_type: ファンの種別
    :type fan_type: str
    :param V_fan_d_t: 1時間当たりの空気搬送ファンの風量 (m3/h)
    :type V_fan_d_t: ndarray
    :param t_fan_d_t: 1時間当たりの空気搬送ファンの稼働時間 (h/h)
    :type t_fan_d_t: ndarray
    :return: 1時間当たりの空気搬送ファンの消費電力量 (kWh/h)
    :rtype: ndarray
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

    :param fan_type: ファンの種別
    :type fan_type: str
    :return: 空気搬送ファンの比消費電力 (W/(m3/h))
    :rtype: float
    """
    if fan_type == 'AC':
        return get_table_1()[0]
    elif fan_type == 'DC':
        return get_table_1()[1]
    else:
        raise ValueError(fan_type)


def get_table_1():
    """表1 空気搬送ファンの比消費電力 f_SFP

    :return: 表1 空気搬送ファンの比消費電力 f_SFP
    :rtype: list
    """
    table_1 = (0.4, 0.2)
    return table_1


# ============================================================================
# 9.4 床下空間または居室へ供給する空気の風量
# ============================================================================

def get_V_sa_d_t_i(i, A_HCZ_i, A_MR, A_OR, V_sa_d_t_A):
    """1時間当たりの床下空間または居室へ供給する空気の風量 (m3/h) (15)

    :param i: 暖冷房区画の番号
    :type i: int
    :param A_HCZ_i: 暖冷房区画iの床面積 (m2)
    :type A_HCZ_i: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param V_sa_d_t_A: 床下空間または居室へ供給する1時間当たりの空気の風量の合計
    :type V_sa_d_t_A: ndarray
    :return: 1時間当たりの床下空間または居室へ供給する空気の風量 (m3/h)
    :rtype: ndarray
    """
    if i in [1, 2, 3, 4, 5]:
        return V_sa_d_t_A * A_HCZ_i / (A_MR + A_OR)

    elif i in [6, 7, 8, 9, 10, 11, 12]:
        return np.zeros(24 * 365)

    else:
        raise ValueError(i)


def get_V_sa_d_t_A(V_fan_d_t, r_sa_d_t):
    """床下空間または居室へ供給する1時間当たりの空気の風量の合計 (m3/h) (16)

    :param V_fan_d_t: 1時間当たりの空気搬送ファンの風量 (m3/h)
    :type V_fan_d_t: ndarray
    :param r_sa_d_t: 1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (-)
    :type r_sa_d_t: ndarray
    :return: 床下空間または居室へ供給する1時間当たりの空気の風量の合計 (m3/h)
    :rtype: ndarray
    """
    V_sa_d_t_A = V_fan_d_t * r_sa_d_t

    return V_sa_d_t_A


def get_r_sa_d_t(t_fan_d_t, heating_flag_d):
    """1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (17)

    :param t_fan_d_t: 1時間当たりの空気搬送ファンの稼働時間 (h/h)
    :type t_fan_d_t: ndarray
    :param heating_flag_d: 暖房日であればTrue
    :type heating_flag_d: ndarray
    :return: 1時間当たりの空気搬送ファンの風量のうち床下空間または居室へ供給する風量の割合 (-)
    :rtype: ndarray
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

    :param V_fan_d_t: 1時間当たりの空気搬送ファンの風量 (m3/h)
    :type V_fan_d_t: ndarray
    :param Theta_col_opg_d_t: 空気搬送ファンの稼働時の集熱部の出口における空気温度 (℃)
    :type Theta_col_opg_d_t: ndarray
    :param Q_col_W_d_t: 1時間当たりの集熱部における集熱量のうちの給湯利用分 (MJ/h)
    :type Q_col_W_d_t: ndarray
    :return: 床下空間または居室へ供給する空気の温度 (℃)
    :rtype: ndarray
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

    :param A_col: 集熱器群の面積 (m2)
    :type A_col: tuple
    :param P_alpha: 方位角 (°)
    :type P_alpha: float
    :param P_beta: 傾斜角 (°)
    :type P_beta: tuple
    :param V_fan_P0: 空気搬送ファンの送風機特性曲線において機外静圧をゼロとしたときの空気搬送ファンの風量 (m3/h)
    :type V_fan_P0: float
    :param d0: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の切片 (-)
    :type d0: tuple
    :param d1: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K))
    :type d1: tuple
    :param m_fan_test: 集熱器群を構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2))
    :type m_fan_test: tuple
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param Theta_ex_d_t: 外気温度 (℃)
    :type Theta_ex_d_t: ndarray
    :return: 空気搬送ファン停止時および稼働時の集熱部の出口における空気温度 (℃)
    :rtype: tuple
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

    :param V_fan_d_t: 1時間当たりの空気搬送ファンの風量 (m3/h)
    :type V_fan_d_t: ndarray
    :param Theta_col_opg_d_t: 空気搬送ファン稼働時の集熱部の出口における空気温度 (℃)
    :type Theta_col_opg_d_t: ndarray
    :param Theta_ex_d_t: 外気温度 (℃)
    :type Theta_ex_d_t: ndarray
    :return: 1時間当たりの集熱部における集熱量 (MJ/h)
    :rtype: ndarray
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

    :param Theta_col_nonopg_j_d_t: 空気搬送ファン停止時の集熱器群ごとの出口における空気温度 (℃)
    :type Theta_col_nonopg_j_d_t: ndarray
    :param V_col_j_d_t: 空気搬送ファン稼働時に集熱器群ごとに流れる空気の体積流量 (m3/h)
    :type V_col_j_d_t: ndarray
    :return: 空気搬送ファン停止時の集熱部の出口における空気温度 (℃)
    :rtype: ndarray
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

    :param Theta_col_opg_j_d_t: 空気搬送ファン稼働時の集熱器群ごとの出口における空気温度 (℃)
    :type Theta_col_opg_j_d_t: ndarray
    :param V_col_j_d_t: 空気搬送ファン稼働時に集熱器群ごとの空気の体積流量 (m3/h)
    :type V_col_j_d_t: ndarray
    :return: 空気搬送ファン稼働時の集熱部の出口における空気温度 (℃)
    :rtype: ndarray
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

    :param P_alpha_j: 方位角 (°)
    :type P_alpha_j: float
    :param P_beta_j: 傾斜角 (°)
    :type P_beta_j: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param Theta_ex_d_t: 外気温度 (℃)
    :type Theta_ex_d_t: ndarray
    :param d0_j: 集熱器群jを構成する集熱器の集熱効率特性線図一次近似式の切片 (-)
    :type d0_j: float
    :param d1_j: 集熱器群jを構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K))
    :type d1_j: float
    :return: 空気搬送ファン停止時の集熱器群jの出口における空気温度 (℃)
    :rtype: ndarray
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

    :return: 集熱効率特性線図一次近似式の切片(規定値)[-]
    :rtype: float
    """
    return 0.1


def get_d1_default():
    """集熱効率特性線図一次近似式の傾き(規定値)[m2K]

    :return: 集熱効率特性線図一次近似式の傾き(規定値)[m2K]
    :rtype: float
    """
    return 2.0


# ============================================================================
# 10.5 空気搬送ファン稼働時の集熱器群の出口における空気温度
# ============================================================================

def get_Theta_col_opg_j_d_t(V_col_j_d_t, A_col_j, U_c_j, Theta_col_nonopg_j_d_t, Theta_ex_d_t):
    """空気搬送ファン稼働時の集熱器群jの出口における空気温度 (℃) (23)

    :param V_col_j_d_t: 空気搬送ファン稼働時に集熱器群jを流れる空気の体積流量
    :type V_col_j_d_t: ndarray
    :param A_col_j: 集熱器群jの面積 (m2)
    :type A_col_j: float
    :param U_c_j: 集熱器群jを構成する集熱器の総合熱損失係数
    :type U_c_j: float
    :param Theta_col_nonopg_j_d_t: 空気搬送ファン停止時の集熱器群jの出口における空気温度 (℃)
    :type Theta_col_nonopg_j_d_t: ndarray
    :param Theta_ex_d_t: 外気温度 (℃)
    :type Theta_ex_d_t: ndarray
    :return: 空気搬送ファン稼働時の集熱器群jの出口における空気温度 (℃)
    :rtype: ndarray
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

    :param V_fan_P0_j: 空気搬送ファンの送風機特性曲線において機外静圧をゼロとしたときの空気搬送ファンの風量 (m3/h)
    :type V_fan_P0_j: float
    :param A_col_j: 集熱器群jの面積 (m2)
    :type A_col_j: float
    :param A_col: 集熱器群の面積 (m2)
    :type A_col: tuple
    :return: 空気搬送ファン稼働時に集熱器群jを流れる空気の体積流量 (m3/h)
    :rtype: float
    """
    V_col_j_d_t = V_fan_P0_j * A_col_j / sum(A_col)
    return V_col_j_d_t


def get_U_c_j(m_fan_test_j=None, d1_j=None):
    """集熱器群jを構成する集熱器の総合熱損失係数 (25)

    :param m_fan_test_j: 集熱器群jを構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2))
    :type m_fan_test_j: float
    :param d1_j: 集熱器群jを構成する集熱器の集熱効率特性線図一次近似式の傾き (W/m2K)
    :type d1_j: float
    :return: 集熱器群jを構成する集熱器の総合熱損失係数
    :rtype: float
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
