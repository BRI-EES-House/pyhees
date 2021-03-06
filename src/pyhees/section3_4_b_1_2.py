# ============================================================================
# 第三章 暖冷房負荷と外皮性能
# 第四節 日射熱取得率
# Ver.11（住宅・住戸の外皮性能の計算プログラム Ver.03～2021.4）
# ----------------------------------------------------------------------------
# 付録B 大部分がガラスで構成されている窓等の開口部における取得日射熱補正係数
# ----------------------------------------------------------------------------
# B.1.2 開口部の上部に日除けが設置されていない場合
# ============================================================================

def get_f_H_i_1(region, glass_spec_category):
    """天窓等の屋根又は屋根の直下の天井に設置されている開口部の暖房期の取得日射熱補正係数

    Args:
      region(int): 省エネルギー地域区分
      glass_spec_category(str): ガラスの仕様の区分

    Returns:
      float: 天窓等の屋根又は屋根の直下の天井に設置されている開口部の暖房期の取得日射熱補正係数

    """
    # 表1(a) 天窓等の屋根又は屋根の直下の天井に設置されている開口部の暖房期の取得日射熱補正係数
    table_1_a = [
        (0.90, 0.91, 0.91, 0.91, 0.90, 0.90, 0.90, None),
        (0.85, 0.86, 0.86, 0.87, 0.85, 0.85, 0.85, None),
        (0.83, 0.84, 0.84, 0.85, 0.83, 0.84, 0.83, None),
        (0.85, 0.86, 0.86, 0.87, 0.85, 0.85, 0.85, None),
        (0.82, 0.83, 0.83, 0.84, 0.82, 0.82, 0.82, None),
        (0.82, 0.83, 0.83, 0.84, 0.82, 0.82, 0.82, None),
        (0.80, 0.81, 0.81, 0.82, 0.80, 0.80, 0.80, None)
    ]
    return table_1_a[glass_spec_category - 1][region - 1]


def get_f_C_i_1(region, glass_spec_category):
    """天窓等の屋根又は屋根の直下の天井に設置されている開口部の冷房期の取得日射熱補正係数

    Args:
      region(int): 省エネルギー地域区分
      glass_spec_category(str): ガラスの仕様の区分

    Returns:
      float: 天窓等の屋根又は屋根の直下の天井に設置されている開口部の冷房期の取得日射熱補正係数

    """
    # 表1(b) 天窓等の屋根又は屋根の直下の天井に設置されている開口部の冷房期の取得日射熱補正係数
    table_1_b = [
        (0.93, 0.93, 0.93, 0.94, 0.93, 0.94, 0.94, 0.93),
        (0.90, 0.90, 0.90, 0.91, 0.90, 0.90, 0.91, 0.90),
        (0.88, 0.88, 0.89, 0.89, 0.88, 0.89, 0.89, 0.88),
        (0.89, 0.89, 0.90, 0.90, 0.89, 0.90, 0.90, 0.90),
        (0.87, 0.87, 0.88, 0.88, 0.87, 0.88, 0.88, 0.88),
        (0.87, 0.88, 0.88, 0.89, 0.88, 0.88, 0.89, 0.88),
        (0.86, 0.86, 0.86, 0.87, 0.86, 0.87, 0.87, 0.86)
    ]
    return table_1_b[glass_spec_category - 1][region - 1]


def get_f_H_i_2(region, glass_spec_category, direction):
    """当該開口部の上部に日除けが設置されていない場合の開口部の暖房期の取得日射熱補正係数

    Args:
      region(int): 省エネルギー地域区分
      glass_spec_category(str): ガラスの仕様の区分
      direction(str): 外皮の部位の方位

    Returns:
      float: 当該開口部の上部に日除けが設置されていない場合の開口部の暖房期の取得日射熱補正係数

    """
    return get_table_2(region, glass_spec_category, 'H', direction)


def get_f_C_i_2(region, glass_spec_category, direction):
    """当該開口部の上部に日除けが設置されていない場合の開口部の冷房期の取得日射熱補正係数

    Args:
      region(int): 省エネルギー地域区分
      glass_spec_category(str): ガラスの仕様の区分
      direction(str): 外皮の部位の方位

    Returns:
      float: 当該開口部の上部に日除けが設置されていない場合の開口部の冷房期の取得日射熱補正係数

    """
    return get_table_2(region, glass_spec_category, 'C', direction)


def get_table_2(region, glass_spec_category, H_or_C, direction):
    """当該開口部の上部に日除けが設置されていない場合の開口部の取得日射熱補正係数

    Args:
      region(int): 省エネルギー地域区分
      glass_spec_category(str): ガラスの仕様の区分
      H_or_CS(str): 計算対象
      direction(str): 外皮の部位の方位
      H_or_C: returns: 当該開口部の上部に日除けが設置されていない場合の開口部の取得日射熱補正係数

    Returns:
      float: 当該開口部の上部に日除けが設置されていない場合の開口部の取得日射熱補正係数

    """
    # 表2 当該開口部の上部に日除けが設置されていない場合の開口部の取得日射熱補正係数
    table_2 = [
        (0.853, 0.865, 0.882, 0.864, 0.807, 0.860, 0.880, 0.866),
        (0.862, 0.848, 0.871, 0.892, 0.892, 0.888, 0.869, 0.850),
        (0.807, 0.821, 0.847, 0.820, 0.746, 0.814, 0.844, 0.822),
        (0.818, 0.799, 0.831, 0.858, 0.856, 0.853, 0.828, 0.802),
        (0.791, 0.805, 0.833, 0.802, 0.727, 0.797, 0.830, 0.806),
        (0.803, 0.783, 0.816, 0.844, 0.842, 0.839, 0.813, 0.787),
        (0.805, 0.818, 0.844, 0.816, 0.745, 0.811, 0.841, 0.819),
        (0.816, 0.797, 0.828, 0.854, 0.853, 0.850, 0.825, 0.800),
        (0.776, 0.791, 0.823, 0.789, 0.707, 0.783, 0.820, 0.792),
        (0.789, 0.767, 0.804, 0.834, 0.831, 0.829, 0.800, 0.771),
        (0.781, 0.796, 0.826, 0.793, 0.715, 0.787, 0.823, 0.797),
        (0.793, 0.772, 0.806, 0.836, 0.833, 0.831, 0.803, 0.775),
        (0.761, 0.776, 0.810, 0.772, 0.688, 0.766, 0.806, 0.777),
        (0.773, 0.751, 0.788, 0.820, 0.816, 0.814, 0.785, 0.755),
        (0.857, 0.864, 0.877, 0.858, 0.812, 0.861, 0.878, 0.864),
        (0.860, 0.851, 0.873, 0.888, 0.880, 0.885, 0.874, 0.850),
        (0.812, 0.820, 0.839, 0.814, 0.753, 0.817, 0.841, 0.819),
        (0.815, 0.802, 0.833, 0.853, 0.840, 0.848, 0.835, 0.802),
        (0.796, 0.804, 0.825, 0.796, 0.734, 0.799, 0.827, 0.803),
        (0.801, 0.787, 0.819, 0.840, 0.825, 0.834, 0.821, 0.786),
        (0.810, 0.817, 0.836, 0.810, 0.751, 0.813, 0.838, 0.817),
        (0.814, 0.801, 0.831, 0.850, 0.837, 0.845, 0.832, 0.800),
        (0.782, 0.790, 0.814, 0.783, 0.714, 0.786, 0.816, 0.790),
        (0.786, 0.771, 0.807, 0.829, 0.813, 0.824, 0.809, 0.770),
        (0.787, 0.794, 0.817, 0.787, 0.721, 0.790, 0.820, 0.794),
        (0.790, 0.775, 0.810, 0.831, 0.815, 0.826, 0.811, 0.775),
        (0.767, 0.774, 0.800, 0.766, 0.695, 0.768, 0.803, 0.774),
        (0.771, 0.754, 0.792, 0.815, 0.797, 0.809, 0.794, 0.754),
        (0.853, 0.862, 0.870, 0.853, 0.799, 0.859, 0.883, 0.865),
        (0.862, 0.850, 0.869, 0.885, 0.884, 0.885, 0.871, 0.850),
        (0.807, 0.817, 0.830, 0.806, 0.738, 0.813, 0.849, 0.821),
        (0.818, 0.803, 0.828, 0.850, 0.846, 0.849, 0.831, 0.802),
        (0.791, 0.802, 0.816, 0.788, 0.720, 0.795, 0.835, 0.805),
        (0.804, 0.787, 0.814, 0.836, 0.831, 0.836, 0.816, 0.787),
        (0.805, 0.815, 0.828, 0.803, 0.737, 0.810, 0.846, 0.819),
        (0.816, 0.801, 0.826, 0.847, 0.842, 0.846, 0.828, 0.801),
        (0.777, 0.788, 0.804, 0.774, 0.699, 0.781, 0.825, 0.792),
        (0.790, 0.772, 0.801, 0.825, 0.819, 0.825, 0.804, 0.771),
        (0.782, 0.792, 0.808, 0.778, 0.707, 0.786, 0.828, 0.796),
        (0.793, 0.776, 0.804, 0.827, 0.821, 0.827, 0.807, 0.776),
        (0.761, 0.772, 0.790, 0.757, 0.681, 0.764, 0.812, 0.776),
        (0.774, 0.756, 0.786, 0.811, 0.803, 0.810, 0.789, 0.755),
        (0.852, 0.861, 0.881, 0.853, 0.784, 0.850, 0.876, 0.861),
        (0.861, 0.846, 0.874, 0.883, 0.874, 0.882, 0.872, 0.845),
        (0.806, 0.816, 0.845, 0.805, 0.721, 0.802, 0.839, 0.816),
        (0.816, 0.797, 0.834, 0.846, 0.832, 0.846, 0.833, 0.796),
        (0.790, 0.800, 0.831, 0.787, 0.704, 0.785, 0.824, 0.800),
        (0.802, 0.782, 0.819, 0.833, 0.817, 0.832, 0.818, 0.780),
        (0.804, 0.813, 0.842, 0.802, 0.721, 0.799, 0.836, 0.813),
        (0.814, 0.796, 0.831, 0.843, 0.829, 0.843, 0.830, 0.794),
        (0.776, 0.786, 0.820, 0.772, 0.683, 0.770, 0.813, 0.786),
        (0.787, 0.766, 0.807, 0.822, 0.804, 0.821, 0.806, 0.764),
        (0.781, 0.791, 0.823, 0.777, 0.691, 0.775, 0.817, 0.790),
        (0.791, 0.770, 0.810, 0.824, 0.807, 0.824, 0.809, 0.769),
        (0.761, 0.770, 0.806, 0.754, 0.665, 0.752, 0.799, 0.770),
        (0.772, 0.749, 0.792, 0.807, 0.787, 0.807, 0.791, 0.747),
        (0.860, 0.863, 0.874, 0.854, 0.807, 0.858, 0.875, 0.862),
        (0.867, 0.838, 0.874, 0.894, 0.894, 0.891, 0.871, 0.840),
        (0.816, 0.820, 0.835, 0.807, 0.749, 0.813, 0.837, 0.817),
        (0.823, 0.787, 0.834, 0.861, 0.858, 0.857, 0.830, 0.789),
        (0.800, 0.804, 0.820, 0.790, 0.732, 0.795, 0.822, 0.801),
        (0.809, 0.771, 0.819, 0.848, 0.842, 0.845, 0.815, 0.773),
        (0.813, 0.817, 0.832, 0.804, 0.749, 0.809, 0.834, 0.815),
        (0.821, 0.786, 0.831, 0.858, 0.854, 0.854, 0.827, 0.788),
        (0.786, 0.791, 0.809, 0.775, 0.713, 0.782, 0.811, 0.788),
        (0.795, 0.754, 0.807, 0.839, 0.832, 0.835, 0.803, 0.756),
        (0.791, 0.795, 0.812, 0.780, 0.720, 0.786, 0.815, 0.792),
        (0.798, 0.759, 0.810, 0.841, 0.833, 0.837, 0.806, 0.761),
        (0.771, 0.775, 0.794, 0.758, 0.696, 0.765, 0.797, 0.772),
        (0.779, 0.737, 0.791, 0.826, 0.816, 0.821, 0.787, 0.740),
        (0.847, 0.862, 0.880, 0.852, 0.795, 0.852, 0.880, 0.864),
        (0.870, 0.839, 0.874, 0.896, 0.889, 0.885, 0.874, 0.844),
        (0.800, 0.818, 0.843, 0.804, 0.738, 0.804, 0.843, 0.820),
        (0.827, 0.788, 0.834, 0.865, 0.851, 0.850, 0.833, 0.794),
        (0.784, 0.802, 0.829, 0.786, 0.721, 0.786, 0.829, 0.805),
        (0.813, 0.772, 0.819, 0.852, 0.836, 0.837, 0.818, 0.778),
        (0.798, 0.816, 0.840, 0.801, 0.737, 0.801, 0.840, 0.818),
        (0.825, 0.787, 0.831, 0.862, 0.848, 0.847, 0.830, 0.793),
        (0.769, 0.789, 0.818, 0.771, 0.702, 0.771, 0.818, 0.791),
        (0.799, 0.755, 0.806, 0.843, 0.824, 0.827, 0.806, 0.762),
        (0.774, 0.793, 0.821, 0.776, 0.709, 0.776, 0.821, 0.796),
        (0.803, 0.760, 0.809, 0.845, 0.826, 0.829, 0.809, 0.767),
        (0.754, 0.773, 0.804, 0.754, 0.685, 0.754, 0.804, 0.776),
        (0.784, 0.739, 0.791, 0.830, 0.808, 0.813, 0.790, 0.745),
        (0.838, 0.861, 0.881, 0.849, 0.788, 0.847, 0.880, 0.862),
        (0.873, 0.833, 0.868, 0.892, 0.896, 0.894, 0.870, 0.834),
        (0.788, 0.817, 0.845, 0.800, 0.730, 0.798, 0.843, 0.818),
        (0.831, 0.780, 0.827, 0.859, 0.860, 0.861, 0.829, 0.780),
        (0.772, 0.801, 0.831, 0.782, 0.713, 0.780, 0.829, 0.802),
        (0.817, 0.764, 0.812, 0.847, 0.844, 0.849, 0.814, 0.764),
        (0.787, 0.814, 0.842, 0.797, 0.729, 0.795, 0.840, 0.815),
        (0.829, 0.779, 0.824, 0.856, 0.856, 0.858, 0.826, 0.779),
        (0.757, 0.787, 0.821, 0.767, 0.694, 0.764, 0.818, 0.788),
        (0.803, 0.746, 0.799, 0.837, 0.833, 0.839, 0.801, 0.746),
        (0.762, 0.792, 0.824, 0.772, 0.701, 0.770, 0.822, 0.793),
        (0.807, 0.752, 0.802, 0.839, 0.835, 0.841, 0.804, 0.752),
        (0.741, 0.772, 0.808, 0.749, 0.677, 0.747, 0.805, 0.772),
        (0.788, 0.729, 0.783, 0.824, 0.816, 0.826, 0.785, 0.729),
        (0.848, 0.857, 0.877, 0.860, 0.824, 0.858, 0.876, 0.859),
        (0.801, 0.811, 0.840, 0.816, 0.773, 0.813, 0.839, 0.814),
        (0.786, 0.795, 0.825, 0.799, 0.755, 0.796, 0.825, 0.798),
        (0.799, 0.809, 0.837, 0.813, 0.771, 0.810, 0.836, 0.812),
        (0.771, 0.780, 0.815, 0.786, 0.739, 0.782, 0.814, 0.784),
        (0.776, 0.785, 0.818, 0.790, 0.745, 0.786, 0.817, 0.789),
        (0.756, 0.764, 0.801, 0.770, 0.722, 0.766, 0.800, 0.768),
    ]

    # 開口部の面する方位からインデックスへ
    dir_dic = {
        '北': 0,
        '北東': 1,
        '東': 2,
        '南東': 3,
        '南': 4,
        '南西': 5,
        '西': 6,
        '北西': 7,
    }
    dir_index = dir_dic[direction]

    if glass_spec_category not in [1, 2, 3, 4, 5, 6, 7]:
        raise ValueError(glass_spec_category)

    if region not in [1, 2, 3, 4, 5, 6, 7, 8]:
        raise ValueError(region)

    region_index = (region - 1) * 14
    glass_index = (glass_spec_category - 1) * 2

    if H_or_C == 'C':
        HC_index = 0
    elif H_or_C == 'H':
        HC_index = 1
    else:
        raise ValueError(H_or_C)

    index = region_index + glass_index + HC_index

    return table_2[index][dir_index]
