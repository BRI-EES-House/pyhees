# 7 大部分がガラスで構成されていないドア等の開口部
import pyhees.section3_4_a as gamma
from pyhees.section3_3_5 import calc_OpeningPart_U_i

# 開口部の暖房期の日射熱取得率  ((W/m)/(W/m2)) (6)
def get_eta_H_i(gamma_H_i, U_i):
    """ 開口部の暖房期の日射熱取得率  ((W/m)/(W/m2)) (6)

    :param gamma_H_i: 開口部の暖房期の日除けの効果係数 (-)
    :type gamma_H_i: float
    :param U_i: 開口部の熱貫流率 (W/m2K)
    :type U_i: float
    :return: 開口部の暖房期の日射熱取得率
    :rtype: float
    """
    return 0.034 * gamma_H_i * U_i


def calc_eta_H_i_byDict(Region, door_part):
    """ DoorPart形式の辞書からドア・ドア部分(ドアや窓が同一枠内で併設される場合)の暖房期の日射熱取得率を求める

    :param region: 省エネルギー地域区分
    :type region: int
    :param door_part: ドア
    :type door_part: dict(DoorPart)
    :return: 開口部の暖房期の日射熱取得率
    :rtype: float
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
    """ 開口部の冷房期の日射熱取得率  ((W/m)/(W/m2)) (7)

    :param gamma_C_i: 一般部位iの冷房期の日除けの効果係数
    :type gamma_C_i: float
    :param U_i: ：一般部位iの熱貫流率 （W/m2K）
    :type U_i: float
    :return: 開口部の冷房期の日射熱取得率
    :rtype: float
    """
    return 0.034 * gamma_C_i * U_i


def calc_eta_C_i_byDict(Region, door_part):
    """ DoorPart形式の辞書からドア・ドア部分の冷房期の日射熱取得率を求める

    :param region: 省エネルギー地域区分
    :type region: int
    :param door_part: ドア
    :type door_part: dict(DoorPart)
    :return: 開口部の冷房期の日射熱取得率
    :rtype: float
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