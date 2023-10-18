# ============================================================================
# 付録R 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機
# （給湯熱源：ガス瞬間式、暖房熱源：電気ヒートポンプ・ガス瞬間式併用、タンクユニット：なし）
# ============================================================================


import numpy as np


import pyhees.section4_7_h as appendix_H
from pyhees.section4_7_common import get_Q_out_H_hs_d_t


# ============================================================================
# R2. エネルギー消費量
# ============================================================================


# ============================================================================
# R.2.1 消費電力量
# ============================================================================


def calc_E_E_hs(Q_dmd_H_hs, Theta_SW_hs, Theta_ex, h_ex, region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh):
    """1時間当たりの温水暖房用熱源機の消費電力量 (1)

    Args:
      Q_dmd_H_hs(ndarray): 1時間当たりの温水暖房用熱源機の温水熱需要 (MJ/h)
      Theta_SW_hs(ndarray): 1時間平均の温水暖房用熱源機の往き温水温度 (℃)
      Theta_ex(ndarray): 1時間平均の外気温度 (℃)
      h_ex(ndarray): 1時間平均の外気相対湿度 (%)
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      has_MR_hwh(bool): 温水暖房の放熱器を主たる居室に設置する場合はTrue
      has_OR_hwh(bool): 温水暖房の放熱器をその他の居室に設置する場合はTrue

    Returns:
      ndarray: 1時間当たりの温水暖房用熱源機の消費電力量 (kWh/h)

    """
    # ---------- 温水暖房用熱源機の暖房出力 ----------

    # ガスユニットの定格暖房能力
    q_GU_rtd = get_q_GU_rtd()

    # 1時間当たりの温水暖房用熱源機の最大暖房出力 (18)
    Q_max_H_hs = get_Q_max_H_hs(q_GU_rtd)

    # 1時間当たりの温水暖房用熱源機の暖房出力
    Q_out_hs = get_Q_out_H_hs_d_t(Q_dmd_H_hs, Q_max_H_hs)

    # ---------- ヒートポンプユニットの消費電力量 ----------

    # ヒートポンプユニットの定格能力 (7)
    q_HPU_rtd = get_q_HPU_rtd(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

    # 1時間当たりのヒートポンプユニット最大暖房出力 (9)
    Q_max_H_HPU = get_Q_max_H_HPU(q_HPU_rtd, Theta_SW_hs, Theta_ex, h_ex)

    # 1時間平均の温水暖房用熱源機の暖房出力 (17)
    q_out_hs = get_q_out_hs(Q_out_hs)

    # 1時間平均のヒートポンプユニットの最大暖房出力 (16)
    q_HPU_max = get_q_HPU_max(Q_max_H_HPU)

    # 1時間平均ののヒートポンプユニットの暖房出力分担率 (15)
    r_HPU = get_r_HPU(q_HPU_max, q_out_hs)

    # 1時間当たりの温水暖房用熱源機のヒートポンプユニット分担暖房出力 (11)
    Q_out_hs_HPU = get_Q_out_hs_HPU(Q_dmd_H_hs, Q_max_H_HPU, r_HPU)

    # 1時間当たりのヒートポンプユニットの暖房出力 (10)
    Q_HPU = get_Q_HPU(Q_out_hs_HPU)

    # 1時間平均のヒートポンプユニットの効率比 (8)
    er_HPU = get_er_HPU(Q_HPU, Q_max_H_HPU, Theta_SW_hs, Theta_ex)

    # ヒートポンプユニットの定格消費電力 (6)
    P_HPU_rtd = get_P_HPU_rtd(q_HPU_rtd)

    # ヒートポンプユニットの最大消費電力 (5)
    P_HPU_max = get_P_HPU_max(P_HPU_rtd)

    # 1時間平均のヒートポンプユニットの効率 (4)
    e_HPU = get_e_HPU(er_HPU, P_HPU_max, Q_max_H_HPU)

    # 1時間当たりのヒートポンプユニットの消費電力量 (3)
    E_E_HPU = get_E_E_HPU(e_HPU, Q_HPU)

    # ---------- ガスユニットの補機の消費電力量 ----------

    # 1時間平均のガスユニットの暖房出力分担率 (14)
    r_GU = get_r_GU(r_HPU)

    # ガスユニットの定格暖房効率
    e_GU_rtd = get_e_GU_rtd()

    # 1時間平均のガスユニットの暖房出力 (13c)
    q_GU = get_q_GU(q_out_hs, q_GU_rtd)

    # 1時間平均のガスユニットのガス消費量 (13b)
    q_G_GU = get_q_G_GU(q_GU, e_GU_rtd, q_GU_rtd, Theta_SW_hs)

    # 1時間当たりのガスユニットの補機の消費電力量 (12)
    E_E_GU_aux = calc_E_E_GU_aux(q_G_GU, r_GU)

    # 1時間当たりの温水暖房用熱源機の消費電力量 (1)
    E_E_hs = get_E_E_hs(E_E_HPU, E_E_GU_aux, Q_out_hs)

    return E_E_hs


def get_E_E_hs(E_E_HPU, E_E_GU_aux, Q_out_hs):
    """1時間当たりの温水暖房用熱源機の消費電力量 (1)

    Args:
      E_E_HPU(ndarray): 1時間当たりのヒートポンプユニットの消費電力量 (kWh/h)
      E_E_GU_aux(ndarray): 1時間当たりのガスユニットの補機の消費電力量 (kWh/h)
      Q_out_hs(ndarray): 1時間当たりの温水暖房用熱源機の暖房出力

    Returns:
      ndarray: 1時間当たりの温水暖房用熱源機の消費電力量 (kWh/h)
    """
    E_E_hs = E_E_HPU + E_E_GU_aux

    f = Q_out_hs == 0.0
    E_E_hs[f] = 0.0

    return E_E_hs


# ============================================================================
# R.2.2 ガス消費量
# ============================================================================


def calc_E_G_hs(Q_dmd_H_hs, Theta_SW_hs, Theta_ex, h_ex, region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh):
    """1時間当たりの温水暖房用熱源機のガス消費量 (2)

    Args:
      Q_dmd_H_hs(ndarray): 1時間当たりの温水暖房用熱源機の温水熱需要 (MJ/h)
      Theta_SW_hs(ndarray): 1時間平均の温水暖房用熱源機の往き温水温度 (℃)
      Theta_ex(ndarray): 1時間平均の外気温度 (℃)
      h_ex(ndarray): 1時間平均の外気相対湿度 (%)
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      has_MR_hwh(bool): 温水暖房の放熱器を主たる居室に設置する場合はTrue
      has_OR_hwh(bool): 温水暖房の放熱器をその他の居室に設置する場合はTrue

    Returns:
      ndarray: 1時間当たりの温水暖房用熱源機のガス消費量 (MJ/h)

    """
    # ---------- 温水暖房用熱源機の暖房出力 ----------

    # ガスユニットの定格暖房能力
    q_GU_rtd = get_q_GU_rtd()

    # 1時間当たりの温水暖房用熱源機の最大暖房出力 (18)
    Q_max_H_hs = get_Q_max_H_hs(q_GU_rtd)

    # 1時間当たりの温水暖房用熱源機の暖房出力
    Q_out_hs = get_Q_out_H_hs_d_t(Q_dmd_H_hs, Q_max_H_hs)

    # ---------- ガスユニットのガス消費量 ----------

    # ヒートポンプユニットの定格能力 (7)
    q_HPU_rtd = get_q_HPU_rtd(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

    # 1時間当たりのヒートポンプユニット最大暖房出力 (9)
    Q_max_H_HPU = get_Q_max_H_HPU(q_HPU_rtd, Theta_SW_hs, Theta_ex, h_ex)

    # 1時間平均の温水暖房用熱源機の暖房出力 (17)
    q_out_hs = get_q_out_hs(Q_out_hs)

    # 1時間平均のヒートポンプユニットの最大暖房出力 (16)
    q_HPU_max = get_q_HPU_max(Q_max_H_HPU)

    # 1時間平均ののヒートポンプユニットの暖房出力分担率 (15)
    r_HPU = get_r_HPU(q_HPU_max, q_out_hs)

    # 1時間平均のガスユニットの暖房出力分担率 (14)
    r_GU = get_r_GU(r_HPU)

    # ガスユニットの定格暖房効率
    e_GU_rtd = get_e_GU_rtd()

    # 1時間当たりのガスユニットのガス消費量 (13)
    E_G_GU = calc_E_G_GU(e_GU_rtd, q_GU_rtd, q_out_hs, r_GU, Theta_SW_hs)

    # 1時間当たりの温水暖房用熱源機のガス消費量 (2)
    E_G_hs = get_E_G_hs(E_G_GU, Q_out_hs)

    return E_G_hs


def get_E_G_hs(E_G_GU, Q_out_hs):
    """1時間当たりの温水暖房用熱源機のガス消費量 (2)

    Args:
      E_G_GU(ndarray): 1時間当たりのガスユニットのガス消費量 (MJ/h)
      Q_out_hs(ndarray): 1時間当たりの温水暖房用熱源機の暖房出力

    Returns:
      ndarray: 1時間当たりの温水暖房用熱源機の消費電力量 (MJ/h)
    """
    E_G_hs = E_G_GU

    f = Q_out_hs == 0.0
    E_G_hs[f] = 0.0

    return E_G_hs


# ============================================================================
# R.2.3 灯油消費量
# ============================================================================


def get_E_K_hs():
    """1時間当たりの温水暖房用熱源機の灯油消費量

    Args:

    Returns:
      ndarray: 1時間当たりの温水暖房用熱源機の灯油消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# R.2.4 その他の燃料の一次エネルギー消費量
# ============================================================================


def get_E_M_hs():
    """1時間当たりの温水暖房用熱源機のその他の燃料の一次エネルギー消費量

    Args:

    Returns:
      ndarray: 1時間当たりの温水暖房用熱源機のその他の燃料の一次エネルギー消費量

    """
    return np.zeros(24 * 365)


# ============================================================================
# R3. 消費電力量及びガス消費量
# ============================================================================


# ============================================================================
# R.3.1 ヒートポンプユニットの消費電力量
# ============================================================================


def get_E_E_HPU(e_HPU, Q_HPU):
    """1時間当たりのヒートポンプユニットの消費電力量 (3)

    Args:
      e_HPU(ndarray): 1時間平均のヒートポンプユニットの効率 (-)
      Q_HPU(ndarray): 1時間あたりのヒートポンプユニットの暖房出力 (MJ/h)

    Returns:
      ndarray: 1時間当たりのヒートポンプユニットの消費電力量 (kWh/h)

    """
    E_E_HPU = Q_HPU / e_HPU * 10**3 / 3600

    return E_E_HPU


def get_e_HPU(er_HPU, P_HPU_max, Q_max_H_HPU):
    """1時間平均のヒートポンプユニットの効率 (4)

    Args:
      er_HPU(ndarray): 1時間平均のヒートポンプユニットの効率比 (-)
      P_HPU_max(float): ヒートポンプユニットの最大消費電力 (W)
      Q_max_H_HPU(ndarray): 1時間当たりのヒートポンプユニットの最大暖房出力 (MJ/h)

    Returns:
      ndarray: 1時間平均のヒートポンプユニットの効率 (-)

    """
    e_HPU = (Q_max_H_HPU * 10**6 / 3600) / P_HPU_max * er_HPU

    return e_HPU


def get_P_HPU_max(P_HPU_rtd):
    """ヒートポンプユニットの最大消費電力 (5)

    Args:
      P_HPU_rtd(float): ヒートポンプユニットの定格消費電力 (W)

    Returns:
      float: ヒートポンプユニットの最大消費電力 (W)

    """
    P_HPU_max = P_HPU_rtd / 0.6

    return P_HPU_max


def get_P_HPU_rtd(q_HPU_rtd):
    """ヒートポンプユニットの定格消費電力 (6)

    Args:
      q_HPU_rtd(float): ヒートポンプユニットの定格定格能力 (W)

    Returns:
      float: ヒートポンプユニットの定格消費電力 (W)

    """
    # ヒートポンプユニットの定格効率 (-)
    e_HPU_rtd = get_e_HPU_rtd()

    P_HPU_rtd = q_HPU_rtd / e_HPU_rtd

    return P_HPU_rtd


def get_e_HPU_rtd():
    """ヒートポンプユニットの定格効率

    Args:

    Returns:
      float: ヒートポンプユニットの定格効率 (-)

    """
    return 4.05


def get_q_HPU_rtd(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh):
    """ヒートポンプユニットの定格能力 (7)

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      has_MR_hwh(bool): 温水暖房の放熱器を主たる居室に設置する場合はTrue
      has_OR_hwh(bool): 温水暖房の放熱器をその他の居室に設置する場合はTrue

    Returns:
      float: ヒートポンプユニットの定格能力

    """
    # ヒートポンプユニットの最大能力 (W) (付録H)
    q_HPU_max = appendix_H.calc_q_max_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

    q_HPU_rtd = q_HPU_max * 0.8

    return q_HPU_rtd


def get_er_HPU(Q_HPU, Q_max_H_HPU, Theta_SW_hs, Theta_ex):
    """1時間平均のヒートポンプユニットの効率比 (8)

    Args:
      Q_HPU(ndarray): 1時間当たりのヒートポンプユニットの暖房出力 (MJ/h)
      Q_max_H_HPU(ndarray): 1時間当たりのヒートポンプユニットの最大暖房出力 (MJ/h)
      Theta_SW_hs(ndarray): 1時間平均の温水暖房用熱源機の往き温水温度 (℃)
      Theta_ex(ndarray): 1時間平均の外気温度 (℃)

    Returns:
      float: 1時間平均のヒートポンプユニットの効率比 (-)

    """
    er_HPU = (1.120656 - 0.03703 * (Theta_SW_hs - Theta_ex)) * (1.0 - Q_HPU / Q_max_H_HPU) ** 2 \
           + (-0.36786 + 0.012152 * (Theta_SW_hs - Theta_ex)) * (1.0 - Q_HPU / Q_max_H_HPU) \
           + 1.0

    return er_HPU


def get_Q_max_H_HPU(q_HPU_rtd, Theta_SW_hs, Theta_ex, h_ex):
    """1時間当たりのヒートポンプユニットの最大暖房出力 (9)

    Args:
      q_HPU_rtd(float): ヒートポンプユニットの定格能力 (W)
      Theta_SW_hs(ndarray): 1時間平均の温水暖房用熱源機の往き温水温度 (℃)
      Theta_ex(ndarray): 1時間平均の外気温度 (℃)
      h_ex(ndarray): 1時間平均の外気相対湿度 (%)

    Returns:
      ndarray: 1時間当たりのヒートポンプユニットの最大暖房出力 (MJ/j)

    """
    # 1時間あたりのデフロスト補正係数
    C_def = get_C_def(Theta_ex, h_ex)

    Q_max_H_HPU = (11.62 + 0.2781 * Theta_ex - 0.00113 * Theta_ex ** 2 \
                - 0.1271 * Theta_SW_hs - 0.00363 * Theta_ex * Theta_SW_hs) * (q_HPU_rtd / 6.0) * (C_def / 0.85) * 3600 * 10 ** (-6)

    return Q_max_H_HPU


def get_C_def(Theta_ex, h_ex):
    """デフロスト補正係数

    Args:
      Theta_ex(ndarray): 1時間平均の外気温度 (℃)
      h_ex(ndarray): 1時間平均の外気相対湿度

    Returns:
      ndarray: デフロスト補正係数

    """
    # 作業領域確保
    C_def = np.ones(24 * 365)

    f = np.logical_and(Theta_ex < 5.0, h_ex >= 80.0)
    C_def[f] = 0.85

    return C_def


# ============================================================================
# R.3.2 ヒートポンプユニットの暖房出力
# ============================================================================


def get_Q_HPU(Q_out_hs_HPU):
    """1時間当たりのヒートポンプユニットの暖房出力 (10)

    Args:
      Q_out_hs_HPU(ndarray): 1時間当たりの温水暖房用熱源機のヒートポンプユニット分担暖房出力 (MJ/h)

    Returns:
      ndarray: 1時間当たりのヒートポンプユニットの暖房出力 (MJ/h)

    """
    Q_HPU = Q_out_hs_HPU

    return Q_HPU


def get_Q_out_hs_HPU(Q_dmd_H_hs, Q_max_H_HPU, r_HPU):
    """1時間当たりの温水暖房用熱源機のヒートポンプユニット分担暖房出力 (11)

    Args:
      Q_dmd_H_hs(ndarray): 1時間当たりの温水暖房用熱源機の温水熱需要 (MJ/h)
      Q_max_H_HPU(ndarray): 1時間当たりのヒートポンプユニットの最大暖房出力 (MJ/h)
      r_HPU(ndarray): 1時間平均のヒートポンプユニット暖房出力分担率 (-)

    Returns:
      ndarray: 1時間当たりの温水暖房用熱源機のヒートポンプユニット分担暖房出力 (MJ/h)

    """
    Q_out_hs_HPU = np.minimum(Q_dmd_H_hs, Q_max_H_HPU) * r_HPU

    return Q_out_hs_HPU


# ============================================================================
# R.3.3 ガスユニットの補機の消費電力
# ============================================================================


def calc_E_E_GU_aux(q_G_GU, r_GU):
    """1時間当たりのガスユニットの補機の消費電力量 (12)

    Args:
      q_G_GU(ndarray): 1時間平均のガスユニットのガス消費量 (W)
      r_GU(ndarray): 1時間平均のガスユニットの暖房出力分担率 (-)

    Returns:
      ndarray: 1時間当たりのガスユニットの補機の消費電力量 (kWh/h)

    """
    # 1時間平均のガス燃焼時のガスユニットの補機の消費電力 (12b)
    P_GU_aux_ON = get_P_GU_aux_ON(q_G_GU)

    # 1時間当たりのガスユニットの補機の消費電力量 (12a)
    E_E_GU_aux = get_E_E_GU_aux(P_GU_aux_ON, r_GU)

    return E_E_GU_aux


def get_E_E_GU_aux(P_GU_aux_ON, r_GU):
    """1時間当たりのガスユニットの補機の消費電力量 (12a)

    Args:
      P_GU_aux_ON(ndarray): 1時間平均のガス燃焼時のガスユニットの補機の消費電力 (W)
      r_GU(ndarray): 1時間平均のガスユニットの暖房出力分担率 (-)

    Returns:
      ndarray: 1時間当たりのガスユニットの補機の消費電力量 (kWh/h)

    """
    E_E_GU_aux = P_GU_aux_ON * r_GU * 10 ** (-3)

    return E_E_GU_aux


def get_P_GU_aux_ON(q_G_GU):
    """1時間平均のガス燃焼時のガスユニットの補機の消費電力 (12b)

    Args:
      q_G_GU(ndarray): 1時間平均のガスユニットのガス消費量 (W)

    Returns:
      ndarray: 1時間平均のガス燃焼時のガスユニットの補機の消費電力 (W)

    """
    P_GU_aux_ON = f_GU_P_aux(q_G_GU)

    return P_GU_aux_ON


# ============================================================================
# R.3.4 ガスユニットのガス消費量
# ============================================================================


def calc_E_G_GU(e_GU_rtd, q_GU_rtd, q_out_hs, r_GU, Theta_SW_hs):
    """1時間当たりのガスユニットのガス消費量 (13)

    Args:
      e_GU_rtd(float): ガスユニットの定格暖房効率 (-)
      q_GU_rtd(float): ガスユニットの定格暖房能力 (W)
      q_out_hs(ndarray): 1時間平均の温水暖房用熱源機の暖房出力 (W)
      r_GU(ndarray): 1時間平均のガスユニットの暖房出力分担率 (-)
      Theta_SW_hs(ndarray): 温水暖房用熱源機の往き温水温度 (℃)

    Returns:
      ndarray: 1時間当たりのガスユニットのガス消費量 (MJ/h)

    """
    # 1時間平均のガスユニットの暖房出力 (13c)
    q_GU = get_q_GU(q_out_hs, q_GU_rtd)

    # 1時間平均のガスユニットのガス消費量 (13b)
    q_G_GU = get_q_G_GU(q_GU, e_GU_rtd, q_GU_rtd, Theta_SW_hs)

    # 1時間当たりのガスユニットのガス消費量 (13a)
    E_G_GU = get_E_G_GU(q_G_GU, r_GU)

    return E_G_GU


def get_E_G_GU(q_G_GU, r_GU):
    """1時間当たりのガスユニットのガス消費量 (13a)

    Args:
      q_G_GU(ndarray): 1時間平均のガスユニットのガス消費量 (W)
      r_GU(ndarray): 1時間平均のガスユニットの暖房出力分担率 (-)

    Returns:
      ndarray: 1時間当たりのガスユニットのガス消費量 (MJ/h)

    """
    E_G_GU = q_G_GU * r_GU * 3600 * 10 ** (-6)

    return E_G_GU


def get_q_G_GU(q_GU, e_GU_rtd, q_GU_rtd, Theta_SW_hs):
    """1時間平均のガスユニットのガス消費量 (13b)

    Args:
      q_GU(ndarray): 1時間平均のガスユニットの暖房出力 (W)
      e_GU_rtd(float): ガスユニットの定格暖房効率 (-)
      q_GU_rtd(float): ガスユニットの定格暖房能力 (W)
      Theta_SW_hs(ndarray): 温水暖房用熱源機の往き温水温度 (℃)

    Returns:
      ndarray: 1時間平均のガスユニットのガス消費量 (-)

    """
    q_G_GU = f_GU_G(q_GU, e_GU_rtd, q_GU_rtd, Theta_SW_hs)

    return q_G_GU


def get_q_GU(q_out_hs, q_GU_rtd):
    """1時間平均のガスユニットの暖房出力 (13c)

    Args:
      q_out_hs(ndarray): 1時間平均の温水暖房用熱源機の暖房出力 (W)
      q_GU_rtd(float): ガスユニットの定格暖房効率 (-)

    Returns:
      ndarray: 1時間平均のガスユニットの暖房出力 (W)

    """
    q_GU = np.minimum(q_out_hs, q_GU_rtd)

    return q_GU


def get_e_GU_rtd():
    """ガスユニットの定格暖房効率

    Args:

    Returns:
      float: ガスユニットの定格暖房効率 (-)

    """
    return 0.87


def get_q_GU_rtd():
    """ガスユニットの定格暖房能力

    Args:

    Returns:
      float: ガスユニットの定格暖房能力 (W)

    """
    return 14000.0


# ============================================================================
# R.3.5 暖房出力分担率
# ============================================================================


def get_r_GU(r_HPU):
    """1時間平均のガスユニットの暖房出力分担率 (14)

    Args:
      r_HPU(ndarray):1時間平均のヒートポンプユニットの暖房出力分担率

    Returns:
      ndarray: 1時間平均のガスユニットの暖房出力分担率

    """
    r_GU = 1.0 - r_HPU

    return r_GU


def get_r_HPU(q_HPU_max, q_out_hs):
    """1時間平均のヒートポンプユニットの暖房出力分担率 (15)

    Args:
      q_HPU_max(ndarray): 1時間平均のヒートポンプユニットの最大暖房出力 (W)
      q_out_hs(ndarray): 1時間平均の温水暖房用熱源機の暖房出力 (W)

    Returns:
      ndarray: 1時間平均のヒートポンプユニットの暖房出力分担率 (-)

    """
    # ヒートポンプ運転率補正係数
    CF_HPU = get_CF_HPU()

    r_HPU = q_HPU_max / q_out_hs * CF_HPU

    return np.clip(r_HPU, 0.0, 1.0)


def get_CF_HPU():
    """ヒートポンプ運転率補正係数

    Args:

    Returns:
      float: ヒートポンプ運転率補正係数

    """
    return 0.84


def get_q_HPU_max(Q_max_H_HPU):
    """1時間平均のヒートポンプユニットの最大暖房出力 (16)

    Args:
      Q_max_H_HPU(float): 1時間当たりのヒートポンプユニットの最大暖房出力 (MJ/h)

    Returns:
      float: 1時間平均のヒートポンプユニットの最大暖房出力 (W)

    """
    q_HPU_max = Q_max_H_HPU * 10**6 / 3600

    return q_HPU_max


# ============================================================================
# R.3.6 温水暖房用熱源機の平均暖房出力及び最大暖房出力
# ============================================================================


def get_q_out_hs(Q_out_hs):
    """1時間平均の温水暖房用熱源機の暖房出力 (17)

    Args:
      Q_out_hs(ndarray): 1時間当たりの温水暖房用熱源機の暖房出力 (MJ/h)

    Returns:
      float: 1時間平均の温水暖房用熱源機の暖房出力 (W)

    """
    q_out_hs = Q_out_hs * 10**6 / 3600

    return q_out_hs


def get_Q_max_H_hs(q_GU_rtd):
    """1時間当たりの温水暖房用熱源機の最大暖房出力 (18)

    Args:
      q_GU_rtd(float): ガスユニットの定格暖房能力 (W)

    Returns:
      ndarray: 1時間当たりの温水暖房用熱源機の最大暖房出力 (MJ/h)

    """
    Q_max_H_hs = np.full(24 * 365, q_GU_rtd * 3600 * 10 ** (-6))

    return Q_max_H_hs


# ============================================================================
# R4. 評価関数
# ============================================================================


# ============================================================================
# R.4.1 ガスユニット
# ============================================================================


def f_GU_G(q_GU, e_GU_rtd, q_GU_rtd, Theta_SW_hs):
    """ガスユニットのガス消費量を求める関数 (19)

    Args:
      q_GU(ndarray): ガスユニットの暖房出力 (W)
      e_GU_rtd(float): ガスユニットの定格暖房効率 (-)
      q_GU_rtd(float): ガスユニットの定格暖房能力 (W)
      Theta_SW_hs(ndarray): 温水暖房用熱源機の往き温水温度 (℃)

    Returns:
      ndarray: ガスユニットのガス消費量 (W)

    """
    # f_ex, q_body の作業領域確保
    f_ex = np.zeros(24 * 365)
    q_body = np.zeros(24 * 365)

    # Theta_SW_hs == 40 の場合
    f1 = Theta_SW_hs == 40.0
    f_ex[f1] = get_table_1()[0][0]
    q_body[f1] = get_table_1()[1][0]

    # Theta_SW_hs == 60 の場合
    f2 = Theta_SW_hs == 60.0
    f_ex[f2] = get_table_1()[0][1]
    q_body[f2] = get_table_1()[1][1]

    e_ex = e_GU_rtd * f_ex * (q_GU_rtd + q_body) / q_GU_rtd

    return (q_GU + q_body) / e_ex


def get_table_1():
    """表1 ガスユニットの定格暖房効率を補正する係数及びガスユニットの筐体放熱損失

    Args:

    Returns:
      list: 表1 ガスユニットの定格暖房効率を補正する係数及びガスユニットの筐体放熱損失

    """
    table_1 = [
        (1.064, 1.038),
        (123.74, 225.26)
    ]

    return table_1


def f_GU_P_aux(q_G_GU):
    """ガスユニットの補機の消費電力を求める関数 (20)

    Args:
      q_G_GU(ndarray): ガスユニットのガス消費量 (W)

    Returns:
      ndarray: ガスユニットの補機の消費電力 (W)

    """
    return 73.0 + 0.003 * q_G_GU
