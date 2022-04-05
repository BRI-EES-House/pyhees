# ============================================================================
# 第二章 単位住戸の一次エネルギー消費量
# 第四節 特定建築主基準
# Ver.05（エネルギー消費性能計算プログラム（住宅版）Ver.02～）
# ============================================================================

def get_E_ST_star(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM, reference):
    """基準一次エネルギー消費量

    Args:
      E_SH(float): 1 時間当たりの暖房設備の基準一次エネルギー消費量
      E_SC(float): 1 時間当たりの冷房設備の基準一次エネルギー消費量
      E_SV(float): 1 時間当たりの換気設備の基準一次エネルギー消費量
      E_SL(float): 1 時間当たりの照明設備の基準一次エネルギー消費量
      E_SW(float): 1 時間当たりの給湯設備の基準一次エネルギー消費量
      E_SM(float): 1 時間当たりのその他の基準一次エネルギー消費量
      reference(dict): 基準計算仕様

    Returns:
      float: 基準一次エネルギー消費量

    Raises:
      ValueError: 建築年度が「令和2年3月までに新築する住宅」または「令和2年4月以降に新築する住宅」でない場合に発生

    """
    building_year = reference['building_year']

    if building_year == '令和2年3月までに新築する住宅':
        E_star_ST_rb = (E_SH + E_SC + E_SV + E_SL + E_SW) * 0.9 + E_SM  # (1-1)
    elif building_year == '令和2年4月以降に新築する住宅':
        E_star_ST_rb = (E_SH + E_SC + E_SV + E_SL + E_SW) * 0.85 + E_SM  # (1-2)
    else:
        raise ValueError(building_year)

    return E_star_ST_rb


def update_spec_for_ees(spec):
    """敷設率を上書きする関数
    
    参照：2章4節 6.2 暖房設備の設計一次エネルギー消費量 
    """
    if spec['type'] == '事業主基準':
        for _ in ['H_MR', 'H_OR']:
            H_xR = spec.get(_)

            if H_xR is not None:
                if H_xR['type'] in ['電気ヒーター床暖房', '温水暖房用床暖房', 'ルームエアコンディショナー付温水床暖房機']:
                    H_xR['r_Af'] = 0.40
