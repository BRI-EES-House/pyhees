# ============================================================================
# 付録C 開放形太陽熱温水器
# ============================================================================

import numpy as np
from pyhees.util import util

# ============================================================================
# C.3 貯湯部
# ============================================================================

# ============================================================================
# C.3.1 熱交換器の温度効率
# ============================================================================

def get_epsilon_t_hx_d_t():
    """熱交換器の温度効率 (-) (1)

    Args:

    Returns:
      ndarray: 熱交換器の温度効率 (-)
    """
    return np.ones(24 * 365)


# ============================================================================
# C.3.2 貯湯タンク内の水の利用可否
# ============================================================================

def get_isAvailable_w_tank(Theta_wtr, Theta_ex_p6h_Ave, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d):
    """貯湯タンク内の水の利用可否 (-) (2)

    Args:
      Theta_wtr(float): 日平均給水温度 (℃)
      Theta_ex_p6h_Ave(float): 当該時刻を含む過去6時間の平均外気温度 (℃)
      Theta_w_tank_mixed_prev(float): 完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度 (℃)
      Theta_w_tank_upper_prev(float): 入水・出水後の貯湯タンク上層部の水の温度 (℃)
      t_hc_start_d(int): 集熱開始時刻 (-)

    Returns:
      bool: 貯湯タンク内の水の利用可否 (-)
    """
    # 貯湯タンクからの出水の有無を判断する基準となる過去6時間の平均外気温度
    Theta_ex_p6h_Ave_lmt = get_Theta_ex_p6h_Ave_lmt()

    if t_hc_start_d == 1:
        f1 = Theta_w_tank_mixed_prev < Theta_wtr or util.is_equal(Theta_w_tank_mixed_prev, Theta_wtr) \
            or Theta_ex_p6h_Ave < Theta_ex_p6h_Ave_lmt or util.is_equal(Theta_ex_p6h_Ave, Theta_ex_p6h_Ave_lmt)
        if f1:
            return False

        f2 = Theta_w_tank_mixed_prev > Theta_wtr and Theta_ex_p6h_Ave > Theta_ex_p6h_Ave_lmt
        if f2:
            return True

    else:
        f1 = Theta_w_tank_upper_prev < Theta_wtr or util.is_equal(Theta_w_tank_upper_prev, Theta_wtr) \
            or Theta_ex_p6h_Ave < Theta_ex_p6h_Ave_lmt or util.is_equal(Theta_ex_p6h_Ave, Theta_ex_p6h_Ave_lmt)
        if f1:
            return False

        f2 = Theta_w_tank_upper_prev > Theta_wtr and Theta_ex_p6h_Ave > Theta_ex_p6h_Ave_lmt
        if f2:
            return True


def get_Theta_ex_p6h_Ave(Theta_ex_d_t, dt):
    """当該時刻を含む過去6時間の平均外気温度 (℃) (3)

    Args:
      Theta_ex_d_t(ndarray): 外気温度 (℃)

    Returns:
      ndarray: 当該時刻を含む過去6時間の平均外気温度 (℃)
    """
    # 5時間前（過去6時間）までを拡張した配列を作る
    tmp = np.concatenate((Theta_ex_d_t[-5:], Theta_ex_d_t))

    # 畳み込み演算
    # 6時間分のデータにそれぞれ1/6を掛けて加算する→平均が求まる
    Theta_ex_p6h_Ave_d_t = np.convolve(tmp,  np.ones(6) / 6, mode='valid')

    return Theta_ex_p6h_Ave_d_t[dt]


def get_Theta_ex_p6h_Ave_lmt():
    """貯湯タンクからの出水の有無を判断する基準となる過去6時間の平均外気温度 (℃)

    Args: 

    Returns:
      float: 貯湯タンクからの出水の有無を判断する基準となる過去6時間の平均外気温度 (℃)
    """
    return -0.5


# ============================================================================
# C.4 集熱部
# ============================================================================

# ============================================================================
# C.4.1 温度効率
# ============================================================================

def get_epsilon_t_stc_d_t(A_stcp, b1, c_p_htm, G_htm_d_t):
    """集熱器の温度効率 (-) (4)

    Args:
      A_stcp(float): 集熱部の有効集熱面積(m2)
      b1(float): 集熱器の集熱効率特性線図一次近似式の傾き (W/(m2・K))
      c_p_htm(float): 熱媒の定圧比熱 (kJ/(kg･K))
      G_htm_d_t(ndarray): 熱媒の循環量 (kg/h)

    Returns:
      ndarray: 集熱器の温度効率 (-)
    """
    epsilon_t_stc_d_t = np.zeros(24 * 365)

    f1 = G_htm_d_t == 0.0
    epsilon_t_stc_d_t[f1] = 1.0

    f2 = G_htm_d_t > 0.0
    exp_tmp = - (b1 * A_stcp) / (c_p_htm * G_htm_d_t[f2] * 10 ** 3 / 3600)
    epsilon_t_stc_d_t[f2] = 1 - np.exp(exp_tmp)

    return epsilon_t_stc_d_t


def get_epsilon_t_stp_d_t():
    """集熱配管の温度効率 (-) (5)

    Args:

    Returns:
      float: 集熱配管の温度効率 (-)
    """
    return np.zeros(24 * 365)


# ============================================================================
# C.4.2 熱媒の循環量
# ============================================================================

def get_G_htm_d_t(g_htm, I_s_d_t, Delta_tau_hc_d_t):
    """1時間当たりの熱媒の循環量 (kg/h) (6)

    Args:
      g_htm(float): 単位日射量当たりの循環流量((kg/h)/(W/m2))
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)
      Delta_tau_hc_d_t(ndarray): 1時間当たりの集熱時間数(-)

    Returns:
      ndarray: 1時間当たりの熱媒の循環量 (kg/h)
    """
    return I_s_d_t * g_htm * Delta_tau_hc_d_t


# ============================================================================
# C.4.3 集熱時間数および集熱開始時刻
# ============================================================================

def get_Delta_tau_hc_d_t(I_s_d_t):
    """1時間当たりの集熱時間数 (h/h) (7)

    Args:
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)

    Returns:
      ndarray: 1時間当たりの集熱時間数 (h/h)
    """
    # 集熱の可否を判断する基準となる単位面積当たりの平均日射量 (W/m2)
    I_s_lmt = get_I_s_lmt()

    # 1時間当たりの集熱時間数の計算領域を確保
    Delta_tau_hc_d_t = np.zeros(24 * 365)

    # I_s_d_t == I_s_lmt の場合
    f1 = I_s_d_t == I_s_lmt
    Delta_tau_hc_d_t[f1] = 0

    # I_s_d_t > I_s_lmt の場合
    f2 = I_s_d_t > I_s_lmt
    Delta_tau_hc_d_t[f2] = 1

    return Delta_tau_hc_d_t


def get_t_hc_start_d(I_s_d_t):
    """集熱開始時刻 (-) (8)

    Args:
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)

    Returns:
      ndarray: 集熱開始時刻 (-)
    """
    # 1時間前
    I_s_d_t_prev = np.roll(I_s_d_t, 1)

    # 集熱の可否を判断する基準となる単位面積当たりの平均日射量
    I_s_lmt = get_I_s_lmt()

    # 集熱開始時刻の計算領域を確保
    t_hc_start_d = np.zeros(24 * 365)

    f = np.logical_and(I_s_d_t > I_s_lmt, I_s_d_t_prev == I_s_lmt)
    t_hc_start_d[f] = 1

    return t_hc_start_d


def get_I_s_lmt():
    """集熱の可否を判断する基準となる単位面積当たりの平均日射量 (W/m2)

    Args:

    Returns:
        int: 集熱の可否を判断する基準となる単位面積当たりの平均日射量 (W/m2)
    """
    return 0


# ============================================================================
# C.4.4 循環ポンプの稼働時間数
# ============================================================================

def get_Delta_tau_pump_hc_d_t():
    """1時間当たりの集熱時における循環ポンプの稼働時間数 (h/h) (9)

    Returns:
      ndarray: 1時間当たりの集熱時における循環ポンプの稼働時間数 (h/h)
    """
    return np.zeros(24 * 365)


def get_Delta_tau_pump_non_hc_d_t():
    """1時間当たりの非集熱時における循環ポンプの稼働時間数 (h/h) (10)

    Returns:
      ndarray: 1時間当たりの非集熱時における循環ポンプの稼働時間数 (h/h)
    """
    return np.zeros(24 * 365)


# ============================================================================
# C.5 仕様
# ============================================================================

def get_b0(b0):
    """集熱器の集熱効率特性線図一次近似式の切片 (-)

    Args:
      b0(float): 集熱器の集熱効率特性線図一次近似式の切片 (-)

    Returns:
      float: 集熱器の集熱効率特性線図一次近似式の切片 (-)
    """
    if b0 is not None:
        return b0
    else:
        # 表2 仕様を表す示すパラメータとその決定方法
        table_2 = get_table_2()
        return table_2[1]


def get_b1(b1):
    """集熱器の集熱効率特性線図一次近似式の傾き W/(m2・K)

    Args:
      b1(float): 集熱器の集熱効率特性線図一次近似式の傾き W/(m2・K)

    Returns:
      float: 集熱器の集熱効率特性線図一次近似式の傾き W/(m2・K)
    """
    if b1 is not None:
        return b1
    else:
        # 表2 仕様を表す示すパラメータとその決定方法
        table_2 = get_table_2()
        return table_2[2]


def get_g_htm(g_htm):
    """単位日射量当たりの循環流量 (kg/h)/(W/m2)

    Args:
      g_htm(float): 単位日射量当たりの循環流量

    Returns:
      float: 単位日射量当たりの循環流量 (kg/h)/(W/m2)
    """
    if g_htm is not None:
        return g_htm
    else:
        # 表2 仕様を表す示すパラメータとその決定方法
        table_2 = get_table_2()
        return table_2[3]


def get_eta_r_tank(eta_r_tank):
    """有効出湯効率 (%)

    Args:
      eta_r_tank(float): 有効出湯効率 (%)

    Returns:
      float: 有効出湯効率 (%)
    """
    if eta_r_tank is not None:
        return eta_r_tank
    else:
        # 表2 仕様を表す示すパラメータとその決定方法
        table_2 = get_table_2()
        return table_2[5]


def get_UA_tank(UA_tank):
    """貯湯タンクの放熱係数(W/K)

    Args:
      UA_tank(float): 貯湯タンクの放熱係数(W/K)

    Returns:
      float: 貯湯タンクの放熱係数(W/K)
    """
    if UA_tank is not None:
        return UA_tank
    else:
        # 表2 仕様を表す示すパラメータとその決定方法
        table_2 = get_table_2()
        return table_2[6]


def get_P_pump_hc():
    """集熱時における循環ポンプの消費電力量 (W) (11)

    Returns:
      float: 集熱時における循環ポンプの消費電力量 (W)
    """
    return 0.0


def get_P_pump_non_hc():
    """非集熱時における循環ポンプの消費電力量 (W) (12)

    Returns:
      float: 非集熱時における循環ポンプの消費電力量 (W)
    """
    return 0.0


def get_table_2():
    """表2 仕様を表す示すパラメータとその決定方法

    Args:

    Returns:
      list: 仕様を表す示すパラメータとその決定方法
    """
    table_2 = [
        None,
        0.73,
        7.65,
        0.164,
        None,
        75.0,
        5.81
    ]
    return table_2
