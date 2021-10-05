# ============================================================================
# 第二章 単位住戸の一次エネルギー消費量
# 第二節 設計一次エネルギー消費量
# Ver.06（エネルギー消費性能計算プログラム（住宅版）Ver.0204～）
# ============================================================================

import numpy as np
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

from pyhees.section2_1_b import get_f_prim
from pyhees.section2_1_c import get_n_p
from pyhees.section4_1 import calc_heating_load, calc_heating_mode, get_virtual_heating_devices, get_virtual_heatsource, \
    get_E_E_H_d_t, get_E_G_H_d_t, calc_E_K_H_d_t, calc_E_M_H_d_t, calc_E_UT_H_d_t
from pyhees.section4_1 import calc_cooling_load, calc_E_E_C_d_t, calc_E_G_C_d_t, calc_E_K_C_d_t, calc_E_M_C_d_t, calc_E_UT_C_d_t
import pyhees.section4_2 as dc
import pyhees.section4_2_b as dc_spec
from pyhees.section5 import calc_E_E_V_d_t
from pyhees.section6 import calc_E_E_L_d_t
from pyhees.section7_1 import calc_hotwater_load, calc_E_E_W_d_t, calc_E_G_W_d_t, calc_E_K_W_d_t, get_E_M_W_d_t
from pyhees.section7_1_b import get_default_hw_type, get_virtual_hotwater
from pyhees.section8 import calc_E_G_CG_d_t, get_E_E_CG_gen_d_t, get_L_DHW_d, get_L_HWH_d, get_E_E_CG_self, get_E_E_TU_aux_d_t
from pyhees.section9_1 import calc_E_E_PV_d_t
from pyhees.section10 import calc_E_E_AP_d_t, get_E_G_AP_d_t, get_E_K_AP_d_t, get_E_M_AP_d_t
from pyhees.section10 import get_E_E_CC_d_t, calc_E_G_CC_d_t, get_E_K_CC_d_t, get_E_M_CC_d_t
from pyhees.section11_1 import load_outdoor


# ============================================================================
# 5. 設計一次エネルギー消費量
# ============================================================================

def get_E_T_star(E_H, E_C, E_V, E_L, E_W, E_S, E_M):
    """ 1 年当たりの設計一次エネルギー消費量（MJ/年）
    
    :param E_H: 1 年当たりの暖房設備の設計一次エネルギー消費量（MJ/年）
    :type E_H: float
    :param E_C: 1 年当たりの冷房設備の設計一次エネルギー消費量
    :type E_C: float
    :param E_V: 1 年当たりの機械換気設備の設計一次エネルギー消費量
    :type E_V: float
    :param E_L: 1 年当たりの照明設備の設計一次エネルギー消費量
    :type E_L: float
    :param E_W: 1 年当たりの給湯設備（コージェネレーション設備を含む）の設計一次エネルギー消費量
    :type E_W: float
    :param E_S: 1 年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量
    :type E_S: float
    :param E_M: 1 年当たりのその他の設計一次エネルギー消費量
    :type E_M: float
    :return: 1 年当たりの設計一次エネルギー消費量（MJ/年）
    :rtype: float
    """
    return E_H + E_C + E_V + E_L + E_W - E_S + E_M  # (1)


# ============================================================================
# 6. 暖房設備の設計一次エネルギー消費量
# ============================================================================

def calc_E_H(region, sol_region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_H, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, CG, SHC,
            heating_flag_d, L_T_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i):
    """ 1 年当たりの暖房設備の設計一次エネルギー消費量（MJ/年）

    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param mode_H: 暖房方式
    :type mode_H: str
    :param H_A: 暖房方式
    :type H_A: dict
    :param spec_MR: 暖房機器の仕様
    :type spec_MR: dict
    :param spec_OR: 暖房機器の仕様
    :type spec_OR: dict
    :param spec_HS: 温水暖房機の仕様
    :type spec_HS: dict
    :param mode_MR: 主たる居室の運転方法 (連続運転|間歇運転)
    :type mode_MR: str
    :param mode_OR: その他の居室の運転方法 (連続運転|間歇運転)
    :type mode_OR: str
    :param CG: コージェネレーションの機器
    :type CG: dict
    :param SHC: 集熱式太陽熱利用設備の仕様
    :type SHC: dict
    :param heating_flag_d: 暖房日
    :type heating_flag_d: ndarray
    :param L_H_A_d_t: 暖房負荷
    :type L_H_A_d_t: ndarray
    :param L_T_H_d_t_i: 暖房区画i=1-5それぞれの暖房負荷
    :type L_T_H_d_t_i: ndarray
    :param L_CS_d_t_i: 暖冷房区画iの 1 時間当たりの冷房顕熱負荷
    :type L_CS_d_t_i: ndarray
    :param L_CL_d_t_i: 暖冷房区画iの 1 時間当たりの冷房潜熱負荷
    :type L_CL_d_t_i: ndarray
    :return: 1 年当たりの暖房設備の設計一次エネルギー消費量（MJ/年）
    :rtype: float
    """
    if region == 8:
        return 0.0
    elif mode_H is not None:
        E_H_d_t = get_E_H_d_t(region, sol_region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_H, H_A, spec_MR, spec_OR, spec_HS, mode_MR,
                              mode_OR, CG, SHC, heating_flag_d, L_T_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i)  # (2)

        E_H = np.sum(E_H_d_t)

        return E_H
    else:
        return 0.0


# 1 時間当たりの暖房設備の設計一次エネルギー消費量
def get_E_H_d_t(region, sol_region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_H, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, CG, SHC,
                heating_flag_d, L_T_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i):
    """1 時間当たりの暖房設備の設計一次エネルギー消費量

    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param mode_H: 暖房方式
    :type mode_H: str
    :param H_A: 暖房方式
    :type H_A: dict
    :param spec_MR: 暖房機器の仕様
    :type spec_MR: dict
    :param spec_OR: 暖房機器の仕様
    :type spec_OR: dict
    :param spec_HS: 温水暖房機の仕様
    :type spec_HS: dict
    :param mode_MR: 主たる居室の運転方法 (連続運転|間歇運転)
    :type mode_MR: str
    :param mode_OR: その他の居室の運転方法 (連続運転|間歇運転)
    :type mode_OR: str
    :param CG: コージェネレーションの機器
    :type CG: dict
    :param SHC: 集熱式太陽熱利用設備の仕様
    :type SHC: dict
    :param heating_flag_d: 暖房日
    :type heating_flag_d: ndarray
    :param L_H_A_d_t: 暖房負荷
    :type L_H_A_d_t: ndarray
    :param L_T_H_d_t_i: 暖房区画i=1-5それぞれの暖房負荷
    :type L_T_H_d_t_i: ndarray
    :param L_CS_d_t_i: 暖冷房区画iの 1 時間当たりの冷房顕熱負荷
    :type L_CS_d_t_i: ndarray
    :param L_CL_d_t_i: 暖冷房区画iの 1 時間当たりの冷房潜熱負荷
    :type L_CL_d_t_i: ndarray
    :return: 1 時間当たりの暖房設備の設計一次エネルギー消費量
    :rtype: ndarray
    """
    if region == 8:
        return 0.0
    else:
        # 電気の量 1kWh を熱量に換算する係数
        f_prim = get_f_prim()

        # 暖房設備の消費電力量（kWh/h）(6a)
        E_E_H_d_t = get_E_E_H_d_t(region, sol_region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, H_A, spec_MR, spec_OR, spec_HS,
                                  mode_MR, mode_OR, CG, SHC, heating_flag_d, L_T_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i)

        # 暖房設備のガス消費量（MJ/h）(6b)
        E_G_H_d_t = get_E_G_H_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, CG,
                                  L_T_H_d_t_i)

        # 暖房設備の灯油消費量（MJ/h）(6c)
        E_K_H_d_t = calc_E_K_H_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, CG,
                                   L_T_H_d_t_i)

        # 暖房設備のその他の燃料による一次エネルギー消費量（MJ/h）(6d)
        E_M_H_d_t = calc_E_M_H_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, L_T_H_d_t_i)

        # 暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値
        E_UT_H_d_t = calc_E_UT_H_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_H, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR,
                                     CG, L_T_H_d_t_i, L_CS_d_t_i, L_CL_d_t_i)

        return E_E_H_d_t * f_prim / 1000 + E_G_H_d_t + E_K_H_d_t + E_M_H_d_t + E_UT_H_d_t  # (3)


# ============================================================================
# 7. 冷房設備の設計一次エネルギー消費量
# ============================================================================

def calc_E_C(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_H_d_t, L_CS_d_t, L_CL_d_t, mode_C):
    """1 年当たりの冷房設備の設計一次エネルギー消費量

    :param region: 省エネルギー地域区分
    :type region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param C_A: 冷房方式
    :type C_A: dict
    :param C_MR: 主たる居室の冷房機器
    :type C_MR: dict
    :param C_OR: その他の居室の冷房機器
    :type C_OR: dict
    :param L_CS_A_d_t: 冷房負荷
    :type L_CS_A_d_t: ndarray
    :param L_CL_A_d_t: 冷房負荷
    :type L_CL_A_d_t: ndarray
    :param L_CS_d_t_i: 暖冷房区画iの 1 時間当たりの冷房顕熱負荷
    :type L_CS_d_t_i: ndarray
    :param L_CL_d_t_i: 暖冷房区画iの 1 時間当たりの冷房潜熱負荷
    :type L_CL_d_t_i: ndarray
    :return: 1 年当たりの冷房設備の設計一次エネルギー消費量
    :rtype: float
    """
    # 1 時間当たりの冷房設備の設計一次エネルギー消費量 (4)
    E_C_d_t = get_E_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_H_d_t, L_CS_d_t, L_CL_d_t, mode_C)

    # 1 年当たりの冷房設備の設計一次エネルギー消費量
    E_C = np.sum(E_C_d_t)

    return E_C


def get_E_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_H_d_t, L_CS_d_t, L_CL_d_t, mode_C):
    """1 時間当たりの冷房設備の設計一次エネルギー消費量 (4)

    :param region: 省エネルギー地域区分
    :type region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param C_A: 冷房方式
    :type C_A: dict
    :param C_MR: 主たる居室の冷房機器
    :type C_MR: dict
    :param C_OR: その他の居室の冷房機器
    :type C_OR: dict
    :param L_CS_A_d_t: 冷房負荷
    :type L_CS_A_d_t: ndarray
    :param L_CL_A_d_t: 冷房負荷
    :type L_CL_A_d_t: ndarray
    :param L_CS_d_t_i: 暖冷房区画iの 1 時間当たりの冷房顕熱負荷
    :type L_CS_d_t_i: ndarray
    :param L_CL_d_t_i: 暖冷房区画iの 1 時間当たりの冷房潜熱負荷
    :type L_CL_d_t_i: ndarray
    :return: 1 時間当たりの冷房設備の設計一次エネルギー消費量 (4)
    :rtype: ndarray
    """
    # 電気の量 1kWh を熱量に換算する係数
    f_prim = get_f_prim()

    E_E_C_d_t = calc_E_E_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_H_d_t, L_CS_d_t, L_CL_d_t)
    E_G_C_d_t = calc_E_G_C_d_t()
    E_K_C_d_t = calc_E_K_C_d_t()
    E_M_C_d_t = calc_E_M_C_d_t()
    E_UT_C_d_t = calc_E_UT_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_H_d_t, L_CS_d_t, L_CL_d_t, mode_C)

    E_C_d_t = E_E_C_d_t * f_prim / 1000 + E_G_C_d_t + E_K_C_d_t + E_M_C_d_t + E_UT_C_d_t  # (5)

    return E_C_d_t


# ============================================================================
# 8. 機械換気設備の設計一次エネルギー消費量
# ============================================================================

def calc_E_V(A_A, V, HEX):
    """1 年当たりの機械換気設備の設計一次エネルギー消費量
    
    :param A_A: 床面積の合計[m^2]
    :type A_A: float
    :param V: 換気設備仕様辞書
    :type V: dict
    :param HEX: 熱交換器型設備仕様辞書
    :type HEX: dict
    :return: 1 年当たりの機械換気設備の設計一次エネルギー消費量
    :rtype: float
    """
    
    if V is None:
        return 0.0

    # 電気の量 1kWh を熱量に換算する係数
    f_prim = get_f_prim()

    n_p = get_n_p(A_A)

    E_E_V_d_t = calc_E_E_V_d_t(n_p, A_A, V, HEX)

    # (6)
    E_V = np.sum(E_E_V_d_t) * f_prim / 1000

    return E_V


# ============================================================================
# 9. 照明設備の設計一次エネルギー消費量
# ============================================================================

# 1 年当たりの照明設備の設計一次エネルギー消費量
def calc_E_L(A_A, A_MR, A_OR, L):
    """1 年当たりの照明設備の設計一次エネルギー消費量
    
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param L: 照明設備仕様辞書
    :type L: dict
    :return: 1 年当たりの照明設備の設計一次エネルギー消費量
    :rtype: ndarray
    """
    
    if L is None:
        return 0.0

    # 電気の量 1kWh を熱量に換算する係数
    f_prim = get_f_prim()

    n_p = get_n_p(A_A)

    E_E_L_d_t = calc_E_E_L_d_t(n_p, A_A, A_MR, A_OR, L)

    E_L = np.sum(E_E_L_d_t) * f_prim / 1000  # (7)

    return E_L


# ============================================================================
# 10. 給湯設備及びコージェネレーション設備の設計一次エネルギー消費量
# ============================================================================

# 1 年当たりの給湯設備（コージェネレーション設備を含む）の設計一次エネルギー消費量
def calc_E_W(A_A, region, sol_region, HW, SHC, CG, H_A=None, H_MR=None, H_OR=None, H_HS=None, C_A=None, C_MR=None,
            C_OR=None,
            V=None, L=None, A_MR=None, A_OR=None, A_env=None, Q=None, mu_H=None, mu_C=None, NV_MR=None, NV_OR=None, TS=None,
            r_A_ufvnt=None, HEX=None, underfloor_insulation=None, mode_H=None, mode_C=None):
    """ 1 年当たりの給湯設備（コージェネレーション設備を含む）の設計一次エネルギー消費量

    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param HW: 給湯機の仕様
    :type HW: dict
    :param SHC: 集熱式太陽熱利用設備の仕様
    :type SHC: dict
    :param CG: コージェネレーションの機器
    :type CG: dict
    :param H_A: 暖房方式, defaults to None
    :type H_A: dict, optional
    :param H_MR: 暖房機器の仕様, defaults to None
    :type H_MR: dict, optional
    :param H_OR: 暖房機器の仕様, defaults to None
    :type H_OR: dict, optional
    :param H_HS: 温水暖房機の仕様, defaults to None
    :type H_HS: dict, optional
    :param C_A: 冷房方式, defaults to None
    :type C_A: dict, optional
    :param C_MR: 主たる居室の冷房機器, defaults to None
    :type C_MR: dict, optional
    :param C_OR: その他の居室の冷房機器, defaults to None
    :type C_OR: dict, optional
    :param V: 換気設備仕様辞書, defaults to None
    :type V: dict, optional
    :param L: 照明設備仕様辞書, defaults to None
    :type L: dict, optional
    :param A_MR: 主たる居室の床面積 (m2), defaults to None
    :type A_MR: float, optional
    :param A_OR: その他の居室の床面積 (m2), defaults to None
    :type A_OR: float, optional
    :param Q: 当該住戸の熱損失係数 (W/m2K), defaults to None
    :type Q: float, optional
    :param mu_H: 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数, defaults to None
    :type mu_H: float, optional
    :param mu_C: 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数, defaults to None
    :type mu_C: float, optional
    :param NV_MR: 主たる居室における通風の利用における相当換気回数, defaults to None
    :type NV_MR: float, optional
    :param NV_OR: その他の居室における通風の利用における相当換気回数, defaults to None
    :type NV_OR: float, optional
    :param TS: 蓄熱, defaults to None
    :type TS: bool, optional
    :param r_A_ufvnt: 床下換気, defaults to None
    :type r_A_ufvnt: float, optional
    :param HEX: 熱交換器型設備仕様辞書, defaults to None
    :type HEX: dict, optional
    :param underfloor_insulation: 床下空間が断熱空間内である場合はTrue, defaults to None
    :type underfloor_insulation: bool, optional
    :param mode_H: 暖房方式, defaults to None
    :type mode_H: str, optional
    :param mode_C: 冷房方式, defaults to None
    :type mode_C: str, optional
    :return: 1 年当たりの給湯設備（コージェネレーション設備を含む）の設計一次エネルギー消費量
    :rtype: tuple
    """
    
    if HW is None:
        return 0.0, np.zeros(24 * 365), np.zeros(24 * 365), np.zeros(24 * 365), np.zeros(24 * 365), \
               np.zeros(24 * 365), np.zeros(24 * 365), np.zeros(24 * 365)

    if HW['hw_type'] != 'コージェネレーションを使用する':
        E_W_d = calc_E_W_d(A_A, region, sol_region, HW, SHC, H_HS, H_MR, H_OR, A_MR, A_OR, Q, mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX,
                          underfloor_insulation)

        # (8a)
        E_W = np.sum(E_W_d)

        return E_W, np.zeros(24 * 365), np.zeros(24 * 365), np.zeros(24 * 365), np.zeros(24 * 365), \
               np.zeros(24 * 365), np.zeros(24 * 365), np.zeros(24 * 365)
    else:
        # 1日当たりのコージェネレーション設備の一次エネルギー消費量
        E_G_CG_d_t, E_E_CG_gen_d_t, E_E_CG_h_d_t, E_E_TU_aux_d_t, E_E_CG_h_d_t, E_G_CG_ded, e_BB_ave, Q_CG_h = \
            calc_E_CG_d_t(A_A, region, sol_region, HW, SHC, CG, H_A, H_MR, H_OR, H_HS, C_A, C_MR, C_OR,
                          V, L, A_MR, A_OR, A_env, Q, mu_H, mu_C, NV_MR, NV_OR, TS,
                                             r_A_ufvnt, HEX, underfloor_insulation, mode_H, mode_C)

        # (8b)
        E_CG = np.sum(E_G_CG_d_t)

        return E_CG, E_E_CG_gen_d_t, E_E_CG_h_d_t, E_E_TU_aux_d_t, E_E_CG_h_d_t, E_G_CG_ded, e_BB_ave, Q_CG_h


# 1日当たりのコージェネレーション設備の一次エネルギー消費量
def calc_E_CG_d_t(A_A, region, sol_region, HW, SHC, CG, H_A=None, H_MR=None, H_OR=None, H_HS=None, C_A=None, C_MR=None,
                C_OR=None,
                V=None, L=None, A_MR=None, A_OR=None, A_env=None, Q=None, mu_H=None, mu_C=None, NV_MR=None, NV_OR=None, TS=None,
                r_A_ufvnt=None, HEX=None, underfloor_insulation=None, mode_H=None, mode_C=None):
    """1時間当たりのコージェネレーション設備の一次エネルギー消費量
    
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param HW: 給湯機の仕様
    :type HW: dict
    :param SHC: 集熱式太陽熱利用設備の仕様
    :type SHC: dict
    :param CG: コージェネレーションの機器
    :type CG: dict
    :param H_A: 暖房方式, defaults to None
    :type H_A: dict, optional
    :param H_MR: 暖房機器の仕様, defaults to None
    :type H_MR: dict, optional
    :param H_OR: 暖房機器の仕様, defaults to None
    :type H_OR: dict, optional
    :param H_HS: 温水暖房機の仕様, defaults to None
    :type H_HS: dict, optional
    :param C_A: 冷房方式, defaults to None
    :type C_A: dict, optional
    :param C_MR: 主たる居室の冷房機器, defaults to None
    :type C_MR: dict, optional
    :param C_OR: その他の居室の冷房機器, defaults to None
    :type C_OR: dict, optional
    :param V: 換気設備仕様辞書, defaults to None
    :type V: dict, optional
    :param L: 照明設備仕様辞書, defaults to None
    :type L: dict, optional
    :param A_MR: 主たる居室の床面積 (m2), defaults to None
    :type A_MR: float, optional
    :param A_OR: その他の居室の床面積 (m2), defaults to None
    :type A_OR: float, optional
    :param Q: 当該住戸の熱損失係数 (W/m2K), defaults to None
    :type Q: float, optional
    :param mu_H: 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数, defaults to None
    :type mu_H: float, optional
    :param mu_C: 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数, defaults to None
    :type mu_C: float, optional
    :param NV_MR: 主たる居室における通風の利用における相当換気回数, defaults to None
    :type NV_MR: float, optional
    :param NV_OR: その他の居室における通風の利用における相当換気回数, defaults to None
    :type NV_OR: float, optional
    :param TS: 蓄熱, defaults to None
    :type TS: bool, optional
    :param r_A_ufvnt: 床下換気, defaults to None
    :type r_A_ufvnt: float, optional
    :param HEX: 熱交換器型設備仕様辞書, defaults to None
    :type HEX: dict, optional
    :param underfloor_insulation: 床下空間が断熱空間内である場合はTrue, defaults to None
    :type underfloor_insulation: bool, optional
    :param mode_H: 暖房方式, defaults to None
    :type mode_H: str, optional
    :param mode_C: 冷房方式, defaults to None
    :type mode_C: str, optional
    :raises ValueError: SHC の type が "液体集熱式"、 "空気集熱式"　以外の場合に発生する 　
    :return: 1時間当たりのコージェネレーション設備の一次エネルギー消費量
    :rtype: tuple
    """
    
    if HW is None or HW['hw_type'] != 'コージェネレーションを使用する':
        return np.zeros(365), np.zeros(24 * 365), None, None, None, None, None, None

    n_p = get_n_p(A_A)

    # 実質的な暖房機器の仕様を取得
    spec_MR, spec_OR = get_virtual_heating_devices(region, H_MR, H_OR)

    # 実質的な温水暖房機の仕様を取得
    spec_HS = get_virtual_heatsource(region, H_HS)

    # 暖房方式及び運転方法の区分
    mode_MR, mode_OR = calc_heating_mode(region=region, H_MR=spec_MR, H_OR=spec_OR)

    # 暖房負荷の取得
    L_T_H_d_t_i, L_dash_H_R_d_t_i = calc_heating_load(
        region, sol_region,
        A_A, A_MR, A_OR,
        Q, mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX,
        underfloor_insulation, mode_H, mode_C,
        spec_MR, spec_OR, mode_MR, mode_OR, SHC)

    # 暖房日の計算
    if SHC is not None and SHC['type'] == '空気集熱式':
        # import section4_1 as H
        # L_T_H_d_t_i, L_dash_H_R_d_t_i = H.calc_L_H_d_t(region, sol_region, A_A, A_MR, A_OR, None, spec_MR, spec_OR,
        #                                               mode_MR, mode_OR, Q, mu_H, TS, r_A_ufvnt, HEX, SHC,
        #                                               underfloor_insulation)
        #
        from pyhees.section3_1_heatingday import get_heating_flag_d

        heating_flag_d = get_heating_flag_d(L_dash_H_R_d_t_i)
    else:
        heating_flag_d = None

    # 暖房
    E_E_H_d_t = get_E_E_H_d_t(region, sol_region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR,
                              CG, SHC, heating_flag_d, L_T_H_d_t_i)
    # 冷房負荷の計算
    L_CS_d_t, L_CL_d_t = \
        calc_cooling_load(region, A_A, A_MR, A_OR, Q, mu_H, mu_C,
                          NV_MR, NV_OR, r_A_ufvnt, underfloor_insulation,
                          mode_C, mode_H, mode_MR, mode_OR, TS, HEX)

    # 冷房
    E_E_C_d_t = calc_E_E_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR,
                               L_T_H_d_t_i, L_CS_d_t, L_CL_d_t)

    # 換気
    E_E_V_d_t = calc_E_E_V_d_t(n_p, A_A, V)

    # 照明
    E_E_L_d_t = calc_E_E_L_d_t(n_p, A_A, A_MR, A_OR, L)

    # 家電
    E_E_AP_d_t = calc_E_E_AP_d_t(n_p)

    # その他または設置しない場合
    spec_HW = get_virtual_hotwater(region, HW)

    if spec_HW['hw_type'] is not None:
        from pyhees.section7_1 import get_normalized_bath_function
        # ふろ機能の修正
        bath_function = get_normalized_bath_function(spec_HW['hw_type'], spec_HW['bath_function'])

        # 給湯負荷の生成
        args = {
            'n_p': n_p,
            'region': region,
            'sol_region': sol_region,
            'has_bath': spec_HW['has_bath'],
            'bath_function': bath_function,
            'pipe_diameter': spec_HW['pipe_diameter'],
            'kitchen_watersaving_A': spec_HW['kitchen_watersaving_A'],
            'kitchen_watersaving_C': spec_HW['kitchen_watersaving_C'],
            'shower_watersaving_A': spec_HW['shower_watersaving_A'],
            'shower_watersaving_B': spec_HW['shower_watersaving_B'],
            'washbowl_watersaving_C': spec_HW['washbowl_watersaving_C'],
            'bath_insulation': spec_HW['bath_insulation']
        }
        if SHC is not None:
            if SHC['type'] == '液体集熱式':
                args.update({
                    'type': SHC['type'],
                    'ls_type': SHC['ls_type'],
                    'A_sp': SHC['A_sp'],
                    'P_alpha_sp': SHC['P_alpha_sp'],
                    'P_beta_sp': SHC['P_beta_sp'],
                    'W_tnk_ss': SHC['W_tnk_ss']
                })
            elif SHC['type'] == '空気集熱式':
                args.update({
                    'type': SHC['type'],
                    'hotwater_use': SHC['hotwater_use'],
                    'heating_flag_d': heating_flag_d,
                    'A_col': SHC['A_col'],
                    'P_alpha': SHC['P_alpha'],
                    'P_beta': SHC['P_beta'],
                    'V_fan_P0': SHC['V_fan_P0'],
                    'd0': SHC['d0'],
                    'd1': SHC['d1'],
                    'W_tnk_ass': SHC['W_tnk_ass']
                })
            else:
                raise ValueError(SHC['type'])

        hotwater_load = calc_hotwater_load(**args)

        L_dashdash_k_d_t = hotwater_load['L_dashdash_k_d_t']
        L_dashdash_s_d_t = hotwater_load['L_dashdash_s_d_t']
        L_dashdash_w_d_t = hotwater_load['L_dashdash_w_d_t']
        L_dashdash_b1_d_t = hotwater_load['L_dashdash_b1_d_t']
        L_dashdash_b2_d_t = hotwater_load['L_dashdash_b2_d_t']
        L_dashdash_ba1_d_t = hotwater_load['L_dashdash_ba1_d_t']
        L_dashdash_ba2_d_t = hotwater_load['L_dashdash_ba2_d_t']

    # 温水暖房負荷の計算
    if H_HS is not None:
        import pyhees.section4_1 as H
        from pyhees.section4_7 import calc_L_HWH

        # 実質的な暖房機器の仕様を取得
        spec_MR, spec_OR = H.get_virtual_heating_devices(region, H_MR, H_OR)

        # 暖房方式及び運転方法の区分
        mode_MR, mode_OR = H.calc_heating_mode(region=region, H_MR=spec_MR, H_OR=spec_OR)
        spec_HS = H.get_virtual_heatsource(region, H_HS)

        L_T_H_d_t_i, _ = H.calc_L_H_d_t(region, sol_region, A_A, A_MR, A_OR, None, None, spec_MR, spec_OR, mode_MR,
                                        mode_OR, Q, mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX, SHC, underfloor_insulation)
    else:
        spec_MR, spec_OR, spec_HS = None, None, None
        mode_MR, mode_OR = None, None
        L_T_H_d_t_i = None

    # 1時間当たりの給湯設備の消費電力量 (s7-1 1)
    E_E_W_d_t = calc_E_E_W_d_t(n_p, L_T_H_d_t_i, heating_flag_d, region, sol_region, HW, SHC)

    # 1時間当たりの電力需要 (28)
    E_E_dmd_d_t = get_E_E_dmd_d_t(E_E_H_d_t, E_E_C_d_t, E_E_V_d_t, E_E_L_d_t, E_E_W_d_t, E_E_AP_d_t)

    # 電力需要の結果
    print('## 電力需要')
    print('E_E_H  = {} [kWh/年]'.format(np.sum(E_E_H_d_t)))
    print('E_E_C  = {} [kWh/年]'.format(np.sum(E_E_C_d_t)))
    print('E_E_V  = {} [kWh/年]'.format(np.sum(E_E_V_d_t)))
    print('E_E_L  = {} [kWh/年]'.format(np.sum(E_E_L_d_t)))
    print('E_E_W  = {} [kWh/年]'.format(np.sum(E_E_W_d_t)))
    print('E_E_AP = {} [kWh/年]'.format(np.sum(E_E_AP_d_t)))
    print('Total  = {} [kWh/年]'.format(np.sum(E_E_H_d_t + E_E_C_d_t + E_E_V_d_t + E_E_L_d_t + E_E_AP_d_t)))

    # 1日当たりのコージェネレーション設備の一次エネルギー消費量
    E_G_CG_d_t, E_E_CG_gen_d_t, E_G_CG_ded, E_E_CG_self, Q_CG_h, E_E_TU_aux_d_t, e_BB_ave = \
        calc_E_G_CG_d_t(bath_function, CG, E_E_dmd_d_t,
                        L_dashdash_k_d_t, L_dashdash_w_d_t, L_dashdash_s_d_t, L_dashdash_b1_d_t,
                        L_dashdash_b2_d_t,
                        L_dashdash_ba1_d_t, L_dashdash_ba2_d_t,
                        spec_HS, spec_MR, spec_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR,
                        L_T_H_d_t_i)

    # 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h) (19-1)(19-2)
    E_E_CG_h_d_t = get_E_E_CG_h_d_t(E_E_CG_gen_d_t, E_E_dmd_d_t, True)

    return E_G_CG_d_t, E_E_CG_gen_d_t, E_E_CG_h_d_t, E_E_TU_aux_d_t, E_E_CG_h_d_t, E_G_CG_ded, e_BB_ave, Q_CG_h

# ============================================================================
# 10.1 給湯設備の設計一次エネルギー消費量
# ============================================================================

def calc_E_W_d(A_A, region, sol_region, HW, SHC, H_HS=None, H_MR=None, H_OR=None, A_MR=None, A_OR=None, Q=None, mu_H=None, mu_C=None, NV_MR=None, NV_OR=None, TS=None, r_A_ufvnt=None, HEX=None, underfloor_insulation=None):
    """1 日当たりの給湯設備の設計一次エネルギー消費量
    
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param HW: 給湯機の仕様
    :type HW: dict
    :param SHC: 集熱式太陽熱利用設備の仕様
    :type SHC: dict
    :param H_HS: 温水暖房機の仕様, defaults to None
    :type H_HS: dict, optional
    :param H_MR: 暖房機器の仕様, defaults to None
    :type H_MR: dict, optional
    :param H_OR: 暖房機器の仕様, defaults to None
    :type H_OR: dict, optional
    :param A_MR: 主たる居室の床面積 (m2), defaults to None
    :type A_MR: float, optional
    :param A_OR: その他の居室の床面積 (m2), defaults to None
    :type A_OR: float, optional
    :param Q: 当該住戸の熱損失係数 (W/m2K), defaults to None
    :type Q: float, optional
    :param mu_H: 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数, defaults to None
    :type mu_H: float, optional
    :param mu_C: 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数, defaults to None
    :type mu_C: float, optional
    :param NV_MR: 主たる居室における通風の利用における相当換気回数, defaults to None
    :type NV_MR: float, optional
    :param NV_OR: その他の居室における通風の利用における相当換気回数, defaults to None
    :type NV_OR: float, optional
    :param TS: 蓄熱, defaults to None
    :type TS: bool, optional
    :param r_A_ufvnt: 床下換気, defaults to None
    :type r_A_ufvnt: float, optional
    :param HEX: 熱交換器型設備仕様辞書, defaults to None
    :type HEX: dict, optional
    :param underfloor_insulation: 床下空間が断熱空間内である場合はTrue, defaults to None
    :type underfloor_insulation: bool, optional
    :raises ValueError: コージェネは対象外。HW の hw_type が 'コージェネレーションを使用する' であった場合発生する。
    :return: 1 日当たりの給湯設備の設計一次エネルギー消費量
    :rtype: ndarray
    """
    
    # コージェネは対象外
    if HW['hw_type'] == 'コージェネレーションを使用する':
        raise ValueError(HW['hw_type'])

    # 電気の量 1kWh を熱量に換算する係数
    f_prim = get_f_prim()

    # 想定人数
    n_p = get_n_p(A_A)

    # その他または設置しない場合
    spec_HW = get_virtual_hotwater(region, HW)

    # 温水暖房負荷の計算
    L_HWH = calc_L_HWH(A_A, A_MR, A_OR, HEX, H_HS, H_MR, H_OR, Q, SHC, TS, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt, region, sol_region,
                       underfloor_insulation)

    # 暖房日の計算
    heating_flag_d = calc_heating_flag_d(A_A, A_MR, A_OR, HEX, H_MR, H_OR, Q, SHC, TS, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt, region,
                                         sol_region, underfloor_insulation)

    E_E_W_d = calc_E_E_W_d_t(n_p, L_HWH, heating_flag_d, region, sol_region, spec_HW, SHC)
    E_G_W_d = calc_E_G_W_d_t(n_p, L_HWH, heating_flag_d, A_A, region, sol_region, spec_HW, SHC)
    E_K_W_d = calc_E_K_W_d_t(n_p, L_HWH, heating_flag_d, A_A, region, sol_region, spec_HW, SHC)
    E_M_W_d = get_E_M_W_d_t()

    print('E_E_W = {} [MJ]'.format(np.sum(E_E_W_d)))
    print('E_G_W = {} [MJ]'.format(np.sum(E_G_W_d)))
    print('E_K_W = {} [MJ]'.format(np.sum(E_K_W_d)))
    print('E_M_W = {} [MJ]'.format(np.sum(E_M_W_d)))

    E_W_d = E_E_W_d * f_prim / 1000 + E_G_W_d + E_K_W_d + E_M_W_d  # (9)

    return E_W_d


def calc_L_HWH(A_A, A_MR, A_OR, HEX, H_HS, H_MR, H_OR, Q, SHC, TS, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt, region, sol_region, underfloor_insulation, CG=None):
    """温水暖房負荷の計算
    
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param HEX: 熱交換器型設備仕様辞書
    :type HEX: dict
    :param H_HS: 温水暖房機の仕様
    :type H_HS: dict, optional
    :param H_MR: 暖房機器の仕様
    :type H_MR: dict
    :param H_OR: 暖房機器の仕様
    :type H_OR: dict
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param SHC: 集熱式太陽熱利用設備の仕様
    :type SHC: dict
    :param TS: 蓄熱
    :type TS: bool
    :param mu_H: 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数
    :type mu_H: float
    :param mu_C: 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数
    :type mu_C: float
    :param NV_MR: 主たる居室における通風の利用における相当換気回数
    :type NV_MR: float
    :param NV_OR: その他の居室における通風の利用における相当換気回数
    :type NV_OR: float
    :param r_A_ufvnt: 床下換気
    :type r_A_ufvnt: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param underfloor_insulation: 床下空間が断熱空間内である場合はTrue
    :type underfloor_insulation: bool
    :param CG: コージェネレーションの機器, defaults to None
    :type CG: dict, optional
    :return: 温水暖房負荷
    :rtype: float
    """
    
    if H_HS is not None:
        import pyhees.section4_1 as H
        from pyhees.section4_7 import calc_L_HWH
        # 実質的な暖房機器の仕様を取得
        spec_MR, spec_OR = H.get_virtual_heating_devices(region, H_MR, H_OR)

        # 暖房方式及び運転方法の区分
        mode_MR, mode_OR = H.calc_heating_mode(region=region, H_MR=spec_MR, H_OR=spec_OR)
        spec_HS = H.get_virtual_heatsource(region, H_HS)

        L_T_H_d_t_i, _ = H.calc_L_H_d_t(region, sol_region, A_A, A_MR, A_OR, None, None, spec_MR, spec_OR, mode_MR, mode_OR, Q,
                                        mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX, SHC, underfloor_insulation)

        L_HWH = calc_L_HWH(spec_HS, spec_MR, spec_OR, A_A, A_MR, A_OR, region, mode_MR, mode_OR, L_T_H_d_t_i, CG)
        L_HWH = np.sum(L_HWH.reshape(365, 24), axis=1)
    else:
        L_HWH = np.zeros(365)
    return L_HWH


def calc_heating_flag_d(A_A, A_MR, A_OR, HEX, H_MR, H_OR, Q, SHC, TS, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt, region, sol_region,underfloor_insulation):
    """暖房日の計算
    
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param HEX: 熱交換器型設備仕様辞書
    :type HEX: dict
    :param H_MR: 暖房機器の仕様
    :type H_MR: dict
    :param H_OR: 暖房機器の仕様
    :type H_OR: dict
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param SHC: 集熱式太陽熱利用設備の仕様
    :type SHC: dict
    :param TS: 蓄熱
    :type TS: bool
    :param mu_H: 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数
    :type mu_H: float
    :param mu_C: 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数
    :type mu_C: float
    :param NV_MR: 主たる居室における通風の利用における相当換気回数
    :type NV_MR: float
    :param NV_OR: その他の居室における通風の利用における相当換気回数
    :type NV_OR: float
    :param r_A_ufvnt: 床下換気
    :type r_A_ufvnt: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param underfloor_insulation: 床下空間が断熱空間内である場合はTrue
    :type underfloor_insulation: bool
    :return: 暖房日
    :rtype: ndarray
    """
    
    # 暖房日の計算
    if SHC is not None and SHC['type'] == '空気集熱式':
        import pyhees.section4_1 as H
        # 実質的な暖房機器の仕様を取得
        spec_MR, spec_OR = H.get_virtual_heating_devices(region, H_MR, H_OR)
        # 暖房方式及び運転方法の区分
        mode_MR, mode_OR = H.calc_heating_mode(region=region, H_MR=spec_MR, H_OR=spec_OR)

        L_T_H_d_t_i, L_dash_H_R_d_t_i = H.calc_L_H_d_t(region, sol_region, A_A, A_MR, A_OR, None, None, spec_MR, spec_OR, mode_MR, mode_OR, Q, mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX, SHC, underfloor_insulation)

        from pyhees.section3_1_heatingday import get_heating_flag_d
        heating_flag_d = get_heating_flag_d(L_dash_H_R_d_t_i)
    else:
        heating_flag_d = None
    return heating_flag_d


# ============================================================================
# 11. その他の設計一次エネルギー消費量
# ============================================================================

def calc_E_M(A_A):
    """1年当たりのその他の設計一次エネルギー消費量
    
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :return: 1年当たりのその他の設計一次エネルギー消費量
    :rtype: float
    """
    
    # 想定人数
    n_p = get_n_p(A_A)

    # 1 時間当たりの家電の設計一次エネルギー消費量
    E_AP_d_t = calc_E_AP_d_t(n_p)

    # 1 時間当たりの調理の設計一次エネルギー消費量
    E_CC_d_t = calc_E_CC_d_t(n_p)

    # 1年当たりのその他の設計一次エネルギー消費量
    E_M = np.sum(E_AP_d_t + E_CC_d_t)  # (11)

    return E_M


# ============================================================================
# 11.1 家電の設計一次エネルギー消費量
# ============================================================================

def calc_E_AP_d_t(n_p):
    """1 時間当たりの家電の設計一次エネルギー消費量
    
    :param n_p: 想定人数
    :type n_p: float
    :return: 1 時間当たりの家電の設計一次エネルギー消費量
    :rtype: ndarray
    """
    
    # 電気の量 1kWh を熱量に換算する係数
    f_prim = get_f_prim()
    return calc_E_E_AP_d_t(n_p) * f_prim / 1000 + get_E_G_AP_d_t() + get_E_K_AP_d_t() + get_E_M_AP_d_t()  # (12)


# ============================================================================
# 11.2 調理の設計一次エネルギー消費量
# ============================================================================

def calc_E_CC_d_t(n_p):
    """1 時間当たりの調理の設計一次エネルギー消費量
    
    :param n_p: 想定人数
    :type n_p: float
    :return: 1 時間当たりの調理の設計一次エネルギー消費量
    :rtype: ndarray
    """
    
    # 電気の量 1kWh を熱量に換算する係数
    f_prim = get_f_prim()

    return get_E_E_CC_d_t() * f_prim / 1000 + calc_E_G_CC_d_t(n_p) + get_E_K_CC_d_t() + get_E_M_CC_d_t()  # (13)


# ============================================================================
# 12. エネルギー利用効率化設備による設計一次エネルギー消費量の削減量
# ============================================================================

def calc_E_S(region, sol_region, PV, CG, E_E_dmd_d_t, E_E_CG_gen_d_t, E_E_TU_aux_d_t, E_E_CG_h, E_G_CG_ded, e_BB_ave, Q_CG_h):
    """1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (14)
    
    :param region: [description]
    :type region: [type]
    :param sol_region: [description]
    :type sol_region: [type]
    :param PV: [description]
    :type PV: [type]
    :param CG: [description]
    :type CG: [type]
    :param E_E_dmd_d_t: 1時間当たりの太陽光発電設備による発電量 (kWh/h)
    :type E_E_dmd_d_t: ndarray
    :param E_E_CG_gen_d_t: 1時間当たりのコージェネレーション設備による発電のうちの自家消費分 (kWh/h)
    :type E_E_CG_gen_d_t: ndarray
    :param E_E_TU_aux_d_t: 1時間当たりのタンクユニットの補機消費電力量 (25)
    :type E_E_TU_aux_d_t: ndarray
    :param E_E_CG_h: 1年当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/yr) (18)
    :type E_E_CG_h: float
    :param E_G_CG_ded: 1年当たりのコージェネレーション設備のガス消費量のうちの売電に係る控除対象分 (MJ/yr)
    :type E_G_CG_ded: float
    :param e_BB_ave: コージェネレーション設備の給湯時のバックアップボイラーの年間平均効率 (-)
    :type e_BB_ave: float
    :param Q_CG_h: 1年当たりのコージェネレーション設備による製造熱量のうちの自家消費算入分 (MJ/yr)
    :type Q_CG_h: float
    :return: 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (14)
    :rtype: float
    """

    if CG is not None:
        has_CG = True
        has_CG_reverse = CG["reverse"] if 'reverse' in CG else False
    else:
        has_CG = False
        has_CG_reverse = False

    if PV is not None:
        has_PV = True
        from pyhees.section11_2 import load_solrad
        from pyhees.section9_1 import calc_E_E_PV_d_t
        solrad = load_solrad(region, sol_region)
        # 太陽光発電設備の発電量 (s9-1 1)
        E_E_PV_d_t = calc_E_E_PV_d_t(PV, solrad)
    else:
        has_PV = False
        E_E_PV_d_t = np.zeros(24 * 365)

    # 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h) (19-1)(19-2)
    E_E_CG_h_d_t = get_E_E_CG_h_d_t(E_E_CG_gen_d_t, E_E_dmd_d_t, has_CG)

    # 1 時間当たりの太陽光発電設備による消費電力削減量 (17-1)(17-2)
    E_E_PV_h_d_t = get_E_E_PV_h_d_t(E_E_PV_d_t, E_E_dmd_d_t, E_E_CG_h_d_t, has_PV)

    # 1時間当たりのコージェネレーション設備による売電量(二次エネルギー) (kWh/h) (24-1)(24-2)
    E_E_CG_sell_d_t = get_E_E_CG_sell_d_t(E_E_CG_gen_d_t, E_E_CG_h_d_t, has_CG_reverse)

    # 1年当たりのコージェネレーション設備による売電量（一次エネルギー換算値）(MJ/yr) (23)
    E_CG_sell = calc_E_CG_sell(E_E_CG_sell_d_t)

    # 1年当たりのコージェネレーション設備による発電量のうちの自己消費分 (kWH/yr) (s8 4)
    E_E_CG_self = get_E_E_CG_self(E_E_TU_aux_d_t)

    # 1年当たりのコージェネレーション設備による売電量に係るガス消費量の控除量 (MJ/yr) (20)
    E_G_CG_sell = calc_E_G_CG_sell(E_CG_sell, E_E_CG_self, E_E_CG_h, E_G_CG_ded, e_BB_ave, Q_CG_h, CG != None)

    # 1年当たりのコージェネレーション設備の売電量に係る設計一次エネルギー消費量の控除量 (MJ/yr) (16)
    E_S_sell = get_E_S_sell(E_G_CG_sell)

    # 1年当たりのエネルギー利用効率化設備による発電量のうちの自家消費分に係る一次エネルギー消費量の控除量 (MJ/yr) (15)
    E_S_h = calc_E_S_h(E_E_PV_h_d_t, E_E_CG_h_d_t)

    # 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/yr) (14)
    E_S = get_E_S(E_S_h, E_S_sell)

    return E_S


def get_E_S(E_S_h, E_S_sell):
    """1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/yr) (14)
    
    :param E_S_h: 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/yr)
    :type E_S_h: float
    :param E_S_sell: 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/yr)
    :type E_S_sell: float
    :return: 1年当たりのエネルギー利用効率化設備による設計一次エネルギー消費量の削減量 (MJ/yr) (14)
    :rtype: float
    """
    
    return E_S_h + E_S_sell


def calc_E_S_h(E_E_PV_h_d_t, E_E_CG_h_d_t):
    """1年当たりのエネルギー利用効率化設備による発電量のうちの自家消費分に係る一次エネルギー消費量の控除量 (MJ/yr) (15)
    
    :param E_E_PV_h_d_t: 1時間当たりの太陽光発電設備による発電量のうちの自家消費分 (kWh/h)
    :type E_E_PV_h_d_t: ndarray
    :param E_E_CG_h_d_t: 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h)
    :type E_E_CG_h_d_t: ndarray
    :return: 1年あたりのエネルギー利用効率化設備による発電量のうちの自家消費分に係る一次エネルギー消費量の控除量 (MJ/yr)
    :rtype: float
    """
    
    # 電気の量 1kWh を熱量に換算する係数 (kJ/kWh)
    f_prim = get_f_prim()

    # 1年あたりのエネルギー利用効率化設備による発電量のうちの自家消費分に係る一次エネルギー消費量の控除量 (MJ/yr)
    E_S_h = np.sum(E_E_PV_h_d_t + E_E_CG_h_d_t) * f_prim * 1e-3

    return E_S_h


def get_E_S_sell(E_G_CG_sell):
    """1年当たりのコージェネレーション設備の売電量に係る設計一次エネルギー消費量の控除量 (MJ/yr) (16)
    
    :param E_G_CG_sell: 1年当たりのコージェネレーション設備の売電量に係る設計一次エネルギー消費量の控除量 (MJ/yr)
    :type E_G_CG_sell: float
    :return: 1年当たりのコージェネレーション設備の売電量に係る設計一次エネルギー消費量の控除量 (MJ/yr
    :rtype: float
    """
    
    return E_G_CG_sell


# ============================================================================
# 12.1 太陽光発電設備による発電量のうちの自家消費分
# ============================================================================


def get_E_E_PV_h_d_t(E_E_PV_d_t, E_E_dmd_d_t, E_E_CG_h_d_t, has_PV):
    """1 時間当たりの太陽光発電設備による発電炉湯のうちの自家消費分 (kWh/h) (17-1)(17-2)
    
    :param E_E_PV_d_t: 1時間当たりの太陽光発電設備による発電量のうちの自家消費分 (kWh/h)
    :type E_E_PV_d_t: ndarray
    :param E_E_dmd_d_t: 1時間当たりの太陽光発電設備による発電量 (kWh/h)
    :type E_E_dmd_d_t: ndarray
    :param E_E_CG_h_d_t: 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h)
    :type E_E_CG_h_d_t: ndarray
    :param has_PV: 太陽光発電設備を採用する場合はTrue
    :type has_PV: bool
    :return: 1 時間当たりの太陽光発電設備による発電炉湯のうちの自家消費分 (kWh/h)
    :rtype: float
    """
    
    if has_PV == False:
        # 太陽光発電設備を採用しない場合 (17-1)
        E_E_PV_h_d_t = np.zeros_like(E_E_PV_d_t)
    else:
        # 太陽光発電設備を採用する場合 (17-2)
        E_E_PV_h_d_t = np.minimum(E_E_PV_d_t, E_E_dmd_d_t - E_E_CG_h_d_t)

    return E_E_PV_h_d_t


# ============================================================================
# 12.2 コージェネレーション設備による発電量
# ============================================================================

def get_E_E_CG_h(E_E_CG_h_d_t):
    """1年当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/yr) (18)
    
    :param E_E_CG_h_d_t: 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h)
    :type E_E_CG_h_d_t: ndarray
    :return: 1年当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/yr)
    :rtype: float
    """
    
    return np.sum(E_E_CG_h_d_t)


# 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h) (19-1)(19-2)
def get_E_E_CG_h_d_t(E_E_CG_gen_d_t, E_E_dmd_d_t, has_CG):
    """1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h) (19-1)(19-2)
    
    :param E_E_CG_gen_d_t: 1時間当たりのコージェネレーション設備による発電のうちの自家消費分 (kWh/h)
    :type E_E_CG_gen_d_t: ndarray
    :param E_E_dmd_d_t: 1時間当たりの電力需要 (kWh/h)
    :type E_E_dmd_d_t: ndarray
    :param has_CG: [description]
    :type has_CG: bool
    :return: 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h)
    :rtype: ndarray
    """

    if has_CG == False:
        # コージェネレーション設備を採用しない場合 (19-1)
        E_E_CG_h_d_t = np.zeros_like(E_E_CG_gen_d_t)
    else:
        # コージェネレーション設備を採用する場合 (19-2)
        E_E_CG_h_d_t = np.minimum(E_E_CG_gen_d_t, E_E_dmd_d_t)
    return E_E_CG_h_d_t


# ============================================================================
# 12.3 コージェネレーション設備による売電量に係るガス消費量の控除量
# ============================================================================


def calc_E_G_CG_sell(E_CG_sell, E_E_CG_self, E_E_CG_h, E_G_CG_ded, e_BB_ave, Q_CG_h, has_CG):
    """1年当たりのコージェネレーション設備による売電量に係るガス消費量の控除量 (MJ/yr) (20)
    
    :param E_CG_sell: 1年当たりのコージェネレーション設備による売電量(一次エネルギー換算値) (MJ/yr)
    :type E_CG_sell: float
    :param E_E_CG_self: 1年当たりのコージェネレーション設備による発電量のうちの自己消費分 (kWh/yr)
    :type E_E_CG_self: float
    :param E_E_CG_h: 1年当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/yr)
    :type E_E_CG_h: float
    :param E_G_CG_ded: 1年当たりのコージェネレーション設備のガス消費量のうちの売電に係る控除対象分 (MJ/yr)
    :type E_G_CG_ded: float
    :param e_BB_ave: コージェネレーション設備の給湯時のバックアップボイラーの年間平均効率 (-)
    :type e_BB_ave: float
    :param Q_CG_h: 1年当たりのコージェネレーション設備による製造熱量のうちの自家消費算入分 (MJ/yr)
    :type Q_CG_h: float
    :param has_CG: コージェネレーション設備を採用する場合はTrue
    :type has_CG: bool
    :return: 1年当たりのコージェネレーション設備による売電量に係るガス消費量の控除量 (MJ/yr)
    :rtype: float
    """
    
    if has_CG == False:
        # コージェネレーション設備を採用しない場合 (20-1)
        E_E_CG_d_t = np.zeros_like(E_CG_sell)
    else:
        # 電気の量 1kWh を熱量に換算する係数
        f_prim = get_f_prim()

        # コージェネレーション設備を採用する場合 (20-2)
        denominator = E_CG_sell + (E_E_CG_self + E_E_CG_h) * f_prim * 1e-3 + Q_CG_h / e_BB_ave
        E_E_CG_d_t = E_G_CG_ded * (E_CG_sell / denominator)

    return E_E_CG_d_t


# ============================================================================
# 12.4 太陽光発電設備による売電量（参考）
# ============================================================================

# 1 年当たりの太陽光発電設備による売電量（一次エネルギー換算値） (21)
def calc_E_PV_sell():
    """ 1 年当たりの太陽光発電設備による売電量（一次エネルギー換算値） (21)
    
    :return: 1 年当たりの太陽光発電設備による売電量（一次エネルギー換算値）(MJ/yr)
    :rtype: float
    """

    # 電気の量 1kWh を熱量に換算する係数 (kJ/kWh) (s2-1-b)
    f_prim = get_f_prim()

    # 1 時間当たりの太陽光発電設備による売電量（二次エネルギー）(kWh/h) (22)
    E_E_PV_sell_d_t = calc_E_E_PV_sell_d_t()

    # 1 年当たりの太陽光発電設備による売電量（一次エネルギー換算値）(MJ/yr) (21)
    E_PV_sell = np.sum(E_E_PV_sell_d_t) * f_prim * 1e-3

    return E_PV_sell


# 1 時間当たりの太陽光発電設備による売電量（二次エネルギー）(kWh/h) (22)
def calc_E_E_PV_sell_d_t():
    """1 時間当たりの太陽光発電設備による売電量（二次エネルギー）(kWh/h) (22)
    
    :return: 1 時間当たりの太陽光発電設備による売電量（二次エネルギー）(kWh/h)
    :rtype: float
    """

    # 太陽光発電設備の発電量 (s9-1 1)
    E_E_PV_d_t = calc_E_E_PV_d_t()

    # 1 時間当たりの太陽光発電設備による発電炉湯のうちの自家消費分 (kWh/h) (17-1)(17-2)
    E_E_PV_h_d_t = get_E_E_PV_h_d_t()

    # 1 時間当たりの太陽光発電設備による売電量（二次エネルギー）(kWh/h) (22)
    E_E_PV_sell_d_t = E_E_PV_d_t - E_E_PV_h_d_t

    return E_E_PV_sell_d_t


# ============================================================================
# 12.5 コージェネレーション設備による売電量（参考）
# ============================================================================

def calc_E_CG_sell(E_E_CG_sell_d_t):
    """1年当たりのコージェネレーション設備による売電量（一次エネルギー換算値）(MJ/yr) (23)
    
    :param E_E_CG_sell_d_t: 1時間当たりのコージェネレーション設備による売電量(二次エネルギー) (kWh/h)
    :type E_E_CG_sell_d_t: ndarray
    :return: 1年当たりのコージェネレーション設備による売電量（一次エネルギー換算値）(MJ/yr)
    :rtype: float
    """
    
    # 電気の量 1kWh を熱量に換算する係数 (kJ/kWh) (s2-1-b)
    f_prim = get_f_prim()

    # 1年当たりのコージェネレーション設備による売電量（一次エネルギー換算値）(MJ/yr) (23)
    E_CG_sell = np.sum(E_E_CG_sell_d_t) * f_prim * 1e-3

    return E_CG_sell


def get_E_E_CG_sell_d_t(E_E_CG_gen_d_t, E_E_CG_h_d_t, has_CG_reverse):
    """1時間当たりのコージェネレーション設備による売電量(二次エネルギー) (kWh/h) (24-1)(24-2)
    
    :param E_E_CG_gen_d_t: 1時間当たりのコージェネレーション設備による発電量 (kWh/h)
    :type E_E_CG_gen_d_t: ndarray
    :param E_E_CG_h_d_t: 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h)
    :type E_E_CG_h_d_t: ndarray
    :param has_CG_reverse: コージェネレーション設備が逆潮流を行う場合はTrue
    :type has_CG_reverse: bool
    :return: 1時間当たりのコージェネレーション設備による売電量(二次エネルギー) (kWh/h)
    :rtype: ndarray
    """

    if has_CG_reverse == False:
        # 逆潮流を行わない場合 (24-1)
        E_E_CG_sell_d_t = np.zeros_like(E_E_CG_gen_d_t)
    else:
        # 逆潮流を行う場合 (24-2)
        E_E_CG_sell_d_t = E_E_CG_gen_d_t - E_E_CG_h_d_t
    return E_E_CG_sell_d_t


# ============================================================================
# 13.設計二次エネルギー消費量
# ============================================================================

def calc_E_E(region, sol_region, A_A, A_MR, A_OR, A_env, HW, Q, TS, mu_H, mu_C, r_A_ufvnt, underfloor_insulation,
            NV_MR, NV_OR, mode_H, mode_C,
            V, L,
            H_A=None,
            H_MR=None, H_OR=None, H_HS=None,
            CG=None,
            SHC=None,
            L_T_H_d_t_i=None,
            C_A=None, C_MR=None, C_OR=None, L_H_d_t=None,
            L_CS_d_t=None, L_CL_d_t=None,
            HEX=None, PV=None, solrad=None
            ):
    """ 1 年当たりの設計消費電力量（kWh/年）

    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param HW: 給湯機の仕様
    :type HW: dict
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param TS: 蓄熱
    :type TS: bool
    :param mu_H: 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数
    :type mu_H: float
    :param mu_C: 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数
    :type mu_C: float
    :param r_A_ufvnt: 床下換気
    :type r_A_ufvnt: float
    :param underfloor_insulation: 床下空間が断熱空間内である場合はTrue
    :type underfloor_insulation: bool
    :param NV_MR: 主たる居室における通風の利用における相当換気回数
    :type NV_MR: float
    :param NV_OR: その他の居室における通風の利用における相当換気回数
    :type NV_OR: float
    :param mode_H: 暖房方式
    :type mode_H: str
    :param mode_C: 冷房方式
    :type mode_C: str
    :param V: 換気設備仕様辞書
    :type V: dict
    :param L: 照明設備仕様辞書
    :type L: dict
    :param H_A: 暖房方式, defaults to None
    :type H_A: dict, optional
    :param H_MR: 暖房機器の仕様, defaults to None
    :type H_MR: dict, optional
    :param H_OR: 暖房機器の仕様, defaults to None
    :type H_OR: dict, optional
    :param H_HS: 温水暖房機の仕様, defaults to None
    :type H_HS: dict, optional
    :param CG: コージェネレーションの機器, defaults to None
    :type CG: dict, optional
    :param SHC: 集熱式太陽熱利用設備の仕様, defaults to None
    :type SHC: dict, optional
    :param L_H_A_d_t: 暖房負荷, defaults to None
    :type L_H_A_d_t: ndarray, optional
    :param L_T_H_d_t_i: 暖房区画i=1-5それぞれの暖房負荷 defaults to None
    :type L_T_H_d_t_i: ndarray, optional
    :param C_A: [description], defaults to None
    :type C_A: [type], optional
    :param C_MR: [description], defaults to None
    :type C_MR: [type], optional
    :param C_OR: [description], defaults to None
    :type C_OR: [type], optional
    :param L_CS_A_d_t: 冷房負荷, defaults to None
    :type L_CS_A_d_t: ndarray, optional
    :param L_CL_A_d_t: 冷房負荷, defaults to None
    :type L_CL_A_d_t: ndarray, optional
    :param L_CS_d_t:  暖冷房区画の 1 時間当たりの冷房顕熱負荷, defaults to None
    :type L_CS_d_t: ndarray, optional
    :param L_CL_d_t:  暖冷房区画の 1 時間当たりの冷房潜熱負荷, defaults to None
    :type L_CL_d_t: ndarray, optional
    :param HEX: 熱交換器型設備仕様辞書, defaults to None
    :type HEX: dict, optional
    :param PV: 太陽光発電設備のリスト, defaults to None
    :type PV: ndarray, optional
    :param solrad: load_solrad の返り値, defaults to None
    :type solrad: ndarray, optional
    :return: 1 年当たりの設計消費電力量（kWh/年）
    :rtype: 1 年当たりの設計消費電力量（kWh/年）
    """
    # 想定人数
    n_p = get_n_p(A_A)

    # 実質的な暖房機器の仕様を取得
    spec_MR, spec_OR = get_virtual_heating_devices(region, H_MR, H_OR)

    # 実質的な温水暖房機の仕様を取得
    spec_HS = get_virtual_heatsource(region, H_HS)

    # 暖房方式及び運転方法の区分
    mode_MR, mode_OR = calc_heating_mode(region=region, H_MR=spec_MR, H_OR=spec_OR)

    # その他または設置しない場合
    spec_HW = get_virtual_hotwater(region, HW)

    # 温水暖房負荷の計算
    L_HWH = calc_L_HWH(A_A, A_MR, A_OR, HEX, H_HS, H_MR, H_OR, Q, SHC, TS, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt, region, sol_region,
                       underfloor_insulation, CG)

    # 暖房日の計算
    heating_flag_d = calc_heating_flag_d(A_A, A_MR, A_OR, HEX, H_MR, H_OR, Q, SHC, TS, mu_H, mu_C, NV_MR, NV_OR, r_A_ufvnt, region,
                                         sol_region, underfloor_insulation)

    # 暖房設備の消費電力量
    E_E_H_d_t = get_E_E_H_d_t(region, sol_region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q,
                              H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, CG, SHC, heating_flag_d,
                              L_T_H_d_t_i, L_CS_d_t, L_CL_d_t)

    # 1時間当たりの冷房設備の消費電力量
    E_E_C_d_t = calc_E_E_C_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, C_A, C_MR, C_OR, L_T_H_d_t_i, L_CS_d_t, L_CL_d_t)

    # 1 時間当たりの機械換気設備の消費電力量
    E_E_V_d_t = calc_E_E_V_d_t(n_p, A_A, V, HEX)

    # 1 時間当たりの照明設備の消費電力量
    E_E_L_d_t = calc_E_E_L_d_t(n_p, A_A, A_MR, A_OR, L)

    # 1日当たりの給湯設備の消費電力量
    E_E_W_d_t = calc_E_E_W_d_t(n_p, L_HWH, heating_flag_d, region, sol_region, spec_HW, SHC)

    # 1 時間当たりの家電の消費電力量
    E_E_AP_d_t = calc_E_E_AP_d_t(n_p)

    # 1 時間当たりの調理の消費電力量
    E_E_CC_d_t = get_E_E_CC_d_t()

    # 1時間当たりのコージェネレーション設備による発電量のうちの自家消費分 (kWh/h)
    E_CG, E_E_CG_gen_d_t, E_E_CG_h_d_t, E_E_TU_aux_d_t, E_E_CG_h_d_t, E_G_CG_ded, e_BB_ave, Q_CG_h =\
        calc_E_W(A_A, region, sol_region, HW, SHC, CG, H_A, H_MR, H_OR, H_HS, C_A, C_MR,
                C_OR,
                                V, L, A_MR, A_OR, A_env, Q, mu_H, mu_C, NV_MR, NV_OR, TS,
                                r_A_ufvnt, HEX, underfloor_insulation, mode_H, mode_C)

    # 太陽光発電設備の発電量
    E_E_PV_d_t = calc_E_E_PV_d_t(PV, solrad)
    E_E_dmd_d_t = get_E_E_dmd_d_t(E_E_H_d_t, E_E_C_d_t, E_E_V_d_t, E_E_L_d_t, E_E_W_d_t, E_E_AP_d_t)
    E_E_PV_h_d_t = get_E_E_PV_h_d_t(E_E_PV_d_t, E_E_dmd_d_t, E_E_CG_h_d_t, has_PV=PV != None)

    E_E = sum(E_E_H_d_t) \
          + sum(E_E_C_d_t) \
          + sum(E_E_V_d_t) \
          + sum(E_E_L_d_t) \
          + sum(E_E_W_d_t) \
          + sum(E_E_AP_d_t) \
          + sum(E_E_CC_d_t) \
          - sum(E_E_PV_h_d_t) \
          - sum(E_E_CG_h_d_t)  # (25)

    # 小数点以下一位未満の端数があるときは、これを四捨五入する。
    return Decimal(E_E).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP), E_E_PV_h_d_t, E_E_PV_d_t, E_E_CG_gen_d_t, E_E_CG_h_d_t, E_E_dmd_d_t, E_E_TU_aux_d_t


def calc_E_G(region, sol_region, A_A, A_MR, A_OR, A_env, Q, mu_H, mu_C, NV_MR, NV_OR, TS, r_A_ufvnt, HEX, underfloor_insulation,
            H_A, H_MR, H_OR, H_HS, C_A, C_MR, C_OR, V, L, HW, SHC,
            spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, mode_H, mode_C, CG, L_T_H_d_t_i,
            L_HWH, heating_flag_d):
    """  1 年当たりの設計ガス消費量（MJ/年）
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param Q: 当該住戸の熱損失係数 (W/m2K)
    :type Q: float
    :param mu_H: 断熱性能の区分݆における日射取得性能の区分݇の暖房期の日射取得係数
    :type mu_H: float
    :param mu_C: 断熱性能の区分݆における日射取得性能の区分݇の冷房期の日射取得係数
    :type mu_C: float
    :param NV_MR: 主たる居室における通風の利用における相当換気回数
    :type NV_MR: float
    :param NV_OR: その他の居室における通風の利用における相当換気回数
    :type NV_OR: float
    :param TS: 蓄熱
    :type TS: bool
    :param r_A_ufvnt: 床下換気
    :type r_A_ufvnt: float
    :param HEX: 熱交換器型設備仕様辞書
    :type HEX: dict
    :param underfloor_insulation: 床下空間が断熱空間内である場合はTrue
    :type underfloor_insulation: bool
    :param H_A: 暖房方式
    :type H_A: dict
    :param H_MR: 暖房機器の仕様
    :type H_MR: dict
    :param H_OR: 暖房機器の仕様
    :type H_OR: dict
    :param H_HS: 温水暖房機の仕様
    :type H_HS: dict
    :param C_A: 冷房方式
    :type C_A: dict
    :param C_MR: 主たる居室の冷房機器
    :type C_MR: dict
    :param C_OR: その他の居室の冷房機器
    :type C_OR: dict
    :param V: 換気設備仕様辞書
    :type V: dict
    :param L: 照明設備仕様辞書
    :type L: dict
    :param HW: 給湯機の仕様
    :type HW: dict
    :param SHC: 集熱式太陽熱利用設備の仕様
    :type SHC: dict
    :param spec_MR: 主たる居室の仕様
    :type spec_MR: dict
    :param spec_OR: その他の居室の仕様
    :type spec_OR: dict
    :param spec_HS:暖房方式及び運転方法の区分
    :type spec_HS: dict
    :param mode_MR: 主たる居室の運転方法 (連続運転|間歇運転)
    :type mode_MR: str
    :param mode_OR: その他の居室の運転方法 (連続運転|間歇運転)
    :type mode_OR: str
    :param mode_H: 暖房方式
    :type mode_H: str
    :param mode_C: 冷房方式
    :type mode_C: str
    :param CG: コージェネレーションの機器
    :type CG: dict
    :param L_T_H_d_t_i: 暖房区画i=1-5それぞれの暖房負荷
    :type L_T_H_d_t_i: ndarray
    :param L_HWH: 1日当たりの温水暖房の熱負荷 (MJ/d)
    :type L_HWH: ndarray
    :param heating_flag_d: 暖房日
    :type heating_flag_d: ndarray
    :return: 1 年当たりの設計ガス消費量（MJ/年）
    :rtype: float
    """
    # 仮想居住人数
    n_p = get_n_p(A_A)

    # 暖房設備のガス消費量（MJ/h）
    E_G_H_d_t = get_E_G_H_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, CG,
                              L_T_H_d_t_i)

    # 1時間当たりの冷房設備のガス消費量
    E_G_C_d_t = calc_E_G_C_d_t()

    # 1日当たりの給湯設備のガス消費量 (MJ/d)
    E_G_W_d = calc_E_G_W_d_t(n_p, L_HWH, heating_flag_d, A_A, region, sol_region, HW, SHC)

    # 1日当たりのコージェネレーション設備のガス消費量
    E_G_CG_d_t, *args = calc_E_CG_d_t(A_A, region, sol_region, HW, SHC, CG, H_A, H_MR, H_OR, H_HS, C_A, C_MR,
                           C_OR,
                           V, L, A_MR, A_OR, A_env, Q, mu_H, mu_C, NV_MR, NV_OR, TS,
                           r_A_ufvnt, HEX, underfloor_insulation, mode_H, mode_C)

    # 1 時間当たりの家電のガス消費量
    E_G_AP_d_t = get_E_G_AP_d_t()

    # 1 時間当たりの調理のガス消費量
    E_G_CC_d_t = calc_E_G_CC_d_t(n_p)

    E_G = sum(E_G_H_d_t) \
          + sum(E_G_C_d_t) \
          + sum(E_G_W_d) \
          + sum(E_G_CG_d_t) \
          + sum(E_G_AP_d_t) \
          + sum(E_G_CC_d_t)  # (26)

    # 小数点以下一位未満の端数があるときは、これを四捨五入する。
    return Decimal(E_G).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)


def calc_E_K(region, sol_region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, CG, L_T_H_d_t_i, L_HWH, heating_flag_d, HW, SHC):
    """ 1 年当たりの設計灯油消費量（MJ/年）
    
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分(1-5)
    :type sol_region: int
    :param A_A: 床面積の合計 (m2)
    :type A_A: float
    :param A_MR: 主たる居室の床面積 (m2)
    :type A_MR: float
    :param A_OR: その他の居室の床面積 (m2)
    :type A_OR: float
    :param H_A: 暖房方式
    :type H_A: dict
    :param mode_MR: 主たる居室の運転方法 (連続運転|間歇運転)
    :type mode_MR: str
    :param mode_OR: その他の居室の運転方法 (連続運転|間歇運転)
    :type mode_OR: str
    :param spec_HS: 温水暖房機の仕様
    :type spec_HS: dict
    :param mode_MR: 主たる居室の運転方法 (連続運転|間歇運転)
    :type mode_MR: str
    :param mode_OR: その他の居室の運転方法 (連続運転|間歇運転)
    :type mode_OR: str
    :param CG: コージェネレーションの機器
    :type CG: dict
    :param L_T_H_d_t_i: 暖房区画i=1-5それぞれの暖房負荷
    :type L_T_H_d_t_i: ndarray
    :param L_HWH: 1日当たりの温水暖房の熱負荷 (MJ/d)
    :type L_HWH: ndarray
    :param heating_flag_d: 暖房日
    :type heating_flag_d: ndarray
    :param HW: 給湯機の仕様
    :type HW: dict
    :param SHC: 集熱式太陽熱利用設備の仕様
    :type SHC: dict
    :return: 1 年当たりの設計灯油消費量（MJ/年）
    :rtype: float
    """
    
    # 仮想居住人数
    n_p = get_n_p(A_A)

    # 暖房設備の灯油消費量（MJ/h）
    E_K_H_d_t = calc_E_K_H_d_t(region, A_A, A_MR, A_OR, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, CG,
                               L_T_H_d_t_i)

    # 1時間当たりの冷房設備の灯油消費量
    E_K_C_d_t = calc_E_K_C_d_t()

    # 1日当たりの給湯設備の灯油消費量 (MJ/d)
    E_K_W_d_t = calc_E_K_W_d_t(n_p, L_HWH, heating_flag_d, A_A, region, sol_region, HW, SHC)

    # 1日当たりのコージェネレーション設備の灯油消費量
    E_K_CG_d = np.zeros(365)

    # 1 時間当たりの家電の灯油消費量
    E_K_AP_d_t = get_E_K_AP_d_t()

    # 1 時間当たりの調理の灯油消費量
    E_K_CC_d_t = get_E_K_CC_d_t()

    # 1年当たりの設計灯油消費量（MJ / 年）
    E_K_raw = sum(E_K_H_d_t) \
              + sum(E_K_C_d_t) \
              + sum(E_K_W_d_t) \
              + sum(E_K_CG_d) \
              + sum(E_K_AP_d_t) \
              + sum(E_K_CC_d_t)  # (27)

    # 小数点以下一位未満の端数があるときは、これを四捨五入する。
    E_K = Decimal(E_K_raw).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

    return E_K


def calc_E_UT_H(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_H, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, CG,
               L_T_H_d_t, L_CS_d_t, L_CL_d_t):
    """

    :param region: 省エネルギー地域区分
    :type region: int
    :param A_A: 床面積の合計 [m2]
    :type A_A: float
    :param A_MR: 主たる居室の床面積 [m2]
    :type A_MR: float
    :param A_OR: その他の居室の床面積 [m2]
    :type A_OR: float
    :param mode_H: 暖房方式
    :type mode_H: str
    :param H_A: 暖房方式
    :type H_A: dict
    :param spec_MR: 主たる居室の仕様
    :type spec_MR: dict
    :param spec_OR: その他の居室の仕様
    :type spec_OR: dict
    :param spec_HS: 暖房方式及び運転方法の区分
    :type spec_HS: dict
    :param mode_MR: 主たる居室の運転方法 (連続運転|間歇運転)
    :type mode_MR: str
    :param mode_OR: その他の居室の運転方法 (連続運転|間歇運転)
    :type mode_OR: str
    :param CG: コージェネレーションの機器
    :type CG: dict
    :param L_H_A_d_t: 暖房負荷
    :type L_H_A_d_t: ndarray
    :param L_T_H_d_t: 暖房区画の暖房負荷
    :type L_T_H_d_t: ndarray
    :param L_CS_d_t: 暖冷房区画の 1 時間当たりの冷房顕熱負荷
    :type L_CS_d_t: ndarray
    :param L_CL_d_t: 暖冷房区画の 1 時間当たりの冷房潜熱負荷
    :type L_CL_d_t: ndarray
    :return: 1 年当たりの未処理暖房負荷の設計一次エネルギー消費量相当値
    :rtype: float
    """
    # 暖房設備の未処理暖房負荷の設計一次エネルギー消費量相当値
    E_UT_H_d_t = calc_E_UT_H_d_t(region, A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_H, H_A, spec_MR, spec_OR, spec_HS, mode_MR, mode_OR, CG,
                                 L_T_H_d_t, L_CS_d_t, L_CL_d_t)

    # 1 年当たりの未処理暖房負荷の設計一次エネルギー消費量相当値
    E_UT_H_raw = sum(E_UT_H_d_t)  # (28)

    # 小数点以下一位未満の端数があるときは、これを四捨五入する。
    E_UT_H = Decimal(E_UT_H_raw).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

    return E_UT_H


# 1 年当たりの未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/年）
def get_E_UT_C(A_A, A_MR, A_OR, A_env, mu_H, mu_C, Q, mode_C, C_A, region, L_H_d_t, L_CS_d_t, L_CL_d_t):
    if mode_C == '住戸全体を連続的に冷房する方式':
        # VAV方式の採用
        if 'VAV' in C_A:
            VAV = C_A['VAV']

        # 全般換気機能の有無
        if 'general_ventilation' in C_A:
            general_ventilation = C_A['general_ventilation']

        # ダクトが通過する空間
        if 'duct_insulation' in C_A:
            duct_insulation = C_A['duct_insulation']

        # 機器の仕様の
        if C_A['EquipmentSpec'] == '入力しない':
            # 付録B
            q_hs_rtd_C = dc_spec.get_q_hs_rtd_C(region, A_A)
        elif C_A['EquipmentSpec'] == '定格能力試験の値を入力する':
            q_hs_rtd_C = C_A['q_hs_rtd_C']
        elif C_A['EquipmentSpec'] == '定格能力試験と中間能力試験の値を入力する':
            q_hs_rtd_C = C_A['q_hs_rtd_C']
        else:
            raise ValueError(C_A['EquipmentSpec'])

        # 設計風量(暖房)
        if 'V_hs_dsgn_C' in C_A:
            V_hs_dsgn_C = C_A['V_hs_dsgn_C']
        else:
            V_fan_rtd_C = dc_spec.get_V_fan_rtd_C(q_hs_rtd_C)
            V_hs_dsgn_C = dc_spec.get_V_fan_dsgn_C(V_fan_rtd_C)

        # 定格冷房能力
        q_hs_rtd_H = 0

        # 設計風量(冷房)
        V_hs_dsgn_H = 0

        E_UT_C_d_t, _, _, _, _, _, \
        _, _, _, _, _ = dc.get_Q_UT_A(A_A, A_MR, A_OR, A_env, mu_H, mu_C, q_hs_rtd_H, q_hs_rtd_C, V_hs_dsgn_H, V_hs_dsgn_C, Q,
             VAV, general_ventilation, duct_insulation, region, L_H_d_t, L_CS_d_t, L_CL_d_t)
    else:
        E_UT_C_d_t = calc_E_UT_C_d_t()

    # 1 年当たりの未処理暖房負荷の設計一次エネルギー消費量相当値（MJ/年）
    E_UT_C_raw = sum(E_UT_C_d_t) # (29)

    # 小数点以下一位未満の端数があるときは、これを四捨五入する。
    E_UT_C = Decimal(E_UT_C_raw).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

    return E_UT_C


# ============================================================================
# 16.電力需要
# ============================================================================


def get_E_E_dmd_d_t(E_E_H_d_t, E_E_C_d_t, E_E_V_d_t, E_E_L_d_t, E_E_W_d_t, E_E_AP_d_t):
    """1時間当たりの電力需要 (28)
    
    :param E_E_H_d_t: 1時間当たりの暖房設備の消費電力量 [kWh/h]
    :type E_E_H_d_t: ndarray
    :param E_E_C_d_t: 1時間当たりの冷房設備の消費電力量 [kWh/h]
    :type E_E_C_d_t: ndarray
    :param E_E_V_d_t:  1時間当たりの機械換気設備の消費電力量 [kWh/h]
    :type E_E_V_d_t: ndarray
    :param E_E_L_d_t: 日付dの時刻tにおける 1 時間当たりの照明設備の消費電力量[kWh/h]
    :type E_E_L_d_t: ndarray
    :param E_E_W_d_t: 1時間当たりの給湯設備の消費電力量 [kWh/h]
    :type E_E_W_d_t:  ndarray
    :param E_E_AP_d_t: 1 時間当たりの家電の消費電力量
    :type E_E_AP_d_t: ndarray
    :return: 1時間当たりの電力需要 (28)
    :rtype: ndarray
    """
    
    return E_E_H_d_t + E_E_C_d_t + E_E_V_d_t + E_E_L_d_t + E_E_W_d_t + E_E_AP_d_t
