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
                      type=None, ls_type=None, P_alpha_sp=None, P_beta_sp=None, W_tnk_ss=None,
                      hotwater_use=None, heating_flag_d=None, A_col=None, P_alpha=None, P_beta=None, V_fan_P0=None,
                      d0=None, d1=None, m_fan_test=None, W_tnk_ass=None, A_stcp=None, b0=None, b1=None, c_p_htm=None,
                      eta_r_tank=None, g_htm=None, Gs_htm=None, hw_connection_type=None, UA_hx=None, UA_stp=None, UA_tank=None
                      ):
    """給湯負荷の計算

    Args:
      n_p(float): 仮想居住人数 (人)
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      has_bath(bool): 浴室等の有無
      bath_function(str): ふろ機能の種類
      pipe_diameter(str): ヘッダー分岐後の径
      kitchen_watersaving_A(bool): 台所水栓の手元止水機能の有無
      kitchen_watersaving_C(bool): 台所水栓の水優先吐水機能の有無
      shower_watersaving_A(bool): 浴室シャワー水栓の手元止水機能の有無
      shower_watersaving_B(bool): 浴室シャワー水栓の小流量吐水機能の有無
      washbowl_watersaving_C(bool): 洗面水栓の水優先吐水機能の有無
      bath_insulation(bool): 浴槽の断熱の有無
      type(str, optional): 太陽熱利用設備の種類 (液体集熱式,空気集熱式,None) (Default value = None)
      ls_type(str, optional): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム) (Default value = None)
      A_sp(float, optional): 太陽熱集熱部の有効集熱面積 (m2) (Default value = None)
      P_alpha_sp(float, optional): 太陽熱集熱部の方位角 (°) (Default value = None)
      P_beta_sp(float, optional): 太陽熱集熱部の傾斜角 (°) (Default value = None)
      W_tnk_ss(float, optional): ソーラーシステムのタンク容量 (L) (Default value = None)
      hotwater_use(bool, optional): 空気集熱式太陽熱利用設備が給湯部を有する場合はTrue (Default value = None)
      heating_flag_d(ndarray, optional): 暖房日 (Default value = None)
      A_col(tuple, optional): 集熱器群の面積 (m2) (Default value = None)
      P_alpha(float, optional): 方位角 (°) (Default value = None)
      P_beta(float, optional): 傾斜角 (°) (Default value = None)
      V_fan_P0(float, optional): 空気搬送ファンの送風機特性曲線において機外静圧をゼロとしたときの空気搬送ファンの風量 (m3/h) (Default value = None)
      d0(tuple, optional): 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の切片 (-) (Default value = None)
      d1(tuple, optional): 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K)) (Default value = None)
      m_fan_test(tuple, optional): 集熱器群を構成する集熱器の集熱性能試験時における単位面積当たりの空気の質量流量 (kg/(s・m2)) (Default value = None)
      W_tnk_ass(float, optional): タンク容量 (L) (Default value = None)

    Returns:
      dict: 1日当たりの給湯設備付加

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
        A_stcp=A_stcp,
        b0=b0,
        b1=b1,
        c_p_htm=c_p_htm,
        eta_r_tank=eta_r_tank,
        g_htm=g_htm,
        Gs_htm=Gs_htm,
        hw_connection_type=hw_connection_type,
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
        UA_hx=UA_hx,
        UA_stp=UA_stp,
        UA_tank=UA_tank,
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

    Args:
      n_p(float): 仮想居住人数 (人)
      L_HWH(ndarray): 温水暖房用熱源機の熱負荷
      heating_flag_d(ndarray): 暖房日
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      HW(dict): 給湯機の仕様
      SHC(dict): 集熱式太陽熱利用設備の仕様

    Returns:
      ndarray: 1日当たりの給湯設備の消費電力量 (kWh/d)

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
                'A_stcp': SHC['A_stcp'],
                'b0': SHC['b0'],
                'b1': SHC['b1'],
                'c_p_htm': SHC['c_p_htm'],
                'eta_r_tank': SHC['eta_r_tank'],
                'g_htm': SHC['g_htm'],
                'Gs_htm': SHC['Gs_htm'],
                'hw_connection_type': SHC['hw_connection_type'],
                'P_alpha_sp': SHC['P_alpha_sp'],
                'P_beta_sp': SHC['P_beta_sp'],
                'UA_hx': SHC['UA_hx'],
                'UA_stp': SHC['UA_stp'],
                'UA_tank': SHC['UA_tank'],
                'W_tnk_ss': SHC['V_tank']
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

    Args:
      SHC(dict): 太陽熱利用設備の仕様
      region(int, optional): 省エネルギー地域区分 (Default value = None)
      sol_region(int, optional): 年間の日射地域区分 (Default value = None)
      heating_flag_d(ndarray, optional): 暖房日 (Default value = None)

    Returns:
      ndarray: 1時間当たりの補機の消費電力量 (kWh/h)

    """
    if SHC is None:
        return np.zeros(24 * 365)
    elif SHC['type'] == '液体集熱式':
        # 第九章「自然エネルギー利用設備」第二節「液体集熱式太陽熱利用設備」の算定方法により定まる
        # 1時間当たりの補機の消費電力量 (kWh/h)
        return lss.calc_E_E_lss_aux_d_t(
            ls_type=SHC['ls_type'],
            P_alpha_sp=SHC['P_alpha_sp'],
            P_beta_sp=SHC['P_beta_sp'],
            region=region,
            sol_region=sol_region,
            P_pump_hc=SHC['P_pump_hc'],
            P_pump_non_hc=SHC['P_pump_non_hc']
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

    Args:
      n_p(float): 仮想居住人数
      L_HWH(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      A_A(float): 床面積の合計[m^2]
      region(int): 地域区分
      sol_region(int): 年間の日射地域区分
      HW(dict): 給湯機の仕様
      SHC(dict): 集熱式太陽熱利用設備の仕様
      heating_flag_d: returns: 1時間当たりの給湯設備のガス消費量 (MJ/h)

    Returns:
      ndarray: 1時間当たりの給湯設備のガス消費量 (MJ/h)

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
                'A_stcp': SHC['A_stcp'],
                'b0': SHC['b0'],
                'b1': SHC['b1'],
                'c_p_htm': SHC['c_p_htm'],
                'eta_r_tank': SHC['eta_r_tank'],
                'g_htm': SHC['g_htm'],
                'Gs_htm': SHC['Gs_htm'],
                'hw_connection_type': SHC['hw_connection_type'],
                'P_alpha_sp': SHC['P_alpha_sp'],
                'P_beta_sp': SHC['P_beta_sp'],
                'UA_hx': SHC['UA_hx'],
                'UA_stp': SHC['UA_stp'],
                'UA_tank': SHC['UA_tank'],
                'W_tnk_ss': SHC['V_tank']
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

    Args:
      n_p(float): 仮想居住人数
      L_HWH(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      A_A(float): 床面積の合計[m^2]
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分
      HW(dict): 給湯機の仕様
      SHC(dict): 集熱式太陽熱利用設備の仕様
      heating_flag_d: returns: 1時間当たりの給湯設備の灯油消費量 (MJ/h) (3)

    Returns:
      ndarray: 1時間当たりの給湯設備の灯油消費量 (MJ/h) (3)

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
                'A_stcp': SHC['A_stcp'],
                'b0': SHC['b0'],
                'b1': SHC['b1'],
                'c_p_htm': SHC['c_p_htm'],
                'eta_r_tank': SHC['eta_r_tank'],
                'g_htm': SHC['g_htm'],
                'Gs_htm': SHC['Gs_htm'],
                'hw_connection_type': SHC['hw_connection_type'],
                'P_alpha_sp': SHC['P_alpha_sp'],
                'P_beta_sp': SHC['P_beta_sp'],
                'UA_hx': SHC['UA_hx'],
                'UA_stp': SHC['UA_stp'],
                'UA_tank': SHC['UA_tank'],
                'W_tnk_ss': SHC['V_tank']
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

    Args:

    Returns:
      ndarray: 1時間当たりの給湯設備のその他の燃料による一次エネルギー消費量

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

    Args:
      hw_type(str): 給湯機／給湯温水暖房機の種類
      bath_function(str): 給湯機の種類
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分
      package_id(str): パッケージID
      hybrid_param(dic): ハイブリッドパラメーター
      e_rtd(float): 当該給湯機の効率
      e_dash_rtd(float): エネルギーの使用の合理化に関する法律」に基づく「特定機器の性能の向上に関する製造事業者等の 判断の基準等」（ガス温水機器）に定義される「エネルギー消費効率」
      Theta_ex_Nave_d(ndarray): 夜間平均外気温 (℃)
      W_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯量 (L/d)
      W_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯量 (L/d)
      W_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯量 (L/d)
      W_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/d)
      W_dash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯量 (L/d)
      W_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯量 (L/d)
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/d)
      L_HWH(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      CO2HP(dict): CO2HPのパラメーター

    Returns:
      ndarray: 1時間当たりの給湯機の消費電力量 (MJ/h)

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

    Args:
      hw_type(str): 給湯機／給湯温水暖房機の種類
      hybrid_category(str): 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機の区分
      e_rtd(float): 当該給湯機の効率
      e_dash_rtd(float): エネルギーの使用の合理化に関する法律」に基づく「特定機器の性能の向上に関する製造事業者等の 判断の基準等」（ガス温水機器）に定義される「エネルギー消費効率」
      bath_function(str): ふろ機能の種類
      Theta_ex_Nave(ndarray): 夜間平均外気温 (℃)
      W_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯量 (L/h)
      W_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯量 (L/h)
      W_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯量 (L/h)
      W_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/h)
      W_dash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯量 (L/h)
      W_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯量 (L/h)
      Theta_ex_Ave(ndarray): 日平均外気温度 (℃)
      L_dashdash_k_d: 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d: 1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_w_d: 1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_b1_d: 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_b2_d: 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_ba1_d: 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_ba2_d: 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/h)
      L_HWH(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      package_id: param L_dashdash_k_d_t:
      L_dashdash_s_d_t: param L_dashdash_w_d_t:
      L_dashdash_b1_d_t: param L_dashdash_b2_d_t:
      L_dashdash_ba1_d_t: param L_dashdash_ba2_d_t:
      hybrid_param: returns: 1時間当たりの給湯機のガス消費量 (MJ/h)
      L_dashdash_k_d_t: 
      L_dashdash_w_d_t: 
      L_dashdash_b2_d_t: 
      L_dashdash_ba2_d_t: 

    Returns:
      ndarray: 1時間当たりの給湯機のガス消費量 (MJ/h)

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

    Args:
      hw_type(str): 給湯機／給湯温水暖房機の種類
      e_rtd(float): 当該給湯機の効率
      e_dash_rtd(float): エネルギーの使用の合理化に関する法律」に基づく「特定機器の性能の向上に関する製造事業者等の 判断の基準等」（ガス温水機器）に定義される「エネルギー消費効率」
      bath_function(str): ふろ機能の種類
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの給湯機の灯油消費量 (MJ/h)

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

    Args:
      hw_type(str): 給湯機／給湯温水暖房機の種類
      bath_function(str): ふろ機能の種類

    Returns:
      str: 評価可能な給湯機／給湯温水暖房機の種類

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

    Args:
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
      L_sun_d_t(ndarray): 1時間当たりの太陽熱利用給湯設備による補正集熱量 (MJ/h)

    Returns:
      ndarray: 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)

    """

    L_dashdash_k_d_t = np.zeros(24 * 365)

    L_dash_d_t = L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t
    f = L_dash_d_t > 0
    L_dashdash_k_d_t[f] = L_dash_k_d_t[f] - L_sun_d_t[f] * (L_dash_k_d_t[f] / L_dash_d_t[f])

    return L_dashdash_k_d_t


def calc_L_dashdash_s_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                         L_sun_d_t):
    """1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/h) (4b)

    Args:
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
      L_sun_d_t(ndarray): 1時間当たりの太陽熱利用給湯設備による補正集熱量 (MJ/h)

    Returns:
      ndarray: 1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/h)

    """
    L_dashdash_s_d_t = np.zeros(24 * 365)

    L_dash_d_t = L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t
    f = L_dash_d_t > 0
    L_dashdash_s_d_t[f] = L_dash_s_d_t[f] - L_sun_d_t[f] * (L_dash_s_d_t[f] / L_dash_d_t[f])

    return L_dashdash_s_d_t


def calc_L_dashdash_w_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                         L_sun_d_t):
    """1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/h) (4c)

    Args:
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
      L_sun_d_t(ndarray): 1時間当たりの太陽熱利用給湯設備による補正集熱量 (MJ/h)

    Returns:
      ndarray: 1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/h)

    """
    L_dashdash_w_d_t = np.zeros(24 * 365)

    L_dash_d_t = L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t
    f = L_dash_d_t > 0
    L_dashdash_w_d_t[f] = L_dash_w_d_t[f] - L_sun_d_t[f] * (L_dash_w_d_t[f] / L_dash_d_t[f])

    return L_dashdash_w_d_t


def calc_L_dashdash_b1_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                          L_sun_d_t):
    """1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯熱負荷 (MJ/h) (4d)

    Args:
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
      L_sun_d_t(ndarray): 1時間当たりの太陽熱利用給湯設備による補正集熱量 (MJ/h)

    Returns:
      ndarray: 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯熱負荷 (MJ/h)

    """
    L_dashdash_b1_d_t = np.zeros(24 * 365)

    L_dash_d_t = L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t
    f = L_dash_d_t > 0
    L_dashdash_b1_d_t[f] = L_dash_b1_d_t[f] - L_sun_d_t[f] * (L_dash_b1_d_t[f] / L_dash_d_t[f])

    return L_dashdash_b1_d_t



def calc_L_dashdash_b2_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                          L_sun_d_t):
    """1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h) (4e)

    Args:
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
      L_sun_d_t(ndarray): 1時間当たりの太陽熱利用給湯設備による補正集熱量 (MJ/h)

    Returns:
      ndarray: 1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h)

    """
    L_dashdash_b2_d_t = np.zeros(24 * 365)

    L_dash_d_t = L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t
    f = L_dash_d_t > 0
    L_dashdash_b2_d_t[f] = L_dash_b2_d_t[f] - L_sun_d_t[f] * (L_dash_b2_d_t[f] / L_dash_d_t[f])

    return L_dashdash_b2_d_t


def calc_L_dashdash_ba1_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                           L_sun_d_t):
    """1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h) (4f)

    Args:
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷 (MJ/hd)
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯熱負荷 (MJ/h)
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷 (MJ/h)
      L_sun_d_t(ndarray): 1時間当たりの太陽熱利用給湯設備による補正集熱量 (MJ/h)

    Returns:
      ndarray: 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)

    """
    L_dashdash_ba1_d_t = np.zeros(24 * 365)

    L_dash_d_t = L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t
    f = L_dash_d_t > 0
    L_dashdash_ba1_d_t[f] = L_dash_ba1_d_t[f] - L_sun_d_t[f] * (L_dash_ba1_d_t[f] / L_dash_d_t[f])

    return L_dashdash_ba1_d_t


def get_L_dashdash_ba2_d_t(L_dash_ba2_d_t):
    """1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h) (4g)

    Args:
      L_dash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における節湯補正給湯負荷 (MJ/h)

    Returns:
      1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h)

    """
    return L_dash_ba2_d_t


def calc_L_sun_d_t(region, sol_region=None, solar_device=None, ls_type=None, P_alpha_sp=None, P_beta_sp=None,
                  W_tnk_ss=None, hotwater_use=None, heating_flag_d=None, A_col=None, P_alpha=None, P_beta=None,
                  V_fan_P0=None, d0=None,
                  d1=None, m_fan_test=None, W_tnk_ass=None, Theta_wtr_d=None, L_dash_k_d_t=None, L_dash_s_d_t=None,
                  L_dash_w_d_t=None, L_dash_b1_d_t=None, L_dash_b2_d_t=None, L_dash_ba1_d_t=None,
                  A_stcp=None, b0=None, b1=None, c_p_htm=None, eta_r_tank=None, g_htm=None, Gs_htm=None,
                  hw_connection_type=None, UA_hx=None, UA_stp=None, UA_tank=None):
    """太陽熱利用給湯設備による補正集熱量

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int, optional): 年間の日射地域区分 (Default value = None)
      solar_device(str, optional): 太陽熱利用設備の種類 (液体集熱式,空気集熱式,None) (Default value = None)
      ls_type(str, optional): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム) (Default value = None)
      A_sp(float, optional): 太陽熱集熱部の有効集熱面積 (m2) (Default value = None)
      P_alpha_sp(float, optional): 太陽熱集熱部の方位角 (°) (Default value = None)
      P_beta_sp(float, optional): 太陽熱集熱部の傾斜角 (°) (Default value = None)
      W_tnk_ss(float, optional): ソーラーシステムのタンク容量 (L) (Default value = None)
      W_tnk_ass(float, optional): タンク容量 (L) (Default value = None)
      Theta_wtr_d(ndarray, optional): 日平均給水温度 (℃) (Default value = None)
      L_dash_k_d_t(ndarrayL, optional): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h) (Default value = None)
      L_dash_s_d_t(ndarray, optional): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h) (Default value = None)
      L_dash_w_d_t(ndarray, optional): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h) (Default value = None)
      L_dash_b1_d_t(ndarray, optional): 1時間当たりの浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/h) (Default value = None)
      L_dash_b2_d_t(ndarray, optional): 1時間当たりの浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/h) (Default value = None)
      L_dash_ba1_d_t(ndarray, optional): 1時間当たりの浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/h) (Default value = None)
      hotwater_use: Default value = None)
      heating_flag_d: Default value = None)
      A_col: Default value = None)
      P_alpha: Default value = None)
      P_beta: Default value = None)
      V_fan_P0: Default value = None)
      d0: Default value = None)
      d1: Default value = None)
      m_fan_test: Default value = None)

    Returns:
      ndarray: 1時間当たりの太陽熱利用設備による補正集熱量 (MJ/h)

    """
    if solar_device == '液体集熱式':
        # 1時間当たりの給湯熱需要（浴槽追焚を除く）
        Q_W_dmd_excl_ba2_d_t = calc_Q_W_dmd_excl_ba2_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t)

        # 日射量データ
        solrad = load_solrad(region, sol_region)

        # 外気温度
        outdoor = load_outdoor()
        Theta_ex_d_t = get_Theta_ex(region, outdoor)

        return lss.calc_L_sun_lss_d_t(
            ls_type=ls_type,
            A_stcp=A_stcp,
            b0 = b0,
            b1 = b1,
            c_p_htm=c_p_htm,
            eta_r_tank=eta_r_tank,
            g_htm=g_htm,
            Gs_htm=Gs_htm,
            hw_connection_type=hw_connection_type,
            P_alpha_sp=P_alpha_sp,
            P_beta_sp=P_beta_sp,
            Theta_wtr_d=Theta_wtr_d,
            UA_hx=UA_hx,
            UA_stp=UA_stp,
            UA_tank=UA_tank,
            V_tank=W_tnk_ss,
            solrad = solrad,
            Q_W_dmd_excl_ba2_d_t = Q_W_dmd_excl_ba2_d_t,
            Theta_ex_d_t = Theta_ex_d_t
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

    Args:
      W_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯量 (L/h)
      Theta_sw_k(int): 台所水栓における基給湯量 (℃)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: 台所水栓における節湯補正給湯負荷 (MJ/h)

    """
    return W_dash_k_d_t * (Theta_sw_k - np.repeat(Theta_wtr_d, 24)) * 4.186 * 10 ** (-3)



def get_L_dash_s_d_t(W_dash_s_d_t, Theta_sw_s, Theta_wtr_d):
    """浴室シャワー水栓における節湯補正給湯負荷 (5b)

    Args:
      W_dash_s_d_t(ndarray): 1時間当たりの浴室シャワーにおける節湯補正給湯量 (L/h)
      Theta_sw_s(int): 浴室シャワーにおける基給湯量 (℃)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: 浴室シャワーにおける節湯補正給湯負荷 (MJ/h)

    """
    return W_dash_s_d_t * (Theta_sw_s - np.repeat(Theta_wtr_d, 24)) * 4.186 * 10 ** (-3)



def get_L_dash_w_d_t(W_dash_w_d_t, Theta_sw_w, Theta_wtr_d):
    """洗面水栓における節湯補正給湯負荷 (5c)

    Args:
      W_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯量 (L/d)
      Theta_sw_w(int): 洗面水栓における基給湯量 (℃)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: 洗面水栓における節湯補正給湯負荷 (MJ/d)

    """
    return W_dash_w_d_t * (Theta_sw_w - np.repeat(Theta_wtr_d, 24)) * 4.186 * 10 ** (-3)


def get_L_dash_bx_d_t(W_dash_b1_d_t, W_dash_b2_d_t, Theta_wtr_d, has_bath, bash_function):
    """浴槽水栓湯はり時における節水補正給湯熱負荷 L_dash_b1_d, L_dash_b2_d

    Args:
      W_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/d)
      W_dash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における節湯補正給湯量 (L/d)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)
      has_bath(bool): 浴室用の有無
      bash_function(str): ふろ機能の種類

    Returns:
      ndarray: 浴槽水栓湯はり時・浴槽自動湯はり時における節水補正給湯熱負荷 (MJ/d)

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

    Args:
      W_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/h)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)
      L_ba_d_t(ndarray): 1時間当たりの浴槽沸かし直しによる給湯熱負荷 (MJ/h)
      has_bath(bool): 浴室等の有無
      bash_function(str): ふろ機能の種類 (給湯単機能,ふろ給湯機(追焚なし),ふろ給湯機(追焚あり))

    Returns:
      ndarray: 浴槽水栓さし湯時／浴槽追焚時における節水補正給湯熱負荷 (MJ/h)

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

    Args:

    Returns:
      int: 台所水栓の基準給湯温度

    """
    return get_table_5()[0]



def get_Theta_sw_s():
    """浴室シャワー水栓の基準給湯温度

    Args:

    Returns:
      int: 浴室シャワー水栓の基準給湯温度

    """
    return get_table_5()[1]



def get_Theta_sw_w():
    """洗面水栓の基準給湯温度

    Args:

    Returns:
      int: 洗面水栓の基準給湯温度

    """
    return get_table_5()[2]


def get_Theta_sw_b1():
    """浴槽水栓湯はりの基準給湯温度

    Args:

    Returns:
      int: 浴槽水栓湯はりの基準給湯温度

    """
    return get_table_5()[3]


def get_Theta_sw_b2():
    """浴槽自動湯はりの基準給湯温度

    Args:

    Returns:
      int: 浴槽自動湯はりの基準給湯温度

    """
    return get_table_5()[4]


def get_Theta_sw_ba1():
    """浴槽水栓さし湯の基準給湯温度

    Args:

    Returns:
      int: 浴槽水栓さし湯の基準給湯温度

    """
    return get_table_5()[5]


def get_table_5():
    """表 5 用途ごとの基準給湯温度

    Args:

    Returns:
      list: 用途ごとの基準給湯温度

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

    Args:
      W_k_d_t(ndarray): 1時間当たりの台所水栓における基準給湯量 (L/h)
      kitchen_watersaving_A(bool): 台所水栓の手元止水機能の有無
      kitchen_watersaving_C(bool): 台所水栓の水優先吐水機能の有無
      pipe_diameter(str): ヘッダー分岐後の径
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: 1時間当たりの台所水栓における節湯補正給湯量 (L/h)

    """
    # 台所水栓における節湯の効果係数
    f_sk = watersaving.get_f_sk(kitchen_watersaving_A, kitchen_watersaving_C, Theta_wtr_d)

    # 配管における節湯の効果係数
    f_sp = watersaving.get_f_sp(pipe_diameter)

    return W_k_d_t * np.repeat(f_sk, 24) * f_sp


def calc_W_dash_s_d_t(W_s_d_t, shower_watersaving_A, shower_watersaving_B, pipe_diameter):
    """1時間当たりの浴室シャワーにおける節湯補正給湯量 (L/h) (6a)

    Args:
      W_s_d_t(ndarray): 浴室シャワーにおける基準給湯量 (L/h)
      shower_watersaving_A(bool): 浴室シャワー水栓の手元止水機能の有無
      shower_watersaving_B(bool): 浴室シャワー水栓の小流量吐水機能の有無
      pipe_diameter(str): ヘッダー分岐後の径

    Returns:
      ndarray: 1時間当たりの浴室シャワーにおける節湯補正給湯量 (L/h)

    """
    # 浴室シャワー水栓のける節湯の効果係数
    f_ss = watersaving.get_f_ss(shower_watersaving_A, shower_watersaving_B)

    # 配管における節湯の効果係数
    f_sp = watersaving.get_f_sp(pipe_diameter)

    return W_s_d_t * f_ss * f_sp


def calc_W_dash_w_d_t(W_w_d_t, washbowl_watersaving_C, pipe_diameter, Theta_wtr_d):
    """1時間当たりの台所水栓における節湯補正給湯量 (L/h) (6c)

    Args:
      W_w_d_t(ndarray): 台所水栓における基準給湯量 (L/h)
      washbowl_watersaving_C(bool): 洗面水栓の水優先吐水機能の有無
      pipe_diameter(str): ヘッダー分岐後の径
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: 1時間当たりの台所水栓における節湯補正給湯量 (L/h)

    """
    # 配管における節湯の効果係数
    f_sp = watersaving.get_f_sp(pipe_diameter)

    # 洗面水栓における節湯の効果係数
    f_sw = watersaving.get_f_sw(washbowl_watersaving_C, Theta_wtr_d)

    return W_w_d_t * np.repeat(f_sw, 24) * f_sp


def calc_W_dash_b1_d_t(W_b1_d_t, pipe_diameter):
    """1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/h) (6d)

    Args:
      W_b1_d_t(ndarray): 浴槽水栓湯はり時における基準給湯量 (L/h)
      pipe_diameter(str): ヘッダー分岐後の径

    Returns:
      ndarray: 1時間当たりの浴槽水栓湯はり時における節湯補正給湯量 (L/h)

    """
    # 配管における節湯の効果係数
    f_sp = watersaving.get_f_sp(pipe_diameter)

    # 浴槽における節湯の効果係数
    f_sb = watersaving.get_f_sb()

    return W_b1_d_t * f_sp * f_sb


def calc_W_dash_b2_d_t(W_b2_d_t):
    """1時間当たりの浴槽自動湯はり時における節湯補正給湯量 (L/h) (6e)

    Args:
      W_b2_d_t(ndarray): 浴槽自動湯はり時における基準給湯量 (L/h)

    Returns:
      ndarray: 1時間当たりの浴槽自動湯はり時における節湯補正給湯量 (L/h)

    """
    # 浴槽における節湯の効果係数
    f_sb = watersaving.get_f_sb()

    return W_b2_d_t * f_sb


def calc_W_dash_ba1_d_t(W_ba1_d_t, pipe_diameter):
    """1時間当たりの浴槽水栓さし湯時における節湯補正給湯量 (L/h) (6f)

    Args:
      W_ba1_d_t(ndarray): 1時間当たりの浴室水栓さし湯時における基準給湯量 (L/h)
      pipe_diameter(str): ヘッダー分岐後の径

    Returns:
      1時間当たりの浴槽水栓さし湯時における節湯補正給湯量 (L/h)

    """
    # 配管における節湯の効果係数
    f_sp = watersaving.get_f_sp(pipe_diameter)

    return W_ba1_d_t * f_sp


# ============================================================================
# 10. 基準給湯量
# ============================================================================

def calc_W_k_d_t(n_p, schedule_hw):
    """1時間当たりの台所水栓における基準給湯量 (L/h) (7a)

    Args:
      n_p(float): 仮想居住人数 (人)
      schedule_hw(ndarray): 給湯スケジュール

    Returns:
      ndarray: 1時間当たりの台所水栓における基準給湯量 (L/h)

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

    Args:
      n_p(float): 仮想居住人数 (人)
      schedule_hw(ndarray): 給湯スケジュール
      has_bath(bool): 浴室等の有無

    Returns:
      ndarray: 1時間当たりの浴室シャワー水栓における基準給湯量 (L/h)

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

    Args:
      n_p(float): 仮想居住人数 (人)
      schedule_hw(ndarray): 給湯スケジュール

    Returns:
      ndarray: 1時間当たりの洗面水栓における基準給湯量 (L/h)

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
    """生活スケジュールパターン

    Args:

    Returns:
      list: 生活スケジュールパターン

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

    Args:
      p(float): 居住人数 (人)
      schedule_hw(ndarray): 給湯スケジュール

    Returns:
      ndarray: 1時間当たりの居住人数がp人における台所水栓における基準給湯量 (L/h)

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

    Args:
      p(float): 居住人数 (人)
      schedule_hw(ndarray): 給湯スケジュール
      has_bath: returns: 1時間当たりの居住人数がp人における洗面シャワー水栓における基準給湯量 (L/h)

    Returns:
      ndarray: 1時間当たりの居住人数がp人における洗面シャワー水栓における基準給湯量 (L/h)

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

    Args:
      p(float): 居住人数 (人)
      schedule_hw(ndarray): 給湯スケジュール

    Returns:
      ndarray: 1日当たりの居住人数がp人における洗面水栓における基準給湯量 (L/d)

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

    Args:
      n_p(float): 仮想居住人数 (人)
      schedule_hw(ndarray): 給湯スケジュール
      has_bath(bool): 浴室等の有無
      bath_function(str): ふろ機能の種類

    Returns:
      ndarray: 浴槽水栓湯はり時における給湯基準量 (L/h)

    """
    if bath_function == '給湯単機能':
        return calc_W_b_d_t(n_p, schedule_hw, has_bath)
    elif bath_function == 'ふろ給湯機(追焚なし)' or bath_function == 'ふろ給湯機(追焚あり)':
        return np.zeros(24 * 365)
    else:
        raise ValueError(bath_function)



def calc_W_b2_d_t(n_p, schedule_hw, has_bath, bath_function):
    """浴槽自動湯はり時における給湯基準量 (L/h)

    Args:
      n_p(float): 仮想居住人数 (人)
      schedule_hw(ndarray): 給湯スケジュール
      has_bath(bool): 浴室等の有無
      bath_function(str): ふろ機能の種類

    Returns:
      ndarray: 浴槽自動湯はり時における給湯基準量 (L/d)

    """
    if bath_function == 'ふろ給湯機(追焚なし)' or bath_function == 'ふろ給湯機(追焚あり)':
        return calc_W_b_d_t(n_p, schedule_hw, has_bath)
    elif bath_function == '給湯単機能':
        return np.zeros(24 * 365)
    else:
        raise ValueError(bath_function)


def calc_W_b_d_t(n_p, schedule_hw, has_bath):
    """1時間当たりの浴槽湯はり時における基準給湯量 (L/h) (8)

    Args:
      n_p(float): 仮想居住人数 (人)
      schedule_hw(ndarray): 給湯スケジュール
      has_bath(bool): 浴室等の有無

    Returns:
      ndarray: 1時間あたりの浴槽湯はり時における基準給湯量 (L/h)

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

    Args:
      p(float): 居住人数 (人)
      schedule_hw(ndarray): 給湯スケジュール
      has_bath(bool): 浴室等の有無

    Returns:
      ndarray: 1時間あたりの居住人数がp人における浴槽湯はり時における基準給湯量 (L/h)

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

    Args:
      p(float): 居住人数 (人)
      schedule_hw(ndarray): 給湯スケジュール
      has_bath(bool): 浴室等の有無

    Returns:
      ndarray: 1時間あたりの居住人数がp人における入浴人数(人/h)

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
    """浴槽水栓さし湯時における基準給湯量 (L/h) (9)

    Args:
      bath_function(str): ふろ機能の種類
      L_ba_d_t(ndarray): 1時間当たりの浴槽沸かし直しによる給湯熱負荷 (MJ/h)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: 浴槽水栓さし湯時における基準給湯量 (L/h)

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

    Args:
      bath_insulation(bool): 浴槽の断熱の有無
      schedule_hw(ndarray): 給湯スケジュール
      has_bath(bool): 浴室等の有無
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)
      n_p(float): 仮想居住人数

    Returns:
      ndarray: 浴槽沸かし直しによる給湯熱負荷 (MJ/d)

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

    Args:
      p(float): 居住人数 (人)
      bath_insulation(bool): 浴槽の断熱の有無
      n_b_p_d_t(ndarray): 居住人数p人における入浴人数(人/h)
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)

    Returns:
      ndarray: 居住人数がp人における浴槽沸かし直しにおける給湯熱負荷 (MJ/d)

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
    """係数a_ba, b_ba

    Args:
      bath_insulation(bool): 浴槽の断熱の有無
      p(float): 居住人数 (人)
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)

    Returns:
      tuple: 係数a_ba, b_ba

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

    Args:

    Returns:
      list: 係数 a_ba, b_ba

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

    Args:
      region(int): 省エネルギー地域区分
      Theta_ex_prd_Ave_d(ndarray): 期間平均外気温度 (℃)

    Returns:
      ndarray: 日平均給水温度 (℃)

    """

    # 日平均給水温度を求める際の会期係数
    a_wtr, b_wtr = get_table_7()[region - 1]

    # 日平均給水温度 (12)
    Theta_wtr_d = np.clip(a_wtr * Theta_ex_prd_Ave_d + b_wtr, 0.5, None)

    return Theta_wtr_d

def get_table_7():
    """表 7 日平均給水温度を求める際の回帰係数の値

    Args:

    Returns:
      list: 日平均給水温度を求める際の回帰係数の値

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

    Args:
      theta_ex_d_Ave_d(ndarray): 日平均外気温度 (℃)

    Returns:
      ndarray: 期間平均外気温度 (℃)

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

    Args:
      Theta_ex_d_t(ndarray): 外気温度 (℃)

    Returns:
      ndarray: 日平均外気温度 (℃)

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

    Args:
      Theta_ex_d_t(ndarray): 外気温度 (℃)

    Returns:
      ndarray: 夜間平均外気温度 (℃)

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
    """1日当たりの温水温度の熱負荷 (MJ/d) (16)

    Args:
      L_HWH_d_t(ndarray): 1時間当たりの温水暖房の熱負荷 (MJ/d)

    Returns:
      ndarray: 1日当たりの温水暖房の熱負荷 (MJ/d)

    """
    # 8760時間の一次配列を365*24の二次配列へ再配置させる
    tmp = L_HWH_d_t.reshape(365, 24)

    # 二次元目を加算することで二次元目を消滅させる
    L_HWH_d = np.sum(tmp, axis=1)

    return L_HWH_d


def calc_Q_W_dmd_excl_ba2_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t):
    """1時間当たりの給湯熱需要（浴槽追焚を除く） (MJ/h) (15)

    Args:
      L_dash_k_d_t(ndarrayL, optional): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h) (Default value = None)
      L_dash_s_d_t(ndarray, optional): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h) (Default value = None)
      L_dash_w_d_t(ndarray, optional): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h) (Default value = None)
      L_dash_b1_d_t(ndarray, optional): 1時間当たりの浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/h) (Default value = None)
      L_dash_b2_d_t(ndarray, optional): 1時間当たりの浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/h) (Default value = None)
      L_dash_ba1_d_t(ndarray, optional): 1時間当たりの浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/h) (Default value = None)

    Returns:
      ndarray: 1時間当たりの給湯熱需要（浴槽追焚を除く） (MJ/h)

    """
    return L_dash_k_d_t + L_dash_s_d_t + L_dash_w_d_t + L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t

