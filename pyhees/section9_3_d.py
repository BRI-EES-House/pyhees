# ============================================================================
# 付録D 集熱器の集熱効率特性線図一次近似式
# ============================================================================

# D.1 記号及び単位

# D.2 集熱器の集熱効率特性線図一次近似式

def get_etr(d_0, d_1, Theta_in, Theta_ex, I_s):
    """集熱器の集熱効率特性線図一次近似式(JIA A 4112 または SS-TS010) (1)

    :param d_0: 集熱器の集熱効率特性線図一次近似式の切片
    :type d_0: tuple
    :param d_1: 集熱器群を構成する集熱器の集熱効率特性線図一次近似式の傾き (W/(m2K))
    :type d_1: tuple
    :param Theta_in: 集熱器の入口における空気温度
    :type Theta_in: float
    :param Theta_ex: 外気温度
    :type Theta_ex: ndarray
    :param I_s: 単位面積当たりの平均日射量
    :type I_s: float
    :return: 集熱器の集熱効率特性線図一次近似式
    :rtype: float
    """
    return d_0 - d_1 * (Theta_in - Theta_ex) / I_s
