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
    """当該住戸の暖冷房区画iの床下空間を経由して外気を導入する換気方式による暖房負荷削減量 (MJ/h) (1)

    Args:
      i(int): 暖冷房区画の番号
      A_A(float): 床面積の合計[m^2]
      A_MR(float): 主たる居室の床面積[m^2]
      A_OR(float): その他の居室の床面積[m^2]
      A_HCZ_i(float): 暖冷房区画iの床面積 (m2)
      region(int): 省エネルギー地域区分
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      r_A_ufvnt(float): 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
      underfloor_insulation(bool): 床下空間が断熱空間内である場合はTrue
      Theta_ex_d_t(ndarray): 外気温度 (℃)
      L_dash_H_R_d_t_i(ndarray): 標準住戸の負荷補正前の暖房負荷 (MJ/h)
      L_dash_CS_R_d_t_i(ndarray): 標準住戸の負荷補正前の冷房顕熱負荷 （MJ/h）

    Returns:
      ndarray: 当該住戸の暖冷房区画iの床下空間を経由して外気を導入する換気方式による暖房負荷削減量 (MJ/h)

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
    """当該住戸の暖冷房区画iの床下空間を経由して外気を導入する換気方式による冷房顕熱負荷削減量 (MJ/h) (2)

    Args:
      i(int): 暖冷房区画の番号
      region(int): 省エネルギー地域区分
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      r_A_ufvnt(param underfloor_insulation: 床下空間が断熱空間内である場合はTrue): 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
      underfloor_insulation(param A_A: 床面積の合計 (m2)): 床下空間が断熱空間内である場合はTrue
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      A_HCZ_i(float): 暖冷房区画iの床面積 (m2)
      Theta_ex_d_t(ndarray): 外気温度 (℃)
      L_dash_H_R_d_t_i(ndarray): 標準住戸の負荷補正前の暖房負荷 (MJ/h)
      L_dash_CS_R_d_t_i(ndarray): 標準住戸の負荷補正前の冷房顕熱負荷 （MJ/h）

    Returns:
      ndarray: 当該住戸の暖冷房区画iの床下空間を経由して外気を導入する換気方式による冷房顕熱負荷削減量 (MJ/h) (2)

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
    """空気の密度 (kg/m3)

    Args:

    Returns:
      float: 空気の密度 (kg/m3)

    """
    return 1.20


def get_c_p_air():
    """空気の比熱 (kJ/(kg・K))

    Args:

    Returns:
      float: 空気の比熱 (kJ/(kg・K))

    """
    return 1.006


def get_U_s():
    """床の熱貫流率 (W/(m2・K))

    Args:

    Returns:
      float: 床の熱貫流率 (W/(m2・K))

    """
    return 2.223


def get_H_floor():
    """床の温度差係数 (-)

    Args:

    Returns:
      float: 床の温度差係数 (-)

    """
    return 0.7


def get_Theta_in_d_t(H_or_CS):
    """室内温度 (℃)

    Args:
      H_or_CS(str): 計算対象('H' for 暖房負荷削減量, 'CS' for 冷房顕熱負荷削減量)

    Returns:
      ndarray: 室内温度 (℃)

    """

    if H_or_CS == 'H':
        return np.repeat(20, 24 * 365)
    elif H_or_CS == 'CS':
        return np.repeat(27, 24 * 365)


# ============================================================================
# D.3.3 換気量
# ============================================================================

def get_V_i(i, V_A, A_HCZ_i, A_MR, A_OR):
    """当該住戸の暖冷房区画iの1時間当たりの換気量 (m3/h) (3)

    Args:
      i(int): 暖冷房区画の番号
      V_A(float): 当該住戸の1時間当たりの換気量 (m3/h)
      A_HCZ_i(float): 暖冷房区画iの床面積 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)

    Returns:
      float: 当該住戸の暖冷房区画iの1時間当たりの換気量 (m3/h)

    """

    if i in [1, 2, 3, 4, 5]:
        return V_A * (A_HCZ_i / (A_MR + A_OR))
    elif i in [6, 7, 8, 9, 10, 11, 12]:
        return 0
    else:
        raise ValueError(i)


def get_V_A(A_A):
    """当該住戸の1時間当たりの換気量 (m3/h) (4)

    Args:
      A_A(float): 床面積の合計 (m2)

    Returns:
      float: 当該住戸の1時間当たりの換気量 (m3/h)

    """

    # 参照天井高さ (m)
    H_R = get_H_R()

    # 換気回数 (回/h)
    N = get_N()

    # 当該住戸の1時間当たりの換気量 (4)
    V_A = A_A * H_R * N

    return V_A


def get_H_R():
    """参照天井高さ (m)

    Args:

    Returns:
      float: 参照天井高さ (m)

    """
    return 2.4


def get_N():
    """換気回数 (回/h)

    Args:

    Returns:
      float: 換気回数 (回/h)

    """
    return 0.5
