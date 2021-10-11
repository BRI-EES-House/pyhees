# ============================================================================
# 付録 E 電気ヒートポンプ給湯機
# ============================================================================

import numpy as np


# ============================================================================
# E.2 消費電力量
# ============================================================================

def calc_E_E_hs_d_t(L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t, L_dashdash_b1_d_t, L_dashdash_b2_d_t,
                    L_dashdash_ba1_d_t, L_dashdash_ba2_d_t,
                    e_rtd=None, theta_ex_d_Ave_d=None, theta_ex_Nave_d=None, CO2HP=None):
    """1日当たりの給湯機の消費電力量 (1)

    Args:
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h)
      e_rtd(float, optional): 当該給湯機の効率 (Default value = None)
      theta_ex_d_Ave_d(ndarray, optional): 日付dにおける日平均外気温 (℃) (Default value = None)
      theta_ex_Nave_d(ndarray, optional): 日付dにおける夜間平均外気温 (℃) (Default value = None)
      CO2HP(dict, optional): CO2HPパラメーターの辞書 (Default value = None)

    Returns:
      ndarray: 1日当たりの給湯機の消費電力量 (kWh/d)

    """
    # 太陽熱補正給湯熱負荷(30a)(30b)(30c)(30d)(30e)(3f)(30g)
    L_dashdash_k_d = get_L_dashdash_k_d(L_dashdash_k_d_t)
    L_dashdash_s_d = get_L_dashdash_s_d(L_dashdash_s_d_t)
    L_dashdash_w_d = get_L_dashdash_w_d(L_dashdash_w_d_t)
    L_dashdash_b1_d = get_L_dashdash_b1_d(L_dashdash_b1_d_t)
    L_dashdash_b2_d = get_L_dashdash_b2_d(L_dashdash_b2_d_t)
    L_dashdash_ba1_d = get_L_dashdash_ba1_d(L_dashdash_ba1_d_t)
    L_dashdash_ba2_d = get_L_dashdash_ba2_d(L_dashdash_ba2_d_t)

    # (29)
    L_dashdash_d = get_L_dashdash_d(L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d, L_dashdash_b1_d, L_dashdash_b2_d,
                                    L_dashdash_ba1_d, L_dashdash_ba2_d)

    # 表4　外気温度
    theta_star_ex_sum = get_theta_star_ex_sum()  # 夏期条件
    theta_star_ex_imd = get_theta_star_ex_imd()  # 中間期条件
    theta_star_ex_win = get_theta_star_ex_win()  # 冬期条件
    theta_star_ex_frst = get_theta_star_ex_frst()  # 着霜条件
    theta_star_ex_win_cd = get_theta_star_ex_win_cd()  # 寒冷地冬期条件
    theta_star_ex_frst_upper = get_theta_star_ex_frst_upper()  # 着霜領域(上限)条件
    theta_star_ex_frst_imd = get_theta_star_ex_frst_imd()  # 着霜領域(中間)条件

    # e_rtdがNoneの場合は、e_APFからe_rtdへ換算 (28)
    if e_rtd is None:
        e_rtd = get_e_rtd()

    # CO2HPがNoneの場合は、表3より給湯機の仕様の決定
    if CO2HP is None:
        CO2HP = get_spec(e_rtd)

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

    # 表2　沸き上げ温度条件の種類　(標準条件,　高温条件)
    theta_star_bw_std, theta_star_bw_high = get_theta_star_bw()

    # ファーストモードのM1スタンダードモード沸き上げ温度 (27a-1)(27b-1)(27c-1)(27d-1)(27e-1)
    theta_hat_bw_sum_cm1 = get_theta_hat_bw_sum_cm1(theta_star_bw_std)
    theta_hat_bw_imd_cm1 = get_theta_hat_bw_imd_cm1(theta_star_bw_std)
    theta_hat_bw_win_cm1 = get_theta_hat_bw_win_cm1(theta_star_bw_std, theta_hat_bw_win_cm1_test)
    theta_hat_bw_frst_cm1 = get_theta_hat_bw_frst_cm1(theta_star_bw_high, theta_hat_bw_win_cm1)
    theta_hat_bw_win_cd_cm1 = get_theta_hat_bw_win_cd_cm1(theta_star_bw_high, theta_hat_bw_win_cm1)
    # セカンドモードのM1スタンダードモード沸き上げ温度 (27a-2)(27b-2)(27c-2)(27d-2)(27e-2)
    theta_hat_bw_win_cm2 = get_theta_hat_bw_win_cm2(theta_hat_bw_win_cm1, theta_hat_bw_win_cm1_test, theta_hat_bw_win_cm2_test)
    theta_hat_bw_sum_cm2 = get_theta_hat_bw_sum_cm2(theta_hat_bw_sum_cm1, theta_hat_bw_win_cm1, theta_hat_bw_win_cm2)
    theta_hat_bw_imd_cm2 = get_theta_hat_bw_imd_cm2(theta_hat_bw_imd_cm1, theta_hat_bw_win_cm1, theta_hat_bw_win_cm2)
    theta_hat_bw_frst_cm2 = get_theta_hat_bw_frst_cm2(theta_star_bw_high, theta_hat_bw_frst_cm1, theta_hat_bw_win_cm1, theta_hat_bw_win_cm2)
    theta_hat_bw_win_cd_cm2 = get_theta_hat_bw_win_cd_cm2(theta_star_bw_high, theta_hat_bw_win_cd_cm1, theta_hat_bw_win_cm1, theta_hat_bw_win_cm2)

    # ファーストモードのM1スタンダードモード沸き上げ温度 (26)
    theta_hat_bw_cm1_d = get_theta_hat_bw_cm_d(theta_star_ex_imd, theta_star_ex_win, theta_star_ex_frst, theta_star_ex_win_cd,
                          theta_star_ex_frst_upper, theta_ex_Nave_d, theta_hat_bw_sum_cm1, theta_hat_bw_imd_cm1,
                          theta_hat_bw_win_cm1, theta_hat_bw_frst_cm1, theta_hat_bw_win_cd_cm1)
    # セカンドモードのM1スタンダードモード沸き上げ温度 (26)
    theta_hat_bw_cm2_d = get_theta_hat_bw_cm_d(theta_star_ex_imd, theta_star_ex_win, theta_star_ex_frst, theta_star_ex_win_cd,
                          theta_star_ex_frst_upper, theta_ex_Nave_d, theta_hat_bw_sum_cm2, theta_hat_bw_imd_cm2,
                          theta_hat_bw_win_cm2, theta_hat_bw_frst_cm2, theta_hat_bw_win_cd_cm2)

    # 試験時の等価貯湯温度 (24)
    theta_tnk_eq_test = get_theta_tnk_eq_test(Q_loss_test, R_tnk_test, theta_star_ex_win)

    # 冬期条件、着霜期条件および着霜領域（上限）における等価貯湯温度 (23)
    theta_tnk_eq_win, theta_tnk_eq_frst, theta_tnk_eq_frst_upper = get_theta_tnk_eq(theta_tnk_eq_test)

    # ファーストモードの等価貯湯温度(22-1)
    theta_tnk_eq_cm1_d = get_theta_tnk_eq_cm1_d(theta_ex_d_Ave_d, theta_star_ex_frst, theta_star_ex_frst_upper, theta_tnk_eq_win,
                           theta_tnk_eq_frst, theta_tnk_eq_frst_upper)
    # セカンドモードの等価貯湯温度(22-2)
    theta_tnk_eq_cm2_d = get_theta_tnk_eq_cm2_d(theta_ex_d_Ave_d, theta_tnk_eq_cm1_d, theta_hat_bw_cm1_d, theta_hat_bw_cm2_d)

    # ファーストモードの1日当たりの貯湯熱損失量(21)
    Q_dot_loss_cm1_d = get_Q_dot_loss_cm_d(theta_tnk_eq_cm1_d, theta_ex_d_Ave_d, R_tnk_test)
    # セカンドモードの1日当たりの貯湯熱損失量(21)
    Q_dot_loss_cm2_d = get_Q_dot_loss_cm_d(theta_tnk_eq_cm2_d, theta_ex_d_Ave_d, R_tnk_test)

    # ファーストモードの1日当たりの沸き上げ熱量(20)
    Q_dot_HP_cm1_d = get_Q_dot_HP_cm_d(L_dashdash_d, Q_dot_loss_cm1_d)
    # セカンドモードの1日当たりの沸き上げ熱量(20)
    Q_dot_HP_cm2_d = get_Q_dot_HP_cm_d(L_dashdash_d, Q_dot_loss_cm2_d)

    # 試験時の着霜期高温条件における除霜効率係数 (16)
    C_def_frst_test = get_C_def_frst_test(e_HP_def_high_test, e_HP_frst_high_test)

    # ファーストモードの着霜期条件における除霜効率係数 (15a)
    C_def_frst_cm1 = get_C_def_frst_cm(theta_hat_bw_frst_cm1, theta_bw_frst_high_test, C_def_frst_test)
    # ファーストモードの着霜期条件における除霜効率係数 (15a)
    C_def_frst_cm2 = get_C_def_frst_cm(theta_hat_bw_frst_cm2, theta_bw_frst_high_test, C_def_frst_test)


    # ファーストモードの寒冷地冬期条件における除霜効率係数 (15b)
    C_def_win_cd_cm1 = get_C_def_win_cd_cm(theta_hat_bw_win_cd_cm1, theta_bw_frst_high_test, theta_star_ex_win_cd, theta_star_ex_frst_imd,
                     C_def_frst_test)
    # セカンドモードの寒冷地冬期条件における除霜効率係数 (15b)
    C_def_win_cd_cm2 = get_C_def_win_cd_cm(theta_hat_bw_win_cd_cm2, theta_bw_frst_high_test, theta_star_ex_win_cd, theta_star_ex_frst_imd,
                     C_def_frst_test)

    # ファーストモードの除霜効率係数 (14)
    C_def_cm1_d = get_C_def_cm_d(theta_star_ex_frst_upper, theta_ex_Nave_d, theta_star_ex_frst, theta_star_ex_frst_imd,
                   theta_star_ex_win_cd, C_def_frst_cm1, C_def_win_cd_cm1)
    # セカンドモードの除霜効率係数 (14)
    C_def_cm2_d = get_C_def_cm_d(theta_star_ex_frst_upper, theta_ex_Nave_d, theta_star_ex_frst, theta_star_ex_frst_imd,
                   theta_star_ex_win_cd, C_def_frst_cm2, C_def_win_cd_cm2)

    # ファーストモードのヒートポンプの消費電力 (13-1)
    P_HP_cm1_d = get_P_HP_cm_d(q_HP_sum_std_test, q_HP_win_std_test, A_p, B_p, theta_hat_bw_cm1_d, theta_ex_Nave_d,
                  theta_star_bw_std, theta_star_ex_sum, P_HP_sum_std_test)
    # セカンドモードのヒートポンプの消費電力 (13-1)
    P_HP_cm2_d = get_P_HP_cm_d(q_HP_sum_std_test, q_HP_win_std_test, A_p, B_p, theta_hat_bw_cm2_d, theta_ex_Nave_d,
                  theta_star_bw_std, theta_star_ex_sum, P_HP_sum_std_test)

    # 試験時のヒートポンプのエネルギー消費効率 (11a)(11b)(11c)
    e_HP_sum_std_test, e_HP_imd_std_test, e_HP_win_std_test = get_e_HP_std_test(q_HP_sum_std_test, q_HP_imd_std_test, q_HP_win_std_test,
                      P_HP_sum_std_test, P_HP_imd_std_test, P_HP_win_std_test)

    # 沸き上げ温度を標準条件または高温条件とした場合のヒートポンプのエネルギー消費効率 (10a)(10b)(10c)(10d)(10e)(10f)
    e_HP_sum_std, e_HP_imd_std, e_HP_win_std, e_HP_frst_upper_std, e_HP_frst_high, e_HP_win_cd_high = \
        get_e_HP_std(theta_bw_sum_std_test, theta_bw_imd_std_test, theta_bw_win_std_test, theta_star_bw_std, theta_star_ex_imd,
                 theta_star_ex_win, theta_star_ex_frst_upper, theta_star_bw_high, theta_bw_frst_high_test,
                 e_HP_sum_std_test, e_HP_imd_std_test, e_HP_win_std_test, e_HP_frst_high_test)

    # ファーストモードの実働効率比 (9-1)
    r_e_HP_cm1 = get_r_e_HP_cm1()

    # ファーストモードの実働効率比 (9-2)
    r_e_HP_cm2 = get_r_e_HP_cm2(theta_hat_bw_win_cm2)

    # ファーストモードのヒートポンプのM1スタンダードモードエネルギー消費効率 (8a)(8b)(8c)(8d)(8e)(8f)
    e_hat_HP_sum_cm1, e_hat_HP_imd_cm1, e_hat_HP_win_cm1, e_hat_HP_frst_upper_cm1, e_hat_HP_frst_cm1, e_hat_HP_win_cd_cm1\
        = get_e_hat_HP_cm(r_e_HP_cm1, e_HP_sum_std, e_HP_imd_std, e_HP_win_std, e_HP_frst_upper_std, e_HP_frst_high, e_HP_win_cd_high,
                    theta_hat_bw_sum_cm1, theta_hat_bw_imd_cm1, theta_hat_bw_win_cm1, theta_hat_bw_frst_cm1, theta_hat_bw_win_cd_cm1,
                    theta_star_bw_std, theta_star_bw_high)
    # セカンドモードのヒートポンプのM1スタンダードモードエネルギー消費効率 (8a)(8b)(8c)(8d)(8e)(8f)
    e_hat_HP_sum_cm2, e_hat_HP_imd_cm2, e_hat_HP_win_cm2, e_hat_HP_frst_upper_cm2, e_hat_HP_frst_cm2, e_hat_HP_win_cd_cm2\
        = get_e_hat_HP_cm(r_e_HP_cm2, e_HP_sum_std, e_HP_imd_std, e_HP_win_std, e_HP_frst_upper_std, e_HP_frst_high, e_HP_win_cd_high,
                    theta_hat_bw_sum_cm2, theta_hat_bw_imd_cm2, theta_hat_bw_win_cm2, theta_hat_bw_frst_cm2, theta_hat_bw_win_cd_cm2,
                    theta_star_bw_std, theta_star_bw_high)

    # ファーストモードのヒートポンプのM1スタンダードモードエネルギー消費効率(7)
    e_hat_HP_cm1_d = get_e_hat_HP_cm_d(theta_ex_Nave_d, theta_star_ex_sum, theta_star_ex_imd, theta_star_ex_win,
                                       theta_star_ex_win_cd, theta_star_ex_frst_upper, theta_star_ex_frst,
                                       e_hat_HP_sum_cm1, e_hat_HP_imd_cm1, e_hat_HP_win_cm1, e_hat_HP_win_cd_cm1,
                                       e_hat_HP_frst_upper_cm1, e_hat_HP_frst_cm1)
    # セカンドモードのヒートポンプのM1スタンダードモードエネルギー消費効率(7)
    e_hat_HP_cm2_d = get_e_hat_HP_cm_d(theta_ex_Nave_d, theta_star_ex_sum, theta_star_ex_imd, theta_star_ex_win,
                                       theta_star_ex_win_cd, theta_star_ex_frst_upper, theta_star_ex_frst,
                                       e_hat_HP_sum_cm2, e_hat_HP_imd_cm2, e_hat_HP_win_cm2, e_hat_HP_win_cd_cm2,
                                       e_hat_HP_frst_upper_cm2, e_hat_HP_frst_cm2)

    # ファーストモードのヒートポンプの加熱能力 (12)
    q_HP_cm1_d = get_q_HP_cm_d(e_hat_HP_cm1_d, P_HP_cm1_d)
    # セカンドモードのヒートポンプの加熱能力 (12)
    q_HP_cm2_d = get_q_HP_cm_d(e_hat_HP_cm2_d, P_HP_cm2_d)

    # 沸き上げ終了時刻
    t_HP_stop = get_t_HP_stop()

    # ファーストモードの1日当たりのヒートポンプ運転時間(19)
    tau_dot_HP_cm1_d = get_tau_dot_HP_cm_d(Q_dot_HP_cm1_d, q_HP_cm1_d)
    # セカンドモードの1日当たりのヒートポンプ運転時間(19)
    tau_dot_HP_cm2_d = get_tau_dot_HP_cm_d(Q_dot_HP_cm2_d, q_HP_cm2_d)

    # ファーストモードの日付dに沸き上げが終了する運転の沸き上げ開始時刻 (18)
    t_HP_start_d_1 = get_t_HP_start_d(t_HP_stop, tau_dot_HP_cm1_d)
    # セカンドモードの日付dに沸き上げが終了する運転の沸き上げ開始時刻 (18)
    t_HP_start_d_2 = get_t_HP_start_d(t_HP_stop, tau_dot_HP_cm2_d)

    # ファーストモードの1時間当たりのヒートポンプ運転時間(17)
    tau_HP_cm1_d_t = get_tau_HP_cm_d_t(t_HP_stop, t_HP_start_d_1, tau_dot_HP_cm1_d)
    # セカンドモードの1時間当たりのヒートポンプ運転時間(17)
    tau_HP_cm2_d_t = get_tau_HP_cm_d_t(t_HP_stop, t_HP_start_d_2, tau_dot_HP_cm2_d)

    # ファーストモードの補機の消費電力量　(25)
    E_E_aux_cm1_d_t = get_E_E_aux_cm_d_t(P_aux_HP_on_test, P_aux_HP_off_test, tau_HP_cm1_d_t)
    # ファーストモードの補機の消費電力量　(25)
    E_E_aux_cm2_d_t = get_E_E_aux_cm_d_t(P_aux_HP_on_test, P_aux_HP_off_test, tau_HP_cm2_d_t)

    # ファーストモードの1日当たりの沸き上げに係るヒートポンプの消費電力量 (5)
    E_dot_E_HP_bw_cm1_d = get_E_dot_E_HP_bw_cm_d(Q_dot_HP_cm1_d, e_hat_HP_cm1_d)
    # セカンドモードの1日当たりの沸き上げに係るヒートポンプの消費電力量 (5)
    E_dot_E_HP_bw_cm2_d = get_E_dot_E_HP_bw_cm_d(Q_dot_HP_cm2_d, e_hat_HP_cm2_d)

    # ファーストモードの1日当たりの除霜に係るヒートポンプの消費電力量　(6)
    E_dot_E_HP_def_cm1_d = get_E_dot_E_HP_def_cm_d(E_dot_E_HP_bw_cm1_d, C_def_cm1_d)
    # セカンドモードの1日当たりの除霜に係るヒートポンプの消費電力量　(6)
    E_dot_E_HP_def_cm2_d = get_E_dot_E_HP_def_cm_d(E_dot_E_HP_bw_cm2_d, C_def_cm2_d)

    # ファーストモードの1日当たりのヒートポンプの消費電力量 (4)
    E_dot_E_HP_cm1_d = get_E_dot_E_HP_cm_d(E_dot_E_HP_bw_cm1_d, E_dot_E_HP_def_cm1_d)
    # セカンドモードの1日当たりのヒートポンプの消費電力量 (4)
    E_dot_E_HP_cm2_d = get_E_dot_E_HP_cm_d(E_dot_E_HP_bw_cm2_d, E_dot_E_HP_def_cm2_d)

    # ファーストモードの1時間当たりのヒートポンプの消費電力量 (3)
    E_E_HP_cm1_d_t = get_E_E_HP_cm_d_t(t_HP_stop, tau_dot_HP_cm1_d, E_dot_E_HP_cm1_d, tau_HP_cm1_d_t)
    # セカンドモードの1時間当たりのヒートポンプの消費電力量 (3)
    E_E_HP_cm2_d_t = get_E_E_HP_cm_d_t(t_HP_stop, tau_dot_HP_cm2_d, E_dot_E_HP_cm2_d, tau_HP_cm2_d_t)

    # ファーストモードの1時間当たりの給湯機の消費電力量 (2)
    E_E_hs_cm1_d_t = get_E_E_hs_cm_d_t(E_E_HP_cm1_d_t, E_E_aux_cm1_d_t)
    # セカンドモードの1時間当たりの給湯機の消費電力量 (2)
    E_E_hs_cm2_d_t = get_E_E_hs_cm_d_t(E_E_HP_cm2_d_t, E_E_aux_cm2_d_t)

    # 制御におけるファーストモードの割合
    r_usg_cm1 = get_r_usg_cm1()

    # 制御におけるセカンドモードの割合
    r_usg_cm2 = get_r_usg_cm2()

    # 消費電力量(1)
    E_E_hs_d_t = r_usg_cm1 * E_E_hs_cm1_d_t + r_usg_cm2 * E_E_hs_cm2_d_t

    return E_E_hs_d_t


def get_r_usg_cm1():
    """制御モードがファーストモードの利用率

    Args:

    Returns:
      float: 御におけるファーストモードの割合

    """
    return 0.6


def get_r_usg_cm2():
    """制御モードがセカンドモードの利用率

    Args:

    Returns:
      float: 御におけるセカンドモードの割合

    """
    return 0.4


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
# E.3 ガス消費量
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
# E.4 灯油消費量
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
# E.5　ヒートポンプ
# ============================================================================

# ============================================================================
# E.5.1 消費電力量
# ============================================================================

def get_E_E_HP_cm_d_t(t_HP_stop, tau_dot_HP_cm_d, E_dot_E_HP_cm_d, tau_HP_cm_d_t):
    """日付dの時刻tにおける制御モードcmの1時間当たりのヒートポンプの消費電力量(3-1)(3-2)

    Args:
      t_HP_stop(float): 沸き上げ終了時刻
      tau_dot_HP_cm_d(ndarray): 日付dにおける制御モードcmの1日当たりのヒートポンプ運転時間
      E_dot_E_HP_cm_d(ndarray): 日付dにおける制御モードcmの1日当たりのヒートポンプの消費電力量
      tau_HP_cm_d_t(ndarray): 日付dの時刻tにおける制御モードcmの1時間当たりのヒートポンプ運転時間

    Returns:
      ndarray: 日付dの時刻tにおける制御モードcmの1時間当たりのヒートポンプの消費電力量

    """
    E_E_HP_cm_d_t = np.zeros(24 * 365)

    # 1日後
    E_dot_E_HP_cm_d_1 = np.roll(E_dot_E_HP_cm_d, -1)
    tau_dot_HP_cm_d_1 = np.roll(tau_dot_HP_cm_d, -1)

    # 24時間化
    tau_dot_HP_cm_d_t = np.repeat(tau_dot_HP_cm_d, 24)
    tau_dot_HP_cm_d_1_t = np.repeat(tau_dot_HP_cm_d_1, 24)
    E_dot_E_HP_cm_d_t = np.repeat(E_dot_E_HP_cm_d, 24)
    E_dot_E_HP_cm_d_1_t = np.repeat(E_dot_E_HP_cm_d_1, 24)

    # 0 <= t < t_HP_stop の場合　(3-1)
    t1 = np.tile(np.logical_and(0 <= np.arange(24), np.arange(24) <= t_HP_stop), 365)

    # tau_dot_HP_cm_d == 0 の場合
    t2 = tau_dot_HP_cm_d_t == 0
    t3 = np.logical_and(t1, t2)
    E_E_HP_cm_d_t[t3] = 0

    # tau_dot_HP_cm_d != 0 の場合
    t4 = tau_dot_HP_cm_d_t != 0
    t5 = np.logical_and(t1, t4)
    E_E_HP_cm_d_t[t5] = E_dot_E_HP_cm_d_t[t5] * (tau_HP_cm_d_t[t5] / tau_dot_HP_cm_d_t[t5])

    # t_HP_stop <= t < 24 の場合　(3-2)
    t6 = np.tile(np.logical_and(t_HP_stop <= np.arange(24), np.arange(24) <= 24), 365)

    # tau_dot_HP_cm_d_1 == 0 の場合
    t7 = tau_dot_HP_cm_d_1_t == 0
    t8 = np.logical_and(t6, t7)
    E_E_HP_cm_d_t[t8] = 0

    # tau_dot_HP_cm_d_1 != 0 の場合
    t9 = tau_dot_HP_cm_d_1_t != 0
    t10 = np.logical_and(t6, t9)
    E_E_HP_cm_d_t[t10] = E_dot_E_HP_cm_d_1_t[t10] * (tau_HP_cm_d_t[t10] / tau_dot_HP_cm_d_1_t[t10])

    return E_E_HP_cm_d_t
    

def get_E_dot_E_HP_cm_d(E_dot_E_HP_bw_cm_d, E_dot_E_HP_def_cm_d):
    """日付dにおける制御モードcmの1日当たりのヒートポンプの消費電力量(4)

    Args:
      E_dot_E_HP_bw_cm_d(ndarray): 日付dにおける制御モードcmの1日当たりの沸き上げに係るヒートポンプの消費電力量
      E_dot_E_HP_def_cm_d(ndarray): 日付dにおける制御モードcmの1日当たりの除霜に係るヒートポンプの消費電力量

    Returns:
      ndarray: 日付dにおける制御モードcmの1日当たりのヒートポンプの消費電力量

    """
    return E_dot_E_HP_bw_cm_d + E_dot_E_HP_def_cm_d


def get_E_dot_E_HP_bw_cm_d(Q_dot_HP_cm_d, e_hat_HP_cm_d):
    """日付dの時刻tにおける制御モードcmの1日当たりの沸き上げに係るヒートポンプの消費電力量(5)

    Args:
      Q_dot_HP_cm_d(ndarray): 日付dにおける制御モードcmの1日当たりの沸き上げ熱量
      e_hat_HP_cm_d(ndarray): 日付dにおける制御モードcmのヒートポンプのM1スタンダードモードエネルギー消費効率

    Returns:
      ndarray: 日付dの時刻tにおける制御モードcmの1日当たりの沸き上げに係るヒートポンプの消費電力量

    """
    return (Q_dot_HP_cm_d / e_hat_HP_cm_d) * (1000 / 3600)


def get_E_dot_E_HP_def_cm_d(E_dot_HP_bw_cm_d, C_def_cm_d):
    """日付dの時刻tにおける制御モードcmの1日当たりの除霜に係るヒートポンプの消費電力量(6)

    Args:
      E_dot_HP_bw_cm_d(ndarray): 日付dにおける制御モードcmの1日当たりの沸き上げに係るヒートポンプの消費電力量
      C_def_cm_d: 日付dにおける制御モードcmの除霜効率係数

    Returns:
      ndarray: 日付dの時刻tにおける制御モードcmの1日当たりの除霜に係るヒートポンプの消費電力量

    """
    return E_dot_HP_bw_cm_d * (1 / C_def_cm_d - 1)


# ============================================================================
# E.5.2 エネルギー消費効率
# ============================================================================

def get_e_hat_HP_cm_d(theta_ex_Nave_d, theta_star_ex_sum, theta_star_ex_imd, theta_star_ex_win, theta_star_ex_win_cd,
                      theta_star_ex_frst_upper, theta_star_ex_frst,
                      e_hat_HP_sum_cm, e_hat_HP_imd_cm, e_hat_HP_win_cm, e_hat_HP_win_cd_cm, e_hat_HP_frst_upper_cm,
                      e_hat_HP_frst_cm):
    """日付dにおける制御モードcmのヒートポンプのM1スタンダードモードエネルギー消費効率(-) (7)

    Args:
      theta_ex_Nave_d(float): 日付dにおける夜間平均外気温度
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
    e_hat_HP_cm_d = np.zeros(365)

    f1 = theta_star_ex_imd < theta_ex_Nave_d
    e_hat_HP_cm_d[f1] = e_hat_HP_imd_cm + (theta_ex_Nave_d[f1] - theta_star_ex_imd) / (theta_star_ex_sum - theta_star_ex_imd) * \
                    (e_hat_HP_sum_cm - e_hat_HP_imd_cm)

    f2 = np.logical_and(theta_star_ex_win < theta_ex_Nave_d, theta_ex_Nave_d <= theta_star_ex_imd)
    e_hat_HP_cm_d[f2] = e_hat_HP_imd_cm + (theta_ex_Nave_d[f2] - theta_star_ex_imd) / (theta_star_ex_imd - theta_star_ex_win) * \
                    (e_hat_HP_imd_cm - e_hat_HP_win_cm)

    f3 = np.logical_and(theta_star_ex_frst_upper < theta_ex_Nave_d, theta_ex_Nave_d <= theta_star_ex_win)
    e_hat_HP_cm_d[f3] = e_hat_HP_win_cm + (theta_ex_Nave_d[f3] - theta_star_ex_win) / (theta_star_ex_win - theta_star_ex_frst_upper) * \
                    (e_hat_HP_win_cm - e_hat_HP_frst_upper_cm)

    f4 = np.logical_and(theta_star_ex_frst < theta_ex_Nave_d, theta_ex_Nave_d <= theta_star_ex_frst_upper)
    e_hat_HP_cm_d[f4] = e_hat_HP_frst_cm + (theta_ex_Nave_d[f4] - theta_star_ex_frst) / (theta_star_ex_frst_upper - theta_star_ex_frst) * \
                    (e_hat_HP_frst_upper_cm - e_hat_HP_frst_cm)

    f5 = theta_ex_Nave_d <= theta_star_ex_frst
    e_hat_HP_cm_d[f5] = e_hat_HP_frst_cm + (theta_ex_Nave_d[f5] - theta_star_ex_frst) / (theta_star_ex_frst - theta_star_ex_win_cd) * \
                    (e_hat_HP_frst_cm - e_hat_HP_win_cd_cm)

    return e_hat_HP_cm_d


def get_e_hat_HP_cm(r_e_HP_cm, e_HP_sum_std, e_HP_imd_std, e_HP_win_std, e_HP_frst_upper_cm, e_HP_frst_high, e_HP_win_cd_high,
                    theta_hat_bw_sum_cm, theta_hat_bw_imd_cm, theta_hat_bw_win_cm, theta_hat_bw_frst_cm, theta_hat_bw_win_cd_cm,
                    theta_star_bw_std, theta_star_bw_high):
    """ヒートポンプのM1スタンダードモードエネルギー消費効率(-) (8a)(8b)(8c)(8d)(8e)(8f)

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
    # (8a)
    e_hat_HP_sum_cm = r_e_HP_cm * e_HP_sum_std * (-0.01 * (theta_hat_bw_sum_cm - theta_star_bw_std) + 1.0)

    # (8b)
    e_hat_HP_imd_cm = r_e_HP_cm * e_HP_imd_std * (-0.01 * (theta_hat_bw_imd_cm - theta_star_bw_std) + 1.0)

    # (8c)
    e_hat_HP_win_cm = r_e_HP_cm * e_HP_win_std * (-0.01 * (theta_hat_bw_win_cm - theta_star_bw_std) + 1.0)

    # (8d)
    e_hat_HP_frst_upper_cm = r_e_HP_cm * e_HP_frst_upper_cm * (-0.01 * (theta_hat_bw_win_cm - theta_star_bw_std) + 1.0)

    # (8e)
    e_hat_HP_frst_cm = r_e_HP_cm * e_HP_frst_high * (-0.01 * (theta_hat_bw_frst_cm - theta_star_bw_high) + 1.0)

    # (8f)
    e_hat_HP_win_cd_cm = r_e_HP_cm * e_HP_win_cd_high * (-0.01 * (theta_hat_bw_win_cd_cm - theta_star_bw_high) + 1.0)

    return e_hat_HP_sum_cm, e_hat_HP_imd_cm, e_hat_HP_win_cm, e_hat_HP_frst_upper_cm, e_hat_HP_frst_cm, e_hat_HP_win_cd_cm


def get_r_e_HP_cm1():
    """ファーストモードの実働効率比(9-1)

    Args:

    Returns:
      float: ファーストモードの実働効率比

    """
    return 0.94


def get_r_e_HP_cm2(theta_hat_bw_win_cm):
    """セカンドモードの実働効率比(9-2)

    Args:
      theta_hat_bw_win_cm(float): 制御モードcmの冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      float: セカンドモードの実働効率比

    """
    if (theta_hat_bw_win_cm <= 75):
        return 0.90
    elif (75 < theta_hat_bw_win_cm):
        return -0.005 * (theta_hat_bw_win_cm - 75) + 0.90
    else:
        raise ValueError(theta_hat_bw_win_cm)



def get_e_HP_std(theta_bw_sum_std_test, theta_bw_imd_std_test, theta_bw_win_std_test, theta_star_bw_std, theta_star_ex_imd,
                 theta_star_ex_win, theta_star_ex_frst_upper, theta_star_bw_high, theta_bw_frst_high_test,
                 e_HP_sum_std_test, e_HP_imd_std_test, e_HP_win_std_test, e_HP_frst_high_test):
    """沸き上げ温度を標準条件または高温条件とした場合のヒートポンプのエネルギー消費効率(10a)(10b)(10c)(10d)(10e)(10f)

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
    # 夏期-標準条件におけるヒートポンプのエネルギー消費効率（-）(10a)
    e_HP_sum_std = e_HP_sum_std_test / (-0.01 * (theta_bw_sum_std_test - theta_star_bw_std) + 1.0)

    # 中間期-標準条件におけるヒートポンプのエネルギー消費効率（-）(10b)
    e_HP_imd_std = e_HP_imd_std_test / (-0.01 * (theta_bw_imd_std_test - theta_star_bw_std) + 1.0)

    # 冬期-標準条件におけるヒートポンプのエネルギー消費効率（-）(10c)
    e_HP_win_std = e_HP_win_std_test / (-0.01 * (theta_bw_win_std_test - theta_star_bw_std) + 1.0)

    # 着霜領域（上限）-標準条件におけるヒートポンプのエネルギー消費効率（-）(10d)
    e_HP_frst_upper_std = e_HP_win_std + \
                          ((theta_star_ex_frst_upper - theta_star_ex_win) / (theta_star_ex_imd - theta_star_ex_win)) *\
                          (e_HP_imd_std - e_HP_win_std)

    # 着霜期-高温条件におけるヒートポンプの除霜運転を除くエネルギー消費効率（-）(10e)
    e_HP_frst_high = e_HP_frst_high_test / (-0.01 * (theta_bw_frst_high_test - theta_star_bw_high) + 1.0)

    # 寒冷地冬期-高温条件におけるヒートポンプの除霜運転を除くエネルギー消費効率（-）(10af)
    e_HP_win_cd_high = e_HP_frst_high * 0.82

    return e_HP_sum_std, e_HP_imd_std, e_HP_win_std, e_HP_frst_upper_std, e_HP_frst_high, e_HP_win_cd_high


def get_e_HP_std_test(q_HP_sum_std_test, q_HP_imd_std_test, q_HP_win_std_test,
                      P_HP_sum_std_test, P_HP_imd_std_test, P_HP_win_std_test):
    """試験時のヒートポンプのエネルギー消費効率(11a)(11b)(11c)

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
    # 試験時の夏期標準加熱条件におけるヒートポンプのエネルギー消費効率（-）(11a)
    e_HP_sum_std_test = q_HP_sum_std_test / P_HP_sum_std_test

    # 試験時の中間期標準加熱条件におけるヒートポンプのエネルギー消費効率（-）(11b)
    e_HP_imd_std_test = q_HP_imd_std_test / P_HP_imd_std_test

    # 試験時の冬期標準条件におけるヒートポンプのエネルギー消費効率（-）(11c)
    e_HP_win_std_test = q_HP_win_std_test / P_HP_win_std_test

    return e_HP_sum_std_test, e_HP_imd_std_test, e_HP_win_std_test


# ============================================================================
# E.5.3 加熱能力
# ============================================================================

def get_q_HP_cm_d(e_HP_cm_d, P_HP_cm_d):
    """日付dにおける制御モードcmのヒートポンプの加熱能力(12)

    Args:
      e_HP_cm_d(ndarray): 日付dにおける制御モードcmのヒートポンプのエネルギー消費効率
      P_HP_cm_d(ndarray): 日付dにおける制御モードcmのヒートポンプの消費電力

    Returns:
      ndarray: 付dにおける制御モードcmのヒートポンプの加熱能力

    """
    return e_HP_cm_d * P_HP_cm_d


def get_P_HP_cm_d(q_HP_sum_std_test, q_HP_win_std_test, A_p, B_p, theta_hat_bw_cm_d, theta_ex_Nave_d,
                  theta_star_bw_std, theta_star_ex_sum, P_HP_sum_std_test):
    """日付dにおける制御モードcmのヒートポンプの消費電力(13)

    Args:
      q_HP_sum_std_test(float): 試験時の夏期標準加熱条件におけるヒートポンプの加熱能力
      q_HP_win_std_test(float): 試験時の冬期標準加熱条件におけるヒートポンプの加熱能力
      A_p(float): ヒートポンプの消費電力を求める回帰式の傾き
      B_p(float): ヒートポンプの消費電力を求める回帰式の切片（kW）
      theta_hat_bw_cm_d(float): 日付dにおける制御モードcmのM1スタンダードモード沸き上げ温度
      theta_ex_Nave_d(float): 日付dにおける夜間平均外気温度
      theta_star_bw_std(float): 標準条件の沸き上げ温度
      theta_star_ex_sum(float): 夏期条件の外気温度
      P_HP_sum_std_test(float): 試験時の夏期標準加熱条件におけるヒートポンプの消費電力

    Returns:
      ndarray: 日付dにおける制御モードcmのヒートポンプの消費電力

    """
    P_HP_cm_d = np.zeros(365)

    # (13-1)
    if (q_HP_sum_std_test == q_HP_win_std_test):
        P_HP_cm_d = A_p * (theta_hat_bw_cm_d - theta_ex_Nave_d) + B_p
    # (13-2)
    else:
        f1 = theta_ex_Nave_d <= 20
        f2 = 20 < theta_ex_Nave_d

        P_HP_cm_d[f1] = A_p * (theta_hat_bw_cm_d[f1] - theta_ex_Nave_d[f1]) + B_p

        P_HP_cm_d[f2] = A_p * ((theta_hat_bw_cm_d[f2] - theta_ex_Nave_d[f2]) - (theta_star_bw_std - theta_star_ex_sum)) + \
                        P_HP_sum_std_test

    return P_HP_cm_d


# ============================================================================
# E.5.4 除霜効率係数
# ============================================================================

def get_C_def_cm_d(theta_star_ex_frst_upper, theta_ex_Nave_d, theta_star_ex_frst, theta_star_ex_frst_imd,
                   theta_star_ex_win_cd, C_def_frst_cm, C_def_win_cd_cm):
    """日付dにおける制御モードcmの除霜効率係数(14)

    Args:
      theta_star_ex_frst_upper(float): 着霜領域（上限）の外気温度
      theta_ex_Nave_d(ndarray): 日付dにおける夜間平均外気温度
      theta_star_ex_frst(float): 着霜期条件の外気温度
      theta_star_ex_frst_imd(float): 着霜領域（中間）の外気温度
      theta_star_ex_win_cd(float): 寒冷地冬期条件の外気温度
      C_def_frst_cm(float): 着霜期条件における除霜効率係数
      C_def_win_cd_cm(float): 寒冷地冬期条件における除霜効率係数

    Returns:
      ndarray: 日付dにおける制御モードcmの除霜効率係数

    """
    get_C_def_cm_d = np.ones(365)

    f1 = theta_star_ex_frst_upper < theta_ex_Nave_d
    get_C_def_cm_d[f1] = 1.0

    f2 = np.logical_and(theta_star_ex_frst < theta_ex_Nave_d, theta_ex_Nave_d <= theta_star_ex_frst_upper)
    get_C_def_cm_d[f2] = np.minimum(1.0, C_def_frst_cm + (theta_ex_Nave_d[f2] - theta_star_ex_frst) /
                                (theta_star_ex_frst_upper - theta_star_ex_frst) * (1.0 - C_def_frst_cm))

    f3 = np.logical_and(theta_star_ex_frst_imd < theta_ex_Nave_d, theta_ex_Nave_d <= theta_star_ex_frst)
    get_C_def_cm_d[f3] = np.minimum(1.0, C_def_frst_cm)

    f4 = theta_ex_Nave_d <= theta_star_ex_frst_imd
    get_C_def_cm_d[f4] = np.minimum(1.0, C_def_win_cd_cm + (theta_ex_Nave_d[f4] - theta_star_ex_win_cd) /
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
# E.5.5 ヒートポンプ運転時間
# ============================================================================

def get_tau_HP_cm_d_t(t_HP_stop, t_HP_start_d, tau_dot_HP_cm_d):
    """日付dの時刻tにおける制御モードcmの1時間当たりのヒートポンプ運転時間(h/h)(17-1)(17-2)(17-3)(17-4)

    Args:
      t_HP_stop(float): 沸き上げ終了時刻
      t_HP_start_d(ndarray): 日付dの時刻tにおける制御モードcmの1時間当たりのヒートポンプ運転時間
      t_HP_start_d(ndarray): 日付dにおける制御モードcmの1日当たりのヒートポンプ運転時間
      tau_dot_HP_cm_d: returns: 日付dの時刻tにおける制御モードcmの1時間当たりのヒートポンプ運転時間

    Returns:
      ndarray: 日付dの時刻tにおける制御モードcmの1時間当たりのヒートポンプ運転時間

    """
    tau_HP_cm_d_t = np.zeros(24 * 365)

    # 1日後
    t_HP_start_d_1 = np.roll(t_HP_start_d, -1)
    tau_dot_HP_cm_d_1 = np.roll(tau_dot_HP_cm_d, -1)

    # 24時間化
    t_HP_start_d_t = np.repeat(t_HP_start_d, 24)
    t_HP_start_d_1_t = np.repeat(t_HP_start_d_1, 24)
    tau_dot_HP_cm_d_t = np.repeat(tau_dot_HP_cm_d, 24)
    tau_dot_HP_cm_d_1_t = np.repeat(tau_dot_HP_cm_d_1, 24)
    t = np.tile(np.arange(24), 365)

    # 0 <= t < t_HP_stop の場合
    t1 = np.tile(np.logical_and(0 <= np.arange(24), np.arange(24) < t_HP_stop), 365)

    # 0 <= t_HP_start_d の場合(沸き上げ開始と沸き上げ終了が同日に行われる場合) (17-1)
    t2 = np.repeat(0 <= t_HP_start_d, 24)

    # t < t_HP_start_d の場合
    t5 = t < t_HP_start_d_t
    t6 = np.logical_and(np.logical_and(t1, t2), t5)
    tau_HP_cm_d_t[t6] = 0

    # t == t_HP_start_d の場合
    t7 = t == t_HP_start_d_t
    t8 = np.logical_and(np.logical_and(t1, t2), t7)
    tau_HP_cm_d_t[t8] = tau_dot_HP_cm_d_t[t8] - np.floor(tau_dot_HP_cm_d_t[t8])

    # t > t_HP_start_d の場合
    t9 = t > t_HP_start_d_t
    t10 = np.logical_and(np.logical_and(t1, t2), t9)
    tau_HP_cm_d_t[t10] = 1

    # 0 > t_HP_start_d の場合(沸き上げが終了する日の前日に沸き上げが開始する場合) (17-2)
    t11 = np.repeat(0 > t_HP_start_d, 24)
    t12 = np.logical_and(t1, t11)
    tau_HP_cm_d_t[t12] = 1

    # t_HP_stop <= t < 24 の場合
    t13 = np.tile(np.logical_and(t_HP_stop <= np.arange(24), np.arange(24) < 24), 365)

    # 0 <= t_HP_start_d_1 の場合(沸き上げ開始と沸き上げ終了が同日に行われる場合) (17-3)
    t14 = np.repeat(0 <= t_HP_start_d_1, 24)
    t15 = np.logical_and(t13, t14)
    tau_HP_cm_d_t[t15] = 0

    # 0 > t_HP_start_d_1 の場合(沸き上げが終了する日の前日に沸き上げが開始する場合) (17-4)
    t16 = np.repeat(0 > t_HP_start_d_1, 24)

    # t < t_HP_start_d_1 + 24 の場合
    t17 = t < t_HP_start_d_1_t + 24
    t18 = np.logical_and(np.logical_and(t13, t16), t17)
    tau_HP_cm_d_t[t18] = 0

    # t == t_HP_start_d_1 + 24 の場合
    t19 = t == t_HP_start_d_1_t + 24
    t20 = np.logical_and(np.logical_and(t13, t16), t19)
    tau_HP_cm_d_t[t20] = tau_dot_HP_cm_d_1_t[t20] - np.floor(tau_dot_HP_cm_d_1_t[t20])

    # t > t_HP_start_d_1 + 24 の場合
    t21 = t > t_HP_start_d_1_t + 24
    t22 = np.logical_and(np.logical_and(t13, t16), t21)
    tau_HP_cm_d_t[t22] = 1

    return tau_HP_cm_d_t


def get_t_HP_start_d(t_HP_stop, tau_dot_HP_cm_d):
    """日付dに沸き上げが終了する運転の沸き上げ開始時刻(-)(18)

    Args:
      Q_dot_HP_cm_d(ndarray): 沸き上げ終了時刻
      q_HP_cm_d(ndarray): 日付dにおける制御モードcmの1日当たりのヒートポンプ運転時間
      t_HP_stop: param tau_dot_HP_cm_d:
      tau_dot_HP_cm_d: 

    Returns:
      ndarray: 日付dに沸き上げが終了する運転の沸き上げ開始時刻

    """
    return t_HP_stop - (np.floor(tau_dot_HP_cm_d) + 1)


def get_tau_dot_HP_cm_d(Q_dot_HP_cm_d, q_HP_cm_d):
    """日付dにおける制御モードcmの1日当たりのヒートポンプ運転時間(19)

    Args:
      Q_dot_HP_cm_d(ndarray): 日付dにおける制御モードcmの1日当たりの沸き上げ熱量
      q_HP_cm_d(ndarray): 日付dにおける制御モードcmのヒートポンプの加熱能力

    Returns:
      ndarray: 日付dにおける制御モードcmの1日当たりのヒートポンプ運転時間

    """
    return np.minimum(24, (Q_dot_HP_cm_d * 1000) / (q_HP_cm_d * 3600))


# ============================================================================
# E.6　貯湯タンク
# ============================================================================

# ============================================================================
# E.6.1 沸き上げ熱量
# ============================================================================

def get_Q_dot_HP_cm_d(L_dashdash_d, Q_dot_loss_cm_d):
    """日付dにおける制御モードcmの1日当たりの沸き上げ熱量(MJ/d)(20)

    Args:
      L_dashdash_d(ndarray): 日付dにおける1日当たりの太陽熱補正給湯熱負荷
      Q_dot_loss_cm_d(ndarray): 日付dにおける制御モードcmの1日当たりの貯湯熱損失量

    Returns:
      ndarray: 日付dにおける制御モードcmの1日当たりの沸き上げ熱量

    """
    return L_dashdash_d + Q_dot_loss_cm_d


# ============================================================================
# E.6.2 貯湯損失熱量
# ============================================================================

def get_Q_dot_loss_cm_d(theta_tnk_eq_cm_d, theta_ex_d_Ave_d, R_tnk_test):
    """日付dにおける制御モードcmの1日当たりの貯湯熱損失量(MJ/d)(21)

    Args:
      theta_tnk_eq_cm_d(ndarray): 日付dにおける制御モードcmの等価貯湯温度
      theta_ex_d_Ave_d(ndarray): 日付dにおける日平均外気温度
      R_tnk_test(float): 貯湯タンク総括熱抵抗

    Returns:
      ndarray: 日付dにおける制御モードcmの1日当たりの貯湯熱損失量

    """
    return (theta_tnk_eq_cm_d - theta_ex_d_Ave_d) / R_tnk_test * 3600 * 24 * 10 ** (-6)


# ============================================================================
# E.6.3 等価貯湯温度
# ============================================================================

def get_theta_tnk_eq_cm1_d(theta_ex_d_Ave_d, theta_star_ex_frst, theta_star_ex_frst_upper, theta_tnk_eq_win,
                           theta_tnk_eq_frst, theta_tnk_eq_frst_upper):
    """日付dにおける制御モードcmの等価貯湯温度（℃）(22-1)

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

    return theta_tnk_eq_cm1_d


def get_theta_tnk_eq_cm2_d(theta_ex_d_Ave_d, theta_tnk_eq_cm1_d, theta_hat_bw_cm1_d, theta_hat_bw_cm2_d):
    """日付dにおける制御モードcmの等価貯湯温度（℃）(22-2)

    Args:
      theta_ex_d_Ave_d(ndarray): 日付dにおける日平均外気温度
      theta_tnk_eq_cm1_d(ndarray): 日付dにおけるファーストモードcmの等価貯湯温度
      theta_hat_bw_cm1_d(ndarray): 日付dにおけるファーストモードのM1スタンダードモード沸き上げ温度
      theta_hat_bw_cm2_d(ndarray): 日付dにおけるセカンドモードのM1スタンダードモード沸き上げ温度

    Returns:
      ndarray: 日付dにおける制御モードcmの等価貯湯温度

    """
    return (theta_tnk_eq_cm1_d - theta_ex_d_Ave_d) * (2.1 * ((theta_hat_bw_cm2_d - theta_ex_d_Ave_d) / (theta_hat_bw_cm1_d - theta_ex_d_Ave_d)) - 1.2) + theta_ex_d_Ave_d


def get_theta_tnk_eq(theta_tnk_eq_test):
    """冬期条件、着霜期条件および着霜領域（上限）における等価貯湯温度(23)

    Args:
      theta_tnk_eq_test(float): 試験時の等価貯湯温度

    Returns:
      tuple: 冬期条件、着霜期条件および着霜領域（上限）における等価貯湯温度

    """
    # 冬期条件における等価貯湯温度(23a)
    theta_tnk_eq_win = theta_tnk_eq_test

    # 着霜期条件における等価貯湯温度(23a)
    theta_tnk_eq_frst = theta_tnk_eq_test + 23

    # 着霜領域（上限）における等価貯湯温度(23a)
    theta_tnk_eq_frst_upper = theta_tnk_eq_test + 6.5

    return theta_tnk_eq_win, theta_tnk_eq_frst, theta_tnk_eq_frst_upper


def get_theta_tnk_eq_test(Q_loss_test, R_tnk_test, theta_star_ex_win):
    """試験時の等価貯湯温度(℃)(24)

    Args:
      Q_loss_test(float): 試験時の貯湯熱損失量
      R_tnk_test(float): 貯湯タンク総括熱抵抗
      theta_star_ex_win(float): 冬期条件の外気温度

    Returns:
      float: 試験時の等価貯湯温度

    """
    return Q_loss_test * (10 ** 6 / (3600 * 24)) * R_tnk_test + theta_star_ex_win

# ============================================================================
# E.7　補機
# ============================================================================

# ============================================================================
# E.7.1 消費電力量
# ============================================================================

def get_E_E_aux_cm_d_t(P_aux_HP_on_test, P_aux_HP_off_test, tau_HP_cm_d_t):
    """日付dにおける制御モードcmの1日当たりの補機の消費電力量(25)

    Args:
      theta_hat_bw_win_cm(float): 試験時のヒートポンプ停止時における補機の消費電力
      theta_hat_bw_frst_cm(float): 試験時のヒートポンプ運転時における補機の消費電力
      theta_hat_bw_win_cd_cm(ndarray): 日付dの時刻tにおける制御モードcmの1時間当たりのヒートポンプ運転時間
      P_aux_HP_on_test: param P_aux_HP_off_test:
      tau_HP_cm_d_t: returns: 日付dにおける制御モードcmの1日当たりの補機の消費電力量
      P_aux_HP_off_test: 

    Returns:
      ndarray: 日付dにおける制御モードcmの1日当たりの補機の消費電力量

    """
    return (P_aux_HP_on_test * tau_HP_cm_d_t + P_aux_HP_off_test * (1 - tau_HP_cm_d_t)) / 1000


# ============================================================================
# E.8　制御
# ============================================================================

# ============================================================================
# E.8.1 制御モード
# ============================================================================

# 表1 沸き上げ温度条件の種類
# 1st:ファーストモード
# 2st:セカンドモード


# ============================================================================
# E.8.2 沸き上げ温度
# ============================================================================

def get_theta_hat_bw_cm_d(theta_star_ex_imd, theta_star_ex_win, theta_star_ex_frst, theta_star_ex_win_cd,
                          theta_star_ex_frst_upper, theta_ex_Nave_d, theta_hat_bw_sum_cm, theta_hat_bw_imd_cm,
                          theta_hat_bw_win_cm, theta_hat_bw_frst_cm, theta_hat_bw_win_cd_cm):
    """日付dにおける制御モードcmのM1スタンダードモード沸き上げ温度（℃）(26)

    Args:
      theta_star_ex_imd(float): 中間期条件の外気温度
      theta_star_ex_win(float): 冬期条件の外気温度
      theta_star_ex_frst(float): 着霜期条件の外気温度
      theta_star_ex_win_cd(float): 寒冷地冬期条件の外気温度
      theta_star_ex_frst_upper(float): 着霜領域（上限）の外気温度
      theta_ex_Nave_d(float): 日付dにおける夜間平均外気温度
      theta_hat_bw_sum_cm(float): 制御モードcmの夏期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_imd_cm(float): 制御モードcmの中間期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cm(float): 制御モードcmの冬期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_frst_cm(float): 制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度
      theta_hat_bw_win_cd_cm(float): 制御モードcmの寒冷地冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      ndarray: 日付dにおける制御モードcmのM1スタンダードモード沸き上げ温度

    """
    theta_hat_bw_cm_d = np.zeros(365)

    f1 = theta_star_ex_imd < theta_ex_Nave_d
    f2 = np.logical_and(theta_star_ex_win < theta_ex_Nave_d, theta_ex_Nave_d <= theta_star_ex_imd)
    f3 = np.logical_and(theta_star_ex_frst_upper < theta_ex_Nave_d, theta_ex_Nave_d <= theta_star_ex_win)
    f4 = np.logical_and(theta_star_ex_frst < theta_ex_Nave_d, theta_ex_Nave_d <= theta_star_ex_frst_upper)
    f5 = np.logical_and(theta_star_ex_win_cd < theta_ex_Nave_d, theta_ex_Nave_d <= theta_star_ex_frst)
    f6 = theta_ex_Nave_d <= theta_star_ex_win_cd

    theta_hat_bw_cm_d[f1] = theta_hat_bw_sum_cm

    theta_hat_bw_cm_d[f2] = theta_hat_bw_sum_cm + (theta_ex_Nave_d[f2] - theta_star_ex_imd) / (theta_star_ex_imd - theta_star_ex_win) * (theta_hat_bw_imd_cm - theta_hat_bw_win_cm)

    theta_hat_bw_cm_d[f3] = theta_hat_bw_win_cm

    theta_hat_bw_cm_d[f4] = theta_hat_bw_frst_cm + (theta_ex_Nave_d[f4] - theta_star_ex_frst) / (theta_star_ex_frst_upper - theta_star_ex_frst) * (theta_hat_bw_win_cm - theta_hat_bw_frst_cm)

    theta_hat_bw_cm_d[f5] = theta_hat_bw_frst_cm + (theta_ex_Nave_d[f5] - theta_star_ex_frst) / (theta_star_ex_frst - theta_star_ex_win_cd) * (theta_hat_bw_frst_cm - theta_hat_bw_win_cd_cm)

    theta_hat_bw_cm_d[f6] = theta_hat_bw_win_cd_cm

    return theta_hat_bw_cm_d


def get_theta_hat_bw_sum_cm1(theta_star_bw_std):
    """制御モードcmの夏期条件におけるM1スタンダードモード沸き上げ温度（℃）(27a-1)

    Args:
      theta_star_bw_std(float): 標準条件の沸き上げ温度（

    Returns:
      float: 制御モードcmの夏期条件におけるM1スタンダードモード沸き上げ温度（

    """
    # 制御モードがファーストモードの場合
    return theta_star_bw_std


def get_theta_hat_bw_imd_cm1(theta_star_bw_std):
    """制御モードcmの中間条件におけるM1スタンダードモード沸き上げ温度（℃）(27b-1)

    Args:
      theta_star_bw_std(float): 標準条件の沸き上げ温度（

    Returns:
      float: 制御モードcmの中間条件におけるM1スタンダードモード沸き上げ温度（

    """
    # 制御モードがファーストモードの場合
    return theta_star_bw_std


def get_theta_hat_bw_win_cm1(theta_star_bw_std, theta_hat_bw_win_cm1_test):
    """制御モードcmの冬期条件におけるM1スタンダードモード沸き上げ温度（℃）(27c-1)

    Args:
      theta_star_bw_std(float): 標準条件の沸き上げ温度（
      theta_hat_bw_win_cm1_test(float): 試験時の制御モードがファーストモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      float: 制御モードcmの冬期条件におけるM1スタンダードモード沸き上げ温度（

    """
    # 制御モードがファーストモードの場合
    return np.maximum(theta_star_bw_std, theta_hat_bw_win_cm1_test)


def get_theta_hat_bw_frst_cm1(theta_star_bw_high, theta_hat_bw_win_cm1):
    """制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度（℃）(27d-1)

    Args:
      theta_star_bw_high(float): 高温条件の沸き上げ温度（
      theta_hat_bw_win_cm1(float): 制御モードがファーストモードの場合の冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      float: 制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度

    """
    # 制御モードがファーストモードの場合
    return np.minimum(theta_star_bw_high, theta_hat_bw_win_cm1 + 6)


def get_theta_hat_bw_win_cd_cm1(theta_star_bw_high, theta_hat_bw_win_cm1):
    """制御モードcmの寒冷地冬期条件におけるM1スタンダードモード沸き上げ温度（℃）(27e-1)

    Args:
      theta_star_bw_high(float): 高温条件の沸き上げ温度（
      theta_hat_bw_win_cm1: returns: 制御モードcmの寒冷地冬期条件におけるM1スタンダードモード沸き上げ温度

    Returns:
      float: 制御モードcmの寒冷地冬期条件におけるM1スタンダードモード沸き上げ温度

    """
    # 制御モードがファーストモードの場合
    return np.minimum(theta_star_bw_high, theta_hat_bw_win_cm1 + 8)


def get_theta_hat_bw_sum_cm2(theta_hat_bw_sum_cm1, theta_hat_bw_win_cm1, theta_hat_bw_win_cm2):
    """制御モードcmの夏期条件におけるM1スタンダードモード沸き上げ温度（℃）(27a-2)

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
    """制御モードcmの中間期条件におけるM1スタンダードモード沸き上げ温度（℃）(27b-2)

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
    """制御モードcmの冬期条件におけるM1スタンダードモード沸き上げ温度（℃）(27c-2)

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
    """制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度（℃）(27d-2)

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
    """制御モードcmの着霜期条件におけるM1スタンダードモード沸き上げ温度（℃）(27e-2)

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
    return 5


def get_theta_star_bw():
    """表2 沸き上げ温度条件の種類

    Args:

    Returns:
      list: E.3 沸き上げ温度条件の種類

    """
    # 表2 沸き上げ温度条件の種類
    table_2 = [
        65,  # 標準条件沸き上げ温度(℃)
        90  # 高温条件沸き上げ温度(℃)
    ]

    return table_2


# ============================================================================
# E.8.3 沸き上げ終了時刻
# ============================================================================

# 沸き上げ終了時刻
def get_t_HP_stop():
    """ """
    # 沸き上げ終了時刻は7時
    return 7


# ============================================================================
# E.9 給湯機の仕様
# ============================================================================

def get_spec(e_rtd):
    """

    Args:
      e_rtd(float): 当該給湯器の効率

    Returns:
      dict: 給湯機の仕様

    """
    spec = []

    table_3_b = get_table_3_b()

    if (e_rtd <= 2.7):
        spec = table_3_b[0]
    elif (e_rtd == 2.8):
        spec = table_3_b[1]
    elif (e_rtd == 2.9):
        spec = table_3_b[2]
    elif (e_rtd == 3.0):
        spec = table_3_b[3]
    elif (e_rtd == 3.1):
        spec = table_3_b[4]
    elif (e_rtd == 3.2):
        spec = table_3_b[5]
    elif (e_rtd == 3.3):
        spec = table_3_b[6]
    elif (e_rtd == 3.4):
        spec = table_3_b[7]
    elif (e_rtd == 3.5):
        spec = table_3_b[8]
    elif (e_rtd >= 3.6):
        spec = table_3_b[9]
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


def get_table_3_b():
    """表3（b） 給湯機の仕様の決定方法（当該給湯機の効率に応じて定まる数値を用いる場合）

    Args:

    Returns:
      list: 表3（b） 給湯機の仕様の決定方法（当該給湯機の効率に応じて定まる数値を用いる場合）

    """
    # 表3（b） 給湯機の仕様の決定方法（当該給湯機の効率に応じて定まる数値を用いる場合）
    table_3_b = [
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

    return table_3_b


def get_e_rtd():
    """e_APFからe_rtdへの換算

    Args:

    Returns:
      float: 当該給湯器の効率

    """
    # 効率の決定
    e_rtd = get_e_rtd_default()

    return e_rtd


def get_e_rtd_default():
    """規定の当該給湯機の効率

    Args:

    Returns:
      float: 規定の当該給湯器の効率

    """
    return 2.7

# 式(28-1)(28-2)はインタフェイスのヘルプに式が記載されていて、
# ユーザー自身が換算を行いe_rtdを入力するため、pyheesでこの関数の呼び出しはしない
def get_e_rtd_from_e_APF(e_APF, bath_function):
    """e_APFからe_rtdへの換算

    Args:
      e_APF(float): 日本冷凍空調工業 会標準規格 JRA4050:2007R に基づく年間給湯効率（APF）
      bath_function(str): ふろ機能の種類

    Returns:
      float: 当該給湯器の効率

    """
    # e_APFからe_rtdへの変換
    if bath_function == 'ふろ給湯機(追焚あり)':
        e_rtd = e_APF - 0.7  # (28-1)
    elif bath_function == '給湯単機能' or bath_function == 'ふろ給湯機(追焚なし)':
        e_rtd = e_APF - 0.5  # (28-2)
    else:
        raise NotImplementedError()

    # 換算値が3.6を超える場合は3.6に等しいとする
    e_rtd = min(3.6, e_rtd)

    return e_rtd


# ============================================================================
# E.10 外気温度条件
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
    """表4　外気温度

    Args:

    Returns:
      list: 表4 外気温度

    """
    # 表4 外気温度
    table_4 = [
        25,
        16,
        7,
        2,
        -7,
        5,
        -2
    ]

    return table_4


# ============================================================================
# E.11 1日当たりの太陽熱補正給湯熱負荷
# ============================================================================


def get_L_dashdash_d(L_dashdash_k_d, L_dashdash_s_d, L_dashdash_w_d, L_dashdash_b1_d, L_dashdash_b2_d, L_dashdash_ba1_d,
                     L_dashdash_ba2_d):
    """1日当たりの太陽熱補正給湯熱負荷 (29)

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
    """1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)（30a）

    Args:
      L_dashdash_k_d_t(ndarray): 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)

    """
    return np.sum(L_dashdash_k_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_s_d(L_dashdash_s_d_t):
    """1日当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/d)（30b）

    Args:
      L_dashdash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_s_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_w_d(L_dashdash_w_d_t):
    """1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)（30c）

    Args:
      L_dashdash_w_d_t(ndarray): 1時間当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_w_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_b1_d(L_dashdash_b1_d_t):
    """1日当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/d)（30d）

    Args:
      L_dashdash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_b1_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_b2_d(L_dashdash_b2_d_t):
    """1日当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/d)（30e）

    Args:
      L_dashdash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_b2_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_ba1_d(L_dashdash_ba1_d_t):
    """1日当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/d)（30f）

    Args:
      L_dashdash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_ba1_d_t.reshape((365, 24)), axis=1)


def get_L_dashdash_ba2_d(L_dashdash_ba2_d_t):
    """1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)（30g）

    Args:
      L_dashdash_ba2_d_t(ndarray): 1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      ndarray: 1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_ba2_d_t.reshape((365, 24)), axis=1)
