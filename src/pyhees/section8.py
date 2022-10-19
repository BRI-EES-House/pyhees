# ============================================================================
# 第八章 コージェネレーション設備
# Ver.12（エネルギー消費性能計算プログラム（住宅版）Ver.02.04～）
# ============================================================================

import numpy as np

import pyhees.section4_7 as hwh
import pyhees.section7_1 as dhw
import pyhees.section8_a as spec
import pyhees.section8_d as bb_dhw
import pyhees.section8_e as bb_hwh

from pyhees.section11_1 import load_outdoor, get_Theta_ex


# ============================================================================
# 5. ガス消費量
# ============================================================================

def calc_E_G_CG_d_t(bath_function, CG, E_E_dmd_d_t,
                    L_dashdash_k_d_t, L_dashdash_w_d_t, L_dashdash_s_d_t, L_dashdash_b1_d_t, L_dashdash_b2_d_t,
                    L_dashdash_ba1_d_t,
                    L_dashdash_ba2_d_t,
                    H_HS, H_MR, H_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_rad):
    """1時間当たりのコージェネレーション設備のガス消費量 (1)

    Args:
      bath_function(str): ふろ機能の種類
      CG(dict): コージェネレーション設備の仕様
      E_E_dmd_d_t(ndarray): 1時間当たりの電力需要 (kWh/h)
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽自動追焚時における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚の太陽熱補正給湯熱負荷 (MJ/h)
      H_HS: param H_MR:
      H_OR: param A_A:
      A_MR: param A_OR:
      region: param mode_MR:
      mode_OR: param L_T_H_rad:
      H_MR: 
      A_A: 
      A_OR: 
      mode_MR: 
      L_T_H_rad: 

    Returns:
      tuple: 1時間当たりのコージェネレーション設備の一次エネルギー消費量及び1時間当たりのコージェネレーション設備による発電量

    """
    # ----- パラメータの取得 -----

    if 'CG_category' in CG:
        # 温水暖房への排熱利用
        exhaust = spec.get_exhaust(CG['CG_category'])

        # 排熱利用方式
        exhaust_priority = spec.get_exhaust_priority(CG['CG_category'])

        # バックアップボイラー(給湯)の給湯機の効率
        e_rtd_DHW_BB = spec.get_e_rtd_BB_DHW(CG['CG_category'])

        # バックアップボイラー(給湯、温水暖房)の種類
        type_BB_HWH = spec.get_type_BB_HWH(CG['CG_category'])

        # バックアップボイラー(温水暖房)の定格効率
        e_rtd_BB_HWH = spec.get_e_rtd_BB_HWH(CG['CG_category'])

        # バックアップボイラー(温水暖房)の定格能力 (W)
        q_rtd_BB_HWH = spec.get_q_rtd_BB_HWH(CG['CG_category'])

        # 発電ユニットの給湯排熱利用率
        r_DHW_gen_PU_d = spec.get_r_DHW_gen_PU_d(CG['CG_category'])

        # 発電ユニットの温水暖房排熱利用率
        r_HWH_gen_PU_d = spec.get_r_HWH_gen_PU_d(CG['CG_category'])

        # 発電ユニットの発電方式
        PU_type = spec.get_PU_type(CG['CG_category'])

        # 発電ユニットの発電量推定時の仮想発電量のパラメータ a_PU, a_DHW, a_HWH, b, c
        param_E_E_gen_PU_Evt_d = spec.get_param_E_E_gen_PU_EVt_d(CG['CG_category'])

        # 発電ユニットの排熱量推定時の仮想燃料消費量を求める係数
        param_E_F_PU_HVt_d = spec.get_param_E_F_PU_HVt_d(CG['CG_category'])

        # 発電ユニットの排熱量推定時の仮想排熱量の上限比を求める係数 a_DHW, a_HWH, b
        param_r_H_gen_PU_HVt_d = spec.get_param_r_H_gen_PU_HVt_d(CG['CG_category'])

        # 発電ユニットの日平均発電効率を求める係数 a_PU, a_DHW, a_HWH, b, 上限値, 下限値
        param_e_E_PU_d = spec.get_param_e_E_PU_d(CG['CG_category'])

        # 発電ユニットの日平均排熱効率を求める係数 a_PU, a_DHW, a_HWH, b, 上限値, 下限値
        param_e_H_PU_d = spec.get_param_e_H_PU_d(CG['CG_category'])

        # 定格発電出力 (W)
        P_rtd_PU = spec.get_P_rtd_PU(CG['CG_category'])

        # タンクユニットの補機消費電力 (給湯)
        P_TU_aux_DHW = spec.get_P_TU_aux_DHW(CG['CG_category'])

        # タンクユニットの補機消費電力 (温水暖房)
        P_TU_aux_HWH = spec.get_P_TU_aux_HWH(CG['CG_category'])

        # 逆潮流の評価
        has_CG_reverse = CG['reverse'] if 'reverse' in CG else False

    else:
        # 温水暖房への排熱利用
        exhaust = CG['exhaust']

        # 排熱利用方式
        exhaust_priority = CG['exhaust_priority']

        # バックアップボイラー(給湯、温水暖房)の種類
        type_BB_HWH = CG['type_BB_HWH']

        # 付録D,Eより
        if type_BB_HWH == 'ガス従来型' or type_BB_HWH == 'G_NEJ':
            # バックアップボイラー(給湯)の給湯機の効率
            e_rtd_DHW_BB = 0.782
            # バックアップボイラー(温水暖房)の定格効率
            e_rtd_BB_HWH = 0.82
            # バックアップボイラー(温水暖房)の定格能力 (W)
            q_rtd_BB_HWH = 17400
        elif type_BB_HWH == 'ガス潜熱回収型' or type_BB_HWH == 'G_EJ':
            # バックアップボイラー(給湯)の給湯機の効率
            e_rtd_DHW_BB = 0.905
            # バックアップボイラー(温水暖房)の定格効率
            e_rtd_BB_HWH = 0.87
            # バックアップボイラー(温水暖房)の定格能力 (W)
            q_rtd_BB_HWH = 17400
        else:
            raise ValueError(type_BB_HWH)

        # 発電ユニットの給湯排熱利用率
        r_DHW_gen_PU_d = CG['r_DHW_gen_PU_d']

        # 発電ユニットの温水暖房排熱利用率
        r_HWH_gen_PU_d = CG['r_HWH_gen_PU_d']

        # 発電ユニットの発電方式
        if 'PU_type' in CG:
            # 発電ユニットの発電方式
            PU_type = CG['PU_type']
        else:
            # 付録A コージェネレーション設備の仕様
            if CG['CG_category_param'] == 'PEFC':
                CG_category = 'PEFC2'
            elif CG['CG_category_param'] == 'SOFC':
                CG_category = 'SOFC1'
            elif CG['CG_category_param'] == 'GEC':
                CG_category = 'GEC1'
            else:
                raise ValueError(CG['CG_category_param'])
            PU_type = spec.get_PU_type(CG_category)

        # 発電ユニットの発電量推定時の仮想発電量のパラメータ a_PU, a_DHW, a_HWH, b, c
        param_E_E_gen_PU_Evt_d = CG['param_E_E_gen_PU_Evt_d']

        # 発電ユニットの排熱量推定時の仮想燃料消費量を求める係数
        if 'param_E_F_PU_HVt_d' in CG:
            param_E_F_PU_HVt_d = CG['param_E_F_PU_HVt_d']

        # 発電ユニットの排熱量推定時の仮想排熱量の上限比を求める係数 a_DHW, a_HWH, b
        if 'param_r_H_gen_PU_HVt_d' in CG:
            param_r_H_gen_PU_HVt_d = CG['param_r_H_gen_PU_HVt_d']

        # 発電ユニットの日平均発電効率を求める係数 a_PU, a_DHW, a_HWH, b, 上限値, 下限値
        param_e_E_PU_d = CG['param_e_E_PU_d']

        # 発電ユニットの日平均排熱効率を求める係数 a_PU, a_DHW, a_HWH, b, 上限値, 下限値
        param_e_H_PU_d = CG['param_e_H_PU_d']

        # 定格発電出力 (W)
        P_rtd_PU = CG['P_rtd_PU']

        # タンクユニットの補機消費電力 (給湯)
        P_TU_aux_DHW = CG['P_TU_aux_DHW']

        # タンクユニットの補機消費電力 (温水暖房)
        P_TU_aux_HWH = CG['P_TU_aux_HWH']

        # 逆潮流の評価
        has_CG_reverse = CG['reverse'] if 'reverse' in CG else False

    # ----- 温水暖房用熱源機の負荷および温水供給運転率の計算 -----

    if H_HS is not None and H_HS['type'] == 'コージェネレーションを使用する':
        # 主たる居室、その他の居室という単位で設定された放熱機器を暖房区画ごとの配列に変換
        rad_list = hwh.get_rad_list(H_MR, H_OR)

        # 主たる居室で温水床暖房とエアコンを併用する場合か否か
        racfh_combed = H_MR['type'] == '温水床暖房（併用運転に対応）'

        # 温水暖房用熱源機の往き温水温度
        Theta_SW_hs_op = hwh.get_Theta_SW_hs_op(type_BB_HWH, racfh_combed=racfh_combed)
        p_hs = hwh.calc_p_hs_d_t(Theta_SW_hs_op, rad_list, L_T_H_rad, A_A, A_MR, A_OR, region, mode_MR, mode_OR)
        Theta_SW_d_t = hwh.get_Theta_SW_d_t(Theta_SW_hs_op, p_hs)

        # 1時間当たりの温水暖房の熱負荷 (MJ/h)
        L_HWH_d_t = hwh.calc_Q_dmd_H_hs_d_t(rad_list, H_HS['pipe_insulation'], H_HS['underfloor_pipe_insulation'],
                                            Theta_SW_d_t, A_A, A_MR, A_OR, region,
                                            mode_MR, mode_OR, L_T_H_rad)

        # 処理暖房負荷
        Q_T_H_rad = np.zeros((5, 24 * 365))
        for i in [1, 3, 4, 5]:

            if rad_list[i - 1] is None:
                continue

            # 1時間当たりの暖冷房区画iに設置された放熱器の最大暖房出力
            A_HCZ = hwh.calc_A_HCZ_i(i, A_A, A_MR, A_OR)
            R_type = '主たる居室' if i == 1 else 'その他の居室'
            mode = mode_MR if i == 1 else mode_OR
            Q_max_H_rad_d_t_i = hwh.calc_Q_max_H_rad_d_t_i(rad_list[i - 1], A_HCZ, Theta_SW_d_t, region, mode, R_type)

            # 1時間当たりの暖冷房区画iに設置された放熱器の処理暖房負荷
            Q_T_H_rad[i - 1, :] = hwh.calc_Q_T_H_rad_d_t_i(Q_max_H_rad_d_t_i, L_T_H_rad[i - 1])

        # 温水暖房用熱源機の温水供給運転率
        r_WS_HWH_d_t = hwh.calc_r_WS_hs_d_t(rad_list, L_HWH_d_t, Q_T_H_rad, Theta_SW_d_t, region, A_A, A_MR, A_OR,
                                            mode_MR)
        # 戻り温水温度 (9)
        Theta_RW_hs = hwh.calc_Theta_RW_hs_d_t(Theta_SW_d_t, rad_list, H_HS['pipe_insulation'],
                                               H_HS['underfloor_pipe_insulation'], A_A, A_MR, A_OR, region,
                                               mode_MR, mode_OR,
                                               L_T_H_rad)

        # 定格能力の計算のためのパラメータの取得
        rad_types = hwh.get_rad_type_list()
        has_MR_hwh = H_MR['type'] in rad_types
        if H_OR is not None:
            has_OR_hwh = H_OR['type'] in rad_types
        else:
            has_OR_hwh = False
    else:
        L_HWH_d_t = np.zeros(24 * 365)
        P_TU_aux_HWH = np.zeros(24 * 365)
        r_WS_HWH_d_t = np.zeros(24 * 365)

    # 外気温度の取得
    outdoor = load_outdoor()
    Theta_ex_d_t = get_Theta_ex(region, outdoor)
    Theta_ex_Ave = dhw.get_theta_ex_d_Ave_d(Theta_ex_d_t)

    # ----- 16. その他 -----

    # 1日当たりの温水暖房の熱負荷 (31)
    L_HWH_d = get_L_HWH_d(L_HWH_d_t)

    # 1時間当たりの発電ユニットによる浴槽追焚を除く給湯熱負荷 (30)
    L_DHW_d_t = get_L_DHW_d_t(L_dashdash_k_d_t, L_dashdash_w_d_t, L_dashdash_s_d_t, L_dashdash_b1_d_t,
                              L_dashdash_b2_d_t, L_dashdash_ba1_d_t)

    # 1日当たりの発電ユニットによる浴槽追焚を除く給湯熱負荷 (MJ/d) (29)
    L_DHW_d = get_L_DHW_d(L_DHW_d_t)

    # ----- 15. タンクユニットの補機消費電力 -----

    # 1時間当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h) (28)
    L_BB_DHW_ba2_d_t = get_L_BB_DHW_ba2_d_t(L_dashdash_ba2_d_t)

    # 1時間当たりの浴槽追焚のタンクユニットの補機消費電力量 (kWh/h)
    E_E_TU_aux_ba2_d_t = calc_E_E_TU_aux_ba2_d_t(L_BB_DHW_ba2_d_t)

    # 1時間当たりの温水暖房時のタンクユニットの補機消費電力量 (kWh/h) (27)
    E_E_TU_aux_HWH_d_t = get_E_E_TU_aux_HWH_d_t(exhaust, P_TU_aux_HWH, r_WS_HWH_d_t)

    # 1時間当たりの給湯時のタンクユニットの補機消費電力量 (kWh/h) (26)
    E_E_TU_aux_DHW_d_t = get_E_E_TU_aux_DHW_d_t(P_TU_aux_DHW)

    # 1時間当たりのタンクユニットの補機消費電力量 (25)
    E_E_TU_aux_d_t = get_E_E_TU_aux_d_t(E_E_TU_aux_DHW_d_t, E_E_TU_aux_HWH_d_t, E_E_TU_aux_ba2_d_t)

    print('E_E_TU_aux_ba2_d_t = {} [kWh/yr] (min={}, max={})'.format(np.sum(E_E_TU_aux_ba2_d_t), min(E_E_TU_aux_ba2_d_t), max(E_E_TU_aux_ba2_d_t)))
    print('E_E_TU_aux_HWH_d_t = {} [kWh/yr] (min={}, max={})'.format(np.sum(E_E_TU_aux_HWH_d_t), min(E_E_TU_aux_HWH_d_t), max(E_E_TU_aux_HWH_d_t)))
    print('E_E_TU_aux_DHW_d_t = {} [kWh]'.format(E_E_TU_aux_DHW_d_t))
    print('E_E_TU_aux_d_t = {} [kWh/yr] (min={}, max={})'.format(np.sum(E_E_TU_aux_d_t), min(E_E_TU_aux_d_t), max(E_E_TU_aux_d_t)))

    # ----- 14. 発電ユニット -----

    # 発電ユニットの電力需要 (kWh/h) (24)
    E_E_dmd_PU_d_t = get_E_E_dmd_PU_d_t(E_E_dmd_d_t, E_E_TU_aux_d_t)

    # 1時間当たりの発電ユニットの分担可能電力負荷 (kWh/h) (23)
    E_E_PU_d_t = get_E_E_PU_d_t(E_E_dmd_PU_d_t, P_rtd_PU, has_CG_reverse)

    # 1日当たりの発電ユニットの分担可能電力負荷 (kWh/d) (22)
    E_E_PU_d = get_E_E_PU_d(E_E_PU_d_t)

    # 発電ユニットの日平均排熱効率 (-) (21)
    e_H_PU_d = get_e_H_PU_d(E_E_PU_d, L_DHW_d, L_HWH_d, **param_e_H_PU_d)

    # 発電ユニットの日平均発電効率 (-) (20)
    e_E_PU_d = get_e_E_PU_d(E_E_PU_d, L_DHW_d, L_HWH_d, **param_e_E_PU_d)

    if PU_type == '熱主':
        # 発電ユニットの排熱量推定時の仮想排熱量上限比 (-) (19)
        r_H_gen_PU_HVt_d = get_r_H_gen_PU_HVt_d(L_DHW_d, L_HWH_d, **param_r_H_gen_PU_HVt_d)

        # 1日当たりの発電ユニットの排熱量推定時の仮想燃料消費 (MJ/d) (18)
        E_F_PU_HVt_d = get_E_G_PU_HVt_d(e_H_PU_d, L_DHW_d, L_HWH_d, r_H_gen_PU_HVt_d, **param_E_F_PU_HVt_d)
    else:
        E_F_PU_HVt_d = np.zeros(365)

    # 1日当たりの発電ユニットの発電量推定時の仮想発電量 (kWh/d) (17)
    E_E_gen_PU_EVt_d = get_E_E_gen_PU_EVt_d(E_E_PU_d, L_DHW_d, L_HWH_d, **param_E_E_gen_PU_Evt_d)

    # 1日当たりの発電ユニットの発電量推定時の仮想ガス消費量 (MJ/d) (16)
    E_F_PU_EVt_d = get_E_G_PU_EVt_d(E_E_gen_PU_EVt_d, e_E_PU_d)

    # 1日当たりの発電ユニットのガス消費量 (MJ/d) (15)
    E_G_PU_d = get_E_G_PU_d(PU_type, E_F_PU_EVt_d, E_F_PU_HVt_d)

    # 1時間当たりの発電ユニットのガス消費量 (MJ/h) (14a)
    E_G_PU_d_t = calc_E_G_PU_d_t(E_G_PU_d, E_E_PU_d, E_E_PU_d_t, e_E_PU_d)

    # 発電ユニットの発電量 (kWh/h) (10)
    E_E_gen_PU_d_t = get_E_E_gen_PU_d_t(E_G_PU_d_t, e_E_PU_d)

    # 1日当たりの発電ユニット排熱量 (MJ/d) (9)
    Q_PU_gen_d = get_Q_PU_gen_d(E_G_PU_d, e_H_PU_d)

    # 1日当たりの給湯・温水暖房の排熱利用量 (MJ/d) (6)(7)(8)
    Q_gen_DHW_d, Q_gen_HWH_d = get_Q_gen_x_d(exhaust, exhaust_priority, Q_PU_gen_d, r_DHW_gen_PU_d, r_HWH_gen_PU_d,
                                             L_DHW_d, L_HWH_d)

    print('E_E_dmd_PU_d_t = {} [MJ/yr] (min={}, max={} [MJ/h])'.format(np.sum(E_E_dmd_PU_d_t), min(E_E_dmd_PU_d_t), max(E_E_dmd_PU_d_t)))
    print('P_rtd_PU = {}'.format(P_rtd_PU))
    print('E_E_PU_d = {} [MJ/yr] (min={}, max={} [MJ/d])'.format(np.sum(E_E_PU_d), min(E_E_PU_d), max(E_E_PU_d)))
    print('E_E_gen_PU_EVt_d = {} [MJ/yr] (min={}, max={} [MJ/d])'.format(np.sum(E_E_gen_PU_EVt_d), min(E_E_gen_PU_EVt_d), max(E_E_gen_PU_EVt_d)))
    print('e_E_PU_d = {} [MJ/yr] (min={}, max={} [MJ/d])'.format(np.sum(e_E_PU_d), min(e_E_PU_d), max(e_E_PU_d)))
    print('E_F_PU_EVt_d = {} [MJ/yr] (min={}, max={} [MJ/d])'.format(np.sum(E_F_PU_EVt_d), min(E_F_PU_EVt_d), max(E_F_PU_EVt_d)))
    print('E_F_PU_HVt_d = {} [MJ/yr] (min={}, max={} [MJ/d])'.format(np.sum(E_F_PU_HVt_d), min(E_F_PU_HVt_d), max(E_F_PU_HVt_d)))
    print('E_G_PU_d = {} [MJ/yr] (min={}, max={} [MJ/d])'.format(np.sum(E_G_PU_d), min(E_G_PU_d), max(E_G_PU_d)))
    print('E_G_PU_d_t = {} [MJ/yr] (min={}, max={} [MJ/d])'.format(np.sum(E_G_PU_d_t), min(E_G_PU_d_t), max(E_G_PU_d_t)))
    print('E_E_gen_PU = {} [MJ/yr] (min={}, max={} [MJ/h])'.format(np.sum(E_E_gen_PU_d_t), min(E_E_gen_PU_d_t), max(E_E_gen_PU_d_t)))
    print('Q_PU_gen = {} [MJ/yr] (min={}, max={} [MJ/d])'.format(np.sum(Q_PU_gen_d), min(Q_PU_gen_d), max(Q_PU_gen_d)))
    print('Q_gen_DHW = {} [MJ/yr] (min={}, max={} [MJ/d])'.format(np.sum(Q_gen_DHW_d), min(Q_gen_DHW_d), max(Q_gen_DHW_d)))
    print('Q_gen_HWH = {} [MJ/yr] (min={}, max={} [MJ/d])'.format(np.sum(Q_gen_HWH_d), min(Q_gen_HWH_d), max(Q_gen_HWH_d)))

    # ----- 13. 温水暖房時のバックアップボイラーのガス消費量(温水暖房への排熱利用がある場合)

    if H_HS is not None and H_HS['type'] == 'コージェネレーションを使用する':
        # 1日当たりの給湯のバックアップボイラーが分担する給湯熱負荷 (MJ/d) (5)
        L_BB_HWH_d_t = get_L_BB_HWH_d_t(L_HWH_d_t, L_HWH_d, Q_gen_HWH_d)

        # 1時間当たりの温水暖房時のバックアップボイラーのガス消費量 (MJ/h)
        E_G_BB_HWH_d_t = bb_hwh.calc_E_G_BB_HWH_d_t(type_BB_HWH, e_rtd_BB_HWH, q_rtd_BB_HWH, L_BB_HWH_d_t, Theta_SW_d_t)
    else:
        L_BB_HWH_d_t = np.zeros(24 * 365)
        E_G_BB_HWH_d_t = np.zeros(24 * 365)

    # ----- 12. 給湯時のバックアップボイラーのガス消費量 ----

    # 1時間あたりのバックアップボイラーが分担する給湯熱負荷 (4)
    L_BB_DHW_d_t, L_BB_DHW_k_d_t, L_BB_DHW_s_d_t, L_BB_DHW_w_d_t, \
    L_BB_DHW_b1_d_t, L_BB_DHW_b2_d_t, L_BB_DHW_ba1_d_t, L_BB_DHW_ba2_d_t = \
        get_L_BB_x_d_t(L_dashdash_k_d_t, L_dashdash_w_d_t, L_dashdash_s_d_t,
                       L_dashdash_b1_d_t, L_dashdash_b2_d_t, L_dashdash_ba1_d_t, L_dashdash_ba2_d_t,
                       Q_gen_DHW_d, L_DHW_d)

    # 1日当たりの給湯時のバックアップボイラーの燃料消費量 (MJ/d) (3)
    E_G_BB_DHW_d_t, E_G_BB_DHW_ba2_d_t = bb_dhw.calc_E_G_BB_DHW_d_t(bath_function,
                                                L_BB_DHW_k_d_t, L_BB_DHW_s_d_t, L_BB_DHW_w_d_t,
                                                L_BB_DHW_b1_d_t, L_BB_DHW_b2_d_t, L_BB_DHW_ba1_d_t, L_BB_DHW_ba2_d_t,
                                                e_rtd_DHW_BB, Theta_ex_Ave)

    # ----- 11. 給湯時のバックアップボイラーの年間平均効率 -----

    # 給湯時のバックアップボイラーの年間平均効率 (-) (6)
    e_BB_ave = get_e_BB_ave(L_BB_DHW_d_t, L_BB_DHW_ba2_d_t, E_G_BB_DHW_d_t, E_G_BB_DHW_ba2_d_t)

    # ----- 10. 製造熱量のうちの自家消費算入分 -----

    # 1年あたりのコージェネレーション設備による製造熱量のうちの自家消費算入分 (MJ/yr) (5)
    Q_CG_h = get_Q_CG_h(L_DHW_d_t)

    # ----- 9. 発電量のうちの自己消費分

    # 1年当たりのコージェネレーション設備による発電量のうちの自己消費分 (kWH/yr) (4)
    E_E_CG_self = get_E_E_CG_self(E_E_TU_aux_d_t)

    # ----- 8. 給湯時のバックアップボイラーの年間平均効率 -----

    # 1年あたりのコージェネレーション設備のガス消費量のうちの売電に係る控除対象分 (MJ/yr) (3)
    E_G_CG_ded = get_E_G_CG_ded(E_G_PU_d_t, E_G_BB_DHW_d_t, E_G_BB_DHW_ba2_d_t)

    # ----- 7. 発電量 -----

    # 1時間当たりのコージェネレーション設備による発電量 (kWh/h) (2)
    E_E_CG_gen_d_t = get_E_E_CG_gen_d_t(E_E_gen_PU_d_t, E_E_TU_aux_d_t)

    # ----- 5. ガス消費量 -----

    # 1時間当たりのコージェネレーション設備のガス消費量 (MJ/h) (1)
    E_G_CG_d_t = E_G_PU_d_t + E_G_BB_DHW_d_t + E_G_BB_HWH_d_t

    print('E_G_PU = {} [MJ/yr]'.format(np.sum(E_G_PU_d_t)))
    print('E_G_BB_DHW = {} [MJ/yr]'.format(np.sum(E_G_BB_DHW_d_t)))
    print('E_G_BB_HWH = {} [MJ/yr]'.format(np.sum(E_G_BB_HWH_d_t)))
    print('E_E_CG_gen = {} [kWh/yr]'.format(np.sum(E_E_CG_gen_d_t)))
    print('E_G_CG = {} [MJ/yr]'.format(np.sum(E_G_CG_d_t)))

    return E_G_CG_d_t, E_E_CG_gen_d_t, E_G_CG_ded, E_E_CG_self, Q_CG_h, E_E_TU_aux_d_t, e_BB_ave


# ============================================================================
# 6. 灯油消費量
# ============================================================================

#
def get_E_K_CG_d_t():
    """1時間当たりのコージェネレーション設備の灯油消費量 (MJ/h)

    Args:

    Returns:
      ndarray: E_K_CG_d_t 1時間当たりのコージェネレーション設備の灯油消費量 (MJ/h)

    """
    return np.zeros(24 * 365)


# ============================================================================
# 7. 発電量
# ============================================================================

def get_E_E_CG_gen_d_t(E_E_gen_PU_d_t, E_E_TU_aux_d_t):
    """1時間当たりのコージェネレーション設備による発電量 (kWh/h) (2)

    Args:
      E_E_gen_PU_d_t(ndarray): 1時間当たりの発電ユニットの発電量 (kWh/h)
      E_E_TU_aux_d_t(ndarray): 1時間当たりのタンクユニットの補機消費電力量 (kWh/h)

    Returns:
      ndarray: 1時間当たりのコージェネレーション設備による発電量 (kWh/h)

    """
    return E_E_gen_PU_d_t - E_E_TU_aux_d_t


# ============================================================================
# 8. 給湯時のバックアップボイラーの年間平均効率
# ============================================================================

def get_E_G_CG_ded(E_G_PU_d_t, E_G_BB_DHW_d_t, E_G_BB_DHW_ba2_d_t):
    """1年あたりのコージェネレーション設備のガス消費量のうちの売電に係る控除対象分 (MJ/yr) (3)

    Args:
      E_G_PU_d_t(ndarray): 日付dの時刻tにおける1時間当たりの発電ユニットのガス消費量 (MJ/h)
      E_G_BB_DHW_d_t(ndarray): 日付dの時刻tにおける1時間当たりの給湯時のバックアップボイラーのガス消費量 (MJ/h)
      E_G_BB_DHW_ba2_d_t(ndarray): 日付dの時刻tにおける1時間当たりの浴槽追焚時におけるバックアップボイラーのガス消費量 (MJ/d)

    Returns:
      float64: 1年あたりのコージェネレーション設備のガス消費量のうちの売電に係る控除対象分 (MJ/yr)

    """
    return np.sum(E_G_PU_d_t + E_G_BB_DHW_d_t - E_G_BB_DHW_ba2_d_t)

# ============================================================================
# 9. 発電量のうちの自己消費分
# ============================================================================

def get_E_E_CG_self(E_E_TU_aux_d_t):
    """1年当たりのコージェネレーション設備による発電量のうちの自己消費分 (kWH/yr) (4)

    Args:
      E_E_TU_aux_d_t(ndarray): 日付dの時刻tにおける1時間当たりのタンクユニットの補機消費電力量 (kWh/yr)

    Returns:
      float64: 1年当たりのコージェネレーション設備による発電量のうちの自己消費分 (kWH/yr)

    """
    return np.sum(E_E_TU_aux_d_t)


# ============================================================================
# 10. 製造熱量のうちの自家消費算入分
# ============================================================================

def get_Q_CG_h(L_DHW_d_t):
    """1年あたりのコージェネレーション設備による製造熱量のうちの自家消費算入分 (MJ/yr) (5)

    Args:
      L_DHW_d_t(ndarray): 日付dの時刻tにおける1時間当たりの浴槽追焚を除く太陽熱補正給湯熱負荷 (MJ/d)

    Returns:
      float64: 1年あたりのコージェネレーション設備による製造熱量のうちの自家消費算入分 (MJ/yr)

    """
    return np.sum(L_DHW_d_t)


# ============================================================================
# 11. 給湯時のバックアップボイラーの年間平均効率
# ============================================================================

def get_e_BB_ave(L_BB_DHW_d_t, L_BB_DHW_ba2_d_t, E_G_BB_DHW_d_t, E_G_BB_DHW_ba2_d_t):
    """給湯時のバックアップボイラーの年間平均効率 (-) (6)

    Args:
      L_BB_DHW_d_t(ndarray): 1時間当たりのバックアップボイラーが分担する給湯熱負荷 (MJ/h)
      L_BB_DHW_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)
      E_G_BB_DHW_d_t(ndarray): 1時間当たりの給湯時のバックアップボイラーのガス消費量 (MJ/h)
      E_G_BB_DHW_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時におけるバックアップボイラーのガス消費量 (MJ/d)

    Returns:
      float64: 給湯時のバックアップボイラーの年間平均効率 (-)

    """
    e_BB_ave = np.sum(L_BB_DHW_d_t - L_BB_DHW_ba2_d_t) / np.sum(E_G_BB_DHW_d_t - E_G_BB_DHW_ba2_d_t)
    return e_BB_ave


# ============================================================================
# 12. 給湯時のバックアップボイラーのガス消費量
# ============================================================================


# ============================================================================
# 12.1 ガス消費量
# ============================================================================

# 付録D

# ============================================================================
# 12.2 バックアップボイラーが分担する給湯熱負荷
# ============================================================================

def get_L_BB_x_d_t(L_dashdash_k_d_t, L_dashdash_w_d_t, L_dashdash_s_d_t,
                   L_dashdash_b1_d_t, L_dashdash_b2_d_t, L_dashdash_ba1_d_t, L_dashdash_ba2_d_t,
                   Q_gen_DHW_d, L_DHW_d):
    """1時間あたりのバックアップボイラーが分担する給湯熱負荷 (7)

    Args:
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はりにおける太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はりにおける太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽水栓さし湯における太陽熱補正給湯熱負荷 (MJ/h)
      Q_gen_DHW_d(ndarray): 1日当たりの給湯の排熱利用量 (MJ/d)
      L_DHW_d(ndarray): 1日当たりの浴槽追焚を除く太陽熱補正給湯熱負荷 (MJ/d)

    Returns:
      tuple: 1時間あたりのバックアップボイラーが分担する給湯熱負荷(MJ/d)

    """

    Q_gen_DHW_d = np.repeat(Q_gen_DHW_d, 24)
    L_DHW_d = np.repeat(L_DHW_d, 24)

    # (7b)
    L_BB_DHW_k_d_t = L_dashdash_k_d_t - Q_gen_DHW_d * (L_dashdash_k_d_t / L_DHW_d)

    # (7c)
    L_BB_DHW_s_d_t = L_dashdash_s_d_t - Q_gen_DHW_d * (L_dashdash_s_d_t / L_DHW_d)

    # (7d)
    L_BB_DHW_w_d_t = L_dashdash_w_d_t - Q_gen_DHW_d * (L_dashdash_w_d_t / L_DHW_d)

    # (7e)
    L_BB_DHW_b1_d_t = L_dashdash_b1_d_t - Q_gen_DHW_d * (L_dashdash_b1_d_t / L_DHW_d)

    # (7f)
    L_BB_DHW_b2_d_t = L_dashdash_b2_d_t - Q_gen_DHW_d * (L_dashdash_b2_d_t / L_DHW_d)

    # (7g)
    L_BB_DHW_ba1_d_t = L_dashdash_ba1_d_t - Q_gen_DHW_d * (L_dashdash_ba1_d_t / L_DHW_d)

    # (7h)
    L_BB_DHW_ba2_d_t = L_dashdash_ba2_d_t

    # (7a)
    L_BB_DHW_d_t = L_BB_DHW_k_d_t + \
                   L_BB_DHW_s_d_t + \
                   L_BB_DHW_w_d_t + \
                   L_BB_DHW_b1_d_t + \
                   L_BB_DHW_b2_d_t + \
                   L_BB_DHW_ba1_d_t + \
                   L_BB_DHW_ba2_d_t

    return L_BB_DHW_d_t, L_BB_DHW_k_d_t, L_BB_DHW_s_d_t, L_BB_DHW_w_d_t, \
           L_BB_DHW_b1_d_t, L_BB_DHW_b2_d_t, L_BB_DHW_ba1_d_t, L_BB_DHW_ba2_d_t


# ============================================================================
# 13. 温水暖房時のバックアップボイラーのガス消費量(温水暖房へ排熱利用がある場合)
# ============================================================================

def get_L_BB_HWH_d_t(L_HWH_d_t, L_HWH_d, Q_gen_HWH_d):
    """1時間当たりのバックアップボイラーが分担する温水暖房熱負荷 (MJ/h) (8)

    Args:
      L_HWH_d_t(ndarray): 1時間当たりの温水暖房の熱負荷 (MJ/h)
      L_HWH_d(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      Q_gen_HWH_d(ndarray): 1日当たりの温水暖房の排熱利用量 (MJ/h)

    Returns:
      ndarray: 1時間当たりのバックアップボイラーが分担する温水暖房熱負荷 (MJ/h)

    """
    L_BB_HWH_d_t = np.zeros(24 * 365)

    L_HWH_d = np.repeat(L_HWH_d, 24)
    Q_gen_HWH_d = np.repeat(Q_gen_HWH_d, 24)

    # L_HWH_d ≠ 0 の場合
    f1 = (L_HWH_d > Q_gen_HWH_d)
    L_BB_HWH_d_t[f1] = L_HWH_d_t[f1] - Q_gen_HWH_d[f1] * (L_HWH_d_t[f1] / L_HWH_d[f1])

    # L_HWH_d = 0 の場合
    f2 = (L_HWH_d <= Q_gen_HWH_d)
    L_BB_HWH_d_t[f2] = 0

    return L_BB_HWH_d_t


# ============================================================================
# 14. 発電ユニット
# ============================================================================

# ============================================================================
# 14.1 排熱利用量
# ============================================================================

def get_Q_gen_x_d(exhaust, exhaust_priority, Q_PU_gen_d, r_DHW_gen_PU_d, r_HWH_gen_PU_d, L_DHW_d, L_HWH_d):
    """1日当たりの給湯・温水暖房の排熱利用量 (MJ/d) (9)(10)(11)

    Args:
      exhaust(bool): 温水暖房への排熱利用がある場合はTrue
      exhaust_priority(str): 温水暖房への排熱利用がある場合の排熱の優先先
      Q_PU_gen_d(ndarray): 1日当たりの発電ユニット排熱量 (MJ/d)
      r_HWH_gen_PU_d(ndarray): 発電ユニットの温水暖房排熱利用率 (-)
      L_DHW_d(ndarray): 1日当たりの浴槽追焚を除く太陽熱補正給湯熱負荷 (MJ/d)
      L_HWH_d(ndarray): 1日当たりの浴槽追焚を除く太陽熱補正給湯熱負荷 (MJ/d)
      r_DHW_gen_PU_d: returns: 1日当たりの給湯・温水暖房の排熱利用量をそれぞれ (MJ/d)

    Returns:
      tuple: 1日当たりの給湯・温水暖房の排熱利用量をそれぞれ (MJ/d)

    """
    if exhaust == False:
        # (9b)
        Q_gen_HWH_d = np.zeros(365)
        # (9a)
        Q_gen_DHW_d = np.clip(Q_PU_gen_d * r_DHW_gen_PU_d, None, L_DHW_d)
    elif exhaust_priority == '給湯優先':
        # (10a)
        Q_gen_DHW_d = np.clip(Q_PU_gen_d * r_DHW_gen_PU_d, None, L_DHW_d)
        # (10b)
        Q_gen_HWH_d = np.clip((Q_PU_gen_d - Q_gen_DHW_d) * r_HWH_gen_PU_d, None, L_HWH_d)
    elif exhaust_priority == '温水暖房優先':
        # (11a)
        Q_gen_HWH_d = np.clip(Q_PU_gen_d * r_HWH_gen_PU_d, None, L_HWH_d)
        # (11b)
        Q_gen_DHW_d = np.clip((Q_PU_gen_d - Q_gen_HWH_d) * r_HWH_gen_PU_d, None, L_DHW_d)
    else:
        raise ValueError((exhaust, exhaust_priority))

    return Q_gen_DHW_d, Q_gen_HWH_d


def get_Q_PU_gen_d(E_G_PU_d, e_H_PU_d):
    """1日当たりの発電ユニット排熱量 (12)

    Args:
      E_G_PU_d(ndarray): 1日当たりの発電ユニットのガス消費量 (MJ/d)
      e_H_PU_d(ndarray): 発電ユニットの日平均排熱効率 (-)

    Returns:
      ndarray: 1日当たりの発電ユニット排熱量 (MJ/d)

    """
    return E_G_PU_d * e_H_PU_d


# ============================================================================
# 14.2 発電量
# ============================================================================


def get_E_E_gen_PU_d_t(E_G_PU_d_t, e_E_PU_d):
    """1時間当たりの発電ユニットの発電量 (kWh/h) (13)

    Args:
      E_G_PU_d_t(ndarray): 1時間当たりの発電ユニットのガス消費量 (MJ/h)
      e_E_PU_d(ndarray): 発電ユニットの日平均発電効率 (-)

    Returns:
      ndarray: 発電ユニットの発電量 (kWh/h)

    """
    e_E_PU_d = np.repeat(e_E_PU_d, 24)

    E_E_gen_PU_d_t = E_G_PU_d_t * e_E_PU_d / 3.6

    return E_E_gen_PU_d_t


# ============================================================================
# 14.3 ガス消費量
# ============================================================================

def calc_E_G_PU_d_t(E_G_PU_d, E_E_PU_d, E_E_PU_d_t, e_E_PU_d):
    """1時間当たりの発電ユニットのガス消費量 (MJ/h) (14a)

    Args:
      E_G_PU_d(ndarray): 1日当たりの発電ユニットのガス消費量 (MJ/d)
      E_E_PU_d(ndarray): 1日当たりの発電ユニットの分担可能電力力負荷 (kWh/d)
      E_E_PU_d_t(ndarray): 1時間当たりの発電ユニットの分担可能電力力負荷 (kWh/h)
      e_E_PU_d(ndarray): 発電ユニットの日平均発電効率 (-)

    Returns:
      ndarray: 1時間当たりの発電ユニットのガス消費量 (MJ/h)

    """

    # 日付dの時刻hにおける当該時刻から23時までの発電ユニットのガス消費量 (MJ/d) (14c)
    E_dash_G_PU_d_h = get_E_dash_G_PU_d_h(E_E_PU_d_t, e_E_PU_d)

    # 日付dにおける発電ユニットの稼働開始時刻 (h) (14b)
    t_star_PU_start_d = get_t_star_PU_start_d(E_G_PU_d, E_dash_G_PU_d_h)

    # 時刻tの表を作成
    t = np.tile(np.arange(24), 365)

    # 計算結果格納領域
    E_G_PU_d_t = np.zeros(24 * 365)

    # 計算用に24時間化
    E_G_PU_d = np.repeat(E_G_PU_d, 24)
    e_E_PU_d = np.repeat(e_E_PU_d, 24)
    t_star_PU_start_d = np.repeat(t_star_PU_start_d, 24)

    # E_dash_G_PU_d_h の1時間後の配列の作成
    E_dash_G_PU_d_h_plus_1h = np.roll(E_dash_G_PU_d_h, -1)

    # 条件1: t_star_PU_start_d < 23 and t < t_star_PU_start_d
    f1 = np.logical_and(t_star_PU_start_d < 23, t < t_star_PU_start_d)
    E_G_PU_d_t[f1] = 0

    # 条件2: t_star_PU_start_d < 23 and t = t_star_PU_start_d
    f2 = np.logical_and(t_star_PU_start_d < 23, t == t_star_PU_start_d)
    E_G_PU_d_t[f2] = E_G_PU_d[f2] - E_dash_G_PU_d_h_plus_1h[f2]

    # 条件3: t_star_PU_start_d < 23 and t > t_star_PU_start_d
    f3 = np.logical_and(t_star_PU_start_d < 23, t > t_star_PU_start_d)
    E_G_PU_d_t[f3] = E_E_PU_d_t[f3] * 3.6 / e_E_PU_d[f3]

    # 条件4: t_star_PU_start_d = 23 and t < t_star_PU_start_d
    f4 = np.logical_and(t_star_PU_start_d == 23, t < t_star_PU_start_d)
    E_G_PU_d_t[f4] = 0

    # 条件5: t_star_PU_start_d = 23 and t = t_star_PU_start_d
    f5 = np.logical_and(t_star_PU_start_d == 23, t == t_star_PU_start_d)
    E_G_PU_d_t[f5] = E_G_PU_d[f5]

    return E_G_PU_d_t


def get_t_star_PU_start_d(E_G_PU_d, E_dash_G_PU_d_h):
    """日付dにおける発電ユニットの稼働開始時刻 (h) (14b)

    Args:
      E_G_PU_d(ndarray): 1日当たりの発電ユニットのガス消費量 (MJ/d)
      E_dash_G_PU_d_h(ndarray): 日付dの時刻hにおける当該時刻から23時までの発電ユニットのガス消費量 (MJ/d)

    Returns:
      ndarray: 日付dにおける発電ユニットの稼働開始時刻 (h)

    """
    # 0,1,2,3...23, 0,1,2...23, .. と 24*365のインデックスを作成
    index_map = np.tile(np.arange(24), 365)

    # E_G_PU_d <= E_dash_PU_d_h を満たすインデックスをTrueにする
    bool_map = np.repeat(E_G_PU_d, 24) <= E_dash_G_PU_d_h

    # index_map のうち、 bool_mapがFalseになっている箇所を0にする
    index_map = index_map * bool_map

    # index_map を 365 * 24 の2次元配列にする
    index_map = np.reshape(index_map, (365, 24))

    # 1日単位で最大のインデックスを取得
    t_star_PU_start_d = np.max(index_map, axis=1)

    return t_star_PU_start_d


def get_E_dash_G_PU_d_h(E_E_PU_d_t, e_E_PU_d):
    """日付dの時刻hにおける当該時刻から23時までの発電ユニットのガス消費量 (MJ/d) (14c)

    Args:
      E_E_PU_d_t(ndarray): 日付dの時刻tにおける1時間当たりの発電ユニットの分担可能電力負荷 (kWh/h)
      e_E_PU_d(ndarray): 日付dにおける発電ユニットの日平均発電効率 (-)

    Returns:
      ndarray: 日付dの時刻hにおける当該時刻から23時までの発電ユニットのガス消費量 (MJ/d)

    """
    E_E_PU_d_t = np.reshape(E_E_PU_d_t, (365, 24))

    E_dash_G_PU_d_h = np.zeros((365, 24))
    for h in range(24):
        E_dash_G_PU_d_h[:, h] = np.sum(E_E_PU_d_t[:, h:24], axis=1) * 3.6 / e_E_PU_d

    return np.reshape(E_dash_G_PU_d_h, 24*365)


def get_E_G_PU_d(PU_type, E_G_PU_EVt_d, E_G_PU_HVt_d=None):
    """1日当たりの発電ユニットのガス消費量 (MJ/d) (15)

    Args:
      PU_type(str): 発電ユニットの発電方式
      E_G_PU_EVt_d(ndarray): 1日当たりの発電ユニットの発電量推定時の仮想ガス消費量 (MJ/d)
      E_G_PU_HVt_d(ndarray, optional): 1日当たりの発電ユニットの排熱量推定時の仮想ガス消費量 (MJ/d) (Default value = None)

    Returns:
      ndarray: 1日当たりの発電ユニットの燃料消費量 (MJ/d)

    """
    if PU_type == '熱主':
        # (15a)
        return np.clip(E_G_PU_EVt_d, None, E_G_PU_HVt_d)
    elif PU_type == '電主':
        # (15b)
        return E_G_PU_EVt_d
    else:
        raise ValueError(PU_type)


def get_E_G_PU_EVt_d(E_E_gen_PU_EVt_d, e_E_PU_d):
    """1日当たりの発電ユニットの発電量推定時の仮想ガス消費量 (MJ/d) (16)

    Args:
      E_E_gen_PU_EVt_d(ndarray): 1日当たりの発電ユニットの発電量推定時の仮想発電量 (kWh/d)
      e_E_PU_d(ndarray): 発電ユニットの日平均発電効率 (-)

    Returns:
      ndarray: 1日当たりの発電ユニットの発電量推定時の仮想燃料消費量 (MJ/d)

    """
    return E_E_gen_PU_EVt_d * 3.6 / e_E_PU_d


def get_E_E_gen_PU_EVt_d(E_E_PU_d, L_DHW_d, L_HWH_d, a_PU, a_DHW, a_HWH, b, c):
    """1日当たりの発電ユニットの発電量推定時の仮想発電量 (kWh/d) (17)

    Args:
      E_E_PU_d(ndarray): 1日当たりの発電ユニットの分担可能電力負荷 (kWh/d)
      L_DHW_d(ndarray): 1日当たりの浴槽追焚を除く太陽熱補正給湯熱負荷 (MJ/d)
      L_HWH_d(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      a_PU(float): パラメータ a_PU
      a_DHW(float): パラメータ a_DHW
      a_HWH(float): パラメータ a_HWH
      b(float): パラメータ b
      c(float): パラメータ c

    Returns:
      ndarray: 1日当たりの発電ユニットの発電量推定時の仮想発電量

    """
    E_E_gen_PU_EVt_d = np.clip(a_PU * E_E_PU_d * 3.6 + a_DHW * L_DHW_d + a_HWH * L_HWH_d + b, None,
                               E_E_PU_d * c * 3.6) / 3.6
    return E_E_gen_PU_EVt_d


def get_E_G_PU_HVt_d(e_H_PU_d, L_DHW_d, L_HWH_d, r_H_gen_PU_HVt_d, a_DHW, a_HWH):
    """1日当たりの発電ユニットの排熱量推定時の仮想燃料消費 (MJ/d) (18)

    Args:
      e_H_PU_d(ndarray): 発電ユニットの日平均排熱効率 (-)
      L_DHW_d(ndarray): 1日当たりの浴槽追焚を除く太陽熱補正給湯熱負荷 (MJ/d)
      L_HWH_d(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      r_H_gen_PU_HVt_d(ndarray): 発電ユニットの排熱量推定時の仮想排熱量上限比 (-)
      a_DHW(float): パラメータ a_DHW
      a_HWH(float): パラメータ a_HWH

    Returns:
      ndarray: 1日当たりの発電ユニットの排熱量推定時の仮想燃料消費 (MJ/d)

    """
    E_G_PU_HVt_d = (a_DHW * L_DHW_d + a_HWH * L_HWH_d) * r_H_gen_PU_HVt_d / e_H_PU_d
    return E_G_PU_HVt_d


def get_r_H_gen_PU_HVt_d(L_DHW_d, L_HWH_d, a_DHW, a_HWH, b):
    """発電ユニットの排熱量推定時の仮想排熱量上限比 (-) (19)

    Args:
      L_DHW_d(ndarray): 1日当たりの浴槽追焚を除く太陽熱補正給湯熱負荷 (MJ/d)
      L_HWH_d(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      a_DHW(float): パラメータ a_DHW
      a_HWH(float): パラメータ a_HWH
      b(float): パラメータ b

    Returns:
      ndarray: 発電ユニットの排熱量推定時の仮想排熱量上限比

    """
    r_H_gen_PU_HVt_d = a_DHW * L_DHW_d + a_HWH * L_HWH_d + b
    return r_H_gen_PU_HVt_d


# ============================================================================
# 14.4 発電効率
# ============================================================================

def get_e_E_PU_d(E_E_PU_d, L_DHW_d, L_HWH_d, a_PU, a_DHW, a_HWH, b, e_E_PU_d_max, e_E_PU_d_min):
    """発電ユニットの日平均発電効率 (-) (20)

    Args:
      E_E_PU_d(ndarray): 1日当たりの発電ユニットの分担可能電力負荷 (kWh/d)
      L_DHW_d(ndarray): 1日当たりの浴槽追焚を除く太陽熱補正給湯熱負荷 (MJ/d)
      L_HWH_d(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      a_PU(float): パレメータ a_PU
      a_DHW(float): パラメータ a_DHW
      a_HWH(float): パラメータ a_HWH
      b(float): パラメータ b
      e_E_PU_d_max(float): 上限値
      e_E_PU_d_min(float): 下限値

    Returns:
      ndarray: 発電ユニットの日平均発電効率 (-)

    """

    e_E_PU_d = a_PU * E_E_PU_d * 3.6 + a_DHW * L_DHW_d + a_HWH * L_HWH_d + b

    return np.clip(e_E_PU_d, e_E_PU_d_min, e_E_PU_d_max)


# ============================================================================
# 14.5 排熱効率
# ============================================================================

def get_e_H_PU_d(E_E_PU_d, L_DHW_d, L_HWH_d, a_PU, a_DHW, a_HWH, b, e_H_PU_d_min, e_H_PU_d_max):
    """発電ユニットの日平均排熱効率 (-) (21)

    Args:
      E_E_PU_d(ndarray): 1日当たりの発電ユニットの分担可能電力負荷 (kWh/d)
      L_DHW_d(ndarray): 1日当たりの浴槽追焚をの除く太陽熱補正給湯熱負荷 (MJ/d)
      L_HWH_d(ndarray): 1日当たりの温水暖房の熱負荷 (MJ/d)
      a_PU(float): パレメータ a_PU
      a_DHW(float): パラメータ a_DHW
      a_HWH(float): パラメータ a_HWH
      b(float): パラメータ b
      e_H_PU_d_max(float): 上限値
      e_H_PU_d_min(float): 下限値

    Returns:
      ndarray: 発電ユニットの日平均排熱効率 (-)

    """
    e_H_PU_d = a_PU * E_E_PU_d * 3.6 + a_DHW * L_DHW_d + a_HWH * L_HWH_d + b

    return np.clip(e_H_PU_d, e_H_PU_d_min, e_H_PU_d_max)


# ============================================================================
# 14.6 分担可能電力負荷
# ============================================================================

def get_E_E_PU_d(E_E_PU_d_t):
    """1日当たりの発電ユニットの分担可能電力負荷 (kWh/d) (22)

    Args:
      E_E_PU_d_t(ndarray): 1時間当たりの発電ユニットの分担可能電力負荷 (kWh/h)

    Returns:
      ndarray: 1日当たりの発電ユニットの分担可能電力負荷 (kWh/d)

    """
    tmp = E_E_PU_d_t.reshape((365, 24))
    E_E_PU_d = np.sum(tmp, axis=1)

    return E_E_PU_d


def get_E_E_PU_d_t(E_E_dmd_PU_d_t, P_rtd_PU, reverse):
    """1時間当たりの発電ユニットの分担可能電力負荷 (kWh/h) (23)

    Args:
      E_E_dmd_PU_d_t(ndarray): 1時間当たりの発電ユニットの電力需要 (kWh/h)
      P_rtd_PU(int): 定格発電出力 (W)
      reverse(bool): 逆潮流の有無

    Returns:
      ndarray: 1時間当たりの発電ユニットの分担可能電力負荷  (kWh/h)

    """
    if reverse == False:
        return np.clip(E_E_dmd_PU_d_t, None, P_rtd_PU * 10 ** (-3))
    else:
        return np.ones_like(E_E_dmd_PU_d_t) * P_rtd_PU * 10 ** (-3)


def get_E_E_dmd_PU_d_t(E_E_dmd_d_t, E_E_TU_aux_d_t):
    """発電ユニットの電力需要 (kWh/h) (24)

    Args:
      E_E_dmd_d_t(ndarray): 1時間当たりの電力需要 (kWh/h)
      E_E_TU_aux_d_t(ndarray): 1時間当たりのタンクユニットの補機消費電力量 (kWh/h)

    Returns:
      発電ユニットの電力需要 (kWh/h)

    """
    E_E_dmd_PU_d_t = E_E_dmd_d_t + E_E_TU_aux_d_t

    return E_E_dmd_PU_d_t


# ============================================================================
# 15. タンクユニットの補機消費電力
# ============================================================================

def get_E_E_TU_aux_d_t(E_E_TU_aux_DHW_d_t, E_E_TU_aux_HWH_d_t, E_E_TU_aux_ba2_d_t):
    """1時間当たりのタンクユニットの補機消費電力量 (25)

    Args:
      E_E_TU_aux_DHW_d_t(ndarray): 1時間当たりの給湯時のタンクユニットの補機消費電力量 (kWh/h)
      E_E_TU_aux_HWH_d_t(ndarray): 1時間当たりの温水暖房時のタンクユニットの補機消費電力量 (kWh/h)
      E_E_TU_aux_ba2_d_t(ndarray): 1時間当たりの浴槽追焚のタンクユニットの補機消費電力量 (kWh/h)

    Returns:
      ndarray: 1時間当たりのタンクユニットの補機消費電力量 (kWh/h)

    """
    E_E_TU_aux_d_t = E_E_TU_aux_DHW_d_t + E_E_TU_aux_HWH_d_t + E_E_TU_aux_ba2_d_t
    return E_E_TU_aux_d_t


def get_E_E_TU_aux_DHW_d_t(P_TU_aux_DHW):
    """1時間当たりの給湯時のタンクユニットの補機消費電力量 (kWh/h) (26)

    Args:
      P_TU_aux_DHW(float): 給湯のタンクユニットの補機消費電力 (W)

    Returns:
      float: 1時間当たりの給湯時のタンクユニットの補機消費電力量 (kWh/h)

    """
    E_E_TU_aux_DHW_d_t = P_TU_aux_DHW * 10 ** (-3)
    return E_E_TU_aux_DHW_d_t


def get_E_E_TU_aux_HWH_d_t(exhaust, P_TU_aux_HWH=None, r_WS_HWH_d_t=None):
    """1時間当たりの温水暖房時のタンクユニットの補機消費電力量 (kWh/h) (27)

    Args:
      exhaust(bool): 温水暖房への排熱利用がある場合はTrue
      P_TU_aux_HWH(param r_WS_HWH_d_t: 温水暖房の温水供給運転率 (-), optional): 給湯のタンクユニットの補機消費電力 (W) (Default value = None)
      r_WS_HWH_d_t(return: 1時間当たりの給湯時のタンクユニットの補機消費電力量 (kWh/h), optional): 温水暖房の温水供給運転率 (-) (Default value = None)

    Returns:
      ndarray: 1時間当たりの給湯時のタンクユニットの補機消費電力量 (kWh/h)

    """
    if exhaust:
        # -- ①温水暖房への排熱利用がある場合 --
        E_E_TU_aux_HWH_d_t = P_TU_aux_HWH * r_WS_HWH_d_t * 10 ** (-3)
    else:
        # -- ②温水暖房への排熱利用がない場合 --
        E_E_TU_aux_HWH_d_t = 73.0 * r_WS_HWH_d_t * 10 ** (-3)

    return E_E_TU_aux_HWH_d_t


def calc_E_E_TU_aux_ba2_d_t(L_BB_DHW_ba2_d_t):
    """1時間当たりの浴槽追焚のタンクユニットの補機消費電力量 (kWh/h)

    Args:
      L_BB_DHW_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの浴槽追焚のタンクユニットの補機消費電力量 (kWh/h)

    """
    E_E_TU_aux_ba2_d_t = bb_dhw.get_E_E_BB_aux_ba2_d_t(L_BB_DHW_ba2_d_t)

    return E_E_TU_aux_ba2_d_t


def get_L_BB_DHW_ba2_d_t(L_dashdash_ba2_d_t):
    """1時間当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷 (MJ/h) (28)

    Args:
      L_dashdash_ba2_d_t(ndarray): 1 時間当たりの浴槽追焚時の太陽熱補正給湯熱負荷（MJ/h）

    Returns:
      ndarray: 1 時間当たりの浴槽追焚時におけるバックアップボイラーが分担する給湯熱負荷(MJ/h)

    """
    return L_dashdash_ba2_d_t


# ============================================================================
# 16. その他
# ============================================================================


def get_L_DHW_d(L_DHW_d_t):
    """1日当たりの発電ユニットによる浴槽追焚を除く給湯熱負荷 (MJ/d) (29)

    Args:
      L_DHW_d_t(ndarray): 1時間当たりの発電ユニットにおける浴槽追焚を除く給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 1日当たりの発電ユニットにおける浴槽追焚を除く給湯熱負荷 (MJ/d)

    """
    L_DHW_d = np.sum(L_DHW_d_t.reshape(365, 24), axis=1)
    return L_DHW_d


def get_L_DHW_d_t(L_dashdash_k_d_t, L_dashdash_w_d_t, L_dashdash_s_d_t, L_dashdash_b1_d_t, L_dashdash_b2_d_t,
                  L_dashdash_ba1_d_t):
    """1時間当たりの発電ユニットによる浴槽追焚を除く給湯熱負荷 (30)

    Args:
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽自動追焚時における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯における太陽熱補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの発電ユニットによる浴槽追焚を除く給湯熱負荷 (MJ/h)

    """
    L_DHW_d_t = L_dashdash_k_d_t + L_dashdash_w_d_t + L_dashdash_s_d_t + L_dashdash_b1_d_t + L_dashdash_b2_d_t + L_dashdash_ba1_d_t
    return L_DHW_d_t


def get_L_HWH_d(L_HWH_d_t):
    """1日当たりの温水暖房の熱負荷 (31)

    Args:
      L_HWH_d_t(ndarray): 1時間当たりの温水暖房の熱負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの温水暖房の熱負荷 (MJ/d)

    """
    # 8760時間の1次元配列を364x24の2次元配列に変換する
    tmp = L_HWH_d_t.reshape((365, 24))

    # 2次元目を合算して配列を1次元化
    L_HWH_d = np.sum(tmp, axis=1)

    return L_HWH_d
