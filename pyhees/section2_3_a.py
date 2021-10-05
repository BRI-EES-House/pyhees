# 付録 A 暖冷房負荷と外皮性能の算定に係る設定

# A.1 地域の区分

# 地域の区分
def get_region(region):
    """付録 A 暖冷房負荷と外皮性能の算定に係る設定
    A.1 地域の区分
    
    :param region: 省エネルギー地域区分
    :type region: int
    :return: 省エネルギー地域区分
    :rtype: int
    """
    return region


# A.2 床面積の合計・主たる居室の面積・その他の居室の面積

# 床面積の合計・主たる居室の面積・その他の居室の面積
def get_A(A_A, A_MR, A_OR):
    """ 付録 A 暖冷房負荷と外皮性能の算定に係る設定
    A.2 床面積の合計・主たる居室の面積・その他の居室の面積
    
    :param A_A: 床面積の合計
    :type A_A: float
    :param A_MR: 主たる居室の面積
    :type A_MR: float
    :param A_OR: その他の居室の面積
    :type A_OR: float
    :return: 床面積の合計, 主たる居室の面積, その他の居室の面積
    :rtype: tuple
    """
    return A_A, A_MR, A_OR


# A.3 外皮の部位の面積の合計

def get_env_A(env_A):
    """ 付録 A 暖冷房負荷と外皮性能の算定に係る設定
    A.3 外皮の部位の面積の合計

    :param env_A: 外皮の部位の面積の合計
    :type env_A: float
    :return: 外皮の部位の面積の合計
    :rtype: float
    """
    return env_A


# A.4 外皮平均熱貫流率・平均日射熱取得率
def get_U_A(tatekata, region):
    """ 付録 A 暖冷房負荷と外皮性能の算定に係る設定
    A.4 外皮平均熱貫流率・平均日射熱取得率
    
    :param tatekata: 建て方
    :type tatekata: str
    :param region: 省エネルギー地域区分
    :type region: int
    :raises ValueError: 建て方が 「戸建住宅」または「共同住宅」以外の場合に発生する
    :return: 表A1に該当する外皮平均熱貫流率
    :rtype: float
    """
    table_a_1 = get_table_a_1()
    if tatekata == '戸建住宅':
        return table_a_1[0][region - 1]
    elif tatekata == '共同住宅':
        return table_a_1[1][region - 1]
    else:
        raise ValueError(tatekata)


def get_etr_A_H(tatekata, region):
    """ 付録 A 暖冷房負荷と外皮性能の算定に係る設定
    A.4 外皮平均熱貫流率・平均日射熱取得率
    
    :param tatekata: 建て方
    :type tatekata: str
    :param region: 省エネルギー地域区分
    :type region: int
    :raises ValueError: 建て方が 「戸建住宅」または「共同住宅」以外の場合に発生する
    :return: 表A1に該当する平均日射熱取得率（暖房）
    :rtype: float
    """
    table_a_1 = get_table_a_1()
    if tatekata == '戸建住宅':
        return table_a_1[2][region - 1]
    elif tatekata == '共同住宅':
        return table_a_1[3][region - 1]
    else:
        raise ValueError(tatekata)


def get_etr_A_C(tatekata, region):
    """ 付録 A 暖冷房負荷と外皮性能の算定に係る設定
    A.4 外皮平均熱貫流率・平均日射熱取得率
    
    :param tatekata: 建て方
    :type tatekata: str
    :param region: 省エネルギー地域区分
    :type region: int
    :raises ValueError: 建て方が 「戸建住宅」または「共同住宅」以外の場合に発生する
    :return: 表A1に該当する平均日射熱取得率（冷房）
    :rtype: float
    """
    table_a_1 = get_table_a_1()
    if tatekata == '戸建住宅':
        return table_a_1[4][region - 1]
    elif tatekata == '共同住宅':
        return table_a_1[5][region - 1]
    else:
        raise ValueError(tatekata)

def get_table_a_1():
    """付録 A 暖冷房負荷と外皮性能の算定に係る設定
    A.4 外皮平均熱貫流率・平均日射熱取得率
    建て方・地域区分に応じた外皮平均熱貫流率・平均日射熱取得率を返す
    
    :return: 表A1
    :rtype: list
    """
    table_a_1 = [
        (0.46, 0.46, 0.56, 0.75, 0.87, 0.87, 0.87, 3.32),
        (0.41, 0.41, 0.44, 0.69, 0.75, 0.75, 0.75, 1.73),
        (2.5, 2.3, 2.7, 3.7, 4.5, 4.3, 4.6, None),
        (1.5, 1.3, 1.5, 1.8, 2.1, 2.0, 2.1, None),
        (1.9, 1.9, 2.0, 2.7, 3.0, 2.8, 2.7, 6.7),
        (1.1, 1.1, 1.1, 1.4, 1.5, 1.4, 1.3, 2.8)
    ]
    return table_a_1


# A.5 通風の利用

# 通風の利用は、主たる居室・その他の居室ともになしとする。
def get_NV():
    """付録 A 暖冷房負荷と外皮性能の算定に係る設定
    A.5 通風の利用
    通風の利用は、主たる居室・その他の居室ともになしとする。

    :return: 主たる居室・その他の居室における通風の利用
    :rtype: tuple
    """
    return 0, 0


# A.6 蓄熱の利用

def get_thermal_storage():
    """付録 A 暖冷房負荷と外皮性能の算定に係る設定
    A.6 蓄熱の利用
    
    :return: 蓄熱の利用
    :rtype: bool
    """
    return False


# A.7 床下空間を経由して外気を導入する換気方法の採用

def get_underfloor_ventilation():
    """付録 A 暖冷房負荷と外皮性能の算定に係る設定
    A.7 床下空間を経由して外気を導入する換気方法の採用
    
    :return: 床下空間を経由して外気を導入する換気方法の採用
    :rtype: bool
    """
    return False


# A.8 熱交換型換気の採用

def get_heatexchanger():
    """付録 A 暖冷房負荷と外皮性能の算定に係る設定
    A.8 熱交換型換気の採用

    :return: 熱交換型換気の採用
    :rtype: bool
    """
    return False
