# ============================================================================
# 第三章 暖冷房負荷と外皮性能
# 第一節 全般
# Ver.09（エネルギー消費性能計算プログラム（住宅版）Ver.02.05～）
# ============================================================================

import numpy as np
from functools import lru_cache

# 暖冷房負荷ファイルの読み込み
from pyhees.section3_1_file import \
    get_filename, \
    get_L_dash_H_R_TSl_Qj_muH_j_k_d_t_i, \
    get_L_dash_CS_R_NVl_Qj_muH_j_k_d_t_i, \
    get_L_dash_CL_R_NVl_Qj_muH_j_k_d_t_i

# 床下空間を経由して外気を導入する方式
import pyhees.section3_1_d as uf

# 空気集熱式太陽熱利用設備による負荷削減量
import pyhees.section9_3 as ass

from pyhees.section11_1 import load_outdoor, get_Theta_ex


# ============================================================================
# 5. 暖冷房負荷の補正
# ============================================================================


@lru_cache()
def calc_L_H_d_t_i(region, A_A, A_MR, A_OR, mode_H, mode_C, TS, Q, mu_H, mu_C, NV_MR, NV_OR, hex, etr_dash_t, r_A_ufvnt,
                   underfloor_insulation,
                   R_l_i, floorheating, hotwater_use=None, supply_target=None, sol_region=None, P_alpha=None,
                   P_beta=None,
                   A_col=None, V_fan_P0=None, m_fan_test=None, d0=None, d1=None, r_A_ufvnt_ass=None,
                   ufv_insulation=None):
    """ 暖冷房区画i݅の１時間当たりの暖房負荷 (1)

    :param region: 省エネルギー区分
    :type region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param mode_H: 暖房方式
    :type mode_H: str
    :param mode_C: 冷房方式
    :type mode_C: str
    :param TS: 蓄熱の利用
    :type TS: bool
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_H: 当該住戸の暖房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_H: float
    :param mu_C: 当該住戸の冷房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_C: float
    :param NV_MR: 主たる居室における通風の利用における相当換気回数
    :type NV_MR: float
    :param NV_OR: その他の居室における通風の利用における相当換気回数
    :type NV_OR: float
    :param hex: 熱交換換気の有無
    :type hex: bool
    :param etr_dash_t: 熱交換型換気設備の補正温度交換効率[-]
    :type etr_dash_t: ndarray
    :param r_A_ufvnt: 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
    :type r_A_ufvnt: float
    :param underfloor_insulation: 床下空間が断熱空間内である場合はTrue
    :type underfloor_insulation: bool
    :param R_l_i: 敷設率
    :type R_l_i: float
    :param floorheating: 温水床暖房又は電気ヒーター床暖房を暖冷房区画݅において採用する
    :type floorheating: bool
    :param hotwater_use: 空気集熱式太陽熱利用設備が給湯部を有する場合はTrue
    :type hotwater_use: bool
    :param supply_target: 集熱後の空気を供給する先
    :type supply_target: str
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
    :param m_fan_test: 集熱器群を構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2))
    :type m_fan_test: tuple
    :param d0: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の切片 (-)
    :type d0: tuple
    :param d1: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K))
    :type d1: tuple
    :param r_A_ufvnt_ass: 集熱後の空気を供給する床下の面積の割合
    :type r_A_ufvnt_ass: float
    :param ufv_insulation: 床下空間が断熱空間内である場合はTrue
    :type ufv_insulation: bool
    :return: 暖冷房区画i݅の１時間当たりの暖房負荷 (1)
    :rtype: tuple
    """
    L_H_d_t_i = np.zeros((12, 24 * 365))

    outdoor = load_outdoor()
    Theta_ex_d_t = get_Theta_ex(region, outdoor)

    # 負荷補正前の暖房負荷
    L_dash_H_d_t_i, L_dash_H_R_d_t_i = calc_L_dash_H_d_t_i(
        region=region,
        A_A=A_A,
        A_MR=A_MR,
        A_OR=A_OR,
        mode_H=mode_H,
        mode_C=mode_C,
        NV_MR=NV_MR,
        NV_OR=NV_OR,
        TS=TS,
        Q=Q,
        mu_H=mu_H,
        mu_C=mu_C,
        hex=hex,
        etr_dash_t=etr_dash_t,
        r_A_ufvnt=r_A_ufvnt,
        underfloor_insulation=underfloor_insulation,
        Theta_ex_d_t=Theta_ex_d_t,
        hotwater_use=hotwater_use,
        supply_target=supply_target,
        sol_region=sol_region,
        P_alpha=P_alpha,
        P_beta=P_beta,
        A_col=A_col,
        V_fan_P0=V_fan_P0,
        m_fan_test=m_fan_test,
        d0=d0,
        d1=d1,
        r_A_ufvnt_ass=r_A_ufvnt_ass,
        ufv_insulation=ufv_insulation
    )

    # ----- 負荷補正の実施 -----
    for i in range(1, 13):
        if mode_H[i - 1] is not None:
            # 外皮等の表面温度による放射温度を考慮した負荷補正係数
            f_R_Evp_i = get_f_R_Evp_i(region=region, mode=mode_H[i - 1], Q=Q)

            # 暖房設備の方式による放射温度を考慮した負荷補正係数
            f_R_Eqp_i = get_f_R_Eqp_i(floorheating=floorheating[i - 1], mode=mode_H[i - 1], R_l_i=R_l_i[i - 1])

            # 上下温度分布を考慮した負荷補正係数
            f_TD_i = get_f_TD_i(floorheating=floorheating[i - 1], region=region, mode=mode_H[i - 1], Q=Q)

            L_H_d_t_i[i - 1, :] = L_dash_H_d_t_i[i - 1, :] * f_R_Evp_i * f_R_Eqp_i * f_TD_i  # (1)
        else:
            L_H_d_t_i[i - 1, :] = L_dash_H_d_t_i[i - 1, :]  # (1)

    return L_H_d_t_i, L_dash_H_R_d_t_i


def get_table_3():
    """ 表 3 式(2)における係数

    :return: 表 3 式(2)における係数
    :rtype: list
    """

    table_3 = [
        (0.031, 0.971, 0.041, 0.975, 0.059, 1.038),
        (0.032, 0.966, 0.043, 0.970, 0.060, 1.034),
        (0.030, 0.963, 0.039, 0.970, 0.050, 1.049),
        (0.027, 0.972, 0.033, 0.985, 0.040, 1.081),
        (0.028, 0.966, 0.034, 0.981, 0.038, 1.092),
        (0.029, 0.961, 0.035, 0.974, 0.039, 1.090),
        (0.020, 0.921, 0.024, 0.937, 0.021, 1.094)
    ]

    return table_3


def get_f_R_Evp_i(region, mode, Q):
    """ 外皮等の表面温度による放射温度を考慮した負荷補正係数 (2)


    :param region: 省エネルギー区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: str
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :return: 外皮等の表面温度による放射温度を考慮した負荷補正係数
    :rtype: float
    """

    # 式(2)における係数
    if mode == 'い' or mode == '住戸全体を連続的に暖房する方式' or mode == '全館連続':
        a_R_Evp_i = get_table_3()[region - 1][0]
        b_R_Evp_i = get_table_3()[region - 1][1]
    elif mode == 'ろ':
        a_R_Evp_i = get_table_3()[region - 1][2]
        b_R_Evp_i = get_table_3()[region - 1][3]
    elif mode == 'は':
        a_R_Evp_i = get_table_3()[region - 1][4]
        b_R_Evp_i = get_table_3()[region - 1][5]
    else:
        raise ValueError(mode)

    return a_R_Evp_i * Q + b_R_Evp_i  # (2)


def get_table_4():
    """ 表 4 式(3)における係数

    :return: 表 4 式(3)における係数
    :rtype: list
    """
    table_4 = (-0.105, -0.137, -0.231)

    return table_4


def get_f_R_Eqp_i(floorheating, mode, R_l_i):
    """ 暖冷房区画݅における暖房設備の方式による放射温度を考慮した負荷補正係数 (3)

    :param floorheating: 温水床暖房又は電気ヒーター床暖房を暖冷房区画݅において採用する
    :type floorheating: bool
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: str
    :param R_l_i: 敷設率
    :type R_l_i: float
    :return: 暖冷房区画݅における暖房設備の方式による放射温度を考慮した負荷補正係数
    :rtype: float
    """

    # 温水床暖房又は電気ヒーター床暖房を暖冷房区画݅において採用する場合は、式(3)により表されるものとし、
    # 温水床暖房又は電気ヒーター床暖房を暖冷房区画݅において採用しない場合は、1.0とする。
    if floorheating:

        # 式(3)における係数
        if mode == 'い':
            a_R_Eqp_i = get_table_4()[0]
        elif mode == 'ろ':
            a_R_Eqp_i = get_table_4()[1]
        elif mode == 'は':
            a_R_Eqp_i = get_table_4()[2]
        else:
            raise ValueError(mode)

        return a_R_Eqp_i * R_l_i + 1.0  # (3)
    else:
        return 1.0


def get_table_5():
    """ 表 5 式(5)における係数

    :return: 表 5 式(5)における係数
    :rtype: list
    """

    table_5 = [
        (0.0157, 1.0842, 0.0163, 1.0862, 0.0176, 1.0860),
        (0.0157, 1.0928, 0.0163, 1.0954, 0.0176, 1.0981),
        (0.0097, 1.1048, 0.0101, 1.1079, 0.0110, 1.1147),
        (0.0063, 1.1111, 0.0066, 1.1146, 0.0072, 1.1235),
        (0.0045, 1.1223, 0.0047, 1.1264, 0.0053, 1.1391),
        (0.0045, 1.1277, 0.0047, 1.1320, 0.0053, 1.1465),
        (0.0014, 1.1357, 0.0015, 1.1404, 0.0017, 1.1576)
    ]

    return table_5


def get_f_TD_i(floorheating, region, mode, Q):
    """ 暖冷房区画݅における上下温度分布を考慮した負荷補正係数

    :param floorheating: 温水床暖房又は電気ヒーター床暖房を暖冷房区画݅において採用する
    :type floorheating: bool
    :param region: 省エネルギー区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: string
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :return: 暖冷房区画݅における上下温度分布を考慮した負荷補正係数
    :rtype: float
    """

    # 暖冷房区画iに温水床暖房又は電気ヒーター床暖房を採用する場合は1.0とし、それ以外の場合は、式(5)により表される。
    if floorheating:
        return 1.0
    else:

        if mode == 'い' or mode == '住戸全体を連続的に暖房する方式' or mode == '全館連続':
            a_TD_i = get_table_5()[region - 1][0]
            f_TD_max = get_table_5()[region - 1][1]
        elif mode == 'ろ':
            a_TD_i = get_table_5()[region - 1][2]
            f_TD_max = get_table_5()[region - 1][3]
        elif mode == 'は':
            a_TD_i = get_table_5()[region - 1][4]
            f_TD_max = get_table_5()[region - 1][5]
        else:
            raise ValueError(mode)

        return min(a_TD_i * Q ** 2 + 1, f_TD_max)  # (5)


def calc_L_CS_d_t_i(region, A_A, A_MR, A_OR, mode_H, mode_C, NV_MR, NV_OR, Q, mu_H, mu_C, TS, etr_dash_t, hex,
                    r_A_ufvnt, underfloor_insulation):
    """ 暖冷房区画iの 1 時間当たりの冷房顕熱負荷

    :param region: 省エネルギー区分
    :type region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param mode_H: 暖房方式
    :type mode_H: str
    :param mode_C: 冷房方式
    :type mode_C: str
    :param NV_MR: 主たる居室における通風の利用における相当換気回数
    :type NV_MR: float
    :param NV_OR: その他の居室における通風の利用における相当換気回数
    :type NV_OR: float
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_H: 当該住戸の暖房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_H: float
    :param mu_C: 当該住戸の冷房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_C: float
    :param TS: 蓄熱の利用
    :type TS: bool
    :param etr_dash_t: 熱交換型換気設備の補正温度交換効率[-]
    :type etr_dash_t: ndarray
    :param hex: 熱交換換気の有無
    :type hex: bool
    :param r_A_ufvnt: 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
    :type r_A_ufvnt: float
    :param underfloor_insulation: 床下空間が断熱空間内である場合はTrue
    :type underfloor_insulation: bool
    :return: 暖冷房区画iの 1 時間当たりの冷房顕熱負荷
    :rtype: ndarray
    """
    from pyhees.section11_1 import load_outdoor, get_Theta_ex
    outdoor = load_outdoor()
    Theta_ex_d_t = get_Theta_ex(region, outdoor)

    L_CS_d_t_i = calc_L_dash_CS_d_t_i(region, A_A, A_MR, A_OR, mode_H, mode_C, NV_MR, NV_OR, Q, mu_H, mu_C, TS,
                                      etr_dash_t, hex, r_A_ufvnt,
                                      underfloor_insulation, Theta_ex_d_t)  # (6a)
    return L_CS_d_t_i


def calc_L_CL_d_t_i(region, A_A, A_MR, A_OR, mode, NV_MR, NV_OR, Q, mu_C):
    """ 暖冷房区画iの 1 時間当たりの冷房潜熱負荷

    :param region: 省エネルギー区分
    :type region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: str
    :param NV_MR: 主たる居室における通風の利用における相当換気回数
    :type NV_MR: float
    :param NV_OR: その他の居室における通風の利用における相当換気回数
    :type NV_OR: float
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_C: 当該住戸の冷房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_C: float
    :return: 暖冷房区画iの 1 時間当たりの冷房潜熱負荷
    :rtype: ndarray
    """
    L_CL_d_t_i = calc_L_dash_CL_d_t_i(region, A_A, A_MR, A_OR, mode, NV_MR, NV_OR, Q, mu_C)  # (6a)
    return L_CL_d_t_i


# ============================================================================
# 6. 負荷補正前の暖冷房負荷
# ============================================================================

def calc_L_dash_H_d_t_i(region, A_A, A_MR, A_OR, mode_H, mode_C, NV_MR, NV_OR, TS, Q, mu_H, mu_C, hex, etr_dash_t,
                        r_A_ufvnt, underfloor_insulation,
                        Theta_ex_d_t, hotwater_use=None, supply_target=None, sol_region=None, P_alpha=None, P_beta=None,
                        A_col=None, V_fan_P0=None, m_fan_test=None, d0=None, d1=None, r_A_ufvnt_ass=None,
                        ufv_insulation=None):
    """ 負荷補正前の暖房負荷 (7a) B_H


    :param region: 省エネルギー区分
    :type region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param mode_H: 暖房方式
    :type mode_H: str
    :param mode_C: 冷房方式
    :type mode_C: str
    :param NV_MR: 主たる居室における通風の利用における相当換気回数
    :type NV_MR: float
    :param NV_OR: その他の居室における通風の利用における相当換気回数
    :type NV_OR: float
    :param TS: 蓄熱の利用
    :type TS: bool
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_H: 当該住戸の暖房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_H: float
    :param mu_C: 当該住戸の冷房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_C: float
    :param hex: 熱交換換気の有無
    :type hex: bool
    :param etr_dash_t: 熱交換型換気設備の補正温度交換効率[-]
    :type etr_dash_t: ndarray
    :param r_A_ufvnt: 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
    :type r_A_ufvnt: float
    :param underfloor_insulation: 床下空間が断熱空間内である場合はTrue
    :type underfloor_insulation: bool
    :param Theta_ex_d_t: 外気温度 (℃)
    :type Theta_ex_d_t: ndarray
    :param hotwater_use: 空気集熱式太陽熱利用設備が給湯部を有する場合はTrue
    :type hotwater_use: bool
    :param supply_target: 集熱後の空気を供給する先
    :type supply_target: str
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
    :param m_fan_test: 集熱器群を構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2))
    :type m_fan_test: tuple
    :param d0: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の切片 (-)
    :type d0: tuple
    :param d1: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K))
    :type d1: tuple
    :param r_A_ufvnt_ass: 集熱後の空気を供給する床下の面積の割合
    :type r_A_ufvnt_ass: float
    :param ufv_insulation: 床下空間が断熱空間内である場合はTrue
    :type ufv_insulation: bool
    :return: 負荷補正前の暖房負荷 (7a) B_H

    :rtype: tuple
    """
    # 標準住戸の負荷補正前の暖房負荷 (8) C_H
    L_dash_H_R_d_t_i = calc_dash_H_R_d_t_i(A_A, A_MR, A_OR, Q, TS, etr_dash_t, hex, mode_H, mu_H, region)

    # 標準住戸の負荷補正前の冷房顕熱負荷  C_C
    L_dash_CS_R_d_t_i = calc_L_dash_CS_R_d_t_i(A_A, A_MR, A_OR, region, mode_C, NV_MR, NV_OR, Q, mu_C)

    # 床面積按分及び床下換気・空気集熱式太陽熱利用設備による負荷削減
    L_dash_H_d_t_i = np.zeros((12, 24 * 365))
    for i in range(1, 13):
        # 床面積
        A_HCZ_R_i = get_A_HCZ_R_i(i)
        A_HCZ_i = get_A_HCZ_i(i, A_A, A_MR, A_OR)

        # 床下空間を経由して外気を導入する換気方式による暖房負荷削減
        delta_L_dash_H_uf_d_t_i = uf.calc_delta_L_dash_H_uf_d_t_i(
            i=i,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            A_HCZ_i=A_HCZ_i,
            region=region,
            Q=Q,
            r_A_ufvnt=r_A_ufvnt,
            underfloor_insulation=underfloor_insulation,
            Theta_ex_d_t=Theta_ex_d_t,
            L_dash_H_R_d_t_i=L_dash_H_R_d_t_i,
            L_dash_CS_R_d_t_i=L_dash_CS_R_d_t_i
        )

        # 空気集熱式太陽熱利用設備を採用する場合
        if supply_target is not None:
            delta_L_dash_H_ass_d_t_i = ass.calc_delta_L_dash_H_ass_d_t_i(
                i=i,
                supply_target=supply_target,
                L_dash_H_R_d_t_i=L_dash_H_R_d_t_i,
                L_dash_CS_R_d_t_i=L_dash_CS_R_d_t_i,
                region=region,
                sol_region=sol_region,
                A_HCZ_i=A_HCZ_i,
                A_A=A_A,
                A_MR=A_MR,
                A_OR=A_OR,
                Q=Q,
                hotwater_use=hotwater_use,
                Theta_ex_d_t=Theta_ex_d_t,
                P_alpha=P_alpha,
                P_beta=P_beta,
                A_col=A_col,
                V_fan_P0=V_fan_P0,
                m_fan_test=m_fan_test,
                d0=d0,
                d1=d1,
                ufv_insulation=ufv_insulation,
                r_A_ufvnt=r_A_ufvnt_ass
            )
        else:
            delta_L_dash_H_ass_d_t_i = np.zeros(24 * 365)

        # (7a)
        L_dash_H_d_t_i[i - 1, :] = L_dash_H_R_d_t_i[i - 1, :] * (A_HCZ_i / A_HCZ_R_i)

        f = L_dash_H_d_t_i[i - 1, :] > 0
        L_dash_H_d_t_i[i - 1, f] = L_dash_H_d_t_i[i - 1, f] - delta_L_dash_H_uf_d_t_i[f]

        f = L_dash_H_d_t_i[i - 1, :] > 0
        L_dash_H_d_t_i[i - 1, f] = L_dash_H_d_t_i[i - 1, f] - delta_L_dash_H_ass_d_t_i[f]

    return L_dash_H_d_t_i, L_dash_H_R_d_t_i


def calc_L_dash_CS_d_t_i(region, A_A, A_MR, A_OR, mode_H, mode_C, NV_MR, NV_OR, Q, mu_H, mu_C, TS, etr_dash_t, hex,
                         r_A_ufvnt, underfloor_insulation,
                         Theta_ex_d_t):
    """ 負荷補正前の冷房顕熱負荷 (7b)

    :param region: 省エネルギー区分
    :type region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param mode_H: 暖房方式
    :type mode_H: str
    :param mode_C: 冷房方式
    :type mode_C: str
    :param NV_MR: 主たる居室における通風の利用における相当換気回数
    :type NV_MR: float
    :param NV_OR: その他の居室における通風の利用における相当換気回数
    :type NV_OR: float
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_H: 当該住戸の暖房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_H: float
    :param mu_C: 当該住戸の冷房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_C: float
    :param TS: 蓄熱の利用
    :type TS: bool
    :param etr_dash_t: 熱交換型換気設備の補正温度交換効率[-]
    :type etr_dash_t: ndarray
    :param hex: 熱交換換気の有無
    :type hex: bool
    :param r_A_ufvnt: 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
    :type r_A_ufvnt: float
    :param underfloor_insulation: 床下空間が断熱空間内である場合はTrue
    :type underfloor_insulation: bool
    :param Theta_ex_d_t: 外気温度 (℃)
    :type Theta_ex_d_t: ndarray
    :return: 負荷補正前の冷房顕熱負荷 (7b)
    :rtype: ndarray
    """
    L_dash_CS_R_d_t_i = np.zeros((12, 24 * 365))
    L_dash_CS_d_t_i = np.zeros((12, 24 * 365))

    # 標準住戸の冷房顕熱負荷
    for i in range(1, 13):
        if mode_C[i - 1] is not None:
            L_dash_CS_R_d_t_i[i - 1, :] = get_L_dash_CS_R_d_t_i(region, mode_C[i - 1], NV_MR, NV_OR, Q, mu_C, i)

    # 標準住戸の負荷補正前の暖房負荷 (8) C_H
    if region == 8:
        L_dash_H_R_d_t_i = np.zeros((12, 24 * 365))
    else:
        L_dash_H_R_d_t_i = calc_dash_H_R_d_t_i(A_A, A_MR, A_OR, Q, TS, etr_dash_t, hex, mode_H, mu_H, region)

    # 床面積による按分と床下空間を経由して外気を導入する換気方式による冷房顕熱負荷削減
    for i in range(1, 13):
        if mode_C[i - 1] is not None:
            # 床面積
            A_HCZ_R_i = get_A_HCZ_R_i(i)
            A_HCZ_i = get_A_HCZ_i(i, A_A, A_MR, A_OR)

            # 床下空間を経由して外気を導入する換気方式による冷房顕熱負荷削減
            delta_L_dash_CS_uf_d_t_i = uf.calc_delta_L_dash_CS_R_d_t_i(i, region, Q, r_A_ufvnt, underfloor_insulation,
                                                                       A_A, A_MR, A_OR, A_HCZ_i, Theta_ex_d_t,
                                                                       L_dash_H_R_d_t_i, L_dash_CS_R_d_t_i)

            L_dash_CS_d_t_i[i - 1, :] = L_dash_CS_R_d_t_i[i - 1, :] * (
                    A_HCZ_i / A_HCZ_R_i) - delta_L_dash_CS_uf_d_t_i  # (7b)

    return L_dash_CS_d_t_i


def calc_L_dash_CL_d_t_i(region, A_A, A_MR, A_OR, mode, NV_MR, NV_OR, Q, mu_C):
    """ 負荷補正前の冷房潜熱負荷 (7c)

    :param region: 省エネルギー区分
    :type region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: str
    :param NV_MR: 主たる居室における通風の利用における相当換気回数
    :type NV_MR: float
    :param NV_OR: その他の居室における通風の利用における相当換気回数
    :type NV_OR: float
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_C: 当該住戸の冷房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_C: float
    :return: 負荷補正前の冷房潜熱負荷 (7c)
    :rtype: ndarray
    """
    L_dash_CL_R_d_t_i = np.zeros((12, 24 * 365))
    L_dash_CL_d_t_i = np.zeros((12, 24 * 365))

    for i in range(1, 13):
        if mode[i - 1] is not None:
            # 床面積
            A_HCZ_R_i = get_A_HCZ_R_i(i)
            A_HCZ_i = get_A_HCZ_i(i, A_A, A_MR, A_OR)

            L_dash_CL_R_d_t_i[i - 1, :] = calc_L_dash_CL_R_d_t_i(region, mode[i - 1], NV_MR, NV_OR, Q, mu_C, i)

            L_dash_CL_d_t_i[i - 1, :] = L_dash_CL_R_d_t_i[i - 1, :] * (A_HCZ_i / A_HCZ_R_i)  # (7c)

    return L_dash_CL_d_t_i


# ============================================================================
# 7. 標準住戸の負荷補正前の暖冷房負荷
# ============================================================================

# ============================================================================
# 7.1 標準住戸の負荷補正前の暖房負荷 
# ============================================================================


def calc_dash_H_R_d_t_i(A_A, A_MR, A_OR, Q, TS, etr_dash_t, hex, mode, mu_H, region):
    """ 標準住戸の負荷補正前の暖房負荷 (8)

    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param TS: 蓄熱の利用
    :type TS: bool
    :param etr_dash_t: 熱交換型換気設備の補正温度交換効率[-]
    :type etr_dash_t: ndarray
    :param hex: 熱交換換気の有無
    :type hex: bool
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: str
    :param mu_H: 当該住戸の暖房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_H: float
    :param region: 省エネルギー区分
    :type region: int
    :return: 標準住戸の負荷補正前の暖房負荷 (8)
    :rtype: ndarray
    """
    L_dash_H_R_d_t_i = np.zeros((12, 24 * 365))

    # 標準住戸の負荷補正前の暖房負荷を全居室求める
    for i in range(1, 13):
        # 床面積
        A_HCZ_i = get_A_HCZ_i(i, A_A, A_MR, A_OR)

        if mode[i - 1] is not None and A_HCZ_i > 0:
            L_dash_H_R_d_t_i[i - 1, :] = calc_L_dash_H_R_d_t_i(
                region=region,
                mode=mode[i - 1],
                TS=TS,
                Q=Q,
                mu_H=mu_H,
                hex=hex,
                etr_dash_t=etr_dash_t,
                i=i
            )
        else:
            L_dash_H_R_d_t_i[i - 1, :] = np.zeros(24 * 365)
    return L_dash_H_R_d_t_i


def get_table_6():
    """ 表 6 蓄熱の採用の可否

    :return: 表 6 蓄熱の採用の可否
    :rtype: list
    """

    table_6 = [
        ('不可', '不可', '可', '可', '可'),
        ('不可', '不可', '可', '可', '可'),
        ('不可', '不可', '可', '可', '可'),
        ('不可', '不可', '可', '可', '可'),
        ('不可', '不可', '可', '可', '可'),
        ('不可', '不可', '不可', '可', '可'),
        ('不可', '不可', '不可', '可', '可')
    ]

    return table_6


def calc_L_dash_H_R_d_t_i(region, mode, TS, Q, mu_H, hex, etr_dash_t, i):
    """ 標準住戸の負荷補正前の暖房負荷 (8)

    :param region: 省エネルギー区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は'
    :type mode: str
    :param TS: 蓄熱の利用
    :type TS: bool
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_H: 当該住戸の暖房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_H: float
    :param hex: 熱交換換気の有無
    :type hex: bool
    :param etr_dash_t: 熱交換型換気設備の補正温度交換効率[-]
    :type etr_dash_t: ndarray
    :param i: 暖冷房区画の番号
    :type i: int
    :return:
    :rtype:
    """
    if not TS:
        # 蓄熱の利用なしの場合
        L_dash_H_R_TSl_d_t_i = calc_L_dash_H_R_TSl_d_t_i(region, mode, 1, Q, mu_H, hex, etr_dash_t, i)  # (8-1)
    else:
        # 蓄熱の利用ありの場合
        L_dash_H_R_TSl_d_t_i = calc_L_dash_H_R_TSl_d_t_i(region, mode, 2, Q, mu_H, hex, etr_dash_t, i)  # (8-2)

    return L_dash_H_R_TSl_d_t_i


def calc_L_dash_H_R_TSl_d_t_i(region, mode, l, Q, mu_H, hex, etr_dash_t, i):
    """ 暖房負荷のQ値按分 (9)

    :param region: 省エネルギー区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は'
    :type mode: str
    :param l: 蓄熱の利用の程度の区分
    :type l: int
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_H: 当該住戸の暖房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_H: float
    :param hex: 熱交換換気の有無
    :type hex: bool
    :param etr_dash_t: 熱交換型換気設備の補正温度交換効率[-]
    :type etr_dash_t: ndarray
    :param i: 暖冷房区画の番号
    :type i: int
    :return: 暖房負荷のQ値按分 (9)
    :rtype: ndarray
    """
    # 熱交換型換気設備による暖房負荷低減を考慮した補正熱損失係数
    Q_HEXC = get_Q_HEXC(region, Q, hex, etr_dash_t)

    if region in [1, 2, 3, 4, 5, 6, 7]:

        Q1 = get_Q_j(region, 1)
        Q2 = get_Q_j(region, 2)
        Q3 = get_Q_j(region, 3)
        Q4 = get_Q_j(region, 4)

        # (9a)
        if Q_HEXC == Q1:
            return calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 1, mu_H, hex, i)
        elif Q_HEXC == Q2:
            return calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 2, mu_H, hex, i)
        elif Q_HEXC == Q3:
            return calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 3, mu_H, hex, i)
        elif Q_HEXC == Q4:
            return calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 4, mu_H, hex, i)
        elif Q_HEXC >= Q2:
            return (Q_HEXC - Q2) / (Q1 - Q2) * calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 1, mu_H, hex, i) \
                   + (Q_HEXC - Q1) / (Q2 - Q1) * calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 2, mu_H, hex, i)
        elif Q2 > Q_HEXC >= Q3:
            return (Q_HEXC - Q3) / (Q2 - Q3) * calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 2, mu_H, hex, i) \
                   + (Q_HEXC - Q2) / (Q3 - Q2) * calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 3, mu_H, hex, i)
        elif Q3 > Q_HEXC:
            return (Q_HEXC - Q4) / (Q3 - Q4) * calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 3, mu_H, hex, i) \
                   + (Q_HEXC - Q3) / (Q4 - Q3) * calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 4, mu_H, hex, i)
        else:
            raise ValueError(Q_HEXC)

    elif region in [8]:

        Q1 = get_Q_j(region, 1)
        Q2 = get_Q_j(region, 2)
        Q3 = get_Q_j(region, 3)

        # (9b)
        if Q == Q1:
            return calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 1, mu_H, hex, i)
        elif Q == Q2:
            return calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 2, mu_H, hex, i)
        elif Q == Q3:
            return calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 3, mu_H, hex, i)
        elif Q >= Q2:
            return (Q_HEXC - Q2) / (Q1 - Q2) * calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 1, mu_H, hex, i) \
                   + (Q_HEXC - Q1) / (Q2 - Q1) * calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 2, mu_H, hex, i)
        elif Q2 > Q >= Q3:
            return (Q_HEXC - Q3) / (Q2 - Q3) * calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 2, mu_H, hex, i) \
                   + (Q_HEXC - Q2) / (Q3 - Q2) * calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, 3, mu_H, hex, i)
        else:
            raise ValueError(Q)

    else:
        raise ValueError(region)


def calc_L_dash_H_R_TSl_Qj_d_t_i(region, mode, l, j, mu_H, hex, i):
    """ 暖房負荷 μ値按分 (10)

    :param region: 省エネルギー区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: str
    :param l: 蓄熱の利用の程度の区分
    :type l: int
    :param j: 断熱性能の区分
    :type j: int
    :param mu_H: 当該住戸の暖房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_H: float
    :param hex: 熱交換換気の有無
    :type hex: bool
    :param i: 暖冷房区画の番号
    :type i: int
    :return: 暖房負荷 μ値按分 (10)
    :rtype: ndarray
    """
    mu_H_j_1 = get_mu_H_j_k(region, j, 1)
    mu_H_j_2 = get_mu_H_j_k(region, j, 2)
    mu_H_j_3 = get_mu_H_j_k(region, j, 3)

    if mu_H < mu_H_j_2:
        return (mu_H - mu_H_j_2) / (mu_H_j_1 - mu_H_j_2) * get_L_dash_H_R_TSl_Qj_muH_j_k_d_t_i(region, mode, l, j, 1,
                                                                                               hex, i) \
               + (mu_H - mu_H_j_1) / (mu_H_j_2 - mu_H_j_1) * get_L_dash_H_R_TSl_Qj_muH_j_k_d_t_i(region, mode, l, j, 2,
                                                                                                 hex, i)
    elif mu_H_j_2 <= mu_H:
        return (mu_H - mu_H_j_3) / (mu_H_j_2 - mu_H_j_3) * get_L_dash_H_R_TSl_Qj_muH_j_k_d_t_i(region, mode, l, j, 2,
                                                                                               hex, i) \
               + (mu_H - mu_H_j_2) / (mu_H_j_3 - mu_H_j_2) * get_L_dash_H_R_TSl_Qj_muH_j_k_d_t_i(region, mode, l, j, 3,
                                                                                                 hex, i)
    else:
        raise ValueError(mu_H)


def get_table_7():
    """ 表 7 断熱性能の区分݆jの熱損失係数Qj

    :return: 表 7 断熱性能の区分݆jの熱損失係数Qj
    :rtype: list
    """

    table_7 = [
        (2.8, 2.8, 4.0, 4.7, 5.19, 5.19, 8.27, 8.27),
        (1.8, 1.8, 2.7, 3.3, 4.2, 4.2, 4.59, 8.01),
        (1.6, 1.6, 1.9, 2.4, 2.7, 2.7, 2.7, 3.7),
        (1.4, 1.4, 1.4, 1.9, 1.9, 1.9, 1.9, 3.7)
    ]

    return table_7


def get_Q_j(region, j):
    """ 断熱性能の区分j݆の熱損失係数ܳQ_j

    :param region: 省エネルギー区分
    :type region: int
    :param j: 断熱性能の区分
    :type j: int
    :return: 断熱性能の区分j݆の熱損失係数ܳQ_j
    :rtype: float
    """

    # 断熱性能の区分݆の熱損失係数Q_j(j=1-4)は地域の区分に応じて表 7 により表される。
    return get_table_7()[j - 1][region - 1]


def get_table_8():
    """ 表 8 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数mu_H_j_k及び冷房期の日射取得係数mu_C_j_k

    :return: 表 8 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数mu_H_j_k及び冷房期の日射取得係数mu_C_j_k
    :rtype: list
    """
    table_8 = [
        (0.029, 0.027, 0.044, 0.048, 0.062, 0.061, 0.129, 0),
        (0.021, 0.022, 0.036, 0.039, 0.050, 0.048, 0.106, 0.11),
        (0.079, 0.074, 0.091, 0.112, 0.138, 0.134, 0.206, 0),
        (0.052, 0.052, 0.065, 0.080, 0.095, 0.090, 0.146, 0.154),
        (0.115, 0.106, 0.123, 0.161, 0.197, 0.191, 0.268, 0),
        (0.071, 0.071, 0.083, 0.107, 0.124, 0.117, 0.172, 0.184),
        (0.029, 0.027, 0.040, 0.046, 0.057, 0.056, 0.063, 0),
        (0.021, 0.022, 0.032, 0.037, 0.044, 0.043, 0.046, 0.129),
        (0.075, 0.070, 0.087, 0.102, 0.132, 0.128, 0.140, 0),
        (0.049, 0.049, 0.061, 0.072, 0.089, 0.085, 0.086, 0.174),
        (0.109, 0.101, 0.119, 0.142, 0.191, 0.185, 0.202, 0),
        (0.068, 0.068, 0.079, 0.094, 0.119, 0.112, 0.111, 0.204),
        (0.025, 0.024, 0.030, 0.033, 0.038, 0.037, 0.038, 0),
        (0.019, 0.019, 0.023, 0.026, 0.027, 0.026, 0.025, 0.023),
        (0.071, 0.066, 0.072, 0.090, 0.104, 0.101, 0.107, 0),
        (0.046, 0.046, 0.049, 0.061, 0.066, 0.062, 0.059, 0.068),
        (0.106, 0.098, 0.104, 0.130, 0.153, 0.148, 0.158, 0),
        (0.065, 0.065, 0.067, 0.082, 0.090, 0.084, 0.080, 0.098),
        (0.024, 0.022, 0.022, 0.026, 0.030, 0.029, 0.030, 0),
        (0.017, 0.017, 0.017, 0.019, 0.021, 0.020, 0.019, 0.019),
        (0.070, 0.065, 0.065, 0.078, 0.090, 0.087, 0.092, 0),
        (0.045, 0.045, 0.043, 0.052, 0.056, 0.053, 0.050, 0.050),
        (0.104, 0.096, 0.096, 0.116, 0.137, 0.132, 0.141, 0),
        (0.063, 0.063, 0.060, 0.072, 0.078, 0.073, 0.070, 0.065)
    ]

    return table_8


def get_mu_H_j_k(region, j, k):
    """ 断熱性能の区分݆jにおける日射取得性能の区分k݇の暖房期の日射取得係数 mu_H_j_k

    :param region: 省エネルギー区分
    :type region: int
    :param j: 断熱性能の区分
    :type j: int
    :param k: 日射遮蔽レベル 1-3 (int)
    :type k: int
    :return: 断熱性能の区分݆jにおける日射取得性能の区分k݇の暖房期の日射取得係数 mu_H_j_k
    :rtype: float
    """
    return get_table_8()[(j - 1) * 6 + (k - 1) * 2 + 0][region - 1]


def get_mu_C_j_k(region, j, k):
    """ 断熱性能の区分݆jにおける日射取得性能の区分k݇の冷房期の日射取得係数 mu_C_j_k

    :param region: 省エネルギー区分
    :type region: int
    :param j: 断熱性能の区分
    :type j: int
    :param k: 日射遮蔽レベル 1-3 (int)
    :type k: int
    :return: 断熱性能の区分݆jにおける日射取得性能の区分k݇の冷房期の日射取得係数 mu_C_j_k
    :rtype: float
    """
    return get_table_8()[(j - 1) * 6 + (k - 1) * 2 + 1][region - 1]


# ============================================================================
# 7.2 標準住戸の負荷補正前の冷房負荷
# ============================================================================

def calc_L_dash_CS_R_d_t_i(A_A, A_MR, A_OR, region, mode, NV_MR, NV_OR, Q, mu_C):
    """ 標準住戸の負荷補正前の冷房顕熱負荷

    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param region: 省エネルギー区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: str
    :param NV_MR: 主たる居室における通風の利用における相当換気回数
    :type NV_MR: float
    :param NV_OR: その他の居室における通風の利用における相当換気回数
    :type NV_OR: float
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_C: 当該住戸の冷房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_C: float
    :return: 標準住戸の負荷補正前の冷房顕熱負荷
    :rtype: ndarray
    """
    L_dash_CS_R_d_t_i = np.zeros((12, 24 * 365))

    # 標準住戸の負荷補正前の暖房負荷を全居室求める
    for i in range(1, 13):
        # 床面積
        A_HCZ_i = get_A_HCZ_i(i, A_A, A_MR, A_OR)

        if mode[i - 1] is not None and A_HCZ_i > 0:
            L_dash_CS_R_d_t_i[i - 1, :] = get_L_dash_CS_R_d_t_i(
                region=region,
                mode=mode[i - 1],
                NV_MR=NV_MR,
                NV_OR=NV_OR,
                Q=Q,
                mu_C=mu_C,
                i=i
            )
        else:
            L_dash_CS_R_d_t_i[i - 1, :] = np.zeros(24 * 365)
    return L_dash_CS_R_d_t_i


# --------------------------------------------------
# 換気回数按分
# --------------------------------------------------

def get_L_dash_CS_R_d_t_i(region, mode, NV_MR, NV_OR, Q, mu_C, i):
    """ 標準住戸の負荷補正前の冷房顕熱負荷

    :param region: 省エネルギー区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: str
    :param NV_MR: 主たる居室における通風の利用における相当換気回数
    :type NV_MR: float
    :param NV_OR: その他の居室における通風の利用における相当換気回数
    :type NV_OR: float
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_C: 当該住戸の冷房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_C: float
    :param i: 暖冷房区画の番号
    :type i: int
    :return: 標準住戸の負荷補正前の冷房顕熱負荷
    :rtype: ndarray
    """
    if mode == 'い' or mode == '全館連続':
        # 通風の利用における相当換気回数ܸܰは、「住戸全体を連続的に冷房する方式」の場合はすべての暖冷房区画において0.0回/h とする。
        NV = 0.0
    elif mode in ['ろ', 'は'] or mode == '居室間歇':
        # 主たる居室
        if i == 1:
            if NV_MR == 0:
                NV = 0.0
            elif NV_MR == 5:
                NV = 5.0
            elif NV_MR == 20:
                NV = 20.0
            else:
                raise ValueError(NV_MR)
        # その他の居室
        elif 2 <= i and i <= 5:
            if NV_OR == 0:
                NV = 0.0
            elif NV_OR == 5:
                NV = 5.0
            elif NV_OR == 20:
                NV = 20.0
            else:
                raise ValueError(NV_OR)
        else:
            raise ValueError(i)
    else:
        raise ValueError(mode)

    NV1 = get_NV(1)
    NV2 = get_NV(2)
    NV3 = get_NV(3)

    # (11a)
    if NV == NV1:
        return calc_L_dash_CS_R_NVl_d_t_i(region, mode, 1, Q, mu_C, i)
    elif NV == NV2:
        return calc_L_dash_CS_R_NVl_d_t_i(region, mode, 2, Q, mu_C, i)
    elif NV == NV3:
        return calc_L_dash_CS_R_NVl_d_t_i(region, mode, 3, Q, mu_C, i)
    elif NV < NV2:
        L_dash_CS_R_NV1_d_t_i = calc_L_dash_CS_R_NVl_d_t_i(region, mode, 1, Q, mu_C, i)
        L_dash_CS_R_NV2_d_t_i = calc_L_dash_CS_R_NVl_d_t_i(region, mode, 2, Q, mu_C, i)
        return (NV - NV2) / (NV1 - NV2) * L_dash_CS_R_NV1_d_t_i + (NV - NV1) / (NV2 - NV1) * L_dash_CS_R_NV2_d_t_i
    elif NV2 <= NV:
        L_dash_CS_R_NV2_d_t_i = calc_L_dash_CS_R_NVl_d_t_i(region, mode, 2, Q, mu_C, i)
        L_dash_CS_R_NV3_d_t_i = calc_L_dash_CS_R_NVl_d_t_i(region, mode, 3, Q, mu_C, i)
        return (NV - NV3) / (NV2 - NV3) * L_dash_CS_R_NV2_d_t_i + (NV - NV2) / (NV3 - NV2) * L_dash_CS_R_NV3_d_t_i
    else:
        raise NotImplementedError()


def calc_L_dash_CL_R_d_t_i(region, mode, NV_MR, NV_OR, Q, mu_C, i):
    """ 標準住戸の負荷補正前の冷房潜熱負荷


    :param region: 省エネルギー区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: str
    :param NV_MR: 主たる居室における通風の利用における相当換気回数
    :type NV_MR: float
    :param NV_OR: その他の居室における通風の利用における相当換気回数
    :type NV_OR: float
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_C: 当該住戸の冷房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_C: float
    :param i: 暖冷房区画の番号
    :type i: int
    :return: 標準住戸の負荷補正前の冷房潜熱負荷
    :rtype: ndarray
    """
    if mode == 'い' or mode == '全館連続':
        # 通風の利用における相当換気回数ܸܰは、「住戸全体を連続的に冷房する方式」の場合はすべての暖冷房区画において0.0回/h とする。
        NV = 0.0
    elif mode in ['ろ', 'は'] or mode == '居室間歇':
        # 主たる居室
        if i == 1:
            if NV_MR == 0:
                NV = 0.0
            elif NV_MR == 5:
                NV = 5.0
            elif NV_MR == 20:
                NV = 20.0
            else:
                raise ValueError(NV_MR)
        # その他の居室
        elif 2 <= i and i <= 5:
            if NV_OR == 0:
                NV = 0.0
            elif NV_OR == 5:
                NV = 5.0
            elif NV_OR == 20:
                NV = 20.0
            else:
                raise ValueError(NV_OR)
        else:
            raise ValueError(i)
    else:
        raise ValueError(mode)

    NV1 = get_NV(1)
    NV2 = get_NV(2)
    NV3 = get_NV(3)

    # (11b)
    if NV == NV1:
        return calc_L_dash_CL_R_NVl_d_t_i(region, mode, 1, Q, mu_C, i)
    elif NV == NV2:
        return calc_L_dash_CL_R_NVl_d_t_i(region, mode, 2, Q, mu_C, i)
    elif NV == NV3:
        return calc_L_dash_CL_R_NVl_d_t_i(region, mode, 3, Q, mu_C, i)
    elif NV < NV2:
        L_dash_CL_R_NV1_d_t_i = calc_L_dash_CL_R_NVl_d_t_i(region, mode, 1, Q, mu_C, i)
        L_dash_CL_R_NV2_d_t_i = calc_L_dash_CL_R_NVl_d_t_i(region, mode, 2, Q, mu_C, i)
        return (NV - NV2) / (NV1 - NV2) * L_dash_CL_R_NV1_d_t_i + (NV - NV1) / (NV2 - NV1) * L_dash_CL_R_NV2_d_t_i
    elif NV2 <= NV:
        L_dash_CL_R_NV2_d_t_i = calc_L_dash_CL_R_NVl_d_t_i(region, mode, 2, Q, mu_C, i)
        L_dash_CL_R_NV3_d_t_i = calc_L_dash_CL_R_NVl_d_t_i(region, mode, 3, Q, mu_C, i)
        return (NV - NV3) / (NV2 - NV3) * L_dash_CL_R_NV2_d_t_i + (NV - NV2) / (NV3 - NV2) * L_dash_CL_R_NV3_d_t_i
    else:
        raise NotImplementedError()


def get_table_9():
    """ 表 9 通風の利用に関する区分݈の通風の利用における相当換気回数 NV_l

    :return: 表 9 通風の利用に関する区分݈の通風の利用における相当換気回数 NV_l
    :rtype: list
    """

    table_9 = (0.0, 5.0, 20.0)

    return table_9


def get_NV(l):
    """ 通風の利用に関する区分lの通風の利用における相当換気回数 NV_l


    :param l: 蓄熱の利用の程度の区分
    :type l: int
    :return: 通風の利用に関する区分lの通風の利用における相当換気回数 NV_l
    :rtype: float
    """
    return get_table_9()[l - 1]


# --------------------------------------------------
# Q値按分
# --------------------------------------------------

def calc_L_dash_CS_R_NVl_d_t_i(region, mode, l, Q, mu_C, i):
    """ 冷房顕熱負荷のQ値按分 (12)

    :param region: 省エネルギー区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: str
    :param l: 蓄熱の利用の程度の区分
    :type l: int
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_C: 当該住戸の冷房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_C: float
    :param i: 暖冷房区画の番号
    :type i: int
    :return: 冷房顕熱負荷のQ値按分 (12)
    :rtype: ndarray
    """
    if region in [1, 2, 3, 4, 5, 6, 7]:

        Q1 = get_Q_j(region, 1)
        Q2 = get_Q_j(region, 2)
        Q3 = get_Q_j(region, 3)
        Q4 = get_Q_j(region, 4)

        # (12a)
        if Q == Q1:
            return calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 1, mu_C, i)
        elif Q == Q2:
            return calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 2, mu_C, i)
        elif Q == Q3:
            return calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 3, mu_C, i)
        elif Q == Q4:
            return calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 4, mu_C, i)
        elif Q >= Q2:
            L_dash_CS_R_NVl_Q1_d_t_i = calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 1, mu_C, i)
            L_dash_CS_R_NVl_Q2_d_t_i = calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 2, mu_C, i)
            return (Q - Q2) / (Q1 - Q2) * L_dash_CS_R_NVl_Q1_d_t_i + (Q - Q1) / (Q2 - Q1) * L_dash_CS_R_NVl_Q2_d_t_i
        elif Q2 > Q and Q >= Q3:
            L_dash_CS_R_NVl_Q2_d_t_i = calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 2, mu_C, i)
            L_dash_CS_R_NVl_Q3_d_t_i = calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 3, mu_C, i)
            return (Q - Q3) / (Q2 - Q3) * L_dash_CS_R_NVl_Q2_d_t_i + (Q - Q2) / (Q3 - Q2) * L_dash_CS_R_NVl_Q3_d_t_i
        elif Q3 > Q:
            L_dash_CS_R_NVl_Q3_d_t_i = calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 3, mu_C, i)
            L_dash_CS_R_NVl_Q4_d_t_i = calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 4, mu_C, i)
            return (Q - Q4) / (Q3 - Q4) * L_dash_CS_R_NVl_Q3_d_t_i + (Q - Q3) / (Q4 - Q3) * L_dash_CS_R_NVl_Q4_d_t_i
        else:
            raise NotImplementedError()
    elif region in [8]:

        Q1 = get_Q_j(region, 1)
        Q2 = get_Q_j(region, 2)
        Q3 = get_Q_j(region, 3)

        # (12c)
        if Q == Q1:
            return calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 1, mu_C, i)
        elif Q == Q2:
            return calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 2, mu_C, i)
        elif Q == Q3:
            return calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 3, mu_C, i)
        elif Q >= Q2:
            L_dash_CS_R_NVl_Q1_d_t_i = calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 1, mu_C, i)
            L_dash_CS_R_NVl_Q2_d_t_i = calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 2, mu_C, i)
            return (Q - Q2) / (Q1 - Q2) * L_dash_CS_R_NVl_Q1_d_t_i + (Q - Q1) / (Q2 - Q1) * L_dash_CS_R_NVl_Q2_d_t_i
        elif Q2 > Q:
            L_dash_CS_R_NVl_Q2_d_t_i = calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 2, mu_C, i)
            L_dash_CS_R_NVl_Q3_d_t_i = calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, 3, mu_C, i)
            return (Q - Q3) / (Q2 - Q3) * L_dash_CS_R_NVl_Q2_d_t_i + (Q - Q2) / (Q3 - Q2) * L_dash_CS_R_NVl_Q3_d_t_i
        else:
            raise ValueError(Q)
    else:
        raise ValueError(region)


def calc_L_dash_CL_R_NVl_d_t_i(region, mode, l, Q, mu_C, i):
    """ 冷房潜熱負荷のQ値按分 (12)

    :param region: 省エネルギー区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: str
    :param l: 蓄熱の利用の程度の区分
    :type l: int
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_C: 当該住戸の冷房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_C: float
    :param i: 暖冷房区画の番号
    :type i: int
    :return: 冷房潜熱負荷のQ値按分
    :rtype: ndarray
    """
    if region in [1, 2, 3, 4, 5, 6, 7]:

        Q1 = get_Q_j(region, 1)
        Q2 = get_Q_j(region, 2)
        Q3 = get_Q_j(region, 3)
        Q4 = get_Q_j(region, 4)

        # (12b)
        if Q == Q1:
            return calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 1, mu_C, i)
        elif Q == Q2:
            return calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 2, mu_C, i)
        elif Q == Q3:
            return calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 3, mu_C, i)
        elif Q == Q4:
            return calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 4, mu_C, i)
        elif Q >= Q2:
            L_dash_CL_R_NVl_Q1_d_t_i = calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 1, mu_C, i)
            L_dash_CL_R_NVl_Q2_d_t_i = calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 2, mu_C, i)
            return (Q - Q2) / (Q1 - Q2) * L_dash_CL_R_NVl_Q1_d_t_i + (Q - Q1) / (Q2 - Q1) * L_dash_CL_R_NVl_Q2_d_t_i
        elif Q2 > Q >= Q3:
            L_dash_CL_R_NVl_Q2_d_t_i = calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 2, mu_C, i)
            L_dash_CL_R_NVl_Q3_d_t_i = calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 3, mu_C, i)
            return (Q - Q3) / (Q2 - Q3) * L_dash_CL_R_NVl_Q2_d_t_i + (Q - Q2) / (Q3 - Q2) * L_dash_CL_R_NVl_Q3_d_t_i
        elif Q3 > Q:
            L_dash_CL_R_NVl_Q3_d_t_i = calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 3, mu_C, i)
            L_dash_CL_R_NVl_Q4_d_t_i = calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 4, mu_C, i)
            return (Q - Q4) / (Q3 - Q4) * L_dash_CL_R_NVl_Q3_d_t_i + (Q - Q3) / (Q4 - Q3) * L_dash_CL_R_NVl_Q4_d_t_i
        else:
            raise ValueError(Q)
    elif region in [8]:

        Q1 = get_Q_j(region, 1)
        Q2 = get_Q_j(region, 2)
        Q3 = get_Q_j(region, 3)

        # (12d)
        if Q == Q1:
            return calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 1, mu_C, i)
        elif Q == Q2:
            return calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 2, mu_C, i)
        elif Q == Q3:
            return calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 3, mu_C, i)
        elif Q >= Q2:
            L_dash_CL_R_NVl_Q1_d_t_i = calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 1, mu_C, i)
            L_dash_CL_R_NVl_Q2_d_t_i = calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 2, mu_C, i)
            return (Q - Q2) / (Q1 - Q2) * L_dash_CL_R_NVl_Q1_d_t_i + (Q - Q1) / (Q2 - Q1) * L_dash_CL_R_NVl_Q2_d_t_i
        elif Q2 > Q:
            L_dash_CL_R_NVl_Q2_d_t_i = calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 2, mu_C, i)
            L_dash_CL_R_NVl_Q3_d_t_i = calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, 3, mu_C, i)
            return (Q - Q3) / (Q2 - Q3) * L_dash_CL_R_NVl_Q2_d_t_i + (Q - Q2) / (Q3 - Q2) * L_dash_CL_R_NVl_Q3_d_t_i
        else:
            raise ValueError(Q)
    else:
        raise ValueError(region)


# --------------------------------------------------
# μ値按分
# --------------------------------------------------

def calc_L_dash_CS_R_NVl_Qj_d_t_i(region, mode, l, j, mu_C, i):
    """ 冷房顕熱負荷のμ値按分 (13a)

    :param region: 省エネルギー区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: str
    :param l: 蓄熱の利用の程度の区分
    :type l: int
    :param j: 断熱性能の区分
    :type j: int
    :param mu_C: 当該住戸の冷房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_C: float
    :param i: 暖冷房区画の番号
    :type i: int
    :return: 冷房顕熱負荷のμ値按分 (13a)
    :rtype: ndarray
    """
    mu_C_j_1 = get_mu_C_j_k(region, j, 1)
    mu_C_j_2 = get_mu_C_j_k(region, j, 2)
    mu_C_j_3 = get_mu_C_j_k(region, j, 3)

    if mu_C == mu_C_j_1:
        return get_L_dash_CS_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 1, i)
    elif mu_C == mu_C_j_2:
        return get_L_dash_CS_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 2, i)
    elif mu_C == mu_C_j_3:
        return get_L_dash_CS_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 3, i)
    elif mu_C < mu_C_j_2:
        L_dash_CS_R_NVl_Qj_muH_j_1_d_t_i = get_L_dash_CS_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 1, i)
        L_dash_CS_R_NVl_Qj_muH_j_2_d_t_i = get_L_dash_CS_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 2, i)
        return (mu_C - mu_C_j_2) / (mu_C_j_1 - mu_C_j_2) * L_dash_CS_R_NVl_Qj_muH_j_1_d_t_i \
               + (mu_C - mu_C_j_1) / (mu_C_j_2 - mu_C_j_1) * L_dash_CS_R_NVl_Qj_muH_j_2_d_t_i
    elif mu_C_j_2 <= mu_C:
        L_dash_CS_R_NVl_Qj_muH_j_2_d_t_i = get_L_dash_CS_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 2, i)
        L_dash_CS_R_NVl_Qj_muH_j_3_d_t_i = get_L_dash_CS_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 3, i)
        return (mu_C - mu_C_j_3) / (mu_C_j_2 - mu_C_j_3) * L_dash_CS_R_NVl_Qj_muH_j_2_d_t_i \
               + (mu_C - mu_C_j_2) / (mu_C_j_3 - mu_C_j_2) * L_dash_CS_R_NVl_Qj_muH_j_3_d_t_i
    else:
        raise ValueError(mu_C)


def calc_L_dash_CL_R_NVl_Qj_d_t_i(region, mode, l, j, mu_C, i):
    """ 冷房潜熱負荷のμ値按分 (13b)

    :param region: 省エネルギー区分
    :type region: int
    :param mode: 運転モード 'い', 'ろ', 'は' (str)
    :type mode: str
    :param l: 蓄熱の利用の程度の区分
    :type l: int
    :param j: 断熱性能の区分
    :type j: int
    :param mu_C: 当該住戸の冷房期の日射取得係数（(W/m2)/(W/m2)）
    :type mu_C: float
    :param i: 暖冷房区画の番号
    :type i: int
    :return: 冷房潜熱負荷のμ値按分
    :rtype: ndarray
    """
    mu_C_j_1 = get_mu_C_j_k(region, j, 1)
    mu_C_j_2 = get_mu_C_j_k(region, j, 2)
    mu_C_j_3 = get_mu_C_j_k(region, j, 3)

    if mu_C == mu_C_j_1:
        return get_L_dash_CL_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 1, i)
    elif mu_C == mu_C_j_2:
        return get_L_dash_CL_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 2, i)
    elif mu_C == mu_C_j_3:
        return get_L_dash_CL_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 3, i)
    elif mu_C < mu_C_j_2:
        L_dash_CL_R_NVl_Qj_muH_j_1_d_t_i = get_L_dash_CL_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 1, i)
        L_dash_CL_R_NVl_Qj_muH_j_2_d_t_i = get_L_dash_CL_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 2, i)
        return (mu_C - mu_C_j_2) / (mu_C_j_1 - mu_C_j_2) * L_dash_CL_R_NVl_Qj_muH_j_1_d_t_i \
               + (mu_C - mu_C_j_1) / (mu_C_j_2 - mu_C_j_1) * L_dash_CL_R_NVl_Qj_muH_j_2_d_t_i
    elif mu_C_j_2 <= mu_C:
        L_dash_CL_R_NVl_Qj_muH_j_2_d_t_i = get_L_dash_CL_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 2, i)
        L_dash_CL_R_NVl_Qj_muH_j_3_d_t_i = get_L_dash_CL_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, 3, i)
        return (mu_C - mu_C_j_3) / (mu_C_j_2 - mu_C_j_3) * L_dash_CL_R_NVl_Qj_muH_j_2_d_t_i \
               + (mu_C - mu_C_j_2) / (mu_C_j_3 - mu_C_j_2) * L_dash_CL_R_NVl_Qj_muH_j_3_d_t_i
    else:
        raise ValueError(mu_C)


# ============================================================================
# 8. 熱損失係数の計算方法
# ============================================================================

def get_Q_HEXC(region, Q, hex, etr_dash_t):
    """ 熱交換型換気設備による暖房負荷低減を考慮した補正熱損失係数

    :param region: 省エネルギー区分
    :type region: int
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param hex: 熱交換換気の有無
    :type hex: bool
    :param etr_dash_t: 熱交換型換気設備の補正温度交換効率[-]
    :type etr_dash_t: ndarray
    :return: 熱交換型換気設備による暖房負荷低減を考慮した補正熱損失係数
    :rtype: float
    """
    # 地域の区分が 1 地域～７地域において熱交換型換気設備を採用している場合は、式(14)により表されることとし、
    # 地域の区分が 8 地域又は熱交換型換気設備を採用していない場合は、熱損失係数ܳに等しいとする。
    if region == 8 or hex == False:
        return Q
    elif region in [1, 2, 3, 4, 5, 6, 7]:
        C_V = 0.35  # 空気の容積比熱
        r_V = 4.0 / 3.0  # 床面積当たりの換気量の比
        return Q - C_V * r_V * etr_dash_t  # (14)
    else:
        raise ValueError((region, hex))


def get_Q(Q_dash):
    """ 熱損失係数

    :param Q_dash: 熱損失係数（換気による熱損失を含まない）(W/m2K)
    :type Q_dash: float
    :return: 熱損失係数
    :rtype: float
    """
    return Q_dash + 0.35 * 0.5 * 2.4  # (15)


# ============================================================================
# 9. 暖冷房区画iの床面積
# ============================================================================

def get_table_10():
    """ 表10 標準住戸における主たる居室、その他の居室及び非居室の面積、並びに暖冷房区画iの床面積

    :return: 表10 標準住戸における主たる居室、その他の居室及び非居室の面積、並びに暖冷房区画iの床面積
    :rtype: list
    """
    # 表10 標準住戸における主たる居室、その他の居室及び非居室の面積、並びに暖冷房区画iの床面積
    table_10 = [
        29.81,
        16.56,
        13.25,
        10.76,
        10.77,
        3.31,
        1.66,
        3.31,
        13.25,
        4.97,
        10.77,
        1.66
    ]
    return table_10


def get_A_HCZ_R_i(i):
    """ 標準住戸における暖冷房区画iの床面積

    :param i: 暖冷房区画i
    :type i: int
    :return: 標準住戸における暖冷房区画iの床面積
    :rtype: float
    """

    return get_table_10()[i - 1]


def get_A_HCZ_i(i, A_A, A_MR, A_OR):
    """ 暖冷房区画iの床面積 (16a)

    :param i: 暖冷房区画i
    :type i: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :return: 暖冷房区画iの床面積 (16a)
    :rtype: float
    """

    # 標準住戸における暖冷房区画iの床面積
    A_HCZ_R_i = get_A_HCZ_R_i(i)

    # 非居室の床面積（m2）(16b)
    A_NR = get_A_NR(A_A, A_MR, A_OR)

    A_MR_R = 29.81
    A_OR_R = 51.34
    A_NO_R = 38.93

    # 暖冷房区画iの床面積を按分して求める
    if i == 1:
        return A_HCZ_R_i * A_MR / A_MR_R
    elif 2 <= i <= 5:
        return A_HCZ_R_i * A_OR / A_OR_R
    elif 6 <= i <= 12:
        return A_HCZ_R_i * A_NR / A_NO_R
    else:
        raise ValueError(i)


def get_A_NR(A_A, A_MR, A_OR):
    """ 非居室の床面積（m2）(16b)

    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :return: 非居室の床面積（m2）
    :rtype: float
    """

    return A_A - A_MR - A_OR

# ============================================================================
# 10. 暖房日
# ============================================================================
