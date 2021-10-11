# ============================================================================
# 付録 B 給湯機を設置しない場合に評価において想定する機器の種類と仕様
# ============================================================================

import copy

def get_virtual_hotwater(region, HW):
    """

    Args:
      region(int): 省エネルギー地域区分
      HW(dict): 給湯機の仕様

    Returns:
      dict: 給湯機の仕様

    """
    if HW is None:
        return None

    # その他または設置しない場合
    if HW['hw_type'] in ['その他', '設置しない', '不明']:
        default = get_default_hw_type(region)
        virt = copy.deepcopy(HW)
        virt['hw_type'] = default[0]
        virt['e_rtd'] = default[1]
        # ふろ機能の種類は「ふろ給湯機（追焚あり）」とする
        virt['bath_function'] = "ふろ給湯機(追焚あり)"
        return virt
    else:
        return HW


# 給湯機を設置しない場合に評価において想定する機器の種類と仕様
def get_default_hw_type(region):
    """

    Args:
      region: 省エネルギー地域区分

    Returns:
      給湯機を設置しない場合に評価において想定する機器の種類と効率

    """
    return get_table_b_1()[region - 1]

def get_table_b_1():
    """表 B.1 給湯機を設置しない場合の評価において想定する機器

    Args:

    Returns:
      list: 給湯機を設置しない場合の評価において想定する機器

    """
    table_b_1 = [
        ('石油従来型給湯機', 0.813),
        ('石油従来型給湯機', 0.813),
        ('石油従来型給湯機', 0.813),
        ('石油従来型給湯機', 0.813),
        ('ガス従来型給湯機', 0.782),
        ('ガス従来型給湯機', 0.782),
        ('ガス従来型給湯機', 0.782),
        ('ガス従来型給湯機', 0.782),
    ]

    return table_b_1


