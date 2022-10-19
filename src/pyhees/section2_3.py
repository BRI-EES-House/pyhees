# ============================================================================
# 第二章 住宅部分の一次エネルギー消費量
# 第三節 基準一次エネルギー消費量
# Ver.13（エネルギー消費性能計算プログラム（住宅版）Ver.2022.10～）
# ============================================================================


from math import ceil, floor
from typing import Tuple, TypedDict, Optional

from pyhees.section2_2 import calc_E_C, calc_E_H
from pyhees.section4_1 import calc_cooling_load, calc_heating_load, get_virtual_heating_devices, calc_heating_mode


class StandardPrimaryEnergyTotal(TypedDict):
    """各適合基準における基準一次エネルギー消費量 (GJ/年)

    Attributes:
        E_ST_gn_du_p (Optional[float]):
            建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量
            （平成28年4月1日時点で現存しない住宅） (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_ST_gn_du_e (Optional[float]):
            建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量
            （平成28年4月1日時点で現存する住宅） (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_ST_trad_du_p (Optional[float]):
            建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量
            （平成28年4月1日時点で現存しない住宅） (GJ/年)
            住宅の種類が「行政庁認定基準」以外の場合はNone
        E_ST_trad_du_e (Optional[float]):
            建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量
            （平成28年4月1日時点で現存する住宅） (GJ/年)
            住宅の種類が「行政庁認定基準」以外の場合はNone
        E_ST_indc_du_p (Optional[float]):
            建築物エネルギー消費性能誘導基準における単位住戸の基準一次エネルギー消費量
            （令和4年10月1日時点で現存しない住宅） (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_ST_indc_du_e (Optional[float]):
            建築物エネルギー消費性能誘導基準における単位住戸の基準一次エネルギー消費量
            （令和4年10月1日時点で現存する住宅） (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_ST_rb_du_cy1 (Optional[float]):
            特定建築主基準における単位住戸の基準一次エネルギー消費量
            （令和2年3月までに新築する住宅） (GJ/年)
            住宅の種類が「事業主基準」以外の場合はNone
        E_ST_rb_du_cy2 (Optional[float]):
            特定建築主基準における単位住戸の基準一次エネルギー消費量
            （令和2年4月以降に新築する住宅） (GJ/年)
            住宅の種類が「事業主基準」以外の場合はNone
        E_ST_lcb_du_p  (Optional[float]):
            建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における
            単位住戸の基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_ST_lcb_du_e  (Optional[float]):
            建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における
            単位住戸の基準一次エネルギー消費量（令和4年10月1日時点で現存する住宅） (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_ST_enh_du  (Optional[float]):
            建築物の低炭素化の促進のために誘導すべきその他の基準における単位住戸の基準一次エネルギー消費量 (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
    """

    E_ST_gn_du_p: Optional[float]
    E_ST_gn_du_e: Optional[float]
    E_ST_trad_du_p: Optional[float]
    E_ST_trad_du_e: Optional[float]
    E_ST_indc_du_p: Optional[float]
    E_ST_indc_du_e: Optional[float]
    E_ST_rb_du_cy1: Optional[float]
    E_ST_rb_du_cy2: Optional[float]
    E_ST_lcb_du_p : Optional[float]
    E_ST_lcb_du_e : Optional[float]
    E_ST_enh_du : Optional[float]


class StandardPrimaryEnergyTotalDash(TypedDict):
    """各適合基準における基準一次エネルギー消費量(その他一次エネルギー消費量を除く) (GJ/年)

    Attributes:
        E_dash_ST_gn_du (Optional[float]):
            建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量
            （その他の基準一次エネルギー消費量を除く） (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_dash_ST_trad_du (Optional[float]):
            建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量
            （その他の基準一次エネルギー消費量を除く） (GJ/年)
            住宅の種類が「行政庁認定基準」以外の場合はNone
        E_dash_ST_indc_du (Optional[float]):
            建築物エネルギー消費性能誘導基準における単位住戸の基準一次エネルギー消費量
            （その他の基準一次エネルギー消費量を除く） (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
        E_dash_ST_rb_du (Optional[float]):
            特定建築主基準における単位住戸の基準一次エネルギー消費量
            （その他の基準一次エネルギー消費量を除く） (GJ/年)
            住宅の種類が「事業主基準」以外の場合はNone
        E_dash_ST_lcb_du (Optional[float]):
            建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における
            単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)
            住宅の種類が「一般住宅」以外の場合はNone
    """

    E_dash_ST_gn_du: Optional[float]
    E_dash_ST_trad_du: Optional[float]
    E_dash_ST_indc_du: Optional[float]
    E_dash_ST_rb_du: Optional[float]
    E_dash_ST_lcb_du: Optional[float]


class StandardPrimaryEnergyDetail(TypedDict):
    """各設備における基準一次エネルギー消費量／削減量 (MJ/年)

    Attributes:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年) 
    """

    E_SH: float
    E_SC: float
    E_SV: float
    E_SL: float
    E_SW: float
    E_SM: float


def calc_E_ST(spec) -> Tuple[StandardPrimaryEnergyTotal, StandardPrimaryEnergyTotalDash, StandardPrimaryEnergyDetail]:
    """基準一次エネルギー消費量の計算

    Args:
        spec(dict): 住戸についての詳細なデータ

    Returns:
        E_ST_dict (StandardPrimaryEnergyTotal):
            各適合基準における基準一次エネルギー消費量合計値を格納する辞書
        E_dash_ST_dict (StandardPrimaryEnergyTotalDash):
            各適合基準における基準一次エネルギー消費量合計値(その他一次エネルギー消費量を除く)を格納する辞書
        E_std_detail (StandardPrimaryEnergyDetail):
            各設備における基準一次エネルギー消費量を格納する辞書
    """
    # 1年当たりの機械換気設備の基準一次エネルギー消費量
    E_SV = calc_E_SV(spec['A_A'])

    # 1 時間当たりの暖房設備の基準一次エネルギー消費量
    E_SH = calc_E_SH(spec['type'], spec['tatekata'], spec['region'], spec['sol_region'], spec['A_A'],
                     spec['A_MR'], spec['A_OR'], spec['ENV'], spec['mode_H'], spec['mode_C'], spec['NV_MR'], spec['NV_OR'], spec['H_MR'], spec['H_OR'])

    # 1 時間当たりの冷房設備の基準一次エネルギー消費量
    E_SC = calc_E_SC(spec['type'], spec['tatekata'], spec['region'], spec['A_A'], spec['A_MR'],
                     spec['A_OR'], spec['ENV'], spec['mode_C'], spec['mode_H'], spec['H_MR'], spec['H_OR'], spec['TS'], spec['HEX'],
                     spec['sol_region'], spec['NV_MR'], spec['NV_OR'])

    # 1年当たりの給湯設備の基準一次エネルギー消費量
    E_SW = calc_E_SW(spec['region'], spec['A_A'], spec['HW'])

    # 1年当たりの照明設備の基準一次エネルギー消費量
    E_SL = calc_E_SL(spec['A_A'], spec['A_MR'], spec['A_OR'])

    # 1年当たりのその他の基準一次エネルギー消費量
    E_SM = calc_E_SM(spec['A_A'])

    # 各適合基準における基準一次エネルギー消費量合計値
    E_ST_dict = calc_E_ST_dict(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM, spec['type'])

    # 各適合基準における基準一次エネルギー消費量合計値(その他一次エネルギー消費量を除く)
    E_dash_ST_dict = calc_E_dash_ST_dict(E_SH, E_SC, E_SV, E_SL, E_SW, spec['type'])

    # 各設備における基準一次エネルギー消費量
    E_std_detail = {
        'E_SH': E_SH,
        'E_SC': E_SC,
        'E_SV': E_SV,
        'E_SL': E_SL,
        'E_SW': E_SW,
        'E_SM': E_SM,
    }

    return E_ST_dict, E_dash_ST_dict, E_std_detail


# ============================================================================
# 5. 基準一次エネルギー消費量および誘導基準一次エネルギー消費量
# ============================================================================

def calc_E_ST_dict(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM, type) -> StandardPrimaryEnergyTotal:
    """各適合基準における基準一次エネルギー消費量合計値を算出する関数

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)
        type (str): 住宅の種類

    Returns:
        StandardPrimaryEnergyTotal: 各適合基準における基準一次エネルギー消費量合計値を格納する辞書
    """
    E_ST_gn_du_p = None
    E_ST_gn_du_e = None
    E_ST_trad_du_p = None
    E_ST_trad_du_e = None
    E_ST_indc_du_p = None
    E_ST_indc_du_e = None
    E_ST_rb_du_cy1 = None
    E_ST_rb_du_cy2 = None
    E_ST_lcb_du_p  = None
    E_ST_lcb_du_e  = None
    E_ST_enh_du  = None

    if type == '一般住宅':
        E_ST_gn_du_p = get_E_ST_gn_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)
        E_ST_gn_du_e = get_E_ST_gn_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)
        E_ST_indc_du_p = get_E_ST_indc_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)
        E_ST_indc_du_e = get_E_ST_indc_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)
        E_ST_lcb_du_p = get_E_ST_lcb_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)
        E_ST_lcb_du_e = get_E_ST_lcb_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)
        E_ST_enh_du = get_E_ST_enh_du(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)
    elif type == '事業主基準':
        E_ST_rb_du_cy1 = get_E_ST_rb_du_cy1(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)
        E_ST_rb_du_cy2 = get_E_ST_rb_du_cy2(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)
    elif type == '行政庁認定住宅':
        E_ST_trad_du_p = get_E_ST_trad_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)
        E_ST_trad_du_e = get_E_ST_trad_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)
    else:
        raise ValueError(type)

    return {
        'E_ST_gn_du_p': E_ST_gn_du_p,
        'E_ST_gn_du_e': E_ST_gn_du_e,
        'E_ST_trad_du_p': E_ST_trad_du_p,
        'E_ST_trad_du_e': E_ST_trad_du_e,
        'E_ST_indc_du_p': E_ST_indc_du_p,
        'E_ST_indc_du_e': E_ST_indc_du_e,
        'E_ST_rb_du_cy1': E_ST_rb_du_cy1,
        'E_ST_rb_du_cy2': E_ST_rb_du_cy2,
        'E_ST_lcb_du_p': E_ST_lcb_du_p,
        'E_ST_lcb_du_e': E_ST_lcb_du_e,
        'E_ST_enh_du': E_ST_enh_du,
    }


# ====================================================================
# 5.2 建築物エネルギー消費性能基準（気候風土適応住宅を除く）における基準一次エネルギー消費量
# ====================================================================

def get_E_ST_gn_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(1) 建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量（平成28年4月1日時点で現存しない住宅） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(1) 建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量（平成28年4月1日時点で現存しない住宅） (GJ/年)
    """
    # 式(3) 建築物エネルギー消費性能基準における単位住戸の1年当たりの基準一次エネルギー消費量（平成28年4月1日時点で現存しない住宅） (MJ/年)
    E_star_ST_gn_du_p = get_E_star_ST_gn_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_ST_gn_du_p / 100) / 10


def get_E_ST_gn_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(2) 建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量（平成28年4月1日時点で現存する住宅） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(2) 建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量（平成28年4月1日時点で現存する住宅） (GJ/年)
    """
    # 式(4) 建築物エネルギー消費性能基準における単位住戸の1年当たりの基準一次エネルギー消費量（平成28年4月1日時点で現存する住宅） (MJ/年)
    E_star_ST_gn_du_e = get_E_star_ST_gn_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_ST_gn_du_e / 100) / 10


def get_E_star_ST_gn_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(3) 建築物エネルギー消費性能基準における単位住戸の1年当たりの基準一次エネルギー消費量（平成28年4月1日時点で現存しない住宅） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(3) 建築物エネルギー消費性能基準における単位住戸の1年当たりの基準一次エネルギー消費量（平成28年4月1日時点で現存しない住宅） (MJ/年)
    """
    return E_SH + E_SC + E_SV + E_SL + E_SW + E_SM


def get_E_star_ST_gn_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(4) 建築物エネルギー消費性能基準における単位住戸の1年当たりの基準一次エネルギー消費量（平成28年4月1日時点で現存する住宅） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(4) 建築物エネルギー消費性能基準における単位住戸の1年当たりの基準一次エネルギー消費量（平成28年4月1日時点で現存する住宅） (MJ/年)
    """
    return (E_SH + E_SC + E_SV + E_SL + E_SW) * 1.1 + E_SM


# ============================================================================
# 5.3 建築物エネルギー消費性能基準（気候風土適応住宅）における基準一次エネルギー消費量
# ============================================================================


def get_E_ST_trad_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(5) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の基準一次エネルギー消費量（平成28年4月1日時点で現存しない住宅） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(5) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の基準一次エネルギー消費量（平成28年4月1日時点で現存しない住宅） (GJ/年)
    """
    # 式(7) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの基準一次エネルギー消費量（平成28年4月1日時点で現存しない住宅） (MJ/年)
    E_star_ST_trad_du_p = get_E_star_ST_trad_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_ST_trad_du_p / 100) / 10


def get_E_ST_trad_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(6) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の基準一次エネルギー消費量（平成28年4月1日時点で現存する住宅） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(6) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の基準一次エネルギー消費量（平成28年4月1日時点で現存する住宅） (GJ/年)
    """
    # 式(8) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの基準一次エネルギー消費量（平成28年4月1日時点で現存する住宅） (MJ/年)
    E_star_ST_trad_du_e = get_E_star_ST_trad_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_ST_trad_du_e / 100) / 10


def get_E_star_ST_trad_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(7) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの基準一次エネルギー消費量（平成28年4月1日時点で現存しない住宅） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(7) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの基準一次エネルギー消費量（平成28年4月1日時点で現存しない住宅） (MJ/年)
    """
    return E_SH + E_SC + E_SV + E_SL + E_SW + E_SM


def get_E_star_ST_trad_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(8) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの基準一次エネルギー消費量（平成28年4月1日時点で現存する住宅） (MJ//年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(8) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの基準一次エネルギー消費量（平成28年4月1日時点で現存する住宅） (MJ/年)
    """
    return (E_SH + E_SC + E_SV + E_SL + E_SW) * 1.1 + E_SM


# ============================================================================
# 5.4 建築物エネルギー消費性能誘導基準における誘導基準一次エネルギー消費量
# ============================================================================

def get_E_ST_indc_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(9) 建築物エネルギー消費性能誘導基準における単位住戸の基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(9) 建築物エネルギー消費性能誘導基準における単位住戸の基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (GJ/年)
    """
    # 式(11) 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (MJ/年)
    E_star_ST_indc_du_p = get_E_star_ST_indc_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_ST_indc_du_p / 100) / 10


def get_E_ST_indc_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(10) 建築物エネルギー消費性能誘導基準における単位住戸の基準一次エネルギー消費量（令和4年10月1日時点で現存する住宅） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(10) 建築物エネルギー消費性能誘導基準における単位住戸の基準一次エネルギー消費量（令和4年10月1日時点で現存する住宅） (GJ/年)
    """
    # 式(12) 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの基準一次エネルギー消費量（令和4年10月1日時点で現存する住宅） (MJ/年)
    E_star_ST_indc_du_e = get_E_star_ST_indc_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_ST_indc_du_e / 100) / 10


def get_E_star_ST_indc_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(11) 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(11) 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (MJ/年)
    """
    return (E_SH + E_SC + E_SV + E_SL + E_SW) * 0.8 + E_SM


def get_E_star_ST_indc_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(12) 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(12) 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (MJ/年)
    """
    return E_SH + E_SC + E_SV + E_SL + E_SW + E_SM


# ============================================================================
# 5.5 特定建築主基準における基準一次エネルギー消費量
# ============================================================================

def get_E_ST_rb_du_cy1(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(13) 特定建築主基準における単位住戸の基準一次エネルギー消費量（令和2年3月までに新築する住宅） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(13) 特定建築主基準における単位住戸の基準一次エネルギー消費量（令和2年3月までに新築する住宅） (GJ/年)
    """
    # 式(15) 特定建築主基準における単位住戸の1年当たりの基準一次エネルギー消費量（令和2年3月までに新築する住宅 (MJ/年)
    E_star_ST_rb_du_cy1 = get_E_star_ST_rb_du_cy1(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_ST_rb_du_cy1 / 100) / 10


def get_E_ST_rb_du_cy2(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(14) 特定建築主基準における単位住戸の基準一次エネルギー消費量（令和2年4月以降に新築する住宅） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(14) 特定建築主基準における単位住戸の基準一次エネルギー消費量（令和2年4月以降に新築する住宅） (GJ/年)
    """
    # 式(16) 特定建築主基準における単位住戸の1年当たりの基準一次エネルギー消費量（令和2年4月以降に新築する住宅） (MJ/年)
    E_star_ST_rb_du_cy2 = get_E_star_ST_rb_du_cy2(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_ST_rb_du_cy2 / 100) / 10


def get_E_star_ST_rb_du_cy1(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(15) 特定建築主基準における1年当たりの一次エネルギー消費量（令和2年3月までに新築する住宅） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(15) 特定建築主基準における1年当たりの一次エネルギー消費量（令和2年3月までに新築する住宅） (MJ/年)
    """
    return (E_SH + E_SC + E_SV + E_SL + E_SW) * 0.9 + E_SM


def get_E_star_ST_rb_du_cy2(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(16) 特定建築主基準における1年当たりの一次エネルギー消費量（令和2年4月以降に新築する住宅） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(16) 特定建築主基準における1年当たりの一次エネルギー消費量（令和2年4月以降に新築する住宅） (MJ/年)
    """
    return (E_SH + E_SC + E_SV + E_SL + E_SW) * 0.85 + E_SM


# ============================================================================
# 5.6 建築物に係るエネルギーの使用の合理化の一層の促進その他の建築物の
#   低炭素化の促進のために誘導すべき基準（建築物の低炭素化誘導基準）における
#   誘導基準一次エネルギー消費量
# ============================================================================

def get_E_ST_lcb_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(17) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(17) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (GJ/年)
    """
    # 式(19) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における1年当たりの基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (MJ/年)
    E_star_ST_lcb_du_p = get_E_star_ST_lcb_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_ST_lcb_du_p / 100) / 10


def get_E_ST_lcb_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(18) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の基準一次エネルギー消費量（令和4年10月1日時点で現存する住宅） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(18) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の基準一次エネルギー消費量（令和4年10月1日時点で現存する住宅） (GJ/年)
    """
    # 式(20) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における1年当たりの基準一次エネルギー消費量（令和4年10月1日時点で現存する住宅） (MJ/年)
    E_star_ST_lcb_du_e = get_E_star_ST_lcb_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_ST_lcb_du_e / 100) / 10


def get_E_star_ST_lcb_du_p(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(19) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における1年当たりの基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(19) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における1年当たりの基準一次エネルギー消費量（令和4年10月1日時点で現存しない住宅） (MJ/年)
    """
    return (E_SH + E_SC + E_SV + E_SL + E_SW) * 0.8 + E_SM


def get_E_star_ST_lcb_du_e(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(20) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における1年当たりの基準一次エネルギー消費量（令和4年10月1日時点で現存する住宅） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(20) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における1年当たりの基準一次エネルギー消費量（令和4年10月1日時点で現存する住宅） (MJ/年)
    """
    return (E_SH + E_SC + E_SV + E_SL + E_SW) * 0.9 + E_SM


# ============================================================================
# 5.7 建築物に係るエネルギーの使用の合理化の一層の促進その他の建築物の
#   低炭素化の促進のために誘導すべき基準（建築物の低炭素化誘導基準）の
#   低炭素化措置における基準一次エネルギー消費量
# ============================================================================

def get_E_ST_enh_du(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(21) 建築物の低炭素化の促進のために誘導すべきその他の基準における単位住戸の基準一次エネルギー消費量 (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(21) 建築物の低炭素化の促進のために誘導すべきその他の基準における単位住戸の基準一次エネルギー消費量 (GJ/年)
    """
    # 式(22) 建築物の低炭素化の促進のために誘導すべきその他の基準における単位住戸の1年当たりの低基準一次エネルギー消費量 (MJ/年)
    E_star_ST_enh_du = get_E_star_ST_enh_du(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_star_ST_enh_du / 100) / 10


def get_E_star_ST_enh_du(E_SH, E_SC, E_SV, E_SL, E_SW, E_SM):
    """式(22) 建築物の低炭素化の促進のために誘導すべきその他の基準における単位住戸の1年当たりの低基準一次エネルギー消費量 (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        E_SM (float): 1年当たりのその他の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(22) 建築物の低炭素化の促進のために誘導すべきその他の基準における単位住戸の1年当たりの低基準一次エネルギー消費量 (MJ/年)
    """
    return (E_SH + E_SC + E_SV + E_SL + E_SW) * 0.5 + E_SM


# ============================================================================
# 6. 基準一次エネルギー消費量(その他の基準一次エネルギー消費量を除く)
# ============================================================================

def calc_E_dash_ST_dict(E_SH, E_SC, E_SV, E_SL, E_SW, type) -> StandardPrimaryEnergyTotalDash:
    """各適合基準における基準一次エネルギー消費量合計値(その他一次エネルギー消費量を除く)を算出する関数

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)
        type (str): 住宅の種類

    Returns:
        StandardPrimaryEnergyTotalDash: 各適合基準における基準一次エネルギー消費量合計値(その他一次エネルギー消費量を除く)を格納する辞書
    """
    E_dash_ST_gn_du = None
    E_dash_ST_trad_du = None
    E_dash_ST_indc_du = None
    E_dash_ST_rb_du = None
    E_dash_ST_lcb_du = None

    if type == '一般住宅':
        E_dash_ST_gn_du = get_E_dash_ST_gn_du(E_SH, E_SC, E_SV, E_SL, E_SW)
        E_dash_ST_indc_du = get_E_dash_ST_indc_du(E_SH, E_SC, E_SV, E_SL, E_SW)
        E_dash_ST_lcb_du = get_E_dash_ST_lcb_du(E_SH, E_SC, E_SV, E_SL, E_SW)
    elif type == '事業主基準':
        E_dash_ST_rb_du = get_E_dash_ST_rb_du(E_SH, E_SC, E_SV, E_SL, E_SW)
    elif type == '行政庁認定住宅':
        E_dash_ST_trad_du = get_E_dash_ST_trad_du(E_SH, E_SC, E_SV, E_SL, E_SW)
    else:
        raise ValueError(type)

    return {
        'E_dash_ST_gn_du': E_dash_ST_gn_du,
        'E_dash_ST_trad_du': E_dash_ST_trad_du,
        'E_dash_ST_indc_du': E_dash_ST_indc_du,
        'E_dash_ST_rb_du': E_dash_ST_rb_du,
        'E_dash_ST_lcb_du': E_dash_ST_lcb_du,
    }


# ====================================================================
# 6.2 建築物エネルギー消費性能基準（気候風土適応住宅を除く）における
#   基準一次エネルギー消費量(その他の基準一次エネルギー消費量を除く)
# ====================================================================

def get_E_dash_ST_gn_du(E_SH, E_SC, E_SV, E_SL, E_SW):
    """式(23) 建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(23) 建築物エネルギー消費性能基準における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)
    """
    # 式(24) 建築物エネルギー消費性能基準における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)
    E_dash_star_ST_gn_du = get_E_dash_star_ST_gn_du(E_SH, E_SC, E_SV, E_SL, E_SW)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_dash_star_ST_gn_du / 100) / 10


def get_E_dash_star_ST_gn_du(E_SH, E_SC, E_SV, E_SL, E_SW):
    """式(24) 建築物エネルギー消費性能基準における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(24) 建築物エネルギー消費性能基準における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)
    """
    return E_SH + E_SC + E_SV + E_SL + E_SW


# ============================================================================
# 6.3 建築物エネルギー消費性能基準（気候風土適応住宅）における
#   基準一次エネルギー消費量(その他の基準一次エネルギー消費量を除く)
# ============================================================================

def get_E_dash_ST_trad_du(E_SH, E_SC, E_SV, E_SL, E_SW):
    """式(25) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(25) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)
    """
    # 式(26) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)
    E_dash_star_ST_trad_du = get_E_dash_star_ST_trad_du(E_SH, E_SC, E_SV, E_SL, E_SW)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_dash_star_ST_trad_du / 100) / 10


def get_E_dash_star_ST_trad_du(E_SH, E_SC, E_SV, E_SL, E_SW):
    """式(26) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(26) 建築物エネルギー消費性能基準（気候風土適応住宅）における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)
    """
    return E_SH + E_SC + E_SV + E_SL + E_SW


# ============================================================================
# 6.4 建築物エネルギー消費性能誘導基準における誘導基準一次エネルギー消費量
#   (その他の基準一次エネルギー消費量を除く)
# ============================================================================

def get_E_dash_ST_indc_du(E_SH, E_SC, E_SV, E_SL, E_SW):
    """式(27) 建築物エネルギー消費性能誘導基準における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(27) 建築物エネルギー消費性能誘導基準における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)
    """
    # 式(28) 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)
    E_dash_star_ST_indc_du = get_E_dash_star_ST_indc_du(E_SH, E_SC, E_SV, E_SL, E_SW)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_dash_star_ST_indc_du / 100) / 10


def get_E_dash_star_ST_indc_du(E_SH, E_SC, E_SV, E_SL, E_SW):
    """式(28) 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(28) 建築物エネルギー消費性能誘導基準における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)
    """
    return E_SH + E_SC + E_SV + E_SL + E_SW


# ============================================================================
# 6.5 特定建築主基準における基準一次エネルギー消費量
#   (その他の基準一次エネルギー消費量を除く)
# ============================================================================

def get_E_dash_ST_rb_du(E_SH, E_SC, E_SV, E_SL, E_SW):
    """式(29) 特定建築主基準における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(29) 特定建築主基準における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)
    """
    # 式(30) 特定建築主基準における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)
    E_dash_star_ST_rb_du = get_E_dash_star_ST_rb_du(E_SH, E_SC, E_SV, E_SL, E_SW)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_dash_star_ST_rb_du / 100) / 10


def get_E_dash_star_ST_rb_du(E_SH, E_SC, E_SV, E_SL, E_SW):
    """式(30) 特定建築主基準における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(30) 特定建築主基準における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)
    """
    return E_SH + E_SC + E_SV + E_SL + E_SW


# ============================================================================
# 6.6 建築物に係るエネルギーの使用の合理化の一層の促進その他の建築物の
#   低炭素化の促進のために誘導すべき基準（建築物の低炭素化誘導基準）における
#   誘導基準一次エネルギー消費量(その他の基準一次エネルギー消費量を除く)
# ============================================================================

def get_E_dash_ST_lcb_du(E_SH, E_SC, E_SV, E_SL, E_SW):
    """式(31) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(31) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (GJ/年)
    """
    # 式(32) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)
    E_dash_star_ST_lcb_du = get_E_dash_star_ST_lcb_du(E_SH, E_SC, E_SV, E_SL, E_SW)

    # MJ -> GJ に変換 & 小数点以下一位未満の端数を切り上げ
    return ceil(E_dash_star_ST_lcb_du / 100) / 10


def get_E_dash_star_ST_lcb_du(E_SH, E_SC, E_SV, E_SL, E_SW):
    """式(32) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)

    Args:
        E_SH (float): 1年当たりの暖房設備の基準一次エネルギー消費量 (MJ/年)
        E_SC (float): 1年当たりの冷房設備の基準一次エネルギー消費量 (MJ/年)
        E_SV (float): 1年当たりの機械換気設備の基準一次エネルギー消費量 (MJ/年)
        E_SL (float): 1年当たりの照明設備の基準一次エネルギー消費量 (MJ/年)
        E_SW (float): 1年当たりの給湯設備(コージェネレーション設備を含む)の基準一次エネルギー消費量 (MJ/年)

    Returns:
        式(32) 建築物に係るエネルギーの使用の合理化の一層の促進のために誘導すべき基準における単位住戸の1年当たりの基準一次エネルギー消費量（その他の基準一次エネルギー消費量を除く） (MJ/年)
    """
    return E_SH + E_SC + E_SV + E_SL + E_SW


# ============================================================================
# 7. 暖房設備の基準一次エネルギー消費量
# ============================================================================


def calc_E_SH(type, tatekata, region, sol_region, A_A, A_MR, A_OR, ENV, mode_H, mode_C, NV_MR, NV_OR, H_MR, H_OR):
    """暖房設備の設計一次エネルギー消費量

    Args:
      type(str): description]
      tatekata(str): 建て方
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分(1-5)
      A_A(float): 床面積の合計 (m2)
      A_MR(float): 主たる居室の床面積 (m2)
      A_OR(float): その他の居室の床面積 (m2)
      ENV(dict): description]
      mode_H(str): 暖房方式
      mode_C(str): 冷房方式
      NV_MR(float): 主たる居室における通風の利用における相当換気回数
      NV_OR(float): その他の居室における通風の利用における相当換気回数
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様

    Returns:
      float: 暖房設備の設計一次エネルギー消費量

    """
    # 暖房基準値計算用仕様の取得
    mode_H, H_A, H_MR, H_OR, H_HS, mode_MR, mode_OR = calc_heating_reference_spec(region, mode_H, H_MR, H_OR)

    # 外皮の基準値計算用仕様の取得
    Q, eta_H, eta_C = calc_env_reference_spec(type, tatekata, region, A_A, ENV)

    # 暖房負荷の取得
    L_T_H_d_t_i, L_dash_H_R_d_t_i = calc_heating_load(
        region, sol_region,
        A_A, A_MR, A_OR,
        Q, eta_H, eta_C, NV_MR, NV_OR, None, None, None,
        None, mode_H, mode_C,
        H_MR, H_OR, mode_MR, mode_OR, None)

    L_CS_d_t_i, L_CL_d_t_i = calc_cooling_load(
        region, A_A, A_MR, A_OR,
        Q, eta_H, eta_C, NV_MR, NV_OR, None, None,
        mode_C, mode_H, mode_MR, mode_OR, None, None)

    if (ENV != None) and ('A_env' in ENV):
        A_env = ENV['A_env']
    else:
        A_env = None

    E_SH = calc_E_H(region, sol_region, A_A, A_MR, A_OR, A_env, eta_H, eta_C, Q, mode_H,
                  H_A, H_MR, H_OR, H_HS, mode_MR, mode_OR, None, None, None,
                  None, L_T_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i)

    return E_SH


def calc_heating_reference_spec(region, mode_H, H_MR, H_OR):
    """暖房設備の基準一次エネルギー消費量

    Args:
      region(int): 省エネルギー地域区分
      mode_H(str): 暖房方式
      H_MR(dict): 暖房機器の仕様
      H_OR(dict): 暖房機器の仕様

    Returns:
      tuple: mode_H, H_A, H_MR, H_OR, H_HS, mode_MR, mode_OR (暖房方式及び運転方法の区分)

    Raises:
      ValueError: mode_MRが「ろ」かつregion が 1-8 でない場合に発生
      ValueError: mode_MRが「は」かつregion が 1-8 でない場合に発生
      ValueError: mode_MRが「ろ」または「は」以外の場合に発生
      ValueError: mode_ORが「ろ」かつregion が 1-8 でない場合に発生
      ValueError: mode_ORが「は」かつregion が 1-8 でない場合に発生
      ValueError: mode_ORが「ろ」または「は」以外の場合に発生
      ValueError: mode_Hが「住戸全体を連続的に暖房する方式」または「」

    """
    if region == 8:
        return None, None, None, None, None, None, None

    if mode_H == '住戸全体を連続的に暖房する方式':
        H_A = {
            'type': 'ダクト式セントラル空調機',
            'duct_insulation': '全てもしくは一部が断熱区画外である',
            'VAV': False,
            'general_ventilation': True,
            'EquipmentSpec': '入力しない'
        }
        H_MR = None
        H_OR = None
        H_HS = None
    elif mode_H == '居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合' or \
            mode_H == '設置しない' or mode_H is None:

        # 実質的な暖房機器の仕様を取得
        spec_MR, spec_OR = get_virtual_heating_devices(region, H_MR, H_OR)
        if spec_MR is None and spec_OR is None:
            return None, None, None, None, None, None, None

        # 暖房方式及び運転方法の区分
        mode_MR, mode_OR = calc_heating_mode(region=region, H_MR=spec_MR, H_OR=spec_OR)

        H_A = None
        H_HS = None

        if mode_MR == 'ろ':
            if region in [1,2,3,4]:
                H_MR = {
                    'type': '温水暖房用パネルラジエーター',
                }
                H_HS = {
                    'type': '石油従来型温水暖房機',
                    'e_rtd_hs': 0.83,
                    'pipe_insulation': True,
                    'underfloor_pipe_insulation': False
                }
            elif region in [5,6,7]:
                H_MR = {
                    'type': '温水暖房用パネルラジエーター',
                }
                H_HS = {
                    'type': 'ガス従来型温水暖房機',
                    'e_rtd_hs': 0.825,
                    'pipe_insulation': True,
                    'underfloor_pipe_insulation': False
                }
            else:
                raise ValueError(region)
        elif mode_MR == 'は':
            if region in [1,2,3,4]:
                H_MR = {
                    'type': 'FF暖房機',
                    'e_rtd': 0.86
                }
            elif region in [5,6,7]:
                H_MR = {
                    'type': 'ルームエアコンディショナー',
                    'e_class': 'ろ',
                    'dualcompressor': False
                }
            else:
                raise ValueError(region)
        else:
            raise ValueError(mode_MR)

        if mode_OR == 'ろ':
            if region in [1,2,3,4]:
                H_OR = {
                    'type': '温水暖房用パネルラジエーター',
                }
                H_HS = {
                    'type': '石油従来型温水暖房機',
                    'e_rtd_hs': 0.83,
                    'pipe_insulation': True,
                    'underfloor_pipe_insulation': False
                }
            elif region in [5,6,7]:
                H_OR = {
                    'type': '温水暖房用パネルラジエーター',
                }
                H_HS = {
                    'type': 'ガス従来型温水暖房機',
                    'e_rtd_hs': 0.825,
                    'pipe_insulation': True,
                    'underfloor_pipe_insulation': False
                }
            else:
                raise ValueError(region)
        elif mode_OR == 'は':
            if region in [1,2,3,4]:
                H_OR = {
                    'type': 'FF暖房機',
                    'e_rtd': 0.86
                }
            elif region in [5,6,7]:
                H_OR = {
                    'type': 'ルームエアコンディショナー',
                    'e_class': 'ろ',
                    'dualcompressor': False
                }
            else:
                raise ValueError(region)
        elif mode_OR is None:
            pass
        else:
            raise ValueError(mode_OR)
    else:
        raise ValueError(mode_H)

    if mode_H is None:
        mode_H = '居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合'

    # 暖房方式及び運転方法の区分
    mode_MR, mode_OR = calc_heating_mode(region=region, H_MR=H_MR, H_OR=H_OR)

    return mode_H, H_A, H_MR, H_OR, H_HS, mode_MR, mode_OR


def calc_env_reference_spec(type, tatekata, region, A_A, ENV):
    """熱損失係数, 熱取得率（暖房）, 熱取得率（冷房）を計算する

    Args:
      type(str): description]
      tatekata(str): 建て方
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      ENV(dict): description]

    Returns:
      tuple: 熱損失係数, 熱取得率（暖房）, 熱取得率（冷房）

    """
    from pyhees.section3_1 import get_Q

    if ENV is None:
        return None, None, None

    if type != '行政庁認定住宅':
        from pyhees.section2_3_a import get_U_A, get_etr_A_H, get_etr_A_C

        U_A = get_U_A(tatekata, region)
        etr_A_H = get_etr_A_H(tatekata, region)
        etr_A_C = get_etr_A_C(tatekata, region)

        from pyhees.section3_2 import get_Q_dash, get_mu_H, get_mu_C

        if ENV['method'] == '当該住宅の外皮面積の合計を用いて評価する':
            A_env = ENV['A_env']
            r_env = A_env / A_A  # 床面積の合計に対する外皮の部位の面積の合計の比
        elif ENV['method'] == '簡易的に求めた外皮面積の合計を用いて評価する':
            from pyhees.section3_2_9 import get_A_dash_env, get_A_dash_A, get_r_env

            U_spec = ENV['U_spec']
            floor_bath_insulation = U_spec['floor_bath_insulation']

            A_dash_env = get_A_dash_env(ENV['house_insulation_type'], floor_bath_insulation)
            A_dash_A = get_A_dash_A()
            r_env = get_r_env(A_dash_env, A_dash_A)
        elif ENV['method'] == '当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法':
            from pyhees.section3_2_9 import get_A_dash_env, get_A_dash_A, get_r_env
            from pyhees.section3_2 import calc_insulation_performance

            U_spec = ENV['U_spec']
            floor_bath_insulation = U_spec['floor_bath_insulation']

            _, _, _, _, _, _, _, house_insulation_type = calc_insulation_performance(**ENV)
            A_dash_env = get_A_dash_env(house_insulation_type, floor_bath_insulation)
            A_dash_A = get_A_dash_A()
            r_env = get_r_env(A_dash_env, A_dash_A)

        Q_dash = get_Q_dash(U_A, r_env)

        mu_H = get_mu_H(etr_A_H, r_env)
        mu_C = get_mu_C(etr_A_C, r_env)
    else:
        from pyhees.section3_2 import calc_insulation_performance
        U_A, r_env, eta_A_H, eta_A_C, Q_dash, mu_H, mu_C,_ = calc_insulation_performance(**ENV)

    Q = get_Q(Q_dash)

    return Q, mu_H, mu_C


# ============================================================================
# 8. 冷房設備の基準一次エネルギー消費量
# ============================================================================

def calc_E_SC(type, tatekata, region, A_A, A_MR, A_OR, ENV, mode_C, mode_H, H_MR, H_OR, TS, HEX,
              sol_region, NV_MR, NV_OR):
    """1 年当たりの冷房設備の設計一次エネルギー消費量

    Args:
        type(str): description]
        tatekata(str): 建て方
        region(int): 省エネルギー地域区分
        A_A(float): 床面積の合計 (m2)
        A_MR(float): 主たる居室の床面積 (m2)
        A_OR(float): その他の居室の床面積 (m2)
        ENV(dict): description]
        mode_C(str): 冷房方式
        mode_H(str): 暖房方式
        H_MR(dict): 暖房機器の仕様
        H_OR(dict): 暖房機器の仕様
        TS(bool): 蓄熱の利用
        HEX(dict): 熱交換器型設備仕様辞書
        sol_region: param NV_MR:
        NV_OR: returns: 1 年当たりの冷房設備の設計一次エネルギー消費量
        NV_MR: 

    Returns:
        float: 1 年当たりの冷房設備の設計一次エネルギー消費量

    Raises:
        ValueError: mode_C が　「住戸全体を連続的に冷房する方式」または「居室のみを冷房する方式」でない場合に発生する

    """
    if ENV is None:
        return 0.0

    if mode_C == '住戸全体を連続的に冷房する方式':
        C_A = {
            'type': 'ダクト式セントラル空調機',
            'duct_insulation': '全てもしくは一部が断熱区画外である',
            'VAV': False,
            'general_ventilation': True,
            'EquipmentSpec': '入力しない'
        }
        C_MR = None
        C_OR = None
    elif mode_C == '居室のみを冷房する方式' or mode_C == '設置しない' or mode_C is None:
        C_A = None
        C_MR = {
            'type': 'ルームエアコンディショナー',
            'e_class': 'ろ',
            'dualcompressor': False
        }
        C_OR = {
            'type': 'ルームエアコンディショナー',
            'e_class': 'ろ',
            'dualcompressor': False
        }
    else:
        raise ValueError(mode_C)

    if mode_C is None:
        mode_C = '居室のみを冷房する方式'

    # 暖房基準値計算用仕様の取得
    mode_H, H_A, H_MR, H_OR, H_HS, mode_MR, mode_OR = calc_heating_reference_spec(region, mode_H, H_MR, H_OR)

    # 外皮の基準値計算用仕様の取得
    Q, eta_H, eta_C = calc_env_reference_spec(type, tatekata, region, A_A, ENV)

    # 暖房負荷の取得
    L_T_H_d_t_i, L_dash_H_R_d_t_i = calc_heating_load(
        region, sol_region,
        A_A, A_MR, A_OR,
        Q, eta_H, eta_C, NV_MR, NV_OR, None, None, None,
        None, mode_H, mode_C,
        H_MR, H_OR, mode_MR, mode_OR, None)

    # 冷房負荷の計算
    L_CS_d_t, L_CL_d_t = calc_cooling_load(
        region=region,
        A_A=A_A,
        A_MR=A_MR,
        A_OR=A_OR,
        Q=Q,
        mu_C=eta_C,
        mu_H=eta_H,
        # 通風なし
        NV_MR=0,
        NV_OR=0,
        # 床下換気なし
        r_A_ufvnt=None,
        underfloor_insulation=None,
        mode_C=mode_C,
        mode_H=mode_H,
        mode_MR=mode_MR,
        mode_OR=mode_OR,
        TS=TS,
        HEX=HEX
    )

    if 'A_env' in ENV:
        A_env = ENV['A_env']
    else:
        A_env = None

    # 1 年当たりの冷房設備の設計一次エネルギー消費量
    E_SC = calc_E_C(region, A_A, A_MR, A_OR, A_env, eta_H, eta_C, Q, C_A, C_MR, C_OR, L_T_H_d_t_i, L_CS_d_t, L_CL_d_t, mode_C)

    return E_SC


# ============================================================================
# 9. 機械換気設備の基準一次エネルギー消費量
# ============================================================================


# 1年あたりの機械換気設備の基準一次エネルギー消費量 (37)
def calc_E_SV(A_A):
    """1年あたりの機械換気設備の基準一次エネルギー消費量 (37)

    Args:
      A_A(float): 床面積の合計(付録Aによる定まる値) (m2)

    Returns:
      float: 1年あたりの機械換気設備の基準一次エネルギー消費量 (MJ/年)

    """
    # 係数 a_SV, b_SV
    a_SV, b_SV = get_table5_coeff(A_A)

    # 1年あたりの機械換気設備の基準一次エネルギー消費量 (37)
    E_SV = get_E_SV(A_A, a_SV, b_SV)

    return E_SV


# 1年あたりの機械換気設備の基準一次エネルギー消費量 (37)
def get_E_SV(A_A, a_SV, b_SV):
    """1年あたりの機械換気設備の基準一次エネルギー消費量 (37)

    Args:
      A_A: 床面積の合計 (m2)
      a_SV: 係数 (MJ/(m2・年))
      b_SV: 係数 (MJ/年)

    Returns:
      1年あたりの機械換気設備の基準一次エネルギー消費量 (MJ/年)

    """
    E_SV = a_SV * A_A + b_SV
    return E_SV


def get_table5_coeff(A_A):
    """その他の一次エネルギー消費量の算出に用いる表5の係数を取得

    Args:
      A_A(float): 床面積の合計 (m2)

    Returns:
      tuple: 係数 a_SV, b_SV

    """

    # その他の一次エネルギー消費量の算出に用いる係数
    table_5 = [
        (33, 38, 33),
        (129, -21, 579)
    ]
    if A_A < 30:
        index = 0
    elif A_A < 120:
        index = 1
    else:
        index = 2

    a_SV = table_5[0][index]
    b_SV = table_5[1][index]

    return a_SV, b_SV


# ============================================================================
# 10. 照明の基準一次エネルギー消費量
# ============================================================================

# 1年あたりの照明の基準一次エネルギー消費量 (38)
def calc_E_SL(A_A, A_MR, A_OR):
    """1年あたりの照明の基準一次エネルギー消費量 (38)

    Args:
        A_A(float): 床面積の合計(付録Aによる定まる値) (m2)
        A_MR(float): 主たる居室の床面積の合計(付録Aによる定まる値) (m2)
        A_OR(float): その他の居室の床面積の合計(付録Aによる定まる値) (m2)

    Returns:
        float: 1年あたりの照明の基準一次エネルギー消費量 (MJ/年)

    """
    E_SL = get_E_SL(A_A, A_MR, A_OR)
    return E_SL


# 1年あたりの照明の基準一次エネルギー消費量 (38)
def get_E_SL(A_A, A_MR, A_OR):
    """1年あたりの照明の基準一次エネルギー消費量 (38)

    Args:
        A_A(float): 床面積の合計(付録Aによる定まる値) (m2)
        A_MR(float): 主たる居室の床面積の合計(付録Aによる定まる値) (m2)
        A_OR(float): その他の居室の床面積の合計(付録Aによる定まる値) (m2)

    Returns:
        float: 1年あたりの照明の基準一次エネルギー消費量 (MJ/年)

    """
    E_SL = 31 * A_A + 169 * A_MR + 39 * A_OR
    return E_SL


# ============================================================================
# 11. 給湯設備及びコージェネレーション設備の基準一次エネルギー消費量
# ============================================================================

# 1年当たりの給湯設備の設計一次エネルギー消費量 (39)
def calc_E_SW(region, A_A, HW):
    """1年当たりの給湯設備の設計一次エネルギー消費量 (39)

    Args:
        region(int): 省エネルギー地域区分
        A_A(float): 床面積の合計 (m2)
        HW(dict): 給湯機の仕様

    Returns:
        float: 1年当たりの給湯設備の設計一次エネルギー消費量 (39)

    """
    if HW is None or HW['hw_type'] is None:
        return 0.0
    else:
        a_SW, b_SW = get_table6_coeff(region, A_A, HW['has_bath'])
        E_SW = get_E_SW(A_A, a_SW, b_SW)
        return E_SW


# 1年当たりの給湯設備の設計一次エネルギー消費量 (39)
def get_E_SW(A_A, a_SW, b_SW):
    """1年当たりの給湯設備の設計一次エネルギー消費量 (39)

    Args:
        A_A(float): 床面積の合計 (m2)
        a_SW(float): 表6 給湯設備の一次エネルギー消費量の算出に用いる係数
        b_SW(float): 表6 給湯設備の一次エネルギー消費量の算出に用いる係数

    Returns:
        float: 1年当たりの給湯設備の設計一次エネルギー消費量 (39)

    """
    if a_SW is None:
        E_SW = b_SW
    else:
        E_SW = a_SW * A_A + b_SW
    return E_SW


def get_table6_coeff(region, A_A, has_bath):
    """表6 給湯設備の一次エネルギー消費量の算出に用いる係数

    Args:
      region(int): 省エネルギー地域区分
      A_A(float): 床面積の合計 (m2)
      has_bath(bool): バスが存在するかどうか

    Returns:
      tuple: 給湯設備の一次エネルギー消費量の算出に用いる係数a_SW, b_SW

    """

    # 表6 給湯設備の一次エネルギー消費量の算出に用いる係数
    table_6 = [
        (None, 234, 307, 109, None),
        (11946, 4926, 546, 18366, 31446),
        (None, 32, 78, 15, None),
        (4835, 3875, 1115, 6785, 8585),
        (None, 228, 300, 107, None),
        (11696, 4856, 536, 17906, 30746),
        (None, 32, 77, 15, None),
        (4742, 3782, 1082, 6662, 8462),
        (None, 212, 280, 100, None),
        (10892, 4532, 452, 16652, 28652),
        (None, 30, 72, 14, None),
        (4442, 3542, 1022, 6242, 7922),
        (None, 205, 272, 97, None),
        (10575, 4425, 405, 16155, 27795),
        (None, 29, 70, 13, None),
        (4321, 3451, 991, 6121, 7681),
        (None, 200, 276, 103, None),
        (10440, 4440, -120, 15450, 27810),
        (None, 29, 71, 14, None),
        (4165, 3295, 775, 5905, 7585),
        (None, 181, 249, 93, None),
        (9401, 3971, -109, 13931, 25091),
        (None, 26, 64, 12, None),
        (3755, 2975, 695, 5375, 6815),
        (None, 165, 227, 85, None),
        (8499, 3549, -171, 12609, 22809),
        (None, 23, 57, 11, None),
        (3402, 2712, 672, 4812, 6132),
        (None, 130, 178, 67, None),
        (6672, 2772, -108, 9882, 17922),
        (None, 18, 45, 9, None),
        (2679, 2139, 519, 3759, 4839)
    ]

    row_index = (region - 1) * 4 + (0 if has_bath else 2)
    column_index = min(4, floor(A_A / 30))
    a_SW = table_6[row_index][column_index]
    b_SW = table_6[row_index + 1][column_index]
    return a_SW, b_SW


# ============================================================================
# 12. その他の基準一次エネルギー消費量
# ============================================================================

# 1年あたりのその他の基準一次エネルギー消費量 (40)
def calc_E_SM(A_A):
    """1年あたりのその他の基準一次エネルギー消費量 (40)

    Args:
        A_A(float): 床面積の合計(付録Aによる定まる値) (m2)

    Returns:
        float: 1年あたりのその他の基準一次エネルギー消費量 (MJ/年)

    """
    # 係数 a_SM, b_SM
    a_SM, b_SM = get_table7_coeff(A_A)

    # 1年あたりのその他の基準一次エネルギー消費量 (40)
    E_SM = get_E_SM(A_A, a_SM, b_SM)

    return E_SM


# 1年あたりのその他の基準一次エネルギー消費量 (40)
def get_E_SM(A_A, a_SM, b_SM):
    """1年あたりのその他の基準一次エネルギー消費量 (40)

    Args:
        A_A(float): 床面積の合計 (m2)
        a_SM(float): 係数 (MJ/(m2・年))
        b_SM(float): 係数 (MJ/年)

    Returns:
        float: 1年あたりのその他の基準一次エネルギー消費量 (MJ/年)

    """
    E_SM = a_SM * A_A + b_SM
    return E_SM


def get_table7_coeff(A_A):
    """その他の一次エネルギー消費量の算出に用いる係数

    Args:
        A_A(float): 床面積の合計 (m2)

    Returns:
        tuple: 係数 a_SM, b_SM

    """
    # その他の一次エネルギー消費量の算出に用いる係数
    table_7 = [
        (0, 87.63, 166.71, 47.64, 0),
        (12181.13, 9552.23, 4807.43, 15523.73, 21240.53)
    ]

    index = min(4, floor(A_A / 30))
    a_SM = table_7[0][index]
    b_SM = table_7[1][index]
    return a_SM, b_SM

