# ============================================================================
# 第二章 単位住戸の一次エネルギー消費量
# 第八節 低炭素建築物の認定基準
# ============================================================================

def get_E_ST_star(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """基準一次エネルギー消費量（１）

    :param E_SH: 1 時間当たりの暖房設備の基準一次エネルギー消費量
    :type E_SH: float
    :param E_SC: 1 時間当たりの冷房設備の基準一次エネルギー消費量
    :type E_SC: float
    :param E_SV: 1 時間当たりの換気設備の基準一次エネルギー消費量
    :type E_SV: float
    :param E_SL: 1 時間当たりの照明設備の基準一次エネルギー消費量
    :type E_SL: float
    :param E_SW: 1 時間当たりの給湯設備の基準一次エネルギー消費量
    :type E_SW: float
    :param E_SM: 1 時間当たりのその他の基準一次エネルギー消費量
    :type E_SM: float
    :return: 基準一次エネルギー消費量
    :rtype: float
    """

    return (E_SH + E_SC + E_SV + E_SL + E_SW) * 0.9 + E_SM
