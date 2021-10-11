# ============================================================================
# 付録 E 床下に空気を供給する場合の床下温度等の算定方法
# ============================================================================

import numpy as np
from math import sqrt
from functools import lru_cache


# ============================================================================
# E.2 床下温度
# ============================================================================

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


def get_r_A_uf_i(i):
    """暖冷房区画iの床面積のうち床下空間に接する床面積の割合 (-)

    Args:
      i(int): 暖冷房区画の番号

    Returns:
      float: 暖冷房区画iの床面積のうち床下空間に接する床面積の割合 (-)

    """

    return get_table_e_6()[i - 1]


# ============================================================================
# E.4 床下空間に接する床の面積及び床下空間の基礎外周長さ
# ============================================================================

def get_L_uf(A_s_ufvnt_A):
    """当該住戸の外気を導入する床下空間の基礎外周長さ (6)

    Args:
      A_s_ufvnt_A(float): 当該住戸の外気を導入する床下空間に接する床の面積の合計 (m2)

    Returns:
      当該住戸の外気を導入する床下空間の基礎外周長さ (6)

    """

    # 床下の平面形状(アスペクト比等)を考慮した係数(無次元)
    r_a = get_r_a()

    # 当該住戸の外気を導入する床下空間の基礎外周長さ (6)
    L_uf = r_a * 4 * sqrt(A_s_ufvnt_A)

    return L_uf


def get_r_a():
    """床下の平面形状(アスペクト比等)を考慮した係数(無次元)

    Args:

    Returns:
      float: 床下の平面形状(アスペクト比等)を考慮した係数(無次元)

    """
    return 1.02


def get_U_s_vert(region, Q):
    """暖冷房負荷計算時に想定した床の熱貫流率 (W/m2K) (4)

    Args:
      region(int): 省エネルギー地域区分
      Q(float): 当該住戸の熱損失係数 (W/m2K)

    Returns:
      float: 暖冷房負荷計算時に想定した床の熱貫流率 (W/m2K)

    """

    if region == 8:
        return 2.223

    Q_0 = get_Q_j(region, 0)
    Q_1 = get_Q_j(region, 1)
    Q_2 = get_Q_j(region, 2)
    Q_3 = get_Q_j(region, 3)
    Q_4 = get_Q_j(region, 4)

    U_s_R_Q_0 = get_U_s_R_Q_j(region, 0)
    U_s_R_Q_1 = get_U_s_R_Q_j(region, 1)
    U_s_R_Q_2 = get_U_s_R_Q_j(region, 2)
    U_s_R_Q_3 = get_U_s_R_Q_j(region, 3)
    U_s_R_Q_4 = get_U_s_R_Q_j(region, 4)

    if Q > Q_1:
        U_s_vert = (Q - Q_1) / (Q_0 - Q_1) * U_s_R_Q_0 + (Q - Q_0) / (Q_1 - Q_0) * U_s_R_Q_1
    elif Q > Q_2:
        U_s_vert = (Q - Q_2) / (Q_1 - Q_2) * U_s_R_Q_1 + (Q - Q_1) / (Q_2 - Q_1) * U_s_R_Q_2
    elif Q > Q_3:
        U_s_vert = (Q - Q_3) / (Q_2 - Q_3) * U_s_R_Q_2 + (Q - Q_2) / (Q_3 - Q_2) * U_s_R_Q_3
    else:
        U_s_vert = (Q - Q_4) / (Q_3 - Q_4) * U_s_R_Q_3 + (Q - Q_3) / (Q_4 - Q_3) * U_s_R_Q_4

    # 2.223 を上回る場合は 2.223
    U_s_vert = min(2.223, U_s_vert)

    return U_s_vert


def get_table_e_3():
    """表E.3 断熱性能の区分jの熱損失係数Qjにおける標準住戸の床の熱貫流率

    Args:

    Returns:
      list: 表E.3 断熱性能の区分jの熱損失係数Qjにおける標準住戸の床の熱貫流率

    """
    table_e_3 = [
        (2.223, 2.223, 2.223, 2.223, 2.223, 2.223, 2.223, 2.223),
        (0.342, 0.342, 0.964, 0.949, 1.208, 1.208, 2.223, 2.223),
        (0.427, 0.427, 0.791, 0.825, 1.360, 1.360, 1.633, 2.223),
        (0.319, 0.319, 0.359, 0.564, 0.554, 0.554, 0.554, 2.223),
        (0.272, 0.272, 0.272, 0.373, 0.373, 0.373, 0.373, 0.373),
    ]

    return table_e_3


def get_U_s_R_Q_j(region, j):
    """断熱性能の区分jの熱損失係数Q_jにおける標準住戸の床の熱貫流率 (W/m2K)

    Args:
      region(int): 省エネルギー地域区分
      j(int): 断熱性能の区分

    Returns:
      float: 断熱性能の区分jの熱損失係数Q_jにおける標準住戸の床の熱貫流率 (W/m2K)

    """
    return get_table_e_3()[j][region - 1]


def get_phi(region, Q):
    """基礎の線熱貫流率 (W/mK) (5)

    Args:
      region(int): 省エネルギー地域区分
      Q(float): 当該住戸の熱損失係数 (W/m2K)

    Returns:
      float: 基礎の線熱貫流率 (W/mK)

    """

    # 8地域においては、当該住戸の熱損失係数に瓦らず　2.289 W/mK
    if region == 8:
        return 2.289

    Q_0 = get_Q_j(region, 0)
    Q_1 = get_Q_j(region, 1)
    Q_2 = get_Q_j(region, 2)
    Q_3 = get_Q_j(region, 3)
    Q_4 = get_Q_j(region, 4)

    phi_Q_0 = get_phi_Q_j(region, 0)
    phi_Q_1 = get_phi_Q_j(region, 1)
    phi_Q_2 = get_phi_Q_j(region, 2)
    phi_Q_3 = get_phi_Q_j(region, 3)
    phi_Q_4 = get_phi_Q_j(region, 4)

    if Q > Q_1:
        phi = (Q - Q_1) / (Q_0 - Q_1) * phi_Q_0 + (Q - Q_0) / (Q_1 - Q_0) * phi_Q_1
    elif Q > Q_2:
        phi = (Q - Q_2) / (Q_1 - Q_2) * phi_Q_1 + (Q - Q_1) / (Q_2 - Q_1) * phi_Q_2
    elif Q > Q_3:
        phi = (Q - Q_3) / (Q_2 - Q_3) * phi_Q_2 + (Q - Q_2) / (Q_3 - Q_2) * phi_Q_3
    else:
        phi = (Q - Q_4) / (Q_3 - Q_4) * phi_Q_3 + (Q - Q_3) / (Q_4 - Q_3) * phi_Q_4

    # 2.289 を上回る場合は 2.289
    phi = min(2.289, phi)

    return phi


def get_table_e_4():
    """表E.4 断熱性能の区分jの計算対象住戸の基礎の仮想線熱貫流率

    Args:

    Returns:
      list: 表E.4 断熱性能の区分jの計算対象住戸の基礎の仮想線熱貫流率

    """

    table_e_4 = [
        (2.289, 2.289, 2.289, 2.289, 2.289, 2.289, 2.289, 2.289),
        (0.635, 0.635, 1.517, 1.504, 1.872, 1.872, 2.289, 2.289),
        (0.675, 0.675, 1.272, 1.329, 2.087, 2.087, 2.289, 2.289),
        (0.516, 0.516, 0.573, 0.877, 0.863, 0.863, 0.863, 2.289),
        (0.450, 0.450, 0.450, 0.601, 0.601, 0.601, 0.601, 2.289),
    ]

    return table_e_4


def get_phi_Q_j(region, j):
    """断熱性能の区分jの熱損失係数Q_jにおける基礎の線熱貫流率 (W/mK)

    Args:
      region(int): 省エネルギー地域区分
      j(int): 断熱性能の区分

    Returns:
      float: 断熱性能の区分jの熱損失係数Q_jにおける基礎の線熱貫流率 (W/mK)

    """

    return get_table_e_4()[j][region - 1]


def get_table_e_5():
    """表E.5 断熱性能の区分jの熱損失係数

    Args:

    Returns:
      list: 表E.5 断熱性能の区分jの熱損失係数

    """
    table_e_5 = [
        (8.26, 8.26, 8.26, 8.49, 8.49, 8.49, 8.49, 8.49),
        (2.8, 2.8, 4.0, 4.7, 5.19, 5.19, 8.27, 8.27),
        (1.8, 1.8, 2.7, 3.3, 4.2, 4.2, 4.59, 8.01),
        (1.6, 1.6, 1.9, 2.4, 2.7, 2.7, 2.7, 2.7),
        (1.4, 1.4, 1.4, 1.9, 1.9, 1.9, 1.9, 3.7),
    ]

    return table_e_5


def get_Q_j(region, j):
    """断熱性能の区分jの熱損失係数 Q_j (W/m2K)

    Args:
      region(int): 
      j(int): 断熱性能の区分

    Returns:
      float: 断熱性能の区分jの熱損失係数 Q_j (W/m2K)

    """

    return get_table_e_5()[j][region - 1]


def calc_A_s_ufvnt_i(i, r_A_ufvnt, A_A, A_MR, A_OR):
    """当該住戸の暖冷房区画iの空気を供給する床下空間に接する床の面積 (m2) (7)

    Args:
      i(int): 暖冷房区画の番号
      r_A_ufvnt(float): 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)

    Returns:
      float: 当該住戸の暖冷房区画iの空気を供給する床下空間に接する床の面積 (m2)

    """

    # 暖冷房区画iの床面積のうち床下空間に接する床面積の割合 (-)
    r_A_uf_i = get_r_A_uf_i(i)

    from pyhees.section3_1 import get_A_HCZ_i
    A_HCZ_i = get_A_HCZ_i(i, A_A, A_MR, A_OR)

    # 当該住戸の暖冷房区画iの空気を供給する床下空間に接する床の面積 (m2) (7)
    A_s_ufvnt_i = r_A_uf_i * A_HCZ_i * r_A_ufvnt

    return A_s_ufvnt_i


def get_A_s_ufvnt_A(r_A_ufvnt, A_A, A_MR, A_OR):
    """当該住戸の空気を供給する床下空間に接する床の面積の合計 (m2) (8)

    Args:
      r_A_ufvnt(float): 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)

    Returns:
      float: 当該住戸の空気を供給する床下空間に接する床の面積の合計 (m2)

    """

    # 当該住戸の空気を供給する床下空間に接する床の面積の合計 (m2) (8)
    A_s_ufvnt_A = sum([calc_A_s_ufvnt_i(i, r_A_ufvnt, A_A, A_MR, A_OR) for i in range(1, 13)])

    return A_s_ufvnt_A


# 暖冷房区画iの床面積のうち床下空間に接する床面積の割合 (-)
# def get_r_A_uf_i(i):
#   return table_e_6[i - 1]


def get_table_e_6():
    """表 E.6 暖冷房区画iの床面積のうち床下空間に接する床面積の割合

    Args:

    Returns:
      list: 表 E.6 暖冷房区画iの床面積のうち床下空間に接する床面積の割合

    """
    table_e_6 = (1.0, 1.0, 0, 0, 0, 1.0, 1.0, 1.0, 10.76 / 13.25, 0, 0, 0)

    return table_e_6


# ============================================================================
# E.5 地盤またはそれを覆う基礎
# ============================================================================

def calc_Theta(region, A_A, A_MR, A_OR, Q, r_A_ufvnt, underfloor_insulation, Theta_sa_d_t, Theta_ex_d_t,
               V_sa_d_t_A, H_OR_C,
               L_dash_H_R_d_t,
               L_dash_CS_R_d_t):
    """床下温度及び地盤またはそれを覆う基礎の表面温度 (℃) (1)(9)

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      r_A_ufvnt(float): 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
      underfloor_insulation(bool): 床下空間が断熱空間内である場合はTrue
      Theta_sa_d_t(ndarray): 床下空間または居室へ供給する空気の温度 (℃)
      Theta_ex_d_t(ndarray): 外気温度 (℃)
      V_sa_d_t_A(ndarray): 床下空間または居室へ供給する1時間当たりの空気の風量の合計
      H_OR_C: type H_OR_C: str
      L_dash_H_R_d_t(ndarray): 標準住戸の負荷補正前の暖房負荷 (MJ/h)
      L_dash_CS_R_d_t(ndarray): 標準住戸の負荷補正前の冷房顕熱負荷 （MJ/h）

    Returns:
      tuple: 床下温度、地盤またはそれを覆う基礎の表面温度 (℃)

    """

    # 地盤またはそれを覆う基礎の表面熱伝達抵抗 ((m2・K)/W)
    R_g = 0.15

    # 吸熱応答係数の初項
    Phi_A_0 = 0.025504994

    # 空気密度[kg/m3]
    ro_air = get_ro_air()

    # 空気の比熱[kJ/kgK]
    c_p_air = get_c_p_air()

    # 床の熱貫流率[W/m2K]
    U_s = get_U_s()

    # 指数項の総数
    M = 10

    # 地盤の不易層温度 (℃) (10)
    Theta_g_avg = get_Theta_g_avg(Theta_ex_d_t)

    # 作業領域の確保
    Theta_uf_d_t = np.zeros(24 * 365)
    Theta_g_surf_d_t = np.zeros(24 * 365)
    Theta_dash_g_surf_A_m = np.zeros(M)

    # 初期値の設定
    Theta_uf_prev = 0.0
    Theta_g_surf_prev = 0.0
    Theta_dash_g_surf_A_m_prev = [0.0] * M

    # ----- 助走計算 -----

    # 助走計算用床下温度
    Theta_uf_runup = get_Theta_uf_d_t_runup(underfloor_insulation, Theta_ex_d_t)

    Theta_in_H = 20
    Theta_in_C = 27

    # 指数項mにおける吸熱応答係数
    phi_1_A_m = np.array([get_phi_1_A_m(m) for m in range(1, M + 1)])

    # 指数項mにおける公比r_m
    r_m = np.array([get_r_m(m) for m in range(1, M + 1)])

    for dt in range(24 * 365):
        # 当該住宅の床下温度 (13)
        Theta_uf = Theta_uf_runup[dt]

        # 日付dの時刻t-1における地盤またはそれを覆う基礎の表面熱流 (W/m2) (12)
        q_g_prev = 1.0 / R_g * (Theta_uf_prev - Theta_g_surf_prev)

        # 日付dの時刻tにおける指数項mの吸熱応答の項別成分 (℃) (11)
        Theta_dash_g_surf_A_m = phi_1_A_m * q_g_prev + r_m * Theta_dash_g_surf_A_m_prev

        # 地盤またはそれを覆う基礎の表面温度 (℃) (9)
        Theta_g_surf = (((Phi_A_0 / R_g) * Theta_uf + np.sum(Theta_dash_g_surf_A_m) + Theta_g_avg)
                        / (1.0 + (Phi_A_0 / R_g)))

        # 次時刻へ値を保存
        Theta_uf_prev = Theta_uf
        Theta_g_surf_prev = Theta_g_surf
        Theta_dash_g_surf_A_m_prev = Theta_dash_g_surf_A_m

    # ----- 本番計算 -----

    if r_A_ufvnt is None:
        r_A_ufvnt = 0

    # 当該住戸の暖冷房区画iの空気を供給する床下空間に接する床の面積(m2) (7)
    A_s_ufvnt = [calc_A_s_ufvnt_i(i, r_A_ufvnt, A_A, A_MR, A_OR) for i in range(1, 13)]

    # 当該住戸の空気を供給する床下空間に接する床の面積の合計 (m2) (8)
    A_s_ufvnt_A = get_A_s_ufvnt_A(r_A_ufvnt, A_A, A_MR, A_OR)

    # 当該住戸の外気を導入する床下空間の基礎外周長さ (6)
    L_uf = get_L_uf(A_s_ufvnt_A)

    H_floor = 0.7

    # 基礎の線熱貫流率 (W/mK) (5)
    phi = get_phi(region, Q)

    Theta_star = np.zeros(12)
    H_star = np.zeros(12)

    for dt in range(24 * 365):
        # 日付dの時刻t-1における地盤またはそれを覆う基礎の表面熱流 (W/m2) (12)
        q_g_prev = 1.0 / R_g * (Theta_uf_prev - Theta_g_surf_prev)

        # 日付dの時刻tにおける指数項mの吸熱応答の項別成分 (℃) (11)
        Theta_dash_g_surf_A_m = phi_1_A_m * q_g_prev + r_m * Theta_dash_g_surf_A_m_prev

        # 参照空気温度及び参照温度差係数 (2)(3)
        # TODO: ここをベクトル化する
        for i in range(1, 13):
            if 0 < L_dash_H_R_d_t[i - 1][dt]:
                Theta_star[i - 1] = Theta_in_H
                H_star[i - 1] = 1
            elif 0 < L_dash_CS_R_d_t[i - 1][dt]:
                Theta_star[i - 1] = Theta_in_C
                H_star[i - 1] = 1
            elif L_dash_H_R_d_t[i - 1][dt] <= 0 and L_dash_CS_R_d_t[i - 1][dt] <= 0 and Theta_ex_d_t[dt] < Theta_in_H:
                Theta_star[i - 1] = Theta_in_H
                H_star[i - 1] = 1
            elif L_dash_H_R_d_t[i - 1][dt] <= 0 and L_dash_CS_R_d_t[i - 1][dt] <= 0 and Theta_in_H <= Theta_ex_d_t[
                dt] <= Theta_in_C:
                Theta_star[i - 1] = Theta_ex_d_t[dt]
                H_star[i - 1] = H_floor
            elif L_dash_H_R_d_t[i - 1][dt] <= 0 and L_dash_CS_R_d_t[i - 1][dt] <= 0 and Theta_in_C < Theta_ex_d_t[dt]:
                Theta_star[i - 1] = Theta_in_C
                H_star[i - 1] = 1
            else:
                raise ValueError((L_dash_CS_R_d_t[i - 1][dt], L_dash_CS_R_d_t[i - 1][dt]))

        # 当該住宅の床下温度 (1)
        Theta_uf = (ro_air * c_p_air * V_sa_d_t_A[dt] * Theta_sa_d_t[dt] +
                    (sum([U_s * A_s_ufvnt[i - 1] * H_star[i - 1] * Theta_star[i - 1] for i in
                          range(1, 13)])
                     + phi * L_uf * Theta_ex_d_t[dt]
                     + (A_s_ufvnt_A / R_g)
                     * ((sum(Theta_dash_g_surf_A_m) + Theta_g_avg) / (1.0 + Phi_A_0 / R_g))) * 3.6) \
                   / (ro_air * c_p_air * V_sa_d_t_A[dt]
                      + (sum([U_s * A_s_ufvnt[i - 1] * H_star[i - 1] for i in range(1, 13)])
                         + phi * L_uf
                         + (A_s_ufvnt_A / R_g)
                         * (1.0 / (1.0 + Phi_A_0 / R_g))) * 3.6)

        # 地盤またはそれを覆う基礎の表面温度 (℃) (9)
        Theta_g_surf = (((Phi_A_0 / R_g) * Theta_uf + np.sum(Theta_dash_g_surf_A_m) + Theta_g_avg)
                        / (1.0 + (Phi_A_0 / R_g)))

        # 次時刻へ値を保存
        Theta_uf_prev = Theta_uf
        Theta_g_surf_prev = Theta_g_surf
        Theta_dash_g_surf_A_m_prev = Theta_dash_g_surf_A_m

        # 計算結果の保存
        Theta_uf_d_t[dt] = Theta_uf
        Theta_g_surf_d_t[dt] = Theta_g_surf

    return Theta_uf_d_t, Theta_g_surf_d_t


def get_Theta_g_avg(Theta_ex_d_t):
    """地盤の不易層温度 (℃) (10)

    Args:
      Theta_ex_d_t(ndarray): 外気温度 (℃)

    Returns:
      float: 地盤の不易層温度 (℃)

    """

    # 地盤の不易層温度は年間平均気温に等しいとする
    return np.average(Theta_ex_d_t)


def get_r_m(m):
    """指数項mにおける公比r_m

    Args:
      m(int): 指数項m

    Returns:
      tuple: 指数項mにおける公比r_m

    """
    return get_table_e_7()[m - 1][0]


def get_table_e_7():
    """表 E.7 指数項mにおける公比r_m及び吸熱応答係数phi_1_A_m

    Args:

    Returns:
      list: 表 E.7 指数項mにおける公比r_m及び吸熱応答係数phi_1_A_m

    """
    table_e_7 = [
        (0.999996185007277, -0.0000000373932617900396),
        (0.999984740116433, 0.0000007335783188647870),
        (0.999938961862903, -0.0000099402124533592900),
        (0.999755929789981, 0.0005842990301842850000),
        (0.999023876718580, 0.00038443482380871200009),
        (0.996101618495491, 0.0006186789168868810000),
        (0.984491514535530, 0.0027429049659913000000),
        (0.939413062813476, 0.0008772601274016750000),
        (0.778800783071405, 0.0116100392142522000000),
        (0.367879441171442, 0.0015655689737126900000)
    ]
    return table_e_7


def get_phi_1_A_m(m):
    """指数項mにおける吸熱応答係数phi_1_A_m

    Args:
      m(int): 指数項m

    Returns:
      tuple: 指数項mにおける吸熱応答係数phi_1_A_m

    """
    return get_table_e_7()[m - 1][1]


def get_Theta_uf_d_t_runup(underfloor_insulation, Theta_ex_d_t):
    """<<助走計算>> 当該住戸の床下温度 (℃) (13)

    Args:
      underfloor_insulation(bool): 床下空間が断熱空間内である場合はTrue
      Theta_ex_d_t(ndarray): 外気温度 (℃)

    Returns:
      ndarray: 助走計算>> 当該住戸の床下温度 (℃) (13)

    """

    # 床の温度差係数 (-)
    H_floor = 0.7

    # TODO: H_base_IS は仕様書においては未定義
    H_base_IS = 0.7

    # 冷房時の室温 (℃)
    Theta_in_C = 27.0

    # 暖房時の室温 (℃)
    Theta_in_H = 20.0

    # 計算領域の確保
    Theta_uf_d_t = np.zeros(24 * 365)

    if underfloor_insulation:
        # 床下空間が断熱区間内である場合
        # (13-1a) Theta_ex_d_t < Theta_in_H の場合
        f1a = Theta_ex_d_t < Theta_in_H
        Theta_uf_d_t[f1a] = Theta_in_H

        # (13-2a) Theta_in_C < Theta_ex_d_t の場合
        f2a = Theta_in_C < Theta_ex_d_t
        Theta_uf_d_t[f2a] = Theta_in_C

        # (13-3a) Theta_in_H <= Theta_ex_d_t <= Theta_in_C の場合
        f3a = np.logical_and(Theta_in_H <= Theta_ex_d_t, Theta_ex_d_t <= Theta_in_C)
        Theta_uf_d_t[f3a] = Theta_ex_d_t[f3a]
    else:
        # 床下空間が断熱区間外である場合
        # (13-1b) Theta_ex_d_t < Theta_in_H の場合
        f1b = Theta_ex_d_t < Theta_in_H
        Theta_uf_d_t[f1b] = Theta_ex_d_t[f1b] * H_floor + Theta_in_H * (1 - H_floor)

        # (13-2b) Theta_in_C < Theta_ex_d_t の場合
        f2b = Theta_in_C < Theta_ex_d_t
        Theta_uf_d_t[f2b] = Theta_ex_d_t[f2b] * H_floor + Theta_in_C * (1 - H_floor)

        # (13-3b) Theta_in_H <= Theta_ex_d_t <= Theta_in_C の場合
        f3b = np.logical_and(Theta_in_H <= Theta_ex_d_t, Theta_ex_d_t <= Theta_in_C)
        Theta_uf_d_t[f3b] = Theta_ex_d_t[f3b]

    return Theta_uf_d_t
