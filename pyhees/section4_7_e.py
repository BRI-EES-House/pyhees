# ============================================================================
# 付録 E 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機
#       （給湯熱源：ガス瞬間式、暖房熱源：電気ヒートポンプ・ガス瞬間式併用）
# ============================================================================

import numpy as np
from pyhees.section4_7_common import get_Q_out_H_hs_d_t


# ============================================================================
# E2. エネルギー消費量
# ============================================================================


# ============================================================================
# E.2.1 消費電力量
# ============================================================================


def calc_E_E_hs(Q_dmd_H_hs_d_t, Theta_ex, Theta_RW_hs, h_ex, Theta_SW_d_t, TU_place):
    """ 1時間当たりの熱源機の消費電力量 (1)

    :param Q_dmd_H_hs_d_t: 1時間当たりの熱源機の熱需要 (MJ/h)
    :type Q_dmd_H_hs_d_t: ndarray
    :param Theta_ex: 外気温度
    :type Theta_ex: ndarray float
    :param Theta_RW_hs: 1時間平均の熱源機の戻り温水温度 (℃)
    :type Theta_RW_hs: ndarray
    :param h_ex: 外気相対湿度
    :type h_ex: ndarray
    :param Theta_SW_d_t: 往き温水温度 (℃)
    :type Theta_SW_d_t: ndarray
    :param TU_place: タンクユニットの設置場所
    :type TU_place: str
    :return: 1時間当たりの熱源機の消費電力量
    :rtype: ndarray
    """
    # ---------- タンクユニット周囲の空気温度 ----------

    # 1時間平均のタンクユニットの周囲空気温度 (℃) (23)
    Theta_TU_amb = calc_Theta_TU_amb(Theta_ex, TU_place)

    # ---------- 熱源機の平均暖房出力及び熱源機最大暖房出力 ----------

    # ガスユニットの定格暖房能力 (W)
    q_GU_rtd = get_q_GU_rtd()

    # 1時間当たりの熱源機の最大暖房出力 (MJ/h) (22)
    Q_max_hs = get_Q_max_hs(q_GU_rtd)

    # 1時間当たりの温水暖房用熱源機の暖房出力 (MJ/h)
    Q_out_hs = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_hs)

    # 1時間平均の熱源機の暖房出力 (W) (21)
    q_out_hs = get_q_out_hs(Q_out_hs)

    # ----------- 暖房出力分担率 -----------

    # ヒートポンプ最大運転時のヒートポンプユニット運転時のガスユニットの熱損失 (W) (20)
    q_dash_GU_loss_HPU = calc_q_dash_GU_loss_HPU(Theta_SW_d_t, Theta_TU_amb)

    # ヒートポンプ最大運転時のタンクユニットのタンクの熱損失 (W) (19)
    q_dash_TU_tank_loss = calc_q_dash_TU_tank_loss(Theta_TU_amb)

    # タンクユニットのヒートポンプ配管の熱損失 (W) (18)
    q_dash_TU_pipe_loss = calc_q_dash_TU_pipe_loss(Theta_SW_d_t, Theta_ex)

    # ヒートポンプユニットの最大暖房出力 (W) (17)
    q_HPU_max = calc_q_HPU_max(Theta_ex, Theta_RW_hs)

    # ヒートポンプユニットの暖房出力分担率 (-) (16)
    r_HPU = get_r_HPU(q_HPU_max, q_dash_TU_tank_loss, q_dash_TU_pipe_loss, q_out_hs, q_dash_GU_loss_HPU)

    # ガスユニットの暖房出力分担率 (-) (15)
    r_GU = get_r_GU(r_HPU)

    # ---------- ガスユニットのガス消費量 ----------

    # 1時間平均のガスユニットのガス消費量 (W) (14b)
    q_G_GU = calc_q_G_GU(q_out_hs, Theta_SW_d_t)

    # ---------- ガスユニットの補機の消費電力 ----------

    # 1時間当たりのガスユニットの補機の消費電力 (kWh/h) (13)
    E_E_GU_aux = calc_E_E_GU_aux(q_G_GU, r_HPU, r_GU)

    # ---------- ヒートポンプユニットの暖房出力 ----------

    # 熱源機のヒートポンプユニット分断暖房出力 (MJ/h) (12)
    Q_out_hs_HPU = get_Q_out_hs_HPU(Q_out_hs, r_HPU)

    # ヒートポンプユニット運転時のガスユニットの熱損失 (MJ/h) (11)
    Q_GU_loss_HPU = calc_Q_GU_loss_HPU(Theta_SW_d_t, Theta_TU_amb, r_HPU)

    # 1時間平均のヒートポンプユニットの出湯温度 (℃)
    Theta_HPU_out = get_Theta_HPU_out(r_HPU, Theta_SW_d_t)

    # タンクユニットのタンクの熱損失 (MJ/h) (10)
    Q_TU_tank_loss = calc_Q_TU_tank_loss(Theta_HPU_out, Theta_TU_amb)

    # タンクユニットのヒートポンプ配管の熱損失 (MJ/h) (9)
    Q_TU_pipe_loss = calc_Q_TU_pipe_loss(Theta_SW_d_t, Theta_ex)

    # ヒートポンプユニットの暖房出力 (MJ/h) (8)
    Q_HPU = get_Q_HPU(Q_out_hs_HPU, Q_GU_loss_HPU, Q_TU_tank_loss, Q_TU_pipe_loss)

    # ---------- ヒートポンプユニットの消費電力量 ----------

    # ヒートポンプユニットの平均暖房出力,最小暖房出力 (6)(7)
    q_HPU_ave = get_q_HPU_ave(Q_HPU)
    q_HPU_min = get_q_HPU_min(Theta_ex, Theta_RW_hs, Theta_HPU_out)

    # 1時間平均のヒートポンプユニットの断続運転率 (-) (5)
    r_intmit = get_r_intmit(q_HPU_ave, q_HPU_min)

    # 1時間当たりのヒートポンプユニットの消費電力量 (kWh/h) (4)
    E_E_HPU = calc_E_E_HPU(q_HPU_ave, q_HPU_min, Theta_ex, h_ex, Theta_RW_hs, Theta_HPU_out)

    # ---------- タンクユニットの補機消費電力量 ----------

    # 1時間当たりのタンクユニットの補機の消費電力量 (kWh/h) (3)
    E_E_TU_aux = calc_E_E_TU_aux(r_intmit)

    # ---------- 熱源機の消費電力量 ----------

    # 1時間当たりの熱源機の消費電力量 (kWh/h) (1)
    E_E_hs = E_E_HPU + E_E_GU_aux + E_E_TU_aux
    E_E_hs[Q_out_hs == 0] = 0

    return E_E_hs


# ============================================================================
# E.2.2 ガス消費量
# ============================================================================


def calc_E_G_hs(Theta_ex, Theta_SW_d_t, Theta_RW_hs, TU_place, Q_dmd_H_hs_d_t):
    """ 熱源機のガス消費量 (2)

    :param Theta_ex: 外気温度（℃）
    :type Theta_ex: ndarray
    :param Theta_SW_d_t: 往き温水温度 (℃)
    :type Theta_SW_d_t: ndarray
    :param Theta_RW_hs: 1時間平均の熱源機の戻り温水温度 (℃)
    :type Theta_RW_hs: ndarray
    :param TU_place: タンクユニットの設置場所
    :type TU_place: str
    :param Q_dmd_H_hs_d_t: 1時間当たりの熱源機の熱需要 (MJ/h)
    :type Q_dmd_H_hs_d_t: ndarray
    :return: 熱源機のガス消費量
    :rtype: ndarray
    """
    # タンクユニットの周囲空気温度 (℃) (23)
    Theta_TU_amb = calc_Theta_TU_amb(Theta_ex, TU_place)

    # ガスユニットの定格暖房能力 (W)
    q_GU_rtd = get_q_GU_rtd()

    # 熱源機の最大暖房出力 (22)
    Q_max_hs = get_Q_max_hs(q_GU_rtd)

    # 温水暖房用熱源機の暖房出力
    Q_out_hs = get_Q_out_H_hs_d_t(Q_dmd_H_hs_d_t, Q_max_hs)

    # 熱源機の暖房出力 (21)
    q_out_hs = get_q_out_hs(Q_out_hs)

    # ヒートポンプ最大運転時のヒートポンプユニット運転時のガスユニットの熱損失 (20)
    q_dash_GU_loss_HPU = calc_q_dash_GU_loss_HPU(Theta_SW_d_t, Theta_TU_amb)

    # ヒートポンプ最大運転時のタンクユニットのタンクの熱損失 (19)
    q_dash_TU_tank_loss = calc_q_dash_TU_tank_loss(Theta_TU_amb)

    # タンクユニットのヒートポンプ配管の熱損失 (18)
    q_dash_TU_pipe_loss = calc_q_dash_TU_pipe_loss(Theta_SW_d_t, Theta_ex)

    # ヒートポンプユニットの最大暖房出力 (17)
    q_HPU_max = calc_q_HPU_max(Theta_ex, Theta_RW_hs)

    # ヒートポンプユニットの暖房出力分担率 (16)
    r_HPU = get_r_HPU(q_HPU_max, q_dash_TU_tank_loss, q_dash_TU_pipe_loss, q_out_hs, q_dash_GU_loss_HPU)

    # ガスユニットの暖房出力分担率 (15)
    r_GU = get_r_GU(r_HPU)

    # ガスユニットのガス消費量 (14a)
    E_G_hs = calc_E_G_GU(r_GU, q_out_hs, Theta_SW_d_t)
    E_G_hs[Q_out_hs == 0] = 0

    return E_G_hs


# ============================================================================
# E.2.3 灯油消費量
# ============================================================================


def get_E_K_hs():
    """ 熱源機の灯油消費量

    :return: 熱源機の灯油消費量
    :rtype: ndarray
    """
    return np.zeros(24 * 365)


# ============================================================================
# E.2.4 その他の燃料の一次エネルギー消費量
# ============================================================================


def get_E_M_hs():
    """ 熱源機のその他の燃料の一次エネルギー消費量

    :return: 熱源機のその他の燃料の一次エネルギー消費量
    :rtype: ndarray
    """
    return np.zeros(24 * 365)


# ============================================================================
# E.3 消費電力量及びガス消費量
# ============================================================================


# ============================================================================
# E.3.1 タンクユニットの補機消費電力量
# ============================================================================


def calc_E_E_TU_aux(r_intmit):
    """ 1時間当たりのタンクユニットの補機消費電力量 (3)

    :param r_intmit: 1時間平均のヒートポンプユニットの断続運転率
    :type r_intmit: ndarray
    :return: 1時間当たりのタンクユニットの補機消費電力量 (3)
    :rtype: ndarray
    """
    # 1時間平均のタンクユニットの補機の消費電力 (3b)
    P_TU_aux = f_TU_P_aux(r_intmit)

    # タンクユニットの補機消費電力量 (3a)
    E_E_TU_aux = P_TU_aux * 10 ** (-3)

    return E_E_TU_aux


# ============================================================================
# E.3.2 ヒートポンプユニットの消費電力量
# ============================================================================


def calc_E_E_HPU(q_HPU_ave, q_HPU_min, Theta_ex, h_ex, Theta_RW_hs, Theta_HPU_out):
    """ 1時間当たりのヒートポンプユニットの消費電力量 (4)

    :param q_HPU_ave: 1時間平均のヒートポンプユニットの暖房出力 (W)
    :type q_HPU_ave: ndarray
    :param q_HPU_min: 1時間平均のヒートポンプユニットの最小暖房出力 (W)
    :type q_HPU_min: ndarray
    :param Theta_ex: 1時間平均の外気温度 (℃)
    :type Theta_ex: ndarray
    :param h_ex: 1時間平均の外気相対湿度 (%)
    :type h_ex: ndarray
    :param Theta_RW_hs: 1時間平均の熱源機の戻り温水温度 (℃)
    :type Theta_RW_hs: ndarray
    :param Theta_HPU_out: 1時間平均のヒートポンプユニットの出湯温度 (℃)
    :type Theta_HPU_out: ndarray
    :return: 1時間当たりのヒートポンプユニットの消費電力量 (4)
    :rtype: ndarray
    """
    # E_E_HPU の作業領域を確保
    E_E_HPU = np.zeros(24 * 365)

    # ==== 連続運転の場合 ====
    f_ctn = q_HPU_ave >= q_HPU_min

    # 1時間平均の連続運転時のヒートポンプユニットの消費電力 (W) (4a-2)
    P_HPU_ctn = f_HPU_p(Theta_ex, h_ex, Theta_RW_hs, Theta_HPU_out, q_HPU_ave)

    # 1時間当たりのヒートポンプユニットの消費電力量 (kW) (4a-1)
    E_E_HPU[f_ctn] = P_HPU_ctn[f_ctn] * 10 ** (-3)

    # ==== 断続運転の場合 ====
    f_intmit = q_HPU_ave < q_HPU_min

    # 1時間平均のヒートポンプユニットの断続運転率 (5)
    r_intmit = get_r_intmit(q_HPU_ave, q_HPU_min)

    # 1時間平均のヒートポンプユニットの最小消費電力 (kW) (4b-2)
    P_HPU_min = f_HPU_p(Theta_ex, h_ex, Theta_RW_hs, Theta_HPU_out, q_HPU_min)

    # 1時間当たりのヒートポンプユニットの消費電力量 (kW) (4b-1)
    CD = 0.23
    E_E_HPU[f_intmit] = q_HPU_ave[f_intmit] / (
            q_HPU_min[f_intmit] / P_HPU_min[f_intmit] * (1 - CD * (1 - r_intmit[f_intmit]))) * 10 ** (-3)

    return E_E_HPU


def get_r_intmit(q_HPU_ave, q_HPU_min):
    """ 1時間平均のヒートポンプユニットの断続運転率 (5)

    :param q_HPU_ave: 1時間平均のヒートポンプユニットの平均暖房出力 (W)
    :type q_HPU_ave: ndarray
    :param q_HPU_min: 1時間平均のヒートポンプユニットの最小暖房出力 (W)
    :type q_HPU_min: ndarray
    :return: 1時間平均のヒートポンプユニットの断続運転率 (5)
    :rtype: ndarray
    """
    r_intmit = np.clip(q_HPU_ave / q_HPU_min, None, 1.0)
    return r_intmit


def get_q_HPU_min(Theta_ex, Theta_RW_hs, Theta_HPU_out):
    """ 1時間平均のヒートポンプユニットの最小暖房出力 (6)

    :param Theta_ex:  1時間平均の外気温度 (℃)
    :type Theta_ex: ndarray
    :param Theta_RW_hs: 1時間平均の熱源機の戻り温水温度 (℃)
    :type Theta_RW_hs: ndarray
    :param Theta_HPU_out: 1時間平均のヒートポンプユニットの出湯温度 (℃)
    :type Theta_HPU_out: ndarray
    :return: 1時間平均のヒートポンプユニットの最小暖房出力 (6)
    :rtype: ndarray
    """
    return f_HPU_q_min(Theta_ex, Theta_RW_hs, Theta_HPU_out)


def get_q_HPU_ave(Q_HPU):
    """ 1時間平均のヒートポンプユニットの平均暖房出力 (7)

    :param Q_HPU: 1時間当たりのヒートポンプユニットの暖房出力 (MJ/h)
    :type Q_HPU: ndarray
    :return: 1時間平均のヒートポンプユニットの平均暖房出力 (7)
    :rtype: ndarray
    """
    return Q_HPU * 10 ** 6 / 3600


# ============================================================================
# E.3.3 ヒートポンプユニットの暖房出力
# ============================================================================


def get_Q_HPU(Q_out_hs_HPU, Q_GU_loss_HPU, Q_TU_tank_loss, Q_TU_pipe_loss):
    """ 1時間当たりのヒートポンプユニットの暖房出力 (8)

    :param Q_out_hs_HPU: 1時間当たりの熱源機のヒートポンプユニット分担暖房出力 (MJ/h)
    :type Q_out_hs_HPU: ndarray
    :param Q_GU_loss_HPU: 1時間当たりのヒートポンプユニット運転時のガスユニットの熱損失量 (MJ/h)
    :type Q_GU_loss_HPU: ndarray
    :param Q_TU_tank_loss: 1時間当たりのタンクユニットのタンクの熱損失量 (MJ/h)
    :type Q_TU_tank_loss: ndarray
    :param Q_TU_pipe_loss: 1時間当たりのタンクユニットのヒートポンプ配管の熱損失量 (MJ/h)
    :type Q_TU_pipe_loss: ndarray
    :return: 1時間当たりのヒートポンプユニットの暖房出力
    :rtype: ndarray
    """
    Q_HPU = Q_out_hs_HPU + Q_GU_loss_HPU + Q_TU_tank_loss + Q_TU_pipe_loss
    return Q_HPU


def calc_Q_TU_pipe_loss(Theta_SW_hs, Theta_ex):
    """ 1時間当たりのタンクユニットのヒートポンプ管の熱損失量 (9)

    :param Theta_SW_hs: 1時間平均の熱源機の往き温水温度 (℃)
    :type Theta_SW_hs: ndarray
    :param Theta_ex: 外気温度 (℃)
    :type Theta_ex: ndarray
    :return: 1時間当たりのタンクユニットのヒートポンプ管の熱損失量 (MJ/h)
    :rtype: ndarray
    """
    # タンクユニットのヒートポンプ配管の熱損失 (W) (9b)
    q_TU_pipe_loss = f_TU_q_HPP(Theta_SW_hs, Theta_ex)

    # タンクユニットのヒートポンプ管の熱損失量 (MJ/h) (9a)
    Q_TU_pipe_loss = q_TU_pipe_loss * 3600 * 10 ** (-6)

    return Q_TU_pipe_loss


def calc_Q_TU_tank_loss(Theta_HPU_out, Theta_TU_amb):
    """ 1時間当たりのタンクユニットのタンクの熱損失量 (10)

    :param Theta_HPU_out: 1時間平均のヒートポンプユニットの出湯温度 (℃)
    :type Theta_HPU_out: ndarray
    :param Theta_TU_amb: 1時間平均のタンクユニットの周囲空気温度 (℃)
    :type Theta_TU_amb: ndarray
    :return: 1時間当たりのタンクユニットのタンクの熱損失量 (MJ/h)
    :rtype: ndarray
    """
    # タンクユニットのタンクの熱損失 (W) (10b)
    q_TU_tank_loss = f_TU_q_tank(Theta_HPU_out, Theta_TU_amb)

    # タンクユニットのタンクの熱損失量 (MJ/h) (10a)
    Q_TU_tank_loss = q_TU_tank_loss * 3600 * 10 ** (-6)

    return Q_TU_tank_loss


def get_Theta_HPU_out(r_HPU, Theta_SW_hs):
    """ 1時間平均のヒートポンプユニットの出湯温度

    :param r_HPU: 1時間平均のヒートポンプユニット暖房出力分担率 (-)
    :type r_HPU: ndarray
    :param Theta_SW_hs: 熱源機の往き温水温度 (℃)
    :type Theta_SW_hs: ndarray
    :return: 1時間平均のヒートポンプユニットの出湯温度 (℃)
    :rtype: ndarray
    """
    Theta_HPU_out = np.zeros(24 * 365)
    Theta_HPU_out[r_HPU < 1.0] = 85.0
    Theta_HPU_out[np.logical_and(r_HPU == 1.0, Theta_SW_hs == 40.0)] = 65.0
    Theta_HPU_out[np.logical_and(r_HPU == 1.0, Theta_SW_hs == 60.0)] = 85.0
    return Theta_HPU_out


def calc_Q_GU_loss_HPU(Theta_SW_hs, Theta_TU_amb, r_HPU):
    """ 1時間当たりのヒートポンプユニット運転時のガスユニットの熱損失量 (11)

    :param Theta_SW_hs: 温水暖房用熱源機の往き温水温度
    :type Theta_SW_hs: ndarray
    :param Theta_TU_amb: 1時間平均のタンクユニットの周囲空気温度 (℃)
    :type Theta_TU_amb: ndarray
    :param r_HPU: 1時間平均のヒートポンプユニット暖房出力分担率 (-)
    :type r_HPU: ndarray
    :return: 1時間当たりのヒートポンプユニット運転時のガスユニットの熱損失量 (MJ/h)
    :rtype: ndarray
    """
    # ヒートポンプユニット運転時のガスユニットの熱損失 (W) (11b)
    q_GU_loss_HPU = f_GU_q_lossHP(Theta_SW_hs, Theta_TU_amb)

    # ヒートポンプユニット運転時のガスユニットの熱損失量 (MJ/h) (11a)
    Q_GU_loss_HPU = q_GU_loss_HPU * r_HPU * 3600 * 10 ** (-6)

    return Q_GU_loss_HPU


def get_Q_out_hs_HPU(Q_out_hs, r_HPU):
    """ 1時間当たりの熱源機のヒートポンプユニット分断暖房出力 (12)

    :param Q_out_hs: 1時間平均の熱源機の暖房出力 (MJ/h)
    :type Q_out_hs: ndarray
    :param r_HPU: 1時間平均のヒートポンプユニット暖房出力分担率 (-)
    :type r_HPU: ndarray
    :return: 1時間当たりの熱源機のヒートポンプユニット分断暖房出力 (MJ/h)
    :rtype: ndarray
    """
    return Q_out_hs * r_HPU


# ============================================================================
# E.3.4 ガスユニットの補機の消費電力
# ============================================================================


def calc_E_E_GU_aux(q_G_GU, r_HPU, r_GU):
    """ 1時間当たりのガスユニットの補機の消費電力 (13)

    :param q_G_GU: ガスユニットのガス消費量 (W)
    :type q_G_GU: ndarray
    :param r_HPU: 1時間平均のヒートポンプユニット暖房出力分担率 (-)
    :type r_HPU: ndarray
    :param r_GU: 1時間平均のガスユニットの暖房出力分担率 (-)
    :type r_GU: ndarray
    :return: 1時間当たりのガスユニットの補機の消費電力
    :rtype: ndarray
    """
    # 1時間平均のガス非燃焼時のガスユニットの補機の消費電力 (W) (13c)
    P_GU_aux_OFF = f_GU_P_aux(0.0)

    # 1時間平均のガス燃焼時のガスユニットの補機の消費電力 (W) (13b)
    P_GU_aux_ON = f_GU_P_aux(q_G_GU)

    # 1時間当たりのガスユニットの補機の消費電力 (13a)
    E_E_GU_aux = (P_GU_aux_ON * r_GU + P_GU_aux_OFF * r_HPU) * 10 ** (-3)

    return E_E_GU_aux


# ============================================================================
# E.3.5 ガスユニットのガス消費量
# ============================================================================


def calc_E_G_GU(r_GU, q_out_hs, Theta_SW_hs):
    """ 1時間平均のガスユニットのガス消費量 (MJ/h) (14a)

    :param r_GU: 1時間平均のガスユニットの暖房出力分担率 (-)
    :type r_GU: ndarray
    :param q_out_hs: 1時間平均の熱源機の暖房出力 (W)
    :type q_out_hs: ndarray
    :param Theta_SW_hs: 温水暖房用熱源機の往き温水温度
    :type Theta_SW_hs: ndarray
    :return: 1時間平均のガスユニットのガス消費量 (MJ/h)
    :rtype: ndarray
    """
    # 1時間平均のガスユニットのガス消費量 (14b)
    q_G_GU = calc_q_G_GU(q_out_hs, Theta_SW_hs)

    # ガスユニットのガス消費量 (14a)
    E_G_GU = q_G_GU * r_GU * 3600 * 10 ** (-6)

    return E_G_GU


def calc_q_G_GU(q_out_hs, Theta_SW_hs):
    """ 1時間平均のガスユニットのガス消費量 (W) (14b)

    :param q_out_hs: 1時間平均の熱源機の暖房出力 (W)
    :type q_out_hs: ndarray
    :param Theta_SW_hs: 温水暖房用熱源機の往き温水温度
    :type Theta_SW_hs: ndarray
    :return: 1時間平均のガスユニットのガス消費量 (W)
    :rtype: ndarray
    """
    # ガスユニットの定格暖房効率
    e_GU_rtd = get_e_GU_rtd()

    # ガスユニットの定格暖房能力
    q_GU_rtd = get_q_GU_rtd()

    # ガスユニットの暖房能力
    q_GU = get_q_GU(q_out_hs, q_GU_rtd)

    return f_GU_G(q_GU, e_GU_rtd, q_GU_rtd, Theta_SW_hs)


def get_q_GU(q_out_hs, q_GU_rtd):
    """ ガスユニットの暖房能力 (14c)

    :param q_out_hs: 1時間平均の熱源機の暖房出力 (W)
    :type q_out_hs: ndarray
    :param q_GU_rtd: ガスユニットの定格暖房能力 (W)
    :type q_GU_rtd: float
    :return: ガスユニットの暖房能力 (14c)
    :rtype: ndarray
    """
    return np.clip(q_out_hs, None, q_GU_rtd)


def get_e_GU_rtd():
    """ ガスユニットの定格暖房効率 (-)

    :return: ガスユニットの定格暖房効率
    :rtype: float
    """
    return 0.87


def get_q_GU_rtd():
    """ ガスユニットの定格暖房能力 (W)

    :return: ガスユニットの定格暖房能力 (W)
    :rtype: float
    """
    return 14000


# ============================================================================
# E.3.6 暖房出力分担率
# ============================================================================


def get_r_GU(r_HPU):
    """ 1時間平均のガスユニットの暖房出力分担率 (15)

    :param r_HPU: 1時間平均のヒートポンプユニット暖房出力分担率 (-)
    :type r_HPU: ndarray
    :return: 1時間平均のガスユニットの暖房出力分担率
    :rtype: ndarray
    """
    return 1 - r_HPU


def get_r_HPU(q_HPU_max, q_dash_TU_tank_loss, q_dash_TU_pipe_loss, q_out_hs, q_dash_GU_loss_HPU):
    """ 1時間平均のヒートポンプユニットの暖房出力分担率 (16)

    :param q_HPU_max: 1時間平均のヒートポンプユニットの最大暖房出力 (W)
    :type q_HPU_max: ndarray
    :param q_dash_TU_tank_loss: 1時間平均のヒートポンプユニット最大運転時のタンクユニットのタンクの熱損失 (W)
    :type q_dash_TU_tank_loss: ndarray
    :param q_dash_TU_pipe_loss: 1時間平均のヒートポンプユニット最大運転時のタンクユニットのヒートポンプ配置の熱損失 (W)
    :type q_dash_TU_pipe_loss: ndarray
    :param q_out_hs: 1時間平均の熱源機の暖房出力 (W)
    :type q_out_hs: ndarray
    :param q_dash_GU_loss_HPU: 1時間平均のヒートポンプユニット最大運転時のヒートポンプユニット運転時のガスユニットの熱損失 (W)
    :type q_dash_GU_loss_HPU: ndarray
    :return: 1時間平均のヒートポンプユニットの暖房出力分担率 (16)
    :rtype: ndarray
    """
    r_HPU = np.zeros(24*365)
    f = (q_out_hs + q_dash_GU_loss_HPU > 0)
    r_HPU[f] = (q_HPU_max[f] - q_dash_TU_tank_loss[f] - q_dash_TU_pipe_loss[f]) / (q_out_hs[f] + q_dash_GU_loss_HPU[f])
    return np.clip(r_HPU, 0, 1)


def calc_q_HPU_max(Theta_ex, Theta_RW_hs):
    """ 1時間平均のヒートポンプユニットの最大暖房出力 (17)

    :param Theta_ex: 1時間平均の外気温度 (℃)
    :type Theta_ex: ndarray
    :param Theta_RW_hs: 1時間平均の熱源機の戻り温水温度 (℃)
    :type Theta_RW_hs: ndarray
    :return: ヒートポンプユニットの最大暖房出力 (W)
    :rtype: ndarray
    """
    # 1時間平均のヒートポンプ大運転時のヒートポンプユニットの出湯温度
    Theta_dash_HPU_out = get_Theta_dash_HPU_out()

    # ヒートポンプユニットの最大暖房出力を求める関数 (26)
    q_HPU_max = f_HPU_q_max(Theta_ex, Theta_RW_hs, Theta_dash_HPU_out)

    return q_HPU_max


def calc_q_dash_TU_pipe_loss(Theta_SW_hs, Theta_ex):
    """ 1時間平均のヒートポンプ最大運転時のタンクユニットのヒートポンプ配管の熱損失 (18)

    :param Theta_SW_hs: 温水暖房用熱源機の往き温水温度
    :type Theta_SW_hs: ndarray
    :param Theta_ex: 外気温度
    :type Theta_ex: ndarray
    :return: 1時間平均のヒートポンプ最大運転時のタンクユニットのヒートポンプ配管の熱損失
    :rtype: ndarray
    """
    # タンクユニットのヒートポンプ配管の熱損失を求める関数 (28)
    q_dash_TU_pipe_loss = f_TU_q_HPP(Theta_SW_hs, Theta_ex)

    return q_dash_TU_pipe_loss


def calc_q_dash_TU_tank_loss(Theta_TU_amb):
    """ ヒートポンプ最大運転時のタンクユニットのタンクの熱損失 (19)

    :param Theta_TU_amb: 1時間平均のタンクユニットの周囲空気温度 (℃)
    :type Theta_TU_amb: ndarray
    :return: ヒートポンプ最大運転時のタンクユニットのタンクの熱損失 (19)
    :rtype: ndarray
    """
    # 1時間平均のヒートポンプ最大運転時のヒートポンプユニットの出湯温度
    Theta_dash_HPU_out = get_Theta_dash_HPU_out()

    # タンクユニットのタンクの熱損失を求める関数 (29)
    q_dash_TU_tank_loss = f_TU_q_tank(Theta_dash_HPU_out, Theta_TU_amb)

    return q_dash_TU_tank_loss


def calc_q_dash_GU_loss_HPU(Theta_SW_hs, Theta_TU_amb):
    """ ヒートポンプ最大運転時のヒートポンプユニット運転時のガスユニットの熱損失 (20)

    :param Theta_SW_hs: 1時間平均の熱源機の往き温水温度 (℃)
    :type Theta_SW_hs: ndarray
    :param Theta_TU_amb: 1時間平均のタンクユニットの周囲空気温度 (℃)
    :type Theta_TU_amb: ndarray
    :return: ヒートポンプ最大運転時のヒートポンプユニット運転時のガスユニットの熱損失
    :rtype: ndarray
    """
    # ヒートポンプユニット運転時のガスユニットの熱損失を求める関数 (32)
    q_dash_GU_loss_HPU = f_GU_q_lossHP(Theta_SW_hs, Theta_TU_amb)

    return q_dash_GU_loss_HPU


def get_Theta_dash_HPU_out():
    """ 1時間平均のヒートポンプ最大運転時のヒートポンプユニットの出湯温度 (℃)

    :return: 1時間平均のヒートポンプ最大運転時のヒートポンプユニットの出湯温度 (℃)
    :rtype: float
    """
    return 85.0


# ============================================================================
# E.3.7 熱源機の平均暖房出力及び熱源機最大暖房出力
# ============================================================================


def get_q_out_hs(Q_out_hs):
    """ 1時間平均の熱源機の暖房出力 (21)

    :param Q_out_hs: 1時間当たりの熱源機の暖房出力 (MJ/h)
    :type Q_out_hs: ndarray
    :return: 1時間平均の熱源機の暖房出力 (W)
    :rtype: ndarray
    """
    return Q_out_hs * 10 ** 6 / 3600


def get_Q_max_hs(q_GU_rtd):
    """ 1時間当たりの熱源機の最大暖房出力 (22)

    :param q_GU_rtd: ガスユニットの定格暖房能力 (W)
    :type q_GU_rtd: float
    :return: 1時間当たりの熱源機の最大暖房出力 (MJ/h)
    :rtype: float
    """
    Q_max_hs = q_GU_rtd * 3600 * 10 ** (-6)
    return Q_max_hs


# ============================================================================
# E.3.8 タンクユニット周囲の空気温度
# ============================================================================


def calc_Theta_TU_amb(Theta_ex, TU_place):
    """ 1時間平均のタンクユニットの周囲空気温度 (23)

    :param Theta_ex: 1時間平均の外気温度 (℃)
    :type Theta_ex: ndarray
    :param TU_place: タンクユニットの設置場所
    :type TU_place: str
    :return: 1時間平均のタンクユニットの周囲空気温度 (℃)
    :rtype: float
    """
    if TU_place == '屋内':
        # 1時間平均の室内温度
        Theta_in = get_Theta_in()
        return 0.25 * Theta_ex + 0.75 * Theta_in  # (23a)
    elif TU_place == '屋外':
        return Theta_ex  # (23b)
    else:
        raise ValueError(TU_place)


def get_Theta_in():
    """ 暖房時運転における1時間平均の室内温度 (℃)

    :return: 暖房時運転における1時間平均の室内温度 (℃)
    :rtype: float
    """
    return 20.0


# ============================================================================
# E.4 評価関数
# ============================================================================


# ============================================================================
# E.4.1 ヒートポンプユニット
# ============================================================================


def f_HPU_p(Theta_ex, h_ex, Theta_RW_hs, Theta_HP_out, q_HPU_out):
    """ ヒートポンプユニットの消費電力を求める関数 (24)

    :param Theta_ex: 外気温度
    :type Theta_ex: ndarray
    :param h_ex: 外気相対湿度
    :type h_ex: ndarray
    :param Theta_RW_hs: 1時間平均の熱源機の戻り温水温度 (℃)
    :type Theta_RW_hs: ndarray
    :param Theta_HP_out: ヒートポンプユニットの出湯温度 (℃)
    :type Theta_HP_out: ndarray
    :param q_HPU_out: ヒートポンプユニットの平均暖房出力 (W)
    :type q_HPU_out: ndarray
    :return: ヒートポンプユニットの消費電力を求める関数 (24)
    :rtype: ndarray
    """
    P = 0.42108 * q_HPU_out * 10 ** (-3) \
        - 0.03889 * Theta_ex \
        - 0.00762 * h_ex \
        + 0.03313 * Theta_RW_hs \
        + 0.00449 * Theta_HP_out \
        - 0.82066
    return (0.1869 * P ** 2 + 0.2963 * P + 0.565) * 10 ** 3


def f_HPU_q_min(Theta_ex, Theta_RW_hs, Theta_HPU_out):
    """ ヒートポンプユニットの最小暖房出力を求める関数 (25)

    :param Theta_ex: 外気温度
    :type Theta_ex: ndarray
    :param Theta_RW_hs: 1時間平均の熱源機の戻り温水温度 (℃)
    :type Theta_RW_hs: ndarray
    :param Theta_HPU_out: 1時間平均のヒートポンプユニットの出湯温度 (℃)
    :type Theta_HPU_out: ndarray
    :return: ヒートポンプユニットの最小暖房出力を求める関数 (25)
    :rtype: ndarray
    """
    return 6.08 * Theta_ex - 46.56 * Theta_RW_hs + 0.04 * Theta_HPU_out + 4739.62


def f_HPU_q_max(Theta_ex, Theta_RW_hs, Theta_HPU_out):
    """ ヒートポンプユニットの最大暖房出力を求める関数 (26)

    :param Theta_ex: 外気温度
    :type Theta_ex: ndarray
    :param Theta_RW_hs: 1時間平均の熱源機の戻り温水温度 (℃)
    :type Theta_RW_hs: ndarray
    :param Theta_HPU_out: 1時間平均のヒートポンプユニットの出湯温度 (℃)
    :type Theta_HPU_out: ndarray
    :return: ヒートポンプユニットの最大暖房出力を求める関数 (26)
    :rtype: ndarray
    """
    return 1.36 * Theta_ex - 89.85 * Theta_RW_hs + 46.5 * Theta_HPU_out + 5627.07


# ============================================================================
# E.4.2 タンクユニット
# ============================================================================


def f_TU_P_aux(r_intmit):
    """ タンクユニットの補機の消費電力を求める関数 (27)

    :param r_intmit: 1時間平均のヒートポンプユニットの断続運転率
    :type r_intmit: ndarray
    :return: タンクユニットの補機の消費電力 (W)
    :rtype: ndarray
    """
    return 5 + 10 * r_intmit


def f_TU_q_HPP(Theta_SW_hs, Theta_ex):
    """ タンクユニットのヒートポンプ配管の熱損失を求める関数 (28)

    :param Theta_SW_hs: 熱源機の往き温水温度 (℃)
    :type Theta_SW_hs: ndarray
    :param Theta_ex: 外気温度 (℃)
    :type Theta_ex: ndarray
    :return: タンクユニットのヒートポンプ配管の熱損失 (W)
    :rtype: ndarray
    """
    return 2.8 * (Theta_SW_hs - Theta_ex)


def f_TU_q_tank(Theta_HP_out, Theta_TU_amb):
    """ タンクユニットのタンクの熱損失を求める関数 (29)

    :param Theta_HP_out: ヒートポンプユニットの出湯温度 (℃)
    :type Theta_HP_out: float
    :param Theta_TU_amb: タンクユニットの周囲空気温度 (℃)
    :type Theta_TU_amb: ndarray
    :return: タンクユニットのタンクの熱損失 (W)
    :rtype: ndarray
    """
    return np.clip(1.6 * (Theta_HP_out - Theta_TU_amb) - 72.1, 0, None)


# ============================================================================
# E.4.3 ガスユニット
# ============================================================================


def f_GU_G(q_GU, e_GU_rtd, q_GU_rtd, Theta_SW_hs):
    """ ガスユニットのガス消費量を求める関数 (30,31)

    :param q_GU: ガスユニットの暖房出力 (W)
    :type q_GU: ndarray
    :param e_GU_rtd: ガスユニットの定格暖房能力 (W)
    :type e_GU_rtd: float
    :param q_GU_rtd: ガスユニットの定格暖房能力 (W)
    :type q_GU_rtd: float
    :param Theta_SW_hs: 熱源機の往き温水温度 (℃)
    :type Theta_SW_hs: ndarray
    :return: ガスユニットのガス消費量を求める関数 (30,31)
    :rtype: ndarray
    """
    # f_ex, q_body の作業領域確保
    f_ex = np.zeros(24 * 365)
    q_body = np.zeros(24 * 365)

    # Theta_SW_hs == 40 の場合
    f1 = Theta_SW_hs == 40
    f_ex[f1] = get_table_e_3()[0][0]
    q_body[f1] = get_table_e_3()[1][0]

    # Theta_SW_hs == 60 の場合
    f2 = Theta_SW_hs == 60
    f_ex[f2] = get_table_e_3()[0][1]
    q_body[f2] = get_table_e_3()[1][1]

    e_ex = e_GU_rtd * f_ex * (q_GU_rtd + q_body) / q_GU_rtd

    return (q_GU + q_body) / e_ex


def get_table_e_3():
    """ 表E.3 ガスユニットの定格暖房効率を補正する係数及びガスユニットの筐体放熱損失

    :return: 表E.3 ガスユニットの定格暖房効率を補正する係数及びガスユニットの筐体放熱損失
    :rtype: list
    """
    table_e_3 = [
        (1.064, 1.038),
        (123.74, 225.26)
    ]
    return table_e_3


def f_GU_q_lossHP(Theta_SW_hs, Theta_TU_amb):
    """ ヒートポンプユニット運転時のガスユニットの熱損失を求める関数 (32)

    :param Theta_SW_hs: 温水暖房用熱源機の往き温水温度
    :type Theta_SW_hs: ndarray
    :param Theta_TU_amb: 1時間平均のタンクユニットの周囲空気温度 (℃)
    :type Theta_TU_amb: ndarray
    :return: ヒートポンプユニット運転時のガスユニットの熱損失を求める関数
    :rtype: ndarray
    """
    return np.clip(5 * (Theta_SW_hs - Theta_TU_amb) - 100, 0, None)


def f_GU_P_aux(q_G_GU):
    """ ガスユニットの補機の消費電力を求める関数 (33)

    :param q_G_GU: ガスユニットのガス消費量 (W)
    :type q_G_GU: ndarray
    :return: ガスユニットの補機の消費電力 (W)
    :rtype: ndarray
    """
    return 73 + 0.003 * q_G_GU
