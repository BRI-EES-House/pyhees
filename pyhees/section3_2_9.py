# ============================================================================
# 9. 当該住戸の外皮の部位の面積等を用いずに外皮性能を評価する方法
# ============================================================================

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

def __calc_U_A(house_insulation_type, floor_bath_insulation, U_roof, U_wall, U_door, U_window, U_floor_bath, U_floor_other,
               U_base_etrc, U_base_bath, U_base_other,
               Psi_prm_etrc, Psi_prm_bath, Psi_prm_other,
               Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall, Psi_HB_wall_wall, Psi_HB_wall_floor):
    """ 外皮平均熱貫流率

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :param U_roof: 屋根又は天井の熱貫流率
    :type U_roof: float
    :param U_wall: 壁の熱貫流率
    :type U_wall: float
    :param U_door: ドアの熱貫流率
    :type U_door: float
    :param U_window: 窓の熱貫流率
    :type U_window: float
    :param U_floor_bath: 浴室の床の熱貫流率
    :type U_floor_bath: float
    :param U_floor_other: その他の熱貫流率
    :type U_floor_other: float
    :param U_base_etrc: 玄関等の基礎の熱貫流率
    :type U_base_etrc: float
    :param U_base_bath: 浴室の基礎の熱貫流率
    :type U_base_bath: float
    :param U_base_other: その他の基礎の熱貫流率
    :type U_base_other: float
    :param Psi_prm_etrc: 玄関等の土間床等の外周部の線熱貫流率
    :type Psi_prm_etrc: float
    :param Psi_prm_bath: 浴室の土間床等の外周部の線熱貫流率
    :type Psi_prm_bath: float
    :param Psi_prm_other: その他の土間床等の外周部の線熱貫流率
    :type Psi_prm_other: float
    :param Psi_HB_roof: 屋根または天井の熱橋の線熱貫流率
    :type Psi_HB_roof: float
    :param Psi_HB_wall: 壁の熱橋の線熱貫流率
    :type Psi_HB_wall: float
    :param Psi_HB_floor: 床の熱橋の線熱貫流率
    :type Psi_HB_floor: float
    :param Psi_HB_roof_wall: 屋根または天井と壁の熱橋の線熱貫流率
    :type Psi_HB_roof_wall: float
    :param Psi_HB_wall_wall: 壁と壁の熱橋の線熱貫流率
    :type Psi_HB_wall_wall: float
    :param Psi_HB_wall_floor: 壁と床の熱橋の線熱貫流率
    :type Psi_HB_wall_floor: float
    :return: 外皮平均熱貫流率
    :rtype: float
    """
    # 単位温度差当たりの外皮熱損失量[W/K] (9b)
    q = get_q(house_insulation_type, floor_bath_insulation,
              U_roof, U_wall, U_door, U_window, U_floor_bath, U_floor_other,
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
    """ 外皮平均熱貫流率 (9a)

    :param q: 単位温度差当たりの外皮熱損失量 (W/K)
    :type q: float
    :param A_dash_env: 標準住戸における外皮の部位の面積の合計 (m2)
    :type A_dash_env: float
    :return: 外皮平均熱貫流率
    :rtype: float
    """
    U_A_raw = q / A_dash_env
    U_A = ceil(U_A_raw * 100) / 100
    return U_A



def get_q(house_insulation_type, floor_bath_insulation,
          U_roof, U_wall, U_door, U_window, U_floor_bath, U_floor_other,
          U_base_etrc, U_base_bath, U_base_other,
          Psi_prm_etrc, Psi_prm_bath, Psi_prm_other,
          Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
          Psi_HB_wall_wall, Psi_HB_wall_floor
          ):
    """ 単位温度差当たりの外皮熱損失量[W/K] (9b)
         (主開口方位は南西とする)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :param U_roof: 屋根又は天井の熱貫流率
    :type U_roof: float
    :param U_wall: 壁の熱貫流率
    :type U_wall: float
    :param U_door: ドアの熱貫流率
    :type U_door: float
    :param U_window: 窓の熱貫流率
    :type U_window: float
    :param U_floor_bath: 浴室の床の熱貫流率
    :type U_floor_bath: float
    :param U_floor_other: その他の熱貫流率
    :type U_floor_other: float
    :param U_base_etrc: 玄関等の基礎の熱貫流率
    :type U_base_etrc: float
    :param U_base_bath: 浴室の基礎の熱貫流率
    :type U_base_bath: float
    :param U_base_other: その他の基礎の熱貫流率
    :type U_base_other: float
    :param Psi_prm_etrc: 玄関等の土間床等の外周部の線熱貫流率
    :type Psi_prm_etrc: float
    :param Psi_prm_bath: 浴室の土間床等の外周部の線熱貫流率
    :type Psi_prm_bath: float
    :param Psi_prm_other: その他の土間床等の外周部の線熱貫流率
    :type Psi_prm_other: float
    :param Psi_HB_roof: 屋根または天井の熱橋の線熱貫流率
    :type Psi_HB_roof: float
    :param Psi_HB_wall: 壁の熱橋の線熱貫流率
    :type Psi_HB_wall: float
    :param Psi_HB_floor: 床の熱橋の線熱貫流率
    :type Psi_HB_floor: float
    :param Psi_HB_roof_wall: 屋根または天井と壁の熱橋の線熱貫流率
    :type Psi_HB_roof_wall: float
    :param Psi_HB_wall_wall: 壁と壁の熱橋の線熱貫流率
    :type Psi_HB_wall_wall: float
    :param Psi_HB_wall_floor: 壁と床の熱橋の線熱貫流率
    :type Psi_HB_wall_floor: float
    :return: 単位温度差当たりの外皮熱損失量[W/K]
    :rtype: float
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
        A_dash_floor_bath * H_IS * U_floor_bath,
        # floor other
        A_dash_floor_other * H_IS * U_floor_other,
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
    """ 暖房期の平均日射熱取得率 (10a)

    :param m_H: 単位日射強度当たりの暖房期の日射熱取得量 (W/(W/m2))
    :type m_H: float
    :param A_dash_env: 標準住戸における外皮の部位の面積の合計 (m2)
    :type A_dash_env: float
    :return: 暖房期の平均日射熱取得率
    :rtype: float
    """

    if m_H is None:
        return None
    etr_A_H = m_H / A_dash_env * 100
    return floor(etr_A_H * 10) / 10


def get_m_H(region, house_insulation_type, floor_bath_insulation, U_roof, U_wall, U_door,
            U_base_etrc, U_base_bath, U_base_other, Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
            Psi_HB_wall_wall, Psi_HB_wall_floor, etr_d, f_H=None):
    """ 単位日射強度当たりの暖房期の日射熱取得量[W/(W/m2)] (10b)

    :param region: 省エネルギー地域区分
    :type region: int
    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :param U_roof: 屋根又は天井の熱貫流率
    :type U_roof: float
    :param U_wall: 壁の熱貫流率
    :type U_wall: float
    :param U_door: ドアの熱貫流率
    :type U_door: float
    :param U_base_etrc: 玄関等の基礎の熱貫流率
    :type U_base_etrc: float
    :param U_base_bath: 浴室の基礎の熱貫流率
    :type U_base_bath: float
    :param U_base_other: その他の基礎の熱貫流率
    :type U_base_other: float
    :param Psi_HB_roof: 屋根または天井の熱橋の線熱貫流率
    :type Psi_HB_roof: float
    :param Psi_HB_wall: 壁の熱橋の線熱貫流率
    :type Psi_HB_wall: float
    :param Psi_HB_floor: 床の熱橋の線熱貫流率
    :type Psi_HB_floor: float
    :param Psi_HB_roof_wall: 屋根または天井と壁の熱橋の線熱貫流率
    :type Psi_HB_roof_wall: float
    :param Psi_HB_wall_wall: 壁と壁の熱橋の線熱貫流率
    :type Psi_HB_wall_wall: float
    :param Psi_HB_wall_floor: 壁と床の熱橋の線熱貫流率
    :type Psi_HB_wall_floor: float
    :param etr_d: 暖房期の垂直面日射熱取得率 (-)
    :type etr_d: float
    :param f_H: 暖房期の取得日射熱補正係数 (-)
    :type f_H: float
    :return: 単位日射強度当たりの暖房期の日射熱取得量[W/(W/m2)]
    :rtype: float
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
    """ 冷房期の平均日射熱取得率 (-) (11a)

    :param m_C: 単位日射強度当たりの冷房期の日射熱取得量 (W/(W/m2))
    :type m_C: float
    :param A_dash_env: 標準住戸における外皮の部位の面積の合計 (m2)
    :type A_dash_env: float
    :return: 冷房期の平均日射熱取得率 (-)
    :rtype: float
    """

    etr_A_C = m_C / A_dash_env * 100
    return ceil(etr_A_C * 10) / 10


def get_m_C(region, house_insulation_type, floor_bath_insulation, U_roof, U_wall, U_door,
            U_base_etrc, U_base_bath, U_base_other, Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
            Psi_HB_wall_wall, Psi_HB_wall_floor, etr_d, f_C=None):
    """ 単位日射強度当たりの冷房期の日射熱取得量[W/(W/m2)] (11b)

    :param region: 省エネルギー地域区分
    :type region: int
    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :param U_roof: 屋根又は天井の熱貫流率
    :type U_roof: float
    :param U_wall: 壁の熱貫流率
    :type U_wall: float
    :param U_door: ドアの熱貫流率
    :type U_door: float
    :param U_base_etrc: 玄関等の基礎の熱貫流率
    :type U_base_etrc: float
    :param U_base_bath: 浴室の基礎の熱貫流率
    :type U_base_bath: float
    :param U_base_other: その他の基礎の熱貫流率
    :type U_base_other: float
    :param Psi_HB_roof: 屋根または天井の熱橋の線熱貫流率
    :type Psi_HB_roof: float
    :param Psi_HB_wall: 壁の熱橋の線熱貫流率
    :type Psi_HB_wall: float
    :param Psi_HB_floor: 床の熱橋の線熱貫流率
    :type Psi_HB_floor: float
    :param Psi_HB_roof_wall: 屋根または天井と壁の熱橋の線熱貫流率
    :type Psi_HB_roof_wall: float
    :param Psi_HB_wall_wall: 壁と壁の熱橋の線熱貫流率
    :type Psi_HB_wall_wall: float
    :param Psi_HB_wall_floor: 壁と床の熱橋の線熱貫流率
    :type Psi_HB_wall_floor: float
    :param etr_d: 暖房期の垂直面日射熱取得率 (-)
    :type etr_d: float
    :param f_C: 冷房期の取得日射熱補正係数 (-)
    :type f_C: float
    :return: 単位日射強度当たりの冷房期の日射熱取得量[W/(W/m2)]
    :rtype: float
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
    """ 床面積の合計に対する外皮の部位の面積の合計の比  (12)

    :param A_dash_env: 標準住戸における外皮の部位の面積の合計 (m2)
    :type A_dash_env: float
    :param A_dash_A: 標準住戸における床面積の合計 (m2)
    :type A_dash_A: float
    :return: 床面積の合計に対する外皮の部位の面積の合計の比 (-)
    :rtype: float
    """

    return A_dash_env / A_dash_A


# ============================================================================
# 9.6 標準住戸における外皮の部位の面積及び土間床等の外周部の長さ等
# ============================================================================

def calc_U_A(insulation_structure, house_structure_type, floor_bath_insulation=None, bath_insulation_type=None,
             U_roof=None, U_wall=None, U_door=None, U_window=None, U_floor_bath=None, U_floor_other=None,
             U_base_etrc=None, U_base_bath=None, U_base_other=None,
             Psi_prm_etrc=None, Psi_prm_bath=None, Psi_prm_other=None, Psi_HB_roof=None, Psi_HB_wall=None,
             Psi_HB_floor=None, Psi_HB_roof_wall=None, Psi_HB_wall_wall=None, Psi_HB_wall_floor=None):
    """ 断熱構造による住戸の種類に応じてU_A値を計算する

    :param insulation_structure: 断熱構造による住戸の種類
    :type insulation_structure: str
    :param house_structure_type: '木造'または'鉄筋コンクリート造'または'鉄骨造'
    :type house_structure_type: str
    :param floor_bath_insulation: 浴室床の断熱
    :type floor_bath_insulation: str
    :param bath_insulation_type: 浴室の断熱タイプ※
    :type bath_insulation_type: str
    :param U_roof: 屋根又は天井の熱貫流率
    :type U_roof: float
    :param U_wall: 壁の熱貫流率
    :type U_wall: float
    :param U_door: ドアの熱貫流率
    :type U_door: float
    :param U_window: 窓の熱貫流率
    :type U_window: float
    :param U_floor_bath: 浴室の床の熱貫流率
    :type U_floor_bath: float
    :param U_floor_other: その他の熱貫流率
    :type U_floor_other: float
    :param Psi_prm_etrc: 玄関等の土間床等の外周部の線熱貫流率
    :type Psi_prm_etrc: float
    :param Psi_prm_bath: 浴室の土間床等の外周部の線熱貫流率
    :type Psi_prm_bath: float
    :param Psi_prm_other: その他の土間床等の外周部の線熱貫流率
    :type Psi_prm_other: float
    :param Psi_HB_roof: 屋根または天井の熱橋の線熱貫流率
    :type Psi_HB_roof: float
    :param Psi_HB_wall: 壁の熱橋の線熱貫流率
    :type Psi_HB_wall: float
    :param Psi_HB_floor: 床の熱橋の線熱貫流率
    :type Psi_HB_floor: float
    :param Psi_HB_roof_wall: 屋根または天井と壁の熱橋の線熱貫流率
    :type Psi_HB_roof_wall: float
    :param Psi_HB_wall_wall: 壁と壁の熱橋の線熱貫流率
    :type Psi_HB_wall_wall: float
    :param Psi_HB_wall_floor: 壁と床の熱橋の線熱貫流率
    :type Psi_HB_wall_floor: float
    :return: 外皮平均熱貫流率 (U_A), 外皮の部位の熱貫流率 (U)
    :rtype: tuple
    """

    # 断熱構造による住戸の種類
    if insulation_structure == '床断熱住戸の場合':
        U = get_U('床断熱住戸', house_structure_type, floor_bath_insulation, bath_insulation_type, U_roof, U_wall,
                  U_door, U_window, U_floor_bath, U_floor_other, U_base_etrc, U_base_bath, U_base_other,
                  Psi_prm_etrc, Psi_prm_bath, Psi_prm_other, Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
                  Psi_HB_wall_wall, Psi_HB_wall_floor)
        U_A = __calc_U_A(**U)
    elif insulation_structure == '基礎断熱住戸の場合':
        U = get_U('基礎断熱住戸', house_structure_type, floor_bath_insulation, bath_insulation_type, U_roof, U_wall,
                  U_door, U_window, U_floor_bath, U_floor_other, U_base_etrc, U_base_bath, U_base_other,
                  Psi_prm_etrc, Psi_prm_bath, Psi_prm_other, Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
                  Psi_HB_wall_wall, Psi_HB_wall_floor)
        U_A = __calc_U_A(**U)
    elif insulation_structure == '玄関等及び浴室を除いた部分の外皮が床と土間床等の外周部の基礎のいずれにも該当する場合':
        # 玄関等及び浴室を除いた部分の外皮が床と土間床等の外周部の基礎のいずれにも該当する場合は、
        # 表3の標準住戸における部位の面積及び土間床等の外周部の長さ等の値について、表3（い）欄に示す値及び
        # 表3（ろ）欄に示す値の両方を式(9a)及び式(9b)で表される外皮平均熱貫流率の計算に適用し、
        # 外皮平均熱貫流率の値が大きい方の場合を採用する
        U_0 = get_U('床断熱住戸', house_structure_type, floor_bath_insulation, bath_insulation_type, U_roof, U_wall,
                    U_door, U_window, U_floor_bath, U_floor_other, U_base_etrc, U_base_bath, U_base_other,
                    Psi_prm_etrc, Psi_prm_bath, Psi_prm_other, Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall,
                    Psi_HB_wall_wall, Psi_HB_wall_floor)
        U_1 = get_U('基礎断熱住戸', house_structure_type, floor_bath_insulation, bath_insulation_type, U_roof, U_wall,
                    U_door, U_window, U_floor_bath, U_floor_other, U_base_etrc, U_base_bath, U_base_other,
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
    """ 表3 標準住戸における部位の面積及び土間床等の外周部の長さ等

    :param i: 表3における行番号
    :type i: int
    :param house_insulation_type: '床断熱'または'基礎断熱'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱'または'基礎断熱'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 標準住戸における部位の面積及び土間床等の外周部の長さ等 (m)または(m2)
    :rtype: float
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
    """ 標準住戸における外皮の部位の面積の合計 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 標準住戸における外皮の部位の面積の合計 (m2)
    :rtype: float
    """
    return get_table_3(0, house_insulation_type, floor_bath_insulation)


def get_A_dash_A():
    """床面積の合計 (m2)

    :return: 床面積の合計 (m2)
    :rtype: float
    """
    return get_table_3(1, None)


def get_A_dash_roof():
    """ 屋根又は天井の面積 (m2)

    :return: 屋根又は天井の面積 (m2)
    :rtype: float
    """
    return get_table_3(2, None)


def get_A_dash_wall_0():
    """ 主開口方向から時計回りに0°の方向に面した壁の面積 (m2)

    :return: 主開口方向から時計回りに0°の方向に面した壁の面積 (m2)
    :rtype: float
    """
    return get_table_3(3, None)


def get_A_dash_wall_90():
    """ 主開口方向から時計回りに90°の方向に面した壁の面積 (m2)

    :return: 主開口方向から時計回りに90°の方向に面した壁の面積 (m2)
    :rtype: float
    """
    return get_table_3(4, None)


def get_A_dash_wall_180():
    """ 主開口方向から時計回りに180°の方向に面した壁の面積 (m2)

    :return: 主開口方向から時計回りに180°の方向に面した壁の面積 (m2)
    :rtype: float
    """
    return get_table_3(5, None)


def get_A_dash_wall_270():
    """ 主開口方向から時計回りに270°の方向に面した壁の面積 (m2)

    :return: 主開口方向から時計回りに270°の方向に面した壁の面積 (m2)
    :rtype: float
    """
    return get_table_3(6, None)


def get_A_dash_door_0():
    """ 主開口方向から時計回りに0°の方向に面したドアの面積 (m2)

    :return: 主開口方向から時計回りに0°の方向に面したドアの面積 (m2)
    :rtype: float
    """
    return get_table_3(7, None)


def get_A_dash_door_90():
    """ 主開口方向から時計回りに90°の方向に面したドアの面積 (m2)

    :return: 主開口方向から時計回りに90°の方向に面したドアの面積 (m2)
    :rtype: float
    """
    return get_table_3(8, None)


def get_A_dash_door_180():
    """ 主開口方向から時計回りに180°の方向に面したドアの面積 (m2)

    :return: 主開口方向から時計回りに180°の方向に面したドアの面積 (m2)
    :rtype: float
    """
    return get_table_3(9, None)


def get_A_dash_door_270():
    """ 主開口方向から時計回りに270°の方向に面したドアの面積 (m2)

    :return: 主開口方向から時計回りに270°の方向に面したドアの面積 (m2)
    :rtype: float
    """
    return get_table_3(10, None)


def get_A_dash_window_0():
    """ 主開口方向から時計回りに0°の方向に面した窓の面積 (m2)

    :return: 主開口方向から時計回りに0°の方向に面した窓の面積 (m2)
    :rtype: float
    """
    return get_table_3(11, None)


def get_A_dash_window_90():
    """  主開口方向から時計回りに90°の方向に面した窓の面積 (m2)

    :return: 主開口方向から時計回りに90°の方向に面した窓の面積 (m2)
    :rtype: float
    """
    return get_table_3(12, None)


def get_A_dash_window_180():
    """ 主開口方向から時計回りに180°の方向に面した窓の面積 (m2)

    :return: 主開口方向から時計回りに180°の方向に面した窓の面積 (m2)
    :rtype: float
    """
    return get_table_3(13, None)


def get_A_dash_window_270():
    """ 主開口方向から時計回りに270°の方向に面した窓の面積 (m2)

    :return: 主開口方向から時計回りに270°の方向に面した窓の面積 (m2)
    :rtype: float
    """
    return get_table_3(14, None)


def get_A_dash_floor_bath(house_insulation_type, floor_bath_insulation):
    """ 浴室の床の面積 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 浴室の床の面積 (m2)
    :rtype: float
    """
    return get_table_3(15, house_insulation_type, floor_bath_insulation)


def get_A_dash_floor_other(house_insulation_type, floor_bath_insulation):
    """ 浴室の床の面積 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 浴室の床の面積 (m2)
    :rtype: float
    """
    return get_table_3(16, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_etrc_OS_0():
    """ 主開口方向から時計回りに0°の方向の外気に面した玄関等の基礎の面積 (m2)

    :return: 主開口方向から時計回りに0°の方向の外気に面した玄関等の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(17, None)


def get_A_dash_base_etrc_OS_90():
    """ 主開口方向から時計回りに90°の方向の外気に面した玄関等の基礎の面積 (m2)

    :return: 主開口方向から時計回りに90°の方向の外気に面した玄関等の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(18, None)


def get_A_dash_base_etrc_OS_180():
    """ 主開口方向から時計回りに180°の方向の外気に面した玄関等の基礎の面積 (m2)

    :return: 主開口方向から時計回りに180°の方向の外気に面した玄関等の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(19, None)


def get_A_dash_base_etrc_OS_270():
    """ 主開口方向から時計回りに270°の方向の外気に面した玄関等の基礎の面積 (m2)

    :return: 主開口方向から時計回りに270°の方向の外気に面した玄関等の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(20, None)


def get_A_dash_base_etrc_IS(house_insulation_type, floor_bath_insulation):
    """ 床下に面した玄関等の基礎の面積 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 床下に面した玄関等の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(21, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_bath_OS_0(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに0°の方向の外気に面した浴室の基礎の面積 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに0°の方向の外気に面した浴室の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(22, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_bath_OS_90(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに90°の方向の外気に面した浴室の基礎の面積 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに90°の方向の外気に面した浴室の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(23, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_bath_OS_180(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに180°の方向の外気に面した浴室の基礎の面積 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに180°の方向の外気に面した浴室の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(24, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_bath_OS_270(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに270°の方向の外気に面した浴室の基礎の面積 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに270°の方向の外気に面した浴室の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(25, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_bath_IS(house_insulation_type, floor_bath_insulation):
    """ 床下に面した浴室の基礎の面積 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 床下に面した浴室の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(26, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_other_OS_0(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに0°の方向の外気に面したその他の基礎の面積 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに0°の方向の外気に面したその他の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(27, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_other_OS_90(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに90°の方向の外気に面したその他の基礎の面積 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに90°の方向の外気に面したその他の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(28, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_other_OS_180(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに180°の方向の外気に面したその他の基礎の面積 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに180°の方向の外気に面したその他の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(29, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_other_OS_270(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに270°の方向の外気に面したその他の基礎の面積 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに270°の方向の外気に面したその他の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(30, house_insulation_type, floor_bath_insulation)


def get_A_dash_base_other_IS(house_insulation_type, floor_bath_insulation):
    """ 床下に面したその他の基礎の面積 (m2)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 床下に面したその他の基礎の面積 (m2)
    :rtype: float
    """
    return get_table_3(31, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_etrc_OS_0():
    """ 主開口方向から時計回りに0°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)

    :return: 主開口方向から時計回りに0°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(32, None)


def get_L_dash_prm_etrc_OS_90():
    """ 主開口方向から時計回りに90°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)

    :return: 主開口方向から時計回りに90°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(33, None)


def get_L_dash_prm_etrc_OS_180():
    """ 主開口方向から時計回りに180°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)

    :return: 主開口方向から時計回りに180°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(34, None)


def get_L_dash_prm_etrc_OS_270():
    """ 主開口方向から時計回りに270°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)

    :return: 主開口方向から時計回りに270°の方向の外気に面した玄関等の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(35, None)


def get_L_dash_prm_etrc_IS(house_insulation_type, floor_bath_insulation):
    """ 床下に面した玄関等の土間床等の外周部の長さ (m)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 床下に面した玄関等の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(36, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_bath_OS_0(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに0°の方向の外気に面した浴室の土間床等の外周部の長さ (m)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに0°の方向の外気に面した浴室の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(37, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_bath_OS_90(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに90°の方向の外気に面した浴室の土間床等の外周部の長さ (m)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに90°の方向の外気に面した浴室の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(38, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_bath_OS_180(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに180°の方向の外気に面した浴室の土間床等の外周部の長さ (m)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに180°の方向の外気に面した浴室の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(39, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_bath_OS_270(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに270°の方向の外気に面した浴室の土間床等の外周部の長さ (m)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに270°の方向の外気に面した浴室の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(40, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_bath_IS(house_insulation_type, floor_bath_insulation):
    """ 床下に面した浴室の土間床等の外周部の長さ (m)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 床下に面した浴室の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(41, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_other_OS_0(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに0°の方向の外気に面したその他の土間床等の外周部の長さ (m)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに0°の方向の外気に面したその他の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(42, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_other_OS_90(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに90°の方向の外気に面したその他の土間床等の外周部の長さ (m)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに90°の方向の外気に面したその他の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(43, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_other_OS_180(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに180°の方向の外気に面したその他の土間床等の外周部の長さ (m)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに180°の方向の外気に面したその他の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(44, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_other_OS_270(house_insulation_type, floor_bath_insulation):
    """ 主開口方向から時計回りに270°の方向の外気に面したその他の土間床等の外周部の長さ (m)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 主開口方向から時計回りに270°の方向の外気に面したその他の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(45, house_insulation_type, floor_bath_insulation)


def get_L_dash_prm_other_IS(house_insulation_type, floor_bath_insulation):
    """ 床下に面したその他の土間床等の外周部の長さ (m)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 床下に面したその他の土間床等の外周部の長さ (m)
    :rtype: float
    """
    return get_table_3(46, house_insulation_type, floor_bath_insulation)


def get_L_dash_HB_roof_top():
    """ 上面に面した屋根又は天井の熱橋の長さ (m)

    :return: 上面に面した屋根又は天井の熱橋の長さ (m)
    :rtype: float
    """
    return get_table_3(47, None)


def get_L_dash_HB_wall_0():
    """ 主開口方向から時計回りに0°の方向の外気に面した壁の熱橋の長さ (m)

    :return: 主開口方向から時計回りに0°の方向の外気に面した壁の熱橋の長さ (m)
    :rtype: float
    """
    return get_table_3(48, None)


def get_L_dash_HB_wall_90():
    """ 主開口方向から時計回りに90°の方向の外気に面した壁の熱橋の長さ (m)

    :return: 主開口方向から時計回りに90°の方向の外気に面した壁の熱橋の長さ (m)
    :rtype: float
    """
    return get_table_3(49, None)


def get_L_dash_HB_wall_180():
    """ 主開口方向から時計回りに180°の方向の外気に面した壁の熱橋の長さ (m)

    :return: 主開口方向から時計回りに180°の方向の外気に面した壁の熱橋の長さ (m)
    :rtype: float
    """
    return get_table_3(50, None)


def get_L_dash_HB_wall_270():
    """ 主開口方向から時計回りに270°の方向の外気に面した壁の熱橋の長さ (m)

    :return: 主開口方向から時計回りに270°の方向の外気に面した壁の熱橋の長さ (m)
    :rtype: float
    """
    return get_table_3(51, None)


def get_L_dash_HB_floor_IS(house_insulation_type, floor_bath_insulation):
    """ 床下に面した床の熱橋の長さ (m)

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: '床断熱住戸'または'基礎断熱住戸'または'浴室の床及び基礎が外気等に面していない'
    :type floor_bath_insulation: str
    :return: 床下に面した床の熱橋の長さ (m)
    :rtype: float
    """
    return get_table_3(52, house_insulation_type, floor_bath_insulation)


def get_L_dash_HB_roof_wall_top():
    """ 上面に面した屋根又は天井と壁の熱橋長さ (m)

    :return: 面に面した屋根又は天井と壁の熱橋長さ (m)
    :rtype: float
    """
    return get_table_3(53, None)


def get_L_dash_HB_roof_wall_top_0():
    """ 主開口方向から時計回りに0°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)

    :return: 主開口方向から時計回りに0°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)
    :rtype: float
    """
    return get_table_3(53, None)


def get_L_dash_HB_roof_wall_top_90():
    """ 主開口方向から時計回りに90°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)

    :return: 主開口方向から時計回りに90°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)
    :rtype: float
    """
    return get_table_3(54, None)


def get_L_dash_HB_roof_wall_top_180():
    """ 主開口方向から時計回りに180°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)

    :return: 主開口方向から時計回りに180°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)
    :rtype: float
    """
    return get_table_3(55, None)


def get_L_dash_HB_roof_wall_top_270():
    """ 主開口方向から時計回りに270°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)

    :return: 主開口方向から時計回りに270°の方向の外気に面した屋根又は天井と壁の熱橋長さ (m)
    :rtype: float
    """
    return get_table_3(56, None)


def get_L_dash_HB_wall_wall_0_90():
    """ 主開口方向から時計回りに0°の方向の外気に面した壁と壁の熱橋長さ (m)

    :return: 主開口方向から時計回りに0°の方向の外気に面した壁と壁の熱橋長さ (m)
    :rtype: float
    """
    return get_table_3(57, None)


def get_L_dash_HB_wall_wall_90_180():
    """ 主開口方向から時計回りに90°の方向の外気に面した壁と壁の熱橋長さ (m)

    :return: 主開口方向から時計回りに90°の方向の外気に面した屋壁と壁の熱橋長さ (m)
    :rtype: float
    """
    return get_table_3(58, None)


def get_L_dash_HB_wall_wall_180_270():
    """ 主開口方向から時計回りに180°の方向の外気に面した壁と壁の熱橋長さ (m)

    :return: 主開口方向から時計回りに180°の方向の外気に面した壁と壁の熱橋長さ (m)
    :rtype: float
    """
    return get_table_3(59, None)


def get_L_dash_HB_wall_wall_270_0():
    """ 主開口方向から時計回りに270°の方向の外気に面した壁と壁の熱橋長さ (m)

    :return: 主開口方向から時計回りに270°の方向の外気に面した壁と壁の熱橋長さ (m)
    :rtype: float
    """
    return get_table_3(60, None)


def get_L_dash_HB_wall_floor_0_IS():
    """ 主開口方向から時計回りに0°の方向の外気に面した壁と床の熱橋長さ (m)

    :return: 主開口方向から時計回りに0°の方向の外気に面した壁と床の熱橋長さ (m)
    :rtype: float
    """
    return get_table_3(61, None)


def get_L_dash_HB_wall_floor_90_IS():
    """ 主開口方向から時計回りに90°の方向の外気に面した壁と床の熱橋長さ (m)

    :return: 主開口方向から時計回りに90°の方向の外気に面した壁と床の熱橋長さ (m)
    :rtype: float
    """
    return get_table_3(62, None)


def get_L_dash_HB_wall_floor_180_IS():
    """ 主開口方向から時計回りに180°の方向の外気に面した壁と床の熱橋長さ (m)

    :return: 主開口方向から時計回りに180°の方向の外気に面した壁と床の熱橋長さ (m)
    :rtype: float
    """
    return get_table_3(63, None)


def get_L_dash_HB_wall_floor_270_IS():
    """ 主開口方向から時計回りに270°の方向の外気に面した壁と床の熱橋長さ (m)

    :return: 主開口方向から時計回りに270°の方向の外気に面した壁と床の熱橋長さ (m)
    :rtype: float
    """
    return get_table_3(64, None)


# ============================================================================
# 9.7 外皮の部位及び熱橋等の温度差係数
# ============================================================================

def get_H_OS():
    """ 屋根又は天井の温度差係数 (-)

    :return: 屋根又は天井の温度差係数 (-)
    :rtype: float
    """
    adjacent_type = '外気'

    return get_H(adjacent_type)


def get_H_IS():
    """ 壁の温度差係数 (-)

    :return: 壁の温度差係数 (-)
    :rtype: float
    """
    adjacent_type = '外気に通じていない空間・外気に通じる床裏'
    return get_H(adjacent_type)


# ============================================================================
# 9.8 外皮の部位及び熱橋等の方位係数
# ============================================================================

# 標準住戸における外皮の部位及び熱橋等の方位係数は、地域の区分・方位・期間に応じて付録Cに定める方法により求めた値とする。


# ============================================================================
# 9.9 外皮の部位の熱貫流率及び熱橋等の線熱貫流率
# ============================================================================

def get_U(house_insulation_type, house_structure_type, floor_bath_insulation=None, bath_insulation_type=None, U_roof=None, U_wall=None,
          U_door=None, U_window=None, U_floor_bath=None, U_floor_other=None, U_base_etrc=None, U_base_bath=None, U_base_other=None,
          Psi_prm_etrc=None, Psi_prm_bath=None, Psi_prm_other=None,
          Psi_HB_roof=None, Psi_HB_wall=None, Psi_HB_floor=None, Psi_HB_roof_wall=None,
          Psi_HB_wall_wall=None, Psi_HB_wall_floor=None):
    """ 屋根又は天井・壁・ドア・窓・熱橋等の熱貫流率

    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param house_structure_type: '木造'または'鉄筋コンクリート造'または'鉄骨造'
    :type house_structure_type: str
    :param floor_bath_insulation: 浴室床の断熱
    :type floor_bath_insulation: str
    :param bath_insulation_type: 浴室の断熱タイプ※
    :type bath_insulation_type: str
    :param U_roof: 屋根又は天井の熱貫流率
    :type U_roof: float
    :param U_wall: 壁の熱貫流率
    :type U_wall: float
    :param U_door: ドアの熱貫流率
    :type U_door: float
    :param U_window: 窓の熱貫流率
    :type U_window: float
    :param U_floor_bath: 浴室の床の熱貫流率
    :type U_floor_bath: float
    :param U_floor_other: その他の熱貫流率
    :type U_floor_other: float
    :param Psi_prm_etrc: 玄関等の土間床等の外周部の線熱貫流率
    :type Psi_prm_etrc: float
    :param Psi_prm_bath: 浴室の土間床等の外周部の線熱貫流率
    :type Psi_prm_bath: float
    :param Psi_prm_other: その他の土間床等の外周部の線熱貫流率
    :type Psi_prm_other: float
    :param Psi_HB_roof: 屋根または天井の熱橋の線熱貫流率
    :type Psi_HB_roof: float
    :param Psi_HB_wall: 壁の熱橋の線熱貫流率
    :type Psi_HB_wall: float
    :param Psi_HB_floor: 床の熱橋の線熱貫流率
    :type Psi_HB_floor: float
    :param Psi_HB_roof_wall: 屋根または天井と壁の熱橋の線熱貫流率
    :type Psi_HB_roof_wall: float
    :param Psi_HB_wall_wall: 壁と壁の熱橋の線熱貫流率
    :type Psi_HB_wall_wall: float
    :param Psi_HB_wall_floor: 壁と床の熱橋の線熱貫流率
    :type Psi_HB_wall_floor: float
    :return: 屋根又は天井・壁・ドア・窓・熱橋等の熱貫流率
    :rtype: dict
    """

    # 屋根又は天井・壁・ドア・窓の熱貫流率
    if house_insulation_type == '床断熱住戸':

        # 浴室の断熱構造
        if floor_bath_insulation == '床断熱':
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
            Psi_prm_etrc = get_psi_prm_etrc(Psi_prm_etrc)
            Psi_prm_bath = get_psi_prm_bath(Psi_prm_bath, Psi_prm_other, house_insulation_type)
            U_base_bath = get_U_base_bath(U_base_bath, U_base_other, house_insulation_type, floor_bath_insulation)
        elif floor_bath_insulation == '浴室の床及び基礎が外気等に面していない':
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
        U_floor_other = 0
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
        'U_floor_other': U_floor_other,
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


def get_U_roof(U_roof, H_roof=None):
    """ 9.9.1 屋根又は天井の熱貫流率

    :param U_roof: 屋根又は天井の熱貫流率
    :type U_roof: float
    :param H_roof: 屋根又は天井の温度差係数
    :type H_roof: float
    :return: 9屋根又は天井の熱貫流率
    :rtype: float
    """
    if type(U_roof) in [list, tuple]:
        return U_roof[np.argmax(np.array(U_roof) * np.array(H_roof))]
    else:
        return U_roof


def get_U_wall(U_wall, H_wall=None):
    """ 9.9.2 壁の熱貫流率

    :param U_wall: 壁の熱貫流率
    :type U_wall: float
    :param H_wall: 壁の温度差係数
    :type H_wall: float
    :return: 壁の熱貫流率
    :rtype: float
    """
    if type(U_wall) in [list, tuple]:
        return U_wall[np.argmax(np.array(U_wall) * np.array(H_wall))]
    else:
        return U_wall


def get_U_door(U_door, H_door=None):
    """ 9.9.3 ドアの熱貫流率

    :param U_door: ドアの熱貫流率
    :type U_door: float
    :param H_door: ドアの温度差係数
    :type H_door: float
    :return: ドアの熱貫流率
    :rtype: float
    """
    if type(U_door) in [list, tuple]:
        return U_door[np.argmax(np.array(U_door) * np.array(H_door))]
    else:
        return U_door


def get_U_window(U_window, H_window=None):
    """ 9.9.4 窓の熱貫流率

    :param U_window: 窓の熱貫流率
    :type U_window: float
    :param H_window: 窓の温度差係数
    :type H_window: float
    :return: 窓の熱貫流率
    :rtype: float
    """
    if type(U_window) in [list, tuple]:
        return U_window[np.argmax(np.array(U_window) * np.array(H_window))]
    else:
        return U_window


def get_U_floor_other(U_floor_other, H_floor_other=None):
    """ 9.9.5 その他の床の熱貫流率

    :param U_floor_other: その他の床の熱貫流率
    :type U_floor_other: float
    :param H_floor_other: その他の床の温度差係数
    :type H_floor_other: float
    :return: その他の床の熱貫流率
    :rtype: float
    """
    if type(U_floor_other) in [list, tuple]:
        return U_floor_other[np.argmax(np.array(U_floor_other) * np.array(H_floor_other))]
    else:
        return U_floor_other


def get_U_floor_bath(U_floor_bath, U_floor_other, house_insulation_type, floor_bath_insulation, H_floor_bath=None):
    """ 9.9.6 浴室の床の熱貫流率

    :param U_floor_bath: 浴室の床の熱貫流率
    :type U_floor_bath: float
    :param U_floor_other: その他の熱貫流率
    :type U_floor_other: float
    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: 浴室床の断熱
    :type floor_bath_insulation: str
    :param H_floor_bath: 浴室の床の温度差係数
    :type H_floor_bath: float
    :return: 浴室の床の熱貫流率
    :rtype: float
    """
    if house_insulation_type == '床断熱住戸':
        if floor_bath_insulation == '浴室部分の外皮を床とする':
            if type(U_floor_bath) in [list, tuple]:
                return U_floor_bath[np.argmax(np.array(U_floor_bath) * np.array(H_floor_bath))]
            else:
                return U_floor_bath
        elif floor_bath_insulation == '浴室の床及び基礎が外気等に面していない':
            # 床断熱住戸において外皮の部位として浴室の床が存在しない場合はその他の床の熱貫流率に等しい
            return U_floor_other
        else:
            raise ValueError(floor_bath_insulation)
    else:
        return None


def get_U_base_etrc(U_base_etrc, H_base_etrc=None):
    """ 9.9.7 玄関等の基礎の熱貫流率

    :param U_base_etrc: 玄関等の基礎の熱貫流率
    :type U_base_etrc: float
    :param H_base_etrc: 玄関等の基礎の温度差係数
    :type H_base_etrc: float
    :return: 玄関等の基礎の熱貫流率
    :rtype: float
    """
    if type(U_base_etrc) in [list, tuple]:
        return U_base_etrc[np.argmax(np.array(U_base_etrc) * np.array(H_base_etrc))]
    else:
        return U_base_etrc


def get_U_base_bath(U_base_bath, U_base_other, house_insulation_type, floor_bath_insulation, H_base_bath=None):
    """ 9.9.8 浴室の基礎の熱貫流率

    :param U_base_bath: 浴室の基礎の熱貫流率
    :type U_base_bath: float
    :param U_base_other: その他の基礎の熱貫流率
    :type U_base_other: float
    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param floor_bath_insulation: 浴室の基礎の断熱
    :type floor_bath_insulation: str
    :param H_base_bath: 浴室の基礎の温度差係数
    :type H_base_bath:
    :return: 浴室の基礎の熱貫流率
    :rtype: float
    """
    if house_insulation_type == '床断熱住戸':
        if floor_bath_insulation == '基礎断熱':
            if type(U_base_bath) in [list, tuple]:
                return U_base_bath[np.argmax(np.array(U_base_bath) * np.array(H_base_bath))]
            else:
                return U_base_bath
        else:
            return None
    if house_insulation_type == '基礎断熱住戸':
        return U_base_other
    else:
        return None


def get_U_base_other(U_base_other, H_base_other=None):
    """ 9.9.9 その他の基礎の熱貫流率

    :param U_base_other: その他の基礎の熱貫流率
    :type U_base_other: float
    :param H_base_other: その他の基礎の温度差係数
    :type H_base_other: float
    :return: その他の基礎の熱貫流率
    :rtype: float
    """
    if type(U_base_other) in [list, tuple]:
        return U_base_other[np.argmax(np.array(U_base_other) * np.array(H_base_other))]
    else:
        return U_base_other


def get_psi_prm_etrc(psi_prm_etrc, H_prm_etrc=None):
    """ 9.9.10 玄関等の土間床等の外周部の線熱貫流率

    :param psi_prm_etrc: 玄関等の土間床等の外周部の線熱貫流率
    :type psi_prm_etrc: list, tuple or float
    :param H_prm_etrc: 玄関等の土間床等の外周部の温度差係数
    :type H_prm_etrc: float
    :return: 玄関等の土間床等の外周部の線熱貫流率
    :rtype: float
    """
    if type(psi_prm_etrc) in [list, tuple]:
        return psi_prm_etrc[np.argmax(np.array(psi_prm_etrc) * np.array(H_prm_etrc))]
    else:
        return psi_prm_etrc


def get_psi_prm_bath(psi_prm_bath, phi_prm_other, house_insulation_type, H_prm_bath=None):
    """ 9.9.11 浴室の土間床等の外周部の線熱貫流率

    :param psi_prm_bath: 浴室の土間床等の外周部の線熱貫流率
    :type psi_prm_bath: list, tuple or float
    :param phi_prm_other: その他の土間床等の外周部の線熱貫流率
    :type phi_prm_other: float
    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param H_prm_bath: 浴室の土間床等の外周部の温度差係数
    :type H_prm_bath: float
    :return: 浴室の土間床等の外周部の線熱貫流率
    :rtype: float
    """
    if house_insulation_type == '床断熱住戸':
        if type(psi_prm_bath) in [list, tuple]:
            return psi_prm_bath[np.argmax(np.array(psi_prm_bath) * np.array(H_prm_bath))]
        else:
            return psi_prm_bath
    elif house_insulation_type == '基礎断熱住戸':
        return phi_prm_other
    else:
        return None


def get_psi_prm_other(psi_prm_other, house_insulation_type, H_prm_other=None):
    """ 9.9.12 その他の土間床等の外周部の線熱貫流率

    :param psi_prm_other: その他の土間床等の外周部の線熱貫流率
    :type psi_prm_other: list, tuple or float
    :param house_insulation_type: '床断熱住戸'または'基礎断熱住戸'
    :type house_insulation_type: str
    :param H_prm_other: その他の土間床等の外周部の温度差係数
    :type H_prm_other: float
    :return: その他の土間床等の外周部の線熱貫流率
    :rtype: float
    """
    if house_insulation_type == '基礎断熱住戸':
        if type(psi_prm_other) in [list, tuple]:
            return psi_prm_other[np.argmax(np.array(psi_prm_other) * np.array(H_prm_other))]
        else:
            return psi_prm_other
    else:
        return None


def get_psi_HB_roof(psi_HB_roof, house_structure_type, H_HB_roof=None):
    """ 9.9.13 屋根又は天井の熱橋の線熱貫流率

    :param psi_HB_roof: 屋根又は天井の熱橋の線熱貫流率
    :type psi_HB_roof: list, tuple or float
    :param house_structure_type: '木造'または'鉄筋コンクリート造'、'鉄骨造'
    :type house_structure_type: str
    :param H_HB_roof: 屋根又は天井の熱橋の温度差係数
    :type H_HB_roof: float
    :return: 屋根又は天井の熱橋の線熱貫流率
    :rtype: float
    """
    if house_structure_type == '鉄筋コンクリート造' or house_structure_type == '鉄骨造':
        if type(psi_HB_roof) in [list, tuple]:
            return psi_HB_roof[np.argmax(np.array(psi_HB_roof) * np.array(H_HB_roof))]
        else:
            return psi_HB_roof
    else:
        return 0


def get_psi_HB_wall(psi_HB_wall, house_structure_type, H_HB_wall=None):
    """ 9.9.14 壁の熱橋の線熱貫流率

    :param psi_HB_wall: 壁の熱橋の線熱貫流率
    :type psi_HB_wall: list, tuple or float
    :param house_structure_type: '木造'または'鉄筋コンクリート造'、'鉄骨造'
    :type house_structure_type: str
    :param H_HB_wall: 壁の熱橋の温度差係数
    :type H_HB_wall: float
    :return: 壁の熱橋の線熱貫流率
    :rtype: float
    """
    if house_structure_type == '鉄筋コンクリート造' or house_structure_type == '鉄骨造':
        if type(psi_HB_wall) in [list, tuple]:
            return psi_HB_wall[np.argmax(np.array(psi_HB_wall) * np.array(H_HB_wall))]
        else:
            return psi_HB_wall
    else:
        return 0


def get_psi_HB_floor(psi_HB_floor, house_structure_type, H_HB_floor=None):
    """ 9.9.15 床の熱橋の線熱貫流率

    :param psi_HB_floor: 床の熱橋の線熱貫流率
    :type psi_HB_floor: list, tuple or float
    :param house_structure_type: '木造'または'鉄筋コンクリート造'、'鉄骨造
    :param H_HB_floor: 床の熱橋の温度差係数
    :type H_HB_floor: float
    :return: 床の熱橋の線熱貫流率
    :rtype: float
    """
    if house_structure_type == '鉄筋コンクリート造' or house_structure_type == '鉄骨造':
        if type(psi_HB_floor) in [list, tuple]:
            return psi_HB_floor[np.argmax(np.array(psi_HB_floor) * np.array(H_HB_floor))]
        else:
            return psi_HB_floor
    else:
        return 0


def get_psi_HB_roof_wall(psi_HB_roof_wall, house_structure_type, H_HB_roof_wall=None):
    """ 9.9.16 屋根又は天井と壁の熱橋の線熱貫流率

    :param psi_HB_roof_wall: 屋根又は天井と壁の熱橋の線熱貫流率
    :type psi_HB_roof_wall: list, tuple or float
    :param house_structure_type: '木造'または'鉄筋コンクリート造'、'鉄骨造'
    :type house_structure_type: str
    :param H_HB_roof_wall: 屋根又は天井と壁の熱橋の温度差係数
    :type H_HB_roof_wall: float
    :return: 屋根又は天井と壁の熱橋の線熱貫流率
    :rtype: float
    """
    if house_structure_type == '鉄筋コンクリート造' or house_structure_type == '鉄骨造':
        if type(psi_HB_roof_wall) in [list, tuple]:
            return psi_HB_roof_wall[np.argmax(np.array(psi_HB_roof_wall) * np.array(H_HB_roof_wall))]
        else:
            return psi_HB_roof_wall
    else:
        return 0


def get_psi_HB_wall_wall(psi_HB_wall_wall, house_structure_type, H_HB_wall_wall=None):
    """ 9.9.17 壁と壁の熱橋の線熱貫流率

    :param psi_HB_wall_wall: 壁と壁の熱橋の線熱貫流率
    :type psi_HB_wall_wall: list, tuple or float
    :param house_structure_type: '木造'または'鉄筋コンクリート造'、'鉄骨造'
    :type house_structure_type: str
    :param H_HB_wall_wall: 壁と壁の熱橋の温度差係数
    :type H_HB_wall_wall: float
    :return: 壁と壁(出隅)の熱橋の線熱貫流率
    :rtype: float
    """
    if house_structure_type == '鉄筋コンクリート造' or house_structure_type == '鉄骨造':
        if type(psi_HB_wall_wall) in [list, tuple]:
            return psi_HB_wall_wall[np.argmax(np.array(psi_HB_wall_wall) * np.array(H_HB_wall_wall))]
        else:
            return psi_HB_wall_wall
    else:
        return 0


def get_psi_HB_wall_floor(psi_HB_wall_floor, house_structure_type, H_HB_wall_floor=None):
    """ 9.9.18 壁と床の熱橋の線熱貫流率

    :param psi_HB_wall_floor: 壁と床の熱橋の線熱貫流率
    :type psi_HB_wall_floor: list, tuple or float
    :param house_structure_type: '木造'または'鉄筋コンクリート造'、'鉄骨造'
    :type house_structure_type: str
    :param H_HB_wall_floor: 壁と床の熱橋の温度差係数
    :type H_HB_wall_floor: float
    :return: 壁と床の熱橋の線熱貫流率
    :rtype: float
    """
    if house_structure_type == '鉄筋コンクリート造' or house_structure_type == '鉄骨造':
        if type(psi_HB_wall_floor) in [list, tuple]:
            return psi_HB_wall_floor[np.argmax(np.array(psi_HB_wall_floor) * np.array(H_HB_wall_floor))]
        else:
            return psi_HB_wall_floor
    else:
        return 0


# ============================================================================
# 9.10 外皮の部位の日射熱取得率
# ============================================================================

def calc_eta_H_roof(U_roof):
    """ 9.10.1 屋根又は天井の日射熱取得率(暖房期)

    :param U_roof: 屋根又は天井の熱貫流率
    :type U_roof: float
    :return: 屋根又は天井の日射熱取得率(暖房期)
    :rtype: float
    """

    return eater.common.get_eta_H_i(1.0, U_roof)


def calc_eta_C_roof(U_roof):
    """  9.10.1 屋根又は天井の日射熱取得率(冷房期)

    :param U_roof: 屋根又は天井の熱貫流率
    :type U_roof: float
    :return: 屋根又は天井の日射熱取得率(冷房期)
    :rtype: float
    """

    return eater.common.get_eta_C_i(1.0, U_roof)



def calc_eta_H_wall(U_wall):
    """ 9.10.2 壁の日射熱取得率(暖房期)

    :param U_wall: 壁の熱貫流率
    :type U_wall: float
    :return: 壁の日射熱取得率(暖房期)
    :rtype: float
    """

    return eater.common.get_eta_H_i(1.0, U_wall)


def calc_eta_C_wall(U_wall):
    """ 9.10.2 壁の日射熱取得率(冷房期)

    :param U_wall:
    :type U_wall:
    :return: 壁の日射熱取得率(冷房期)
    :rtype: float
    """

    return eater.common.get_eta_C_i(1.0, U_wall)


def calc_eta_H_door(U_door):
    """ 9.10.3 ドアの日射熱取得率(暖房期)

    :param U_door: ドアの熱貫流率
    :type U_door: float
    :return: ドアの日射熱取得率(暖房期)
    :rtype: float
    """

    return eater.door.get_eta_H_i(1.0, U_door)


def calc_eta_C_door(U_door):
    """ 9.10.3 ドアの日射熱取得率(冷房期)

    :param U_door: ドアの熱貫流率
    :type U_door: float
    :return: ドアの日射熱取得率(冷房期)
    :rtype: float
    """

    return eater.door.get_eta_C_i(1.0, U_door)


def calc_eta_H_window(region, etr_d, f_H=None):
    """ 9.10.4 窓の日射熱取得率(暖房期)

    :param region: 省エネルギー地域区分
    :type region: int
    :param etr_d: 暖房期の垂直面日射熱取得率 (-)
    :type etr_d: float
    :param f_H: 暖房期の取得日射熱補正係数 (-)
    :type f_H: float
    :return: 窓の日射熱取得率(暖房期)
    :rtype: tuple
    """

    #################################################
    ### HEESENV-66(2020/08/27)
    ## 9.10.4①に「ガラス区分を7、l1=0、l2=1/0.3として、地域の区分・方位に応じて」～とあるが、
    ## 現時点の3章4節付録Bの仕様書中にl1・l2やガラス区分の参照がなく、
    ## 取得日射熱補正係数を求める計算方法が不明。
    ## →暫定で、仕様変更前の計算方法を使用するが、計算方法が決まり次第修正が必要
    #################################################
    # 暖房期については、必ず（実際の有無に係わらず）「日よけあり」で評価する
    # 当該開口部の上部に日除けが設置されている場合の開口部の暖房期の取得日射熱補正係数
    if f_H is None:
        f1_H_0 = eater.f.shade.get_glass_f(region, 7, 0, 'H', '南西')
        f2_H_0 = eater.f.shade.get_glass_f(region, 7, 1 / 0.3, 'H', '南西')
        f_H_0 = eater.f.shade.get_f(f1_H_0, f2_H_0)

        f1_H_90 = eater.f.shade.get_glass_f(region, 7, 0, 'H', '北西')
        f2_H_90 = eater.f.shade.get_glass_f(region, 7, 1 / 0.3, 'H', '北西')
        f_H_90 = eater.f.shade.get_f(f1_H_90, f2_H_90)

        f1_H_180 = eater.f.shade.get_glass_f(region, 7, 0, 'H', '北東')
        f2_H_180 = eater.f.shade.get_glass_f(region, 7, 1 / 0.3, 'H', '北東')
        f_H_180 = eater.f.shade.get_f(f1_H_180, f2_H_180)

        f1_H_270 = eater.f.shade.get_glass_f(region, 7, 0, 'H', '南東')
        f2_H_270 = eater.f.shade.get_glass_f(region, 7, 1 / 0.3, 'H', '南東')
        f_H_270 = eater.f.shade.get_f(f1_H_270, f2_H_270)
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


def calc_eta_C_window(region, etr_d, f_C=None):
    """ 9.10.4 窓の日射熱取得率(冷房期)

    :param region: 省エネルギー地域区分
    :type region: int
    :param etr_d: 垂直面日射熱取得率 (-)
    :type etr_d: float
    :param f_C: 冷房期の取得日射熱補正係数 (-)
    :type f_C: float
    :return: 窓の日射熱取得率(冷房期)
    :rtype: tuple
    """

    #################################################
    ### HEESENV-66(2020/08/27)
    ## 暖房期の場合と同様（calc_eta_H_windowコメント参照）に、計算方法が決まり次第修正が必要
    #################################################
    # 当該開口部の上部に日除けが設置されていない場合の開口部の冷房期の取得日射熱補正係数
    if f_C is None:
        f_C_0 = eater.f.noshade.get_f_C_i_2(region, 1, '南西')
        f_C_90 = eater.f.noshade.get_f_C_i_2(region, 1, '北西')
        f_C_180 = eater.f.noshade.get_f_C_i_2(region, 1, '北東')
        f_C_270 = eater.f.noshade.get_f_C_i_2(region, 1, '南東')
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


def calc_eta_H_base_etrc(U_base_etrc):
    """ 9.10.5 玄関等の基礎の日射熱取得率(暖房期)

    :param U_base_etrc: 玄関等の基礎の熱貫流率
    :type U_base_etrc: float
    :return: 玄関等の基礎の日射熱取得率(暖房期)
    :rtype: float
    """

    return eater.common.get_eta_H_i(1.0, U_base_etrc)


def calc_eta_C_base_etrc(U_base_etrc):
    """ 9.10.5 玄関等の基礎の日射熱取得率(冷房期)

    :param U_base_etrc: 玄関等の基礎の熱貫流率
    :type U_base_etrc: float
    :return: 玄関等の基礎の日射熱取得率(冷房期)
    :rtype: float
    """

    return eater.common.get_eta_C_i(1.0, U_base_etrc)



def calc_eta_H_base_bath(U_base_bath):
    """ 9.10.6 浴室の基礎の日射熱取得率(暖房期)

    :param U_base_bath: 浴室の基礎の熱貫流率
    :type U_base_bath: float
    :return: 浴室の基礎の日射熱取得率(暖房期)
    :rtype: float
    """

    return eater.common.get_eta_H_i(1.0, U_base_bath)


def calc_eta_C_base_bath(U_base_bath):
    """ 9.10.6 浴室の基礎の日射熱取得率(冷房期)

    :param U_base_bath: 浴室の基礎の熱貫流率
    :type U_base_bath: float
    :return: 浴室の基礎の日射熱取得率(冷房期)
    :rtype:
    """
    return eater.common.get_eta_C_i(1.0, U_base_bath)


def calc_eta_H_base_other(U_base_other):
    """ 9.10.7 その他の基礎の日射熱取得率(暖房期)

    :param U_base_other: その他の基礎の熱貫流率
    :type U_base_other: float
    :return: その他の基礎の日射熱取得率(暖房期)
    :rtype: float
    """
    return eater.common.get_eta_H_i(1.0, U_base_other)


def calc_eta_C_base_other(U_base_other):
    """ 9.10.7 その他の基礎の日射熱取得率(冷房期)

    :param U_base_other: その他の基礎の熱貫流率
    :type U_base_other: float
    :return: その他の基礎の日射熱取得率(冷房期)
    :rtype: float
    """
    return eater.common.get_eta_C_i(1.0, U_base_other)


def calc_eta_dash_H_HB_roof(psi_HB_roof):
    """ 9.10.8 屋根又は天井の熱橋の日射熱取得率(暖房期)

    :param psi_HB_roof: 屋根または天井の熱橋の線熱貫流率
    :type psi_HB_roof: float
    :return: 屋根又は天井の熱橋の日射熱取得率(暖房期)
    :rtype: float
    """
    return eater.heatbridge.get_eta_dash_H_j(1.0, psi_HB_roof)


def calc_eta_dash_C_HB_roof(psi_HB_roof):
    """ 9.10.8 屋根又は天井の熱橋の日射熱取得率(冷房期)

    :param psi_HB_roof: 屋根または天井の熱橋の線熱貫流率
    :type psi_HB_roof: float
    :return: 屋根又は天井の熱橋の日射熱取得率(冷房期)
    :rtype: float
    """
    return eater.heatbridge.get_eta_dash_C_j(1.0, psi_HB_roof)


def calc_eta_dash_H_HB_wall(psi_HB_wall):
    """ 9.10.9 壁の熱橋の日射熱取得率(暖房期)

    :param psi_HB_wall: 屋根または天井の熱橋の線熱貫流率
    :type psi_HB_wall: float
    :return: 屋根又は天井の熱橋の日射熱取得率(暖房期)
    :rtype: float
    """
    return eater.heatbridge.get_eta_dash_H_j(1.0, psi_HB_wall)


def calc_eta_dash_C_HB_wall(psi_HB_wall):
    """ 9.10.9 壁の熱橋の日射熱取得率(冷房期)

    :param psi_HB_wall: 屋根または天井の熱橋の線熱貫流率
    :type psi_HB_wall: float
    :return: 屋根又は天井の熱橋の日射熱取得率(冷房期)
    :rtype: float
    """
    return eater.heatbridge.get_eta_dash_C_j(1.0, psi_HB_wall)


def calc_eta_dash_H_HB_floor(psi_HB_floor):
    """ 9.10.10 床の熱橋の日射熱取得率(暖房期)

    :param psi_HB_floor: 床の熱橋の線熱貫流率
    :type psi_HB_floor: float
    :return: 床の熱橋の日射熱取得率(暖房期)
    :rtype: float
    """
    return eater.heatbridge.get_eta_dash_H_j(1.0, psi_HB_floor)


def calc_eta_dash_C_HB_floor(psi_HB_floor):
    """ 9.10.10 床の熱橋の日射熱取得率(冷房期)

    :param psi_HB_floor: 床の熱橋の線熱貫流率
    :type psi_HB_floor: float
    :return: 床の熱橋の日射熱取得率    (冷房期)
    :rtype: float
    """
    return eater.heatbridge.get_eta_dash_C_j(1.0, psi_HB_floor)


def calc_eta_dash_H_HB_roof_wall(psi_HB_roof_wall):
    """ 9.10.11 屋根又は天井と壁の熱橋の日射熱取得率(暖房期)

    :param psi_HB_roof_wall: 屋根又は天井と壁の熱橋の線熱貫流率
    :type psi_HB_roof_wall: float
    :return: 屋根又は天井と壁の熱橋の日射熱取得率(暖房期)
    :rtype: float
    """
    return eater.heatbridge.get_eta_dash_H_j(1.0, psi_HB_roof_wall)


def calc_eta_dash_C_HB_roof_wall(psi_HB_roof_wall):
    """ 9.10.11 屋根又は天井と壁の熱橋の日射熱取得率(冷房期)

    :param psi_HB_roof_wall: 屋根又は天井と壁の熱橋の線熱貫流率
    :type psi_HB_roof_wall: float
    :return: 屋根又は天井と壁の熱橋の日射熱取得率(冷房期)
    :rtype: float
    """
    return eater.heatbridge.get_eta_dash_C_j(1.0, psi_HB_roof_wall)


def calc_eta_dash_H_HB_wall_wall(psi_HB_wall_wall):
    """ 9.10.12 壁と壁の熱橋の日射熱取得率(暖房期)

    :param psi_HB_wall_wall: 壁と壁の熱橋の日射熱取得率
    :type psi_HB_wall_wall: float
    :return: 壁と壁（出隅）の熱橋の日射熱取得率(暖房期)
    :rtype: float
    """
    return eater.heatbridge.get_eta_dash_H_j(1.0, psi_HB_wall_wall)


def calc_eta_dash_C_HB_wall_wall(psi_HB_wall_wall):
    """ 9.10.12 壁と壁の熱橋の日射熱取得率(暖房期)

    :param psi_HB_wall_wall: 壁と壁の熱橋の日射熱取得率
    :type psi_HB_wall_wall: float
    :return: 壁と壁（入隅）の熱橋の日射熱取得率(暖房期)
    :rtype: float
    """
    return eater.heatbridge.get_eta_dash_C_j(1.0, psi_HB_wall_wall)


def calc_eta_dash_H_HB_wall_floor(psi_HB_wall_floor):
    """ 9.10.13 壁と床の熱橋の日射熱取得率(暖房期)

    :param psi_HB_wall_floor: 壁と床の熱橋の日射熱取得率
    :type psi_HB_wall_floor: float
    :return: 壁と床の熱橋の日射熱取得率(暖房期)
    :rtype: float
    """
    return eater.heatbridge.get_eta_dash_H_j(1.0, psi_HB_wall_floor)


def calc_eta_dash_C_HB_wall_floor(psi_HB_wall_floor):
    """ 9.10.13 壁と床の熱橋の日射熱取得率(冷房期)

    :param psi_HB_wall_floor: 壁と床の熱橋の日射熱取得率
    :type psi_HB_wall_floor: float
    :return: 壁と床の熱橋の日射熱取得率(冷房期)
    :rtype: float
    """
    return eater.heatbridge.get_eta_dash_C_j(1.0, psi_HB_wall_floor)