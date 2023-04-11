# 5 一般部位

#
import pyhees.section3_4_e as calc_alpha_i

def get_eta_H_i(gamma_H_i, U_i, alpha = None):
    """一般部位の暖房期の日射熱取得率(熱貫流率から計算) (1)

    Args:
      gamma_H_i(float): 開口部の暖房期の日除けの効果係数 (-)
      U_i(float): 開口部の熱貫流率 (W/m2K)
      alpha(float, optional): 外気側表⾯の日射吸収率 (-), defaults to None

    Returns:
      float: 一般部位の暖房期の日射熱取得率(熱貫流率から計算) ((W/m2)/(W/m2))(1)

    """
    # 外気側表⾯の日射吸収率に応じた係数の計算
    f_alpha_i = calc_alpha_i.get_f_alpha_i(alpha)

    return 0.034 * f_alpha_i * gamma_H_i * U_i


def get_eta_C_i(gamma_C_i, U_i, alpha = None):
    """一般部位の冷房期の日射熱取得率(熱貫流率から計算) (2)

    Args:
      gamma_C_i(float): 一般部位iの冷房期の日除けの効果係数
      U_i(float): 一般部位iの熱貫流率 （W/m2K）
      alpha(float, optional): 外気側表⾯の日射吸収率 (-), defaults to None

    Returns:
      float: 一般部位の冷房期の日射熱取得率(熱貫流率から計算) ((W/m2)/(W/m2))(2)

    """
    # 外気側表⾯の日射吸収率に応じた係数の計算
    f_alpha_i = calc_alpha_i.get_f_alpha_i(alpha)

    return 0.034 * f_alpha_i * gamma_C_i * U_i
