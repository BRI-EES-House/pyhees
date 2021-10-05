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

    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :param ls_type: 液体集熱式太陽熱利用設備の種類 (太陽熱温水器,ソーラーシステム)
    :type ls_type: str
    :param A_sp: 太陽熱集熱部の有効集熱面積 (m2)
    :type A_sp: float
    :param P_alpha_sp: 太陽熱集熱部の方位角 (°)
    :type P_alpha_sp: float
    :param P_beta_sp: 太陽熱集熱部の傾斜角 (°)
    :type P_beta_sp: float
    :param W_tnk_ss: タンク容量 (L)
    :type W_tnk_ss: float
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :param L_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_k_d_t: ndarray
    :param L_dash_s_d_t: 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_s_d_t: ndarray
    :param L_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_w_d_t: ndarray
    :param L_dash_b1_d_t: 1時間当たりの浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b1_d_t: ndarray
    :param L_dash_b2_d_t: 1時間当たりの浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b2_d_t: ndarray
    :param L_dash_ba1_d_t: 1時間当たりの浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_ba1_d_t: ndarray
    :return: 1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/h)
    :rtype: ndarray
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

    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :param ls_type: 液体集熱式太陽熱利用設備の種類 (太陽熱温水器,ソーラーシステム)
    :type ls_type: str
    :param pmp_type: ソーラーシステムの循環ポンプの種類 (省消費電力型,上記以外の機種)
    :type pmp_type: str
    :param P_alpha_sp: 太陽熱集熱部の方位角 (°)
    :type P_alpha_sp: float
    :param P_beta_sp: 太陽熱集熱部の傾斜角 (°)
    :type P_beta_sp: float
    :return: 1日当たりの補機の消費電力量 (kWh/d)
    :rtype: ndarray
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

    :param Q_sh_d: 1日当たりの基準集熱量 (MJ/h)
    :type Q_sh_d: ndarray
    :param L_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_k_d_t: ndarray
    :param L_dash_s_d_t: 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_s_d_t: ndarray
    :param L_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_w_d_t: ndarray
    :param L_dash_b1_d_t: 1時間当たりの浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b1_d_t: ndarray
    :param L_dash_b2_d_t: 1時間当たりの浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b2_d_t: ndarray
    :param L_dash_ba1_d_t: 1時間当たりの浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_ba1_d_t: ndarray
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :return: 1時間当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/h)
    :rtype: ndarray
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

    :param Q_sh_d: 1日当たりの基準集熱量 (MJ/d)
    :type Q_sh_d: ndarray
    :param L_dash_k_d: 台所水栓における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_k_d: ndarray
    :param L_dash_s_d: 浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_s_d: ndarray
    :param L_dash_w_d: 洗面水栓における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_w_d: ndarray
    :param L_dash_b1_d: 浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_b1_d: ndarray
    :param L_dash_b2_d: 浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_b2_d: ndarray
    :param L_dash_ba1_d: 浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_ba1_d: ndarray
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :return: 1日当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/d)
    :rtype: ndarray
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

    :return: 液体集熱式太陽熱利用設備を使用できる外気温度の下限
    :rtype: float
    """
    return 5.0


def get_f_sr_uplim_sh():
    """ 液体集熱式太陽熱利用設備の分担率上限値

    :return: 液体集熱式太陽熱利用設備の分担率上限値
    :rtype: float
    """
    return 0.9


# ============================================================================
# 6.2 基準集熱量
# ============================================================================

def calc_Q_sh_d(A_sp_sh, P_alpha_sp_sh, P_beta_sp_sh, region, sol_region):
    """1日当たりの基準集熱量 (5)

    :param A_sp_sh: 太陽熱集熱部の有効集熱面積 (m2)
    :type A_sp_sh: float
    :param P_alpha_sp_sh: 太陽熱集熱部設置面の方位角
    :type P_alpha_sp_sh: float
    :param P_beta_sp_sh: 太陽熱集熱部設置面の傾斜角
    :type P_beta_sp_sh: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :return: 1日当たりの基準集熱量 (MJ/d)
    :rtype: ndarray
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

    :return:太陽熱集熱部の集熱効率
    :rtype: float
    """
    return 0.4


def get_f_s_sh():
    """液体集熱式太陽熱利用設備のシステム効率

    :return: 液体集熱式太陽熱利用設備のシステム効率
    :rtype: float
    """
    return 0.85


def get_A_sp_sh_JIS_A_4111(A):
    """太陽熱集熱部の有効集熱面積(IS A 4111)

    :param A: 太陽熱集熱部総面積
    :type A: float
    :return: 太陽熱集熱部の有効集熱面積
    :rtype: float
    """
    return A * 0.85


def calc_Q_sp_sh_d(P_alpha_sp_sh, P_beta_sp_sh, region, sol_region):
    """1日当たりの太陽熱集熱部設置面の単位面積当たりの日射量 (6)

    :param P_alpha_sp_sh: 太陽熱集熱部設置面の方位角
    :type P_alpha_sp_sh: float
    :param P_beta_sp_sh: 太陽熱集熱部設置面の傾斜角
    :type P_beta_sp_sh: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :return: 1日当たりの太陽熱集熱部設置面の単位面積当たりの日射量 (MJ/(m2・d))
    :rtype: ndarray
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

    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :return: 期間平均太陽熱外気温度 (℃)
    :rtype: ndarray
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

    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :return: 日平均太陽熱外気温度 (℃)
    :rtype: ndarray
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

    :param Q_ss_d: 1日当たりの基準集熱量 (MJ/d)
    :type Q_ss_d: ndarray
    :param W_tnk_ss: ソーラーシステムのタンク容量 (L)
    :type W_tnk_ss: float
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :param L_dash_k_d_t: 1時間当たりの台所水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_k_d_t: ndarrayL
    :param L_dash_s_d_t: 1時間当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_s_d_t: ndarray
    :param L_dash_w_d_t: 1時間当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_w_d_t: ndarray
    :param L_dash_b1_d_t: 1時間当たりの浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b1_d_t: ndarray
    :param L_dash_b2_d_t: 1時間当たりの浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_b2_d_t: ndarray
    :param L_dash_ba1_d_t: 1時間当たりの浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/h)
    :type L_dash_ba1_d_t: ndarray
    :return: 1時間当たりの液体集熱式太陽熱利用設備による補正集熱量
    :rtype: ndarray
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

    :param Q_ss_d: 1日当たりの基準集熱量 (MJ/d)
    :type Q_ss_d: ndarray
    :param W_tnk_ss: ソーラーシステムのタンク容量 (L)
    :type W_tnk_ss: ndarray
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :param L_dash_k_d: 1日当たりの台所水栓における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_k_d: ndarray
    :param L_dash_s_d: 1日当たりの浴室シャワー水栓における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_s_d: ndarray
    :param L_dash_w_d: 1日当たりの洗面水栓における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_w_d: ndarray
    :param L_dash_b1_d: 1日当たりの浴槽水栓湯はりにおける節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_b1_d: ndarray
    :param L_dash_b2_d: 1日当たりの浴槽自動湯はりにおける節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_b2_d: ndarray
    :param L_dash_ba1_d: 1日当たりの浴槽水栓さし湯における節湯補正給湯熱負荷 (MJ/d)
    :type L_dash_ba1_d: ndarray
    :return: 1日当たりの液体集熱式太陽熱利用設備による補正集熱量 (MJ/d)
    :rtype: ndarray
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

    :return: 液体集熱式太陽熱利用設備の分担率上限値
    :rtype: float
    """
    return 0.9


def calc_L_tnk_ss_d(Q_ss_d, W_tnk_ss, Theta_wtr_d):
    """1日当たりのソーラーシステムのタンク蓄熱量の上限による補正集熱量 (11)

    :param Q_ss_d: 1日当たりの基準集熱量 (MJ/d)
    :type Q_ss_d: ndarray
    :param W_tnk_ss: ソーラーシステムのタンク容量 (L)
    :type W_tnk_ss: float
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :return: 1日当たりのソーラーシステムのタンク蓄熱量の上限による補正集熱量 (MJ/d)
    :rtype: ndarray
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

    :return: ソーラーシステムのタンク有効利用率 (-)
    :rtype: float
    """
    return 1.0


def get_HC_tnk_ss_d(W_tnk_ss, Theta_wtr_d):
    """ソーラーシステムのタンク蓄熱量 (12)

    :param W_tnk_ss: ソーラーシステムのタンク容量 (L)
    :type W_tnk_ss: float
    :param Theta_wtr_d: 日平均給水温度 (℃)
    :type Theta_wtr_d: ndarray
    :return: ソーラーシステムのタンク蓄熱量 (MJ)
    :rtype: ndarray
    """
    # ソーラーシステムのタンク内温度 (℃)
    Theta_tnk_ss = get_Theta_tnk_ss()

    # ソーラーシステムのタンク蓄熱量 (10)
    HC_tnk_ss_d = (Theta_tnk_ss - Theta_wtr_d) * W_tnk_ss * 4.186 * 10 ** (-3)

    return HC_tnk_ss_d


def get_Theta_tnk_ss():
    """ソーラーシステムのタンク内温度 (℃)

    :return: ソーラーシステムのタンク内温度 (℃)
    :rtype: float
    """
    return 65.0


# ============================================================================
# 7.2 基準集熱量
# ============================================================================

def calc_Q_ss_d(A_sp_ss, P_alpha_sp_ss, P_beta_sp_ss, region, sol_region):
    """1日当たりの基準集熱量 (13)

    :param A_sp_ss: ソーラーシステムの太陽熱集熱部の有効集熱面積 (m2)
    :type A_sp_ss: float
    :param P_alpha_sp_ss: ソーラーシステムの太陽熱集熱部の方位角 (°)
    :type P_alpha_sp_ss: float
    :param P_beta_sp_ss: ソーラーシステムの太陽熱集熱部の傾斜角 (°)
    :type P_beta_sp_ss: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :return: 1日当たりの基準集熱量 (MJ/d))
    :rtype: ndarray
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

    :return: 太陽熱集熱部の集熱効率 (-)
    :rtype: float
    """
    return 0.4


def get_f_s_ss():
    """液体集熱式太陽熱利用設備のシステム効率 (-)

    :return: 液体集熱式太陽熱利用設備のシステム効率 (-)
    :rtype: float
    """
    return 0.85


def get_A_sp_ss_JIS_A_4112(A):
    """太陽熱集熱部の有効集熱面積 (m2)

    :param A: 太陽熱集熱部総面積 (m2)
    :type A: float
    :return: 太陽熱集熱部の有効集熱面積 (m2)
    :rtype: float
    """
    return A * 0.85


def calc_Q_sp_ss_d(P_alpha_sp_ss, P_beta_sp_ss, region, sol_region):
    """1日当たりの太陽熱集熱部設置面の単位面積当たりの日射量 (MJ/(m2・d)) (14)

    :param P_alpha_sp_ss: ソーラーシステムの太陽熱集熱部の方位角 (°)
    :type P_alpha_sp_ss: float
    :param P_beta_sp_ss: ソーラーシステムの太陽熱集熱部の傾斜角 (°)
    :type P_beta_sp_ss: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :return: 1日当たりの太陽熱集熱部設置面の単位面積当たりの日射量 (MJ/(m2・d))
    :rtype: ndarray
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

    :param pmp_type: ソーラーシステムの循環ポンプの種類 (省消費電力型,上記以外の機種)
    :type pmp_type: str
    :param P_alpha_sp_ss: ソーラーシステムの太陽熱集熱部の方位角 (°)
    :type P_alpha_sp_ss: float
    :param P_beta_sp_ss: ソーラーシステムの太陽熱集熱部の傾斜角 (°)
    :type P_beta_sp_ss: float
    :param region: 省エネルギー地域区分
    :type region: int
    :param sol_region: 年間の日射地域区分
    :type sol_region: int
    :return: 1時間当たりのソーラーシステムの循環ポンプの消費電力量 (kWh/h)
    :rtype: ndarray
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

    :param pmp_type: ソーラーシステムの循環ポンプの種類 (省消費電力型,上記以外の機種)
    :type pmp_type: str
    :return: ソーラーシステムの循環ポンプの消費電力 (W)
    :rtype: float
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

    :param I_s_sp_ss_d_t: 傾斜面の単位面積当たりの平均日射量 (W/m2)
    :type I_s_sp_ss_d_t: ndarray
    :return: 1時間当たりのソーラーシステムの循環ポンプの稼働時間 (h/h)
    :rtype: ndarray
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

    :return: ソーラーシステムの循環ポンプが稼働する太陽熱集熱部設置面の単位面積当たりの日射量の下限 (W/2m)
    :rtype: float
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
