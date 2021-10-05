# ============================================================================
# 第二章 単位住戸の一次エネルギー消費量
# 第四節 特定建築主基準
# Ver.05（エネルギー消費性能計算プログラム（住宅版）Ver.02～）
# ============================================================================

def get_E_ST_star(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM, reference):
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
    :param reference: 基準計算仕様
    :type reference: dict
    :raises ValueError: 建築年度が「令和2年3月までに新築する住宅」または「令和2年4月以降に新築する住宅」でない場合に発生
    :return: 基準一次エネルギー消費量
    :rtype: float
    """
    building_year = reference['building_year']

    if building_year == '令和2年3月までに新築する住宅':
        E_star_ST_rb = (E_SH + E_SC + E_SV + E_SL + E_SW) * 0.9 + E_SM  # (1-1)
    elif building_year == '令和2年4月以降に新築する住宅':
        E_star_ST_rb = (E_SH + E_SC + E_SV + E_SL + E_SW) * 0.85 + E_SM  # (1-2)
    else:
        raise ValueError(building_year)

    return E_star_ST_rb