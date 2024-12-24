# ============================================================================
# 第三章 暖冷房負荷と外皮性能
# 第二節 外皮性能
# Ver.04（住宅・住戸の外皮性能の計算プログラム Ver.02.01～）
# ============================================================================

import pyhees.section3_2_8 as detail
import pyhees.section3_2_9 as spec


def calc_insulation_performance(tatekata, method, A_env=None, A_A=None, U_A=None, eta_A_H=None, eta_A_C=None):
    """外皮の断熱性能の計算
     入力方法によって、r_env の計算方法が異なる
     ・当該住宅の外皮面積の合計を用いて評価する => 別途計算された結果を用いる
     ・仕様基準又は誘導仕様基準により外皮性能を評価する方法

    Args:
      tatekata(str): 建て方
      method(str): 入力方法
      A_env(float, optional): 外皮の部位の面積の合計 (m2) (Default value = None)
      A_A(float, optional): 床面積の合計[m^2] (Default value = None)
      U_A(float, optional): 外皮平均熱貫流率 (Default value = None)
      eta_A_H(float, optional): 暖房期の平均日射熱取得率 (Default value = None)
      eta_A_C(float, optional): 冷房期の平均日射熱取得率 (Default value = None)

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
    elif method in ['仕様基準により外皮性能を評価する方法',
                    '誘導仕様基準により外皮性能を評価する方法（住戸全体を対象に評価）',
                    '誘導仕様基準により外皮性能を評価する方法（増改築部分を対象に評価）']:
        # 床面積の合計に対する外皮の部位の面積の合計の比
        r_env = calc_r_env(
            method='仕様基準又は誘導仕様基準により外皮性能を評価する方法',
            tatekata=tatekata
        )

    else:
        raise ValueError(method)

    # 熱損失係数（換気による熱損失を含まない）
    Q_dash = get_Q_dash(U_A, r_env)

    # 日射取得係数
    mu_H = get_mu_H(eta_A_H, r_env)
    mu_C = get_mu_C(eta_A_C, r_env)

    return r_env, Q_dash, mu_H, mu_C


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
    if method == '仕様基準又は誘導仕様基準により外皮性能を評価する方法':
        return spec.get_U_A(**args)
    else:
        raise ValueError(method)


def calc_eta_A_H(method, **args):
    """暖房期の平均日射熱取得率

    Args:
      method(str): 入力方法
      args(args):

    Returns:
      float: 暖房期の平均日射熱取得率

    """

    if method == '仕様基準又は誘導仕様基準により外皮性能を評価する方法':
        return spec.get_eta_A_H(**args)
    else:
        raise ValueError(method)


def calc_eta_A_C(method, **args):
    """冷房期の平均日射熱取得率

    Args:
      method(str): 入力方法
      args(args):

    Returns:
      float: 冷房期の平均日射熱取得率

    """

    if method == '仕様基準又は誘導仕様基準により外皮性能を評価する方法':
        return spec.get_eta_A_C(**args)
    else:
        raise ValueError(method)


def calc_r_env(method, tatekata=None, A_env=None, A_A=None, house_insulation_type=None, floor_bath_insulation=None):
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
    elif method == '仕様基準又は誘導仕様基準により外皮性能を評価する方法':
        # 外皮の部位の面積の合計 (m2)
        A_dash_env = spec.get_A_dash_env(tatekata)

        # 床面積の合計 (m2)
        A_dash_A = spec.get_A_dash_A(tatekata)

        return spec.get_r_env(
            A_dash_env=A_dash_env,
            A_dash_A=A_dash_A
        )
    else:
        raise ValueError(method)
