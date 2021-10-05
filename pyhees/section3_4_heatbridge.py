# 9 熱橋

# 熱橋の暖房期の日射熱取得率 ((W/m)/(W/m2))　(10)
def get_eta_dash_H_j(gamma_H_i, psi_j):
    """熱橋の暖房期の日射熱取得率 ((W/m)/(W/m2)) (10)

    Args:
      gamma_H_i(float): 熱橋の暖房期の日除けの効果係数 (-)
      psi_j(float): 熱橋の線熱貫流率 (W/mK)

    Returns:
      float: 熱橋の暖房期の日射熱取得率

    """
    return 0.034 * gamma_H_i * psi_j


# 熱橋の冷房期の日射熱取得率 ((W/m)/(W/m2))　(11)
def get_eta_dash_C_j(gamma_C_i, psi_j):
    """熱橋の冷房期の日射熱取得率 ((W/m)/(W/m2)) (11)

    Args:
      gamma_C_i(float): 熱橋の冷房期の日除けの効果係数
      psi_j(float): 熱橋の線熱貫流率 (W/mK)

    Returns:
      float: 熱橋の冷房期の日射熱取得率

    """
    return 0.034 * gamma_C_i * psi_j
