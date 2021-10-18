# ============================================================================
# 付録 J 節湯の効果係数
# ============================================================================

import numpy as np


def get_f_sk(kitchen_watersaving_A, kitchen_watersaving_C, Theta_wtr_d):
    """# 台所水栓における節湯の効果係数 (1a)

    Args:
      kitchen_watersaving_A(bool): 台所水栓の手元止水機能の有無
      kitchen_watersaving_C(bool): 台所水栓の水優先吐水機能の有無
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      float: 台所水栓における節湯の効果係数 (-)

    """
    return get_f_sk_A(kitchen_watersaving_A) * get_f_sk_C(kitchen_watersaving_C, Theta_wtr_d)


def get_f_ss(shower_watersaving_A, shower_watersaving_B):
    """# 浴室シャワー水栓における節湯の効果係数 (1b)

    Args:
      shower_watersaving_A(bool): 浴室シャワー水栓の手元止水機能の有無
      shower_watersaving_B(bool): 浴室シャワー水栓の小流量吐水機能の有無

    Returns:
      float: 浴室シャワー水栓における節湯の効果係数 (-)

    """
    return get_f_ss_A(shower_watersaving_A) * get_f_ss_B(shower_watersaving_B)


def get_f_sw(washbowl_watersaving_C, Theta_wtr_d):
    """# 洗面水栓における節湯の効果係数 (1c)

    Args:
      washbowl_watersaving_C(bool): 洗面水栓の水優先吐水機能の有無
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      float: 洗面水栓における節湯の効果係数 (-)

    """
    return get_f_sw_C(washbowl_watersaving_C, Theta_wtr_d)


def get_f_sk_A(kitchen_watersaving_A):
    """# 台所水栓の手元止水機能における節湯の効果係数

    Args:
      kitchen_watersaving_A(ndarray): 台所水栓の手元止水機能の有無

    Returns:
      float: 台所水栓の手元止水機能における節湯の効果係数 (-)

    """
    if kitchen_watersaving_A:
        return get_table_j_1()[0]
    else:
        return get_table_j_1()[1]


def get_f_sk_C(kitchen_watersaving_C, Theta_wtr_d):
    """# 台所水栓の水優先吐水水機能における節湯の効果係数

    Args:
      kitchen_watersaving_C(bool): 台所水栓の手元止水機能の有無
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: 台所水栓の水優先吐水機能における節湯の効果係数 (-)

    """
    f_sk_C_d = np.ones(365)

    if kitchen_watersaving_C:
        f_sk_C_d[Theta_wtr_d > 18] = get_table_j_1()[2]

    return f_sk_C_d

def get_f_ss_A(bathshower_watersaving_A):
    """# 浴室シャワー水栓の手元止水機能における節湯の効果係数

    Args:
      bathshower_watersaving_A(bool): 浴室シャワー水栓の手元止水機能の有無

    Returns:
      float: 浴室シャワー水栓の手元止水機能における節湯の効果係数 (-)

    """
    if bathshower_watersaving_A:
        return get_table_j_1()[5]
    else:
        return get_table_j_1()[6]


def get_f_ss_B(bathshower_watersaving_B):
    """# 浴室シャワー水栓の小流量吐水機能における節湯の効果係数

    Args:
      bathshower_watersaving_B(bool): 浴室シャワー水栓の小流量吐水機能の有無

    Returns:
      float: 浴室シャワー水栓の小流量吐水機能における節湯の効果係数 (-)

    """
    if bathshower_watersaving_B:
        return get_table_j_1()[7]
    else:
        return get_table_j_1()[8]


def get_f_sw_C(washbowl_watersaving_C, Theta_wtr_d):
    """# 洗面水栓の水優先吐水機能における節湯の保温効果係数

    Args:
      washbowl_watersaving_C(bool): 洗面水栓の水優先吐水機能の有無
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: 洗面水栓の水優先吐水機能における節湯の効果係数 (-)

    """
    f_sw_C_d = np.ones(365)

    if washbowl_watersaving_C:
        f_sw_C_d[Theta_wtr_d > 18] = get_table_j_1()[9]

    return f_sw_C_d


def get_f_sp(pipe_diameter):
    """# 配管のヘッダー分岐後の径における節湯の保温効果係数

    Args:
      pipe_diameter(str): ヘッダー分岐後の径

    Returns:
      float: 配管のヘッダー分岐後の径におけるせゆつの保温効果係数 (-)

    """
    if pipe_diameter == 'ヘッダーにより台所水栓・シャワー水栓・洗面水栓に分岐され、かつ分岐後の配管すべての径が13A以下であるもの':
        return get_table_j_1()[12]
    elif pipe_diameter == '上記以外':
        return get_table_j_1()[13]
    else:
        raise ValueError()


def get_f_sb():
    """# 浴槽の保温効果係数

    Args:

    Returns:
      float: 浴槽の保温効果係数

    """
    return get_table_j_1()[14]


def get_table_j_1():
    """表J.1 節湯の効果係数

    Args:

    Returns:
      list: 表J.1 節湯の効果係数

    """
    # 表J.1 節湯の効果係数
    table_j_1 = [
        # f_sk_A
        0.91,
        1.00,
        # f_sk_C
        0.70,
        1.00,
        1.00,
        # f_ss_A
        0.80,
        1.00,
        # f_ss_B
        0.85,
        1.00,
        # f_sw_C
        0.70,
        1.00,
        1.00,
        # f_sp
        0.95,
        1.00,
        # f_sb
        1.00
    ]
    return table_j_1