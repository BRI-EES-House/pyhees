# ============================================================================
# 付録A 密閉形太陽熱温水器（直圧式）
# ============================================================================

import numpy as np

# ============================================================================
# A.3 貯湯部
# ============================================================================

# ============================================================================
# A.3.1 熱交換器の温度効率
# ============================================================================

def calc_Epsilon_t_hx_d_t(c_p_htm, UA_hx, G_htm_d_t):
    """熱交換器の温度効率 (-) (1)

    Args:
      c_p_htm(float): 熱媒の定圧比熱
      UA_hx(float): 熱交換器の伝熱係数 (-)
      G_htm_d_t(ndarray): 1時間当たりの熱媒の循環量 (kg/h)

    Returns:
      ndarray: 熱交換器の温度効率 (-)

    """
    Epsilon_t_hx_d_t = np.zeros(24 * 365)

    f1 = G_htm_d_t == 0
    Epsilon_t_hx_d_t[f1] = 1

    f2 = G_htm_d_t > 0
    exp_tmp = - UA_hx / (c_p_htm * G_htm_d_t[f2] * 10 **3 / 3600)
    Epsilon_t_hx_d_t[f2] = 1 - np.exp(exp_tmp)

    return Epsilon_t_hx_d_t


# ============================================================================
# A.3.2 貯湯タンク内の水の利用可否
# ============================================================================

def calc_isAvailable_w_tank(Theta_wtr, Theta_ex_p6h_Ave, Theta_w_tank_mixed_prev, Theta_w_tank_upper_prev, t_hc_start_d):
    """貯湯タンク内の水の利用可否 (-) (2)

    Args:
      Theta_wtr(ndarray): 日平均給水温度 (℃)
      Theta_ex_p6h_Ave(ndarray): 当該時刻を含む過去6時間の平均外気温度 (℃)
      Theta_w_tank_mixed_prev(float): 完全混合を仮定した場合の入水・出水後の貯湯タンクの水の温度
      Theta_w_tank_upper_prev(float): 入水・出水後の貯湯タンク上層部の水の温度
      t_hc_start_d(int): 集熱開始時刻
    
    Returns:
      bool: 貯湯タンク内の水の利用可否 (-)

    """
    # 貯湯タンク内の水の利用可否の計算領域を確保
    isAvailable_w_tank_d_t = False

    # 貯湯タンクからの出水の有無を判断する基準となる過去6時間の平均外気温度
    Theta_ex_p6h_Ave_lmt= get_Theta_ex_p6h_Ave_lmt()

    if t_hc_start_d == 1:
        f1 = Theta_w_tank_mixed_prev <= Theta_wtr or Theta_ex_p6h_Ave <= Theta_ex_p6h_Ave_lmt
        if f1:
          isAvailable_w_tank_d_t = False

        f2 = Theta_w_tank_mixed_prev > Theta_wtr and Theta_ex_p6h_Ave > Theta_ex_p6h_Ave_lmt
        if f2:
          isAvailable_w_tank_d_t = True
    
    else:
        f1 = Theta_w_tank_upper_prev <= Theta_wtr or Theta_ex_p6h_Ave <= Theta_ex_p6h_Ave_lmt
        if f1:
          isAvailable_w_tank_d_t = False

        f2 = Theta_w_tank_upper_prev > Theta_wtr and Theta_ex_p6h_Ave > Theta_ex_p6h_Ave_lmt
        if f2:
          isAvailable_w_tank_d_t = True

    return isAvailable_w_tank_d_t


def calc_Theta_ex_p6h_Ave_d_t(Theta_ex_d_t):
    """当該時刻を含む過去6時間の平均外気温度 (℃) (3)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分
    
    Returns:
      ndarray: 当該時刻を含む過去6時間の平均外気温度 (℃)

    """
    # 5時間前（過去6時間）までを拡張した配列を作る
    tmp = np.zeros(365 * 24 + 5)
    tmp[0:5] = Theta_ex_d_t[-5:]
    tmp[5:] = Theta_ex_d_t[0:8760]

    # 畳み込み演算
    # 6時間分のデータにそれぞれ1/6を掛けて加算する→平均が求まる
    Theta_ex_p6h_Ave_d_t = np.convolve(tmp,  np.ones(6) / 6, mode='valid')

    return Theta_ex_p6h_Ave_d_t


def get_Theta_ex_p6h_Ave_lmt():
    """貯湯タンクからの出水の有無を判断する基準となる過去6時間の平均外気温度 (℃)

    Args: 

    Returns:
      float: 貯湯タンクからの出水の有無を判断する基準となる過去6時間の平均外気温度 (℃)
    """
    return -0.5


# ============================================================================
# A.4.1 温度効率
# ============================================================================
def calc_Epsilon_t_stc_d_t(A_stcp, b1, c_p_htm, G_htm_d_t):
    """熱交換器の温度効率 (-) (4)

    Args:
      A_stcp(float): 集熱部の有効集熱面積(m2)
      b1(float): 集熱器の集熱効率特性線図一次近似式の傾き（W/(m2・K)）
      c_p_htm(float): 熱媒の定圧比熱（kJ/(kg･K)）
      G_htm_d_t(ndarray): 1時間当たりの熱媒の循環量 (kg/h)

    Returns:
      ndarray: 熱交換器の温度効率

    """
    Epsilon_t_stc_d_t = np.zeros(24 * 365)

    f1 = G_htm_d_t == 0 
    Epsilon_t_stc_d_t[f1] = 1

    f2 = G_htm_d_t > 0
    exp_tmp = - ( b1 * A_stcp)/ (c_p_htm * G_htm_d_t[f2] * 10 ** 3 / 3600)
    Epsilon_t_stc_d_t[f2] = 1 - np.exp(exp_tmp)

    return Epsilon_t_stc_d_t


def get_Epsilon_t_stp_d_t():
    """集熱配管の温度効率 (-) (5)

    Args:

    Returns:
      float: 集熱配管の温度効率 (-)

    """
    return np.zeros(24 * 365)


def calc_G_htm_d_t(g_htm, I_s_d_t, delta_tau_hc_d_t):
    """1時間当たりの熱媒の循環量 (6)

    Args:
      g_htm(float): 単位日射量当たりの循環流量((kg/h)/(W/m2))
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)
      delta_tau_hc_d_t(ndarray): 1時間当たりの集熱時間数(-)

    Returns:
      ndarray: 1時間当たりの熱媒の循環量

    """
    return I_s_d_t * g_htm * delta_tau_hc_d_t


# ============================================================================
# A.4.3 集熱時間数および集熱開始時刻
# ============================================================================

def calc_delta_tau_hc_d_t(I_s_d_t):
    """1時間当たりの集熱時間数 (h/h) (7)

    Args:
      I_s_d_t(ndarray): 集熱器の単位面積当たりの平均日射量 (W/m2)

    Returns:
      ndarray: 1時間当たりの集熱時間数 (h/h)

    """
    # 集熱の可否を判断する基準となる単位面積当たりの平均日射量 (W/m2)
    I_s_lmt = get_I_s_lmt()

    # 1時間当たりの集熱時間数の計算領域を確保
    delta_tau_hc_d_t = np.zeros(24 * 365, dtype=np.int32)

    # I_s_d_t == I_s_lmt  の場合
    f1 = I_s_d_t == I_s_lmt
    delta_tau_hc_d_t[f1] = 0

    # I_s_d_t > I_s_lmt の場合
    f2 = I_s_d_t > I_s_lmt
    delta_tau_hc_d_t[f2] = 1

    return delta_tau_hc_d_t


def calc_t_hc_start_d(I_s_d_t):
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
    t_hc_start_d = np.zeros(365 * 24, dtype=np.int32)

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
# A.4.4 循環ポンプの稼働時間数
# ============================================================================

def get_delta_tau_pump_hc_d_t():
    """1時間当たりの集熱時における循環ポンプの稼働時間数 (9)

    Returns:
      ndarray: 1時間当たりの集熱時における循環ポンプの稼働時間数 (h/h)

    """
    return np.zeros(24 * 365, dtype=np.int32)


def get_delta_tau_pump_non_hc_d_t():
    """1時間当たりの非集熱時における循環ポンプの稼働時間数 (10)

    Returns:
      ndarray: 1時間当たりの非集熱時における循環ポンプの稼働時間数 (h/h)

    """
    return np.zeros(24 * 365, dtype=np.int32)


# ============================================================================
# A.5 仕様
# ============================================================================

def calc_b0(b0):
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


def calc_b1(b1):
    """集熱器の集熱効率特性線図一次近似式の傾き W/(m2・K)

    Args:
      b0(float): 集熱器の集熱効率特性線図一次近似式の傾き W/(m2・K)

    Returns:
      float: 集熱器の集熱効率特性線図一次近似式の傾き W/(m2・K)

    """
    if b1 is not None:
        return b1
    else:
        # 表2 仕様を表す示すパラメータとその決定方法
        table_2 = get_table_2()
        return table_2[2]


def calc_g_htm(g_htm):
    """単位日射量当たりの循環流量（kg/h)/（W/m2）

    Args:
      g_htm(float): 単位日射量当たりの循環流量

    Returns:
      float: 単位日射量当たりの循環流量（kg/h)/（W/m2）

    """
    if g_htm is not None:
        return g_htm
    else:
        # 表2 仕様を表す示すパラメータとその決定方法
        table_2 = get_table_2()
        return table_2[3]


def calc_UA_hx(UA_hx):
    """熱交換器の伝熱係数 (W/K)

    Args:
      UA_hx(float): 熱交換器の伝熱係数

    Returns:
      float: 熱交換器の伝熱係数 (W/K)

    """
    if UA_hx is not None:
        return UA_hx
    else:
        # 表2 仕様を表す示すパラメータとその決定方法
        table_2 = get_table_2()
        return table_2[4]


def calc_eta_r_tank(eta_r_tank):
    """有効出湯効率 (%)

    Args:
      eta_r_tank(float): 有効出湯効率

    Returns:
      float: 有効出湯効率 (W/K)

    """
    if eta_r_tank is not None:
        return eta_r_tank
    else:
        # 表2 仕様を表す示すパラメータとその決定方法
        table_2 = get_table_2()
        return table_2[6]


def calc_UA_tank(UA_tank):
    """熱交換器の伝熱係数 (W/K)

    Args:
      UA_hx(float): 熱交換器の伝熱係数

    Returns:
      float: 熱交換器の伝熱係数 (W/K)

    """
    if UA_tank is not None:
        return UA_tank
    else:
        # 表2 仕様を表す示すパラメータとその決定方法
        table_2 = get_table_2()
        return table_2[7]


def get_P_pump_hc():
    """集熱時における循環ポンプの消費電力量 (11)

    Returns:
      float: 集熱時における循環ポンプの消費電力量 (W)

    """
    return 0.0


def get_P_pump_non_hc():
    """非集熱時における循環ポンプの消費電力量 (12)

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
        220,
        None,
        75,
        5.81
    ]
    return table_2
