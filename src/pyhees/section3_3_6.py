import math
from pyhees.section3_3_5 import calc_R_i_k

# ============================================================================
# 6. 熱橋等の線熱貫流率
# ============================================================================

# ============================================================================
# 6.1.1 木造
# ============================================================================
def get_Wood_psi_j(heatbridge_j):
    """木造における熱橋jの線熱貫流率

    Args:
      heatbridge_j(dict(LinearHeatBridge_steel)): 熱橋j

    Returns:
      float, dict(LinearHeatBridge_wood形式): 熱橋jの線熱貫流率, heatbridge_jに計算結果を付加した辞書

    """

    psi = heatbridge_j['LinearThermalTransmittance']
    heatbridge_j['Psi'] = psi

    return psi, heatbridge_j


# ============================================================================
# 6.1.2 鉄筋コンクリート造等
# ============================================================================
def get_RC_psi_j(heatbridge_j):
    """鉄筋コンクリート造等における熱橋jの線熱貫流率

    Args:
      heatbridge_j(dict(LinearHeatBridge_steel)): 熱橋j

    Returns:
      float, dict(LinearHeatBridge_rc形式): 熱橋jの線熱貫流率, heatbridge_jに計算結果を付加した辞書

    """

    psi = heatbridge_j['LinearThermalTransmittance']
    heatbridge_j['Psi'] = psi

    return psi, heatbridge_j


# ============================================================================
# 6.1.3 鉄骨造
# ============================================================================

def calc_Steel_psi_j(heatbridge_j):
    """鉄骨造における熱橋jの線熱貫流率

    Args:
      heatbridge_j(dict(LinearHeatBridge_steel)): 熱橋j

    Returns:
      float, dict(LinearHeatBridge_steel形式): 熱橋jの線熱貫流率, heatbridge_jに計算結果を付加した辞書

    """

    if heatbridge_j['Type'] == 'Column':
        psi = get_table_9(heatbridge_j['ExteriorThermalResistance'], heatbridge_j['ColumnInterval'])
    elif heatbridge_j['Type'] == 'Beam':
        psi = get_table_10(heatbridge_j['ExteriorThermalResistance'], heatbridge_j['BeamInterval'])
    else:
        raise ValueError("invalid value in ['Type']")

    heatbridge_j['Psi'] = psi

    return psi, heatbridge_j


def get_table_9(ExteriorThermalResistance, ColumnInterval):
    """表9 鉄骨造における一般部位の熱橋の線熱貫流率

    Args:
      ExteriorThermalResistance(str): 外装材＋断熱補強材の熱抵抗
    'Over1.7'(1.7以上)または'Under1.7'(1.7未満1.5以上)または
    'Under1.5'(1.5未満1.3以上)または'Under1.3'(1.3未満1.1以上)または
    'Under1.1'(1.1未満0.9以上)または'Under0.9'(0.9未満0.7以上)または
    'Under0.7'(0.7未満0.5以上)または'Under0.5'(0.5未満0.3以上)または
    'Under0.3'(0.3未満0.1以上)または'Under0.1'(0.1未満)
      ColumnInterval(str): 柱見付寸法
    'Over300'(300以上)または'Under300'(300未満200以上)または
    'Under200'(200未満100以上)または'Under100'(100未満)

    Returns:
      float: 鉄骨造における一般部位の熱橋の線熱貫流率(psi_j)

    """

    Over1_7_dict = {'Over300': 0.0, 'Under300': 0.0,
                    'Under200': 0.0, 'Under100': 0.0}
    Under1_7_dict = {'Over300': 0.15, 'Under300': 0.12,
                     'Under200': 0.05, 'Under100': 0.04}
    Under1_5_dict = {'Over300': 0.18, 'Under300': 0.14,
                     'Under200': 0.06, 'Under100': 0.05}
    Under1_3_dict = {'Over300': 0.20, 'Under300': 0.16,
                     'Under200': 0.07, 'Under100': 0.06}
    Under1_1_dict = {'Over300': 0.25, 'Under300': 0.18,
                     'Under200': 0.08, 'Under100': 0.07}
    Under0_9_dict = {'Over300': 0.30, 'Under300': 0.22,
                     'Under200': 0.11, 'Under100': 0.09}
    Under0_7_dict = {'Over300': 0.35, 'Under300': 0.27,
                     'Under200': 0.12, 'Under100': 0.10}
    Under0_5_dict = {'Over300': 0.43, 'Under300': 0.32,
                     'Under200': 0.15, 'Under100': 0.14}
    Under0_3_dict = {'Over300': 0.60, 'Under300': 0.40,
                     'Under200': 0.18, 'Under100': 0.17}
    Under0_1_dict = {'Over300': 0.80, 'Under300': 0.55,
                     'Under200': 0.25, 'Under100': 0.21}

    psi_j_dict = {'Over1.7': Over1_7_dict, 'Under1.7': Under1_7_dict, 'Under1.5': Under1_5_dict, 'Under1.3': Under1_3_dict, 'Under1.1': Under1_1_dict,
                  'Under0.9': Under0_9_dict, 'Under0.7': Under0_7_dict, 'Under0.5': Under0_5_dict, 'Under0.3': Under0_3_dict, 'Under0.1': Under0_1_dict}

    return psi_j_dict[ExteriorThermalResistance][ColumnInterval]


def get_table_10(ExteriorThermalResistance, BeamInterval):
    """表10 鉄骨造における一般部位の熱橋の線熱貫流率

    Args:
      ExteriorThermalResistance(str): 外装材＋断熱補強材の熱抵抗
    'Over1.7'(1.7以上)または'Under1.7'(1.7未満1.5以上)または
    'Under1.5'(1.5未満1.3以上)または'Under1.3'(1.3未満1.1以上)または
    'Under1.1'(1.1未満0.9以上)または'Under0.9'(0.9未満0.7以上)または
    'Under0.7'(0.7未満0.5以上)または'Under0.5'(0.5未満0.3以上)または
    'Under0.3'(0.3未満0.1以上)または'Under0.1'(0.1未満)
      BeamInterval(str): 梁見付寸法
    'Over400'(400以上)または'Under400'(400未満200以上)または'Under200'(200未満)

    Returns:
      float: 鉄骨造における一般部位の熱橋の線熱貫流率(psi_j)

    """

    Over1_7_dict = {'Over400': 0.0, 'Under400': 0.0, 'Under200': 0.0}
    Under1_7_dict = {'Over400': 0.15, 'Under400': 0.12, 'Under200': 0.05}
    Under1_5_dict = {'Over400': 0.18, 'Under400': 0.14, 'Under200': 0.06}
    Under1_3_dict = {'Over400': 0.20, 'Under400': 0.16, 'Under200': 0.07}
    Under1_1_dict = {'Over400': 0.25, 'Under400': 0.18, 'Under200': 0.08}
    Under0_9_dict = {'Over400': 0.30, 'Under400': 0.22, 'Under200': 0.11}
    Under0_7_dict = {'Over400': 0.35, 'Under400': 0.27, 'Under200': 0.12}
    Under0_5_dict = {'Over400': 0.43, 'Under400': 0.32, 'Under200': 0.15}
    Under0_3_dict = {'Over400': 0.60, 'Under400': 0.40, 'Under200': 0.18}
    Under0_1_dict = {'Over400': 0.80, 'Under400': 0.55, 'Under200': 0.25}

    psi_j_dict = {'Over1.7': Over1_7_dict, 'Under1.7': Under1_7_dict, 'Under1.5': Under1_5_dict, 'Under1.3': Under1_3_dict, 'Under1.1': Under1_1_dict,
                  'Under0.9': Under0_9_dict, 'Under0.7': Under0_7_dict, 'Under0.5': Under0_5_dict, 'Under0.3': Under0_3_dict, 'Under0.1': Under0_1_dict}

    return psi_j_dict[ExteriorThermalResistance][BeamInterval]


# ============================================================================
# 6.2 土間床等の外周部
# ============================================================================

def calc_psi_F_j(foundation):
    """基礎等の熱損失を含めた土間床等の外周部の線熱貫流率

    Args:
      foundation(dict(Foundation)): 土間床等の外周部

    Returns:
      float: 土間床等の外周部及び基礎等の線熱貫流率(W/m2K)

    """

    # 線熱貫流率は直接入力
    psi_F_j = foundation['PsiF']
    # 結果
    foundation['U_F'] = psi_F_j

    return psi_F_j, foundation


def get_foundation_part(part_list, type_name):
    """土間床等の外周部に含まれる一般部分のリストpart_listから、
    'Type'KeyのValueがtype_nameに一致する一般部分を返す

    Args:
      part_list(list: list: list<dict>): 土間床等の外周部に含まれる一般部分のリスト
      type_name(str(GeneralPart_foundation>'Type')): 取り出したい一般部分のType

    Returns:
      float: 基礎等の熱損失を含めた土間床等の外周部の線熱貫流率(地盤面からの基礎等の底盤等上端の深さが1m以内)

    """

    for part_i in part_list:
        if part_i['Type'] == type_name:
            return part_i
    return None


def get_psi_lower_1(R_1, R_2, R_3, R_4, H_1, H_2, W_1, W):
    """基礎等の熱損失を含めた土間床等の外周部の線熱貫流率…………式(11)

    Args:
      R_1(float): 基礎等の立ち上がり部分の外気側に設置した断熱材の熱抵抗
      R_2(float): 基礎等の底盤部分等の室内側に設置した断熱材の熱抵抗
      R_3(float): 基礎等の底盤部分等の外気側に設置した断熱材の熱抵抗
      R_4(float): 基礎等の立ち上がり部分の室内側に設置した断熱材の熱抵抗
      H_1(float): 地盤面からの基礎等の寸法
      H_2(float): 地盤面からの基礎等の底盤等上端までの寸法
      W_1(float): 地盤面より下の基礎等の立ち上がり部分の外気側の断熱材の施工深さ
      W(float): W_2及びW_3の寸法のうちいずれか大きい方の寸法

    Returns:
      float: 基礎等の熱損失を含めた土間床等の外周部の線熱貫流率(地盤面からの基礎等の底盤等上端の深さが1m以内)

    """

    return 1.80 - 1.36 * pow((R_1 * (H_1 + W_1) + R_4 * (H_1 - H_2)),
                                    0.15) - 0.01 * (6.14 - R_1) * pow((R_2 + 0.5 * R_3), 0.5)


def get_psi_lower_2(R_1, R_2, R_3, R_4, W):
    """基礎等の熱損失を含めた土間床等の外周部の線熱貫流率…………式(12)

    Args:
      R_1(float): 基礎等の立ち上がり部分の外気側に設置した断熱材の熱抵抗
      R_2(float): 基礎等の底盤部分等の室内側に設置した断熱材の熱抵抗
      R_3(float): 基礎等の底盤部分等の外気側に設置した断熱材の熱抵抗
      R_4(float): 基礎等の立ち上がり部分の室内側に設置した断熱材の熱抵抗
      W(float): W_2及びW_3の寸法のうちいずれか大きい方の寸法

    Returns:
      float: 基礎等の熱損失を含めた土間床等の外周部の線熱貫流率(地盤面からの基礎等の底盤等上端の深さが1m以内)

    """

    if R_1 + R_4 >= 3:
        return 0.76 - 0.05 * (R_1 + R_4) - 0.1 * (R_2 + 0.5 * R_3)
    elif R_1 + R_4 >= 0.1:
        return 1.30 - 0.23 * (R_1 + R_4) - 0.1 * (R_2 + 0.5 * R_3) * W
    else:  # 0.1 > (R1 + R4) のとき
        return 1.80 - 0.1 * (R_2 + 0.5 * R_3) * W


def get_psi_higher_1(R_1, R_4):
    """基礎等の熱損失を含めた土間床等の外周部の線熱貫流率…………式(13)

    Args:
      R_1(float): 基礎等の立ち上がり部分の外気側に設置した断熱材の熱抵抗
      R_4(float): 基礎等の立ち上がり部分の室内側に設置した断熱材の熱抵抗
      W(float): W_2及びW_3の寸法のうちいずれか大きい方の寸法

    Returns:
      float: 基礎等の熱損失を含めた土間床等の外周部の線熱貫流率(地盤面からの基礎等の底盤等上端の深さが1mを超える)

    """

    if R_1 + R_4 >= 3:
        return 1.80 - 1.47 * pow((R_1 + R_4), 0.08)
    else:  # (R1 + R4) < 3 のとき
        return 1.80 - 1.36 * pow((R_1 + R_4), 0.15)


def get_psi_higher_2(R_1, R_4):
    """基礎等の熱損失を含めた土間床等の外周部の線熱貫流率…………式(14)

    Args:
      R_1(float): 基礎等の立ち上がり部分の外気側に設置した断熱材の熱抵抗
      R_4(float): 基礎等の立ち上がり部分の室内側に設置した断熱材の熱抵抗
      W(float): W_2及びW_3の寸法のうちいずれか大きい方の寸法

    Returns:
      float: 基礎等の熱損失を含めた土間床等の外周部の線熱貫流率(地盤面からの基礎等の底盤等上端の深さが1mを超える)

    """

    if R_1 + R_4 >= 2:
        return 0.36 - 0.03 * (R_1 + R_4)
    else:  # (R1 + R4) < 2 のとき
        return 1.80 - 0.75 * (R_1 + R_4)