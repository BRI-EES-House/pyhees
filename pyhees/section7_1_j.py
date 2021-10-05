# ============================================================================
# 付録 J 節湯の効果係数
# ============================================================================

import numpy as np


def get_f_sk(kitchen_watersaving_A, kitchen_watersaving_C, Theta_wtr_d):
    """# 台所水栓における節湯の効果係数 (1a)

    Args:
      kitchen_watersaving_A(bool): 台所水栓の手元止水機能の有無
      kitchen_watersaving_C(bool): 台所水栓の水優先吐水機能の有無
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      float: 台所水栓における節湯の効果係数 (-)

    """
    return get_f_sk_A(kitchen_watersaving_A) * get_f_sk_C(kitchen_watersaving_C, Theta_wtr_d)


def get_f_ss(shower_watersaving_A, shower_watersaving_B):
    """# 浴室シャワー水栓における節湯の効果係数 (1b)

    Args:
      shower_watersaving_A(bool): 浴室シャワー水栓の手元止水機能の有無
      shower_watersaving_B(bool): 浴室シャワー水栓の小流量吐水機能の有無

    Returns:
      float: 浴室シャワー水栓における節湯の効果係数 (-)

    """
    return get_f_ss_A(shower_watersaving_A) * get_f_ss_B(shower_watersaving_B)


def get_f_sw(washbowl_watersaving_C, Theta_wtr_d):
    """# 洗面水栓における節湯の効果係数 (1c)

    Args:
      washbowl_watersaving_C(bool): 洗面水栓の水優先吐水機能の有無
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      float: 洗面水栓における節湯の効果係数 (-)

    """
    return get_f_sw_C(washbowl_watersaving_C, Theta_wtr_d)


def get_f_sk_A(kitchen_watersaving_A):
    """# 台所水栓の手元止水機能における節湯の効果係数

    Args:
      kitchen_watersaving_A(ndarray): 台所水栓の手元止水機能の有無

    Returns:
      float: 台所水栓の手元止水機能における節湯の効果係数 (-)

    """
    if kitchen_watersaving_A:
        return get_table_j_1()[0]
    else:
        return get_table_j_1()[1]


def get_f_sk_C(kitchen_watersaving_C, Theta_wtr_d):
    """# 台所水栓の水優先吐水水機能における節湯の効果係数

    Args:
      kitchen_watersaving_C(bool): 台所水栓の手元止水機能の有無
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: 台所水栓の水優先吐水機能における節湯の効果係数 (-)

    """
    f_sk_C_d = np.ones(365)

    if kitchen_watersaving_C:
        f_sk_C_d[Theta_wtr_d > 18] = get_table_j_1()[2]

    return f_sk_C_d

def get_f_ss_A(bathshower_watersaving_A):
    """# 浴室シャワー水栓の手元止水機能における節湯の効果係数

    Args:
      bathshower_watersaving_A(bool): 浴室シャワー水栓の手元止水機能の有無

    Returns:
      float: 浴室シャワー水栓の手元止水機能における節湯の効果係数 (-)

    """
    if bathshower_watersaving_A:
        return get_table_j_1()[5]
    else:
        return get_table_j_1()[6]


def get_f_ss_B(bathshower_watersaving_B):
    """# 浴室シャワー水栓の小流量吐水機能における節湯の効果係数

    Args:
      bathshower_watersaving_B(bool): 浴室シャワー水栓の小流量吐水機能の有無

    Returns:
      float: 浴室シャワー水栓の小流量吐水機能における節湯の効果係数 (-)

    """
    if bathshower_watersaving_B:
        return get_table_j_1()[7]
    else:
        return get_table_j_1()[8]


def get_f_sw_C(washbowl_watersaving_C, Theta_wtr_d):
    """# 洗面水栓の水優先吐水機能における節湯の保温効果係数

    Args:
      washbowl_watersaving_C(bool): 洗面水栓の水優先吐水機能の有無
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: 洗面水栓の水優先吐水機能における節湯の効果係数 (-)

    """
    f_sw_C_d = np.ones(365)

    if washbowl_watersaving_C:
        f_sw_C_d[Theta_wtr_d > 18] = get_table_j_1()[9]

    return f_sw_C_d


def get_f_sp(pipe_diameter):
    """# 配管のヘッダー分岐後の径における節湯の保温効果係数

    Args:
      pipe_diameter(str): ヘッダー分岐後の径

    Returns:
      float: 配管のヘッダー分岐後の径におけるせゆつの保温効果係数 (-)

    """
    if pipe_diameter == 'ヘッダーにより台所水栓・シャワー水栓・洗面水栓に分岐され、かつ分岐後の配管すべての径が13A以下であるもの':
        return get_table_j_1()[12]
    elif pipe_diameter == '上記以外':
        return get_table_j_1()[13]
    else:
        raise ValueError()


def get_f_sb():
    """# 浴槽の保温効果係数

    Args:

    Returns:
      float: 浴槽の保温効果係数

    """
    return get_table_j_1()[14]


def get_table_j_1():
    """表J.1 節湯の効果係数

    Args:

    Returns:
      list: 表J.1 節湯の効果係数

    """
    # 表J.1 節湯の効果係数
    table_j_1 = [
        # f_sk_A
        0.91,
        1.00,
        # f_sk_C
        0.70,
        1.00,
        1.00,
        # f_ss_A
        0.80,
        1.00,
        # f_ss_B
        0.85,
        1.00,
        # f_sw_C
        0.70,
        1.00,
        1.00,
        # f_sp
        0.95,
        1.00,
        # f_sb
        1.00
    ]
    return table_j_1


# ============================================================================
# デバッグ用コード
# ============================================================================
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
    import pandas as pd
    import numpy as np
    from pyhees.section2_2 import calc_E_W
    from pyhees.section3_1 import get_Q
    from pyhees.section3_2 import calc_r_env, get_Q_dash, get_eta_H, get_eta_C

    # ---------- 基本情報の設定 ----------

    # 床面積
    A_A = 120.08
    A_MR = 29.81
    A_OR = 51.34
    # 地域区分
    region_array = np.array([1, 2, 3, 4, 5, 6, 7, 8])
    # 年間日射地域区分
    sol_region = None

    # ---------- 外皮の設定 ----------

    # 外皮面積の合計
    A_env = 307.51
    # 外皮平均熱貫流率(UA値)
    U_A = 0.87
    # 日射取得係数
    eta_A_H = 4.3
    eta_A_C = 2.8
    # 自然風の利用 主たる居室
    NV_MR = 0
    # 自然風の利用 その他居室
    NV_OR = 0
    # 蓄熱
    TS = False
    # 床下空間を経由して外気を導入する換気方式の利用
    r_A_ufvnt = None
    # 床下空間の断熱
    underfloor_insulation = None

    # ---------- 暖冷房の設定 ----------

    # 暖房方式
    mode_H = '設置しない'
    # 住戸全体を暖房する
    H_A = None
    # 主たる居室暖房機器
    H_MR = {'type': '設置しない'}
    # その他居室暖房機器
    H_OR = {'type': '設置しない'}
    # 温水暖房機の種類
    H_HS = None

    # 冷房方式
    mode_C = '設置しない'
    # 住戸全体を冷房する
    C_A = None
    # 主たる居室冷房機器
    C_MR = {'type': '設置しない'}
    # その他居室冷房機器
    C_OR = {'type': '設置しない'}

    # ---------- 給湯設備の設定 ----------

    # ガス従来型給湯機
    GasClassic = {
        'hw_type': 'ガス従来型給湯機',
        'e_rtd': 70.4 / 100,
        'hybrid_category': None
    }

    # ガス潜熱回収型給湯機
    GasLatentHeatRecovery = {
        'hw_type': 'ガス潜熱回収型給湯機',
        'e_rtd': 83.6 / 100,
        'hybrid_category': None
    }

    # 石油従来型給湯機
    OilClassic = {
        'hw_type': '石油従来型給湯機',
        'e_rtd': 77.9 / 100,
        'hybrid_category': None
    }

    # 石油潜熱回収型給湯機
    OilLatentHeatRecovery = {
        'hw_type': '石油潜熱回収型給湯機',
        'e_rtd': 81.9 / 100,
        'hybrid_category':  None
    }

    # 電気ヒートポンプ給湯機（CO2冷媒）
    ElectricHeatPump = {
        'hw_type': '電気ヒートポンプ給湯機',
        'e_rtd': 2.7,
        'hybrid_category': None
    }

    # 電気ヒートポンプ・ガス併用型給湯機：品番を入力しない→フロン系冷媒→タンク容量(小)
    Hybrid = {
        'hw_type': '電気ヒートポンプ・ガス併用型給湯機(仕様による)',
        'e_rtd': None,
        'hybrid_category': '区分1'
    }

    # 熱源機(給湯専用型)の種類
    hw_array = np.array([GasClassic, GasLatentHeatRecovery, OilClassic,
                        OilLatentHeatRecovery, ElectricHeatPump, Hybrid,
                        GasClassic, GasLatentHeatRecovery, OilClassic,
                        OilLatentHeatRecovery, ElectricHeatPump, Hybrid])

    # 洗面：水優先吐水機能
    washbowl_watersaving_C_array = np.array([True, True, True, True, True, True,
                                             False, False, False, False, False, False])

    # 給湯設備全体
    HW = {
        # 給湯設備・浴室等の有無
        'has_bath': True,
        # 熱源機(給湯専用型)の種類
        'hw_type': None,
        # モード熱効率
        'e_rtd': None,
        # エネルギー消費効率
        'e_dash_rtd': None,
        # 電気ヒートポンプ・ガス併用型給湯機(仕様による)の場合の区分
        'hybrid_category': None,

        # ふろ機能の種類
        'bath_function': 'ふろ給湯機(追焚あり)',
        # 配管
        'pipe_diameter': '上記以外',
        # 台所：手元止水機能
        'kitchen_watersaving_A': True,
        # 台所：水優先吐水機能
        'kitchen_watersaving_C': False,
        # 浴室：手元止水機能
        'shower_watersaving_A': False,
        # 浴室：小流量吐水機能
        'shower_watersaving_B': True,
        # 洗面：水優先吐水機能
        'washbowl_watersaving_C': False,
        # 浴槽の保温措置
        'bath_insulation': False
    }

    # ---------- その他設備の設定 ----------

    # 換気
    V = None
    # 照明
    L = None
    # 熱交換型換気
    HEX = None
    # 太陽熱利用
    SHC = None
    # コージェネ
    CG = None

    # ---------- 外皮の計算 ----------

    # 床面積の合計に対する外皮の部位の面積の合計の比の取得
    r_env = calc_r_env('当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法', A_env, A_A)

    # 日射取得係数の取得
    eta_H = get_eta_H(eta_A_H, r_env)
    eta_C = get_eta_C(eta_A_C, r_env)

    # 熱損失係数（換気による熱損失を含まない）
    Q_dash = get_Q_dash(U_A, r_env)
    # 熱損失係数
    Q = get_Q(Q_dash)

    # ---------- 給湯の計算 ----------

    # 8地域分12パターンの計算値を格納するための配列を初期化
    E_W_all_region_array = np.zeros((8, 12))
    # 12パターンの計算値を格納するための配列を初期化
    E_W_array = np.zeros(12)

    # 地域区分ごとに計算
    for i in range(8):
        region = region_array[i]

        # 熱源機(給湯専用型)の種類および洗面の条件ごとに計算
        for j in range(12):

            HW['hw_type'] = hw_array[j]['hw_type']
            HW['e_rtd'] = hw_array[j]['e_rtd']
            HW['hybrid_category'] = hw_array[j]['hybrid_category']
            HW['washbowl_watersaving_C'] = washbowl_watersaving_C_array[j]

            E_W, _, _, _, _, _, _, _ = calc_E_W(A_A, region, sol_region, HW, SHC, CG, H_A, H_MR, H_OR, H_HS, C_A, C_MR,
                                                C_OR, V, L, A_MR, A_OR, A_env, Q, eta_H, eta_C, NV_MR, NV_OR, TS,
                                                r_A_ufvnt, HEX, underfloor_insulation, mode_H, mode_C)

            # 計算値を配列に格納
            E_W_array[j] = E_W

        E_W_all_region_array[i] = E_W_array

    # ---------- 出力 ----------

    # sample/outディレクトリの作成
    if os.path.exists('samples\\out') == False:
        os.mkdir('samples\\out')

    # 出力用カラム名の設定
    columns = ['1地域', '2地域', '3地域', '4地域', '5地域', '6地域', '7地域', '8地域']

    # DataFrameを作成
    df = pd.DataFrame(
            data={columns[0]: E_W_all_region_array[0],
                  columns[1]: E_W_all_region_array[1],
                  columns[2]: E_W_all_region_array[2],
                  columns[3]: E_W_all_region_array[3],
                  columns[4]: E_W_all_region_array[4],
                  columns[5]: E_W_all_region_array[5],
                  columns[6]: E_W_all_region_array[6],
                  columns[7]: E_W_all_region_array[7]},
            columns=columns
        )
    # csv出力
    df.to_csv('samples\\out\\' + 'E_W_節湯C' + '.csv', encoding="shift_jis")
