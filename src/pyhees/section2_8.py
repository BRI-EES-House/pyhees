# ============================================================================
# 第二章 単位住戸の一次エネルギー消費量
# 第八節 低炭素建築物の認定基準
# ============================================================================

def get_E_ST_star(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """基準一次エネルギー消費量（１）

    Args:
      E_SH(float): 1 時間当たりの暖房設備の基準一次エネルギー消費量
      E_SC(float): 1 時間当たりの冷房設備の基準一次エネルギー消費量
      E_SV(float): 1 時間当たりの換気設備の基準一次エネルギー消費量
      E_SL(float): 1 時間当たりの照明設備の基準一次エネルギー消費量
      E_SW(float): 1 時間当たりの給湯設備の基準一次エネルギー消費量
      E_SM(float): 1 時間当たりのその他の基準一次エネルギー消費量

    Returns:
      float: 基準一次エネルギー消費量

    """

    return (E_SH + E_SC + E_SV + E_SL + E_SW) * 0.9 + E_SM
