# ============================================================================
# 第九章 自然エネルギー利用設備
# 第二節 液体集熱式太陽熱利用設備
# Ver.08（エネルギー消費性能計算プログラム（住宅版）Ver.0203～）
# ============================================================================

import numpy as np
from pyhees.section11_2 import \
    load_solrad, \
    calc_I_s_d_t, \
    get_Theta_ex




# ============================================================================
# 5．全般
# ============================================================================

# ============================================================================
# 5.1 補正集熱量
# ============================================================================

def calc_L_sun_lss_d_t(region, sol_region, ls_type, A_sp, P_alpha_sp, P_beta_sp, W_tnk_ss, Theta_wtr_d, L_dash_k_d_t,
                       L_dash_s_d_t, L_dash_w_d_t,
                       L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t):
    """1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (1)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (太陽熱温水器,ソーラーシステム)
      A_sp(float): 太陽熱集熱部の有効集熱面積 (m2)
      P_alpha_sp(float): 太陽熱集熱部の方位角 (°)
      P_beta_sp(float): 太陽熱集熱部の傾斜角 (°)
      W_tnk_ss(float): タンク容量 (L)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/h)
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/h)
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/h)

    """
    if ls_type == '太陽熱温水器':
        # 採用する設備が太陽熱温水器の場合

        # 1日当たりの基準集熱量
        Q_sh_d = calc_Q_sh_d(
            A_sp_sh=A_sp,
            P_alpha_sp_sh=P_alpha_sp,
            P_beta_sp_sh=P_beta_sp,
            region=region,
            sol_region=sol_region
        )

        # 補正集熱量 (1-1)
        L_sun_lss_d_t = get_L_sun_lss_sh_d_t(
            Q_sh_d=Q_sh_d,
            L_dash_k_d_t=L_dash_k_d_t,
            L_dash_s_d_t=L_dash_s_d_t,
            L_dash_w_d_t=L_dash_w_d_t,
            L_dash_b1_d_t=L_dash_b1_d_t,
            L_dash_b2_d_t=L_dash_b2_d_t,
            L_dash_ba1_d_t=L_dash_ba1_d_t,
            region=region,
            sol_region=sol_region
        )

        return L_sun_lss_d_t
    elif ls_type == 'ソーラーシステム':
        # 採用する設備がソーラーシステムの場合

        # 1日当たりの基準集熱量
        Q_ss_d = calc_Q_ss_d(
            A_sp_ss=A_sp,
            P_alpha_sp_ss=P_alpha_sp,
            P_beta_sp_ss=P_beta_sp,
            region=region,
            sol_region=sol_region
        )

        # 補正集熱量 (1-2)
        L_sun_lss_d_t = calc_L_sun_lss_ss_d_t(
            Q_ss_d=Q_ss_d,
            W_tnk_ss=W_tnk_ss,
            Theta_wtr_d=Theta_wtr_d,
            L_dash_k_d_t=L_dash_k_d_t,
            L_dash_s_d_t=L_dash_s_d_t,
            L_dash_w_d_t=L_dash_w_d_t,
            L_dash_b1_d_t=L_dash_b1_d_t,
            L_dash_b2_d_t=L_dash_b2_d_t,
            L_dash_ba1_d_t=L_dash_ba1_d_t
        )

        return L_sun_lss_d_t
    else:
        raise ValueError(ls_type)


# ============================================================================
# 5.2 補機の消費電力量
# ============================================================================

def calc_E_E_lss_aux_d_t(region, sol_region, ls_type, pmp_type=None, P_alpha_sp=None, P_beta_sp=None):
    """1日当たりの補機の消費電力量 (2)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分
      ls_type(str): 液体集熱式太陽熱利用設備の種類 (太陽熱温水器,ソーラーシステム)
      pmp_type(str, optional): ソーラーシステムの循環ポンプの種類 (省消費電力型,上記以外の機種) (Default value = None)
      P_alpha_sp(float, optional): 太陽熱集熱部の方位角 (°) (Default value = None)
      P_beta_sp(float, optional): 太陽熱集熱部の傾斜角 (°) (Default value = None)

    Returns:
      ndarray: 1日当たりの補機の消費電力量 (kWh/d)

    """
    if ls_type == '太陽熱温水器':
        # 採用する説委が太陽熱温水器の場合 (2-1)
        E_E_lss_aux_d_t = np.zeros(24 * 365)
        return E_E_lss_aux_d_t
    elif ls_type == 'ソーラーシステム':
        # 採用する設備がソーラーシステムの場合
        # 1日当たりのソーラーシステムの循環ポンプの消費電力量 (2-2)
        E_E_lss_aux_d_t = calc_E_E_ss_cp_d_t(pmp_type, P_alpha_sp, P_beta_sp, region, sol_region)
        return E_E_lss_aux_d_t
    else:
        raise ValueError(ls_type)


# ============================================================================
# 6. 太陽熱温水器
# ============================================================================

# ============================================================================
# 6.1 補正集熱量
# ============================================================================

def get_L_sun_lss_sh_d_t(Q_sh_d, L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t, L_dash_b2_d_t, L_dash_ba1_d_t,
                         region,
                         sol_region):
    """1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/h) (3)

    Args:
      Q_sh_d(ndarray): 1日当たりの基準集熱量 (MJ/h)
      L_dash_k_d_t(ndarray): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/h)
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/h)
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/h)
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分

    Returns:
      ndarray: 1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/h)

    """
    # 24時間化
    L_dash_k_d = np.sum(L_dash_k_d_t.reshape((365, 24)), axis=1)
    L_dash_s_d = np.sum(L_dash_s_d_t.reshape((365, 24)), axis=1)
    L_dash_w_d = np.sum(L_dash_w_d_t.reshape((365, 24)), axis=1)
    L_dash_b1_d = np.sum(L_dash_b1_d_t.reshape((365, 24)), axis=1)
    L_dash_b2_d = np.sum(L_dash_b2_d_t.reshape((365, 24)), axis=1)
    L_dash_ba1_d = np.sum(L_dash_ba1_d_t.reshape((365, 24)), axis=1)

    # 1日当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/d) (4)
    L_sun_lss_ss_d = calc_L_sun_lss_sh_d(Q_sh_d, L_dash_k_d, L_dash_s_d, L_dash_w_d, L_dash_b1_d, L_dash_b2_d,
                                         L_dash_ba1_d, region,
                                         sol_region)

    # 24時間化
    L_dash_k_d = np.repeat(L_dash_k_d, 24)
    L_dash_s_d = np.repeat(L_dash_s_d, 24)
    L_dash_w_d = np.repeat(L_dash_w_d, 24)
    L_dash_b1_d = np.repeat(L_dash_b1_d, 24)
    L_dash_b2_d = np.repeat(L_dash_b2_d, 24)
    L_dash_ba1_d = np.repeat(L_dash_ba1_d, 24)

    L_sun_lss_ss_d = np.repeat(L_sun_lss_ss_d, 24)

    L_sun_lss_ss_d_t = np.zeros(24 * 365)

    # (9-1) 節湯補正給湯熱負荷が0の場合
    f1 = (L_dash_k_d + L_dash_s_d + L_dash_w_d + L_dash_b1_d + L_dash_b2_d + L_dash_ba1_d) == 0
    L_sun_lss_ss_d_t[f1] = 0

    # (9-2) 節湯補正給湯熱負荷 > 0の場合
    f2 = (L_dash_k_d + L_dash_s_d + L_dash_w_d + L_dash_b1_d + L_dash_b2_d + L_dash_ba1_d) > 0
    L_sun_lss_ss_d_t[f2] = (L_sun_lss_ss_d[f2]
                            * (L_dash_k_d_t[f2] + L_dash_s_d_t[f2] + L_dash_w_d_t[f2] + L_dash_b1_d_t[f2] +
                               L_dash_b2_d_t[f2] + L_dash_ba1_d_t[f2])
                            / (L_dash_k_d[f2] + L_dash_s_d[f2] + L_dash_w_d[f2] + L_dash_b1_d[f2] + L_dash_b2_d[f2] +
                               L_dash_ba1_d[f2]))

    return L_sun_lss_ss_d_t


def calc_L_sun_lss_sh_d(Q_sh_d, L_dash_k_d, L_dash_s_d, L_dash_w_d, L_dash_b1_d, L_dash_b2_d, L_dash_ba1_d, region,
                        sol_region):
    """1日当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/d) (4)

    Args:
      Q_sh_d(ndarray): 1日当たりの基準集熱量 (MJ/d)
      L_dash_k_d(ndarray): 台所水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dash_s_d(ndarray): 浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dash_w_d(ndarray): 洗面水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dash_b1_d(ndarray): 浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/d)
      L_dash_b2_d(ndarray): 浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/d)
      L_dash_ba1_d(ndarray): 浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/d)
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分

    Returns:
      ndarray: 1日当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/d)

    """
    # 期間平均太陽熱外気温度
    Theta_ex_s_prd_Ave_d = calc_Theta_ex_s_prd_Ave_d(region, sol_region)

    # 液体集熱式太陽熱利用設備を使用できる外気温度の下限
    Theta_ex_lwlim_sh = get_Theta_ex_lwlim_sh()

    # 液体集熱式太陽熱利用設備の分担率の上限値
    f_sr_uplim_sh = get_f_sr_uplim_sh()

    # Theta_ex_lwlim <= Theta_ex_s_prd_Ave_d の場合 (3-1)
    # ひとまず、条件を無視してすべての日について計算する
    L_sun_lss_sh_d = np.min(
        [Q_sh_d, (L_dash_k_d + L_dash_s_d + L_dash_w_d + L_dash_b1_d + L_dash_b2_d + L_dash_ba1_d) * f_sr_uplim_sh],
        axis=0)

    # Theta_ex_s_prd_Ave_d < Theta_ex_lwlim_sh の場合 (3-2)
    # この条件を満たす日だけ0で上書きする
    L_sun_lss_sh_d[Theta_ex_s_prd_Ave_d < Theta_ex_lwlim_sh] = 0.0

    return L_sun_lss_sh_d


def get_Theta_ex_lwlim_sh():
    """液体集熱式太陽熱利用設備を使用できる外気温度の下限

    Args:

    Returns:
      float: 液体集熱式太陽熱利用設備を使用できる外気温度の下限

    """
    return 5.0


def get_f_sr_uplim_sh():
    """液体集熱式太陽熱利用設備の分担率上限値

    Args:

    Returns:
      float: 液体集熱式太陽熱利用設備の分担率上限値

    """
    return 0.9


# ============================================================================
# 6.2 基準集熱量
# ============================================================================

def calc_Q_sh_d(A_sp_sh, P_alpha_sp_sh, P_beta_sp_sh, region, sol_region):
    """1日当たりの基準集熱量 (5)

    Args:
      A_sp_sh(float): 太陽熱集熱部の有効集熱面積 (m2)
      P_alpha_sp_sh(float): 太陽熱集熱部設置面の方位角
      P_beta_sp_sh(float): 太陽熱集熱部設置面の傾斜角
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分

    Returns:
      ndarray: 1日当たりの基準集熱量 (MJ/d)

    """
    # 1日当たりの太陽熱集熱部設置面の単位面積当たりの日射量
    Q_sp_sh_d = calc_Q_sp_sh_d(P_alpha_sp_sh, P_beta_sp_sh, region, sol_region)

    # 太陽熱集熱部の集熱効率
    f_sp_sh = get_f_sp_sh()

    # 液体集熱式太陽熱利用設備のシステム効率
    f_s_sh = get_f_s_sh()

    # 1日当たりの基準集熱量
    Q_sh_d = Q_sp_sh_d * A_sp_sh * f_sp_sh * f_s_sh

    return Q_sh_d


def get_f_sp_sh():
    """太陽熱集熱部の集熱効率

    Args:

    Returns:
      float: 太陽熱集熱部の集熱効率

    """
    return 0.4


def get_f_s_sh():
    """液体集熱式太陽熱利用設備のシステム効率

    Args:

    Returns:
      float: 液体集熱式太陽熱利用設備のシステム効率

    """
    return 0.85


def get_A_sp_sh_JIS_A_4111(A):
    """太陽熱集熱部の有効集熱面積(IS A 4111)

    Args:
      A(float): 太陽熱集熱部総面積

    Returns:
      float: 太陽熱集熱部の有効集熱面積

    """
    return A * 0.85


def calc_Q_sp_sh_d(P_alpha_sp_sh, P_beta_sp_sh, region, sol_region):
    """1日当たりの太陽熱集熱部設置面の単位面積当たりの日射量 (6)

    Args:
      P_alpha_sp_sh(float): 太陽熱集熱部設置面の方位角
      P_beta_sp_sh(float): 太陽熱集熱部設置面の傾斜角
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分

    Returns:
      ndarray: 1日当たりの太陽熱集熱部設置面の単位面積当たりの日射量 (MJ/(m2・d))

    """
    # 太陽熱集熱部設置面の単位面積当たりの平均日射量
    solrad = load_solrad(region, sol_region)
    I_s_sp_sh_d_t = calc_I_s_d_t(P_alpha_sp_sh, P_beta_sp_sh, solrad)

    # 1日当たりの太陽熱集熱部設置面の単位面積当たりの日射量
    tmp = I_s_sp_sh_d_t.reshape(365, 24)
    Q_sp_sh_d = np.sum(tmp, axis=1) * 3600 * 10 ** (-6)

    return Q_sp_sh_d


# ============================================================================
# 6.3 期間平均太陽熱外気温度
# ============================================================================

def calc_Theta_ex_s_prd_Ave_d(region, sol_region):
    """期間平均太陽熱外気温度 (7)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分

    Returns:
      ndarray: 期間平均太陽熱外気温度 (℃)

    """
    # 日平均太陽熱外気温度
    Theta_ex_s_Ave_d = calc_Theta_ex_s_Ave_d(region, sol_region)

    # 31日平均なので、データを前後15日ずつ拡張する
    tmp_ex = np.zeros(365 + 30)
    tmp_ex[:15] = Theta_ex_s_Ave_d[-15:]
    tmp_ex[15:15 + 365] = Theta_ex_s_Ave_d[:]
    tmp_ex[-15:] = Theta_ex_s_Ave_d[:15]

    # 31日平均
    # 基準日と前後15日の31日に1/31を乗算して合算する。
    tmp = np.convolve(tmp_ex, np.ones(31) / 31, mode='valid')

    return tmp


def calc_Theta_ex_s_Ave_d(region, sol_region):
    """日平均太陽熱外気温度 (8)

    Args:
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分

    Returns:
      ndarray: 日平均太陽熱外気温度 (℃)

    """

    # 太陽熱外気温度
    solrad = load_solrad(region, sol_region)
    Theta_ex_s_d = get_Theta_ex(solrad)

    tmp = Theta_ex_s_d.reshape(365, 24)
    tmp = np.sum(tmp, axis=1)

    Theta_ex_s_Ave_d = tmp / 24

    return Theta_ex_s_Ave_d


# ============================================================================
# 7. ソーラーシステム
# ============================================================================

# ============================================================================
# 7.1 補正集熱量
# ============================================================================


def calc_L_sun_lss_ss_d_t(Q_ss_d, W_tnk_ss, Theta_wtr_d, L_dash_k_d_t, L_dash_s_d_t, L_dash_w_d_t, L_dash_b1_d_t,
                          L_dash_b2_d_t,
                          L_dash_ba1_d_t):
    """1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (9)

    Args:
      Q_ss_d(ndarray): 1日当たりの基準集熱量 (MJ/d)
      W_tnk_ss(float): ソーラーシステムのタンク容量 (L)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)
      L_dash_k_d_t(ndarrayL): 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_s_d_t(ndarray): 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_w_d_t(ndarray): 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
      L_dash_b1_d_t(ndarray): 1時間当たりの浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/h)
      L_dash_b2_d_t(ndarray): 1時間当たりの浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/h)
      L_dash_ba1_d_t(ndarray): 1時間当たりの浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/h)

    Returns:
      ndarray: 1時間当たりの液体集熱式太陽熱利用設備による補正集熱量

    """
    # 24時間化
    L_dash_k_d = np.sum(L_dash_k_d_t.reshape((365, 24)), axis=1)
    L_dash_s_d = np.sum(L_dash_s_d_t.reshape((365, 24)), axis=1)
    L_dash_w_d = np.sum(L_dash_w_d_t.reshape((365, 24)), axis=1)
    L_dash_b1_d = np.sum(L_dash_b1_d_t.reshape((365, 24)), axis=1)
    L_dash_b2_d = np.sum(L_dash_b2_d_t.reshape((365, 24)), axis=1)
    L_dash_ba1_d = np.sum(L_dash_ba1_d_t.reshape((365, 24)), axis=1)

    # 1日当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/h) (10)
    L_sun_lss_ss_d = calc_L_sun_lss_ss_d(Q_ss_d, W_tnk_ss, Theta_wtr_d, L_dash_k_d, L_dash_s_d, L_dash_w_d, L_dash_b1_d,
                                         L_dash_b2_d, L_dash_ba1_d)
    L_sun_lss_ss_d = np.repeat(L_sun_lss_ss_d, 24)

    L_sun_lss_ss_d_t = np.zeros(24 * 365)

    # 24時間化
    L_dash_k_d = np.repeat(L_dash_k_d, 24)
    L_dash_s_d = np.repeat(L_dash_s_d, 24)
    L_dash_w_d = np.repeat(L_dash_w_d, 24)
    L_dash_b1_d = np.repeat(L_dash_b1_d, 24)
    L_dash_b2_d = np.repeat(L_dash_b2_d, 24)
    L_dash_ba1_d = np.repeat(L_dash_ba1_d, 24)

    # (9-1) 節湯補正給湯熱負荷が0の場合
    f1 = (L_dash_k_d + L_dash_s_d + L_dash_w_d + L_dash_b1_d + L_dash_b2_d + L_dash_ba1_d) == 0
    L_sun_lss_ss_d_t[f1] = 0

    # (9-2) 節湯補正給湯熱負荷 > 0の場合
    f2 = (L_dash_k_d + L_dash_s_d + L_dash_w_d + L_dash_b1_d + L_dash_b2_d + L_dash_ba1_d) > 0
    L_sun_lss_ss_d_t[f2] = (L_sun_lss_ss_d[f2]
                            * (L_dash_k_d_t[f2] + L_dash_s_d_t[f2] + L_dash_w_d_t[f2] + L_dash_b1_d_t[f2] +
                               L_dash_b2_d_t[f2] + L_dash_ba1_d_t[f2])
                            / (L_dash_k_d[f2] + L_dash_s_d[f2] + L_dash_w_d[f2] + L_dash_b1_d[f2] + L_dash_b2_d[f2] +
                               L_dash_ba1_d[f2]))

    return L_sun_lss_ss_d_t


def calc_L_sun_lss_ss_d(Q_ss_d, W_tnk_ss, Theta_wtr_d, L_dash_k_d, L_dash_s_d, L_dash_w_d, L_dash_b1_d, L_dash_b2_d,
                        L_dash_ba1_d):
    """1日当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/h) (10)

    Args:
      Q_ss_d(ndarray): 1日当たりの基準集熱量 (MJ/d)
      W_tnk_ss(ndarray): ソーラーシステムのタンク容量 (L)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)
      L_dash_k_d(ndarray): 1日当たりの台所水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dash_s_d(ndarray): 1日当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dash_w_d(ndarray): 1日当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/d)
      L_dash_b1_d(ndarray): 1日当たりの浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/d)
      L_dash_b2_d(ndarray): 1日当たりの浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/d)
      L_dash_ba1_d(ndarray): 1日当たりの浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/d)

    Returns:
      ndarray: 1日当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/d)

    """
    # 1日当たりのソーラーシステムのタンク蓄熱量の上限による補正集熱量
    L_tnk_ss_d = calc_L_tnk_ss_d(Q_ss_d, W_tnk_ss, Theta_wtr_d)

    # 液体集熱式太陽熱利用設備の分担率上限値
    f_sr_uplim_ss = get_f_sr_uplim_ss()

    # 1日当たりの液体集熱式太陽熱利用設備による補正集熱量 (8)
    L_sun_lss_ss_d = np.min(
        [L_tnk_ss_d, (L_dash_k_d + L_dash_s_d + L_dash_w_d + L_dash_b1_d + L_dash_b2_d + L_dash_ba1_d) * f_sr_uplim_ss],
        axis=0)

    return L_sun_lss_ss_d


def get_f_sr_uplim_ss():
    """液体集熱式太陽熱利用設備の分担率上限値

    Args:

    Returns:
      float: 液体集熱式太陽熱利用設備の分担率上限値

    """
    return 0.9


def calc_L_tnk_ss_d(Q_ss_d, W_tnk_ss, Theta_wtr_d):
    """1日当たりのソーラーシステムのタンク蓄熱量の上限による補正集熱量 (11)

    Args:
      Q_ss_d(ndarray): 1日当たりの基準集熱量 (MJ/d)
      W_tnk_ss(float): ソーラーシステムのタンク容量 (L)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: 1日当たりのソーラーシステムのタンク蓄熱量の上限による補正集熱量 (MJ/d)

    """
    # ソーラーシステムのタンク蓄熱量 (MJ)
    HC_tnk_ss_d = get_HC_tnk_ss_d(W_tnk_ss, Theta_wtr_d)

    # ソーラーシステムのタンク有効利用率 (-)
    alpha_tnk_ss_d = get_alpha_tnk_ss_d()

    # 1日当たりのソーラーシステムのタンク蓄熱量の上限による補正集熱量 (9)
    # Q_ss_d および HC_tnk_ss_d * alpha_tnk_ss_d の1日ごとの最小をとるために、axis=0を指定
    L_tnk_ss_d = np.min([Q_ss_d, HC_tnk_ss_d * alpha_tnk_ss_d], axis=0)

    return L_tnk_ss_d


def get_alpha_tnk_ss_d():
    """ソーラーシステムのタンク有効利用率 (-)

    Args:

    Returns:
      float: ソーラーシステムのタンク有効利用率 (-)

    """
    return 1.0


def get_HC_tnk_ss_d(W_tnk_ss, Theta_wtr_d):
    """ソーラーシステムのタンク蓄熱量 (12)

    Args:
      W_tnk_ss(float): ソーラーシステムのタンク容量 (L)
      Theta_wtr_d(ndarray): 日平均給水温度 (℃)

    Returns:
      ndarray: ソーラーシステムのタンク蓄熱量 (MJ)

    """
    # ソーラーシステムのタンク内温度 (℃)
    Theta_tnk_ss = get_Theta_tnk_ss()

    # ソーラーシステムのタンク蓄熱量 (10)
    HC_tnk_ss_d = (Theta_tnk_ss - Theta_wtr_d) * W_tnk_ss * 4.186 * 10 ** (-3)

    return HC_tnk_ss_d


def get_Theta_tnk_ss():
    """ソーラーシステムのタンク内温度 (℃)

    Args:

    Returns:
      float: ソーラーシステムのタンク内温度 (℃)

    """
    return 65.0


# ============================================================================
# 7.2 基準集熱量
# ============================================================================

def calc_Q_ss_d(A_sp_ss, P_alpha_sp_ss, P_beta_sp_ss, region, sol_region):
    """1日当たりの基準集熱量 (13)

    Args:
      A_sp_ss(float): ソーラーシステムの太陽熱集熱部の有効集熱面積 (m2)
      P_alpha_sp_ss(float): ソーラーシステムの太陽熱集熱部の方位角 (°)
      P_beta_sp_ss(float): ソーラーシステムの太陽熱集熱部の傾斜角 (°)
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分

    Returns:
      ndarray: 1日当たりの基準集熱量 (MJ/d))

    """
    # 1日当たりの太陽熱集熱部設置面の単位面積当たりの日射量
    Q_sp_ss_d = calc_Q_sp_ss_d(P_alpha_sp_ss, P_beta_sp_ss, region, sol_region)

    # 太陽熱集熱部の集熱効率
    f_sp_ss = get_f_sp_ss()

    # 液体集熱式太陽熱利用設備のシステム効率
    f_s_ss = get_f_s_ss()

    # 1日当たりの基準集熱量 (11)
    Q_ss_d = Q_sp_ss_d * A_sp_ss * f_sp_ss * f_s_ss

    return Q_ss_d


def get_f_sp_ss():
    """太陽熱集熱部の集熱効率 (-)

    Args:

    Returns:
      float: 太陽熱集熱部の集熱効率 (-)

    """
    return 0.4


def get_f_s_ss():
    """液体集熱式太陽熱利用設備のシステム効率 (-)

    Args:

    Returns:
      float: 液体集熱式太陽熱利用設備のシステム効率 (-)

    """
    return 0.85


def get_A_sp_ss_JIS_A_4112(A):
    """太陽熱集熱部の有効集熱面積 (m2)

    Args:
      A(float): 太陽熱集熱部総面積 (m2)

    Returns:
      float: 太陽熱集熱部の有効集熱面積 (m2)

    """
    return A * 0.85


def calc_Q_sp_ss_d(P_alpha_sp_ss, P_beta_sp_ss, region, sol_region):
    """1日当たりの太陽熱集熱部設置面の単位面積当たりの日射量 (MJ/(m2・d)) (14)

    Args:
      P_alpha_sp_ss(float): ソーラーシステムの太陽熱集熱部の方位角 (°)
      P_beta_sp_ss(float): ソーラーシステムの太陽熱集熱部の傾斜角 (°)
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分

    Returns:
      ndarray: 1日当たりの太陽熱集熱部設置面の単位面積当たりの日射量 (MJ/(m2・d))

    """
    # 太陽熱集熱部設置面の単位面積当たりの平均日射量
    solrad = load_solrad(region, sol_region)
    I_s_sp_ss_d_t = calc_I_s_d_t(P_alpha_sp_ss, P_beta_sp_ss, solrad)

    # 1日当たりの太陽熱集熱部設置面の単位面積当たりの日射量を求める
    # 8760時間が一次配列で与えられるので、365*24の2次配列へ並べ替える
    tmp = I_s_sp_ss_d_t.reshape(365, 24)

    # 配列の2次の軸(=各日24時間分)を加算する
    tmp = np.sum(tmp, axis=1)

    # 単位をWからMJへ換算する
    Q_sp_ss_d = tmp * 3600 * 10 ** (-6)

    return Q_sp_ss_d


# ============================================================================
# 7.3 循環ポンプの消費電力量
# ============================================================================

def calc_E_E_ss_cp_d_t(pmp_type, P_alpha_sp_ss, P_beta_sp_ss, region, sol_region):
    """1時間当たりのソーラーシステムの循環ポンプの消費電力量 (15)

    Args:
      pmp_type(str): ソーラーシステムの循環ポンプの種類 (省消費電力型,上記以外の機種)
      P_alpha_sp_ss(float): ソーラーシステムの太陽熱集熱部の方位角 (°)
      P_beta_sp_ss(float): ソーラーシステムの太陽熱集熱部の傾斜角 (°)
      region(int): 省エネルギー地域区分
      sol_region(int): 年間の日射地域区分

    Returns:
      ndarray: 1時間当たりのソーラーシステムの循環ポンプの消費電力量 (kWh/h)

    """
    # ソーラーシステムの循環ポンプの消費電力 (W)
    P_cp_ss = get_P_cp_ss(pmp_type)

    # 太陽熱集熱部設置面の単位面積当たりの平均日射量 (W/m2)
    solrad = load_solrad(region, sol_region)
    I_s_sp_ss_d_t = calc_I_s_d_t(P_alpha_sp_ss, P_beta_sp_ss, solrad)

    # 1時間当たりのソーラーシステムの循環ポンプの稼働時間
    t_cp_ss_d = get_t_cp_ss_d_t(I_s_sp_ss_d_t)

    return P_cp_ss * t_cp_ss_d * 10 ** (-3)


def get_P_cp_ss(pmp_type):
    """ソーラーシステムの循環ポンプの消費電力

    Args:
      pmp_type(str): ソーラーシステムの循環ポンプの種類 (省消費電力型,上記以外の機種)

    Returns:
      float: ソーラーシステムの循環ポンプの消費電力 (W)

    """
    # 表3 ソーラーシステムの循環ポンプの消費電力の値と適用条件
    table_3 = (40.0, 80.0)

    if pmp_type == '省消費電力型':
        return table_3[0]
    elif pmp_type == '上記以外の機種':
        return table_3[1]
    else:
        raise ValueError(pmp_type)


# ============================================================================
# 7.4 循環ポンプの稼働時間
# ============================================================================


def get_t_cp_ss_d_t(I_s_sp_ss_d_t):
    """1時間当たりのソーラーシステムの循環ポンプの稼働時間 (h/h) (16)

    Args:
      I_s_sp_ss_d_t(ndarray): 傾斜面の単位面積当たりの平均日射量 (W/m2)

    Returns:
      ndarray: 1時間当たりのソーラーシステムの循環ポンプの稼働時間 (h/h)

    """
    # ソーラーシステムの循環ポンプが稼働する太陽熱集熱部設置面の単位面積当たりの日射量の下限
    I_s_lwlim_cp_ss = get_I_s_lwlim_cp_ss()

    # 1時間当たりのソーラーシステムの循環ポンプの稼働時間の計算領域を確保
    t_cp_ss_d_t = np.zeros(24 * 365, dtype=np.int32)

    # I_s_lwlim_cp_ss <= I_s_sp_ss_d_t の場合
    f1 = I_s_lwlim_cp_ss <= I_s_sp_ss_d_t
    t_cp_ss_d_t[f1] = 1  # (15-1)

    # I_s_sp_ss_d_t < I_s_lwlim_cp_ss  の場合
    f2 = I_s_sp_ss_d_t < I_s_lwlim_cp_ss
    t_cp_ss_d_t[f2] = 0  # (15-2)

    return t_cp_ss_d_t


def get_I_s_lwlim_cp_ss():
    """ソーラーシステムの循環ポンプが稼働する太陽熱集熱部設置面の単位面積当たりの日射量の下限 (W/2m)

    Args:

    Returns:
      float: ソーラーシステムの循環ポンプが稼働する太陽熱集熱部設置面の単位面積当たりの日射量の下限 (W/2m)

    """
    return 150.0


if __name__ == '__main__':
    from section11_2 import load_solrad

    solrad = load_solrad(6, 3)

    # ********** 太陽熱温水器 **********

    # 補正集熱量
    L_sun_lss_d = calc_L_sun_lss_d_t('太陽熱温水器', 2.0, 0.1, 0.2, 150, np.ones(365), np.ones(365), np.ones(365),
                                     np.ones(365),
                                     np.ones(365), np.ones(365), np.ones(365), solrad)

    # 補機の消費電力量
    E_E_lss_aux_d = calc_E_E_lss_aux_d_t('太陽熱温水器', '省消費電力型', 0.1, 0.2, solrad)

    print('太陽熱温水器')
    print('L_sun_lss = {}'.format(np.sum(L_sun_lss_d)))
    print('E_E_lss_aux = {}'.format(np.sum(E_E_lss_aux_d)))

    # ********** ソーラーシステム **********

    # 補正集熱量
    L_sun_lss_d = calc_L_sun_lss_d_t('ソーラーシステム', 2.0, 0.1, 0.2, 150, np.ones(365), np.ones(365), np.ones(365),
                                     np.ones(365), np.ones(365), np.ones(365), np.ones(365), solrad)

    # 補機の消費電力量
    E_E_lss_aux_d = calc_E_E_lss_aux_d_t('ソーラーシステム', '省消費電力型', 0.1, 0.2, solrad)

    print('ソーラーシステム')
    print('L_sun_lss = {}'.format(np.sum(L_sun_lss_d)))
    print('E_E_lss_aux = {}'.format(np.sum(E_E_lss_aux_d)))
