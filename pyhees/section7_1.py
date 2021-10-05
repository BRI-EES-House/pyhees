# ============================================================================
# 第七章 給湯設備
# 第一節 給湯設備
# Ver.18（エネルギー消費性能計算プログラム（住宅版）Ver.02.05～）
# ============================================================================


import numpy as np
from functools import lru_cache

import pyhees.section7_1_b as default
import pyhees.section7_1_c as gas
import pyhees.section7_1_d as oil
import pyhees.section7_1_e as eheatpump
import pyhees.section7_1_f as eheater
import pyhees.section7_1_g as hybrid_gas
import pyhees.section7_1_g_3 as hybrid_gas_3
import pyhees.section7_1_h as gas_hybrid
import pyhees.section7_1_i as whybrid
import pyhees.section7_1_j as watersaving
import pyhees.section7_1_m as schedule

import pyhees.section9_2 as lss
import pyhees.section9_3 as ass

from pyhees.section11_1 import load_outdoor, get_Theta_ex
from pyhees.section11_2 import load_solrad
from pyhees.section11_3 import load_schedule, get_schedule_hw


# ============================================================================
# 5. 給湯設備によるエネルギー消費量
# ============================================================================


# ============================================================================
# 5.1 消費電力量
# ============================================================================

@lru_cache()
def calc_hotwater_load(n_p, region, sol_region, has_bath, bath_function, pipe_diameter, kitchen_watersaving_A,
                      kitchen_watersaving_C, shower_watersaving_A, shower_watersaving_B, washbowl_watersaving_C,
                      bath_insulation,
                      type=None, ls_type=None, A_sp=None, P_alpha_sp=None, P_beta_sp=None, W_tnk_ss=None,
                      hotwater_use=None, heating_flag_d=None, A_col=None, P_alpha=None, P_beta=None, V_fan_P0=None,
                      d0=None, d1=None, m_fan_test=None, W_tnk_ass=None
                      ):
    """給湯負荷の計算

    :param n_p: 仮想居住人数 (人)
    :type n_p: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param has_bath: 浴室等の有無
    :type has_bath: bool
    :param bath_function: ふろ機能の種類
    :type bath_function: str
    :param pipe_diameter: ヘッダー分岐後の径
    :type pipe_diameter: str
    :param kitchen_watersaving_A: 台所水栓の手元止水機能の有無
    :type kitchen_watersaving_A: bool
    :param kitchen_watersaving_C: 台所水栓の水優先吐水機能の有無
    :type kitchen_watersaving_C: bool
    :param shower_watersaving_A: 浴室シャワー水栓の手元止水機能の有無
    :type shower_watersaving_A: bool
    :param shower_watersaving_B: 浴室シャワー水栓の小流量吐水機能の有無
    :type shower_watersaving_B: bool
    :param washbowl_watersaving_C: 洗面水栓の水優先吐水機能の有無
    :type washbowl_watersaving_C: bool
    :param bath_insulation: 浴槽の断熱の有無
    :type bath_insulation: bool
    :param type: 太陽熱利用設備の種類 (液体集熱式,空気集熱式,None)
    :type type: str
    :param ls_type: 液体集熱式太陽熱利用設備の種類 (太陽熱温水器,ソーラーシステム)
    :type ls_type: str
    :param A_sp: 太陽熱集熱部の有効集熱面積 (m2)
    :type A_sp: float
    :param P_alpha_sp: 太陽熱集熱部の方位角 (°)
    :type P_alpha_sp: float
    :param P_beta_sp: 太陽熱集熱部の傾斜角 (°)
    :type P_beta_sp: float
    :param W_tnk_ss: ソーラーシステムのタンク容量 (L)
    :type W_tnk_ss: float
    :param hotwater_use: 空気集熱式太陽熱利用設備が給湯部を有する場合はTrue
    :type hotwater_use: bool
    :param heating_flag_d: 暖房日
    :type heating_flag_d: ndarray
    :param A_col: 集熱器群の面積 (m2)
    :type A_col: tuple
    :param P_alpha: 方位角 (°)
    :type P_alpha: float
    :param P_beta: 傾斜角 (°)
    :type P_beta: float
    :param V_fan_P0: 空気搬送ファンの送風機特性曲線において機外静圧をゼロとしたときの空気搬送ファンの風量 (m3/h)
    :type V_fan_P0: float
    :param d0: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の切片 (-)
    :type d0: tuple
    :param d1: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K))
    :type d1: tuple
    :param m_fan_test: 集熱器群を構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2))
    :type m_fan_test: tuple
    :param W_tnk_ass: タンク容量 (L)
    :type W_tnk_ass: float
    :return: 1日当たりの給湯設備付加
    :rtype: dict
    """


    # 生活スケジュール
    schedule = load_schedule()
    schedule_hw = get_schedule_hw(schedule)

    # 外部環境
    outdoor = load_outdoor()
    Theta_ex_d_t = get_Theta_ex(region, outdoor)

    # ----- 14. 夜間平均外気温度 -----

    # 夜間平均外気温度 (℃) (15)
    Theta_ex_Nave_d = get_Theta_ex_Nave_d(Theta_ex_d_t)

    # ----- 13. 日平均外気温度 -----

    # 日平均外気温度 (℃) (14)
    theta_ex_d_Ave_d = get_theta_ex_d_Ave_d(Theta_ex_d_t)

    # ----- 12. 日平均給水温度 -----

    # 期間平均外気温度 (℃) (13)
    Theta_ex_prd_Ave_d = get_Theta_ex_prd_Ave_d(theta_ex_d_Ave_d)

    # 日平均給水温度 (℃) (12)
    Theta_wtr_d = get_Theta_wtr_d(region, Theta_ex_prd_Ave_d)

    # ----- 11. 浴槽沸かし直しによる給湯熱負荷 -----

    # 浴槽沸かし直しによる給湯熱負荷 (MJ/h) (10)
    L_ba_d_t = calc_L_ba_d_t(bath_insulation, schedule_hw, has_bath, theta_ex_d_Ave_d, n_p)

    # ----- 10. 基準給湯量 -----

    # 基準給湯量 (L/h) (7)
    W_k_d_t = calc_W_k_d_t(n_p, schedule_hw)
    W_s_d_t = calc_W_s_d_t(n_p, schedule_hw, has_bath)
    W_w_d_t = calc_W_w_d_t(n_p, schedule_hw)
    W_b1_d_t = calc_W_b1_d_t(n_p, schedule_hw, has_bath, bath_function)
    W_b2_d_t = calc_W_b2_d_t(n_p, schedule_hw, has_bath, bath_function)

    # 浴槽水栓さし湯時における基準給湯量 (L/h) (9)
    W_ba1_d_t = calc_W_ba1_d_t(bath_function, L_ba_d_t, Theta_wtr_d)

    # ----- 9. 節湯補正給湯量 -----

    # 節湯補正給湯量 (L/h) (6)
    W_dash_k_d_t = calc_W_dash_k_d_t(W_k_d_t, kitchen_watersaving_A, kitchen_watersaving_C, pipe_diameter, Theta_wtr_d)
    W_dash_s_d_t = calc_W_dash_s_d_t(W_s_d_t, shower_watersaving_A, shower_watersaving_B, pipe_diameter)
    W_dash_w_d_t = calc_W_dash_w_d_t(W_w_d_t, washbowl_watersaving_C, pipe_diameter, Theta_wtr_d)
    W_dash_b1_d_t = calc_W_dash_b1_d_t(W_b1_d_t, pipe_diameter)
    W_dash_b2_d_t = calc_W_dash_b2_d_t(W_b2_d_t)
    W_dash_ba1_d_t = calc_W_dash_ba1_d_t(W_ba1_d_t, pipe_diameter)

    # ----- 8. 節湯補正給湯熱負荷 -----

    # 基準給湯温度 (℃)
    Theta_sw_k = get_Theta_sw_k()
    Theta_sw_s = get_Theta_sw_s()
    Theta_sw_w = get_Theta_sw_w()

    # 節湯補正給湯熱負荷 (MJ/h) (5)
    L_dash_k_d_t = get_L_dash_k_d_t(W_dash_k_d_t, Theta_sw_k, Theta_wtr_d)
    L_dash_s_d_t = get_L_dash_s_d_t(W_dash_s_d_t, Theta_sw_s, Theta_wtr_d)
    L_dash_w_d_t = get_L_dash_w_d_t(W_dash_w_d_t, Theta_sw_w, Theta_wtr_d)
    L_dash_b1_d_t, L_dash_b2_d_t = get_L_dash_bx_d_t(W_dash_b1_d_t, W_dash_b2_d_t, Theta_wtr_d, has_bath, bath_function)
    L_dash_ba1_d_t, L_dash_ba2_d_t = get_L_dash_bax_d_t(W_dash_ba1_d_t, Theta_wtr_d, L_ba_d_t, has_bath, bath_function)

    # ----- 7. 太陽熱補正給湯熱負荷 -----

    # 太陽熱利用給湯設備による補正集熱量
    L_sun_d_t = calc_L_sun_d_t(
        region=region,
        sol_region=sol_region,
        solar_device=type,
        ls_type=ls_type,
        A_sp=A_sp,
        P_alpha_sp=P_alpha_sp,
        P_beta_sp=P_beta_sp,
        W_tnk_ss=W_tnk_ss,
        hotwater_use=hotwater_use,
        heating_flag_d=heating_flag_d,
        A_col=A_col,
        P_alpha=P_alpha,
        P_beta=P_beta,
        V_fan_P0=V_fan_P0,
        d0=d0,
        d1=d1,
        m_fan_test=m_fan_test,
        W_tnk_ass=W_tnk_ass,
        Theta_wtr_d=Theta_wtr_d,
        L_dash_k_d_t=L_dash_k_d_t,
        L_dash_s_d_t=L_dash_s_d_t,
        L_dash_w_d_t=L_dash_w_d_t,
        L_dash_b1_d_t=L_dash_b1_d_t,
        L_dash_b2_d_t=L_dash_b2_d_t,
        L_dash_ba1_d_t=L_dash_ba1_d_t
    )

    # 太陽熱補正給湯熱負荷
    L_dashdash_k_d_t = calc_L_dashdash_k_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t,
                                            L_dash_ba1_d_t,
                                            L_sun_d_t)
    L_dashdash_s_d_t = calc_L_dashdash_s_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t,
                                            L_dash_ba1_d_t,
                                            L_sun_d_t)
    L_dashdash_w_d_t = calc_L_dashdash_w_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t,
                                            L_dash_ba1_d_t,
                                            L_sun_d_t)
    L_dashdash_b1_d_t = calc_L_dashdash_b1_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t,
                                              L_dash_ba1_d_t, L_sun_d_t)
    L_dashdash_b2_d_t = calc_L_dashdash_b2_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t,
                                              L_dash_ba1_d_t, L_sun_d_t)
    L_dashdash_ba1_d_t = calc_L_dashdash_ba1_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t,
                                                L_dash_ba1_d_t, L_sun_d_t)
    L_dashdash_ba2_d_t = get_L_dashdash_ba2_d_t(L_dash_ba2_d_t)

    print('L_ba = {}'.format(np.sum(L_ba_d_t)))

    print('W_k = {}'.format(np.sum(W_k_d_t)))
    print('W_s = {}'.format(np.sum(W_s_d_t)))
    print('W_w = {}'.format(np.sum(W_w_d_t)))
    print('W_b1 = {}'.format(np.sum(W_b1_d_t)))
    print('W_b2 = {}'.format(np.sum(W_b2_d_t)))
    print('W_ba1 = {}'.format(np.sum(W_ba1_d_t)))

    print('W_dash_k = {}'.format(np.sum(W_dash_k_d_t)))
    print('W_dash_s = {}'.format(np.sum(W_dash_s_d_t)))
    print('W_dash_w = {}'.format(np.sum(W_dash_w_d_t)))
    print('W_dash_b1 = {}'.format(np.sum(W_dash_b1_d_t)))
    print('W_dash_b2 = {}'.format(np.sum(W_dash_b2_d_t)))
    print('W_dash_ba1 = {}'.format(np.sum(W_dash_ba1_d_t)))

    print('L_dash_k = {}'.format(np.sum(L_dash_k_d_t)))
    print('L_dash_s = {}'.format(np.sum(L_dash_s_d_t)))
    print('L_dash_w = {}'.format(np.sum(L_dash_w_d_t)))
    print('L_dash_b1 = {}'.format(np.sum(L_dash_b1_d_t)))
    print('L_dash_b2 = {}'.format(np.sum(L_dash_b2_d_t)))
    print('L_dash_ba1 = {}'.format(np.sum(L_dash_ba1_d_t)))
    print('L_dash_ba2 = {}'.format(np.sum(L_dash_ba2_d_t)))

    print('L_dashdash_k = {}'.format(np.sum(L_dashdash_k_d_t)))
    print('L_dashdash_s = {}'.format(np.sum(L_dashdash_s_d_t)))
    print('L_dashdash_w = {}'.format(np.sum(L_dashdash_w_d_t)))
    print('L_dashdash_b1 = {}'.format(np.sum(L_dashdash_b1_d_t)))
    print('L_dashdash_b2 = {}'.format(np.sum(L_dashdash_b2_d_t)))
    print('L_dashdash_ba1 = {}'.format(np.sum(L_dashdash_ba1_d_t)))
    print('L_dashdash_ba2 = {}'.format(np.sum(L_dashdash_ba2_d_t)))

    return {
        'L_dash_k_d_t': L_dash_k_d_t,
        'L_dash_s_d_t': L_dash_s_d_t,
        'L_dash_w_d_t': L_dash_w_d_t,
        'L_dash_b1_d_t': L_dash_b1_d_t,
        'L_dash_b2_d_t': L_dash_b2_d_t,
        'L_dash_ba1_d_t': L_dash_ba1_d_t,
        'L_dash_ba2_d_t': L_dash_ba2_d_t,
        'L_dashdash_k_d_t': L_dashdash_k_d_t,
        'L_dashdash_s_d_t': L_dashdash_s_d_t,
        'L_dashdash_w_d_t': L_dashdash_w_d_t,
        'L_dashdash_b1_d_t': L_dashdash_b1_d_t,
        'L_dashdash_b2_d_t': L_dashdash_b2_d_t,
        'L_dashdash_ba1_d_t': L_dashdash_ba1_d_t,
        'L_dashdash_ba2_d_t': L_dashdash_ba2_d_t,
        'W_dash_k_d_t': W_dash_k_d_t,
        'W_dash_s_d_t': W_dash_s_d_t,
        'W_dash_w_d_t': W_dash_w_d_t,
        'W_dash_b1_d_t': W_dash_b1_d_t,
        'W_dash_b2_d_t': W_dash_b2_d_t,
        'W_dash_ba1_d_t': W_dash_ba1_d_t,
        'theta_ex_d_Ave_d': theta_ex_d_Ave_d,
        'Theta_ex_Nave_d': Theta_ex_Nave_d
    }


def calc_E_E_W_d_t(n_p, L_HWH, heating_flag_d, region, sol_region, HW, SHC):
    """1時間当たりの給湯設備の消費電力量 (1)

    :param n_p: 仮想居住人数 (人)
    :type n_p: float
    :param L_HWH: 温水暖房用熱源機の熱負荷
    :type L_HWH: ndarray
    :param heating_flag_d: 暖房日
    :type heating_flag_d: ndarray
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param HW: 給湯機の仕様
    :type HW: dict
    :param SHC: 集熱式太陽熱利用設備の仕様
    :type SHC: dict
    :return: 1日当たりの給湯設備の消費電力量 (kWh/d)
    :rtype: ndarray
    """
    if HW is None or HW['hw_type'] is None:
        # 台所、洗面所及 び浴室等がいずれも無い場合は0とする
        return np.zeros(24 * 365)

    if HW['hw_type'] == 'コージェネレーションを使用する':
        return np.zeros(24 * 365)

    # ふろ機能の修正
    bath_function = get_normalized_bath_function(HW['hw_type'], HW.get('bath_function'))

    # 給湯負荷の生成
    args = {
        'n_p': n_p,
        'region': region,
        'sol_region': sol_region,
        'has_bath': HW['has_bath'],
        'bath_function': bath_function,
        'pipe_diameter': HW['pipe_diameter'],
        'kitchen_watersaving_A': HW['kitchen_watersaving_A'],
        'kitchen_watersaving_C': HW['kitchen_watersaving_C'],
        'shower_watersaving_A': HW['shower_watersaving_A'],
        'shower_watersaving_B': HW['shower_watersaving_B'],
        'washbowl_watersaving_C': HW['washbowl_watersaving_C'],
        'bath_insulation': HW['bath_insulation']
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
                'heating_flag_d': tuple(heating_flag_d),
                'A_col': SHC['A_col'],
                'P_alpha': SHC['P_alpha'],
                'P_beta': SHC['P_beta'],
                'V_fan_P0': SHC['V_fan_P0'],
                'm_fan_test': SHC['m_fan_test'],
                'd0': SHC['d0'],
                'd1': SHC['d1'],
                'W_tnk_ass': SHC['W_tnk_ass']
            })
        else:
            raise ValueError(SHC['type'])

    hotwater_load = calc_hotwater_load(**args)

    # 1時間当たりの給湯機の消費電力量 (kWh/h)
    E_E_hs_d_t = calc_E_E_hs_d_t(
        hw_type=HW['hw_type'],
        bath_function=bath_function,
        hybrid_category=HW['hybrid_category'],
        package_id=HW.get('package_id'),
        hybrid_param=HW.get('hybrid_param'),
        e_rtd=HW['e_rtd'],
        e_dash_rtd=HW['e_dash_rtd'],
        L_dashdash_k_d_t=hotwater_load['L_dashdash_k_d_t'],
        L_dashdash_s_d_t=hotwater_load['L_dashdash_s_d_t'],
        L_dashdash_w_d_t=hotwater_load['L_dashdash_w_d_t'],
        L_dashdash_b1_d_t=hotwater_load['L_dashdash_b1_d_t'],
        L_dashdash_b2_d_t=hotwater_load['L_dashdash_b2_d_t'],
        L_dashdash_ba1_d_t=hotwater_load['L_dashdash_ba1_d_t'],
        L_dashdash_ba2_d_t=hotwater_load['L_dashdash_ba2_d_t'],
        W_dash_k_d_t=hotwater_load['W_dash_k_d_t'],
        W_dash_s_d_t=hotwater_load['W_dash_s_d_t'],
        W_dash_w_d_t=hotwater_load['W_dash_w_d_t'],
        W_dash_b1_d_t=hotwater_load['W_dash_b1_d_t'],
        W_dash_b2_d_t=hotwater_load['W_dash_b2_d_t'],
        W_dash_ba1_d_t=hotwater_load['W_dash_ba1_d_t'],
        theta_ex_d_Ave_d=hotwater_load['theta_ex_d_Ave_d'],
        Theta_ex_Nave_d=hotwater_load['Theta_ex_Nave_d'],
        L_HWH=L_HWH,
        CO2HP=HW['CO2HP'] if 'CO2HP' in HW else None
    )

    # 太陽利用設備の補機の消費電力量
    E_E_aux_ss_d_t = calc_E_E_aux_ss_d_t(
        SHC=SHC,
        region=region,
        sol_region=sol_region,
        heating_flag_d=heating_flag_d
    )

    # 1時間当たりの給湯設備の消費電力量(1)
    E_E_W_d_t = E_E_hs_d_t + E_E_aux_ss_d_t

    return E_E_W_d_t


def calc_E_E_aux_ss_d_t(SHC, region=None, sol_region=None, heating_flag_d=None):
    """1時間当たりの補機の消費電力量 (kWh/h)

    :param SHC: 太陽熱利用設備の仕様
    :type SHC: dict
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :param heating_flag_d: 暖房日
    :type heating_flag_d: ndarray
    :return: 1時間当たりの補機の消費電力量 (kWh/h)
    :rtype: ndarray
    """
    if SHC is None:
        return np.zeros(24 * 365)
    elif SHC['type'] == '液体集熱式':
        # 第九章「自然エネルギー利用設備」第二節「液体集熱式太陽熱利用設備」の算定方法により定まる
        # 1時間当たりの補機の消費電力量 (kWh/h)
        return lss.calc_E_E_lss_aux_d_t(
            ls_type=SHC['ls_type'],
            pmp_type='上記以外の機種',
            P_alpha_sp=SHC['P_alpha_sp'],
            P_beta_sp=SHC['P_beta_sp'],
            region=region,
            sol_region=sol_region
        )
    elif SHC['type'] == '空気集熱式':
        # 第九章「自然エネルギー利用設備」第三節「空気集熱式太陽熱利用設備」の算定方法により定まる
        # 1時間当たりの補機の消費電力量のうちの給湯設備への付加分 (kWh/h)
        return ass.calc_E_E_W_aux_ass_d_t(
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
            pump_sso=SHC['pump_sso']
        )
    else:
        raise ValueError(SHC['type'])


# ============================================================================
# 5.2 ガス消費量
# ============================================================================


def calc_E_G_W_d_t(n_p, L_HWH, heating_flag_d, A_A, region, sol_region, HW, SHC):
    """1時間当たりの給湯設備のガス消費量 (MJ/h) (2)

    :param n_p: 仮想居住人数
    :type n_p: float
    :param L_HWH: 1日当たりの温水暖房の熱負荷 (MJ/d)
    :type L_HWH: ndarray
    :param A_A: 床面積の合計[m^2]
    :type A_A: float
    :param region: 地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :param HW: 給湯機の仕様
    :type HW: dict
    :param SHC: 集熱式太陽熱利用設備の仕様
    :type SHC: dict
    :return: 1時間当たりの給湯設備のガス消費量 (MJ/h)
    :rtype: ndarray
    """
    if HW is None or HW['hw_type'] is None:
        # 台所、洗面所及 び浴室等がいずれも無い場合は0とする
        return np.zeros(24 * 365)

    # ふろ機能の修正
    bath_function = get_normalized_bath_function(HW['hw_type'], HW.get('bath_function'))

    # 給湯負荷の生成
    args = {
        'n_p': n_p,
        'region': region,
        'sol_region': sol_region,
        'has_bath': HW['has_bath'],
        'bath_function': bath_function,
        'pipe_diameter': HW['pipe_diameter'],
        'kitchen_watersaving_A': HW['kitchen_watersaving_A'],
        'kitchen_watersaving_C': HW['kitchen_watersaving_C'],
        'shower_watersaving_A': HW['shower_watersaving_A'],
        'shower_watersaving_B': HW['shower_watersaving_B'],
        'washbowl_watersaving_C': HW['washbowl_watersaving_C'],
        'bath_insulation': HW['bath_insulation']
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
                'heating_flag_d': tuple(heating_flag_d),
                'A_col': SHC['A_col'],
                'P_alpha': SHC['P_alpha'],
                'P_beta': SHC['P_beta'],
                'V_fan_P0': SHC['V_fan_P0'],
                'm_fan_test': SHC['m_fan_test'],
                'd0': SHC['d0'],
                'd1': SHC['d1'],
                'W_tnk_ass': SHC['W_tnk_ass']
            })
        else:
            raise ValueError(SHC['type'])

    hotwater_load = calc_hotwater_load(**args)

    # 1日当たりの給湯機のガス消費量
    E_G_hs_d = calc_E_G_hs_d(
        hw_type=HW['hw_type'],
        hybrid_category=HW['hybrid_category'],
        e_rtd=HW['e_rtd'],
        e_dash_rtd=HW['e_dash_rtd'],
        bath_function=bath_function,
        package_id=HW.get('package_id'),
        L_dashdash_k_d_t=hotwater_load['L_dashdash_k_d_t'],
        L_dashdash_s_d_t=hotwater_load['L_dashdash_s_d_t'],
        L_dashdash_w_d_t=hotwater_load['L_dashdash_w_d_t'],
        L_dashdash_b1_d_t=hotwater_load['L_dashdash_b1_d_t'],
        L_dashdash_b2_d_t=hotwater_load['L_dashdash_b2_d_t'],
        L_dashdash_ba1_d_t=hotwater_load['L_dashdash_ba1_d_t'],
        L_dashdash_ba2_d_t=hotwater_load['L_dashdash_ba2_d_t'],
        W_dash_k_d_t=hotwater_load['W_dash_k_d_t'],
        W_dash_s_d_t=hotwater_load['W_dash_s_d_t'],
        W_dash_w_d_t=hotwater_load['W_dash_w_d_t'],
        W_dash_b1_d_t=hotwater_load['W_dash_b1_d_t'],
        W_dash_b2_d_t=hotwater_load['W_dash_b2_d_t'],
        W_dash_ba1_d_t=hotwater_load['W_dash_ba1_d_t'],
        Theta_ex_Ave=hotwater_load['theta_ex_d_Ave_d'],
        Theta_ex_Nave=hotwater_load['Theta_ex_Nave_d'],
        L_HWH=L_HWH,
        hybrid_param=HW.get('hybrid_param')
    )

    return E_G_hs_d


# ============================================================================
# 5.3 灯油消費量
# ============================================================================


def calc_E_K_W_d_t(n_p, L_HWH, heating_flag_d, A_A, region, sol_region, HW, SHC):
    """1時間当たりの給湯設備の灯油消費量 (MJ/h) (3)

    :param n_p: 仮想居住人数
    :type n_p: float
    :param L_HWH: 1日当たりの温水暖房の熱負荷 (MJ/d)
    :type L_HWH: ndarray
    :param A_A: 床面積の合計[m^2]
    :type A_A: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :param HW: 給湯機の仕様
    :type HW: dict
    :param SHC: 集熱式太陽熱利用設備の仕様
    :type SHC: dict
    :return: 1時間当たりの給湯設備の灯油消費量 (MJ/h) (3)
    :rtype: ndarray
    """
    if HW is None or HW['hw_type'] is None:
        # 台所、洗面所及 び浴室等がいずれも無い場合は0とする
        return np.zeros(24 * 365)

    # ふろ機能の修正
    bath_function = get_normalized_bath_function(HW['hw_type'], HW.get('bath_function'))

    # 給湯負荷の生成
    args = {
        'n_p': n_p,
        'region': region,
        'sol_region': sol_region,
        'has_bath': HW['has_bath'],
        'bath_function': bath_function,
        'pipe_diameter': HW['pipe_diameter'],
        'kitchen_watersaving_A': HW['kitchen_watersaving_A'],
        'kitchen_watersaving_C': HW['kitchen_watersaving_C'],
        'shower_watersaving_A': HW['shower_watersaving_A'],
        'shower_watersaving_B': HW['shower_watersaving_B'],
        'washbowl_watersaving_C': HW['washbowl_watersaving_C'],
        'bath_insulation': HW['bath_insulation']
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
                'heating_flag_d': tuple(heating_flag_d),
                'A_col': SHC['A_col'],
                'P_alpha': SHC['P_alpha'],
                'P_beta': SHC['P_beta'],
                'V_fan_P0': SHC['V_fan_P0'],
                'm_fan_test': SHC['m_fan_test'],
                'd0': SHC['d0'],
                'd1': SHC['d1'],
                'W_tnk_ass': SHC['W_tnk_ass']
            })
        else:
            raise ValueError(SHC['type'])

    hotwater_load = calc_hotwater_load(**args)

    # 1時間当たりの給湯機の灯油消費量 (MJ/h)
    E_k_hs_d_t = calc_E_K_hs_d_t(
        hw_type=HW['hw_type'],
        e_rtd=HW['e_rtd'],
        e_dash_rtd=HW['e_dash_rtd'],
        bath_function=bath_function,
        L_dashdash_k_d_t=hotwater_load['L_dashdash_k_d_t'],
        L_dashdash_s_d_t=hotwater_load['L_dashdash_s_d_t'],
        L_dashdash_w_d_t=hotwater_load['L_dashdash_w_d_t'],
        L_dashdash_b1_d_t=hotwater_load['L_dashdash_b1_d_t'],
        L_dashdash_b2_d_t=hotwater_load['L_dashdash_b2_d_t'],
        L_dashdash_ba1_d_t=hotwater_load['L_dashdash_ba1_d_t'],
        L_dashdash_ba2_d_t=hotwater_load['L_dashdash_ba2_d_t'],
        theta_ex_d_Ave_d=hotwater_load['theta_ex_d_Ave_d']
    )

    return E_k_hs_d_t


# ============================================================================
# 5.4 その他の燃料による一次エネルギー消費量
# ============================================================================


def get_E_M_W_d_t():
    """1時間当たりの給湯設備のその他の燃料による一次エネルギー消費量

    :return: 1時間当たりの給湯設備のその他の燃料による一次エネルギー消費量
    :rtype: ndarray
    """
    # 1時間当たりの給湯設備のその他の燃料による一次エネルギー消費量は0とする
    return np.zeros(24 * 365)


# ============================================================================
# 6. 給湯機のエネルギー消費量
# ============================================================================


def calc_E_E_hs_d_t(hw_type, bath_function, package_id, hybrid_param, hybrid_category, e_rtd, e_dash_rtd, Theta_ex_Nave_d, W_dash_k_d_t, W_dash_s_d_t,
                    W_dash_w_d_t,
                    W_dash_b1_d_t,
                    W_dash_b2_d_t, W_dash_ba1_d_t, theta_ex_d_Ave_d, L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t,
                    L_dashdash_b1_d_t,
                    L_dashdash_b2_d_t, L_dashdash_ba1_d_t, L_dashdash_ba2_d_t, L_HWH, CO2HP):
    """1時間当たりの給湯機の消費電力量 (kWh/h)

    :param hw_type: 給湯機／給湯温水暖房機の種類
    :type hw_type: str
    :param bath_function: 給湯機の種類
    :type bath_function: str
    :param hybrid_category: 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分
    :type hybrid_category: str
    :param package_id: パッケージID
    :type package_id: str
    :param hybrid_param: ハイブリッドパラメーター
    :type hybrid_param: dic
    :param e_rtd: 当該給湯機の効率
    :type e_rtd: float
    :param e_dash_rtd: 「エネルギーの使用の合理化に関する法律」に基づく「特定機器の性能の向上に関する製造事業者等の 判断の基準等」（ガス温水機器）に定義される「エネルギー消費効率」
    :type e_dash_rtd: float
    :param Theta_ex_Nave_d: 夜間平均外気温 (℃)
    :type Theta_ex_Nave_d: ndarray
    :param W_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯量 (L/d)
    :type W_dash_k_d_t: ndarray
    :param W_dash_s_d_t: 1時間当たりの浴室シャワー水栓における節湯補正給湯量 (L/d)
    :type W_dash_s_d_t: ndarray
    :param W_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯量 (L/d)
    :type W_dash_w_d_t: ndarray
    :param W_dash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/d)
    :type W_dash_b1_d_t: ndarray
    :param W_dash_b2_d_t: 1時間当たりの浴槽追焚時における節湯補正給湯量 (L/d)
    :type W_dash_b2_d_t: ndarray
    :param W_dash_ba1_d_t: 1時間当たりの浴槽水栓さし湯時における節湯補正給湯量 (L/d)
    :type W_dash_ba1_d_t: ndarray
    :param theta_ex_d_Ave_d: 日平均外気温度 (℃)
    :type theta_ex_d_Ave_d: ndarray
    :param L_dashdash_k_d_t: 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)
    :type L_dashdash_k_d_t: ndarray
    :param L_dashdash_s_d_t: 1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/d)
    :type L_dashdash_s_d_t: ndarray
    :param L_dashdash_w_d_t: 1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/d)
    :type L_dashdash_w_d_t: ndarray
    :param L_dashdash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯熱負荷 (MJ/d)
    :type L_dashdash_b1_d_t: ndarray
    :param L_dashdash_b2_d_t: 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/d)
    :type L_dashdash_b2_d_t: ndarray
    :param L_dashdash_ba1_d_t: 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯熱負荷 (MJ/d)
    :type L_dashdash_ba1_d_t: ndarray
    :param L_dashdash_ba2_d_t: 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/d)
    :type L_dashdash_ba2_d_t: ndarray
    :param L_HWH: 1日当たりの温水暖房の熱負荷 (MJ/d)
    :type L_HWH: ndarray
    :param CO2HP: CO2HPのパラメーター
    :type CO2HP: dict
    :return: 1時間当たりの給湯機の消費電力量 (MJ/h)
    :rtype: ndarray
    """
    if hw_type == 'ガス従来型給湯機' or hw_type == 'ガス従来型給湯温水暖房機' \
            or hw_type == 'ガス潜熱回収型給湯機' or hw_type == 'ガス潜熱回収型給湯温水暖房機':
        return gas.calc_E_E_hs_d_t(
            W_dash_k_d_t=W_dash_k_d_t,
            W_dash_s_d_t=W_dash_s_d_t,
            W_dash_w_d_t=W_dash_w_d_t,
            W_dash_b1_d_t=W_dash_b1_d_t,
            W_dash_b2_d_t=W_dash_b2_d_t,
            W_dash_ba1_d_t=W_dash_ba1_d_t,
            theta_ex_d_Ave_d=theta_ex_d_Ave_d,
            L_dashdash_ba2_d_t=L_dashdash_ba2_d_t
        )
    elif hw_type == '石油従来型給湯機' or hw_type == '石油従来型給湯温水暖房機' \
            or hw_type == '石油潜熱回収型給湯機' or hw_type == '石油潜熱回収型給湯温水暖房機':
        return oil.calc_E_E_hs_d_t(W_dash_k_d_t=W_dash_k_d_t, W_dash_s_d_t=W_dash_s_d_t, W_dash_w_d_t=W_dash_w_d_t,
                                   W_dash_b1_d_t=W_dash_b1_d_t, W_dash_ba1_d_t=W_dash_ba1_d_t,
                                   W_dash_b2_d_t=W_dash_b2_d_t, theta_ex_d_Ave_d=theta_ex_d_Ave_d,
                                   L_dashdash_ba2_d_t=L_dashdash_ba2_d_t)
    elif hw_type == '電気ヒートポンプ給湯機':
        return eheatpump.calc_E_E_hs_d_t(
            L_dashdash_k_d_t=L_dashdash_k_d_t,
            L_dashdash_s_d_t=L_dashdash_s_d_t,
            L_dashdash_w_d_t=L_dashdash_w_d_t,
            L_dashdash_b1_d_t=L_dashdash_b1_d_t,
            L_dashdash_b2_d_t=L_dashdash_b2_d_t,
            L_dashdash_ba1_d_t=L_dashdash_ba1_d_t,
            L_dashdash_ba2_d_t=L_dashdash_ba2_d_t,
            e_rtd=e_rtd,
            theta_ex_d_Ave_d=theta_ex_d_Ave_d,
            theta_ex_Nave_d=Theta_ex_Nave_d,
            CO2HP=CO2HP
        )
    elif hw_type == '電気ヒーター給湯機' or hw_type == '電気ヒーター給湯温水暖房機':
        return eheater.calc_E_E_hs_d_t(
            L_dashdash_k_d_t=L_dashdash_k_d_t,
            L_dashdash_s_d_t=L_dashdash_s_d_t,
            L_dashdash_w_d_t=L_dashdash_w_d_t,
            L_dashdash_b1_d_t=L_dashdash_b1_d_t,
            L_dashdash_b2_d_t=L_dashdash_b2_d_t,
            L_dashdash_ba1_d_t=L_dashdash_ba1_d_t,
            L_dashdash_ba2_d_t=L_dashdash_ba2_d_t,
            theta_ex_d_Ave_d=theta_ex_d_Ave_d
        )
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(仕様による)' \
            or hw_type == '電気ヒートポンプ・ガス併用型給湯機(仕様による)':
        return hybrid_gas.calc_E_E_hs_d_t(
            hybrid_category=hybrid_category,
            theta_ex_d_Ave_d=theta_ex_d_Ave_d,
            L_dashdash_k_d_t=L_dashdash_k_d_t,
            L_dashdash_s_d_t=L_dashdash_s_d_t,
            L_dashdash_w_d_t=L_dashdash_w_d_t,
            L_dashdash_b2_d_t=L_dashdash_b2_d_t,
            L_dashdash_ba2_d_t=L_dashdash_ba2_d_t
        )
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(試験された値を用いる)' \
            or hw_type == '電気ヒートポンプ・ガス併用型給湯機(試験された値を用いる)':
        return hybrid_gas_3.calc_E_E_hs_d_t(
            bath_function=bath_function,
            package_id=package_id,
            hybrid_param=hybrid_param,
            W_dash_ba1_d_t=W_dash_ba1_d_t,
            theta_ex_d_Ave_d=theta_ex_d_Ave_d,
            L_dashdash_k_d_t=L_dashdash_k_d_t,
            L_dashdash_s_d_t=L_dashdash_s_d_t,
            L_dashdash_w_d_t=L_dashdash_w_d_t,
            L_dashdash_b1_d_t=L_dashdash_b1_d_t,
            L_dashdash_b2_d_t=L_dashdash_b2_d_t,
            L_dashdash_ba1_d_t=L_dashdash_ba1_d_t,
            L_dashdash_ba2_d_t=L_dashdash_ba2_d_t
        )
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：ガス瞬間式、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return gas_hybrid.get_E_E_hs(
            W_dash_k_d_t=W_dash_k_d_t,
            W_dash_s_d_t=W_dash_s_d_t,
            W_dash_w_d_t=W_dash_w_d_t,
            W_dash_b1_d_t=W_dash_b1_d_t,
            W_dash_b2_d_t=W_dash_b2_d_t,
            W_dash_ba1_d_t=W_dash_ba1_d_t,
            theta_ex_d_Ave_d=theta_ex_d_Ave_d,
            L_dashdash_ba2_d_t=L_dashdash_ba2_d_t
        )
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return whybrid.calc_E_E_hs_d_t(
            L_HWH=L_HWH,
            hybrid_category=hybrid_category,
            theta_ex_d_Ave_d=theta_ex_d_Ave_d,
            L_dashdash_k_d_t=L_dashdash_k_d_t,
            L_dashdash_s_d_t=L_dashdash_s_d_t,
            L_dashdash_w_d_t=L_dashdash_w_d_t,
            L_dashdash_b2_d_t=L_dashdash_b2_d_t,
            L_dashdash_ba2_d_t=L_dashdash_ba2_d_t
        )
    else:
        raise ValueError(hw_type)


def calc_E_G_hs_d(hw_type, hybrid_category, e_rtd, e_dash_rtd, bath_function, package_id, Theta_ex_Nave, W_dash_k_d_t, W_dash_s_d_t,
                 W_dash_w_d_t, W_dash_b1_d_t, W_dash_b2_d_t, W_dash_ba1_d_t, Theta_ex_Ave, L_dashdash_k_d_t,
                 L_dashdash_s_d_t, L_dashdash_w_d_t,
                 L_dashdash_b1_d_t, L_dashdash_b2_d_t, L_dashdash_ba1_d_t, L_dashdash_ba2_d_t, L_HWH, hybrid_param):
    """1日当たりの給湯機のガス消費量

    :param hw_type: 給湯機／給湯温水暖房機の種類
    :type hw_type: str
    :param hybrid_category: 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分
    :type hybrid_category: str
    :param e_rtd: 当該給湯機の効率
    :type e_rtd: float
    :param e_dash_rtd: ：「エネルギーの使用の合理化に関する法律」に基づく「特定機器の性能の向上に関する製造事業者等の 判断の基準等」（ガス温水機器）に定義される「エネルギー消費効率」
    :type e_dash_rtd: float
    :param bath_function: ふろ機能の種類
    :type bath_function: str
    :param Theta_ex_Nave: 夜間平均外気温 (℃)
    :type Theta_ex_Nave: ndarray
    :param W_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯量 (L/h)
    :type W_dash_k_d_t: ndarray
    :param W_dash_s_d_t: 1時間当たりの浴室シャワー水栓における節湯補正給湯量 (L/h)
    :type W_dash_s_d_t: ndarray
    :param W_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯量 (L/h)
    :type W_dash_w_d_t: ndarray
    :param W_dash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/h)
    :type W_dash_b1_d_t: ndarray
    :param W_dash_b2_d_t: 1時間当たりの浴槽追焚時における節湯補正給湯量 (L/h)
    :type W_dash_b2_d_t: ndarray
    :param W_dash_ba1_d_t: 1時間当たりの浴槽水栓さし湯時における節湯補正給湯量 (L/h)
    :type W_dash_ba1_d_t: ndarray
    :param Theta_ex_Ave: 日平均外気温度 (℃)
    :type Theta_ex_Ave: ndarray
    :param L_dashdash_k_d: 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_k_d_t: ndarray
    :param L_dashdash_s_d: 1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_s_d_t: ndarray
    :param L_dashdash_w_d: 1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_w_d_t: ndarray
    :param L_dashdash_b1_d: 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_b1_d_t: ndarray
    :param L_dashdash_b2_d: 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_b2_d_t: ndarray
    :param L_dashdash_ba1_d: 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_ba1_d_t: ndarray
    :param L_dashdash_ba2_d: 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_ba2_d_t: ndarray
    :param L_HWH: 1日当たりの温水暖房の熱負荷 (MJ/d)
    :type: L_HWH: ndarray
    :return: 1時間当たりの給湯機のガス消費量 (MJ/h)
    :rtype: ndarray
    """
    if hw_type == 'ガス従来型給湯機' or hw_type == 'ガス従来型給湯温水暖房機' \
            or hw_type == 'ガス潜熱回収型給湯機' or hw_type == 'ガス潜熱回収型給湯温水暖房機':
        return gas.calc_E_G_hs_d_t(
            hw_type=hw_type,
            e_rtd=e_rtd,
            e_dash_rtd=e_dash_rtd,
            theta_ex_d_Ave_d=Theta_ex_Ave,
            L_dashdash_k_d_t=L_dashdash_k_d_t,
            L_dashdash_s_d_t=L_dashdash_s_d_t,
            L_dashdash_w_d_t=L_dashdash_w_d_t,
            L_dashdash_b1_d_t=L_dashdash_b1_d_t,
            L_dashdash_b2_d_t=L_dashdash_b2_d_t,
            L_dashdash_ba1_d_t=L_dashdash_ba1_d_t,
            L_dashdash_ba2_d_t=L_dashdash_ba2_d_t,
            bath_function=bath_function
        )
    elif hw_type == '石油従来型給湯機' or hw_type == '石油従来型給湯温水暖房機' \
            or hw_type == '石油潜熱回収型給湯機' or hw_type == '石油潜熱回収型給湯温水暖房機':
        return oil.get_E_G_hs_d_t()
    elif hw_type == '電気ヒートポンプ給湯機':
        return eheatpump.get_E_G_hs_d_t()
    elif hw_type == '電気ヒーター給湯機' or hw_type == '電気ヒーター給湯温水暖房機':
        return eheater.get_E_G_hs()
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(仕様による)' \
            or hw_type == '電気ヒートポンプ・ガス併用型給湯機(仕様による)':
        return hybrid_gas.calc_E_G_hs_d_t(
            hybrid_category=hybrid_category,
            theta_ex_d_Ave_d=Theta_ex_Ave,
            L_dashdash_k_d_t=L_dashdash_k_d_t,
            L_dashdash_s_d_t=L_dashdash_s_d_t,
            L_dashdash_w_d_t=L_dashdash_w_d_t,
            L_dashdash_b2_d_t=L_dashdash_b2_d_t,
            L_dashdash_ba2_d_t=L_dashdash_ba2_d_t
        )
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(試験された値を用いる)' \
            or hw_type == '電気ヒートポンプ・ガス併用型給湯機(試験された値を用いる)':
        return hybrid_gas_3.get_E_G_hs_d_t(
            bath_function=bath_function,
            package_id=package_id,
            theta_ex_d_Ave_d=Theta_ex_Ave,
            L_dashdash_k_d_t=L_dashdash_k_d_t,
            L_dashdash_s_d_t=L_dashdash_s_d_t,
            L_dashdash_w_d_t=L_dashdash_w_d_t,
            L_dashdash_b1_d_t=L_dashdash_b1_d_t,
            L_dashdash_b2_d_t=L_dashdash_b2_d_t,
            L_dashdash_ba1_d_t=L_dashdash_ba1_d_t,
            L_dashdash_ba2_d_t=L_dashdash_ba2_d_t,
            W_dash_ba1_d_t=W_dash_ba1_d_t,
            hybrid_param=hybrid_param
        )
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：ガス瞬間式、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return gas_hybrid.get_E_G_hs(
            Theta_ex_Ave=Theta_ex_Ave,
            L_dashdash_k=L_dashdash_k_d_t,
            L_dashdash_s=L_dashdash_s_d_t,
            L_dashdash_w=L_dashdash_w_d_t,
            L_dashdash_b1=L_dashdash_b1_d_t,
            L_dashdash_b2=L_dashdash_b2_d_t,
            L_dashdash_ba1=L_dashdash_ba1_d_t,
            L_dashdash_ba2=L_dashdash_ba2_d_t,
            bath_function=bath_function
        )
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return whybrid.calc_E_G_hs_d_t(
            L_HWH=L_HWH,
            hybrid_category=hybrid_category,
            Theta_ex_Ave=Theta_ex_Ave,
            L_dashdash_k_d_t=L_dashdash_k_d_t,
            L_dashdash_s_d_t=L_dashdash_s_d_t,
            L_dashdash_w_d_t=L_dashdash_w_d_t,
            L_dashdash_b2_d_t=L_dashdash_b2_d_t,
            L_dashdash_ba2_d_t=L_dashdash_ba2_d_t
        )
    elif hw_type == 'コージェネレーションを使用する':
        return np.zeros(365)
    else:
        raise ValueError(hw_type)


def calc_E_K_hs_d_t(hw_type, e_rtd, e_dash_rtd, bath_function, theta_ex_d_Ave_d, L_dashdash_k_d_t, L_dashdash_s_d_t,
                    L_dashdash_w_d_t,
                    L_dashdash_b1_d_t, L_dashdash_b2_d_t, L_dashdash_ba1_d_t, L_dashdash_ba2_d_t):
    """1時間当たりの給湯機の灯油消費量 (MJ/h)

    :param hw_type: 給湯機／給湯温水暖房機の種類
    :type hw_type: str
    :param e_rtd: 当該給湯機の効率
    :type e_rtd: float
    :param e_dash_rtd: ：「エネルギーの使用の合理化に関する法律」に基づく「特定機器の性能の向上に関する製造事業者等の 判断の基準等」（ガス温水機器）に定義される「エネルギー消費効率」
    :type e_dash_rtd: float
    :param bath_function: ふろ機能の種類
    :type bath_function: str
    :param theta_ex_d_Ave_d: 日平均外気温度 (℃)
    :type theta_ex_d_Ave_d: ndarray
    :param L_dashdash_w_d_t: 1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_w_d_t: ndarray
    :param L_dashdash_k_d_t: 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_k_d_t: ndarray
    :param L_dashdash_s_d_t: 1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_s_d_t: ndarray
    :param L_dashdash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_b1_d_t: ndarray
    :param L_dashdash_b2_d_t: 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_b2_d_t: ndarray
    :param L_dashdash_ba1_d_t: 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_ba1_d_t: ndarray
    :param L_dashdash_ba2_d_t: 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/h)
    :type L_dashdash_ba2_d_t: ndarray
    :return: 1時間当たりの給湯機の灯油消費量 (MJ/h)
    :rtype: ndarray
    """
    if hw_type == 'ガス従来型給湯機' or hw_type == 'ガス従来型給湯温水暖房機' \
            or hw_type == 'ガス潜熱回収型給湯機' or hw_type == 'ガス潜熱回収型給湯温水暖房機':
        return gas.get_E_K_hs_d_t()
    elif hw_type == '石油従来型給湯機' or hw_type == '石油従来型給湯温水暖房機' \
            or hw_type == '石油潜熱回収型給湯機' or hw_type == '石油潜熱回収型給湯温水暖房機':
        return oil.calc_E_K_hs_d_t(
            hw_type=hw_type,
            bath_function=bath_function,
            e_rtd=e_rtd,
            e_dash_rtd=e_dash_rtd,
            theta_ex_d_Ave_d=theta_ex_d_Ave_d,
            L_dashdash_k_d_t=L_dashdash_k_d_t,
            L_dashdash_s_d_t=L_dashdash_s_d_t,
            L_dashdash_w_d_t=L_dashdash_w_d_t,
            L_dashdash_b1_d_t=L_dashdash_b1_d_t,
            L_dashdash_b2_d_t=L_dashdash_b2_d_t,
            L_dashdash_ba1_d_t=L_dashdash_ba1_d_t,
            L_dashdash_ba2_d_t=L_dashdash_ba2_d_t
        )
    elif hw_type == '電気ヒートポンプ給湯機':
        return eheatpump.get_E_K_hs_d_t()
    elif hw_type == '電気ヒーター給湯機' or hw_type == '電気ヒーター給湯温水暖房機':
        return eheater.get_E_K_hs()
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(仕様による)' \
            or hw_type == '電気ヒートポンプ・ガス併用型給湯機(仕様による)':
        return gas_hybrid.get_E_K_hs()
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(試験された値を用いる)' \
            or hw_type == '電気ヒートポンプ・ガス併用型給湯機(試験された値を用いる)':
        return hybrid_gas.get_E_K_hs_d_t()
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：ガス瞬間式、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return hybrid_gas.get_E_K_hs_d_t()
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return whybrid.get_E_K_hs_d_t()
    elif hw_type == 'コージェネレーションを使用する':
        return np.zeros(365)
    else:
        raise ValueError(hw_type)



def get_normalized_bath_function(hw_type, bath_function):
    """表4 評価可能な給湯機／給湯温水暖房機の種類

    :param hw_type: 給湯機／給湯温水暖房機の種類
    :type hw_type: str
    :param bath_function: ふろ機能の種類
    :type bath_function:  str
    :return: 評価可能な給湯機／給湯温水暖房機の種類
    :rtype: str
    """
    if hw_type == 'ガス従来型給湯機' or hw_type == 'ガス従来型給湯温水暖房機' \
            or hw_type == 'ガス潜熱回収型給湯機' or hw_type == 'ガス潜熱回収型給湯温水暖房機':
        return bath_function
    elif hw_type == '石油従来型給湯機' or hw_type == '石油従来型給湯温水暖房機' \
            or hw_type == '石油潜熱回収型給湯機' or hw_type == '石油潜熱回収型給湯温水暖房機':
        return bath_function
    elif hw_type == '電気ヒートポンプ給湯機':
        return bath_function
    elif hw_type == '電気ヒーター給湯機' or hw_type == '電気ヒーター給湯温水暖房機':
        return bath_function
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(試験された値を用いる)' \
            or hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(仕様による)' \
            or hw_type == '電気ヒートポンプ・ガス併用型給湯機(試験された値を用いる)' \
            or hw_type == '電気ヒートポンプ・ガス併用型給湯機(仕様による)':
        return "ふろ給湯機(追焚あり)"
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：ガス瞬間式、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return "ふろ給湯機(追焚あり)"
    elif hw_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return "ふろ給湯機(追焚あり)"
    elif hw_type == 'コージェネレーションを使用する':
        return bath_function
    else:
        raise ValueError(hw_type)


# ============================================================================
# 7. 太陽熱補正給湯熱負荷
# ============================================================================


def calc_L_dashdash_k_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                         L_sun_d_t):
    """1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h) (4a)

    :param L_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_k_d_t: ndarray
    :param L_dash_s_d_t: 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_s_d_t: ndarray
    :param L_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_w_d_t: ndarray
    :param L_dash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b1_d_t: ndarray
    :param L_dash_b2_d_t: 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b2_d_t: ndarray
    :param L_dash_ba1_d_t: 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_ba1_d_t: ndarray
    :param L_sun_d_t: 1時間当たりの太陽熱利用給湯設備による補正集熱量 (MJ/h)
    :type L_sun_d_t: ndarray
    :return: 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
    :rtype: ndarray
    """

    L_dashdash_k_d_t = np.zeros(24 * 365)

    L_dash_d_t = L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t
    f = L_dash_d_t > 0
    L_dashdash_k_d_t[f] = L_dash_k_d_t[f] - L_sun_d_t[f] * (L_dash_k_d_t[f] / L_dash_d_t[f])

    return L_dashdash_k_d_t


def calc_L_dashdash_s_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                         L_sun_d_t):
    """1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/h) (4b)

    :param L_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_k_d_t: ndarray
    :param L_dash_s_d_t: 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_s_d_t: ndarray
    :param L_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_w_d_t: ndarray
    :param L_dash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b1_d_t: ndarray
    :param L_dash_b2_d_t: 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b2_d_t: ndarray
    :param L_dash_ba1_d_t: 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_ba1_d_t: ndarray
    :param L_sun_d_t: 1時間当たりの太陽熱利用給湯設備による補正集熱量 (MJ/h)
    :type L_sun_d_t: ndarray
    :return: 1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/h)
    :rtype: ndarray
    """
    L_dashdash_s_d_t = np.zeros(24 * 365)

    L_dash_d_t = L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t
    f = L_dash_d_t > 0
    L_dashdash_s_d_t[f] = L_dash_s_d_t[f] - L_sun_d_t[f] * (L_dash_s_d_t[f] / L_dash_d_t[f])

    return L_dashdash_s_d_t


def calc_L_dashdash_w_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                         L_sun_d_t):
    """1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/h) (4c)

    :param L_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_k_d_t: ndarray
    :param L_dash_s_d_t: 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_s_d_t: ndarray
    :param L_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_w_d_t: ndarray
    :param L_dash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b1_d_t: ndarray
    :param L_dash_b2_d_t: 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b2_d_t: ndarray
    :param L_dash_ba1_d_t: 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_ba1_d_t: ndarray
    :param L_sun_d_t: 1時間当たりの太陽熱利用給湯設備による補正集熱量 (MJ/h)
    :type L_sun_d_t: ndarray
    :return: 1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/h)
    :rtype: ndarray
    """
    L_dashdash_w_d_t = np.zeros(24 * 365)

    L_dash_d_t = L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t
    f = L_dash_d_t > 0
    L_dashdash_w_d_t[f] = L_dash_w_d_t[f] - L_sun_d_t[f] * (L_dash_w_d_t[f] / L_dash_d_t[f])

    return L_dashdash_w_d_t


def calc_L_dashdash_b1_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                          L_sun_d_t):
    """1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯熱負荷 (MJ/h) (4d)

    :param L_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_k_d_t: ndarray
    :param L_dash_s_d_t: 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_s_d_t: ndarray
    :param L_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_w_d_t: ndarray
    :param L_dash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b1_d_t: ndarray
    :param L_dash_b2_d_t: 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b2_d_t: ndarray
    :param L_dash_ba1_d_t: 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_ba1_d_t: ndarray
    :param L_sun_d_t: 1時間当たりの太陽熱利用給湯設備による補正集熱量 (MJ/h)
    :type L_sun_d_t: ndarray
    :return: 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯熱負荷 (MJ/h)
    :rtype: ndarray
    """
    L_dashdash_b1_d_t = np.zeros(24 * 365)

    L_dash_d_t = L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t
    f = L_dash_d_t > 0
    L_dashdash_b1_d_t[f] = L_dash_b1_d_t[f] - L_sun_d_t[f] * (L_dash_b1_d_t[f] / L_dash_d_t[f])

    return L_dashdash_b1_d_t



def calc_L_dashdash_b2_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                          L_sun_d_t):
    """1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h) (4e)

    :param L_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_k_d_t: ndarray
    :param L_dash_s_d_t: 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_s_d_t: ndarray
    :param L_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_w_d_t: ndarray
    :param L_dash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b1_d_t: ndarray
    :param L_dash_b2_d_t: 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b2_d_t: ndarray
    :param L_dash_ba1_d_t: 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_ba1_d_t: ndarray
    :param L_sun_d_t: 1時間当たりの太陽熱利用給湯設備による補正集熱量 (MJ/h)
    :type L_sun_d_t: ndarray
    :return: 1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h)
    :rtype: ndarray
    """
    L_dashdash_b2_d_t = np.zeros(24 * 365)

    L_dash_d_t = L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t
    f = L_dash_d_t > 0
    L_dashdash_b2_d_t[f] = L_dash_b2_d_t[f] - L_sun_d_t[f] * (L_dash_b2_d_t[f] / L_dash_d_t[f])

    return L_dashdash_b2_d_t


def calc_L_dashdash_ba1_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                           L_sun_d_t):
    """1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h) (4f)

    :param L_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_k_d_t: ndarray
    :param L_dash_s_d_t: 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_s_d_t: ndarray
    :param L_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_w_d_t: ndarray
    :param L_dash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/hd)
    :type L_dash_b1_d_t: ndarray
    :param L_dash_b2_d_t: 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b2_d_t: ndarray
    :param L_dash_ba1_d_t: 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_ba1_d_t: ndarray
    :param L_sun_d_t: 1時間当たりの太陽熱利用給湯設備による補正集熱量 (MJ/h)
    :type L_sun_d_t: ndarray
    :return: 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)
    :rtype: ndarray
    """
    L_dashdash_ba1_d_t = np.zeros(24 * 365)

    L_dash_d_t = L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t
    f = L_dash_d_t > 0
    L_dashdash_ba1_d_t[f] = L_dash_ba1_d_t[f] - L_sun_d_t[f] * (L_dash_ba1_d_t[f] / L_dash_d_t[f])

    return L_dashdash_ba1_d_t


def get_L_dashdash_ba2_d_t(L_dash_ba2_d_t):
    """ 1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h) (4g)

    :param L_dash_ba2_d_t: 1時間当たりの浴槽追焚時における節湯補正給湯負荷 (MJ/h)
    :type L_dash_ba2_d_t: ndarray
    :return: 1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h)
    :type: ndarray
    """
    return L_dash_ba2_d_t


def calc_L_sun_d_t(region, sol_region=None, solar_device=None, ls_type=None, A_sp=None, P_alpha_sp=None, P_beta_sp=None,
                  W_tnk_ss=None, hotwater_use=None, heating_flag_d=None, A_col=None, P_alpha=None, P_beta=None,
                  V_fan_P0=None, d0=None,
                  d1=None, m_fan_test=None, W_tnk_ass=None, Theta_wtr_d=None, L_dash_k_d_t=None, L_dash_s_d_t=None,
                  L_dash_w_d_t=None, L_dash_b1_d_t=None, L_dash_b2_d_t=None, L_dash_ba1_d_t=None):
    """太陽熱利用給湯設備による補正集熱量

    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :param solar_device: 太陽熱利用設備の種類 (液体集熱式,空気集熱式,None)
    :type solar_device: str
    :param ls_type: 液体集熱式太陽熱利用設備の種類 (太陽熱温水器,ソーラーシステム)
    :type ls_type: str
    :param A_sp: 太陽熱集熱部の有効集熱面積 (m2)
    :type A_sp: float
    :param P_alpha_sp: 太陽熱集熱部の方位角 (°)
    :type P_alpha_sp: float
    :param P_beta_sp: 太陽熱集熱部の傾斜角 (°)
    :type P_beta_sp: float
    :param W_tnk_ss: ソーラーシステムのタンク容量 (L)
    :type W_tnk_ss: float
    :param W_tnk_ass: タンク容量 (L)
    :type W_tnk_ass: float
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :param L_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_k_d_t: ndarrayL
    :param L_dash_s_d_t: 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_s_d_t: ndarray
    :param L_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_w_d_t: ndarray
    :param L_dash_b1_d_t: 1時間当たりの浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b1_d_t: ndarray
    :param L_dash_b2_d_t: 1時間当たりの浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b2_d_t: ndarray
    :param L_dash_ba1_d_t: 1時間当たりの浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_ba1_d_t: ndarray
    :return: 1時間当たりの太陽熱利用設備による補正集熱量 (MJ/h)
    :rtype: ndarray
    """
    if solar_device == '液体集熱式':
        return lss.calc_L_sun_lss_d_t(
            region=region,
            sol_region=sol_region,
            ls_type=ls_type,
            A_sp=A_sp,
            P_alpha_sp=P_alpha_sp,
            P_beta_sp=P_beta_sp,
            W_tnk_ss=W_tnk_ss,
            Theta_wtr_d=Theta_wtr_d,
            L_dash_k_d_t=L_dash_k_d_t,
            L_dash_s_d_t=L_dash_s_d_t,
            L_dash_w_d_t=L_dash_w_d_t,
            L_dash_b1_d_t=L_dash_b1_d_t,
            L_dash_b2_d_t=L_dash_b2_d_t,
            L_dash_ba1_d_t=L_dash_ba1_d_t
        )
    elif solar_device == '空気集熱式':
        if hotwater_use == True:
            outdoor = load_outdoor()
            Theta_ex_d_t = get_Theta_ex(region, outdoor)
            Theta_col_nonopg_d_t, Theta_col_opg_d_t = ass.calc_Theta_col(A_col, P_alpha, P_beta, V_fan_P0, d0, d1,
                                                                         m_fan_test, region, sol_region, Theta_ex_d_t)
            t_fan_d_t = ass.get_t_fan_d_t(Theta_col_nonopg_d_t, Theta_col_opg_d_t)
            t_cp_d_t = ass.get_t_cp_d_t(hotwater_use, t_fan_d_t, heating_flag_d)
            V_fan_d_t = ass.get_V_fan_d_t(t_fan_d_t, V_fan_P0)
            Q_col_d_t = ass.get_Q_col_d_t(V_fan_d_t, Theta_col_opg_d_t, Theta_ex_d_t)
            Q_d = ass.calc_Q_d(Q_col_d_t, t_cp_d_t)
            L_tnk_d = ass.calc_L_tnk_d(Q_d, W_tnk_ass, Theta_wtr_d)
            return ass.calc_L_sun_ass_d_t(L_tnk_d, L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t,
                                          L_dash_b2_d_t, L_dash_ba1_d_t)
        else:
            return np.zeros(24 * 365)
    elif solar_device is None:
        return np.zeros(24 * 365)
    else:
        raise ValueError(solar_device)


# ============================================================================
# 8. 節湯補正給湯熱負荷
# ============================================================================


def get_L_dash_k_d_t(W_dash_k_d_t, Theta_sw_k, Theta_wtr_d):
    """台所水栓における節湯補正給湯負荷 (MJ/h) (5a)

    :param W_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯量 (L/h)
    :type W_dash_k_d_t: ndarray
    :param Theta_sw_k: 台所水栓における基給湯量 (℃)
    :type Theta_sw_k: int
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :return: 台所水栓における節湯補正給湯負荷 (MJ/h)
    :rtype: ndarray
    """
    return W_dash_k_d_t * (Theta_sw_k - np.repeat(Theta_wtr_d, 24)) * 4.186 * 10 ** (-3)



def get_L_dash_s_d_t(W_dash_s_d_t, Theta_sw_s, Theta_wtr_d):
    """浴室シャワー水栓における節湯補正給湯負荷 (5b)

    :param W_dash_s_d_t: 1時間当たりの浴室シャワーにおける節湯補正給湯量 (L/h)
    :type W_dash_s_d_t: ndarray
    :param Theta_sw_s: 浴室シャワーにおける基給湯量 (℃)
    :type Theta_sw_s: int
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :return: 浴室シャワーにおける節湯補正給湯負荷 (MJ/h)
    :rtype: ndarray
    """
    return W_dash_s_d_t * (Theta_sw_s - np.repeat(Theta_wtr_d, 24)) * 4.186 * 10 ** (-3)



def get_L_dash_w_d_t(W_dash_w_d_t, Theta_sw_w, Theta_wtr_d):
    """洗面水栓における節湯補正給湯負荷 (5c)

    :param W_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯量 (L/d)
    :type W_dash_w_d_t: ndarray
    :param Theta_sw_w: 洗面水栓における基給湯量 (℃)
    :type Theta_sw_w: int
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :return: 洗面水栓における節湯補正給湯負荷 (MJ/d)
    :rtype: ndarray
    """
    return W_dash_w_d_t * (Theta_sw_w - np.repeat(Theta_wtr_d, 24)) * 4.186 * 10 ** (-3)


def get_L_dash_bx_d_t(W_dash_b1_d_t, W_dash_b2_d_t, Theta_wtr_d, has_bath, bash_function):
    """浴槽水栓湯はり時における節水補正給湯熱負荷 L_dash_b1_d, L_dash_b2_d

    :param W_dash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/d)
    :type W_dash_b1_d_t: ndarray
    :param W_dash_b2_d_t: 1時間当たりの浴槽自動湯はり時における節湯補正給湯量 (L/d)
    :type W_dash_b2_d_t: ndarray
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :param has_bath: 浴室用の有無
    :type has_bath: bool
    :param bash_function: ふろ機能の種類
    :type bash_function: str
    :return: 浴槽水栓湯はり時・浴槽自動湯はり時における節水補正給湯熱負荷 (MJ/d)
    :rtype: ndarray
    """
    if has_bath == False:
        L_dash_b1_d_t = np.zeros(24 * 365)  # (5-1d)
        L_dash_b2_d_t = np.zeros(24 * 365)  # (5-1e)
        return L_dash_b1_d_t, L_dash_b2_d_t
    elif bash_function == '給湯単機能':
        Theta_sw_b1 = get_Theta_sw_b1()
        L_dash_b1_d_t = W_dash_b1_d_t * (Theta_sw_b1 - np.repeat(Theta_wtr_d, 24)) * 4.186 * 10 ** (-3)  # (5-2d)
        L_dash_b2_d_t = np.zeros(24 * 365)  # (5-2e)
        return L_dash_b1_d_t, L_dash_b2_d_t
    elif bash_function == 'ふろ給湯機(追焚あり)' or bash_function == 'ふろ給湯機(追焚なし)':
        Theta_sw_b2 = get_Theta_sw_b2()
        L_dash_b1_d_t = np.zeros(24 * 365)  # (5-3d)
        L_dash_b2_d_t = W_dash_b2_d_t * (Theta_sw_b2 - np.repeat(Theta_wtr_d, 24)) * 4.186 * 10 ** (-3)  # (5-3e)
        return L_dash_b1_d_t, L_dash_b2_d_t
    else:
        raise ValueError(bash_function)



def get_L_dash_bax_d_t(W_dash_ba1_d_t, Theta_wtr_d, L_ba_d_t, has_bath, bash_function):
    """浴槽水栓さし湯時における節水補正給湯熱負荷 L_dash_ba1_d, L_dash_ba2_d

    :param W_dash_ba1_d_t: 1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/h)
    :type W_dash_ba1_d_t: ndarray
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :param L_ba_d_t: 1時間当たりの浴槽沸かし直しによる給湯熱負荷 (MJ/h)
    :type L_ba_d_t: ndarray
    :param has_bath: 浴室等の有無
    :type has_bath: bool
    :param bash_function: ふろ機能の種類 (給湯単機能,ふろ給湯機(追焚なし),ふろ給湯機(追焚あり))
    :type bash_function: str
    :return: 浴槽水栓さし湯時／浴槽追焚時における節水補正給湯熱負荷 (MJ/h)
    :rtype: ndarray
    """
    if has_bath == False:
        L_dash_ba1_d_t = np.zeros(24 * 365)  # (5-1f)
        L_dash_ba2_d_t = np.zeros(24 * 365)  # (5-1g)
        return L_dash_ba1_d_t, L_dash_ba2_d_t
    elif bash_function == '給湯単機能' or bash_function == 'ふろ給湯機(追焚なし)':
        Theta_sw_ba1 = get_Theta_sw_ba1()
        L_dash_ba1_d_t = W_dash_ba1_d_t * (Theta_sw_ba1 - np.repeat(Theta_wtr_d, 24)) * 4.186 * 10 ** (-3)  # (5-2f)
        L_dash_ba2_d_t = np.zeros(24 * 365)  # (5-2g)
        return L_dash_ba1_d_t, L_dash_ba2_d_t
    elif bash_function == 'ふろ給湯機(追焚あり)':
        L_dash_ba1_d_t = np.zeros(24 * 365)  # (5-3f)
        L_dash_ba2_d_t = L_ba_d_t * 1.25  # (5-3g)
        return L_dash_ba1_d_t, L_dash_ba2_d_t
    else:
        raise ValueError(bash_function)


def get_Theta_sw_k():
    """台所水栓の基準給湯温度

    :return: 台所水栓の基準給湯温度
    :rtype: int
    """
    return get_table_5()[0]



def get_Theta_sw_s():
    """浴室シャワー水栓の基準給湯温度

    :return: 浴室シャワー水栓の基準給湯温度
    :rtype: int
    """
    return get_table_5()[1]



def get_Theta_sw_w():
    """洗面水栓の基準給湯温度

    :return: 洗面水栓の基準給湯温度
    :rtype: int
    """
    return get_table_5()[2]


def get_Theta_sw_b1():
    """浴槽水栓湯はりの基準給湯温度

    :return: 浴槽水栓湯はりの基準給湯温度
    :rtype: int
    """
    return get_table_5()[3]


def get_Theta_sw_b2():
    """浴槽自動湯はりの基準給湯温度

    :return: 浴槽自動湯はりの基準給湯温度
    :rtype: int
    """
    return get_table_5()[4]


def get_Theta_sw_ba1():
    """浴槽水栓さし湯の基準給湯温度

    :return: 浴槽水栓さし湯の基準給湯温度
    :rtype: int
    """
    return get_table_5()[5]


def get_table_5():
    """表 5 用途ごとの基準給湯温度

    :return: 用途ごとの基準給湯温度
    :rtype: list
    """
    table_5 = [
        40,
        40,
        40,
        40,
        40,
        60
    ]
    return table_5

# ============================================================================
# 9. 節湯補正給湯量
# ============================================================================

def calc_W_dash_k_d_t(W_k_d_t, kitchen_watersaving_A, kitchen_watersaving_C, pipe_diameter, Theta_wtr_d):
    """1時間当たりの台所水栓における節湯補正給湯量 [L/h] (6a)

    :param W_k_d_t: 1時間当たりの台所水栓における基準給湯量 (L/h)
    :type W_k_d_t: ndarray
    :param kitchen_watersaving_A: 台所水栓の手元止水機能の有無
    :type kitchen_watersaving_A: bool
    :param kitchen_watersaving_C: 台所水栓の水優先吐水機能の有無
    :type kitchen_watersaving_C: bool
    :param pipe_diameter: ヘッダー分岐後の径
    :type pipe_diameter: str
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :return: 1時間当たりの台所水栓における節湯補正給湯量 (L/h)
    :rtype: ndarray
    """
    # 台所水栓における節湯の効果係数
    f_sk = watersaving.get_f_sk(kitchen_watersaving_A, kitchen_watersaving_C, Theta_wtr_d)

    # 配管における節湯の効果係数
    f_sp = watersaving.get_f_sp(pipe_diameter)

    return W_k_d_t * np.repeat(f_sk, 24) * f_sp


def calc_W_dash_s_d_t(W_s_d_t, shower_watersaving_A, shower_watersaving_B, pipe_diameter):
    """1時間当たりの浴室シャワーにおける節湯補正給湯量 (L/h) (6a)

    :param W_s_d_t: 浴室シャワーにおける基準給湯量 (L/h)
    :type W_s_d_t: ndarray
    :param shower_watersaving_A: 浴室シャワー水栓の手元止水機能の有無
    :type shower_watersaving_A: bool
    :param shower_watersaving_B: 浴室シャワー水栓の小流量吐水機能の有無
    :type shower_watersaving_B: bool
    :param pipe_diameter: ヘッダー分岐後の径
    :type pipe_diameter: str
    :return: 1時間当たりの浴室シャワーにおける節湯補正給湯量 (L/h)
    :rtype: ndarray
    """
    # 浴室シャワー水栓のける節湯の効果係数
    f_ss = watersaving.get_f_ss(shower_watersaving_A, shower_watersaving_B)

    # 配管における節湯の効果係数
    f_sp = watersaving.get_f_sp(pipe_diameter)

    return W_s_d_t * f_ss * f_sp


def calc_W_dash_w_d_t(W_w_d_t, washbowl_watersaving_C, pipe_diameter, Theta_wtr_d):
    """1時間当たりの台所水栓における節湯補正給湯量 (L/h) (6c)

    :param W_w_d_t: 台所水栓における基準給湯量 (L/h)
    :type W_w_d_t: ndarray
    :param washbowl_watersaving_C: 洗面水栓の水優先吐水機能の有無
    :type washbowl_watersaving_C: bool
    :param pipe_diameter: ヘッダー分岐後の径
    :type pipe_diameter: str
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :return: 1時間当たりの台所水栓における節湯補正給湯量 (L/h)
    :rtype: ndarray
    """
    # 配管における節湯の効果係数
    f_sp = watersaving.get_f_sp(pipe_diameter)

    # 洗面水栓における節湯の効果係数
    f_sw = watersaving.get_f_sw(washbowl_watersaving_C, Theta_wtr_d)

    return W_w_d_t * np.repeat(f_sw, 24) * f_sp


def calc_W_dash_b1_d_t(W_b1_d_t, pipe_diameter):
    """1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/h) (6d)

    :param W_b1_d_t: 浴槽水栓湯はり時における基準給湯量 (L/h)
    :type W_b1_d_t: ndarray
    :param pipe_diameter: ヘッダー分岐後の径
    :type pipe_diameter: str
    :return: 1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/h)
    :rtype: ndarray
    """
    # 配管における節湯の効果係数
    f_sp = watersaving.get_f_sp(pipe_diameter)

    # 浴槽における節湯の効果係数
    f_sb = watersaving.get_f_sb()

    return W_b1_d_t * f_sp * f_sb


def calc_W_dash_b2_d_t(W_b2_d_t):
    """1時間当たりの浴槽自動湯はり時における節湯補正給湯量 (L/h) (6e)

    :param W_b2_d_t: 浴槽自動湯はり時における基準給湯量 (L/h)
    :type W_b2_d_t: ndarray
    :return: 1時間当たりの浴槽自動湯はり時における節湯補正給湯量 (L/h)
    :rtype: ndarray
    """
    # 浴槽における節湯の効果係数
    f_sb = watersaving.get_f_sb()

    return W_b2_d_t * f_sb


def calc_W_dash_ba1_d_t(W_ba1_d_t, pipe_diameter):
    """ 1時間当たりの浴槽水栓さし湯時における節湯補正給湯量 (L/h) (6f)

    :param W_ba1_d_t: 1時間当たりの浴室水栓さし湯時における基準給湯量 (L/h)
    :type W_ba1_d_t: ndarray
    :param pipe_diameter: ヘッダー分岐後の径
    :type pipe_diameter: str
    :return: 1時間当たりの浴槽水栓さし湯時における節湯補正給湯量 (L/h)
    :type: ndarray
    """
    # 配管における節湯の効果係数
    f_sp = watersaving.get_f_sp(pipe_diameter)

    return W_ba1_d_t * f_sp


# ============================================================================
# 10. 基準給湯量
# ============================================================================

def calc_W_k_d_t(n_p, schedule_hw):
    """1時間当たりの台所水栓における基準給湯量 (L/h) (7a)
    :param n_p: 仮想居住人数 (人)
    :type n_p: float
    :param schedule_hw: 給湯スケジュール
    :type schedule_hw: ndarray
    :return: 1時間当たりの台所水栓における基準給湯量 (L/h)
    :rtype: ndarray
    """
    if n_p in [1, 2, 3, 4]:
        return calc_W_k_p_d_t(n_p, schedule_hw)
    elif 1 <= n_p and n_p <= 2:
        W_k_1_d_t = calc_W_k_p_d_t(1, schedule_hw)
        W_k_2_d_t = calc_W_k_p_d_t(2, schedule_hw)
        return W_k_1_d_t * (2 - n_p) / (2 - 1) + W_k_2_d_t * (n_p - 1) / (2 - 1)
    elif 2 <= n_p and n_p <= 3:
        W_k_2_d_t = calc_W_k_p_d_t(2, schedule_hw)
        W_k_3_d_t = calc_W_k_p_d_t(3, schedule_hw)
        return W_k_2_d_t * (3 - n_p) / (3 - 2) + W_k_3_d_t * (n_p - 2) / (3 - 2)
    elif 3 <= n_p and n_p <= 4:
        W_k_3_d_t = calc_W_k_p_d_t(3, schedule_hw)
        W_k_4_d_t = calc_W_k_p_d_t(4, schedule_hw)
        return W_k_3_d_t * (4 - n_p) / (4 - 3) + W_k_4_d_t * (n_p - 3) / (4 - 3)


def calc_W_s_d_t(n_p, schedule_hw, has_bath):
    """1時間当たりの浴室シャワー水栓における基準給湯量 (7b)

    :param n_p: 仮想居住人数 (人)
    :type n_p: float
    :param schedule_hw: 給湯スケジュール
    :type schedule_hw: ndarray
    :param has_bath: 浴室等の有無
    :type has_bath: bool
    :return: 1時間当たりの浴室シャワー水栓における基準給湯量 (L/h)
    :rtype: ndarray
    """
    if n_p in [1, 2, 3, 4]:
        return calc_W_s_p_d_t(n_p, schedule_hw, has_bath)
    elif 1 <= n_p and n_p <= 2:
        W_s_1_d_t = calc_W_s_p_d_t(1, schedule_hw, has_bath)
        W_s_2_d_t = calc_W_s_p_d_t(2, schedule_hw, has_bath)
        return W_s_1_d_t * (2 - n_p) / (2 - 1) + W_s_2_d_t * (n_p - 1) / (2 - 1)
    elif 2 <= n_p and n_p <= 3:
        W_s_2_d_t = calc_W_s_p_d_t(2, schedule_hw, has_bath)
        W_s_3_d_t = calc_W_s_p_d_t(3, schedule_hw, has_bath)
        return W_s_2_d_t * (3 - n_p) / (3 - 2) + W_s_3_d_t * (n_p - 2) / (3 - 2)
    elif 3 <= n_p and n_p <= 4:
        W_s_3_d_t = calc_W_s_p_d_t(3, schedule_hw, has_bath)
        W_s_4_d_t = calc_W_s_p_d_t(4, schedule_hw, has_bath)
        return W_s_3_d_t * (4 - n_p) / (4 - 3) + W_s_4_d_t * (n_p - 3) / (4 - 3)


def calc_W_w_d_t(n_p, schedule_hw):
    """1時間当たりの洗面水栓における基準給湯量 (7c)

    :param n_p: 仮想居住人数 (人)
    :type n_p: float
    :param schedule_hw: 給湯スケジュール
    :type schedule_hw: ndarray
    :return: 1時間当たりの洗面水栓における基準給湯量 (L/h)
    :rtype: ndarray
    """
    if n_p in [1, 2, 3, 4]:
        return calc_W_w_p_d_t(n_p, schedule_hw)
    elif 1 <= n_p and n_p <= 2:
        W_w_1_d_t = calc_W_w_p_d_t(1, schedule_hw)
        W_w_2_d_t = calc_W_w_p_d_t(2, schedule_hw)
        return W_w_1_d_t * (2 - n_p) / (2 - 1) + W_w_2_d_t * (n_p - 1) / (2 - 1)
    elif 2 <= n_p and n_p <= 3:
        W_w_2_d_t = calc_W_w_p_d_t(2, schedule_hw)
        W_w_3_d_t = calc_W_w_p_d_t(3, schedule_hw)
        return W_w_2_d_t * (3 - n_p) / (3 - 2) + W_w_3_d_t * (n_p - 2) / (3 - 2)
    elif 3 <= n_p and n_p <= 4:
        W_w_3_d_t = calc_W_w_p_d_t(3, schedule_hw)
        W_w_4_d_t = calc_W_w_p_d_t(4, schedule_hw)
        return W_w_3_d_t * (4 - n_p) / (4 - 3) + W_w_4_d_t * (n_p - 3) / (4 - 3)
    else:
        raise ValueError(n_p)


def get_schedule_pattern_list():
    """ 生活スケジュールパターン

    :return: 生活スケジュールパターン
    :rtype: list
    """
    ptn_list = [
        '休日在宅（大）',
        '休日在宅（小）',
        '平日（大）',
        '平日（中）',
        '平日（小）',
        '休日外出'
    ]
    return ptn_list


def calc_W_k_p_d_t(p, schedule_hw):
    """1時間当たりの居住人数がp人における台所水栓における基準給湯量

    :param p: 居住人数 (人)
    :type p: float
    :param schedule_hw: 給湯スケジュール
    :type schedule_hw: ndarray
    :return: 1時間当たりの居住人数がp人における台所水栓における基準給湯量 (L/h)
    :rtype: ndarray
    """
    # 読み取るべき表の選択
    table = schedule.get_table_m_for_p(p)

    # 作業用
    W_k_p_d_t = np.zeros(24 * 365)

    # 生活スケジュールパターン
    ptn_list = get_schedule_pattern_list()

    # パターンごとに合算
    for i, ptn in enumerate(ptn_list):
        f = np.repeat(schedule_hw == ptn, 24)
        W_k_p_d_t[f] = np.tile(table[i][:, 0], 365)[f]

    return W_k_p_d_t


def calc_W_s_p_d_t(p, schedule_hw, has_bath):
    """1時間当たりの居住人数がp人における浴室シャワー水栓における基準給湯量

    :param p: 居住人数 (人)
    :type p: float
    :param schedule_hw: 給湯スケジュール
    :type schedule_hw: ndarray
    :return: 1時間当たりの居住人数がp人における洗面シャワー水栓における基準給湯量 (L/h)
    :rtype: ndarray
    """
    # 読み取るべき表の選択
    table = schedule.get_table_m_for_p(p)

    # 作業用
    W_s_p_d_t = np.zeros(24 * 365)

    # 生活スケジュールパターン
    ptn_list = get_schedule_pattern_list()

    # 表6で読み取るべき列インデックス
    j = 1 if has_bath else 2

    # パターンごとに合算
    for i, ptn in enumerate(ptn_list):
        f = np.repeat(schedule_hw == ptn, 24)
        W_s_p_d_t[f] = np.tile(table[i][:, j], 365)[f]

    return W_s_p_d_t


def calc_W_w_p_d_t(p, schedule_hw):
    """1時間あたりの居住人数がp人における洗面水栓における基準給湯量

    :param p: 居住人数 (人)
    :type p: float
    :param schedule_hw: 給湯スケジュール
    :type schedule_hw: ndarray
    :return: 1日当たりの居住人数がp人における洗面水栓における基準給湯量 (L/d)
    :rtype: ndarray
    """
    # 読み取るべき表の選択
    table = schedule.get_table_m_for_p(p)

    # 作業用
    W_w_p_d_t = np.zeros(24 * 365)

    # 生活スケジュールパターン
    ptn_list = get_schedule_pattern_list()

    # パターンごとに合算
    for i, ptn in enumerate(ptn_list):
        f = np.repeat(schedule_hw == ptn, 24)
        W_w_p_d_t[f] = np.tile(table[i][:, 3], 365)[f]

    return W_w_p_d_t



def calc_W_b1_d_t(n_p, schedule_hw, has_bath, bath_function):
    """浴槽水栓湯はり時における給湯基準量 (L/h)

    :param n_p: 仮想居住人数 (人)
    :type n_p: float
    :param schedule_hw: 給湯スケジュール
    :type schedule_hw: ndarray
    :param has_bath: 浴室等の有無
    :type has_bath: bool
    :param bath_function: ふろ機能の種類
    :type bath_function: str
    :return: 浴槽水栓湯はり時における給湯基準量 (L/h)
    :rtype: ndarray
    """
    if bath_function == '給湯単機能':
        return calc_W_b_d_t(n_p, schedule_hw, has_bath)
    elif bath_function == 'ふろ給湯機(追焚なし)' or bath_function == 'ふろ給湯機(追焚あり)':
        return np.zeros(24 * 365)
    else:
        raise ValueError(bath_function)



def calc_W_b2_d_t(n_p, schedule_hw, has_bath, bath_function):
    """浴槽自動湯はり時における給湯基準量 (L/h)

    :param n_p: 仮想居住人数 (人)
    :type n_p: float
    :param schedule_hw: 給湯スケジュール
    :type schedule_hw: ndarray
    :param has_bath: 浴室等の有無
    :type has_bath: bool
    :param bath_function: ふろ機能の種類
    :type bath_function: str
    :return: 浴槽自動湯はり時における給湯基準量 (L/d)
    :rtype: ndarray
    """
    if bath_function == 'ふろ給湯機(追焚なし)' or bath_function == 'ふろ給湯機(追焚あり)':
        return calc_W_b_d_t(n_p, schedule_hw, has_bath)
    elif bath_function == '給湯単機能':
        return np.zeros(24 * 365)
    else:
        raise ValueError(bath_function)


def calc_W_b_d_t(n_p, schedule_hw, has_bath):
    """1時間当たりの浴槽湯はり時における基準給湯量 (L/h) (8)

    :param n_p: 仮想居住人数 (人)
    :type n_p: float
    :param schedule_hw: 給湯スケジュール
    :type schedule_hw: ndarray
    :param has_bath: 浴室等の有無
    :type has_bath: bool
    :return: 1時間あたりの浴槽湯はり時における基準給湯量 (L/h)
    :rtype: ndarray
    """
    if n_p in [1, 2, 3, 4]:
        return calc_W_b_p_d_t(n_p, schedule_hw, has_bath)
    if 1 <= n_p and n_p <= 2:
        W_b_1_d_t = calc_W_b_p_d_t(1, schedule_hw, has_bath)
        W_b_2_d_t = calc_W_b_p_d_t(2, schedule_hw, has_bath)
        return W_b_1_d_t * (2 - n_p) / (2 - 1) + W_b_2_d_t * (n_p - 1) / (2 - 1)
    elif 2 <= n_p and n_p <= 3:
        W_b_2_d_t = calc_W_b_p_d_t(2, schedule_hw, has_bath)
        W_b_3_d_t = calc_W_b_p_d_t(3, schedule_hw, has_bath)
        return W_b_2_d_t * (3 - n_p) / (3 - 2) + W_b_3_d_t * (n_p - 2) / (3 - 2)
    elif 3 <= n_p and n_p <= 4:
        W_b_3_d_t = calc_W_b_p_d_t(3, schedule_hw, has_bath)
        W_b_4_d_t = calc_W_b_p_d_t(4, schedule_hw, has_bath)
        return W_b_3_d_t * (4 - n_p) / (4 - 3) + W_b_4_d_t * (n_p - 3) / (4 - 3)
    else:
        raise ValueError(n_p)


def calc_W_b_p_d_t(p, schedule_hw, has_bath):
    """1時間あたりの居住人数がp人における浴槽湯はり時における基準給湯量

    :param p: 居住人数 (人)
    :type p: float
    :param schedule_hw: 給湯スケジュール
    :type schedule_hw: ndarray
    :param has_bath: 浴室等の有無
    :type has_bath: bool
    :return: 1時間あたりの居住人数がp人における浴槽湯はり時における基準給湯量 (L/h)
    :rtype: ndarray
    """
    # 読み取るべき表の選択
    table = schedule.get_table_m_for_p(p)

    # 作業用
    W_b_p_d_t = np.zeros(24 * 365)

    # 生活スケジュールパターン
    ptn_list = get_schedule_pattern_list()

    # 読み取るべき表の列インデックス
    j = 4 if has_bath else 5

    # パターンごとに合算
    for i, ptn in enumerate(ptn_list):
        f = np.repeat(schedule_hw == ptn, 24)
        W_b_p_d_t[f] = np.tile(table[i][:, j], 365)[f]

    return W_b_p_d_t


def calc_n_b_p_d_t(p, schedule_hw, has_bath):
    """1時間あたりの居住人数がp人における入浴人数(人/h)

    :param p: 居住人数 (人)
    :type p: float
    :param schedule_hw: 給湯スケジュール
    :type schedule_hw: ndarray
    :param has_bath: 浴室等の有無
    :type has_bath: bool
    :return: 1時間あたりの居住人数がp人における入浴人数(人/h)
    :rtype: ndarray
    """
    # 読み取るべき表の選択
    table = schedule.get_table_m_for_p(p)

    # 作業用
    n_b_p_d_t = np.zeros(24 * 365)

    # 生活スケジュールパターン
    ptn_list = get_schedule_pattern_list()

    # 読み取るべき表の列インデックス
    j = 6 if has_bath else 7

    # パターンごとに合算
    for i, ptn in enumerate(ptn_list):
        f = np.repeat(schedule_hw == ptn, 24)
        n_b_p_d_t[f] = np.tile(table[i][:, j], 365)[f]

    return n_b_p_d_t


def calc_W_ba1_d_t(bath_function, L_ba_d_t, Theta_wtr_d):
    """ 浴槽水栓さし湯時における基準給湯量 (L/h) (9)

    :param bath_function: ふろ機能の種類
    :type bath_function: str
    :param L_ba_d_t: 1時間当たりの浴槽沸かし直しによる給湯熱負荷 (MJ/h)
    :type L_ba_d_t: ndarray
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :return: 浴槽水栓さし湯時における基準給湯量 (L/h)
    :rtype: ndarray
    """
    if bath_function == '給湯単機能' or bath_function == 'ふろ給湯機(追焚なし)':
        # 浴槽水栓さし湯時における基準給湯温度
        Theta_sw_ba1 = get_Theta_sw_ba1()
        return L_ba_d_t * (1.0 / (Theta_sw_ba1 - np.repeat(Theta_wtr_d, 24))) * (1.0 / 4.186) * 10 ** 3
    elif bath_function == 'ふろ給湯機(追焚あり)':
        return np.zeros(24 * 365)
    else:
        raise ValueError(bath_function)


# ============================================================================
# 11. 浴槽沸かし直しによる給湯熱負荷
# ============================================================================

def calc_L_ba_d_t(bath_insulation, schedule_hw, has_bath, theta_ex_d_Ave_d, n_p):
    """浴槽沸かし直しによる給湯熱負荷 (MJ/h) (10)

    :param bath_insulation: 浴槽の断熱の有無
    :type bath_insulation: bool
    :param schedule_hw: 給湯スケジュール
    :type schedule_hw: ndarray
    :param has_bath: 浴室等の有無
    :type has_bath: bool
    :param theta_ex_d_Ave_d: 日平均外気温度 (℃)
    :type theta_ex_d_Ave_d: ndarray
    :param n_p: 仮想居住人数
    :type n_p: float
    :return: 浴槽沸かし直しによる給湯熱負荷 (MJ/d)
    :rtype: ndarray
    """
    if 1 <= n_p and n_p <= 2:
        n_b_1_d_t = calc_n_b_p_d_t(1, schedule_hw, has_bath)
        n_b_2_d_t = calc_n_b_p_d_t(2, schedule_hw, has_bath)
        L_ba_1_d_ = calc_L_ba_p_d_t(1, bath_insulation, n_b_1_d_t, theta_ex_d_Ave_d)
        L_ba_2_d_t = calc_L_ba_p_d_t(2, bath_insulation, n_b_2_d_t, theta_ex_d_Ave_d)
        return L_ba_1_d_ * (2 - n_p) / (2 - 1) + L_ba_2_d_t * (n_p - 1) / (2 - 1)
    elif 2 <= n_p and n_p <= 3:
        n_b_2_d_t = calc_n_b_p_d_t(2, schedule_hw, has_bath)
        n_b_3_d_t = calc_n_b_p_d_t(3, schedule_hw, has_bath)
        L_ba_2_d_t = calc_L_ba_p_d_t(2, bath_insulation, n_b_2_d_t, theta_ex_d_Ave_d)
        L_ba_3_d_t = calc_L_ba_p_d_t(3, bath_insulation, n_b_3_d_t, theta_ex_d_Ave_d)
        return L_ba_2_d_t * (3 - n_p) / (3 - 2) + L_ba_3_d_t * (n_p - 2) / (3 - 2)
    elif 3 <= n_p and n_p <= 4:
        n_b_3_d_t = calc_n_b_p_d_t(3, schedule_hw, has_bath)
        n_b_4_d_t = calc_n_b_p_d_t(4, schedule_hw, has_bath)
        L_ba_3_d_t = calc_L_ba_p_d_t(3, bath_insulation, n_b_3_d_t, theta_ex_d_Ave_d)
        L_ba_4_d_t = calc_L_ba_p_d_t(4, bath_insulation, n_b_4_d_t, theta_ex_d_Ave_d)
        return L_ba_3_d_t * (4 - n_p) / (4 - 3) + L_ba_4_d_t * (n_p - 3) / (4 - 3)
    else:
        raise ValueError(n_p)


def calc_L_ba_p_d_t(p, bath_insulation, n_b_p_d_t, theta_ex_d_Ave_d):
    """居住人数がp人における浴槽沸かし直しにおける給湯熱負荷 (11)

    :param p: 居住人数 (人)
    :type p: float
    :param bath_insulation: 浴槽の断熱の有無
    :type bath_insulation: bool
    :param n_b_p_d_t: 居住人数p人における入浴人数(人/h)
    :type n_b_p_d_t: ndarray
    :param theta_ex_d_Ave_d: 日平均外気温度 (℃)
    :type theta_ex_d_Ave_d: ndarray
    :return: 居住人数がp人における浴槽沸かし直しにおける給湯熱負荷 (MJ/d)
    :rtype: ndarray
    """
    # 係数a_ba, b_ba
    a_ba_p_d, b_ba_p_d = get_coeff_eq11(bath_insulation, p, theta_ex_d_Ave_d)

    # 24時間化
    a_ba_p_d = np.repeat(a_ba_p_d, 24)
    b_ba_p_d = np.repeat(b_ba_p_d, 24)
    theta_ex_d_Ave_d = np.repeat(theta_ex_d_Ave_d, 24)

    # 浴槽沸かし直しによよる給湯熱負荷 (MJ/h) (11)

    # L_ba_p_d_t の作業領域確保
    L_ba_p_d_t = np.zeros(24 * 365)

    # 1日あたりののべ入浴人数
    n_b_p_d = np.repeat(np.sum(n_b_p_d_t.reshape(365, 24), axis=1), 24)

    # W_b_p_d > = 0 の場合
    f1 = (n_b_p_d > 0)
    L_ba_p_d_t[f1] = (a_ba_p_d[f1] * theta_ex_d_Ave_d[f1] + b_ba_p_d[f1]) * (n_b_p_d_t[f1] / n_b_p_d[f1])

    # W_b_p_d = 0 の場合
    f2 = (n_b_p_d == 0)
    L_ba_p_d_t[f2] = 0

    return L_ba_p_d_t


def get_coeff_eq11(bath_insulation, p, theta_ex_d_Ave_d):
    """ 係数a_ba, b_ba

    :param bath_insulation: 浴槽の断熱の有無
    :type bath_insulation: bool
    :param p: 居住人数 (人)
    :type p: float
    :param theta_ex_d_Ave_d: 日平均外気温度 (℃)
    :type theta_ex_d_Ave_d: ndarray
    :return: 係数a_ba, b_ba
    :rtype: tuple
    """
    if bath_insulation == False:
        # 通常浴槽
        y_off = 0
    elif bath_insulation == True:
        # 高断熱浴槽
        y_off = 1
    else:
        raise ValueError(bath_insulation)

    x_off = (4 - p) * 2

    # 7度未満
    tmp_a = ([get_table_6()[y_off][x_off + 0]] * 365) * (theta_ex_d_Ave_d < 7.0)
    tmp_b = ([get_table_6()[y_off][x_off + 1]] * 365) * (theta_ex_d_Ave_d < 7.0)

    # 7度以上かつ16度未満
    tmp_a = tmp_a + ([get_table_6()[y_off + 2][x_off + 0]] * 365) * (7.0 <= theta_ex_d_Ave_d) * (theta_ex_d_Ave_d < 16.0)
    tmp_b = tmp_b + ([get_table_6()[y_off + 2][x_off + 1]] * 365) * (7.0 <= theta_ex_d_Ave_d) * (theta_ex_d_Ave_d < 16.0)

    # 16度以上かつ25度未満
    tmp_a = tmp_a + ([get_table_6()[y_off + 4][x_off + 0]] * 365) * (16.0 <= theta_ex_d_Ave_d) * (theta_ex_d_Ave_d < 25.0)
    tmp_b = tmp_b + ([get_table_6()[y_off + 4][x_off + 1]] * 365) * (16.0 <= theta_ex_d_Ave_d) * (theta_ex_d_Ave_d < 25.0)

    # 25度以上
    tmp_a = tmp_a + ([get_table_6()[y_off + 6][x_off + 0]] * 365) * (25.0 <= theta_ex_d_Ave_d)
    tmp_b = tmp_b + ([get_table_6()[y_off + 6][x_off + 1]] * 365) * (25.0 <= theta_ex_d_Ave_d)

    return tmp_a, tmp_b





def get_table_6():
    """表6 係数 a_ba, b_ba

    :return: 係数 a_ba, b_ba
    :rtype: list
    """
    table_6 = [
        (-0.12, 6.00, -0.10, 4.91, -0.06, 3.02, 0.00, 0.00),
        (-0.07, 3.98, -0.06, 3.22, -0.04, 2.01, 0.00, 0.00),
        (-0.13, 6.04, -0.10, 4.93, -0.06, 3.04, 0.00, 0.00),
        (-0.08, 4.02, -0.06, 3.25, -0.04, 2.03, 0.00, 0.00),
        (-0.14, 6.21, -0.11, 5.07, -0.07, 3.13, 0.00, 0.00),
        (-0.09, 4.19, -0.07, 3.39, -0.04, 2.12, 0.00, 0.00),
        (-0.12, 5.81, -0.10, 4.77, -0.06, 2.92, 0.00, 0.00),
        (-0.07, 3.80, -0.06, 3.09, -0.04, 1.92, 0.00, 0.00)
    ]
    return table_6

# ============================================================================
# 12. 日平均給水温度
# ============================================================================

def get_Theta_wtr_d(region, Theta_ex_prd_Ave_d):
    """日平均給水温度 (℃) (12)

    :param region: 省エネルギー地域区分
    :type region: int
    :param Theta_ex_prd_Ave_d: 期間平均外気温度 (℃)
    :type Theta_ex_prd_Ave_d: ndarray
    :return: 日平均給水温度 (℃)
    :rtype: ndarray
    """

    # 日平均給水温度を求める際の会期係数
    a_wtr, b_wtr = get_table_7()[region - 1]

    # 日平均給水温度 (12)
    Theta_wtr_d = np.clip(a_wtr * Theta_ex_prd_Ave_d + b_wtr, 0.5, None)

    return Theta_wtr_d

def get_table_7():
    """表 7 日平均給水温度を求める際の回帰係数の値

    :return: 日平均給水温度を求める際の回帰係数の値
    :rtype: list
    """
    table_7 = [
        (0.6639, 3.466),
        (0.6639, 3.466),
        (0.6054, 4.515),
        (0.6054, 4.515),
        (0.8660, 1.665),
        (0.8516, 2.473),
        (0.9223, 2.097),
        (0.6921, 7.167)
    ]
    return table_7

def get_Theta_ex_prd_Ave_d(theta_ex_d_Ave_d):
    """期間平均外気温度 (℃) (13)

    :param theta_ex_d_Ave_d: 日平均外気温度 (℃)
    :type theta_ex_d_Ave_d: ndarray
    :return: 期間平均外気温度 (℃)
    :rtype: ndarray
    """
    # 10日前までを拡張した配列を作る(最終日は削る=>-1)
    tmp = np.zeros(365 + 10 - 1)
    tmp[0:10] = theta_ex_d_Ave_d[-10:]
    tmp[10:] = theta_ex_d_Ave_d[0:364]

    # 畳み込み演算
    # 10日分のデータにそれぞれ0.1を掛けて加算する→平均が求まる
    Theta_ex_prd_Ave_d = np.convolve(tmp, [0.1] * 10, mode='valid')

    return Theta_ex_prd_Ave_d


# ============================================================================
# 13. 日平均外気温度
# ============================================================================

def get_theta_ex_d_Ave_d(Theta_ex_d_t):
    """日平均外気温度 (℃) (14)

    :param Theta_ex_d_t: 外気温度 (℃)
    :type Theta_ex_d_t: ndarray
    :return: 日平均外気温度 (℃)
    :rtype: ndarray
    """
    # 8760時間の一次配列を365*24の二次配列へ再配置させる
    tmp = Theta_ex_d_t.reshape(365, 24)

    # 二次元目を加算することで二次元目を消滅させる
    tmp = np.sum(tmp, axis=1)

    # 24で割ることで平均化する
    theta_ex_d_Ave_d = tmp / 24

    return theta_ex_d_Ave_d


# ============================================================================
# 14. 夜間平均外気温度
# ============================================================================

def get_Theta_ex_Nave_d(Theta_ex_d_t):
    """夜間平均外気温度 (℃) (15)

    :param Theta_ex_d_t: 外気温度 (℃)
    :type Theta_ex_d_t: ndarray
    :return: 夜間平均外気温度 (℃)
    :rtype: ndarray
    """
    # 1時間後ろに配列をずらす(そして、12月31日23時を1月1日0時に移動させる)
    tmp = np.roll(Theta_ex_d_t, 1)

    # ** 1時間ずらしたので、前日23時から当日7時までの代わりに、当日0時から8時までの平均を計算すればよい **

    # 8760時間の一次配列を365*24の二次配列へ再配置させる
    tmp = tmp.reshape(365, 24)

    # 8時～23時を0にする
    tmp[:, 8:] = 0

    # 配列の2次元目を合算して2次元目を消す
    tmp = np.sum(tmp, axis=1)

    # 8で割ることで平均化する
    Theta_ex_Nave_d = tmp / 8

    return Theta_ex_Nave_d


# ============================================================================
# 15. 温水温度の熱負荷
# ============================================================================

def get_L_HWH_d(L_HWH_d_t):
    """ 1日当たりの温水温度の熱負荷 (MJ/d) (16)

    :param L_HWH_d_t: 1時間当たりの温水暖房の熱負荷 (MJ/d)
    :type L_HWH_d_t: ndarray
    :return: 1日当たりの温水暖房の熱負荷 (MJ/d)
    :rtype: ndarray
    """
    # 8760時間の一次配列を365*24の二次配列へ再配置させる
    tmp = L_HWH_d_t.reshape(365, 24)

    # 二次元目を加算することで二次元目を消滅させる
    L_HWH_d = np.sum(tmp, axis=1)

    return L_HWH_d
