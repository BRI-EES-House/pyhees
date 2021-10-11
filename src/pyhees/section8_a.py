# ============================================================================
# 付録A コージェネレーション設備の仕様
# ============================================================================

def get_value(CG_category, index):
    """

    Args:
      CG_category(str): コージェネレーション設備の種類
      index(int): 表A.1における番号

    Returns:
      bool: 表A.1から読み取った値

    """
    column_index = {
        'GEC1': 0,
        'GEC2': 1,
        'PEFC1': 2,
        'PEFC2': 3,
        'PEFC3': 4,
        'PEFC4': 5,
        'PEFC5': 6,
        'PEFC6': 7,
        'SOFC1': 8,
        'SOFC2': 9
    }
    if CG_category in column_index:
        return get_table_a_1()[index - 1][column_index[CG_category]]
    else:
        raise ValueError(CG_category)


def get_exhaust(CG_category):
    """1. 温水暖房への排熱利用

    Args:
      CG_category(str): コージェネレーション設備の種類 コージェネレーション設備の種類

    Returns:
      bool: 温水暖房への排熱利用

    """
    return get_value(CG_category, 1)


def get_exhaust_priority(CG_category):
    """2. 排熱利用方式 (温水暖房への排熱利用がある場合の排熱の優先先)

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      str: 排熱利用方式

    """
    return get_value(CG_category, 2)


def get_type_BB_DHW(CG_category):
    """3. バックアップボイラー(給湯)の熱源種別

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      str: バックアップボイラー（給湯）の熱源種別

    """
    return get_value(CG_category, 3)


def get_e_rtd_BB_DHW(CG_category):
    """4. バックアップボイラー(給湯)の給湯機の効率

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      float: バックアップボイラー(給湯)の給湯機の効率

    """
    return get_value(CG_category, 4)


def get_type_BB_HWH(CG_category):
    """5. バックアップボイラー(温水暖房)の種類

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      str: バックアップボイラー(温水暖房)の種類

    """
    return get_value(CG_category, 5)


def get_e_rtd_BB_HWH(CG_category):
    """6. バックアップボイラー(温水暖房)の定格効率

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      float: バックアップボイラー(温水暖房)の定格効率

    """
    return get_value(CG_category, 6)


def get_q_rtd_BB_HWH(CG_category):
    """7. バックアップボイラー(温水暖房)の定格能力 (W)

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      float: バックアップボイラー(温水暖房)の定格能力

    """
    return get_value(CG_category, 7)


def get_r_DHW_gen_PU_d(CG_category):
    """8. 発電ユニットの給湯排熱利用率

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      float: 発電ユニットの給湯排熱利用率

    """
    return get_value(CG_category, 8)


def get_r_HWH_gen_PU_d(CG_category):
    """9. 発電ユニットの温水暖房排熱利用率

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      float: 発電ユニットの温水暖房排熱利用率

    """
    return get_value(CG_category, 9)


def get_PU_type(CG_category):
    """10. 発電ユニットの発電方式

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      str: 発電ユニットの発電方式

    """
    return get_value(CG_category, 10)


def get_param_E_E_gen_PU_EVt_d(CG_category):
    """11-15. 発電ユニットの発電量推定時の仮想発電量のパラメータ a_PU, a_DHW, a_HWH, b, c

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      dict: 発電ユニットの発電量推定時の仮想発電量のパラメータ a_PU, a_DHW, a_HWH, b, c

    """
    return {
        'a_PU': get_value(CG_category, 11),
        'a_DHW': get_value(CG_category, 12),
        'a_HWH': get_value(CG_category, 13),
        'b': get_value(CG_category, 14),
        'c': get_value(CG_category, 15)
    }


def get_param_E_F_PU_HVt_d(CG_category):
    """16-17. 発電ユニットの排熱量推定時の仮想燃料消費量を求める係数 a_DHW, a_HWH

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      dict: 発電ユニットの排熱量推定時の仮想燃料消費量を求める係数 a_DHW, a_HWH

    """
    return {
        'a_DHW': get_value(CG_category, 16),
        'a_HWH': get_value(CG_category, 17)
    }


def get_param_r_H_gen_PU_HVt_d(CG_category):
    """18-20. 発電ユニットの排熱量推定時の仮想排熱量の上限比を求める係数 a_DHW, a_HWH, b

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      dict: 発電ユニットの排熱量推定時の仮想排熱量の上限比を求める係数 a_DHW, a_HWH, b

    """
    return {
        'a_DHW': get_value(CG_category, 18),
        'a_HWH': get_value(CG_category, 19),
        'b': get_value(CG_category, 20)
    }


def get_param_e_E_PU_d(CG_category):
    """21-26. 発電ユニットの日平均発電効率を求める係数 a_PU, a_DHW, a_HWH, b, 上限値, 下限値

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      dict: 発電ユニットの日平均発電効率を求める係数 a_PU, a_DHW, a_HWH, b, 上限値, 下限値

    """
    return {
        'a_PU': get_value(CG_category, 21),
        'a_DHW': get_value(CG_category, 22),
        'a_HWH': get_value(CG_category, 23),
        'b': get_value(CG_category, 24),
        'e_E_PU_d_max': get_value(CG_category, 25),
        'e_E_PU_d_min': get_value(CG_category, 26)
    }


def get_param_e_H_PU_d(CG_category):
    """27-32. 発電ユニットの日平均排熱効率を求める係数 a_PU, a_DHW, a_HWH, b, 上限値, 下限値

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      dict: 発電ユニットの日平均排熱効率を求める係数 a_PU, a_DHW, a_HWH, b, 上限値, 下限値

    """
    return {
        'a_PU': get_value(CG_category, 27),
        'a_DHW': get_value(CG_category, 28),
        'a_HWH': get_value(CG_category, 29),
        'b': get_value(CG_category, 30),
        'e_H_PU_d_max': get_value(CG_category, 31),
        'e_H_PU_d_min': get_value(CG_category, 32)
    }


def get_P_rtd_PU(CG_category):
    """33. 定格発電出力 (W)

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      float: 定格発電出力 (W)

    """
    return get_value(CG_category, 33)


def get_P_TU_aux_DHW(CG_category):
    """34. タンクユニットの補機消費電力 (給湯)

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      float: タンクユニットの補機消費電力 (給湯)

    """
    return get_value(CG_category, 34)


def get_P_TU_aux_HWH(CG_category):
    """35. タンクユニットの補機消費電力 (温水暖房)

    Args:
      CG_category(str): コージェネレーション設備の種類

    Returns:
      float: タンクユニットの補機消費電力 (温水暖房)

    """
    return get_value(CG_category, 35)


def get_table_a_1():
    """表A.1　コージェネレーション設備の仕様

    Args:

    Returns:
      list: 表A.1　コージェネレーション設備の仕様

    """
    table_a_1 = [
        (True, True, True, True, True, True, True, False, False, False),
        ('給湯優先', '給湯優先', '給湯優先', '給湯優先', '給湯優先', '給湯優先', '給湯優先', None, None, None),
        ('ガス', 'ガス', 'ガス', 'ガス', 'ガス', 'ガス', 'ガス', 'ガス', 'ガス', 'ガス'),
        (0.782, 0.782, 0.905, 0.782, 0.905, 0.905, 0.782, 0.905, 0.905, 0.905),
        ('ガス従来型', 'ガス従来型', 'ガス潜熱回収型', 'ガス従来型', 'ガス潜熱回収型', 'ガス潜熱回収型', 'ガス従来型', 'ガス潜熱回収型', 'ガス潜熱回収型', 'ガス潜熱回収型'),

        (0.82, 0.82, 0.87, 0.82, 0.87, 0.87, 0.82, 0.87, 0.87, 0.87),
        (17400, 17400, 17400, 17400, 17400, 17400, 17400, 17400, 17400, 17400),
        (0.7494, 0.7520, 0.9118, 0.7525, 0.9711, 0.7290, 0.9654, 0.8941, 0.7227, 0.6885),
        (0.7758, 0.6301, 0.9118, 0.0000, 0.9538, 0.0000, 0.0000, None, None, None),
        ('熱主', '熱主', '熱主', '熱主', '熱主', '熱主', '熱主', '熱主', '電主', '電主'),

        (0.0000, 0.0000, 1.2248, 1.3570, 1.1732, 1.1406, 1.2469, 0.8546, 1.1175, 1.1262),
        (0.1398, 0.1649, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000),
        (0.1398, 0.1649, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000),
        (7.7827, 7.8506, -22.1324, -19.2214, -11.3125, -8.3893, -14.9213, -5.5854, -6.6385, -6.5572),
        (0.6925, 0.8896, 0.9686, 0.9950, 0.9327, 0.9727, 0.9950, 0.8511, 0.9950, 0.9846),

        (1, 1, 1, 1, 1, 1, 1, 1, None, None),
        (0, 1, 1, 0, 0, 0, 0, 0, None, None),
        (-0.0075, 0.0124, 0.0000, 0.0217, 0.0230, 0.000, 0.0000, 0.0177, None, None),
        (-0.0075, 0.0124, 0.0000, 0.0000, 0.0230, 0.0000, 0.0000, 0.0000, None, None),
        (1.4847, 0.7572, 1.1437, 0.3489, 0.2266, 1.3160, 1.0526, 0.6022, None, None),

        (0.000000, 0.000000, 0.000000, 0.003000, 0.000000, 0.002138, 0.003096, 0.000000, 0.003600, 0.005800),
        (-0.000034, -0.000100, 0.001000, 0.000000, 0.000200, 0.000000, 0.000000, 0.000402, 0.000000, 0.000000),
        (-0.000034, -0.000100, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000),
        (0.1779, 0.2073, 0.2640, 0.1473, 0.3181, 0.2246, 0.1483, 0.3111, 0.1951, 0.1611),
        (0.2069, 0.2401, 0.3438, 0.3109, 0.3342, 0.3217, 0.3193, 0.3396, 0.3925, 0.4290),

        (0.1499, 0.1659, 0.2315, 0.2159, 0.3124, 0.2633, 0.2301, 0.2959, 0.3092, 0.3503),
        (0.000000, 0.000000, 0.000900, -0.000000, 0.004100, -0.001039, 0.000000, 0.003019, 0.000500, 0.002800),
        (0.000342, 0.000400, 0.000000, 0.000000, 0.000000, 0.000000, 0.000452, 0.000000, 0.000000, 0.000000),
        (0.000342, 0.000400, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000),
        (0.5787, 0.5950, 0.3367, 0.4179, 0.1877, 0.4301, 0.3017, 0.2496, 0.3135, 0.1854),

        (0.6811, 0.7030, 0.4101, 0.4429, 0.3899, 0.4228, 0.3716, 0.4059, 0.3539, 0.3179),
        (0.5576, 0.5688, 0.3051, 0.3963, 0.3166, 0.3524, 0.2803, 0.3351, 0.3169, 0.2756),
        (1000, 1000, 1000, 700, 750, 700, 700, 750, 700, 700),
        (15.1, 15.7, 9.7, 15.4, 13.9, 12.1, 15.4, 11.2, 17.1, 11.8),
        (132.1, 111.7, 63.6, 130.0, 128.3, 129.8, 138.1, None, None, None)
    ]
    return table_a_1
