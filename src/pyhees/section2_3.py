# ============================================================================
# 第二章 単位住戸の一次エネルギー消費量
# 第三節 基準一次エネルギー消費量
# Ver.06（エネルギー消費性能計算プログラム（住宅版）Ver.02～）
# ============================================================================

from math import floor
from pyhees.section2_2 import calc_E_C, calc_E_H
import pyhees.section2_4 as section2_4
import pyhees.section2_5 as section2_5
import pyhees.section2_8 as section2_8
from pyhees.section4_1 import calc_cooling_load, calc_heating_load, get_virtual_heating_devices, calc_heating_mode


def get_E_ST_star(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM, reference, type):
    """基準一次エネルギー消費量

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
      float: 基準一次エネルギー消費量

    """

    E_star_ST_gn_p = None
    E_star_ST_gn_e = None
    E_star_ST_indc_p = None
    E_star_ST_indc_e = None
    E_star_ST_lcb = None
    E_star_ST_rb = None
    E_star_ST_trad_p = None
    E_star_ST_trad_e = None

    if type == '一般住宅':
        # 建築物エネルギー消費性能基準（平成 28 年 4 月 1 日時点で現存しない住宅） (1)
        E_star_ST_gn_p = E_SH + E_SC + E_SV + E_SL + E_SW + E_SM
        # 建築物エネルギー消費性能基準（平成 28 年 4 月 1 日時点で現存する住宅） (2)
        E_star_ST_gn_e = (E_SH + E_SC + E_SV + E_SL + E_SW) * 1.1 + E_SM
        # 建築物エネルギー消費性能誘導基準（平成 28 年 4 月 1 日時点で現存しない住宅） (3)
        E_star_ST_indc_p = (E_SH + E_SC + E_SV + E_SL + E_SW) * 0.9 + E_SM
        # 建築物エネルギー消費性能誘導基準（平成 28 年 4 月 1 日時点で現存する住宅） (4)
        E_star_ST_indc_e = E_SH + E_SC + E_SV + E_SL + E_SW + E_SM
        # 低炭素建築物の認定基準
        E_star_ST_lcb = section2_8.get_E_ST_star(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)
    elif type == '事業主基準':
        # 特定建築主基準
        E_star_ST_rb = section2_4.get_E_ST_star(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM, reference)
    elif type == '行政庁認定住宅':
        # 気候風土適応住宅
        E_star_ST_trad_p, E_star_ST_trad_e = section2_5.get_E_ST_star(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)
    else:
        raise ValueError('type')

    E_star_ST = {
        'E_star_ST_gn_p': E_star_ST_gn_p,
        'E_star_ST_gn_e': E_star_ST_gn_e,
        'E_star_ST_indc_p': E_star_ST_indc_p,
        'E_star_ST_indc_e': E_star_ST_indc_e,
        'E_star_ST_lcb': E_star_ST_lcb,
        'E_star_ST_rb': E_star_ST_rb,
        'E_star_ST_trad_p': E_star_ST_trad_p,
        'E_star_ST_trad_e': E_star_ST_trad_e
    }

    return E_star_ST


# ============================================================================
# 6. 暖房設備の基準一次エネルギー消費量
# ============================================================================


def calc_heating_refernce_spec(region, mode_H, H_MR, H_OR):
    """暖房設備の基準一次エネルギー消費量

    Args:
      region(int): 省エネルギー地域区分
      mode_H(str): 暖房方式
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様

    Returns:
      tuple: mode_H, H_A, H_MR, H_OR, H_HS, mode_MR, mode_OR (暖房方式及び運転方法の区分)

    Raises:
      ValueError: mode_MRが「ろ」かつregion が 1-8 でない場合に発生
      ValueError: mode_MRが「は」かつregion が 1-8 でない場合に発生
      ValueError: mode_MRが「ろ」または「は」以外の場合に発生
      ValueError: mode_ORが「ろ」かつregion が 1-8 でない場合に発生
      ValueError: mode_ORが「は」かつregion が 1-8 でない場合に発生
      ValueError: mode_ORが「ろ」または「は」以外の場合に発生
      ValueError: mode_Hが「住戸全体を連続的に暖房する方式」または「」

    """
    if region == 8:
        return None, None, None, None, None, None, None

    if mode_H == '住戸全体を連続的に暖房する方式':
        H_A = {
            'type': 'ダクト式セントラル空調機',
            'duct_insulation': '全てもしくは一部が断熱区画外である',
            'VAV': False,
            'general_ventilation': True,
            'EquipmentSpec': '入力しない'
        }
        H_MR = None
        H_OR = None
        H_HS = None
    elif mode_H == '居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合' or \
            mode_H == '設置しない' or mode_H is None:

        # 実質的な暖房機器の仕様を取得
        spec_MR, spec_OR = get_virtual_heating_devices(region, H_MR, H_OR)
        if spec_MR is None and spec_OR is None:
            return None, None, None, None, None, None, None

        # 暖房方式及び運転方法の区分
        mode_MR, mode_OR = calc_heating_mode(region=region, H_MR=spec_MR, H_OR=spec_OR)

        H_A = None
        H_HS = None

        if mode_MR == 'ろ':
            if region in [1,2,3,4]:
                H_MR = {
                    'type': '温水暖房用パネルラジエーター',
                }
                H_HS = {
                    'type': '石油従来型温水暖房機',
                    'e_rtd_hs': 0.83,
                    'pipe_insulation': True,
                    'underfloor_pipe_insulation': False
                }
            elif region in [5,6,7]:
                H_MR = {
                    'type': '温水暖房用パネルラジエーター',
                }
                H_HS = {
                    'type': 'ガス従来型温水暖房機',
                    'e_rtd_hs': 0.825,
                    'pipe_insulation': True,
                    'underfloor_pipe_insulation': False
                }
            else:
                raise ValueError(region)
        elif mode_MR == 'は':
            if region in [1,2,3,4]:
                H_MR = {
                    'type': 'FF暖房機',
                    'e_rtd': 0.86
                }
            elif region in [5,6,7]:
                H_MR = {
                    'type': 'ルームエアコンディショナー',
                    'e_class': 'ろ',
                    'dualcompressor': False
                }
            else:
                raise ValueError(region)
        else:
            raise ValueError(mode_MR)

        if mode_OR == 'ろ':
            if region in [1,2,3,4]:
                H_OR = {
                    'type': '温水暖房用パネルラジエーター',
                }
                H_HS = {
                    'type': '石油従来型温水暖房機',
                    'e_rtd_hs': 0.83,
                    'pipe_insulation': True,
                    'underfloor_pipe_insulation': False
                }
            elif region in [5,6,7]:
                H_OR = {
                    'type': '温水暖房用パネルラジエーター',
                }
                H_HS = {
                    'type': 'ガス従来型温水暖房機',
                    'e_rtd_hs': 0.825,
                    'pipe_insulation': True,
                    'underfloor_pipe_insulation': False
                }
            else:
                raise ValueError(region)
        elif mode_OR == 'は':
            if region in [1,2,3,4]:
                H_OR = {
                    'type': 'FF暖房機',
                    'e_rtd': 0.86
                }
            elif region in [5,6,7]:
                H_OR = {
                    'type': 'ルームエアコンディショナー',
                    'e_class': 'ろ',
                    'dualcompressor': False
                }
            else:
                raise ValueError(region)
        elif mode_OR is None:
            pass
        else:
            raise ValueError(mode_OR)
    else:
        raise ValueError(mode_H)



    if mode_H is None:
        mode_H = '居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合'

    # 暖房方式及び運転方法の区分
    mode_MR, mode_OR = calc_heating_mode(region=region, H_MR=H_MR, H_OR=H_OR)

    return mode_H, H_A, H_MR, H_OR, H_HS, mode_MR, mode_OR


def calc_env_reference_spec(type, tatekata, region, A_A, ENV):
    """熱損失係数, 熱取得率（暖房）, 熱取得率（冷房）を計算する

    Args:
      type(str): description]
      tatekata(str): 建て方
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      ENV(dict): description]

    Returns:
      tuple: 熱損失係数, 熱取得率（暖房）, 熱取得率（冷房）

    """
    from pyhees.section3_1 import get_Q

    if ENV is None:
        return None, None, None

    if type != '行政庁認定住宅':
        from pyhees.section2_3_a import get_U_A, get_etr_A_H, get_etr_A_C

        U_A = get_U_A(tatekata, region)
        etr_A_H = get_etr_A_H(tatekata, region)
        etr_A_C = get_etr_A_C(tatekata, region)

        from pyhees.section3_2 import get_Q_dash, get_mu_H, get_mu_C

        if ENV['method'] == '当該住宅の外皮面積の合計を用いて評価する':
            A_env = ENV['A_env']
            r_env = A_env / A_A  # 床面積の合計に対する外皮の部位の面積の合計の比
        elif ENV['method'] == '簡易的に求めた外皮面積の合計を用いて評価する':
            from pyhees.section3_2_9 import get_A_dash_env, get_A_dash_A, get_r_env

            U_spec = ENV['U_spec']
            floor_bath_insulation = U_spec['floor_bath_insulation']

            A_dash_env = get_A_dash_env(ENV['house_insulation_type'], floor_bath_insulation)
            A_dash_A = get_A_dash_A()
            r_env = get_r_env(A_dash_env, A_dash_A)
        elif ENV['method'] == '当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法':
            from pyhees.section3_2_9 import get_A_dash_env, get_A_dash_A, get_r_env
            from pyhees.section3_2 import calc_insulation_performance

            U_spec = ENV['U_spec']
            floor_bath_insulation = U_spec['floor_bath_insulation']

            _, _, _, _, _, _, _, house_insulation_type = calc_insulation_performance(**ENV)
            A_dash_env = get_A_dash_env(house_insulation_type, floor_bath_insulation)
            A_dash_A = get_A_dash_A()
            r_env = get_r_env(A_dash_env, A_dash_A)

        Q_dash = get_Q_dash(U_A, r_env)

        mu_H = get_mu_H(etr_A_H, r_env)
        mu_C = get_mu_C(etr_A_C, r_env)
    else:
        from pyhees.section3_2 import calc_insulation_performance
        U_A, r_env, eta_A_H, eta_A_C, Q_dash, mu_H, mu_C,_ = calc_insulation_performance(**ENV)

    Q = get_Q(Q_dash)

    return Q, mu_H, mu_C

def calc_E_SH(type, tatekata, region, sol_region, A_A, A_MR, A_OR, ENV, mode_H, mode_C, NV_MR, NV_OR, H_MR, H_OR):
    """暖房設備の設計一次エネルギー消費量

    Args:
      type(str): description]
      tatekata(str): 建て方
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      ENV(dict): description]
      mode_H(str): 暖房方式
      mode_C(str): 冷房方式
      NV_MR(float): 主たる居室における通風の利用における相当換気回数
      NV_OR(float): その他の居室における通風の利用における相当換気回数
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様

    Returns:
      float: 暖房設備の設計一次エネルギー消費量

    """
    # 暖房基準値計算用仕様の取得
    mode_H, H_A, H_MR, H_OR, H_HS, mode_MR, mode_OR = calc_heating_refernce_spec(region, mode_H, H_MR, H_OR)

    # 外皮の基準値計算用仕様の取得
    Q, eta_H, eta_C = calc_env_reference_spec(type, tatekata, region, A_A, ENV)

    # 暖房負荷の取得
    L_T_H_d_t_i, L_dash_H_R_d_t_i = calc_heating_load(
        region, sol_region,
        A_A, A_MR, A_OR,
        Q, eta_H, eta_C, NV_MR, NV_OR, None, None, None,
        None, mode_H, mode_C,
        H_MR, H_OR, mode_MR, mode_OR, None)

    L_CS_d_t_i, L_CL_d_t_i = calc_cooling_load(
        region, A_A, A_MR, A_OR,
        Q, eta_H, eta_C, NV_MR, NV_OR, None, None,
        mode_C, mode_H, mode_MR, mode_OR, None, None)

    if (ENV != None) and ('A_env' in ENV):
        A_env = ENV['A_env']
    else:
        A_env = None

    E_SH = calc_E_H(region, sol_region, A_A, A_MR, A_OR, A_env, eta_H, eta_C, Q, mode_H,
                  H_A, H_MR, H_OR, H_HS, mode_MR, mode_OR, None, None,
                  None, L_T_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i)

    return E_SH


# ============================================================================
# 7. 冷房設備の基準一次エネルギー消費量
# ============================================================================

def calc_E_SC(type, tatekata, region, A_A, A_MR, A_OR, ENV, mode_C, mode_H, H_MR, H_OR, TS, HEX,
              sol_region, NV_MR, NV_OR):
    """1 年当たりの冷房設備の設計一次エネルギー消費量

    Args:
      type(str): description]
      tatekata(str): 建て方
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      ENV(dict): description]
      mode_C(str): 冷房方式
      mode_H(str): 暖房方式
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様
      TS(bool): 蓄熱の利用
      HEX(dict): 熱交換器型設備仕様辞書
      sol_region: param NV_MR:
      NV_OR: returns: 1 年当たりの冷房設備の設計一次エネルギー消費量
      NV_MR: 

    Returns:
      float: 1 年当たりの冷房設備の設計一次エネルギー消費量

    Raises:
      ValueError: mode_C が　「住戸全体を連続的に冷房する方式」または「居室のみを冷房する方式」でない場合に発生する

    """
    if ENV is None:
        return 0.0

    if mode_C == '住戸全体を連続的に冷房する方式':
        C_A = {
            'type': 'ダクト式セントラル空調機',
            'duct_insulation': '全てもしくは一部が断熱区画外である',
            'VAV': False,
            'general_ventilation': True,
            'EquipmentSpec': '入力しない'
        }
        C_MR = None
        C_OR = None
    elif mode_C == '居室のみを冷房する方式' or mode_C == '設置しない' or mode_C is None:
        C_A = None
        C_MR = {
            'type': 'ルームエアコンディショナー',
            'e_class': 'ろ',
            'dualcompressor': False
        }
        C_OR = {
            'type': 'ルームエアコンディショナー',
            'e_class': 'ろ',
            'dualcompressor': False
        }
    else:
        raise ValueError(mode_C)

    if mode_C is None:
        mode_C = '居室のみを冷房する方式'

    # 暖房基準値計算用仕様の取得
    mode_H, H_A, H_MR, H_OR, H_HS, mode_MR, mode_OR = calc_heating_refernce_spec(region, mode_H, H_MR, H_OR)

    # 外皮の基準値計算用仕様の取得
    Q, eta_H, eta_C = calc_env_reference_spec(type, tatekata, region, A_A, ENV)

    # 暖房負荷の取得
    L_T_H_d_t_i, L_dash_H_R_d_t_i = calc_heating_load(
        region, sol_region,
        A_A, A_MR, A_OR,
        Q, eta_H, eta_C, NV_MR, NV_OR, None, None, None,
        None, mode_H, mode_C,
        H_MR, H_OR, mode_MR, mode_OR, None)

    # 冷房負荷の計算
    L_CS_d_t, L_CL_d_t = calc_cooling_load(
        region=region,
        A_A=A_A,
        A_MR=A_MR,
        A_OR=A_OR,
        Q=Q,
        mu_C=eta_C,
        mu_H=eta_H,
        # 通風なし
        NV_MR=0,
        NV_OR=0,
        # 床下換気なし
        r_A_ufvnt=None,
        underfloor_insulation=None,
        mode_C=mode_C,
        mode_H=mode_H,
        mode_MR=mode_MR,
        mode_OR=mode_OR,
        TS=TS,
        HEX=HEX
    )

    if 'A_env' in ENV:
        A_env = ENV['A_env']
    else:
        A_env = None

    # 1 年当たりの冷房設備の設計一次エネルギー消費量
    E_SC = calc_E_C(region, A_A, A_MR, A_OR, A_env, eta_H, eta_C, Q, C_A, C_MR, C_OR, L_T_H_d_t_i, L_CS_d_t, L_CL_d_t, mode_C)

    return E_SC


# ============================================================================
# 8. 機械換気設備の基準一次エネルギー消費量
# ============================================================================


# 1年あたりの機械換気設備の基準一次エネルギー消費量 (6)
def calc_E_SV(A_A):
    """1年あたりの機械換気設備の基準一次エネルギー消費量 (6)

    Args:
      A_A(float): 床面積の合計(付録Aによる定まる値) (m2)

    Returns:
      float: 1年あたりの機械換気設備の基準一次エネルギー消費量 (MJ/年)

    """
    # 係数 a_SV, b_SV
    a_SV, b_SV = get_table3_coeff(A_A)

    # 1年あたりの機械換気設備の基準一次エネルギー消費量 (9)
    E_SV = get_E_SV(A_A, a_SV, b_SV)

    return E_SV


# 1年あたりの機械換気設備の基準一次エネルギー消費量 (6)
def get_E_SV(A_A, a_SV, b_SV):
    """1年あたりの機械換気設備の基準一次エネルギー消費量 (6)

    Args:
      A_A: 床面積の合計 (m2)
      a_SV: 係数 (MJ/(m2・年))
      b_SV: 係数 (MJ/年)

    Returns:
      1年あたりの機械換気設備の基準一次エネルギー消費量 (MJ/年)

    """
    E_SV = a_SV * A_A + b_SV
    return E_SV


def get_table3_coeff(A_A):
    """その他の一次エネルギー消費量の算出に用いる表3の係数を取得

    Args:
      A_A(float): 床面積の合計 (m2)

    Returns:
      tuple: 係数 a_SV, b_SV

    """

    # その他の一次エネルギー消費量の算出に用いる係数
    table_3 = [
        (33, 38, 33),
        (129, -21, 579)
    ]
    if A_A < 30:
        index = 0
    elif A_A < 120:
        index = 1
    else:
        index = 2

    a_SV = table_3[0][index]
    b_SV = table_3[1][index]

    return a_SV, b_SV



# ============================================================================
# 9. 照明の基準一次エネルギー消費量
# ============================================================================

# 1年あたりの照明の基準一次エネルギー消費量 (7)
def calc_E_SL(A_A, A_MR, A_OR):
    """1年あたりの照明の基準一次エネルギー消費量 (7)

    Args:
      A_A(float): 床面積の合計(付録Aによる定まる値) (m2)
      A_MR(float): 主たる居室の床面積の合計(付録Aによる定まる値) (m2)
      A_OR(float): その他の居室の床面積の合計(付録Aによる定まる値) (m2)

    Returns:
      float: 1年あたりの照明の基準一次エネルギー消費量 (MJ/年)

    """
    E_SL = get_E_SL(A_A, A_MR, A_OR)
    return E_SL


# 1年あたりの照明の基準一次エネルギー消費量 (7)
def get_E_SL(A_A, A_MR, A_OR):
    """1年あたりの照明の基準一次エネルギー消費量 (7)

    Args:
      A_A(float): 床面積の合計(付録Aによる定まる値) (m2)
      A_MR(float): 主たる居室の床面積の合計(付録Aによる定まる値) (m2)
      A_OR(float): その他の居室の床面積の合計(付録Aによる定まる値) (m2)

    Returns:
      float: 1年あたりの照明の基準一次エネルギー消費量 (MJ/年)

    """
    E_SL = 31 * A_A + 169 * A_MR + 39 * A_OR
    return E_SL


# ============================================================================
# 10. 給湯設備及びコージェネレーション設備の基準一次エネルギー消費量
# ============================================================================

# 1年当たりの給湯設備の設計一次エネルギー消費量 (8)
def calc_E_SW(region, A_A, HW):
    """1年当たりの給湯設備の設計一次エネルギー消費量 (8)

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      HW(dict): 給湯機の仕様

    Returns:
      float: 1年当たりの給湯設備の設計一次エネルギー消費量 (8)

    """
    if HW is None or HW['hw_type'] is None:
        return 0.0
    else:
        a_SW, b_SW = get_table4_coeff(region, A_A, HW['has_bath'])
        E_SW = get_E_SW(A_A, a_SW, b_SW)
        return E_SW


# 1年当たりの給湯設備の設計一次エネルギー消費量 (8)
def get_E_SW(A_A, a_SW, b_SW):
    """1年当たりの給湯設備の設計一次エネルギー消費量 (8)

    Args:
      A_A(float): 床面積の合計 (m2)
      a_SW(float): 表4 給湯設備の一次エネルギー消費量の算出に用いる係数
      b_SW(float): 表4 給湯設備の一次エネルギー消費量の算出に用いる係数

    Returns:
      float: 1年当たりの給湯設備の設計一次エネルギー消費量 (8)

    """
    if a_SW is None:
        E_SW = b_SW
    else:
        E_SW = a_SW * A_A + b_SW
    return E_SW


def get_table4_coeff(region, A_A, has_bath):
    """表4 給湯設備の一次エネルギー消費量の算出に用いる係数

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      has_bath(bool): バスが存在するかどうか

    Returns:
      tuple: 給湯設備の一次エネルギー消費量の算出に用いる係数a_SW, b_SW

    """

    # 表4 給湯設備の一次エネルギー消費量の算出に用いる係数
    table_4 = [
        (None, 234, 307, 109, None),
        (11946, 4926, 546, 18366, 31446),
        (None, 32, 78, 15, None),
        (4835, 3875, 1115, 6785, 8585),
        (None, 228, 300, 107, None),
        (11696, 4856, 536, 17906, 30746),
        (None, 32, 77, 15, None),
        (4742, 3782, 1082, 6662, 8462),
        (None, 212, 280, 100, None),
        (10892, 4532, 452, 16652, 28652),
        (None, 30, 72, 14, None),
        (4442, 3542, 1022, 6242, 7922),
        (None, 205, 272, 97, None),
        (10575, 4425, 405, 16155, 27795),
        (None, 29, 70, 13, None),
        (4321, 3451, 991, 6121, 7681),
        (None, 200, 276, 103, None),
        (10440, 4440, -120, 15450, 27810),
        (None, 29, 71, 14, None),
        (4165, 3295, 775, 5905, 7585),
        (None, 181, 249, 93, None),
        (9401, 3971, -109, 13931, 25091),
        (None, 26, 64, 12, None),
        (3755, 2975, 695, 5375, 6815),
        (None, 165, 227, 85, None),
        (8499, 3549, -171, 12609, 22809),
        (None, 23, 57, 11, None),
        (3402, 2712, 672, 4812, 6132),
        (None, 130, 178, 67, None),
        (6672, 2772, -108, 9882, 17922),
        (None, 18, 45, 9, None),
        (2679, 2139, 519, 3759, 4839)
    ]

    row_index = (region - 1) * 4 + (0 if has_bath else 2)
    column_index = min(4, floor(A_A / 30))
    a_SW = table_4[row_index][column_index]
    b_SW = table_4[row_index + 1][column_index]
    return a_SW, b_SW


# ============================================================================
# 11. その他の基準一次エネルギー消費量
# ============================================================================

# 1年あたりのその他の基準一次エネルギー消費量 (9)
def calc_E_SM(A_A):
    """1年あたりのその他の基準一次エネルギー消費量 (9)

    Args:
      A_A(float): 床面積の合計(付録Aによる定まる値) (m2)

    Returns:
      float: 1年あたりのその他の基準一次エネルギー消費量 (MJ/年)

    """
    # 係数 a_SM, b_SM
    a_SM, b_SM = get_table5_coeff(A_A)

    # 1年あたりのその他の基準一次エネルギー消費量 (9)
    E_SM = get_E_SM(A_A, a_SM, b_SM)

    return E_SM


# 1年あたりのその他の基準一次エネルギー消費量 (9)
def get_E_SM(A_A, a_SM, b_SM):
    """1年あたりのその他の基準一次エネルギー消費量 (9)

    Args:
      A_A(float): 床面積の合計 (m2)
      a_SM(float): 係数 (MJ/(m2・年))
      b_SM(float): 係数 (MJ/年)

    Returns:
      float: 1年あたりのその他の基準一次エネルギー消費量 (MJ/年)

    """
    E_SM = a_SM * A_A + b_SM
    return E_SM


def get_table5_coeff(A_A):
    """その他の一次エネルギー消費量の算出に用いる係数

    Args:
      A_A(float): 床面積の合計 (m2)

    Returns:
      tuple: 係数 a_SM, b_SM

    """
    # その他の一次エネルギー消費量の算出に用いる係数
    table_5 = [
        (0, 87.63, 166.71, 47.64, 0),
        (12181.13, 9552.23, 4807.43, 15523.73, 21240.53)
    ]

    index = min(4, floor(A_A / 30))
    a_SM = table_5[0][index]
    b_SM = table_5[1][index]
    return a_SM, b_SM
