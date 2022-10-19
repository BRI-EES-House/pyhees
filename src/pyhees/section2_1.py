# ============================================================================
# 第二章 住宅部分の一次エネルギー消費量
# 第一節 一般
# Ver.13（エネルギー消費性能計算プログラム（住宅版）Ver.2022.10～）
# ============================================================================

from typing import Optional, TypedDict


# ============================================================================
# 8 各種基準への適合
# ============================================================================


# ============================================================================
# 8.1 一次エネルギー消費量
# ============================================================================

class AchievementStatus(TypedDict):
    """各適合基準における適合判定結果

    AAttributes:
        STATUS_gn_p (Optional[bool]):
            建築物エネルギー消費性能基準における適合判定（平成28年4月1日時点で現存しない住宅）
            住宅の種類が「一般住宅」以外の場合はNone
        STATUS_gn_e (Optional[bool]):
            建築物エネルギー消費性能基準における適合判定（平成28年4月1日時点で現存する住宅）
            住宅の種類が「一般住宅」以外の場合はNone
        STATUS_trad_p (Optional[bool]):
            建築物エネルギー消費性能基準（気候風土適応住宅版）における適合判定（平成28年4月1日時点で現存しない住宅）
            住宅の種類が「行政庁認定住宅」以外の場合はNone
        STATUS_trad_e (Optional[bool]):
            建築物エネルギー消費性能基準（気候風土適応住宅版）における適合判定（平成28年4月1日時点で現存する住宅）
            住宅の種類が「行政庁認定住宅」以外の場合はNone
        STATUS_indc_p (Optional[bool]):
            建築物エネルギー消費性能誘導基準における適合判定（令和4年10月1日時点で現存しない住宅）
            住宅の種類が「一般住宅」以外の場合はNone
        STATUS_indc_e (Optional[bool]):
            建築物エネルギー消費性能誘導基準における適合判定（令和4年10月1日時点で現存する住宅）
            住宅の種類が「一般住宅」以外の場合はNone
        STATUS_rb_cy1 (Optional[bool]):
            特定建築主基準における適合判定（令和2年3月までに新築する住宅）
            住宅の種類が「事業主基準」以外の場合はNone
        STATUS_rb_cy2 (Optional[bool]):
            特定建築主基準における適合判定（令和2年4月以降に新築する住宅）
            住宅の種類が「事業主基準」以外の場合はNone
        STATUS_lcb_p (Optional[bool]):
            建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における適合判定（平成28年4月1日時点で現存しない住宅）
            住宅の種類が「一般住宅」以外の場合はNone
        STATUS_lcb_e (Optional[bool]):
            建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における適合判定（平成28年4月1日時点で現存する住宅）
            住宅の種類が「一般住宅」以外の場合はNone
        STATUS_enh (Optional[bool]):
            低炭素化の促進のために誘導すべきその他の基準における適合判定
            住宅の種類が「一般住宅」以外の場合はNone
    """

    STATUS_gn_p: Optional[bool]
    STATUS_gn_e: Optional[bool]
    STATUS_trad_p: Optional[bool]
    STATUS_trad_e: Optional[bool]
    STATUS_indc_p: Optional[bool]
    STATUS_indc_e: Optional[bool]
    STATUS_rb_cy1: Optional[bool]
    STATUS_rb_cy2: Optional[bool]
    STATUS_lcb_p: Optional[bool]
    STATUS_lcb_e: Optional[bool]
    STATUS_enh: Optional[bool]


def get_status(E_T_dict, E_ST_dict, type) -> AchievementStatus:
    """各適合基準における適合判定結果を取得

    Args:
        E_T_dict (DesignedPrimaryEnergyTotal):
            各適合基準における設計一次エネルギー消費量を格納する辞書
        E_ST_dict (StandardPrimaryEnergyTotal):
            各適合基準における基準一次エネルギー消費量を格納する辞書
        type (str): 住宅タイプ

    Returns:
        AchievementStatus:各適合基準における適合判定結果を格納する辞書
    """
    STATUS_gn_p = None
    STATUS_gn_e = None
    STATUS_trad_p = None
    STATUS_trad_e = None
    STATUS_indc_p = None
    STATUS_indc_e = None
    STATUS_rb_cy1 = None
    STATUS_rb_cy2 = None
    STATUS_lcb_p = None
    STATUS_lcb_e = None
    STATUS_enh = None

    if type == '一般住宅':
        STATUS_gn_p = get_STATUS_gn_p(E_T_dict['E_T_gn_du'], E_ST_dict['E_ST_gn_du_p'])
        STATUS_gn_e = get_STATUS_gn_e(E_T_dict['E_T_gn_du'], E_ST_dict['E_ST_gn_du_e'])
        STATUS_indc_p = get_STATUS_indc_p(E_T_dict['E_T_indc_du'], E_ST_dict['E_ST_indc_du_p'])
        STATUS_indc_e = get_STATUS_indc_e(E_T_dict['E_T_indc_du'], E_ST_dict['E_ST_indc_du_e'])
        STATUS_lcb_p = get_STATUS_lcb_p(E_T_dict['E_T_lcb_du'], E_ST_dict['E_ST_lcb_du_p'])
        STATUS_lcb_e = get_STATUS_lcb_e(E_T_dict['E_T_lcb_du'], E_ST_dict['E_ST_lcb_du_e'])
        STATUS_enh = get_STATUS_enh(E_T_dict['E_T_enh_du'], E_ST_dict['E_ST_enh_du'])
    elif type == '事業主基準':
        STATUS_rb_cy1 = get_STATUS_rb_cy1(E_T_dict['E_T_rb_du'], E_ST_dict['E_ST_rb_du_cy1'])
        STATUS_rb_cy2 = get_STATUS_rb_cy2(E_T_dict['E_T_rb_du'], E_ST_dict['E_ST_rb_du_cy2'])
    elif type == '行政庁認定住宅':
        STATUS_trad_p = get_STATUS_trad_p(E_T_dict['E_T_trad_du'], E_ST_dict['E_ST_trad_du_p'])
        STATUS_trad_e = get_STATUS_trad_e(E_T_dict['E_T_trad_du'], E_ST_dict['E_ST_trad_du_e'])
    else:
        raise ValueError(type)

    return {
        'STATUS_gn_p': STATUS_gn_p,
        'STATUS_gn_e': STATUS_gn_e,
        'STATUS_trad_p': STATUS_trad_p,
        'STATUS_trad_e': STATUS_trad_e,
        'STATUS_indc_p': STATUS_indc_p,
        'STATUS_indc_e': STATUS_indc_e,
        'STATUS_rb_cy1': STATUS_rb_cy1,
        'STATUS_rb_cy2': STATUS_rb_cy2,
        'STATUS_lcb_p': STATUS_lcb_p,
        'STATUS_lcb_e': STATUS_lcb_e,
        'STATUS_enh': STATUS_enh,
    }


# ============================================================================
# 8.1.1 建築物エネルギー消費性能基準（気候風土適応住宅を除く）
# ============================================================================

def get_STATUS_gn_p(E_T_gn_du, E_ST_gn_du_p):
    """(1) 建築物エネルギー消費性能基準における適合判定（平成28年4月1日時点で現存しない住宅）

    Args:
        E_T_gn_du (float):
            建築物エネルギー消費性能基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
        E_ST_gn_du_p (float):
            建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量
            （平成28年4月1日時点で現存しない住宅） (GJ/年)

    Returns:
        bool: (1) 建築物エネルギー消費性能基準における適合判定（平成28年4月1日時点で現存しない住宅）
    """
    return E_T_gn_du <= E_ST_gn_du_p


def get_STATUS_gn_e(E_T_gn_du, E_ST_gn_du_e):
    """(2) 建築物エネルギー消費性能基準における適合判定（平成28年4月1日時点で現存する住宅）

    Args:
        E_T_gn_du (float):
            建築物エネルギー消費性能基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
        E_ST_gn_du_e (float):
            建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量（平成28年4月1日時点で現存する住宅） (GJ/年)

    Returns:
        bool: (2) 建築物エネルギー消費性能基準における適合判定（平成28年4月1日時点で現存する住宅）
    """
    return E_T_gn_du <= E_ST_gn_du_e


# ============================================================================
# 8.1.2 建築物エネルギー消費性能基準（気候風土適応住宅）
# ============================================================================

def get_STATUS_trad_p(E_T_trad_du, E_ST_trad_du_p):
    """(5) 建築物エネルギー消費性能基準（気候風土適応住宅版）における適合判定（平成28年4月1日時点で現存しない住宅）

    Args:
        E_T_trad_du (float):
            建築物エネルギー消費性能基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
        E_ST_trad_du_p (float):
            建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量（平成28年4月1日時点で現存しない住宅） (GJ/年)

    Returns:
        bool: (5) 建築物エネルギー消費性能基準（気候風土適応住宅版）における適合判定（平成28年4月1日時点で現存しない住宅）
    """
    return E_T_trad_du <= E_ST_trad_du_p


def get_STATUS_trad_e(E_T_trad_du, E_ST_trad_du_e):
    """(6) 建築物エネルギー消費性能基準（気候風土適応住宅版）における適合判定（平成28年4月1日時点で現存する住宅）

    Args:
        E_T_trad_du (float):
            建築物エネルギー消費性能基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
        E_ST_trad_du_e (float):
            建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量（平成28年4月1日時点で現存する住宅） (GJ/年)

    Returns:
        bool: (6) 建築物エネルギー消費性能基準（気候風土適応住宅版）における適合判定（平成28年4月1日時点で現存する住宅）
    """
    return E_T_trad_du <= E_ST_trad_du_e


# ============================================================================
# 8.1.3 建築物エネルギー消費性能誘導基準
# ============================================================================

def get_STATUS_indc_p(E_T_indc_du, E_ST_indc_du_p):
    """(7) 建築物エネルギー消費性能誘導基準における適合判定（令和4年10月1日時点で現存しない住宅）

    Args:
        E_T_indc_du (float):
            建築物エネルギー消費性能誘導基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
        E_ST_indc_du_p (float):
            建築物エネルギー消費性能誘導基準における単位住戸の基準一次エネルギー消費量（令和4年10月日時点で現存しない住宅） (GJ/年)

    Returns:
        bool: (7) 建築物エネルギー消費性能誘導基準における適合判定（令和4年10月1日時点で現存しない住宅）
    """
    return E_T_indc_du <= E_ST_indc_du_p


def get_STATUS_indc_e(E_T_indc_du, E_ST_indc_du_e):
    """(8) 建築物エネルギー消費性能誘導基準における適合判定（令和4年10月1日時点で現存する住宅）

    Args:
        E_T_indc_du (float):
            建築物エネルギー消費性能誘導基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
        E_ST_indc_du_e (float):
            建築物エネルギー消費性能誘導基準における単位住戸の基準一次エネルギー消費量（令和4年10月日時点で現存する住宅） (GJ/年)

    Returns:
        bool: (8) 建築物エネルギー消費性能誘導基準における適合判定（令和4年10月1日時点で現存する住宅）
    """
    # 等号を含まないことに注意
    return E_T_indc_du < E_ST_indc_du_e


# ============================================================================
# 8.1.4 特定建築主基準
# ============================================================================

def get_STATUS_rb_cy1(E_T_rb_du, E_ST_rb_du_cy1):
    """(11) 特定建築主基準における適合判定（令和2年3月までに新築する住宅）

    Args:
        E_T_rb_du (float):
            特定建築主基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
        E_ST_rb_du_cy1 (float):
            特定建築主基準における単位住戸の基準一次エネルギー消費量（令和2年3月までに新築する住宅） (GJ/年)

    Returns:
        bool: (11) 特定建築主基準における適合判定（令和2年3月までに新築する住宅）
    """
    return E_T_rb_du <= E_ST_rb_du_cy1


def get_STATUS_rb_cy2(E_T_rb_du, E_ST_rb_du_cy2):
    """(12) 特定建築主基準における適合判定（令和2年4月以降に新築する住宅）

    Args:
        E_T_rb_du (float):
            特定建築主基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
        E_ST_rb_du_cy2 (float):
            特定建築主基準における単位住戸の基準一次エネルギー消費量（令和2年4月以降に新築する住宅） (GJ/年)

    Returns:
        bool: (12) 特定建築主基準における適合判定（令和2年4月以降に新築する住宅）
    """
    return E_T_rb_du <= E_ST_rb_du_cy2


# ============================================================================
# 8.1.5 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準
# ============================================================================

def get_STATUS_lcb_p(E_T_lcb_du, E_ST_lcb_du_p):
    """(13) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における適合判定（平成28年4月1日時点で現存しない住宅）

    Args:
        E_T_lcb_du (float):
            建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
        E_ST_lcb_du_p (float):
            建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (GJ/年)
    Returns:
        bool: (13) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における適合判定（平成28年4月1日時点で現存しない住宅）
    """
    return E_T_lcb_du <= E_ST_lcb_du_p


def get_STATUS_lcb_e(E_T_lcb_du, E_ST_lcb_du_e):
    """(14) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における適合判定（平成28年4月1日時点で現存する住宅）

    Args:
        E_T_lcb_du (float):
            建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
        E_ST_lcb_du_e (float):
            建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の基準一次エネルギー消費量（令和4年10月1日時点で現存する住宅） (GJ/年)
    Returns:
        bool: (14) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における適合判定（平成28年4月1日時点で現存する住宅）
    """
    return E_T_lcb_du <= E_ST_lcb_du_e


# ============================================================================
# 8.1.6 建築物の低炭素化の促進のために誘導すべきその他の基準
# ============================================================================

def get_STATUS_enh(E_T_enh_du, E_ST_enh_du):
    """(17) 低炭素化の促進のために誘導すべきその他の基準における適合判定

    Args:
        E_T_enh_du (float):
            建築物の低炭素化の促進のために誘導すべきその他の基準における単位住戸の設計一次エネルギー消費量 (GJ/年)
        E_ST_enh_du (float):
            建築物の低炭素化の促進のために誘導すべきその他の基準における単位住戸の基準一次エネルギー消費量 (GJ/年)

    Returns:
        bool: (17) 低炭素化の促進のために誘導すべきその他の基準における適合判定
    """
    return E_T_enh_du <= E_ST_enh_du
