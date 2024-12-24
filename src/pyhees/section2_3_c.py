# 付録 C 冷房設備の基準一次エネルギー消費量の算定に係る設定

import pyhees.section11_7 as sc11_7


def get_reference_spec_C(region, mode_C, C_MR_in, C_OR_in):
    """冷房設備の基準一次エネルギー消費量の算定に係る設定 を取得する関数

    Args:
        region (int): 省エネルギー地域区分
        mode_C (str): 冷房方式 '住戸全体を連続的に冷房する方式', '居室のみを冷房する方式'
        C_MR_in (dict): 主たる居室の冷房機器の仕様(入力値)
        C_OR_in (dict): その他の居室の冷房機器の仕様(入力値)

    Returns:
        C_A (dict): 住戸全体を連続的に冷房する方式における冷房機器の仕様
        C_MR (dict): 主たる居室の冷房機器の仕様
        C_OR (dict): その他の居室の冷房機器の仕様
    """
    # 第十一章「その他」第七節「基準設定仕様」を適用する。
    return sc11_7.get_reference_spec_C(region, mode_C, C_MR_in, C_OR_in)
