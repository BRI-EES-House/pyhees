# ============================================================================
# 第四章 暖冷房設備
# 第七節 温水暖房
# Ver.10（エネルギー消費性能計算プログラム（住宅版）Ver.02.04～）
# ============================================================================

import numpy as np

import pyhees.section3_1 as ld

import pyhees.section4_7_a as hs_oil
import pyhees.section4_7_b as hs_gas
import pyhees.section4_7_c as hs_eheater
import pyhees.section4_7_d as hs_ehpump
import pyhees.section4_7_e as hs_gas_hybrid
import pyhees.section4_7_f as hs_hybrid_gas
import pyhees.section4_7_g as hs_whybrid
import pyhees.section4_7_n as hs_ghpump

import pyhees.section4_7_j as rad_panel
import pyhees.section4_7_k as rad_fanc
import pyhees.section4_7_l as rad_floor

import pyhees.section4_7_q as sc4_7_q

import pyhees.section4_7_i as pipe

from pyhees.section4_7_common import get_Q_out_H_hs_d_t

from pyhees.section11_1 import \
    load_outdoor, \
    get_Theta_ex, \
    get_X_ex, \
    calc_h_ex, \
    get_Theta_ex_a_Ave, \
    get_Theta_ex_d_Ave_d, \
    get_Theta_ex_H_Ave


# ============================================================================
# 5. 最大暖房出力
# ============================================================================


def calc_Q_max_H_d_t_i(radiator, A_HCZ, Theta_SW, region, mode, R_type):
    """最大暖房出力

    Args:
      radiator(dict): 放熱器仕様
      A_HCZ(float): 暖冷房区画の床面積
      Theta_SW(float): 往き温水温度
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      R_type(string): 居室の形式

    Returns:
      ndarray: 最大暖房出力

    """
    return calc_Q_max_H_rad_d_t_i(radiator, A_HCZ, Theta_SW, region, mode, R_type)


# ============================================================================
# 6. エネルギー消費量
# ============================================================================


# ============================================================================
# 6.1 消費電力量
# ============================================================================


def calc_E_E_H_d_t(H_HS, H_MR, H_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_rad, L_CS_x_t, L_CL_x_t, HW=None, CG=None):
    """消費電力量 (1)

    Args:
      H_HS(dict): 温水暖房機の仕様
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      L_T_H_rad(ndarray): 放熱器の暖房負荷
      L_CS_x_t(ndarray): 暖冷房区画の冷房顕熱負荷
      L_CL_x_t(ndarray): 暖冷房区画の冷房潜熱負荷
      HW(dict, optional): 給湯機の仕様 (Default value = None)
      CG(dict, optional): コージェネレーション設備の仕様 (Default value = None)
      A_A: returns: 消費電力量 (1)

    Returns:
      ndarray: 消費電力量 (1)

    """
    rad_types = get_rad_type_list()

    rad_list = get_rad_list(H_MR, H_OR)

    E_E_hs_d_t = calc_E_E_hs_d_t(H_HS, H_MR, H_OR, region, A_A, A_MR, A_OR, mode_MR, mode_OR, L_T_H_rad, HW, CG, L_CS_x_t, L_CL_x_t)

    # 主たる居室で温水床暖房とエアコンを併用する場合か否か
    racfh_combed = H_MR['type'] == '温水床暖房（併用運転に対応）'

    # 温水暖房用熱源機の往き温水温度
    Theta_SW_hs_op = get_Theta_SW_hs_op(H_HS['type'], HW, CG, racfh_combed)
    p_hs_d_t = calc_p_hs_d_t(Theta_SW_hs_op, rad_list, L_T_H_rad, A_A, A_MR, A_OR, region, mode_MR, mode_OR)
    Theta_SW_d_t = get_Theta_SW_d_t(Theta_SW_hs_op, p_hs_d_t)

    E_E_rad_d_t = np.zeros((5, 24 * 365))
    for i in [1, 3, 4, 5]:
        if rad_list[i - 1] is None:
            continue
        if rad_list[i - 1]['type'] in rad_types:
            radiator = rad_list[i - 1]
            R_type = '主たる居室' if i == 1 else 'その他の居室'
            mode = mode_MR if i == 1 else mode_OR
            A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)

            Q_max_H_rad_d_t_i = calc_Q_max_H_rad_d_t_i(radiator, A_HCZ, Theta_SW_d_t, region, mode, R_type)
            Q_T_H_rad_d_t_i = calc_Q_T_H_rad_d_t_i(Q_max_H_rad_d_t_i, L_T_H_rad[i - 1])

            E_E_rad_d_t_i = calc_E_E_rad_d_t_i(i, radiator, Q_T_H_rad_d_t_i, Theta_SW_d_t, A_A, A_MR, A_OR, region, mode,
                                               R_type)
            E_E_rad_d_t[i - 1, :] = E_E_rad_d_t_i

            print('{} E_E_rad_d_t_{} = {} [KWh] (L_T_H_rad_d_t_{} = {} [MJ])'.format(radiator['type'], i,
                                                                                     np.sum(E_E_rad_d_t_i), i,
                                                                                     np.sum(L_T_H_rad[i - 1])))

    E_E_H_d_t = E_E_hs_d_t + np.sum(E_E_rad_d_t, axis=0)

    return E_E_H_d_t


# ============================================================================
# 6.2 灯油消費量
# ============================================================================


def calc_E_K_H_d_t(H_HS, H_MR, H_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_rad, HW, CG):
    """灯油消費量 (2)

    Args:
      H_HS(dict): 温水暖房機の仕様
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      L_T_H_rad(ndarray): 放熱器の暖房負荷
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器

    Returns:
      ndarray: 灯油消費量 (2)

    """
    return calc_E_K_hs_d_t(H_HS, H_MR, H_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_rad, HW, CG)


# ============================================================================
# 6.3 ガス消費量
# ============================================================================


def calc_E_G_H_d_t(H_HS, H_MR, H_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_rad, HW, CG):
    """ガス消費量 (3)

    Args:
      H_HS(dict): 温水暖房機の仕様
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      L_T_H_rad(ndarray): 放熱器の暖房負荷
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器

    Returns:
      ndarray: ガス消費量 (3)

    """
    return calc_E_G_hs_d_t(H_HS, H_MR, H_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_rad, HW, CG)


# ============================================================================
# 6.4 その他の燃料による一次エネルギー消費量
# ============================================================================


def calc_E_M_H_d_t(H_HS):
    """その他の燃料による一次エネルギー消費量 (4)

    Args:
      H_HS(dict): 温水暖房機の仕様

    Returns:
      ndarray: その他の燃料による一次エネルギー消費量 (4)

    """
    return get_E_M_hs_d_t(H_HS)


# ============================================================================
# 7. 温水暖房熱源機のエネルギー消費量
# ============================================================================


def calc_Q_UT_hs_d_t(H_HS, H_MR, H_OR, region, A_A, A_MR, A_OR, mode_MR, mode_OR, L_T_H_rad, HW, CG, L_CS_x_t_i, L_CL_x_t_i):
    """温水暖房用熱源機の未処理

    Args:
      H_HS(dict): 温水暖房機の仕様
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      L_T_H_rad(ndarray): 放熱器の暖房負荷
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      L_CS_x_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの冷房顕熱負荷 (MJ/h)
      L_CL_x_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの冷房潜熱負荷 (MJ/h)

    Returns:
      ndarray: 温水暖房用熱源機の未処理

    """
    hs_type = H_HS['type']

    # 主たる居室、その他の居室という単位で設定された放熱機器を暖房区画ごとの配列に変換
    rad_list = get_rad_list(H_MR, H_OR)

    # 主たる居室で温水床暖房とエアコンを併用する場合か否か
    racfh_combed = H_MR['type'] == '温水床暖房（併用運転に対応）'

    # 温水暖房用熱源機の往き温水温度
    Theta_SW_hs_op = get_Theta_SW_hs_op(hs_type, HW, CG, racfh_combed)
    p_hs = calc_p_hs_d_t(Theta_SW_hs_op, rad_list, L_T_H_rad, A_A, A_MR, A_OR, region, mode_MR, mode_OR)
    Theta_SW_d_t = get_Theta_SW_d_t(Theta_SW_hs_op, p_hs)

    # 温水暖房用熱源機の温水熱需要
    Q_dmd_H_hs_d_t = calc_Q_dmd_H_hs_d_t(rad_list, H_HS['pipe_insulation'], H_HS['underfloor_pipe_insulation'],
                                         Theta_SW_d_t, A_A, A_MR, A_OR, region,
                                         mode_MR, mode_OR, L_T_H_rad)

    # 処理暖房負荷
    Q_T_H_rad = np.zeros((5, 24 * 365))
    for i in [1, 3, 4, 5]:

        if rad_list[i - 1] is None:
            continue

        # 1時間当たりの暖冷房区画iに設置された放熱器の最大暖房出力
        A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)
        R_type = '主たる居室' if i == 1 else 'その他の居室'
        mode = mode_MR if i == 1 else mode_OR
        Q_max_H_rad_d_t_i = calc_Q_max_H_rad_d_t_i(rad_list[i - 1], A_HCZ, Theta_SW_d_t, region, mode, R_type)

        # 1時間当たりの暖冷房区画iに設置された放熱器の処理暖房負荷
        Q_T_H_rad[i - 1, :] = calc_Q_T_H_rad_d_t_i(Q_max_H_rad_d_t_i, L_T_H_rad[i - 1])

    # 温水暖房用熱源機の温水供給運転率
    r_WS_hs = calc_r_WS_hs_d_t(rad_list, Q_dmd_H_hs_d_t, Q_T_H_rad, Theta_SW_d_t, region, A_A, A_MR, A_OR, mode_MR)

    if hs_type in ['石油温水暖房機', '石油給湯温水暖房機', '石油従来型温水暖房機', '石油従来型給湯温水暖房機', '石油潜熱回収型温水暖房機', '石油潜熱回収型給湯温水暖房機']:

        # 定格効率
        if 'e_rtd_hs' in H_HS:
            e_rtd = H_HS['e_rtd_hs']
        else:
            e_rtd = hs_oil.get_e_rtd_default(hs_type)

        # 温水暖房用熱源機の温水熱需要
        Q_dmd_H_hs_d_t = calc_Q_dmd_H_hs_d_t(rad_list, H_HS['pipe_insulation'], H_HS['underfloor_pipe_insulation'],
                                             Theta_SW_d_t, A_A, A_MR, A_OR, region,
                                             mode_MR, mode_OR, L_T_H_rad)

        # 定格能力の計算のためのパラメータの取得
        rad_types = get_rad_type_list()
        has_MR_hwh = H_MR['type'] in rad_types
        if H_OR is not None:
            has_OR_hwh = H_OR['type'] in rad_types
        else:
            has_OR_hwh = False

        # 温水暖房熱源機の定格能力
        q_rtd_hs = hs_oil.calc_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

        # 最大暖房出力
        Q_max_H_hs_d_t = hs_oil.get_Q_max_H_hs(q_rtd_hs)

        # 温水暖房用熱源機の暖房出力
        Q_out_H_hs = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

        return Q_dmd_H_hs_d_t - Q_out_H_hs
    elif hs_type in ['ガス温水暖房機', 'ガス給湯温水暖房機', 'ガス従来型温水暖房機', 'ガス従来型給湯温水暖房機', 'ガス潜熱回収型温水暖房機', 'ガス潜熱回収型給湯温水暖房機']:

        # 定格効率
        if 'e_rtd_hs' in H_HS:
            e_rtd = H_HS['e_rtd_hs']
        else:
            e_rtd = hs_gas.get_e_rtd_default(hs_type)

        # 温水暖房用熱源機の温水熱需要
        Q_dmd_H_hs_d_t = calc_Q_dmd_H_hs_d_t(rad_list, H_HS['pipe_insulation'], H_HS['underfloor_pipe_insulation'],
                                             Theta_SW_d_t, A_A, A_MR, A_OR, region,
                                             mode_MR, mode_OR, L_T_H_rad)

        # 定格能力の計算のためのパラメータの取得
        rad_types = get_rad_type_list()
        has_MR_hwh = H_MR['type'] in rad_types
        if H_OR is not None:
            has_OR_hwh = H_OR['type'] in rad_types
        else:
            has_OR_hwh = False

        # 温水暖房熱源機の定格能力
        q_rtd_hs = hs_gas.calc_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

        # 最大暖房出力
        Q_max_H_hs_d_t = hs_gas.get_Q_max_H_hs(q_rtd_hs)

        # 温水暖房用熱源機の暖房出力
        Q_out_H_hs = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

        return Q_dmd_H_hs_d_t - Q_out_H_hs
    elif hs_type == '電気ヒーター温水暖房機' or hs_type == '電気ヒーター給湯温水暖房機':
        # 最大出力の計算のためのパラメータの取得
        rad_types = get_rad_type_list()
        has_MR_hwh = H_MR['type'] in rad_types
        if H_OR is not None:
            has_OR_hwh = H_OR['type'] in rad_types
        else:
            has_OR_hwh = False

        # 最大出力
        Q_max_H_hs_d_t = hs_eheater.calc_Q_max_H_hs(
            region=region,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            mode_MR=mode_MR,
            mode_OR=mode_OR,
            has_MR_hwh=has_MR_hwh,
            has_OR_hwh=has_OR_hwh
        )

        # 温水暖房用熱源機の暖房出力
        Q_out_H_hs_d_t = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

        return Q_dmd_H_hs_d_t - Q_out_H_hs_d_t
    elif hs_type == '電気ヒートポンプ温水暖房機':
        # 定格の計算のためのパラメータの取得
        rad_types = get_rad_type_list()
        has_MR_hwh = H_MR['type'] in rad_types
        if H_OR is not None:
            has_OR_hwh = H_OR['type'] in rad_types
        else:
            has_OR_hwh = False

        # 定格能力
        q_rtd_hs = hs_ehpump.calc_q_rtd_hs(
            region=region,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            mode_MR=mode_MR,
            mode_OR=mode_OR,
            has_MR_hwh=has_MR_hwh,
            has_OR_hwh=has_OR_hwh
        )

        # 外気条件の取得
        outdoor = load_outdoor()
        Theta_ex = get_Theta_ex(region, outdoor)
        X_ex = get_X_ex(region, outdoor)
        h_ex = calc_h_ex(X_ex, Theta_ex)

        # 最大出力
        Q_max_H_hs_d_t = hs_ehpump.calc_Q_max_H_hs(
            q_rtd_hs=q_rtd_hs,
            Theta_SW_hs=Theta_SW_d_t,
            Theta_ex=Theta_ex,
            h_ex=h_ex
        )

        # 温水暖房用熱源機の暖房出力
        Q_out_H_hs_d_t = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

        return Q_dmd_H_hs_d_t - Q_out_H_hs_d_t
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：ガス瞬間式、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return np.zeros(24 * 365)
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(試験された値を用いる)' or \
            hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(仕様による)':
        # 温水暖房用熱源機の温水熱需要
        Q_dmd_H_hs_d_t = calc_Q_dmd_H_hs_d_t(rad_list, H_HS['pipe_insulation'], H_HS['underfloor_pipe_insulation'],
                                             Theta_SW_d_t, A_A, A_MR, A_OR, region,
                                             mode_MR, mode_OR, L_T_H_rad)

        # 定格能力の計算のためのパラメータの取得
        rad_types = get_rad_type_list()
        has_MR_hwh = H_MR['type'] in rad_types
        if H_OR is not None:
            has_OR_hwh = H_OR['type'] in rad_types
        else:
            has_OR_hwh = False

        # 温水暖房熱源機の定格能力
        q_rtd_hs = hs_gas.calc_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

        # 最大暖房出力
        Q_max_H_hs_d_t = hs_gas.get_Q_max_H_hs(q_rtd_hs)

        # 温水暖房用熱源機の暖房出力
        Q_out_H_hs = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

        return Q_dmd_H_hs_d_t - Q_out_H_hs
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return np.zeros(24 * 365)
    elif hs_type == 'コージェネレーションを使用する':
        return np.zeros(24 * 365)
    elif hs_type == '地中熱ヒートポンプ温水暖房機':
        # 外気条件の取得
        # 外気温
        outdoor = load_outdoor()
        Theta_ex = get_Theta_ex(region, outdoor)
        Theta_ex_a_Ave = get_Theta_ex_a_Ave(Theta_ex)
        Theta_ex_d_Ave_d = get_Theta_ex_d_Ave_d(Theta_ex)
        Theta_ex_H_Ave = get_Theta_ex_H_Ave(Theta_ex, L_T_H_rad)

        # 定格の計算のためのパラメータの取得
        rad_types = get_rad_type_list()
        has_MR_hwh = H_MR['type'] in rad_types
        if H_OR is not None:
            has_OR_hwh = H_OR['type'] in rad_types
        else:
            has_OR_hwh = False

        # 定格能力 付録Hに定める温水暖房用熱源機の最大能力 q_max_hs に等しい
        q_rtd_hs = hs_ghpump.calc_q_rtd_hs(
            region=region,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            mode_MR=mode_MR,
            mode_OR=mode_OR,
            has_MR_hwh=has_MR_hwh,
            has_OR_hwh=has_OR_hwh
        )
        
        # 最大出力
        Q_max_H_hs_d_t = hs_ghpump.calc_Q_max_H_hs_d_t(
            Theta_SW_d_t=Theta_SW_d_t,
            Theta_ex_d_Ave_d=Theta_ex_d_Ave_d,
            Theta_ex_H_Ave=Theta_ex_H_Ave,
            Theta_ex_a_Ave=Theta_ex_a_Ave,
            q_max_hs=q_rtd_hs,
            L_H_x_t_i=L_T_H_rad,
            L_CS_x_t_i=L_CS_x_t_i,
            L_CL_x_t_i=L_CL_x_t_i,
            HeatExchangerType=H_HS.get('HeatExchanger')
        )

        # 温水暖房用熱源機の暖房出力
        Q_out_H_hs_d_t = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

        return Q_dmd_H_hs_d_t - Q_out_H_hs_d_t
    else:
        raise ValueError(hs_type)


# ============================================================================
# 7.1 エネルギー消費量
# ============================================================================


def calc_E_E_hs_d_t(H_HS, H_MR, H_OR, region, A_A, A_MR, A_OR, mode_MR, mode_OR, L_T_H_rad, HW, CG, L_CS_x_t_i, L_CL_x_t_i):
    """温水暖房用熱源機の消費電力量

    Args:
      H_HS(dict): 温水暖房機の仕様
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      L_T_H_rad(ndarray): 放熱器の暖房負荷
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器
      L_CS_x_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの冷房顕熱負荷 (MJ/h)
      L_CL_x_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの冷房潜熱負荷 (MJ/h)

    Returns:
      ndarray: 水暖房用熱源機の消費電力量

    """
    hs_type = H_HS['type']

    # 主たる居室、その他の居室という単位で設定された放熱機器を暖房区画ごとの配列に変換
    rad_list = get_rad_list(H_MR, H_OR)

    # 主たる居室で温水床暖房とエアコンを併用する場合か否か
    racfh_combed = H_MR['type'] == '温水床暖房（併用運転に対応）'

    # 温水暖房用熱源機の往き温水温度
    Theta_SW_hs_op = get_Theta_SW_hs_op(hs_type, HW, CG, racfh_combed)
    p_hs = calc_p_hs_d_t(Theta_SW_hs_op, rad_list, L_T_H_rad, A_A, A_MR, A_OR, region, mode_MR, mode_OR)
    Theta_SW_d_t = get_Theta_SW_d_t(Theta_SW_hs_op, p_hs)

    # 温水暖房用熱源機の温水熱需要
    Q_dmd_H_hs_d_t = calc_Q_dmd_H_hs_d_t(rad_list, H_HS['pipe_insulation'], H_HS['underfloor_pipe_insulation'],
                                         Theta_SW_d_t, A_A, A_MR, A_OR, region,
                                         mode_MR, mode_OR, L_T_H_rad)

    # 処理暖房負荷
    Q_T_H_rad = np.zeros((5, 24 * 365))
    for i in [1, 3, 4, 5]:

        if rad_list[i - 1] is None:
            continue

        # 1時間当たりの暖冷房区画iに設置された放熱器の最大暖房出力
        A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)
        R_type = '主たる居室' if i == 1 else 'その他の居室'
        mode = mode_MR if i == 1 else mode_OR
        Q_max_H_rad_d_t_i = calc_Q_max_H_rad_d_t_i(rad_list[i - 1], A_HCZ, Theta_SW_d_t, region, mode, R_type)

        # 1時間当たりの暖冷房区画iに設置された放熱器の処理暖房負荷
        Q_T_H_rad[i - 1, :] = calc_Q_T_H_rad_d_t_i(Q_max_H_rad_d_t_i, L_T_H_rad[i - 1])

    # 温水暖房用熱源機の温水供給運転率
    r_WS_hs = calc_r_WS_hs_d_t(rad_list, Q_dmd_H_hs_d_t, Q_T_H_rad, Theta_SW_d_t, region, A_A, A_MR, A_OR, mode_MR)

    if hs_type in ['石油温水暖房機', '石油給湯温水暖房機', '石油従来型温水暖房機', '石油従来型給湯温水暖房機', '石油潜熱回収型温水暖房機', '石油潜熱回収型給湯温水暖房機']:
        # 温水暖房用熱源機の灯油消費量
        E_K_hs = calc_E_K_hs_d_t(H_HS, H_MR, H_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_rad, HW, CG)

        E_E_hs = hs_oil.calc_E_E_hs(
            hs_type=hs_type,
            r_WS_hs=r_WS_hs,
            E_K_hs=E_K_hs
        )
    elif hs_type in ['ガス温水暖房機', 'ガス給湯温水暖房機', 'ガス従来型温水暖房機', 'ガス従来型給湯温水暖房機', 'ガス潜熱回収型温水暖房機', 'ガス潜熱回収型給湯温水暖房機']:
        # 温水暖房用熱源機のガス消費量
        E_G_hs = calc_E_G_hs_d_t(H_HS, H_MR, H_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_rad, HW, CG)

        E_E_hs = hs_gas.calc_E_E_hs(
            r_WS_hs=r_WS_hs,
            E_G_hs=E_G_hs
        )
    elif hs_type == '電気ヒーター温水暖房機' or hs_type == '電気ヒーター給湯温水暖房機':
        # 最大出力の計算のためのパラメータの取得
        rad_types = get_rad_type_list()
        has_MR_hwh = H_MR['type'] in rad_types
        if H_OR is not None:
            has_OR_hwh = H_OR['type'] in rad_types
        else:
            has_OR_hwh = False

        # 最大出力
        Q_max_H_hs_d_t = hs_eheater.calc_Q_max_H_hs(
            region=region,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            mode_MR=mode_MR,
            mode_OR=mode_OR,
            has_MR_hwh=has_MR_hwh,
            has_OR_hwh=has_OR_hwh
        )

        # 温水暖房用熱源機の暖房出力
        Q_out_H_hs_d_t = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

        E_E_hs = hs_eheater.calc_E_E_hs(
            Q_out_H_hs=Q_out_H_hs_d_t,
            r_WS_hs=r_WS_hs
        )
    elif hs_type == '電気ヒートポンプ温水暖房機':
        # 定格の計算のためのパラメータの取得
        rad_types = get_rad_type_list()
        has_MR_hwh = H_MR['type'] in rad_types
        if H_OR is not None:
            has_OR_hwh = H_OR['type'] in rad_types
        else:
            has_OR_hwh = False

        # 定格能力
        q_rtd_hs = hs_ehpump.calc_q_rtd_hs(
            region=region,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            mode_MR=mode_MR,
            mode_OR=mode_OR,
            has_MR_hwh=has_MR_hwh,
            has_OR_hwh=has_OR_hwh
        )

        # 外気条件の取得
        outdoor = load_outdoor()
        Theta_ex = get_Theta_ex(region, outdoor)
        X_ex = get_X_ex(region, outdoor)
        h_ex = calc_h_ex(X_ex, Theta_ex)

        # 最大出力
        Q_max_H_hs_d_t = hs_ehpump.calc_Q_max_H_hs(
            q_rtd_hs=q_rtd_hs,
            Theta_SW_hs=Theta_SW_d_t,
            Theta_ex=Theta_ex,
            h_ex=h_ex
        )

        # 温水暖房用熱源機の暖房出力
        Q_out_H_hs_d_t = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

        # 1時間当たりの熱源機の消費電力量 (kWh/h)
        E_E_hs = hs_ehpump.calc_E_E_hs(
            Q_out_H_hs=Q_out_H_hs_d_t,
            Q_max_H_hs=Q_max_H_hs_d_t,
            Q_dmd_H_hs_d_t=Q_dmd_H_hs_d_t,
            Theta_SW_hs=Theta_SW_d_t,
            Theta_ex=Theta_ex,
            q_rtd_hs=q_rtd_hs
        )
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：ガス瞬間式、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        # 外気温
        outdoor = load_outdoor()
        Theta_ex = get_Theta_ex(region, outdoor)
        X_ex = get_X_ex(region, outdoor)
        h_ex = calc_h_ex(X_ex, Theta_ex)

        # 戻り温水温度 (℃)
        Theta_RW_hs = calc_Theta_RW_hs_d_t(Theta_SW_d_t, rad_list, H_HS['pipe_insulation'],
                                           H_HS['underfloor_pipe_insulation'], A_A, A_MR, A_OR, region,
                                           mode_MR, mode_OR, L_T_H_rad)

        # 1時間当たりの熱源機の消費電力量 (kWh/h)
        E_E_hs = hs_gas_hybrid.calc_E_E_hs(
            Q_dmd_H_hs_d_t=Q_dmd_H_hs_d_t,
            Theta_RW_hs=Theta_RW_hs,
            Theta_ex=Theta_ex,
            h_ex=h_ex,
            Theta_SW_d_t=Theta_SW_d_t,
            TU_place=H_HS['TU_place']
        )
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(試験された値を用いる)' or \
            hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(仕様による)':
        # 温水暖房用熱源機のガス消費量 (MJ/h)
        E_G_hs = calc_E_G_hs_d_t(H_HS, H_MR, H_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_rad, HW, CG)

        # 1時間当たりの熱源機の消費電力量 (kWh/h)
        E_E_hs = hs_hybrid_gas.calc_E_E_hs(
            r_WS_hs=r_WS_hs,
            E_G_hs=E_G_hs
        )
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        # 1時間当たりの熱源機の消費電力量 (kWh/h)
        return hs_whybrid.get_E_E_hs()
    elif hs_type == 'コージェネレーションを使用する':
        # コージェネレーションの場合は電力を計上しない
        return np.zeros(24 * 365)
    elif hs_type == '地中熱ヒートポンプ温水暖房機':
        # 外気温
        outdoor = load_outdoor()
        Theta_ex = get_Theta_ex(region, outdoor)
        Theta_ex_a_Ave = get_Theta_ex_a_Ave(Theta_ex)
        Theta_ex_d_Ave_d = get_Theta_ex_d_Ave_d(Theta_ex)
        Theta_ex_H_Ave = get_Theta_ex_H_Ave(Theta_ex, L_T_H_rad)

        # 定格の計算のためのパラメータの取得
        rad_types = get_rad_type_list()
        has_MR_hwh = H_MR['type'] in rad_types
        if H_OR is not None:
            has_OR_hwh = H_OR['type'] in rad_types
        else:
            has_OR_hwh = False

        # 定格能力 付録Hに定める温水暖房用熱源機の最大能力 q_max_hs に等しい
        q_rtd_hs = hs_ghpump.calc_q_rtd_hs(
            region=region,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            mode_MR=mode_MR,
            mode_OR=mode_OR,
            has_MR_hwh=has_MR_hwh,
            has_OR_hwh=has_OR_hwh
        )

        # 1時間当たりの熱源機の消費電力量 (kWh/h)
        E_E_hs = hs_ghpump.calc_E_E_hs_d_t(
            Q_dmd_H_hs_d_t=Q_dmd_H_hs_d_t,
            Theta_ex_a_Ave=Theta_ex_a_Ave,
            Theta_ex_d_Ave_d=Theta_ex_d_Ave_d,
            Theta_ex_H_Ave=Theta_ex_H_Ave,
            Theta_SW_d_t=Theta_SW_d_t,
            q_max_hs=q_rtd_hs,
            L_H_x_t_i=L_T_H_rad,
            L_CS_x_t_i=L_CS_x_t_i,
            L_CL_x_t_i=L_CL_x_t_i,
            HeatExchangerType=H_HS.get('HeatExchanger')
        )
    else:
        raise ValueError(hs_type)

    print('{} E_E_hs = {} [kwh]'.format(hs_type, np.sum(E_E_hs)))

    return E_E_hs


def get_rad_type_list():
    """放熱系の種類

    Args:

    Returns:
      list: 放熱系の種類

    """
    # 放熱系の種類
    return [
        '温水暖房用パネルラジエーター',
        '温水暖房用ファンコンベクター',
        '温水暖房用床暖房',
        '温水床暖房（併用運転に対応）',
    ]


def get_rad_list(H_MR, H_OR):
    """主たる居室、その他の居室という単位で設定された放熱機器を暖房区画ごとの配列に変換

    Args:
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様

    Returns:
      list: 放熱機器の暖房区画ごとの配列

    """
    # 暖房区画i=1-5に対応した放熱器のリストを作成
    rad_list = [None, None, None, None, None]

    # 放熱系の種類
    rad_types = get_rad_type_list()

    # 主たる居室
    if H_MR is not None:
        if H_MR['type'] in rad_types:
            rad_list[0] = H_MR

    # その他の居室
    if H_OR is not None:
        if H_OR['type'] in rad_types:
            rad_list[1] = H_OR
            rad_list[2] = H_OR
            rad_list[3] = H_OR
            rad_list[4] = H_OR

    return rad_list


def calc_L_HWH(H_HS, H_MR, H_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_rad, HW, CG):
    """温水暖房用熱源機の熱負荷

    Args:
      H_HS(dict): 温水暖房機の仕様
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      L_T_H_rad(ndarray): 放熱器の暖房負荷
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器

    Returns:
      ndarray: 温水暖房用熱源機の熱負荷

    """
    hs_type = H_HS['type']

    # 主たる居室、その他の居室という単位で設定された放熱機器を暖房区画ごとの配列に変換
    rad_list = get_rad_list(H_MR, H_OR)

    # 主たる居室で温水床暖房とエアコンを併用する場合か否か
    racfh_combed = H_MR['type'] == '温水床暖房（併用運転に対応）'

    # 温水暖房用熱源機の往き温水温度
    Theta_SW_hs_op = get_Theta_SW_hs_op(hs_type, HW, CG, racfh_combed)
    p_hs = calc_p_hs_d_t(Theta_SW_hs_op, rad_list, L_T_H_rad, A_A, A_MR, A_OR, region, mode_MR, mode_OR)
    Theta_SW_d_t = get_Theta_SW_d_t(Theta_SW_hs_op, p_hs)

    # 温水暖房用熱源機の温水熱需要
    Q_dmd_H_hs_d_t = calc_Q_dmd_H_hs_d_t(rad_list, H_HS['pipe_insulation'], H_HS['underfloor_pipe_insulation'],
                                         Theta_SW_d_t, A_A, A_MR, A_OR, region,
                                         mode_MR, mode_OR, L_T_H_rad)

    return Q_dmd_H_hs_d_t


def calc_E_K_hs_d_t(H_HS, H_MR, H_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_rad, HW, CG):
    """温水暖房用熱源機の灯油消費量

    Args:
      H_HS(dict): 温水暖房機の仕様
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      L_T_H_rad(ndarray): 放熱器の暖房負荷
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器

    Returns:
      ndarray: 温水暖房用熱源機の灯油消費量

    """
    hs_type = H_HS['type']

    # 主たる居室、その他の居室という単位で設定された放熱機器を暖房区画ごとの配列に変換
    rad_list = get_rad_list(H_MR, H_OR)

    # 主たる居室で温水床暖房とエアコンを併用する場合か否か
    racfh_combed = H_MR['type'] == '温水床暖房（併用運転に対応）'

    # 温水暖房用熱源機の往き温水温度
    Theta_SW_hs_op = get_Theta_SW_hs_op(hs_type, HW, CG, racfh_combed)
    p_hs = calc_p_hs_d_t(Theta_SW_hs_op, rad_list, L_T_H_rad, A_A, A_MR, A_OR, region, mode_MR, mode_OR)
    Theta_SW_d_t = get_Theta_SW_d_t(Theta_SW_hs_op, p_hs)

    if hs_type in ['石油温水暖房機', '石油給湯温水暖房機', '石油従来型温水暖房機', '石油従来型給湯温水暖房機', '石油潜熱回収型温水暖房機', '石油潜熱回収型給湯温水暖房機']:

        # 定格効率
        if 'e_rtd_hs' in H_HS:
            e_rtd = H_HS['e_rtd_hs']
        else:
            e_rtd = hs_oil.get_e_rtd_default(hs_type)

        # 温水暖房用熱源機の温水熱需要
        Q_dmd_H_hs_d_t = calc_Q_dmd_H_hs_d_t(rad_list, H_HS['pipe_insulation'], H_HS['underfloor_pipe_insulation'],
                                             Theta_SW_d_t, A_A, A_MR, A_OR, region,
                                             mode_MR, mode_OR, L_T_H_rad)

        # 定格能力の計算のためのパラメータの取得
        rad_types = get_rad_type_list()
        has_MR_hwh = H_MR['type'] in rad_types
        if H_OR is not None:
            has_OR_hwh = H_OR['type'] in rad_types
        else:
            has_OR_hwh = False

        # 温水暖房熱源機の定格能力
        q_rtd_hs = hs_oil.calc_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

        # 最大暖房出力
        Q_max_H_hs_d_t = hs_oil.get_Q_max_H_hs(q_rtd_hs)

        # 温水暖房用熱源機の暖房出力
        Q_out_H_hs = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

        # 戻り温水温度 (9)
        Theta_RW_hs = calc_Theta_RW_hs_d_t(Theta_SW_d_t, rad_list, H_HS['pipe_insulation'],
                                           H_HS['underfloor_pipe_insulation'], A_A, A_MR, A_OR, region,
                                           mode_MR, mode_OR,
                                           L_T_H_rad)

        # 温水暖房用熱源機の灯油消費量
        E_K_hs = hs_oil.calc_E_K_hs(
            Q_out_H_hs=Q_out_H_hs,
            e_rtd=e_rtd,
            hs_type=hs_type,
            Theta_SW_hs=Theta_SW_d_t,
            Theta_RW_hs=Theta_RW_hs,
            region=region,
            A_A=A_A,
            A_MR=A_MR,
            A_OR=A_OR,
            mode_MR=mode_MR,
            mode_OR=mode_OR,
            has_MR_hwh=has_MR_hwh,
            has_OR_hwh=has_OR_hwh
        )
    elif hs_type in ['ガス温水暖房機', 'ガス給湯温水暖房機', 'ガス従来型温水暖房機', 'ガス従来型給湯温水暖房機', 'ガス潜熱回収型温水暖房機', 'ガス潜熱回収型給湯温水暖房機']:
        E_K_hs = hs_gas.get_E_K_hs()
    elif hs_type == '電気ヒーター温水暖房機' or hs_type == '電気ヒーター給湯温水暖房機':
        E_K_hs = hs_eheater.get_E_K_hs()
    elif hs_type == '電気ヒートポンプ温水暖房機':
        E_K_hs = hs_ehpump.get_E_K_hs()
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：ガス瞬間式、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        E_K_hs = hs_gas_hybrid.get_E_K_hs()
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(試験された値を用いる)' or \
            hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(仕様による)':
        E_K_hs = hs_hybrid_gas.calc_E_K_hs()
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        E_K_hs = hs_whybrid.get_E_K_hs()
    elif hs_type == 'コージェネレーションを使用する':
        E_K_hs = np.zeros(24 * 365)
    elif hs_type == '地中熱ヒートポンプ温水暖房機':
        E_K_hs = hs_ghpump.get_E_K_hs_d_t()
    else:
        raise ValueError(hs_type)

    print('{} E_K_hs = {} [MJ] (L_T_H_rad = {} [MJ])'.format(hs_type, np.sum(E_K_hs), np.sum(L_T_H_rad)))

    return E_K_hs


def calc_E_G_hs_d_t(H_HS, H_MR, H_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_rad, HW, CG):
    """温水暖房用熱源機のガス消費量

    Args:
      H_HS(dict): 温水暖房機の仕様
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      L_T_H_rad(ndarray): 放熱器の暖房負荷
      HW(dict): 給湯機の仕様
      CG(dict): コージェネレーションの機器

    Returns:
      ndarray: 温水暖房用熱源機のガス消費量

    """
    hs_type = H_HS['type']

    # 主たる居室、その他の居室という単位で設定された放熱機器を暖房区画ごとの配列に変換
    rad_list = get_rad_list(H_MR, H_OR)

    # 主たる居室で温水床暖房とエアコンを併用する場合か否か
    racfh_combed = H_MR['type'] == '温水床暖房（併用運転に対応）'

    # 温水暖房用熱源機の往き温水温度
    Theta_SW_hs_op = get_Theta_SW_hs_op(hs_type, HW, CG, racfh_combed)
    p_hs = calc_p_hs_d_t(Theta_SW_hs_op, rad_list, L_T_H_rad, A_A, A_MR, A_OR, region, mode_MR, mode_OR)
    Theta_SW_d_t = get_Theta_SW_d_t(Theta_SW_hs_op, p_hs)

    if hs_type in ['石油温水暖房機', '石油給湯温水暖房機', '石油従来型温水暖房機', '石油従来型給湯温水暖房機', '石油潜熱回収型温水暖房機', '石油潜熱回収型給湯温水暖房機']:
        E_G_hs = hs_oil.get_E_G_hs()
    elif hs_type in ['ガス温水暖房機', 'ガス給湯温水暖房機', 'ガス従来型温水暖房機', 'ガス従来型給湯温水暖房機', 'ガス潜熱回収型温水暖房機', 'ガス潜熱回収型給湯温水暖房機']:

        # 定格効率
        if 'e_rtd_hs' in H_HS:
            e_rtd = H_HS['e_rtd_hs']
        else:
            e_rtd = hs_gas.get_e_rtd_default(hs_type)

        # 温水暖房用熱源機の温水熱需要
        Q_dmd_H_hs_d_t = calc_Q_dmd_H_hs_d_t(rad_list, H_HS['pipe_insulation'], H_HS['underfloor_pipe_insulation'],
                                             Theta_SW_d_t, A_A, A_MR, A_OR, region,
                                             mode_MR, mode_OR, L_T_H_rad)

        # 定格能力の計算のためのパラメータの取得
        rad_types = get_rad_type_list()
        has_MR_hwh = H_MR['type'] in rad_types
        if H_OR is not None:
            has_OR_hwh = H_OR['type'] in rad_types
        else:
            has_OR_hwh = False

        # 温水暖房熱源機の定格能力
        q_rtd_hs = hs_gas.calc_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

        # 最大暖房出力
        Q_max_H_hs_d_t = hs_gas.get_Q_max_H_hs(q_rtd_hs)

        # 温水暖房用熱源機の暖房出力
        Q_out_H_hs = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

        # 戻り温水温度
        Theta_RW_hs = calc_Theta_RW_hs_d_t(Theta_SW_d_t, rad_list, H_HS['pipe_insulation'],
                                           H_HS['underfloor_pipe_insulation'], A_A, A_MR, A_OR, region,
                                           mode_MR, mode_OR, L_T_H_rad)

        # 温水暖房用熱源機の定格能力 (W)
        q_rtd_hs = hs_gas.calc_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

        E_G_hs = hs_gas.calc_E_G_hs(
            e_rtd=e_rtd,
            q_rtd_hs=q_rtd_hs,
            Q_out_H_hs=Q_out_H_hs,
            hs_type=hs_type,
            Theta_SW_hs=Theta_SW_d_t,
        )
    elif hs_type == '電気ヒーター温水暖房機' or hs_type == '電気ヒーター給湯温水暖房機':
        E_G_hs = hs_eheater.get_E_G_hs()
    elif hs_type == '電気ヒートポンプ温水暖房機':
        E_G_hs = hs_ehpump.get_E_G_hs()
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：ガス瞬間式、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':

        # 外気温
        outdoor = load_outdoor()
        Theta_ex = get_Theta_ex(region, outdoor)
        X_ex = get_X_ex(region, outdoor)
        h_ex = calc_h_ex(X_ex, Theta_ex)

        # 温水暖房用熱源機の温水熱需要
        Q_dmd_H_hs_d_t = calc_Q_dmd_H_hs_d_t(rad_list, H_HS['pipe_insulation'], H_HS['underfloor_pipe_insulation'],
                                             Theta_SW_d_t, A_A, A_MR, A_OR, region,
                                             mode_MR, mode_OR, L_T_H_rad)

        # 戻り温水温度
        Theta_RW_hs = calc_Theta_RW_hs_d_t(Theta_SW_d_t, rad_list, H_HS['pipe_insulation'],
                                           H_HS['underfloor_pipe_insulation'], A_A,
                                           A_MR, A_OR, region, mode_MR, mode_OR,
                                           L_T_H_rad)

        E_G_hs = hs_gas_hybrid.calc_E_G_hs(
            Theta_ex=Theta_ex,
            Theta_SW_d_t=Theta_SW_d_t,
            Theta_RW_hs=Theta_RW_hs,
            TU_place=H_HS['TU_place'],
            Q_dmd_H_hs_d_t=Q_dmd_H_hs_d_t
        )
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(試験された値を用いる)' or \
            hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(仕様による)':

        # 温水暖房用熱源機の温水熱需要
        Q_dmd_H_hs_d_t = calc_Q_dmd_H_hs_d_t(rad_list, H_HS['pipe_insulation'], H_HS['underfloor_pipe_insulation'],
                                             Theta_SW_d_t, A_A, A_MR, A_OR, region,
                                             mode_MR, mode_OR, L_T_H_rad)

        # 定格能力の計算のためのパラメータの取得
        rad_types = get_rad_type_list()
        has_MR_hwh = H_MR['type'] in rad_types
        if H_OR is not None:
            has_OR_hwh = H_OR['type'] in rad_types
        else:
            has_OR_hwh = False

        # 温水暖房熱源機の定格能力
        q_rtd_hs = hs_gas.calc_q_rtd_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

        # 最大暖房出力
        Q_max_H_hs_d_t = hs_gas.get_Q_max_H_hs(q_rtd_hs)

        # 温水暖房用熱源機の暖房出力
        Q_out_H_hs = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_H_hs_d_t)

        # 戻り温水温度
        Theta_RW_hs = calc_Theta_RW_hs_d_t(Theta_SW_d_t, rad_list, H_HS['pipe_insulation'],
                                           H_HS['underfloor_pipe_insulation'], A_A, A_MR, A_OR, region,
                                           mode_MR, mode_OR, L_T_H_rad)

        E_G_hs = hs_hybrid_gas.calc_E_G_hs(
            q_rtd_hs=q_rtd_hs,
            Q_out_H_hs=Q_out_H_hs,
            Theta_SW_hs=Theta_SW_d_t,
        )
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        E_G_hs = hs_whybrid.get_E_G_hs()
    elif hs_type == 'コージェネレーションを使用する':
        E_G_hs = np.zeros(24 * 365)
    elif hs_type == '地中熱ヒートポンプ温水暖房機':
        E_G_hs = hs_ghpump.get_E_G_hs_d_t()
    else:
        raise ValueError(hs_type)

    print('{} E_G_hs = {} [MJ] (L_T_H_rad = {} [MJ])'.format(hs_type, np.sum(E_G_hs), np.sum(L_T_H_rad)))

    return E_G_hs


def get_E_M_hs_d_t(H_HS):
    """温水暖房用熱源機のその他の燃料による一次エネルギー消費量

    Args:
      H_HS(dict): 温水暖房機の仕様

    Returns:
      ndarray: 温水暖房用熱源機のその他の燃料による一次エネルギー消費量

    """
    hs_type = H_HS['type']

    if hs_type in ['石油温水暖房機', '石油給湯温水暖房機', '石油従来型温水暖房機', '石油従来型給湯温水暖房機', '石油潜熱回収型温水暖房機', '石油潜熱回収型給湯温水暖房機']:
        return hs_oil.get_E_M_hs()
    elif hs_type in ['ガス温水暖房機', 'ガス給湯温水暖房機', 'ガス従来型温水暖房機', 'ガス従来型給湯温水暖房機', 'ガス潜熱回収型温水暖房機', 'ガス潜熱回収型給湯温水暖房機']:
        return hs_gas.get_E_M_hs()
    elif hs_type == '電気ヒーター温水暖房機' or hs_type == '電気ヒーター給湯温水暖房機':
        return hs_eheater.get_E_M_hs()
    elif hs_type == '電気ヒートポンプ温水暖房機':
        return hs_ehpump.get_E_M_hs()
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：ガス瞬間式、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return hs_gas_hybrid.get_E_M_hs()
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(試験された値を用いる)' or \
            hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(仕様による)':
        return hs_hybrid_gas.calc_E_M_hs()
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return hs_whybrid.get_E_M_hs()
    elif hs_type == 'コージェネレーションを使用する':
        return np.zeros(24 * 365)
    elif hs_type == '地中熱ヒートポンプ温水暖房機':
        return hs_ghpump.get_E_M_hs_d_t()
    else:
        raise ValueError(hs_type)


# ============================================================================
# 7.2 暖房出力
# ============================================================================

def calc_Q_dmd_H_hs_d_t(rad_list, pipe_insulation, underfloor_pipe_insulation, Theta_SW_d_t, A_A, A_MR, A_OR, region,
                        mode_MR, mode_OR,
                        L_T_H_rad_d_t):
    """温水暖房用熱源機の温水熱需要 (6)

    Args:
      rad_list(list: list: list): 放熱機器の暖房区画ごとの配列
      pipe_insulation(bool): 配管断熱の有無
      underfloor_pipe_insulation(bool): 床下配管断熱の有無
      Theta_SW_d_t(ndarray): 往き温水温度 (℃)
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      L_T_H_rad(ndarray): 放熱器の暖房負荷
      L_T_H_rad_d_t: returns: 温水暖房用熱源機の温水熱需要

    Returns:
      ndarray: 温水暖房用熱源機の温水熱需要

    """
    MR_rad_type, r_Af_1 = get_MR_rad_type_and_r_Af_1(rad_list)

    outdoor = load_outdoor()
    Theta_ex = get_Theta_ex(region, outdoor)

    Q_dmd_H_hs_d_t = np.zeros_like(Theta_SW_d_t)

    for i in [1, 3, 4, 5]:

        if rad_list[i - 1] is None:
            continue

        # 1時間当たりの暖冷房区画iに設置された放熱器の最大暖房出力
        A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)
        R_type = '主たる居室' if i == 1 else 'その他の居室'
        mode = mode_MR if i == 1 else mode_OR
        Q_max_H_rad_d_t_i = calc_Q_max_H_rad_d_t_i(rad_list[i - 1], A_HCZ, Theta_SW_d_t, region, mode, R_type)

        # 1時間当たりの暖冷房区画iに設置された放熱器の処理暖房負荷
        Q_T_H_rad_d_t_i = calc_Q_T_H_rad_d_t_i(Q_max_H_rad_d_t_i, L_T_H_rad_d_t[i - 1])

        # 1時間当たりの暖冷房区画iに設置された放熱器の温水供給運転率
        r_WS_rad_d_t_i = calc_r_WS_rad_d_t_i(
            A_HCZ=A_HCZ,
            radiator=rad_list[i - 1],
            Q_T_H_rad=Q_T_H_rad_d_t_i,
            Theta_SW=Theta_SW_d_t,
            region=region,
            mode=mode,
            R_type=R_type
        )

        Q_dmd_H_ln_d_t_i = calc_Q_dmd_H_ln_d_t_i(
            i=i,
            radiator=rad_list[i - 1],
            Q_T_H_rad_d_t_i=Q_T_H_rad_d_t_i,
            Q_max_H_rad_d_t_i=Q_max_H_rad_d_t_i,
            L_T_H_rad_d_t_i=L_T_H_rad_d_t[i - 1],
            Theta_SW_d_t=Theta_SW_d_t,
            Theta_ex=Theta_ex,
            r_WS_rad_d_t_i=r_WS_rad_d_t_i,
            A_A=A_A,
            pipe_insulation=pipe_insulation,
            underfloor_pipe_insulation=underfloor_pipe_insulation,
            MR_rad_type=MR_rad_type,
            r_Af_1=r_Af_1
        )

        Q_dmd_H_hs_d_t = Q_dmd_H_hs_d_t + Q_dmd_H_ln_d_t_i

    return Q_dmd_H_hs_d_t


def get_MR_rad_type_and_r_Af_1(rad_list):
    """主たる居室の放熱機器と当該住戸における温水床暖房の敷設率 (-)

    Args:
      rad_list(list: list: list): 放熱機器の暖房区画ごとの配列

    Returns:
      tuple: 主たる居室の放熱機器と当該住戸における温水床暖房の敷設率 (-)

    """
    if rad_list[0] is not None:
        MR_rad_type = rad_list[0]['type']
        if 'r_Af' in rad_list[0]:
            r_Af_1 = rad_list[0]['r_Af']
        else:
            r_Af_1 = None
    else:
        MR_rad_type = None
        r_Af_1 = None
    return MR_rad_type, r_Af_1


# ============================================================================
# 7.3 温水供給運転率
# ============================================================================


def calc_r_WS_hs_d_t(rad_list, Q_dmd_H_hs_d_t, Q_T_H_rad, Theta_SW, region, A_A, A_MR, A_OR, mode_MR):
    """温水暖房用熱源機の温水供給運転率

    Args:
      rad_list(list: list: list): 放熱機器の暖房区画ごとの配列
      Q_dmd_H_hs_d_t(ndarray): 1時間当たりの熱源機の熱需要 (MJ/h)
      Q_T_H_rad(ndarray): 放熱器の処理暖房負荷
      Theta_SW(ndarray): 往き温水温度 (℃)
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 運転モード 'い', 'ろ', 'は'

    Returns:
      ndarray: 温水暖房用熱源機の温水供給運転率

    """
    # (7a)
    n = sum([rad is not None for rad in rad_list])  # 放熱系統数
    if n == 1:
        A_HCZ = calc_A_HCZ_i(1, A_A, A_MR, A_OR)
        radiator = rad_list[0]
        R_type = '主たる居室'
        tmp = calc_r_WS_ln_d_t_i(A_HCZ, radiator, Q_T_H_rad[0], Theta_SW, region, mode_MR, R_type)
    elif n > 1:
        tmp = np.ones(24 * 365)
    else:
        raise ValueError(n)

    # (7b)
    tmp[Q_dmd_H_hs_d_t == 0] = 0

    return tmp


# ============================================================================
# 7.4 往き温水温度
# ============================================================================


def get_Theta_SW_hs_op(hs_type, HW=None, CG=None, racfh_combed=False):
    """温水暖房用熱源機の往き温水温度の候補

    Args:
      hs_type(str): 温水暖房用熱源機の種類
      HW(dict, optional): 給湯機の仕様 (Default value = None)
      CG(dict, optional): コージェネレーションの機器 (Default value = None)
      racfh_combed (bool, optional): 主たる居室で温水床暖房とエアコンを併用する場合か否か (Default value = False)

    Returns:
      tuple: 温水暖房用熱源機の往き温水温度の候補

    """
    if racfh_combed:
        return sc4_7_q.get_Theta_SW_hs_op()

    if hs_type == '石油従来型温水暖房機' or hs_type == '石油従来型給湯温水暖房機':
        return get_table_4()[0]
    elif hs_type == '石油潜熱回収型温水暖房機' or hs_type == '石油潜熱回収型給湯温水暖房機':
        return get_table_4()[1]
    elif hs_type == 'ガス従来型温水暖房機' or hs_type == 'ガス従来型給湯温水暖房機' or hs_type == 'ガス従来型' or hs_type == 'G_NEJ':
        return get_table_4()[2]
    elif hs_type == 'ガス潜熱回収型温水暖房機' or hs_type == 'ガス潜熱回収型給湯温水暖房機' or hs_type == 'ガス潜熱回収型' or hs_type == 'G_EJ':
        return get_table_4()[3]
    elif hs_type == '電気ヒーター温水暖房機' or hs_type == '電気ヒーター給湯温水暖房機':
        return get_table_4()[4]
    elif hs_type == '電気ヒートポンプ温水暖房機':
        return get_table_4()[5]
    elif hs_type == '地中熱ヒートポンプ温水暖房機':
        return get_table_4()[6]
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：ガス瞬間式、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return get_table_4()[7]
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(試験された値を用いる)' or\
            hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式)(仕様による)':
        return get_table_4()[8]
    elif hs_type == '電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機(給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：電気ヒートポンプ・ガス瞬間式併用)':
        return get_table_4()[9]
    elif hs_type == 'コージェネレーションを使用する':
        from pyhees.section8_a import get_type_BB_HWH
        if 'CG_category' in CG:
            type_BB_HWH = get_type_BB_HWH(CG['CG_category'])
        else:
            type_BB_HWH = CG['type_BB_HWH']
        return get_Theta_SW_hs_op(type_BB_HWH)
    elif hs_type == '給湯・温水暖房一体型を使用する':
        return get_Theta_SW_hs_op(HW['hw_type'])
    else:
        raise ValueError(hs_type)


def calc_p_hs_d_t(Theta_SW_hs_op, rad_list, L_T_H_rad, A_A, A_MR, A_OR, region, mode_MR, mode_OR):
    """温水暖房用熱源機の往き温水温度の区分 (8)

    Args:
      Theta_SW_hs_op(tuple): 温水暖房用熱源機の往き温水温度の候補
      rad_list(list: list: list): 放熱機器の暖房区画ごとの配列
      L_T_H_rad(ndarray): 放熱器の暖房負荷
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'

    Returns:
      ndarray: 温水暖房用熱源機の往き温水温度の区分 (8)

    """
    p_ln = np.zeros((5, 24 * 365), dtype=np.int32)

    # 初期値として、最低温度を指定
    p_ln[:] = len(Theta_SW_hs_op)

    for i in [1, 3, 4, 5]:
        if rad_list[i - 1] is not None:
            A_HCZ_i = calc_A_HCZ_i(i, A_A, A_MR, A_OR)
            mode = mode_MR if i == 1 else mode_OR
            R_type = '主たる居室' if i == 1 else 'その他の居室'
            p_ln_i = calc_p_ln_d_t_i(rad_list[i - 1], L_T_H_rad[i - 1], Theta_SW_hs_op, A_HCZ_i, region, mode, R_type)
            p_ln[i - 1, :] = p_ln_i

    return np.min(p_ln, axis=0)


def get_Theta_SW_d_t(Theta_SW_hs_op, p_hs_d_t):
    """要求往き温水温度

    Args:
      Theta_SW_hs_op(tuple): 各区分における温水暖房用熱源機の往き温水温度 (℃)
      p_hs_d_t(ndarray): 日付d時刻tにおける温水暖房用熱源機の往き温水温度の区分

    Returns:
      ndarray: 日付d時刻tにおける温水暖房用熱源機の往き温水温度 (℃)

    """
    # 一括変換用のndarrayを作成
    n = len(Theta_SW_hs_op)
    array_Theta_SW_hs_op = np.array(Theta_SW_hs_op).reshape((n, 1))

    # p_d_tに基づいて1時間当たりの往き温水温度を取得
    Theta_SW_d_t = array_Theta_SW_hs_op[p_hs_d_t - 1]

    return Theta_SW_d_t.reshape(p_hs_d_t.shape)

def get_table_4():
    """表4 温水暖房用熱源機における往き温水温度の区分及び候補

    Args:

    Returns:
      list: 表4 温水暖房用熱源機における往き温水温度の区分及び候補

    """
    table_4 = [
        (60,),
        (60, 40),
        (60,),
        (60, 40),
        (60,),
        (55, 45, 35),
        (55, 45, 35),
        (60, 40),
        (60, 40),
        (60, 40),
    ]

    return table_4


# ============================================================================
# 7.5 戻り温水温度
# ============================================================================


def calc_Theta_RW_hs_d_t(Theta_SW_hs_d_t, rad_list, pipe_insulation, underfloor_pipe_insulation, A_A, A_MR, A_OR, region,
                         mode_MR, mode_OR,
                         L_T_H_rad):
    """戻り温水温度 (9)

    Args:
      Theta_SW_hs_d_t(ndarray): 温水暖房用熱源機の往き温水温度
      rad_list(list: list: list): 放熱機器の暖房区画ごとの配列
      pipe_insulation(bool): 配管断熱の有無
      underfloor_pipe_insulation(bool): 床下配管断熱の有無
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      L_T_H_rad(ndarray): 放熱器の暖房負荷

    Returns:
      ndarray: 戻り温水温度 (9)

    """
    MR_rad_type, r_Af_1 = get_MR_rad_type_and_r_Af_1(rad_list)

    outdoor = load_outdoor()
    Theta_ex = get_Theta_ex(region, outdoor)

    Q_dmd_H_ln_d_t = np.zeros((5, 24 * 365))
    Q_dash_max_H_rad_d_t = np.zeros((5, 24 * 365))

    for i in [1, 3, 4, 5]:
        if rad_list[i - 1] is None:
            continue
        else:
            if rad_list[i - 1] is None:
                continue

            # 1時間当たりの暖冷房区画iに設置された放熱器の最大暖房出力
            A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)
            R_type = '主たる居室' if i == 1 else 'その他の居室'
            mode = mode_MR if i == 1 else mode_OR
            Q_max_H_rad_d_t_i = calc_Q_max_H_rad_d_t_i(rad_list[i - 1], A_HCZ, Theta_SW_hs_d_t, region, mode, R_type)

            # 1時間当たりの暖冷房区画iに設置された放熱器の処理暖房負荷
            Q_T_H_rad_d_t_i = calc_Q_T_H_rad_d_t_i(Q_max_H_rad_d_t_i, L_T_H_rad[i - 1])

            # 1時間当たりの暖冷房区画iに設置された放熱器の温水供給運転率
            r_WS_rad_d_t_i = calc_r_WS_rad_d_t_i(
                A_HCZ=A_HCZ,
                radiator=rad_list[i - 1],
                Q_T_H_rad=Q_T_H_rad_d_t_i,
                Theta_SW=Theta_SW_hs_d_t,
                region=region,
                mode=mode,
                R_type=R_type
            )

            Q_dmd_H_ln_d_t[i - 1] = calc_Q_dmd_H_ln_d_t_i(
                i=i,
                radiator=rad_list[i - 1],
                Q_T_H_rad_d_t_i=Q_T_H_rad_d_t_i,
                Q_max_H_rad_d_t_i=Q_max_H_rad_d_t_i,
                L_T_H_rad_d_t_i=L_T_H_rad[i - 1],
                Theta_SW_d_t=Theta_SW_hs_d_t,
                Theta_ex=Theta_ex,
                r_WS_rad_d_t_i=r_WS_rad_d_t_i,
                A_A=A_A,
                pipe_insulation=pipe_insulation,
                underfloor_pipe_insulation=underfloor_pipe_insulation,
                MR_rad_type=MR_rad_type,
                r_Af_1=r_Af_1
            )

            Q_dash_max_H_rad_d_t_i = get_Q_dash_max_H_rad_d_t_i(Q_max_H_rad_d_t_i, Q_dmd_H_ln_d_t[i - 1])
            Q_dash_max_H_rad_d_t[i - 1, :] = Q_dash_max_H_rad_d_t_i

    # 1時間ごとの対数平均温度差 (9b)
    T_dif = get_T_dif_d_t(Q_dmd_H_ln_d_t, Q_dash_max_H_rad_d_t)

    # 温水暖房用熱源機の戻り温水温度 (9a)
    Theta_RW_hs_d_t = np.zeros(24 * 365)

    # - 条件1 (熱源機の往き温水温度60度)
    f1 = (Theta_SW_hs_d_t == 60)
    Theta_RW_hs_d_t[f1] = 0.0301 * T_dif[f1] ** 2 - 0.1864 * T_dif[f1] + 20

    # - 条件2 (熱源機の往き温水温度40度)
    f2 = (Theta_SW_hs_d_t == 40)
    Theta_RW_hs_d_t[f2] = 0.0604 * T_dif[f2] ** 2 - 0.1881 * T_dif[f2] + 20

    # 温水暖房用戻り温度は往き温度を超えない
    fover = (Theta_RW_hs_d_t > Theta_SW_hs_d_t)  # 温水暖房用戻り温度は往き温度を超えた日時インデックス
    Theta_RW_hs_d_t[fover] = Theta_SW_hs_d_t[fover]  # 逆転日時の限り、戻り温度=往き温度とする

    return Theta_RW_hs_d_t


def get_Q_dash_max_H_rad_d_t_i(Q_max_H_rad_d_t_i, Q_dmd_H_ln_d_t_i):
    """1時間当たりの温水熱需要が発生する場合の暖冷房区画iに設置された放熱器の最大暖房出力 (9c)

    Args:
      Q_max_H_rad_d_t_i(ndarray): 1時間当たりの暖冷房区画iに設置された放熱器の最大暖房出力
      Q_dmd_H_ln_d_t_i(ndarray): 1時間当たりの暖冷房区画iに設置された放熱器の放熱系統の温水熱需要

    Returns:
      ndarray: 1時間当たりの温水熱需要が発生する場合の暖冷房区画iに設置された放熱器の最大暖房出力 (9c)

    """
    Q_dash_max_H_rad_d_t_i = np.copy(Q_max_H_rad_d_t_i)
    Q_dash_max_H_rad_d_t_i[Q_dmd_H_ln_d_t_i == 0] = 0
    return Q_dash_max_H_rad_d_t_i


def get_T_dif_d_t(Q_dmd_H_ln_d_t, Q_dash_max_H_rad_d_t):
    """1時間ごとの対数平均温度差 (9b)

    Args:
      Q_dmd_H_ln_d_t(ndarray): 1時間当たりの放熱系統の温水熱需要
      Q_dash_max_H_rad_d_t(ndarray): 1時間当たりの放熱器の最大暖房出力

    Returns:
      ndarray: 1時間ごとの対数平均温度差 (9b)

    """
    Q_dmd = np.sum(Q_dmd_H_ln_d_t, axis=0)
    Q_dash_max = np.sum(Q_dash_max_H_rad_d_t, axis=0)

    T_dif_d_t = np.zeros(24 * 365)
    f = (Q_dmd > 0)
    T_dif_d_t[f] = Q_dmd[f] / (Q_dash_max[f] * 0.027583)

    return T_dif_d_t


# ============================================================================
# 8. 放熱系統
# ============================================================================


# ============================================================================
# 8.1 温水熱需要
# ============================================================================


def calc_Q_dmd_H_ln_d_t_i(i, radiator, Q_T_H_rad_d_t_i, Q_max_H_rad_d_t_i, L_T_H_rad_d_t_i, Theta_SW_d_t, Theta_ex,
                          r_WS_rad_d_t_i, A_A, pipe_insulation, underfloor_pipe_insulation,
                          MR_rad_type, r_Af_1):
    """1時間当たりの放熱系統iの温水熱需要 (10)

    Args:
      i(int): 暖冷房区画i
      radiator(dict): 放熱器仕様
      Q_T_H_rad_d_t_i(ndarray): 1時間当たりの暖冷房区画iに設置された放熱器の処理暖房負荷
      Q_max_H_rad_d_t_i(ndarray): 1時間当たりの暖冷房区画iに設置された放熱器の最大暖房出力
      L_T_H_rad_d_t_i(ndarray): 1時間当たりの暖冷房区画iに設置された放熱器の暖房負荷
      Theta_SW_d_t(ndarray): 往き温水温度 (℃)
      Theta_ex(ndarray): 外気絶対温度[K]
      r_WS_rad_d_t_i(ndarray): 1時間当たりの暖冷房区画iに設置された温水床暖房の温水供給運転率
      A_A(float): 床面積の合計 (m2)
      pipe_insulation(bool): 配管断熱の有無
      underfloor_pipe_insulation(bool): 床下配管断熱の有無
      MR_rad_type(str): 主たる居室の放熱器の種類
      r_Af_1(float): 当該住戸における温水床暖房の敷設率 (-)

    Returns:
      ndarray: 1時間当たりの放熱系統iの温水熱需要 (10)

    """
    # 1時間当たりの暖冷房区画iに設置された放熱器の温水熱需要
    Q_dmd_H_rad_d_t_i = calc_Q_dmd_H_rad_d_t_i(radiator, Q_max_H_rad_d_t_i, L_T_H_rad_d_t_i)

    # 1時間当たりの配管iの熱損失
    Q_loss_pp_d_t_i = calc_Q_loss_pp_d_t_i(
        i=i,
        Theta_SW_d_t=Theta_SW_d_t,
        Theta_ex_d_t=Theta_ex,
        r_WS_rad_d_t_i=r_WS_rad_d_t_i,
        A_A=A_A,
        pipe_insulation=pipe_insulation,
        underfloor_pipe_insulation=underfloor_pipe_insulation,
        MR_rad_type=MR_rad_type,
        r_Af_1=r_Af_1
    )

    return Q_dmd_H_rad_d_t_i + Q_loss_pp_d_t_i


# ============================================================================
# 8.2 温水供給運転率
# ============================================================================


def calc_r_WS_ln_d_t_i(A_HCZ, radiator, Q_T_H_rad, Theta_SW, region, mode, R_type):
    """放熱系統iの温水供給運転率 (11)

    Args:
      A_HCZ(float): 暖冷房区画の床面積
      radiator(dict): 放熱器仕様
      Q_T_H_rad(ndarray): 放熱器の処理暖房負荷
      Theta_SW(ndarray): 往き温水温度 (℃)
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      R_type(string): 居室の形式

    Returns:
      tuple: 放熱系統iの温水供給運転率 (11)

    """
    return calc_r_WS_rad_d_t_i(A_HCZ, radiator, Q_T_H_rad, Theta_SW, region, mode, R_type)


# ============================================================================
# 8.3 要求往き温水温度の区分
# ============================================================================


def calc_p_ln_d_t_i(radiator, L_T_H_rad_d_t_i, Theta_SW_hs_op, A_HCZ, region, mode, R_type):
    """放熱系統の要求往き温水温度の区分

    Args:
      radiator(dict): 放熱器仕様
      L_T_H_rad_d_t_i(ndarray): 1時間当たりの暖冷房区画iに設置された放熱器の暖房負荷
      Theta_SW_hs_op(tuple): 温水暖房用熱源機の往き温水温度の候補
      A_HCZ(float): 暖冷房区画の床面積
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      R_type(string): 居室の形式

    Returns:
      float: 放熱系統の要求往き温水温度の区分

    """
    n = len(Theta_SW_hs_op)
    if n == 1:
        # 候補が1つの場合は決定
        return np.ones(24 * 365)
    else:
        # 候補が2つ以上の場合は未処理負荷の発生状況を確認

        # 放熱器がない暖房区画が指定されて場合は便宜上、最低の温水温度の区分を返す
        if radiator is None:
            return n * np.ones(24 * 365)

        # 往き温水温度の候補ごとに未処理負荷の発生状況を確認する
        # このとき、最大の往き温水温度の候補(p=1)は確認をしない
        flag_UT_d_t_p = np.ones((n - 1, 24 * 365))  # 基本はp=1
        for p in range(2, n + 1):
            # 往き温水温度の候補p
            Theta_SW = Theta_SW_hs_op[p - 1]

            # 往き温水温度の候補pにおける放熱器の最大出力
            Q_max_H_rad_d_t_i_p = calc_Q_max_H_rad_d_t_i(radiator, A_HCZ, Theta_SW, region, mode, R_type)

            # 往き温水温度の候補pにおける1時間当たりの暖冷房区画iに設置された放熱器の処理暖房負荷
            Q_T_H_rad_d_t_i_p = calc_Q_T_H_rad_d_t_i(Q_max_H_rad_d_t_i_p, L_T_H_rad_d_t_i)

            # 往き温水温度の候補pにおける1時間当たりの暖冷房区画iに設置された放熱器の未処理暖房負荷
            Q_UT_H_rad_d_t_i_p = L_T_H_rad_d_t_i - Q_T_H_rad_d_t_i_p

            # 未処理負荷が発生しなかった時刻にはpを保存
            flag_UT_d_t_i_p = Q_UT_H_rad_d_t_i_p <= 0.0
            flag_UT_d_t_p[p - 2][flag_UT_d_t_i_p] = p

        # 1時間当たりの往き温水温度の候補p
        p_ln_d_t_i = np.max(flag_UT_d_t_p, axis=0)
        return p_ln_d_t_i


# ===========================================================================
# 9. 配管
# ============================================================================


def calc_Q_loss_pp_d_t_i(i, Theta_SW_d_t, Theta_ex_d_t, r_WS_rad_d_t_i, A_A, pipe_insulation, underfloor_pipe_insulation,
                         MR_rad_type, r_Af_1):
    """1時間当たりの配管iの熱損失 (12)

    Args:
      i(int): 暖冷房区画の番号
      Theta_SW_d_t(ndarray): 往き温水温度 (℃)
      Theta_ex_d_t(ndarray): 外気温度(℃)
      r_WS_rad_d_t_i(ndarray): 1時間当たりの暖冷房区画iに設置された温水床暖房の温水供給運転率
      A_A(float): 床面積の合計 (m2)
      pipe_insulation(bool): 配管断熱の有無
      underfloor_pipe_insulation(bool): 床下配管断熱の有無
      MR_rad_type(str): 主たる居室の放熱器の種類
      r_Af_1(float): 当該住戸における温水床暖房の敷設率 (-)

    Returns:
      ndarray: 1時間当たりの配管iの熱損失 (12)

    """
    # 配管の断熱区画外における長さ
    L_pp_ex_i = pipe.calc_L_pp_ex_i(i, A_A, underfloor_pipe_insulation, MR_rad_type, r_Af_1)

    # 配管の断熱区画内における長さ
    L_pp_in_i = pipe.calc_L_pp_in_i(i, A_A, underfloor_pipe_insulation, MR_rad_type, r_Af_1)

    # 線熱損失係数
    K_loss_pp_i = pipe.get_K_loss_pp(pipe_insulation)

    return ((Theta_SW_d_t - (Theta_ex_d_t * 0.7 + 20 * 0.3)) * L_pp_ex_i + (Theta_SW_d_t - 20) * L_pp_in_i) \
           * K_loss_pp_i * r_WS_rad_d_t_i * 3600 * 10 ** (-6)


# ***************************************************************************
# 10. 放熱器
# ***************************************************************************


# ============================================================================
# 10.1 供給熱量
# ============================================================================


def calc_Q_dmd_H_rad_d_t_i(radiator, Q_max_H_rad_d_t_i, L_T_H_rad_d_t_i):
    """1時間当たりの暖冷房区画iに設置された放熱器の温水熱需要 (13)

    Args:
      radiator(dict): 放熱器仕様
      Q_max_H_rad_d_t_i(ndarray): 1時間当たりの暖冷房区画iに設置された放熱器の最大暖房出力
      L_T_H_rad_d_t_i(ndarray): 1時間当たりの暖冷房区画iに設置された放熱器の暖房負荷

    Returns:
      ndarray: 1時間当たりの暖冷房区画iに設置された放熱器の温水熱需要

    """
    # 1時間当たりの暖冷房区画iに設置された放熱器の処理暖房負荷
    Q_T_H_rad_d_t_i = calc_Q_T_H_rad_d_t_i(Q_max_H_rad_d_t_i, L_T_H_rad_d_t_i)

    # 1時間当たりの暖冷房区画iに設置された放熱器の熱損失
    Q_loss_rad_d_t_i = calc_Q_loss_rad_d_t_i(radiator, Q_T_H_rad_d_t_i)

    return Q_T_H_rad_d_t_i + Q_loss_rad_d_t_i


# ============================================================================
# 10.2 消費電力量
# ============================================================================

def calc_E_E_rad_d_t_i(i, radiator, Q_T_H_rad, Theta_SW, A_A, A_MR, A_OR, region, mode, R_type):
    """1時間当たりの暖冷房区画iに設置された放熱器の消費電力量

    Args:
      i(int): 暖冷房区画の番号
      radiator(dict): 放熱器仕様
      Q_T_H_rad(ndarray): 放熱器の処理暖房負荷
      Theta_SW(ndarray): 往き温水温度 (℃)
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      R_type(string): 居室の形式

    Returns:
      ndarray: 1時間当たりの暖冷房区画iに設置された放熱器の消費電力量

    """
    if radiator['type'] in ['温水暖房用パネルラジエーター', '温水暖房用床暖房', '温水床暖房（併用運転に対応）']:
        return np.zeros(24 * 365)
    elif radiator['type'] == '温水暖房用ファンコンベクター':

        A_HCZ = calc_A_HCZ_i(i, A_A, A_MR, A_OR)

        return rad_fanc.calc_E_E_rad(
            A_HCZ=A_HCZ,
            region=region,
            mode=mode,
            R_type=R_type,
            Theta_SW=Theta_SW,
            Q_T_H_rad=Q_T_H_rad,
        )
    else:
        raise ValueError(radiator['type'])


def calc_A_HCZ_i(i, A_A, A_MR, A_OR):
    """暖冷房区画iの床面積

    Args:
      i(int): 暖冷房区画の番号
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)

    Returns:
      float: 暖冷房区画iの床面積

    """
    return ld.get_A_HCZ_i(i, A_A, A_MR, A_OR)


# ============================================================================
# 10.3 熱損失
# ============================================================================


def calc_Q_loss_rad_d_t_i(radiator, Q_T_H_rad):
    """1時間当たりの暖冷房区画iに設置された放熱器の熱損失

    Args:
      radiator(dict): 放熱器仕様
      Q_T_H_rad(ndarray): 放熱器の処理暖房負荷

    Returns:
      ndarray: 1時間当たりの暖冷房区画iに設置された放熱器の熱損失

    """
    if radiator['type'] in ['温水暖房用パネルラジエーター', '温水暖房用ファンコンベクター']:
        return np.zeros_like(Q_T_H_rad)
    elif radiator['type'] in ['温水暖房用床暖房', '温水床暖房（併用運転に対応）']:
        return rad_floor.get_Q_loss_rad(
            r_up=radiator['r_up'],
            Q_T_H_rad=Q_T_H_rad
        )
    else:
        raise ValueError(radiator['type'])


# ============================================================================
# 10.4 温水供給運転率
# ============================================================================


def calc_r_WS_rad_d_t_i(A_HCZ, radiator, Q_T_H_rad, Theta_SW, region, mode, R_type):
    """放熱器の温水供給運転率

    Args:
      A_HCZ(float): 暖冷房区画の床面積
      radiator(dict): 放熱器仕様
      Q_T_H_rad(ndarray): 放熱器の処理暖房負荷
      Theta_SW(ndarray): 往き温水温度 (℃)
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      R_type(string): 居室の形式

    Returns:
      ndarray: 放熱器の温水供給運転率

    """
    if radiator['type'] == '温水暖房用パネルラジエーター':
        # 温水供給運転率の計算
        r_WS_rad_d_t_i = rad_panel.calc_r_WS_rad(
            region=region,
            mode=mode,
            A_HCZ=A_HCZ,
            R_type=R_type,
            Theta_SW=Theta_SW,
            Q_T_H_rad=Q_T_H_rad
        )
    elif radiator['type'] == '温水暖房用ファンコンベクター':
        # 仕様の取得
        q_max_FC = rad_fanc.calc_q_max_FC(region, mode, A_HCZ, R_type)
        q_min_FC = rad_fanc.get_q_min_FC(q_max_FC)
        Q_min_H_FC = rad_fanc.get_Q_min_H_FC(Theta_SW, q_min_FC)

        # 温水供給運転率の計算
        r_WS_rad_d_t_i = rad_fanc.get_r_WS_rad(
            Q_min_H_FC=Q_min_H_FC,
            Q_T_H_rad=Q_T_H_rad
        )
    elif radiator['type'] in ['温水暖房用床暖房', '温水床暖房（併用運転に対応）']:
        # 仕様の取得
        A_f = rad_floor.get_A_f(A_HCZ, radiator.get('r_Af'))

        # 主たる居室で温水床暖房とエアコンを併用する場合か否か
        racfh_combed = (R_type == '主たる居室') and (radiator['type'] == '温水床暖房（併用運転に対応）')

        Q_max_H_rad = rad_floor.get_Q_max_H_rad(Theta_SW, A_f, racfh_combed)

        # 温水供給運転率の計算
        r_WS_rad_d_t_i = rad_floor.get_r_WS_rad(
            Q_T_H_rad=Q_T_H_rad,
            Q_max_H_rad=Q_max_H_rad,
            racfh_combed=racfh_combed,
        )
    else:
        raise ValueError(radiator['type'])

    # 温水供給運転率が1を超える場合は1、0を下回る場合は0
    r_WS_rad_d_t_i = np.clip(r_WS_rad_d_t_i, 0, 1)

    return r_WS_rad_d_t_i


# ============================================================================
# 10.5 処理暖房負荷
# ============================================================================

def calc_Q_T_H_rad_d_t_i(Q_max_H_d_t_i, L_H_d_t_i):
    """1時間当たりの暖冷房区画iに設置された放熱器の処理暖房負荷

    Args:
      Q_max_H_d_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの1時間当たりの暖冷房区画𝑖に設置された放熱器の最大暖房出力
      L_H_d_t_i(ndarray): 日付dの時刻tにおける暖冷房区画iの1時間当たりの暖房負荷（MJ/h）

    Returns:
      ndarray: 1時間当たりの暖冷房区画iに設置された放熱器の処理暖房負荷

    """
    import pyhees.section4_1_Q
    return pyhees.section4_1_Q.get_Q_T_H_d_t_i(Q_max_H_d_t_i, L_H_d_t_i)


# ============================================================================
# 10.6 最大暖房出力
# ============================================================================


def calc_Q_max_H_rad_d_t_i(radiator, A_HCZ, Theta_SW, region, mode, R_type):
    """放熱器の最大暖房出力

    Args:
      radiator(dict): 放熱器仕様
      A_HCZ(float): 暖冷房区画の床面積
      Theta_SW(ndarray): 往き温水温度 (℃)
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      R_type(string): 居室の形式

    Returns:
      ndarray: 放熱器の最大暖房出力

    """
    if radiator['type'] == '温水暖房用パネルラジエーター':
        # 仕様の取得
        q_max_rad = rad_panel.calc_q_max_rad(region, mode, A_HCZ, R_type)

        # 最大暖房出力の計算
        return rad_panel.get_Q_max_H_rad(
            q_max_rad=q_max_rad,
            Theta_SW=Theta_SW
        )
    elif radiator['type'] == '温水暖房用ファンコンベクター':
        # 仕様の取得
        q_max_FC = rad_fanc.calc_q_max_FC(region, mode, A_HCZ, R_type)

        # 最大暖房出力の計算
        return rad_fanc.calc_Q_max_H_rad(
            q_max_FC=q_max_FC,
            Theta_SW=Theta_SW
        )
    elif radiator['type'] in ['温水暖房用床暖房', '温水床暖房（併用運転に対応）']:
        # 仕様の取得
        A_f = rad_floor.get_A_f(A_HCZ, radiator.get('r_Af'))

        # 主たる居室で温水床暖房とエアコンを併用する場合か否か
        racfh_combed = (R_type == '主たる居室') and (radiator['type'] == '温水床暖房（併用運転に対応）')

        # 最大暖房出力の計算
        return rad_floor.get_Q_max_H_rad(
            A_f=A_f,
            Theta_SW=Theta_SW,
            racfh_combed=racfh_combed,
        )
    else:
        raise ValueError(radiator['type'])


if __name__ == '__main__':
    # 温水暖房用熱源機の往き温水温度の候補
    Theta_SW_hs_op = get_Theta_SW_hs_op('石油温水暖房機潜熱回収型')
    print('Theta_SW_hs_op = {}'.format(Theta_SW_hs_op))

    # 仮に最低温度を選択しておく
    Theta_SW = Theta_SW_hs_op[len(Theta_SW_hs_op) - 1] * np.ones(24 * 365)
    print('Theta_SW = {}'.format(Theta_SW))

    # 放熱系の暖房負荷
    Q_T_H_rad = np.ones(24 * 365)

    # 仕様
    spec = {'region': 1, 'mode': '間歇運転', 'R_type': '主たる居室', 'A_A': 120.8, 'A_MR': 29.81, 'A_OR': 50}
    region = spec['region']
    mode = spec['mode']
    R_type = spec['R_type']

    # 仮の放熱器
    pnl = {'type': 'パネルラジエーター'}
    fhw = {'type': '温水床暖房', 'r_Af': 0.5, 'r_up': 0.7}
    fc = {'type': 'ファンコンベクター'}

    # 放熱系の消費電力
    print('*放熱系の消費電力')
    print(np.sum(calc_E_E_rad_d_t_i(1, pnl, Q_T_H_rad, Theta_SW, **spec)))
    print(np.sum(calc_E_E_rad_d_t_i(1, fhw, Q_T_H_rad, Theta_SW, **spec)))
    print(np.sum(calc_E_E_rad_d_t_i(1, fc, Q_T_H_rad, Theta_SW, **spec)))

    # 放熱系の熱損失
    print('*放熱系の熱損失')
    print(np.sum(calc_Q_loss_rad_d_t_i(pnl, Q_T_H_rad)))
    print(np.sum(calc_Q_loss_rad_d_t_i(fhw, Q_T_H_rad)))
    print(np.sum(calc_Q_loss_rad_d_t_i(fc, Q_T_H_rad)))

    # 放熱器の温水供給運転率
    A_HCZ = 15.2
    Q_max_H_rad_d_t_pnl = calc_Q_max_H_rad_d_t_i(pnl, A_HCZ, Theta_SW, region, mode, R_type)
    Q_max_H_rad_d_t_fhw = calc_Q_max_H_rad_d_t_i(fhw, A_HCZ, Theta_SW, region, mode, R_type)
    Q_max_H_rad_d_t_fc = calc_Q_max_H_rad_d_t_i(fc, A_HCZ, Theta_SW, region, mode, R_type)
    print('*放熱器の温水供給運転率')
    print(np.sum(Q_max_H_rad_d_t_pnl))
    print(np.sum(Q_max_H_rad_d_t_fhw))
    print(np.sum(Q_max_H_rad_d_t_fc))

    # 放熱器の温水熱需要
    print('*放熱器の温水熱需要')
    print(np.sum(calc_Q_dmd_H_rad_d_t_i(pnl, Q_max_H_rad_d_t_pnl, Q_T_H_rad)))
    print(np.sum(calc_Q_dmd_H_rad_d_t_i(fhw, Q_max_H_rad_d_t_fhw, Q_T_H_rad)))
    print(np.sum(calc_Q_dmd_H_rad_d_t_i(fc, Q_max_H_rad_d_t_fc, Q_T_H_rad)))
