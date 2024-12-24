# 付録 B 暖房設備の基準一次エネルギー消費量の算定に係る設定

import pyhees.section11_7 as sc11_7


def get_reference_spec_H(region, mode_H, H_MR_in, H_OR_in):
    """暖房設備の基準一次エネルギー消費量の算定に係る設定 を取得する関数

    Args:
        region (int): 省エネルギー地域区分
        mode_H (str): 暖房方式 '住戸全体を連続的に暖房する方式', '居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合'
        H_MR_in (dict): 主たる居室の暖房機器の仕様(入力値)
        H_OR_in (dict): その他の居室の暖房機器の仕様(入力値)

    Returns:
        H_A (dict): 住戸全体を連続的に暖房する方式における暖房機器の仕様
        H_MR (dict): 主たる居室の暖房機器の仕様
        H_OR (dict): その他の居室の暖房機器の仕様
        H_HS (dict): 温水暖房機の仕様
    """
    if region == 8:
        return None, None, None, None

    # 第十一章「その他」第七節「基準設定仕様」を適用する。
    return sc11_7.get_reference_spec_H(region, mode_H, H_MR_in, H_OR_in)
