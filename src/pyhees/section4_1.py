# ============================================================================
# 第四章 暖冷房設備
# 第一節 全般
# Ver.06（エネルギー消費性能計算プログラム（住宅版）Ver.0205～）
# ============================================================================

############### 他モジュールの参照 ###############

import numpy as np

import pyhees.section3_1 as ld
from pyhees.section3_1_a import calc_etr_dash_t

from pyhees.section4_1_a import calc_heating_mode, get_default_heating_spec, get_default_heatsource

import pyhees.section9_3 as ass

# 設置なしの場合の設定
from pyhees.section4_1_b import get_default_cooling_spec

# ダクト式セントラル空調機
import pyhees.section4_2 as dc
import pyhees.section4_2_a as dc_a
import pyhees.section4_2_b as dc_spec

# エアーコンディショナー
import pyhees.section4_3 as rac
import pyhees.section4_3_a as rac_spec

# FF暖房
import pyhees.section4_4 as ff
import pyhees.section4_4_a as ff_spec

# 電気ヒーター床暖房
import pyhees.section4_5 as eheater
import pyhees.section4_5_a as eheater_spec

# 電気蓄熱暖房
import pyhees.section4_6 as ets
import pyhees.section4_6_a as ets_spec

# 温水暖房
import pyhees.section4_7 as hwh

# 温水暖房用パネルラジエーター
import pyhees.section4_7_j as rad_panel

# 温水暖房用ファンコンベクター
import pyhees.section4_7_k as rad_fanc

# 温水暖房用床暖房
import pyhees.section4_7_l as rad_floor

# ルームエアコンディショナー付温水床暖房
import pyhees.section4_8 as racfh
import pyhees.section4_8_a as racfh_spec


###################################################
# 6. 暖房設備の一次エネルギー消費量及び処理負荷と未処理負荷
###################################################

# ===================================================
# 6.1 処理負荷及び未処理負荷
# ===================================================

def calc_heating_load(region, sol_region, A_A, A_MR, A_OR, Q, mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX, underfloor_insulation, mode_H, mode_C,
                      spec_MR, spec_OR, mode_MR, mode_OR, SHC):
    """暖房負荷の取得

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      NV_MR(float): 主たる居室における通風の利用における相当換気回数
      NV_OR(float): その他の居室における通風の利用における相当換気回数
      TS(bool): 蓄熱の利用
      r_A_ufvnt(float): 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
      HEX(dict): 熱交換器型設備仕様辞書
      underfloor_insulation(bool): 床下空間が断熱空間内である場合はTrue
      mode_H(str): 暖房方式
      mode_C(str): 冷房方式
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      SHC(dict): 集熱式太陽熱利用設備の仕様

    Returns:
      tuple(ndarray, ndarray): 暖房区画i=1-5それぞれの暖房負荷, 標準住戸の暖冷房区画iの負荷補正前の暖房負荷 (MJ/h))

    """
    if region == 8:
        return np.zeros((12, 24 * 365)), np.zeros((12, 24 * 365))

    if mode_H == '住戸全体を連続的に暖房する方式' or \
            mode_H == '居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合' or \
            mode_H == '設置しない':
        # 暖房区画i=1-5それぞれの暖房負荷
        L_T_H_d_t_i, L_dash_H_R_d_t_i = calc_L_H_d_t(region, sol_region, A_A, A_MR, A_OR, mode_H, mode_C, spec_MR, spec_OR,
                                                     mode_MR, mode_OR, Q,
                                                     mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX, SHC, underfloor_insulation)
        return L_T_H_d_t_i, L_dash_H_R_d_t_i
    elif mode_H is None:
        return None, None
    else:
        raise ValueError(mode_H)


# ---------------------------------------------------
# 6.1.1 住戸全体を連続的に暖房する方式 
# ---------------------------------------------------

def calc_Q_UT_H_A_d_t(A_A, A_MR, A_OR, A_env, mu_H, mu_C, q_hs_rtd_H, q_hs_rtd_C, V_hs_dsgn_H, V_hs_dsgn_C, Q,
                     VAV, general_ventilation, duct_insulation, region, L_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i):
    """住宅全体を連続的に暖房する方式おける暖房設備の未処理暖房負荷 (1)

    Args:
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      A_env(float): 外皮の部位の面積の合計 (m2)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      q_hs_rtd_H(float): 熱源機の暖房時の定格出力 (MJ/h)
      q_hs_rtd_C(float): 熱源機の冷房時の定格出力 (MJ/h)
      V_hs_dsgn_H(float): 暖房時の設計風量（m3/h）
      V_hs_dsgn_C(float): 冷房時の設計風量（m3/h）
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      VAV(bool): VAV有無
      general_ventilation(bool): 全版換気の機能の有無
      duct_insulation(str): ダクトが通過する空間
      region(int): 省エネルギー地域区分
      L_H_d_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの1時間当たりの暖房負荷（MJ/h）
      L_CS_d_t_i(ndarray): 暖冷房区画iの 1 時間当たりの冷房顕熱負荷
      L_CL_d_t_i(ndarray): 暖冷房区画iの 1 時間当たりの冷房潜熱負荷

    Returns:
      ndarray: 住戸全体を連続的に暖房する方式における1時間当たりの暖房設備の未処理暖房負荷(MJ/h)

    """
    _, Q_UT_H_d_t_i, _, _, _, _, _, _, _, _, _ = dc.calc_Q_UT_A(A_A, A_MR, A_OR, A_env, mu_H, mu_C, q_hs_rtd_H, q_hs_rtd_C,
                                          V_hs_dsgn_H, V_hs_dsgn_C, Q, VAV, general_ventilation,
                                          duct_insulation, region, L_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i)

    Q_UT_H_A_d_t = np.sum(Q_UT_H_d_t_i, axis=0)

    return Q_UT_H_A_d_t


# ---------------------------------------------------
# 6.1.2 居室のみを暖房する方式 
# ---------------------------------------------------

# # 主たる居室に設置された暖房設備の処理暖房負荷 (3a)
# def get_Q_T_H_MR_d_t():
#     return get_Q_T_H_d_t_i(i=1)
#
#
# # その他の居室に設置された暖房設備の処理暖房負荷 (4a)
# def get_Q_T_H_OR_d_t():
#     return np.sum([get_Q_T_H_d_t_i(i) for i in range(2, 6)], axis=0)


def calc_Q_UT_H_MR_d_t(region, A_A, A_MR, A_OR, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG, L_T_H_d_t):
    """主たる居室に設置された暖房設備の未処理暖房負荷 (2b)

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      L_T_H_d_t(ndarray): 暖房区画の暖房負荷

    Returns:
      ndarray: 住戸全体を連続的に暖房する方式における1時間当たりの主たる居室の暖房設備の未処理暖房負荷(MJ/h)

    """
    if spec_MR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）']:
        # 主たる居室で温水床暖房とエアコンを併用する場合か否か
        racfh_combed = spec_MR['type'] == '温水床暖房（併用運転に対応）'

        # 送水温度の決定
        Theta_SW_hs_op = hwh.get_Theta_SW_hs_op(spec_HS['type'], HW, CG, racfh_combed)
        rad_list = hwh.get_rad_list(spec_MR, spec_OR)
        p_hs_d_t = hwh.calc_p_hs_d_t(Theta_SW_hs_op, rad_list, L_T_H_d_t, A_A, A_MR, A_OR, region, mode_MR, mode_OR)
        Theta_SW_d_t = hwh.get_Theta_SW_d_t(Theta_SW_hs_op, p_hs_d_t)

        if spec_MR['type'] == '温水暖房用パネルラジエーター':
            # 床面積
            A_HCZ = calc_A_HCZ_i(1, A_A, A_MR, A_OR)
            R_type = '主たる居室'

            # パネルラジエーターの最大能力
            q_max_rad = rad_panel.calc_q_max_rad(region, mode_MR, A_HCZ, R_type)
            # パネルラジエーターの最大暖房出力
            Q_max_H_rad = rad_panel.get_Q_max_H_rad(Theta_SW_d_t, q_max_rad)
        elif spec_MR['type'] in ['温水暖房用床暖房', '温水床暖房（併用運転に対応）']:
            # 床面積
            A_HCZ = calc_A_HCZ_i(1, A_A, A_MR, A_OR)
            r_Af = spec_MR.get('r_Af')
            A_f = rad_floor.get_A_f(A_HCZ, r_Af)
            # 温水床暖房の単位面積当たりの上面最大放熱能力
            Q_max_H_rad = rad_floor.get_Q_max_H_rad(Theta_SW_d_t, A_f, racfh_combed)
        elif spec_MR['type'] == '温水暖房用ファンコンベクター':
            # 床面積
            A_HCZ = calc_A_HCZ_i(1, A_A, A_MR, A_OR)
            R_type = '主たる居室'
            q_max_FC = rad_fanc.calc_q_max_FC(region, mode_MR, A_HCZ, R_type)
            Q_max_H_rad = rad_fanc.calc_Q_max_H_rad(Theta_SW_d_t, q_max_FC)
        else:
            raise ValueError(spec_MR['type'])

        # 処理負荷
        Q_T_H_d_t_i = np.min([Q_max_H_rad, L_T_H_d_t[0]], axis=0)

        # 未処理負荷
        Q_UT_H_d_t_i = L_T_H_d_t[0] - Q_T_H_d_t_i

        print('{} Q_UT_H_d_t_1 = {} [MJ]'.format(spec_MR['type'], np.sum(Q_UT_H_d_t_i)))

        return Q_UT_H_d_t_i
    else:
        return calc_Q_UT_H_d_t(1, spec_MR, A_A, A_MR, A_OR, region, mode_MR, L_T_H_d_t[0])


def calc_Q_UT_H_OR_d_t(region, A_A, A_MR, A_OR, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG, L_T_H_d_t):
    """その他の居室に設置された暖房設備の未処理暖房負荷 (3b)

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      L_T_H_d_t(ndarray): 暖房区画の暖房負荷

    Returns:
      ndarray: 住戸全体を連続的に暖房する方式における1時間当たりのその他の居室の暖房設備の未処理暖房負荷(MJ/h)

    """
    # その他の居室がない場合
    if A_OR == 0:
        return np.zeros(24 * 365)
    else:
        if spec_OR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター']:
            # 主たる居室で温水床暖房とエアコンを併用する場合か否か
            racfh_combed = spec_MR['type'] == '温水床暖房（併用運転に対応）'

            # 送水温度の決定
            Theta_SW_hs_op = hwh.get_Theta_SW_hs_op(spec_HS['type'], HW, CG, racfh_combed)
            rad_list = hwh.get_rad_list(spec_MR, spec_OR)
            p_hs_d_t = hwh.calc_p_hs_d_t(Theta_SW_hs_op, rad_list, L_T_H_d_t, A_A, A_MR, A_OR, region, mode_MR,
                                         mode_OR)
            Theta_SW_d_t = hwh.get_Theta_SW_d_t(Theta_SW_hs_op, p_hs_d_t)

            # 未処理負荷
            Q_UT_H_d_t_i = np.zeros((5, 24 * 365))
            for i in range(2, 6):

                if spec_OR['type'] == '温水暖房用パネルラジエーター':
                    # 床面積
                    A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)
                    R_type = 'その他の居室'

                    # パネルラジエーターの最大能力
                    q_max_rad = rad_panel.calc_q_max_rad(region, mode_OR, A_HCZ, R_type)
                    # パネルラジエーターの最大暖房出力
                    Q_max_H_rad = rad_panel.get_Q_max_H_rad(Theta_SW_d_t, q_max_rad)
                elif spec_OR['type'] == '温水暖房用床暖房':
                    # 床面積
                    A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)
                    r_Af = spec_OR.get('r_Af')
                    A_f = rad_floor.get_A_f(A_HCZ, r_Af)
                    # 温水床暖房の単位面積当たりの上面最大放熱能力
                    Q_max_H_rad = rad_floor.get_Q_max_H_rad(Theta_SW_d_t, A_f)
                elif spec_OR['type'] == '温水暖房用ファンコンベクター':
                    # 床面積
                    A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)
                    R_type = 'その他の居室'
                    q_max_FC = rad_fanc.calc_q_max_FC(region, mode_OR, A_HCZ, R_type)
                    Q_max_H_rad = rad_fanc.calc_Q_max_H_rad(Theta_SW_d_t, q_max_FC)
                else:
                    raise ValueError(spec_OR['type'])

                # 処理負荷
                Q_T_H_d_t_i = np.min([Q_max_H_rad, L_T_H_d_t[i - 1]], axis=0)

                # 未処理負荷
                Q_UT_H_d_t_i[i - 1] = L_T_H_d_t[i - 1] - Q_T_H_d_t_i

                print('{} Q_UT_H_d_t_{} = {} [MJ]'.format(spec_OR['type'], i, np.sum(Q_UT_H_d_t_i[i - 1])))

            return np.sum(Q_UT_H_d_t_i, axis=0)
        else:
            return np.sum(
                [calc_Q_UT_H_d_t(i, spec_OR, A_A, A_MR, A_OR, region, mode_OR, L_T_H_d_t[i - 1]) for i in
                 range(2, 6)], axis=0)


def calc_Q_UT_H_d_t(i, device, A_A, A_MR, A_OR, region, mode, L_H_d_t):
    """未処理負荷を計算する

    Args:
      i(int): 暖冷房区画の番号
      device(dict): 暖房機器の仕様
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分
      mode(str): 運転方法 (連続運転|間歇運転)
      L_H_d_t(ndarray): 暖冷房区画݅の１時間当たりの暖房負荷(MJ/h)

    Returns:
      ndarray:: 1時間当たりの暖房設備機器等の未処理暖房負荷(MJ/h)

    """
    # 床面積
    A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)

    if device['type'] == 'ルームエアコンディショナー':

        # 仕様の取得
        q_rtd_C = rac_spec.get_q_rtd_C(A_HCZ)
        q_rtd_H = rac_spec.get_q_rtd_H(q_rtd_C)
        e_rtd_C = rac_spec.get_e_rtd_C(device['e_class'], q_rtd_C)
        e_rtd_H = rac_spec.get_e_rtd_H(e_rtd_C)

        # 未処理負荷の計算
        Q_UT_H_d_t = rac.calc_Q_UT_H_d_t(
            region=region,
            q_rtd_C=q_rtd_C,
            q_rtd_H=q_rtd_H,
            e_rtd_H=e_rtd_H,
            L_H_d_t=L_H_d_t,
        )

    elif device['type'] == 'FF暖房機':

        # 仕様の取得
        q_max_H = ff_spec.get_q_max_H(A_HCZ)
        q_min_H = ff_spec.get_q_min_H(q_max_H)
        P_rtd_H = ff_spec.get_P_rtd_H(q_max_H)
        P_itm_H = ff_spec.get_P_itm_H()

        # 未処理負荷の計算
        Q_UT_H_d_t = ff.calc_Q_UT_H_d_t(
            q_max_H=q_max_H,
            L_H_d_t=L_H_d_t
        )

    elif device['type'] == '電気蓄熱暖房器':

        # 仕様の取得
        q_rq_H = ets_spec.calc_q_rq_H(region)
        f_cT = ets_spec.get_f_cT(region)
        f_cI = ets_spec.calc_f_cI(mode, '主たる居室' if i == 1 else 'その他の居室')
        q_rtd_H = ets_spec.get_q_rtd_H(q_rq_H, A_HCZ, f_cT, f_cI)
        e_rtd_H = ets_spec.get_e_rtd_H()

        # 未処理負荷の計算
        Q_UT_H_d_t = ets.calc_Q_UT_H_d_t(
            q_rtd_H=q_rtd_H,
            e_rtd_H=e_rtd_H,
            L_H_d_t=L_H_d_t
        )

    elif device['type'] == '電気ヒーター床暖房':

        # 仕様の取得
        r_Af = device.get('r_Af')
        r_up = device['r_up']
        A_f = eheater_spec.get_A_f(A_HCZ, r_Af)

        # 未処理負荷の計算
        Q_UT_H_d_t = eheater.calc_Q_UT_H_d_t(
            A_f=A_f,
            r_up=r_up,
            L_H_d_t=L_H_d_t
        )

    elif device['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）']:
        raise ValueError(device['type'])

    elif device['type'] == 'ルームエアコンディショナー付温水床暖房機':

        # 仕様の取得
        r_Af = device.get('r_Af')

        # 未処理負荷の計算
        Q_UT_H_d_t = racfh.calc_Q_UT_H_d_t(region, A_HCZ, r_Af, L_H_d_t)

    else:
        raise ValueError(device['type'])

    print('{} Q_UT_H_d_t_{} = {} [MJ]'.format(device['type'], i, np.sum(Q_UT_H_d_t)))

    return Q_UT_H_d_t


# (5a)式は section4_1_Q.pyに定義

def get_Q_UT_H_d_t_i(Q_T_H_d_t_i, L_H_d_t_i):
    """暖冷房区画iに設置された暖房設備機器等の未処理暖房負荷 (6b)

    Args:
      Q_T_H_d_t_i(ndarray): 暖冷房区画iに設置された1時間当たりの処理暖房負荷 (MJ/h)
      L_H_d_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの1時間当たりの暖房負荷（MJ/h）

    Returns:
      ndarray:

    """
    # 1 時間当たりの暖房負荷
    __L_H_d_t_i = np.max([np.zeros(24 * 365), L_H_d_t_i], axis=0)  # 0未満の場合は0

    return __L_H_d_t_i - Q_T_H_d_t_i


# ===================================================
# 6.2 暖房設備のエネルギー消費量 
# ===================================================

def get_E_E_H_d_t(region, sol_region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q,
                  H_A=None,
                  spec_MR=None,
                  spec_OR=None, spec_HS=None,
                  mode_MR=None, mode_OR=None,
                  HW=None,
                  CG=None,
                  SHC=None, heating_flag_d=None,
                  L_T_H_d_t_i=None,
                  L_T_CS_d_t_i=None, L_T_CL_d_t_i=None,
                  **args):
    """暖房設備の消費電力量（kWh/h）(7a)

    Args:
      region(int): 省エネルギー地域区分
      sol_region: type sol_region:
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      A_env(float): 外皮の部位の面積の合計 (m2)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      H_A(dict, optional): 暖房方式 (Default value = None)
      spec_MR(dict, optional): 主たる居室の暖房機器の仕様 (Default value = None)
      spec_OR(dict, optional): その他の居室の暖房機器の仕様 (Default value = None)
      spec_HS(dict, optional): 温水暖房機の仕様 (Default value = None)
      mode_MR(str, optional): 主たる居室の運転方法 (連続運転|間歇運転) (Default value = None)
      mode_OR(str, optional): その他の居室の運転方法 (連続運転|間歇運転) (Default value = None)
      HW(dict, optional): 給湯機の仕様 (Default value = None)
      CG(dict, optional): コージェネレーションの機器 (Default value = None)
      SHC(dict, optional): 集熱式太陽熱利用設備の仕様 (Default value = None)
      heating_flag_d(ndarray, optional): 暖房日 (Default value = None)
      L_T_H_d_t_i(ndarray, optional): 暖房区画i=1-5それぞれの暖房負荷 (Default value = None)
      L_T_CS_d_t_i(ndarray, optional): 冷房区画i=1-5それぞれの冷房顕熱負荷 (Default value = None)
      L_T_CL_d_t_i(ndarray, optional): 冷房区画i=1-5それぞれの冷房潜熱負荷 (Default value = None)
      **args: 

    Returns:
      ndarray: 暖房設備の消費電力量（kWh/h）

    """
    if region == 8:
        return np.zeros(24 * 365)

    # 暖房設備機器等の消費電力量
    E_E_hs_d_t = calc_E_E_hs_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG,
                                 L_T_H_d_t_i, L_T_CS_d_t_i, L_T_CL_d_t_i)

    # 空気集熱式太陽熱利用設備の補機の消費電力量のうちの暖房設備への付加分
    E_E_aux_ass_d_t = get_E_E_aux_ass_d_t(SHC, heating_flag_d, region, sol_region)

    return E_E_hs_d_t + E_E_aux_ass_d_t


def get_E_E_aux_ass_d_t(SHC, heating_flag_d, region, sol_region):
    """空気集熱式太陽熱利用設備の補機の消費電力量のうちの暖房設備への付加分を計算する

    Args:
      SHC(dict): 集熱式太陽熱利用設備の仕様
      heating_flag_d(ndarray): 暖房日
      region(int): 省エネルギー地域区分
      sol_region: type sol_region:

    Returns:
      ndarray: 空気集熱式太陽熱利用設備の補機の消費電力量のうちの暖房設備への付加分（kWh/h）

    """
    if SHC is not None and SHC['type'] == '空気集熱式':
        E_E_aux_ass_d_t = ass.calc_E_E_H_aux_ass_d_t(
            hotwater_use=SHC['hotwater_use'],
            heating_flag_d=heating_flag_d,
            region=region,
            sol_region=sol_region,
            P_alpha=SHC['P_alpha'],
            P_beta=SHC['P_beta'],
            A_col=SHC['A_col'],
            V_fan_P0=SHC['V_fan_P0'],
            m_fan_test=SHC['m_fan_test'],
            d0=SHC['d0'],
            d1=SHC['d1'],
            fan_sso=SHC['fan_sso'],
            fan_type=SHC['fan_type'],
        )
    else:
        E_E_aux_ass_d_t = np.zeros(24 * 365)

    print('空気集熱式太陽熱利用設備の補機の消費電力量のうちの暖房設備への付加分 E_E_aux_ass = {} [kWh/年]'.format(np.sum(E_E_aux_ass_d_t)))

    return E_E_aux_ass_d_t


def calc_E_E_hs_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG,
                    L_T_H_d_t_i, L_T_CS_d_t_i, L_T_CL_d_t_i):
    """暖房設備機器等の消費電力量（kWh/h）を計算する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      A_env(float): 外皮の部位の面積の合計 (m2)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      H_A(dict): 暖房方式
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷
      L_T_CS_d_t_i(ndarray): 冷房区画i=1-5それぞれの冷房顕熱負荷
      L_T_CL_d_t_i(ndarray): 冷房区画i=1-5それぞれの冷房潜熱負荷

    Returns:
      ndarray: 暖房設備機器等の消費電力量（kWh/h）

    """
    if H_A is not None:
        return calc_E_E_H_hs_A_d_t(A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, H_A, L_T_H_d_t_i, L_T_CS_d_t_i, L_T_CL_d_t_i, region)
    elif (spec_MR is not None or spec_OR is not None) and L_T_H_d_t_i is not None:
        if is_hotwaterheatingonly(spec_MR, spec_OR):
            # 居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合 (8a)
            return calc_E_E_H_hs_MROR_d_t(region, A_A, A_MR, A_OR, spec_MR, spec_OR, spec_HS, HW, CG, L_T_H_d_t_i, L_T_CS_d_t_i, L_T_CL_d_t_i)
        else:
            # 居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合 (9a)
            return calc_E_E_H_hs_MR_d_t(region, A_A, A_MR, A_OR, mode_MR, mode_OR, spec_MR, spec_OR, spec_HS,
                                        L_T_H_d_t_i, L_T_CS_d_t_i, L_T_CL_d_t_i, HW, CG) \
                   + get_E_E_H_hs_OR_d_t(region, A_A, A_MR, A_OR, mode_MR, mode_OR, spec_MR, spec_OR, spec_HS,
                                         L_T_H_d_t_i, L_T_CS_d_t_i, L_T_CL_d_t_i, HW, CG)
    else:
        return np.zeros(24*365)


def is_hotwaterheatingonly(H_MR, H_OR):
    """居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置するかどうかを判定する

    Args:
      H_MR(dict): 主たる居室の暖房機器の仕様
      H_OR(dict): その他の居室の暖房機器の仕様

    Returns:
      bool: 居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置するかどうか

    """
    from pyhees.section4_7 import get_rad_type_list
    rad_types = get_rad_type_list()

    if H_MR['type'] not in rad_types:
        return False

    if H_OR is None:
        return True

    if H_OR['type'] in rad_types:
        return True

    return False


def calc_E_E_H_hs_MR_d_t(region, A_A, A_MR, A_OR, mode_MR, mode_OR, spec_MR, spec_OR, spec_HS, L_T_H_d_t_i, L_CS_x_t_i, L_CL_x_t_i, HW=None, CG=None):
    """居室のみを暖房する方式における主たる居室の暖房設備機器等の消費電力量（kWh/h）を計算する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷
      L_CS_x_t_i(ndarray): 冷房区画i=1-5それぞれの冷房顕熱負荷
      L_CL_x_t_i(ndarray): 冷房区画i=1-5それぞれの冷房潜熱負荷
      HW(dict, optional): 給湯機の仕様 (Default value = None)
      CG(dict, optional): コージェネレーションの機器 (Default value = None)

    Returns:
      ndarray: 居室のみを暖房する方式における主たる居室の暖房設備機器の消費電力量（kWh/h）

    """
    if spec_MR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）']:
        return hwh.calc_E_E_H_d_t(
            H_HS=spec_HS,
            H_MR=spec_MR,
            H_OR=spec_OR,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            region=region,
            mode_MR=mode_MR,
            mode_OR=mode_OR,
            L_T_H_rad=L_T_H_d_t_i,
            L_CS_x_t=L_CS_x_t_i,
            L_CL_x_t=L_CL_x_t_i,
            HW=HW,
            CG=CG
        )
    else:
        return calc_E_E_H_d_t(1, spec_MR, A_A, A_MR, A_OR, region, mode_MR, L_T_H_d_t_i[0])


def get_E_E_H_hs_OR_d_t(region, A_A, A_MR, A_OR, mode_MR, mode_OR, spec_MR, spec_OR, spec_HS, L_T_H_d_t_i, L_CS_x_t_i, L_CL_x_t_i, HW=None, CG=None):
    """居室のみを暖房する方式におけるその他の居室の暖房設備機器等の消費電力量（kWh/h）を計算する (11a)

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷
      L_CS_x_t_i(ndarray): 冷房区画i=1-5それぞれの冷房顕熱負荷
      L_CL_x_t_i(ndarray): 冷房区画i=1-5それぞれの冷房潜熱負荷
      HW(dict, optional): 給湯機の仕様 (Default value = None)
      CG(dict, optional): コージェネレーションの機器 (Default value = None)

    Returns:
      ndarray: 居室のみを暖房する方式におけるその他の居室の暖房設備機器の消費電力量（kWh/h）

    """
    # その他の居室がない場合
    if spec_OR is None:
        return np.zeros(24 * 365)
    else:
        if spec_OR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）']:
            return hwh.calc_E_E_H_d_t(
                H_HS=spec_HS,
                H_MR=spec_MR,
                H_OR=spec_OR,
                A_A=A_A,
                A_MR=A_MR,
                A_OR=A_OR,
                region=region,
                mode_MR=mode_MR,
                mode_OR=mode_OR,
                L_T_H_rad=L_T_H_d_t_i,
                L_CS_x_t=L_CS_x_t_i,
                L_CL_x_t=L_CL_x_t_i,
                HW=HW,
                CG=CG)
        else:
            # 暖房区画i=2～5の電力消費量を計算して合算する
            return np.sum(
                [calc_E_E_H_d_t(i, spec_OR, A_A, A_MR, A_OR, region, mode_OR, L_T_H_d_t_i[i - 1]) for i in
                 [3, 4, 5]], axis=0)


def get_virtual_heatsource(region, H_HS):
    """実質的な温水暖房機の仕様を取得する

    Args:
      region(int): 省エネルギー地域区分
      H_HS(dict): 温水暖房機の仕様

    Returns:
      dict: 実質的な温水暖房機の仕様

    """
    default_HS = get_default_heatsource(region)

    if H_HS is None:
        return default_HS
    elif H_HS['type'] == 'その他の温水暖房機':
        return {
            'type': default_HS['type'],
            'e_rtd_hs': default_HS['e_rtd_hs'],
            'pipe_insulation': H_HS['pipe_insulation'],
            'underfloor_pipe_insulation': H_HS['underfloor_pipe_insulation'],
        }
    elif H_HS['type'] == '温水暖房機を設置しない':
        return {
            'type': default_HS['type'],
            'e_rtd_hs': default_HS['e_rtd_hs'],
            'pipe_insulation': False,
            'underfloor_pipe_insulation': False,
        }
    else:
        return H_HS


def calc_E_E_H_d_t(i, device, A_A, A_MR, A_OR, region, mode, L_H_d_t):
    """暖房区画1つと1つの暖房設備機器によって消費される電力消費量

    Args:
      i(int): 暖冷房区画の番号
      device(dict): 暖房機器の仕様
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分
      mode(str): 運転方法 (連続運転|間歇運転)
      L_H_d_t(ndarray): 暖冷房区画݅の１時間当たりの暖房負荷(MJ/h)

    Returns:
      ndarray:: 暖房設備の消費電力量(kWh/h)

    """
    # 床面積の取得
    A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)

    if device['type'] == 'ルームエアコンディショナー':

        # 仕様の取得
        q_rtd_C = rac_spec.get_q_rtd_C(A_HCZ)
        q_rtd_H = rac_spec.get_q_rtd_H(q_rtd_C)
        e_rtd_C = rac_spec.get_e_rtd_C(device['e_class'], q_rtd_C)
        e_rtd_H = rac_spec.get_e_rtd_H(e_rtd_C)

        # 消費電力量の計算
        E_E_H_d_t = rac.calc_E_E_H_d_t(
            region=region,
            q_rtd_C=q_rtd_C,
            q_rtd_H=q_rtd_H,
            e_rtd_H=e_rtd_H,
            dualcompressor=device['dualcompressor'],
            L_H_d_t=L_H_d_t,
        )

    elif device['type'] == 'FF暖房機':

        # 仕様の取得
        q_max_H = ff_spec.get_q_max_H(A_HCZ)
        q_min_H = ff_spec.get_q_min_H(q_max_H)
        P_rtd_H = ff_spec.get_P_rtd_H(q_max_H)
        P_itm_H = ff_spec.get_P_itm_H()

        # 消費電力量の計算
        E_E_H_d_t = ff.calc_E_E_H_d_t(
            q_max_H=q_max_H,
            q_min_H=q_min_H,
            P_rtd_H=P_rtd_H,
            P_itm_H=P_itm_H,
            L_H_d_t=L_H_d_t
        )

    elif device['type'] == '電気ヒーター床暖房':

        # 仕様の取得
        r_Af = device.get('r_Af')
        r_up = device['r_up']
        A_f = eheater_spec.get_A_f(A_HCZ, r_Af)

        # 消費電力量の計算
        E_E_H_d_t = eheater.calc_E_E_H_d_t(
            A_f=A_f,
            r_up=r_up,
            L_H_d_t=L_H_d_t
        )

    elif device['type'] == '電気蓄熱暖房器':

        # 仕様の取得
        q_rq_H = ets_spec.calc_q_rq_H(region)
        f_cT = ets_spec.get_f_cT(region)
        f_cI = ets_spec.calc_f_cI(mode, '主たる居室' if i == 1 else 'その他の居室')
        q_rtd_H = ets_spec.get_q_rtd_H(q_rq_H, A_HCZ, f_cT, f_cI)
        e_rtd_H = ets_spec.get_e_rtd_H()

        # 消費電力量の計算
        E_E_H_d_t = ets.calc_E_E_H_d_t(
            q_rtd_H=q_rtd_H,
            e_rtd_H=e_rtd_H,
            L_H_d_t=L_H_d_t
        )

    elif device['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）']:
        # 温水暖房は第7節で取り扱うためここでは処理しない
        raise UserWarning(device['type'])

    elif device['type'] == 'ルームエアコンディショナー付温水床暖房機':

        # 仕様の取得
        r_Af = device.get('r_Af')
        r_up = device['r_up']
        pipe_insulation = device['pipe_insulation']

        # 消費電力量の計算
        E_E_H_d_t = racfh.calc_E_E_d_t(
            region=region,
            A_A_act=A_A,
            i=i,
            A_HCZ=A_HCZ,
            r_Af=r_Af,
            r_up=r_up,
            pipe_insulation=pipe_insulation,
            L_H_d_t=L_H_d_t
        )

    else:
        raise ValueError(device['type'])

    print('{} E_E_H_d_t_{} = {} [kWh] (L_H_d_t_{} = {} [MJ])'.format(device['type'], i, np.sum(E_E_H_d_t), i,
                                                                     np.sum(L_H_d_t)))

    return E_E_H_d_t


def calc_L_H_d_t(region, sol_region, A_A, A_MR, A_OR, mode_H, mode_C, H_MR, H_OR, mode_MR, mode_OR, Q, mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX,
                 SHC, underfloor_insulation, normalize=True):
    """暖冷房区画の１時間当たりの暖房負荷を計算する

    Args:
      region(int): 省エネルギー地域区分
      sol_region: type sol_region:
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_H(str): 暖房方式
      mode_C(str): 冷房方式
      H_MR(dict): 主たる居室の暖房機器の仕様
      H_OR(dict): その他の居室の暖房機器の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      NV_MR(float): 主たる居室における通風の利用における相当換気回数
      NV_OR(float): その他の居室における通風の利用における相当換気回数
      TS(bool): 蓄熱の利用
      r_A_ufvnt(param HEX: 熱交換器型設備仕様辞書): 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
      HEX(dict): 熱交換器型設備仕様辞書
      SHC(dict): 集熱式太陽熱利用設備の仕様
      underfloor_insulation: type underfloor_insulation:
      normalize(bool, optional): 正規化の有無 (Default value = True)

    Returns:
      ndarray: 暖冷房区画の１時間当たりの暖房負荷

    """
    # 温水暖房
    floorheating_i = get_floorheating_i(H_MR, H_OR)
    R_l_i = get_R_l_i(H_MR, H_OR)


    # 暖冷房区画i݅の1時間当たりの暖房負荷 (1)
    args = {
        'region': region,
        'A_A': A_A,
        'A_MR': A_MR,
        'A_OR': A_OR,

        # 外皮
        'Q': Q,
        'mu_H': mu_H,
        'mu_C': mu_C,
        'NV_MR': NV_MR,
        'NV_OR': NV_OR,
        'TS': TS,

        # 床下換気
        'r_A_ufvnt': r_A_ufvnt,
        'underfloor_insulation': underfloor_insulation,

        # 床下暖房
        'floorheating': tuple(floorheating_i),
        'R_l_i': tuple(R_l_i),
    }

    # 運転モード(暖房)
    args['mode_H'] = get_mode_H_array(mode_H, mode_MR, mode_OR)

    # 運転モード(冷房)
    args['mode_C'] = get_mode_C_array(mode_C)

    # 熱交換型換気
    if HEX is not None:
        args['hex'] = True
        args['etr_dash_t'] = calc_etr_dash_t(
            etr_t_raw=HEX['etr_t'],
            e=HEX.get('e'),
            C_bal=HEX.get('C_bal'),
            C_leak=HEX.get('C_leak')
        )
    else:
        args['hex'] = False
        args['etr_dash_t'] = None

    # 太陽熱集熱式
    if SHC is not None and SHC['type'] == '空気集熱式':
        args.update({
            'hotwater_use': SHC['hotwater_use'],
            'supply_target': SHC['supply_target'],
            'sol_region': sol_region,
            'P_alpha': SHC['P_alpha'],
            'P_beta': SHC['P_beta'],
            'A_col': SHC['A_col'],
            'V_fan_P0': SHC['V_fan_P0'],
            'm_fan_test': SHC['m_fan_test'],
            'd0': SHC['d0'],
            'd1': SHC['d1'],
            'ufv_insulation': SHC['ufv_insulation'],
            'r_A_ufvnt_ass': SHC['r_A_ufvnt_ass'],
        })

    L_T_H_d_t_i, L_dash_H_R_d_t_i = ld.calc_L_H_d_t_i(**args)

    if normalize:
        L_T_H_d_t_i[L_T_H_d_t_i < 0] = 0

    return L_T_H_d_t_i, L_dash_H_R_d_t_i


def get_mode_C_array(mode_C):
    """冷房の運転モードを取得する

    Args:
      mode_C(str): 冷房方式

    Returns:
      tuple: 冷房の運転モード

    """
    # 運転モード(冷房)
    if mode_C == '住戸全体を連続的に冷房する方式':
        return tuple(["全館連続"] * 12)
    else:
        return ('居室間歇', '居室間歇', '居室間歇', '居室間歇', '居室間歇', None, None, None, None, None, None, None)


def get_mode_H_array(mode_H, mode_MR, mode_OR):
    """暖房の運転モードを取得する

    Args:
      mode_H(str): 暖房方式
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)

    Returns:
      tuple: 暖房の運転モード

    """
    # 運転モード(暖房)
    if mode_H == '住戸全体を連続的に暖房する方式':
        # 全館連続
        return tuple(["全館連続"] * 12)
    else:
        return (mode_MR, None, mode_OR, mode_OR, mode_OR, None, None, None, None, None, None, None)


def get_floorheating_i(H_MR, H_OR):
    """床暖房の有無を取得する

    Args:
      H_MR(dict): 主たる居室の暖房機器の仕様
      H_OR(dict): その他の居室の暖房機器の仕様

    Returns:
      ndarray:: 床暖房の有無

    """
    floorheating = np.zeros(12)

    if H_MR is not None:
        if H_MR['type'] in ['電気ヒーター床暖房', '温水暖房用床暖房', 'ルームエアコンディショナー付温水床暖房機', '温水床暖房（併用運転に対応）']:
            floorheating[0] = True

    if H_OR is not None:
        if H_OR['type'] in ['電気ヒーター床暖房', '温水暖房用床暖房', 'ルームエアコンディショナー付温水床暖房機']:
            floorheating[1:6] = True

    return floorheating


def get_R_l_i(H_MR, H_OR):
    """敷設率を取得する

    Args:
      H_MR(dict): 主たる居室の暖房機器の仕様
      H_OR(dict): その他の居室の暖房機器の仕様

    Returns:
      ndarray:: 敷設率

    """
    # 床暖房
    R_l_i = np.zeros(12)

    if H_MR is not None:
        if H_MR['type'] in ['電気ヒーター床暖房', '温水暖房用床暖房', 'ルームエアコンディショナー付温水床暖房機', '温水床暖房（併用運転に対応）']:
            if 'r_dash_Af' not in H_MR:
                R_l_i[0] = H_MR.get('r_Af')
            else:
                # 吹き抜けを有する場合
                R_l_i[0] = H_MR.get('r_dash_Af')

    if H_OR is not None:
        if H_OR['type'] in ['電気ヒーター床暖房', '温水暖房用床暖房', 'ルームエアコンディショナー付温水床暖房機']:
            R_l_i[1:6] = H_OR.get('r_Af')

    return R_l_i


def calc_A_HCZ_i(i, A_A, A_MR, A_OR):
    """暖冷房区画iの床面積 (m2)

    Args:
      i(int): 暖冷房区画の番号
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(flaot): その他の居室の床面積 (m2)

    Returns:
      float: 暖冷房区画iの床面積 (m2)

    """
    return ld.get_A_HCZ_i(i, A_A, A_MR, A_OR)


def get_E_G_H_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG, L_T_H_d_t_i):
    """暖房設備のガス消費量(MJ/h)(7b)を取得する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      H_A(dict): 暖房方式
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷

    Returns:
      ndarray: 暖房設備のガス消費量(MJ/h)

    """
    return calc_E_G_hs_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, L_T_H_d_t_i, HW, CG)


def calc_E_G_hs_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, L_T_H_d_t_i, HW, CG):
    """暖房設備機器等のガス消費量(MJ/h)を取得する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      H_A(dict): 暖房方式
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器

    Returns:
      ndarray: 暖房設備機器等のガス消費量(MJ/h)

    """
    if H_A is not None:
        # (7b)
        return calc_E_G_H_hs_A_d_t()
    elif (spec_MR is not None or spec_OR is not None) and L_T_H_d_t_i is not None:
        if is_hotwaterheatingonly(spec_MR, spec_OR):
            # 居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合 (8b)
            return calc_E_G_H_hs_MROR_d_t(mode_MR, mode_OR, spec_HS, spec_MR, spec_OR, L_T_H_d_t_i, HW, CG, A_A, A_MR, A_OR,
                                          region)
        else:
            # 居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合
            # (9b)
            return calc_E_G_H_hs_MR_d_t(region, A_A, A_MR, A_OR, mode_MR, mode_OR, spec_MR, spec_OR, spec_HS,
                                        L_T_H_d_t_i, HW, CG) \
                   + calc_E_G_H_hs_OR_d_t(region, A_A, A_MR, A_OR, mode_MR, mode_OR, spec_MR, spec_OR, spec_HS,
                                          L_T_H_d_t_i, HW, CG)
    else:
        return np.zeros(24*365)


def calc_E_G_H_hs_MR_d_t(region, A_A, A_MR, A_OR, mode_MR, mode_OR, spec_MR, spec_OR, spec_HS, L_T_H_d_t, HW, CG):
    """居室のみを暖房する方式における主たる居室に設置された暖房設備機器のガス消費量（MJ/h）を取得する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      L_T_H_d_t(ndarray): 暖房負荷
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器

    Returns:
      ndarray: 居室のみを暖房する方式における主たる居室に設置された暖房設備機器のガス消費量（MJ/h）

    """
    if spec_MR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）']:
        return hwh.calc_E_G_H_d_t(
            H_HS=spec_HS,
            H_MR=spec_MR,
            H_OR=spec_OR,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            region=region,
            mode_MR=mode_MR,
            mode_OR=mode_OR,
            L_T_H_rad=L_T_H_d_t,
            HW=HW,
            CG=CG)
    else:

        return calc_E_G_H_d_t(1, spec_MR, A_A, A_MR, A_OR, L_T_H_d_t[0])


def calc_E_G_H_hs_OR_d_t(region, A_A, A_MR, A_OR, mode_MR, mode_OR, spec_MR, spec_OR, spec_HS, L_T_H_d_t, HW=None, CG=None):
    """居室のみを暖房する方式におけるその他の居室に設置された暖房設備機器のガス消費量（MJ/h）を取得する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      L_T_H_d_t(ndarray): 暖房負荷
      HW(dict, optional): 給湯機の仕様 (Default value = None)
      CG(dict, optional): コージェネレーションの機器 (Default value = None)

    Returns:
      ndarray: 居室のみを暖房する方式におけるその他の居室に設置された暖房設備機器のガス消費量（MJ/h）

    """
    # その他の居室がない場合
    if spec_OR is None:
        return np.zeros(24 * 365)

    else:
        if spec_OR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター']:
            return hwh.calc_E_G_H_d_t(
                H_HS=spec_HS,
                H_MR=spec_MR,
                H_OR=spec_OR,
                A_A=A_A,
                A_MR=A_MR,
                A_OR=A_OR,
                region=region,
                mode_MR=mode_MR,
                mode_OR=mode_OR,
                L_T_H_rad=L_T_H_d_t,
                HW=HW,
                CG=CG)
        else:
            return np.sum(
                [calc_E_G_H_d_t(i, spec_OR, A_A, A_MR, A_OR, L_T_H_d_t[i - 1])
                 for i in
                 range(2, 6)], axis=0)


def calc_E_G_H_d_t(i, device, A_A, A_MR, A_OR, L_H_d_t):
    """暖房設備のガス消費量(MJ/h)(7b)を取得する

    Args:
      i(int): 暖冷房区画の番号
      device(dict): 暖房機器の仕様
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      L_H_d_t(ndarray): 暖冷房区画݅の１時間当たりの暖房負荷(MJ/h)

    Returns:
      ndarray: 暖房設備のガス消費量(MJ/h)

    """
    # 床面積
    A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)

    if device['type'] == 'ルームエアコンディショナー':
        # ガス消費量の計算
        E_G_H_d_t = rac.get_E_G_H_d_t()

    elif device['type'] == 'FF暖房機':

        # 仕様の取得
        q_max_H = ff_spec.get_q_max_H(A_HCZ)
        if 'e_rtd_H' in device:
            e_rtd_H = device['e_rtd_H']
        else:
            e_rtd_H = ff_spec.get_e_rtd_H_default()

        # ガス消費量の計算
        E_G_H_d_t = ff.calc_E_G_H_d_t(
            fuel='K',
            q_max_H=q_max_H,
            e_rtd_H=e_rtd_H,
            L_H_d_t=L_H_d_t
        )

    elif device['type'] == '電気蓄熱暖房器':
        # ガス消費量の計算
        E_G_H_d_t = ets.get_E_G_H_d_t()

    elif device['type'] == '電気ヒーター床暖房':
        # ガス消費量の計算
        E_G_H_d_t = eheater.get_E_G_H_d_t()

    elif device['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）']:
        # 温水暖房は第7節で取り扱うためここでは処理しない
        raise UserWarning(device['type'])

    elif device['type'] == 'ルームエアコンディショナー付温水床暖房機':
        # ガス消費量の計算
        E_G_H_d_t = racfh.get_E_G_d_t()

    else:
        raise ValueError(device['type'])

    print('{} E_G_H_d_t_{} = {} [MJ] (L_H_d_t_{} = {} [MJ])'.format(device['type'], i, np.sum(E_G_H_d_t), i,
                                                                    np.sum(L_H_d_t)))

    return E_G_H_d_t


def calc_E_K_H_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG, L_T_H_d_t_i):
    """暖房設備の灯油消費量（MJ/h）(7c)を取得する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      H_A(dict): 暖房方式
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷

    Returns:
      ndarray: 暖房設備の灯油消費量（MJ/h）

    """
    return calc_E_K_hs_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, L_T_H_d_t_i,
                           HW, CG)


def calc_E_K_hs_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, L_T_H_d_t_i, HW, CG):
    """暖房設備機器等の灯油消費量（MJ/h）を取得する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      H_A(dict): 暖房方式
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器

    Returns:
      ndarray: 暖房設備機器等の灯油消費量（MJ/h）

    """
    if H_A is not None:
        # (7c)
        return calc_E_K_H_hs_A_d_t()
    elif (spec_MR is not None or spec_OR is not None) and L_T_H_d_t_i is not None:
        if is_hotwaterheatingonly(spec_MR, spec_OR):
            # 居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合 (8c)
            return calc_E_K_H_hs_MROR_d_t(spec_HS, spec_MR, spec_OR, HW, CG, A_A, A_MR, A_OR, region, mode_MR, mode_OR,
                                          L_T_H_d_t_i)
        else:

            # 居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合 (9c)
            return calc_E_K_H_hs_MR_d_t(region, A_A, A_MR, A_OR, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR,
                                        L_T_H_d_t_i, HW, CG) \
                   + calc_E_K_H_hs_OR_d_t(region, A_A, A_MR, A_OR, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR,
                                          L_T_H_d_t_i, HW, CG)
    else:
        return np.zeros(24*365)


def calc_E_K_H_hs_MR_d_t(region, A_A, A_MR, A_OR, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, L_T_H_d_t, HW, CG):
    """居室のみを暖房する方式における主たる居室に設置された暖房設備機器のガス消費量(MJ/h)

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      H_A(dict): 暖房方式
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      L_T_H_d_t: returns: 居室のみを暖房する方式における主たる居室に設置された暖房設備機器のガス消費量(MJ/h)

    Returns:
      ndarray: 居室のみを暖房する方式における主たる居室に設置された暖房設備機器のガス消費量(MJ/h)

    """
    if spec_MR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）']:
        return hwh.calc_E_K_H_d_t(
            H_HS=spec_HS,
            H_MR=spec_MR,
            H_OR=spec_OR,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            region=region,
            mode_MR=mode_MR,
            mode_OR=mode_OR,
            L_T_H_rad=L_T_H_d_t,
            HW=HW,
            CG=CG)
    else:
        return calc_E_K_d_t(1, spec_MR, A_A, A_MR, A_OR, L_T_H_d_t[0])


def calc_E_K_H_hs_OR_d_t(region, A_A, A_MR, A_OR, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, L_T_H_d_t, HW, CG):
    """居室のみを暖房する方式におけるその他の居室に設置された暖房設備機器のガス消費量(MJ/h)

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      H_A(dict): 暖房方式
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      L_T_H_d_t(ndarray): 暖房区画i=1-5それぞれの暖房負荷
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器

    Returns:
      ndarray: 居室のみを暖房する方式におけるその他の居室に設置された暖房設備機器のガス消費量(MJ/h)

    """
    # その他の居室がない場合
    if spec_OR is None:
        return np.zeros(24 * 365)

    else:
        if spec_OR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター']:
            return hwh.calc_E_K_H_d_t(
                H_HS=spec_HS,
                H_MR=spec_MR,
                H_OR=spec_OR,
                A_A=A_A,
                A_MR=A_MR,
                A_OR=A_OR,
                region=region,
                mode_MR=mode_MR,
                mode_OR=mode_OR,
                L_T_H_rad=L_T_H_d_t,
                HW=HW,
                CG=CG)
        else:
            return np.sum(
                [calc_E_K_d_t(i, spec_OR, A_A, A_MR, A_OR, L_T_H_d_t[i - 1])
                 for i in
                 range(2, 6)], axis=0)


def get_virtual_heating_devices(region, H_MR, H_OR):
    """実質的な暖房機器の仕様を取得する

    Args:
      region(int): 省エネルギー地域区分
      H_MR(dict): 主たる居室の暖房機器の仕様
      H_OR(dict): その他の居室の暖房機器の仕様

    Returns:
      tuple(dict, dict): 実質的な暖房機器の仕様(主たる居室, その他の居室)

    """
    # 規定の暖房機器を取得
    default_spec = get_default_heating_spec(region)

    # 設置しないまたはその他の機器の場合は規定の機器に置き換える
    if H_MR is not None:
        if H_MR['type'] == '設置しない' or H_MR['type'] == 'その他':
            H_MR = default_spec[0]
    if H_OR is not None:
        if H_OR['type'] == '設置しない' or H_OR['type'] == 'その他':
            H_OR = default_spec[1]

    return H_MR, H_OR


def calc_E_K_d_t(i, device, A_A, A_MR, A_OR, L_H_d_t):
    """暖房区画1つと1つの暖房設備機器によって消費されるガス消費量(MJ/h)を取得する

    Args:
      i(int): 暖冷房区画の番号
      device(dict): 暖房機器の仕様
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      L_H_d_t(ndarray): 暖冷房区画݅の１時間当たりの暖房負荷(MJ/h)

    Returns:
      ndarray: 暖房区画1つと1つの暖房設備機器によって消費されるガス消費量(MJ/h)

    """
    # 床面積
    A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)

    if device['type'] == 'ルームエアコンディショナー':
        # 灯油の消費量の計算
        E_K_d_t = rac.get_E_K_H_d_t()

    elif device['type'] == 'FF暖房機':

        # 仕様の取得
        q_max_H = ff_spec.get_q_max_H(A_HCZ)
        if 'e_rtd_H' in device:
            e_rtd_H = device['e_rtd_H']
        else:
            e_rtd_H = ff_spec.get_e_rtd_H_default()

        # ガス消費量の計算
        E_K_d_t = ff.calc_E_K_H_d_t(
            fuel='K',
            q_max_H=q_max_H,
            e_rtd_H=e_rtd_H,
            L_H_d_t=L_H_d_t
        )

    elif device['type'] == '電気蓄熱暖房器':
        # 灯油の消費量の計算
        E_K_d_t = ets.get_E_K_H_d_t()

    elif device['type'] == '電気ヒーター床暖房':
        # 灯油の消費量の計算
        E_K_d_t = eheater.get_E_K_H_d_t()

    elif device['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）']:
        # 温水暖房は第7節で取り扱うためここでは処理しない
        raise UserWarning(device['type'])

    elif device['type'] == 'ルームエアコンディショナー付温水床暖房機':
        # 灯油の消費量の計算
        E_K_d_t = racfh.get_E_K_d_t()

    else:
        raise ValueError(device['type'])

    print(
        '{} E_K_d_t_{} = {} [MJ] (L_H_d_t_{} = {} [MJ)'.format(device['type'], i, np.sum(E_K_d_t), i, np.sum(L_H_d_t)))

    return E_K_d_t


def calc_E_M_H_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, L_T_H_d_t_i):
    """暖房設備のその他の燃料による一次エネルギー消費量（MJ/h）(7d)を取得する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      H_A(dict): 暖房方式
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷

    Returns:
      ndarray: 暖房設備のその他の燃料による一次エネルギー消費量（MJ/h）

    """
    return calc_E_M_hs_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, L_T_H_d_t_i)


def calc_E_M_hs_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, L_H_d_t):
    """暖房設備機器等のその他の燃料による一次エネルギー消費量（MJ/h）を取得する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      H_A(dict): 暖房方式
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      L_H_d_t(ndarray): 暖冷房区画݅の１時間当たりの暖房負荷(MJ/h)

    Returns:
      ndarray: 暖房設備機器等のその他の燃料による一次エネルギー消費量（MJ/h）

    """
    if H_A is not None:
        # (7d)
        return calc_E_M_H_hs_A_d_t()
    else:

        if is_hotwaterheatingonly(spec_MR, spec_OR):
            # 居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合
            # (8d)
            return calc_E_M_H_hs_MROR_d_t(region, spec_HS)
        else:
            # 居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合
            # (9d)
            return calc_E_M_H_hs_MR_d_t(A_A, A_MR, A_OR, spec_MR, spec_HS, L_H_d_t) + \
                   calc_E_M_H_hs_OR_d_t(A_A, A_MR, A_OR, spec_OR, spec_HS, L_H_d_t)


# ===================================================
# 6.3 暖房設備機器のエネルギー消費量 
# ===================================================

# ---------------------------------------------------
# 6.3.1 住戸全体を連続的に暖房する方式 
# ---------------------------------------------------

def calc_E_E_H_hs_A_d_t(A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, H_A, L_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i, region):
    """住戸全体を連続的に暖房する方式における暖房設備機器の消費電力量（kWh/h）を計算する

    Args:
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      A_env(float): 外皮の部位の面積の合計 (m2)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      H_A(dict): 暖房方式
      L_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷
      L_CS_d_t_i(ndarray): 冷房区画i=1-5それぞれの冷房顕熱負荷
      L_CL_d_t_i(ndarray): 冷房区画i=1-5それぞれの冷房潜熱負荷
      region(int): 省エネルギー地域区分

    Returns:
      ndarray: 住戸全体を連続的に暖房する方式における暖房設備機器の消費電力量（kWh/h）

    """
    # VAV方式の採用
    if 'VAV' in H_A:
        VAV = H_A['VAV']

    # 全般換気機能の有無
    if 'general_ventilation' in H_A:
        general_ventilation = H_A['general_ventilation']

    # ダクトが通過する空間
    if 'duct_insulation' in H_A:
        duct_insulation = H_A['duct_insulation']

    # 機器の仕様の
    if H_A['EquipmentSpec'] == '入力しない':
        # 付録B
        EquipmentSpec = '入力しない'
        q_hs_rtd_H = dc_spec.get_q_hs_rtd_H(region, A_A)
        q_hs_mid_H = dc_spec.get_q_hs_mid_H(q_hs_rtd_H)
        q_hs_min_H = dc_spec.get_q_hs_min_H(q_hs_rtd_H)
        P_hs_rtd_H = dc_spec.get_P_hs_rtd_H(q_hs_rtd_H)
        V_fan_rtd_H = dc_spec.get_V_fan_rtd_H(q_hs_rtd_H)
        V_fan_mid_H = dc_spec. get_V_fan_mid_H(q_hs_mid_H)
        P_fan_rtd_H = dc_spec.get_P_fan_rtd_H(V_fan_rtd_H)
        P_fan_mid_H = dc_spec.get_P_fan_mid_H(V_fan_mid_H)
        P_hs_mid_H = np.NAN
    elif H_A['EquipmentSpec'] == '定格能力試験の値を入力する':
        EquipmentSpec = '定格能力試験の値を入力する'
        q_hs_rtd_H = H_A['q_hs_rtd_H']
        P_hs_rtd_H = H_A['P_hs_rtd_H']
        V_fan_rtd_H =H_A['V_fan_rtd_H']
        P_fan_rtd_H = H_A['P_fan_rtd_H']
        q_hs_mid_H = dc_spec.get_q_hs_mid_H(q_hs_rtd_H)
        q_hs_min_H = dc_spec.get_q_hs_min_H(q_hs_rtd_H)
        V_fan_mid_H = dc_spec. get_V_fan_mid_H(q_hs_mid_H)
        P_fan_mid_H = dc_spec.get_P_fan_mid_H(V_fan_mid_H)
        P_hs_mid_H = np.NAN
    elif H_A['EquipmentSpec'] == '定格能力試験と中間能力試験の値を入力する':
        EquipmentSpec = '定格能力試験と中間能力試験の値を入力する'
        q_hs_rtd_H = H_A['q_hs_rtd_H']
        P_hs_rtd_H = H_A['P_hs_rtd_H']
        V_fan_rtd_H = H_A['V_fan_rtd_H']
        P_fan_rtd_H = H_A['P_fan_rtd_H']
        q_hs_mid_H = H_A['q_hs_mid_H']
        P_hs_mid_H = H_A['P_hs_mid_H']
        V_fan_mid_H = H_A['V_fan_mid_H']
        P_fan_mid_H = H_A['P_fan_mid_H']
        q_hs_min_H = dc_spec.get_q_hs_min_H(q_hs_rtd_H)
    else:
        raise ValueError(H_A['EquipmentSpec'])

     # 設計風量(暖房)
    if 'V_hs_dsgn_H' in H_A:
        V_hs_dsgn_H = H_A['V_hs_dsgn_H']
    else:
        V_hs_dsgn_H = dc_spec.get_V_fan_dsgn_H(V_fan_rtd_H)

    # 定格冷房能力
    q_hs_rtd_C = None

    # 設計風量(冷房)
    V_hs_dsgn_C = None

    _, _, _, _, Theta_hs_out_d_t, Theta_hs_in_d_t, \
    _, _, V_hs_supply_d_t, V_hs_vent_d_t, C_df_H_d_t = dc.calc_Q_UT_A(A_A, A_MR, A_OR, A_env, mu_H, mu_C,
                                                                    q_hs_rtd_H, q_hs_rtd_C, V_hs_dsgn_H,
                                                                    V_hs_dsgn_C, Q, VAV, general_ventilation,
                                                                    duct_insulation, region, L_H_d_t_i,
                                                                    L_CS_d_t_i, L_CL_d_t_i)

    # 電力消費量の計算
    E_E_H_d_t = dc_a.calc_E_E_H_d_t(
        Theta_hs_out_d_t=Theta_hs_out_d_t,
        Theta_hs_in_d_t=Theta_hs_in_d_t,
        V_hs_supply_d_t=V_hs_supply_d_t,
        V_hs_vent_d_t=V_hs_vent_d_t,
        C_df_H_d_t=C_df_H_d_t,
        q_hs_rtd_H=q_hs_rtd_H,
        V_hs_dsgn_H=V_hs_dsgn_H,
        P_hs_mid_H=P_hs_mid_H,
        P_hs_rtd_H=P_hs_rtd_H,
        P_fan_rtd_H=P_fan_rtd_H,
        P_fan_mid_H=P_fan_mid_H,
        q_hs_min_H=q_hs_min_H,
        q_hs_mid_H=q_hs_mid_H,
        V_fan_rtd_H=V_fan_rtd_H,
        V_fan_mid_H=V_fan_mid_H,
        EquipmentSpec=EquipmentSpec,
        region=region
    )

    return E_E_H_d_t


def calc_E_G_H_hs_A_d_t():
    """住戸全体を連続的に暖房する方式における暖房設備機器のガス消費量（MJ/h）

    Args:

    Returns:
      ndarray: 住戸全体を連続的に暖房する方式における暖房設備機器のガス消費量（MJ/h）

    """
    return dc.get_E_G_H_d_t()


def calc_E_K_H_hs_A_d_t(**args):
    """住戸全体を連続的に暖房する方式における暖房設備機器の灯油消費量（MJ/h）を取得する

    Args:
      **args: 

    Returns:
      ndarray: 住戸全体を連続的に暖房する方式における暖房設備機器の灯油消費量（MJ/h）

    """
    return dc.get_E_K_H_d_t()


def calc_E_M_H_hs_A_d_t():
    """暖房設備のその他の燃料による一次エネルギー消費量（MJ/h）(7d)を取得する

    Args:

    Returns:
      ndarray: 暖房設備のその他の燃料による一次エネルギー消費量（MJ/h）

    """
    return dc.get_E_M_H_d_t()


# ---------------------------------------------------
# 6.3.2 居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合
# ---------------------------------------------------

def calc_E_E_H_hs_MROR_d_t(region, A_A, A_MR, A_OR, H_MR, H_OR, H_HS, HW, CG, L_T_H_d_t_i, L_CS_x_t_i, L_CL_x_t_i):
    """居室のみを暖房する方式における主たる居室及びその他の居室に設置された暖房設備機器の消費電力量（kWh/h）

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      H_MR(dict): 主たる居室の暖房機器の仕様
      H_OR(dict): その他の居室の暖房機器の仕様
      H_HS(dict): 温水暖房機の仕様
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷
      L_CS_x_t_i(ndarray): 冷房区画i=1-5それぞれの冷房顕熱負荷
      L_CL_x_t_i(ndarray): 冷房区画i=1-5それぞれの冷房潜熱負荷

    Returns:
      ndarray: 居室のみを暖房する方式における主たる居室及びその他の居室に設置された暖房設備機器の消費電力量（kWh/h）

    """
    # 暖房方式及び運転方法の区分
    mode_MR, mode_OR = calc_heating_mode(region=region, H_MR=H_MR, H_OR=H_OR)

    return hwh.calc_E_E_H_d_t(H_HS, H_MR, H_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_d_t_i, L_CS_x_t_i, L_CL_x_t_i, HW, CG)


def calc_E_G_H_hs_MROR_d_t(mode_MR, mode_OR, spec_HS, spec_MR, spec_OR, L_T_H_d_t_i, HW, CG, A_A, A_MR, A_OR, region):
    """居室のみを暖房する方式における主たる居室及びその他の居室に設置された暖房設備機器のガス消費量（MJ/h）

    Args:
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      spec_HS(dict): 暖房方式及び運転方法の区分
      spec_MR(dict): 主たる居室の仕様
      spec_OR(dict): その他の居室の仕様
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分

    Returns:
      ndarray: 居室のみを暖房する方式における主たる居室及びその他の居室に設置された暖房設備機器のガス消費量（MJ/h）

    """
    return hwh.calc_E_G_H_d_t(spec_HS, spec_MR, spec_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_d_t_i, HW, CG)


def calc_E_K_H_hs_MROR_d_t(spec_HS, spec_MR, spec_OR, HW, CG, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_d_t_i):
    """居室のみを暖房する方式における主たる居室及びその他の居室に設置された暖房設備機器の灯油消費量（MJ/h）

    Args:
      spec_HS(dict): 暖房方式及び運転方法の区分
      spec_MR(dict): 主たる居室の仕様
      spec_OR(dict): その他の居室の仕様
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      L_T_H_d_t_i(ndarray): 暖房区画i=1-5それぞれの暖房負荷

    Returns:
      ndarray: 居室のみを暖房する方式における主たる居室及びその他の居室に設置された暖房設備機器の灯油消費量（MJ/h）

    """
    return hwh.calc_E_K_H_d_t(spec_HS, spec_MR, spec_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_d_t_i, HW, CG)


def calc_E_M_H_hs_MROR_d_t(region, H_HS):
    """居室のみを暖房する方式における主たる居室及びその他の居室に設置された暖房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）

    Args:
      region(int): 省エネルギー地域区分
      H_HS(dict): 温水暖房機の仕様

    Returns:
      ndarray: 居室のみを暖房する方式における主たる居室及びその他の居室に設置された暖房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）

    """
    # 実質的な温水暖房熱源の取得
    spec_HS = get_virtual_heatsource(region, H_HS)

    return hwh.calc_E_M_H_d_t(spec_HS)


# ---------------------------------------------------
# 6.3.3 居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合
# ---------------------------------------------------

def calc_E_M_H_hs_MR_d_t(A_A, A_MR, A_OR, spec_MR, spec_HS, L_H_d_t):
    """居室のみを暖房する方式における主たる居室に設置された暖房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）

    Args:
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      spec_MR(dict): 主たる居室の仕様
      spec_HS(dict): 暖房方式及び運転方法の区分
      L_H_d_t(ndarray): 暖冷房区画݅の１時間当たりの暖房負荷(MJ/h)

    Returns:
      ndarray: 居室のみを暖房する方式における主たる居室に設置された暖房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）

    """
    if spec_MR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）']:
        return hwh.calc_E_M_H_d_t(spec_HS)
    else:
        return calc_E_M_d_t(1, spec_MR, A_A, A_MR, A_OR, L_H_d_t[0])


def calc_E_M_H_hs_OR_d_t(A_A, A_MR, A_OR, spec_OR, spec_HS, L_H_d_t):
    """居室のみを暖房する方式におけるその他の居室に設置された暖房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）

    Args:
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      spec_OR(dict): その他の居室の仕様
      spec_HS(dict): 暖房方式及び運転方法の区分
      L_H_d_t(ndarray): 暖冷房区画݅の１時間当たりの暖房負荷(MJ/h)

    Returns:
      ndarray: 居室のみを暖房する方式におけるその他の居室に設置された暖房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）

    """
    # その他の居室がない場合
    if spec_OR is None:
        return np.zeros(24 * 365)

    else:

        if spec_OR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター']:
            return hwh.calc_E_M_H_d_t(spec_HS)
        else:
            return np.sum(
                [calc_E_M_d_t(i, spec_OR, A_A, A_MR, A_OR, L_H_d_t[i - 1]) for
                 i in
                 range(2, 6)], axis=0)


def calc_E_M_d_t(i, device, A_A, A_MR, A_OR, L_H_d_t):
    """暖房区画1つと1つの暖房設備機器によって消費されるその他の一次エネルギー消費量を取得する

    Args:
      i(int): 暖冷房区画の番号
      device(dict): 暖房機器の仕様
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      L_H_d_t(ndarray): 暖冷房区画݅の１時間当たりの暖房負荷(MJ/h)

    Returns:
      ndarray: 暖房区画1つと1つの暖房設備機器によって消費されるその他の一次エネルギー消費量

    """
    # 床面積
    A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)

    if device['type'] == 'ルームエアコンディショナー':
        # その他の一次エネルギー消費量の計算
        E_M_d_t = rac.get_E_M_H_d_t()

    elif device['type'] == 'FF暖房機':
        # その他の一次エネルギー消費量の計算
        E_M_d_t = ff.get_E_M_H_d_t()

    elif device['type'] == '電気蓄熱暖房器':
        # その他の一次エネルギー消費量の計算
        E_M_d_t = ets.get_E_M_H_d_t()

    elif device['type'] == '電気ヒーター床暖房':
        # その他の一次エネルギー消費量の計算
        E_M_d_t = eheater.get_E_M_H_d_t()

    elif device['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）']:
        # 温水暖房は第7節で取り扱うためここでは処理しない
        raise UserWarning(device['type'])

    elif device['type'] == 'ルームエアコンディショナー付温水床暖房機':
        # その他の一次エネルギー消費量の計算
        E_M_d_t = racfh.get_E_M_d_t()

    else:
        raise ValueError(device['type'])

    print(
        '{} E_M_d_t_{} = {} [MJ] (L_H_d_t_{} = {} [MJ)'.format(device['type'], i, np.sum(E_M_d_t), i, np.sum(L_H_d_t)))

    return E_M_d_t


# ===================================================
# 6.4 暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値 
# ===================================================

def calc_E_UT_H_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_H, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG,
                    L_T_H_d_t, L_CS_d_t, L_CL_d_t):
    """暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/h）(13)を取得する
    (12)(13)式を内部分岐して呼び出す関数

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      A_env(float): 外皮の部位の面積の合計 (m2)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      H_A(dict): 暖房方式
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      L_T_H_d_t(ndarray): 暖房区画の暖房負荷
      L_CS_d_t(ndarray): 冷房区画の冷房顕熱負荷
      L_CL_d_t(ndarray): 冷房区画の冷房潜熱負荷
      mode_H: returns: 暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/h）

    Returns:
      ndarray: 暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/h）

    """
    if mode_H == '住戸全体を連続的に暖房する方式':
        # 全館連続
        return calc_E_UT_H_d_t__modeA(H_A, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, region,
                                      L_T_H_d_t, L_CS_d_t, L_CL_d_t)
    elif mode_H == '居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合' or \
            mode_H == '設置しない':
        # 居室暖房
        return calc_E_UT_H_d_t__modeMROR(region, A_A, A_MR, A_OR, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG,
                                         L_T_H_d_t, L_CS_d_t, L_CL_d_t)
    elif mode_H is None:
        return np.zeros(24*365)
    else:
        raise ValueError(mode_H)


# ---------------------------------------------------
# 6.4.1 住戸全体を連続的に暖房する方式 
# ---------------------------------------------------

def calc_E_UT_H_d_t__modeA(H_A, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, region, L_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i):
    """暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/h）(13)を取得する

    Args:
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      A_env(float): 外皮の部位の面積の合計 (m2)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      region(int): 省エネルギー地域区分
      L_H_d_t_i(ndarray): 暖房区画の暖房負荷
      L_CS_d_t_i(ndarray): 冷房区画の冷房顕熱負荷
      L_CL_d_t_i(ndarray): 冷房区画の冷房潜熱負荷
      H_A: returns: 暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/h）

    Returns:
      ndarray: 暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/h）

    """
    # 未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数
    alpha_UT_H_A = get_alpha_UT_H_A(region)

    # VAV方式の採用
    if 'VAV' in H_A:
        VAV = H_A['VAV']

    # 全般換気機能の有無
    if 'general_ventilation' in H_A:
        general_ventilation = H_A['general_ventilation']

    # ダクトが通過する空間
    if 'duct_insulation' in H_A:
        duct_insulation = H_A['duct_insulation']

    # 定格暖房能力
    if 'q_hs_rtd_H' in H_A:
        q_hs_rtd_H = H_A['q_hs_rtd_H']
    else:
        q_hs_rtd_H = dc_spec.get_q_hs_rtd_H(region, A_A)

    # 定格風量(暖房)
    if 'V_fan_rtd_H' in H_A:
        V_fan_rtd_H = H_A['V_fan_rtd_H']
    else:
        V_fan_rtd_H = dc_spec.get_V_fan_rtd_H(q_hs_rtd_H)

    # 設計風量(暖房)
    if 'V_hs_dsgn_H' in H_A:
        V_hs_dsgn_H = H_A['V_hs_dsgn_H']
    else:
        V_hs_dsgn_H = dc_spec.get_V_fan_dsgn_H(V_fan_rtd_H)

    # 定格冷房能力
    q_hs_rtd_C = None

    # 設計風量(冷房)
    V_hs_dsgn_C = None

    # 未処理負荷を取得
    Q_UT_H_A_d_t = calc_Q_UT_H_A_d_t(A_A, A_MR, A_OR, A_env, mu_H, mu_C, q_hs_rtd_H, q_hs_rtd_C, V_hs_dsgn_H, V_hs_dsgn_C, Q,
                     VAV, general_ventilation, duct_insulation, region, L_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i)

    return Q_UT_H_A_d_t * alpha_UT_H_A


def get_table_3():
    """表 3 未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数

    Args:

    Returns:
      list: 表 3 未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数

    """
    table_3 = [
        1.61,
        1.46,
        1.32,
        1.30,
        1.20,
        1.09,
        1.12
    ]
    return table_3


def get_alpha_UT_H_A(region):
    """未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数(表3)を取得する

    Args:
      region(int): 省エネルギー地域区分

    Returns:
      float: 未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数

    """
    return get_table_3()[region - 1]


# ---------------------------------------------------
# 6.4.2 居室のみを暖房する方式 
# ---------------------------------------------------

def calc_E_UT_H_d_t__modeMROR(region, A_A, A_MR, A_OR, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG, L_T_H_d_t, L_CS_d_t, L_CL_d_t):
    """暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/h）(13)を取得する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      spec_MR(dict): 主たる居室の暖房機器の仕様
      spec_OR(dict): その他の居室の暖房機器の仕様
      spec_HS(dict): 温水暖房機の仕様
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      L_T_H_d_t(ndarray): 暖房区画の暖房負荷
      L_CS_d_t(ndarray): 冷房区画の冷房顕熱負荷
      L_CL_d_t(ndarray): 冷房区画の冷房潜熱負荷

    Returns:
      ndarray: 暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/h）

    """
    # -- 暖房機または放熱器の未処理 --
    # 暖房方式及び運転方法の区分
    if spec_OR is not None:
        # 未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数
        alpha_UT_H_MR = get_alpha_UT_H_MR(region, mode_MR)
        alpha_UT_H_OR = get_alpha_UT_H_OR(region, mode_OR)

        # 未処理暖房負荷
        Q_UT_H_MR_d_t = calc_Q_UT_H_MR_d_t(region, A_A, A_MR, A_OR, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG,
                                           L_T_H_d_t)
        Q_UT_H_OR_d_t = calc_Q_UT_H_OR_d_t(region, A_A, A_MR, A_OR, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG,
                                           L_T_H_d_t)

        # 未処理暖房負荷に未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数を掛けて合算
        Q_UT_rad = Q_UT_H_MR_d_t * alpha_UT_H_MR + Q_UT_H_OR_d_t * alpha_UT_H_OR
    else:
        # 未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数
        alpha_UT_H_MR = get_alpha_UT_H_MR(region, mode_MR)

        # 未処理暖房負荷
        Q_UT_H_MR_d_t = calc_Q_UT_H_MR_d_t(region, A_A, A_MR, A_OR, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, HW, CG,
                                           L_T_H_d_t)

        # 未処理暖房負荷に未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数を掛ける
        Q_UT_rad = Q_UT_H_MR_d_t * alpha_UT_H_MR

    # -- 熱源機の未処理 --

    has_howaterheating = spec_MR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）']
    if spec_OR is not None:
        has_howaterheating = has_howaterheating or spec_OR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター']

    if has_howaterheating:
        Q_UT_hs = hwh.calc_Q_UT_hs_d_t(spec_HS, spec_MR, spec_OR, region, A_A, A_MR, A_OR, mode_MR, mode_OR, L_T_H_d_t,
                                       HW, CG, L_CS_d_t, L_CL_d_t)

        print('Q_UT_hs = {} [MJ]'.format(np.sum(Q_UT_hs)))
    else:
        Q_UT_hs = 0.0

    # -- 熱源機未処理負荷と放熱器未処理負荷合算 --

    if spec_OR is None:
        return Q_UT_hs * alpha_UT_H_MR + Q_UT_rad
    elif spec_MR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）'] \
            and spec_OR['type'] not in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター']:
        return Q_UT_hs * alpha_UT_H_MR + Q_UT_rad
    elif spec_MR['type'] not in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター', '温水床暖房（併用運転に対応）'] \
            and spec_OR['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水暖房用ファンコンベクター']:
        return Q_UT_hs * alpha_UT_H_OR + Q_UT_rad
    else:
        return Q_UT_rad


def get_table_4():
    """表 4 未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数

    Args:

    Returns:
      list: 表 4 未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数

    """
    table_4 = [
        (1.59, 1.21, 1.59, 1.22),
        (1.66, 1.22, 1.66, 1.24),
        (1.63, 1.22, 1.63, 1.23),
        (1.60, 1.21, 1.60, 1.23),
        (1.53, 1.05, 1.53, 1.04),
        (1.57, 0.96, 1.57, 1.00),
        (1.63, 1.01, 1.63, 1.34)
    ]
    return table_4


def get_alpha_UT_H_MR(region, mode_H_MR):
    """居室のみを暖房する方式における主たる居室に設置された暖房設備の未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数(表4)を取得する

    Args:
      region(int): 省エネルギー地域区分
      mode_H_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)

    Returns:
      float: 居室のみを暖房する方式における主たる居室に設置された暖房設備の未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数

    """
    if mode_H_MR in ['ろ', '連続運転']:
        return get_table_4()[region - 1][0]
    elif mode_H_MR in ['は', '間歇運転']:
        return get_table_4()[region - 1][1]
    else:
        raise ValueError(mode_H_MR)


def get_alpha_UT_H_OR(region, mode_H_OR):
    """居室のみを暖房する方式におけるその他の居室に設置された暖房設備の未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数(表4)を取得する

    Args:
      region(int): 省エネルギー地域区分
      mode_H_OR(str): 主たる居室の運転方法 (連続運転|間歇運転)

    Returns:
      float: 居室のみを暖房する方式におけるその他の居室に設置された暖房設備の未処理暖房負荷を未処理暖房負荷の設計一次エネルギー消費量相当値に換算するための係数

    """
    if mode_H_OR in ['ろ', '連続運転']:
        return get_table_4()[region - 1][0]
    elif mode_H_OR in ['は', '間歇運転']:
        return get_table_4()[region - 1][3]
    else:
        raise ValueError(mode_H_OR)


# ===================================================
# 6.5 コージェネレーション設備又は住棟セントラル暖房設備が賄う温水暖房の熱負荷等 
# ===================================================

# ---------------------------------------------------
# 6.5.1 居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合
# ---------------------------------------------------

# ---------------------------------------------------
# 6.5.2 居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房設備を設置する場合に該当しない場合 
# ---------------------------------------------------


###################################################
# 7. 冷房設備の一次エネルギー消費量及び処理負荷と未処理負荷
###################################################

# ===================================================
# 7.1 処理負荷及び未処理負荷 
# ===================================================


def calc_cooling_load(region, A_A, A_MR, A_OR, Q, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt, underfloor_insulation, mode_C, mode_H, mode_MR, mode_OR, TS, HEX):
    """冷房負荷(MJ/h)を取得する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      NV_MR(float): 主たる居室における通風の利用における相当換気回数
      NV_OR(float): その他の居室における通風の利用における相当換気回数
      r_A_ufvnt(float): 当該住戸において、床下空間全体の面積に対する空気を供給する床下空間の面積の比 (-)
      underfloor_insulation(bool): 床下空間が断熱空間内である場合はTrue
      mode_C(str): 冷房方式
      mode_H(str): 暖房方式
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      TS(bool): 蓄熱の利用
      HEX(dict): 熱交換器型設備仕様辞書

    Returns:
      tuple(ndarray, ndarray): 冷房負荷(冷房顕熱負荷, 冷房潜熱負荷)(MJ/h)

    """

    # 運転モード
    args = dict()
    args['mode_H'] = get_mode_H_array(mode_H, mode_MR, mode_OR)
    args['mode_C'] = get_mode_C_array(mode_C)

    # 熱交換型換気
    if HEX is not None:
        hex = True
        etr_dash_t = calc_etr_dash_t(
            etr_t_raw=HEX['etr_t'],
            e=HEX.get('e'),
            C_bal=HEX.get('C_bal'),
            C_leak=HEX.get('C_leak')
        )
    else:
        hex = False
        etr_dash_t = None

    if mode_C == '住戸全体を連続的に冷房する方式' or mode_C == '居室のみを冷房する方式' or mode_C == '設置しない':
        L_CS_d_t = ld.calc_L_CS_d_t_i(
            region=region,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            mode_H=args['mode_H'],
            mode_C=args['mode_C'],
            NV_MR=NV_MR,
            NV_OR=NV_OR,
            Q=Q,
            mu_H=mu_H,
            mu_C=mu_C,
            TS=TS,
            etr_dash_t=etr_dash_t,
            hex=hex,
            r_A_ufvnt=r_A_ufvnt,
            underfloor_insulation=underfloor_insulation
        )
        L_CL_d_t = ld.calc_L_CL_d_t_i(
            region=region,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            mode=args['mode_C'],
            NV_MR=NV_MR,
            NV_OR=NV_OR,
            Q=Q,
            mu_C=mu_C,
        )

        L_CS_d_t[L_CS_d_t < 0] = 0
        L_CL_d_t[L_CL_d_t < 0] = 0

        return L_CS_d_t, L_CL_d_t
    elif mode_C is None:
        return np.zeros(24*365), np.zeros(24*365)
    else:
        raise ValueError(mode_C)


# ---------------------------------------------------
# 7.1.1 住戸全体を連続的に冷房する方式 
# ---------------------------------------------------

def calc_Q_UT_CS_A_d_t(A_A, A_MR, A_OR, A_env, mu_H, mu_C, q_hs_rtd_H, q_hs_rtd_C, V_hs_dsgn_H, V_hs_dsgn_C, Q,
                       VAV, general_ventilation, duct_insulation, region, L_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i):
    """住戸全体を連続的に冷房する方式における冷房設備の未処理冷房顕熱負荷（MJ/h）(15)を取得する

    Args:
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      q_hs_rtd_H(float): 熱源機の暖房時の定格出力 (MJ/h)
      q_hs_rtd_C(float): 熱源機の冷房時の定格出力 (MJ/h)
      V_hs_dsgn_H(float): 暖房時の設計風量（m3/h）
      V_hs_dsgn_C(float): 冷房時の設計風量（m3/h）
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      VAV(bool): VAV有無
      general_ventilation(bool): 全版換気の機能の有無
      duct_insulation(str): ダクトが通過する空間
      region(int): 省エネルギー地域区分
      L_H_d_t(ndarray): 暖房区画の暖房負荷
      L_CS_d_t(ndarray): 冷房区画の冷房顕熱負荷
      L_CL_d_t(ndarray): 冷房区画の冷房潜熱負荷
      A_env: param L_H_d_t_i:
      L_CS_d_t_i: param L_CL_d_t_i:
      L_H_d_t_i: 
      L_CL_d_t_i: 

    Returns:
      ndarray: 住戸全体を連続的に冷房する方式における冷房設備の未処理冷房顕熱負荷（MJ/h）

    """
    _, _, Q_UT_CS_d_t_i, _, _, _, _, _, _, _, _= dc.calc_Q_UT_A(A_A, A_MR, A_OR, A_env, mu_H, mu_C,
                                                               q_hs_rtd_H, q_hs_rtd_C, V_hs_dsgn_H, V_hs_dsgn_C, Q, VAV,
                                                               general_ventilation, duct_insulation, region,
                                                               L_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i)
    Q_UT_CS_A_d_t = np.sum(Q_UT_CS_d_t_i, axis=0)

    return Q_UT_CS_A_d_t


def calc_Q_UT_CL_A_d_t(A_A, A_MR, A_OR, A_env, mu_H, mu_C, q_hs_rtd_H, q_hs_rtd_C, V_hs_dsgn_H, V_hs_dsgn_C, Q,
                       VAV, general_ventilation, duct_insulation, region, L_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i):
    """住戸全体を連続的に冷房する方式における冷房設備の未処理冷房潜熱負荷（MJ/h）(16)を取得する

    Args:
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      q_hs_rtd_H(float): 熱源機の暖房時の定格出力 (MJ/h)
      q_hs_rtd_C(float): 熱源機の冷房時の定格出力 (MJ/h)
      V_hs_dsgn_H(float): 暖房時の設計風量（m3/h）
      V_hs_dsgn_C(float): 冷房時の設計風量（m3/h）
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      VAV(bool): VAV有無
      general_ventilation(bool): 全版換気の機能の有無
      duct_insulation(str): ダクトが通過する空間
      region(int): 省エネルギー地域区分
      L_H_d_t(ndarray): 暖房区画の暖房負荷
      L_CS_d_t(ndarray): 冷房区画の冷房顕熱負荷
      L_CL_d_t(ndarray): 冷房区画の冷房潜熱負荷
      A_env: param L_H_d_t_i:
      L_CS_d_t_i: param L_CL_d_t_i:
      L_H_d_t_i: 
      L_CL_d_t_i: 

    Returns:
      ndarray: 住戸全体を連続的に冷房する方式における冷房設備の未処理冷房潜熱負荷（MJ/h）

    """
    _, _, _, Q_UT_CL_d_t_i, _, _, _, _, _, _, _= dc.calc_Q_UT_A(A_A, A_MR, A_OR, A_env, mu_H, mu_C,
                                                               q_hs_rtd_H, q_hs_rtd_C, V_hs_dsgn_H, V_hs_dsgn_C, Q, VAV,
                                                               general_ventilation, duct_insulation, region,
                                                               L_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i)
    Q_UT_CL_A_d_t = np.sum(Q_UT_CL_d_t_i, axis=0)

    return Q_UT_CL_A_d_t


# ---------------------------------------------------
# 7.1.2 居室のみを冷房する方式
# ---------------------------------------------------

def calc_Q_T_CS_MR_d_t(**args):
    """居室のみを冷房する方式における主たる居室に設置された冷房設備の処理冷房顕熱負荷 (17a)を計算する

    Args:
      **args: 

    Returns:
      ndarray: 居室のみを冷房する方式における主たる居室に設置された冷房設備の処理冷房顕熱負荷

    """
    # i=1の冷房区画の処理冷房顕熱負荷を計算して合算
    return get_Q_T_CS_d_t_i(i=1, **args)


def calc_Q_T_CL_MR_d_t(**args):
    """居室のみを冷房する方式における主たる居室に設置された冷房設備の処理冷房潜熱負荷 (17b)を計算する

    Args:
      **args: 

    Returns:
      ndarray: 居室のみを冷房する方式における主たる居室に設置された冷房設備の処理冷房潜熱負荷

    """
    # i=1の冷房区画の処理冷房潜熱負荷を計算して合算
    return get_Q_T_CL_d_t_i(i=1, **args)


def calc_Q_UT_CS_MR_d_t(**args):
    """居室のみを冷房する方式における主たる居室に設置された冷房設備の未処理冷房顕熱負荷 (17c)を計算する

    Args:
      **args: 

    Returns:
      ndarray: 居室のみを冷房する方式における主たる居室に設置された冷房設備の未処理冷房顕熱負荷

    """
    # i=1の冷房区画の未処理冷房顕熱負荷を計算して合算
    return get_Q_UT_CS_d_t_i(i=1, **args)


def calc_Q_UT_CL_MR_d_t(**args):
    """居室のみを冷房する方式における主たる居室に設置された冷房設備の未処理冷房潜熱負荷 (17d)を計算する

    Args:
      **args: 

    Returns:
      ndarray: 居室のみを冷房する方式における主たる居室に設置された冷房設備の未処理冷房潜熱負荷

    """
    # i=1の冷房区画の未処理冷房潜熱負荷を計算して合算
    return get_Q_UT_CL_d_t_i(i=1, **args)


def calc_Q_T_CS_OR_d_t(**args):
    """居室のみを冷房する方式におけるその他の居室に設置された冷房設備の処理冷房顕熱負荷 (18a)を計算する

    Args:
      **args: 

    Returns:
      ndarray: 居室のみを冷房する方式におけるその他の居室に設置された冷房設備の処理冷房顕熱負荷

    """
    # i=2～5の冷房区画の処理冷房顕熱負荷を計算して合算
    return np.sum([get_Q_T_CS_d_t_i(i, **args) for i in range(2, 6)], axis=0)


def calc_Q_T_CL_OR_d_t(**args):
    """居室のみを冷房する方式におけるその他の居室に設置された冷房設備の処理冷房潜熱負荷 (18b)を計算する

    Args:
      **args: 

    Returns:
      ndarray: 居室のみを冷房する方式におけるその他の居室に設置された冷房設備の処理冷房潜熱負荷

    """
    # i=2～5の冷房区画の処理冷房潜熱負荷を計算して合算
    return np.sum([get_Q_T_CL_d_t_i(i, **args) for i in range(2, 6)], axis=0)


def calc_Q_UT_CS_OR_d_t(**args):
    """居室のみを冷房する方式におけるその他の居室に設置された冷房設備の未処理冷房顕熱負荷 (18c)を計算する

    Args:
      **args: 

    Returns:
      ndarray: 居室のみを冷房する方式におけるその他の居室に設置された冷房設備の未処理冷房顕熱負荷

    """
    # i=2～5の冷房区画の未処理冷房顕熱負荷を計算して合算
    return np.sum([get_Q_UT_CS_d_t_i(i, **args) for i in range(2, 6)], axis=0)


def calc_Q_UT_CL_OR_d_t(**args):
    """居室のみを冷房する方式におけるその他の居室に設置された冷房設備の未処理冷房潜熱負荷 (18d)を計算する

    Args:
      **args: 

    Returns:
      ndarray: 居室のみを冷房する方式におけるその他の居室に設置された冷房設備の未処理冷房潜熱負荷

    """
    # i=2～5の冷房区画の未処理冷房潜熱負荷を計算して合算
    return np.sum([get_Q_UT_CL_d_t_i(i, **args) for i in range(2, 6)], axis=0)


# (19)(20)式は section4_1_Q.pyに定義

# ===================================================
# 7.2 冷房設備のエネルギー消費量 
# ===================================================

def calc_E_E_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A=None, C_MR=None, C_OR=None, L_H_d_t=None,
                   L_CS_d_t=None, L_CL_d_t=None):
    """冷房設備の消費電力量（kWh/h） (21a)を取得する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      A_env(float): 外皮の部位の面積の合計 (m2)
      mu_H(float): 当該住戸の暖房期の日射取得係数 ((W/m2)/(W/m2))
      mu_C(float): 当該住戸の冷房期の日射取得係数 ((W/m2)/(W/m2))
      Q(float): 当該住戸の熱損失係数 (W/m2K)
      C_A(dict, optional): 冷房方式 (Default value = None)
      C_MR(dict, optional): 主たる居室の冷房機器 (Default value = None)
      C_OR(dict, optional): その他の居室の冷房機器 (Default value = None)
      L_H_d_t(ndarray, optional): 暖房区画の暖房負荷 (Default value = None)
      L_CS_d_t(ndarray, optional): 冷房区画の冷房顕熱負荷 (Default value = None)
      L_CL_d_t(ndarray, optional): 冷房区画の冷房潜熱負荷 (Default value = None)

    Returns:
      ndarray: 冷房設備の消費電力量（kWh/h）

    """
    return calc_E_E_C_hs_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_H_d_t, L_CS_d_t, L_CL_d_t)


def calc_E_G_C_d_t(**args):
    """冷房設備のガス消費量（MJ/h）(21b)を取得する

    Args:
      **args: 

    Returns:
      ndarray: 冷房設備のガス消費量

    """
    return calc_E_G_C_hs_d_t()


def calc_E_K_C_d_t(**args):
    """冷房設備の灯油消費量（MJ/h）(21c)を取得する

    Args:
      **args: 

    Returns:
      ndarray: 冷房設備の灯油消費量

    """
    return calc_E_K_C_hs_d_t()


def calc_E_M_C_d_t(**args):
    """冷房設備のその他の燃料による一次エネルギー消費量（MJ/h）(21d)を取得する

    Args:
      **args: 

    Returns:
      ndarray: 冷房設備のその他の燃料による一次エネルギー消費量

    """
    return calc_E_M_C_hs_d_t()


# ===================================================
# 7.3 冷房設備機器のエネルギー消費量 
# ===================================================

def calc_E_E_C_hs_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_H_d_t, L_CS_d_t, L_CL_d_t):
    """冷房設備機器の消費電力量（kWh/h）(22a, 23a)を取得する

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
      L_H_d_t(ndarray): 暖房区画の暖房負荷
      L_CS_d_t(ndarray): 冷房区画の冷房顕熱負荷
      L_CL_d_t(ndarray): 冷房区画の冷房潜熱負荷

    Returns:
      ndarray: 冷房設備機器の消費電力量（kWh/h）

    """
    if C_A is not None:
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
            EquipmentSpec = '入力しない'
            q_hs_rtd_C = dc_spec.get_q_hs_rtd_C(region, A_A)
            q_hs_mid_C = dc_spec.get_q_hs_mid_C(q_hs_rtd_C)
            q_hs_min_C = dc_spec.get_q_hs_min_C(q_hs_rtd_C)
            P_hs_rtd_C = dc_spec.get_P_hs_rtd_C(q_hs_rtd_C)
            V_fan_rtd_C = dc_spec.get_V_fan_rtd_C(q_hs_rtd_C)
            V_fan_mid_C = dc_spec.get_V_fan_mid_C(q_hs_mid_C)
            P_fan_rtd_C = dc_spec.get_P_fan_rtd_C(V_fan_rtd_C)
            P_fan_mid_C = dc_spec.get_P_fan_mid_C(V_fan_mid_C)
            P_hs_mid_C = np.NAN
        elif C_A['EquipmentSpec'] == '定格能力試験の値を入力する':
            EquipmentSpec = '定格能力試験の値を入力する'
            q_hs_rtd_C = C_A['q_hs_rtd_C']
            P_hs_rtd_C = C_A['P_hs_rtd_C']
            V_fan_rtd_C = C_A['V_fan_rtd_C']
            P_fan_rtd_C = C_A['P_fan_rtd_C']
            q_hs_mid_C = dc_spec.get_q_hs_mid_C(q_hs_rtd_C)
            q_hs_min_C = dc_spec.get_q_hs_min_C(q_hs_rtd_C)
            V_fan_mid_C = dc_spec.get_V_fan_mid_C(q_hs_mid_C)
            P_fan_mid_C = dc_spec.get_P_fan_mid_C(V_fan_mid_C)
            P_hs_mid_C = np.NAN
        elif C_A['EquipmentSpec'] == '定格能力試験と中間能力試験の値を入力する':
            EquipmentSpec = '定格能力試験と中間能力試験の値を入力する'
            q_hs_rtd_C = C_A['q_hs_rtd_C']
            P_hs_rtd_C = C_A['P_hs_rtd_C']
            V_fan_rtd_C = C_A['V_fan_rtd_C']
            P_fan_rtd_C = C_A['P_fan_rtd_C']
            q_hs_mid_C = C_A['q_hs_mid_C']
            P_hs_mid_C = C_A['P_hs_mid_C']
            V_fan_mid_C = C_A['V_fan_mid_C']
            P_fan_mid_C = C_A['P_fan_mid_C']
            q_hs_min_C = dc_spec.get_q_hs_min_C(q_hs_rtd_C)
        else:
            raise ValueError(C_A['EquipmentSpec'])

        # 設計風量(冷房)
        if 'V_hs_dsgn_C' in C_A:
            V_hs_dsgn_C = C_A['V_hs_dsgn_C']
        else:
            V_hs_dsgn_C = dc_spec.get_V_fan_dsgn_C(V_fan_rtd_C)

        # 定格暖房能力
        q_hs_rtd_H = None

        # 設計風量(暖房)
        V_hs_dsgn_H = None

        _, _, _, _, \
        Theta_hs_out_d_t, Theta_hs_in_d_t, X_hs_out_d_t, \
        X_hs_in_d_t, V_hs_supply_d_t, V_hs_vent_d_t, _ = dc.calc_Q_UT_A(A_A, A_MR, A_OR, A_env, mu_H, mu_C, q_hs_rtd_H,
                                                                       q_hs_rtd_C, V_hs_dsgn_H, V_hs_dsgn_C, Q, VAV,
                                                                       general_ventilation, duct_insulation, region,
                                                                       L_H_d_t, L_CS_d_t, L_CL_d_t)

        E_E_C_d_t_i = dc_a.get_E_E_C_d_t(
            Theta_hs_out_d_t=Theta_hs_out_d_t,
            Theta_hs_in_d_t=Theta_hs_in_d_t,
            X_hs_out_d_t=X_hs_out_d_t,
            X_hs_in_d_t=X_hs_in_d_t,
            V_hs_supply_d_t=V_hs_supply_d_t,
            V_hs_vent_d_t=V_hs_vent_d_t,
            q_hs_rtd_C=q_hs_rtd_C,
            V_hs_dsgn_C=V_hs_dsgn_C,
            q_hs_mid_C=q_hs_mid_C,
            q_hs_min_C=q_hs_min_C,
            P_fan_rtd_C=P_fan_rtd_C,
            P_fan_mid_C=P_fan_mid_C,
            P_hs_rtd_C=P_hs_rtd_C,
            P_hs_mid_C=P_hs_mid_C,
            V_fan_rtd_C=V_fan_rtd_C,
            V_fan_mid_C=V_fan_mid_C,
            EquipmentSpec=EquipmentSpec,
            region=region
        )

        return E_E_C_d_t_i
    elif C_MR is not None or C_OR is not None:
        # 消費電力量の計算 (23a)
        return calc_E_E_C_hs_MR_d_t(region, A_A, A_MR, A_OR, C_MR, L_CS_d_t, L_CL_d_t) \
               + calc_E_E_C_hs_OR_d_t(region, A_A, A_MR, A_OR, C_OR, L_CS_d_t, L_CL_d_t)
    else:
        return np.zeros(24*365)


def get_E_G_C_hs_d_t():
    """冷房設備機器のガス消費量（MJ/h）(22b)を計算する

    Args:

    Returns:
      ndarray: 冷房設備機器のガス消費量（MJ/h）

    """
    return dc.get_E_G_C_d_t()


def get_E_K_C_hs_d_t():
    """冷房設備機器の灯油消費量（MJ/h）(22c)を計算する

    Args:

    Returns:
      ndarray: 冷房設備機器の灯油消費量（MJ/h）

    """
    return dc.get_E_K_C_d_t()


def get_E_M_C_hs_d_t():
    """冷房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）(22d)を計算する

    Args:

    Returns:
      ndarray: 冷房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）

    """
    return dc.get_E_M_C_d_t()


def calc_E_G_C_hs_d_t():
    """冷房設備機器のガス消費量（MJ/h）(23b)を計算する

    Args:

    Returns:
      ndarray: 冷房設備機器のガス消費量（MJ/h）

    """
    return calc_E_G_C_hs_MR_d_t() + calc_E_G_C_hs_OR_d_t()


def calc_E_K_C_hs_d_t():
    """冷房設備機器の灯油消費量（MJ/h）(23c)を計算する

    Args:

    Returns:
      ndarray: 冷房設備機器の灯油消費量（MJ/h）

    """
    return calc_E_K_C_hs_MR_d_t() + calc_E_K_C_hs_OR_d_t()


def calc_E_M_C_hs_d_t():
    """冷房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）(22d, 23d)を計算する

    Args:

    Returns:
      ndarray: 冷房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）

    """
    return calc_E_M_C_hs_MR_d_t() + calc_E_M_C_hs_OR_d_t()


def calc_E_E_C_hs_MR_d_t(region, A_A, A_MR, A_OR, C_MR, L_CS_d_t, L_CL_d_t):
    """居室のみを冷房する方式における主たる居室に設置された冷房設備機器の消費電力（kWh/h） (24a)を計算する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      C_MR(dict): 主たる居室の冷房機器
      C_OR(dict): その他の居室の冷房機器
      L_CS_d_t(ndarray): 冷房区画の冷房顕熱負荷
      L_CL_d_t(ndarray): 冷房区画の冷房潜熱負荷

    Returns:
      ndarray: 居室のみを冷房する方式における主たる居室に設置された冷房設備機器の消費電力（kWh/h）

    """
    spec_MR = C_MR

    if spec_MR['type'] == '設置しない' or spec_MR['type'] == 'その他':
        spec_MR = get_default_cooling_spec()

    E_E_C_d_t_i = calc_E_E_C_hs_d_t_i(1, spec_MR, region, A_A, A_MR, A_OR, L_CS_d_t, L_CL_d_t)

    return E_E_C_d_t_i


def calc_E_G_C_hs_MR_d_t():
    """居室のみを冷房する方式における主たる居室に設置された冷房設備機器のガス消費量（MJ/h）(24b)を計算する

    Args:

    Returns:
      ndarray: 居室のみを冷房する方式における主たる居室に設置された冷房設備機器のガス消費量（MJ/h）

    """
    return rac.get_E_G_C_d_t()


def calc_E_K_C_hs_MR_d_t():
    """居室のみを冷房する方式における主たる居室に設置された冷房設備機器の灯油消費量（MJ/h）(24c)を計算する

    Args:

    Returns:
      ndarray: 居室のみを冷房する方式における主たる居室に設置された冷房設備機器の灯油消費量（MJ/h）

    """
    return rac.get_E_K_C_d_t()


def calc_E_M_C_hs_MR_d_t():
    """居室のみを冷房する方式における主たる居室に設置された冷房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）(24d)を計算する

    Args:

    Returns:
      ndarray: 居室のみを冷房する方式における主たる居室に設置された冷房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）

    """
    return rac.get_E_M_C_d_t()


def calc_E_E_C_hs_OR_d_t(region, A_A, A_MR, A_OR, C_OR, L_CS_d_t, L_CL_d_t):
    """居室のみを冷房する方式におけるその他の居室に設置された冷房設備機器の消費電力（kWh/h） (25a)を計算する

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      C_OR(dict): その他の居室の冷房機器
      L_CS_d_t(ndarray): 冷房区画の冷房顕熱負荷
      L_CL_d_t(ndarray): 冷房区画の冷房潜熱負荷

    Returns:
      ndarray: 居室のみを冷房する方式におけるその他の居室に設置された冷房設備機器の消費電力（kWh/h）

    """
    # その他の居室がない場合
    if A_OR == 0 or C_OR is None:
        return np.zeros(24 * 365)

    spec_OR = C_OR

    if spec_OR['type'] == '設置しない' or spec_OR['type'] == 'その他':
        spec_OR = get_default_cooling_spec()

    tmp = []
    for i in [3, 4, 5]:
        E_E_C_d_t_i = calc_E_E_C_hs_d_t_i(i, spec_OR, region, A_A, A_MR, A_OR, L_CS_d_t, L_CL_d_t)
        tmp.append(E_E_C_d_t_i)

    return np.sum(tmp, axis=0)


def calc_E_E_C_hs_d_t_i(i, device, region, A_A, A_MR, A_OR, L_CS_d_t, L_CL_d_t):
    """暖冷房区画𝑖に設置された冷房設備機器の消費電力量（kWh/h）を計算する

    Args:
      i(int): 暖冷房区画の番号
      device(dict): 暖冷房機器の仕様
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      L_CS_d_t(ndarray): 冷房区画の冷房顕熱負荷
      L_CL_d_t(ndarray): 冷房区画の冷房潜熱負荷

    Returns:
      ndarray: 暖冷房区画𝑖に設置された冷房設備機器の消費電力量（kWh/h）

    """
    if device['type'] == 'ルームエアコンディショナー':

        # 仕様の取得
        A_HCZ_i = calc_A_HCZ_i(i, A_A, A_MR, A_OR)
        q_rtd_C = rac_spec.get_q_rtd_C(A_HCZ_i)
        e_rtd_C = rac_spec.get_e_rtd_C(device['e_class'], q_rtd_C)

        # 電力消費量の計算
        E_E_C_d_t_i = rac.calc_E_E_C_d_t(
            region=region,
            q_rtd_C=q_rtd_C,
            e_rtd_C=e_rtd_C,
            dualcompressor=device['dualcompressor'],
            L_CS_d_t=L_CS_d_t[i - 1],
            L_CL_d_t=L_CL_d_t[i - 1]
        )
    else:
        raise ValueError(device['type'])

    print('{} E_E_C_d_t_{} = {} [kWh] (L_H_d_t_{} = {} [MJ])'.format(device['type'], i, np.sum(E_E_C_d_t_i), i,
                                                                     np.sum(L_CS_d_t + L_CL_d_t)))

    return E_E_C_d_t_i



def calc_E_G_C_hs_OR_d_t():
    """居室のみを冷房する方式におけるその他の居室に設置された冷房設備機器のガス消費量（MJ/h）(25b)を計算する

    Args:

    Returns:
      ndarray: 居室のみを冷房する方式におけるその他の居室に設置された冷房設備機器のガス消費量（MJ/h）

    """
    return np.sum([rac.get_E_G_C_d_t() for i in range(2, 6)], axis=0)


def calc_E_K_C_hs_OR_d_t():
    """居室のみを冷房する方式におけるその他の居室に設置された冷房設備機器の灯油消費量（MJ/h）(25c)を計算する

    Args:

    Returns:
      ndarray: 居室のみを冷房する方式におけるその他の居室に設置された冷房設備機器の灯油消費量（MJ/h）

    """
    return np.sum([rac.get_E_K_C_d_t() for i in range(2, 6)], axis=0)


def calc_E_M_C_hs_OR_d_t():
    """居室のみを冷房する方式におけるその他の居室に設置された冷房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）(25d)を計算する

    Args:

    Returns:
      ndarray: 居室のみを冷房する方式におけるその他の居室に設置された冷房設備機器のその他の燃料による一次エネルギー消費量（MJ/h）

    """
    return np.sum([rac.get_E_M_C_d_t() for i in range(2, 6)], axis=0)


def calc_E_UT_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_H_d_t, L_CS_d_t, L_CL_d_t, mode_C):
    """冷房設備の未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/h）を計算する

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
      L_CS_d_t(ndarray): 冷房区画の冷房顕熱負荷
      L_CL_d_t(ndarray): 冷房区画の冷房潜熱負荷
      mode_C(str): 冷房方式
      L_H_d_t: returns: 冷房設備の未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/h）

    Returns:
      ndarray: 冷房設備の未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/h）

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

        # 定格風量（冷房）
        if 'V_fan_rtd_C' in C_A:
            V_fan_rtd_C = C_A['V_fan_rtd_C']
        else:
            V_fan_rtd_C = dc_spec.get_V_fan_rtd_H(q_hs_rtd_C)

        # 設計風量(冷房)
        if 'V_hs_dsgn_C' in C_A:
            V_hs_dsgn_C = C_A['V_hs_dsgn_C']
        else:
            V_hs_dsgn_C = dc_spec.get_V_fan_dsgn_C(V_fan_rtd_C)

        # 定格暖房能力
        q_hs_rtd_H = None

        # 設計風量(暖房)
        V_hs_dsgn_H = None

        E_UT_C_d_t, _, _, _, _, _, \
        _, _, _, _, _ = dc.calc_Q_UT_A(A_A, A_MR, A_OR, A_env, mu_H, mu_C, q_hs_rtd_H, q_hs_rtd_C, V_hs_dsgn_H, V_hs_dsgn_C, Q,
             VAV, general_ventilation, duct_insulation, region, L_H_d_t, L_CS_d_t, L_CL_d_t)

        E_UT_C_d_t = E_UT_C_d_t

    else:
        E_UT_C_d_t = np.zeros(24 * 365)


    return E_UT_C_d_t
