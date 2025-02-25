# ============================================================================
# 付録 E 基準設定仕様による各設備の設計一次エネルギー消費量の算定に係る設定
# ============================================================================

import pyhees.section11_7 as sc11_7


# ============================================================================
# E.3 暖房設備
# ============================================================================

def get_spec_H(region, mode_H):
    """基準設定仕様による暖房設備の設計一次エネルギー消費量の算定に係る設定 を取得する関数

    Args:
        region (int): 省エネルギー地域区分
        mode_H (str): 暖房方式 '住戸全体を連続的に暖房する方式', '居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合'

    Returns:
        H_A (dict): 住戸全体を連続的に暖房する方式における暖房機器の基準設定仕様
        H_MR (dict): 主たる居室の暖房機器の基準設定仕様
        H_OR (dict): その他の居室の暖房機器の基準設定仕様
        H_HS (dict): 温水暖房機の基準設定仕様
    """
    if region == 8:
        return None, None, None, None

    # 暖房方式が「居室のみを暖房する方式」である場合、運転方法は1地域および2地域については「連続運転」とし、3地域～7地域については「間歇運転」とする。
    match (mode_H, region):
        case ('住戸全体を連続的に暖房する方式', _):
            operating_mode_XR = None
        case ('居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合', _region) if _region in [1, 2]:
            operating_mode_XR = '連続'
        case ('居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合', _region) if _region in [3, 4, 5, 6, 7]:
            operating_mode_XR = '間歇'
        case _:
            raise NotImplementedError()

    return sc11_7.get_reference_spec_H(region, mode_H,
                                       H_MR_in=None, H_OR_in=None,
                                       operating_mode_MR=operating_mode_XR,
                                       operating_mode_OR=operating_mode_XR)


# ============================================================================
# E.4 冷房設備
# ============================================================================

def get_spec_C(region, mode_C):
    """基準設定仕様による冷房設備の設計一次エネルギー消費量の算定に係る設定 を取得する関数

    Args:
        region (int): 省エネルギー地域区分
        mode_C (str): 冷房方式 '住戸全体を連続的に冷房する方式', '居室のみを冷房する方式'

    Returns:
        C_A (dict): 住戸全体を連続的に冷房する方式における冷房機器の基準設定仕様
        C_MR (dict): 主たる居室の冷房機器の基準設定仕様
        C_OR (dict): その他の居室の冷房機器の基準設定仕様
    """
    # 冷房方式が「居室のみを冷房する方式」である場合、運転方法は「間歇運転」とする。
    match mode_C:
        case '住戸全体を連続的に冷房する方式':
            operating_mode_XR = None
        case '居室のみを冷房する方式':
            operating_mode_XR = '間歇'
        case _:
            raise NotImplementedError()

    return sc11_7.get_reference_spec_C(region, mode_C,
                                       C_MR_in=None, C_OR_in=None,
                                       operating_mode_MR=operating_mode_XR,
                                       operating_mode_OR=operating_mode_XR)


# ============================================================================
# E.5 機械換気設備
# ============================================================================

def get_spec_V():
    """基準設定仕様による機械換気設備の設計一次エネルギー消費量の算定に係る設定 を取得する関数

    Returns:
        V (dict): 機械換気設備の基準設定仕様
    """
    return sc11_7.get_reference_spec_V()


# ============================================================================
# E.6 照明設備
# ============================================================================

def get_spec_L():
    """基準設定仕様による照明設備の設計一次エネルギー消費量の算定に係る設定 を取得する関数

    Returns:
        L_MR (dict): 主たる居室における照明設備の基準設定仕様
        L_OR (dict): その他の居室における照明設備の基準設定仕様
        L_NO (dict): 非居室における照明設備の基準設定仕様
    """
    spec_L_MR = sc11_7.get_reference_spec_L('主たる居室')
    spec_L_OR = sc11_7.get_reference_spec_L('その他の居室')
    spec_L_NO = sc11_7.get_reference_spec_L('非居室')

    return spec_L_MR, spec_L_OR, spec_L_NO


# ============================================================================
# E.7 給湯設備
# ============================================================================

def get_spec_HW(region):
    """基準設定仕様による給湯設備の設計一次エネルギー消費量の算定に係る設定 を取得する関数

    Args:
        region (int): 省エネルギー地域区分

    Returns:
        HW (dict): 給湯設備の基準設定仕様
    """
    return sc11_7.get_reference_spec_HW(region)
