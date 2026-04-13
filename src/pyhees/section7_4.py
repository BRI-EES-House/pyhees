# ============================================================================
# 第七章 給湯設備
# 第四節 電気ヒートポンプ給湯機
# ============================================================================

import numpy as np


# ============================================================================
# 5. 消費電力量
# ============================================================================

def calc_E_E_hs_d_t(L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t, L_dashdash_b1_d_t, L_dashdash_b2_d_t,
                    L_dashdash_ba1_d_t, L_dashdash_ba2_d_t, daytime_heating, R_E_day_in, daytime_heating_control_in,
                    e_rtd=None, theta_ex_d_Ave_d=None, theta_ex_d_t=None, CO2HP=None):
    """1日当たりの給湯機の消費電力量 (1)

    Args:
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h)
      daytime_heating(bool): 昼間沸上げを評価するかのフラグ
      R_E_day_in(float): 昼間消費電力量比率（入力値） (%)
      daytime_heating_control_in(str): 昼間沸き上げ時間帯の制御（入力値）
      e_rtd(float, optional): 当該給湯機の効率 (Default value = None)
      theta_ex_d_Ave_d(ndarray, optional): 日付dにおける日平均外気温 (℃) (Default value = None)
      theta_ex_d_t(ndarray, optional): 日付dの時刻tにおける外気温度 (℃) (Default value = None)
      CO2HP(dict, optional): CO2HPパラメーターの辞書 (Default value = None)

    Returns:
      ndarray: 1日当たりの給湯機の消費電力量 (kWh/d)

    """
    # 各用途における太陽熱補正給湯熱負荷 (36)
    L_dashdash_k_d = get_L_dashdash_k_d(L_dashdash_k_d_t)
    L_dashdash_s_d = get_L_dashdash_s_d(L_dashdash_s_d_t)
    L_dashdash_w_d = get_L_dashdash_w_d(L_dashdash_w_d_t)
    L_dashdash_b1_d = get_L_dashdash_b1_d(L_dashdash_b1_d_t)
    L_dashdash_b2_d = get_L_dashdash_b2_d(L_dashdash_b2_d_t)
    L_dashdash_ba1_d = get_L_dashdash_ba1_d(L_dashdash_ba1_d_t)
    L_dashdash_ba2_d = get_L_dashdash_ba2_d(L_dashdash_ba2_d_t)

    # 太陽熱補正給湯熱負荷 (35)
    L_dashdash_d = get_L_dashdash_d(L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d, L_dashdash_b1_d, L_dashdash_b2_d,
                                    L_dashdash_ba1_d, L_dashdash_ba2_d)

    # 表8　外気温度
    theta_star_ex_sum = get_theta_star_ex_sum()  # 夏期条件
    theta_star_ex_imd = get_theta_star_ex_imd()  # 中間期条件
    theta_star_ex_win = get_theta_star_ex_win()  # 冬期条件
    theta_star_ex_frst = get_theta_star_ex_frst()  # 着霜条件
    theta_star_ex_win_cd = get_theta_star_ex_win_cd()  # 寒冷地冬期条件
    theta_star_ex_frst_upper = get_theta_star_ex_frst_upper()  # 着霜領域(上限)条件
    theta_star_ex_frst_imd = get_theta_star_ex_frst_imd()  # 着霜領域(中間)条件

    # e_rtdがNoneの場合は、規定値を用いる
    if e_rtd is None:
        e_rtd = get_e_rtd_default()
    else:
        e_rtd = get_e_rtd(e_rtd)

    # CO2HPがNoneの場合は、表7より給湯機の仕様の決定
    if CO2HP is None:
        CO2HP = get_spec(e_rtd)

    # 昼間消費電力量比率（%）
    # 昼間沸き上げ時間帯の制御
    R_E_day = get_R_E_day(daytime_heating, R_E_day_in, daytime_heating_control_in)
    daytime_heating_control = get_daytime_heating_control(daytime_heating, R_E_day_in, daytime_heating_control_in)

    P_HP_imd_std_test = CO2HP['P_HP_imd_std_test']
    P_HP_sum_std_test = CO2HP['P_HP_sum_std_test']
    P_HP_win_std_test = CO2HP['P_HP_win_std_test']
    q_HP_imd_std_test = CO2HP['q_HP_imd_std_test']
    q_HP_sum_std_test = CO2HP['q_HP_sum_std_test']
    q_HP_win_std_test = CO2HP['q_HP_win_std_test']
    e_HP_def_high_test = CO2HP['e_HP_def_high_test']
    e_HP_frst_high_test = CO2HP['e_HP_frst_high_test']
    theta_bw_frst_high_test = CO2HP['theta_bw_frst_high_test']
    theta_bw_sum_std_test = CO2HP['theta_bw_sum_std_test']
    theta_bw_imd_std_test = CO2HP['theta_bw_imd_std_test']
    theta_bw_win_std_test = CO2HP['theta_bw_win_std_test']
    A_p = CO2HP['A_p']
    B_p = CO2HP['B_p']
    P_aux_HP_on_test = CO2HP['P_aux_HP_on_test']
    P_aux_HP_off_test = CO2HP['P_aux_HP_off_test']
    Q_loss_test = CO2HP['Q_loss_test']
    R_tnk_test = CO2HP['R_tnk_test']
    theta_hat_bw_win_cm1_test = CO2HP['theta_hat_bw_win_cm1_test']
    theta_hat_bw_win_cm2_test = CO2HP['theta_hat_bw_win_cm2_test']

    # ファーストモードの1日当たりの沸き上げ熱量に対する昼間の沸き上げ熱量の比 (34-1)(34-2)
    R_Q_dot_HP_day_cm1 = get_R_Q_dot_HP_day_cm1(R_E_day)
    # セカンドモードの1日当たりの沸き上げ熱量に対する昼間の沸き上げ熱量の比 (34-1)(34-3)
    R_Q_dot_HP_day_cm2 = get_R_Q_dot_HP_day_cm2(R_E_day)

    # 表5　沸き上げ温度条件の種類　(標準条件,　高温条件)
    theta_star_bw_std, theta_star_bw_high = get_theta_star_bw()

    # ファーストモードのM1スタンダードモード沸き上げ温度 (32a-1)(32b-1)(32c-1)(32d-1)(32e-1)
    theta_hat_bw_sum_cm1 = get_theta_hat_bw_sum_cm1(theta_star_bw_std)
    theta_hat_bw_imd_cm1 = get_theta_hat_bw_imd_cm1(theta_star_bw_std)
    theta_hat_bw_win_cm1 = get_theta_hat_bw_win_cm1(theta_star_bw_std, theta_hat_bw_win_cm1_test)
    theta_hat_bw_frst_cm1 = get_theta_hat_bw_frst_cm1(theta_star_bw_high, theta_hat_bw_win_cm1)
    theta_hat_bw_win_cd_cm1 = get_theta_hat_bw_win_cd_cm1(theta_star_bw_high, theta_hat_bw_win_cm1)
    # セカンドモードのM1スタンダードモード沸き上げ温度 (32a-2)(32b-2)(32c-2)(32d-2)(32e-2)
    theta_hat_bw_win_cm2 = get_theta_hat_bw_win_cm2(theta_hat_bw_win_cm1, theta_hat_bw_win_cm1_test, theta_hat_bw_win_cm2_test)
    theta_hat_bw_sum_cm2 = get_theta_hat_bw_sum_cm2(theta_hat_bw_sum_cm1, theta_hat_bw_win_cm1, theta_hat_bw_win_cm2)
    theta_hat_bw_imd_cm2 = get_theta_hat_bw_imd_cm2(theta_hat_bw_imd_cm1, theta_hat_bw_win_cm1, theta_hat_bw_win_cm2)
    theta_hat_bw_frst_cm2 = get_theta_hat_bw_frst_cm2(theta_star_bw_high, theta_hat_bw_frst_cm1, theta_hat_bw_win_cm1, theta_hat_bw_win_cm2)
    theta_hat_bw_win_cd_cm2 = get_theta_hat_bw_win_cd_cm2(theta_star_bw_high, theta_hat_bw_win_cd_cm1, theta_hat_bw_win_cm1, theta_hat_bw_win_cm2)

    # ファーストモードのM1スタンダードモード沸き上げ温度 (31)
    theta_hat_bw_cm1_d = get_theta_hat_bw_cm_d(theta_star_ex_imd, theta_star_ex_win, theta_star_ex_frst, theta_star_ex_win_cd,
                          theta_star_ex_frst_upper, theta_ex_d_t, theta_hat_bw_sum_cm1, theta_hat_bw_imd_cm1,
                          theta_hat_bw_win_cm1, theta_hat_bw_frst_cm1, theta_hat_bw_win_cd_cm1)
    # セカンドモードのM1スタンダードモード沸き上げ温度 (31)
    theta_hat_bw_cm2_d = get_theta_hat_bw_cm_d(theta_star_ex_imd, theta_star_ex_win, theta_star_ex_frst, theta_star_ex_win_cd,
                          theta_star_ex_frst_upper, theta_ex_d_t, theta_hat_bw_sum_cm2, theta_hat_bw_imd_cm2,
                          theta_hat_bw_win_cm2, theta_hat_bw_frst_cm2, theta_hat_bw_win_cd_cm2)

    # 試験時の等価貯湯温度 (29)
    theta_tnk_eq_test = get_theta_tnk_eq_test(Q_loss_test, R_tnk_test, theta_star_ex_win)

    # 冬期条件、着霜期条件および着霜領域（上限）における等価貯湯温度 (28)
    theta_tnk_eq_win, theta_tnk_eq_frst, theta_tnk_eq_frst_upper = get_theta_tnk_eq(theta_tnk_eq_test)

    # ファーストモードの等価貯湯温度(27-1)
    theta_tnk_eq_cm1_d = get_theta_tnk_eq_cm1_d(theta_ex_d_Ave_d, theta_star_ex_frst, theta_star_ex_frst_upper, theta_tnk_eq_win,
                           theta_tnk_eq_frst, theta_tnk_eq_frst_upper)
    # セカンドモードの等価貯湯温度(27-2)
    theta_tnk_eq_cm2_d = get_theta_tnk_eq_cm2_d(theta_ex_d_Ave_d, theta_tnk_eq_cm1_d, theta_hat_bw_cm1_d, theta_hat_bw_cm2_d)

    # ファーストモードの1日当たりの貯湯熱損失量(26)
    Q_dot_loss_cm1_d = get_Q_dot_loss_cm_d(theta_tnk_eq_cm1_d, theta_ex_d_Ave_d, R_tnk_test)
    # セカンドモードの1日当たりの貯湯熱損失量(26)
    Q_dot_loss_cm2_d = get_Q_dot_loss_cm_d(theta_tnk_eq_cm2_d, theta_ex_d_Ave_d, R_tnk_test)

    # ファーストモードの1日当たりの沸き上げ熱量(25)
    Q_dot_HP_cm1_d = get_Q_dot_HP_cm_d(L_dashdash_d, Q_dot_loss_cm1_d)
    # セカンドモードの1日当たりの沸き上げ熱量(25)
    Q_dot_HP_cm2_d = get_Q_dot_HP_cm_d(L_dashdash_d, Q_dot_loss_cm2_d)

    # 試験時の着霜期高温条件における除霜効率係数 (17)
    C_def_frst_test = get_C_def_frst_test(e_HP_def_high_test, e_HP_frst_high_test)

    # ファーストモードの着霜期条件における除霜効率係数 (16a)
    C_def_frst_cm1 = get_C_def_frst_cm(theta_hat_bw_frst_cm1, theta_bw_frst_high_test, C_def_frst_test)
    # ファーストモードの着霜期条件における除霜効率係数 (16a)
    C_def_frst_cm2 = get_C_def_frst_cm(theta_hat_bw_frst_cm2, theta_bw_frst_high_test, C_def_frst_test)

    # ファーストモードの寒冷地冬期条件における除霜効率係数 (16b)
    C_def_win_cd_cm1 = get_C_def_win_cd_cm(theta_hat_bw_win_cd_cm1, theta_bw_frst_high_test, theta_star_ex_win_cd, theta_star_ex_frst_imd,
                                           C_def_frst_test)
    # セカンドモードの寒冷地冬期条件における除霜効率係数 (16b)
    C_def_win_cd_cm2 = get_C_def_win_cd_cm(theta_hat_bw_win_cd_cm2, theta_bw_frst_high_test, theta_star_ex_win_cd, theta_star_ex_frst_imd,
                                           C_def_frst_test)

    # 試験時のヒートポンプのエネルギー消費効率 (12)
    e_HP_sum_std_test, e_HP_imd_std_test, e_HP_win_std_test = get_e_HP_std_test(q_HP_sum_std_test, q_HP_imd_std_test, q_HP_win_std_test,
                      P_HP_sum_std_test, P_HP_imd_std_test, P_HP_win_std_test)

    # 沸き上げ温度を標準条件または高温条件とした場合のヒートポンプのエネルギー消費効率 (11)
    e_HP_sum_std, e_HP_imd_std, e_HP_win_std, e_HP_frst_upper_std, e_HP_frst_high, e_HP_win_cd_high = \
        get_e_HP_std(theta_bw_sum_std_test, theta_bw_imd_std_test, theta_bw_win_std_test, theta_star_bw_std, theta_star_ex_imd,
                 theta_star_ex_win, theta_star_ex_frst_upper, theta_star_bw_high, theta_bw_frst_high_test,
                 e_HP_sum_std_test, e_HP_imd_std_test, e_HP_win_std_test, e_HP_frst_high_test)

    # ファーストモードの実動効率比 (10-1)
    r_e_HP_cm1 = get_r_e_HP_cm1()

    # ファーストモードの実動効率比 (10-2)
    r_e_HP_cm2 = get_r_e_HP_cm2(theta_hat_bw_win_cm2)

    # ファーストモードのヒートポンプのM1スタンダードモードエネルギー消費効率 (9)
    e_hat_HP_sum_cm1, e_hat_HP_imd_cm1, e_hat_HP_win_cm1, e_hat_HP_frst_upper_cm1, e_hat_HP_frst_cm1, e_hat_HP_win_cd_cm1\
        = get_e_hat_HP_cm(r_e_HP_cm1, e_HP_sum_std, e_HP_imd_std, e_HP_win_std, e_HP_frst_upper_std, e_HP_frst_high, e_HP_win_cd_high,
                    theta_hat_bw_sum_cm1, theta_hat_bw_imd_cm1, theta_hat_bw_win_cm1, theta_hat_bw_frst_cm1, theta_hat_bw_win_cd_cm1,
                    theta_star_bw_std, theta_star_bw_high)
    # セカンドモードのヒートポンプのM1スタンダードモードエネルギー消費効率 (9)
    e_hat_HP_sum_cm2, e_hat_HP_imd_cm2, e_hat_HP_win_cm2, e_hat_HP_frst_upper_cm2, e_hat_HP_frst_cm2, e_hat_HP_win_cd_cm2\
        = get_e_hat_HP_cm(r_e_HP_cm2, e_HP_sum_std, e_HP_imd_std, e_HP_win_std, e_HP_frst_upper_std, e_HP_frst_high, e_HP_win_cd_high,
                    theta_hat_bw_sum_cm2, theta_hat_bw_imd_cm2, theta_hat_bw_win_cm2, theta_hat_bw_frst_cm2, theta_hat_bw_win_cd_cm2,
                    theta_star_bw_std, theta_star_bw_high)

    # 沸き上げ時間帯の種類
    hrs_bw_tbl = get_table_6()

    tau_HP_cm1_hrs_bw_d_t_dic = {}
    tau_HP_cm2_hrs_bw_d_t_dic = {}

    E_E_HP_cm1_hrs_bw_d_t_dic = {}
    E_E_HP_cm2_hrs_bw_d_t_dic = {}

    for hrs_bw in hrs_bw_tbl:
        # 日付dの沸き上げ熱量に応じる運転における沸き上げ時間帯の区分hrs_bwに対する平均外気温度（℃） (37)
        theta_ex_ave_hrs_bw_d = get_theta_ex_ave_hrs_bw_d(hrs_bw, theta_ex_d_t)

        # 沸き上げ時間帯の区分hrs_bwに対する沸き上げ時間帯の制御
        heating_control_hrs_bw = get_heating_control_hrs_bw(hrs_bw, daytime_heating_control)

        # 沸き上げ時間帯の区分hrs_bwに対する沸き上げ時間帯の制御の参照時刻
        t_HP_ref_hrs_bw = get_t_HP_ref_hrs_bw(hrs_bw, heating_control_hrs_bw)

        # 沸き上げ時間帯に対する1日当たりのヒートポンプ運転時間数の上限(h/d) (33)
        tau_dot_HP_max_cm1_hrs_bw = get_tau_dot_HP_max_hrs_bw(hrs_bw, R_Q_dot_HP_day_cm1)
        tau_dot_HP_max_cm2_hrs_bw = get_tau_dot_HP_max_hrs_bw(hrs_bw, R_Q_dot_HP_day_cm2)
        assert tau_dot_HP_max_cm1_hrs_bw == tau_dot_HP_max_cm2_hrs_bw
        tau_dot_HP_max_hrs_bw = tau_dot_HP_max_cm1_hrs_bw

        # ファーストモード 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプのM1スタンダードモードエネルギー消費効率(-) (8)
        e_hat_HP_cm1_hrs_bw_d = get_e_hat_HP_cm_hrs_bw_d(theta_ex_ave_hrs_bw_d, theta_star_ex_sum, theta_star_ex_imd, theta_star_ex_win,
                                                         theta_star_ex_win_cd, theta_star_ex_frst_upper, theta_star_ex_frst,
                                                         e_hat_HP_sum_cm1, e_hat_HP_imd_cm1, e_hat_HP_win_cm1, e_hat_HP_win_cd_cm1,
                                                         e_hat_HP_frst_upper_cm1, e_hat_HP_frst_cm1)
        # セカンドモード 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプのM1スタンダードモードエネルギー消費効率(-) (8)
        e_hat_HP_cm2_hrs_bw_d = get_e_hat_HP_cm_hrs_bw_d(theta_ex_ave_hrs_bw_d, theta_star_ex_sum, theta_star_ex_imd, theta_star_ex_win,
                                                         theta_star_ex_win_cd, theta_star_ex_frst_upper, theta_star_ex_frst,
                                                         e_hat_HP_sum_cm2, e_hat_HP_imd_cm2, e_hat_HP_win_cm2, e_hat_HP_win_cd_cm2,
                                                         e_hat_HP_frst_upper_cm2, e_hat_HP_frst_cm2)

        # ファーストモード 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプの消費電力(kW) (14)
        P_HP_cm1_hrs_bw_d = get_P_HP_cm_hrs_bw_d(q_HP_sum_std_test, q_HP_win_std_test, A_p, B_p, theta_hat_bw_cm1_d, theta_ex_ave_hrs_bw_d,
                                                 theta_star_bw_std, theta_star_ex_sum, P_HP_sum_std_test)
        # セカンドモード 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプの消費電力(kW) (14)
        P_HP_cm2_hrs_bw_d = get_P_HP_cm_hrs_bw_d(q_HP_sum_std_test, q_HP_win_std_test, A_p, B_p, theta_hat_bw_cm2_d, theta_ex_ave_hrs_bw_d,
                                                 theta_star_bw_std, theta_star_ex_sum, P_HP_sum_std_test)

        # ファーストモード 日付dにおける制御モードcmの沸き上げ時間帯に対するヒートポンプの加熱能力 (13)
        q_HP_cm1_hrs_bw_d = get_q_HP_cm_hrs_bw_d(e_hat_HP_cm1_hrs_bw_d, P_HP_cm1_hrs_bw_d)
        # セカンドモード 日付dにおける制御モードcmの沸き上げ時間帯に対するヒートポンプの加熱能力 (13)
        q_HP_cm2_hrs_bw_d = get_q_HP_cm_hrs_bw_d(e_hat_HP_cm2_hrs_bw_d, P_HP_cm2_hrs_bw_d)

        # ファーストモード 日付dにおける制御モードcmの沸き上げ時間帯に対する1日当たりの沸き上げ熱量(MJ/d) (24)
        Q_dot_HP_cm1_hrs_bw_d =  get_Q_dot_HP_cm_hrs_bw_d(hrs_bw, Q_dot_HP_cm1_d, R_Q_dot_HP_day_cm1)
        # セカンドモード 日付dにおける制御モードcmの沸き上げ時間帯に対する1日当たりの沸き上げ熱量(MJ/d) (24)
        Q_dot_HP_cm2_hrs_bw_d =  get_Q_dot_HP_cm_hrs_bw_d(hrs_bw, Q_dot_HP_cm2_d, R_Q_dot_HP_day_cm2)

        # ファーストモード 日付dにおける制御モードcmの1日当たりのヒートポンプ運転時間 (23)
        tau_dot_HP_cm1_hrs_bw_d = get_tau_dot_HP_cm_hrs_bw_d(Q_dot_HP_cm1_hrs_bw_d, q_HP_cm1_hrs_bw_d, tau_dot_HP_max_hrs_bw)
        # セカンドモード 日付dにおける制御モードcmの1日当たりのヒートポンプ運転時間 (23)
        tau_dot_HP_cm2_hrs_bw_d = get_tau_dot_HP_cm_hrs_bw_d(Q_dot_HP_cm2_hrs_bw_d, q_HP_cm2_hrs_bw_d, tau_dot_HP_max_hrs_bw)

        # ファーストモード 日付dにおける制御モードcmの沸き上げ時間帯の区分に対する沸き上げ開始／終了時刻 (21)(22)
        t_HP_start_cm1_hrs_bw_d, t_HP_stop_cm1_hrs_bw_d = get_t_HP_start_stop_cm_hrs_bw_d(heating_control_hrs_bw, t_HP_ref_hrs_bw, tau_dot_HP_cm1_hrs_bw_d)
        # セカンドモード 日付dにおける制御モードcmの沸き上げ時間帯の区分に対する沸き上げ開始／終了時刻 (21)(22)
        t_HP_start_cm2_hrs_bw_d, t_HP_stop_cm2_hrs_bw_d = get_t_HP_start_stop_cm_hrs_bw_d(heating_control_hrs_bw, t_HP_ref_hrs_bw, tau_dot_HP_cm2_hrs_bw_d)

        # ファーストモード 日付dにおける制御モードcmの沸き上げ時間帯の区分に対する沸き上げ開始時刻における1時間当たりのヒートポンプ運転時間数 (20)
        tau_HP_start_cm1_hrs_bw_d = get_tau_HP_start_cm_hrs_bw_d(heating_control_hrs_bw, tau_dot_HP_cm1_hrs_bw_d)
        # セカンドモード 日付dにおける制御モードcmの沸き上げ時間帯の区分に対する沸き上げ開始時刻における1時間当たりのヒートポンプ運転時間数 (20)
        tau_HP_start_cm2_hrs_bw_d = get_tau_HP_start_cm_hrs_bw_d(heating_control_hrs_bw, tau_dot_HP_cm2_hrs_bw_d)

        # ファーストモード 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプ運転開始からの経過時間数 (19)
        etau_HP1_cm1_hrs_bw_d_t, etau_HP2_cm1_hrs_bw_d_t = get_etau_HP_cm_hrs_bw_d_t(t_HP_stop_cm1_hrs_bw_d, t_HP_start_cm1_hrs_bw_d, tau_HP_start_cm1_hrs_bw_d, tau_dot_HP_cm1_hrs_bw_d)
        # セカンドモード 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプ運転開始からの経過時間数 (19)
        etau_HP1_cm2_hrs_bw_d_t, etau_HP2_cm2_hrs_bw_d_t = get_etau_HP_cm_hrs_bw_d_t(t_HP_stop_cm2_hrs_bw_d, t_HP_start_cm2_hrs_bw_d, tau_HP_start_cm2_hrs_bw_d, tau_dot_HP_cm2_hrs_bw_d)

        # ファーストモード 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりのヒートポンプ運転時間 (18)
        tau_HP_cm1_hrs_bw_d_t_dic[hrs_bw], tau_HP1_cm1_hrs_bw_d_t, tau_HP2_cm1_hrs_bw_d_t = get_tau_HP_cm_hrs_bw_d_t(etau_HP1_cm1_hrs_bw_d_t, etau_HP2_cm1_hrs_bw_d_t)
        # セカンドモード 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりのヒートポンプ運転時間 (18)
        tau_HP_cm2_hrs_bw_d_t_dic[hrs_bw], tau_HP1_cm2_hrs_bw_d_t, tau_HP2_cm2_hrs_bw_d_t = get_tau_HP_cm_hrs_bw_d_t(etau_HP1_cm2_hrs_bw_d_t, etau_HP2_cm2_hrs_bw_d_t)

        # ファーストモード 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する除霜効率係数(-) (15)
        C_def_cm1_hrs_bw_d = get_C_def_cm_hrs_bw_d(theta_star_ex_frst_upper, theta_ex_ave_hrs_bw_d, theta_star_ex_frst, theta_star_ex_frst_imd,
                                                   theta_star_ex_win_cd, C_def_frst_cm1, C_def_win_cd_cm1)
        # セカンドモード 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する除霜効率係数(-) (15)
        C_def_cm2_hrs_bw_d = get_C_def_cm_hrs_bw_d(theta_star_ex_frst_upper, theta_ex_ave_hrs_bw_d, theta_star_ex_frst, theta_star_ex_frst_imd,
                                                   theta_star_ex_win_cd, C_def_frst_cm2, C_def_win_cd_cm2)

        # ファーストモード 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの沸き上げに係るヒートポンプの消費電力量(kWh/d) (6)
        E_dot_E_HP_bw_cm1_hrs_bw_d = get_E_dot_E_HP_bw_cm_hrs_bw_d(Q_dot_HP_cm1_hrs_bw_d, e_hat_HP_cm1_hrs_bw_d)
        # セカンドモード 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの沸き上げに係るヒートポンプの消費電力量(kWh/d) (6)
        E_dot_E_HP_bw_cm2_hrs_bw_d = get_E_dot_E_HP_bw_cm_hrs_bw_d(Q_dot_HP_cm2_hrs_bw_d, e_hat_HP_cm2_hrs_bw_d)

        # ファーストモード 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの除霜に係るヒートポンプの消費電力量(kWh/d) (7)
        E_dot_E_HP_def_cm1_hrs_bw_d = get_E_dot_E_HP_def_cm_hrs_bw_d(E_dot_E_HP_bw_cm1_hrs_bw_d, C_def_cm1_hrs_bw_d)
        # セカンドモード 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの除霜に係るヒートポンプの消費電力量(kWh/d) (7)
        E_dot_E_HP_def_cm2_hrs_bw_d = get_E_dot_E_HP_def_cm_hrs_bw_d(E_dot_E_HP_bw_cm2_hrs_bw_d, C_def_cm2_hrs_bw_d)

        # ファーストモード 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりのヒートポンプの消費電力量(kWh/d) (5)
        E_dot_E_HP_cm1_hrs_bw_d = get_E_dot_E_HP_cm_hrs_bw_d(E_dot_E_HP_bw_cm1_hrs_bw_d, E_dot_E_HP_def_cm1_hrs_bw_d)
        # セカンドモード 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりのヒートポンプの消費電力量(kWh/d) (5)
        E_dot_E_HP_cm2_hrs_bw_d = get_E_dot_E_HP_cm_hrs_bw_d(E_dot_E_HP_bw_cm2_hrs_bw_d, E_dot_E_HP_def_cm2_hrs_bw_d)

        # ファーストモード 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりのヒートポンプの消費電力量(kWh/h) (4)
        E_E_HP_cm1_hrs_bw_d_t_dic[hrs_bw] = get_E_E_HP_cm_hrs_bw_d_t(E_dot_E_HP_cm1_hrs_bw_d, tau_dot_HP_cm1_hrs_bw_d, tau_HP1_cm1_hrs_bw_d_t, tau_HP2_cm1_hrs_bw_d_t)
        # セカンドモード 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりのヒートポンプの消費電力量(kWh/h) (4)
        E_E_HP_cm2_hrs_bw_d_t_dic[hrs_bw] = get_E_E_HP_cm_hrs_bw_d_t(E_dot_E_HP_cm2_hrs_bw_d, tau_dot_HP_cm2_hrs_bw_d, tau_HP1_cm2_hrs_bw_d_t, tau_HP2_cm2_hrs_bw_d_t)

    # ファーストモードの補機の消費電力量　(30)
    E_E_aux_cm1_d_t = get_E_E_aux_cm_d_t(P_aux_HP_on_test, P_aux_HP_off_test, tau_HP_cm1_hrs_bw_d_t_dic)
    # ファーストモードの補機の消費電力量　(30)
    E_E_aux_cm2_d_t = get_E_E_aux_cm_d_t(P_aux_HP_on_test, P_aux_HP_off_test, tau_HP_cm2_hrs_bw_d_t_dic)

    # ファーストモード 日付dの時刻tにおける制御モードcmの1時間当たりのヒートポンプの消費電力量(kWh/h) (3)
    E_E_HP_cm1_d_t = get_E_E_HP_cm_d_t(E_E_HP_cm1_hrs_bw_d_t_dic)
    # セカンドモード 日付dの時刻tにおける制御モードcmの1時間当たりのヒートポンプの消費電力量(kWh/h) (3)
    E_E_HP_cm2_d_t = get_E_E_HP_cm_d_t(E_E_HP_cm2_hrs_bw_d_t_dic)

    # ファーストモードの1時間当たりの給湯機の消費電力量 (2)
    E_E_hs_cm1_d_t = get_E_E_hs_cm_d_t(E_E_HP_cm1_d_t, E_E_aux_cm1_d_t)
    # セカンドモードの1時間当たりの給湯機の消費電力量 (2)
    E_E_hs_cm2_d_t = get_E_E_hs_cm_d_t(E_E_HP_cm2_d_t, E_E_aux_cm2_d_t)

    # 制御におけるファーストモードの割合
    r_usg_cm1 = get_r_usg_cm1()

    # 制御におけるセカンドモードの割合
    r_usg_cm2 = get_r_usg_cm2()

    # 消費電力量(1)
    E_E_hs_d_t = get_E_E_hs_d_t(E_E_hs_cm1_d_t, E_E_hs_cm2_d_t, r_usg_cm1, r_usg_cm2)

    return E_E_hs_d_t


def get_E_E_hs_d_t(E_E_hs_cm1_d_t, E_E_hs_cm2_d_t, r_usg_cm1, r_usg_cm2):
    """1日当たりの給湯機の消費電力量 (kWh/d) (1)

    Args:
      E_E_hs_cm1_d_t(ndarray): 日付dの時刻tにおけるファーストモードの1時間当たりの給湯機の消費電力量
      E_E_hs_cm2_d_t(ndarray): 日付dの時刻tにおけるセカンドモードの1時間当たりの給湯機の消費電力量
      r_usg_cm1(ndarray): 制御モードがファーストモードの利用率
      r_usg_cm2(ndarray): 制御モードがセカンドモードの利用率

    Returns:
      ndarray: 1日当たりの給湯機の消費電力量 (kWh/d)

    """
    return r_usg_cm1 * E_E_hs_cm1_d_t + r_usg_cm2 * E_E_hs_cm2_d_t


def get_r_usg_cm1():
    """制御モードがファーストモードの利用率

    Args:

    Returns:
      float: 御におけるファーストモードの割合

    """
    return 0.8


def get_r_usg_cm2():
    """制御モードがセカンドモードの利用率

    Args:

    Returns:
      float: 御におけるセカンドモードの割合

    """
    return 0.2


def get_E_E_hs_cm_d_t(E_E_HP_cm_d_t, E_E_aux_cm_d_t):
    """日付dの時刻tにおける制御モードcmの1時間当たりの給湯機の消費電力量（kWh/h）(2)

    Args:
      E_E_HP_cm_d_t(ndarray): 日付dの時刻tにおける制御モードcmの1時間当たりのヒートポンプの消費電力量
      E_E_aux_cm_d_t(ndarray): 日付dの時刻tにおける制御モードcmの1時間当たりの補機の消費電力量

    Returns:
      ndarray: 日付dの時刻tにおける制御モードcmの1時間当たりの給湯機の消費電力量

    """
    return E_E_HP_cm_d_t + E_E_aux_cm_d_t


# ============================================================================
# 6. ガス消費量
# ============================================================================

def get_E_G_hs_d_t():
    """1時間当たりの給湯機のガス消費量 (MJ/h)

    Args:

    Returns:
      ndarray: 1時間当たりの給湯機のガス消費量 (MJ/h)

    """
    # 1日当たりの給湯機のガス消費量は0とする
    return np.zeros(24 * 365)


# ============================================================================
# 7. 灯油消費量
# ============================================================================

def get_E_K_hs_d_t():
    """1時間当たりの給湯機の灯油消費量 (MJ/h)

    Args:

    Returns:
      ndarray: 1時間当たりの給湯機の灯油消費量 (MJ/h)

    """
    # 1日当たりの給湯機の灯油消費量は0とする
    return np.zeros(24 * 365)


# ============================================================================
# 8. ヒートポンプ
# ============================================================================

# ============================================================================
# 8.1 消費電力量
# ============================================================================

def get_E_E_HP_cm_d_t(E_E_HP_cm_hrs_bw_d_t_dic):
    """日付dの時刻tにおける制御モードcm1時間当たりのヒートポンプの消費電力量(kWh/h) (3)

    Args:
        E_E_HP_cm_hrs_bw_d_t_dic(dict[str, ndarray]): 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりのヒートポンプの消費電力量(kWh/h)

    Returns:
        ndarray: 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりのヒートポンプの消費電力量(kWh/h)

    """

    return E_E_HP_cm_hrs_bw_d_t_dic['day'] + E_E_HP_cm_hrs_bw_d_t_dic['night']


def get_E_E_HP_cm_hrs_bw_d_t(E_dot_E_HP_cm_hrs_bw_d, tau_dot_HP_cm_hrs_bw_d, tau_HP1_cm_hrs_bw_d_t, tau_HP2_cm_hrs_bw_d_t):
    """日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりのヒートポンプの消費電力量(kWh/h) (4)

    Args:
        E_dot_E_HP_cm_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりのヒートポンプの消費電力量(kWh/d)
        tau_dot_HP_cm_hrs_bw_d(ndarray): 日付dにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりのヒートポンプ運転時間数(h/d)
        tau_HP1_cm_hrs_bw_d_t (ndarray): 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりの当該日の沸き上げ熱量に応じるヒートポンプ運転時間(h/h)
        tau_HP2_cm_hrs_bw_d_t (ndarray): 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりの翌日の沸き上げ熱量に応じるヒートポンプ運転時間(h/h)

    Returns:
        ndarray: 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりのヒートポンプの消費電力量(kWh/h)

    """
    E_E_HP1_cm_hrs_bw_d_t = np.zeros(24 * 365)
    E_E_HP2_cm_hrs_bw_d_t = np.zeros(24 * 365)

    # 1日後
    E_dot_E_HP_cm_hrs_bw_d_1 = np.roll(E_dot_E_HP_cm_hrs_bw_d, -1)
    tau_dot_HP_cm_hrs_bw_d_1 = np.roll(tau_dot_HP_cm_hrs_bw_d, -1)

    # 24時間化
    E_dot_E_HP_cm_hrs_bw_d_t = np.repeat(E_dot_E_HP_cm_hrs_bw_d, 24)
    E_dot_E_HP_cm_hrs_bw_d_1_t = np.repeat(E_dot_E_HP_cm_hrs_bw_d_1, 24)
    tau_dot_HP_cm_hrs_bw_d_t = np.repeat(tau_dot_HP_cm_hrs_bw_d, 24)
    tau_dot_HP_cm_hrs_bw_d_1_t = np.repeat(tau_dot_HP_cm_hrs_bw_d_1, 24)

    # (4b-1)
    f4b_1 = tau_dot_HP_cm_hrs_bw_d_t == 0.0
    E_E_HP1_cm_hrs_bw_d_t[f4b_1] = 0.0

    # (4b-2)
    f4b_2 = tau_dot_HP_cm_hrs_bw_d_t > 0.0
    E_E_HP1_cm_hrs_bw_d_t[f4b_2] = E_dot_E_HP_cm_hrs_bw_d_t[f4b_2] * tau_HP1_cm_hrs_bw_d_t[f4b_2] / tau_dot_HP_cm_hrs_bw_d_t[f4b_2]

    # (4c-1)
    f4c_1 = tau_dot_HP_cm_hrs_bw_d_1_t == 0.0
    E_E_HP2_cm_hrs_bw_d_t[f4c_1] = 0.0

    # (4c-2)
    f4c_2 = tau_dot_HP_cm_hrs_bw_d_1_t > 0.0
    E_E_HP2_cm_hrs_bw_d_t[f4c_2] = E_dot_E_HP_cm_hrs_bw_d_1_t[f4c_2] * tau_HP2_cm_hrs_bw_d_t[f4c_2] / tau_dot_HP_cm_hrs_bw_d_1_t[f4c_2]

    # (4a)
    E_E_HP_cm_hrs_bw_d_t = E_E_HP1_cm_hrs_bw_d_t + E_E_HP2_cm_hrs_bw_d_t

    return E_E_HP_cm_hrs_bw_d_t


def get_E_dot_E_HP_cm_hrs_bw_d(E_dot_E_HP_bw_cm_hrs_bw_d, E_dot_E_HP_def_cm_hrs_bw_d):
    """日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりのヒートポンプの消費電力量(kWh/d) (5)

    Args:
      E_dot_E_HP_bw_cm_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの沸き上げに係るヒートポンプの消費電力量(kWh/d)
      E_dot_E_HP_def_cm_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの除霜に係るヒートポンプの消費電力量(kWh/d)

    Returns:
      ndarray: 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりのヒートポンプの消費電力量(kWh/d)

    """
    return E_dot_E_HP_bw_cm_hrs_bw_d + E_dot_E_HP_def_cm_hrs_bw_d


def get_E_dot_E_HP_bw_cm_hrs_bw_d(Q_dot_HP_cm_hrs_bw_d, e_hat_HP_cm_hrs_bw_d):
    """日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの沸き上げに係るヒートポンプの消費電力量(kWh/d) (6)

    Args:
      Q_dot_HP_cm_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの沸き上げ熱量(MJ/d)
      e_hat_HP_cm_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプのM1スタンダードモードエネルギー消費効率(-)

    Returns:
      ndarray: 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの沸き上げに係るヒートポンプの消費電力量(kWh/d)

    """
    return (Q_dot_HP_cm_hrs_bw_d / e_hat_HP_cm_hrs_bw_d) * (1000 / 3600)


def get_E_dot_E_HP_def_cm_hrs_bw_d(E_dot_E_HP_bw_cm_hrs_bw_d, C_def_cm_hrs_bw_d):
    """日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの除霜に係るヒートポンプの消費電力量(kWh/d) (7)

    Args:
      E_dot_E_HP_bw_cm_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの沸き上げに係るヒートポンプの消費電力量(kWh/d)
      C_def_cm_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する除霜効率係数(-)

    Returns:
      ndarray: 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの除霜に係るヒートポンプの消費電力量(kWh/d)

    """
    return E_dot_E_HP_bw_cm_hrs_bw_d * (1.0 / C_def_cm_hrs_bw_d - 1.0)


# ============================================================================
# 8.2 エネルギー消費効率
# ============================================================================

def get_e_hat_HP_cm_hrs_bw_d(theta_ex_ave_hrs_bw_d, theta_star_ex_sum, theta_star_ex_imd, theta_star_ex_win, theta_star_ex_win_cd,
                             theta_star_ex_frst_upper, theta_star_ex_frst,
                             e_hat_HP_sum_cm, e_hat_HP_imd_cm, e_hat_HP_win_cm, e_hat_HP_win_cd_cm, e_hat_HP_frst_upper_cm,
                             e_hat_HP_frst_cm):
    """日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプのM1スタンダードモードエネルギー消費効率(-) (8)

    Args:
      theta_ex_ave_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における沸き上げ時間帯の区分hrs_bwに対する平均外気温度(℃)
      theta_star_ex_imd(float): 夏期条件の外気温度
      theta_star_ex_imd(float): 中間期条件の外気温度
      theta_star_ex_win(float): 冬期条件の外気温度
      theta_star_ex_win_cd(float): 標準条件の沸き上げ温度
      theta_star_ex_frst_upper(float): 着霜領域（上限）の外気温度
      theta_star_ex_frst(float): 着霜期条件の外気温度
      e_hat_HP_sum_cm(float): 制御モードcmの夏期条件におけるヒートポンプのM1スタンダードモードエネルギー消費効率
      e_hat_HP_imd_cm(float): 制御モードcmの中間期条件におけるヒートポンプのM1スタンダードモードエネルギー消費効率
      e_hat_HP_win_cm(float): 制御モードcmの冬期条件におけるヒートポンプのM1スタンダードモードエネルギー消費効率
      e_hat_HP_win_cd_cm(float): 制御モードcmの寒冷地冬期条件におけるヒートポンプの除霜運転を除くM1スタンダードモードエネルギー消費効率
      e_hat_HP_frst_upper_cm(float): 制御モードcmの着霜領域（上限）におけるヒートポンプのM1スタンダードモードエネルギー消費効率
      e_hat_HP_frst_cm(float): 制御モードcmの着霜期条件におけるヒートポンプの除霜運転を除くM1スタンダードモードエネルギー消費効率
      theta_star_ex_sum: returns: 日付dにおける制御モードcmのヒートポンプのM1スタンダードモードエネルギー消費効率

    Returns:
      ndarray: 日付dにおける制御モードcmのヒートポンプのM1スタンダードモードエネルギー消費効率

    """
    e_hat_HP_cm_hrs_bw_d = np.zeros(365)

    f1 = theta_star_ex_imd < theta_ex_ave_hrs_bw_d
    e_hat_HP_cm_hrs_bw_d[f1] = np.minimum(e_hat_HP_imd_cm + (theta_ex_ave_hrs_bw_d[f1] - theta_star_ex_imd) / (theta_star_ex_sum - theta_star_ex_imd) * \
                    (e_hat_HP_sum_cm - e_hat_HP_imd_cm), e_hat_HP_sum_cm)

    f2 = np.logical_and(theta_star_ex_win < theta_ex_ave_hrs_bw_d, theta_ex_ave_hrs_bw_d <= theta_star_ex_imd)
    e_hat_HP_cm_hrs_bw_d[f2] = e_hat_HP_imd_cm + (theta_ex_ave_hrs_bw_d[f2] - theta_star_ex_imd) / (theta_star_ex_imd - theta_star_ex_win) * \
                    (e_hat_HP_imd_cm - e_hat_HP_win_cm)

    f3 = np.logical_and(theta_star_ex_frst_upper < theta_ex_ave_hrs_bw_d, theta_ex_ave_hrs_bw_d <= theta_star_ex_win)
    e_hat_HP_cm_hrs_bw_d[f3] = e_hat_HP_win_cm + (theta_ex_ave_hrs_bw_d[f3] - theta_star_ex_win) / (theta_star_ex_win - theta_star_ex_frst_upper) * \
                    (e_hat_HP_win_cm - e_hat_HP_frst_upper_cm)

    f4 = np.logical_and(theta_star_ex_frst < theta_ex_ave_hrs_bw_d, theta_ex_ave_hrs_bw_d <= theta_star_ex_frst_upper)
    e_hat_HP_cm_hrs_bw_d[f4] = e_hat_HP_frst_cm + (theta_ex_ave_hrs_bw_d[f4] - theta_star_ex_frst) / (theta_star_ex_frst_upper - theta_star_ex_frst) * \
                    (e_hat_HP_frst_upper_cm - e_hat_HP_frst_cm)

    f5 = theta_ex_ave_hrs_bw_d <= theta_star_ex_frst
    e_hat_HP_cm_hrs_bw_d[f5] = e_hat_HP_frst_cm + (theta_ex_ave_hrs_bw_d[f5] - theta_star_ex_frst) / (theta_star_ex_frst - theta_star_ex_win_cd) * \
                    (e_hat_HP_frst_cm - e_hat_HP_win_cd_cm)

    return np.clip(e_hat_HP_cm_hrs_bw_d, 1.0, None)


def get_e_hat_HP_cm(r_e_HP_cm, e_HP_sum_std, e_HP_imd_std, e_HP_win_std, e_HP_frst_upper_cm, e_HP_frst_high, e_HP_win_cd_high,
                    theta_hat_bw_sum_cm, theta_hat_bw_imd_cm, theta_hat_bw_win_cm, theta_hat_bw_frst_cm, theta_hat_bw_win_cd_cm,
                    theta_star_bw_std, theta_star_bw_high):
    """ヒートポンプのM1スタンダードモードエネルギー消費効率(-) (9)

    Args:
      r_e_HP_cm(float): 制御モードcmの実動効率比
      e_HP_sum_std(float): 夏期-標準条件におけるヒートポンプのエネルギー消費効率
      e_HP_imd_std(float): 中間期-標準条件におけるヒートポンプのエネルギー消費効率
      e_HP_win_std(float): 冬期-標準条件におけるヒートポンプのエネルギー消費効率
      e_HP_frst_upper_cm(float): 着霜領域（上限）-標準条件におけるヒートポンプのエネルギー消費効率
      e_HP_frst_high(float): 着霜期-高温条件におけるヒートポンプの除霜運転を除くエネルギー消費効率
      e_HP_win_cd_high(float): 寒冷地冬期-高温条件におけるヒートポンプの除霜運転を除くエネルギー消費効率
      theta_hat_bw_sum_cm(float): 制御モードcmの夏期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_imd_cm(float): 制御モードcmの中間期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cm(float): 制御モードcmの冬期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_frst_cm(float): 制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cd_cm(float): 制御モードcmの寒冷地冬期条件におけるM1スタンダードモード沸き上げ温度
      theta_star_bw_std(float): 標準条件の沸き上げ温度
      theta_star_bw_high(float): 高温条件の沸き上げ温度

    Returns:
      tuple: ヒートポンプのM1スタンダードモードエネルギー消費効率

    """
    # (9a)
    e_hat_HP_sum_cm = r_e_HP_cm * e_HP_sum_std * (-0.01 * (theta_hat_bw_sum_cm - theta_star_bw_std) + 1.0)

    # (9b)
    e_hat_HP_imd_cm = r_e_HP_cm * e_HP_imd_std * (-0.01 * (theta_hat_bw_imd_cm - theta_star_bw_std) + 1.0)

    # (9c)
    e_hat_HP_win_cm = r_e_HP_cm * e_HP_win_std * (-0.01 * (theta_hat_bw_win_cm - theta_star_bw_std) + 1.0)

    # (9d)
    e_hat_HP_frst_upper_cm = r_e_HP_cm * e_HP_frst_upper_cm * (-0.01 * (theta_hat_bw_win_cm - theta_star_bw_std) + 1.0)

    # (9e)
    e_hat_HP_frst_cm = r_e_HP_cm * e_HP_frst_high * (-0.01 * (theta_hat_bw_frst_cm - theta_star_bw_high) + 1.0)

    # (9f)
    e_hat_HP_win_cd_cm = r_e_HP_cm * e_HP_win_cd_high * (-0.01 * (theta_hat_bw_win_cd_cm - theta_star_bw_high) + 1.0)

    return e_hat_HP_sum_cm, e_hat_HP_imd_cm, e_hat_HP_win_cm, e_hat_HP_frst_upper_cm, e_hat_HP_frst_cm, e_hat_HP_win_cd_cm


def get_r_e_HP_cm1():
    """ファーストモードの実動効率比(10-1)

    Args:

    Returns:
      float: ファーストモードの実動効率比

    """
    return 0.94


def get_r_e_HP_cm2(theta_hat_bw_win_cm):
    """セカンドモードの実動効率比(10-2)

    Args:
      theta_hat_bw_win_cm(float): 制御モードcmの冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      float: セカンドモードの実動効率比

    """
    if (theta_hat_bw_win_cm <= 75.0):
        return 0.90
    elif (75.0 < theta_hat_bw_win_cm):
        return -0.005 * (theta_hat_bw_win_cm - 75.0) + 0.90
    else:
        raise ValueError(theta_hat_bw_win_cm)


def get_e_HP_std(theta_bw_sum_std_test, theta_bw_imd_std_test, theta_bw_win_std_test, theta_star_bw_std, theta_star_ex_imd,
                 theta_star_ex_win, theta_star_ex_frst_upper, theta_star_bw_high, theta_bw_frst_high_test,
                 e_HP_sum_std_test, e_HP_imd_std_test, e_HP_win_std_test, e_HP_frst_high_test):
    """沸き上げ温度を標準条件または高温条件とした場合のヒートポンプのエネルギー消費効率(11)

    Args:
      theta_bw_sum_std_test(float): 試験時の夏期標準加熱条件における沸き上げ温度
      theta_bw_imd_std_test(float): 試験時の中間期標準加熱条件における沸き上げ温度
      theta_bw_win_std_test(float): 試験時の冬期標準加熱条件における沸き上げ温度
      theta_star_bw_std(float): 標準条件の沸き上げ温度
      theta_star_ex_imd(float): 中間期条件の外気温度
      theta_star_ex_win(float): 冬期条件の外気温度
      theta_star_ex_frst_upper(float): 着霜領域（上限）の外気温度
      theta_star_bw_high(float): 高温条件の沸き上げ温度
      theta_bw_frst_high_test(float): 試験時の着霜期高温加熱条件における沸き上げ温度
      e_HP_sum_std_test(float): 試験時の夏期標準加熱条件におけるヒートポンプのエネルギー消費効率
      e_HP_imd_std_test(float): 試験時の中間期標準加熱条件におけるヒートポンプのエネルギー消費効率
      e_HP_win_std_test(float): 試験時の冬期標準加熱条件におけるヒートポンプのエネルギー消費効率
      e_HP_frst_high_test(float): 試験時の着霜期高温加熱条件におけるヒートポンプの除霜運転を除くエネルギー消費効率

    Returns:
      tuple: 沸き上げ温度を標準条件または高温条件とした場合のヒートポンプのエネルギー消費効率

    """
    # 夏期-標準条件におけるヒートポンプのエネルギー消費効率（-）(11a)
    e_HP_sum_std = e_HP_sum_std_test / (-0.01 * (theta_bw_sum_std_test - theta_star_bw_std) + 1.0)

    # 中間期-標準条件におけるヒートポンプのエネルギー消費効率（-）(11b)
    e_HP_imd_std = e_HP_imd_std_test / (-0.01 * (theta_bw_imd_std_test - theta_star_bw_std) + 1.0)

    # 冬期-標準条件におけるヒートポンプのエネルギー消費効率（-）(11c)
    e_HP_win_std = e_HP_win_std_test / (-0.01 * (theta_bw_win_std_test - theta_star_bw_std) + 1.0)

    # 着霜領域（上限）-標準条件におけるヒートポンプのエネルギー消費効率（-）(11d)
    e_HP_frst_upper_std = e_HP_win_std + \
                          ((theta_star_ex_frst_upper - theta_star_ex_win) / (theta_star_ex_imd - theta_star_ex_win)) *\
                          (e_HP_imd_std - e_HP_win_std)

    # 着霜期-高温条件におけるヒートポンプの除霜運転を除くエネルギー消費効率（-）(11e)
    e_HP_frst_high = e_HP_frst_high_test / (-0.01 * (theta_bw_frst_high_test - theta_star_bw_high) + 1.0)

    # 寒冷地冬期-高温条件におけるヒートポンプの除霜運転を除くエネルギー消費効率（-）(11f)
    e_HP_win_cd_high = e_HP_frst_high * 0.82

    return e_HP_sum_std, e_HP_imd_std, e_HP_win_std, e_HP_frst_upper_std, e_HP_frst_high, e_HP_win_cd_high


def get_e_HP_std_test(q_HP_sum_std_test, q_HP_imd_std_test, q_HP_win_std_test,
                      P_HP_sum_std_test, P_HP_imd_std_test, P_HP_win_std_test):
    """試験時のヒートポンプのエネルギー消費効率(12)

    Args:
      q_HP_sum_std_test(float): 試験時の夏期標準加熱条件におけるヒートポンプの加熱能力
      q_HP_imd_std_test(float): 試験時の中間期標準加熱条件におけるヒートポンプの加熱能力
      q_HP_win_std_test(float): 試験時の冬期標準加熱条件におけるヒートポンプの加熱能力
      P_HP_sum_std_test(float): 試験時の夏期標準加熱条件におけるヒートポンプの消費電力
      P_HP_imd_std_test(float): 試験時の中間期標準加熱条件におけるヒートポンプの消費電力
      P_HP_win_std_test(float): 試験時の冬期標準加熱条件におけるヒートポンプの消費電力

    Returns:
      tuple: 試験時のヒートポンプのエネルギー消費効率

    """
    # 試験時の夏期標準加熱条件におけるヒートポンプのエネルギー消費効率（-）(12a)
    e_HP_sum_std_test = q_HP_sum_std_test / P_HP_sum_std_test

    # 試験時の中間期標準加熱条件におけるヒートポンプのエネルギー消費効率（-）(12b)
    e_HP_imd_std_test = q_HP_imd_std_test / P_HP_imd_std_test

    # 試験時の冬期標準条件におけるヒートポンプのエネルギー消費効率（-）(12c)
    e_HP_win_std_test = q_HP_win_std_test / P_HP_win_std_test

    return e_HP_sum_std_test, e_HP_imd_std_test, e_HP_win_std_test


# ============================================================================
# 8.3 加熱能力
# ============================================================================

def get_q_HP_cm_hrs_bw_d(e_hat_HP_cm_hrs_bw_d, P_HP_cm_hrs_bw_d):
    """日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプの加熱能力(kW) (13)

    Args:
      e_hat_HP_cm_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプのエネルギー消費効率(-)
      P_HP_cm_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプの消費電力(kW)

    Returns:
      ndarray: 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプの加熱能力(kW)

    """
    return e_hat_HP_cm_hrs_bw_d * P_HP_cm_hrs_bw_d


def get_P_HP_cm_hrs_bw_d(q_HP_sum_std_test, q_HP_win_std_test, A_p, B_p, theta_hat_bw_cm_d, theta_ex_ave_hrs_bw_d,
                         theta_star_bw_std, theta_star_ex_sum, P_HP_sum_std_test):
    """日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプの消費電力(kW) (14)

    Args:
      q_HP_sum_std_test(float): 試験時の夏期標準加熱条件におけるヒートポンプの加熱能力(kW)
      q_HP_win_std_test(float): 試験時の冬期標準加熱条件におけるヒートポンプの加熱能力(kW)
      A_p(float): ヒートポンプの消費電力を求める回帰式の傾き(kW/℃)
      B_p(float): ヒートポンプの消費電力を求める回帰式の切片(kW)
      theta_hat_bw_cm_d(float): 日付dの沸き上げ熱量に応じる運転における制御モードcmのM1スタンダードモード沸き上げ温度(℃)
      theta_ex_ave_hrs_bw_d(float): 日付dの沸き上げ熱量に応じる運転における沸き上げ時間帯の区分hrs_bwに対する平均外気温度(℃)
      theta_star_bw_std(float): 標準条件の沸き上げ温度(℃)
      theta_star_ex_sum(float): 夏期条件の外気温度(℃)
      P_HP_sum_std_test(float): 試験時の夏期標準加熱条件におけるヒートポンプの消費電力(kW)

    Returns:
      ndarray: 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプの消費電力(kW)

    """
    P_HP_cm_hrs_bw_d = np.zeros(365)

    # (14-1)
    if (q_HP_sum_std_test == q_HP_win_std_test):
        P_HP_cm_hrs_bw_d = A_p * (theta_hat_bw_cm_d - theta_ex_ave_hrs_bw_d) + B_p
    # (14-2)
    else:
        f1 = theta_ex_ave_hrs_bw_d <= 20.0
        f2 = 20.0 < theta_ex_ave_hrs_bw_d

        P_HP_cm_hrs_bw_d[f1] = A_p * (theta_hat_bw_cm_d[f1] - theta_ex_ave_hrs_bw_d[f1]) + B_p

        P_HP_cm_hrs_bw_d[f2] = A_p * ((theta_hat_bw_cm_d[f2] - theta_ex_ave_hrs_bw_d[f2]) - (theta_star_bw_std - theta_star_ex_sum)) + \
                        P_HP_sum_std_test

    return np.clip(P_HP_cm_hrs_bw_d, 0.1, None)


# ============================================================================
# 8.4 除霜効率係数
# ============================================================================

def get_C_def_cm_hrs_bw_d(theta_star_ex_frst_upper, theta_ex_ave_hrs_bw_d, theta_star_ex_frst, theta_star_ex_frst_imd,
                          theta_star_ex_win_cd, C_def_frst_cm, C_def_win_cd_cm):
    """日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する除霜効率係数(-) (15)

    Args:
      theta_star_ex_frst_upper(float): 着霜領域（上限）の外気温度(℃)
      theta_ex_ave_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における沸き上げ時間帯の区分hrs_bwに対する平均外気温度(℃)
      theta_star_ex_frst(float): 着霜期条件の外気温度(℃)
      theta_star_ex_frst_imd(float): 着霜領域（中間）の外気温度(℃)
      theta_star_ex_win_cd(float): 寒冷地冬期条件の外気温度(℃)
      C_def_frst_cm(float): 着霜期条件における除霜効率係数(-)
      C_def_win_cd_cm(float): 寒冷地冬期条件における除霜効率係数(-)

    Returns:
      ndarray: 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する除霜効率係数(-)

    """
    get_C_def_cm_d = np.ones(365)

    f1 = theta_star_ex_frst_upper < theta_ex_ave_hrs_bw_d
    get_C_def_cm_d[f1] = 1.0

    f2 = np.logical_and(theta_star_ex_frst < theta_ex_ave_hrs_bw_d, theta_ex_ave_hrs_bw_d <= theta_star_ex_frst_upper)
    get_C_def_cm_d[f2] = np.minimum(1.0, C_def_frst_cm + (theta_ex_ave_hrs_bw_d[f2] - theta_star_ex_frst) /
                                (theta_star_ex_frst_upper - theta_star_ex_frst) * (1.0 - C_def_frst_cm))

    f3 = np.logical_and(theta_star_ex_frst_imd < theta_ex_ave_hrs_bw_d, theta_ex_ave_hrs_bw_d <= theta_star_ex_frst)
    get_C_def_cm_d[f3] = np.minimum(1.0, C_def_frst_cm)

    f4 = theta_ex_ave_hrs_bw_d <= theta_star_ex_frst_imd
    get_C_def_cm_d[f4] = np.minimum(1.0, C_def_win_cd_cm + (theta_ex_ave_hrs_bw_d[f4] - theta_star_ex_win_cd) /
                                (theta_star_ex_frst_imd - theta_star_ex_win_cd) * (C_def_frst_cm - C_def_win_cd_cm))

    return get_C_def_cm_d


def get_C_def_frst_cm(theta_hat_bw_frst_cm, theta_bw_frst_high_test, C_def_frst_test):
    """制御モードcmの着霜期条件における除霜効率係数(-)(15a)

    Args:
      theta_hat_bw_frst_cm(float): 制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度
      theta_bw_frst_high_test(float): 試験時の着霜期高温加熱条件における沸き上げ温度
      C_def_frst_test(float): 試験時の着霜期高温条件における除霜効率係数

    Returns:
      float: 試験時の着霜期高温条件における除霜効率係数

    """
    return 0.0024 * (theta_hat_bw_frst_cm - theta_bw_frst_high_test) + C_def_frst_test


def get_C_def_win_cd_cm(theta_hat_bw_win_cd_cm, theta_bw_frst_high_test, theta_star_ex_win_cd, theta_star_ex_frst_imd, C_def_frst_test):
    """制御モードcmの寒冷地冬期条件における除霜効率係数(-)(15b)

    Args:
      theta_hat_bw_win_cd_cm(float): 制御モードcmの寒冷地冬期条件におけるM1スタンダードモード沸き上げ温度
      theta_bw_frst_high_test(float): 試験時の着霜期高温加熱条件における沸き上げ温度
      theta_star_ex_win_cd(float): 寒冷地冬期条件の外気温度
      theta_star_ex_frst_imd(float): 着霜領域（中間）の外気温度
      C_def_frst_test(float): 試験時の着霜期高温条件における除霜効率係数

    Returns:
      float: 試験時の着霜期高温条件における除霜効率係数

    """
    return 0.0024 * (theta_hat_bw_win_cd_cm - theta_bw_frst_high_test) + \
           (-0.01 * (theta_star_ex_win_cd - theta_star_ex_frst_imd) + C_def_frst_test)


def get_C_def_frst_test(e_HP_def_high_test, e_HP_frst_high_test):
    """試験時の着霜期高温条件における除霜効率係数(-)(16)

    Args:
      e_HP_def_high_test(float): 試験時の着霜期高温加熱条件におけるヒートポンプの除霜運転を含むエネルギー消費効率
      e_HP_frst_high_test(float): 試験時の着霜期高温加熱条件におけるヒートポンプの除霜運転を除くエネルギー消費効率

    Returns:
      float: 試験時の着霜期高温条件における除霜効率係数

    """
    return e_HP_def_high_test / e_HP_frst_high_test


# ============================================================================
# 8.5 ヒートポンプ運転時間
# ============================================================================

def get_tau_HP_cm_hrs_bw_d_t(etau_HP1_cm_hrs_bw_d_t, etau_HP2_cm_hrs_bw_d_t):
    """日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりのヒートポンプ運転時間(h/h) (18)

    Args:
        etau_HP1_cm_hrs_bw_d_t (ndarray): 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する当該日の沸き上げ熱量に応じるヒートポンプ運転開始からの経過時間数(h/d)
        etau_HP2_cm_hrs_bw_d_t (ndarray): 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する翌日の沸き上げ熱量に応じるヒートポンプ運転開始からの経過時間数(h/d)

    Returns:
        tau_HP_cm_hrs_bw_d_t (ndarray): 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりのヒートポンプ運転時間(h/h)
        tau_HP1_cm_hrs_bw_d_t (ndarray): 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりの当該日の沸き上げ熱量に応じるヒートポンプ運転時間(h/h)
        tau_HP2_cm_hrs_bw_d_t (ndarray): 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりの翌日の沸き上げ熱量に応じるヒートポンプ運転時間(h/h)

    """
    t = np.tile(np.arange(24), 365)
    cond_t_0 = t == 0

    # 日付dの時刻t-1における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプ運転開始からの経過時間数(h/d)
    etau_HP1_cm_hrs_bw_d_t_1 = np.roll(etau_HP1_cm_hrs_bw_d_t, 1)
    etau_HP2_cm_hrs_bw_d_t_1 = np.roll(etau_HP2_cm_hrs_bw_d_t, 1)

    tau_HP1_cm_hrs_bw_d_t = np.zeros(24 * 365)
    tau_HP1_cm_hrs_bw_d_t[~cond_t_0] = np.maximum(0.0, etau_HP1_cm_hrs_bw_d_t[~cond_t_0] - etau_HP1_cm_hrs_bw_d_t_1[~cond_t_0])
    tau_HP1_cm_hrs_bw_d_t[cond_t_0]  = np.maximum(0.0, etau_HP1_cm_hrs_bw_d_t[cond_t_0]  - etau_HP2_cm_hrs_bw_d_t_1[cond_t_0])

    tau_HP2_cm_hrs_bw_d_t = np.maximum(0.0, etau_HP2_cm_hrs_bw_d_t - etau_HP2_cm_hrs_bw_d_t_1)

    tau_HP_cm_hrs_bw_d_t = tau_HP1_cm_hrs_bw_d_t + tau_HP2_cm_hrs_bw_d_t

    return tau_HP_cm_hrs_bw_d_t, tau_HP1_cm_hrs_bw_d_t, tau_HP2_cm_hrs_bw_d_t


def get_etau_HP_cm_hrs_bw_d_t(t_HP_stop_cm_hrs_bw_d, t_HP_start_cm_hrs_bw_d, tau_HP_start_cm_hrs_bw_d, tau_dot_HP_cm_hrs_bw_d):
    """日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプ運転開始からの経過時間数(h/d) (19)

    Args:
        t_HP_stop_cm_hrs_bw_d (ndarray): 日付dにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する沸き上げ終了時刻(-)
        t_HP_start_cm_hrs_bw_d (ndarray): 日付dにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する沸き上げ開始時刻(-)
        tau_HP_start_cm_hrs_bw_d (ndarray): 日付dにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する開始時刻における1時間当たりのヒートポンプ運転時間数(h/h)
        tau_dot_HP_cm_hrs_bw_d (ndarray): 日付dにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりのヒートポンプ運転時間数(h/d)

    Returns:
        etau_HP1_cm_hrs_bw_d_t (ndarray): 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する当該日の沸き上げ熱量に応じるヒートポンプ運転開始からの経過時間数(h/d)
        etau_HP2_cm_hrs_bw_d_t (ndarray): 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する翌日の沸き上げ熱量に応じるヒートポンプ運転開始からの経過時間数(h/d)

    """
    etau_HP1_cm_hrs_bw_d_t = np.zeros(24 * 365)
    etau_HP2_cm_hrs_bw_d_t = np.zeros(24 * 365)

    # 1日後
    t_HP_start_cm_hrs_bw_d_1 = np.roll(t_HP_start_cm_hrs_bw_d, -1)
    tau_HP_start_cm_hrs_bw_d_1 = np.roll(tau_HP_start_cm_hrs_bw_d, -1)
    tau_dot_HP_cm_hrs_bw_d_1 = np.roll(tau_dot_HP_cm_hrs_bw_d, -1)

    # 24時間化
    t_HP_stop_cm_hrs_bw_d_t = np.repeat(t_HP_stop_cm_hrs_bw_d, 24)
    t_HP_start_cm_hrs_bw_d_t = np.repeat(t_HP_start_cm_hrs_bw_d, 24)
    t_HP_start_cm_hrs_bw_d_1_t = np.repeat(t_HP_start_cm_hrs_bw_d_1, 24)
    tau_HP_start_cm_hrs_bw_d_t = np.repeat(tau_HP_start_cm_hrs_bw_d, 24)
    tau_HP_start_cm_hrs_bw_d_1_t = np.repeat(tau_HP_start_cm_hrs_bw_d_1, 24)
    tau_dot_HP_cm_hrs_bw_d_t = np.repeat(tau_dot_HP_cm_hrs_bw_d, 24)
    tau_dot_HP_cm_hrs_bw_d_1_t = np.repeat(tau_dot_HP_cm_hrs_bw_d_1, 24)
    t = np.tile(np.arange(24), 365)

    # tau_dot_HP_cm_hrs_bw_d_t == 0 の場合 # (19a-1)
    f1 = tau_dot_HP_cm_hrs_bw_d_t == 0.0
    etau_HP1_cm_hrs_bw_d_t[f1] = 0.0

    f2 = tau_dot_HP_cm_hrs_bw_d_t > 0.0

    # 0 <= t_HP_start_cm_hrs_bw_d_t の場合(沸き上げ開始と沸き上げ終了が同日に行われる場合)
    cond_t_HP1_start_hrs_bw_d1 = 0.0 <= t_HP_start_cm_hrs_bw_d_t

    f3 = np.logical_and(f2, cond_t_HP1_start_hrs_bw_d1)

    # 0 <= t < t_HP_start_cm_hrs_bw_d_t または t_HP_stop_cm_hrs_bw_d_t <= t < 24 の場合 # (19a-2)
    cond_t_HP1_start1 = np.logical_and(0.0 <= t, t < t_HP_start_cm_hrs_bw_d_t)
    cond_t_HP1_stop1  = np.logical_and(t_HP_stop_cm_hrs_bw_d_t <= t, t < 24)
    cond_t_HP1_1 = np.logical_or(cond_t_HP1_start1, cond_t_HP1_stop1)

    f4 = np.logical_and(f3, cond_t_HP1_1)
    etau_HP1_cm_hrs_bw_d_t[f4] = 0.0

    # t_HP_start_cm_hrs_bw_d_t <= t < t_HP_stop_cm_hrs_bw_d_t の場合 # (19a-3)
    cond_t_HP1_2 = np.logical_and(t_HP_start_cm_hrs_bw_d_t <= t, t < t_HP_stop_cm_hrs_bw_d_t)

    f5 = np.logical_and(f3, cond_t_HP1_2)
    etau_HP1_cm_hrs_bw_d_t[f5] = np.minimum(tau_HP_start_cm_hrs_bw_d_t[f5] + 1 * (t[f5] - t_HP_start_cm_hrs_bw_d_t[f5]), tau_dot_HP_cm_hrs_bw_d_t[f5])

    # 0 > t_HP_start_cm_hrs_bw_d_t の場合(沸き上げが終了する日の前日に沸き上げが開始する場合)
    cond_t_HP1_start_hrs_bw_next_day2 = 0.0 > t_HP_start_cm_hrs_bw_d_t

    f6 = np.logical_and(f2, cond_t_HP1_start_hrs_bw_next_day2)

    # 0 <= t < t_HP_stop_cm_hrs_bw_d_t の場合 # (19a-4)
    cond_t_HP1_3 = np.logical_and(0.0 <= t, t < t_HP_stop_cm_hrs_bw_d_t)

    f7 = np.logical_and(f6, cond_t_HP1_3)
    etau_HP1_cm_hrs_bw_d_t[f7] = np.minimum(tau_HP_start_cm_hrs_bw_d_t[f7] + 1 * (t[f7] - t_HP_start_cm_hrs_bw_d_t[f7]), tau_dot_HP_cm_hrs_bw_d_t[f7])

    # t_HP_stop_cm_hrs_bw_d_t <= t < 24 の場合 # (19a-5)
    cond_t_HP1_4 = np.logical_and(t_HP_stop_cm_hrs_bw_d_t <= t, t < 24)

    f8 = np.logical_and(f6, cond_t_HP1_4)
    etau_HP1_cm_hrs_bw_d_t[f8] = 0.0

    # tau_dot_HP_cm_hrs_bw_d_1_t == 0 の場合 # (19b-1)
    f9 = tau_dot_HP_cm_hrs_bw_d_1_t == 0.0
    etau_HP2_cm_hrs_bw_d_t[f9] = 0.0

    f10 = tau_dot_HP_cm_hrs_bw_d_1_t > 0.0

    # 0 <= t_HP_start_cm_hrs_bw_d_1_t の場合(沸き上げ開始と沸き上げ終了が同日に行われる場合) # (19b-2)
    cond_t_HP2_1 = 0.0 <= t_HP_start_cm_hrs_bw_d_1_t

    f11 = np.logical_and(f10, cond_t_HP2_1)
    etau_HP2_cm_hrs_bw_d_t[f11] = 0.0

    # 0 > t_HP_start_cm_hrs_bw_d_1_t の場合(沸き上げが終了する日の前日に沸き上げが開始する場合)
    cond_t_HP2_2 = 0.0 > t_HP_start_cm_hrs_bw_d_1_t

    f12 = np.logical_and(f10, cond_t_HP2_2)

    # 0 <= t < t_HP_start_cm_hrs_bw_d_1_t + 24 の場合 # (19b-3)
    cond_t_HP2_3 = np.logical_and(0.0 <= t, t < t_HP_start_cm_hrs_bw_d_1_t + 24)

    f13 = np.logical_and(f12, cond_t_HP2_3)
    etau_HP2_cm_hrs_bw_d_t[f13] = 0.0

    # t_HP_start_cm_hrs_bw_d_1_t + 24 <= t < 24 の場合 # (19b-4)
    cond_t_HP2_4 = np.logical_and(t_HP_start_cm_hrs_bw_d_1_t + 24 <= t, t < 24)

    f14 = np.logical_and(f12, cond_t_HP2_4)
    etau_HP2_cm_hrs_bw_d_t[f14] = np.minimum(tau_HP_start_cm_hrs_bw_d_1_t[f14] + 1 * (t[f14] - (t_HP_start_cm_hrs_bw_d_1_t[f14] + 24)), tau_dot_HP_cm_hrs_bw_d_1_t[f14])

    return etau_HP1_cm_hrs_bw_d_t, etau_HP2_cm_hrs_bw_d_t


def get_tau_HP_start_cm_hrs_bw_d(heating_control_hrs_bw, tau_dot_HP_cm_hrs_bw_d):
    """日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する沸き上げ開始時刻における1時間当たりのヒートポンプ運転時間数(h/h) (20)

    Args:
        heating_control_hrs_bw(str): 沸き上げ時間帯の区分hrs_bwに対する沸き上げ時間帯の制御
        tau_dot_HP_cm_hrs_bw_d(ndarray): 日付dにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりのヒートポンプ運転時間数 (h/d)

    Returns:
        ndarray: 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する沸き上げ開始時刻における1時間当たりのヒートポンプ運転時間数(h/h)

    """
    tau_HP_start_cm_hrs_bw_d = np.zeros(365)

    # tau_dot_HP_cm_hrs_bw_d がゼロの場合は、定義しない
    f1 = tau_dot_HP_cm_hrs_bw_d == 0.0
    tau_HP_start_cm_hrs_bw_d[f1] = np.nan

    f2 = tau_dot_HP_cm_hrs_bw_d != 0.0
    # 沸き上げ時間帯の制御が終了時刻制御である場合 (20-1)
    if heating_control_hrs_bw == '終了時刻制御':
        tmp = tau_dot_HP_cm_hrs_bw_d - np.floor(tau_dot_HP_cm_hrs_bw_d)
        f2_1 = f2 & (tmp == 0.0)
        f2_2 = f2 & (tmp > 0.0)
        tau_HP_start_cm_hrs_bw_d[f2_1] = 1.0
        tau_HP_start_cm_hrs_bw_d[f2_2] = tmp[f2_2]

    # 沸き上げ時間帯の制御が中心時刻制御である場合 (20-2)
    elif heating_control_hrs_bw == '中心時刻制御':
        tmp = (tau_dot_HP_cm_hrs_bw_d - 1.0) / 2 - np.floor((tau_dot_HP_cm_hrs_bw_d - 1.0) / 2)
        f2_1 = f2 & (tmp == 0.0)
        f2_2 = f2 & (tmp > 0.0)
        tau_HP_start_cm_hrs_bw_d[f2_1] = 1.0
        tau_HP_start_cm_hrs_bw_d[f2_2] = tmp[f2_2]

    # 沸き上げ時間帯の制御が開始時刻制御である場合 (20-3)
    elif heating_control_hrs_bw == '開始時刻制御':
        f2_1 = f2 & (tau_dot_HP_cm_hrs_bw_d >= 1.0)
        f2_2 = f2 & (tau_dot_HP_cm_hrs_bw_d < 1.0)
        tau_HP_start_cm_hrs_bw_d[f2_1] = 1.0
        tau_HP_start_cm_hrs_bw_d[f2_2] = tau_dot_HP_cm_hrs_bw_d[f2_2]

    return tau_HP_start_cm_hrs_bw_d


def get_t_HP_start_stop_cm_hrs_bw_d(heating_control_hrs_bw, t_HP_ref_hrs_bw, tau_dot_HP_cm_hrs_bw_d):
    """日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する沸き上げ開始／終了時刻(-) (21)(22)

    Args:
        heating_control_hrs_bw(str): 沸き上げ時間帯の区分hrs_bwに対する沸き上げ時間帯の制御
        t_HP_ref_hrs_bw(int): 沸き上げ時間帯の区分hrs_bwに対する沸き上げ時間帯の制御の参照時刻
        tau_dot_HP_cm_hrs_bw_d(ndarray): 日付dにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりのヒートポンプ運転時間数 (h/d)

    Returns:
        t_HP_start_cm_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する沸き上げ開始時刻(-)
        t_HP_stop_cm_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する沸き上げ終了時刻(-)

    """
    t_HP_start_hrs_bw_d = np.zeros(365)
    t_HP_stop_hrs_bw_d = np.zeros(365)

    # tau_dot_HP_cm_hrs_bw_d がゼロの場合は、定義しない
    f1 = tau_dot_HP_cm_hrs_bw_d == 0.0
    t_HP_start_hrs_bw_d[f1] = np.nan
    t_HP_stop_hrs_bw_d[f1]  = np.nan

    f2 = tau_dot_HP_cm_hrs_bw_d != 0.0
    # 沸き上げ時間帯の制御が終了時刻時刻である場合 (21-1)(22-1)
    if heating_control_hrs_bw == '終了時刻制御':
      t_HP_stop_hrs_bw_d[f2]  = t_HP_ref_hrs_bw      
      t_HP_start_hrs_bw_d[f2] = t_HP_stop_hrs_bw_d[f2] - np.ceil(tau_dot_HP_cm_hrs_bw_d[f2])

    # 沸き上げ時間帯の制御が中心時刻時刻である場合 (21-2)(22-2)
    elif heating_control_hrs_bw == '中心時刻制御':
      t_HP_start_hrs_bw_d[f2] = t_HP_ref_hrs_bw - np.ceil((tau_dot_HP_cm_hrs_bw_d[f2] - 1) / 2)
      t_HP_stop_hrs_bw_d[f2]  = t_HP_ref_hrs_bw + np.ceil((tau_dot_HP_cm_hrs_bw_d[f2] - 1) / 2) + 1

    # 沸き上げ時間帯の制御が開始時刻制御である場合 (21-3)(22-3)
    elif heating_control_hrs_bw == '開始時刻制御':
      t_HP_start_hrs_bw_d[f2] = t_HP_ref_hrs_bw      
      t_HP_stop_hrs_bw_d[f2]  = t_HP_start_hrs_bw_d[f2] + np.ceil(tau_dot_HP_cm_hrs_bw_d[f2])

    return t_HP_start_hrs_bw_d, t_HP_stop_hrs_bw_d


def get_tau_dot_HP_cm_hrs_bw_d(Q_dot_HP_cm_hrs_bw_d, q_HP_cm_hrs_bw_d, tau_dot_HP_max_hrs_bw):
    """日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりのヒートポンプ運転時間数 (h/d) (23)

    Args:
      Q_dot_HP_cm_hrs_bw_d(ndarray): 日付dにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの沸き上げ熱量 (MJ/d)
      q_HP_cm_hrs_bw_d(ndarray): 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対するヒートポンプの加熱能力 (kW)
      tau_dot_HP_max_hrs_bw(float): 沸き上げ時間帯の区分hrs_bwに対する1日当たりのヒートポンプ運転時間数の上限 (h/d)

    Returns:
      ndarray: 日付dの沸き上げ熱量に応じる運転における制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりのヒートポンプ運転時間数 (h/d)

    """
    return np.minimum(tau_dot_HP_max_hrs_bw, (Q_dot_HP_cm_hrs_bw_d * 1000) / (q_HP_cm_hrs_bw_d * 3600))


# ============================================================================
# 9. 貯湯タンク
# ============================================================================

# ============================================================================
# 9.1 沸き上げ熱量
# ============================================================================

def get_Q_dot_HP_cm_hrs_bw_d(hrs_bw, Q_dot_HP_cm_d, R_Q_dot_HP_day_cm):
    """日付dにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの沸き上げ熱量(MJ/d) (24)

    Args:
        hrs_bw(str): 沸き上げ時間帯の区分
        Q_dot_HP_cm_d(ndarray): 日付dにおける制御モードcmの1日当たりの沸き上げ熱量(MJ/d)
        R_Q_dot_HP_day_cm(float): 制御モードcmの1日当たりの沸き上げ熱量に対する昼間の沸き上げ熱量（-）

    Returns:
        ndarray: 日付dにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1日当たりの沸き上げ熱量(MJ/d)

    """
    # 沸き上げ時間帯の区分が夜間の場合 (24-1)
    if hrs_bw == 'night':
        return Q_dot_HP_cm_d * (1.0 - R_Q_dot_HP_day_cm)

    # 沸き上げ時間帯の区分が昼間の場合 (24-2)
    elif hrs_bw == 'day':
        return Q_dot_HP_cm_d * R_Q_dot_HP_day_cm

    else:
        raise ValueError(hrs_bw)


def get_Q_dot_HP_cm_d(L_dashdash_d, Q_dot_loss_cm_d):
    """日付dにおける制御モードcmの1日当たりの沸き上げ熱量(MJ/d)(25)

    Args:
      L_dashdash_d(ndarray): 日付dにおける1日当たりの太陽熱補正給湯熱負荷
      Q_dot_loss_cm_d(ndarray): 日付dにおける制御モードcmの1日当たりの貯湯熱損失量

    Returns:
      ndarray: 日付dにおける制御モードcmの1日当たりの沸き上げ熱量(MJ/d)

    """
    return L_dashdash_d + Q_dot_loss_cm_d


# ============================================================================
# 9.2 貯湯損失熱量
# ============================================================================

def get_Q_dot_loss_cm_d(theta_tnk_eq_cm_d, theta_ex_d_Ave_d, R_tnk_test):
    """日付dにおける制御モードcmの1日当たりの貯湯熱損失量(MJ/d)(26)

    Args:
      theta_tnk_eq_cm_d(ndarray): 日付dにおける制御モードcmの等価貯湯温度
      theta_ex_d_Ave_d(ndarray): 日付dにおける日平均外気温度
      R_tnk_test(float): 貯湯タンク総括熱抵抗

    Returns:
      ndarray: 日付dにおける制御モードcmの1日当たりの貯湯熱損失量

    """
    return (theta_tnk_eq_cm_d - theta_ex_d_Ave_d) / R_tnk_test * 3600 * 24 * 10 ** (-6)


# ============================================================================
# 9.3 等価貯湯温度
# ============================================================================

def get_theta_tnk_eq_cm1_d(theta_ex_d_Ave_d, theta_star_ex_frst, theta_star_ex_frst_upper, theta_tnk_eq_win,
                           theta_tnk_eq_frst, theta_tnk_eq_frst_upper):
    """日付dにおける制御モードcmの等価貯湯温度（℃）(27-1)

    Args:
      theta_ex_d_Ave_d(ndarray): 日付dにおける日平均外気温度
      theta_star_ex_frst(float): 着霜期条件の外気温度
      theta_star_ex_frst_upper(float): 着霜領域（上限）の外気温度
      theta_tnk_eq_win(float): 冬期条件における等価貯湯温度
      theta_tnk_eq_frst(float): 着霜期条件における等価貯湯温度
      theta_tnk_eq_frst_upper(float): 着霜領域（上限）における等価貯湯温度

    Returns:
      ndarray: 日付dにおける制御モードcmの等価貯湯温度

    """
    theta_tnk_eq_cm1_d = np.zeros(365)

    f1 = theta_star_ex_frst_upper < theta_ex_d_Ave_d
    f2 = np.logical_and(theta_star_ex_frst < theta_ex_d_Ave_d, theta_ex_d_Ave_d <= theta_star_ex_frst_upper)
    f3 = theta_ex_d_Ave_d <= theta_star_ex_frst

    theta_tnk_eq_cm1_d[f1] = theta_tnk_eq_win + (-0.4 * theta_ex_d_Ave_d[f1] + 8.5)

    theta_tnk_eq_cm1_d[f2] = theta_tnk_eq_frst + (theta_ex_d_Ave_d[f2] - theta_star_ex_frst) / \
                             (theta_star_ex_frst_upper - theta_star_ex_frst) * (theta_tnk_eq_frst_upper - theta_tnk_eq_frst)

    theta_tnk_eq_cm1_d[f3] = -0.4 * (theta_ex_d_Ave_d[f3] - theta_star_ex_frst) + theta_tnk_eq_frst

    return np.clip(theta_tnk_eq_cm1_d, theta_ex_d_Ave_d, None)


def get_theta_tnk_eq_cm2_d(theta_ex_d_Ave_d, theta_tnk_eq_cm1_d, theta_hat_bw_cm1_d, theta_hat_bw_cm2_d):
    """日付dにおける制御モードcmの等価貯湯温度（℃）(27-2)

    Args:
      theta_ex_d_Ave_d(ndarray): 日付dにおける日平均外気温度
      theta_tnk_eq_cm1_d(ndarray): 日付dにおけるファーストモードcmの等価貯湯温度
      theta_hat_bw_cm1_d(ndarray): 日付dの沸き上げ熱量に応じる運転におけるファーストモードのM1スタンダードモード沸き上げ温度
      theta_hat_bw_cm2_d(ndarray): 日付dの沸き上げ熱量に応じる運転におけるセカンドモードのM1スタンダードモード沸き上げ温度

    Returns:
      ndarray: 日付dにおける制御モードcmの等価貯湯温度

    """
    theta_tnk_eq_cm2_d = (theta_tnk_eq_cm1_d - theta_ex_d_Ave_d) * \
                         (2.1 * ((theta_hat_bw_cm2_d - theta_ex_d_Ave_d) / (theta_hat_bw_cm1_d - theta_ex_d_Ave_d)) - 1.2) + theta_ex_d_Ave_d

    return np.clip(theta_tnk_eq_cm2_d, theta_ex_d_Ave_d, None)


def get_theta_tnk_eq(theta_tnk_eq_test):
    """冬期条件、着霜期条件および着霜領域（上限）における等価貯湯温度(28)

    Args:
      theta_tnk_eq_test(float): 試験時の等価貯湯温度

    Returns:
      tuple: 冬期条件、着霜期条件および着霜領域（上限）における等価貯湯温度

    """
    # 冬期条件における等価貯湯温度(28a)
    theta_tnk_eq_win = theta_tnk_eq_test

    # 着霜期条件における等価貯湯温度(28b)
    theta_tnk_eq_frst = theta_tnk_eq_test + 23.0

    # 着霜領域（上限）における等価貯湯温度(28c)
    theta_tnk_eq_frst_upper = theta_tnk_eq_test + 6.5

    return theta_tnk_eq_win, theta_tnk_eq_frst, theta_tnk_eq_frst_upper


def get_theta_tnk_eq_test(Q_loss_test, R_tnk_test, theta_star_ex_win):
    """試験時の等価貯湯温度(℃)(29)

    Args:
      Q_loss_test(float): 試験時の貯湯熱損失量
      R_tnk_test(float): 貯湯タンク総括熱抵抗
      theta_star_ex_win(float): 冬期条件の外気温度

    Returns:
      float: 試験時の等価貯湯温度

    """
    return Q_loss_test * (10 ** 6 / (3600 * 24)) * R_tnk_test + theta_star_ex_win

# ============================================================================
# 10. 補機
# ============================================================================

# ============================================================================
# 10.1 消費電力量
# ============================================================================

def get_E_E_aux_cm_d_t(P_aux_HP_on_test, P_aux_HP_off_test, tau_HP_cm_hrs_bw_d_t_dic):
    """日付dの時刻tにおける制御モードcmの1日当たりの補機の消費電力量(30)

    Args:
      P_aux_HP_on_test: 試験時のヒートポンプ停止時における補機の消費電力 (W)
      P_aux_HP_off_test: 試験時のヒートポンプ運転時における補機の消費電力 (W)
      tau_HP_cm_hrs_bw_d_t_dic: 日付dの時刻tにおける制御モードcmの沸き上げ時間帯の区分hrs_bwに対する1時間当たりのヒートポンプ運転時間数 (h/h)

    Returns:
      ndarray: 日付dの時刻tにおける制御モードcmの1日当たりの補機の消費電力量

    """
    tau_HP_cm_hrs_bw_d_t_night = tau_HP_cm_hrs_bw_d_t_dic['night']
    tau_HP_cm_hrs_bw_d_t_day = tau_HP_cm_hrs_bw_d_t_dic['day']

    tmp = tau_HP_cm_hrs_bw_d_t_night + tau_HP_cm_hrs_bw_d_t_day

    return (P_aux_HP_on_test * tmp + P_aux_HP_off_test * (1.0 - tmp)) / 1000


# ============================================================================
# 11. 制御
# ============================================================================

# ============================================================================
# 11.1 制御モード
# ============================================================================

# 表4 沸き上げ温度条件の種類
# 1st:ファーストモード
# 2st:セカンドモード


# ============================================================================
# 11.2 沸き上げ温度
# ============================================================================

def get_theta_hat_bw_cm_d(theta_star_ex_imd, theta_star_ex_win, theta_star_ex_frst, theta_star_ex_win_cd,
                          theta_star_ex_frst_upper, theta_ex_d_t, theta_hat_bw_sum_cm, theta_hat_bw_imd_cm,
                          theta_hat_bw_win_cm, theta_hat_bw_frst_cm, theta_hat_bw_win_cd_cm):
    """日付dの沸き上げ熱量に応じる運転における制御モードcmのM1スタンダードモード沸き上げ温度（℃）(31)

    Args:
      theta_star_ex_imd(float): 中間期条件の外気温度
      theta_star_ex_win(float): 冬期条件の外気温度
      theta_star_ex_frst(float): 着霜期条件の外気温度
      theta_star_ex_win_cd(float): 寒冷地冬期条件の外気温度
      theta_star_ex_frst_upper(float): 着霜領域（上限）の外気温度
      theta_ex_d_t(ndarray): 日付dの時刻tにおける外気温度
      theta_hat_bw_sum_cm(float): 制御モードcmの夏期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_imd_cm(float): 制御モードcmの中間期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cm(float): 制御モードcmの冬期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_frst_cm(float): 制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cd_cm(float): 制御モードcmの寒冷地冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      ndarray: 日付dの沸き上げ熱量に応じる運転における制御モードcmのM1スタンダードモード沸き上げ温度

    """
    # 日付dの沸き上げ熱量に応じる運転における夜間沸き上げ時間帯の区分hrs_bwに対する平均外気温度 (hrs_bw == night の場合)
    theta_ex_ave_night_d = get_theta_ex_ave_hrs_bw_d(hrs_bw='night', theta_ex_d_t=theta_ex_d_t)

    theta_hat_bw_cm_d = np.zeros(365)

    f1 = theta_star_ex_imd < theta_ex_ave_night_d
    f2 = np.logical_and(theta_star_ex_win < theta_ex_ave_night_d, theta_ex_ave_night_d <= theta_star_ex_imd)
    f3 = np.logical_and(theta_star_ex_frst_upper < theta_ex_ave_night_d, theta_ex_ave_night_d <= theta_star_ex_win)
    f4 = np.logical_and(theta_star_ex_frst < theta_ex_ave_night_d, theta_ex_ave_night_d <= theta_star_ex_frst_upper)
    f5 = np.logical_and(theta_star_ex_win_cd < theta_ex_ave_night_d, theta_ex_ave_night_d <= theta_star_ex_frst)
    f6 = theta_ex_ave_night_d <= theta_star_ex_win_cd

    theta_hat_bw_cm_d[f1] = theta_hat_bw_sum_cm

    theta_hat_bw_cm_d[f2] = theta_hat_bw_sum_cm + (theta_ex_ave_night_d[f2] - theta_star_ex_imd) / (theta_star_ex_imd - theta_star_ex_win) * (theta_hat_bw_imd_cm - theta_hat_bw_win_cm)

    theta_hat_bw_cm_d[f3] = theta_hat_bw_win_cm

    theta_hat_bw_cm_d[f4] = theta_hat_bw_frst_cm + (theta_ex_ave_night_d[f4] - theta_star_ex_frst) / (theta_star_ex_frst_upper - theta_star_ex_frst) * (theta_hat_bw_win_cm - theta_hat_bw_frst_cm)

    theta_hat_bw_cm_d[f5] = theta_hat_bw_frst_cm + (theta_ex_ave_night_d[f5] - theta_star_ex_frst) / (theta_star_ex_frst - theta_star_ex_win_cd) * (theta_hat_bw_frst_cm - theta_hat_bw_win_cd_cm)

    theta_hat_bw_cm_d[f6] = theta_hat_bw_win_cd_cm

    return theta_hat_bw_cm_d


def get_theta_hat_bw_sum_cm1(theta_star_bw_std):
    """制御モードcmの夏期条件におけるM1スタンダードモード沸き上げ温度（℃）(32a-1)

    Args:
      theta_star_bw_std(float): 標準条件の沸き上げ温度（

    Returns:
      float: 制御モードcmの夏期条件におけるM1スタンダードモード沸き上げ温度（

    """
    # 制御モードがファーストモードの場合
    return theta_star_bw_std


def get_theta_hat_bw_imd_cm1(theta_star_bw_std):
    """制御モードcmの中間条件におけるM1スタンダードモード沸き上げ温度（℃）(32b-1)

    Args:
      theta_star_bw_std(float): 標準条件の沸き上げ温度（

    Returns:
      float: 制御モードcmの中間条件におけるM1スタンダードモード沸き上げ温度（

    """
    # 制御モードがファーストモードの場合
    return theta_star_bw_std


def get_theta_hat_bw_win_cm1(theta_star_bw_std, theta_hat_bw_win_cm1_test):
    """制御モードcmの冬期条件におけるM1スタンダードモード沸き上げ温度（℃）(32c-1)

    Args:
      theta_star_bw_std(float): 標準条件の沸き上げ温度（
      theta_hat_bw_win_cm1_test(float): 試験時の制御モードがファーストモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      float: 制御モードcmの冬期条件におけるM1スタンダードモード沸き上げ温度（

    """
    # 制御モードがファーストモードの場合
    return np.maximum(theta_star_bw_std, theta_hat_bw_win_cm1_test)


def get_theta_hat_bw_frst_cm1(theta_star_bw_high, theta_hat_bw_win_cm1):
    """制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度（℃）(32d-1)

    Args:
      theta_star_bw_high(float): 高温条件の沸き上げ温度（
      theta_hat_bw_win_cm1(float): 制御モードがファーストモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      float: 制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度

    """
    # 制御モードがファーストモードの場合
    return np.minimum(theta_star_bw_high, theta_hat_bw_win_cm1 + 6.0)


def get_theta_hat_bw_win_cd_cm1(theta_star_bw_high, theta_hat_bw_win_cm1):
    """制御モードcmの寒冷地冬期条件におけるM1スタンダードモード沸き上げ温度（℃）(32e-1)

    Args:
      theta_star_bw_high(float): 高温条件の沸き上げ温度（
      theta_hat_bw_win_cm1: returns: 制御モードcmの寒冷地冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      float: 制御モードcmの寒冷地冬期条件におけるM1スタンダードモード沸き上げ温度

    """
    # 制御モードがファーストモードの場合
    return np.minimum(theta_star_bw_high, theta_hat_bw_win_cm1 + 8.0)


def get_theta_hat_bw_sum_cm2(theta_hat_bw_sum_cm1, theta_hat_bw_win_cm1, theta_hat_bw_win_cm2):
    """制御モードcmの夏期条件におけるM1スタンダードモード沸き上げ温度（℃）(32a-2)

    Args:
      theta_hat_bw_sum_cm1(float): 制御モードがファーストモードの場合の夏期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cm1(float): 制御モードがファーストモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cm2(float): 制御モードがセカンドモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      float: 制御モードcmの寒冷地冬期条件におけるM1スタンダードモード沸き上げ温度

    """
    # 制御モードがセカンドモードの場合
    return theta_hat_bw_sum_cm1 + (theta_hat_bw_win_cm2 - theta_hat_bw_win_cm1)


def get_theta_hat_bw_imd_cm2(theta_hat_bw_imd_cm1, theta_hat_bw_win_cm1, theta_hat_bw_win_cm2):
    """制御モードcmの中間期条件におけるM1スタンダードモード沸き上げ温度（℃）(32b-2)

    Args:
      theta_hat_bw_imd_cm1(float): 制御モードがファーストモードの場合の中間期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cm1(float): 制御モードがファーストモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cm2(float): 制御モードがセカンドモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      float: 制御モードcmの寒冷地冬期条件におけるM1スタンダードモード沸き上げ温度

    """
    # 制御モードがセカンドモードの場合
    return theta_hat_bw_imd_cm1 + (theta_hat_bw_win_cm2 - theta_hat_bw_win_cm1)


def get_theta_hat_bw_win_cm2(theta_hat_bw_win_cm1, theta_hat_bw_win_cm1_test, theta_hat_bw_win_cm2_test):
    """制御モードcmの冬期条件におけるM1スタンダードモード沸き上げ温度（℃）(32c-2)

    Args:
      theta_hat_bw_win_cm1(float): 制御モードがファーストモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cm1_test(float): 試験時の制御モードがファーストモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cm2_test(float): 試験時の制御モードがセカンドモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      float: 制御モードcmの冬期条件におけるM1スタンダードモード沸き上げ温度（

    """
    # 試験時のファーストモードの冬期条件におけるM1スタンダードモード沸き上げ温度とセカンドモードの冬期条件におけるM1スタンダードモード沸き上げ温度の差の最小値
    delta_theta_hat_star_bw_win_test = get_delta_theta_hat_star_bw_win_test()

    # 制御モードがセカンドモードの場合
    return theta_hat_bw_win_cm1 + np.maximum(delta_theta_hat_star_bw_win_test, theta_hat_bw_win_cm2_test - theta_hat_bw_win_cm1_test)


def get_theta_hat_bw_frst_cm2(theta_star_bw_high, theta_hat_bw_frst_cm1, theta_hat_bw_win_cm1, theta_hat_bw_win_cm2):
    """制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度（℃）(32d-2)

    Args:
      theta_star_bw_high(float): 高温条件の沸き上げ温度（
      theta_hat_bw_frst_cm1(float): 制御モードがファーストモードの場合の着霜期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cm1(float): 制御モードがファーストモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cm2(float): 制御モードがセカンドモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      float: 制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度

    """
    # 制御モードがセカンドモードの場合
    return np.minimum(theta_star_bw_high, theta_hat_bw_frst_cm1 + (theta_hat_bw_win_cm2 - theta_hat_bw_win_cm1))


def get_theta_hat_bw_win_cd_cm2(theta_star_bw_high, theta_hat_bw_win_cd_cm1, theta_hat_bw_win_cm1, theta_hat_bw_win_cm2):
    """制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度（℃）(32e-2)

    Args:
      theta_star_bw_high(float): 高温条件の沸き上げ温度（
      theta_hat_bw_win_cd_cm1(float): 制御モードがファーストモードの場合の寒冷地冬期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cm1(float): 制御モードがファーストモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cm2(float): 制御モードがセカンドモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      float: 制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度

    """
    # 制御モードがセカンドモードの場合
    return np.minimum(theta_star_bw_high, theta_hat_bw_win_cd_cm1 + (theta_hat_bw_win_cm2 - theta_hat_bw_win_cm1))


def get_delta_theta_hat_star_bw_win_test():
    """試験時のファーストモードの冬期条件におけるM1スタンダードモード沸き上げ温度とセカンドモードの冬期条件におけるM1スタンダードモード沸き上げ温度の差の最小値（℃）

    Args:

    Returns:
      float: 試験時のファーストモードの冬期条件におけるM1スタンダードモード沸き上げ温度とセカンドモードの冬期条件におけるM1スタンダードモード沸き上げ温度の差の最小値

    """
    return 5.0


def get_theta_star_bw():
    """表5 沸き上げ温度条件の種類

    Args:

    Returns:
      list: 沸き上げ温度条件の種類

    """
    # 表5 沸き上げ温度条件の種類
    table_5 = [
        65,  # 標準条件沸き上げ温度(℃)
        90  # 高温条件沸き上げ温度(℃)
    ]

    return table_5


# ============================================================================
# 11.3 沸き上げ時間帯・沸き上げ時間帯の制御の参照時刻・ヒートポンプ運転時間数の上限
# ============================================================================

def get_table_6():
    """表 6 沸き上げ時間帯の種類

    Args:

    Returns:
      list: 沸き上げ時間帯の種類

    """
    table6 = [
        'night',    #夜間
        'day'       #昼間
    ]
    return table6


def get_heating_control_hrs_bw(hrs_bw, daytime_heating_control):
    """沸き上げ時間帯の区分hrs_bwに対する沸き上げ時間帯の制御

    Args:
        hrs_bw(str): 沸き上げ時間帯の区分
        daytime_heating_control(str): 昼間沸き上げ時間帯の制御

    Returns:
        str: 沸き上げ時間帯の区分hrs_bwに対する沸き上げ時間帯の制御

    """
    # 沸き上げ時間帯の区分が夜間の場合、終了時刻制御のみとする。
    if hrs_bw == 'night':
      return "終了時刻制御"

    # 沸き上げ時間帯の区分が昼間の場合、終了時刻制御、開始時刻制御および中心時刻制御のいずれかとする。
    elif hrs_bw == 'day':
      return daytime_heating_control

    else:
      raise ValueError(hrs_bw)


def get_t_HP_ref_hrs_bw(hrs_bw, heating_control_hrs_bw):
    """沸き上げ時間帯の区分hrs_bwに対する沸き上げ時間帯の制御の参照時刻

    Args:
        hrs_bw(str): 沸き上げ時間帯の区分
        heating_control_hrs_bw(str): 沸き上げ時間帯の区分hrs_bwに対する沸き上げ時間帯の制御

    Returns:
        int: 沸き上げ時間帯の区分hrs_bwに対する沸き上げ時間帯の制御の参照時刻

    """
    # 沸き上げ時間帯の区分が夜間であって沸き上げ時間帯の制御が終了時刻制御である場合には7時とする。
    # 沸き上げ時間帯の区分が昼間であって沸き上げ時間帯の制御が終了時刻制御である場合には16時、開始時刻制御である場合には9時、中心時刻制御である場合には12時とする。
    return {
      ('night', '終了時刻制御'): 7,
      ('day',   '終了時刻制御'): 16,
      ('day',   '開始時刻制御'): 9,
      ('day',   '中心時刻制御'): 12,
    }.get((hrs_bw, heating_control_hrs_bw))


def get_tau_dot_HP_max_hrs_bw(hrs_bw, R_Q_dot_HP_day_cm):
    """沸き上げ時間帯に対する1日当たりのヒートポンプ運転時間数の上限(h/d) (33)

    Args:
        hrs_bw(str): 沸き上げ時間帯の区分
        R_Q_dot_HP_day_cm(float): 制御モードcmの1日当たりの沸き上げ熱量に対する昼間の沸き上げ熱量（-）

    Returns:
        沸き上げ時間帯に対する1日当たりのヒートポンプ運転時間数の上限(h/d)

    """
    # 沸き上げ時間帯が夜間の場合
    if hrs_bw == 'night':
      # (33-1)
      if R_Q_dot_HP_day_cm == 0.0:
        return 24.0
      elif R_Q_dot_HP_day_cm != 0.0:
        return 15.0
    # 沸き上げ時間帯が昼間の場合
    elif hrs_bw == 'day':
      # (33-2)
      if R_Q_dot_HP_day_cm == 0.0:
        return 0.0
      elif R_Q_dot_HP_day_cm != 0.0:
        return 7.0


# ============================================================================
# 11.4 1日当たりの沸き上げ熱量に対する昼間の沸き上げ熱量の比
# ============================================================================

def get_R_Q_dot_HP_day_cm1(R_E_day):
    """制御モードcmの1日当たりの沸き上げ熱量に対する昼間の沸き上げ熱量（-） (34-1)(34-2)

    Args:
        R_E_day (float): 昼間消費電力量比率 (%)

    Returns:
        float: 制御モードcmの1日当たりの沸き上げ熱量に対する昼間の沸き上げ熱量（-）

    """
    if R_E_day == 0.0:
      return 0.00
    # 制御モードがファーストモードの場合
    else:
      return max(R_E_day / 100.0 - 0.05, 0.50)


def get_R_Q_dot_HP_day_cm2(R_E_day):
    """制御モードcmの1日当たりの沸き上げ熱量に対する昼間の沸き上げ熱量（-） (34-1)(34-3)

    Args:
        R_E_day (float): 昼間消費電力量比率 (%)

    Returns:
        float: 制御モードcmの1日当たりの沸き上げ熱量に対する昼間の沸き上げ熱量（-）

    """
    if R_E_day == 0.0:
      return 0.00
    # 制御モードがセカンドモードの場合
    else:
      return 0.50


# ============================================================================
# 12. 給湯機の仕様
# ============================================================================

def get_spec(e_rtd):
    """

    Args:
      e_rtd(float): 当該給湯器の効率

    Returns:
      dict: 給湯機の仕様

    """
    spec = []

    table_7_b = get_table_7_b()

    if (e_rtd <= 2.7):
        spec = table_7_b[0]
    elif (e_rtd == 2.8):
        spec = table_7_b[1]
    elif (e_rtd == 2.9):
        spec = table_7_b[2]
    elif (e_rtd == 3.0):
        spec = table_7_b[3]
    elif (e_rtd == 3.1):
        spec = table_7_b[4]
    elif (e_rtd == 3.2):
        spec = table_7_b[5]
    elif (e_rtd == 3.3):
        spec = table_7_b[6]
    elif (e_rtd == 3.4):
        spec = table_7_b[7]
    elif (e_rtd == 3.5):
        spec = table_7_b[8]
    elif (e_rtd >= 3.6):
        spec = table_7_b[9]
    else:
        raise ValueError('e_rtd')

    CO2HP = {
        'P_HP_imd_std_test': spec[0],
        'P_HP_sum_std_test': spec[1],
        'P_HP_win_std_test': spec[2],
        'q_HP_imd_std_test': spec[3],
        'q_HP_sum_std_test': spec[4],
        'q_HP_win_std_test': spec[5],
        'e_HP_def_high_test': spec[6],
        'e_HP_frst_high_test': spec[7],
        'theta_bw_frst_high_test': spec[8],
        'theta_bw_imd_std_test': spec[9],
        'theta_bw_sum_std_test': spec[10],
        'theta_bw_win_std_test': spec[11],
        'A_p': spec[12],
        'B_p': spec[13],
        'P_aux_HP_on_test': spec[14],
        'P_aux_HP_off_test': spec[15],
        'Q_loss_test': spec[16],
        'R_tnk_test': spec[17],
        'theta_hat_bw_win_cm1_test': spec[18],
        'theta_hat_bw_win_cm2_test': spec[19]
    }

    return CO2HP


def get_table_7_b():
    """表7（b） 給湯機の仕様の決定方法（当該給湯機の効率に応じて定まる数値を用いる場合）

    Args:

    Returns:
      list: 表7（b） 給湯機の仕様の決定方法（当該給湯機の効率に応じて定まる数値を用いる場合）

    """
    # 表7（b） 給湯機の仕様の決定方法（当該給湯機の効率に応じて定まる数値を用いる場合）
    table_7_b = [
        (1.175, 1.031, 1.263, 4.5, 4.5, 4.5, 2.37, 2.56, 90, 65, 65, 65, 0.0135, 0.4961, 21, 6, 11.5, 0.3, 69, 76),
        (1.146, 1.005, 1.232, 4.5, 4.5, 4.5, 2.43, 2.62, 90, 65, 65, 65, 0.0132, 0.4827, 21, 6, 11.5, 0.3, 69, 76),
        (1.117, 0.980, 1.201, 4.5, 4.5, 4.5, 2.49, 2.69, 90, 65, 65, 65, 0.0129, 0.4709, 21, 6, 11.5, 0.3, 69, 76),
        (1.088, 0.954, 1.170, 4.5, 4.5, 4.5, 2.56, 2.76, 90, 65, 65, 65, 0.0125, 0.4574, 21, 6, 11.5, 0.3, 69, 76),
        (1.059, 0.929, 1.139, 4.5, 4.5, 4.5, 2.63, 2.84, 90, 65, 65, 65, 0.0122, 0.4456, 21, 6, 11.5, 0.3, 69, 76),
        (1.031, 0.904, 1.109, 4.5, 4.5, 4.5, 2.70, 2.91, 90, 65, 65, 65, 0.0119, 0.4329, 21, 6, 11.5, 0.3, 69, 76),
        (1.002, 0.879, 1.077, 4.5, 4.5, 4.5, 2.78, 3.00, 90, 65, 65, 65, 0.0115, 0.4228, 21, 6, 11.5, 0.3, 69, 76),
        (0.973, 0.854, 1.046, 4.5, 4.5, 4.5, 2.87, 3.09, 90, 65, 65, 65, 0.0112, 0.4110, 21, 6, 11.5, 0.3, 69, 76),
        (0.944, 0.828, 1.015, 4.5, 4.5, 4.5, 2.95, 3.18, 90, 65, 65, 65, 0.0109, 0.3976, 21, 6, 11.5, 0.3, 69, 76),
        (0.915, 0.803, 0.984, 4.5, 4.5, 4.5, 3.04, 3.28, 90, 65, 65, 65, 0.0105, 0.3858, 21, 6, 11.5, 0.3, 69, 76)
    ]

    return table_7_b



def get_e_rtd_default():
    """規定の当該給湯機の効率

    Args:

    Returns:
      float: 規定の当該給湯器の効率

    """
    return 2.7

def get_e_rtd(e_rtd):
    """3.6を超える場合、3.6にする。2.7を下回る場合、2.7にする。


    Returns:
      float: 当該給湯器の効率

    """
    # 3.6を超える場合は3.6に等しいとする
    e_rtd = min(3.6, e_rtd)
    # 2.7を下回る場合は2.7に等しいとする
    e_rtd = max(2.7, e_rtd)

    return e_rtd


def get_R_E_day(daytime_heating, R_E_day_in, daytime_heating_control_in):
    """昼間消費電力量比率 (%)

    Args:
      daytime_heating(bool): 認定機種に該当し、かつ昼間沸上げを評価するかどうか
      R_E_day_in(float): 昼間消費電力量比率（入力値） (%)
      daytime_heating_control_in(str): 昼間沸き上げ時間帯の制御（入力値）

    Returns:
      float: 昼間消費電力量比率 (%)

    """
    # 昼間沸上げを評価する場合、昼間消費電力量比率はJRA4085に規定する方法により得られる値とする。
    # ただし、以下の①、②、もしくは①②の両方に該当する場合は、昼間消費電力量比率は50%とする。
    #   ①昼間消費電力量比率についてJRA4085に規定する方法により得られる値が不明である場合
    #   ②昼間沸上げ時間帯の制御が終了時刻制御、開始時刻制御および中心時刻制御のいずれにも該当しないか不明である場合
    if daytime_heating == True:
        if all(_ is not None for _ in [R_E_day_in, daytime_heating_control_in]):
          return R_E_day_in
        else:
          return 50.0
    # 昼間沸き上げを評価しない場合、昼間消費電力量比率は0%とする。
    else:
        return 0.0


def get_daytime_heating_control(daytime_heating, R_E_day_in, daytime_heating_control_in):
    """昼間沸き上げ時間帯の制御

    Args:
      daytime_heating(bool): 認定機種に該当し、かつ昼間沸上げを評価するかどうか
      R_E_day_in(float): 昼間消費電力量比率（入力値） (%)
      daytime_heating_control_in(str): 昼間沸き上げ時間帯の制御（入力値）

    Returns:
      str: 昼間沸き上げ時間帯の制御

    """
    # 昼間沸上げを評価する場合、昼間沸上げ時間帯の制御は「エネルギー消費性能計算プログラムにおける昼間沸上げ形家庭用ヒートポンプ給湯機の運用管理要綱」に基づき判定された仕様とする。
    # ただし、以下の①、②、もしくは①②の両方に該当する場合は、昼間沸き上げ時間帯の制御は「終了時刻制御」とする。
    #   ①昼間消費電力量比率についてJRA4085に規定する方法により得られる値が不明である場合
    #   ②昼間沸上げ時間帯の制御が終了時刻制御、開始時刻制御および中心時刻制御のいずれにも該当しないか不明である場合
    if daytime_heating == True:
        if all(_ is not None for _ in [R_E_day_in, daytime_heating_control_in]):
          return daytime_heating_control_in
        else:
          return "終了時刻制御"
    # 昼間沸き上げを評価しない場合、昼間沸き上げ時間帯の制御は定義しないものとする。
    else:
        return None


# ============================================================================
# 13. 外気温度条件
# ============================================================================

def get_theta_star_ex_sum():
    """夏期条件外気温度

    Args:

    Returns:
      int: 夏期条件外気温度

    """
    theta_start_ex_table = get_theta_start_ex_table()
    return theta_start_ex_table[0]


def get_theta_star_ex_imd():
    """中間期条件外気温度

    Args:

    Returns:
      int: 中間期条件外気温度

    """
    theta_start_ex_table = get_theta_start_ex_table()
    return theta_start_ex_table[1]


def get_theta_star_ex_win():
    """冬期条件外気温度

    Args:

    Returns:
      int: 冬期条件外気温度

    """
    theta_start_ex_table = get_theta_start_ex_table()
    return theta_start_ex_table[2]


def get_theta_star_ex_frst():
    """着霜条件外気温度

    Args:

    Returns:
      int: 着霜条件外気温度

    """
    theta_start_ex_table = get_theta_start_ex_table()
    return theta_start_ex_table[3]


def get_theta_star_ex_win_cd():
    """寒冷地冬期条件外気温度

    Args:

    Returns:
      int: 寒冷地冬期条件外気温度

    """
    theta_start_ex_table = get_theta_start_ex_table()
    return theta_start_ex_table[4]


def get_theta_star_ex_frst_upper():
    """着霜領域(上限)外気温度

    Args:

    Returns:
      int: 着霜領域(上限)条件外気温度

    """
    theta_start_ex_table = get_theta_start_ex_table()
    return theta_start_ex_table[5]


def get_theta_star_ex_frst_imd():
    """着霜領域(中間)条件外気温度

    Args:

    Returns:
      int: 着霜領域(中間)条件外気温度

    """
    theta_start_ex_table = get_theta_start_ex_table()
    return theta_start_ex_table[6]


def get_theta_start_ex_table():
    """表8　外気温度

    Args:

    Returns:
      list: 表8 外気温度

    """
    # 表8 外気温度
    table_8 = [
        25,
        16,
        7,
        2,
        -7,
        5,
        -2
    ]

    return table_8


# ============================================================================
# 14. 1日当たりの太陽熱補正給湯熱負荷
# ============================================================================


def get_L_dashdash_d(L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d, L_dashdash_b1_d, L_dashdash_b2_d, L_dashdash_ba1_d,
                     L_dashdash_ba2_d):
    """1日当たりの太陽熱補正給湯熱負荷 (35)

    Args:
      L_dashdash_k_d(ndarray): 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_s_d(ndarray): 1日当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/d)
      L_dashdash_w_d(ndarray): 1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)
      L_dashdash_b1_d(ndarray): 1日当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/d)
      L_dashdash_b2_d(ndarray): 1日当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/d)
      L_dashdash_ba1_d(ndarray): 1日当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/d)
      L_dashdash_ba2_d(ndarray): 1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)

    Returns:
      ndarray: 1日当たりの太陽熱補正給湯熱負荷 (MJ/d)

    """
    return (L_dashdash_k_d
            + L_dashdash_s_d
            + L_dashdash_w_d
            + L_dashdash_b1_d
            + L_dashdash_b2_d
            + L_dashdash_ba1_d
            + L_dashdash_ba2_d)


def get_L_dashdash_k_d(L_dashdash_k_d_t):
    """1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)（37a）

    Args:
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)

    """
    return np.sum(L_dashdash_k_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_s_d(L_dashdash_s_d_t):
    """1日当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/d)（37b）

    Args:
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_s_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_w_d(L_dashdash_w_d_t):
    """1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)（37c）

    Args:
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_w_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_b1_d(L_dashdash_b1_d_t):
    """1日当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/d)（37d）

    Args:
      L_dashdash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_b1_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_b2_d(L_dashdash_b2_d_t):
    """1日当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/d)（37e）

    Args:
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_b2_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_ba1_d(L_dashdash_ba1_d_t):
    """1日当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/d)（37f）

    Args:
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_ba1_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_ba2_d(L_dashdash_ba2_d_t):
    """1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)（37g）

    Args:
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_ba2_d_t.reshape((365, 24)), axis=1)


# ============================================================================
# 15. 外気温度
# ============================================================================

def get_theta_ex_ave_hrs_bw_d(hrs_bw, theta_ex_d_t):
    """日付dの沸き上げ熱量に応じる運転における沸き上げ時間帯の区分hrs_bwに対する平均外気温度（℃） (37)

    Args:
        hrs_bw (str): 沸き上げ時間帯の区分
        theta_ex_d_t(ndarray): 日付dの時刻tにおける外気温度 (℃)

    Returns:
        ndarray: 日付dの沸き上げ熱量に応じる運転における沸き上げ時間帯の区分hrs_bwに対する平均外気温度（℃）

    """
    # 8760時間の一次配列を365*24の二次配列へ再配置させる
    tmp_d_t = theta_ex_d_t.reshape(365, 24)

    # 日付d-1の時刻tにおける外気温度 (℃)
    tmp_d_1_t = np.roll(tmp_d_t, 1, axis=0)

    # 沸き上げ時間帯の区分が夜間の場合、前日の23時から当日の7時までの外気温度の平均とする。 (37-1)
    if hrs_bw == 'night':
        return (tmp_d_1_t[:, 23] + np.sum(tmp_d_t[:, 0:7], axis=1)) / 8

    # 沸き上げ時間帯の区分が昼間の場合、当日の9時から16時までの外気温度の平均とする。 (37-2)
    elif hrs_bw == 'day':
        return np.sum(tmp_d_t[:, 9:16], axis=1) / 7

    else:
        raise ValueError(hrs_bw)
