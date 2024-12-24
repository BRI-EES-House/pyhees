from pyhees.section3_2_b import get_H
from pyhees.section3_2_c import get_nu_H, get_nu_C
from pyhees.section3_4_b_2 import get_glass_spec_category
from pyhees.section3_4 import common, window, door, heatbridge, earthfloor
from pyhees.section3_3_5 import *
from pyhees.section3_3_6 import *
from pyhees.util.env_types import EnvelopeData, HeatBridgeData, T_Direction, T_Adjacent
import typing
from typing import Any

# ============================================================================
# 8. 当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法
# ============================================================================

# ============================================================================
# 8.1 外皮平均熱貫流率
# ============================================================================

def calc_U_A(envelope : EnvelopeData) -> tuple[Any,Any]:
    """外皮平均熱貫流率 (4)

    Args:
      envelope(dict(Envelope)): Envelope要素のノード名をkey、値をvalueとして持つ辞書

    Returns:
      float, dict: 外皮平均熱貫流率, envelopeに計算結果を付加した辞書

    """

    Region = envelope['Region']
    sigma_A_i_U_i_H_i = 0

    # 一般部位または開口部
    # 窓を除く外皮等
    wall_list = envelope['Wall']
    for i in range(len(wall_list)):
    
        wall_i = wall_list[i]

        A_i = wall_i['Area']
        H_i = calc_H_byKey(wall_i['Adjacent'], Region)

        if wall_i['Method'] == 'Direct':
            U_i, wall_i  = get_Wood_Direct_U_i(wall_i)
        elif wall_i['Method'] == 'Accurate':
            U_i, wall_i  = calc_Wood_Accurate_U_i(wall_i)
        elif wall_i['Method'] == 'Simple':
            U_i, wall_i =  calc_Wood_Simple_U_i(wall_i)
        elif wall_i['Method'] == 'RC':
            U_i, wall_i =  calc_RC_U_i(wall_i)
        elif wall_i['Method'] == 'Steel' :
            U_i, wall_i = calc_Steel_U_i(wall_i)
        else:
            raise ValueError("invalid value in ['Method']")
        
        sigma_A_i_U_i_H_i += A_i * U_i * H_i

    # 窓
    window_list = envelope['Window']
    for i in range(len(window_list)):
        window_i = window_list[i]
        A_i = window_i['WindowPart']['Area']
        H_i = calc_H_byKey(window_i['Adjacent'], Region)
        U_i, window_i = calc_Opening_U_i(window_i)
        sigma_A_i_U_i_H_i += A_i * U_i * H_i
    
    # ドア
    door_list = envelope['Door']
    for i in range(len(door_list)):
        door_i = door_list[i]
        A_i = door_i['DoorPart']['Area']
        H_i = calc_H_byKey(door_i['Adjacent'], Region)
        U_i, door_i = calc_Opening_U_i(door_i)
        sigma_A_i_U_i_H_i += A_i * U_i * H_i

    sigma_L_j_psi_j_H_j = 0
    # 熱橋及び土間床等の外周部
    heatbridge_list : list[HeatBridgeData] = envelope['LinearHeatBridge']
    for heatbridge_j in heatbridge_list:
        # 温度差係数
        adjacent = heatbridge_j['Adjacent']
        H_j = calc_H_byKey(adjacent, Region)
        L_j = heatbridge_j['Length']
        structure_type = heatbridge_j['StructureType']

        match structure_type:
            case 'Wood':
                psi_j, heatbridge_j = get_Wood_psi_j(heatbridge_j)
            case 'RC':
                psi_j, heatbridge_j = get_RC_psi_j(heatbridge_j)
            case 'Steel':
                psi_j, heatbridge_j = calc_Steel_psi_j(heatbridge_j)
            case _:
                raise ValueError("invalid value in ['StructureType']")
            
        sigma_L_j_psi_j_H_j += L_j * psi_j * H_j

    # 土間床等の外周部
    foundation_list = envelope['Foundation']
    for j in range(len(foundation_list)):
        foundation_j = foundation_list[j]
        
        L_j = foundation_j['OuterLength']
        H_j = calc_H_byKey(foundation_j['Adjacent'], Region)
        psi_j, foundation = calc_psi_F_j(foundation_j)

        sigma_L_j_psi_j_H_j += L_j * psi_j * H_j
        

    A_env = get_A_env(envelope)
    U_A_raw = (sigma_A_i_U_i_H_i + sigma_L_j_psi_j_H_j) / A_env

    U_A = math.ceil(U_A_raw * 10 ** 2) / (10 ** 2)

    return U_A_raw, U_A


# ============================================================================
# 8.2 暖房期の平均日射熱取得率及び冷房期の平均日射熱取得率
# ============================================================================

def calc_eta_A_H(envelope: EnvelopeData) -> tuple[Any, Any]:
    """暖房期の平均日射熱取得率 (5)

    Args:
      envelope(dict(Envelope)): Envelope要素のノード名をkey、値をvalueとして持つ辞書

    Returns:
      float, dict: 暖房期の平均日射熱取得率, envelopeに計算結果を付加した辞書

    """

    
    Region = envelope['Region']

    if Region in [8, '8']:
        return None, None

    A_i_eta_H_i_nu_H_i = 0.0
    L_j_eta_H_i_nu_H_i = 0.0

    # 窓を除く外皮等
    wall_list = envelope['Wall']
    for wall_i in wall_list:
        A_i = wall_i['Area']

        if wall_i['Method'] == 'Direct':
            U_i, wall_i  = get_Wood_Direct_U_i(wall_i)
        elif wall_i['Method'] == 'Accurate':
            U_i, wall_i  = calc_Wood_Accurate_U_i(wall_i)
        elif wall_i['Method'] == 'Simple':
            U_i, wall_i =  calc_Wood_Simple_U_i(wall_i)
        elif wall_i['Method'] == 'RC':
            U_i, wall_i =  calc_RC_U_i(wall_i)
        elif wall_i['Method'] == 'Steel' :
            U_i, wall_i = calc_Steel_U_i(wall_i)
        else:
            raise ValueError("invalid value in ['Method']")

        # 方位係数(付録C)

        # 隣接空間の種類が外気の場合に方位係数を取得する
        if wall_i['Adjacent'] == 'Outside':
            nu_H_i = calc_nu_byKey(Region, wall_i['Direction'], 'H')
        else:
            # 隣接空間の種類が外気に通じる空間・外気に通じていない空間・外気に通じる床裏・住戸及び住戸と同様の熱的環境の空間・外気に通じていない床裏等の日射が当たらない場合の方位係数は0とする。
            nu_H_i = 0.0

        # 日射熱取得率を計算
        # 方位係数が0の場合、最終的な日射熱取得率は0になるためここより下の日射熱取得率の計算を実施しない
        if nu_H_i > 0.0:
            gamma_H_i = wall_i['GammaH']
            # 外気側表⾯の日射吸収率を指定する場合
            if ('SolarAbsorptance' in wall_i):
                alpha = wall_i['SolarAbsorptance']
                eta_H_i = common.get_eta_H_i(gamma_H_i, U_i, alpha)
            else:
                eta_H_i = common.get_eta_H_i(gamma_H_i, U_i)
        else:
            eta_H_i = 0.0

        A_i_eta_H_i_nu_H_i += A_i * eta_H_i * nu_H_i

    # 窓
    window_list = envelope['Window']
    for window_i in window_list:
        A_i = window_i['WindowPart']['Area']

        # 方位係数(付録C)

        # 隣接空間の種類が外気か有の場合に方位係数を取得する
        if window_i['Adjacent'] == 'Outside':
            nu_H_i = calc_nu_byKey(Region, window_i['Direction'], 'H')
        else:
            # 隣接空間の種類が外気に通じる空間・外気に通じていない空間・外気に通じる床裏・住戸及び住戸と同様の熱的環境の空間・外気に通じていない床裏等の日射が当たらない場合の方位係数は0とする。
            nu_H_i = 0.0

        # 日射熱取得率
        # 方位係数が0の場合、最終的な日射熱取得率は0になるためここより下の日射熱取得率の計算を実施しない
        if nu_H_i > 0.0:
            eta_H_i = window.calc_eta_H_i_byDict(Region, window_i['Direction'], window_i['WindowPart'])
        else:
            eta_H_i = 0.0

        A_i_eta_H_i_nu_H_i += A_i * eta_H_i * nu_H_i
    
    # ドア
    door_list = envelope['Door']
    for door_i in door_list:
        A_i = door_i['DoorPart']['Area']

        # 方位係数(付録C)

        # 隣接空間の種類が外気の場合に方位係数を取得する
        if door_i['Adjacent'] == 'Outside':
            nu_H_i = calc_nu_byKey(Region, door_i['Direction'], 'H')
        else:
            # 隣接空間の種類が外気に通じる空間・外気に通じていない空間・外気に通じる床裏・住戸及び住戸と同様の熱的環境の空間・外気に通じていない床裏等の日射が当たらない場合の方位係数は0とする。
            nu_H_i = 0.0

        # 日射熱取得率
        # 方位係数が0の場合、最終的な日射熱取得率は0になるためここより下の日射熱取得率の計算を実施しない
        if nu_H_i > 0.0:
            eta_H_i = door.calc_eta_H_i_byDict(Region, door_i['DoorPart'])
        else:
            eta_H_i = 0.0

        A_i_eta_H_i_nu_H_i += A_i * eta_H_i * nu_H_i


    # 熱橋
    heatbridge_list = envelope['LinearHeatBridge']
    for heatbridge_j in heatbridge_list:
        structure_type = heatbridge_j['StructureType']
        # 木造
        match structure_type:
            case "Wood": #木造
                psi_i_j, heatbridge_j = get_Wood_psi_j(heatbridge_j)
            case "RC": # 鉄筋コンクリート造等
                psi_i_j, heatbridge_j = get_RC_psi_j(heatbridge_j)
            case "Steel": # 鉄骨造
                psi_i_j, heatbridge_j = calc_Steel_psi_j(heatbridge_j)
            case _:
                raise ValueError("invalid value in ['StructureType']")
        
        L_i_j = heatbridge_j['Length']
        nu_H_i_sum = 0
        # カンマ区切りの方位を取得
        directions = typing.cast(list[T_Direction], heatbridge_j.get('Direction','').split(','))
        for direction in directions:
            # 方位係数(付録C)
            # 方位の異なる外皮の部位（一般部位又は開口部）に接する熱橋等の方位係数は、異なる方位の方位係数の平均値とする

            # 隣接空間の種類が外気の場合に方位係数を取得する
            if heatbridge_j.get('Adjacent') == 'Outside':
                nu = calc_nu_byKey(Region, direction, 'H')
                nu_H_i_sum += nu if nu is not None else 0.0
            else:
                # 隣接空間の種類が外気に通じる空間・外気に通じていない空間・外気に通じる床裏・住戸及び住戸と同様の熱的環境の空間・外気に通じていない床裏等の日射が当たらない場合の方位係数は0とする。
                nu_H_i_sum += 0.0

        # 日射熱取得率を計算
        # 方位係数が0の場合、最終的な日射熱取得率は0になるためここより下の日射熱取得率の計算を実施しない
        if nu_H_i_sum > 0.0:
            gamma_H_i = heatbridge_j.get('GammaH')
            # 外気側表⾯の日射吸収率を指定する場合
            if ('SolarAbsorptance' in heatbridge_j):
                alpha = heatbridge_j['SolarAbsorptance']
                eta_H_i = heatbridge.get_eta_dash_H_j(gamma_H_i, psi_i_j, alpha)
            else:
                eta_H_i = heatbridge.get_eta_dash_H_j(gamma_H_i, psi_i_j)
        else:
            eta_H_i = 0.0

        n =  len(directions)
        # 方位係数の平均値
        nu_H_i = nu_H_i_sum / n if n != 0 else 0.0

        L_j_eta_H_i_nu_H_i += L_i_j * eta_H_i * nu_H_i


    # 土間床等の外周部の暖房期の日射熱取得率及び冷房期の日射熱取得率は0 (W/mK)/(W/m2K) とする。
    L_j_eta_H_i_nu_H_i += earthfloor.get_eta_dash_H_j()

    A_env = get_A_env(envelope)

    eta_A_H_raw = (A_i_eta_H_i_nu_H_i + L_j_eta_H_i_nu_H_i) / A_env * 100

    eta_A_H = math.floor(eta_A_H_raw * 10 ** 1) / (10 ** 1)

    return eta_A_H_raw, eta_A_H



def calc_eta_A_C(envelope: EnvelopeData) -> tuple[Any, Any]:
    """冷房期の平均日射熱取得率 (5)

    Args:
      envelope(dict(Envelope)): Envelope要素のノード名をkey、値をvalueとして持つ辞書

    Returns:
      float, dict: 冷房期の平均日射熱取得率, envelopeに計算結果を付加した辞書

    """

    A_env = get_A_env(envelope)
    
    
    Region = envelope['Region']

    A_i_eta_C_i_nu_C_i = 0.0
    L_j_eta_C_i_nu_C_i = 0.0

    # 窓を除く外皮等
    wall_list = envelope['Wall']
    for wall_i in wall_list:
        A_i = wall_i['Area']

        if wall_i['Method'] == 'Direct':
            U_i, wall_i  = get_Wood_Direct_U_i(wall_i)
        elif wall_i['Method'] == 'Accurate':
            U_i, wall_i  = calc_Wood_Accurate_U_i(wall_i)
        elif wall_i['Method'] == 'Simple':
            U_i, wall_i =  calc_Wood_Simple_U_i(wall_i)
        elif wall_i['Method'] == 'RC':
            U_i, wall_i =  calc_RC_U_i(wall_i)
        elif wall_i['Method'] == 'Steel' :
            U_i, wall_i = calc_Steel_U_i(wall_i)
        else:
            raise ValueError("invalid value in ['Method']")

        # 日よけの効果係数

        # 方位係数(付録C)

        # 隣接空間の種類が外気の場合に方位係数を取得する
        if wall_i['Adjacent'] == 'Outside':
            nu_C_i = calc_nu_byKey(Region, wall_i['Direction'], 'C')
        else:
            # 隣接空間の種類が外気に通じる空間・外気に通じていない空間・外気に通じる床裏・住戸及び住戸と同様の熱的環境の空間・外気に通じていない床裏等の日射が当たらない場合の方位係数は0とする。
            nu_C_i = 0.0

        # 日射熱取得率を計算
        # 方位係数が0の場合、最終的な日射熱取得率は0になるためここより下の日射熱取得率の計算を実施しない
        if nu_C_i > 0.0:
            gamma_C_i = wall_i['GammaC']
            # 外気側表⾯の日射吸収率を指定する場合
            if ('SolarAbsorptance' in wall_i):
                alpha = wall_i['SolarAbsorptance']
                eta_C_i = common.get_eta_C_i(gamma_C_i, U_i, alpha)
            else:
                eta_C_i = common.get_eta_C_i(gamma_C_i, U_i)
        else:
            eta_C_i = 0.0

        A_i_eta_C_i_nu_C_i += A_i * eta_C_i * nu_C_i

    # 窓
    window_list = envelope['Window']
    for window_i in window_list:
        A_i = window_i['WindowPart']['Area']

        # 方位係数(付録C)

        # 隣接空間の種類が外気の場合に方位係数を取得する
        if window_i['Adjacent'] == 'Outside':
            nu_C_i = calc_nu_byKey(Region, window_i['Direction'], 'C')
        else:
            # 隣接空間の種類が外気に通じる空間・外気に通じていない空間・外気に通じる床裏・住戸及び住戸と同様の熱的環境の空間・外気に通じていない床裏等の日射が当たらない場合の方位係数は0とする。
            nu_C_i = 0.0

        # 日射熱取得率
        # 方位係数が0の場合、最終的な日射熱取得率は0になるためここより下の日射熱取得率の計算を実施しない
        if nu_C_i > 0.0:
            eta_C_i = window.calc_eta_C_i_byDict(Region, window_i['Direction'], window_i['WindowPart'])
        else:
            eta_C_i = 0.0

        A_i_eta_C_i_nu_C_i += A_i * eta_C_i * nu_C_i

    # ドア
    door_list = envelope['Door']
    for door_i in door_list:
        A_i = door_i['DoorPart']['Area']

        # 方位係数(付録C)

        # 隣接空間の種類が外気の場合に方位係数を取得する
        if door_i['Adjacent'] == 'Outside':
            nu_C_i = calc_nu_byKey(Region, door_i['Direction'], 'C')
        else:
            # 隣接空間の種類が外気に通じる空間・外気に通じていない空間・外気に通じる床裏・住戸及び住戸と同様の熱的環境の空間・外気に通じていない床裏等の日射が当たらない場合の方位係数は0とする。
            nu_C_i = 0.0

        # 日射熱取得率
        # 方位係数が0の場合、最終的な日射熱取得率は0になるためここより下の日射熱取得率の計算を実施しない
        if nu_C_i > 0.0:
            eta_C_i = door.calc_eta_C_i_byDict(Region, door_i['DoorPart'])
        else:
            eta_C_i = 0.0

        A_i_eta_C_i_nu_C_i += A_i * eta_C_i * nu_C_i


    # 熱橋
    heatbridge_list = envelope['LinearHeatBridge']
    for heatbridge_j in heatbridge_list:
        structure_type = heatbridge_j.get('StructureType')
        match structure_type:
            case 'Wood': # 木造
                psi_i_j, heatbridge_j = get_Wood_psi_j(heatbridge_j)
            case 'RC': # 鉄筋コンクリート造等
                psi_i_j, heatbridge_j = get_RC_psi_j(heatbridge_j)
            case 'Steel': # 鉄骨造
                psi_i_j, heatbridge_j = calc_Steel_psi_j(heatbridge_j)
            case _:
                raise ValueError("invalid value in ['StructureType']")

        L_i_j = heatbridge_j['Length']
        nu_C_i_sum = 0
        # カンマ区切りの方位を取得
        directions = typing.cast(list[T_Direction], heatbridge_j.get('Direction','').split(','))
        for direction in directions:
            # 方位係数(付録C)
            # 方位の異なる外皮の部位（一般部位又は開口部）に接する熱橋等の方位係数は、異なる方位の方位係数の平均値とする

            # 隣接空間の種類が外気の場合に方位係数を取得する
            if heatbridge_j['Adjacent'] == 'Outside':
                nu = calc_nu_byKey(Region,direction,'C')
                nu_C_i_sum += nu if nu is not None else 0.0
            else:
                # 隣接空間の種類が外気に通じる空間・外気に通じていない空間・外気に通じる床裏・住戸及び住戸と同様の熱的環境の空間・外気に通じていない床裏等の日射が当たらない場合の方位係数は0とする。
                nu_C_i_sum += 0.0

        # 日射熱取得率を計算
        # 方位係数が0の場合、最終的な日射熱取得率は0になるためここより下の日射熱取得率の計算を実施しない
        if nu_C_i_sum > 0.0:
            gamma_C_i = heatbridge_j.get('GammaC')
            # 外気側表⾯の日射吸収率を指定する場合
            if ('SolarAbsorptance' in heatbridge_j):
                alpha = heatbridge_j['SolarAbsorptance']
                eta_C_i = heatbridge.get_eta_dash_C_j(gamma_C_i, psi_i_j, alpha)
            else:
                eta_C_i = heatbridge.get_eta_dash_C_j(gamma_C_i, psi_i_j)
        else:
            eta_C_i = 0.0

        n =  len(directions)
        # 方位係数の平均値
        nu_C_i = nu_C_i_sum / n if n != 0 else 0.0

        L_j_eta_C_i_nu_C_i += L_i_j * eta_C_i * nu_C_i

    # 土間床等の外周部の暖房期の日射熱取得率及び冷房期の日射熱取得率は0 (W/mK)/(W/m2K) とする。
    L_j_eta_C_i_nu_C_i += earthfloor.get_eta_dash_C_j()

    A_env = get_A_env(envelope)

    eta_A_C_raw = (A_i_eta_C_i_nu_C_i + L_j_eta_C_i_nu_C_i) / A_env * 100

    eta_A_C = math.ceil(eta_A_C_raw * 10 ** 1) / (10 ** 1)

    return eta_A_C_raw, eta_A_C


# ============================================================================
# 8.3 床面積の合計に対する外皮の部位の面積の合計の比
# ============================================================================

def get_r_env(A_env, A_A):
    """床面積の合計に対する外皮の部位の面積の合計の比 (7)

    Args:
      A_env(float): 外皮の部位の面積の合計 (m2)
      A_A(float): 床面積の合計 (m2)

    Returns:
      float: 床面積の合計に対する外皮の部位の面積の合計の比

    """

    return A_env / A_A



def get_A_env(envelope) -> float:
    """外皮の部位の面積の合計 式(8)

    Args:
      envelope(dict(Envelope)): Envelope要素のノード名をkey、値をvalueとして持つ辞書

    Returns:
      float: 外皮の部位の面積の合計

    """

    A_env = 0.0
    # 窓を除く外皮等
    wall_list = envelope['Wall']
    for i in range(len(wall_list)):
        A_env += wall_list[i]['Area']

    # 窓
    window_list = envelope['Window']
    for i in range(len(window_list)):
        A_env += window_list[i]['WindowPart']['Area']
    
    # ドア
    door_list = envelope['Door']
    for i in range(len(door_list)):
        A_env += door_list[i]['DoorPart']['Area']

    # 土間床の面積
    foundation_list = envelope['Foundation']
    for j in range(len(foundation_list)):
        A_env += foundation_list[j]['Area']
        
    return A_env



def calc_H_byKey(adjacent_type : T_Adjacent, region):
    """パラメータの値から温度差係数の表を参照する

    Args:
      adjacent_type(String): 隣接空間の種類
      region(int): 地域区分

    Returns:
      float: 温度差係数

    """

    # ノードの値と関数get_H内の隣接空間の種類名を対応づける
    adjacent_dict : dict[T_Adjacent, str] = {
        'Outside': '外気',
        'Open': '外気に通じる空間',
        'Connected': '外気・外気に通じる空間',
        'Close': '外気に通じていない空間・外気に通じる床裏',
        'SeparatorZero': '住戸（温度差係数を0とする要件を満たす場合）',
        'Separator': '住戸及び住戸と同様の熱的環境の空間・外気に通じていない床裏'
        }
    
    return get_H(adjacent_dict[adjacent_type], region)


def calc_nu_byKey(region, Direction : T_Direction, season) -> float|None:
    """パラメータの値から暖房期・冷房期の方位係数の表を参照する

    Args:
      region(int): 地域区分
      Direction(String): 方位
      season(String): H'(暖房期)または'C'(冷房期)

    Returns:
      float: 方位係数

    """
    
    # ノードの値と関数get_nu_H/get_nu_C内方位名を対応づける
    Direction_dict : dict[T_Direction, str] = {'Top':'上面', 'N':'北', 'NE':'北東', 'E':'東', 'SE':'南東', 
                    'S':'南', 'SW':'南西', 'W':'西', 'NW':'北西', 'Bottom':'下面'}
    
    # 暖房期
    if season == 'H':
        return get_nu_H(region, Direction_dict[Direction])
    # 冷房期
    else:
        return get_nu_C(region, Direction_dict[Direction])





def get_component_by_name(wall_list : list, componentname : str) -> dict:
    """名前から部位のパラメータを持つ辞書を得る

    Args:
      wall_list(List<dict>(Wall_direct Wall_accurate Wall_simple Wall_rc Wall_steel)): 窓を除く外皮等のリスト
      componentname: 部位の名前
      componentname: str

    Returns:
      dict(Wall_direct Wall_accurate Wall_simple Wall_rc Wall_steel): 部位のパラメータを持つ辞書

    """

    for wall_i in wall_list:
        if wall_i['Name'] == componentname:
            return wall_i
    raise ValueError(f"指定した名前'{componentname}'を持つ部位は存在しませんでした。")
