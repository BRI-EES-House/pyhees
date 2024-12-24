# ============================================================================
# 付録 A 各設備の設計一次エネルギー消費量の算定に係る設定
# ============================================================================

import pyhees.section3_2_9 as sc3_2_9


# ============================================================================
# A.2.2 床面積の合計・主たる居室の床面積・その他の居室の床面積
# ============================================================================

def get_A(spec):
    """床面積の合計、主たる居室の床面積およびその他の居室の床面積 を取得する関数

    Args:
        spec (dict): 住戸についての詳細なデータ

    Returns:
        A_A (float): 床面積の合計 (m2)
        A_MR (float): 主たる居室の床面積 (m2)
        A_OR (float): その他の居室の床面積 (m2)
    """
    A_A  = spec['A_A']
    A_MR = spec['A_MR']
    A_OR = spec['A_OR']

    return A_A, A_MR, A_OR


# ============================================================================
# A.2.4 外皮平均熱貫流率・平均日射熱取得率
# ============================================================================

def get_U_A_and_eta_A(tatekata, region, ENV):
    """外皮平均熱貫流率および平均日射熱取得率 を取得する関数

    Args:
        tatekata (str): 建て方
        region (int): 省エネルギー地域区分
        ENV (dict): 外皮仕様辞書

    Returns:
        U_A (float): 外皮平均熱貫流率
        eta_A_H (float): 暖房期の平均日射熱取得率
        eta_A_C (float): 冷房期の平均日射熱取得率
    """
    if ENV['method'] == '当該住宅の外皮面積の合計を用いて評価する':
        U_A     = ENV['U_A']
        eta_A_H = ENV['eta_A_H']
        eta_A_C = ENV['eta_A_C']

    elif ENV['method'] in ['仕様基準により外皮性能を評価する方法',
                           '誘導仕様基準により外皮性能を評価する方法（住戸全体を対象に評価）']:
        U_A     = sc3_2_9.get_U_A(ENV['method'], tatekata, region)
        eta_A_H = sc3_2_9.get_eta_A_H(ENV['method'], tatekata, region)
        eta_A_C = sc3_2_9.get_eta_A_C(ENV['method'], tatekata, region)

    else:
        raise ValueError(ENV['method'])

    return U_A, eta_A_H, eta_A_C
