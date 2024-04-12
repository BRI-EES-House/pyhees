# ============================================================================
# 付録 O 太陽熱利用設備
# ============================================================================


import numpy as np


# ============================================================================
# O.2 各用途における補正集熱量
# ============================================================================

def calc_L_sun_d_t(hw_connection_type, solar_device, solar_water_tap, Theta_sw_s, 
                L_sun_total_d_t, L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t,
                L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t, Theta_w_sun_d_t):
    """各用途における太陽熱利用設備による補正集熱量 (MJ/h)

    Args:
      hw_connection_type(str): 給湯接続方式の種類 (-)
      solar_device(str): 太陽熱利用設備の種類 (-)
      solar_water_tap(str): 太陽熱用水栓 (-)
      Theta_w_sun_d_t(ndarray): 太陽熱利用設備から供給される水の温度
      Theta_sw_s(int): 浴室シャワー水栓における基準給湯温度
      L_sun_total_d_t(ndarray): 1時間当たりの太陽熱利用給湯設備による補正集熱量の総量 (MJ/h)
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷（MJ/h）
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷（MJ/h）
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷（MJ/h）
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷（MJ/h）
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における節湯補正給湯熱負荷（MJ/h）
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷（MJ/h）

    Returns:
      tuple: 各用途における太陽熱利用設備による補正集熱量 (MJ/h)
  """

    # 各用途における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合
    r_sun_k_d_t, r_sun_s_d_t, r_sun_w_d_t, r_sun_b1_d_t, r_sun_b2_d_t, r_sun_ba1_d_t = [np.zeros(24 * 365) for _ in range(6)]

    for dt in range(24 * 365):
      r_sun_k_d_t[dt], r_sun_s_d_t[dt], r_sun_w_d_t[dt], \
        r_sun_b1_d_t[dt], r_sun_b2_d_t[dt], r_sun_ba1_d_t[dt] = get_r_sun(hw_connection_type, solar_device, solar_water_tap, Theta_w_sun_d_t[dt], Theta_sw_s,
                  L_dash_b1_d_t[dt], L_dash_b2_d_t[dt], L_dash_ba1_d_t[dt])

    # 給湯熱需要のうちの太陽熱利用設備の分担分
    Q_W_dmd_sun_d_t = get_Q_W_dmd_sun_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                          r_sun_k_d_t, r_sun_s_d_t, r_sun_w_d_t, r_sun_b1_d_t, r_sun_b2_d_t, r_sun_ba1_d_t)

    # 各用途における太陽熱利用設備による補正集熱量 (1)
    L_sun_k_d_t, L_sun_s_d_t, L_sun_w_d_t, \
      L_sun_b1_d_t, L_sun_b2_d_t, L_sun_ba1_d_t = get_L_sun_d_t(L_sun_total_d_t, L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t,
                                                      L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t, Q_W_dmd_sun_d_t,
                                                      r_sun_k_d_t, r_sun_s_d_t, r_sun_w_d_t,
                                                      r_sun_b1_d_t, r_sun_b2_d_t, r_sun_ba1_d_t)

    return L_sun_k_d_t, L_sun_s_d_t, L_sun_w_d_t, L_sun_b1_d_t, L_sun_b2_d_t, L_sun_ba1_d_t


def get_L_sun_d_t(L_sun_total_d_t, L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t,
                L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t, Q_W_dmd_sun_d_t,
                r_sun_k_d_t, r_sun_s_d_t, r_sun_w_d_t,
                r_sun_b1_d_t, r_sun_b2_d_t, r_sun_ba1_d_t):
    """各用途における太陽熱利用設備による補正集熱量 (MJ/h) (1)

    Args:
      L_sun_total_d_t(ndarray): 1時間当たりの太陽熱利用給湯設備による補正集熱量の総量 (MJ/h)
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷（MJ/h）
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷（MJ/h）
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷（MJ/h）
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷（MJ/h）
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における節湯補正給湯熱負荷（MJ/h）
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷（MJ/h）
      Q_W_dmd_sun_d_t(ndarray): 給湯熱需要のうちの太陽熱利用設備の分担分 (MJ/h)
      r_sun_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合（-）
      r_sun_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合（-）
      r_sun_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合（-）
      r_sun_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合（-）
      r_sun_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合（-）
      r_sun_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合（-）

    Returns:
      tuple: 各用途における太陽熱利用設備による補正集熱量 (MJ/h)
    """
    L_sun_k_d_t, L_sun_s_d_t, L_sun_w_d_t, L_sun_b1_d_t, L_sun_b2_d_t, L_sun_ba1_d_t = [np.zeros(24 * 365) for _ in range(6)]

    # Q_W_dmd_sun_d_t = 0の場合
    f1 = Q_W_dmd_sun_d_t == 0
    # Q_W_dmd_sun_d_t != 0の場合
    f2 = Q_W_dmd_sun_d_t != 0

    # 1時間当たりの台所水栓における太陽熱利用設備による補正集熱量
    # (1a-1)
    L_sun_k_d_t[f1] = 0.0
    # (1a-2)
    L_sun_k_d_t[f2] = L_sun_total_d_t[f2] * ((r_sun_k_d_t[f2] * L_dash_k_d_t[f2]) / Q_W_dmd_sun_d_t[f2])

    # 1時間当たりの浴室シャワーにおける太陽熱利用設備による補正集熱量
    # (1b-1)
    L_sun_s_d_t[f1] = 0.0
    # (1b-2)
    L_sun_s_d_t[f2] = L_sun_total_d_t[f2] * ((r_sun_s_d_t[f2] * L_dash_s_d_t[f2]) / Q_W_dmd_sun_d_t[f2])

    # 1時間当たりの洗面水栓における太陽熱利用設備による補正集熱量
    # (1c-1)
    L_sun_w_d_t[f1] = 0.0
    # (1c-2)
    L_sun_w_d_t[f2] = L_sun_total_d_t[f2] * ((r_sun_w_d_t[f2] * L_dash_w_d_t[f2]) / Q_W_dmd_sun_d_t[f2])

    # 1時間当たりの浴槽水栓湯はり時における太陽熱利用設備による補正集熱量
    # (1d-1)
    L_sun_b1_d_t[f1] = 0.0
    # (1d-2)
    L_sun_b1_d_t[f2] = L_sun_total_d_t[f2] * ((r_sun_b1_d_t[f2] * L_dash_b1_d_t[f2]) / Q_W_dmd_sun_d_t[f2])

    # 1時間当たりの浴槽自動湯はり時における太陽熱利用設備による補正集熱量
    # (1e-1)
    L_sun_b2_d_t[f1] = 0.0
    # (1e-2)
    L_sun_b2_d_t[f2] = L_sun_total_d_t[f2] * ((r_sun_b2_d_t[f2] * L_dash_b2_d_t[f2]) / Q_W_dmd_sun_d_t[f2])

    # 1時間当たりの浴槽水栓さし湯時における太陽熱利用設備による補正集熱量
    # (1f-1)
    L_sun_ba1_d_t[f1] = 0.0
    # (1f-2)
    L_sun_ba1_d_t[f2] = L_sun_total_d_t[f2] * ((r_sun_ba1_d_t[f2] * L_dash_ba1_d_t[f2]) / Q_W_dmd_sun_d_t[f2])

    return L_sun_k_d_t, L_sun_s_d_t, L_sun_w_d_t, L_sun_b1_d_t, L_sun_b2_d_t, L_sun_ba1_d_t


# ============================================================================
# O.3 給湯熱需要のうちの太陽熱利用設備の分担分
# ============================================================================

def get_Q_W_dmd_sun_d_t(L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                        r_sun_k_d_t, r_sun_s_d_t, r_sun_w_d_t, r_sun_b1_d_t, r_sun_b2_d_t, r_sun_ba1_d_t):
    """給湯熱需要のうちの太陽熱利用設備の分担分 (MJ/h) (2)

    Args:
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷（MJ/h）
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷（MJ/h）
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷（MJ/h）
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷（MJ/h）
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における節湯補正給湯熱負荷（MJ/h）
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷（MJ/h）
      r_sun_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合（-）
      r_sun_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合（-）
      r_sun_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合（-）
      r_sun_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合（-）
      r_sun_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合（-）
      r_sun_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合（-）

    Returns:
      ndarray: 給湯熱需要のうちの太陽熱利用設備の分担分 (MJ/h)
    """
    return r_sun_k_d_t * L_dash_k_d_t + r_sun_s_d_t * L_dash_s_d_t + r_sun_w_d_t * L_dash_w_d_t + \
            r_sun_b1_d_t * L_dash_b1_d_t + r_sun_b2_d_t * L_dash_b2_d_t + r_sun_ba1_d_t * L_dash_ba1_d_t


# ============================================================================
# O.4 節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合
# ============================================================================

def get_r_sun(hw_connection_type, solar_device, solar_water_tap, Theta_w_sun_d_t, Theta_sw_s,
                  L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t):
    """各用途における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合 (-)

    Args:
      supplied_target_d_t(ndarray): 太陽熱利用設備により供給される熱を利用する水栓等 (str)

    Returns:
      tuple: 各用途における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合 (-)
    """
    table_3 = get_table_3()

    # 太陽熱利用設備により供給される熱を利用する水栓等
    if solar_device == '液体集熱式':
        supplied_target = get_swh_supplied_target(hw_connection_type, solar_water_tap, Theta_w_sun_d_t, Theta_sw_s, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t)
    elif solar_device == '空気集熱式':
        supplied_target = get_open_swh_supplied_target()
    else:
        raise ValueError(solar_device)

    # 「太陽熱利用設備により供給される熱を利用する水栓等」を、表3のインデックスに変換
    if supplied_target == '全ての水栓等':
        supplied_target = 0
    elif supplied_target == '浴室シャワー水栓':
        supplied_target = 1
    elif supplied_target == '浴槽湯張り':
        supplied_target = 2
    else:
        raise ValueError(supplied_target)

    r_sun_k = table_3[supplied_target, 0]
    r_sun_s = table_3[supplied_target, 1]
    r_sun_w = table_3[supplied_target, 2]
    r_sun_b1 = table_3[supplied_target, 3]
    r_sun_b2 = table_3[supplied_target, 4]
    r_sun_ba1 = table_3[supplied_target, 5]

    return r_sun_k, r_sun_s, r_sun_w, r_sun_b1, r_sun_b2, r_sun_ba1


def get_table_3():
    """表3 各用途における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合

    Args:

    Returns:
      ndarray: 各用途における節湯補正給湯熱負荷に対する太陽熱利用設備の分担割合
    """
    return np.array([
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
    ])


# ============================================================================
# O.5 液体集熱式太陽熱利用設備
# ============================================================================

# ============================================================================
# O.5.2 浴槽湯張りの方法
# ============================================================================

def get_swh_bathtub_filling_method_d_t(hw_connection_type, L_sun_total_d_t):
    """液体集熱式太陽熱利用設備 : 浴槽湯張りの方法

    Args:
      hw_connection_type(str): 給湯接続方式の種類 (-)
      L_sun_total_d_t(ndarray): 1時間当たりの太陽熱利用給湯設備による補正集熱量の総量 (MJ/h)

    Returns:
      ndarray: 液体集熱式太陽熱利用設備 : 浴槽湯張りの方法
    """
    swh_bathtub_filling_method_d_t = np.full(24 * 365, None)

    if hw_connection_type in ["接続ユニット方式", "三方弁方式", "給水予熱方式"]:
        swh_bathtub_filling_method_d_t[:] = "給湯機で温度調整して浴槽湯張りを行う"
    elif hw_connection_type == "浴槽落とし込み方式":
        # 1時間当たりの太陽熱利用給湯設備による補正集熱量の総量がゼロである場合
        f1 = L_sun_total_d_t == 0
        swh_bathtub_filling_method_d_t[f1] = "給湯機で温度調整して浴槽湯張りを行う"

        # 1時間当たりの太陽熱利用給湯設備による補正集熱量の総量がゼロを超える場合
        f2 = L_sun_total_d_t > 0
        swh_bathtub_filling_method_d_t[f2] = "給湯機を経由せずに浴槽に落とした中温水に対して浴槽水栓さし湯または浴槽追焚を行うことで浴槽湯張りを行う"
    else:
        raise ValueError(hw_connection_type)

    return swh_bathtub_filling_method_d_t


# ============================================================================
# O.5.3 太陽熱利用設備により供給される熱を利用する水栓等
# ============================================================================

def get_swh_supplied_target(hw_connection_type, solar_water_tap, Theta_w_sun_d_t, Theta_sw_s, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t):
    """液体集熱式太陽熱利用設備 : 太陽熱利用設備により供給される熱を利用する水栓等

    Args:
      hw_connection_type(str): 給湯接続方式の種類 (-)
      solar_water_tap(str): 太陽熱用水栓 (-)
      Theta_w_sun_d_t(ndarray): 太陽熱利用設備から供給される水の温度
      Theta_sw_s(int): 浴室シャワー水栓における基準給湯温度
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はり時における節湯補正給湯熱負荷（MJ/h）
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はり時における節湯補正給湯熱負荷（MJ/h）
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯時における節湯補正給湯熱負荷（MJ/h）

    Returns:
      str: 液体集熱式太陽熱利用設備 : 太陽熱利用設備により供給される熱を利用する水栓等
    """
    if hw_connection_type in ["接続ユニット方式", "三方弁方式", "給水予熱方式"]:
        return "全ての水栓等"
    elif hw_connection_type == "浴槽落とし込み方式":
        if solar_water_tap == "シャワー・浴槽水栓":
            # 1時間当たりの浴槽湯はり時における節湯補正給湯熱負荷の合計がゼロであり、かつ日付の時刻における太陽熱利用設備から供給される水の温度が浴室シャワー水栓における基準給湯温度以上である場合
            if L_dash_b1_d_t + L_dash_b2_d_t + L_dash_ba1_d_t == 0 and Theta_w_sun_d_t >= Theta_sw_s:
                return "浴室シャワー水栓"
            # 1時間当たりの浴槽湯はり時における節湯補正給湯熱負荷の合計がゼロであり、かつ日付の時刻における太陽熱利用設備から供給される水の温度が浴室シャワー水栓における基準給湯温度以上である場合に該当しない場合
            else:
                return "浴槽湯張り"
        elif solar_water_tap == "浴槽水栓":
            return "浴槽湯張り"
        else:
            raise ValueError(solar_water_tap)
    else:
        raise ValueError(hw_connection_type)


# ============================================================================
# O.6 空気集熱式太陽熱利用設備
# ============================================================================

# ============================================================================
# O.6.2 浴槽湯張りの方法
# ============================================================================

def get_open_swh_bathtub_filling_method_d_t():
    """空気集熱式太陽熱利用設備 : 浴槽湯張りの方法

    Args:

    Returns:
      ndarray: 空気集熱式太陽熱利用設備 : 浴槽湯張りの方法
    """
    return np.full(24 * 365, "給湯機で温度調整して浴槽湯張りを行う")


# ============================================================================
# O.6.3 太陽熱利用設備により供給される熱を利用する水栓等
# ============================================================================

def get_open_swh_supplied_target():
    """空気集熱式太陽熱利用設備 : 太陽熱利用設備により供給される熱を利用する水栓等

    Args:

    Returns:
      str: 空気集熱式太陽熱利用設備 : 太陽熱利用設備により供給される熱を利用する水栓等
    """
    return "全ての水栓等"
