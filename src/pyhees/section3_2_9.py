# ============================================================================
# 9. 当該住戸の外皮の部位の面積等を用いずに外皮性能を評価する方法
# ============================================================================

import os
import pandas as pd
import numpy as np
from math import ceil, floor

from pyhees.section3_2_b import get_H
from pyhees.section3_2_c import get_nu_H, get_nu_C
import pyhees.section3_4 as eater


# ============================================================================
# 9.2 主開口方位
# ============================================================================

# 標準住戸における主開口方位は南西とする。

# ============================================================================
# 9.3 外皮平均熱貫流率
# ============================================================================

def __calc_U_A(house_insulation_type, floor_bath_insulation, U_roof, U_wall, U_door, U_window, U_floor_bath, H_floor_bath, U_floor_other, H_floor_other,
               U_base_etrc, U_base_bath, U_base_other,
               Psi_prm_etrc, Psi_prm_bath, Psi_prm_other,
               Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall, Psi_HB_wall_wall, Psi_HB_wall_floor):
    """ 外皮平均熱貫流率

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない
      U_roof(float): 屋根又は天井の熱貫流率
      U_wall(float): 壁の熱貫流率
      U_door(float): ドアの熱貫流率
      U_window(float): 窓の熱貫流率
      U_floor_bath(float): 浴室の床の熱貫流率
      H_floor_bath(float): 浴室の床の温度差係数
      U_floor_other(float): その他の熱貫流率
      H_floor_other(float): その他の床の温度差係数
      U_base_etrc(float): 玄関等の基礎の熱貫流率
      U_base_bath(float): 浴室の基礎の熱貫流率
      U_base_other(float): その他の基礎の熱貫流率
      Psi_prm_etrc(float): 玄関等の土間床等の外周部の線熱貫流率
      Psi_prm_bath(float): 浴室の土間床等の外周部の線熱貫流率
      Psi_prm_other(float): その他の土間床等の外周部の線熱貫流率
      Psi_HB_roof(float): 屋根または天井の熱橋の線熱貫流率
      Psi_HB_wall(float): 壁の熱橋の線熱貫流率
      Psi_HB_floor(float): 床の熱橋の線熱貫流率
      Psi_HB_roof_wall(float): 屋根または天井と壁の熱橋の線熱貫流率
      Psi_HB_wall_wall(float): 壁と壁の熱橋の線熱貫流率
      Psi_HB_wall_floor(float): 壁と床の熱橋の線熱貫流率

    Returns:
      float: 外皮平均熱貫流率

    """
    # 単位温度差当たりの外皮熱損失量[W/K] (9b)
    q = get_q(house_insulation_type, floor_bath_insulation,
              U_roof, U_wall, U_door, U_window, U_floor_bath, H_floor_bath, U_floor_other, H_floor_other,
              U_base_etrc, U_base_bath, U_base_other,
              Psi_prm_etrc, Psi_prm_bath, Psi_prm_other,
              Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
              Psi_HB_wall_wall, Psi_HB_wall_floor
              )

    # 外部部位の面積の合計 (m2)
    A_dash_env = get_A_dash_env(house_insulation_type, floor_bath_insulation)

    # 外皮平均熱貫流率 (9a)
    U_A = get_U_A(q, A_dash_env)

    return U_A


def get_U_A(q, A_dash_env):
    """外皮平均熱貫流率 (9a)

    Args:
      q(float): 単位温度差当たりの外皮熱損失量 (W/K)
      A_dash_env(float): 標準住戸における外皮の部位の面積の合計 (m2)

    Returns:
      float: 外皮平均熱貫流率

    """
    U_A_raw = q / A_dash_env
    U_A = ceil(U_A_raw * 100) / 100
    return U_A



def get_q(house_insulation_type, floor_bath_insulation,
          U_roof, U_wall, U_door, U_window, U_floor_bath, H_floor_bath, U_floor_other, H_floor_other,
          U_base_etrc, U_base_bath, U_base_other,
          Psi_prm_etrc, Psi_prm_bath, Psi_prm_other,
          Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
          Psi_HB_wall_wall, Psi_HB_wall_floor
          ):
    """単位温度差当たりの外皮熱損失量[W/K] (9b)
         (主開口方位は南西とする)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
      U_roof(float): 屋根又は天井の熱貫流率
      U_wall(float): 壁の熱貫流率
      U_door(float): ドアの熱貫流率
      U_window(float): 窓の熱貫流率
      U_floor_bath(float): 浴室の床の熱貫流率
      H_floor_bath(float): 浴室の床の温度差係数
      U_floor_other(float): その他の熱貫流率
      H_floor_other(float): その他の床の温度差係数
      U_base_etrc(float): 玄関等の基礎の熱貫流率
      U_base_bath(float): 浴室の基礎の熱貫流率
      U_base_other(float): その他の基礎の熱貫流率
      Psi_prm_etrc(float): 玄関等の土間床等の外周部の線熱貫流率
      Psi_prm_bath(float): 浴室の土間床等の外周部の線熱貫流率
      Psi_prm_other(float): その他の土間床等の外周部の線熱貫流率
      Psi_HB_roof(float): 屋根または天井の熱橋の線熱貫流率
      Psi_HB_wall(float): 壁の熱橋の線熱貫流率
      Psi_HB_floor(float): 床の熱橋の線熱貫流率
      Psi_HB_roof_wall(float): 屋根または天井と壁の熱橋の線熱貫流率
      Psi_HB_wall_wall(float): 壁と壁の熱橋の線熱貫流率
      Psi_HB_wall_floor(float): 壁と床の熱橋の線熱貫流率

    Returns:
      float: 単位温度差当たりの外皮熱損失量[W/K]

    """

    A_dash_roof = get_A_dash_roof()
    A_dash_wall_0 = get_A_dash_wall_0()
    A_dash_wall_90 = get_A_dash_wall_90()
    A_dash_wall_180 = get_A_dash_wall_180()
    A_dash_wall_270 = get_A_dash_wall_270()
    A_dash_door_0 = get_A_dash_door_0()
    A_dash_door_90 = get_A_dash_door_90()
    A_dash_door_180 = get_A_dash_door_180()
    A_dash_door_270 = get_A_dash_door_270()
    A_dash_window_0 = get_A_dash_window_0()
    A_dash_window_90 = get_A_dash_window_90()
    A_dash_window_180 = get_A_dash_window_180()
    A_dash_window_270 = get_A_dash_window_270()
    A_dash_floor_bath = get_A_dash_floor_bath(house_insulation_type, floor_bath_insulation)
    A_dash_floor_other = get_A_dash_floor_other(house_insulation_type, floor_bath_insulation)
    A_dash_base_etrc_OS_0 = get_A_dash_base_etrc_OS_0()
    A_dash_base_etrc_OS_90 = get_A_dash_base_etrc_OS_90()
    A_dash_base_etrc_OS_180 = get_A_dash_base_etrc_OS_180()
    A_dash_base_etrc_OS_270 = get_A_dash_base_etrc_OS_270()
    A_dash_base_etrc_IS = get_A_dash_base_etrc_IS(house_insulation_type, floor_bath_insulation)
    A_dash_base_bath_OS_0 = get_A_dash_base_bath_OS_0(house_insulation_type, floor_bath_insulation)
    A_dash_base_bath_OS_90 = get_A_dash_base_bath_OS_90(house_insulation_type, floor_bath_insulation)
    A_dash_base_bath_OS_180 = get_A_dash_base_bath_OS_180(house_insulation_type, floor_bath_insulation)
    A_dash_base_bath_OS_270 = get_A_dash_base_bath_OS_270(house_insulation_type, floor_bath_insulation)
    A_dash_base_bath_IS = get_A_dash_base_bath_IS(house_insulation_type, floor_bath_insulation)
    A_dash_base_other_OS_0 = get_A_dash_base_other_OS_0(house_insulation_type, floor_bath_insulation)
    A_dash_base_other_OS_90 = get_A_dash_base_other_OS_90(house_insulation_type, floor_bath_insulation)
    A_dash_base_other_OS_180 = get_A_dash_base_other_OS_180(house_insulation_type, floor_bath_insulation)
    A_dash_base_other_OS_270 = get_A_dash_base_other_OS_270(house_insulation_type, floor_bath_insulation)
    A_dash_base_other_IS = get_A_dash_base_other_IS(house_insulation_type, floor_bath_insulation)
    L_dash_prm_etrc_OS_0 = get_L_dash_prm_etrc_OS_0()
    L_dash_prm_etrc_OS_90 = get_L_dash_prm_etrc_OS_90()
    L_dash_prm_etrc_OS_180 = get_L_dash_prm_etrc_OS_180()
    L_dash_prm_etrc_OS_270 = get_L_dash_prm_etrc_OS_270()
    L_dash_prm_etrc_IS = get_L_dash_prm_etrc_IS(house_insulation_type, floor_bath_insulation)
    L_dash_prm_bath_OS_0 = get_L_dash_prm_bath_OS_0(house_insulation_type, floor_bath_insulation)
    L_dash_prm_bath_OS_90 = get_L_dash_prm_bath_OS_90(house_insulation_type, floor_bath_insulation)
    L_dash_prm_bath_OS_180 = get_L_dash_prm_bath_OS_180(house_insulation_type, floor_bath_insulation)
    L_dash_prm_bath_OS_270 = get_L_dash_prm_bath_OS_270(house_insulation_type, floor_bath_insulation)
    L_dash_prm_bath_IS = get_L_dash_prm_bath_IS(house_insulation_type, floor_bath_insulation)
    L_dash_prm_other_OS_0 = get_L_dash_prm_other_OS_0(house_insulation_type, floor_bath_insulation)
    L_dash_prm_other_OS_90 = get_L_dash_prm_other_OS_90(house_insulation_type, floor_bath_insulation)
    L_dash_prm_other_OS_180 = get_L_dash_prm_other_OS_180(house_insulation_type, floor_bath_insulation)
    L_dash_prm_other_OS_270 = get_L_dash_prm_other_OS_270(house_insulation_type, floor_bath_insulation)
    L_dash_prm_other_IS = get_L_dash_prm_other_IS(house_insulation_type, floor_bath_insulation)
    L_dash_HB_roof_top = get_L_dash_HB_roof_top()
    L_dash_HB_wall_0 = get_L_dash_HB_wall_0()
    L_dash_HB_wall_90 = get_L_dash_HB_wall_90()
    L_dash_HB_wall_180 = get_L_dash_HB_wall_180()
    L_dash_HB_wall_270 = get_L_dash_HB_wall_270()
    L_dash_HB_floor_IS = get_L_dash_HB_floor_IS(house_insulation_type, floor_bath_insulation)
    L_dash_HB_roof_wall_top_0 = get_L_dash_HB_roof_wall_top_0()
    L_dash_HB_roof_wall_top_90 = get_L_dash_HB_roof_wall_top_90()
    L_dash_HB_roof_wall_top_180 = get_L_dash_HB_roof_wall_top_180()
    L_dash_HB_roof_wall_top_270 = get_L_dash_HB_roof_wall_top_270()
    L_dash_HB_wall_wall_0_90 = get_L_dash_HB_wall_wall_0_90()
    L_dash_HB_wall_wall_90_180 = get_L_dash_HB_wall_wall_90_180()
    L_dash_HB_wall_wall_180_270 = get_L_dash_HB_wall_wall_180_270()
    L_dash_HB_wall_wall_270_0 = get_L_dash_HB_wall_wall_270_0()
    L_dash_HB_wall_floor_0_IS = get_L_dash_HB_wall_floor_0_IS()
    L_dash_HB_wall_floor_90_IS = get_L_dash_HB_wall_floor_90_IS()
    L_dash_HB_wall_floor_180_IS = get_L_dash_HB_wall_floor_180_IS()
    L_dash_HB_wall_floor_270_IS = get_L_dash_HB_wall_floor_270_IS()

    # 温度差係数
    H_OS = get_H_OS()
    H_IS = get_H_IS()

    q_list = [
        # 屋根又は天井
        A_dash_roof * H_OS * U_roof,
        # 壁
        (A_dash_wall_0
         + A_dash_wall_90
         + A_dash_wall_180
         + A_dash_wall_270) * H_OS * U_wall,
        # ドア
        (A_dash_door_0
         + A_dash_door_90
         + A_dash_door_180
         + A_dash_door_270) * H_OS * U_door,
        # 窓
        (A_dash_window_0
         + A_dash_window_90
         + A_dash_window_180
         + A_dash_window_270) * H_OS * U_window,
        # floor bath
        A_dash_floor_bath * H_floor_bath * U_floor_bath,
        # floor other
        A_dash_floor_other * H_floor_other * U_floor_other,
        # 玄関等の基礎
        ((A_dash_base_etrc_OS_0
          + A_dash_base_etrc_OS_90
          + A_dash_base_etrc_OS_180
          + A_dash_base_etrc_OS_270) * H_OS
         + A_dash_base_etrc_IS * H_IS) * U_base_etrc,
        # 浴室の床
        ((A_dash_base_bath_OS_0
          + A_dash_base_bath_OS_90
          + A_dash_base_bath_OS_180
          + A_dash_base_bath_OS_270) * H_OS
         + A_dash_base_bath_IS * H_IS) * U_base_bath,
        # その他
        ((A_dash_base_other_OS_0
          + A_dash_base_other_OS_90
          + A_dash_base_other_OS_180
          + A_dash_base_other_OS_270) * H_OS
         + A_dash_base_other_IS * H_IS) * U_base_other,
        # 玄関等の土間床等の外周部
        ((L_dash_prm_etrc_OS_0
          + L_dash_prm_etrc_OS_90
          + L_dash_prm_etrc_OS_180
          + L_dash_prm_etrc_OS_270) * H_OS
         + L_dash_prm_etrc_IS * H_IS) * Psi_prm_etrc,
        # 浴室の土間床等の外周部
        ((L_dash_prm_bath_OS_0
          + L_dash_prm_bath_OS_90
          + L_dash_prm_bath_OS_180
          + L_dash_prm_bath_OS_270) * H_OS
         + L_dash_prm_bath_IS * H_IS) * Psi_prm_bath,
        # その他の土間床等の外周部
        ((L_dash_prm_other_OS_0
          + L_dash_prm_other_OS_90
          + L_dash_prm_other_OS_180
          + L_dash_prm_other_OS_270) * H_OS
         + L_dash_prm_other_IS * H_IS) * Psi_prm_other,
        # 屋根または天井の熱橋
        L_dash_HB_roof_top * H_OS * Psi_HB_roof,
        # 壁の熱橋
        (L_dash_HB_wall_0
         + L_dash_HB_wall_90
         + L_dash_HB_wall_180
         + L_dash_HB_wall_270) * H_OS * Psi_HB_wall,
        # 床の熱橋
        L_dash_HB_floor_IS * H_IS * Psi_HB_floor,
        # 屋根または天井と壁の熱橋
        (L_dash_HB_roof_wall_top_0
         + L_dash_HB_roof_wall_top_90
         + L_dash_HB_roof_wall_top_180
         + L_dash_HB_roof_wall_top_270) * H_OS * Psi_HB_roof_wall,
        # 壁と壁の熱橋
        (L_dash_HB_wall_wall_0_90
         + L_dash_HB_wall_wall_90_180
         + L_dash_HB_wall_wall_180_270
         + L_dash_HB_wall_wall_270_0) * H_OS * Psi_HB_wall_wall,
        # 壁と床の熱橋
        (L_dash_HB_wall_floor_0_IS
         + L_dash_HB_wall_floor_90_IS
         + L_dash_HB_wall_floor_180_IS
         + L_dash_HB_wall_floor_270_IS) * H_OS * Psi_HB_wall_floor,
    ]

    q = sum(q_list)

    return q


# ============================================================================
# 9.4 暖房期の平均日射熱取得率及び冷房期の平均日射熱取得率
# ============================================================================

def get_eta_A_H(m_H, A_dash_env):
    """暖房期の平均日射熱取得率 (10a)

    Args:
      m_H(float): 単位日射強度当たりの暖房期の日射熱取得量 (W/(W/m2))
      A_dash_env(float): 標準住戸における外皮の部位の面積の合計 (m2)

    Returns:
      float: 暖房期の平均日射熱取得率

    """

    if m_H is None:
        return None
    etr_A_H = m_H / A_dash_env * 100
    return floor(etr_A_H * 10) / 10


def get_m_H(region, house_insulation_type, floor_bath_insulation, U_roof, U_wall, U_door,
            U_base_etrc, U_base_bath, U_base_other, Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
            Psi_HB_wall_wall, Psi_HB_wall_floor, etr_d, f_H=None):
    """単位日射強度当たりの暖房期の日射熱取得量[W/(W/m2)] (10b)

    Args:
      region(int): 省エネルギー地域区分
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
      U_roof(float): 屋根又は天井の熱貫流率
      U_wall(float): 壁の熱貫流率
      U_door(float): ドアの熱貫流率
      U_base_etrc(float): 玄関等の基礎の熱貫流率
      U_base_bath(float): 浴室の基礎の熱貫流率
      U_base_other(float): その他の基礎の熱貫流率
      Psi_HB_roof(float): 屋根または天井の熱橋の線熱貫流率
      Psi_HB_wall(float): 壁の熱橋の線熱貫流率
      Psi_HB_floor(float): 床の熱橋の線熱貫流率
      Psi_HB_roof_wall(float): 屋根または天井と壁の熱橋の線熱貫流率
      Psi_HB_wall_wall(float): 壁と壁の熱橋の線熱貫流率
      Psi_HB_wall_floor(float): 壁と床の熱橋の線熱貫流率
      etr_d(float): 暖房期の垂直面日射熱取得率 (-)
      f_H(float, optional): 暖房期の取得日射熱補正係数 (-) (Default value = None)

    Returns:
      float: 単位日射強度当たりの暖房期の日射熱取得量[W/(W/m2)]

    """

    if region == 8:
        return None

    A_dash_roof = get_A_dash_roof()
    A_dash_wall_0 = get_A_dash_wall_0()
    A_dash_wall_90 = get_A_dash_wall_90()
    A_dash_wall_180 = get_A_dash_wall_180()
    A_dash_wall_270 = get_A_dash_wall_270()
    A_dash_door_0 = get_A_dash_door_0()
    A_dash_door_90 = get_A_dash_door_90()
    A_dash_door_180 = get_A_dash_door_180()
    A_dash_door_270 = get_A_dash_door_270()
    A_dash_window_0 = get_A_dash_window_0()
    A_dash_window_90 = get_A_dash_window_90()
    A_dash_window_180 = get_A_dash_window_180()
    A_dash_window_270 = get_A_dash_window_270()
    A_dash_base_etrc_OS_0 = get_A_dash_base_etrc_OS_0()
    A_dash_base_etrc_OS_90 = get_A_dash_base_etrc_OS_90()
    A_dash_base_etrc_OS_180 = get_A_dash_base_etrc_OS_180()
    A_dash_base_etrc_OS_270 = get_A_dash_base_etrc_OS_270()
    A_dash_base_bath_OS_0 = get_A_dash_base_bath_OS_0(house_insulation_type, floor_bath_insulation)
    A_dash_base_bath_OS_90 = get_A_dash_base_bath_OS_90(house_insulation_type, floor_bath_insulation)
    A_dash_base_bath_OS_180 = get_A_dash_base_bath_OS_180(house_insulation_type, floor_bath_insulation)
    A_dash_base_bath_OS_270 = get_A_dash_base_bath_OS_270(house_insulation_type, floor_bath_insulation)
    A_dash_base_other_OS_0 = get_A_dash_base_other_OS_0(house_insulation_type, floor_bath_insulation)
    A_dash_base_other_OS_90 = get_A_dash_base_other_OS_90(house_insulation_type, floor_bath_insulation)
    A_dash_base_other_OS_180 = get_A_dash_base_other_OS_180(house_insulation_type, floor_bath_insulation)
    A_dash_base_other_OS_270 = get_A_dash_base_other_OS_270(house_insulation_type, floor_bath_insulation)
    L_dash_HB_roof_top = get_L_dash_HB_roof_top()
    L_dash_HB_wall_0 = get_L_dash_HB_wall_0()
    L_dash_HB_wall_90 = get_L_dash_HB_wall_90()
    L_dash_HB_wall_180 = get_L_dash_HB_wall_180()
    L_dash_HB_wall_270 = get_L_dash_HB_wall_270()
    L_dash_HB_roof_wall_top_0 = get_L_dash_HB_roof_wall_top_0()
    L_dash_HB_roof_wall_top_90 = get_L_dash_HB_roof_wall_top_90()
    L_dash_HB_roof_wall_top_180 = get_L_dash_HB_roof_wall_top_180()
    L_dash_HB_roof_wall_top_270 = get_L_dash_HB_roof_wall_top_270()
    L_dash_HB_wall_wall_0_90 = get_L_dash_HB_wall_wall_0_90()
    L_dash_HB_wall_wall_90_180 = get_L_dash_HB_wall_wall_90_180()
    L_dash_HB_wall_wall_180_270 = get_L_dash_HB_wall_wall_180_270()
    L_dash_HB_wall_wall_270_0 = get_L_dash_HB_wall_wall_270_0()
    L_dash_HB_wall_floor_0_IS = get_L_dash_HB_wall_floor_0_IS()
    L_dash_HB_wall_floor_90_IS = get_L_dash_HB_wall_floor_90_IS()
    L_dash_HB_wall_floor_180_IS = get_L_dash_HB_wall_floor_180_IS()
    L_dash_HB_wall_floor_270_IS = get_L_dash_HB_wall_floor_270_IS()


    # 方位係数：主方位=南西
    nu_H_top = get_nu_H(region, '上面')
    nu_H_0 = get_nu_H(region, '南西')
    nu_H_90 = get_nu_H(region, '北西')
    nu_H_180 = get_nu_H(region, '北東')
    nu_H_270 = get_nu_H(region, '南東')
    # 付録Cより：方位の異なる外皮の部位（一般部位又は開口部）に接する熱橋等の方位係数は、異なる方位の方位係数の平均値とする。
    nu_H_top_0 = (get_nu_H(region, '上面') + get_nu_H(region, '南西')) / 2
    nu_H_top_90 = (get_nu_H(region, '上面') + get_nu_H(region, '北西')) / 2
    nu_H_top_180 = (get_nu_H(region, '上面') + get_nu_H(region, '北東')) / 2
    nu_H_top_270 = (get_nu_H(region, '上面') + get_nu_H(region, '南東')) / 2
    nu_H_0_90 = (get_nu_H(region, '南西') + get_nu_H(region, '北西')) / 2
    nu_H_90_180 = (get_nu_H(region, '北西') + get_nu_H(region, '北東')) / 2
    nu_H_180_270 = (get_nu_H(region, '北東') + get_nu_H(region, '南東')) / 2
    nu_H_270_0 = (get_nu_H(region, '南東') + get_nu_H(region, '南西')) / 2
    nu_H_0_IS = (get_nu_H(region, '南西') + get_nu_H(region, '下面')) / 2
    nu_H_90_IS = (get_nu_H(region, '北西') + get_nu_H(region, '下面')) / 2
    nu_H_180_IS = (get_nu_H(region, '北東') + get_nu_H(region, '下面')) / 2
    nu_H_270_IS = (get_nu_H(region, '南東') + get_nu_H(region, '下面')) / 2

    # 屋根又は天井・壁・ドアの日射熱取得率
    eta_H_roof = calc_eta_H_roof(U_roof)
    eta_H_wall = calc_eta_H_wall(U_wall)
    eta_H_door = calc_eta_H_door(U_door)

    # 窓の日射熱取得率
    eta_H_window_0, eta_H_window_90, eta_H_window_180, eta_H_window_270 = calc_eta_H_window(region, etr_d, f_H)

    # 玄関等・浴室・その他の基礎の日射熱取得率
    eta_H_base_etrc = calc_eta_H_base_etrc(U_base_etrc)
    eta_H_base_bath = calc_eta_H_base_bath(U_base_bath)
    eta_H_base_other = calc_eta_H_base_other(U_base_other)

    # 熱橋の日射熱取得率
    eta_dash_H_HB_roof = calc_eta_dash_H_HB_roof(Psi_HB_roof)
    eta_dash_H_HB_wall = calc_eta_dash_H_HB_wall(Psi_HB_wall)
    eta_dash_H_HB_roof_wall = calc_eta_dash_H_HB_roof_wall(Psi_HB_roof_wall)
    eta_dash_H_HB_wall_wall = calc_eta_dash_H_HB_wall_wall(Psi_HB_wall_wall)
    eta_dash_H_HB_wall_floor = calc_eta_dash_H_HB_wall_floor(Psi_HB_wall_floor)

    m_H_list = [
        # roof
        A_dash_roof * nu_H_top * eta_H_roof,
        # wall
        (A_dash_wall_0 * nu_H_0
         + A_dash_wall_90 * nu_H_90
         + A_dash_wall_180 * nu_H_180
         + A_dash_wall_270 * nu_H_270) * eta_H_wall,
        # door
        (A_dash_door_0 * nu_H_0
         + A_dash_door_90 * nu_H_90
         + A_dash_door_180 * nu_H_180
         + A_dash_door_270 * nu_H_270) * eta_H_door,
        # window
        (A_dash_window_0 * nu_H_0 * eta_H_window_0
         + A_dash_window_90 * nu_H_90 * eta_H_window_90
         + A_dash_window_180 * nu_H_180 * eta_H_window_180
         + A_dash_window_270 * nu_H_270 * eta_H_window_270),
        # base entrance
        (A_dash_base_etrc_OS_0 * nu_H_0
         + A_dash_base_etrc_OS_90 * nu_H_90
         + A_dash_base_etrc_OS_180 * nu_H_180
         + A_dash_base_etrc_OS_270 * nu_H_270) * eta_H_base_etrc,
        # base bath
        (A_dash_base_bath_OS_0 * nu_H_0
         + A_dash_base_bath_OS_90 * nu_H_90
         + A_dash_base_bath_OS_180 * nu_H_180
         + A_dash_base_bath_OS_270 * nu_H_270) * eta_H_base_bath,
        # base other
        (A_dash_base_other_OS_0 * nu_H_0
         + A_dash_base_other_OS_90 * nu_H_90
         + A_dash_base_other_OS_180 * nu_H_180
         + A_dash_base_other_OS_270 * nu_H_270) * eta_H_base_other,
        # HB roof
        L_dash_HB_roof_top * nu_H_top * eta_dash_H_HB_roof,
        # HB wall
        (L_dash_HB_wall_0 * nu_H_0
         + L_dash_HB_wall_90 * nu_H_90
         + L_dash_HB_wall_180 * nu_H_180
         + L_dash_HB_wall_270 * nu_H_270) * eta_dash_H_HB_wall,
        # HB roof_wall
        (L_dash_HB_roof_wall_top_0 * nu_H_top_0
         + L_dash_HB_roof_wall_top_90 * nu_H_top_90
         + L_dash_HB_roof_wall_top_180 * nu_H_top_180
         + L_dash_HB_roof_wall_top_270 * nu_H_top_270) * eta_dash_H_HB_roof_wall,
        # HB wall_wall
        (L_dash_HB_wall_wall_0_90 * nu_H_0_90
         + L_dash_HB_wall_wall_90_180 * nu_H_90_180
         + L_dash_HB_wall_wall_180_270 * nu_H_180_270
         + L_dash_HB_wall_wall_270_0 * nu_H_270_0) * eta_dash_H_HB_wall_wall,
        # HB wall_floor
        (L_dash_HB_wall_floor_0_IS * nu_H_0_IS
         + L_dash_HB_wall_floor_90_IS * nu_H_90_IS
         + L_dash_HB_wall_floor_180_IS * nu_H_180_IS
         + L_dash_HB_wall_floor_270_IS * nu_H_270_IS) * eta_dash_H_HB_wall_floor
    ]

    m_H = sum(m_H_list)

    return m_H


def get_eta_A_C(m_C, A_dash_env):
    """冷房期の平均日射熱取得率 (-) (11a)

    Args:
      m_C(float): 単位日射強度当たりの冷房期の日射熱取得量 (W/(W/m2))
      A_dash_env(float): 標準住戸における外皮の部位の面積の合計 (m2)

    Returns:
      float: 冷房期の平均日射熱取得率 (-)

    """

    etr_A_C = m_C / A_dash_env * 100
    return ceil(etr_A_C * 10) / 10


def get_m_C(region, house_insulation_type, floor_bath_insulation, U_roof, U_wall, U_door,
            U_base_etrc, U_base_bath, U_base_other, Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
            Psi_HB_wall_wall, Psi_HB_wall_floor, etr_d, f_C=None):
    """単位日射強度当たりの冷房期の日射熱取得量[W/(W/m2)] (11b)

    Args:
      region(int): 省エネルギー地域区分
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
      U_roof(float): 屋根又は天井の熱貫流率
      U_wall(float): 壁の熱貫流率
      U_door(float): ドアの熱貫流率
      U_base_etrc(float): 玄関等の基礎の熱貫流率
      U_base_bath(float): 浴室の基礎の熱貫流率
      U_base_other(float): その他の基礎の熱貫流率
      Psi_HB_roof(float): 屋根または天井の熱橋の線熱貫流率
      Psi_HB_wall(float): 壁の熱橋の線熱貫流率
      Psi_HB_floor(float): 床の熱橋の線熱貫流率
      Psi_HB_roof_wall(float): 屋根または天井と壁の熱橋の線熱貫流率
      Psi_HB_wall_wall(float): 壁と壁の熱橋の線熱貫流率
      Psi_HB_wall_floor(float): 壁と床の熱橋の線熱貫流率
      etr_d(float): 暖房期の垂直面日射熱取得率 (-)
      f_C(float, optional): 冷房期の取得日射熱補正係数 (-) (Default value = None)

    Returns:
      float: 単位日射強度当たりの冷房期の日射熱取得量[W/(W/m2)]

    """

    A_dash_roof = get_A_dash_roof()
    A_dash_wall_0 = get_A_dash_wall_0()
    A_dash_wall_90 = get_A_dash_wall_90()
    A_dash_wall_180 = get_A_dash_wall_180()
    A_dash_wall_270 = get_A_dash_wall_270()
    A_dash_door_0 = get_A_dash_door_0()
    A_dash_door_90 = get_A_dash_door_90()
    A_dash_door_180 = get_A_dash_door_180()
    A_dash_door_270 = get_A_dash_door_270()
    A_dash_window_0 = get_A_dash_window_0()
    A_dash_window_90 = get_A_dash_window_90()
    A_dash_window_180 = get_A_dash_window_180()
    A_dash_window_270 = get_A_dash_window_270()
    A_dash_base_etrc_OS_0 = get_A_dash_base_etrc_OS_0()
    A_dash_base_etrc_OS_90 = get_A_dash_base_etrc_OS_90()
    A_dash_base_etrc_OS_180 = get_A_dash_base_etrc_OS_180()
    A_dash_base_etrc_OS_270 = get_A_dash_base_etrc_OS_270()
    A_dash_base_bath_OS_0 = get_A_dash_base_bath_OS_0(house_insulation_type, floor_bath_insulation)
    A_dash_base_bath_OS_90 = get_A_dash_base_bath_OS_90(house_insulation_type, floor_bath_insulation)
    A_dash_base_bath_OS_180 = get_A_dash_base_bath_OS_180(house_insulation_type, floor_bath_insulation)
    A_dash_base_bath_OS_270 = get_A_dash_base_bath_OS_270(house_insulation_type, floor_bath_insulation)
    A_dash_base_other_OS_0 = get_A_dash_base_other_OS_0(house_insulation_type, floor_bath_insulation)
    A_dash_base_other_OS_90 = get_A_dash_base_other_OS_90(house_insulation_type, floor_bath_insulation)
    A_dash_base_other_OS_180 = get_A_dash_base_other_OS_180(house_insulation_type, floor_bath_insulation)
    A_dash_base_other_OS_270 = get_A_dash_base_other_OS_270(house_insulation_type, floor_bath_insulation)
    L_dash_HB_roof_top = get_L_dash_HB_roof_top()
    L_dash_HB_wall_0 = get_L_dash_HB_wall_0()
    L_dash_HB_wall_90 = get_L_dash_HB_wall_90()
    L_dash_HB_wall_180 = get_L_dash_HB_wall_180()
    L_dash_HB_wall_270 = get_L_dash_HB_wall_270()
    L_dash_HB_roof_wall_top_0 = get_L_dash_HB_roof_wall_top_0()
    L_dash_HB_roof_wall_top_90 = get_L_dash_HB_roof_wall_top_90()
    L_dash_HB_roof_wall_top_180 = get_L_dash_HB_roof_wall_top_180()
    L_dash_HB_roof_wall_top_270 = get_L_dash_HB_roof_wall_top_270()
    L_dash_HB_wall_wall_0_90 = get_L_dash_HB_wall_wall_0_90()
    L_dash_HB_wall_wall_90_180 = get_L_dash_HB_wall_wall_90_180()
    L_dash_HB_wall_wall_180_270 = get_L_dash_HB_wall_wall_180_270()
    L_dash_HB_wall_wall_270_0 = get_L_dash_HB_wall_wall_270_0()
    L_dash_HB_wall_floor_0_IS = get_L_dash_HB_wall_floor_0_IS()
    L_dash_HB_wall_floor_90_IS = get_L_dash_HB_wall_floor_90_IS()
    L_dash_HB_wall_floor_180_IS = get_L_dash_HB_wall_floor_180_IS()
    L_dash_HB_wall_floor_270_IS = get_L_dash_HB_wall_floor_270_IS()

    # 方位係数：主方位=南西
    nu_C_top = get_nu_C(region, '上面')
    nu_C_0 = get_nu_C(region, '南西')
    nu_C_90 = get_nu_C(region, '北西')
    nu_C_180 = get_nu_C(region, '北東')
    nu_C_270 = get_nu_C(region, '南東')
    # 付録Cより：方位の異なる外皮の部位（一般部位又は開口部）に接する熱橋等の方位係数は、異なる方位の方位係数の平均値とする。
    nu_C_top_0 = (get_nu_C(region, '上面') + get_nu_C(region, '南西')) / 2
    nu_C_top_90 = (get_nu_C(region, '上面') + get_nu_C(region, '北西')) / 2
    nu_C_top_180 = (get_nu_C(region, '上面') + get_nu_C(region, '北東')) / 2
    nu_C_top_270 = (get_nu_C(region, '上面') + get_nu_C(region, '南東')) / 2
    nu_C_0_90 = (get_nu_C(region, '南西') + get_nu_C(region, '北西')) / 2
    nu_C_90_180 = (get_nu_C(region, '北西') + get_nu_C(region, '北東')) / 2
    nu_C_180_270 = (get_nu_C(region, '北東') + get_nu_C(region, '南東')) / 2
    nu_C_270_0 = (get_nu_C(region, '南東') + get_nu_C(region, '南西')) / 2
    nu_C_0_IS = (get_nu_C(region, '南西') + get_nu_C(region, '下面')) / 2
    nu_C_90_IS = (get_nu_C(region, '北西') + get_nu_C(region, '下面')) / 2
    nu_C_180_IS = (get_nu_C(region, '北東') + get_nu_C(region, '下面')) / 2
    nu_C_270_IS = (get_nu_C(region, '南東') + get_nu_C(region, '下面')) / 2

    # 屋根又は天井・壁・ドアの日射熱取得率
    eta_C_roof = calc_eta_C_roof(U_roof)
    eta_C_wall = calc_eta_C_wall(U_wall)
    eta_C_door = calc_eta_C_door(U_door)

    # 窓の日射熱取得率
    eta_C_window_0, eta_C_window_90, eta_C_window_180, eta_C_window_270 = calc_eta_C_window(region, etr_d, f_C)

    # 玄関等・浴室・その他の基礎の日射熱取得率
    eta_C_base_etrc = calc_eta_C_base_etrc(U_base_etrc)
    eta_C_base_bath = calc_eta_C_base_bath(U_base_bath)
    eta_C_base_other = calc_eta_C_base_other(U_base_other)

    # 熱橋の日射熱取得率
    eta_dash_C_HB_roof = calc_eta_dash_C_HB_roof(Psi_HB_roof)
    eta_dash_C_HB_wall = calc_eta_dash_C_HB_wall(Psi_HB_wall)
    eta_dash_C_HB_roof_wall = calc_eta_dash_C_HB_roof_wall(Psi_HB_roof_wall)
    eta_dash_C_HB_wall_wall = calc_eta_dash_C_HB_wall_wall(Psi_HB_wall_wall)
    eta_dash_C_HB_wall_floor = calc_eta_dash_C_HB_wall_floor(Psi_HB_wall_floor)

    m_C_list = [
        # roof
        A_dash_roof * nu_C_top * eta_C_roof,
        # wall
        (A_dash_wall_0 * nu_C_0
         + A_dash_wall_90 * nu_C_90
         + A_dash_wall_180 * nu_C_180
         + A_dash_wall_270 * nu_C_270) * eta_C_wall,
        # door
        (A_dash_door_0 * nu_C_0
         + A_dash_door_90 * nu_C_90
         + A_dash_door_180 * nu_C_180
         + A_dash_door_270 * nu_C_270) * eta_C_door,
        # window
        (A_dash_window_0 * nu_C_0 * eta_C_window_0
         + A_dash_window_90 * nu_C_90 * eta_C_window_90
         + A_dash_window_180 * nu_C_180 * eta_C_window_180
         + A_dash_window_270 * nu_C_270 * eta_C_window_270),
        # base entrance
        (A_dash_base_etrc_OS_0 * nu_C_0
         + A_dash_base_etrc_OS_90 * nu_C_90
         + A_dash_base_etrc_OS_180 * nu_C_180
         + A_dash_base_etrc_OS_270 * nu_C_270) * eta_C_base_etrc,
        # base bath
        (A_dash_base_bath_OS_0 * nu_C_0
         + A_dash_base_bath_OS_90 * nu_C_90
         + A_dash_base_bath_OS_180 * nu_C_180
         + A_dash_base_bath_OS_270 * nu_C_270) * eta_C_base_bath,
        # base other
        (A_dash_base_other_OS_0 * nu_C_0
         + A_dash_base_other_OS_90 * nu_C_90
         + A_dash_base_other_OS_180 * nu_C_180
         + A_dash_base_other_OS_270 * nu_C_270) * eta_C_base_other,
        # HB roof
        L_dash_HB_roof_top * nu_C_top * eta_dash_C_HB_roof,
        # HB wall
        (L_dash_HB_wall_0 * nu_C_0
         + L_dash_HB_wall_90 * nu_C_90
         + L_dash_HB_wall_180 * nu_C_180
         + L_dash_HB_wall_270 * nu_C_270) * eta_dash_C_HB_wall,
        # HB roof_wall
        (L_dash_HB_roof_wall_top_0 * nu_C_top_0
         + L_dash_HB_roof_wall_top_90 * nu_C_top_90
         + L_dash_HB_roof_wall_top_180 * nu_C_top_180
         + L_dash_HB_roof_wall_top_270 * nu_C_top_270) * eta_dash_C_HB_roof_wall,
        # HB wall_wall
        (L_dash_HB_wall_wall_0_90 * nu_C_0_90
         + L_dash_HB_wall_wall_90_180 * nu_C_90_180
         + L_dash_HB_wall_wall_180_270 * nu_C_180_270
         + L_dash_HB_wall_wall_270_0 * nu_C_270_0) * eta_dash_C_HB_wall_wall,
        # HB wall_floor
        (L_dash_HB_wall_floor_0_IS * nu_C_0_IS
         + L_dash_HB_wall_floor_90_IS * nu_C_90_IS
         + L_dash_HB_wall_floor_180_IS * nu_C_180_IS
         + L_dash_HB_wall_floor_270_IS * nu_C_270_IS) * eta_dash_C_HB_wall_floor
    ]

    m_C = sum(m_C_list)

    return m_C


# ============================================================================
# 9.5 床面積の合計に対する外皮の部位の面積の合計の比
# ============================================================================

def get_r_env(A_dash_env, A_dash_A):
    """床面積の合計に対する外皮の部位の面積の合計の比  (12)

    Args:
      A_dash_env(float): 標準住戸における外皮の部位の面積の合計 (m2)
      A_dash_A(float): 標準住戸における床面積の合計 (m2)

    Returns:
      float: 床面積の合計に対する外皮の部位の面積の合計の比 (-)

    """

    return A_dash_env / A_dash_A


# ============================================================================
# 9.6 標準住戸における外皮の部位の面積及び土間床等の外周部の長さ等
# ============================================================================

def calc_U_A(insulation_structure, house_structure_type, floor_bath_insulation=None, bath_insulation_type=None,
             U_roof=None, U_wall=None, U_door=None, U_window=None, U_floor_bath=None, H_floor_bath=None, U_floor_other=None, H_floor_other=None,
             U_base_etrc=None, U_base_bath=None, U_base_other=None,
             Psi_prm_etrc=None, Psi_prm_bath=None, Psi_prm_other=None, Psi_HB_roof=None, Psi_HB_wall=None,
             Psi_HB_floor=None, Psi_HB_roof_wall=None, Psi_HB_wall_wall=None, Psi_HB_wall_floor=None):
    """断熱構造による住戸の種類に応じてU_A値を計算する

    Args:
      insulation_structure(structure: structure: str): 断熱構造による住戸の種類
      house_structure_type(structure_type: structure_type: str): 木造'または'鉄筋コンクリート造'または'鉄骨造'
      floor_bath_insulation(str, optional): 浴室床の断熱 (Default value = None)
      bath_insulation_type(str, optional): 浴室の断熱タイプ※ (Default value = None)
      U_roof(float, optional): 屋根又は天井の熱貫流率 (Default value = None)
      U_wall(float, optional): 壁の熱貫流率 (Default value = None)
      U_door(float, optional): ドアの熱貫流率 (Default value = None)
      U_window(float, optional): 窓の熱貫流率 (Default value = None)
      U_floor_bath(float, optional): 浴室の床の熱貫流率 (Default value = None)
      H_floor_bath(float, optional): 浴室の床の温度差係数 (Default value = None)
      U_floor_other(float, optional): その他の熱貫流率 (Default value = None)
      H_floor_other(float, optional): その他の床の温度差係数 (Default value = None)
      Psi_prm_etrc(float, optional): 玄関等の土間床等の外周部の線熱貫流率 (Default value = None)
      Psi_prm_bath(float, optional): 浴室の土間床等の外周部の線熱貫流率 (Default value = None)
      Psi_prm_other(float, optional): その他の土間床等の外周部の線熱貫流率 (Default value = None)
      Psi_HB_roof(float, optional): 屋根または天井の熱橋の線熱貫流率 (Default value = None)
      Psi_HB_wall(float, optional): 壁の熱橋の線熱貫流率 (Default value = None)
      Psi_HB_floor(float, optional): 床の熱橋の線熱貫流率 (Default value = None)
      Psi_HB_roof_wall(float, optional): 屋根または天井と壁の熱橋の線熱貫流率 (Default value = None)
      Psi_HB_wall_wall(float, optional): 壁と壁の熱橋の線熱貫流率 (Default value = None)
      Psi_HB_wall_floor(float, optional): 壁と床の熱橋の線熱貫流率 (Default value = None)
      U_base_etrc: Default value = None)
      U_base_bath: Default value = None)
      U_base_other: Default value = None)

    Returns:
      tuple: 外皮平均熱貫流率 (U_A), 外皮の部位の熱貫流率 (U)

    """

    # 断熱構造による住戸の種類
    if insulation_structure == '床断熱住戸の場合':
        U = get_U('床断熱住戸', house_structure_type, floor_bath_insulation, bath_insulation_type, U_roof, U_wall,
                  U_door, U_window, U_floor_bath, H_floor_bath, U_floor_other, H_floor_other, U_base_etrc, U_base_bath, U_base_other,
                  Psi_prm_etrc, Psi_prm_bath, Psi_prm_other, Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
                  Psi_HB_wall_wall, Psi_HB_wall_floor)
        U_A = __calc_U_A(**U)
    elif insulation_structure == '基礎断熱住戸の場合':
        U = get_U('基礎断熱住戸', house_structure_type, floor_bath_insulation, bath_insulation_type, U_roof, U_wall,
                  U_door, U_window, U_floor_bath, H_floor_bath, U_floor_other, H_floor_other, U_base_etrc, U_base_bath, U_base_other,
                  Psi_prm_etrc, Psi_prm_bath, Psi_prm_other, Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
                  Psi_HB_wall_wall, Psi_HB_wall_floor)
        U_A = __calc_U_A(**U)
    elif insulation_structure == '玄関等及び浴室を除いた部分の外皮が床と土間床等の外周部の基礎のいずれにも該当する場合':
        # 玄関等及び浴室を除いた部分の外皮が床と土間床等の外周部の基礎のいずれにも該当する場合は、
        # 表3の標準住戸における部位の面積及び土間床等の外周部の長さ等の値について、表3（い）欄に示す値及び
        # 表3（ろ）欄に示す値の両方を式(9a)及び式(9b)で表される外皮平均熱貫流率の計算に適用し、
        # 外皮平均熱貫流率の値が大きい方の場合を採用する
        U_0 = get_U('床断熱住戸', house_structure_type, floor_bath_insulation, bath_insulation_type, U_roof, U_wall,
                    U_door, U_window, U_floor_bath, H_floor_bath, U_floor_other, H_floor_other, U_base_etrc, U_base_bath, U_base_other,
                    Psi_prm_etrc, Psi_prm_bath, Psi_prm_other, Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
                    Psi_HB_wall_wall, Psi_HB_wall_floor)
        U_1 = get_U('基礎断熱住戸', house_structure_type, floor_bath_insulation, bath_insulation_type, U_roof, U_wall,
                    U_door, U_window, U_floor_bath, H_floor_bath, U_floor_other, H_floor_other, U_base_etrc, U_base_bath, U_base_other,
                    Psi_prm_etrc, Psi_prm_bath, Psi_prm_other, Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
                    Psi_HB_wall_wall, Psi_HB_wall_floor)
        U_A_0 = __calc_U_A(**U_0)
        U_A_1 = __calc_U_A(**U_1)

        if U_A_0 > U_A_1:
            U = U_0
            U_A = U_A_0
        else:
            U = U_1
            U_A = U_A_1
    else:
        raise ValueError(insulation_structure)

    return U_A, U


def get_table_3(i, house_insulation_type, floor_bath_insulation=None):
    """表3 標準住戸における部位の面積及び土間床等の外周部の長さ等

    Args:
      i(int): 表3における行番号
      house_insulation_type(str): 床断熱'または'基礎断熱'
      floor_bath_insulation(str, optional): 床断熱'または'基礎断熱'または'浴室の床及び基礎が外気等に面していない' (Default value = None)

    Returns:
      float: 標準住戸における部位の面積及び土間床等の外周部の長さ等 (m)または(m2)

    """
    table_3 = [
        (262.46, 262.46, 266.10, 275.69),
        90.0,
        50.85,
        34.06,
        22.74,
        48.49,
        22.97,
        0.0,
        1.89,
        1.62,
        0.0,
        19.11,
        2.01,
        3.05,
        3.68,
        (3.31, 3.31, 0.00, 0.00),
        (45.05, 45.05, 45.05, 0.00),
        0.00,
        0.33,
        0.25,
        0.00,
        (0.57, 0.57, 0.57, 0.00),
        (0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 0.91, 0.91),
        (0.00, 0.00, 0.91, 0.91),
        (0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 1.82, 0.00),
        (0.00, 0.00, 0.00, 5.30),
        (0.00, 0.00, 0.00, 0.58),
        (0.00, 0.00, 0.00, 3.71),
        (0.00, 0.00, 0.00, 2.40),
        (0.00, 0.00, 0.00, 0.00),
        0.00,
        1.82,
        1.37,
        0.00,
        (3.19, 3.19, 3.19, 0.00),
        (0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 1.82, 1.82),
        (0.00, 0.00, 1.82, 1.82),
        (0.00, 0.00, 0.00, 0.00),
        (0.00, 0.00, 3.64, 0.00),
        (0.00, 0.00, 0.00, 10.61),
        (0.00, 0.00, 0.00, 1.15),
        (0.00, 0.00, 0.00, 7.42),
        (0.00, 0.00, 0.00, 4.79),
        (0.00, 0.00, 0.00, 0.00),
        15.40,
        13.89,
        5.60,
        5.60,
        10.32,
        (19.04, 19.04, 19.04, 0.0),
        10.61,
        14.23,
        27.2,
        4.79,
        5.60,
        17.2,
        5.6,
        5.6,
        10.61,
        2.97,
        9.24,
        4.79,
    ]


    if house_insulation_type == '床断熱住戸':
        if floor_bath_insulation == '浴室の床及び基礎が外気等に面していない':
            return table_3[i][0]
        elif floor_bath_insulation == '床断熱':
            return table_3[i][1]
        elif floor_bath_insulation == '基礎断熱':
            return table_3[i][2]
        else:
            raise ValueError(floor_bath_insulation)
    elif house_insulation_type == '基礎断熱住戸':
        return table_3[i][3]
    elif house_insulation_type == None:
        return table_3[i]
    else:
        raise ValueError(house_insulation_type)


def get_A_dash_env(house_insulation_type, floor_bath_insulation):
    """標準住戸における外皮の部位の面積の合計 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 標準住戸における外皮の部位の面積の合計 (m2)

    """
    return get_table_3(0, house_insulation_type, floor_bath_insulation)


def get_A_dash_A():
    """床面積の合計 (m2)

    Args:

    Returns:
      float: 床面積の合計 (m2)

    """
    return get_table_3(1, None)


def get_A_dash_roof():
    """屋根又は天井の面積 (m2)

    Args:

    Returns:
      float: 屋根又は天井の面積 (m2)

    """
    return get_table_3(2, None)


def get_A_dash_wall_0():
    """主開口方向から時計回りに0°の方向に面した壁の面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに0°の方向に面した壁の面積 (m2)

    """
    return get_table_3(3, None)


def get_A_dash_wall_90():
    """主開口方向から時計回りに90°の方向に面した壁の面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに90°の方向に面した壁の面積 (m2)

    """
    return get_table_3(4, None)


def get_A_dash_wall_180():
    """主開口方向から時計回りに180°の方向に面した壁の面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに180°の方向に面した壁の面積 (m2)

    """
    return get_table_3(5, None)


def get_A_dash_wall_270():
    """主開口方向から時計回りに270°の方向に面した壁の面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに270°の方向に面した壁の面積 (m2)

    """
    return get_table_3(6, None)


def get_A_dash_door_0():
    """主開口方向から時計回りに0°の方向に面したドアの面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに0°の方向に面したドアの面積 (m2)

    """
    return get_table_3(7, None)


def get_A_dash_door_90():
    """主開口方向から時計回りに90°の方向に面したドアの面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに90°の方向に面したドアの面積 (m2)

    """
    return get_table_3(8, None)


def get_A_dash_door_180():
    """主開口方向から時計回りに180°の方向に面したドアの面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに180°の方向に面したドアの面積 (m2)

    """
    return get_table_3(9, None)


def get_A_dash_door_270():
    """主開口方向から時計回りに270°の方向に面したドアの面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに270°の方向に面したドアの面積 (m2)

    """
    return get_table_3(10, None)


def get_A_dash_window_0():
    """主開口方向から時計回りに0°の方向に面した窓の面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに0°の方向に面した窓の面積 (m2)

    """
    return get_table_3(11, None)


def get_A_dash_window_90():
    """主開口方向から時計回りに90°の方向に面した窓の面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに90°の方向に面した窓の面積 (m2)

    """
    return get_table_3(12, None)


def get_A_dash_window_180():
    """主開口方向から時計回りに180°の方向に面した窓の面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに180°の方向に面した窓の面積 (m2)

    """
    return get_table_3(13, None)


def get_A_dash_window_270():
    """主開口方向から時計回りに270°の方向に面した窓の面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに270°の方向に面した窓の面積 (m2)

    """
    return get_table_3(14, None)


def get_A_dash_floor_bath(house_insulation_type, floor_bath_insulation):
    """浴室の床の面積 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 浴室の床の面積 (m2)

    """
    return get_table_3(15, house_insulation_type, floor_bath_insulation)


def get_A_dash_floor_other(house_insulation_type, floor_bath_insulation):
    """浴室の床の面積 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 浴室の床の面積 (m2)

    """
    return get_table_3(16, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_etrc_OS_0():
    """主開口方向から時計回りに0°の方向の外気に面した玄関等の基礎の面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに0°の方向の外気に面した玄関等の基礎の面積 (m2)

    """
    return get_table_3(17, None)


def get_A_dash_base_etrc_OS_90():
    """主開口方向から時計回りに90°の方向の外気に面した玄関等の基礎の面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに90°の方向の外気に面した玄関等の基礎の面積 (m2)

    """
    return get_table_3(18, None)


def get_A_dash_base_etrc_OS_180():
    """主開口方向から時計回りに180°の方向の外気に面した玄関等の基礎の面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに180°の方向の外気に面した玄関等の基礎の面積 (m2)

    """
    return get_table_3(19, None)


def get_A_dash_base_etrc_OS_270():
    """主開口方向から時計回りに270°の方向の外気に面した玄関等の基礎の面積 (m2)

    Args:

    Returns:
      float: 主開口方向から時計回りに270°の方向の外気に面した玄関等の基礎の面積 (m2)

    """
    return get_table_3(20, None)


def get_A_dash_base_etrc_IS(house_insulation_type, floor_bath_insulation):
    """床下に面した玄関等の基礎の面積 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 床下に面した玄関等の基礎の面積 (m2)

    """
    return get_table_3(21, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_bath_OS_0(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに0°の方向の外気に面した浴室の基礎の面積 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに0°の方向の外気に面した浴室の基礎の面積 (m2)

    """
    return get_table_3(22, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_bath_OS_90(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに90°の方向の外気に面した浴室の基礎の面積 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに90°の方向の外気に面した浴室の基礎の面積 (m2)

    """
    return get_table_3(23, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_bath_OS_180(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに180°の方向の外気に面した浴室の基礎の面積 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに180°の方向の外気に面した浴室の基礎の面積 (m2)

    """
    return get_table_3(24, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_bath_OS_270(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに270°の方向の外気に面した浴室の基礎の面積 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに270°の方向の外気に面した浴室の基礎の面積 (m2)

    """
    return get_table_3(25, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_bath_IS(house_insulation_type, floor_bath_insulation):
    """床下に面した浴室の基礎の面積 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 床下に面した浴室の基礎の面積 (m2)

    """
    return get_table_3(26, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_other_OS_0(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに0°の方向の外気に面したその他の基礎の面積 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに0°の方向の外気に面したその他の基礎の面積 (m2)

    """
    return get_table_3(27, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_other_OS_90(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに90°の方向の外気に面したその他の基礎の面積 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに90°の方向の外気に面したその他の基礎の面積 (m2)

    """
    return get_table_3(28, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_other_OS_180(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに180°の方向の外気に面したその他の基礎の面積 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに180°の方向の外気に面したその他の基礎の面積 (m2)

    """
    return get_table_3(29, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_other_OS_270(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに270°の方向の外気に面したその他の基礎の面積 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに270°の方向の外気に面したその他の基礎の面積 (m2)

    """
    return get_table_3(30, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_other_IS(house_insulation_type, floor_bath_insulation):
    """床下に面したその他の基礎の面積 (m2)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 床下に面したその他の基礎の面積 (m2)

    """
    return get_table_3(31, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_etrc_OS_0():
    """主開口方向から時計回りに0°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに0°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)

    """
    return get_table_3(32, None)


def get_L_dash_prm_etrc_OS_90():
    """主開口方向から時計回りに90°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに90°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)

    """
    return get_table_3(33, None)


def get_L_dash_prm_etrc_OS_180():
    """主開口方向から時計回りに180°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに180°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)

    """
    return get_table_3(34, None)


def get_L_dash_prm_etrc_OS_270():
    """主開口方向から時計回りに270°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに270°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)

    """
    return get_table_3(35, None)


def get_L_dash_prm_etrc_IS(house_insulation_type, floor_bath_insulation):
    """床下に面した玄関等の土間床等の外周部の長さ (m)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 床下に面した玄関等の土間床等の外周部の長さ (m)

    """
    return get_table_3(36, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_bath_OS_0(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに0°の方向の外気に面した浴室の土間床等の外周部の長さ (m)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに0°の方向の外気に面した浴室の土間床等の外周部の長さ (m)

    """
    return get_table_3(37, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_bath_OS_90(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに90°の方向の外気に面した浴室の土間床等の外周部の長さ (m)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに90°の方向の外気に面した浴室の土間床等の外周部の長さ (m)

    """
    return get_table_3(38, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_bath_OS_180(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに180°の方向の外気に面した浴室の土間床等の外周部の長さ (m)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに180°の方向の外気に面した浴室の土間床等の外周部の長さ (m)

    """
    return get_table_3(39, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_bath_OS_270(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに270°の方向の外気に面した浴室の土間床等の外周部の長さ (m)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに270°の方向の外気に面した浴室の土間床等の外周部の長さ (m)

    """
    return get_table_3(40, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_bath_IS(house_insulation_type, floor_bath_insulation):
    """床下に面した浴室の土間床等の外周部の長さ (m)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 床下に面した浴室の土間床等の外周部の長さ (m)

    """
    return get_table_3(41, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_other_OS_0(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに0°の方向の外気に面したその他の土間床等の外周部の長さ (m)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに0°の方向の外気に面したその他の土間床等の外周部の長さ (m)

    """
    return get_table_3(42, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_other_OS_90(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに90°の方向の外気に面したその他の土間床等の外周部の長さ (m)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに90°の方向の外気に面したその他の土間床等の外周部の長さ (m)

    """
    return get_table_3(43, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_other_OS_180(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに180°の方向の外気に面したその他の土間床等の外周部の長さ (m)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに180°の方向の外気に面したその他の土間床等の外周部の長さ (m)

    """
    return get_table_3(44, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_other_OS_270(house_insulation_type, floor_bath_insulation):
    """主開口方向から時計回りに270°の方向の外気に面したその他の土間床等の外周部の長さ (m)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 主開口方向から時計回りに270°の方向の外気に面したその他の土間床等の外周部の長さ (m)

    """
    return get_table_3(45, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_other_IS(house_insulation_type, floor_bath_insulation):
    """床下に面したその他の土間床等の外周部の長さ (m)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 床下に面したその他の土間床等の外周部の長さ (m)

    """
    return get_table_3(46, house_insulation_type, floor_bath_insulation)


def get_L_dash_HB_roof_top():
    """上面に面した屋根又は天井の熱橋の長さ (m)

    Args:

    Returns:
      float: 上面に面した屋根又は天井の熱橋の長さ (m)

    """
    return get_table_3(47, None)


def get_L_dash_HB_wall_0():
    """主開口方向から時計回りに0°の方向の外気に面した壁の熱橋の長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに0°の方向の外気に面した壁の熱橋の長さ (m)

    """
    return get_table_3(48, None)


def get_L_dash_HB_wall_90():
    """主開口方向から時計回りに90°の方向の外気に面した壁の熱橋の長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに90°の方向の外気に面した壁の熱橋の長さ (m)

    """
    return get_table_3(49, None)


def get_L_dash_HB_wall_180():
    """主開口方向から時計回りに180°の方向の外気に面した壁の熱橋の長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに180°の方向の外気に面した壁の熱橋の長さ (m)

    """
    return get_table_3(50, None)


def get_L_dash_HB_wall_270():
    """主開口方向から時計回りに270°の方向の外気に面した壁の熱橋の長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに270°の方向の外気に面した壁の熱橋の長さ (m)

    """
    return get_table_3(51, None)


def get_L_dash_HB_floor_IS(house_insulation_type, floor_bath_insulation):
    """床下に面した床の熱橋の長さ (m)

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'

    Returns:
      float: 床下に面した床の熱橋の長さ (m)

    """
    return get_table_3(52, house_insulation_type, floor_bath_insulation)


def get_L_dash_HB_roof_wall_top():
    """上面に面した屋根又は天井と壁の熱橋長さ (m)

    Args:

    Returns:
      float: 面に面した屋根又は天井と壁の熱橋長さ (m)

    """
    return get_table_3(53, None)


def get_L_dash_HB_roof_wall_top_0():
    """主開口方向から時計回りに0°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに0°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)

    """
    return get_table_3(53, None)


def get_L_dash_HB_roof_wall_top_90():
    """主開口方向から時計回りに90°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに90°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)

    """
    return get_table_3(54, None)


def get_L_dash_HB_roof_wall_top_180():
    """主開口方向から時計回りに180°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに180°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)

    """
    return get_table_3(55, None)


def get_L_dash_HB_roof_wall_top_270():
    """主開口方向から時計回りに270°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに270°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)

    """
    return get_table_3(56, None)


def get_L_dash_HB_wall_wall_0_90():
    """主開口方向から時計回りに0°の方向の外気に面した壁と壁の熱橋長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに0°の方向の外気に面した壁と壁の熱橋長さ (m)

    """
    return get_table_3(57, None)


def get_L_dash_HB_wall_wall_90_180():
    """主開口方向から時計回りに90°の方向の外気に面した壁と壁の熱橋長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに90°の方向の外気に面した屋壁と壁の熱橋長さ (m)

    """
    return get_table_3(58, None)


def get_L_dash_HB_wall_wall_180_270():
    """主開口方向から時計回りに180°の方向の外気に面した壁と壁の熱橋長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに180°の方向の外気に面した壁と壁の熱橋長さ (m)

    """
    return get_table_3(59, None)


def get_L_dash_HB_wall_wall_270_0():
    """主開口方向から時計回りに270°の方向の外気に面した壁と壁の熱橋長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに270°の方向の外気に面した壁と壁の熱橋長さ (m)

    """
    return get_table_3(60, None)


def get_L_dash_HB_wall_floor_0_IS():
    """主開口方向から時計回りに0°の方向の外気に面した壁と床の熱橋長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに0°の方向の外気に面した壁と床の熱橋長さ (m)

    """
    return get_table_3(61, None)


def get_L_dash_HB_wall_floor_90_IS():
    """主開口方向から時計回りに90°の方向の外気に面した壁と床の熱橋長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに90°の方向の外気に面した壁と床の熱橋長さ (m)

    """
    return get_table_3(62, None)


def get_L_dash_HB_wall_floor_180_IS():
    """主開口方向から時計回りに180°の方向の外気に面した壁と床の熱橋長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに180°の方向の外気に面した壁と床の熱橋長さ (m)

    """
    return get_table_3(63, None)


def get_L_dash_HB_wall_floor_270_IS():
    """主開口方向から時計回りに270°の方向の外気に面した壁と床の熱橋長さ (m)

    Args:

    Returns:
      float: 主開口方向から時計回りに270°の方向の外気に面した壁と床の熱橋長さ (m)

    """
    return get_table_3(64, None)


# ============================================================================
# 9.7 外皮の部位及び熱橋等の温度差係数
# ============================================================================

def get_H_OS():
    """屋根又は天井の温度差係数 (-)

    Args:

    Returns:
      float: 屋根又は天井の温度差係数 (-)

    """
    adjacent_type = '外気'

    return get_H(adjacent_type)


def get_H_IS():
    """壁の温度差係数 (-)

    Args:

    Returns:
      float: 壁の温度差係数 (-)

    """
    adjacent_type = '外気に通じていない空間・外気に通じる床裏'
    return get_H(adjacent_type)


def get_H_floor_other(H_floor_other):
    """9.7.1 その他の床の温度差係数

    Args:
      H_floor_other(float): その他の床の温度差係数

    Returns:
      float: その他床の温度差係数
    """
    return H_floor_other

def get_H_floor_bath(H_floor_bath, H_floor_other, house_insulation_type, floor_bath_insulation):
    """9.7.2 浴室の床の温度差係数

    Args:
      H_floor_bath(float): 浴室の床の温度差係数
      H_floor_other(float): その他の床の温度差係数
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 浴室床の断熱
    Returns:
      float: 浴室の床の温度差係数

    """

    if house_insulation_type == '床断熱住戸':
        if floor_bath_insulation == '浴室部分の外皮を床とする':
              return H_floor_bath
        elif floor_bath_insulation == '浴室の床及び基礎が外気等に面していない':
            # 床断熱住戸において外皮の部位として浴室の床が存在しない場合はその他の床の温度差係数に等しい
            return H_floor_other
        else:
            raise ValueError(floor_bath_insulation)
    else:
        return None

# ============================================================================
# 9.8 外皮の部位及び熱橋等の方位係数
# ============================================================================

# 標準住戸における外皮の部位及び熱橋等の方位係数は、地域の区分・方位・期間に応じて付録Cに定める方法により求めた値とする。


# ============================================================================
# 9.9 外皮の部位の熱貫流率及び熱橋等の線熱貫流率
# ============================================================================

def get_U(house_insulation_type, house_structure_type, floor_bath_insulation=None, bath_insulation_type=None, U_roof=None, U_wall=None,
          U_door=None, U_window=None, U_floor_bath=None, H_floor_bath=None, U_floor_other=None, H_floor_other=None, U_base_etrc=None, U_base_bath=None, U_base_other=None,
          Psi_prm_etrc=None, Psi_prm_bath=None, Psi_prm_other=None,
          Psi_HB_roof=None, Psi_HB_wall=None, Psi_HB_floor=None, Psi_HB_roof_wall=None,
          Psi_HB_wall_wall=None, Psi_HB_wall_floor=None):
    """屋根又は天井・壁・ドア・窓・熱橋等の熱貫流率

    Args:
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      house_structure_type(structure_type: structure_type: str): 木造'または'鉄筋コンクリート造'または'鉄骨造'
      floor_bath_insulation(str, optional): 浴室床の断熱 (Default value = None)
      bath_insulation_type(str, optional): 浴室の断熱タイプ※ (Default value = None)
      U_roof(float, optional): 屋根又は天井の熱貫流率 (Default value = None)
      U_wall(float, optional): 壁の熱貫流率 (Default value = None)
      U_door(float, optional): ドアの熱貫流率 (Default value = None)
      U_window(float, optional): 窓の熱貫流率 (Default value = None)
      U_floor_bath(float, optional): 浴室の床の熱貫流率 (Default value = None)
      H_floor_bath(float, optional): 浴室の床の温度差係数 (Default value = None)
      U_floor_other(float, optional): その他の熱貫流率 (Default value = None)
      H_floor_other(float, optional): その他の床の温度差係数 (Default value = None)
      Psi_prm_etrc(float, optional): 玄関等の土間床等の外周部の線熱貫流率 (Default value = None)
      Psi_prm_bath(float, optional): 浴室の土間床等の外周部の線熱貫流率 (Default value = None)
      Psi_prm_other(float, optional): その他の土間床等の外周部の線熱貫流率 (Default value = None)
      Psi_HB_roof(float, optional): 屋根または天井の熱橋の線熱貫流率 (Default value = None)
      Psi_HB_wall(float, optional): 壁の熱橋の線熱貫流率 (Default value = None)
      Psi_HB_floor(float, optional): 床の熱橋の線熱貫流率 (Default value = None)
      Psi_HB_roof_wall(float, optional): 屋根または天井と壁の熱橋の線熱貫流率 (Default value = None)
      Psi_HB_wall_wall(float, optional): 壁と壁の熱橋の線熱貫流率 (Default value = None)
      Psi_HB_wall_floor(float, optional): 壁と床の熱橋の線熱貫流率 (Default value = None)
      U_base_etrc: Default value = None)
      U_base_bath: Default value = None)
      U_base_other: Default value = None)

    Returns:
      dict: 屋根又は天井・壁・ドア・窓・熱橋等の熱貫流率

    """

    # 屋根又は天井・壁・ドア・窓の熱貫流率
    if house_insulation_type == '床断熱住戸':

        # 浴室の断熱構造
        if floor_bath_insulation == '床断熱':
            H_floor_bath = get_H_floor_bath(
              H_floor_bath=H_floor_bath,
              H_floor_other=H_floor_other,
              house_insulation_type=house_insulation_type,
              floor_bath_insulation='浴室部分の外皮を床とする'
            )
            U_floor_bath = get_U_floor_bath(
                U_floor_bath=U_floor_bath,
                U_floor_other=U_floor_other,
                house_insulation_type=house_insulation_type,
                floor_bath_insulation='浴室部分の外皮を床とする'
            )
            Psi_prm_etrc = get_psi_prm_etrc(Psi_prm_etrc)
            Psi_prm_bath = 0
            U_base_bath = 0
        elif floor_bath_insulation == '基礎断熱':
            U_floor_bath = 0
            H_floor_bath = 0
            Psi_prm_etrc = get_psi_prm_etrc(Psi_prm_etrc)
            Psi_prm_bath = get_psi_prm_bath(Psi_prm_bath, Psi_prm_other, house_insulation_type)
            U_base_bath = get_U_base_bath(U_base_bath, U_base_other, house_insulation_type, floor_bath_insulation)
        elif floor_bath_insulation == '浴室の床及び基礎が外気等に面していない':
            H_floor_bath = get_H_floor_bath(
              H_floor_bath=H_floor_bath,
              H_floor_other=H_floor_other,
              house_insulation_type=house_insulation_type,
              floor_bath_insulation=floor_bath_insulation
            )
            U_floor_bath = get_U_floor_bath(
                U_floor_bath=U_floor_bath,
                U_floor_other=U_floor_other,
                house_insulation_type=house_insulation_type,
                floor_bath_insulation=floor_bath_insulation
            )
            Psi_prm_etrc = get_psi_prm_etrc(Psi_prm_etrc)
            Psi_prm_bath = 0
            U_base_bath = 0
        else:
            raise ValueError(floor_bath_insulation)

        U_roof = get_U_roof(U_roof)
        U_wall = get_U_wall(U_wall)
        U_door = get_U_door(U_door)
        U_window = get_U_window(U_window)
        H_floor_other = get_H_floor_other(H_floor_other)
        U_floor_other = get_U_floor_other(U_floor_other)
        U_base_etrc = get_U_base_etrc(U_base_etrc)
        U_base_other = 0
        Psi_prm_other = 0

    elif house_insulation_type == '基礎断熱住戸':
        U_roof = get_U_roof(U_roof)
        U_wall = get_U_wall(U_wall)
        U_door = get_U_door(U_door)
        U_window = get_U_window(U_window)
        U_floor_bath = 0
        H_floor_bath = 0
        U_floor_other = 0
        H_floor_other = 0
        U_base_etrc = get_U_base_etrc(U_base_etrc)
        U_base_bath = get_U_base_bath(U_base_bath, U_base_other, house_insulation_type, floor_bath_insulation)
        U_base_bath = get_U_base_bath(U_base_bath, U_base_other, house_insulation_type, floor_bath_insulation)
        U_base_other = get_U_base_other(U_base_other)
        Psi_prm_etrc = get_psi_prm_etrc(Psi_prm_etrc)
        Psi_prm_bath = get_psi_prm_bath(
            psi_prm_bath=Psi_prm_bath,
            phi_prm_other=Psi_prm_other,
            house_insulation_type=house_insulation_type
        )
        Psi_prm_other = get_psi_prm_other(Psi_prm_other, house_insulation_type)
    else:
        raise ValueError(house_insulation_type)

    # 熱橋
    Psi_HB_roof = get_psi_HB_roof(Psi_HB_roof, house_structure_type)
    Psi_HB_wall = get_psi_HB_wall(Psi_HB_wall, house_structure_type)
    Psi_HB_floor = get_psi_HB_floor(Psi_HB_floor, house_structure_type)
    Psi_HB_roof_wall = get_psi_HB_roof_wall(Psi_HB_roof_wall, house_structure_type)
    Psi_HB_wall_wall = get_psi_HB_wall_wall(Psi_HB_wall_wall, house_structure_type)
    Psi_HB_wall_floor = get_psi_HB_wall_floor(Psi_HB_wall_floor, house_structure_type)

    return {
        'house_insulation_type': house_insulation_type,
        'floor_bath_insulation': floor_bath_insulation,
        'U_roof': U_roof,
        'U_door': U_door,
        'U_wall': U_wall,
        'U_window': U_window,
        'U_floor_bath': U_floor_bath,
        'H_floor_bath': H_floor_bath,
        'U_floor_other': U_floor_other,
        'H_floor_other': H_floor_other,
        'U_base_etrc': U_base_etrc,
        'U_base_bath': U_base_bath,
        'U_base_other': U_base_other,
        'Psi_prm_etrc': Psi_prm_etrc,
        'Psi_prm_bath': Psi_prm_bath,
        'Psi_prm_other': Psi_prm_other,
        'Psi_HB_roof': Psi_HB_roof,
        'Psi_HB_wall': Psi_HB_wall,
        'Psi_HB_floor': Psi_HB_floor,
        'Psi_HB_roof_wall': Psi_HB_roof_wall,
        'Psi_HB_wall_wall': Psi_HB_wall_wall,
        'Psi_HB_wall_floor': Psi_HB_wall_floor,
    }


def get_U_roof(U_roof):
    """9.9.1 屋根又は天井の熱貫流率

    Args:
      U_roof(float): 屋根又は天井の熱貫流率

    Returns:
      float: 9屋根又は天井の熱貫流率

    """
    return U_roof


def get_U_wall(U_wall):
    """9.9.2 壁の熱貫流率

    Args:
      U_wall(float): 壁の熱貫流率

    Returns:
      float: 壁の熱貫流率

    """
    return U_wall


def get_U_door(U_door):
    """9.9.3 ドアの熱貫流率

    Args:
      U_door(float): ドアの熱貫流率

    Returns:
      float: ドアの熱貫流率

    """
    return U_door


def get_U_window(U_window):
    """9.9.4 窓の熱貫流率

    Args:
      U_window(float): 窓の熱貫流率

    Returns:
      float: 窓の熱貫流率

    """
    return U_window


def get_U_floor_other(U_floor_other):
    """9.9.5 その他の床の熱貫流率

    Args:
      U_floor_other(float): その他の床の熱貫流率

    Returns:
      float: その他の床の熱貫流率

    """
    return U_floor_other


def get_U_floor_bath(U_floor_bath, U_floor_other, house_insulation_type, floor_bath_insulation):
    """9.9.6 浴室の床の熱貫流率

    Args:
      U_floor_bath(float): 浴室の床の熱貫流率
      U_floor_other(float): その他の熱貫流率
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 浴室床の断熱

    Returns:
      float: 浴室の床の熱貫流率

    """
    if house_insulation_type == '床断熱住戸':
        if floor_bath_insulation == '浴室部分の外皮を床とする':
            return U_floor_bath
        elif floor_bath_insulation == '浴室の床及び基礎が外気等に面していない':
            # 床断熱住戸において外皮の部位として浴室の床が存在しない場合はその他の床の熱貫流率に等しい
            return U_floor_other
        else:
            raise ValueError(floor_bath_insulation)
    else:
        return None


def get_U_base_etrc(U_base_etrc):
    """9.9.7 玄関等の基礎の熱貫流率

    Args:
      U_base_etrc(float): 玄関等の基礎の熱貫流率

    Returns:
      float: 玄関等の基礎の熱貫流率

    """
    return U_base_etrc


def get_U_base_bath(U_base_bath, U_base_other, house_insulation_type, floor_bath_insulation):
    """9.9.8 浴室の基礎の熱貫流率

    Args:
      U_base_bath(float): 浴室の基礎の熱貫流率
      U_base_other(float): その他の基礎の熱貫流率
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 浴室の基礎の断熱

    Returns:
      float: 浴室の基礎の熱貫流率

    """
    if house_insulation_type == '床断熱住戸':
        if floor_bath_insulation == '基礎断熱':
            return U_base_bath
        else:
            return None
    if house_insulation_type == '基礎断熱住戸':
        return U_base_other
    else:
        return None


def get_U_base_other(U_base_other):
    """9.9.9 その他の基礎の熱貫流率

    Args:
      U_base_other(float): その他の基礎の熱貫流率

    Returns:
      float: その他の基礎の熱貫流率

    """
    return U_base_other


def get_psi_prm_etrc(psi_prm_etrc):
    """9.9.10 玄関等の土間床等の外周部の線熱貫流率

    Args:
      psi_prm_etrc(list, tuple or float): 玄関等の土間床等の外周部の線熱貫流率

    Returns:
      float: 玄関等の土間床等の外周部の線熱貫流率

    """
    return psi_prm_etrc


def get_psi_prm_bath(psi_prm_bath, phi_prm_other, house_insulation_type):
    """9.9.11 浴室の土間床等の外周部の線熱貫流率

    Args:
      psi_prm_bath(list, tuple or float): 浴室の土間床等の外周部の線熱貫流率
      phi_prm_other(float): その他の土間床等の外周部の線熱貫流率
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'

    Returns:
      float: 浴室の土間床等の外周部の線熱貫流率

    """
    if house_insulation_type == '床断熱住戸':
        return psi_prm_bath
    elif house_insulation_type == '基礎断熱住戸':
        return phi_prm_other
    else:
        return None


def get_psi_prm_other(psi_prm_other, house_insulation_type):
    """9.9.12 その他の土間床等の外周部の線熱貫流率

    Args:
      psi_prm_other(list, tuple or float): その他の土間床等の外周部の線熱貫流率
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'

    Returns:
      float: その他の土間床等の外周部の線熱貫流率

    """
    if house_insulation_type == '基礎断熱住戸':
        return psi_prm_other
    else:
        return None


def get_psi_HB_roof(psi_HB_roof, house_structure_type):
    """9.9.13 屋根又は天井の熱橋の線熱貫流率

    Args:
      psi_HB_roof(list, tuple or float): 屋根又は天井の熱橋の線熱貫流率
      house_structure_type(structure_type: structure_type: str): 木造'または'鉄筋コンクリート造'、'鉄骨造'

    Returns:
      float: 屋根又は天井の熱橋の線熱貫流率

    """
    if house_structure_type == '鉄筋コンクリート造' or house_structure_type == '鉄骨造':
        return psi_HB_roof
    else:
        return 0


def get_psi_HB_wall(psi_HB_wall, house_structure_type):
    """9.9.14 壁の熱橋の線熱貫流率

    Args:
      psi_HB_wall(list, tuple or float): 壁の熱橋の線熱貫流率
      house_structure_type(structure_type: structure_type: str): 木造'または'鉄筋コンクリート造'、'鉄骨造'

    Returns:
      float: 壁の熱橋の線熱貫流率

    """
    if house_structure_type == '鉄筋コンクリート造' or house_structure_type == '鉄骨造':
        return psi_HB_wall
    else:
        return 0


def get_psi_HB_floor(psi_HB_floor, house_structure_type):
    """9.9.15 床の熱橋の線熱貫流率

    Args:
      psi_HB_floor(list, tuple or float): 床の熱橋の線熱貫流率
      house_structure_type: 木造'または'鉄筋コンクリート造'、'鉄骨造

    Returns:
      float: 床の熱橋の線熱貫流率

    """
    if house_structure_type == '鉄筋コンクリート造' or house_structure_type == '鉄骨造':
        return psi_HB_floor
    else:
        return 0


def get_psi_HB_roof_wall(psi_HB_roof_wall, house_structure_type):
    """9.9.16 屋根又は天井と壁の熱橋の線熱貫流率

    Args:
      psi_HB_roof_wall(list, tuple or float): 屋根又は天井と壁の熱橋の線熱貫流率
      house_structure_type(structure_type: structure_type: str): 木造'または'鉄筋コンクリート造'、'鉄骨造'

    Returns:
      float: 屋根又は天井と壁の熱橋の線熱貫流率

    """
    if house_structure_type == '鉄筋コンクリート造' or house_structure_type == '鉄骨造':
        return psi_HB_roof_wall
    else:
        return 0


def get_psi_HB_wall_wall(psi_HB_wall_wall, house_structure_type):
    """9.9.17 壁と壁の熱橋の線熱貫流率

    Args:
      psi_HB_wall_wall(list, tuple or float): 壁と壁の熱橋の線熱貫流率
      house_structure_type(structure_type: structure_type: str): 木造'または'鉄筋コンクリート造'、'鉄骨造'

    Returns:
      float: 壁と壁(出隅)の熱橋の線熱貫流率

    """
    if house_structure_type == '鉄筋コンクリート造' or house_structure_type == '鉄骨造':
        return psi_HB_wall_wall
    else:
        return 0


def get_psi_HB_wall_floor(psi_HB_wall_floor, house_structure_type):
    """9.9.18 壁と床の熱橋の線熱貫流率

    Args:
      psi_HB_wall_floor(list, tuple or float): 壁と床の熱橋の線熱貫流率
      house_structure_type(structure_type: structure_type: str): 木造'または'鉄筋コンクリート造'、'鉄骨造'

    Returns:
      float: 壁と床の熱橋の線熱貫流率

    """
    if house_structure_type == '鉄筋コンクリート造' or house_structure_type == '鉄骨造':
        return psi_HB_wall_floor
    else:
        return 0


# ============================================================================
# 9.10 外皮の部位の日射熱取得率
# ============================================================================

def calc_eta_H_roof(U_roof):
    """9.10.1 屋根又は天井の日射熱取得率(暖房期)

    Args:
      U_roof(float): 屋根又は天井の熱貫流率

    Returns:
      float: 屋根又は天井の日射熱取得率(暖房期)

    """

    return eater.common.get_eta_H_i(1.0, U_roof)


def calc_eta_C_roof(U_roof):
    """9.10.1 屋根又は天井の日射熱取得率(冷房期)

    Args:
      U_roof(float): 屋根又は天井の熱貫流率

    Returns:
      float: 屋根又は天井の日射熱取得率(冷房期)

    """

    return eater.common.get_eta_C_i(1.0, U_roof)



def calc_eta_H_wall(U_wall):
    """9.10.2 壁の日射熱取得率(暖房期)

    Args:
      U_wall(float): 壁の熱貫流率

    Returns:
      float: 壁の日射熱取得率(暖房期)

    """

    return eater.common.get_eta_H_i(1.0, U_wall)


def calc_eta_C_wall(U_wall):
    """9.10.2 壁の日射熱取得率(冷房期)

    Args:
      U_wall: type U_wall:

    Returns:
      float: 壁の日射熱取得率(冷房期)

    """

    return eater.common.get_eta_C_i(1.0, U_wall)


def calc_eta_H_door(U_door):
    """9.10.3 ドアの日射熱取得率(暖房期)

    Args:
      U_door(float): ドアの熱貫流率

    Returns:
      float: ドアの日射熱取得率(暖房期)

    """

    return eater.door.get_eta_H_i(1.0, U_door)


def calc_eta_C_door(U_door):
    """9.10.3 ドアの日射熱取得率(冷房期)

    Args:
      U_door(float): ドアの熱貫流率

    Returns:
      float: ドアの日射熱取得率(冷房期)

    """

    return eater.door.get_eta_C_i(1.0, U_door)


def calc_eta_H_window(region, etr_d, f_H=None):
    """9.10.4 窓の日射熱取得率(暖房期)

    Args:
      region(int): 省エネルギー地域区分
      etr_d(float): 暖房期の垂直面日射熱取得率 (-)
      f_H(float, optional): 暖房期の取得日射熱補正係数 (-) (Default value = None)

    Returns:
      tuple: 窓の日射熱取得率(暖房期)

    """
    if f_H is None:
        f_H_0 = calc_f_H_i(region, '南西')
        f_H_90 = calc_f_H_i(region, '北西')
        f_H_180 = calc_f_H_i(region, '北東')
        f_H_270 = calc_f_H_i(region, '南東')
    else:
        f_H_0 = f_H
        f_H_90 = f_H
        f_H_180 = f_H
        f_H_270 = f_H

    eta_H_window_0 = eater.window.get_eta_H_i(f_H_0, etr_d)
    eta_H_window_90 = eater.window.get_eta_H_i(f_H_90, etr_d)
    eta_H_window_180 = eater.window.get_eta_H_i(f_H_180, etr_d)
    eta_H_window_270 = eater.window.get_eta_H_i(f_H_270, etr_d)

    return eta_H_window_0, eta_H_window_90, eta_H_window_180, eta_H_window_270


def calc_f_H_i(region, direction):
    """暖房期における開口部の取得日射熱補正係数を表4 から取得する関数

    Args:
        region (int): 省エネルギー地域区分
        direction (str): 開口部の面する方位

    Returns:
        float: 暖房期における開口部の取得日射熱補正係数 (-)
    """
    # 開口部の面する方位から表4 の列のインデックスを取得
    col_index = {
        '北': 0,
        '北東': 1,
        '東': 2,
        '南東': 3,
        '南': 4,
        '南西': 5,
        '西': 6,
        '北西': 7,
    }[direction]

    # 省エネルギー地域区分から表4 の行のインデックスを取得
    # (l=3 か l=3.5 かによって取得する行のインデックスが異なる)
    row_index_l1 = 2 * (region - 1)
    row_index_l2 = 2 * (region - 1) + 1

    # 表4 からl=3とl=3.5における暖房期の取得日射熱補正係数を取得
    f_H_i_l1 = get_table_4()[row_index_l1][col_index]
    f_H_i_l2 = get_table_4()[row_index_l2][col_index]

    # 暖房期の取得日射熱補正係数f_Hは、l=1⁄0.3として、地域の区分・方位に応じて、
    # 表 4 に定めるl=3の値とl=3.5の値を線形補間した値とする。
    l1 = 3
    l2 = 3.5
    l = 1 / 0.3
    f_H_i = f_H_i_l1 + (f_H_i_l2 - f_H_i_l1) * (l - l1) / (l2 - l1)

    return f_H_i


def get_table_4():
    """表4. 暖房期の取得日射熱補正係数 を取得する関数

    Returns:
        list: 表4. 暖房期の取得日射熱補正係数
    """
    return [
        (0.604, 0.586, 0.623, 0.646, 0.636, 0.640, 0.620, 0.589),
        (0.628, 0.610, 0.649, 0.674, 0.665, 0.667, 0.645, 0.613),
        (0.602, 0.589, 0.625, 0.637, 0.608, 0.629, 0.626, 0.588),
        (0.626, 0.613, 0.651, 0.665, 0.639, 0.657, 0.652, 0.612),
        (0.601, 0.585, 0.614, 0.630, 0.618, 0.631, 0.619, 0.585),
        (0.626, 0.610, 0.640, 0.658, 0.647, 0.659, 0.645, 0.610),
        (0.603, 0.581, 0.620, 0.623, 0.596, 0.623, 0.618, 0.579),
        (0.628, 0.606, 0.646, 0.652, 0.626, 0.652, 0.645, 0.603),
        (0.612, 0.576, 0.630, 0.652, 0.635, 0.648, 0.626, 0.579),
        (0.636, 0.600, 0.655, 0.680, 0.664, 0.676, 0.651, 0.603),
        (0.611, 0.573, 0.625, 0.656, 0.622, 0.635, 0.624, 0.579),
        (0.636, 0.597, 0.651, 0.684, 0.652, 0.663, 0.649, 0.603),
        (0.620, 0.572, 0.623, 0.647, 0.629, 0.651, 0.627, 0.574),
        (0.644, 0.595, 0.648, 0.675, 0.660, 0.679, 0.651, 0.597),
    ]


def calc_eta_C_window(region, etr_d, f_C=None):
    """9.10.4 窓の日射熱取得率(冷房期)

    Args:
      region(int): 省エネルギー地域区分
      etr_d(float): 垂直面日射熱取得率 (-)
      f_C(float, optional): 冷房期の取得日射熱補正係数 (-) (Default value = None)

    Returns:
      tuple: 窓の日射熱取得率(冷房期)

    """
    if f_C is None:
        f_C_0 = calc_f_C_i(region, '南西')
        f_C_90 = calc_f_C_i(region, '北西')
        f_C_180 = calc_f_C_i(region, '北東')
        f_C_270 = calc_f_C_i(region, '南東')
    else:
        f_C_0 = f_C
        f_C_90 = f_C
        f_C_180 = f_C
        f_C_270 = f_C

    eta_C_window_0 = eater.window.get_eta_C_i(f_C_0, etr_d)
    eta_C_window_90 = eater.window.get_eta_C_i(f_C_90, etr_d)
    eta_C_window_180 = eater.window.get_eta_C_i(f_C_180, etr_d)
    eta_C_window_270 = eater.window.get_eta_C_i(f_C_270, etr_d)

    return eta_C_window_0, eta_C_window_90, eta_C_window_180, eta_C_window_270


def calc_f_C_i(region, direction):
    """冷房期における開口部の取得日射熱補正係数を表5 から取得する関数

    Args:
        region (int): 省エネルギー地域区分
        direction (str): 開口部の面する方位

    Returns:
        float: 冷房期における開口部の取得日射熱補正係数 (-)
    """
    # 開口部の面する方位から表5 の列のインデックスを取得
    col_index = {
        '北': 0,
        '北東': 1,
        '東': 2,
        '南東': 3,
        '南': 4,
        '南西': 5,
        '西': 6,
        '北西': 7,
    }[direction]

    # 省エネルギー地域区分から表5 の行のインデックスを取得
    row_index = region - 1

    return get_table_5()[row_index][col_index]


def get_table_5():
    """表5. 冷房期の取得日射熱補正係数 を取得する関数

    Returns:
        list: 表5. 冷房期の取得日射熱補正係数
    """
    return [
        (0.853, 0.865, 0.882, 0.864, 0.807, 0.860, 0.880, 0.866),
        (0.857, 0.864, 0.877, 0.858, 0.812, 0.861, 0.878, 0.864),
        (0.853, 0.862, 0.870, 0.853, 0.799, 0.859, 0.883, 0.865),
        (0.852, 0.861, 0.881, 0.853, 0.784, 0.850, 0.876, 0.861),
        (0.860, 0.863, 0.874, 0.854, 0.807, 0.858, 0.875, 0.862),
        (0.847, 0.862, 0.880, 0.852, 0.795, 0.852, 0.880, 0.864),
        (0.838, 0.861, 0.881, 0.849, 0.788, 0.847, 0.880, 0.862),
        (0.848, 0.857, 0.877, 0.860, 0.824, 0.858, 0.876, 0.859),
    ]


def calc_eta_H_base_etrc(U_base_etrc):
    """9.10.5 玄関等の基礎の日射熱取得率(暖房期)

    Args:
      U_base_etrc(float): 玄関等の基礎の熱貫流率

    Returns:
      float: 玄関等の基礎の日射熱取得率(暖房期)

    """

    return eater.common.get_eta_H_i(1.0, U_base_etrc)


def calc_eta_C_base_etrc(U_base_etrc):
    """9.10.5 玄関等の基礎の日射熱取得率(冷房期)

    Args:
      U_base_etrc(float): 玄関等の基礎の熱貫流率

    Returns:
      float: 玄関等の基礎の日射熱取得率(冷房期)

    """

    return eater.common.get_eta_C_i(1.0, U_base_etrc)



def calc_eta_H_base_bath(U_base_bath):
    """9.10.6 浴室の基礎の日射熱取得率(暖房期)

    Args:
      U_base_bath(float): 浴室の基礎の熱貫流率

    Returns:
      float: 浴室の基礎の日射熱取得率(暖房期)

    """

    return eater.common.get_eta_H_i(1.0, U_base_bath)


def calc_eta_C_base_bath(U_base_bath):
    """9.10.6 浴室の基礎の日射熱取得率(冷房期)

    Args:
      U_base_bath(float): 浴室の基礎の熱貫流率

    Returns:
      浴室の基礎の日射熱取得率(冷房期)

    """
    return eater.common.get_eta_C_i(1.0, U_base_bath)


def calc_eta_H_base_other(U_base_other):
    """9.10.7 その他の基礎の日射熱取得率(暖房期)

    Args:
      U_base_other(float): その他の基礎の熱貫流率

    Returns:
      float: その他の基礎の日射熱取得率(暖房期)

    """
    return eater.common.get_eta_H_i(1.0, U_base_other)


def calc_eta_C_base_other(U_base_other):
    """9.10.7 その他の基礎の日射熱取得率(冷房期)

    Args:
      U_base_other(float): その他の基礎の熱貫流率

    Returns:
      float: その他の基礎の日射熱取得率(冷房期)

    """
    return eater.common.get_eta_C_i(1.0, U_base_other)


def calc_eta_dash_H_HB_roof(psi_HB_roof):
    """9.10.8 屋根又は天井の熱橋の日射熱取得率(暖房期)

    Args:
      psi_HB_roof(float): 屋根または天井の熱橋の線熱貫流率

    Returns:
      float: 屋根又は天井の熱橋の日射熱取得率(暖房期)

    """
    return eater.heatbridge.get_eta_dash_H_j(1.0, psi_HB_roof)


def calc_eta_dash_C_HB_roof(psi_HB_roof):
    """9.10.8 屋根又は天井の熱橋の日射熱取得率(冷房期)

    Args:
      psi_HB_roof(float): 屋根または天井の熱橋の線熱貫流率

    Returns:
      float: 屋根又は天井の熱橋の日射熱取得率(冷房期)

    """
    return eater.heatbridge.get_eta_dash_C_j(1.0, psi_HB_roof)


def calc_eta_dash_H_HB_wall(psi_HB_wall):
    """9.10.9 壁の熱橋の日射熱取得率(暖房期)

    Args:
      psi_HB_wall(float): 屋根または天井の熱橋の線熱貫流率

    Returns:
      float: 屋根又は天井の熱橋の日射熱取得率(暖房期)

    """
    return eater.heatbridge.get_eta_dash_H_j(1.0, psi_HB_wall)


def calc_eta_dash_C_HB_wall(psi_HB_wall):
    """9.10.9 壁の熱橋の日射熱取得率(冷房期)

    Args:
      psi_HB_wall(float): 屋根または天井の熱橋の線熱貫流率

    Returns:
      float: 屋根又は天井の熱橋の日射熱取得率(冷房期)

    """
    return eater.heatbridge.get_eta_dash_C_j(1.0, psi_HB_wall)


def calc_eta_dash_H_HB_floor(psi_HB_floor):
    """9.10.10 床の熱橋の日射熱取得率(暖房期)

    Args:
      psi_HB_floor(float): 床の熱橋の線熱貫流率

    Returns:
      float: 床の熱橋の日射熱取得率(暖房期)

    """
    return eater.heatbridge.get_eta_dash_H_j(1.0, psi_HB_floor)


def calc_eta_dash_C_HB_floor(psi_HB_floor):
    """9.10.10 床の熱橋の日射熱取得率(冷房期)

    Args:
      psi_HB_floor(float): 床の熱橋の線熱貫流率

    Returns:
      float: 床の熱橋の日射熱取得率    (冷房期)

    """
    return eater.heatbridge.get_eta_dash_C_j(1.0, psi_HB_floor)


def calc_eta_dash_H_HB_roof_wall(psi_HB_roof_wall):
    """9.10.11 屋根又は天井と壁の熱橋の日射熱取得率(暖房期)

    Args:
      psi_HB_roof_wall(float): 屋根又は天井と壁の熱橋の線熱貫流率

    Returns:
      float: 屋根又は天井と壁の熱橋の日射熱取得率(暖房期)

    """
    return eater.heatbridge.get_eta_dash_H_j(1.0, psi_HB_roof_wall)


def calc_eta_dash_C_HB_roof_wall(psi_HB_roof_wall):
    """9.10.11 屋根又は天井と壁の熱橋の日射熱取得率(冷房期)

    Args:
      psi_HB_roof_wall(float): 屋根又は天井と壁の熱橋の線熱貫流率

    Returns:
      float: 屋根又は天井と壁の熱橋の日射熱取得率(冷房期)

    """
    return eater.heatbridge.get_eta_dash_C_j(1.0, psi_HB_roof_wall)


def calc_eta_dash_H_HB_wall_wall(psi_HB_wall_wall):
    """9.10.12 壁と壁の熱橋の日射熱取得率(暖房期)

    Args:
      psi_HB_wall_wall(float): 壁と壁の熱橋の日射熱取得率

    Returns:
      float: 壁と壁（出隅）の熱橋の日射熱取得率(暖房期)

    """
    return eater.heatbridge.get_eta_dash_H_j(1.0, psi_HB_wall_wall)


def calc_eta_dash_C_HB_wall_wall(psi_HB_wall_wall):
    """9.10.12 壁と壁の熱橋の日射熱取得率(暖房期)

    Args:
      psi_HB_wall_wall(float): 壁と壁の熱橋の日射熱取得率

    Returns:
      float: 壁と壁（入隅）の熱橋の日射熱取得率(暖房期)

    """
    return eater.heatbridge.get_eta_dash_C_j(1.0, psi_HB_wall_wall)


def calc_eta_dash_H_HB_wall_floor(psi_HB_wall_floor):
    """9.10.13 壁と床の熱橋の日射熱取得率(暖房期)

    Args:
      psi_HB_wall_floor(float): 壁と床の熱橋の日射熱取得率

    Returns:
      float: 壁と床の熱橋の日射熱取得率(暖房期)

    """
    return eater.heatbridge.get_eta_dash_H_j(1.0, psi_HB_wall_floor)


def calc_eta_dash_C_HB_wall_floor(psi_HB_wall_floor):
    """9.10.13 壁と床の熱橋の日射熱取得率(冷房期)

    Args:
      psi_HB_wall_floor(float): 壁と床の熱橋の日射熱取得率

    Returns:
      float: 壁と床の熱橋の日射熱取得率(冷房期)

    """
    return eater.heatbridge.get_eta_dash_C_j(1.0, psi_HB_wall_floor)