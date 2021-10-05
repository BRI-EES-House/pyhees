# ============================================================================
# 付録 D 床下空間を経由して外気を導入する換気方式
# ============================================================================

import numpy as np

import pyhees.section3_1_e as algo


# ============================================================================
# D.3.2 暖冷房負荷削減量
# ============================================================================

def calc_delta_L_dash_H_uf_d_t_i(i, A_A, A_MR, A_OR, A_HCZ_i, region, Q, r_A_ufvnt, underfloor_insulation, Theta_ex_d_t,
                                 L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i):
    """ 当該住戸の暖冷房区画iの床下空間を経由して外気を導入する換気方式による暖房負荷削減量 (MJ/h) (1)

    :param i: 暖冷房区画の番号
    :type i: int
    :param A_A: 床面積の合計[m^2]
    :type A_A: float
    :param A_MR: 主たる居室の床面積[m^2]
    :type A_MR: float
    :param A_OR: その他の居室の床面積[m^2]
    :type A_OR: float
    :param A_HCZ_i: 暖冷房区画iの床面積 (m2)
    :type A_HCZ_i: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param r_A_ufvnt: 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
    :type r_A_ufvnt: float
    :param underfloor_insulation: 床下空間が断熱空間内である場合はTrue
    :type underfloor_insulation: bool
    :param Theta_ex_d_t: 外気温度 (℃)
    :type Theta_ex_d_t: ndarray
    :param L_dash_H_R_d_t_i: 標準住戸の負荷補正前の暖房負荷 (MJ/h)
    :type L_dash_H_R_d_t_i: ndarray
    :param L_dash_CS_R_d_t_i: 標準住戸の負荷補正前の冷房顕熱負荷 （MJ/h）
    :type L_dash_CS_R_d_t_i: ndarray
    :return: 当該住戸の暖冷房区画iの床下空間を経由して外気を導入する換気方式による暖房負荷削減量 (MJ/h)
    :rtype: ndarray
    """

    delta_L_dash_H_uf_d_t_i = np.zeros(24 * 365)

    if r_A_ufvnt is None or underfloor_insulation is None:
        return delta_L_dash_H_uf_d_t_i

    # ----------------------------------------
    # (1-1) L_dash_H_R_d_t_i <= 0
    # ----------------------------------------
    f1 = (L_dash_H_R_d_t_i[i - 1] <= 0)
    delta_L_dash_H_uf_d_t_i[f1] = 0

    # ----------------------------------------
    # (1-2) 0 < L_dash_H_R_d_t_i
    # ----------------------------------------
    f2 = (0 < L_dash_H_R_d_t_i[i - 1])

    # 空気の密度 (kg/m3)
    ro_air = get_ro_air()

    # 空気の比熱 (kJ/(kg・K))
    c_p_air = get_c_p_air()

    # 床の熱貫流率 (W/(m2・K))
    U_s = get_U_s()

    # 床の温度差係数 (-)
    H_floor = get_H_floor()

    # 室内温度 (℃)
    Theta_in_d_t = get_Theta_in_d_t('H')

    # 当該住戸の暖冷房区画iの外気を導入する床下空間に接する床の面積
    A_s_ufvnt_i = algo.calc_A_s_ufvnt_i(i, r_A_ufvnt, A_A, A_MR, A_OR)

    # 暖冷房負荷計算時に想定した床の熱貫流率
    U_s_vert = algo.get_U_s_vert(region, Q)

    # 当該住戸の1時間当たりの換気量 (m3/h) (4)
    V_A = get_V_A(A_A)

    # 当該住戸の暖冷房区画iの1時間当たりの換気量 (m3/h) (3)
    V_i = get_V_i(i, V_A, A_HCZ_i, A_MR, A_OR)

    # 床下温度及び地盤またはそれを覆う基礎の表面温度 (℃)
    Theta_uf_d_t, Theta_g_surf_d_t = algo.calc_Theta(
        region=region,
        A_A=A_A,
        A_MR=A_MR,
        A_OR=A_OR,
        Q=Q,
        r_A_ufvnt=r_A_ufvnt,
        underfloor_insulation=underfloor_insulation,
        Theta_sa_d_t=Theta_ex_d_t,
        Theta_ex_d_t=Theta_ex_d_t,
        V_sa_d_t_A=np.repeat(V_A, 24 * 365),
        H_OR_C='H',
        L_dash_H_R_d_t=L_dash_H_R_d_t_i,
        L_dash_CS_R_d_t=L_dash_CS_R_d_t_i
    )

    delta_L_dash_H_uf_d_t_i[f2] = (ro_air * c_p_air * V_i * (Theta_uf_d_t[f2] - Theta_in_d_t[f2]) * 10 ** (-3)
                                   - ro_air * c_p_air * V_i * (Theta_ex_d_t[f2] - Theta_in_d_t[f2]) * 10 ** (-3)
                                   - U_s * A_s_ufvnt_i * (Theta_in_d_t[f2] - Theta_uf_d_t[f2]) * 3.6 * 10 ** (-3)
                                   + U_s_vert * A_s_ufvnt_i
                                   * (Theta_in_d_t[f2] - Theta_ex_d_t[f2]) * H_floor * 3.6 * 10 ** (-3))

    return delta_L_dash_H_uf_d_t_i


def calc_delta_L_dash_CS_R_d_t_i(i, region, Q, r_A_ufvnt, underfloor_insulation, A_A, A_MR, A_OR, A_HCZ_i, Theta_ex_d_t,
                                 L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i):
    """ 当該住戸の暖冷房区画iの床下空間を経由して外気を導入する換気方式による冷房顕熱負荷削減量 (MJ/h) (2)

    :param i: 暖冷房区画の番号
    :type i: int
    :param region: 省エネルギー地域区分
    :type region: int
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param r_A_ufvnt: 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
    :type r_A_ufvnt:
    :param underfloor_insulation: 床下空間が断熱空間内である場合はTrue
    :type underfloor_insulation:
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param A_HCZ_i: 暖冷房区画iの床面積 (m2)
    :type A_HCZ_i: float
    :param Theta_ex_d_t: 外気温度 (℃)
    :type Theta_ex_d_t: ndarray
    :param L_dash_H_R_d_t_i: 標準住戸の負荷補正前の暖房負荷 (MJ/h)
    :type L_dash_H_R_d_t_i: ndarray
    :param L_dash_CS_R_d_t_i: 標準住戸の負荷補正前の冷房顕熱負荷 （MJ/h）
    :type L_dash_CS_R_d_t_i: ndarray
    :return: 当該住戸の暖冷房区画iの床下空間を経由して外気を導入する換気方式による冷房顕熱負荷削減量 (MJ/h) (2)
    :rtype: ndarray
    """

    delta_L_dash_CS_R_d_t_i = np.zeros(24 * 365)

    if r_A_ufvnt is None:
        return delta_L_dash_CS_R_d_t_i

    # ----------------------------------------
    # (2-1) L_dash_CS_R_d_t_i < 0
    # ----------------------------------------
    f1 = (L_dash_CS_R_d_t_i[i - 1] < 0)
    delta_L_dash_CS_R_d_t_i[f1] = 0

    # ----------------------------------------
    # (2-2) 0 < L_dash_CS_R_d_t_i
    # ----------------------------------------
    f2 = (0 < L_dash_CS_R_d_t_i[i - 1])

    # 空気の密度 (kg/m3)
    ro_air = get_ro_air()

    # 空気の比熱 (kJ/(kg・K))
    c_p_air = get_c_p_air()

    # 床の熱貫流率 (W/(m2・K))
    U_s = get_U_s()

    # 床の温度差係数 (-)
    H_floor = get_H_floor()

    # 当該住戸の1時間当たりの換気量 (m3/h) (4)
    V_A = get_V_A(A_A)

    # 当該住戸の暖冷房区画iの1時間当たりの換気量 (m3/h) (3)
    V_i = get_V_i(i, V_A, A_HCZ_i, A_MR, A_OR)

    # 室内温度 (℃)
    Theta_in_d_t = get_Theta_in_d_t('CS')

    # 床下温度及び地盤またはそれを覆う基礎の表面温度 (℃)
    Theta_uf_d_t, Theta_g_surf_d_t = algo.calc_Theta(
        region=region,
        A_A=A_A,
        A_MR=A_MR,
        A_OR=A_OR,
        Q=Q,
        r_A_ufvnt=r_A_ufvnt,
        underfloor_insulation=underfloor_insulation,
        Theta_sa_d_t=Theta_ex_d_t,
        Theta_ex_d_t=Theta_ex_d_t,
        V_sa_d_t_A=np.repeat(V_A, 24 * 365),
        H_OR_C='C',
        L_dash_H_R_d_t=L_dash_H_R_d_t_i,
        L_dash_CS_R_d_t=L_dash_CS_R_d_t_i
    )

    # 当該住戸の暖冷房区画iの外気を導入する床下空間に接する床の面積
    A_s_ufvnt_i = algo.calc_A_s_ufvnt_i(i, r_A_ufvnt, A_A, A_MR, A_OR)

    # 暖冷房負荷計算時に想定した床の熱貫流率
    U_s_vert = algo.get_U_s_vert(region, Q)

    delta_L_dash_CS_R_d_t_i[f2] = (- ro_air * c_p_air * V_i * (Theta_uf_d_t[f2] - Theta_in_d_t[f2]) * 10 ** (-3)
                                   + ro_air * c_p_air * V_i * (Theta_ex_d_t[f2] - Theta_in_d_t[f2]) * 10 ** (-3)
                                   + U_s * A_s_ufvnt_i * (Theta_in_d_t[f2] - Theta_uf_d_t[f2]) * 3.6 * 10 ** (-3)
                                   - U_s_vert * A_s_ufvnt_i * (
                                           Theta_in_d_t[f2] - Theta_ex_d_t[f2]) * H_floor * 3.6 * 10 ** (-3))

    return delta_L_dash_CS_R_d_t_i


def get_ro_air():
    """ 空気の密度 (kg/m3)

    :return: 空気の密度 (kg/m3)
    :rtype: float
    """
    return 1.20


def get_c_p_air():
    """ 空気の比熱 (kJ/(kg・K))

    :return: 空気の比熱 (kJ/(kg・K))
    :rtype: float
    """
    return 1.006


def get_U_s():
    """ 床の熱貫流率 (W/(m2・K))

    :return: 床の熱貫流率 (W/(m2・K))
    :rtype: float
    """
    return 2.223


def get_H_floor():
    """ 床の温度差係数 (-)

    :return: 床の温度差係数 (-)
    :rtype: float
    """
    return 0.7


def get_Theta_in_d_t(H_or_CS):
    """ 室内温度 (℃)

    :param H_or_CS: 計算対象('H' for 暖房負荷削減量, 'CS' for 冷房顕熱負荷削減量)
    :type H_or_CS: str
    :return: 室内温度 (℃)
    :rtype: ndarray
    """

    if H_or_CS == 'H':
        return np.repeat(20, 24 * 365)
    elif H_or_CS == 'CS':
        return np.repeat(27, 24 * 365)


# ============================================================================
# D.3.3 換気量
# ============================================================================

def get_V_i(i, V_A, A_HCZ_i, A_MR, A_OR):
    """ 当該住戸の暖冷房区画iの1時間当たりの換気量 (m3/h) (3)

    :param i: 暖冷房区画の番号
    :type i: int
    :param V_A: 当該住戸の1時間当たりの換気量 (m3/h)
    :type V_A: float
    :param A_HCZ_i: 暖冷房区画iの床面積 (m2)
    :type A_HCZ_i: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :return: 当該住戸の暖冷房区画iの1時間当たりの換気量 (m3/h)
    :rtype: float
    """

    if i in [1, 2, 3, 4, 5]:
        return V_A * (A_HCZ_i / (A_MR + A_OR))
    elif i in [6, 7, 8, 9, 10, 11, 12]:
        return 0
    else:
        raise ValueError(i)


def get_V_A(A_A):
    """ 当該住戸の1時間当たりの換気量 (m3/h) (4)

    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :return: 当該住戸の1時間当たりの換気量 (m3/h)
    :rtype: float
    """

    # 参照天井高さ (m)
    H_R = get_H_R()

    # 換気回数 (回/h)
    N = get_N()

    # 当該住戸の1時間当たりの換気量 (4)
    V_A = A_A * H_R * N

    return V_A


def get_H_R():
    """ 参照天井高さ (m)

    :return: 参照天井高さ (m)
    :rtype: float
    """
    return 2.4


def get_N():
    """ 換気回数 (回/h)

    :return: 換気回数 (回/h)
    :rtype: float
    """
    return 0.5
