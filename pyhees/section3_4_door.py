# 7 大部分がガラスで構成されていないドア等の開口部
import pyhees.section3_4_a as gamma
from pyhees.section3_3_5 import calc_OpeningPart_U_i

# 開口部の暖房期の日射熱取得率  ((W/m)/(W/m2)) (6)
def get_eta_H_i(gamma_H_i, U_i):
    """開口部の暖房期の日射熱取得率  ((W/m)/(W/m2)) (6)

    Args:
      gamma_H_i(float): 開口部の暖房期の日除けの効果係数 (-)
      U_i(float): 開口部の熱貫流率 (W/m2K)

    Returns:
      float: 開口部の暖房期の日射熱取得率

    """
    return 0.034 * gamma_H_i * U_i


def calc_eta_H_i_byDict(Region, door_part):
    """DoorPart形式の辞書からドア・ドア部分(ドアや窓が同一枠内で併設される場合)の暖房期の日射熱取得率を求める

    Args:
      region(int): 省エネルギー地域区分
      door_part(dict(DoorPart)): ドア
      Region: returns: 開口部の暖房期の日射熱取得率

    Returns:
      float: 開口部の暖房期の日射熱取得率

    """
    U_i = calc_OpeningPart_U_i(door_part, 'Door')
    
    # 日除けがない場合
    # 日除けの効果係数→1.0
    if door_part['HasShade'] == 'No':
        gamma_H_i = gamma.get_gamma_H_i_default()

    # 日除けがある場合
    # 日除けの効果係数→式(1)
    else:
        gamma_H_i = door_part['GammaH']

    return get_eta_H_i(gamma_H_i, U_i)


# 開口部の冷房期の日射熱取得率  ((W/m)/(W/m2)) (6)
def get_eta_C_i(gamma_C_i, U_i):
    """開口部の冷房期の日射熱取得率  ((W/m)/(W/m2)) (7)

    Args:
      gamma_C_i(float): 一般部位iの冷房期の日除けの効果係数
      U_i(float): 一般部位iの熱貫流率 （W/m2K）

    Returns:
      float: 開口部の冷房期の日射熱取得率

    """
    return 0.034 * gamma_C_i * U_i


def calc_eta_C_i_byDict(Region, door_part):
    """DoorPart形式の辞書からドア・ドア部分の冷房期の日射熱取得率を求める

    Args:
      region(int): 省エネルギー地域区分
      door_part(dict(DoorPart)): ドア
      Region: returns: 開口部の冷房期の日射熱取得率

    Returns:
      float: 開口部の冷房期の日射熱取得率

    """

    U_i = calc_OpeningPart_U_i(door_part, 'Door')
    
    # 日除けがない場合
    # 日除けの効果係数→1.0
    if door_part['HasShade'] == 'No':
        gamma_C_i = gamma.get_gamma_C_i_default()

    # 日除けがある場合
    # 日除けの効果係数→式(1)
    else:
        gamma_C_i = door_part['GammaC']

    return get_eta_C_i(gamma_C_i, U_i)