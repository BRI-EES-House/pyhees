# ============================================================================
# 第九章 自然エネルギー利用設備
# 第二節 液体集熱式太陽熱利用設備
# Ver.08（エネルギー消費性能計算プログラム（住宅版）Ver.0203～）
# ============================================================================

import numpy as np
import pyhees.section7_1_o as solar
import pyhees.section9_2_a as lss1
import pyhees.section9_2_b as lss2
import pyhees.section9_2_c as lss3
from pyhees.section11_2 import \
    load_solrad, \
    calc_I_s_d_t

# ============================================================================
# 6. 補正集熱量
# ============================================================================

def calc_L_sun_lss_d_t(ls_type, A_stcp, b0, b1, c_p_htm, eta_r_tank, g_htm, Gs_htm, hw_connection_type, 
                      P_alpha_sp, P_beta_sp, Theta_wtr_d, UA_hx, UA_stp, UA_tank, V_tank,
                      solrad, solar_device, solar_water_tap, Theta_ex_d_t, Theta_sw_s, L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t,
                      L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t):
    """1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (1a)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      A_stcp(float): 集熱部の有効集熱面積(m2)
      b0(float): 集熱器の集熱効率特性線図一次近似式の切片 (-)
      b1(float): 集熱器の集熱効率特性線図一次近似式の傾き (W/(m2・K))
      c_p_htm(float): 熱媒の定圧比熱 (kJ/(kg･K)) 
      eta_r_tank(float): 有効出湯効率 (%)
      g_htm(float): 単位日射量当たりの循環流量((kg/h)/(W/m2))
      Gs_htm(float): 熱媒の基準循環流量(kg/h)
      hw_connection_type(str): 給湯接続方式の種類 (-)
      P_alpha_sp(float): ソーラーシステムの太陽熱集熱部の方位角 (°)
      P_beta_sp(float): ソーラーシステムの太陽熱集熱部の傾斜角 (°)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)
      UA_tank(float): 貯湯タンクの放熱係数(W/K)
      UA_stp(float): 集熱配管の放熱係数 (W/(m.K)
      UA_hx(float): 熱交換器の伝熱係数 (-)
      V_tank(float): タンク容量 (L),
      solrad(ndarray): 日射量データ (W/m2)
      solar_device(str): 太陽熱利用設備の種類 (液体集熱式,空気集熱式)
      solar_water_tap(str): 太陽熱用水栓
      Theta_ex_d_t(ndarray): 外気温度 (℃)
      Theta_sw_s(int): 浴室シャワー水栓の基準給湯温度
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/h)
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/h)
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/h)
    """
    args = {
        'ls_type':ls_type,
        'A_stcp':A_stcp,
        'b0': b0,
        'b1': b1,
        'c_p_htm':c_p_htm,
        'eta_r_tank':eta_r_tank,
        'g_htm':g_htm,
        'Gs_htm':Gs_htm,
        'hw_connection_type':hw_connection_type,
        'P_alpha_sp':P_alpha_sp,
        'P_beta_sp':P_beta_sp,
        'Theta_wtr_d':Theta_wtr_d,
        'UA_hx':UA_hx,
        'UA_stp':UA_stp,
        'UA_tank':UA_tank,
        'V_tank':V_tank,
        'solrad': solrad,
        'solar_device': solar_device,
        'solar_water_tap': solar_water_tap,
        'Theta_ex_d_t': Theta_ex_d_t,
        'Theta_sw_s': Theta_sw_s,
        'L_dash_k_d_t':L_dash_k_d_t,
        'L_dash_s_d_t':L_dash_s_d_t,
        'L_dash_w_d_t':L_dash_w_d_t,
        'L_dash_b1_d_t':L_dash_b1_d_t,
        'L_dash_b2_d_t':L_dash_b2_d_t,
        'L_dash_ba1_d_t':L_dash_ba1_d_t
    }

    # 1時間当たりの液体集熱式太陽熱利用設備による補正集熱量を求めるために必要な変数の計算
    swh = calc_swh_variables(**args)

    # 給湯配管からの熱損失の程度を判断する基準となる、給湯配管内を流れる1時間当たりの水の質量
    M_dot_w_pipe_lim = get_M_dot_w_pipe_lim()

    # 給湯配管内流量の区分における貯湯タンクから補助熱源機までの給湯配管の熱損失率
    f_loss_pipe_tank_boiler_pw_1, f_loss_pipe_tank_boiler_pw_2 = calc_f_loss_pipe_tank_boiler_pw(ls_type, hw_connection_type)

    # 貯湯タンクから補助熱源機までの給湯配管の熱損失率 (1b)
    f_loss_pipe_tank_boiler_d_t = get_f_loss_pipe_tank_boiler_d_t(swh['M_dot_w_tank_out_d_t'], M_dot_w_pipe_lim, f_loss_pipe_tank_boiler_pw_1, f_loss_pipe_tank_boiler_pw_2)

    # 1時間当たりの貯湯タンク出湯熱量 (3)
    Q_tank_d_t = calc_Q_tank_d_t(
        swh['Theta_wtr_d_t'],
        swh['Delta_tau_w_tank_out_d_t'],
        swh['M_dot_w_tank_out_d_t'],
        swh['Theta_w_tank_mixed_d_t'],
        swh['Theta_w_tank_upper_d_t'],
        swh['t_hc_start_d'])

    # 1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (1a)
    L_sun_lss_d_t = get_L_sun_lss_d_t(f_loss_pipe_tank_boiler_d_t, Q_tank_d_t)

    return L_sun_lss_d_t


def get_L_sun_lss_d_t(f_loss_pipe_tank_boiler_d_t, Q_tank_d_t):
    """1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (1a)

    Args:
      f_loss_pipe_tank_boiler_d_t(ndarray): 貯湯タンクから補助熱源機までの給湯配管の熱損失率 (-)
      Q_tank_d_t(ndarray): 1時間当たりの貯湯タンク出湯熱量 (MJ/h)

    Returns:
      ndarray: 1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/h)
    """
    L_sun_lss_d_t = (1 - f_loss_pipe_tank_boiler_d_t) * Q_tank_d_t

    return L_sun_lss_d_t


def get_f_loss_pipe_tank_boiler_d_t(M_dot_w_tank_out_d_t, M_dot_w_pipe_lim, f_loss_pipe_tank_boiler_pw_1, f_loss_pipe_tank_boiler_pw_2):
    """貯湯タンクから補助熱源機までの給湯配管の熱損失率 (1b)

    Args:
      M_dot_w_tank_out_d_t(ndarray): 1時間当たりの貯湯タンクから出水する水の質量 (kg/h)
      M_dot_w_pipe_lim(int): 給湯配管からの熱損失の程度を判断する基準となる、給湯配管内を流れる1時間当たりの水の質量 (-)
      f_loss_pipe_tank_boiler_pw_1(float): 給湯配管内流量の区分1における貯湯タンクから補助熱源機までの給湯配管の熱損失率 (-)
      f_loss_pipe_tank_boiler_pw_2(float): 給湯配管内流量の区分2における貯湯タンクから補助熱源機までの給湯配管の熱損失率 (-)

    Returns:
      ndarray: 貯湯タンクから補助熱源機までの給湯配管の熱損失率 (-)
    """
    f_loss_pipe_tank_boiler_d_t = np.zeros(24 * 365)

    # M_dot_w_tank_out_d_t <= M_dot_w_pipe_lim の場合
    f1 = M_dot_w_tank_out_d_t <= M_dot_w_pipe_lim
    f_loss_pipe_tank_boiler_d_t[f1] = f_loss_pipe_tank_boiler_pw_1

    # M_dot_w_tank_out_d_t > M_dot_w_pipe_lim の場合
    f2 = M_dot_w_tank_out_d_t > M_dot_w_pipe_lim
    f_loss_pipe_tank_boiler_d_t[f2] = f_loss_pipe_tank_boiler_pw_2

    return f_loss_pipe_tank_boiler_d_t


def calc_swh_variables(ls_type, A_stcp, b0, b1, c_p_htm, eta_r_tank, g_htm, Gs_htm, hw_connection_type, 
                      P_alpha_sp, P_beta_sp, Theta_wtr_d, UA_hx, UA_stp, UA_tank, V_tank,
                      solrad, solar_device, solar_water_tap, Theta_ex_d_t, Theta_sw_s, L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t,
                      L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t):
    """1時間当たりの液体集熱式太陽熱利用設備による補正集熱量を求めるために必要な変数の計算

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      A_stcp(float): 集熱部の有効集熱面積(m2)
      b0(float): 集熱器の集熱効率特性線図一次近似式の切片 (-)
      b1(float): 集熱器の集熱効率特性線図一次近似式の傾き (W/(m2・K))
      c_p_htm(float): 熱媒の定圧比熱 (kJ/(kg･K)) 
      eta_r_tank(float): 有効出湯効率 (%)
      g_htm(float): 単位日射量当たりの循環流量((kg/h)/(W/m2))
      Gs_htm(float): 熱媒の基準循環流量(kg/h)
      hw_connection_type(str): 給湯接続方式の種類 (-)
      P_alpha_sp(float): ソーラーシステムの太陽熱集熱部の方位角 (°)
      P_beta_sp(float): ソーラーシステムの太陽熱集熱部の傾斜角 (°)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)
      UA_hx(float): 熱交換器の伝熱係数 (-)
      UA_stp(float): 集熱配管の放熱係数 (W/(m.K)
      UA_tank(float): 貯湯タンクの放熱係数(W/K)
      V_tank(float): タンク容量 (L),
      solar_device(str): 太陽熱利用設備の種類 (液体集熱式,空気集熱式)
      solar_water_tap(str): 太陽熱用水栓
      Theta_sw_s(int): 浴室シャワー水栓の基準給湯温度
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/h)
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/h)
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/h)

    Returns:
      dict: 1時間当たりの液体集熱式太陽熱利用設備による補正集熱量を求めるために必要な変数
    """
    # 作業領域の確保
    M_w_tank_upper_d_t = np.zeros(24 * 365)
    M_w_tank_lower_d_t = np.zeros(24 * 365)
    M_dot_w_tank_out_d_t = np.zeros(24 * 365)

    Gamma_w_tank_d_t = np.zeros(24 * 365)
    Theta_w_tank_upper_d_t = np.zeros(24 * 365)
    Theta_w_tank_lower_d_t = np.zeros(24 * 365)
    Theta_w_tank_mixed_d_t =  np.zeros(24 * 365)

    Gamma_wu_tank_upper_d_t = np.zeros(24 * 365)
    Delta_tau_w_tank_out_d_t = np.zeros(24 * 365)

    Theta_reqw_tank_d_t = np.zeros(24 * 365)
    Q_W_dmd_sun_d_t = np.zeros(24 * 365)
    r_sun_k_d_t, r_sun_s_d_t, r_sun_w_d_t, r_sun_b1_d_t, r_sun_b2_d_t, r_sun_ba1_d_t = [np.zeros(24 * 365) for _ in range(6)]

    # 仕様
    b0 = get_b0(ls_type, b0)
    b1 = get_b1(ls_type, b1)
    Gs_htm = get_Gs_htm(ls_type, Gs_htm)
    g_htm = get_g_htm(ls_type, g_htm)
    c_p_htm = get_c_p_htm(ls_type, c_p_htm)
    eta_r_tank = get_eta_r_tank(ls_type, eta_r_tank)
    UA_tank = get_UA_tank(ls_type, UA_tank)
    UA_stp = get_UA_stp(ls_type, UA_stp)
    UA_hx = get_UA_hx(ls_type, UA_hx)

    # 貯湯タンク全体の水の質量 (23)
    M_w_tank_total = get_M_w_tank_total(V_tank)

    # 集熱器の単位面積当たりの平均日射量 第十一章第二節
    I_s_d_t = calc_I_s_d_t(P_alpha_sp, P_beta_sp, solrad)

    # 集熱開始時刻 付録A (8)または付録B (7)
    t_hc_start_d = get_t_hc_start_d(ls_type, I_s_d_t)

    # 1時間当たりの集熱時間数 付録A (7)または付録B (6)
    Delta_tau_hc_d_t = get_Delta_tau_hc_d_t(ls_type, I_s_d_t)

    # 1時間当たりの熱媒の循環量 付録A (6)または付録B (5)
    G_htm_d_t = get_G_htm_d_t(ls_type, g_htm, Gs_htm, I_s_d_t, Delta_tau_hc_d_t)

    # 集熱配管の温度効率 付録A (5)または付録B (4)
    epsilon_t_stp_d_t = get_epsilon_t_stp_d_t(ls_type, c_p_htm, UA_stp, G_htm_d_t)

    # 集熱器の温度効率 付録A (4)または付録B (3)
    epsilon_t_stc_d_t = get_epsilon_t_stc_d_t(ls_type, A_stcp, b1, c_p_htm, G_htm_d_t)

    # 集熱経路の総合温度効率 (33)
    e_t_stcs_d_t = get_e_t_stcs_d_t(epsilon_t_stp_d_t, epsilon_t_stc_d_t)

    # 日平均給水温度を時間ごとに拡張
    Theta_wtr_d_t = np.repeat(Theta_wtr_d, 24)

    # 熱的平衡状態を仮定した場合の集熱経路における熱媒温度 (31)
    Theta_htm_stcs_d_t = calc_Theta_htm_stcs_d_t(b0, b1, I_s_d_t, Theta_ex_d_t, epsilon_t_stp_d_t, epsilon_t_stc_d_t, e_t_stcs_d_t)

    # 熱交換器の温度効率 付録A (1)または付録B (1)
    epsilon_t_hx_d_t = get_epsilon_t_hx_d_t(ls_type, c_p_htm, UA_hx, G_htm_d_t)

    # 集熱配管還り熱媒温度の算定に係る貯湯タンクの下層部の水の温度に対する案分比率 (34)
    Beta_htm_tank_d_t = get_Beta_htm_tank_d_t(e_t_stcs_d_t, epsilon_t_hx_d_t)

    # 集熱配管還り熱媒温度の算定に係る集熱経路に対して熱的平衡状態を仮定した場合の集熱経路における熱媒温度に対する案分比率 (35)
    Beta_htm_stcs_d_t = get_Beta_htm_stcs_d_t(e_t_stcs_d_t, epsilon_t_hx_d_t)

    # 計算タイムステップ
    Delta_t_calc = get_Delta_t_calc()

    for dt in range(24 * 365):
      # 日時が1月1日0時である場合の一時刻前における計算
      if dt == 0:
          # 一時刻前における貯湯タンク上層部の水の質量 (29)
          M_w_tank_upper_d_t[-1] = get_M_w_tank_upper_prev(M_w_tank_total)

          M_w_tank_lower_d_t[-1] = M_w_tank_total - M_w_tank_upper_d_t[-1]

          # 一時刻前における貯湯タンク上層部の水の質量 (30)
          Theta_w_tank_upper_d_t[-1] = get_Theta_w_tank_upper_prev(Theta_wtr_d)

          # 一時刻前における貯湯タンク下層部の水の温度は定義しない
          Theta_w_tank_lower_d_t[-1] = np.nan

          # 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 
          Gamma_w_tank_d_t[-1] = M_w_tank_lower_d_t[-1] / M_w_tank_total

      # 完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度 (17)
      Theta_w_tank_mixed_d_t[dt-1] = get_Theta_w_tank_mixed(Gamma_w_tank_d_t[dt-1], Theta_w_tank_upper_d_t[dt-1], Theta_w_tank_lower_d_t[dt-1])

      # Theta_w_sun_d_t == Theta_reqw_tank_d_t (27)
      Theta_reqw_tank_d_t[dt] = get_Theta_reqw_tank(Theta_w_tank_mixed_d_t[dt-1], Theta_w_tank_upper_d_t[dt-1], t_hc_start_d[dt])

      # 各用途における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合 第7章付録O.4
      r_sun_k_d_t[dt], r_sun_s_d_t[dt], r_sun_w_d_t[dt], \
          r_sun_b1_d_t[dt], r_sun_b2_d_t[dt], r_sun_ba1_d_t[dt] = solar.get_r_sun(hw_connection_type, solar_device, solar_water_tap, Theta_reqw_tank_d_t[dt], Theta_sw_s,
                                                          L_dash_b1_d_t[dt], L_dash_b2_d_t[dt], L_dash_ba1_d_t[dt])

      # 給湯熱需要のうちの太陽熱利用設備の分担分 第7章付録O.3.(2)
      Q_W_dmd_sun_d_t[dt] = solar.get_Q_W_dmd_sun_d_t(L_dash_k_d_t[dt], L_dash_s_d_t[dt], L_dash_w_d_t[dt], L_dash_b1_d_t[dt], L_dash_b2_d_t[dt], L_dash_ba1_d_t[dt],
                            r_sun_k_d_t[dt], r_sun_s_d_t[dt], r_sun_w_d_t[dt], r_sun_b1_d_t[dt], r_sun_b2_d_t[dt], r_sun_ba1_d_t[dt])

      # 当該時刻を含む過去6時間の平均外気温度
      Theta_ex_p6h_Ave = get_Theta_ex_p6h_Ave(ls_type, Theta_ex_d_t, dt)

      # 貯湯タンクからの出水時間数 (28)
      Delta_tau_w_tank_out_d_t[dt] = calc_Delta_tau_w_tank_out(ls_type, Theta_wtr_d_t[dt], Theta_ex_p6h_Ave, Q_W_dmd_sun_d_t[dt], Theta_w_tank_mixed_d_t[dt-1], Theta_w_tank_upper_d_t[dt-1], t_hc_start_d[dt])

      # 貯湯タンク上層部の水の使用率 (25)
      Gamma_wu_tank_upper_d_t[dt] = calc_Gamma_wu_tank_upper(ls_type, hw_connection_type,
                                  Theta_wtr_d_t[dt], Q_W_dmd_sun_d_t[dt], M_w_tank_total, M_w_tank_upper_d_t[dt-1], Theta_w_tank_mixed_d_t[dt-1], Theta_w_tank_upper_d_t[dt-1], 
                                  Delta_tau_w_tank_out_d_t[dt], t_hc_start_d[dt])

      # 貯湯タンクから出水する水の質量 (5)
      M_dot_w_tank_out_d_t[dt] = get_M_dot_w_tank_out(Gamma_wu_tank_upper_d_t[dt], M_w_tank_upper_d_t[dt-1], Delta_t_calc)

      # 入水・出水後の貯湯タンク上層部の水の質量 (18)
      M_w_tank_upper_d_t[dt] = get_M_w_tank_upper(M_w_tank_total, Gamma_wu_tank_upper_d_t[dt], M_dot_w_tank_out_d_t[dt], M_w_tank_upper_d_t[dt-1], M_w_tank_lower_d_t[dt-1], Gamma_w_tank_d_t[dt-1], t_hc_start_d[dt], Delta_t_calc)

      # 入水・出水後の貯湯タンク下層部の水の質量 (19)
      M_w_tank_lower_d_t[dt] = get_M_w_tank_lower(M_w_tank_total, M_w_tank_upper_d_t[dt])

      # 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (22)
      Gamma_w_tank_d_t[dt] = get_Gamma_w_tank(M_w_tank_total,  M_w_tank_lower_d_t[dt])

      # 入水・出水後の貯湯タンク上層部の水の温度 (6)
      # 入水・出水後の貯湯タンク下層部の水の温度 (7)
      Theta_w_tank_upper_d_t[dt], Theta_w_tank_lower_d_t[dt] = calc_Theta_w_tank(c_p_htm, eta_r_tank, 
                      Theta_wtr_d_t[dt], UA_tank, M_w_tank_total, Gamma_w_tank_d_t[dt], Gamma_w_tank_d_t[dt-1], M_w_tank_upper_d_t[dt], 
                      M_dot_w_tank_out_d_t[dt], M_w_tank_lower_d_t[dt], M_w_tank_lower_d_t[dt-1], Theta_w_tank_mixed_d_t[dt-1], Theta_w_tank_upper_d_t[dt-1],
                      Theta_w_tank_lower_d_t[dt-1], Gamma_wu_tank_upper_d_t[dt], Delta_tau_w_tank_out_d_t[dt], t_hc_start_d[dt],
                      Theta_htm_stcs_d_t[dt], Beta_htm_stcs_d_t[dt], Beta_htm_tank_d_t[dt], epsilon_t_hx_d_t[dt], G_htm_d_t[dt], Theta_ex_d_t[dt], Delta_tau_hc_d_t[dt])

    return {
        'Theta_wtr_d_t': Theta_wtr_d_t,
        'Delta_tau_w_tank_out_d_t': Delta_tau_w_tank_out_d_t,
        'M_dot_w_tank_out_d_t': M_dot_w_tank_out_d_t,
        'Theta_w_tank_mixed_d_t': Theta_w_tank_mixed_d_t,
        'Theta_w_tank_upper_d_t': Theta_w_tank_upper_d_t,
        't_hc_start_d': t_hc_start_d,
        'Theta_reqw_tank_d_t': Theta_reqw_tank_d_t
    }


# ============================================================================
# 7. 補機の消費電力量
# ============================================================================

def calc_E_E_lss_aux_d_t(region, sol_region, ls_type, P_pump_hc, P_pump_non_hc, P_alpha_sp, P_beta_sp):
    """1時間当たりの補機の消費電力量 (2)

    Args:
      region(int): 省エネルギー地域区分 (-)
      sol_region(int): 年間の日射地域区分 (-)
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      P_pump_hc(float): 集熱時における循環ポンプの消費電力量 (W) [入力/固定]
      P_pump_non_hc(float): 非集熱時における循環ポンプの消費電力量 (W) [入力/固定]
      P_alpha_sp(float): 太陽熱集熱部の方位角 (°)
      P_beta_sp(float): 太陽熱集熱部の傾斜角 (°)

    Returns:
      ndarray: 1時間当たりの補機の消費電力量 (kWh/h)
    """
    if ls_type in ['密閉形太陽熱温水器（直圧式）', 'ソーラーシステム', '開放形太陽熱温水器']:
        # 1時間当たりの循環ポンプの消費電力量 (36)
        E_E_lss_aux_d_t = calc_E_pump_d_t(region, sol_region, ls_type, P_pump_hc, P_pump_non_hc, P_alpha_sp, P_beta_sp)
        return E_E_lss_aux_d_t
    else:
        raise ValueError(ls_type)


# ============================================================================
# 8. 貯湯部
# ============================================================================

# ============================================================================
# 8.1 貯湯タンク出湯熱量
# ============================================================================

def calc_Q_tank_d_t(Theta_wtr_d_t, Delta_tau_w_tank_out_d_t, M_dot_w_tank_out_d_t, Theta_w_tank_mixed_d_t, Theta_w_tank_upper_d_t, t_hc_start_d):
    """1時間当たりの貯湯タンク出湯熱量 (MJ/h) (3)

    Args:
      Theta_wtr_d_t(ndarray): 日平均給水温度 (℃)
      Delta_tau_w_tank_out_d_t(ndarray): 貯湯タンクの放熱係数(W/K)
      M_dot_w_tank_out_d_t(ndarray): 集熱配管の放熱係数 (W/(m.K)
      Theta_w_tank_mixed_d_t(ndarray): 熱交換器の伝熱係数 (-)
      Theta_w_tank_upper_d_t(ndarray): タンク容量 (L)
      t_hc_start_d(ndarray): 集熱開始時刻 (-)

    Returns:
      ndarray: 1時間当たりの貯湯タンク出湯熱量( MJ/h)
    """
    # 水の定圧比熱
    c_p_water = get_c_p_water()

    Q_tank_d_t = np.zeros(24 * 365)

    # Delta_tau_w_tank_out_d_t == 0の場合
    f1 = Delta_tau_w_tank_out_d_t == 0
    Q_tank_d_t[f1] = 0

    # Delta_tau_w_tank_out_d_t > 0の場合
    f2 = Delta_tau_w_tank_out_d_t > 0

    # 貯湯タンクから出水する水の温度
    Theta_w_tank_out_d_t = get_Theta_w_tank_out_d_t(Delta_tau_w_tank_out_d_t, Theta_w_tank_mixed_d_t, Theta_w_tank_upper_d_t, t_hc_start_d)

    Q_tank_d_t[f2] = c_p_water * M_dot_w_tank_out_d_t[f2] * (Theta_w_tank_out_d_t[f2] - Theta_wtr_d_t[f2] ) * 10 ** (-3)

    return Q_tank_d_t


# ============================================================================
# 8.2 貯湯タンクから出水する水の温度
# ============================================================================

def get_Theta_w_tank_out_d_t(Delta_tau_w_tank_out_d_t, Theta_w_tank_mixed_d_t, Theta_w_tank_upper_d_t, t_hc_start_d):
    """貯湯タンクから出水する水の温度 (℃) (4)

    Args:
      Delta_tau_w_tank_out_d_t(ndarray): 貯湯タンクの放熱係数(W/K)
      Theta_w_tank_mixed_d_t(ndarray): 熱交換器の伝熱係数 (-)
      Theta_w_tank_upper_d_t(ndarray): タンク容量 (L)
      t_hc_start_d(ndarray): 集熱開始時刻  (-)

    Returns:
      ndarray: 貯湯タンクから出水する水の温度( ℃)
    """
    Theta_w_tank_out_d_t = np.zeros(24 * 365)

    # (4-1)
    # Delta_tau_w_tank_out_d_t > 0 and t_hc_start_d == 1 の場合
    f1 = np.logical_and(Delta_tau_w_tank_out_d_t > 0, t_hc_start_d == 1)
    Theta_w_tank_mixed_d_t_prev = np.roll(Theta_w_tank_mixed_d_t, 1)
    Theta_w_tank_out_d_t[f1] = Theta_w_tank_mixed_d_t_prev[f1]

    # (4-2)
    # Delta_tau_w_tank_out_d_t > 0 and t_hc_start_d == 0 の場合
    f2 = np.logical_and(Delta_tau_w_tank_out_d_t > 0, t_hc_start_d == 0)
    Theta_w_tank_upper_d_t_prev = np.roll(Theta_w_tank_upper_d_t, 1)
    Theta_w_tank_out_d_t[f2] =Theta_w_tank_upper_d_t_prev[f2]

    # 貯湯タンクからの出水がない場合は定義しない
    f3 = Delta_tau_w_tank_out_d_t == 0
    Theta_w_tank_out_d_t[f3] = np.nan

    return Theta_w_tank_out_d_t


# ============================================================================
# 8.3 貯湯タンクの水の温度
# ============================================================================

def get_M_dot_w_tank_out(Gamma_wu_tank_upper, M_w_tank_upper_prev, Delta_t_calc):
    """貯湯タンクから出水する水の質量 (kg/h) (5)

    Args:
      Gamma_wu_tank_upper(float): 貯湯タンク上層部の水の使用率 (-)
      M_w_tank_upper_prev(float): 1時間前の貯湯タンク上層部の水の質量 (kg)
      Delta_t_calc(int): 計算タイムステップ

    Returns:
      float: 貯湯タンクから出水する水の質量 (kg/h)
    """
    return (Gamma_wu_tank_upper * M_w_tank_upper_prev / Delta_t_calc)


# ============================================================================
# 8.4 貯湯タンクから出水する水の質量
# ============================================================================

def calc_Theta_w_tank(c_p_htm, eta_r_tank, Theta_wtr, UA_tank,
                      M_w_tank_total, Gamma_w_tank, Gamma_w_tank_prev, M_w_tank_upper, M_w_tank_out, M_w_tank_lower, M_w_tank_lower_prev,
                      Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, Theta_w_tank_lower_prev, Gamma_wu_tank_upper,
                      Delta_tau_w_tank_out, t_hc_start_d, Theta_htm_stcs, Beta_htm_stcs, Beta_htm_tank, epsilon_t_hx, G_htm, Theta_ex, Delta_tau_hc):
    """貯湯タンクの水の温度 (6) (7)

    Args:
      c_p_htm(float): 熱媒の定圧比熱 (kJ/(kg･K)) 
      eta_r_tank(float): 有効出湯効率 (%)
      Theta_wtr(float): 日平均給水温度 (℃)
      UA_tank(float): 貯湯タンクの放熱係数(W/K)
      M_w_tank_total(float): 貯湯タンク全体の水の質量  (kg)
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
      Gamma_w_tank_prev(float): 1時間前の入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
      M_w_tank_upper(float): 入水・出水後の貯湯タンク上層部の水の質量 (kg)
      M_w_tank_out(float): 貯湯タンクから出水する水の質量 (kg)
      M_w_tank_lower(float): 入水・出水後の貯湯タンク下層部の水の質量 (kg)
      M_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の質量 (kg)
      Theta_w_tank_mixed_prev(float): 1時間前の完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度 (℃)
      Theta_w_tank_upper_prev(float): 1時間前の入水・出水後の貯湯タンク上層部の水の温度 (℃)
      Theta_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の温度 (℃)
      Gamma_wu_tank_upper(float): 貯湯タンク上層部の水の使用率 (-)
      Delta_tau_w_tank_out(float): 貯湯タンクからの出水時間数 (h/h)
      t_hc_start_d(float): 集熱開始時刻 (-)
      Theta_htm_stcs(float): 熱的平衡状態を仮定した場合の集熱経路における熱媒温度 (℃)
      Beta_htm_stcs(float): 集熱配管還り熱媒温度の算定に係る集熱経路に対して熱的平衡状態を仮定した場合の集熱経路における熱媒温度に対する案分比率 (-)
      Beta_htm_tank(float): 集熱配管還り熱媒温度の算定に係る貯湯タンクの下層部の水の温度に対する案分比率 (-)
      epsilon_t_hx(float): 熱交換器の温度効率 (-)
      G_htm(float): 熱媒の循環量 (kg/h)
      Theta_ex(float): 外気温度 (℃)
      Delta_tau_hc(int): 集熱時間数 (h/h)

    Returns:
      tuple: 入水・出水後の貯湯タンク上層部の水の温度 (℃), 入水・出水後の貯湯タンク下層部の水の温度 (℃)
    """
    # 貯湯タンク全体の水の質量
    M_w_tank_mix = calc_M_w_tank_mix(eta_r_tank, M_w_tank_total, Gamma_w_tank, Delta_tau_w_tank_out, Delta_tau_hc)

    # 集熱量のうち貯湯タンク下層部で熱交換される割合
    Gamma_hx_tank = calc_Gamma_hx_tank(Gamma_w_tank)

    # 水の定圧比熱
    c_p_water = get_c_p_water()

    # 計算タイムステップ
    Delta_t_calc = get_Delta_t_calc()

    # 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素
    at_11, at_12, at_21, at_22 = get_at(c_p_htm, UA_tank, M_w_tank_mix, Gamma_w_tank, M_w_tank_upper, M_w_tank_lower, Gamma_hx_tank, G_htm, epsilon_t_hx, 
                   Beta_htm_tank, c_p_water, Delta_t_calc)

    # 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の行列式
    detA = get_detA(at_11, at_12, at_21, at_22)

    # 連立方程式を行列表現した場合の日付の時刻における定数項ベクトルの要素 
    bt_1, bt_2 = calc_bt(c_p_htm, Theta_wtr, UA_tank, Gamma_w_tank, Gamma_w_tank_prev, M_w_tank_upper, M_w_tank_out, M_w_tank_lower, M_w_tank_lower_prev,
                  Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, Theta_w_tank_lower_prev, Gamma_wu_tank_upper, Gamma_hx_tank, G_htm, epsilon_t_hx,
                  Theta_htm_stcs, Beta_htm_stcs, c_p_water, Delta_t_calc, t_hc_start_d, Theta_ex)

    # 入水・出水後の貯湯タンク上層部の水の温度 (6)
    # 入水・出水後の貯湯タンク下層部の水の温度 (7)
    Theta_w_tank_upper_dt, Theta_w_tank_lower_dt = get_Theta_w_tank(Theta_wtr, Gamma_w_tank, at_11, at_12, at_21, at_22, detA, bt_1, bt_2)

    return Theta_w_tank_upper_dt, Theta_w_tank_lower_dt


def get_Theta_w_tank(Theta_wtr, Gamma_w_tank, at_11, at_12, at_21, at_22, detA, bt_1, bt_2):
    """貯湯タンクの水の温度 (6) (7)

    Args:%)
      Theta_wtr(float): 日平均給水温度 (℃)
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
      Gamma_w_tank_prev(float): 1時間前の入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
      at_11(float): 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 (-)
      at_12(float): 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 (-)
      at_21(float): 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 (-)
      at_22(float): 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 (-)
      detA(float): 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の行列式 (-)
      bt_1(float): 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 (-)
      bt_2(float): 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 (-)

    Returns:
      tuple: 入水・出水後の貯湯タンク上層部の水の温度 (℃), 入水・出水後の貯湯タンク下層部の水の温度 (℃)
    """
    Theta_w_tank_upper_dt = 0
    Theta_w_tank_lower_dt = 0

    if Gamma_w_tank == 0:
        # 入水・出水後の貯湯タンク下層部の水の温度は定義しない
        Theta_w_tank_lower_dt = np.nan

        f1 = at_11 == 0
        if f1: 
          # (6-1)
          Theta_w_tank_upper_dt = Theta_wtr

        f2 = at_11 != 0
        if f2:
          # (6-1)
          Theta_w_tank_upper_dt = bt_1 / at_11

    elif Gamma_w_tank > 0:
        f1 = detA <= 1
        if f1:
          # (6-2)
          Theta_w_tank_upper_dt = Theta_wtr
          # (7)
          Theta_w_tank_lower_dt = Theta_wtr

        f2 = detA > 1
        if f2:
          # (6-2)
          Theta_w_tank_upper_dt = (1 / detA) * (at_22 * bt_1 - at_12 * bt_2)
          # (7)
          Theta_w_tank_lower_dt = (1 / detA) * (-at_21 * bt_1 + at_11 * bt_2)

    return Theta_w_tank_upper_dt, Theta_w_tank_lower_dt


def get_detA(at_11, at_12, at_21, at_22):
    """連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の行列式 (-) (8)

    Args:
      at_11(float): 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 at_11
      at_12(float): 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 at_12
      at_21(float): 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 at_21
      at_22(float): 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 at_22

    Returns:
      float: 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の行列式 (-) 
    """
    return at_11 * at_22 - at_12 * at_21


def get_at(c_p_htm, UA_tank, M_w_tank_mix, Gamma_w_tank, M_w_tank_upper, M_w_tank_lower, Gamma_hx_tank, G_htm, epsilon_t_hx,
            Beta_htm_tank, c_p_water, Delta_t_calc):
    """連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 (-) (9) (10) (11) (12)

    Args:
      c_p_htm(float): 熱媒の定圧比熱 (kJ/(kg･K)) 
      UA_tank(float): 貯湯タンクの放熱係数 (W/K)
      M_w_tank_mix(float): 貯湯タンクから出水する水の質量 (kg/h)
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
      M_w_tank_upper(float): 入水・出水後の貯湯タンク上層部の水の質量 (kg)
      Gamma_hx_tank(float): 集熱量のうち貯湯タンク下層部で熱交換される割合 (-)
      G_htm(float): 1時間当たりの熱媒の循環量 (kg/h)
      epsilon_t_hx(float): 熱交換器の温度効率 (-)
      Beta_htm_tank(float): 集熱配管還り熱媒温度の算定に係る貯湯タンクの下層部の水の温度に対する案分比率 (-)
      c_p_water(float): 水の定圧比熱 (kJ/(kg･K))
      Delta_t_calc(float): 計算タイムステップ (-)

    Returns:
      tuple: 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 at_11, at_12, at_21, at_22 (-) 
    """
    # (9)
    at_11 = (c_p_water * M_w_tank_upper) / Delta_t_calc + 3.6 * (1 - Gamma_w_tank) * UA_tank + c_p_water * M_w_tank_mix + (1 - Gamma_hx_tank) ** 2 * c_p_htm * G_htm * epsilon_t_hx * (1 - Beta_htm_tank)

    # (10)
    at_12 = -c_p_water * M_w_tank_mix + Gamma_hx_tank * (1 - Gamma_hx_tank) * c_p_htm * G_htm * epsilon_t_hx * (1 - Beta_htm_tank)

    # (11)
    at_21 = -c_p_water * M_w_tank_mix + Gamma_hx_tank * (1 - Gamma_hx_tank) * c_p_htm * G_htm * epsilon_t_hx * (1 - Beta_htm_tank)

    # (12)
    at_22 = (c_p_water * M_w_tank_lower) / Delta_t_calc + 3.6 * Gamma_w_tank * UA_tank + c_p_water * M_w_tank_mix + (Gamma_hx_tank) ** 2 * c_p_htm * G_htm * epsilon_t_hx * (1 - Beta_htm_tank)

    return at_11, at_12, at_21, at_22


def calc_bt(c_p_htm, Theta_wtr, UA_tank, Gamma_w_tank, Gamma_w_tank_prev, M_w_tank_upper, M_w_tank_out, M_w_tank_lower, M_w_tank_lower_prev,
            Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, Theta_w_tank_lower_prev, Gamma_wu_tank_upper, Gamma_hx_tank, G_htm, epsilon_t_hx,
            Theta_htm_stcs, Beta_htm_stcs, c_p_water, Delta_t_calc, t_hc_start_d, Theta_ex):
    """連立方程式を行列表現した場合の日付の時刻における定数項ベクトルの要素 (-) (13) (14)

    Args:
      c_p_htm(float): 熱媒の定圧比熱 (kJ/(kg･K)) 
      Theta_wtr(float): 日平均給水温度 (℃)
      UA_tank(float): 貯湯タンクの放熱係数 (W/K)
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
      Gamma_w_tank_prev(float): 1時間前の入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
      M_w_tank_upper(float): 入水・出水後の貯湯タンク上層部の水の質量 (kg)
      M_w_tank_out(float): 貯湯タンクから出水する水の質量 (kg/h)
      M_w_tank_lower(float): 入水・出水後の貯湯タンク下層部の水の質量 (kg)
      M_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の質量 (kg)
      Theta_w_tank_mixed_prev(float): 1時間前の完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度 (℃)
      Theta_w_tank_upper_prev(float): 1時間前の入水・出水後の貯湯タンク上層部の水の温度 (℃)
      Theta_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の温度 (℃)
      Gamma_wu_tank_upper(float): 貯湯タンク上層部の水の使用率 (-)
      Gamma_hx_tank(float): 集熱量のうち貯湯タンク下層部で熱交換される割合 (-)
      G_htm(float): 1時間当たりの熱媒の循環量 (kg/h)
      epsilon_t_hx(float): 熱交換器の温度効率 (-)
      Theta_htm_stcs(float): 熱的平衡状態を仮定した場合の集熱経路における熱媒温度 (℃)
      Beta_htm_stcs(float): 集熱配管還り熱媒温度の算定に係る集熱経路に対して熱的平衡状態を仮定した場合の集熱経路における熱媒温度に対する案分比率 (-)
      c_p_water(float): 水の定圧比熱 (kJ/(kg･K))
      Delta_t_calc(float): 計算タイムステップ (-)
      t_hc_start_d(float): 集熱開始時刻 (-)
      Theta_ex(float): 外気温度 (℃)

    Returns:
      tuple: 連立方程式を行列表現した場合の日付の時刻における定数項ベクトルの要素 bt_1, bt_2 (-) 
    """
    # 入水・出水後に熱的平衡状態となる前の貯湯タンク上層部の水が有する熱量(0℃基準
    Q_star_w_tank_upper, Q_star_w_tank_lower = get_Q_star_w_tank(
                          Theta_wtr, M_w_tank_upper, M_w_tank_out, M_w_tank_lower, M_w_tank_lower_prev,
                          Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, Theta_w_tank_lower_prev, 
                          Gamma_w_tank, Gamma_w_tank_prev, Gamma_wu_tank_upper, t_hc_start_d, c_p_water, Delta_t_calc
    )

    # 連立方程式を行列表現した場合の日付の時刻における定数項ベクトルの要素 (13) (14)
    bt_1, bt_2 = get_bt(c_p_htm, UA_tank, Gamma_w_tank, Gamma_hx_tank, G_htm, epsilon_t_hx,
                        Theta_htm_stcs, Beta_htm_stcs, Delta_t_calc, Theta_ex, Q_star_w_tank_upper, Q_star_w_tank_lower)

    return bt_1, bt_2


def get_bt(c_p_htm, UA_tank, Gamma_w_tank, Gamma_hx_tank, G_htm, epsilon_t_hx,
            Theta_htm_stcs, Beta_htm_stcs, Delta_t_calc, Theta_ex, Q_star_w_tank_upper, Q_star_w_tank_lower):
    """連立方程式を行列表現した場合の日付の時刻における定数項ベクトルの要素 (-) (13) (14)

    Args:
      c_p_htm(float): 熱媒の定圧比熱 (kJ/(kg･K)) 
      UA_tank(float): 貯湯タンクの放熱係数 (W/K)
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
      Gamma_hx_tank(float): 集熱量のうち貯湯タンク下層部で熱交換される割合 (-)
      G_htm(float): 1時間当たりの熱媒の循環量 (kg/h)
      epsilon_t_hx(float): 熱交換器の温度効率 (-)
      Theta_htm_stcs(float): 熱的平衡状態を仮定した場合の集熱経路における熱媒温度 (℃)
      Beta_htm_stcs(float): 集熱配管還り熱媒温度の算定に係る集熱経路に対して熱的平衡状態を仮定した場合の集熱経路における熱媒温度に対する案分比率 (-)
      Delta_t_calc(float): 計算タイムステップ (-)
      Theta_ex(float): 外気温度 (℃)
      Q_star_w_tank_upper(float): 入水・出水後に熱的平衡状態となる前の貯湯タンク上層部の水が有する熱量 (kJ)
      Q_star_w_tank_upper(float): 入水・出水後に熱的平衡状態となる前の貯湯タンク下層部の水が有する熱量 (kJ)

    Returns:
      tuple: 連立方程式を行列表現した場合の日付の時刻における定数項ベクトルの要素 bt_1, bt_2 (-) 
    """
    # (13)
    bt_1 = (Q_star_w_tank_upper / Delta_t_calc) + 3.6 * (1 - Gamma_w_tank) * UA_tank * Theta_ex + (1 - Gamma_hx_tank) * c_p_htm * G_htm * epsilon_t_hx * Beta_htm_stcs * Theta_htm_stcs

    # (14)
    bt_2 = (Q_star_w_tank_lower / Delta_t_calc) + 3.6 * Gamma_w_tank * UA_tank * Theta_ex + Gamma_hx_tank * c_p_htm * G_htm * epsilon_t_hx * Beta_htm_stcs * Theta_htm_stcs

    return bt_1, bt_2


def get_Q_star_w_tank(Theta_wtr, M_w_tank_upper, M_w_tank_out, M_w_tank_lower, M_w_tank_lower_prev, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, Theta_w_tank_lower_prev,
                       Gamma_w_tank, Gamma_w_tank_prev, Gamma_wu_tank_upper, t_hc_start_d, c_p_water, Delta_t_calc):
    """入水・出水後に熱的平衡状態となる前の貯湯タンク上層部と下層部の水が有する熱量(0℃基準) (kJ) (15) (16)

    Args:
    Theta_wtr(float): 日平均給水温度 (℃)
    M_w_tank_upper(float): 入水・出水後の貯湯タンク上層部の水の質量 (kg)
    M_w_tank_out(float): 貯湯タンクから出水する水の質量 (kg/h)
    M_w_tank_lower(float): 入水・出水後の貯湯タンク下層部の水の質量 (kg)
    M_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の質量 (kg)
    Theta_w_tank_mixed_prev(float): 1時間前の完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度 (℃)
    Theta_w_tank_upper_prev(float): 1時間前の入水・出水後の貯湯タンク上層部の水の温度 (℃)
    Theta_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の温度 (℃)
    Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
    Gamma_w_tank_prev(float): 1時間前の入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
    Gamma_wu_tank_upper(float): 貯湯タンク上層部の水の使用率 (-)
    t_hc_start_d(float): 集熱開始時刻 (-)
    c_p_water(float): 水の定圧比熱 (kJ/(kg･K))
    Delta_t_calc(float): 熱交換器の温度効率 (-)

    Returns:
      (float, float): 入水・出水後に熱的平衡状態となる前の貯湯タンク上層部の水が有する熱量 (kJ), 入水・出水後に熱的平衡状態となる前の貯湯タンク下層部の水が有する熱量 (kJ) 
    """
    Q_star_w_tank_upper = 0
    Q_star_w_tank_lower = 0

    if Gamma_w_tank == 0:
        f1 =  Gamma_wu_tank_upper == 1
        if f1:
          # (15 -1)
          Q_star_w_tank_upper = c_p_water * M_w_tank_upper * Theta_wtr
          # (16 -1)
          Q_star_w_tank_lower = 0

        f2 =  Gamma_wu_tank_upper < 1
        if f2:
          # (15 -2)
          Q_star_w_tank_upper = c_p_water * M_w_tank_upper * Theta_w_tank_mixed_prev
          # (16 -2)
          Q_star_w_tank_lower = 0

    elif Gamma_w_tank > 0 :
        f1 = Gamma_wu_tank_upper == 1
        if f1:
          # (15-3)
          Q_star_w_tank_upper = c_p_water * M_w_tank_upper * Theta_w_tank_lower_prev
          # (16-3)
          Q_star_w_tank_lower = c_p_water * M_w_tank_lower * Theta_wtr

        f2 =  Gamma_wu_tank_upper < 1
        if f2:
          f3 = t_hc_start_d == 1 or Gamma_w_tank_prev == 0
          if f3:
            # (15-4)
            Q_star_w_tank_upper = c_p_water * M_w_tank_upper * Theta_w_tank_mixed_prev
            # (16-4)
            Q_star_w_tank_lower = c_p_water * M_w_tank_out * Theta_wtr * Delta_t_calc

          f4 = t_hc_start_d == 0 and Gamma_w_tank_prev > 0
          if f4:
            # (15-5)
            Q_star_w_tank_upper = c_p_water * M_w_tank_upper * Theta_w_tank_upper_prev
            # (16-5)
            Q_star_w_tank_lower = c_p_water * (M_w_tank_lower_prev * Theta_w_tank_lower_prev + M_w_tank_out * Delta_t_calc * Theta_wtr)

    return Q_star_w_tank_upper, Q_star_w_tank_lower


def get_Theta_w_tank_mixed(Gamma_w_tank, Theta_w_tank_upper, Theta_w_tank_lower):
    """完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度 (℃) (17)

    Args:
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
      Theta_w_tank_upper(float): 入水・出水後の貯湯タンク上層部の水の温度 (℃)
      Theta_w_tank_lower(float): 入水・出水後の貯湯タンク下層部の水の温度 (℃)

    Returns:
      float: 完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度 (℃)
    """
    if Gamma_w_tank == 0:
      # (17-1)
      return Theta_w_tank_upper
    elif Gamma_w_tank > 0:
      # (17-2)
      return ((1 - Gamma_w_tank) * Theta_w_tank_upper + Gamma_w_tank * Theta_w_tank_lower)


# ============================================================================
# 8.5 貯湯タンクの水の質量
# ============================================================================

def get_M_w_tank_upper(M_w_tank_total, Gamma_wu_tank_upper, M_w_tank_out, M_w_tank_upper_prev, M_w_tank_lower_prev, Gamma_w_tank_prev, t_hc_start_d, Delta_t_calc):
    """入水・出水後の貯湯タンク上層部の水の質量 (kg) (18)

    Args:
      M_w_tank_total(int): 貯湯タンク上層部の水の使用率 (-)
      Gamma_wu_tank_upper(float): 貯湯タンク上層部の水の使用率 (-)
      M_w_tank_out(float): 貯湯タンクから出水する水の質量 (kg/h)
      M_w_tank_upper_prev(float): 1時間前の入水・出水後の貯湯タンク上層部の水の質量 (kg)
      M_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の質量 (kg)
      Gamma_w_tank_prev(float): 1時間前の入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
      t_hc_start_d(int): 集熱開始時刻 (-)
      Delta_t_calc(int): 計算タイムステップ

    Returns:
      float: 入水・出水後の貯湯タンク上層部の水の質量 (kg)
    """
    M_w_tank_upper = 0

    if Gamma_wu_tank_upper == 1:
        if t_hc_start_d == 1 or Gamma_w_tank_prev == 0:
            # (18-1)
            M_w_tank_upper = M_w_tank_total
        elif t_hc_start_d == 0 and Gamma_w_tank_prev > 0:
            # (18-2)
            M_w_tank_upper = M_w_tank_lower_prev
    elif Gamma_wu_tank_upper < 1:
        if t_hc_start_d == 1 or Gamma_w_tank_prev == 0:
            # (18-3)
            M_w_tank_upper = M_w_tank_total - M_w_tank_out * Delta_t_calc
        elif t_hc_start_d == 0 and  Gamma_w_tank_prev > 0:
            # (18-4)
            M_w_tank_upper = M_w_tank_upper_prev - M_w_tank_out * Delta_t_calc

    return  M_w_tank_upper


def get_M_w_tank_lower(M_w_tank_total, M_w_tank_upper):
    """入水・出水後の貯湯タンク下層部の水の質量 (kg) (19)

    Args:
      M_w_tank_total(float): 貯湯タンク全体の水の質量 (kg)
      M_w_tank_upper(float): 入水・出水後の貯湯タンク上層部の水の質量 (kg)

    Returns:
      float: 入水・出水後の貯湯タンク下層部の水の質量 (kg) 
    """
    return M_w_tank_total - M_w_tank_upper


def calc_M_w_tank_mix(eta_r_tank, M_w_tank_total, Gamma_w_tank, Delta_tau_w_tank_out, Delta_tau_hc):
    """貯湯タンク全体の水の質量 (kg) (20)

    Args:
      eta_r_tank(float): 有効出湯効率 (%)
      M_w_tank_total(float): 貯湯タンク全体の水の質量 (kg)
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
      Delta_tau_w_tank_out(float): 貯湯タンクからの出水時間数 (h/h)
      Delta_tau_hc(int): 集熱時間数 (h/h)

    Returns:
      ndarray: 貯湯タンク全体の水の質量 (kg) 
    """
    # 1時間当たりの貯湯タンクの上層部・下層部間での混合回数
    n_w_tank_mix = calc_n_w_tank_mix(eta_r_tank, Gamma_w_tank, Delta_tau_w_tank_out, Delta_tau_hc)

    return n_w_tank_mix * M_w_tank_total


def calc_n_w_tank_mix(eta_r_tank, Gamma_w_tank, Delta_tau_w_tank_out, Delta_tau_hc):
    """1時間当たりの貯湯タンクの上層部・下層部間での混合回数 (回/h) (21)

    Args:
      eta_r_tank(float): 有効出湯効率 (%)
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
      Delta_tau_w_tank_out(float): 貯湯タンクからの出水時間数 (h/h)
      Delta_tau_hc(int): 集熱時間数 (h/h)

    Returns:
      ndarray: 1時間当たりの貯湯タンクの上層部・下層部間での混合回数 (回/h)
    """
    n_w_tank_mix = 0

    if Gamma_w_tank == 0:
      # (21-1)
      n_w_tank_mix = 0

    if Gamma_w_tank > 0:
        if Delta_tau_hc > 0:
          # 集熱時における混合回数
          n_w_tank_mix_hc = get_n_w_tank_mix_hc()

          # (21-2a)
          n_w_tank_mix = n_w_tank_mix_hc

        elif Delta_tau_hc == 0:
          # 非集熱時であって貯湯タンクからの出水がある場合の混合回数
          n_w_tank_mix_non_hc_out = get_n_w_tank_mix_non_hc_out(eta_r_tank)

          if Delta_tau_w_tank_out == 0:
            # 非集熱時であって貯湯タンクからの出水がない場合の混合回数
            n_w_tank_mix_non_hc_stop = get_n_w_tank_mix_non_hc_stop(n_w_tank_mix_non_hc_out)

            # (21-3a)
            n_w_tank_mix = n_w_tank_mix_non_hc_stop

          elif Delta_tau_w_tank_out > 0:
            # (21-4a)
            n_w_tank_mix = n_w_tank_mix_non_hc_out

    return n_w_tank_mix


def get_n_w_tank_mix_hc():
    """集熱時における混合回数 (回/h) (21-2b)

    Args:

    Returns:
      int: 集熱時における混合回数 (回/h)
    """
    return 10


def get_n_w_tank_mix_non_hc_stop(n_w_tank_mix_non_hc_out):
    """非集熱時であって貯湯タンクからの出水がない場合の混合回数 (回/h) (21-3b)

    Args:
      n_w_tank_mix_non_hc_out(float): 非集熱時であって貯湯タンクからの出水がある場合の混合回数

    Returns:
      float: 非集熱時であって貯湯タンクからの出水がない場合の混合回数 (回/h)

    """
    return n_w_tank_mix_non_hc_out * 0.05


def get_n_w_tank_mix_non_hc_out(eta_r_tank):
    """非集熱時であって貯湯タンクからの出水がある場合の混合回数 (回/h) (21-4b)

    Args:
      eta_r_tank(float): 有効出湯効率 (%)

    Returns:
      float: 非集熱時であって貯湯タンクからの出水がある場合の混合回数 (回/h)
    """
    return 1 - eta_r_tank / 100


def get_Gamma_w_tank(M_w_tank_total, M_w_tank_lower):
    """入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-) (22)

    Args:
      M_w_tank_total(float): 貯湯タンク全体の水の質量 (kg)
      M_w_tank_lower(float): 入水・出水後の貯湯タンク下層部の水の質量 (kg)

    Returns:
      float: 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-) 
    """
    return (M_w_tank_lower / M_w_tank_total)


def get_M_w_tank_total(V_tank):
    """貯湯タンク全体の水の質量 (kg) (23)

    Args:
      V_tank(int): 貯湯タンクの容量 (L)

    Returns:
      ndarray: 貯湯タンク全体の水の質量 (kg)
    """
    # 水の密度
    Rho_w = get_Rho_w()

    return (Rho_w * V_tank * 10 ** (-3))


# ============================================================================
# 8.6 集熱量のうち貯湯タンク下層部で熱交換される割合
# ============================================================================

def calc_Gamma_hx_tank(Gamma_w_tank):
    """集熱量のうち貯湯タンク下層部で熱交換される割合 (-)

    Args:
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)

    Returns:
      float: 集熱量のうち貯湯タンク下層部で熱交換される割合 (-)
    """
    # 集熱量のうち貯湯タンク下層部で熱交換される割合を表す関係式を切り替える、入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比の値
    Gamma_limw_tank = get_Gamma_limw_tank()

    # 集熱量のうち貯湯タンク下層部で熱交換される割合 (24)
    Gamma_hx_tank = get_Gamma_hx_tank(Gamma_w_tank, Gamma_limw_tank)

    return Gamma_hx_tank


def get_Gamma_hx_tank(Gamma_w_tank, Gamma_limw_tank):
    """集熱量のうち貯湯タンク下層部で熱交換される割合 (-) (24)

    Args:
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-)
      Gamma_limw_tank(float): 集熱量のうち貯湯タンク下層部で熱交換される割合を表す関係式を切り替える、入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比の値 (-)

    Returns:
      float: 集熱量のうち貯湯タンク下層部で熱交換される割合 (-)
    """
    # (24-1)
    if Gamma_w_tank >= Gamma_limw_tank:
        return 1

    # (24-2)
    if Gamma_w_tank < Gamma_limw_tank:
        return (1 / Gamma_limw_tank) * Gamma_w_tank


def get_Gamma_limw_tank():
    """集熱量のうち貯湯タンク下層部で熱交換される割合を表す関係式を切り替える、入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比の値 (-)

    Args:

    Returns:
      float: 集熱量のうち貯湯タンク下層部で熱交換される割合を表す関係式を切り替える、入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比の値 (-)
    """
    return 0.5


# ============================================================================
# 8.7 貯湯タンク上層部の水の使用率
# ============================================================================

def calc_Gamma_wu_tank_upper(ls_type, hw_connection_type, Theta_wtr, Q_W_dmd_sun, M_w_tank_total, M_w_tank_upper_prev,
                            Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, Delta_tau_w_tank_out, t_hc_start_d):
    """貯湯タンク上層部の水の使用率 (-) (25)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      hw_connection_type(str): 給湯接続方式の種類 (-)
      Theta_wtr(float): 日平均給水温度 (℃)
      Q_W_dmd_sun(float): 給湯熱需要（浴槽追焚を除く） (MJ/h)
      M_w_tank_total(float): 貯湯タンクの放熱係数(W/K)
      M_w_tank_upper_prev(float): 貯湯タンク上層部の水の質量 (kg)
      Theta_w_tank_mixed_prev(float): 一時間前の入水・出水後の貯湯タンク上層部の水の温度 (℃)
      Theta_w_tank_upper_prev(float): 一時間前の入水・出水後の貯湯タンク下層部の水の温度 (℃)
      Delta_tau_w_tank_out(float): 貯湯タンクからの出水時間数 (h/h)
      t_hc_start_d(int): 集熱開始時刻 (-)

    Returns:
      float: 貯湯タンク上層部の水の使用率 (-)
    """
    if Delta_tau_w_tank_out == 0:
        # (25-1)
        return 0
    elif Delta_tau_w_tank_out > 0:
        # 給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量
        M_reqw_tank_upper = calc_M_reqw_tank_upper(ls_type, hw_connection_type, Theta_wtr, Q_W_dmd_sun, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d)

        # 給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量を算出する際に基準となる貯湯タンク上層部の水の質量
        M_reqw_tank = get_M_reqw_tank(M_w_tank_total, M_w_tank_upper_prev, t_hc_start_d)

        # (25-2a)
        return min(M_reqw_tank_upper / M_reqw_tank, 1)


def calc_M_reqw_tank_upper(ls_type, hw_connection_type, Theta_wtr, Q_W_dmd_sun, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d):
    """給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量 (kg)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      hw_connection_type(str): 給湯接続方式の種類 (-)
      Theta_wtr(float): 日平均給水温度 (℃)
      Q_W_dmd_sun(float): 給湯熱需要（浴槽追焚を除く） (MJ/h)
      Theta_w_tank_mixed_prev(float): 一時間前の入水・出水後の貯湯タンク上層部の水の温度 (℃)
      Theta_w_tank_upper_prev(float): 一時間前の入水・出水後の貯湯タンク下層部の水の温度 (℃)
      t_hc_start_d(int): 集熱開始時刻 (-)
    
    Returns:
      float: 給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量 (kg)
    """
    # 給湯熱需要を満たすために必要となる貯湯タンクから出水する水の質量
    M_dot_reqw_tank_out = calc_M_dot_reqw_tank_out(Theta_wtr, Q_W_dmd_sun, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d)

    # 給湯配管からの熱損失の程度を判断する基準となる、給湯配管内を流れる1時間当たりの水の質量
    M_dot_w_pipe_lim = get_M_dot_w_pipe_lim()

    # 計算タイムステップ
    Delta_t_calc = get_Delta_t_calc()

    # 給湯配管内流量の区分における貯湯タンクから給水混合弁までの給湯配管の熱損失率
    f_loss_pipe_tank_valve_pw_1, f_loss_pipe_tank_valve_pw_2 = calc_f_loss_pipe_tank_valve_pw(ls_type, hw_connection_type)

    # 給湯配管内流量の区分における貯湯タンクから給水混合弁までの給湯配管の熱損失率により補正した、日付の時刻において給湯熱需要を満たすために必要となる1時間当たりの貯湯タンクから出水する水の質量
    M_dot_dash_reqw_tank_out_pw_1, M_dot_dash_reqw_tank_out_pw_2 = get_M_dot_dash_reqw_tank_out_pw(M_dot_reqw_tank_out, f_loss_pipe_tank_valve_pw_1, f_loss_pipe_tank_valve_pw_2)

    # 給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量 (25-2b)
    M_reqw_tank_upper = get_M_reqw_tank_upper(M_dot_reqw_tank_out, M_dot_dash_reqw_tank_out_pw_1, M_dot_dash_reqw_tank_out_pw_2, M_dot_w_pipe_lim, Delta_t_calc)

    return M_reqw_tank_upper


def get_M_reqw_tank_upper(M_dot_reqw_tank_out, M_dot_dash_reqw_tank_out_pw_1, M_dot_dash_reqw_tank_out_pw_2, M_dot_w_pipe_lim, Delta_t_calc):
    """給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量 (kg) (25-2b)

    Args:
      M_reqw_tank_out(float): 給湯熱需要を満たすために必要となる貯湯タンクから出水する水の質量 (kg/h)
      f_loss_pipe_tank_valve(str): 貯湯タンクから給水混合弁までの給湯配管の熱損失率 (-)
      Delta_t_calc(int): 計算タイムステップ (-)

    Returns:
      float: 給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量 (kg)
    """
    if M_dot_reqw_tank_out <= M_dot_w_pipe_lim and M_dot_dash_reqw_tank_out_pw_1 <= M_dot_w_pipe_lim:
        return M_dot_dash_reqw_tank_out_pw_1 * Delta_t_calc
    elif M_dot_reqw_tank_out <= M_dot_w_pipe_lim and M_dot_dash_reqw_tank_out_pw_1 > M_dot_w_pipe_lim:
        return M_dot_dash_reqw_tank_out_pw_2 * Delta_t_calc
    elif M_dot_reqw_tank_out > M_dot_w_pipe_lim:
        return M_dot_dash_reqw_tank_out_pw_2 * Delta_t_calc


def get_M_dot_dash_reqw_tank_out_pw(M_dot_reqw_tank_out, f_loss_pipe_tank_valve_pw_1, f_loss_pipe_tank_valve_pw_2):
    """給湯配管内流量の区分における貯湯タンクから給水混合弁までの給湯配管の熱損失率により補正した、日付の時刻において給湯熱需要を満たすために必要となる1時間当たりの貯湯タンクから出水する水の質量 (kg/h) (25-2c) (25-2d)

    Args:
      M_dot_reqw_tank_out(float): 給湯熱需要を満たすために必要となる1時間当たりの貯湯タンクから出水する水の質量 (kg/h)
      f_loss_pipe_tank_valve_pw_1(float): 給湯配管内流量の区分1における貯湯タンクから給水混合弁までの給湯配管の熱損失率 (-)
      f_loss_pipe_tank_valve_pw_2(float): 給湯配管内流量の区分2における貯湯タンクから給水混合弁までの給湯配管の熱損失率 (-)

    Returns:
      tuple: 給湯配管内流量の区分における貯湯タンクから給水混合弁までの給湯配管の熱損失率により補正した、日付の時刻において給湯熱需要を満たすために必要となる1時間当たりの貯湯タンクから出水する水の質量 (kg/h)
    """
    # (25-2c)
    M_dot_dash_reqw_tank_out_pw_1 = M_dot_reqw_tank_out / (1 - f_loss_pipe_tank_valve_pw_1)

    #(25-2d)
    M_dot_dash_reqw_tank_out_pw_2 = M_dot_reqw_tank_out / (1 - f_loss_pipe_tank_valve_pw_2)

    return M_dot_dash_reqw_tank_out_pw_1, M_dot_dash_reqw_tank_out_pw_2


def calc_M_dot_reqw_tank_out(Theta_wtr, Q_W_dmd_sun, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d):
    """給湯熱需要を満たすために必要となる貯湯タンクから出水する水の質量 (kg/h)

    Args:
      Theta_wtr(float): 日平均給水温度 (℃)
      Q_W_dmd_sun(float): 給湯熱需要（浴槽追焚を除く） (MJ/h)
      Theta_w_tank_mixed_prev(float): 一時間前の入水・出水後の貯湯タンク上層部の水の温度 (℃)
      Theta_w_tank_upper_prev(float): 一時間前の入水・出水後の貯湯タンク下層部の水の温度 (℃)
      t_hc_start_d(int): 集熱開始時刻 (-)
    
    Returns:
      float: 給湯熱需要を満たすために必要となる貯湯タンクから出水する水の質量 (kg/h)
    """
    # 水の定圧比熱
    c_p_water = get_c_p_water()

    # 給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量を算出する際に基準となる貯湯タンク上層部の水の温度
    Theta_reqw_tank = get_Theta_reqw_tank(Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d)

    # 給湯熱需要を満たすために必要となる貯湯タンクから出水する水の質量 (25-2e)
    M_dot_reqw_tank_out = get_M_dot_reqw_tank_out(Theta_wtr, Q_W_dmd_sun, c_p_water, Theta_reqw_tank)

    return M_dot_reqw_tank_out


def get_M_dot_reqw_tank_out(Theta_wtr, Q_W_dmd_sun, c_p_water, Theta_reqw_tank):
    """給湯熱需要を満たすために必要となる貯湯タンクから出水する水の質量 (kg/h) (25-2e)

    Args:
      Theta_wtr(float): 日平均給水温度 (℃)
      Q_W_dmd_sun(float): 給湯熱需要（浴槽追焚を除く） (MJ/h)
      c_p_water(float): 水の定圧比熱 (-)
      Theta_reqw_tank(float): 給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量を算出する際に基準となる貯湯タンク上層部の水の温度 (℃)
      t_hc_start_d(int): 集熱開始時刻 (-)

    Returns:
      float: 給湯熱需要を満たすために必要となる貯湯タンクから出水する水の質量 (kg/h)
    """
    return (Q_W_dmd_sun * (10) ** 3 / c_p_water) / (Theta_reqw_tank - Theta_wtr)


def get_M_reqw_tank(M_w_tank_total, M_w_tank_upper_prev, t_hc_start_d):
    """給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量を算出する際に基準となる貯湯タンク上層部の水の質量 (kg) (26)

    Args:
      M_w_tank_total(float): 貯湯タンクの放熱係数(W/K)
      M_w_tank_upper_prev(float): 貯湯タンク上層部の水の質量 (kg)
      t_hc_start_d(int): 集熱開始時刻 (-)

    Returns:
      float: 給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量を算出する際に基準となる貯湯タンク上層部の水の質量 (kg)
    """
    if t_hc_start_d == 1:
        # (26-1)
        # 貯湯タンク全体の水の質量
        return M_w_tank_total
    else:
        # (26-2)
        # おける入水・出水後の貯湯タンク上層部の水の質量
        return M_w_tank_upper_prev


def get_Theta_reqw_tank(Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d):
    """給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量を算出する際に基準となる貯湯タンク上層部の水の温度 (℃) (27)

    Args:
      Theta_w_tank_mixed_prev(float): 一時間前の入水・出水後の貯湯タンク上層部の水の温度 (℃)
      Theta_w_tank_upper_prev(float): 一時間前の入水・出水後の貯湯タンク下層部の水の温度 (℃)
      t_hc_start_d(int): 集熱開始時刻 (-)

    Returns:
      float: 給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量を算出する際に基準となる貯湯タンク上層部の水の温度 (℃)
    """
    if t_hc_start_d == 1:
        # (27-1)
        # 完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度
        return Theta_w_tank_mixed_prev
    else:
        # (27-2)
        # 入水・出水後の貯湯タンク上層部の水の温度
        return Theta_w_tank_upper_prev


# ============================================================================
# 8.8 貯湯タンクからの出水時間数
# ============================================================================

def calc_Delta_tau_w_tank_out(ls_type, Theta_wtr, Theta_ex_p6h_Ave, Q_W_dmd_sun, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d):
    """貯湯タンクからの出水時間数 (h/h)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      Theta_wtr(float): 日平均給水温度 (℃)
      Theta_ex_p6h_Ave(float): 過去6時間の平均外気温度 (℃)
      Q_W_dmd_sun(float): 給湯熱需要（浴槽追焚を除く） (MJ/h)
      Theta_w_tank_mixed_prev(float): 完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度 (℃)
      Theta_w_tank_upper_prev(float): 入水・出水後の貯湯タンク上層部の水の温度 (℃)
      t_hc_start_d(int): 集熱開始時刻 (-)

    Returns:
      float: 貯湯タンクからの出水時間数 (h/h)
    """
    # 貯湯タンク内の水の利用可否
    isAvailable_w_tank = get_isAvailable_w_tank(ls_type, Theta_wtr, Theta_ex_p6h_Ave, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d)

    # 貯湯タンクからの出水時間数の計算領域を確保
    Delta_tau_w_tank_out = get_Delta_tau_w_tank_out(Q_W_dmd_sun, isAvailable_w_tank)

    return Delta_tau_w_tank_out


def get_Delta_tau_w_tank_out(Q_W_dmd_sun, isAvailable_w_tank):
    """貯湯タンクからの出水時間数 (h/h) (28)

    Args:
      Q_W_dmd_sun(float): 給湯熱需要（浴槽追焚を除く） (MJ/h)
      isAvailable_w_tank(bool): 貯湯タンク内の水の利用可否 (-)

    Returns:
      float: 貯湯タンクからの出水時間数 (h/h)
    """
    # 貯湯タンクからの出水時間数の計算領域を確保
    Delta_tau_w_tank_out = 0

    # Q_W_dmd_sun == 0 or isAvailable_w_tank == False の場合
    # (28-1)
    f1 =Q_W_dmd_sun == 0 or isAvailable_w_tank == False
    if f1:
      Delta_tau_w_tank_out = 0

    # Q_W_dmd_sun > 0 and isAvailable_w_tank == True の場合
    # (28-2)
    f2 = Q_W_dmd_sun > 0 and isAvailable_w_tank == True
    if f2:
      Delta_tau_w_tank_out = 1

    return Delta_tau_w_tank_out


# ============================================================================
# 8.9 日時が1月1日0時である場合の一時刻前における貯湯タンクの水の質量・温度
# ============================================================================

def get_M_w_tank_upper_prev(M_w_tank_total):
    """一時刻前における貯湯タンク上層部の水の質量 (kg) (29)

    Args:
      M_w_tank_total(int): 貯湯タンク全体の水の質量 (kg)

    Returns:
      int: 一時刻前における貯湯タンク上層部の水の質量 (kg)
    """
    # 貯湯タンク全体の水の質量
    return M_w_tank_total


def get_Theta_w_tank_upper_prev(Theta_wtr_d):
    """一時刻前における貯湯タンク上層部の水の質量 (kg) (30)

    Args:
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      float: 一時刻前における貯湯タンク上層部の水の質量 (kg)
    """
    # 日平均給水温度
    Theta_wtr_d_prev = Theta_wtr_d[-1]
    return Theta_wtr_d_prev


# ============================================================================
# 9.1. 熱媒温度
# ============================================================================

def calc_Theta_htm_stcs_d_t(b0, b1, I_s_d_t, Theta_ex_d_t, epsilon_t_stp_d_t, epsilon_t_stc_d_t, e_t_stcs_d_t):
    """熱的平衡状態を仮定した場合の集熱経路における熱媒温度 (℃)

    Args:
      b0(float): 集熱器の集熱効率特性線図一次近似式の切片 (-)
      b1(float): 集熱器の集熱効率特性線図一次近似式の傾き (W/(m2・K))
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)
      Theta_ex_d_t(ndarray): 外気温度 (℃)
      epsilon_t_stp_d_t(ndarray): 集熱配管の温度効率 (-)
      epsilon_t_stc_d_t(ndarray): 集熱器の温度効率 (-)
      e_t_stcs_d_t(ndarray): 集熱経路の総合温度効率 (-)

    Returns:
      ndarray: 熱的平衡状態を仮定した場合の集熱経路における熱媒温度 (℃)
    """
    # 集熱器のみに対して熱的平衡状態を仮定した場合の集熱器における熱媒温度 (32)
    Theta_htm_stc_d_t = get_Theta_htm_stc_d_t(b0, b1, I_s_d_t, Theta_ex_d_t)

    # 熱的平衡状態を仮定した場合の集熱経路における熱媒温度 (31)
    Theta_htm_stcs_d_t = get_Theta_htm_stcs_d_t(Theta_ex_d_t, epsilon_t_stp_d_t, epsilon_t_stc_d_t, e_t_stcs_d_t, Theta_htm_stc_d_t)

    return Theta_htm_stcs_d_t


def get_Theta_htm_stcs_d_t(Theta_ex_d_t, epsilon_t_stp_d_t, epsilon_t_stc_d_t, e_t_stcs_d_t, Theta_htm_stc_d_t):
    """熱的平衡状態を仮定した場合の集熱経路における熱媒温度 (℃) (31)

    Args:
      Theta_ex_d_t(ndarray): 外気温度 (℃)
      epsilon_t_stp_d_t(ndarray): 集熱配管の温度効率 (-)
      epsilon_t_stc_d_t(ndarray): 集熱器の温度効率 (-)
      e_t_stcs_d_t(ndarray): 集熱経路の総合温度効率 (-)
      Theta_htm_stc_d_t(ndarray): 集熱器のみに対して熱的平衡状態を仮定した場合の集熱器における熱媒温度 (-)

    Returns:
      ndarray: 熱的平衡状態を仮定した場合の集熱経路における熱媒温度 (℃)
    """
    return (((1 - epsilon_t_stp_d_t) * epsilon_t_stc_d_t) / e_t_stcs_d_t) * (Theta_htm_stc_d_t - Theta_ex_d_t) + Theta_ex_d_t


def get_Theta_htm_stc_d_t(b0, b1, I_s_d_t, Theta_ex_d_t):
    """集熱器のみに対して熱的平衡状態を仮定した場合の集熱器における熱媒温度 (℃) (32)

    Args:
      b0(float): 集熱器の集熱効率特性線図一次近似式の切片 (-)
      b1(float): 集熱器の集熱効率特性線図一次近似式の傾き (W/(m2・K))
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)
      Theta_ex_d_t(ndarray): 外気温度 (℃)

    Returns:
      ndarray: 集熱器のみに対して熱的平衡状態を仮定した場合の集熱器における熱媒温度 (℃)
    """
    return (b0 / b1) * I_s_d_t + Theta_ex_d_t


# ============================================================================
# 9.2. 集熱経路の総合温度効率
# ============================================================================

def get_e_t_stcs_d_t(epsilon_t_stp_d_t, epsilon_t_stc_d_t):
    """集熱経路の総合温度効率 (-) (33)

    Args:
      epsilon_t_stp_d_t(ndarray): 集熱配管の温度効率
      epsilon_t_stc_d_t(ndarray): 集熱器の温度効率

    Returns:
      ndarray: 集熱経路の総合温度効率 (-)
    """
    return (1 - (1 - epsilon_t_stp_d_t) ** 2 * (1 - epsilon_t_stc_d_t))


# ============================================================================
# 9.3. 集熱配管還り熱媒温度の算定に係る案分比率
# ============================================================================

def get_Beta_htm_tank_d_t(e_stcs_d_t, epsilon_t_hx_d_t):
    """集熱配管還り熱媒温度の算定に係る貯湯タンクの下層部の水の温度に対する案分比率 (-) (34)

    Args:
      e_stcs_d_t(ndarray): 集熱経路の総合温度効率 (-)
      epsilon_t_hx_d_t(ndarray): 熱交換器の温度効率 (-)

    Returns:
      ndarray: 集熱配管還り熱媒温度の算定に係る貯湯タンクの下層部の水の温度に対する案分比率 (-)
    """
    return (1 - e_stcs_d_t) * epsilon_t_hx_d_t / (1 - (1 - e_stcs_d_t) * (1 - epsilon_t_hx_d_t))


def get_Beta_htm_stcs_d_t(e_stcs_d_t, epsilon_t_hx_d_t):
    """集熱配管還り熱媒温度の算定に係る集熱経路に対して熱的平衡状態を仮定した場合の集熱経路における熱媒温度に対する案分比率 (-) (35)

    Args:
      e_stcs_d_t(ndarray): 集熱経路の総合温度効率
      epsilon_t_hx_d_t(ndarray): 熱交換器の温度効率 (-)

    Returns:
      ndarray: 集熱配管還り熱媒温度の算定に係る集熱経路に対して熱的平衡状態を仮定した場合の集熱経路における熱媒温度に対する案分比率 (-)
    """
    return e_stcs_d_t / (1 - (1 - e_stcs_d_t) * (1 - epsilon_t_hx_d_t))


# ============================================================================
# 9.4 循環ポンプ
# ============================================================================

def calc_E_pump_d_t(region, sol_region, ls_type, P_pump_hc, P_pump_non_hc, P_alpha_sp, P_beta_sp):
    """1時間当たりの循環ポンプの消費電力量

    Args:
      region(int): 省エネルギー地域区分 (-)
      sol_region(int): 年間の日射地域区分 (-)
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      P_pump_hc(float): 集熱時における循環ポンプの消費電力量 (W) [入力/固定]
      P_pump_non_hc(float): 非集熱時における循環ポンプの消費電力量 (W) [入力/固定]
      P_alpha_sp(float): ソーラーシステムの太陽熱集熱部の方位角 (°)
      P_beta_sp(float): ソーラーシステムの太陽熱集熱部の傾斜角 (°)

    Returns:
      ndarray: 1時間当たりの循環ポンプの消費電力量 (kWh/h)
    """
    # 集熱器の単位面積当たりの平均日射量 (W/m2)
    solrad = load_solrad(region, sol_region)
    I_s_d_t = calc_I_s_d_t(P_alpha_sp, P_beta_sp, solrad)

    # 集熱時における循環ポンプの消費電力量 (W)
    P_pump_hc = get_P_pump_hc(ls_type, P_pump_hc)

    # 非集熱時における循環ポンプの消費電力量 (W)
    P_pump_non_hc = get_P_pump_non_hc(ls_type, P_pump_non_hc)

    # 1時間当たりの集熱時間数
    Delta_tau_hc_d_t = get_Delta_tau_hc_d_t(ls_type, I_s_d_t)

    # 1時間当たりの集熱時における循環ポンプの稼働時間数
    Delta_tau_pump_hc_d_t = get_Delta_tau_pump_hc_d_t(ls_type, Delta_tau_hc_d_t)

    # 1時間当たりの非集熱時における循環ポンプの稼働時間数
    Delta_tau_pump_non_hc_d_t = get_Delta_tau_pump_non_hc_d_t(ls_type, I_s_d_t, Delta_tau_hc_d_t)

    # 1時間当たりの循環ポンプの消費電力量 (36)
    E_pump_d_t = get_E_pump_d_t(P_pump_hc, Delta_tau_pump_hc_d_t, P_pump_non_hc, Delta_tau_pump_non_hc_d_t)

    return E_pump_d_t


def get_E_pump_d_t(P_pump_hc, Delta_tau_pump_hc_d_t, P_pump_non_hc, Delta_tau_pump_non_hc_d_t):
    """1時間当たりの循環ポンプの消費電力量 (36)

    Args:
      P_pump_hc(float): 集熱時における循環ポンプの消費電力量 (W) [入力/固定]
      P_pump_non_hc(float): 非集熱時における循環ポンプの消費電力量 (W) [入力/固定]
      Delta_tau_pump_hc_d_t(ndarray): 1時間当たりの集熱時における循環ポンプの稼働時間数 (h/h)
      Delta_tau_pump_non_hc_d_t(ndarray): 1時間当たりの非集熱時における循環ポンプの稼働時間数 (h/h)

    Returns:
      ndarray: 1時間当たりの循環ポンプの消費電力量 (kWh/h)
    """
    return (P_pump_hc * Delta_tau_pump_hc_d_t + P_pump_non_hc * Delta_tau_pump_non_hc_d_t) * 10 ** (-3)


# ============================================================================
# 10. 給湯接続部
# ============================================================================

# ============================================================================
# 10.1 給湯配管の熱損失率
# ============================================================================

def calc_f_loss_pipe_tank_boiler_pw(ls_type, hw_connection_type):
    """給湯配管内流量の区分における貯湯タンクから補助熱源機までの給湯配管の熱損失率 (-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      hw_connection_type(str): 給湯接続方式の種類 (-)

    Returns:
      tuple: 給湯配管内流量の区分における貯湯タンクから補助熱源機までの給湯配管の熱損失率 (-)
    """
    # 給湯配管内流量の区分における貯湯タンクから補助熱源機までの給湯配管の熱損失率および貯湯タンクから給水混合弁までの給湯配管の熱損失率
    f_loss_pipe_tank_pw = get_f_loss_pipe_tank_pw(ls_type, hw_connection_type)

    # 貯湯タンクから補助熱源機までの給湯配管の熱損失率
    return f_loss_pipe_tank_pw[0], f_loss_pipe_tank_pw[1]


def calc_f_loss_pipe_tank_valve_pw(ls_type, hw_connection_type):
    """給湯配管内流量の区分における貯湯タンクから給水混合弁までの給湯配管の熱損失率 (-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      hw_connection_type(str): 給湯接続方式の種類 (-)

    Returns:
      tuple: 給湯配管内流量の区分における貯湯タンクから給水混合弁までの給湯配管の熱損失率 (-)
    """
    # 給湯配管内流量の区分における貯湯タンクから補助熱源機までの給湯配管の熱損失率および貯湯タンクから給水混合弁までの給湯配管の熱損失率
    f_loss_pipe_tank_pw = get_f_loss_pipe_tank_pw(ls_type, hw_connection_type)

    # 貯湯タンクから給水混合弁までの給湯配管の熱損失率
    return f_loss_pipe_tank_pw[2], f_loss_pipe_tank_pw[3]


def get_f_loss_pipe_tank_pw(ls_type, hw_connection_type):
    """給湯配管内流量の区分における貯湯タンクから補助熱源機までの給湯配管の熱損失率および貯湯タンクから給水混合弁までの給湯配管の熱損失率 (-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      hw_connection_type(str): 給湯接続方式の種類 (-)

    Returns:
      ndarray: 給湯配管内流量の区分における貯湯タンクから補助熱源機までの給湯配管の熱損失率および貯湯タンクから給水混合弁までの給湯配管の熱損失率 (-)
    """
    # 表5 貯湯タンクから補助熱源機までの給湯配管の熱損失率
    table_5 = np.array([
        [0.174, 0.059, 0.159, 0.054],
        [0.040, 0.025, 0.020, 0.013],
        [0.027, 0.017, 0.013, 0.009],
        [0.187, 0.064, 0.187, 0.064],
        [0.050, 0.024, 0.050, 0.024]
    ])

    if hw_connection_type == "接続ユニット方式":
        if ls_type == '密閉形太陽熱温水器（直圧式）':
            return table_5[0]
        elif ls_type == 'ソーラーシステム':
            return table_5[1]
        else:
            raise ValueError(ls_type)
    elif hw_connection_type == "三方弁方式":
        return table_5[2]
    elif hw_connection_type == "給水予熱方式":
        return table_5[3]
    elif hw_connection_type == '浴槽落とし込み方式':
        return table_5[4]
    else:
        raise ValueError(hw_connection_type)


# ============================================================================
# 10.5 給湯配管からの熱損失の程度を判断する基準となる、給湯配管内を流れる1時間当たりの水の質量
# ============================================================================

def get_M_dot_w_pipe_lim():
    """給湯配管からの熱損失の程度を判断する基準となる、給湯配管内を流れる1時間当たりの水の質量 (kg/h)

    Args:

    Returns:
      int: 給湯配管からの熱損失の程度を判断する基準となる、給湯配管内を流れる1時間当たりの水の質量 (kg/h)
    """
    return 150


# ============================================================================
# 11. 仕様
# ============================================================================

def get_b0(ls_type, b0):
    """集熱器の集熱効率特性線図一次近似式の切片 (-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      b0(float): 集熱器の集熱効率特性線図一次近似式の切片 (-)

    Returns:
      float: 集熱器の集熱効率特性線図一次近似式の切片 (-)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_b0(b0)
    elif ls_type == 'ソーラーシステム':
        return lss2.get_b0(b0)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_b0(b0)


def get_b1(ls_type, b1):
    """集熱器の集熱効率特性線図一次近似式の傾き W/(m2・K)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      b0(float): 集熱器の集熱効率特性線図一次近似式の傾き W/(m2・K)

    Returns: 集熱器の集熱効率特性線図一次近似式の傾き W/(m2・K)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_b1(b1)
    elif ls_type == 'ソーラーシステム':
        return lss2.get_b1(b1)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_b1(b1)


def get_Gs_htm(ls_type, Gs_htm):
    """熱媒の基準循環流量

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      Gs_htm(float): 熱媒の基準循環流量

    Returns: 熱媒の基準循環流量
    """
    if ls_type == 'ソーラーシステム':
        return lss2.get_Gs_htm(Gs_htm)


def get_g_htm(ls_type, g_htm):
    """単位日射量当たりの循環流量 (kg/h)/(W/m2)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      g_htm(float): 単位日射量当たりの循環流量 (kg/h)/(W/m2)

    Returns: 単位日射量当たりの循環流量 (kg/h)/(W/m2)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_g_htm(g_htm)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_g_htm(g_htm)


def get_c_p_htm(ls_type, c_p_htm):
    """熱媒の定圧比熱 (kJ/(kg.K))

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      c_p_htm(float): 熱媒の定圧比熱 (kJ/(kg･K)) 

    Returns: 熱媒の定圧比熱 (kJ/(kg.K)
    """
    if ls_type in ['密閉形太陽熱温水器（直圧式）', '開放形太陽熱温水器']:
        return get_c_p_water()
    elif ls_type == 'ソーラーシステム':
        return lss2.get_c_p_htm(c_p_htm)


def get_UA_stp(ls_type, UA_stp):
    """集熱配管の放熱係数 W/(m・K)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      UA_stp(float): 集熱配管の放熱係数 W/(m・K)

    Returns: 集熱配管の放熱係数 W/(m・K)
    """
    if ls_type == 'ソーラーシステム':
        return lss2.get_UA_stp(UA_stp)


def get_UA_hx(ls_type, UA_hx):
    """熱交換器の伝熱係数 (W/K)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      UA_hx(float): 熱交換器の伝熱係数 (-)

    Returns: 熱交換器の伝熱係数 (W/K)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_UA_hx(UA_hx)
    elif ls_type == 'ソーラーシステム':
        return lss2.get_UA_hx(UA_hx)


def get_P_pump_hc(ls_type, P_pump_hc):
    """集熱時における循環ポンプの消費電力量

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      P_pump_hc(float): 集熱時における循環ポンプの消費電力量 (W) [入力/固定]

    Returns:
      float: 集熱時における循環ポンプの消費電力量 (W)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_P_pump_hc()
    elif ls_type == 'ソーラーシステム':
        return lss2.get_P_pump_hc(P_pump_hc)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_P_pump_hc()


def get_P_pump_non_hc(ls_type, P_pump_non_hc):
    """非集熱時における循環ポンプの消費電力量

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      P_pump_non_hc(float): 非集熱時における循環ポンプの消費電力量 (W) [入力/固定]

    Returns:
      float: 非集熱時における循環ポンプの消費電力量 (W)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_P_pump_non_hc()
    elif ls_type == 'ソーラーシステム':
        return lss2.get_P_pump_non_hc(P_pump_non_hc)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_P_pump_non_hc()


def get_eta_r_tank(ls_type, eta_r_tank):
    """有効出湯効率  (%)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      eta_r_tank(float): 有効出湯効率 (%)

    Returns:
      float: 有効出湯効率  (%)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_eta_r_tank(eta_r_tank)
    elif ls_type == 'ソーラーシステム':
        return lss2.get_eta_r_tank(eta_r_tank)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_eta_r_tank(eta_r_tank)


def get_UA_tank(ls_type, UA_tank):
    """熱交換器の伝熱係数 (W/K)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      UA_tank(float): 有効出湯効率 (%)

    Returns:
      float: 熱交換器の伝熱係数 (W/K)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_UA_tank(UA_tank)
    elif ls_type == 'ソーラーシステム':
        return lss2.get_UA_tank(UA_tank)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_UA_tank(UA_tank)


# ============================================================================
# 16. 水の物性値
# ============================================================================

def get_c_p_water():
    """水の定圧比熱 (kJ/(kg.K))

    Args:

    Returns:
      float: 水の定圧比熱 (kJ/(kg.K))
    """
    return 4.186


def get_Rho_w():
    """水の密度 (kg/m3)
    
    Args:

    Returns:
      int: 水の密度 (kJ/m3)
    """
    return 1000


# ============================================================================
# 17. 計算タイムステップ
# ============================================================================

def get_Delta_t_calc():
    """計算タイムステップ (-)
    
    Args:

    Returns:
      int: 計算タイムステップ (-)
    """
    return 1


def get_G_htm_d_t(ls_type, g_htm, Gs_htm, I_s_d_t, Delta_tau_hc_d_t):
    """1時間当たりの熱媒の循環量 (kg/h)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      g_htm(float): 単位日射量当たりの循環流量((kg/h)/(W/m2))
      Gs_htm(float): 熱媒の基準循環流量(kg/h)
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)
      Delta_tau_hc_d_t(ndarray): 1時間当たりの集熱時間数 (h/h)

    Returns:
      ndarray: 1時間当たりの熱媒の循環量 (kg/h)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_G_htm_d_t(g_htm, I_s_d_t, Delta_tau_hc_d_t)
    elif ls_type == 'ソーラーシステム':
        return lss2.get_G_htm_d_t(Gs_htm, Delta_tau_hc_d_t)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_G_htm_d_t(g_htm, I_s_d_t, Delta_tau_hc_d_t)


def get_Delta_tau_hc_d_t(ls_type, I_s_d_t):
    """集熱開始時刻 (-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)

    Returns:
      ndarray: 集熱開始時刻 (-)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_Delta_tau_hc_d_t(I_s_d_t)
    elif ls_type == 'ソーラーシステム':
        return lss2.get_Delta_tau_hc_d_t(I_s_d_t)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_Delta_tau_hc_d_t(I_s_d_t)


def get_isAvailable_w_tank(ls_type, Theta_wtr, Theta_ex_p6h_Ave, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d):
    """貯湯タンク内の水の利用可否 (-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      Theta_wtr(float): 日平均給水温度 (℃)
      Theta_ex_p6h_Ave(float): 過去6時間の平均外気温度 (℃)
      Theta_w_tank_mixed_prev(float): 完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度 (℃)
      Theta_w_tank_upper_prev(float): 入水・出水後の貯湯タンク上層部の水の温度 (℃)
      t_hc_start_d(int): 集熱開始時刻 (-)

    Returns:
      bool: 貯湯タンク内の水の利用可否 (-)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_isAvailable_w_tank(Theta_wtr, Theta_ex_p6h_Ave, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d)
    elif ls_type == 'ソーラーシステム':
        return lss2.get_isAvailable_w_tank(Theta_wtr, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_isAvailable_w_tank(Theta_wtr, Theta_ex_p6h_Ave, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d)


def get_Delta_tau_pump_hc_d_t(ls_type, Delta_tau_hc_d_t):
    """1時間当たりの集熱時における循環ポンプの稼働時間数 (h/h)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      Delta_tau_hc_d_t(ndarray): 1時間当たりの集熱時間数 (h/h)
    Returns:
      ndarray: 1時間当たりの集熱時における循環ポンプの稼働時間数 (h/h)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_Delta_tau_pump_hc_d_t()
    elif ls_type == 'ソーラーシステム':
        return lss2.get_Delta_tau_pump_hc_d_t(Delta_tau_hc_d_t)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_Delta_tau_pump_hc_d_t()


def get_Delta_tau_pump_non_hc_d_t(ls_type, I_s_d_t, Delta_tau_hc_d_t):
    """1時間当たりの非集熱時における循環ポンプの稼働時間数 (h/h)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)
      Delta_tau_hc_d_t(ndarray): 1時間当たりの集熱時間数 (h/h)

    Returns:
      ndarray: 1時間当たりの非集熱時における循環ポンプの稼働時間数 (h/h)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_Delta_tau_pump_non_hc_d_t()
    elif ls_type == 'ソーラーシステム':
        return lss2.get_Delta_tau_pump_non_hc_d_t(I_s_d_t, Delta_tau_hc_d_t)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_Delta_tau_pump_non_hc_d_t()


def get_epsilon_t_hx_d_t(ls_type, c_p_htm, UA_hx, G_htm_d_t):
    """熱交換器の温度効率(-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      c_p_htm(float): 熱媒の定圧比熱 (kJ/(kg･K)) 
      UA_hx(float): 熱交換器の伝熱係数 (-)
      G_htm_d_t(ndarray): 1時間当たりの熱媒の循環量 (kg/h)

    Returns:
      ndarray: 熱交換器の温度効率 (-)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_epsilon_t_hx_d_t(c_p_htm, UA_hx, G_htm_d_t)
    elif ls_type == 'ソーラーシステム':
        return lss2.get_epsilon_t_hx_d_t(c_p_htm, UA_hx, G_htm_d_t)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_epsilon_t_hx_d_t()


def get_epsilon_t_stc_d_t(ls_type, A_stcp, b1, c_p_htm, G_htm_d_t):
    """集熱器の温度効率

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      A_stcp(float): 集熱部の有効集熱面積(m2)
      b1(float): 集熱器の集熱効率特性線図一次近似式の傾き (W/(m2・K))
      c_p_htm(float): 熱媒の定圧比熱 (kJ/(kg･K)) 
      G_htm_d_t(ndarray): 1時間当たりの熱媒の循環量 (kg/h)

    Returns:
      ndarray: 集熱器の温度効率
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_epsilon_t_stc_d_t(A_stcp, b1, c_p_htm, G_htm_d_t)
    elif ls_type == 'ソーラーシステム':
        return lss2.get_epsilon_t_stc_d_t(A_stcp, b1, c_p_htm, G_htm_d_t)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_epsilon_t_stc_d_t(A_stcp, b1, c_p_htm, G_htm_d_t)


def get_epsilon_t_stp_d_t(ls_type, c_p_htm, UA_stp, G_htm_d_t):
    """集熱配管の温度効率 (-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      c_p_htm(float): 熱媒の定圧比熱 (kJ/(kg･K)) 
      UA_stp(float): 集熱配管の放熱係数 (W/(m.K)
      G_htm_d_t(ndarray): 1時間当たりの熱媒の循環量 (kg/h)

    Returns:
      float: 集熱配管の温度効率 (-)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_epsilon_t_stp_d_t()
    elif ls_type == 'ソーラーシステム':
        return lss2.get_epsilon_t_stp_d_t(c_p_htm, UA_stp, G_htm_d_t)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_epsilon_t_stp_d_t()


def get_t_hc_start_d(ls_type, I_s_d_t):
    """集熱開始時刻 (-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)

    Returns:
      ndarray: 集熱開始時刻 (-)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_t_hc_start_d(I_s_d_t)
    elif ls_type == 'ソーラーシステム':
        return lss2.get_t_hc_start_d(I_s_d_t)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_t_hc_start_d(I_s_d_t)


def get_Theta_ex_p6h_Ave(ls_type, Theta_ex_d_t, dt):
    """当該時刻を含む過去6時間の平均外気温度 (℃)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム, 開放形太陽熱温水器)
      Theta_ex_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)
      dt: 日時

    Returns:
      ndarray: 当該時刻を含む過去6時間の平均外気温度 (℃)
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_Theta_ex_p6h_Ave(Theta_ex_d_t, dt)
    elif ls_type == '開放形太陽熱温水器':
        return lss3.get_Theta_ex_p6h_Ave(Theta_ex_d_t, dt)
