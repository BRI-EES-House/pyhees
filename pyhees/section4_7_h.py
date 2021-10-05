# ============================================================================
# 付録 H 温水暖房用熱源機の最大能力
# ============================================================================

from pyhees.section3_1 import get_A_HCZ_i

# ============================================================================
# H.2 温水暖房用熱源機の最大能力
# ============================================================================

def calc_q_max_hs(region, A_A, A_MR, A_OR, mode_MR, mode_OR, has_MR_hwh, has_OR_hwh):
    """温水暖房用熱源機の最大能力 (1)

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      mode_MR(str): 主たる居室の運転モード 'い', 'ろ', 'は'
      mode_OR(str): その他の居室の運転モード 'い', 'ろ', 'は'
      has_MR_hwh(bool): 温水暖房の放熱器を主たる居室に設置する場合はTrue
      has_MR_hwh: 温水暖房の放熱器を主たる居室に設置する場合はTrue
      has_OR_hwh: returns: 温水暖房用熱源機の最大能力 (W)

    Returns:
      float: 温水暖房用熱源機の最大能力 (W)

    """

    # 単位面積当たりの必要暖房能力
    q_rq_H = get_q_rq_H(region, has_MR_hwh, has_OR_hwh)

    # 外気温度補正係数
    f_cT = get_f_cT()

    # 間歇運転能力補正係数
    f_cI = get_f_cI(mode_MR, mode_OR, has_MR_hwh, has_OR_hwh)

    # 暖冷房区画の床面積(温水暖房により暖 房される暖冷房区画のみを積算する)
    A_HCZ_hs = 0
    if has_MR_hwh:
        A_HCZ_hs = get_A_HCZ_i(1, A_A, A_MR, A_OR)
    if has_OR_hwh:
        A_HCZ_hs = A_HCZ_hs + sum([get_A_HCZ_i(i, A_A, A_MR, A_OR) for i in range(2, 6)])

    return q_rq_H * A_HCZ_hs * f_cT * f_cI


def get_q_rq_H(region, has_MR_hwh, has_OR_hwh):
    """単位面積当たりの必要暖房能力 (W/m2)

    Args:
      region(int): 省エネルギー地域区分
      has_MR_hwh(bool): 温水暖房の放熱器を主たる居室に設置する場合はTrue
      has_OR_hwh(bool): 温水暖房の放熱器をその他の居室に設置する場合はTrue

    Returns:
      float: 単位面積当たりの必要暖房能力 (W/m2)

    """

    if has_MR_hwh and has_OR_hwh:
        return get_table_h_3()[region - 1][0]
    elif has_MR_hwh:
        return get_table_h_3()[region - 1][1]
    elif has_OR_hwh:
        return get_table_h_3()[region - 1][2]
    else:
        raise ValueError('温水暖房の放熱器を主たる居室にもその他の居室にも設置しない場合の単位面積当たりの必要暖房能力は定義されません。')


def get_f_cT():
    """外気温度補正係数

    Args:

    Returns:
      float: 外気温度補正係数

    """

    return 1.05


def get_f_cI(mode_MR, mode_OR, has_MR_hwh, has_OR_hwh):
    """間歇運転能力補正係数

    Args:
      mode_MR(str): 主たる居室の運転方法 (連続運転|間歇運転)
      mode_OR(str): その他の居室の運転方法 (連続運転|間歇運転)
      has_MR_hwh(bool): 温水暖房の放熱器を主たる居室に設置する場合はTrue
      has_OR_hwh(bool): 温水暖房の放熱器をその他の居室に設置する場合はTrue

    Returns:
      float: 間歇運転能力補正係数

    """
    def normalize_mode(s):
        """

        Args:
          s: 

        Returns:

        """
        if s == 'は':
            return '間歇運転'
        if s == 'ろ':
            return '連続運転'
        return s

    mode_MR = normalize_mode(mode_MR)
    mode_OR = normalize_mode(mode_OR)

    if has_MR_hwh and has_OR_hwh:
        if mode_MR == '連続運転':
            if mode_OR == '連続運転':
                return get_table_h_4()[0]
            elif mode_OR == '間歇運転':
                return get_table_h_4()[1]
            else:
                raise ValueError(mode_OR)
        elif mode_MR == '間歇運転':
            if mode_OR == '連続運転':
                return get_table_h_4()[2]
            elif mode_OR == '間歇運転':
                return get_table_h_4()[3]
            else:
                raise ValueError(mode_MR)
        else:
            raise ValueError(mode_MR)
    elif has_MR_hwh:
        if mode_MR == '連続運転':
            return get_table_h_4()[4]
        elif mode_MR == '間歇運転':
            return get_table_h_4()[5]
        else:
            raise ValueError(mode_MR)
    elif has_OR_hwh:
        if mode_OR == '連続運転':
            return get_table_h_4()[6]
        elif mode_OR == '間歇運転':
            return get_table_h_4()[7]
        else:
            raise ValueError(mode_OR)


def get_table_h_3():
    """表 H.3 単位面積当たりの必要暖房能力

    Args:

    Returns:
      list: 表 H.3 単位面積当たりの必要暖房能力

    """
    table_h_3 = [
        (90.02, 139.26, 62.28),
        (77.81, 120.65, 53.26),
        (73.86, 111.32, 53.81),
        (77.74, 118.98, 55.41),
        (83.24, 126.56, 59.43),
        (69.76, 106.48, 49.94),
        (74.66, 112.91, 53.48)
    ]
    return table_h_3


def get_table_h_4():
    """表 H.4 間歇運転能力補正係数

    Args:

    Returns:
      list: 表 H.4 間歇運転能力補正係数

    """
    table_h_4 = [
        1.0,
        1.0,
        2.25,
        2.25,
        1.0,
        3.03,
        1.0,
        1.62
    ]
    return table_h_4
