# ============================================================================
# 第二章 住宅部分の一次エネルギー消費量
# 第四節 BEI
# Ver.13（エネルギー消費性能計算プログラム（住宅版）Ver.2022.10～）
# ============================================================================


# ============================================================================
# 5. BEIおよび誘導BEI
# ============================================================================

from math import ceil
from typing import TypedDict, Optional


class BEI(TypedDict):
    """各適合基準におけるBEI (-)

    Attributes:
        BEI_gn_du (Optional[float]):
            建築物エネルギー消費性能基準（気候風土適応住宅を除く）における単位住戸のBEI (-)
            住宅の種類が「一般住宅」以外の場合はNone
        BEI_trad_du (Optional[float]):
            建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸のBEI (-)
            住宅の種類が「行政庁認定住宅」以外の場合はNone
        BEI_indc_du (Optional[float]):
            建築物エネルギー消費性能誘導基準における単位住戸のBEI (-)
            住宅の種類が「一般住宅」以外の場合はNone
        BEI_rb_du (Optional[float]):
            特定建築主基準における単位住戸のBEI (-)
            住宅の種類が「事業主基準」以外の場合はNone
        BEI_lcb_du (Optional[float]):
            建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸のBEI (-)
            住宅の種類が「一般住宅」以外の場合はNone
    """

    BEI_gn_du: Optional[float]
    BEI_trad_du: Optional[float]
    BEI_indc_du: Optional[float]
    BEI_rb_du: Optional[float]
    BEI_lcb_du: Optional[float]


def calc_BEI(E_dash_T_dict, E_dash_ST_dict, type) -> BEI:
    """各適合基準におけるBEI算出結果を取得

    Args:
        E_dash_T_dict (DesignedPrimaryEnergyTotalDash):
            各適合基準における設計一次エネルギー消費量(その他一次エネルギー消費量を除く)を格納する辞書
        E_dash_ST_dict (StandardPrimaryEnergyTotalDash): _description_
            各適合基準における基準一次エネルギー消費量(その他一次エネルギー消費量を除く)を格納する辞書
        type (str): 住宅タイプ

    Returns:
        BEI: 各適合基準におけるBEi算出結果を格納する辞書
    """
    BEI_gn_du = None
    BEI_trad_du = None
    BEI_indc_du = None
    BEI_rb_du = None
    BEI_lcb_du = None

    if type == '一般住宅':
        BEI_gn_du = get_BEI_gn_du(E_dash_T_dict['E_dash_T_gn_du'], E_dash_ST_dict['E_dash_ST_gn_du'])
        BEI_indc_du = get_BEI_indc_du(E_dash_T_dict['E_dash_T_indc_du'], E_dash_ST_dict['E_dash_ST_indc_du'])
        BEI_lcb_du = get_BEI_lcb_du(E_dash_T_dict['E_dash_T_lcb_du'], E_dash_ST_dict['E_dash_ST_lcb_du'])
    elif type == '事業主基準':
        BEI_rb_du = get_BEI_rb_du(E_dash_T_dict['E_dash_T_rb_du'], E_dash_ST_dict['E_dash_ST_rb_du'])
    elif type == '行政庁認定住宅':
        BEI_trad_du = get_BEI_trad_du(E_dash_T_dict['E_dash_T_trad_du'], E_dash_ST_dict['E_dash_ST_trad_du'])
    else:
        raise ValueError(type)

    return {
        'BEI_gn_du': BEI_gn_du,
        'BEI_trad_du': BEI_trad_du,
        'BEI_indc_du': BEI_indc_du,
        'BEI_rb_du': BEI_rb_du,
        'BEI_lcb_du': BEI_lcb_du,
    }


# ====================================================================
# 5.2 建築物エネルギー消費性能基準（気候風土適応住宅を除く）におけるBEI
# ====================================================================

def get_BEI_gn_du(E_dash_T_gn_du, E_dash_ST_gn_du):
    """式(1) 建築物エネルギー消費性能基準における単位住戸のBEI (-)

    Args:
        E_dash_T_gn_du (float):
            建築物エネルギー消費性能基準における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)
        E_dash_ST_gn_du (float):
            建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)

    Returns:
        float: 式(1) 建築物エネルギー消費性能基準における単位住戸のBEI (-)
    """
    # 丸め誤差回避のため、独自に定義した関数を使用
    BEI_gn_du_raw = _division(E_dash_T_gn_du, E_dash_ST_gn_du, digit=1)

    # 小数点以下二位未満の端数を切り上げ
    return ceil(BEI_gn_du_raw * 100) / 100


# ============================================================================
# 5.3 建築物エネルギー消費性能基準（気候風土適応住宅）におけるBEI
# ============================================================================

def get_BEI_trad_du(E_dash_T_trad_du, E_dash_ST_trad_du):
    """式(5) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸のBEI (-)

    Args:
        E_dash_T_trad_du (float):
            建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)
        E_dash_ST_trad_du (float):
            建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)

    Returns:
        float: 式(5) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸のBEI (-)

    """
    # 丸め誤差回避のため、独自に定義した関数を使用
    BEI_trad_du_raw = _division(E_dash_T_trad_du, E_dash_ST_trad_du, digit=1)

    # 小数点以下二位未満の端数を切り上げ
    return ceil(BEI_trad_du_raw * 100) / 100


# ============================================================================
# 5.4 建築物エネルギー消費性能誘導基準における誘導BEI
# ============================================================================

def get_BEI_indc_du(E_dash_T_indc_du, E_dash_ST_indc_du):
    """式(6) 建築物エネルギー消費性能誘導基準における単位住戸のBEI (-)

    Args:
        E_dash_T_indc_du (float):
            建築物エネルギー消費性能誘導基準における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)
        E_dash_ST_indc_du (float):
            建築物エネルギー消費性能誘導基準における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)

    Returns:
        float: 式(6) 建築物エネルギー消費性能誘導基準における単位住戸のBEI (-)
    """
    # 丸め誤差回避のため、独自に定義した関数を使用
    BEI_indc_du_raw = _division(E_dash_T_indc_du, E_dash_ST_indc_du, digit=1)

    # 小数点以下二位未満の端数を切り上げ
    return ceil(BEI_indc_du_raw * 100) / 100


# ============================================================================
# 5.5 特定建築主基準におけるBEI
# ============================================================================

def get_BEI_rb_du(E_dash_T_rb_du, E_dash_ST_rb_du):
    """式(10) 特定建築主基準における単位住戸のBEI (-)

    Args:
        E_dash_T_rb_du (float):
            特定建築主基準における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)
        E_dash_ST_rb_du (float):
            特定建築主基準における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)

    Returns:
        式(10) 特定建築主基準における単位住戸のBEI (-)
    """
    # 丸め誤差回避のため、独自に定義した関数を使用
    BEI_rb_du_raw = _division(E_dash_T_rb_du, E_dash_ST_rb_du, digit=1)

    # 小数点以下二位未満の端数を切り上げ
    return ceil(BEI_rb_du_raw * 100) / 100


# ============================================================================
# 5.6 建築物に係るエネルギーの使用の合理化の一層の促進その他の建築物の
#   低炭素化の促進のために誘導すべき基準（建築物の低炭素化誘導基準）における
#   誘導BEI
# ============================================================================

def get_BEI_lcb_du(E_dash_T_lcb_du, E_dash_ST_lcb_du):
    """式(11) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸のBEI (-)

    Args:
        E_dash_T_lcb_du (float):
            建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の設計一次エネルギー消費量（その他の設計一次エネルギー消費量を除く） (GJ/年)
        E_dash_ST_lcb_du (float):
            建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)

    Returns:
        float: 式(11) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸のBEI (-)
    """
    # 丸め誤差回避のため、独自に定義した関数を使用
    BEI_lcb_du_raw = _division(E_dash_T_lcb_du, E_dash_ST_lcb_du, digit=1)

    # 小数点以下二位未満の端数を切り上げ
    return ceil(BEI_lcb_du_raw * 100) / 100


# =============================================================================
# 以下、共通の処理を定義
# =============================================================================

def _division(numerator: float, denominator: float, digit: int) -> float:
    """丸め誤差の回避を目的として利用される関数

    Args:
        numerator (float): 分子の値
        denominator (float): 分母の値
        digit (int): 分子・分母の有効桁数

    Returns:
        float: 割り算の計算結果
    """
    if denominator == 0.0:
        return 0.0

    # 丸め誤差回避のため、整数同士の除算に置き換える
    p = 10**digit
    n = numerator * p
    d = denominator * p
    return n / d
