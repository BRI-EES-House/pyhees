# ============================================================================
# 第二章 住宅部分の一次エネルギー消費量
# 第二節 設計一次エネルギー消費量
# Ver.13（エネルギー消費性能計算プログラム（住宅版）Ver.2022.10～）
# ============================================================================

import numpy as np
from math import ceil
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple, TypedDict, Optional

from pyhees.section2_1_b import get_f_prim
from pyhees.section2_1_c import get_n_p
from pyhees.section3_1 import get_Q
from pyhees.section3_2 import calc_insulation_performance
from pyhees.section4_1 import calc_heating_load, calc_heating_mode, get_virtual_heating_devices, get_virtual_heatsource, \
    get_E_E_H_d_t, get_E_G_H_d_t, calc_E_K_H_d_t, calc_E_M_H_d_t, calc_E_UT_H_d_t
from pyhees.section4_1 import calc_cooling_load, calc_E_E_C_d_t, calc_E_G_C_d_t, calc_E_K_C_d_t, calc_E_M_C_d_t, calc_E_UT_C_d_t
import pyhees.section4_2 as dc
import pyhees.section4_2_b as dc_spec
from pyhees.section5 import calc_E_E_V_d_t
from pyhees.section6 import calc_E_E_L_d_t
from pyhees.section7_1 import calc_hotwater_load, calc_E_E_W_d_t, calc_E_G_W_d_t, calc_E_K_W_d_t, get_E_M_W_d_t
from pyhees.section7_1_b import get_virtual_hotwater
from pyhees.section8 import calc_E_G_CG_d_t, get_E_E_CG_self, get_E_K_CG_d_t
from pyhees.section9_1 import calc_E_E_PV_d_t
from pyhees.section10 import calc_E_E_AP_d_t, get_E_G_AP_d_t, get_E_K_AP_d_t, get_E_M_AP_d_t
from pyhees.section10 import get_E_E_CC_d_t, calc_E_G_CC_d_t, get_E_K_CC_d_t, get_E_M_CC_d_t


class DesignedPrimaryEnergyTotal(TypedDict):
    """各適合基準における設計一次エネルギー消費量

    Attributes:
        E_T_gn_du (Optional[float]):
            建築物エネルギー消費性能基準（気候風土適応住宅を除く）における設計一次エネルギー消費量 (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_T_trad_du (Optional[float]):
            建築物エネルギー消費性能基準（気候風土適応住宅）における設計一次エネルギー消費量 (GJ/年)
            住宅の種類が「行政庁認定住宅」以外の場合はNone
        E_T_indc_du (Optional[float]):
            建築物エネルギー消費性能誘導基準における誘導設計一次エネルギー消費量 (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_T_rb_du (Optional[float]):
            特定建築主基準における設計一次エネルギー消費量 (GJ/年)
            住宅の種類が「事業主基準」以外の場合はNone
        E_T_lcb_du (Optional[float]):
            建築物に係るエネルギーの使用の合理化の一層の促進その他の建築物の低炭素化の促進のために
            誘導すべき基準（建築物の低炭素化誘導基準）における誘導設計一次エネルギー消費量 (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_T_enh_du (Optional[float]):
            建築物に係るエネルギーの使用の合理化の一層の促進その他の建築物の低炭素化の促進のために
            誘導すべき基準（建築物の低炭素化誘導基準）の低炭素化措置における設計一次エネルギー消費量 (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_star_T_gn_du (Optional[float]):
            建築物エネルギー消費性能基準における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)
            住宅の種類が「事業主基準」以外の場合はNone

    NOTE:
        各適合基準のうち、建築物エネルギー消費性能基準（気候風土適応住宅を除く）についてのみ
        端数処理前の値(E_star_T_gn_du (MJ/年))を出力する(計算結果比較のため)
    """

    E_T_gn_du: Optional[float]
    E_T_trad_du: Optional[float]
    E_T_indc_du: Optional[float]
    E_T_rb_du: Optional[float]
    E_T_lcb_du: Optional[float]
    E_T_enh_du: Optional[float]
    E_star_T_gn_du: Optional[float]


class DesignedPrimaryEnergyTotalDash(TypedDict):
    """各適合基準における設計一次エネルギー消費量 (その他の設計一次エネルギー消費量を除く)

    Attributes:
        E_dash_T_gn_du (Optional[float]):
            建築物エネルギー消費性能基準（気候風土適応住宅を除く）における設計一次エネルギー消費量
            (その他の設計一次エネルギー消費量を除く) (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_dash_T_trad_du (Optional[float]):
            建築物エネルギー消費性能基準（気候風土適応住宅）における設計一次エネルギー消費量
            (その他の設計一次エネルギー消費量を除く) (GJ/年)
            住宅の種類が「行政庁認定住宅」以外の場合はNone
        E_dash_T_indc_du (Optional[float]):
            建築物エネルギー消費性能誘導基準における誘導設計一次エネルギー消費量
            (その他の設計一次エネルギー消費量を除く) (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_dash_T_rb_du (Optional[float]):
            特定建築主基準における設計一次エネルギー消費量
            (その他の設計一次エネルギー消費量を除く) (GJ/年)
            住宅の種類が「事業主基準」以外の場合はNone
        E_dash_T_lcb_du (Optional[float]):
            建築物に係るエネルギーの使用の合理化の一層の促進その他の建築物の低炭素化の促進のために
            誘導すべき基準（建築物の低炭素化誘導基準）における誘導設計一次エネルギー消費量
            (その他の設計一次エネルギー消費量を除く) (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
    """

    E_dash_T_gn_du: Optional[float]
    E_dash_T_trad_du: Optional[float]
    E_dash_T_indc_du: Optional[float]
    E_dash_T_rb_du: Optional[float]
    E_dash_T_lcb_du: Optional[float]


class DesignedPrimaryEnergyDetail(TypedDict):
    """各設備における設計一次エネルギー消費量／削減量

    Attributes:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S (float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/年)
        E_S_CG (float): 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量 (MJ/年)
        E_R (float): 1年当たりの太陽光発電設備による発電量のうちの自家消費分に係る設計一次エネルギー消費量の削減量 (MJ/年)
        E_M (float): 1年当たりのその他の設計一次エネルギー消費量 (MJ/年) 
    """

    E_H: float
    E_C: float
    E_V: float
    E_L: float
    E_W: float
    E_S: float
    E_S_CG: float
    E_R: float
    E_M: float


class DesignedSecondaryEnergyDetail(TypedDict):
    """各種設計二次エネルギー消費量／削減量

    NOTE:
        * 現状の実態としては、既存のコードで計算されているテスト対象外の出力項目をまとめただけの辞書クラスである。
        * 各種二次エネルギー消費量について、どの値をテスト対象として計算結果を出力するかについては、今後の検討が必要。
    """

    UPL: float
    E_gen: float
    E_E_gen: float
    E_E_PV_h_d_t: np.ndarray
    E_E: float
    E_G: float
    E_K: float


def calc_E_T(spec) -> Tuple[DesignedPrimaryEnergyTotal, DesignedPrimaryEnergyTotalDash, DesignedPrimaryEnergyDetail, DesignedSecondaryEnergyDetail]:
    """設計一次エネルギー消費量[GJ/年]を計算する

    Args:
        spec (dict): 住戸についての詳細なデータ

    Returns:
        E_T_dict (DesignedPrimaryEnergyTotal):
            各適合基準における設計一次エネルギー消費量合計値を格納する辞書
        E_T_dash_dict (DesignedPrimaryEnergyTotalDash):
            各適合基準における設計一次エネルギー消費量合計値(その他一次エネルギー消費量を除く)を格納する辞書
        E_pri_dict (DesignedPrimaryEnergyDetail):
            各設備における設計一次エネルギー消費量／削減量を格納する辞書
        E_sec_dict (DesignedSecondaryEnergyDetail):
            各設備における設計二次エネルギー消費量／削減量を格納する辞書

    """
    E_H = None
    E_C = None
    E_W = None
    E_L = None
    E_V = None
    E_M = None
    E_gen = None
    E_E_gen = None
    E_S = None

    E_E = None
    E_G = None
    E_K = None
    UPL = None

    # ---- 事前データ読み込み ----

    # 日射量データの読み込み
    from pyhees.section11_2 import load_solrad
    from pyhees.section9_1 import calc_E_E_PV_d_t

    solrad = None
    if (spec['SHC'] is not None or spec['PV'] is not None) and 'sol_region' in spec:
        if spec['sol_region'] is not None:
            solrad = load_solrad(spec['region'], spec['sol_region'])

    # ---- 外皮の計算 ----

    # 外皮の断熱性能の計算
    if spec['ENV'] is not None:
        U_A, _, _, _, Q_dash, eta_H, eta_C, _ = calc_insulation_performance(**spec['ENV'])
        # 熱損失係数
        Q = get_Q(Q_dash)
        A_env = spec['ENV'].get('A_env')
    else:
        Q = None
        eta_H, eta_C = None, None
        A_env = None

    # ---- 暖房設備 ----

    # 1 時間当たりの暖房設備の設計一次エネルギー消費量

    # 実質的な暖房機器の仕様を取得
    spec_MR, spec_OR = get_virtual_heating_devices(spec['region'], spec['H_MR'], spec['H_OR'])

    # 暖房方式及び運転方法の区分
    mode_MR, mode_OR = calc_heating_mode(region=spec['region'], H_MR=spec_MR, H_OR=spec_OR)

    # ---- 暖房負荷 ----

    # 暖房負荷の取得
    L_T_H_d_t_i, L_dash_H_R_d_t_i = calc_heating_load(
        spec['region'], spec['sol_region'],
        spec['A_A'], spec['A_MR'], spec['A_OR'],
        Q, eta_H, eta_C, spec['NV_MR'], spec['NV_OR'], spec['TS'], spec['r_A_ufvnt'], spec['HEX'],
        spec['underfloor_insulation'], spec['mode_H'], spec['mode_C'],
        spec_MR, spec_OR, mode_MR, mode_OR, spec['SHC'])

    # ---- 冷房負荷 ----

    # 冷房負荷の取得
    L_CS_d_t, L_CL_d_t = \
        calc_cooling_load(spec['region'], spec['A_A'], spec['A_MR'], spec['A_OR'], Q, eta_H, eta_C,
                          spec['NV_MR'], spec['NV_OR'], spec['r_A_ufvnt'], spec['underfloor_insulation'],
                          spec['mode_C'], spec['mode_H'], mode_MR, mode_OR, spec['TS'], spec['HEX'])

    # ---- 冷房設備 ----

    # 1 年当たりの冷房設備の設計一次エネルギー消費量
    E_C = calc_E_C(spec['region'], spec['A_A'], spec['A_MR'], spec['A_OR'],
                  A_env, eta_H, eta_C, Q,
                  spec['C_A'], spec['C_MR'], spec['C_OR'],
                  L_T_H_d_t_i, L_CS_d_t, L_CL_d_t, spec['mode_C'])


    # ---- 暖房設備 ----

    # 1 時間当たりの暖房設備の設計一次エネルギー消費量

    # 実質的な温水暖房機の仕様を取得
    spec_HS = get_virtual_heatsource(spec['region'], spec['H_HS'])

    # 暖房日の計算
    if spec['SHC'] is not None and spec['SHC']['type'] == '空気集熱式':
        from pyhees.section3_1_heatingday import get_heating_flag_d

        heating_flag_d = get_heating_flag_d(L_dash_H_R_d_t_i)
    else:
        heating_flag_d = None

    E_H = calc_E_H(spec['region'], spec['sol_region'], spec['A_A'], spec['A_MR'], spec['A_OR'],
                  A_env, eta_H, eta_C, Q,
                  spec['mode_H'],
                  spec['H_A'], spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, spec['HW'], spec['CG'], spec['SHC'],
                  heating_flag_d, L_T_H_d_t_i, L_CS_d_t, L_CL_d_t)

    # 暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値
    UPL = calc_E_UT_H(spec['region'], spec['A_A'], spec['A_MR'], spec['A_OR'], A_env, eta_H, eta_C, Q, spec['mode_H'],
                     spec['H_A'], spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, spec['HW'], spec['CG'],
                     L_T_H_d_t_i, L_CS_d_t, L_CL_d_t)
    UPL = np.sum(UPL)

    # 温水暖房負荷の計算
    L_HWH = calc_L_HWH(spec['A_A'], spec['A_MR'], spec['A_OR'], spec['HEX'], spec['H_HS'], spec['H_MR'],
                           spec['H_OR'], Q, spec['SHC'], spec['TS'], eta_H, eta_C, spec['NV_MR'], spec['NV_OR'],
                           spec['r_A_ufvnt'], spec['region'], spec['sol_region'], spec['underfloor_insulation'],
                           spec['HW'], spec['CG'])

    # ---- 給湯/コージェネ設備 ----

    # その他または設置しない場合
    spec_HW = get_virtual_hotwater(spec['region'], spec['HW'])

    # 1 年当たりの給湯設備（コージェネレーション設備を含む）の設計一次エネルギー消費量
    E_W, E_E_CG_gen_d_t, _, E_E_TU_aux_d_t, E_E_CG_h_d_t, E_G_CG_ded, e_BB_ave, Q_CG_h \
            = calc_E_W(spec['A_A'], spec['region'], spec['sol_region'], spec_HW, spec['SHC'], spec['CG'],
                      spec['H_A'],
                      spec['H_MR'], spec['H_OR'], spec['H_HS'], spec['C_A'], spec['C_MR'], spec['C_OR'],
                      spec['V'],
                      spec['L'], spec['A_MR'], spec['A_OR'], A_env, Q, eta_H, eta_C,
                      spec['NV_MR'],
                      spec['NV_OR'], spec['TS'], spec['r_A_ufvnt'], spec['HEX'],
                      spec['underfloor_insulation'],
                      spec['mode_H'], spec['mode_C'])

    # ---- 照明,換気,その他設備 ----

    # 1 年当たりの照明設備の設計一次エネルギー消費量
    E_L = calc_E_L(spec['A_A'], spec['A_MR'], spec['A_OR'], spec['L'])

    # 1 年当たりの機械換気設備の設計一次エネルギー消費量
    E_V = calc_E_V(spec['A_A'], spec['V'], spec['HEX'])

    # 1年当たりのその他の設計一次エネルギー消費量
    E_M = calc_E_M(spec['A_A'])

    # ---- 二次エネの計算 ----

    # 1 年当たりの設計消費電力量（kWh/年）
    E_E, E_E_PV_h_d_t, E_E_PV_d_t, E_E_CG_gen_d_t, E_E_CG_h_d_t, E_E_dmd_d_t, E_E_TU_aux_d_t = \
                calc_E_E(spec['region'], spec['sol_region'], spec['A_A'], spec['A_MR'], spec['A_OR'],
                        A_env, spec_HW, Q, spec['TS'], eta_H, eta_C, spec['r_A_ufvnt'],
                        spec['underfloor_insulation'], spec['NV_MR'], spec['NV_OR'],
                        spec['mode_H'], spec['mode_C'],
                        spec['V'], spec['L'],
                        spec['H_A'], spec['H_MR'], spec['H_OR'], spec['H_HS'],
                        spec['CG'], spec['SHC'],
                        L_T_H_d_t_i,
                        spec['C_A'], spec['C_MR'], spec['C_OR'], L_T_H_d_t_i,
                        L_CS_d_t, L_CL_d_t,
                        spec['HEX'], spec['PV'], solrad
                        )
    f_prim = get_f_prim()
    E_gen = (np.sum(E_E_PV_d_t) + np.sum(E_E_CG_gen_d_t)) * f_prim / 1000

    # 1 年当たりの設計ガス消費量（MJ/年）
    E_G = calc_E_G(spec['region'], spec['sol_region'], spec['A_A'], spec['A_MR'], spec['A_OR'],
                          A_env, Q, eta_H, eta_C, spec['NV_MR'], spec['NV_OR'], spec['TS'],
                          spec['r_A_ufvnt'], spec['HEX'], spec['underfloor_insulation'],
                          spec['H_A'], spec['H_MR'], spec['H_OR'], spec['H_HS'], spec['C_A'], spec['C_MR'],
                          spec['C_OR'], spec['V'], spec['L'], spec_HW, spec['SHC'],
                          spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, spec['mode_H'], spec['mode_C'],
                          spec['CG'],
                          L_T_H_d_t_i, L_HWH, heating_flag_d)

    # 1 年当たりの設計灯油消費量（MJ/年）
    E_K = calc_E_K(spec['region'], spec['sol_region'], spec['A_A'], spec['A_MR'], spec['A_OR'],
                          spec['H_A'],
                          spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, spec['CG'],
                          L_T_H_d_t_i,
                          L_HWH, heating_flag_d, spec_HW, spec['SHC'])

    # ---- エネルギー利用効率化の評価 ----

    # エネルギー利用効率化設備による設計一次エネルギー消費量の削減量
    E_E_CG_h = get_E_E_CG_h(E_E_CG_h_d_t)
    E_S, E_S_CG, E_R = calc_E_S(spec['region'], spec['sol_region'], spec['PV'], spec['CG'], E_E_dmd_d_t, E_E_CG_gen_d_t,
                   E_E_TU_aux_d_t, E_E_CG_h, E_G_CG_ded, e_BB_ave, Q_CG_h)

    E_E_gen = np.sum(calc_E_E_PV_d_t(spec['PV'], solrad) + E_E_CG_gen_d_t)

    # ---- 合計 ----

    # 各適合基準における設計一次エネルギー消費量合計値
    E_T_dict = calc_E_T_dict(E_H, E_C, E_V, E_L, E_W, E_S, E_S_CG, E_R, E_M, spec['type'])

    # 各適合基準における設計一次エネルギー消費量合計値(その他一次エネルギー消費量を除く)
    E_dash_T_dict = calc_E_dash_T_dict(E_H, E_C, E_V, E_L, E_W, E_S, E_S_CG, spec['type'])

    # 各設備における設計一次エネルギー消費量／削減量
    E_pri_dict = {
        'E_H': E_H,
        'E_C': E_C,
        'E_V': E_V,
        'E_L': E_L,
        'E_W': E_W,
        'E_S': E_S,
        'E_S_CG': E_S_CG,
        'E_R': E_R,
        'E_M': E_M,
    }

    # 各設備における設計二次エネルギー消費量／削減量
    E_sec_dict = {
        'UPL': UPL,
        'E_gen': E_gen,
        'E_E_gen': E_E_gen,
        'E_E_PV_h_d_t': E_E_PV_h_d_t,
        'E_E': E_E,
        'E_G': E_G,
        'E_K': E_K,
    }

    return E_T_dict, E_dash_T_dict, E_pri_dict, E_sec_dict


# ============================================================================
# 5. 設計一次エネルギー消費量および誘導設計一次エネルギー消費量
# ============================================================================


def calc_E_T_dict(E_H, E_C, E_V, E_L, E_W, E_S, E_S_CG, E_R, E_M, type) -> DesignedPrimaryEnergyTotal:
    E_T_gn_du   = None
    E_T_trad_du = None
    E_T_indc_du = None
    E_T_rb_du   = None
    E_T_lcb_du  = None
    E_T_enh_du  = None
    E_star_T_gn_du = None
    # NOTE: 
    #   各適合基準のうち、建築物エネルギー消費性能基準（気候風土適応住宅を除く）についてのみ
    #   端数処理前の値(E_star_T_gn_du (MJ/年))を出力する(計算結果比較のため)

    if type == '一般住宅':
        E_T_gn_du, E_star_T_gn_du = get_E_T_gn_du(E_H, E_C, E_V, E_L, E_W, E_S, E_M)
        E_T_indc_du = get_E_T_indc_du(E_H, E_C, E_V, E_L, E_W, E_S_CG, E_M)
        E_T_lcb_du = get_E_T_lcb_du(E_H, E_C, E_V, E_L, E_W, E_S_CG, E_M)
        E_T_enh_du = get_E_T_enh_du(E_H, E_C, E_V, E_L, E_W, E_S_CG, E_R, E_M)
    elif type == '事業主基準':
        E_T_rb_du = get_E_T_rb_du(E_H, E_C, E_V, E_L, E_W, E_S, E_M)
    elif type == '行政庁認定住宅':
        E_T_trad_du = get_E_T_trad_du(E_H, E_C, E_V, E_L, E_W, E_S, E_M)
    else:
        raise ValueError(type)

    return {
        'E_T_gn_du': E_T_gn_du,
        'E_T_trad_du': E_T_trad_du,
        'E_T_indc_du': E_T_indc_du,
        'E_T_rb_du': E_T_rb_du,
        'E_T_lcb_du': E_T_lcb_du,
        'E_T_enh_du': E_T_enh_du,
        'E_star_T_gn_du': E_star_T_gn_du,
    }


# ====================================================================
# 5.2 建築物エネルギー消費性能基準（気候風土適応住宅を除く）における設計一次エネルギー消費量
# ====================================================================

def get_E_T_gn_du(E_H, E_C, E_V, E_L, E_W, E_S, E_M) -> Tuple[float, float]:
    E_star_T_gn_du = get_E_star_T_gn_du(E_H, E_C, E_V, E_L, E_W, E_S, E_M)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    E_T_gn_du = ceil(E_star_T_gn_du / 100) / 10

    return E_T_gn_du, E_star_T_gn_du


def get_E_star_T_gn_du(E_H, E_C, E_V, E_L, E_W, E_S, E_M):
    """式(2) 建築物エネルギー消費性能基準における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S (float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/年)
        E_M (float): 1年当たりのその他の設計一次エネルギー消費量 (MJ/年)

    Returns:
        float: 建築物エネルギー消費性能基準における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)
    """
    return E_H + E_C + E_V + E_L + E_W - E_S + E_M


# ============================================================================
# 5.3 建築物エネルギー消費性能基準（気候風土適応住宅）における設計一次エネルギー消費量
# ============================================================================

def get_E_T_trad_du(E_H, E_C, E_V, E_L, E_W, E_S, E_M) -> float:
    """式(3) 建築物エネルギー消費性能基準（気候風土適応住宅）における設計一次エネルギー消費量 (GJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S (float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/年)
        E_M (float): 1年当たりのその他の設計一次エネルギー消費量 (MJ/年)

    Returns:
        float: 建築物エネルギー消費性能基準（気候風土適応住宅）における設計一次エネルギー消費量 (GJ/年)
    """
    # 式(4) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)
    E_star_T_trad_du = get_E_star_T_trad_du(E_H, E_C, E_V, E_L, E_W, E_S, E_M)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_T_trad_du / 100) / 10


def get_E_star_T_trad_du(E_H, E_C, E_V, E_L, E_W, E_S, E_M):
    """式(4) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S (float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/年)
        E_M (float): 1年当たりのその他の設計一次エネルギー消費量 (MJ/年)

    Returns:
        float: 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)
    """
    return E_H + E_C + E_V + E_L + E_W - E_S + E_M


# ============================================================================
# 5.4 建築物エネルギー消費性能誘導基準における誘導設計一次エネルギー消費量
# ============================================================================

def get_E_T_indc_du(E_H, E_C, E_V, E_L, E_W, E_S_CG, E_M) -> float:
    """式(5) 建築物エネルギー消費性能誘導基準における単位住戸の設計一次エネルギー消費量 (GJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S_CG (float): 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量 (MJ/年)
        E_M (float): 1年当たりのその他の設計一次エネルギー消費量 (MJ/年)

    Returns:
        float: 建築物エネルギー消費性能誘導基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
    """
    # 式(6) 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)
    E_star_T_indc_du = get_E_star_T_indc_du(E_H, E_C, E_V, E_L, E_W, E_S_CG, E_M)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_T_indc_du / 100) / 10


def get_E_star_T_indc_du(E_H, E_C, E_V, E_L, E_W, E_S_CG, E_M):
    """式(6) 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S_CG (float): 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量 (MJ/年)
        E_M (float): 1年当たりのその他の設計一次エネルギー消費量 (MJ/年)

    Returns:
        float: 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)
    """
    return E_H + E_C + E_V + E_L + E_W - E_S_CG + E_M


# ============================================================================
# 5.5 特定建築主基準における設計一次エネルギー消費量
# ============================================================================

def get_E_T_rb_du(E_H, E_C, E_V, E_L, E_W, E_S, E_M) -> float:
    """式(7) 特定建築主基準における単位住戸の設計一次エネルギー消費量 (GJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S (float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/年)
        E_M (float): 1年当たりのその他の設計一次エネルギー消費量 (MJ/年)

    Returns:
        float: 特定建築主基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
    """
    E_star_T_rb_du = get_E_star_T_rb_du(E_H, E_C, E_V, E_L, E_W, E_S, E_M)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_T_rb_du / 100) / 10


def get_E_star_T_rb_du(E_H, E_C, E_V, E_L, E_W, E_S, E_M):
    """式(8) 特定建築主基準における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S (float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/年)
        E_M (float): 1年当たりのその他の設計一次エネルギー消費量 (MJ/年)

    Returns:
        float: 特定建築主基準における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)
    """
    return E_H + E_C + E_V + E_L + E_W - E_S + E_M


# ============================================================================
# 5.6 建築物に係るエネルギーの使用の合理化の一層の促進その他の建築物の
#   低炭素化の促進のために誘導すべき基準（建築物の低炭素化誘導基準）における
#   誘導設計一次エネルギー消費量
# ============================================================================

def get_E_T_lcb_du(E_H, E_C, E_V, E_L, E_W, E_S_CG, E_M) -> float:
    """式(9) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の設計一次エネルギー消費量 (GJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S_CG (float): 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量 (MJ/年)
        E_M (float): 1年当たりのその他の設計一次エネルギー消費量 (MJ/年)

    Returns:
        float: 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
    """
    # 式(10) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の1年当たりの設計一次エネルギー消費量 (GJ/年)
    E_star_T_lcb_du = get_E_star_T_lcb_du(E_H, E_C, E_V, E_L, E_W, E_S_CG, E_M)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_T_lcb_du / 100) / 10


def get_E_star_T_lcb_du(E_H, E_C, E_V, E_L, E_W, E_S_CG, E_M):
    """式(10) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の設計一次エネルギー消費量 (GJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S_CG (float): 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量 (MJ/年)
        E_M (float): 1年当たりのその他の設計一次エネルギー消費量 (MJ/年)

    Returns:
        float: 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
    """
    return E_H + E_C + E_V + E_L + E_W - E_S_CG + E_M


# ============================================================================
# 5.7 建築物に係るエネルギーの使用の合理化の一層の促進その他の建築物の
#   低炭素化の促進のために誘導すべき基準（建築物の低炭素化誘導基準）の
#   低炭素化措置における設計一次エネルギー消費量
# ============================================================================

def get_E_T_enh_du(E_H, E_C, E_V, E_L, E_W, E_S_CG, E_R, E_M) -> float:
    """式(11) 建築物の低炭素化の促進のために誘導すべきその他の基準における単位住戸の設計一次エネルギー消費量 (GJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S_CG (float): 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量 (MJ/年)
        E_R (float): 1年当たりの再生可能エネルギー源の利用に資する設備で生成されるエネルギー量（誘導設計一次エネルギー消費量の算定で考慮されるものを除く） (MJ/年)
        E_M (float): 1年当たりのその他の設計一次エネルギー消費量 (MJ/年)

    Returns:
        float: 建築物の低炭素化の促進のために誘導すべきその他の基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
    """
    # 式(12) 建築物の低炭素化の促進のために誘導すべきその他の基準における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)
    E_star_T_enh_du = get_E_star_T_enh_du(E_H, E_C, E_V, E_L, E_W, E_S_CG, E_R, E_M)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_T_enh_du / 100) / 10


def get_E_star_T_enh_du(E_H, E_C, E_V, E_L, E_W, E_S_CG, E_R, E_M):
    """式(12) 建築物の低炭素化の促進のために誘導すべきその他の基準における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S_CG (float): 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量 (MJ/年)
        E_R (float): 1年当たりの再生可能エネルギー源の利用に資する設備で生成されるエネルギー量（誘導設計一次エネルギー消費量の算定で考慮されるものを除く） (MJ/年)
        E_M (float): 1年当たりのその他の設計一次エネルギー消費量 (MJ/年)

    Returns:
        float: 建築物の低炭素化の促進のために誘導すべきその他の基準における単位住戸の1年当たりの設計一次エネルギー消費量 (MJ/年)
    """
    return E_H + E_C + E_V + E_L + E_W - E_S_CG - E_R + E_M


# ============================================================================
# 6. 設計一次エネルギー消費量(その他の設計一次エネルギー消費量を除く)
# ============================================================================


def calc_E_dash_T_dict(E_H, E_C, E_V, E_L, E_W, E_S, E_S_CG, type) -> DesignedPrimaryEnergyTotalDash:
    E_dash_T_gn_du   = None
    E_dash_T_indc_du = None
    E_dash_T_lcb_du  = None
    E_dash_T_rb_du   = None
    E_dash_T_trad_du = None

    if type == '一般住宅':
        E_dash_T_gn_du = get_E_dash_T_gn_du(E_H, E_C, E_V, E_L, E_W, E_S)
        E_dash_T_indc_du = get_E_dash_T_indc_du(E_H, E_C, E_V, E_L, E_W, E_S_CG)
        E_dash_T_lcb_du = get_E_dash_T_lcb_du(E_H, E_C, E_V, E_L, E_W, E_S_CG)
    elif type == '事業主基準':
        E_dash_T_rb_du = get_E_dash_T_rb_du(E_H, E_C, E_V, E_L, E_W, E_S)
    elif type == '行政庁認定住宅':
        E_dash_T_trad_du = get_E_dash_T_trad_du(E_H, E_C, E_V, E_L, E_W, E_S)
    else:
        raise ValueError(type)

    return {
        'E_dash_T_gn_du': E_dash_T_gn_du,
        'E_dash_T_indc_du': E_dash_T_indc_du,
        'E_dash_T_lcb_du': E_dash_T_lcb_du,
        'E_dash_T_rb_du': E_dash_T_rb_du,
        'E_dash_T_trad_du': E_dash_T_trad_du,
    }


# ====================================================================
# 6.2 建築物エネルギー消費性能基準（気候風土適応住宅を除く）における
#   設計一次エネルギー消費量(その他の設計一次エネルギー消費量を除く)
# ====================================================================

def get_E_dash_T_gn_du(E_H, E_C, E_V, E_L, E_W, E_S) -> float:
    """式(13) 建築物エネルギー消費性能基準における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S (float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/年)

    Returns:
        float: 建築物エネルギー消費性能基準における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)
    """
    # 式(14) 建築物エネルギー消費性能基準における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (MJ/年)
    E_dash_star_T_gn_du = get_E_dash_star_T_gn_du(E_H, E_C, E_V, E_L, E_W, E_S)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_dash_star_T_gn_du / 100) / 10


def get_E_dash_star_T_gn_du(E_H, E_C, E_V, E_L, E_W, E_S):
    """式(14) 建築物エネルギー消費性能基準における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (MJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S (float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/年)

    Returns:
        float: 建築物エネルギー消費性能基準における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (MJ/年)
    """
    return E_H + E_C + E_V + E_L + E_W - E_S


# ============================================================================
# 6.3 建築物エネルギー消費性能基準（気候風土適応住宅）における
#   設計一次エネルギー消費量(その他の設計一次エネルギー消費量を除く)
# ============================================================================

def get_E_dash_T_trad_du(E_H, E_C, E_V, E_L, E_W, E_S) -> float:
    """式(15) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S (float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/年)

    Returns:
        float: 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)
    """
    # 式(16) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)
    E_dash_star_T_trad_du = get_E_dash_star_T_trad_du(E_H, E_C, E_V, E_L, E_W, E_S)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_dash_star_T_trad_du / 100) / 10


def get_E_dash_star_T_trad_du(E_H, E_C, E_V, E_L, E_W, E_S):
    """式(16) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S (float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/年)

    Returns:
        float: 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)
    """
    return E_H + E_C + E_V + E_L + E_W - E_S


# ============================================================================
# 6.4 建築物エネルギー消費性能誘導基準における誘導設計一次エネルギー消費量
#   (その他の設計一次エネルギー消費量を除く)
# ============================================================================

def get_E_dash_T_indc_du(E_H, E_C, E_V, E_L, E_W, E_S_CG) -> float:
    """式(17) 建築物エネルギー消費性能誘導基準における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S_CG (float): 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量 (MJ/年)

    Returns:
        float: 建築物エネルギー消費性能誘導基準における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)
    """
    # 式(18) 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (MJ/年)
    E_dash_star_T_indc_du = get_E_dash_star_T_indc_du(E_H, E_C, E_V, E_L, E_W, E_S_CG)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_dash_star_T_indc_du / 100) / 10


def get_E_dash_star_T_indc_du(E_H, E_C, E_V, E_L, E_W, E_S_CG):
    """式(18) 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S_CG (float): 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量 (MJ/年)

    Returns:
        float: 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)
    """
    return E_H + E_C + E_V + E_L + E_W - E_S_CG


# ============================================================================
# 6.5 特定建築主基準における設計一次エネルギー消費量
#   (その他の設計一次エネルギー消費量を除く)
# ============================================================================

def get_E_dash_T_rb_du(E_H, E_C, E_V, E_L, E_W, E_S) -> float:
    """式(19) 特定建築主基準における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S (float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/年)

    Returns:
        float: 特定建築主基準における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)
    """
    # 式(20) 
    E_dash_star_T_rb_du = get_E_dash_star_T_rb_du(E_H, E_C, E_V, E_L, E_W, E_S)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_dash_star_T_rb_du / 100) / 10


def get_E_dash_star_T_rb_du(E_H, E_C, E_V, E_L, E_W, E_S):
    """式(20) 特定建築主基準における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (MJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S (float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/年)

    Returns:
        float: 特定建築主基準における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (MJ/年)
    """
    return E_H + E_C + E_V + E_L + E_W - E_S


# ============================================================================
# 6.6 建築物に係るエネルギーの使用の合理化の一層の促進その他の建築物の
#   低炭素化の促進のために誘導すべき基準（建築物の低炭素化誘導基準）における
#   誘導設計一次エネルギー消費量(その他の設計一次エネルギー消費量を除く)
# ============================================================================

def get_E_dash_T_lcb_du(E_H, E_C, E_V, E_L, E_W, E_S_CG) -> float:
    """式(21) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S_CG (float): 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量 (MJ/年)

    Returns:
        float: 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)
    """
    # 式(23) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (MJ/年)
    E_dash_star_T_lcb_du = get_E_dash_star_T_lcb_du(E_H, E_C, E_V, E_L, E_W, E_S_CG)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_dash_star_T_lcb_du / 100) / 10


def get_E_dash_star_T_lcb_du(E_H, E_C, E_V, E_L, E_W, E_S_CG):
    """式(23) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (MJ/年)

    Args:
        E_H (float): 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_C (float): 1年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年)
        E_V (float): 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年)
        E_L (float): 1年当たりの照明設備の設計一次エネルギー消費量 (MJ/年)
        E_W (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の設計一次エネルギー消費量 (MJ/年)
        E_S_CG (float): 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量 (MJ/年)

    Returns:
        float: 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の1年当たりの設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (MJ/年)

    NOTE:
        ここから式番号が 1つ飛んでいる
    """
    return E_H + E_C + E_V + E_L + E_W - E_S_CG


# ============================================================================
# 7. 暖房設備の設計一次エネルギー消費量
# ============================================================================

def calc_E_H(region, sol_region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_H, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG, SHC,
            heating_flag_d, L_T_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i):
    """1 年当たりの暖房設備の設計一次エネルギー消費量（MJ/年） (24)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      A_env(float): 外皮の部位の面積の合計 (m2)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      mode_H(str): 暖房方式
      H_A(dict): 暖房方式
      spec_MR(dict): 暖房機器の仕様
      spec_OR(dict): 暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      SHC(dict): 集熱式太陽熱利用設備の仕様
      heating_flag_d(ndarray): 暖房日
      L_T_H_d_t_i(ndarray): 暖冷房区画iの 1 時間当たりの暖房負荷 (MJ/h)
      L_CS_d_t_i(ndarray): 暖冷房区画iの 1 時間当たりの冷房顕熱負荷 (MJ/h)
      L_CL_d_t_i(ndarray): 暖冷房区画iの 1 時間当たりの冷房潜熱負荷 (MJ/h)

    Returns:
      float: 1 年当たりの暖房設備の設計一次エネルギー消費量（MJ/年） (24)

    """
    if region == 8:
        return 0.0
    elif mode_H is not None:
        # 式(25) 日付dの時刻tにおける1時間当たりの暖房設備の設計一次エネルギー消費量 (MJ/h)
        E_H_d_t = get_E_H_d_t(region, sol_region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_H, H_A, spec_MR, spec_OR, spec_HS, mode_MR,
                              mode_OR, HW, CG, SHC, heating_flag_d, L_T_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i)

        # 式(24) 1年当たりの暖房設備の設計一次エネルギー消費量 (MJ/年)
        E_H = np.sum(E_H_d_t)

        return E_H
    else:
        return 0.0


# 1 時間当たりの暖房設備の設計一次エネルギー消費量
def get_E_H_d_t(region, sol_region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_H, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG, SHC,
                heating_flag_d, L_T_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i):
    """1 時間当たりの暖房設備の設計一次エネルギー消費量 (MJ/h) (25)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      A_env(float): 外皮の部位の面積の合計 (m2)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      mode_H(str): 暖房方式
      H_A(dict): 暖房方式
      spec_MR(dict): 暖房機器の仕様
      spec_OR(dict): 暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      SHC(dict): 集熱式太陽熱利用設備の仕様
      heating_flag_d(ndarray): 暖房日
      L_T_H_d_t_i(ndarray): 暖冷房区画iの 1 時間当たりの暖房負荷 (MJ/h)
      L_CS_d_t_i(ndarray): 暖冷房区画iの 1 時間当たりの冷房顕熱負荷 (MJ/h)
      L_CL_d_t_i(ndarray): 暖冷房区画iの 1 時間当たりの冷房潜熱負荷 (MJ/h)

    Returns:
      ndarray: 1 時間当たりの暖房設備の設計一次エネルギー消費量 (MJ/h) (25)

    """
    if region == 8:
        return 0.0
    else:
        # (第二章第一節付録B) 電気の量 1kWh を熱量に換算する係数 (kJ/kWh)
        f_prim = get_f_prim()

        # (第四章第一節) 暖房設備の消費電力量（kWh/h）
        E_E_H_d_t = get_E_E_H_d_t(region, sol_region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, H_A, spec_MR, spec_OR, spec_HS,
                                  mode_MR, mode_OR, HW, CG, SHC, heating_flag_d, L_T_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i)

        # (第四章第一節) 暖房設備のガス消費量（MJ/h）
        E_G_H_d_t = get_E_G_H_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG,
                                  L_T_H_d_t_i)

        # (第四章第一節) 暖房設備の灯油消費量（MJ/h）
        E_K_H_d_t = calc_E_K_H_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG,
                                   L_T_H_d_t_i)

        # (第四章第一節) 暖房設備のその他の燃料による一次エネルギー消費量（MJ/h）
        E_M_H_d_t = calc_E_M_H_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, L_T_H_d_t_i)

        # (第四章第一節) 暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/h）
        E_UT_H_d_t = calc_E_UT_H_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_H, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR,
                                     HW, CG, L_T_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i)

        # 式(25) 1時間当たりの暖房設備の設計一次エネルギー消費量 （MJ/h）
        return E_E_H_d_t * f_prim / 1000 + E_G_H_d_t + E_K_H_d_t + E_M_H_d_t + E_UT_H_d_t


# ============================================================================
# 8. 冷房設備の設計一次エネルギー消費量
# ============================================================================

def calc_E_C(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_H_d_t, L_CS_d_t, L_CL_d_t, mode_C):
    """1 年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年) (26)

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      A_env(float): 外皮の部位の面積の合計 (m2)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      C_A(dict): 冷房方式
      C_MR(dict): 主たる居室の冷房機器
      C_OR(dict): その他の居室の冷房機器
      L_H_d_t(ndarray): 暖冷房区画iの 1 時間当たりの暖房負荷 (MJ/h)
      L_CS_d_t(ndarray): 暖冷房区画iの 1 時間当たりの冷房顕熱負荷 (MJ/h)
      L_CL_d_t(ndarray): 暖冷房区画iの 1 時間当たりの冷房潜熱負荷 (MJ/h)
      mode_C(str): 冷房方式

    Returns:
      float: 1 年当たりの冷房設備の設計一次エネルギー消費量 (MJ/年) (26)

    """
    # 1 時間当たりの冷房設備の設計一次エネルギー消費量 (27)
    E_C_d_t = get_E_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_H_d_t, L_CS_d_t, L_CL_d_t, mode_C)

    # 1 年当たりの冷房設備の設計一次エネルギー消費量 (26)
    E_C = np.sum(E_C_d_t)

    return E_C


def get_E_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_H_d_t, L_CS_d_t, L_CL_d_t, mode_C):
    """1 時間当たりの冷房設備の設計一次エネルギー消費量 (MJ/h) (27)

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      A_env(float): 外皮の部位の面積の合計 (m2)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      C_A(dict): 冷房方式
      C_MR(dict): 主たる居室の冷房機器
      C_OR(dict): その他の居室の冷房機器
      L_H_d_t(ndarray): 暖冷房区画iの 1 時間当たりの暖房負荷 (MJ/h)
      L_CS_d_t(ndarray): 暖冷房区画iの 1 時間当たりの冷房顕熱負荷 (MJ/h)
      L_CL_d_t(ndarray): 暖冷房区画iの 1 時間当たりの冷房潜熱負荷 (MJ/h)
      mode_C(str): 冷房方式

    Returns:
      ndarray: 1 時間当たりの冷房設備の設計一次エネルギー消費量 (MJ/h) (27)

    """
    # 電気の量 1kWh を熱量に換算する係数 (第二章第一節付録B)
    f_prim = get_f_prim()

    # 第四章「暖冷房設備」第一節「全般」
    E_E_C_d_t = calc_E_E_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_H_d_t, L_CS_d_t, L_CL_d_t)
    E_G_C_d_t = calc_E_G_C_d_t()
    E_K_C_d_t = calc_E_K_C_d_t()
    E_M_C_d_t = calc_E_M_C_d_t()
    E_UT_C_d_t = calc_E_UT_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_H_d_t, L_CS_d_t, L_CL_d_t, mode_C)

    E_C_d_t = E_E_C_d_t * f_prim / 1000 + E_G_C_d_t + E_K_C_d_t + E_M_C_d_t + E_UT_C_d_t  # (27)

    return E_C_d_t


# ============================================================================
# 9. 機械換気設備の設計一次エネルギー消費量
# ============================================================================

def calc_E_V(A_A, V, HEX):
    """1 年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年) (28)

    Args:
      A_A(float): 床面積の合計[m^2]
      V(dict): 換気設備仕様辞書
      HEX(dict): 熱交換器型設備仕様辞書

    Returns:
      float: 1 年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年) (28)

    """
    
    if V is None:
        return 0.0

    # 電気の量 1kWh を熱量に換算する係数 (kJ/kWh) (第二章第一節付録B)
    f_prim = get_f_prim()

    # 仮想居住人数 (第二章第一節付録C)
    n_p = get_n_p(A_A)

    # 日付dの時刻tにおける1時間当たりの機械換気設備の消費電力量 (kWh/h) (第五章「換気設備」)
    E_E_V_d_t = calc_E_E_V_d_t(n_p, A_A, V, HEX)

    # 1年当たりの機械換気設備の設計一次エネルギー消費量 (MJ/年) (28)
    E_V = np.sum(E_E_V_d_t) * f_prim / 1000

    return E_V


# ============================================================================
# 10. 照明設備の設計一次エネルギー消費量
# ============================================================================

# 1 年当たりの照明設備の設計一次エネルギー消費量
def calc_E_L(A_A, A_MR, A_OR, L):
    """1 年当たりの照明設備の設計一次エネルギー消費量 (MJ/年) (29)

    Args:
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      L(dict): 照明設備仕様辞書

    Returns:
      ndarray: 1 年当たりの照明設備の設計一次エネルギー消費量 (MJ/年) (29)

    """
    
    if L is None:
        return 0.0

    # 電気の量 1kWh を熱量に換算する係数 (kJ/kWh) (第二章第一節付録B)
    f_prim = get_f_prim()

    # 仮想居住人数 (第二章第一節付録C)
    n_p = get_n_p(A_A)

    # 日付dの時刻tにおける1時間当たりの照明設備の消費電力量（kWh/h） (第六章「照明設備」)
    E_E_L_d_t = calc_E_E_L_d_t(n_p, A_A, A_MR, A_OR, L)

    # 1 年当たりの照明設備の設計一次エネルギー消費量 (MJ/年) (29)
    E_L = np.sum(E_E_L_d_t) * f_prim / 1000

    return E_L


# ============================================================================
# 11. 給湯設備及びコージェネレーション設備の設計一次エネルギー消費量
# ============================================================================

# 1 年当たりの給湯設備（コージェネレーション設備を含む）の設計一次エネルギー消費量
def calc_E_W(A_A, region, sol_region, HW, SHC, CG, H_A=None, H_MR=None, H_OR=None, H_HS=None, C_A=None, C_MR=None,
            C_OR=None,
            V=None, L=None, A_MR=None, A_OR=None, A_env=None, Q=None, mu_H=None, mu_C=None, NV_MR=None, NV_OR=None, TS=None,
            r_A_ufvnt=None, HEX=None, underfloor_insulation=None, mode_H=None, mode_C=None):
    """1 年当たりの給湯設備（コージェネレーション設備を含む）の設計一次エネルギー消費量 (MJ/年) (30)

    Args:
      A_A(float): 床面積の合計 (m2)
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      HW(dict): 給湯機の仕様
      SHC(dict): 集熱式太陽熱利用設備の仕様
      CG(dict): コージェネレーションの機器
      H_A(dict, optional, optional): 暖房方式, defaults to None
      H_MR(dict, optional, optional): 暖房機器の仕様, defaults to None
      H_OR(dict, optional, optional): 暖房機器の仕様, defaults to None
      H_HS(dict, optional, optional): 温水暖房機の仕様, defaults to None
      C_A(dict, optional, optional): 冷房方式, defaults to None
      C_MR(dict, optional, optional): 主たる居室の冷房機器, defaults to None
      C_OR(dict, optional, optional): その他の居室の冷房機器, defaults to None
      V(dict, optional, optional): 換気設備仕様辞書, defaults to None
      L(dict, optional, optional): 照明設備仕様辞書, defaults to None
      A_MR(float, optional, optional): 主たる居室の床面積 (m2), defaults to None
      A_OR(float, optional, optional): その他の居室の床面積 (m2), defaults to None
      Q(float, optional, optional): 当該住戸の熱損失係数 (W/m2K), defaults to None
      mu_H(float, optional, optional): 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数, defaults to None
      mu_C(float, optional, optional): 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数, defaults to None
      NV_MR(float, optional, optional): 主たる居室における通風の利用における相当換気回数, defaults to None
      NV_OR(float, optional, optional): その他の居室における通風の利用における相当換気回数, defaults to None
      TS(bool, optional, optional): 蓄熱, defaults to None
      r_A_ufvnt(float, optional, optional): 床下換気, defaults to None
      HEX(dict, optional, optional): 熱交換器型設備仕様辞書, defaults to None
      underfloor_insulation(bool, optional, optional): 床下空間が断熱空間内である場合はTrue, defaults to None
      mode_H(str, optional, optional): 暖房方式, defaults to None
      mode_C(str, optional, optional): 冷房方式, defaults to None
      A_env: Default value = None)

    Returns:
      tuple: 1 年当たりの給湯設備（コージェネレーション設備を含む）の設計一次エネルギー消費量 (MJ/年)

    """
    
    if HW is None:
        return 0.0, np.zeros(24 * 365), np.zeros(24 * 365), np.zeros(24 * 365), np.zeros(24 * 365), \
               np.zeros(24 * 365), np.zeros(24 * 365), np.zeros(24 * 365)

    if HW['hw_type'] != 'コージェネレーションを使用する':
        E_W_d = calc_E_W_d(A_A, region, sol_region, HW, SHC, H_HS, H_MR, H_OR, A_MR, A_OR, Q, mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX,
                          underfloor_insulation)

        # (30a)
        E_W = np.sum(E_W_d)

        return E_W, np.zeros(24 * 365), np.zeros(24 * 365), np.zeros(24 * 365), np.zeros(24 * 365), \
               np.zeros(24 * 365), np.zeros(24 * 365), np.zeros(24 * 365)
    else:
        # 1日当たりのコージェネレーション設備の一次エネルギー消費量
        E_G_CG_d_t, E_E_CG_gen_d_t, E_E_CG_h_d_t, E_E_TU_aux_d_t, E_E_CG_h_d_t, E_G_CG_ded, e_BB_ave, Q_CG_h = \
            calc_E_CG_d_t(A_A, region, sol_region, HW, SHC, CG, H_A, H_MR, H_OR, H_HS, C_A, C_MR, C_OR,
                          V, L, A_MR, A_OR, A_env, Q, mu_H, mu_C, NV_MR, NV_OR, TS,
                                             r_A_ufvnt, HEX, underfloor_insulation, mode_H, mode_C)

        # (30b)
        E_CG = np.sum(E_G_CG_d_t)

        return E_CG, E_E_CG_gen_d_t, E_E_CG_h_d_t, E_E_TU_aux_d_t, E_E_CG_h_d_t, E_G_CG_ded, e_BB_ave, Q_CG_h


# 1日当たりのコージェネレーション設備の一次エネルギー消費量
def calc_E_CG_d_t(A_A, region, sol_region, HW, SHC, CG, H_A=None, H_MR=None, H_OR=None, H_HS=None, C_A=None, C_MR=None,
                C_OR=None,
                V=None, L=None, A_MR=None, A_OR=None, A_env=None, Q=None, mu_H=None, mu_C=None, NV_MR=None, NV_OR=None, TS=None,
                r_A_ufvnt=None, HEX=None, underfloor_insulation=None, mode_H=None, mode_C=None):
    """1時間当たりのコージェネレーション設備の一次エネルギー消費量

    Args:
      A_A(float): 床面積の合計 (m2)
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      HW(dict): 給湯機の仕様
      SHC(dict): 集熱式太陽熱利用設備の仕様
      CG(dict): コージェネレーションの機器
      H_A(dict, optional, optional): 暖房方式, defaults to None
      H_MR(dict, optional, optional): 暖房機器の仕様, defaults to None
      H_OR(dict, optional, optional): 暖房機器の仕様, defaults to None
      H_HS(dict, optional, optional): 温水暖房機の仕様, defaults to None
      C_A(dict, optional, optional): 冷房方式, defaults to None
      C_MR(dict, optional, optional): 主たる居室の冷房機器, defaults to None
      C_OR(dict, optional, optional): その他の居室の冷房機器, defaults to None
      V(dict, optional, optional): 換気設備仕様辞書, defaults to None
      L(dict, optional, optional): 照明設備仕様辞書, defaults to None
      A_MR(float, optional, optional): 主たる居室の床面積 (m2), defaults to None
      A_OR(float, optional, optional): その他の居室の床面積 (m2), defaults to None
      Q(float, optional, optional): 当該住戸の熱損失係数 (W/m2K), defaults to None
      mu_H(float, optional, optional): 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数, defaults to None
      mu_C(float, optional, optional): 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数, defaults to None
      NV_MR(float, optional, optional): 主たる居室における通風の利用における相当換気回数, defaults to None
      NV_OR(float, optional, optional): その他の居室における通風の利用における相当換気回数, defaults to None
      TS(bool, optional, optional): 蓄熱, defaults to None
      r_A_ufvnt(float, optional, optional): 床下換気, defaults to None
      HEX(dict, optional, optional): 熱交換器型設備仕様辞書, defaults to None
      underfloor_insulation(bool, optional, optional): 床下空間が断熱空間内である場合はTrue, defaults to None
      mode_H(str, optional, optional): 暖房方式, defaults to None
      mode_C(str, optional, optional): 冷房方式, defaults to None
      A_env: Default value = None)

    Returns:
      tuple: 1時間当たりのコージェネレーション設備の一次エネルギー消費量

    Raises:
      ValueError: SHC の type が "液体集熱式"、 "空気集熱式"　以外の場合に発生する

    """
    
    if HW is None or HW['hw_type'] != 'コージェネレーションを使用する':
        return np.zeros(365), np.zeros(24 * 365), None, None, None, None, None, None

    n_p = get_n_p(A_A)

    # 実質的な暖房機器の仕様を取得
    spec_MR, spec_OR = get_virtual_heating_devices(region, H_MR, H_OR)

    # 実質的な温水暖房機の仕様を取得
    spec_HS = get_virtual_heatsource(region, H_HS)

    # 暖房方式及び運転方法の区分
    mode_MR, mode_OR = calc_heating_mode(region=region, H_MR=spec_MR, H_OR=spec_OR)

    # 暖房負荷の取得
    L_T_H_d_t_i, L_dash_H_R_d_t_i = calc_heating_load(
        region, sol_region,
        A_A, A_MR, A_OR,
        Q, mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX,
        underfloor_insulation, mode_H, mode_C,
        spec_MR, spec_OR, mode_MR, mode_OR, SHC)

    # 暖房日の計算
    if SHC is not None and SHC['type'] == '空気集熱式':
        # import section4_1 as H
        # L_T_H_d_t_i, L_dash_H_R_d_t_i = H.calc_L_H_d_t(region, sol_region, A_A, A_MR, A_OR, None, spec_MR, spec_OR,
        #                                               mode_MR, mode_OR, Q, mu_H, TS, r_A_ufvnt, HEX, SHC,
        #                                               underfloor_insulation)
        #
        from pyhees.section3_1_heatingday import get_heating_flag_d

        heating_flag_d = get_heating_flag_d(L_dash_H_R_d_t_i)
    else:
        heating_flag_d = None

    # 冷房負荷の計算
    L_CS_d_t, L_CL_d_t = \
        calc_cooling_load(region, A_A, A_MR, A_OR, Q, mu_H, mu_C,
                          NV_MR, NV_OR, r_A_ufvnt, underfloor_insulation,
                          mode_C, mode_H, mode_MR, mode_OR, TS, HEX)
        
    # 暖房
    E_E_H_d_t = get_E_E_H_d_t(region, sol_region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR,
                              HW, CG, SHC, heating_flag_d, L_T_H_d_t_i, L_CS_d_t, L_CL_d_t)

    # 冷房
    E_E_C_d_t = calc_E_E_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR,
                               L_T_H_d_t_i, L_CS_d_t, L_CL_d_t)

    # 換気
    E_E_V_d_t = calc_E_E_V_d_t(n_p, A_A, V)

    # 照明
    E_E_L_d_t = calc_E_E_L_d_t(n_p, A_A, A_MR, A_OR, L)

    # 家電
    E_E_AP_d_t = calc_E_E_AP_d_t(n_p)

    # 1 時間当たりの調理の消費電力量
    E_E_CC_d_t = get_E_E_CC_d_t()

    # その他または設置しない場合
    spec_HW = get_virtual_hotwater(region, HW)

    if spec_HW['hw_type'] is not None:
        from pyhees.section7_1 import get_normalized_bath_function
        # ふろ機能の修正
        bath_function = get_normalized_bath_function(spec_HW['hw_type'], spec_HW['bath_function'])

        # 給湯負荷の生成
        args = {
            'n_p': n_p,
            'region': region,
            'sol_region': sol_region,
            'has_bath': spec_HW['has_bath'],
            'bath_function': bath_function,
            'pipe_diameter': spec_HW['pipe_diameter'],
            'kitchen_watersaving_A': spec_HW['kitchen_watersaving_A'],
            'kitchen_watersaving_C': spec_HW['kitchen_watersaving_C'],
            'shower_watersaving_A': spec_HW['shower_watersaving_A'],
            'shower_watersaving_B': spec_HW['shower_watersaving_B'],
            'washbowl_watersaving_C': spec_HW['washbowl_watersaving_C'],
            'bath_insulation': spec_HW['bath_insulation']
        }
        if SHC is not None:
            if SHC['type'] == '液体集熱式':
                args.update({
                    'type': SHC['type'],
                    'ls_type': SHC['ls_type'],
                    'A_sp': SHC['A_sp'],
                    'P_alpha_sp': SHC['P_alpha_sp'],
                    'P_beta_sp': SHC['P_beta_sp'],
                    'W_tnk_ss': SHC['W_tnk_ss']
                })
            elif SHC['type'] == '空気集熱式':
                args.update({
                    'type': SHC['type'],
                    'hotwater_use': SHC['hotwater_use'],
                    'heating_flag_d': heating_flag_d,
                    'A_col': SHC['A_col'],
                    'P_alpha': SHC['P_alpha'],
                    'P_beta': SHC['P_beta'],
                    'V_fan_P0': SHC['V_fan_P0'],
                    'd0': SHC['d0'],
                    'd1': SHC['d1'],
                    'W_tnk_ass': SHC['W_tnk_ass']
                })
            else:
                raise ValueError(SHC['type'])

        hotwater_load = calc_hotwater_load(**args)

        L_dashdash_k_d_t = hotwater_load['L_dashdash_k_d_t']
        L_dashdash_s_d_t = hotwater_load['L_dashdash_s_d_t']
        L_dashdash_w_d_t = hotwater_load['L_dashdash_w_d_t']
        L_dashdash_b1_d_t = hotwater_load['L_dashdash_b1_d_t']
        L_dashdash_b2_d_t = hotwater_load['L_dashdash_b2_d_t']
        L_dashdash_ba1_d_t = hotwater_load['L_dashdash_ba1_d_t']
        L_dashdash_ba2_d_t = hotwater_load['L_dashdash_ba2_d_t']

    # 温水暖房負荷の計算
    if H_HS is not None:
        import pyhees.section4_1 as H
        from pyhees.section4_7 import calc_L_HWH

        # 実質的な暖房機器の仕様を取得
        spec_MR, spec_OR = H.get_virtual_heating_devices(region, H_MR, H_OR)

        # 暖房方式及び運転方法の区分
        mode_MR, mode_OR = H.calc_heating_mode(region=region, H_MR=spec_MR, H_OR=spec_OR)
        spec_HS = H.get_virtual_heatsource(region, H_HS)

        L_T_H_d_t_i, _ = H.calc_L_H_d_t(region, sol_region, A_A, A_MR, A_OR, None, None, spec_MR, spec_OR, mode_MR,
                                        mode_OR, Q, mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX, SHC, underfloor_insulation)
    else:
        spec_MR, spec_OR, spec_HS = None, None, None
        mode_MR, mode_OR = None, None
        L_T_H_d_t_i = None

    # 1時間当たりの給湯設備の消費電力量 (s7-1 1)
    E_E_W_d_t = calc_E_E_W_d_t(n_p, L_T_H_d_t_i, heating_flag_d, region, sol_region, HW, SHC)

    # 1時間当たりの電力需要 (60)
    E_E_dmd_d_t = get_E_E_dmd_d_t(E_E_H_d_t, E_E_C_d_t, E_E_V_d_t, E_E_L_d_t, E_E_W_d_t, E_E_AP_d_t, E_E_CC_d_t)

    # 電力需要の結果
    print('## 電力需要')
    print('E_E_H  = {} [kWh/年]'.format(np.sum(E_E_H_d_t)))
    print('E_E_C  = {} [kWh/年]'.format(np.sum(E_E_C_d_t)))
    print('E_E_V  = {} [kWh/年]'.format(np.sum(E_E_V_d_t)))
    print('E_E_L  = {} [kWh/年]'.format(np.sum(E_E_L_d_t)))
    print('E_E_W  = {} [kWh/年]'.format(np.sum(E_E_W_d_t)))
    print('E_E_AP = {} [kWh/年]'.format(np.sum(E_E_AP_d_t)))
    print('Total  = {} [kWh/年]'.format(np.sum(E_E_H_d_t + E_E_C_d_t + E_E_V_d_t + E_E_L_d_t + E_E_AP_d_t)))

    # 1日当たりのコージェネレーション設備の一次エネルギー消費量
    E_G_CG_d_t, E_E_CG_gen_d_t, E_G_CG_ded, E_E_CG_self, Q_CG_h, E_E_TU_aux_d_t, e_BB_ave = \
        calc_E_G_CG_d_t(bath_function, CG, E_E_dmd_d_t,
                        L_dashdash_k_d_t, L_dashdash_w_d_t, L_dashdash_s_d_t, L_dashdash_b1_d_t,
                        L_dashdash_b2_d_t,
                        L_dashdash_ba1_d_t, L_dashdash_ba2_d_t,
                        spec_HS, spec_MR, spec_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR,
                        L_T_H_d_t_i)

    # 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h) (44)
    E_E_CG_h_d_t = get_E_E_CG_h_d_t(E_E_CG_gen_d_t, E_E_dmd_d_t, True)

    return E_G_CG_d_t, E_E_CG_gen_d_t, E_E_CG_h_d_t, E_E_TU_aux_d_t, E_E_CG_h_d_t, E_G_CG_ded, e_BB_ave, Q_CG_h

# ============================================================================
# 11.1 給湯設備の設計一次エネルギー消費量
# ============================================================================

def calc_E_W_d(A_A, region, sol_region, HW, SHC, H_HS=None, H_MR=None, H_OR=None, A_MR=None, A_OR=None, Q=None, mu_H=None, mu_C=None, NV_MR=None, NV_OR=None, TS=None, r_A_ufvnt=None, HEX=None, underfloor_insulation=None):
    """1 日当たりの給湯設備の設計一次エネルギー消費量 (MJ/h) (31)

    Args:
      A_A(float): 床面積の合計 (m2)
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      HW(dict): 給湯機の仕様
      SHC(dict): 集熱式太陽熱利用設備の仕様
      H_HS(dict, optional, optional): 温水暖房機の仕様, defaults to None
      H_MR(dict, optional, optional): 暖房機器の仕様, defaults to None
      H_OR(dict, optional, optional): 暖房機器の仕様, defaults to None
      A_MR(float, optional, optional): 主たる居室の床面積 (m2), defaults to None
      A_OR(float, optional, optional): その他の居室の床面積 (m2), defaults to None
      Q(float, optional, optional): 当該住戸の熱損失係数 (W/m2K), defaults to None
      mu_H(float, optional, optional): 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数, defaults to None
      mu_C(float, optional, optional): 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数, defaults to None
      NV_MR(float, optional, optional): 主たる居室における通風の利用における相当換気回数, defaults to None
      NV_OR(float, optional, optional): その他の居室における通風の利用における相当換気回数, defaults to None
      TS(bool, optional, optional): 蓄熱, defaults to None
      r_A_ufvnt(float, optional, optional): 床下換気, defaults to None
      HEX(dict, optional, optional): 熱交換器型設備仕様辞書, defaults to None
      underfloor_insulation(bool, optional, optional): 床下空間が断熱空間内である場合はTrue, defaults to None

    Returns:
      ndarray: 1 日当たりの給湯設備の設計一次エネルギー消費量 (MJ/h)

    Raises:
      ValueError: コージェネは対象外。HW の hw_type が 'コージェネレーションを使用する' であった場合発生する。

    """
    
    # コージェネは対象外
    if HW['hw_type'] == 'コージェネレーションを使用する':
        raise ValueError(HW['hw_type'])

    # 電気の量 1kWh を熱量に換算する係数
    f_prim = get_f_prim()

    # 想定人数
    n_p = get_n_p(A_A)

    # その他または設置しない場合
    spec_HW = get_virtual_hotwater(region, HW)

    # 温水暖房負荷の計算
    L_HWH = calc_L_HWH(A_A, A_MR, A_OR, HEX, H_HS, H_MR, H_OR, Q, SHC, TS, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt, region, sol_region,
                       underfloor_insulation)

    # 暖房日の計算
    heating_flag_d = calc_heating_flag_d(A_A, A_MR, A_OR, HEX, H_MR, H_OR, Q, SHC, TS, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt, region,
                                         sol_region, underfloor_insulation)

    E_E_W_d = calc_E_E_W_d_t(n_p, L_HWH, heating_flag_d, region, sol_region, spec_HW, SHC)
    E_G_W_d = calc_E_G_W_d_t(n_p, L_HWH, heating_flag_d, A_A, region, sol_region, spec_HW, SHC)
    E_K_W_d = calc_E_K_W_d_t(n_p, L_HWH, heating_flag_d, A_A, region, sol_region, spec_HW, SHC)
    E_M_W_d = get_E_M_W_d_t()

    print('E_E_W = {} [MJ]'.format(np.sum(E_E_W_d)))
    print('E_G_W = {} [MJ]'.format(np.sum(E_G_W_d)))
    print('E_K_W = {} [MJ]'.format(np.sum(E_K_W_d)))
    print('E_M_W = {} [MJ]'.format(np.sum(E_M_W_d)))

    E_W_d = E_E_W_d * f_prim / 1000 + E_G_W_d + E_K_W_d + E_M_W_d  # (31)

    return E_W_d


def calc_L_HWH(A_A, A_MR, A_OR, HEX, H_HS, H_MR, H_OR, Q, SHC, TS, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt, region, sol_region, underfloor_insulation, HW=None, CG=None):
    """温水暖房負荷の計算

    Args:
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      HEX(dict): 熱交換器型設備仕様辞書
      H_HS(dict, optional): 温水暖房機の仕様
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      SHC(dict): 集熱式太陽熱利用設備の仕様
      TS(bool): 蓄熱
      mu_H(float): 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数
      mu_C(float): 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数
      NV_MR(float): 主たる居室における通風の利用における相当換気回数
      NV_OR(float): その他の居室における通風の利用における相当換気回数
      r_A_ufvnt(float): 床下換気
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      underfloor_insulation(bool): 床下空間が断熱空間内である場合はTrue
      HW(dict, optional): 給湯機の仕様 (Default value = None)
      CG(dict, optional, optional): コージェネレーションの機器, defaults to None

    Returns:
      float: 温水暖房負荷

    """
    
    if H_HS is not None:
        import pyhees.section4_1 as H
        from pyhees.section4_7 import calc_L_HWH
        # 実質的な暖房機器の仕様を取得
        spec_MR, spec_OR = H.get_virtual_heating_devices(region, H_MR, H_OR)

        # 暖房方式及び運転方法の区分
        mode_MR, mode_OR = H.calc_heating_mode(region=region, H_MR=spec_MR, H_OR=spec_OR)
        spec_HS = H.get_virtual_heatsource(region, H_HS)

        L_T_H_d_t_i, _ = H.calc_L_H_d_t(region, sol_region, A_A, A_MR, A_OR, None, None, spec_MR, spec_OR, mode_MR, mode_OR, Q,
                                        mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX, SHC, underfloor_insulation)

        L_HWH = calc_L_HWH(spec_HS, spec_MR, spec_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_d_t_i, HW, CG)
        L_HWH = np.sum(L_HWH.reshape(365, 24), axis=1)
    else:
        L_HWH = np.zeros(365)
    return L_HWH


def calc_heating_flag_d(A_A, A_MR, A_OR, HEX, H_MR, H_OR, Q, SHC, TS, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt, region, sol_region,underfloor_insulation):
    """暖房日の計算

    Args:
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      HEX(dict): 熱交換器型設備仕様辞書
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      SHC(dict): 集熱式太陽熱利用設備の仕様
      TS(bool): 蓄熱
      mu_H(float): 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数
      mu_C(float): 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数
      NV_MR(float): 主たる居室における通風の利用における相当換気回数
      NV_OR(float): その他の居室における通風の利用における相当換気回数
      r_A_ufvnt(float): 床下換気
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      underfloor_insulation(bool): 床下空間が断熱空間内である場合はTrue

    Returns:
      ndarray: 暖房日

    """
    
    # 暖房日の計算
    if SHC is not None and SHC['type'] == '空気集熱式':
        import pyhees.section4_1 as H
        # 実質的な暖房機器の仕様を取得
        spec_MR, spec_OR = H.get_virtual_heating_devices(region, H_MR, H_OR)
        # 暖房方式及び運転方法の区分
        mode_MR, mode_OR = H.calc_heating_mode(region=region, H_MR=spec_MR, H_OR=spec_OR)

        L_T_H_d_t_i, L_dash_H_R_d_t_i = H.calc_L_H_d_t(region, sol_region, A_A, A_MR, A_OR, None, None, spec_MR, spec_OR, mode_MR, mode_OR, Q, mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX, SHC, underfloor_insulation)

        from pyhees.section3_1_heatingday import get_heating_flag_d
        heating_flag_d = get_heating_flag_d(L_dash_H_R_d_t_i)
    else:
        heating_flag_d = None
    return heating_flag_d


# ============================================================================
# 12. その他の設計一次エネルギー消費量
# ============================================================================

def calc_E_M(A_A):
    """1年当たりのその他の設計一次エネルギー消費量（MJ/h） (33)

    Args:
      A_A(float): 床面積の合計 (m2)

    Returns:
      float: 1年当たりのその他の設計一次エネルギー消費量（MJ/h） (33)

    """
    
    # 想定人数
    n_p = get_n_p(A_A)

    # 1 時間当たりの家電の設計一次エネルギー消費量（MJ/h） (34)
    E_AP_d_t = calc_E_AP_d_t(n_p)

    # 1 時間当たりの調理の設計一次エネルギー消費量（MJ/h） (35)
    E_CC_d_t = calc_E_CC_d_t(n_p)

    # 1年当たりのその他の設計一次エネルギー消費量 (MJ/年) (33)
    E_M = np.sum(E_AP_d_t + E_CC_d_t)

    return E_M


# ============================================================================
# 12.1 家電の設計一次エネルギー消費量
# ============================================================================

def calc_E_AP_d_t(n_p):
    """1 時間当たりの家電の設計一次エネルギー消費量（MJ/h） (34)

    Args:
      n_p(float): 想定人数

    Returns:
      ndarray: 1 時間当たりの家電の設計一次エネルギー消費量（MJ/h） (34)

    """
    
    # 電気の量 1kWh を熱量に換算する係数
    f_prim = get_f_prim()
    return calc_E_E_AP_d_t(n_p) * f_prim / 1000 + get_E_G_AP_d_t() + get_E_K_AP_d_t() + get_E_M_AP_d_t()  # (34)


# ============================================================================
# 12.2 調理の設計一次エネルギー消費量
# ============================================================================

def calc_E_CC_d_t(n_p):
    """1 時間当たりの調理の設計一次エネルギー消費量（MJ/h） (35)

    Args:
      n_p(float): 想定人数

    Returns:
      ndarray: 1 時間当たりの調理の設計一次エネルギー消費量

    """
    
    # 電気の量 1kWh を熱量に換算する係数
    f_prim = get_f_prim()

    return get_E_E_CC_d_t() * f_prim / 1000 + calc_E_G_CC_d_t(n_p) + get_E_K_CC_d_t() + get_E_M_CC_d_t()  # (35)


# ============================================================================
# 13. エネルギー利用効率化設備による設計一次エネルギー消費量の削減量
# ============================================================================

def calc_E_S(region, sol_region, PV, CG, E_E_dmd_d_t, E_E_CG_gen_d_t, E_E_TU_aux_d_t, E_E_CG_h, E_G_CG_ded, e_BB_ave, Q_CG_h):
    """1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      PV(dict): 太陽光発電設備
      CG(dict): コージェネレーションの機器
      E_E_dmd_d_t(ndarray): 1時間当たりの太陽光発電設備による発電量 (kWh/h)
      E_E_CG_gen_d_t(ndarray): 1時間当たりのコージェネレーション設備による発電のうちの自家消費分 (kWh/h)
      E_E_TU_aux_d_t(ndarray): 1時間当たりのタンクユニットの補機消費電力量 (25)
      E_E_CG_h(float): 1年当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/yr) (18)
      E_G_CG_ded(float): 1年当たりのコージェネレーション設備のガス消費量のうちの売電に係る控除対象分 (MJ/yr)
      e_BB_ave(float): コージェネレーション設備の給湯時のバックアップボイラーの年間平均効率 (-)
      Q_CG_h(float): 1年当たりのコージェネレーション設備による製造熱量のうちの自家消費算入分 (MJ/yr)

    Returns:
      E_S(float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/yr)
      E_S_CG(float): 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量 (MJ/yr)
      E_R(float): 1年当たりの再生可能エネルギー源の利用に資する設備で生成されるエネルギー量（誘導設計一次エネルギー消費量の算定で考慮されるものを除く）（MJ/yr）

    """

    if CG is not None:
        has_CG = True
        has_CG_reverse = CG["reverse"] if 'reverse' in CG else False
    else:
        has_CG = False
        has_CG_reverse = False

    if PV is not None:
        has_PV = True
        from pyhees.section11_2 import load_solrad
        from pyhees.section9_1 import calc_E_E_PV_d_t
        solrad = load_solrad(region, sol_region)
        # 太陽光発電設備の発電量 (s9-1 1)
        E_E_PV_d_t = calc_E_E_PV_d_t(PV, solrad)
    else:
        has_PV = False
        E_E_PV_d_t = np.zeros(24 * 365)

    # 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h) (44)
    E_E_CG_h_d_t = get_E_E_CG_h_d_t(E_E_CG_gen_d_t, E_E_dmd_d_t, has_CG)

    # 1 時間当たりの太陽光発電設備による消費電力削減量 (42)
    E_E_PV_h_d_t = get_E_E_PV_h_d_t(E_E_PV_d_t, E_E_dmd_d_t, E_E_CG_h_d_t, has_PV)

    # 1時間当たりのコージェネレーション設備による売電量(二次エネルギー) (kWh/h) (52)
    E_E_CG_sell_d_t = get_E_E_CG_sell_d_t(E_E_CG_gen_d_t, E_E_CG_h_d_t, has_CG_reverse)

    # 1年当たりのコージェネレーション設備による売電量（一次エネルギー換算値）(MJ/yr) (51)
    E_CG_sell = calc_E_CG_sell(E_E_CG_sell_d_t)

    # 1時間当たりの太陽光発電設備による売電量(二次エネルギー) (kWh/h) (49)
    E_E_PV_sell_d_t = get_E_E_PV_sell_d_t(E_E_PV_d_t, E_E_PV_h_d_t)

    # 1年当たりの太陽光発電設備による売電量（一次エネルギー換算値）(MJ/yr) (48)
    E_PV_sell = calc_E_PV_sell(E_E_PV_sell_d_t)

    # 1年当たりのコージェネレーション設備による発電量のうちの自己消費分 (kWH/yr) (s8 4)
    E_E_CG_self = get_E_E_CG_self(E_E_TU_aux_d_t)

    # 1年当たりのコージェネレーション設備による売電量に係るガス消費量の控除量 (MJ/yr) (46)
    E_G_CG_sell = calc_E_G_CG_sell(E_CG_sell, E_E_CG_self, E_E_CG_h, E_G_CG_ded, e_BB_ave, Q_CG_h, CG != None)

    # 1年当たりのコージェネレーション設備の売電量に係る設計一次エネルギー消費量の控除量 (MJ/yr) (41)
    E_S_sell = get_E_S_sell(E_G_CG_sell)

    # 1年当たりの太陽光発電設備による発電量のうちの自家消費分に係る設計一次エネルギー消費量の削減量 (MJ/yr) (39)
    E_S_PV_h = calc_E_S_PV_h(E_E_PV_h_d_t)

    # 1年当たりのコージェネレーション設備による発電量のうちの自家消費分に係る設計一次エネルギー消費量の削減量 (MJ/yr) (40)
    E_S_CG_h = calc_E_S_CG_h(E_E_CG_h_d_t)

    # 1年当たりのエネルギー利用効率化設備による発電量のうちの自家消費分に係る一次エネルギー消費量の控除量 (MJ/yr) (38)
    E_S_h = get_E_S_h(E_S_PV_h, E_S_CG_h)

    # 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/yr) (36)
    E_S = get_E_S(E_S_h, E_S_sell)

    # 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量 (MJ/yr) (37)
    E_S_CG = get_E_S_CG(E_S_CG_h, E_S_sell)

    # 1年当たりの再生可能エネルギー源の利用に資する設備で生成されるエネルギー量（誘導設計一次エネルギー消費量の算定で考慮されるものを除く）（MJ/yr） (53)
    E_R = get_E_R(E_S_PV_h, E_PV_sell)

    return E_S, E_S_CG, E_R


def get_E_S(E_S_h, E_S_sell):
    """1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/yr) (36)

    Args:
      E_S_h(float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/yr)
      E_S_sell(float): 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/yr)

    Returns:
      float: 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/yr) (36)

    """
    
    return E_S_h + E_S_sell


def get_E_S_CG(E_S_CG_h, E_S_sell):
    """1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量（MJ/yr） (37)

    Args:
        E_S_CG_h (float): 1年当たりのージェネレーション設備による発電量のうちの自家消費分に係る設計一次エネルギー消費量の削減量（MJ/yr）
        E_S_sell (float): 1年当たりのコージェネレーション設備による売電量に係る設計一次エネルギー消費量の控除量（MJ/yr）

    Returns:
        float: 1年当たりのエネルギー利用効率化設備（コージェネレーション設備に限る）による設計一次エネルギー消費量の削減量（MJ/yr） (37)
    """
    return E_S_CG_h + E_S_sell


def get_E_S_h(E_S_PV_h, E_S_CG_h):
    """1年当たりのエネルギー利用効率化設備による発電量のうちの自家消費分に係る設計一次エネルギー消費量の削減量（MJ/yr） (38)

    Args:
        E_S_PV_h (float): 1年当たりの太陽光発電設備による発電量のうちの自家消費分に係る設計一次エネルギー消費量の削減量（MJ/yr）
        E_S_CG_h (float): 1年当たりのージェネレーション設備による発電量のうちの自家消費分に係る設計一次エネルギー消費量の削減量（MJ/yr）

    Returns:
        float: 1年当たりのエネルギー利用効率化設備による発電量のうちの自家消費分に係る設計一次エネルギー消費量の削減量（MJ/yr） (38)
    """
    return E_S_PV_h + E_S_CG_h


def calc_E_S_PV_h(E_E_PV_h_d_t):
    """1年当たりの太陽光発電設備による発電量のうちの自家消費分に係る設計一次エネルギー消費量の削減量 (MJ/yr) (39)

    Args:
        E_E_PV_h_d_t(ndarray): 1時間当たりの太陽光発電設備による発電量のうちの自家消費分 (kWh/h)

    Returns:
        float: 1年当たりの太陽光発電設備による発電量のうちの自家消費分に係る設計一次エネルギー消費量の削減量 (MJ/yr)
    """
    
    # 電気の量 1kWh を熱量に換算する係数 (kJ/kWh)
    f_prim = get_f_prim()

    # 1年あたりの太陽光発電設備による発電量のうちの自家消費分に係る一次エネルギー消費量の控除量 (MJ/yr)
    E_S_PV_h = np.sum(E_E_PV_h_d_t) * f_prim * 1e-3

    return E_S_PV_h


def calc_E_S_CG_h(E_E_CG_h_d_t):
    """1年当たりのコージェネレーション設備による発電量のうちの自家消費分に係る設計一次エネルギー消費量の削減量 (MJ/yr) (40)

    Args:
        E_E_CG_h_d_t(ndarray): 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h)

    Returns:
        float: 1年当たりのコージェネレーション設備による発電量のうちの自家消費分に係る設計一次エネルギー消費量の削減量 (MJ/yr)
    """
    
    # 電気の量 1kWh を熱量に換算する係数 (kJ/kWh)
    f_prim = get_f_prim()

    # 1年あたりのコージェネレーション設備による発電量のうちの自家消費分に係る一次エネルギー消費量の控除量 (MJ/yr)
    E_S_CG_h = np.sum(E_E_CG_h_d_t) * f_prim * 1e-3

    return E_S_CG_h


def get_E_S_sell(E_G_CG_sell):
    """1年当たりのコージェネレーション設備の売電量に係る設計一次エネルギー消費量の控除量 (MJ/yr) (41)

    Args:
      E_G_CG_sell(float): 1年当たりのコージェネレーション設備の売電量に係る設計一次エネルギー消費量の控除量 (MJ/yr)

    Returns:
      float: 1年当たりのコージェネレーション設備の売電量に係る設計一次エネルギー消費量の控除量 (MJ/yr)

    """
    
    return E_G_CG_sell


# ============================================================================
# 13.1 太陽光発電設備による発電量のうちの自家消費分
# ============================================================================


def get_E_E_PV_h_d_t(E_E_PV_d_t, E_E_dmd_d_t, E_E_CG_h_d_t, has_PV):
    """1 時間当たりの太陽光発電設備による発電炉湯のうちの自家消費分 (kWh/h) (42)

    Args:
      E_E_PV_d_t(ndarray): 1時間当たりの太陽光発電設備による発電量のうちの自家消費分 (kWh/h)
      E_E_dmd_d_t(ndarray): 1時間当たりの太陽光発電設備による発電量 (kWh/h)
      E_E_CG_h_d_t(ndarray): 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h)
      has_PV(bool): 太陽光発電設備を採用する場合はTrue

    Returns:
      float: 1 時間当たりの太陽光発電設備による発電炉湯のうちの自家消費分 (kWh/h)

    """
    
    if has_PV == False:
        # 太陽光発電設備を採用しない場合 (42-1)
        E_E_PV_h_d_t = np.zeros_like(E_E_PV_d_t)
    else:
        # 太陽光発電設備を採用する場合 (42-2)
        E_E_PV_h_d_t = np.minimum(E_E_PV_d_t, E_E_dmd_d_t - E_E_CG_h_d_t)

    return E_E_PV_h_d_t


# ============================================================================
# 13.2 コージェネレーション設備による発電量
# ============================================================================

def get_E_E_CG_h(E_E_CG_h_d_t):
    """1年当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/yr) (43)

    Args:
      E_E_CG_h_d_t(ndarray): 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h)

    Returns:
      float: 1年当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/yr)

    """
    
    return np.sum(E_E_CG_h_d_t)


# 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h) (44)
def get_E_E_CG_h_d_t(E_E_CG_gen_d_t, E_E_dmd_d_t, has_CG):
    """1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h) (44)

    Args:
      E_E_CG_gen_d_t(ndarray): 1時間当たりのコージェネレーション設備による発電のうちの自家消費分 (kWh/h)
      E_E_dmd_d_t(ndarray): 1時間当たりの電力需要 (kWh/h)
      has_CG(bool): コージェネレーション設備を採用する場合はTrue

    Returns:
      ndarray: 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h)

    """

    if has_CG == False:
        # コージェネレーション設備を採用しない場合 (44-1)
        E_E_CG_h_d_t = np.zeros_like(E_E_CG_gen_d_t)
    else:
        # コージェネレーション設備を採用する場合 (45-2)
        E_E_CG_h_d_t = np.minimum(E_E_CG_gen_d_t, E_E_dmd_d_t)
    return E_E_CG_h_d_t


# ============================================================================
# 13.3 コージェネレーション設備による売電量に係るガス消費量の控除量
# ============================================================================


def calc_E_G_CG_sell(E_CG_sell, E_E_CG_self, E_E_CG_h, E_G_CG_ded, e_BB_ave, Q_CG_h, has_CG):
    """1年当たりのコージェネレーション設備による売電量に係るガス消費量の控除量 (MJ/yr) (46)

    Args:
      E_CG_sell(float): 1年当たりのコージェネレーション設備による売電量(一次エネルギー換算値) (MJ/yr)
      E_E_CG_self(float): 1年当たりのコージェネレーション設備による発電量のうちの自己消費分 (kWh/yr)
      E_E_CG_h(float): 1年当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/yr)
      E_G_CG_ded(float): 1年当たりのコージェネレーション設備のガス消費量のうちの売電に係る控除対象分 (MJ/yr)
      e_BB_ave(float): コージェネレーション設備の給湯時のバックアップボイラーの年間平均効率 (-)
      Q_CG_h(float): 1年当たりのコージェネレーション設備による製造熱量のうちの自家消費算入分 (MJ/yr)
      has_CG(bool): コージェネレーション設備を採用する場合はTrue

    Returns:
      float: 1年当たりのコージェネレーション設備による売電量に係るガス消費量の控除量 (MJ/yr)

    """
    
    if has_CG == False:
        # コージェネレーション設備を採用しない場合 (46-1)
        E_G_CG_sell = np.zeros_like(E_CG_sell)
    else:
        # 電気の量 1kWh を熱量に換算する係数
        f_prim = get_f_prim()

        # コージェネレーション設備を採用する場合 (46-2)
        denominator = E_CG_sell + (E_E_CG_self + E_E_CG_h) * f_prim * 1e-3 + Q_CG_h / e_BB_ave
        E_G_CG_sell = E_G_CG_ded * (E_CG_sell / denominator)

    return E_G_CG_sell


# ============================================================================
# 13.4 太陽光発電設備による売電量（参考）
# ============================================================================

# 1 年当たりの太陽光発電設備による売電量（一次エネルギー換算値） (48)
def calc_E_PV_sell(E_E_PV_sell_d_t):
    """1 年当たりの太陽光発電設備による売電量（一次エネルギー換算値） (48)

    Args:
        E_E_PV_sell_d_t (ndarray): 1 時間当たりの太陽光発電設備による売電量（二次エネルギー）(kWh/h)

    Returns:
        float: 1 年当たりの太陽光発電設備による売電量（一次エネルギー換算値）(MJ/yr)
    """

    # 電気の量 1kWh を熱量に換算する係数 (kJ/kWh) (s2-1-b)
    f_prim = get_f_prim()

    # 1 年当たりの太陽光発電設備による売電量（一次エネルギー換算値）(MJ/yr) (48)
    E_PV_sell = np.sum(E_E_PV_sell_d_t) * f_prim * 1e-3

    return E_PV_sell


# 1 時間当たりの太陽光発電設備による売電量（二次エネルギー）(kWh/h) (49)
def get_E_E_PV_sell_d_t(E_E_PV_d_t, E_E_PV_h_d_t):
    """1 時間当たりの太陽光発電設備による売電量（二次エネルギー）(kWh/h) (49)

    Args:

    Returns:
      float: 1 時間当たりの太陽光発電設備による売電量（二次エネルギー）(kWh/h)

    """
    return E_E_PV_d_t - E_E_PV_h_d_t


# ============================================================================
# 13.5 コージェネレーション設備による売電量（参考）
# ============================================================================

def calc_E_CG_sell(E_E_CG_sell_d_t):
    """1年当たりのコージェネレーション設備による売電量（一次エネルギー換算値）(MJ/yr) (51)

    Args:
      E_E_CG_sell_d_t(ndarray): 1時間当たりのコージェネレーション設備による売電量(二次エネルギー) (kWh/h)

    Returns:
      float: 1年当たりのコージェネレーション設備による売電量（一次エネルギー換算値）(MJ/yr)

    """
    
    # 電気の量 1kWh を熱量に換算する係数 (kJ/kWh) (s2-1-b)
    f_prim = get_f_prim()

    # 1年当たりのコージェネレーション設備による売電量（一次エネルギー換算値）(MJ/yr) (51)
    E_CG_sell = np.sum(E_E_CG_sell_d_t) * f_prim * 1e-3

    return E_CG_sell


def get_E_E_CG_sell_d_t(E_E_CG_gen_d_t, E_E_CG_h_d_t, has_CG_reverse):
    """1時間当たりのコージェネレーション設備による売電量(二次エネルギー) (kWh/h) (52)

    Args:
      E_E_CG_gen_d_t(ndarray): 1時間当たりのコージェネレーション設備による発電量 (kWh/h)
      E_E_CG_h_d_t(ndarray): 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h)
      has_CG_reverse(bool): コージェネレーション設備が逆潮流を行う場合はTrue

    Returns:
      ndarray: 1時間当たりのコージェネレーション設備による売電量(二次エネルギー) (kWh/h)

    """

    if has_CG_reverse == False:
        # 逆潮流を行わない場合 (52-1)
        E_E_CG_sell_d_t = np.zeros_like(E_E_CG_gen_d_t)
    else:
        # 逆潮流を行う場合 (52-2)
        E_E_CG_sell_d_t = E_E_CG_gen_d_t - E_E_CG_h_d_t
    return E_E_CG_sell_d_t


# ============================================================================
# 14.再生可能エネルギー源の利用に資する設備で生成されるエネルギー量
#   （誘導設計一次エネルギー消費量の算定で考慮されるものを除く）
# ============================================================================

def get_E_R(E_S_PV_h, E_PV_sell):
    """1年当たりの再生可能エネルギー源の利用に資する設備で生成されるエネルギー量（誘導設計一次エネルギー消費量の算定で考慮されるものを除く） (MJ/yr) (53)

    Args:
        E_S_PV_h (float): 1年当たりの太陽光発電設備による発電量のうちの自家消費分に係る設計一次エネルギー消費量の削減量 (MJ/yr)
        E_PV_sell (float): 1年当たりの太陽光発電設備による売電量（一次エネルギー）(MJ/yr)

    Returns:
        float: 1年当たりの再生可能エネルギー源の利用に資する設備で生成されるエネルギー量（誘導設計一次エネルギー消費量の算定で考慮されるものを除く） (MJ/yr)
    """
    return E_S_PV_h + E_PV_sell


# ============================================================================
# 15.設計二次エネルギー消費量(参考)
# ============================================================================

def calc_E_E(region, sol_region, A_A, A_MR, A_OR, A_env, HW, Q, TS, mu_H, mu_C, r_A_ufvnt, underfloor_insulation,
            NV_MR, NV_OR, mode_H, mode_C,
            V, L,
            H_A=None,
            H_MR=None, H_OR=None, H_HS=None,
            CG=None,
            SHC=None,
            L_T_H_d_t_i=None,
            C_A=None, C_MR=None, C_OR=None, L_H_d_t=None,
            L_CS_d_t=None, L_CL_d_t=None,
            HEX=None, PV=None, solrad=None
            ):
    """1 年当たりの設計消費電力量（kWh/年） (54)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      HW(dict): 給湯機の仕様
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      TS(bool): 蓄熱
      mu_H(float): 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数
      mu_C(float): 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数
      r_A_ufvnt(float): 床下換気
      underfloor_insulation(bool): 床下空間が断熱空間内である場合はTrue
      NV_MR(float): 主たる居室における通風の利用における相当換気回数
      NV_OR(float): その他の居室における通風の利用における相当換気回数
      mode_H(str): 暖房方式
      mode_C(str): 冷房方式
      V(dict): 換気設備仕様辞書
      L(dict): 照明設備仕様辞書
      H_A(dict, optional, optional): 暖房方式, defaults to None
      H_MR(dict, optional, optional): 暖房機器の仕様, defaults to None
      H_OR(dict, optional, optional): 暖房機器の仕様, defaults to None
      H_HS(dict, optional, optional): 温水暖房機の仕様, defaults to None
      CG(dict, optional, optional): コージェネレーションの機器, defaults to None
      SHC(dict, optional, optional): 集熱式太陽熱利用設備の仕様, defaults to None
      L_H_A_d_t(ndarray, optional): 暖房負荷, defaults to None
      L_T_H_d_t_i(ndarray, optional, optional): 暖房区画i=1-5それぞれの暖房負荷 defaults to None
      C_A(type], optional, optional): description], defaults to None
      C_MR(type], optional, optional): description], defaults to None
      C_OR(type], optional, optional): description], defaults to None
      L_CS_A_d_t(ndarray, optional): 冷房負荷, defaults to None
      L_CL_A_d_t(ndarray, optional): 冷房負荷, defaults to None
      L_CS_d_t(ndarray, optional, optional): 暖冷房区画の 1 時間当たりの冷房顕熱負荷, defaults to None
      L_CL_d_t(ndarray, optional, optional): 暖冷房区画の 1 時間当たりの冷房潜熱負荷, defaults to None
      HEX(dict, optional, optional): 熱交換器型設備仕様辞書, defaults to None
      PV(ndarray, optional, optional): 太陽光発電設備のリスト, defaults to None
      solrad(ndarray, optional, optional): load_solrad の返り値, defaults to None
      A_env: param L_H_d_t:  (Default value = None)
      L_H_d_t: Default value = None)

    Returns:
      1 年当たりの設計消費電力量（kWh/年）: 1 年当たりの設計消費電力量（kWh/年）

    """
    # 想定人数
    n_p = get_n_p(A_A)

    # 実質的な暖房機器の仕様を取得
    spec_MR, spec_OR = get_virtual_heating_devices(region, H_MR, H_OR)

    # 実質的な温水暖房機の仕様を取得
    spec_HS = get_virtual_heatsource(region, H_HS)

    # 暖房方式及び運転方法の区分
    mode_MR, mode_OR = calc_heating_mode(region=region, H_MR=spec_MR, H_OR=spec_OR)

    # その他または設置しない場合
    spec_HW = get_virtual_hotwater(region, HW)

    # 温水暖房負荷の計算
    L_HWH = calc_L_HWH(A_A, A_MR, A_OR, HEX, H_HS, H_MR, H_OR, Q, SHC, TS, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt, region, sol_region,
                       underfloor_insulation, HW, CG)

    # 暖房日の計算
    heating_flag_d = calc_heating_flag_d(A_A, A_MR, A_OR, HEX, H_MR, H_OR, Q, SHC, TS, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt, region,
                                         sol_region, underfloor_insulation)

    # 暖房設備の消費電力量
    E_E_H_d_t = get_E_E_H_d_t(region, sol_region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q,
                              H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG, SHC, heating_flag_d,
                              L_T_H_d_t_i, L_CS_d_t, L_CL_d_t)

    # 1時間当たりの冷房設備の消費電力量
    E_E_C_d_t = calc_E_E_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_T_H_d_t_i, L_CS_d_t, L_CL_d_t)

    # 1 時間当たりの機械換気設備の消費電力量
    E_E_V_d_t = calc_E_E_V_d_t(n_p, A_A, V, HEX)

    # 1 時間当たりの照明設備の消費電力量
    E_E_L_d_t = calc_E_E_L_d_t(n_p, A_A, A_MR, A_OR, L)

    # 1日当たりの給湯設備の消費電力量
    E_E_W_d_t = calc_E_E_W_d_t(n_p, L_HWH, heating_flag_d, region, sol_region, spec_HW, SHC)

    # 1 時間当たりの家電の消費電力量
    E_E_AP_d_t = calc_E_E_AP_d_t(n_p)

    # 1 時間当たりの調理の消費電力量
    E_E_CC_d_t = get_E_E_CC_d_t()

    # 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h)
    E_CG, E_E_CG_gen_d_t, E_E_CG_h_d_t, E_E_TU_aux_d_t, E_E_CG_h_d_t, E_G_CG_ded, e_BB_ave, Q_CG_h =\
        calc_E_W(A_A, region, sol_region, HW, SHC, CG, H_A, H_MR, H_OR, H_HS, C_A, C_MR,
                C_OR,
                                V, L, A_MR, A_OR, A_env, Q, mu_H, mu_C, NV_MR, NV_OR, TS,
                                r_A_ufvnt, HEX, underfloor_insulation, mode_H, mode_C)

    # 太陽光発電設備の発電量
    E_E_PV_d_t = calc_E_E_PV_d_t(PV, solrad)
    E_E_dmd_d_t = get_E_E_dmd_d_t(E_E_H_d_t, E_E_C_d_t, E_E_V_d_t, E_E_L_d_t, E_E_W_d_t, E_E_AP_d_t, E_E_CC_d_t)
    E_E_PV_h_d_t = get_E_E_PV_h_d_t(E_E_PV_d_t, E_E_dmd_d_t, E_E_CG_h_d_t, has_PV=PV != None)

    E_E = sum(E_E_H_d_t) \
          + sum(E_E_C_d_t) \
          + sum(E_E_V_d_t) \
          + sum(E_E_L_d_t) \
          + sum(E_E_W_d_t) \
          + sum(E_E_AP_d_t) \
          + sum(E_E_CC_d_t) \
          - sum(E_E_PV_h_d_t) \
          - sum(E_E_CG_h_d_t)  # (54)

    # 小数点以下一位未満の端数があるときは、これを四捨五入する。
    return Decimal(E_E).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP), E_E_PV_h_d_t, E_E_PV_d_t, E_E_CG_gen_d_t, E_E_CG_h_d_t, E_E_dmd_d_t, E_E_TU_aux_d_t


def calc_E_G(region, sol_region, A_A, A_MR, A_OR, A_env, Q, mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX, underfloor_insulation,
            H_A, H_MR, H_OR, H_HS, C_A, C_MR, C_OR, V, L, HW, SHC,
            spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, mode_H, mode_C, CG, L_T_H_d_t_i,
            L_HWH, heating_flag_d):
    """1 年当たりの設計ガス消費量（MJ/年） (55)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      A_env(float): 外皮の部位の面積の合計 (m2)
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      mu_H(float): 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数
      mu_C(float): 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数
      NV_MR(float): 主たる居室における通風の利用における相当換気回数
      NV_OR(float): その他の居室における通風の利用における相当換気回数
      TS(bool): 蓄熱
      r_A_ufvnt(float): 床下換気
      HEX(dict): 熱交換器型設備仕様辞書
      underfloor_insulation(bool): 床下空間が断熱空間内である場合はTrue
      H_A(dict): 暖房方式
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様
      H_HS(dict): 温水暖房機の仕様
      C_A(dict): 冷房方式
      C_MR(dict): 主たる居室の冷房機器
      C_OR(dict): その他の居室の冷房機器
      V(dict): 換気設備仕様辞書
      L(dict): 照明設備仕様辞書
      HW(dict): 給湯機の仕様
      SHC(dict): 集熱式太陽熱利用設備の仕様
      spec_MR(dict): 主たる居室の仕様
      spec_OR(dict): その他の居室の仕様
      spec_HS(dict): 暖房方式及び運転方法の区分
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      mode_H(str): 暖房方式
      mode_C(str): 冷房方式
      CG(dict): コージェネレーションの機器
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷
      L_HWH(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      heating_flag_d(ndarray): 暖房日

    Returns:
      float: 1 年当たりの設計ガス消費量（MJ/年）

    """
    # 仮想居住人数
    n_p = get_n_p(A_A)

    # 暖房設備のガス消費量（MJ/h）
    E_G_H_d_t = get_E_G_H_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG,
                              L_T_H_d_t_i)

    # 1時間当たりの冷房設備のガス消費量 (MJ/h)
    E_G_C_d_t = calc_E_G_C_d_t()

    # 1日当たりの給湯設備のガス消費量 (MJ/d)
    E_G_W_d = calc_E_G_W_d_t(n_p, L_HWH, heating_flag_d, A_A, region, sol_region, HW, SHC)

    # 1日当たりのコージェネレーション設備のガス消費量 (MJ/h)
    E_G_CG_d_t, *args = calc_E_CG_d_t(A_A, region, sol_region, HW, SHC, CG, H_A, H_MR, H_OR, H_HS, C_A, C_MR,
                           C_OR,
                           V, L, A_MR, A_OR, A_env, Q, mu_H, mu_C, NV_MR, NV_OR, TS,
                           r_A_ufvnt, HEX, underfloor_insulation, mode_H, mode_C)

    # 1 時間当たりの家電のガス消費量 (MJ/h)
    E_G_AP_d_t = get_E_G_AP_d_t()

    # 1 時間当たりの調理のガス消費量 (MJ/h)
    E_G_CC_d_t = calc_E_G_CC_d_t(n_p)

    E_G = sum(E_G_H_d_t) \
          + sum(E_G_C_d_t) \
          + sum(E_G_W_d) \
          + sum(E_G_CG_d_t) \
          + sum(E_G_AP_d_t) \
          + sum(E_G_CC_d_t)  # (55)

    # 小数点以下一位未満の端数があるときは、これを四捨五入する。
    return Decimal(E_G).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)


def calc_E_K(region, sol_region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, CG, L_T_H_d_t_i, L_HWH, heating_flag_d, HW, SHC):
    """1 年当たりの設計灯油消費量（MJ/年） (56)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      H_A(dict): 暖房方式
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      CG(dict): コージェネレーションの機器
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷
      L_HWH(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      heating_flag_d(ndarray): 暖房日
      HW(dict): 給湯機の仕様
      SHC(dict): 集熱式太陽熱利用設備の仕様

    Returns:
      float: 1 年当たりの設計灯油消費量（MJ/年） (56)

    """
    
    # 仮想居住人数
    n_p = get_n_p(A_A)

    # 暖房設備の灯油消費量（MJ/h）
    E_K_H_d_t = calc_E_K_H_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG,
                               L_T_H_d_t_i)

    # 1時間当たりの冷房設備の灯油消費量
    E_K_C_d_t = calc_E_K_C_d_t()

    # 1日当たりの給湯設備の灯油消費量 (MJ/d)
    E_K_W_d_t = calc_E_K_W_d_t(n_p, L_HWH, heating_flag_d, A_A, region, sol_region, HW, SHC)

    # 1日当たりのコージェネレーション設備の灯油消費量
    E_K_CG_d = np.zeros(365)

    # 1 時間当たりの家電の灯油消費量
    E_K_AP_d_t = get_E_K_AP_d_t()

    # 1 時間当たりの調理の灯油消費量
    E_K_CC_d_t = get_E_K_CC_d_t()

    # 1年当たりの設計灯油消費量（MJ / 年）
    E_K_raw = sum(E_K_H_d_t) \
              + sum(E_K_C_d_t) \
              + sum(E_K_W_d_t) \
              + sum(E_K_CG_d) \
              + sum(E_K_AP_d_t) \
              + sum(E_K_CC_d_t)  # (46)

    # 小数点以下一位未満の端数があるときは、これを四捨五入する。
    E_K = Decimal(E_K_raw).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

    return E_K


def calc_E_UT_H(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_H, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG,
               L_T_H_d_t, L_CS_d_t, L_CL_d_t):
    """1 年当たりの未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/年） (58)

    Args:
        region(int): 省エネルギー地域区分
        A_A(float): 床面積の合計 [m2]
        A_MR(float): 主たる居室の床面積 [m2]
        A_OR(float): その他の居室の床面積 [m2]
        A_env(float): 外皮の部位の面積の合計 [m2]
        mu_H(float): 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数 [(W/m2)/(W/m2)]
        mu_C(float): 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数 [(W/m2)/(W/m2)]
        Q(float): 当該住戸の熱損失係数 [W/m2K]
        mode_H(str): 暖房方式
        H_A(dict): 暖房方式
        spec_MR(dict): 主たる居室の仕様
        spec_OR(dict): その他の居室の仕様
        spec_HS(dict): 暖房方式及び運転方法の区分
        mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
        mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
        HW(dict): 給湯機の仕様
        CG(dict): コージェネレーションの機器
        L_T_H_d_t(ndarray): 暖房区画の暖房負荷
        L_CS_d_t(ndarray): 暖冷房区画の 1 時間当たりの冷房顕熱負荷
        L_CL_d_t(ndarray): 暖冷房区画の 1 時間当たりの冷房潜熱負荷

    Returns:
        float: 1 年当たりの未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/年）

    """
    # 暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値
    E_UT_H_d_t = calc_E_UT_H_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_H, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG,
                                 L_T_H_d_t, L_CS_d_t, L_CL_d_t)

    # 1 年当たりの未処理暖房負荷の設計一次エネルギー消費量相当値
    E_UT_H_raw = sum(E_UT_H_d_t)  # (58)

    # 小数点以下一位未満の端数があるときは、これを四捨五入する。
    E_UT_H = Decimal(E_UT_H_raw).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

    return E_UT_H


# 1 年当たりの未処理冷房負荷の設計一次エネルギー消費量相当値（MJ/年）
def get_E_UT_C(A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_C, C_A, region, L_H_d_t, L_CS_d_t, L_CL_d_t):
    """1 年当たりの未処理冷房負荷の設計一次エネルギー消費量相当値（MJ/年） (59)

    Args:
        A_A(float): 床面積の合計 [m2]
        A_MR(float): 主たる居室の床面積 [m2]
        A_OR(float): その他の居室の床面積 [m2]
        A_env(float): 外皮の部位の面積の合計 [m2]
        mu_H(float): 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数 [(W/m2)/(W/m2)]
        mu_C(float): 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数 [(W/m2)/(W/m2)]
        Q(float): 当該住戸の熱損失係数 [W/m2K]
        mode_C(str): 冷房方式
        C_A(dict): 冷房方式
        region(int): 省エネルギー地域区分
        L_T_H_d_t(ndarray): 暖房区画の暖房負荷
        L_CS_d_t(ndarray): 暖冷房区画の 1 時間当たりの冷房顕熱負荷
        L_CL_d_t(ndarray): 暖冷房区画の 1 時間当たりの冷房潜熱負荷

    Returns:
        float: 1 年当たりの未処理冷房負荷の設計一次エネルギー消費量相当値（MJ/年）
    """
    if mode_C == '住戸全体を連続的に冷房する方式':
        # VAV方式の採用
        if 'VAV' in C_A:
            VAV = C_A['VAV']

        # 全般換気機能の有無
        if 'general_ventilation' in C_A:
            general_ventilation = C_A['general_ventilation']

        # ダクトが通過する空間
        if 'duct_insulation' in C_A:
            duct_insulation = C_A['duct_insulation']

        # 機器の仕様の
        if C_A['EquipmentSpec'] == '入力しない':
            # 付録B
            q_hs_rtd_C = dc_spec.get_q_hs_rtd_C(region, A_A)
        elif C_A['EquipmentSpec'] == '定格能力試験の値を入力する':
            q_hs_rtd_C = C_A['q_hs_rtd_C']
        elif C_A['EquipmentSpec'] == '定格能力試験と中間能力試験の値を入力する':
            q_hs_rtd_C = C_A['q_hs_rtd_C']
        else:
            raise ValueError(C_A['EquipmentSpec'])

        # 設計風量(暖房)
        if 'V_hs_dsgn_C' in C_A:
            V_hs_dsgn_C = C_A['V_hs_dsgn_C']
        else:
            V_fan_rtd_C = dc_spec.get_V_fan_rtd_C(q_hs_rtd_C)
            V_hs_dsgn_C = dc_spec.get_V_fan_dsgn_C(V_fan_rtd_C)

        # 定格冷房能力
        q_hs_rtd_H = 0

        # 設計風量(冷房)
        V_hs_dsgn_H = 0

        E_UT_C_d_t, _, _, _, _, _, \
        _, _, _, _, _ = dc.get_Q_UT_A(A_A, A_MR, A_OR, A_env, mu_H, mu_C, q_hs_rtd_H, q_hs_rtd_C, V_hs_dsgn_H, V_hs_dsgn_C, Q,
             VAV, general_ventilation, duct_insulation, region, L_H_d_t, L_CS_d_t, L_CL_d_t)
    else:
        E_UT_C_d_t = calc_E_UT_C_d_t()

    # 1 年当たりの未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/年）
    E_UT_C_raw = sum(E_UT_C_d_t) # (59)

    # 小数点以下一位未満の端数があるときは、これを四捨五入する。
    E_UT_C = Decimal(E_UT_C_raw).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

    return E_UT_C


# ============================================================================
# 17.電力需要
# ============================================================================


def get_E_E_dmd_d_t(E_E_H_d_t, E_E_C_d_t, E_E_V_d_t, E_E_L_d_t, E_E_W_d_t, E_E_AP_d_t, E_E_CC_d_t):
    """日付dの時刻tにおける1時間当たりの電力需要 (kWh/h) (60)

    Args:
      E_E_H_d_t(ndarray): 日付dの時刻tにおける1時間当たりの暖房設備の消費電力量 [kWh/h]
      E_E_C_d_t(ndarray): 日付dの時刻tにおける1時間当たりの冷房設備の消費電力量 [kWh/h]
      E_E_V_d_t(ndarray): 日付dの時刻tにおける1時間当たりの機械換気設備の消費電力量 [kWh/h]
      E_E_L_d_t(ndarray): 日付dの時刻tにおける1時間当たりの照明設備の消費電力量[kWh/h]
      E_E_W_d_t(ndarray): 日付dの時刻tにおける1時間当たりの給湯設備の消費電力量 [kWh/h]
      E_E_AP_d_t(ndarray): 日付dの時刻tにおける1時間当たりの家電の消費電力量 [kWh/h]
      E_E_CC_d_t(ndarray): 日付dの時刻tにおける1時間当たりの調理の消費電力量 [kWh/h]

    Returns:
      ndarray: 日付dの時刻tにおける1時間当たりの電力需要 (kWh/h) (60)

    """
    return E_E_H_d_t + E_E_C_d_t + E_E_V_d_t + E_E_L_d_t + E_E_W_d_t + E_E_AP_d_t + E_E_CC_d_t


# =============================================================================
# 各設備の設計一次エネルギー消費量の算定に係る設定
# =============================================================================
