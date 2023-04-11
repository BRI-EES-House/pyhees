# 9 熱橋
import pyhees.section3_4_e as calc_alpha_i

# 熱橋の暖房期の日射熱取得率 ((W/m)/(W/m2))　(10)
def get_eta_dash_H_j(gamma_H_i, psi_j, alpha = None):
    """熱橋の暖房期の日射熱取得率 ((W/m)/(W/m2)) (10)

    Args:
      gamma_H_i(float): 熱橋の暖房期の日除けの効果係数 (-)
      psi_j(float): 熱橋の線熱貫流率 (W/mK)
      alpha(float, optional): 外気側表⾯の日射吸収率 (-), defaults to None

    Returns:
      float: 熱橋の暖房期の日射熱取得率

    """
    # 外気側表⾯の日射吸収率に応じた係数の計算
    f_alpha_i = calc_alpha_i.get_f_alpha_i(alpha)

    return 0.034 * f_alpha_i * gamma_H_i * psi_j


# 熱橋の冷房期の日射熱取得率 ((W/m)/(W/m2))　(11)
def get_eta_dash_C_j(gamma_C_i, psi_j, alpha = None):
    """熱橋の冷房期の日射熱取得率 ((W/m)/(W/m2)) (11)

    Args:
      gamma_C_i(float): 熱橋の冷房期の日除けの効果係数
      psi_j(float): 熱橋の線熱貫流率 (W/mK)
      alpha(float, optional): 外気側表⾯の日射吸収率 (-), defaults to None

    Returns:
      float: 熱橋の冷房期の日射熱取得率

    """
    # 外気側表⾯の日射吸収率に応じた係数の計算
    f_alpha_i = calc_alpha_i.get_f_alpha_i(alpha)

    return 0.034 * f_alpha_i * gamma_C_i * psi_j
