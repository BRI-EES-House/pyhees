# ============================================================================
# 第三章 暖冷房負荷と外皮性能
# 第二節 外皮性能
# Ver.04（住宅・住戸の外皮性能の計算プログラム Ver.02.01～）
# ============================================================================

import pyhees.section3_2_8 as detail
import pyhees.section3_2_9 as simple




def calc_insulation_performance(method, A_env=None, A_A=None, U_A=None, eta_A_H=None, eta_A_C=None,
                                house_insulation_type=None, house_structure_type=None, insulation_structure=None,
                                U_spec=None,f_H=None,f_C=None,eta_d_H=None,eta_d_C=None,region=None):
    """外皮の断熱性能の計算
     入力方法によって、U_A, eta_A_H, eta_A_C, r_env の計算方法が異なる
     1.当該住宅の外皮面積の合計を用いて評価する => すべて別途計算された結果を用いる
     2.簡易的に求めた外皮面積の合計を用いて評価する => U_A, eta_A_H, eta_A_Cは別途計算された値を用いるが、r_envは簡易計算
     3.当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法 => すべて簡易計算

    Args:
      method(str): 入力方法
      A_env(float, optional): 外皮の部位の面積の合計 (m2) (Default value = None)
      A_A(float, optional): 床面積の合計[m^2] (Default value = None)
      U_A(float, optional): 外皮平均熱貫流率 (Default value = None)
      eta_A_H(float, optional): 暖房期の平均日射熱取得率 (Default value = None)
      eta_A_C(float, optional): 冷房期の平均日射熱取得率 (Default value = None)
      house_insulation_type(str, optional): 床断熱住戸'または'基礎断熱住戸' (Default value = None)
      house_structure_type(structure_type: structure_type: str, optional): 木造'または'鉄筋コンクリート造'または'鉄骨造' (Default value = None)
      insulation_structure(structure: structure: str, optional): 断熱構造による住戸の種類 (Default value = None)
      U_spec(dict, optional): 外皮の部位の熱貫流率の辞書 (Default value = None)
      f_H(float, optional): 暖房期の取得日射熱補正係数 (-) (Default value = None)
      f_C(float, optional): 冷房期の取得日射熱補正係数 (-) (Default value = None)
      eta_d_H(param eta_d_C:, optional): 暖房期の日射熱取得率 (Default value = None)
      eta_d_C: type eta_d_C: (Default value = None)
      region(int, optional): 省エネルギー地域区分 (Default value = None)

    Returns:
      tuple: 外皮の断熱性能

    """
    if method == '当該住宅の外皮面積の合計を用いて評価する':
        # 床面積の合計に対する外皮の部位の面積の合計の比
        r_env = calc_r_env(
            method='当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法',
            A_env=A_env,
            A_A=A_A
        )
    elif method == '簡易的に求めた外皮面積の合計を用いて評価する':
        # 床面積の合計に対する外皮の部位の面積の合計の比
        r_env = calc_r_env(
            method='当該住戸の外皮の部位の面積等を用いずに外皮性能を評価する方法',
            house_insulation_type=house_insulation_type,
            floor_bath_insulation=U_spec['floor_bath_insulation']
        )
    elif method == '当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法':
        # 断熱構造による住戸の種類に応じてU_A値を計算する
        U_A, U = simple.calc_U_A(insulation_structure, house_structure_type, **U_spec)

        # 床面積の合計に対する外皮の部位の面積の合計の比
        r_env = calc_r_env(
            method='当該住戸の外皮の部位の面積等を用いずに外皮性能を評価する方法',
            A_env=None,
            A_A=None,
            house_insulation_type=U['house_insulation_type'],
            floor_bath_insulation=U['floor_bath_insulation']
        )

        # 暖房期平均日射熱取得率(ηAH)
        eta_A_H = calc_eta_A_H(
            method='当該住戸の外皮の部位の面積等を用いずに外皮性能を評価する方法',
            region=region,
            house_insulation_type=U['house_insulation_type'],
            floor_bath_insulation=U['floor_bath_insulation'],
            U_roof=U['U_roof'],
            U_wall=U['U_wall'],
            U_door=U['U_door'],
            U_base_etrc=U['U_base_etrc'],
            U_base_bath=U['U_base_bath'],
            U_base_other=U['U_base_other'],
            Psi_HB_roof=U['Psi_HB_roof'],
            Psi_HB_wall=U['Psi_HB_wall'],
            Psi_HB_floor=U['Psi_HB_floor'],
            Psi_HB_roof_wall=U['Psi_HB_roof_wall'],
            Psi_HB_wall_wall=U['Psi_HB_wall_wall'],
            Psi_HB_wall_floor=U['Psi_HB_wall_floor'],
            etr_d=eta_d_H,
            f_H=f_H
        )

        # 冷房期平均日射熱取得率(ηAC)
        eta_A_C = calc_eta_A_C(
            method='当該住戸の外皮の部位の面積等を用いずに外皮性能を評価する方法',
            region=region,
            house_insulation_type=U['house_insulation_type'],
            floor_bath_insulation=U['floor_bath_insulation'],
            U_roof=U['U_roof'],
            U_wall=U['U_wall'],
            U_door=U['U_door'],
            U_base_etrc=U['U_base_etrc'],
            U_base_bath=U['U_base_bath'],
            U_base_other=U['U_base_other'],
            Psi_HB_roof=U['Psi_HB_roof'],
            Psi_HB_wall=U['Psi_HB_wall'],
            Psi_HB_floor=U['Psi_HB_floor'],
            Psi_HB_roof_wall=U['Psi_HB_roof_wall'],
            Psi_HB_wall_wall=U['Psi_HB_wall_wall'],
            Psi_HB_wall_floor=U['Psi_HB_wall_floor'],
            etr_d=eta_d_C,
            f_C=f_C
        )

        house_insulation_type = U['house_insulation_type']
    else:
        raise ValueError(method)

    # 熱損失係数（換気による熱損失を含まない）
    Q_dash = get_Q_dash(U_A, r_env)

    # 日射取得係数
    mu_H = get_mu_H(eta_A_H, r_env)
    mu_C = get_mu_C(eta_A_C, r_env)

    return U_A, r_env, eta_A_H, eta_A_C, Q_dash, mu_H, mu_C, house_insulation_type


# ============================================================================
# 5. 熱損失係数（換気による熱損失を含まない）
# ============================================================================

def get_Q_dash(U_A, r_env):
    """熱損失係数（換気による熱損失を含まない） (1)

    Args:
      U_A(float): 外皮平均熱貫流率
      r_env(float): 床面積の合計に対しる外皮の部位の面積の合計の比（-）

    Returns:
      float: 熱損失係数（換気による熱損失を含まない）

    """
    return U_A * r_env  # (1)


# ============================================================================
# 6. 日射取得係数
# ============================================================================

def get_mu_H(eta_A_H, r_env):
    """暖房期の日射取得係数 (2)

    Args:
      eta_A_H(float): 暖房期の平均日射熱取得率
      r_env(float): 床面積の合計に対しる外皮の部位の面積の合計の比（-）

    Returns:
      float: 暖房期の日射取得係数

    """
    if eta_A_H is None:
        return None
    return eta_A_H / 100.0 * r_env


def get_mu_C(eta_A_C, r_env):
    """冷房期の日射取得係数 (3)

    Args:
      eta_A_C(float): 冷房期の平均日射熱取得率
      r_env(float): 床面積の合計に対しる外皮の部位の面積の合計の比（-）

    Returns:
      float: 冷房期の日射取得係数

    """
    return eta_A_C / 100.0 * r_env


# ============================================================================
# 7. 外皮平均熱貫流率並びに暖房期及び冷房期の平均日射熱取得率
# ============================================================================

def calc_U_A(method, **args):
    """外皮平均熱貫流率

    Args:
      method(str): 入力方法
      args(args):

    Returns:
      float: 外皮平均熱貫流率

    """
    if method == '当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法':
        return detail.get_U_A(**args)
    elif method == '当該住戸の外皮の部位の面積等を用いずに外皮性能を評価する方法':
        return simple.calc_U_A(**args)
    else:
        raise ValueError(method)


def calc_eta_A_H(method, region, house_insulation_type, floor_bath_insulation, U_roof, U_wall, U_door, U_base_etrc, U_base_bath,
                 U_base_other, Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall, Psi_HB_wall_wall,
                 Psi_HB_wall_floor, etr_d, f_H):
    """暖房期の平均日射熱取得率

    Args:
      method(str): 入力方法
      region(int): 省エネルギー地域区分
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱'または'基礎断熱'、'浴室の床及び基礎が外気等に面していない'
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
      f_H(float): 暖房期の取得日射熱補正係数 (-)

    Returns:
      float: 暖房期の平均日射熱取得率

    """

    if method == '当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法':
        return detail.calc_eta_A_H()
    elif method == '当該住戸の外皮の部位の面積等を用いずに外皮性能を評価する方法':

        # 単位日射強度当たりの暖房期の日射熱取得量[W/(W/m2)]
        m_H = simple.get_m_H(
            region=region,
            house_insulation_type=house_insulation_type,
            floor_bath_insulation=floor_bath_insulation,
            U_roof=U_roof,
            U_wall=U_wall,
            U_door=U_door,
            U_base_etrc=U_base_etrc,
            U_base_bath=U_base_bath,
            U_base_other=U_base_other,
            Psi_HB_roof=Psi_HB_roof,
            Psi_HB_wall=Psi_HB_wall,
            Psi_HB_floor=Psi_HB_floor,
            Psi_HB_roof_wall=Psi_HB_roof_wall,
            Psi_HB_wall_wall=Psi_HB_wall_wall,
            Psi_HB_wall_floor=Psi_HB_wall_floor,
            etr_d=etr_d,
            f_H=f_H
        )

        A_dash_env = simple.get_A_dash_env(house_insulation_type, floor_bath_insulation)

        return simple.get_eta_A_H(m_H=m_H, A_dash_env=A_dash_env)
    else:
        raise ValueError(method)


def calc_eta_A_C(method, region, house_insulation_type, floor_bath_insulation, U_roof, U_wall, U_door, U_base_etrc, U_base_bath, U_base_other,
                 Psi_HB_roof, Psi_HB_wall, Psi_HB_floor, Psi_HB_roof_wall, Psi_HB_wall_wall, Psi_HB_wall_floor,
                 etr_d, f_C):
    """冷房期の平均日射熱取得率

    Args:
      method(str): 入力方法
      region(int): 省エネルギー地域区分
      house_insulation_type(str): 床断熱住戸'または'基礎断熱住戸'
      floor_bath_insulation(str): 床断熱'または'基礎断熱'、'浴室の床及び基礎が外気等に面していない'
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
      f_C(float): 冷房期の取得日射熱補正係数 (-)

    Returns:
      float: 冷房期の平均日射熱取得率

    """

    if method == '当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法':
        return detail.calc_eta_A_C()
    elif method == '当該住戸の外皮の部位の面積等を用いずに外皮性能を評価する方法':

        # 単位日射強度当たりの冷房期の日射熱取得量[W/(W/m2)]
        m_C = simple.get_m_C(
            region=region,
            house_insulation_type=house_insulation_type,
            floor_bath_insulation=floor_bath_insulation,
            U_roof=U_roof,
            U_wall=U_wall,
            U_door=U_door,
            U_base_etrc=U_base_etrc,
            U_base_bath=U_base_bath,
            U_base_other=U_base_other,
            Psi_HB_roof=Psi_HB_roof,
            Psi_HB_wall=Psi_HB_wall,
            Psi_HB_floor=Psi_HB_floor,
            Psi_HB_roof_wall=Psi_HB_roof_wall,
            Psi_HB_wall_wall=Psi_HB_wall_wall,
            Psi_HB_wall_floor=Psi_HB_wall_floor,
            etr_d=etr_d,
            f_C=f_C)

        A_dash_env = simple.get_A_dash_env(house_insulation_type, floor_bath_insulation)

        return simple.get_eta_A_C(m_C=m_C, A_dash_env=A_dash_env)
    else:
        raise ValueError(method)


def calc_r_env(method, A_env=None, A_A=None, house_insulation_type=None, floor_bath_insulation=None):
    """床面積の合計に対する外皮の部位の面積の合計の比

    Args:
      method(str): 入力方法
      A_env(float, optional): 外皮の部位の面積の合計 (m2) (Default value = None)
      A_A(float, optional): 床面積の合計[m^2] (Default value = None)
      house_insulation_type(str, optional): 床断熱住戸'または'基礎断熱住戸' (Default value = None)
      floor_bath_insulation: Default value = None)

    Returns:
      float: 床面積の合計に対する外皮の部位の面積の合計の比

    """
    if method == '当該住戸の外皮の部位の面積等を用いて外皮性能を評価する方法':
        return detail.get_r_env(
            A_env=A_env,
            A_A=A_A
        )
    elif method == '当該住戸の外皮の部位の面積等を用いずに外皮性能を評価する方法':

        # 外部部位の面積の合計 (m2)
        A_dash_env = simple.get_A_dash_env(house_insulation_type, floor_bath_insulation)

        # 床面積の合計
        A_dash_A = simple.get_A_dash_A()

        return simple.get_r_env(
            A_dash_env=A_dash_env,
            A_dash_A=A_dash_A
        )
    else:
        raise ValueError(method)
