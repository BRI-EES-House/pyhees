# ============================================================================
# 付録 A 機器の性能を表す仕様の決定方法
# ============================================================================

# ============================================================================
# A.2 定格暖房能力
# ============================================================================

def get_q_rtd_H(q_rq_H, A_HCZ, f_cT, f_cI):
    """定格暖房能力

    Args:
      q_rq_H(float): 単位面積当たりの必要暖房能力
      A_HCZ(float): 暖冷房区画の床面積
      f_cT(float): 外気温度補正係数
      f_cI(float): 間歇運転能力補正係数

    Returns:
      float: 定格暖房能力

    """
    return q_rq_H * A_HCZ * f_cT * f_cI  # (1)


# 単位面積当たりの必要暖房能力
def calc_q_rq_H(region):
    """単位面積当たりの必要暖房能力

    Args:
      region(int): 地域区分

    Returns:
      float: 単位面積当たりの必要暖房能力

    """
    table_a_2 = get_table_a_2()

    return table_a_2[region - 1]


# 外気温度補正係数
def get_f_cT(region):
    """外気温度補正係数

    Args:
      region(int): 地域区分

    Returns:
      float: 外気温度補正係数

    """
    return 1.05


# 間歇運転能力補正係数
def calc_f_cI(mode, R_type):
    """間歇運転能力補正係数

    Args:
      mode(str): 運転方式
      R_type(string): 居室の形式

    Returns:
      float: 間歇運転能力補正係数

    Raises:
      ValueError: modeが'ろ', '連続', 'は', '間歇'以外の場合に発生
      ValueError: R_typeが'主たる居室', 'その他の居室'以外の場合に発生

    """
    if mode in ['ろ', '連続']:
        y = 0
    elif mode in ['は', '間歇']:
        y = 1
    else:
        raise ValueError(mode)

    if R_type == '主たる居室':
        x = 0
    elif R_type == 'その他の居室':
        x = 1
    else:
        raise ValueError(R_type)

    table_a_3 = get_table_a_3()

    return table_a_3[y][x]

def get_table_a_2():
    """表A.2 単位面積当たりの必要暖房能力

    Args:

    Returns:
      list: 単位面積当たりの必要暖房能力

    """
    # 表A.2 単位面積当たりの必要暖房能力
    table_a_2 = [
        139.3,
        120.7,
        111.3,
        119.0,
        126.6,
        106.5,
        112.9
    ]
    return table_a_2


def get_table_a_3():
    """表A.3 間歇運転能力補正係数

    Args:

    Returns:
      list: 間歇運転能力補正係数

    """
    # 表A.3 間歇運転能力補正係数
    table_a_3 = [
        (1.0, 1.0),
        (3.034, 4.805)
    ]
    return table_a_3


# ============================================================================
# A.3 蓄熱効率
# ============================================================================

def get_e_rtd_H():
    """蓄熱効率

    Args:

    Returns:
      float: 蓄熱効率

    """
    return 0.850


if __name__ == '__main__':
    region = 6
    A_HCZ = 27.7
    mode = '間歇運転'
    R_type = '主たる居室'

    # 単位面積当たりの必要暖房能力
    q_rq_H = calc_q_rq_H(region)

    # 外気温度補正係数
    f_cT = get_f_cT(region)

    # 間歇運転能力補正係数
    f_cI = calc_f_cI(mode, R_type)

    # 定格暖房能力
    q_rtd_H = get_q_rtd_H(q_rq_H, A_HCZ, f_cT, f_cI)

    print('region = {}'.format(region))
    print('A_HCZ = {}'.format(A_HCZ))
    print('mode = {}'.format(mode))
    print('R_type = {}'.format(R_type))
    print('q_rq_H = {}'.format(q_rq_H))
    print('f_cT = {}'.format(f_cT))
    print('f_cI = {}'.format(f_cI))
    print('q_rtd_H = {}'.format(q_rtd_H))
