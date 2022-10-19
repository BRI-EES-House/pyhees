# ===========================================================================
# 付録 I 配管
# ===========================================================================

from math import sqrt


# ===========================================================================
# I.2 線熱損失係数
# ===========================================================================

def get_K_loss_pp(is_pipe_insulated):
    """線熱損失係数

    Args:
      is_pipe_insulated(bool): 配管の断熱被覆の有無

    Returns:
      float: 線熱損失係数

    """
    if is_pipe_insulated:
        return 0.15
    else:
        return 0.21


# ===========================================================================
# I.3 長さ
# ===========================================================================

def calc_L_pp_ex_i(i, A_A, underfloor_pipe_insulation, MR_rad_type, r_Af_1):
    """配管の断熱区画外における長さ (1a)

    Args:
      i(int): 暖冷房区画の番号
      A_A(float): 床面積の合計 (m2)
      underfloor_pipe_insulation(bool): 床下配管断熱の有無
      MR_rad_type(str): 主たる居室の放熱器の種類
      r_Af_1(float): 当該住戸における温水床暖房の敷設率 (-)

    Returns:
      float: 配管の断熱区画外における長さ (1a)

    """
    # 標準住戸における配管の断熱区画外における長さ
    L_pp_ex_i_R = get_L_pp_ex_R_i(i, underfloor_pipe_insulation, MR_rad_type, r_Af_1)

    # 標準住戸の床面積の合計
    A_A_R = get_A_A_R()

    return L_pp_ex_i_R * sqrt(A_A / A_A_R)


def calc_L_pp_in_i(i, A_A, underfloor_pipe_insulation, MR_rad_type, r_Af_1):
    """配管の断熱区画内における長さ (1b)

    Args:
      i(int): 暖冷房区画の番号
      A_A(float): 床面積の合計 (m2)
      underfloor_pipe_insulation(bool): 床下配管断熱の有無
      MR_rad_type(str): 主たる居室の放熱器の種類
      r_Af_1(float): 当該住戸における温水床暖房の敷設率 (-)

    Returns:
      float: 配管の断熱区画内における長さ (1b)

    """
    # 標準住戸における配管の断熱区画内における長さ
    L_pp_in_i_R = get_L_pp_in_R_i(i, underfloor_pipe_insulation, MR_rad_type, r_Af_1)

    # 標準住戸の床面積の合計
    A_A_R = get_A_A_R()

    return L_pp_in_i_R * sqrt(A_A / A_A_R)


def get_A_A_R():
    """標準住戸の床面積の合計

    Args:

    Returns:
      float: 標準住戸の床面積の合計

    """
    return 120.08


def get_L_pp_ex_R_i(i, underfloor_pipe_insulation, MR_rad_type, r_Af_1=None):
    """標準住戸における配管の断熱区画外における長さ

    Args:
      i(int): 暖冷房区画の番号
      underfloor_pipe_insulation(bool): 床下配管断熱の有無
      MR_rad_type(str): 主たる居室の放熱器の種類
      r_Af_1(float, optional): 当該住戸における温水床暖房の敷設率 (-) (Default value = None)

    Returns:
      float: 標準住戸における配管の断熱区画外における長さ

    """
    if underfloor_pipe_insulation:
        if i in [1]:
            L_pp_ex_R_i = get_table_i_3()[0][0]
        elif i in [3, 4, 5]:
            L_pp_ex_R_i = get_table_i_3()[0][i - 2]
        else:
            raise ValueError(i)
    else:
        if i in [1]:
            L_pp_ex_R_i = get_table_i_3()[2][0]
        elif i in [3, 4, 5]:
            L_pp_ex_R_i = get_table_i_3()[2][i - 2]
        else:
            raise ValueError(i)

    if callable(L_pp_ex_R_i):
        return L_pp_ex_R_i(MR_rad_type, r_Af_1)
    else:
        return L_pp_ex_R_i


def get_L_pp_in_R_i(i, underfloor_pipe_insulation, MR_rad_type, r_Af_1):
    """標準住戸における配管の断熱区画内における長さ

    Args:
      i(int): 暖冷房区画の番号
      underfloor_pipe_insulation(bool): 床下配管断熱の有無
      MR_rad_type(str): 主たる居室の放熱器の種類
      r_Af_1(float): 当該住戸における温水床暖房の敷設率 (-)

    Returns:
      float: 標準住戸における配管の断熱区画内における長さ

    """
    if underfloor_pipe_insulation:
        if i in [1]:
            L_pp_in_R_i = get_table_i_3()[1][0]
        elif i in [3, 4, 5]:
            L_pp_in_R_i = get_table_i_3()[1][i - 2]
        else:
            raise ValueError()
    else:
        if i in [1]:
            L_pp_in_R_i = get_table_i_3()[3][0]
        elif i in [3, 4, 5]:
            L_pp_in_R_i = get_table_i_3()[3][i - 2]
        else:
            raise ValueError()

    if callable(L_pp_in_R_i):
        return L_pp_in_R_i(MR_rad_type, r_Af_1)
    else:
        return L_pp_in_R_i


def get_L_pp_R_1(MR_rad_type, r_Af_1=None):
    """標準住戸における暖冷房区画1に対する配管1の長さ (2)

    Args:
      MR_rad_type(str): 主たる居室の放熱器の種類
      r_Af_1(float, optional): 当該住戸における温水床暖房の敷設率 (-) (Default value = None)

    Returns:
      float: 標準住戸における暖冷房区画1に対する配管1の長さ (2)

    """
    if MR_rad_type in ['温水暖房用床暖房', '温水床暖房（併用運転に対応）']:
        # 4章7節付録Iでは敷設率の計算に関する記述が無いが、
        # 本実装では下記のようにする
        #
        # 敷設率𝑅𝑙,𝑖は、電気ヒーター床暖房の場合は第四章「暖冷房設備」第五節「電気ヒーター床暖房」付録 A、温水
        # 床暖房の場合は第四章「暖冷房設備」第七節「温水暖房」付録 L で定まる床暖房の敷設率𝑟𝐴𝑓とする
        # どちらの場合でも規定値は0.4のため、便宜上本関数内で規定値を0.4にする
        if r_Af_1 is None:
            r_Af_1 = 0.40
        
        # (2a)
        if 0 < r_Af_1 and r_Af_1 <= 0.542:
            return 16.38
        elif 0.542 < r_Af_1 and r_Af_1 <= 0.75:
            return 16.38 * (0.75 - r_Af_1) / (0.75 - 0.542) + 29.58 * (r_Af_1 - 0.542) / (0.75 - 0.542)
        elif 0.75 < r_Af_1 and r_Af_1 <= 1:
            return 29.58
        else:
            raise NotImplementedError()
    elif MR_rad_type == '温水暖房用パネルラジエーター' or MR_rad_type == '温水暖房用ファンコンベクター':
        return 29.58
    else:
        raise ValueError(MR_rad_type)


def get_table_i_3():
    """表I.3 係数L_pp_ex_R及びL_pp_in_R

    Args:

    Returns:
      list: 表I.3 係数L_pp_ex_R及びL_pp_in_R

    """
    table_i_3 = [
        (0.00, 0.00, 0.00, 0.00),
        (get_L_pp_R_1, 22.86, 19.22, 26.62),
        (get_L_pp_R_1, 0.00, 0.00, 0.00),
        (0.00, 22.86, 19.22, 26.62)
    ]
    return table_i_3
