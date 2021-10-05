# ============================================================================
# 付録 A 熱交換型換気設備
# ============================================================================

from math import exp, sin, cos, pi, ceil, floor


# ============================================================================
# A.2 熱交換型換気設備の補正温度交換効率
# ============================================================================

def calc_etr_dash_t(etr_t_raw, e, C_bal, C_leak):
    """ 熱交換型換気設備の補正熱交換効率 (-) (1)

    :param etr_t_raw: 熱交換型換気設備の温度交換効率 (-)
    :type etr_t_raw: float
    :param e: 有効換気量率 (-)
    :type e: float
    :param C_bal: 給気と排気の比率による温度交換効率の補正係数 (-)
    :type C_bal: float
    :param C_leak: 排気過多時における住宅外皮経由の漏気による温度交換効率の補正係数 (-)
    :type C_leak: float
    :return: 熱交換型換気設備の補正熱交換効率 (-)
    :rtype: float
    """

    # 熱交換型換気設備の温度交換効率
    etr_t = get_etr_t(etr_t_raw)

    # カタログ表記誤差による温度交換効率の補正係数 (-)
    C_tol = get_C_tol()

    # 有効換気量率による温度交換効率の補正係数 (2)
    C_eff = get_C_eff(etr_t, e)

    # 熱交換型換気設備の補正熱交換効率 (-) (1)
    etr_dash_t = get_etr_dash_t(etr_t, C_tol, C_eff, C_bal, C_leak)

    return etr_dash_t


def get_etr_dash_t(etr_t, C_tol, C_eff, C_bal, C_leak):
    """ 熱交換型換気設備の補正熱交換効率 (-) (1)

    :param etr_t: 熱交換型換気設備の温度交換効率 (-)
    :type etr_t: float
    :param C_tol: カタログ表示誤差による温度交換効率の補正係数 (-)
    :type C_tol: float
    :param C_eff: 有効換気量率による温度交換効率の補正係数 (-)
    :type C_eff: float
    :param C_bal: 給気と排気の比率による温度交換効率の補正係数 (-)
    :type C_bal: float
    :param C_leak: 排気過多時における住宅外皮経由の漏気による温度交換効率の補正係数 (-)
    :type C_leak: float
    :return: 熱交換型換気設備の補正熱交換効率 (-)
    :rtype: float
    """

    etr_dash_t = etr_t * C_tol * C_eff * C_bal * C_leak  # (1)
    return etr_dash_t


# ============================================================================
# A.3 熱交換型換気設備の温度交換効率
# ============================================================================

def get_etr_t(etr_t_raw):
    """ 熱交換型換気設備の温度交換効率

    :param etr_t_raw: 熱交換型換気設備の温度交換効率 (-)
    :type etr_t_raw: float
    :return: 熱交換型換気設備の温度交換効率
    :rtype: float
    """

    # 温度交換効率の値は、100 分の 1 未満の端数を切り下げた小数第二位までの値
    etr_t = ceil(etr_t_raw * 100) / 100
    if etr_t > 0.95:
        return 0.95
    else:
        return etr_t


# ============================================================================
# A.4 カタログ表記誤差による温度交換効率の補正係数
# ============================================================================

def get_C_tol():
    """ カタログ表記誤差による温度交換効率の補正係数

    :return: カタログ表記誤差による温度交換効率の補正係数
    :rtype: float
    """
    return 0.95


# ============================================================================
# A.5 有効換気量率による温度交換効率の補正係数
# ============================================================================

def get_C_eff(etr_t, e):
    """ 有効換気量率による温度交換効率の補正係数 (2)

    :param etr_t: 熱交換型換気設備の温度交換効率 (-)
    :type etr_t: float
    :param e: 有効換気量率
    :type e: float
    :return: 有効換気量率による温度交換効率の補正係数
    :rtype: float
    """

    C_eff = 1 - ((1 / e - 1) * (1 - etr_t) / etr_t)  # (2)

    #100 分の 1 未満の端数を切り下げた小数第二位までの値
    C_eff = floor(C_eff * 100) / 100
    if C_eff < 0.0:
        C_eff = 0.0

    return C_eff


# ============================================================================
# A.6 給気と排気の比率による温度交換効率の補正係数
# ============================================================================

def get_C_bal(etr_t, etr_t_d, correction_flag):
    """ 給気と排気の比率による温度交換効率の補正係数

    :param etr_t: 給気と排気の比率による温度交換効率の補正係数
    :type etr_t: float
    :param etr_t_d: 補正設計風量比での熱交換型換気設備の温度交換効率
    :type etr_t_d: float
    :param correction_flag: 給気と排気の比率による補正を行うかの判定(Trueで行い、Falseで行わない。仕様書A.8)
    :type correction_flag: bool

    :return: 給気と排気の比率による温度交換効率の補正係数
    :rtype: float
    """
    if not correction_flag:
        return 0.90

    C_bal =  etr_t_d / etr_t  # (3)

    #100 分の 1 未満の端数を切り下げた小数第二位までの値
    C_bal = floor(C_bal * 100) / 100

    return C_bal


def get_etr_t_d(etr_d, R_dash_vnt_d, V_d_SA, V_d_RA):
    """ 当該住戸における補正設計風量比での熱通過有効度

    :param etr_d: 補正設計風量比での熱通過有効度
    :type etr_d: float
    :param R_dash_vnt_d: 補正設計風量比
    :type R_dash_vnt_d: float
    :param V_d_SA: 当該住戸における設計給気風量
    :type V_d_SA: float
    :param V_d_RA: 当該住戸における設計還気風量
    :type V_d_RA: float

    :return: 当該住戸における補正設計風量比での熱通過有効度
    :rtype: float
    """
    # (4)
    if V_d_RA > V_d_SA:
        return etr_d
    elif V_d_RA <= V_d_SA:
        return etr_d * R_dash_vnt_d


def get_etr(etr_t, R_dash_vnt_rtd, V_rtd_SA, V_rtd_RA):
    """ 定格条件における補正風量比での熱通過有効度

    :param etr_t: 熱交換型換気設備の温度交換効率
    :type etr_t: float
    :param R_dash_vnt_rtd: 定格条件における補正風量比
    :type R_dash_vnt_rtd: float
    :param V_rtd_SA: 定格条件における給気風量
    :type V_rtd_SA: float
    :param V_rtd_RA: 定格条件における還気風量
    :type V_rtd_RA: float

    :return: 定格条件における補正風量比での熱通過有効度
    :rtype: float
    """
    # (12)
    if V_rtd_RA > V_rtd_SA:
        return etr_t
    else:
        return etr_t / R_dash_vnt_rtd


def get_R(V_d_SA, V_d_RA, V_rtd_SA, V_rtd_RA):
    """ 風量比Rの計算

    :param V_d_SA: 当該住戸における設計給気風量
    :type V_d_SA: float
    :param V_d_RA: 当該住戸における設計還気風量
    :type V_d_RA: float
    :param V_rtd_SA: 定格条件における給気風量
    :type V_rtd_SA: float
    :param V_rtd_RA: 定格条件における還気風量
    :type V_rtd_RA: float

    :return R_vnt_d: 当該住戸における設計風量比
    :rtype R_vnt_d: float
    :return R_vnt_rtd: 定格条件における風量比
    :rtype R_vnt_rtd: float
    :return R_dash_vnt_d: 当該住戸における補正設計風量比
    :rtype R_dash_vnt_d: float
    :return R_dash_vnt_rtd: 定格条件における補正風量比
    :rtype R_dash_vnt_rtd: float
    """
    R_vnt_d         = min(V_d_SA/V_d_RA,        V_d_RA/V_d_SA)              # (7)
    R_vnt_rtd       = min(V_rtd_SA/V_rtd_RA,    V_rtd_RA/V_rtd_SA)          # (14)
    R_dash_vnt_d    = (lambda x: x if x!=1.0 else 1.0 - 1.0e-8)(R_vnt_d)    # (6)
    R_dash_vnt_rtd  = (lambda x: x if x!=1.0 else 1.0 - 1.0e-8)(R_vnt_rtd)  # (13)
    return R_vnt_d, R_vnt_rtd, R_dash_vnt_d, R_dash_vnt_rtd


def get_Vmin(V_d_SA, V_d_RA, V_rtd_SA, V_rtd_RA):
    """ 最小風量V_*_minの計算

    :param V_d_SA: 当該住戸における設計給気風量
    :type V_d_SA: float
    :param V_d_RA: 当該住戸における設計還気風量
    :type V_d_RA: float
    :param V_rtd_SA: 定格条件における給気風量
    :type V_rtd_SA: float
    :param V_rtd_RA: 定格条件における還気風量
    :type V_rtd_RA: float

    :return V_d_min: 当該住戸における設計最小風量
    :rtype V_d_min: float
    :return V_rtd_min: 定格条件における最小風量
    :rtype V_rtd_min: float
    """
    V_d_min     = min(V_d_SA,   V_d_RA)     # (10)
    V_rtd_min   = min(V_rtd_SA, V_rtd_RA)   # (9)
    return V_d_min, V_rtd_min


def get_etr_d_dc(R_dash_vnt_d, R_dash_vnt_rtd, etr, V_d_min, V_rtd_min):
    """ 直交流型熱交換器の場合に当該住戸における補正設計風量比での熱通過有効度を計算

    :param R_dash_vnt_d: 当該住戸における補正設計風量比
    :type R_dash_vnt_d: float
    :param R_dash_vnt_rtd: 定格条件における補正風量比
    :type R_dash_vnt_rtd: float
    :param etr: 定格条件における補正風量比での熱通過有効度
    :type etr: float
    :param V_d_min: 当該住戸における設計最小風量
    :type V_d_min: float
    :param V_rtd_min: 定格条件における最小風量
    :type V_rtd_min: float

    :return: 当該住戸における補正設計風量比での熱通過有効度(直交流型熱交換器の場合)
    :rtype: float
    """
    def etr_function_dc(N, R):
        # 引数が(N, R) = (N_rtd, R_dash_vnt_rtd)のとき(11a)式etrを返し、
        # 引数が(N, R) = (N_d, R_dash_vnt_d)のとき(5a)式etr_dを返す。
        return 1 - exp((exp(-pow(N, 0.78) * R) - 1) / (pow(N, -0.22) * R))

    def function_to_solve_dc(N_rtd):
        return etr_function_dc(N_rtd, R_dash_vnt_rtd) - etr  # (11a)

    # 二分法でfunction_to_solve_dc(N_rtd) = 0を解く
    min = pow(10.0, -8.0)
    max = pow(10.0, +8.0)
    err = pow(10.0, -8.0)

    while max - min > err:
        mid = (min + max) / 2.0
        if function_to_solve_dc(mid) * function_to_solve_dc(max) < 0:
            min = mid
        elif function_to_solve_dc(mid) * function_to_solve_dc(max) > 0:
            max = mid
        else:
            min = mid
            max = mid
            break

    N_rtd = (min + max) / 2.0

    N_d = N_rtd * V_rtd_min / V_d_min  # (8)

    return etr_function_dc(N_d, R_dash_vnt_d)  # (5a)


def get_etr_d_ac(R_dash_vnt_d, R_dash_vnt_rtd, etr, V_d_min, V_rtd_min, b, l, alpha):
    """ 向流-直交流型熱交換器の場合に当該住戸における補正設計風量比での熱通過有効度を計算

    :param R_dash_vnt_d: 当該住戸における補正設計風量比
    :type R_dash_vnt_d: float
    :param R_dash_vnt_rtd: 定格条件における補正風量比
    :type R_dash_vnt_rtd: float
    :param etr: 定格条件における補正風量比での熱通過有効度
    :type etr: float
    :param V_d_min: 当該住戸における設計最小風量
    :type V_d_min: float
    :param V_rtd_min: 定格条件における最小風量
    :type V_rtd_min: float
    :param b: 向流-直交流複合型熱交換器の向流部の幅
    :type b: float
    :param l: 向流-直交流複合型熱交換器の向流部の長さ
    :type l: float
    :param alpha: 向流-直交流複合型熱交換器の向流部と直交流部の接続角度 [deg]
    :type alpha: float

    :return: 当該住戸における補正設計風量比での熱通過有効度(向流-直交流型熱交換器の場合)
    :rtype: float
    """
    alpha *= pi / 180.0  # alphaの単位を[deg]から[rad]に変換

    def etr_function_ac(N, R):
        # 引数が(N, R) = (N_rtd, R_dash_vnt_rtd)のとき(11b)式etrを返し、
        # 引数が(N, R) = (N_d, R_dash_vnt_d)のとき(5b)式etr_dを返す。
        return (1 - exp(-(1 - R) * (
                1 + ((b / l) * sin(alpha) * cos(alpha) / (0.0457143 * N ** 2 + 0.0691429 * N + 0.9954286))) * N)) \
               / (1 - R * exp(-(1 - R) * (
                ((b / l) * sin(alpha) * cos(alpha)) / (0.00457143 * N ** 2 + 0.0691429 ** N + 0.9954286)) * N))

    def function_to_solve_ac(N_rtd):
        return etr_function_ac(N_rtd, R_dash_vnt_rtd) - etr  # (11b)

    # 二分法でfunction_to_solve_ac(N_rtd) = 0を解く
    min = pow(10.0, -8.0)
    max = pow(10.0, +8.0)
    err = pow(10.0, -8.0)

    while max - min > err:
        mid = (min + max) / 2.0
        # print(min, mid, max)
        # print(function_to_solve_ac(min), function_to_solve_ac(mid), function_to_solve_ac(max))
        if function_to_solve_ac(mid) * function_to_solve_ac(max) < 0:
            min = mid
        elif function_to_solve_ac(mid) * function_to_solve_ac(max) > 0:
            max = mid
        else:
            min = mid
            max = mid
            break

    N_rtd = (min + max) / 2.0

    N_d = N_rtd * V_rtd_min / V_d_min  # (8)

    return etr_function_ac(N_d, R_dash_vnt_d)  # (5b)
 

# ============================================================================
# A.7 排気過多時における住宅外皮経由の漏気による温度交換効率の補正係数
# ============================================================================

def get_C_leak(V_d_SA, V_d_RA, correction_flag):
    """ 給気と排気の比率による温度交換効率の補正係数

    :param V_d_SA: 当該住戸における設計給気風量
    :type V_d_SA: float
    :param V_d_RA: 当該住戸における設計還気風量
    :type V_d_RA: float
    :param correction_flag: 給気と排気の比率による補正を行うかの判定(Trueで行い、Falseで行わない。仕様書A.8)
    :type correction_flag: bool

    :return: 排気過多時における住宅外皮経由の漏気による温度交換効率の補正係数
    :rtype: float
    """
    if not correction_flag:
        return 1.00

    C_leak =  min(1.0, V_d_SA / V_d_RA)  # (15)

    #100 分の 1 未満の端数を切り下げた小数第二位までの値
    C_leak = floor(C_leak * 100) / 100

    return C_leak
