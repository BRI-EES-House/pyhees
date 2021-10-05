# ============================================================================
# 第二章 単位住戸の一次エネルギー消費量
# 第五節 気候風土適応住宅
# Ver.06（エネルギー消費性能計算プログラム（住宅版）Ver.02～）
# ============================================================================

def get_E_ST_star(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """基準一次エネルギー消費量

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
    :param result_type: 基準値計算タイプ
    :type result_type: str
    :return: 基準一次エネルギー消費量
    :rtype: float
    """
    # 平成 28 年 4 月 1 日時点で現存しない住宅 (1-1)
    E_star_ST_trad_p = E_SH + E_SC + E_SV + E_SL + E_SW + E_SM
    # 平成 28 年 4 月 1 日時点で現存する住宅  (1-2)
    E_star_ST_trad_e = (E_SH + E_SC + E_SV + E_SL + E_SW) * 1.1 + E_SM

    return E_star_ST_trad_p, E_star_ST_trad_e
