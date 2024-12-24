# ============================================================================
# 付録 B 設置する冷房設備機器の種類に応じた冷房方式及び運転方法の決定方法 並びに評価上想定される冷房設備機器の種類
# ============================================================================


def calc_cooling_mode(C_A=None, C_MR=None, C_OR=None):
    """冷房方式及び運転方法の区分を取得する

    Args:
      C_A(dict, optional): 冷房方式 (Default value = None)
      C_MR(dict, optional): 主たる居室の冷房機器の仕様 (Default value = None)
      C_OR(dict, optional): その他の居室の冷房機器の仕様 (Default value = None)

    Returns:
      tuple(str, str): 冷房方式及び運転方法の区分

    """
    if C_A is None:

        if C_MR is None and C_OR is None:
            return None, None

        def to_roha(s):
            """

            Args:
              s: 

            Returns:

            """
            if type(s) is tuple:
                return (to_roha(s[0]), to_roha(s[1]))
            else:
                if s == '連続':
                    return 'ろ'
                elif s == '間歇':
                    return 'は'
                else:
                    raise ValueError(s)

        if C_OR is not None:
            return to_roha(('間歇', '間歇'))
        else:
            return to_roha('間歇'), None

    if C_A['type'] == 'ダクト式セントラル空調機':
        # 住宅全体を連続的に冷房する方式
        return 'い'

    else:
        raise ValueError(C_A['type'])


# 主たる居室、その他の居室に冷房設備機器を設置しない場合又
# はルームエアコンディショナー以外の冷房設備機器を設置する場合は、
# ルームエアコンディショナーが設置されたものとして評価する。
# その際、ルームエ アコンディショナーのエネルギー消費効率の区分は
# 区分（ろ）とする。
def get_default_cooling_spec():
    """主たる居室、その他の居室に冷房設備機器を設置しない場合又はルームエアコンディショナー以外の冷房設備機器を設置する場合の評価上想定される冷房房設備機器等の種を取得する

    Args:

    Returns:
      dict: 冷房房設備機器等の種

    """
    return {
        'type': 'ルームエアコンディショナー',
        'e_class': 'ろ',
        'dualcompressor': False,
    }
