# 5 一般部位

#
def get_eta_H_i(gamma_H_i, U_i):
    """ 一般部位の暖房期の日射熱取得率(熱貫流率から計算) (1)

    :param gamma_H_i: 開口部の暖房期の日除けの効果係数 (-)
    :type gamma_H_i: float
    :param U_i: 開口部の熱貫流率 (W/m2K)
    :type U_i: float
    :return: 一般部位の暖房期の日射熱取得率(熱貫流率から計算) ((W/m2)/(W/m2))(1)
    :rtype: float
    """
    return 0.034 * gamma_H_i * U_i


def get_eta_C_i(gamma_C_i, U_i):
    """ 一般部位の冷房期の日射熱取得率(熱貫流率から計算) (2)

    :param gamma_C_i: 一般部位iの冷房期の日除けの効果係数
    :type gamma_C_i: float
    :param U_i: ：一般部位iの熱貫流率 （W/m2K）
    :type U_i: float
    :return: 一般部位の冷房期の日射熱取得率(熱貫流率から計算) ((W/m2)/(W/m2))(2)
    :rtype: float
    """
    return 0.034 * gamma_C_i * U_i
