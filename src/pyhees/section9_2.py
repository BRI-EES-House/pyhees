# ============================================================================
# 第九章 自然エネルギー利用設備
# 第二節 液体集熱式太陽熱利用設備
# Ver.08（エネルギー消費性能計算プログラム（住宅版）Ver.0203～）
# ============================================================================

import numpy as np
import pyhees.section9_2_a as lss1
import pyhees.section9_2_b as lss2
from pyhees.section11_2 import \
    load_solrad, \
    calc_I_s_d_t

# ============================================================================
# 6. 補正集熱量
# ============================================================================

def calc_L_sun_lss_d_t(ls_type, A_stcp, b0, b1, c_p_htm, eta_r_tank, g_htm, Gs_htm, hw_connection_type, 
                      P_alpha_sp, P_beta_sp, Theta_wtr_d, UA_hx, UA_stp, UA_tank, V_tank,
                      solrad, Q_W_dmd_excl_ba2_d_t, Theta_ex_d_t):
    """1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (1)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      A_stcp(float): 集熱部の有効集熱面積(m2)
      b0(float): 集熱器の集熱効率特性線図一次近似式の切片（-）
      b1(float): 集熱器の集熱効率特性線図一次近似式の傾き（W/(m2・K)）
      c_p_htm(float): 熱媒の定圧比熱
      eta_r_tank(float): 有効出湯効率
      g_htm(float): 単位日射量当たりの循環流量((kg/h)/(W/m2))
      Gs_htm(float): 熱媒の基準循環流量(kg/h)
      hw_connection_type(str): 給湯接続方式の種類
      P_alpha_sp(float): ソーラーシステムの太陽熱集熱部の方位角 (°)
      P_beta_sp(float): ソーラーシステムの太陽熱集熱部の傾斜角 (°)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)
      UA_tank(float): 貯湯タンクの放熱係数(W/K)
      UA_stp(float): 集熱配管の放熱係数 (W/(m.K)
      UA_hx(float): 熱交換器の伝熱係数 (-)
      V_tank(float): タンク容量 (L),
      solrad(ndarray): 日射量データ
      Q_W_dmd_excl_ba2_d_t(ndarray): 1時間当たりの給湯熱需要（浴槽追焚を除く） (MJ/h)
      Theta_ex_d_t(ndarray): 外気温度

    Returns:
      ndarray: 1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/h)

    """
    M_w_tank_upper_d_t = np.zeros(24 * 365)
    M_w_tank_lower_d_t = np.zeros(24 * 365)
    M_w_tank_out_d_t = np.zeros(24 * 365)

    Gamma_w_tank_d_t = np.zeros(24 * 365)
    Theta_w_tank_upper_d_t = np.zeros(24 * 365)
    Theta_w_tank_lower_d_t = np.zeros(24 * 365)
    Theta_w_tank_mixed_d_t =  np.zeros(24 * 365)

    Gamma_wu_tank_upper_d_t = np.zeros(24 * 365)
    delta_tau_w_tank_out_d_t = np.zeros(24 * 365)

    b0 = calc_b0(ls_type, b0)
    b1 = calc_b1(ls_type, b1)
    c_p_htm = calc_c_p_htm(ls_type, c_p_htm)
    eta_r_tank = calc_eta_r_tank(ls_type, eta_r_tank)
    UA_tank = calc_UA_tank(ls_type, UA_tank)
    UA_hx = calc_UA_hx(ls_type, UA_hx)

    if ls_type == "密閉形太陽熱温水器（直圧式）":
      g_htm = lss1.calc_g_htm(g_htm)

      # 当該時刻を含む過去6時間の平均外気温度
      Theta_ex_p6h_Ave_d_t = lss1.calc_Theta_ex_p6h_Ave_d_t(Theta_ex_d_t)

    elif ls_type == "ソーラーシステム":
      Gs_htm = lss2.calc_Gs_htm(Gs_htm)
      UA_stp = lss2.calc_UA_stp(UA_stp)

    # 貯湯タンク全体の水の質量 
    M_w_tank_total = calc_M_w_tank_total(V_tank)

    # 集熱器の単位面積当たりの平均日射量 (W/m2)
    I_s_d_t = calc_I_s_d_t(P_alpha_sp, P_beta_sp, solrad)

    # 集熱開始時刻
    t_hc_start_d = calc_t_hc_start_d(ls_type, I_s_d_t)

    # 1時間当たりの集熱時間数
    delta_tau_hc_d_t = calc_delta_tau_hc_d_t(ls_type, I_s_d_t)

    # 1時間当たりの熱媒の循環量
    G_htm_d_t = calc_G_htm_d_t(ls_type, g_htm, Gs_htm, I_s_d_t, delta_tau_hc_d_t)

    # 集熱配管の温度効率
    Epsilon_t_stp_d_t = calc_Epsilon_t_stp_d_t(ls_type, c_p_htm, UA_stp, G_htm_d_t)

    # 集熱器の温度効率
    Epsilon_t_stc_d_t = calc_Epsilon_t_stc_d_t(ls_type, A_stcp, b1, c_p_htm, G_htm_d_t)

    # 集熱経路の総合温度効率
    e_t_stcs_d_t = calc_e_t_stcs_d_t(Epsilon_t_stp_d_t, Epsilon_t_stc_d_t)

    # 日平均給水温度を時間ごとに拡張
    Theta_wtr_d_t = np.repeat(Theta_wtr_d, 24)

    # 給湯熱需要のうちの太陽熱利用設備の分担分
    Q_W_dmd_sun_d_t = calc_Q_W_dmd_sun_d_t(Q_W_dmd_excl_ba2_d_t)

    # 熱的平衡状態を仮定した場合の集熱経路における熱媒温度
    Theta_htm_stcs_d_t = calc_Theta_htm_stcs_d_t(b0, b1, I_s_d_t, Theta_ex_d_t, Epsilon_t_stp_d_t, Epsilon_t_stc_d_t, e_t_stcs_d_t)

    # 熱交換器の温度効率
    Epsilon_t_hx_d_t = calc_Epsilon_t_hx_d_t(ls_type, c_p_htm, UA_hx, G_htm_d_t)

    # 集熱配管還り熱媒温度の算定に係る貯湯タンクの下層部の水の温度に対する案分比率
    Beta_htm_tank_d_t = calc_Beta_htm_tank_d_t(e_t_stcs_d_t, Epsilon_t_hx_d_t)

    # 集熱配管還り熱媒温度の算定に係る集熱経路に対して熱的平衡状態を仮定した場合の集熱経路における熱媒温度に対する案分比率
    Beta_htm_stcs_d_t = calc_Beta_htm_stcs_d_t(e_t_stcs_d_t, Epsilon_t_hx_d_t)

    for dt in range(24 * 365):
      # 日時が1月1日0時である場合の一時刻前における計算
      if dt == 0:
          # 貯湯タンク上層部の水の質量
          M_w_tank_upper_d_t[-1] = calc_M_w_tank_upper_prev(V_tank)

          M_w_tank_lower_d_t[-1] = M_w_tank_total - M_w_tank_upper_d_t[-1]

          # 入水・出水後の貯湯タンク上層部の水の温度
          Theta_w_tank_upper_d_t[-1] = calc_Theta_w_tank_upper_prev(Theta_wtr_d)

          # 一時刻前における貯湯タンク下層部の水の温度は定義しない
          Theta_w_tank_lower_d_t[-1] = np.nan

          # 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 
          Gamma_w_tank_d_t[-1] = M_w_tank_lower_d_t[-1] / M_w_tank_total

      # 完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度
      Theta_w_tank_mixed_d_t[dt-1] = calc_Theta_w_tank_mixed(Gamma_w_tank_d_t[dt-1], Theta_w_tank_upper_d_t[dt-1], Theta_w_tank_lower_d_t[dt-1])

      # 貯湯タンクからの出水時間数
      Theta_ex_p6h_Ave = Theta_ex_p6h_Ave_d_t[dt] if ls_type == "密閉形太陽熱温水器（直圧式）" else None
      delta_tau_w_tank_out_d_t[dt] = calc_delta_tau_w_tank_out(ls_type, Theta_wtr_d_t[dt], Theta_ex_p6h_Ave, Q_W_dmd_sun_d_t[dt], Theta_w_tank_mixed_d_t[dt-1], Theta_w_tank_upper_d_t[dt-1], t_hc_start_d[dt])

      # 貯湯タンク上層部の水の使用率
      Gamma_wu_tank_upper_d_t[dt] = calc_Gamma_wu_tank_upper(ls_type, hw_connection_type,
                                  Theta_wtr_d_t[dt], Q_W_dmd_sun_d_t[dt], M_w_tank_total, M_w_tank_upper_d_t[dt-1], Theta_w_tank_mixed_d_t[dt-1], Theta_w_tank_upper_d_t[dt-1], 
                                  delta_tau_w_tank_out_d_t[dt], t_hc_start_d[dt])

      # 貯湯タンクから出水する水の質量
      M_w_tank_out_d_t[dt] = calc_M_w_tank_out(Gamma_wu_tank_upper_d_t[dt], M_w_tank_upper_d_t[dt-1])

      # 入水・出水後の貯湯タンク上層部の水の質量
      M_w_tank_upper_d_t[dt] = calc_M_w_tank_upper(M_w_tank_total, Gamma_wu_tank_upper_d_t[dt], M_w_tank_out_d_t[dt], M_w_tank_upper_d_t[dt-1], M_w_tank_lower_d_t[dt-1], Gamma_w_tank_d_t[dt-1], t_hc_start_d[dt])

      # 入水・出水後の貯湯タンク下層部の水の質量
      M_w_tank_lower_d_t[dt] = calc_M_w_tank_lower(M_w_tank_total, M_w_tank_upper_d_t[dt])

      # 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比
      Gamma_w_tank_d_t[dt] = calc_Gamma_w_tank(M_w_tank_total,  M_w_tank_lower_d_t[dt])

      # 入水・出水後の貯湯タンク上層部の水の温度
      Theta_w_tank_upper_d_t[dt], Theta_w_tank_lower_d_t[dt] = calc_Theta_w_tank(c_p_htm, eta_r_tank, 
                      Theta_wtr_d_t[dt], UA_tank, M_w_tank_total, Gamma_w_tank_d_t[dt], Gamma_w_tank_d_t[dt-1], M_w_tank_upper_d_t[dt], 
                      M_w_tank_out_d_t[dt], M_w_tank_lower_d_t[dt], M_w_tank_lower_d_t[dt-1], Theta_w_tank_mixed_d_t[dt-1], Theta_w_tank_upper_d_t[dt-1],
                      Theta_w_tank_lower_d_t[dt-1], Gamma_wu_tank_upper_d_t[dt], delta_tau_w_tank_out_d_t[dt], t_hc_start_d[dt],
                      Theta_htm_stcs_d_t[dt], Beta_htm_stcs_d_t[dt], Beta_htm_tank_d_t[dt], Epsilon_t_hx_d_t[dt], G_htm_d_t[dt], Theta_ex_d_t[dt], delta_tau_hc_d_t[dt])

    # 貯湯タンクから補助熱源機までの給湯配管の熱損失率
    f_pipe_loss_tank_boiler = calc_f_pipe_loss_tank_boiler(ls_type, hw_connection_type, M_w_tank_out_d_t)

    # 1時間当たりの貯湯タンク出湯熱量
    Q_tank_d_t = calc_Q_tank_d_t(Theta_wtr_d_t, delta_tau_w_tank_out_d_t, M_w_tank_out_d_t, Theta_w_tank_mixed_d_t, Theta_w_tank_upper_d_t, t_hc_start_d)

    L_sun_lss_d_t = (1 - f_pipe_loss_tank_boiler) * Q_tank_d_t

    return L_sun_lss_d_t


# ============================================================================
# 7. 補機の消費電力量
# ============================================================================

def calc_E_E_lss_aux_d_t(region, sol_region, ls_type, P_pump_hc, P_pump_non_hc, P_alpha_sp, P_beta_sp):
    """1時間当たりの補機の消費電力量 (2)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      P_pump_hc(float): 集熱時における循環ポンプの消費電力量 (W) [入力/固定]
      P_pump_non_hc(float): 非集熱時における循環ポンプの消費電力量 (W) [入力/固定]
      P_alpha_sp(float): 太陽熱集熱部の方位角 (°)
      P_beta_sp(float): 太陽熱集熱部の傾斜角 (°)

    Returns:
      ndarray: 1時間当たりの補機の消費電力量 (kWh/h)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）' or ls_type == 'ソーラーシステム':
        # 1時間当たりの循環ポンプの消費電力量
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

def calc_Q_tank_d_t(Theta_wtr_d_t, delta_tau_w_tank_out_d_t, M_w_tank_out_d_t, Theta_w_tank_mixed_d_t, Theta_w_tank_upper_d_t, t_hc_start_d):
    """1時間当たりの貯湯タンク出湯熱量 (MJ/h) (3)

    Args:
      Theta_wtr_d_t(ndarray): 日平均給水温度 (℃)
      delta_tau_w_tank_out_d_t(ndarray): 貯湯タンクの放熱係数(W/K)
      M_w_tank_out_d_t(ndarray): 集熱配管の放熱係数 (W/(m.K)
      Theta_w_tank_mixed_d_t(ndarray): 熱交換器の伝熱係数 (-)
      Theta_w_tank_upper_d_t(ndarray): タンク容量 (L)
      t_hc_start_d(ndarray): 集熱開始時刻

    Returns:
      ndarray: 1時間当たりの貯湯タンク出湯熱量( MJ/h)

    """
    # 水の定圧比熱
    c_p_water = get_c_p_water()

    Q_tank_d_t = np.zeros(24 * 365)

    # delta_tau_w_tank_out_d_t == 0の場合
    f1 = delta_tau_w_tank_out_d_t == 0
    Q_tank_d_t[f1] = 0

    # delta_tau_w_tank_out_d_t > 0の場合
    f2 = delta_tau_w_tank_out_d_t > 0

    # 貯湯タンクから出水する水の温度
    Theta_w_tank_out_d_t = calc_Theta_w_tank_out_d_t(delta_tau_w_tank_out_d_t, Theta_w_tank_mixed_d_t, Theta_w_tank_upper_d_t, t_hc_start_d)

    Q_tank_d_t[f2] = c_p_water * M_w_tank_out_d_t[f2]  * (Theta_w_tank_out_d_t[f2] - Theta_wtr_d_t[f2] ) * 10 ** (-3)

    return Q_tank_d_t


# ============================================================================
# 8.2 貯湯タンクから出水する水の温度
# ============================================================================

def calc_Theta_w_tank_out_d_t(delta_tau_w_tank_out_d_t, Theta_w_tank_mixed_d_t, Theta_w_tank_upper_d_t, t_hc_start_d):
    """貯湯タンクから出水する水の温度 (℃) (4)

    Args:
      delta_tau_w_tank_out_d_t(ndarray): 貯湯タンクの放熱係数(W/K)
      Theta_w_tank_mixed_d_t(ndarray): 熱交換器の伝熱係数 (-)
      Theta_w_tank_upper_d_t(ndarray): タンク容量 (L)
      t_hc_start_d(ndarray): 集熱開始時刻 (L)

    Returns:
      ndarray: 貯湯タンクから出水する水の温度( ℃)

    """
    Theta_w_tank_out_d_t = np.zeros(24 * 365)

    # (4-1)
    # delta_tau_w_tank_out_d_t > 0 and t_hc_start_d == 1 の場合
    f1 = np.logical_and(delta_tau_w_tank_out_d_t > 0, t_hc_start_d == 1)
    Theta_w_tank_mixed_d_t_prev = np.roll(Theta_w_tank_mixed_d_t, 1)
    Theta_w_tank_out_d_t[f1] = Theta_w_tank_mixed_d_t_prev[f1]

    # (4-2)
    # delta_tau_w_tank_out_d_t > 0 and t_hc_start_d == 0 の場合
    f2 = np.logical_and(delta_tau_w_tank_out_d_t > 0, t_hc_start_d == 0)
    Theta_w_tank_upper_d_t_prev = np.roll(Theta_w_tank_upper_d_t, 1)
    Theta_w_tank_out_d_t[f2] =Theta_w_tank_upper_d_t_prev[f2]

    # 貯湯タンクからの出水がない場合は定義しない
    f3 = delta_tau_w_tank_out_d_t == 0
    Theta_w_tank_out_d_t[f3] = np.nan

    return Theta_w_tank_out_d_t


# ============================================================================
# 8.3 貯湯タンクの水の温度
# ============================================================================

def calc_M_w_tank_out(Gamma_wu_tank_upper, M_w_tank_upper_prev):
    """貯湯タンクから出水する水の質量 (kg/h) (5)

    Args:
      Gamma_wu_tank_upper(float): 貯湯タンク上層部の水の使用率
      M_w_tank_upper_prev(float): 1時間前の貯湯タンク上層部の水の質量

    Returns:
      float: 貯湯タンクから出水する水の質量 (kg/h)

    """
    # 計算タイムステップ
    Delta_t_calc = get_Delta_t_calc()

    return (Gamma_wu_tank_upper * M_w_tank_upper_prev / Delta_t_calc)


# ============================================================================
# 8.4 貯湯タンクから出水する水の質量
# ============================================================================

def calc_Theta_w_tank(c_p_htm, eta_r_tank, Theta_wtr, UA_tank,
                      M_w_tank_total, Gamma_w_tank, Gamma_w_tank_prev, M_w_tank_upper, M_w_tank_out, M_w_tank_lower, M_w_tank_lower_prev,
                      Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, Theta_w_tank_lower_prev, Gamma_wu_tank_upper,
                      delta_tau_w_tank_out, t_hc_start_d, Theta_htm_stcs, Beta_htm_stcs, Beta_htm_tank, Epsilon_t_hx, G_htm, Theta_ex, delta_tau_hc):
    """貯湯タンクの水の温度 (6) (7)

    Args:
      c_p_htm(float): 熱媒の定圧比熱
      eta_r_tank(float): 有効出湯効率
      Theta_wtr(float): 日平均給水温度 (℃)
      UA_tank(float): 貯湯タンクの放熱係数(W/K)
      M_w_tank_total(float): 貯湯タンク全体の水の質量 
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比
      Gamma_w_tank_prev(float): 1時間前の入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比
      M_w_tank_upper(float): 入水・出水後の貯湯タンク上層部の水の質量
      M_w_tank_out(float): 貯湯タンクから出水する水の質量
      M_w_tank_lower(float): 入水・出水後の貯湯タンク下層部の水の質量
      M_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の質量
      Theta_w_tank_mixed_prev(float): 1時間前の完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度
      Theta_w_tank_upper_prev(float): 1時間前の入水・出水後の貯湯タンク上層部の水の温度
      Theta_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の温度
      Gamma_wu_tank_upper(float): 貯湯タンク上層部の水の使用率
      delta_tau_w_tank_out(float): 貯湯タンクからの出水時間数
      t_hc_start_d(float): 集熱開始時刻
      Theta_htm_stcs(float): 熱的平衡状態を仮定した場合の集熱経路における熱媒温度
      Beta_htm_stcs(float): 集熱配管還り熱媒温度の算定に係る集熱経路に対して熱的平衡状態を仮定した場合の集熱経路における熱媒温度に対する案分比率
      Beta_htm_tank(float): 集熱配管還り熱媒温度の算定に係る貯湯タンクの下層部の水の温度に対する案分比率
      Epsilon_t_hx(float): 熱交換器の温度効率
      G_htm(float): 熱媒の循環量
      Theta_ex(float): 外気温度
      delta_tau_hc(int): 集熱時間数

    Returns:
      tuple: 入水・出水後の貯湯タンク上層部の水の温度( ℃), 入水・出水後の貯湯タンク下層部の水の温度（℃）

    """
    Theta_w_tank_upper_dt = 0
    Theta_w_tank_lower_dt = 0

    # 貯湯タンク全体の水の質量
    M_w_tank_mix = calc_M_w_tank_mix(eta_r_tank, M_w_tank_total, Gamma_w_tank, delta_tau_w_tank_out, delta_tau_hc)

    # 集熱量のうち貯湯タンク下層部で熱交換される割合
    Gamma_hx_tank = calc_Gamma_hx_tank(Gamma_w_tank)

    # 水の定圧比熱
    c_p_water = get_c_p_water()

    # 計算タイムステップ
    Delta_t_calc = get_Delta_t_calc()

    # 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素
    at_11, at_12, at_21, at_22 = calc_at(c_p_htm, UA_tank, M_w_tank_mix, Gamma_w_tank, M_w_tank_upper, M_w_tank_lower, Gamma_hx_tank, G_htm, Epsilon_t_hx, 
                   Beta_htm_tank, c_p_water, Delta_t_calc)

    # 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の行列式
    detA = calc_detA(at_11, at_12, at_21, at_22)

    # 連立方程式を行列表現した場合の日付の時刻における定数項ベクトルの要素 
    bt_1, bt_2 = calc_bt(c_p_htm, Theta_wtr, UA_tank, Gamma_w_tank, Gamma_w_tank_prev, M_w_tank_upper, M_w_tank_out, M_w_tank_lower, M_w_tank_lower_prev,
                  Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, Theta_w_tank_lower_prev, Gamma_wu_tank_upper, Gamma_hx_tank, G_htm, Epsilon_t_hx,
                  Theta_htm_stcs, Beta_htm_stcs, c_p_water, Delta_t_calc, t_hc_start_d, Theta_ex)

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


def calc_detA(at_11, at_12, at_21, at_22):
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


def calc_at(c_p_htm, UA_tank, M_w_tank_mix, Gamma_w_tank, M_w_tank_upper, M_w_tank_lower, Gamma_hx_tank, G_htm, Epsilon_t_hx,
            Beta_htm_tank, c_p_water, Delta_t_calc):
    """連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 (-) (9) (10) (11) (12)

    Args:
      c_p_htm(float): 熱媒の定圧比熱
      UA_tank(float): 貯湯タンクの放熱係数(W/K)
      M_w_tank_mix(float): 貯湯タンクから出水する水の質量
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比
      M_w_tank_upper(float): 入水・出水後の貯湯タンク上層部の水の質量
      Gamma_hx_tank(float): 集熱量のうち貯湯タンク下層部で熱交換される割合
      G_htm(float): 1時間当たりの熱媒の循環量
      Epsilon_t_hx(float): 熱交換器の温度効率
      Beta_htm_tank(float): 集熱配管還り熱媒温度の算定に係る貯湯タンクの下層部の水の温度に対する案分比率
      c_p_water(float): 水の定圧比熱
      Delta_t_calc(float): 計算タイムステップ

    Returns:
      tuple: 連立方程式を行列表現した場合の日付の時刻における係数行列の逆行列の要素 at_11, at_12, at_21, at_22 (-) 

    """
    # (9)
    at_11 = (c_p_water * M_w_tank_upper) / Delta_t_calc + 3.6 * (1 - Gamma_w_tank) * UA_tank + c_p_water * M_w_tank_mix + (1 - Gamma_hx_tank) ** 2 * c_p_htm * G_htm * Epsilon_t_hx * (1 - Beta_htm_tank)

    # (10)
    at_12 = -c_p_water * M_w_tank_mix + Gamma_hx_tank * (1 - Gamma_hx_tank) * c_p_htm * G_htm * Epsilon_t_hx * (1 - Beta_htm_tank)

    # (11)
    at_21 = -c_p_water * M_w_tank_mix + Gamma_hx_tank * (1 - Gamma_hx_tank) * c_p_htm * G_htm * Epsilon_t_hx * (1 - Beta_htm_tank)

    # (12)
    at_22 = (c_p_water * M_w_tank_lower) / Delta_t_calc + 3.6 * Gamma_w_tank * UA_tank + c_p_water * M_w_tank_mix + (Gamma_hx_tank) ** 2 * c_p_htm * G_htm * Epsilon_t_hx * (1 - Beta_htm_tank)

    return at_11, at_12, at_21, at_22


def calc_bt(c_p_htm, Theta_wtr, UA_tank, Gamma_w_tank, Gamma_w_tank_prev, M_w_tank_upper, M_w_tank_out, M_w_tank_lower, M_w_tank_lower_prev,
            Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, Theta_w_tank_lower_prev, Gamma_wu_tank_upper, Gamma_hx_tank, G_htm, Epsilon_t_hx,
            Theta_htm_stcs, Beta_htm_stcs, c_p_water, Delta_t_calc, t_hc_start_d, Theta_ex):
    """連立方程式を行列表現した場合の日付の時刻における定数項ベクトルの要素 (-) (13) (14)

    Args:
      c_p_htm(float): 熱媒の定圧比熱
      Theta_wtr(float): 日平均給水温度 (℃)
      UA_tank(float): 貯湯タンクの放熱係数(W/K)
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比
      Gamma_w_tank_prev(float): 1時間前の入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比
      M_w_tank_upper(float): 入水・出水後の貯湯タンク上層部の水の質量
      M_w_tank_out(float): 貯湯タンクから出水する水の質量
      M_w_tank_lower(float): 入水・出水後の貯湯タンク下層部の水の質量
      M_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の質量
      Theta_w_tank_mixed_prev(float): 1時間前の完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度
      Theta_w_tank_upper_prev(float): 1時間前の入水・出水後の貯湯タンク上層部の水の温度
      Theta_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の温度
      Gamma_wu_tank_upper(float): 貯湯タンク上層部の水の使用率
      Gamma_hx_tank(float): 集熱量のうち貯湯タンク下層部で熱交換される割合
      G_htm(float): 1時間当たりの熱媒の循環量
      Epsilon_t_hx(float): 熱交換器の温度効率
      Theta_htm_stcs(float): 熱的平衡状態を仮定した場合の集熱経路における熱媒温度
      Beta_htm_stcs(float): 集熱配管還り熱媒温度の算定に係る集熱経路に対して熱的平衡状態を仮定した場合の集熱経路における熱媒温度に対する案分比率
      c_p_water(float): 水の定圧比熱
      Delta_t_calc(float): 計算タイムステップ
      t_hc_start_d(float): 集熱開始時刻
      Theta_ex(float): 外気温度

    Returns:
      tuple: 連立方程式を行列表現した場合の日付の時刻における定数項ベクトルの要素 bt_1, bt_2 (-) 

    """
    # 入水・出水後に熱的平衡状態となる前の貯湯タンク上層部の水が有する熱量(0℃基準
    Q_star_w_tank_upper, Q_star_w_tank_lower = calc_Q_star_w_tank(
                          Theta_wtr, M_w_tank_upper, M_w_tank_out, M_w_tank_lower, M_w_tank_lower_prev,
                          Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, Theta_w_tank_lower_prev, 
                          Gamma_w_tank, Gamma_w_tank_prev, Gamma_wu_tank_upper, t_hc_start_d, c_p_water, Delta_t_calc
    )

    # (13)
    bt_1 = (Q_star_w_tank_upper / Delta_t_calc) + 3.6 * (1 - Gamma_w_tank) * UA_tank * Theta_ex + (1 - Gamma_hx_tank) * c_p_htm * G_htm * Epsilon_t_hx * Beta_htm_stcs * Theta_htm_stcs

    # (14)
    bt_2 = (Q_star_w_tank_lower / Delta_t_calc) + 3.6 * Gamma_w_tank * UA_tank * Theta_ex + Gamma_hx_tank * c_p_htm * G_htm * Epsilon_t_hx * Beta_htm_stcs * Theta_htm_stcs

    return bt_1, bt_2


def calc_Q_star_w_tank(Theta_wtr, M_w_tank_upper, M_w_tank_out, M_w_tank_lower, M_w_tank_lower_prev, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, Theta_w_tank_lower_prev,
                       Gamma_w_tank, Gamma_w_tank_prev, Gamma_wu_tank_upper, t_hc_start_d, c_p_water, Delta_t_calc):
    """入水・出水後に熱的平衡状態となる前の貯湯タンク上層部と下層部の水が有する熱量(0℃基準) (kJ) (15) (16)

    Args:
    Theta_wtr(float): 日平均給水温度 (℃)
    M_w_tank_upper(float): 入水・出水後の貯湯タンク上層部の水の質量
    M_w_tank_out(float): 貯湯タンクから出水する水の質量
    M_w_tank_lower(float): 入水・出水後の貯湯タンク下層部の水の質量
    M_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の質量
    Theta_w_tank_mixed_prev(float): 1時間前の完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度
    Theta_w_tank_upper_prev(float): 1時間前の入水・出水後の貯湯タンク上層部の水の温度
    Theta_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の温度
    Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比
    Gamma_w_tank_prev(float): 1時間前の入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比
    Gamma_wu_tank_upper(float): 貯湯タンク上層部の水の使用率
    t_hc_start_d(float): 集熱開始時刻
    c_p_water(float): 水の定圧比熱
    Delta_t_calc(float): 熱交換器の温度効率

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


def calc_Theta_w_tank_mixed(Gamma_w_tank, Theta_w_tank_upper, Theta_w_tank_lower):
    """完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度 (℃) (17)

    Args:
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比
      Theta_w_tank_upper(float): 入水・出水後の貯湯タンク上層部の水の温度
      Theta_w_tank_lower(float): 入水・出水後の貯湯タンク下層部の水の温度

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

def calc_M_w_tank_upper(M_w_tank_total, Gamma_wu_tank_upper, M_w_tank_out, M_w_tank_upper_prev, M_w_tank_lower_prev, Gamma_w_tank_prev, t_hc_start_d):
    """入水・出水後の貯湯タンク上層部の水の質量 (kg) (18)

    Args:
      M_w_tank_total(int): 貯湯タンク上層部の水の使用率
      Gamma_wu_tank_upper(float): 貯湯タンク上層部の水の使用率
      M_w_tank_out(float): 貯湯タンクから出水する水の質量
      M_w_tank_upper_prev(float): 1時間前の入水・出水後の貯湯タンク上層部の水の質量
      M_w_tank_lower_prev(float): 1時間前の入水・出水後の貯湯タンク下層部の水の質量
      Gamma_w_tank_prev(float): 1時間前の入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比
      t_hc_start_d(int): 集熱開始時刻

    Returns:
      float: 入水・出水後の貯湯タンク上層部の水の質量 (kg)

    """
    # 計算タイムステップ
    Delta_t_calc = get_Delta_t_calc()

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


def calc_M_w_tank_lower(M_w_tank_total, M_w_tank_upper):
    """入水・出水後の貯湯タンク下層部の水の質量 (kg) (19)

    Args:
      M_w_tank_total(float): 貯湯タンク全体の水の質量
      M_w_tank_upper(float): 入水・出水後の貯湯タンク上層部の水の質量

    Returns:
      float: 入水・出水後の貯湯タンク下層部の水の質量 (kg) 

    """
    return M_w_tank_total - M_w_tank_upper


def calc_M_w_tank_mix(eta_r_tank, M_w_tank_total, Gamma_w_tank, delta_tau_w_tank_out, delta_tau_hc):
    """貯湯タンク全体の水の質量 (kg) (20)

    Args:
      eta_r_tank(float): 有効出湯効率
      M_w_tank_total(float): 貯湯タンク全体の水の質量
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比
      delta_tau_w_tank_out(float): 貯湯タンクからの出水時間数
      delta_tau_hc(int): 集熱時間数

    Returns:
      ndarray: 貯湯タンク全体の水の質量 (kg) 

    """
    # 1時間当たりの貯湯タンクの上層部・下層部間での混合回数
    n_w_tank_mix = calc_n_w_tank_mix(eta_r_tank, Gamma_w_tank, delta_tau_w_tank_out, delta_tau_hc)

    return n_w_tank_mix * M_w_tank_total


def calc_n_w_tank_mix(eta_r_tank, Gamma_w_tank, delta_tau_w_tank_out, delta_tau_hc):
    """1時間当たりの貯湯タンクの上層部・下層部間での混合回数 (回/h) (21)

    Args:
      eta_r_tank(float): 有効出湯効率
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比
      delta_tau_w_tank_out(float): 貯湯タンクからの出水時間数
      delta_tau_hc(int): 集熱時間数

    Returns:
      ndarray: 1時間当たりの貯湯タンクの上層部・下層部間での混合回数 (回/h)

    """
    n_w_tank_mix = 0

    if Gamma_w_tank == 0:
      # (21-1)
      n_w_tank_mix = 0

    if Gamma_w_tank > 0:
        if delta_tau_hc > 0:
          # 集熱時における混合回数
          n_w_tank_mix_hc = get_n_w_tank_mix_hc()

          # (21-2a)
          n_w_tank_mix = n_w_tank_mix_hc

        elif delta_tau_hc == 0:
          # 非集熱時であって貯湯タンクからの出水がある場合の混合回数
          n_w_tank_mix_non_hc_out = get_n_w_tank_mix_non_hc_out(eta_r_tank)

          if delta_tau_w_tank_out == 0:
            # 非集熱時であって貯湯タンクからの出水がない場合の混合回数
            n_w_tank_mix_non_hc_stop = calc_n_w_tank_mix_non_hc_stop(n_w_tank_mix_non_hc_out)

            # (21-3a)
            n_w_tank_mix = n_w_tank_mix_non_hc_stop

          elif delta_tau_w_tank_out > 0:
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


def calc_n_w_tank_mix_non_hc_stop(n_w_tank_mix_non_hc_out):
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
      eta_r_tank(float): 有効出湯効率

    Returns:
      float: 非集熱時であって貯湯タンクからの出水がある場合の混合回数 (回/h)

    """
    return 1 - eta_r_tank / 100


def calc_Gamma_w_tank(M_w_tank_total, M_w_tank_lower):
    """入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-) (22)

    Args:
      M_w_tank_total(float): 貯湯タンク全体の水の質量
      M_w_tank_lower(float): 入水・出水後の貯湯タンク下層部の水の質量

    Returns:
      float: 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比 (-) 

    """
    return (M_w_tank_lower / M_w_tank_total)


def calc_M_w_tank_total(V_tank):
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
    """集熱量のうち貯湯タンク下層部で熱交換される割合 (-) (24)

    Args:
      Gamma_w_tank(float): 入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比

    Returns:
      float: 集熱量のうち貯湯タンク下層部で熱交換される割合 (-)

    """
    # 集熱量のうち貯湯タンク下層部で熱交換される割合を表す関係式を切り替える、入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比の値
    Gamma_limw_tank = get_Gamma_limw_tank()

    # 集熱量のうち貯湯タンク下層部で熱交換される割合の計算領域を確保
    Gamma_hx_tank = 0

    # (24-1)
    if Gamma_w_tank >= Gamma_limw_tank:
      Gamma_hx_tank = 1

    # (24-2)
    if Gamma_w_tank  < Gamma_limw_tank:
      Gamma_hx_tank = (1 / Gamma_limw_tank) * Gamma_w_tank

    return Gamma_hx_tank


def get_Gamma_limw_tank():
    """集熱量のうち貯湯タンク下層部で熱交換される割合を表す関係式を切り替える、入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比の値
    Args:

    Returns:
      float: 集熱量のうち貯湯タンク下層部で熱交換される割合を表す関係式を切り替える、入水・出水後の貯湯タンク全体の水の質量に対する下層部の水の質量の比の値

    """
    return 0.5


# ============================================================================
# 8.7 貯湯タンク上層部の水の使用率
# ============================================================================

def calc_Gamma_wu_tank_upper(ls_type, hw_connection_type, Theta_wtr, Q_W_dmd_sun, M_w_tank_total, M_w_tank_upper_prev,
                            Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, delta_tau_w_tank_out, t_hc_start_d):
    """貯湯タンク上層部の水の使用率 (-) (25)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      hw_connection_type(str): 給湯接続方式の種類
      Theta_wtr(float): 日平均給水温度 (℃)
      Q_W_dmd_sun(float): 給湯熱需要（浴槽追焚を除く） (MJ/h)
      M_w_tank_total(float): 貯湯タンクの放熱係数(W/K)
      M_w_tank_upper_prev(float): 貯湯タンク上層部の水の質量
      Theta_w_tank_mixed_prev(float): 一時間前の入水・出水後の貯湯タンク上層部の水の温度
      Theta_w_tank_upper_prev(float): 一時間前の入水・出水後の貯湯タンク下層部の水の温度
      delta_tau_w_tank_out(float): 貯湯タンクからの出水時間数
      t_hc_start_d(int): 集熱開始時刻

    Returns:
      float: 貯湯タンク上層部の水の使用率 (-)

    """
    if delta_tau_w_tank_out == 0:
        # (25-1)
        return 0
    elif delta_tau_w_tank_out > 0:
        # 給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量
        M_reqw_tank_upper = calc_M_reqw_tank_upper(ls_type, hw_connection_type, Theta_wtr, Q_W_dmd_sun, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d)

        # 給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量を算出する際に基準となる貯湯タンク上層部の水の質量
        M_reqw_tank = calc_M_reqw_tank(M_w_tank_total, M_w_tank_upper_prev, t_hc_start_d)

        # (25-2a)
        return min(M_reqw_tank_upper / M_reqw_tank, 1)


def calc_M_reqw_tank_upper(ls_type, hw_connection_type, Theta_wtr, Q_W_dmd_sun, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d):
    """給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量 (kg) (25-2b)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      hw_connection_type(str): 給湯接続方式の種類
      Theta_wtr(float): 日平均給水温度 (℃)
      Q_W_dmd_sun(float): 給湯熱需要（浴槽追焚を除く） (MJ/h)
      Theta_w_tank_mixed_prev(float): 一時間前の入水・出水後の貯湯タンク上層部の水の温度
      Theta_w_tank_upper_prev(float): 一時間前の入水・出水後の貯湯タンク下層部の水の温度
      t_hc_start_d(int): 集熱開始時刻
    
    Returns:
      float: 給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量 (kg)
    
    """
    # 給湯熱需要を満たすために必要となる貯湯タンクから出水する水の質量
    M_reqw_tank_out = calc_M_reqw_tank_out(Theta_wtr, Q_W_dmd_sun, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d)

    # 貯湯タンクから給水混合弁までの給湯配管の熱損失率
    f_loss_pipe_tank_valve  =  calc_f_loss_pipe_tank_valve(ls_type, hw_connection_type, M_reqw_tank_out)

    # 計算タイムステップ
    Delta_t_calc = get_Delta_t_calc()

    return (M_reqw_tank_out / (1 - f_loss_pipe_tank_valve)) * Delta_t_calc


def calc_M_reqw_tank_out(Theta_wtr, Q_W_dmd_sun, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d):
    """給湯熱需要を満たすために必要となる貯湯タンクから出水する水の質量 (kg/h) (25-2c)

    Args:
      Theta_wtr(float): 日平均給水温度 (℃)
      Q_W_dmd_sun(float): 給湯熱需要（浴槽追焚を除く） (MJ/h)
      Theta_w_tank_mixed_prev(float): 一時間前の入水・出水後の貯湯タンク上層部の水の温度
      Theta_w_tank_upper_prev(float): 一時間前の入水・出水後の貯湯タンク下層部の水の温度
      t_hc_start_d(int): 集熱開始時刻
    
    Returns:
      float: 給湯熱需要を満たすために必要となる貯湯タンクから出水する水の質量 (kg/h)
    
    """
    # 水の定圧比熱
    c_p_water = get_c_p_water()

    # 給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量を算出する際に基準となる貯湯タンク上層部の水の温度
    Theta_reqw_tank = calc_Theta_reqw_tank(Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d)

    return (Q_W_dmd_sun * (10) ** 3 / c_p_water) / (Theta_reqw_tank - Theta_wtr)


def calc_M_reqw_tank(M_w_tank_total, M_w_tank_upper_prev, t_hc_start_d):
    """給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量を算出する際に基準となる貯湯タンク上層部の水の質量 (kg) (26)

    Args:
      M_w_tank_total(float): 貯湯タンクの放熱係数(W/K)
      M_w_tank_upper_prev(float): 貯湯タンク上層部の水の質量
      t_hc_start_d(int): 集熱開始時刻

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


def calc_Theta_reqw_tank(Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d):
    """給湯熱需要を満たすために必要となる貯湯タンク上層部の水の質量を算出する際に基準となる貯湯タンク上層部の水の温度 (℃) (27)

    Args:
      Theta_w_tank_mixed_prev(float): 一時間前の入水・出水後の貯湯タンク上層部の水の温度
      Theta_w_tank_upper_prev(float): 一時間前の入水・出水後の貯湯タンク下層部の水の温度
      t_hc_start_d(int): 集熱開始時刻

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


def calc_Q_W_dmd_sun_d_t(Q_W_dmd_excl_ba2_d_t):
    """給湯熱需要のうちの太陽熱利用設備の分担分 (MJ/h) (28)

    Args:
      Q_W_dmd_excl_ba2_d_t(ndarray): 1時間当たりの給湯熱需要（浴槽追焚を除く） (MJ/h)

    Returns:
      ndarray: 給湯熱需要のうちの太陽熱利用設備の分担分 (MJ/h)

    """
    Q_W_dmd_sun_d_t = Q_W_dmd_excl_ba2_d_t

    return Q_W_dmd_sun_d_t


# ============================================================================
# 8.8 貯湯タンクからの出水時間数
# ============================================================================

def calc_delta_tau_w_tank_out(ls_type, Theta_wtr, Theta_ex_p6h_Ave, Q_W_dmd_sun, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d):
    """貯湯タンクからの出水時間数 (h/h) (29)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      A_stcp(float): 集熱部の有効集熱面積(m2)
      b0(float): 集熱器の集熱効率特性線図一次近似式の切片（-）
      b1(float): 集熱器の集熱効率特性線図一次近似式の傾き（W/(m2・K)）
      Q_W_dmd_sun(float): 給湯熱需要（浴槽追焚を除く） (MJ/h)
      Theta_w_tank_mixed_prev(float): 完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度
      Theta_w_tank_upper_prev(float): 入水・出水後の貯湯タンク上層部の水の温度
      dt(int): 時間

    Returns:
      float: 貯湯タンクからの出水時間数 (h/h)

    """
    # 貯湯タンク内の水の利用可否
    isAvailable_w_tank = calc_isAvailable_w_tank(ls_type, Theta_wtr, Theta_ex_p6h_Ave, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d)

    # 貯湯タンクからの出水時間数の計算領域を確保
    delta_tau_w_tank_out = 0

    # Q_W_dmd_sun == 0 or isAvailable_w_tank == False の場合
    # (29-1)
    f1 =Q_W_dmd_sun == 0 or isAvailable_w_tank == False
    if f1:
      delta_tau_w_tank_out = 0

    # Q_W_dmd_sun > 0 and isAvailable_w_tank == True の場合
    # (29-2)
    f2 = Q_W_dmd_sun > 0 and isAvailable_w_tank == True
    if f2:
      delta_tau_w_tank_out = 1

    return delta_tau_w_tank_out


# ============================================================================
# 8.9 日時が1月1日0時である場合の一時刻前における貯湯タンクの水の質量・温度
# ============================================================================

def calc_M_w_tank_upper_prev(V_tank):
    """一時刻前における貯湯タンク上層部の水の質量 (kg) (30)

    Args:
      V_tank(int): 貯湯タンクの容量 (L)

    Returns:
      int: 一時刻前における貯湯タンク上層部の水の質量 (kg)

    """
    # 貯湯タンク全体の水の質量
    return calc_M_w_tank_total(V_tank)


def calc_Theta_w_tank_upper_prev(Theta_wtr_d):
    """一時刻前における貯湯タンク上層部の水の質量 (kg) (31)

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

def calc_Theta_htm_stcs_d_t(b0, b1, I_s_d_t, Theta_ex_d_t, Epsilon_t_stp_d_t, Epsilon_t_stc_d_t, e_t_stcs_d_t):
    """熱的平衡状態を仮定した場合の集熱経路における熱媒温度 (℃) (32)

    Args:
      b0(float): 集熱器の集熱効率特性線図一次近似式の切片（-）
      b1(float): 集熱器の集熱効率特性線図一次近似式の傾き（W/(m2・K)）
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)
      Theta_ex_d_t(ndarray): 外気温度
      Epsilon_t_stp_d_t(ndarray): 集熱配管の温度効率
      Epsilon_t_stc_d_t(ndarray): 集熱器の温度効率
      e_t_stcs_d_t(ndarray): 集熱経路の総合温度効率

    Returns:
      ndarray: 熱的平衡状態を仮定した場合の集熱経路における熱媒温度 (℃)

    """
    # 集熱器のみに対して熱的平衡状態を仮定した場合の集熱器における熱媒温度
    Theta_htm_stc_d_t = calc_Theta_htm_stc_d_t(b0, b1, I_s_d_t, Theta_ex_d_t)

    return (((1 - Epsilon_t_stp_d_t) * Epsilon_t_stc_d_t) / e_t_stcs_d_t) * (Theta_htm_stc_d_t - Theta_ex_d_t) + Theta_ex_d_t


def calc_Theta_htm_stc_d_t(b0, b1, I_s_d_t, Theta_ex_d_t):
    """集熱器のみに対して熱的平衡状態を仮定した場合の集熱器における熱媒温度 (℃) (33)

    Args:
      b0(float): 集熱器の集熱効率特性線図一次近似式の切片（-）
      b1(float): 集熱器の集熱効率特性線図一次近似式の傾き（W/(m2・K)）
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)
      Theta_ex_d_t(ndarray): 外気温度

    Returns:
      ndarray: 集熱器のみに対して熱的平衡状態を仮定した場合の集熱器における熱媒温度 (℃)

    """
    return (b0 / b1) * I_s_d_t + Theta_ex_d_t


# ============================================================================
# 9.2. 集熱経路の総合温度効率
# ============================================================================

def calc_e_t_stcs_d_t(Epsilon_t_stp_d_t, Epsilon_t_stc_d_t):
    """集熱経路の総合温度効率 (-) (34)

    Args:
      Epsilon_t_stp_d_t(ndarray): 集熱配管の温度効率
      Epsilon_t_stc_d_t(ndarray): 集熱器の温度効率

    Returns:
      ndarray: 集熱経路の総合温度効率 (-)

    """
    return (1 - (1 - Epsilon_t_stp_d_t) ** 2 * (1 - Epsilon_t_stc_d_t))


# ============================================================================
# 9.3. 集熱配管還り熱媒温度の算定に係る案分比率
# ============================================================================

def calc_Beta_htm_tank_d_t(e_stcs_d_t, Epsilon_t_hx_d_t):
    """集熱配管還り熱媒温度の算定に係る貯湯タンクの下層部の水の温度に対する案分比率 (-) (35)

    Args:
      e_stcs_d_t(ndarray): 集熱経路の総合温度効率
      Epsilon_t_hx_d_t(ndarray): 熱交換器の温度効率

    Returns:
      ndarray: 集熱配管還り熱媒温度の算定に係る貯湯タンクの下層部の水の温度に対する案分比率 (-)

    """
    return (1 - e_stcs_d_t) * Epsilon_t_hx_d_t / (1 - (1 - e_stcs_d_t) * (1 - Epsilon_t_hx_d_t))


def calc_Beta_htm_stcs_d_t(e_stcs_d_t, Epsilon_t_hx_d_t):
    """集熱配管還り熱媒温度の算定に係る集熱経路に対して熱的平衡状態を仮定した場合の集熱経路における熱媒温度に対する案分比率 (-) (36)

    Args:
      e_stcs_d_t(ndarray): 集熱経路の総合温度効率
      Epsilon_t_hx_d_t(ndarray): 熱交換器の温度効率

    Returns:
      ndarray: 集熱配管還り熱媒温度の算定に係る集熱経路に対して熱的平衡状態を仮定した場合の集熱経路における熱媒温度に対する案分比率 (-)

    """
    return e_stcs_d_t / (1 - (1 - e_stcs_d_t) * (1 - Epsilon_t_hx_d_t))


# ============================================================================
# 9.4 循環ポンプ
# ============================================================================

def calc_E_pump_d_t(region, sol_region, ls_type, P_pump_hc, P_pump_non_hc, P_alpha_sp, P_beta_sp):
    """1時間当たりの循環ポンプの消費電力量 (37)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
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
    P_pump_hc = calc_P_pump_hc(ls_type, P_pump_hc)

    # 1時間当たりの集熱時間数
    delta_tau_hc_d_t = calc_delta_tau_hc_d_t(ls_type, I_s_d_t)

    # 1時間当たりの集熱時における循環ポンプの稼働時間数
    delta_tau_pump_hc_d_t = calc_delta_tau_pump_hc_d_t(ls_type, delta_tau_hc_d_t)

    # 非集熱時における循環ポンプの消費電力量 (W)
    P_pump_non_hc = calc_P_pump_non_hc(ls_type, P_pump_non_hc)

    # 1時間当たりの非集熱時における循環ポンプの稼働時間数
    delta_tau_pump_non_hc_d_t = calc_delta_tau_pump_non_hc_d_t(ls_type, I_s_d_t, delta_tau_hc_d_t)

    return (P_pump_hc * delta_tau_pump_hc_d_t + P_pump_non_hc * delta_tau_pump_non_hc_d_t) * 10 ** (-3)


# ============================================================================
# 10. 給湯接続部
# ============================================================================

def calc_f_pipe_loss_tank_boiler(ls_type, hw_connection_type, M_w_pipe):
    """貯湯タンクから補助熱源機までの給湯配管の熱損失率 (-) (38)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      hw_connection_type(str): 給湯接続方式の種類
      M_w_tank_out_d_t(ndarray): 集熱部の有効集熱面積(m2)

    Returns:
      ndarray: 貯湯タンクから補助熱源機までの給湯配管の熱損失率 (-)

    """
    f_pipe_loss_tank_boiler = np.zeros(24 *365)

    # 給湯配管からの熱損失の程度を判断する基準となる1時間当たりの貯湯タンクから出水する水の質量
    M_w_tank_out_lim = get_M_w_tank_out_lim()

    f1 = M_w_pipe <= M_w_tank_out_lim
    f2 = M_w_pipe > M_w_tank_out_lim

    if hw_connection_type == "接続ユニット方式":
          if ls_type == '密閉形太陽熱温水器（直圧式）':
              # (38-1)
              f_pipe_loss_tank_boiler[f1] =  0.187
              f_pipe_loss_tank_boiler[f2] =  0.064
          elif ls_type == 'ソーラーシステム':
              # (38-2)
              f_pipe_loss_tank_boiler[f1] =  0.040
              f_pipe_loss_tank_boiler[f2] =  0.025
          else:
              raise ValueError(ls_type)
    elif hw_connection_type == "三方弁方式":
          # (40)
          f_pipe_loss_tank_boiler[f1] =  0.027
          f_pipe_loss_tank_boiler[f2] = 0.017
    elif hw_connection_type == "給水予熱方式":
          # (42)
          f_pipe_loss_tank_boiler[f1] =  0.174
          f_pipe_loss_tank_boiler[f2] =  0.059
    else:
        raise ValueError(hw_connection_type)

    return f_pipe_loss_tank_boiler


def calc_f_loss_pipe_tank_valve(ls_type, hw_connection_type, M_w_pipe):
    """貯湯タンクから給水混合弁までの給湯配管の熱損失率 (-) (39)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      hw_connection_type(str): 給湯接続方式の種類
      M_reqw_tank_out(float): 給湯配管内を流れる1時間当たりの水の質量

    Returns:
      float: 貯湯タンクから給水混合弁までの給湯配管の熱損失率 (-)

    """
    # 給湯配管からの熱損失の程度を判断する基準となる1時間当たりの貯湯タンクから出水する水の質量
    M_w_tank_out_lim = get_M_w_tank_out_lim()

    f1 = M_w_pipe <= M_w_tank_out_lim
    f2 = M_w_pipe > M_w_tank_out_lim

    if hw_connection_type == "接続ユニット方式":
          if ls_type == '密閉形太陽熱温水器（直圧式）':
              # (39-1)
              if f1:
                  return 0.187
              elif f2:
                  return 0.064
          elif ls_type == 'ソーラーシステム':
              # (39-2)
              if f1:
                  return 0.020
              elif f2:
                  return 0.013
          else:
              raise ValueError(ls_type)
    elif hw_connection_type == "三方弁方式":
        # (41)
        if f1:
            return 0.013
        elif f2:
            return 0.009
    elif hw_connection_type == "給水予熱方式":
        # (43)
        if f1:
            return 0.159
        elif f2:
            return 0.054
    else:
        raise ValueError(hw_connection_type)


# ============================================================================
# 10.4 給湯配管からの熱損失の程度を判断する基準となる貯湯タンクから出水する水の質量
# ============================================================================

def get_M_w_tank_out_lim():
    """給湯配管からの熱損失の程度を判断する基準となる1時間当たりの貯湯タンクから出水する水の質量 (kg/h)

    Args:

    Returns:
      int: 給湯配管からの熱損失の程度を判断する基準となる1時間当たりの貯湯タンクから出水する水の質量 (kg/h)

    """
    return 150


# ============================================================================
# 11. 仕様
# ============================================================================

def calc_b0(ls_type, b0):
    """集熱器の集熱効率特性線図一次近似式の切片 (-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      b0(float): 集熱器の集熱効率特性線図一次近似式の切片 (-)

    Returns:
      float: 集熱器の集熱効率特性線図一次近似式の切片 (-)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.calc_b0(b0)
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_b0(b0)


def calc_b1(ls_type, b1):
    """集熱器の集熱効率特性線図一次近似式の傾き W/(m2・K)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      b0(float): 集熱器の集熱効率特性線図一次近似式の傾き W/(m2・K)

    Returns: 集熱器の集熱効率特性線図一次近似式の傾き W/(m2・K)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.calc_b1(b1)
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_b1(b1)


def calc_c_p_htm(ls_type, c_p_htm):
    """熱媒の定圧比熱 (kJ/(kg.K))

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      c_p_htm(float): 熱媒の定圧比熱

    Returns: 熱媒の定圧比熱 (kJ/(kg.K)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return get_c_p_water()
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_c_p_htm(c_p_htm)


def calc_UA_hx(ls_type, UA_hx):
    """熱交換器の伝熱係数 (W/K)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      UA_hx(float): 熱交換器の伝熱係数

    Returns: 熱交換器の伝熱係数 (W/K)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.calc_UA_hx(UA_hx)
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_UA_hx(UA_hx)


def calc_P_pump_hc(ls_type, P_pump_hc):
    """集熱時における循環ポンプの消費電力量

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      P_pump_hc(float): 集熱時における循環ポンプの消費電力量 (W) [入力/固定]

    Returns:
      float: 集熱時における循環ポンプの消費電力量 (W)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_P_pump_hc()
    elif ls_type == 'ソーラーシステム':
        return lss2.get_P_pump_hc(P_pump_hc)


def calc_P_pump_non_hc(ls_type, P_pump_non_hc):
    """非集熱時における循環ポンプの消費電力量

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      P_pump_non_hc(float): 非集熱時における循環ポンプの消費電力量 (W) [入力/固定]

    Returns:
      float: 非集熱時における循環ポンプの消費電力量 (W)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_P_pump_non_hc()
    elif ls_type == 'ソーラーシステム':
        return lss2.get_P_pump_non_hc(P_pump_non_hc)


def calc_eta_r_tank(ls_type, eta_r_tank):
    """有効出湯効率 (W/K)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      eta_r_tank(float): 有効出湯効率

    Returns:
      float: 有効出湯効率 (W/K)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.calc_eta_r_tank(eta_r_tank)
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_eta_r_tank(eta_r_tank)


def calc_UA_tank(ls_type, UA_tank):
    """熱交換器の伝熱係数 (W/K)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      UA_tank(float): 有効出湯効率

    Returns:
      float: 熱交換器の伝熱係数 (W/K)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.calc_UA_tank(UA_tank)
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_UA_tank(UA_tank)


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
    """計算タイムステップ (h)
    
    Args:

    Returns:
      int: 計算タイムステップ (h)
    """
    return 1


def calc_G_htm_d_t(ls_type, g_htm, Gs_htm, I_s_d_t, delta_tau_hc_d_t):
    """1時間当たりの熱媒の循環量 (kg/h)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      g_htm(float): 単位日射量当たりの循環流量((kg/h)/(W/m2))
      Gs_htm(float): 熱媒の基準循環流量(kg/h)
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)
      delta_tau_hc_d_t(ndarray): 1時間当たりの集熱時間数(-)

    Returns:
      ndarray: 1時間当たりの熱媒の循環量 (kg/h)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.calc_G_htm_d_t(g_htm, I_s_d_t, delta_tau_hc_d_t)
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_G_htm_d_t(Gs_htm, delta_tau_hc_d_t)


def calc_delta_tau_hc_d_t(ls_type, I_s_d_t):
    """集熱開始時刻 (-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)

    Returns:
      ndarray: 集熱開始時刻 (-)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.calc_delta_tau_hc_d_t(I_s_d_t)
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_delta_tau_hc_d_t(I_s_d_t)


def calc_isAvailable_w_tank(ls_type, Theta_wtr, Theta_ex_p6h_Ave, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d):
    """貯湯タンク内の水の利用可否 (-)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      Theta_wtr(float): 日平均給水温度 (℃)
      Theta_w_tank_mixed_prev(float): 完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度
      Theta_w_tank_upper_prev(float): 入水・出水後の貯湯タンク上層部の水の温度
      t_hc_start_d(int): 集熱開始時刻
      dt(int): 時間

    Returns:
      bool: 貯湯タンク内の水の利用可否 (-)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.calc_isAvailable_w_tank(Theta_wtr, Theta_ex_p6h_Ave, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d)
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_isAvailable_w_tank(Theta_wtr, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d)


def calc_delta_tau_pump_hc_d_t(ls_type, delta_tau_hc_d_t):
    """1時間当たりの集熱時における循環ポンプの稼働時間数 (h/h)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      P_alpha_sp(float): ソーラーシステムの太陽熱集熱部の方位角 (°)
      P_beta_sp(float): ソーラーシステムの太陽熱集熱部の傾斜角 (°)

    Returns:
      ndarray: 1時間当たりの集熱時における循環ポンプの稼働時間数 (h/h)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_delta_tau_pump_hc_d_t()
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_delta_tau_pump_hc_d_t(delta_tau_hc_d_t)


def calc_delta_tau_pump_non_hc_d_t(ls_type, I_s_d_t, delta_tau_hc_d_t):
    """1時間当たりの非集熱時における循環ポンプの稼働時間数 (h/h)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)
      delta_tau_hc_d_t(ndarray): 1時間当たりの集熱時間数(-)

    Returns:
      ndarray: 1時間当たりの非集熱時における循環ポンプの稼働時間数 (h/h)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_delta_tau_pump_non_hc_d_t()
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_delta_tau_pump_non_hc_d_t(I_s_d_t, delta_tau_hc_d_t)


def calc_Epsilon_t_hx_d_t(ls_type, c_p_htm, UA_hx, G_htm_d_t):
    """熱交換器の温度効率(-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      c_p_htm(float): 熱媒の定圧比熱
      UA_hx(float): 熱交換器の伝熱係数 (-)
      G_htm_d_t(ndarray): 1時間当たりの熱媒の循環量

    Returns:
      ndarray: 熱交換器の温度効率 (-)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.calc_Epsilon_t_hx_d_t(c_p_htm, UA_hx, G_htm_d_t)
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_Epsilon_t_hx_d_t(c_p_htm, UA_hx, G_htm_d_t)


def calc_Epsilon_t_stc_d_t(ls_type, A_stcp, b1, c_p_htm, G_htm_d_t):
    """集熱器の温度効率

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      A_stcp(float): 集熱部の有効集熱面積(m2)
      b1(float): 集熱器の集熱効率特性線図一次近似式の傾き（W/(m2・K)）
      c_p_htm(float): 熱媒の定圧比熱
      G_htm_d_t(ndarray): 1時間当たりの熱媒の循環量

    Returns:
      ndarray: 集熱器の温度効率
    
    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.calc_Epsilon_t_stc_d_t(A_stcp, b1, c_p_htm, G_htm_d_t)
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_Epsilon_t_stc_d_t(A_stcp, b1, c_p_htm, G_htm_d_t)


def calc_Epsilon_t_stp_d_t(ls_type, c_p_htm, UA_stp, G_htm_d_t):
    """集熱配管の温度効率 (-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      c_p_htm(float): 熱媒の定圧比熱
      UA_stp(float): 集熱配管の放熱係数
      G_htm_d_t(ndarray): 1時間当たりの熱媒の循環量

    Returns:
      float: 集熱配管の温度効率 (-)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.get_Epsilon_t_stp_d_t()
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_Epsilon_t_stp_d_t(c_p_htm, UA_stp, G_htm_d_t)


def calc_t_hc_start_d(ls_type, I_s_d_t):
    """集熱開始時刻 (-)

    Args:
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (密閉形太陽熱温水器（直圧式）,ソーラーシステム)
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)

    Returns:
      ndarray: 集熱開始時刻 (-)

    """
    if ls_type == '密閉形太陽熱温水器（直圧式）':
        return lss1.calc_t_hc_start_d(I_s_d_t)
    elif ls_type == 'ソーラーシステム':
        return lss2.calc_t_hc_start_d(I_s_d_t)
