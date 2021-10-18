# ============================================================================
# 第二章 単位住戸の一次エネルギー消費量
# 第一節 全般
# Ver.07（エネルギー消費性能計算プログラム（住宅版）Ver.02～）
# ============================================================================

import numpy as np
from math import ceil

from pyhees.section2_1_b import get_f_prim
from pyhees.section2_2 import get_E_T_star, calc_E_H, calc_E_C, calc_E_W, calc_E_L, calc_E_V, calc_E_M, calc_heating_load, calc_cooling_load, \
    get_virtual_heating_devices, get_virtual_heatsource, calc_heating_mode, calc_L_HWH, calc_E_E, calc_E_G, calc_E_K, \
    calc_E_UT_H, calc_E_S, get_E_E_CG_h
from pyhees.section2_3 import get_E_ST_star, calc_E_SH, calc_E_SC, calc_E_SV, calc_E_SW, calc_E_SL, calc_E_SM
from pyhees.section3_1 import get_Q
from pyhees.section3_2 import calc_insulation_performance
from pyhees.section7_1_b import get_virtual_hotwater


# ============================================================================
# 5. 住戸の床面積並びに主たる居室、その他の居室及び非居室の定義
# ============================================================================

# ============================================================================
# 6. 電気の量 1kWh を熱量に換算する係数
# ============================================================================


# ============================================================================
# 7. 仮想居住人数
# ============================================================================


# ============================================================================
# 8. 設計一次エネルギー消費量
# ============================================================================

def calc_E_T(spec):
    """設計一次エネルギー消費量[GJ/年]を計算する

    Args:
      spec(dict): 住戸についての詳細なデータ

    Returns:
      tuple: 1年当たりの各消費量 E_T, E_H, E_C, E_V, E_L, E_W, E_S, E_M, UPL, E_gen, E_E_gen, E_E_PV_h_d_t, E_E, E_G, E_K (15 variables)

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
                  spec['H_A'], spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, spec['CG'], spec['SHC'],
                  heating_flag_d, L_T_H_d_t_i, L_CS_d_t, L_CL_d_t)

    # 暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値
    UPL = calc_E_UT_H(spec['region'], spec['A_A'], spec['A_MR'], spec['A_OR'], A_env, eta_H, eta_C, Q, spec['mode_H'],
                     spec['H_A'], spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, spec['CG'],
                     L_T_H_d_t_i, L_CS_d_t, L_CL_d_t)
    UPL = np.sum(UPL)

    # 温水暖房負荷の計算
    L_HWH = calc_L_HWH(spec['A_A'], spec['A_MR'], spec['A_OR'], spec['HEX'], spec['H_HS'], spec['H_MR'],
                           spec['H_OR'], Q, spec['SHC'], spec['TS'], eta_H, eta_C, spec['NV_MR'], spec['NV_OR'],
                           spec['r_A_ufvnt'], spec['region'], spec['sol_region'], spec['underfloor_insulation'],
                           spec['CG'])

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
    E_S = calc_E_S(spec['region'], spec['sol_region'], spec['PV'], spec['CG'], E_E_dmd_d_t, E_E_CG_gen_d_t,
                   E_E_TU_aux_d_t, E_E_CG_h, E_G_CG_ded, e_BB_ave, Q_CG_h)

    E_E_gen = np.sum(calc_E_E_PV_d_t(spec['PV'], solrad) + E_E_CG_gen_d_t)

    # ---- 合計 ----

    E_T = get_E_T(E_H, E_C, E_V, E_L, E_W, E_S, E_M)

    return E_T, E_H, E_C, E_V, E_L, E_W, E_S, E_M, UPL, E_gen, E_E_gen, E_E_PV_h_d_t, E_E, E_G, E_K


def get_E_T(E_H, E_C, E_V, E_L, E_W, E_S, E_M):
    """各1 年当たりの設計一次エネルギー消費量を合計する

    Args:
      E_H(float): 1 年当たりの暖房設備の設計一次エネルギー消費量（MJ/年）
      E_C(float): 1 年当たりの冷房設備の設計一次エネルギー消費量
      E_V(float): 1 年当たりの機械換気設備の設計一次エネルギー消費量
      E_L(float): 1 年当たりの照明設備の設計一次エネルギー消費量
      E_W(float): 1 年当たりの給湯設備（コージェネレーション設備を含む）の設計一次エネルギー消費量
      E_S(float): 1 年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量
      E_M(float): 1 年当たりのその他の設計一次エネルギー消費量

    Returns:
      float: 1 年当たりの設計一次エネルギー消費量（GJ/年）

    """
    # 1 年当たりの設計一次エネルギー消費量（MJ/年）(s2-2-1)
    E_T_star = get_E_T_star(E_H, E_C, E_V, E_L, E_W, E_S, E_M)

    # 小数点以下一位未満の端数があるときはこれを切り上げてMJをGJに変更する
    E_T = ceil(E_T_star / 100) / 10  # (1)

    return E_T


# ============================================================================
# 9. 基準一次エネルギー消費量
# ============================================================================

def calc_E_ST(spec):
    """基準一次エネルギー消費量の計算

    Args:
      spec(dict): 住戸についての詳細なデータ

    Returns:
      tuple: 1年当たりの各消費量 E_ST, E_SH, E_SC, E_SV, E_SL, E_SW, E_SM (7 variables)

    """
    # 1年当たりの機械換気設備の基準一次エネルギー消費量
    E_SV = calc_E_SV(spec['A_A'])

    # 1 時間当たりの暖房設備の基準一次エネルギー消費量
    E_SH = calc_E_SH(spec['type'], spec['tatekata'], spec['region'], spec['sol_region'], spec['A_A'],
                     spec['A_MR'], spec['A_OR'], spec['ENV'], spec['mode_H'], spec['mode_C'], spec['NV_MR'], spec['NV_OR'], spec['H_MR'], spec['H_OR'])

    # 1 時間当たりの冷房設備の基準一次エネルギー消費量
    E_SC = calc_E_SC(spec['type'], spec['tatekata'], spec['region'], spec['A_A'], spec['A_MR'],
                     spec['A_OR'], spec['ENV'], spec['mode_C'], spec['mode_H'], spec['H_MR'], spec['H_OR'], spec['TS'], spec['HEX'],
                     spec['sol_region'], spec['NV_MR'], spec['NV_OR'])

    # 1年当たりの給湯設備の基準一次エネルギー消費量
    E_SW = calc_E_SW(spec['region'], spec['A_A'], spec['HW'])

    # 1年当たりの照明設備の基準一次エネルギー消費量
    E_SL = calc_E_SL(spec['A_A'], spec['A_MR'], spec['A_OR'])

    # 1年当たりのその他の基準一次エネルギー消費量
    E_SM = calc_E_SM(spec['A_A'])

    # 合計
    E_ST = get_E_ST(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM, spec['reference'], spec['type'])

    return E_ST, E_SH, E_SC, E_SV, E_SL, E_SW, E_SM

# 基準一次エネルギー消費量（GJ/年）
def get_E_ST(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM, reference, type):
    """基準一次エネルギー消費量（GJ/年）の取得

    Args:
      E_SH(float): 1 時間当たりの暖房設備の基準一次エネルギー消費量
      E_SC(float): 1 時間当たりの冷房設備の基準一次エネルギー消費量
      E_SV(float): 1 時間当たりの換気設備の基準一次エネルギー消費量
      E_SL(float): 1 時間当たりの照明設備の基準一次エネルギー消費量
      E_SW(float): 1 時間当たりの給湯設備の基準一次エネルギー消費量
      E_SM(float): 1 時間当たりのその他の基準一次エネルギー消費量
      reference(dict): 基準値計算仕様
      type(str): 住宅タイプ

    Returns:
      dict: 基準一次エネルギー消費量（GJ/年）

    """
    # 小数点以下一位未満の端数があるときはこれを切り上げる

    E_star_ST = get_E_ST_star(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM, reference, type)

    E_ST_gn_p = None
    E_ST_gn_e = None
    E_ST_indc_p = None
    E_ST_indc_e = None
    E_ST_lcb = None
    E_ST_rb = None
    E_ST_trad_p = None
    E_ST_trad_e = None

    if type == '一般住宅':
        # 建築物エネルギー消費性能基準（平成 28 年 4 月 1 日時点で現存しない住宅）
        E_ST_gn_p = calc_E_ST_GJ(E_star_ST['E_star_ST_gn_p'])
        # 建築物エネルギー消費性能基準（平成 28 年 4 月 1 日時点で現存する住宅）
        E_ST_gn_e = calc_E_ST_GJ(E_star_ST['E_star_ST_gn_e'])
        # 建築物エネルギー消費性能誘導基準（平成 28 年 4 月 1 日時点で現存しない住宅）
        E_ST_indc_p = calc_E_ST_GJ(E_star_ST['E_star_ST_indc_p'])
        # 建築物エネルギー消費性能誘導基準（平成 28 年 4 月 1 日時点で現存する住宅）
        E_ST_indc_e = calc_E_ST_GJ(E_star_ST['E_star_ST_indc_e'])
        # 低炭素建築物の認定基準
        E_ST_lcb = calc_E_ST_GJ(E_star_ST['E_star_ST_lcb'])
    elif type == '事業主基準':
        # 特定建築主基準
        E_ST_rb = calc_E_ST_GJ(E_star_ST['E_star_ST_rb'])
    elif type == '行政庁認定住宅':
        # 気候風土適応住宅 平成 28 年 4 月 1 日時点で現存しない住宅
        E_ST_trad_p = calc_E_ST_GJ(E_star_ST['E_star_ST_trad_p'])
        # 気候風土適応住宅 平成 28 年 4 月 1 日時点で現存する住宅
        E_ST_trad_e = calc_E_ST_GJ(E_star_ST['E_star_ST_trad_e'])
    else:
        raise ValueError('type')

    E_ST = {
        'E_ST_gn_p': E_ST_gn_p,
        'E_ST_gn_e': E_ST_gn_e,
        'E_ST_indc_p': E_ST_indc_p,
        'E_ST_indc_e': E_ST_indc_e,
        'E_ST_lcb': E_ST_lcb,
        'E_ST_rb': E_ST_rb,
        'E_ST_trad_p': E_ST_trad_p,
        'E_ST_trad_e': E_ST_trad_e
    }

    return E_ST

def calc_E_ST_GJ(E_star_ST):
    """基準一次エネルギー消費量（GJ/年）の計算 (2)

    Args:
      E_star_ST(float): 基準一次エネルギー消費量（J/年）

    Returns:
      float: 基準一次エネルギー消費量（GJ/年）

    """

    # 小数点以下一位未満の端数があるときはこれを切り上げる
    return ceil(E_star_ST / 100) / 10  # (2)


# ============================================================================
# 10. BEI(Building Energy Index）
# ============================================================================

# BEI(Building Energy Index）
def calc_BEI(E_H, E_C, E_V, E_L, E_W, E_S, E_M, E_SH, E_SC, E_SV, E_SL, E_SW, E_SM, reference, type):
    """BEI(Building Energy Index） の取得

    Args:
      E_H(float): 1 年当たりの暖房設備の設計一次エネルギー消費量（MJ/年）
      E_C(float): 1 年当たりの冷房設備の設計一次エネルギー消費量（MJ/年）
      E_V(float): 1 年当たりの機械換気設備の設計一次エネルギー消費量（MJ/年）
      E_L(float): 1 年当たりの照明設備の設計一次エネルギー消費量（MJ/年）
      E_W(float): 1 年当たりの給湯設備（コージェネレーション設備を含む）の設計一次エネルギー消費量（MJ/年）
      E_S(float): 1 年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量（MJ/年）
      E_M(float): 1 年当たりのその他の設計一次エネルギー消費量（MJ/年）
      E_SH(float): 1 年当たりの暖房設備の基準一次エネルギー消費量（MJ/年）
      E_SC(float): 1 年当たりの冷房設備の基準一次エネルギー消費量（MJ/年）
      E_SV(float): 1 年当たりの機械換気設備の基準一次エネルギー消費量（MJ/年）
      E_SL(float): 1 年当たりの照明設備の基準一次エネルギー消費量（MJ/年）
      E_SW(float): 1 年当たりの給湯設備（コージェネレーション設備を含む）の基準一次エネルギー消費量（MJ/年）
      E_SM(float): 1 年当たりのその他の基準一次エネルギー消費量（MJ/年）
      reference(dict): 基準値計算仕様
      type(str): 住宅タイプ

    Returns:
      float: BEI(Building Energy Index）

    """
    # 設計一次エネルギー消費量（MJ/年）
    E_star_T = get_E_T_star(E_H, E_C, E_V, E_L, E_W, E_S, E_M)

    # BEIで用いるE_star_STは'建築物エネルギー消費性能基準（平成 28 年 4 月 1 日時点で現存しない住宅）'とする
    type = '一般住宅'
    # 基準一次エネルギー消費量（MJ/年）
    E_star_ST = get_E_ST_star(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM, reference, type)
    E_star_ST_gn_p = E_star_ST['E_star_ST_gn_p']

    # 小数点以下一位未満の端数があるときはこれを切り上げる
    E_T_dash = ceil((E_star_T - E_M) / 100) / 10  # (3b)
    E_ST_dash = ceil((E_star_ST_gn_p - E_SM) / 100) / 10  # (3c)
    # 小数点以下二位未満の端数があるときはこれを切り上げる
    BEI = ceil(E_T_dash / E_ST_dash * 100) / 100  # (3a)
    return BEI