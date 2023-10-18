# ============================================================================
# 10. 仕様基準又は誘導仕様基準により外皮性能を評価する方法
# ============================================================================


# ============================================================================
# 10.1 外皮平均熱貫流率ならびに暖房期の平均日射熱取得率及び冷房期の平均日射熱取得率
# ============================================================================

def get_U_A(env_standard, tatekata, region):
    """外皮平均熱貫流率 を表6 から取得する関数

    Args:
        env_standard(str): 適応する外皮基準
        tatekata(str): 建て方
        region(int): 省エネルギー地域区分

    Returns:
        float: 外皮平均熱貫流率 (W/m2K)
    """
    index = get_index_of_table_6(env_standard, tatekata, region)
    return get_table_6()[index][0]


def get_eta_A_H(env_standard, tatekata, region):
    """暖房期の平均日射熱取得率 を表6 から取得する関数

    Args:
        env_standard(str): 適応する外皮基準
        tatekata(str): 建て方
        region(int): 省エネルギー地域区分

    Returns:
        float: 暖房期の平均日射熱取得率 (-)
    """
    index = get_index_of_table_6(env_standard, tatekata, region)
    return get_table_6()[index][1]


def get_eta_A_C(env_standard, tatekata, region):
    """冷房期の平均日射熱取得率 を表6 から取得する関数

    Args:
        env_standard(str): 適応する外皮基準
        tatekata(str): 建て方
        region(int): 省エネルギー地域区分

    Returns:
        float: 冷房期の平均日射熱取得率 (-)
    """
    index = get_index_of_table_6(env_standard, tatekata, region)
    return get_table_6()[index][2]


def get_index_of_table_6(env_standard, tatekata, region):
    """表6における行番号を取得する関数

    Args:
        env_standard(str): 適応する外皮基準
        tatekata(str): 建て方
        region(int): 省エネルギー地域区分

    Returns:
        int: 表6における行番号
    """
    if env_standard == "仕様基準により外皮性能を評価する方法":
        if tatekata == "戸建住宅":
            return region - 1
        elif tatekata == "共同住宅":
            return  8 + region - 1
        else:
            raise ValueError(tatekata)
    elif env_standard == "誘導仕様基準により外皮性能を評価する方法":
        if tatekata == "戸建住宅":
            return 16 + region - 1
        elif tatekata == "共同住宅":
            return 24 + region - 1
        else:
            raise ValueError(tatekata)
    else:
        raise ValueError(env_standard)
    

def get_table_6():
    """表6. 仕様基準又は誘導仕様基準により外皮性能を評価する場の外皮平均熱貫流率および暖房期の平均日射熱取得率及び冷房期の平均日射熱取得率 を取得する関数

    Returns:
        list: 表6. 仕様基準又は誘導仕様基準により外皮性能を評価する場の外皮平均熱貫流率および暖房期の平均日射熱取得率及び冷房期の平均日射熱取得率
    """
    return [
        (0.46, 2.5, 1.9),
        (0.46, 2.3, 1.9),
        (0.56, 2.7, 2.0),
        (0.75, 3.7, 2.7),
        (0.87, 4.5, 3.0),
        (0.87, 4.3, 2.8),
        (0.87, 4.6, 2.7),
        (3.32, None, 6.7),
        (0.39, 1.4, 0.9),
        (0.39, 1.3, 1.0),
        (0.46, 1.5, 1.1),
        (0.62, 1.6, 1.2),
        (0.72, 2.2, 1.5),
        (0.72, 2.1, 1.4),
        (0.72, 2.2, 1.4),
        (1.60, None, 2.5),
        (0.40, 2.1, 1.3),
        (0.40, 1.9, 1.3),
        (0.50, 2.1, 1.4),
        (0.60, 2.6, 1.7),
        (0.60, 3.1, 1.8),
        (0.60, 3.0, 1.7),
        (0.60, 3.2, 1.6),
        (3.32, None, 6.7),
        (0.34, 1.3, 0.9),
        (0.34, 1.2, 0.9),
        (0.42, 1.4, 1.0),
        (0.50, 1.5, 1.1),
        (0.50, 1.7, 1.2),
        (0.50, 1.7, 1.1),
        (0.50, 1.7, 1.1),
        (1.60, None, 2.5),
    ]


# ============================================================================
# 10.1 外皮平均熱貫流率ならびに暖房期の平均日射熱取得率及び冷房期の平均日射熱取得率
# ============================================================================
def get_r_env(A_dash_env, A_dash_A):
    """床面積の合計に対する外皮の部位の面積の合計の比  (16)

    Args:
      A_dash_env(float): 標準住戸における外皮の部位の面積の合計 (m2)
      A_dash_A(float): 標準住戸における床面積の合計 (m2)

    Returns:
      float: 床面積の合計に対する外皮の部位の面積の合計の比 (-)

    """

    return A_dash_env / A_dash_A


def get_A_dash_env(tatekata):
    """標準住戸における外皮の部位の面積の合計 (m2)

    Args:
      tatekata(str): 建て方

    Returns:
      float: 標準住戸における外皮の部位の面積の合計 (m2)

    """
    if tatekata == "戸建住宅":
        return get_table_7()[0][0]
    elif tatekata == "共同住宅":
        return get_table_7()[1][0]
    else:
        raise ValueError(tatekata)
        


def get_A_dash_A(tatekata):
    """床面積の合計 (m2)

    Args:
      tatekata(str): 建て方

    Returns:
      float: 床面積の合計 (m2)

    """
    if tatekata == "戸建住宅":
        return get_table_7()[0][1]
    elif tatekata == "共同住宅":
        return get_table_7()[1][1]
    else:
        raise ValueError(tatekata)


def get_table_7():
    """表7. 仕様基準又は誘導仕様基準により外皮性能を評価する場の標準住戸における外皮の部位の面積の合計及び床面積 を取得する関数

    Returns:
        list: 表7. 仕様基準又は誘導仕様基準により外皮性能を評価する場の標準住戸における外皮の部位の面積の合計及び床面積
    """
    return [
        (307.51, 120.08),
        (238.22, 70.00),
    ]