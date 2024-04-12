# ============================================================================
# 付録D 設置する給湯設備の種類
# ============================================================================

def is_installed_hw_type(hw_connection_type, hw_type):
    """液体集熱式太陽熱利用設備と併用する給湯設備の確認

    Args:
      hw_connection_type(str): 給湯接続方式の種類 (-)
      hw_type(str): 給湯機／給湯温水暖房機の種類

    Returns:
    """
    flag = False
    if hw_connection_type in ["接続ユニット方式", "三方弁方式", "給水予熱方式"]:
        flag = hw_type != '電気ヒートポンプ給湯機'
    elif hw_connection_type == "浴槽落とし込み方式":
        flag = hw_type in ['ガス従来型給湯機', 'ガス従来型給湯温水暖房機',
            'ガス潜熱回収型給湯機', 'ガス潜熱回収型給湯温水暖房機',
            '石油従来型給湯機', '石油従来型給湯温水暖房機',
            '石油潜熱回収型給湯機', '石油潜熱回収型給湯温水暖房機']
    else:
        raise ValueError(hw_connection_type)

    if not flag:
        raise Exception("液体集熱式太陽熱利用設備と併用する給湯設備ではありません。")
