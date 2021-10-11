# ============================================================================
# 付録 G 電気ヒートポンプ・ガス瞬間式併用型給湯温水暖房機
#       （給湯熱源：電気ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式）
# ============================================================================

import numpy as np
import pandas as pd

from pyhees.section7_1_c import \
    get_e_k_d, \
    get_e_s_d, \
    get_e_w_d, \
    get_e_b1_d, \
    get_e_b2_d, \
    get_e_ba1_d, \
    get_e_ba2_d, \
    get_f_hs


# ============================================================================
# G.3 試験された値を用いる方法
# ============================================================================


# ============================================================================
# G.3.3 ハイブリッド給湯機の仕様
# ============================================================================

# ハイブリッド給湯機の仕様一覧を読み込む
def load_specification(filename):
    """

    Args:
      filename: ファイル名

    Returns:

    """
    global csv
    csv = pd.read_csv(filename, encoding='Shift_JIS')


# ハイブリッド給湯機の仕様を取得する
def get_specification(package_id):
    """

    Args:
      package_id: パッケージID

    Returns:
      ハイブリッド給湯機の仕様

    """
    list = csv[csv['NO'] == int(package_id)]
    data = list.values[0, 12:25]
    return {
        'a_HP': data[0],
        'b_HP': data[1],
        'a_TU': data[2],
        'b_TU': data[3],
        'e_HP_std_m7': data[4],
        'e_HP_std_2': data[5],
        'e_HP_std_7': data[6],
        'e_HP_std_25': data[7],
        'Q_HP_max': data[8],
        'etr_loss_TU': data[9],
        'Theta_ex_min_HP': data[10],
        'e_BB_jis': data[11],
        # 'R_day': data[12]
        #TODO: 読込方法は要検討
        'R_day': 0.5
    }


# 直接指定されたハイブリッド給湯機のパラメーターを取得する
def get_input_specification(hybrid_param):
    """

    Args:
      hybrid_param: ハイブリッド給湯機のパラメーター

    Returns:
      ハイブリッド給湯機のパラメーター

    """
    return {
        'a_HP': hybrid_param['a_HP'],
        'a_TU': hybrid_param['a_TU'],
        'b_HP': hybrid_param['b_HP'],
        'b_TU': hybrid_param['b_TU'],
        'e_HP_std_m7': hybrid_param['e_HP_std_m7'],
        'e_HP_std_2': hybrid_param['e_HP_std_2'],
        'e_HP_std_7': hybrid_param['e_HP_std_7'],
        'e_HP_std_25': hybrid_param['e_HP_std_25'],
        'Q_HP_max': hybrid_param['Q_HP_max'],
        'etr_loss_TU': hybrid_param['etr_loss_TU'],
        'Theta_ex_min_HP': hybrid_param['Theta_ex_min_HP'],
        'e_BB_jis': hybrid_param['e_BB_jis'],
        'R_day': hybrid_param['R_day']
    }

# ============================================================================
# G.3.4 消費電力量
# ============================================================================

# 1日当たりの給湯機の消費電量量 (8)
def calc_E_E_hs_d_t(bath_function, package_id, hybrid_param, theta_ex_d_Ave_d, L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t,
                    L_dashdash_b1_d_t, L_dashdash_b2_d_t, L_dashdash_ba1_d_t, L_dashdash_ba2_d_t, W_dash_ba1_d_t):
    """

    Args:
      bath_function: param package_id:
      hybrid_param: param theta_ex_d_Ave_d:
      L_dashdash_k_d_t: param L_dashdash_s_d_t:
      L_dashdash_w_d_t: param L_dashdash_b1_d_t:
      L_dashdash_b2_d_t: param L_dashdash_ba1_d_t:
      L_dashdash_ba2_d_t: param W_dash_ba1_d_t:
      package_id: 
      theta_ex_d_Ave_d: 
      L_dashdash_s_d_t: 
      L_dashdash_b1_d_t: 
      L_dashdash_ba1_d_t: 
      W_dash_ba1_d_t: 

    Returns:

    """
    # ハイブリッド給湯機の仕様
    if package_id != None:
        # 試験された値を用いる場合
        spec = get_specification(package_id)
    else:
        # パラメーターが直接指定された場合
        spec = get_input_specification(hybrid_param)

    # 1時間当たりの太陽熱補正給湯熱負荷 (MJ/h)
    L_dashdash_d_t = get_L_dashdash_d_t(L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t, L_dashdash_b1_d_t,
                                        L_dashdash_b2_d_t, L_dashdash_ba1_d_t)

    # 1日当たりの太陽熱補正給湯熱負荷 (MJ/d)
    L_dashdash_d = get_L_dashdash_d(L_dashdash_d_t)

    # 1日当たりの電気ヒートポンプが分担する給湯熱負荷 (MJ/d)
    L_HP_d = get_L_HP_d(spec['Theta_ex_min_HP'], spec['a_HP'], spec['b_HP'], spec['etr_loss_TU'], spec['Q_HP_max'],
                        L_dashdash_d, theta_ex_d_Ave_d)

    # 1日当たりの電気ヒートポンプの加熱量 (MJ/d)
    Q_HP_d = get_Q_HP_d(L_HP_d, spec['etr_loss_TU'])

    # 電気ヒートポンプの日平均熱効率 (-)
    e_HP_d = get_e_HP_d(spec['e_HP_std_m7'], spec['e_HP_std_2'], spec['e_HP_std_7'], spec['e_HP_std_25'], theta_ex_d_Ave_d)

    # 1時間当たりの電気ヒートポンプの消費電力量 (kWh/h)
    E_E_hs_HP_d_t = get_E_E_hs_HP_d_t(Q_HP_d, e_HP_d, spec['R_day'], L_dashdash_d, L_dashdash_d_t)

    # 1時間当たりのタンクユニットの消費電力量 (kWh/h)
    E_E_hs_TU_d_t = get_E_E_hs_TU_d_t(spec['a_TU'], spec['b_TU'], L_dashdash_d, L_dashdash_d_t)

    # 1時間当たりの保温時における消費電力量 (kWh/h)
    L_dashdash_ba2_d = get_L_dashdash_ba2_d(L_dashdash_ba2_d_t)
    L_BB_ba2_d = get_L_BB_ba2_d(L_dashdash_ba2_d)
    L_BB_ba2_d_t = get_L_BB_ba2_d_t(L_dashdash_ba2_d_t)
    E_E_hs_BB_d_t = get_E_E_hs_BB_d_t(W_dash_ba1_d_t, L_BB_ba2_d, L_BB_ba2_d_t, bath_function)

    print('E_E_hs_HP = {}'.format(np.sum(E_E_hs_HP_d_t)))
    print('E_E_hs_TU = {}'.format(np.sum(E_E_hs_TU_d_t)))
    print('E_E_hs_BB = {}'.format(np.sum(E_E_hs_BB_d_t)))

    return E_E_hs_HP_d_t + E_E_hs_TU_d_t + E_E_hs_BB_d_t


# 1時間当たりの電気ヒートポンプ消費電力量 (kWh/h)  (9-1) (9-2)
def get_E_E_hs_HP_d_t(Q_HP_d, e_HP_d, R_day, L_dashdash_d, L_dashdash_d_t):
    """

    Args:
      Q_HP_d: 1日当たりの電気ヒートポンプの過熱量 (MJ/d)
      e_HP_d: 電気ヒートポンプの日平均熱効率 (-)
      R_day: ヒートポンプ昼間沸上率（-）
      L_dashdash_d: 1日当たりの太陽熱補正給湯熱負荷 (MJ/d)
      L_dashdash_d_t: 1時間当たりの太陽熱補正給湯熱負荷 (MJ/h)

    Returns:
      1時間当たりの電気ヒートポンプ消費電力量 (kWh/h)

    """
    E_E_hs_HP_d_t = np.zeros(24 * 365)

    # 24時間化
    L_dashdash_d = np.repeat(L_dashdash_d, 24)
    e_HP_d = np.repeat(e_HP_d, 24)
    Q_HP_d = np.repeat(Q_HP_d, 24)

    # ヒートポンプ昼間沸上運転開始時刻
    t_bw_start = get_t_bw_start()

    # ヒートポンプ昼間沸上運転終了時刻
    t_bw_end = get_t_bw_end()

    # t_bw_start <= t < t_bw_end の場合 (9-1)
    t1 = np.tile(np.logical_and(t_bw_start <= np.arange(24), np.arange(24) < t_bw_end), 365)

    E_E_hs_HP_d_t[t1] = Q_HP_d[t1] / (3.6 * e_HP_d[t1]) * R_day * (1 / (t_bw_end - t_bw_start))

    # 0 <= t < t_bw_start または　t_bw_end <= t < 24 の場合 (9-2)
    t2 = np.tile(np.logical_or(np.logical_and(0 <= np.arange(24), np.arange(24) < t_bw_start),
                               np.logical_and(t_bw_end <= np.arange(24), np.arange(24) < 24)), 365)

    t3 = np.tile(np.logical_and(t_bw_start <= np.arange(24), np.arange(24) < t_bw_end - 1), 365)

    temp = L_dashdash_d_t.copy()
    temp[t2] = 0.0
    L_dashdash_d_t_start_end = np.repeat(np.sum(temp.reshape((365, 24)), axis=1), 24)

    f1 = L_dashdash_d != L_dashdash_d_t_start_end

    f2 = np.logical_and(t2, f1)

    E_E_hs_HP_d_t[f2] = Q_HP_d[f2] / (3.6 * e_HP_d[f2]) * (1 - R_day) * \
                        (L_dashdash_d_t[f2] / (L_dashdash_d[f2] - L_dashdash_d_t_start_end[f2]))

    return E_E_hs_HP_d_t


def get_t_bw_start():
    """ヒートポンプ昼間沸上運転開始時刻

    Args:

    Returns:
      int: ヒートポンプ昼間沸上運転開始時刻

    """
    return 9


def get_t_bw_end():
    """ヒートポンプ昼間沸上運転終了時刻

    Args:

    Returns:
      int: ヒートポンプ昼間沸上運転終了時刻

    """
    return 16


# 1時間当たりのタンクユニットの消費電力量 (10)
def get_E_E_hs_TU_d_t(a_TU, b_TU, L_dashdash_d, L_dashdash_d_t):
    """

    Args:
      a_TU: param b_TU:
      L_dashdash_d: param L_dashdash_d_t:
      b_TU: 
      L_dashdash_d_t: 

    Returns:

    """
    E_E_hs_TU_d_t = np.zeros(24 * 365)

    # L_dashdash_d_t > 0
    f1 = L_dashdash_d_t > 0
    E_E_hs_TU_d_t[f1] = a_TU * L_dashdash_d_t[f1] + b_TU / 24

    # L_dashdash_d = 0
    f2 = L_dashdash_d_t == 0
    E_E_hs_TU_d_t[f2] = b_TU / 24

    return E_E_hs_TU_d_t


# 1日当たりの保温時における消費電力量 (11)
def get_E_E_hs_BB_d_t(W_dash_ba1_d_t, L_BB_ba2_d, L_BB_ba2_d_t, bath_function):
    """

    Args:
      W_dash_ba1_d_t: param L_BB_ba2_d:
      L_BB_ba2_d_t: param bath_function:
      L_BB_ba2_d: 
      bath_function: 

    Returns:

    """
    if bath_function == '給湯単機能' or bath_function == 'ふろ給湯機(追焚なし)':
        # (11a)
        return (0.000393 * W_dash_ba1_d_t * 10 ** 3 / 3600)
    elif bath_function == 'ふろ給湯機(追焚あり)':
        # (11b)
        L_BB_ba2_d = np.repeat(L_BB_ba2_d, 24)
        E_E_hs_BB_d_t = np.zeros(24 * 365)

        fb1 = L_BB_ba2_d > 0
        E_E_hs_BB_d_t[fb1] = ((0.01723 * L_BB_ba2_d[fb1] + 0.06099) * 10 ** 3 / 3600) \
                             * L_BB_ba2_d_t[fb1] / L_BB_ba2_d[fb1]

        fb2 = L_BB_ba2_d == 0
        E_E_hs_BB_d_t[fb2] = 0

        return E_E_hs_BB_d_t
    else:
        raise ValueError(bath_function)


# ============================================================================
# G.3.5 ガス消費量
# ============================================================================

# 1日当たりの給湯機のガス消費量 (12)
def get_E_G_hs_d_t(bath_function, package_id, theta_ex_d_Ave_d, L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t,
                   L_dashdash_b1_d_t, L_dashdash_b2_d_t, L_dashdash_ba1_d_t, L_dashdash_ba2_d_t, W_dash_ba1_d_t, hybrid_param):
    """

    Args:
      bath_function: param package_id:
      theta_ex_d_Ave_d: param L_dashdash_k_d_t:
      L_dashdash_s_d_t: param L_dashdash_w_d_t:
      L_dashdash_b1_d_t: param L_dashdash_b2_d_t:
      L_dashdash_ba1_d_t: param L_dashdash_ba2_d_t:
      W_dash_ba1_d_t: param hybrid_param:
      package_id: 
      L_dashdash_k_d_t: 
      L_dashdash_w_d_t: 
      L_dashdash_b2_d_t: 
      L_dashdash_ba2_d_t: 
      hybrid_param: 

    Returns:

    """
    # ハイブリッド給湯機の仕様
    if package_id != None:
        # 試験された値を用いる場合
        spec = get_specification(package_id)
    else:
        # パラメーターが直接指定された場合
        spec = get_input_specification(hybrid_param)

    # 当該給湯機に対する効率の補正係数
    f_hs = get_f_hs(spec['e_BB_jis'])

    L_dashdash_d_t = get_L_dashdash_d_t(
        L_dashdash_k_d_t=L_dashdash_k_d_t,
        L_dashdash_s_d_t=L_dashdash_s_d_t,
        L_dashdash_w_d_t=L_dashdash_w_d_t,
        L_dashdash_b1_d_t=L_dashdash_b1_d_t,
        L_dashdash_b2_d_t=L_dashdash_b2_d_t,
        L_dashdash_ba1_d_t=L_dashdash_ba1_d_t,
    )
    L_dashdash_k_d = get_L_dashdash_k_d(L_dashdash_k_d_t)
    L_dashdash_s_d = get_L_dashdash_s_d(L_dashdash_s_d_t)
    L_dashdash_w_d = get_L_dashdash_w_d(L_dashdash_w_d_t)
    L_dashdash_b1_d = get_L_dashdash_b1_d(L_dashdash_b1_d_t)
    L_dashdash_b2_d = get_L_dashdash_b2_d(L_dashdash_b2_d_t)
    L_dashdash_ba1_d = get_L_dashdash_ba1_d(L_dashdash_ba1_d_t)
    L_dashdash_ba2_d = get_L_dashdash_ba1_d(L_dashdash_ba2_d_t)
    L_dashdash_d = get_L_dashdash_d(L_dashdash_d_t)

    L_HP = get_L_HP_d(
        Theta_ex_min_HP=spec['Theta_ex_min_HP'],
        a_HP=spec['a_HP'],
        b_HP=spec['b_HP'],
        etr_loss_TU=spec['etr_loss_TU'],
        Q_HP_max=spec['Q_HP_max'],
        L_dashdash_d=L_dashdash_d,
        theta_ex_d_Ave_d=theta_ex_d_Ave_d
    )
    L_BB_k_d = get_L_BB_k_d(L_HP, L_dashdash_d, L_dashdash_k_d)
    L_BB_s_d = get_L_BB_s_d(L_HP, L_dashdash_d, L_dashdash_s_d)
    L_BB_w_d = get_L_BB_w_d(L_HP, L_dashdash_d, L_dashdash_w_d)
    L_BB_b1_d = get_L_BB_b1_d(L_HP, L_dashdash_d, L_dashdash_b1_d)
    L_BB_b2_d = get_L_BB_b2_d(L_HP, L_dashdash_d, L_dashdash_b2_d)
    L_BB_ba1_d = get_L_BB_ba1_d(L_HP, L_dashdash_d, L_dashdash_ba1_d)
    L_BB_ba2_d = get_L_BB_ba2_d(L_dashdash_ba2_d)

    L_BB_k_d_t = get_L_BB_k_d_t(L_BB_k_d, L_dashdash_k_d_t)
    L_BB_s_d_t = get_L_BB_s_d_t(L_BB_s_d, L_dashdash_s_d_t)
    L_BB_w_d_t = get_L_BB_w_d_t(L_BB_w_d, L_dashdash_w_d_t)
    L_BB_b1_d_t = get_L_BB_b1_d_t(L_BB_b1_d, L_dashdash_b1_d_t)
    L_BB_b2_d_t = get_L_BB_b2_d_t(L_BB_b2_d, L_dashdash_b2_d_t)
    L_BB_ba1_d_t = get_L_BB_ba1_d_t(L_BB_ba1_d, L_dashdash_ba1_d_t)
    L_BB_ba2_d_t = get_L_BB_ba2_d_t(L_dashdash_ba2_d_t)

    # 日平均給湯機効率
    e_BB_k_d = get_e_k_d(theta_ex_d_Ave_d, L_BB_k_d, L_BB_w_d, f_hs)
    e_BB_s_d = get_e_s_d(theta_ex_d_Ave_d, L_BB_s_d, f_hs)
    e_BB_w_d = get_e_w_d(theta_ex_d_Ave_d, L_BB_k_d, L_BB_w_d, f_hs)

    if bath_function == '給湯単機能':

        # 日平均給湯機効率
        e_BB_b1_d = get_e_b1_d(theta_ex_d_Ave_d, L_BB_b1_d, f_hs)
        e_BB_ba1_d = get_e_ba1_d(theta_ex_d_Ave_d, L_BB_ba1_d, f_hs)

        # (12a)
        E_G_hs_d_t = L_BB_k_d_t / np.repeat(e_BB_k_d, 24) \
                     + L_BB_s_d_t / np.repeat(e_BB_s_d, 24) \
                     + L_BB_w_d_t / np.repeat(e_BB_w_d, 24) \
                     + L_BB_b1_d_t / np.repeat(e_BB_b1_d, 24) \
                     + L_BB_ba1_d_t / np.repeat(e_BB_ba1_d, 24)
    elif bath_function == 'ふろ給湯機(追焚なし)':

        # 日平均給湯機効率
        e_BB_b2_d = get_e_b2_d(theta_ex_d_Ave_d, L_BB_b2_d, f_hs)
        e_BB_ba1_d = get_e_ba1_d(theta_ex_d_Ave_d, L_BB_ba1_d, f_hs)

        # (12b)
        E_G_hs_d_t = L_BB_k_d_t / np.repeat(e_BB_k_d, 24) \
                     + L_BB_s_d_t / np.repeat(e_BB_s_d, 24) \
                     + L_BB_w_d_t / np.repeat(e_BB_w_d, 24) \
                     + L_BB_b2_d_t / np.repeat(e_BB_b2_d, 24) \
                     + L_BB_ba1_d_t / np.repeat(e_BB_ba1_d, 24)
    elif bath_function == 'ふろ給湯機(追焚あり)':

        # 日平均給湯機効率
        e_BB_b2_d = get_e_b2_d(theta_ex_d_Ave_d, L_BB_b2_d, f_hs)
        e_BB_ba2_d = get_e_ba2_d(theta_ex_d_Ave_d, L_BB_ba2_d, f_hs)

        # (12c)
        E_G_hs_d_t = L_BB_k_d_t / np.repeat(e_BB_k_d, 24) \
                     + L_BB_s_d_t / np.repeat(e_BB_s_d, 24) \
                     + L_BB_w_d_t / np.repeat(e_BB_w_d, 24) \
                     + L_BB_b2_d_t / np.repeat(e_BB_b2_d, 24) \
                     + L_BB_ba2_d_t / np.repeat(e_BB_ba2_d, 24)
    else:
        raise ValueError(bath_function)

    return E_G_hs_d_t


# ============================================================================
# G.3.6 電気ヒートポンプの加熱量
# ============================================================================

# 1日当たりの電気ヒートポンプの加熱量 (13)
def get_Q_HP_d(L_HP_d, etr_loss_TU):
    """

    Args:
      L_HP_d: param etr_loss_TU:
      etr_loss_TU: 

    Returns:

    """
    return L_HP_d / (1 - etr_loss_TU)


# ============================================================================
# G.3.7 電気ヒートポンプの日平均熱効率
# ============================================================================

# 電気ヒートポンプの日平均熱効率 (14)
def get_e_HP_d(e_HP_std_m7, e_HP_std_2, e_HP_std_7, e_HP_std_25, theta_ex_d_Ave_d):
    """

    Args:
      e_HP_std_m7: param e_HP_std_2:
      e_HP_std_7: param e_HP_std_25:
      theta_ex_d_Ave_d: 
      e_HP_std_2: 
      e_HP_std_25: 

    Returns:

    """
    e_HP_d = np.zeros(365)

    # 1) theta_ex_d_Ave_d < 2
    f1 = (theta_ex_d_Ave_d < 2)
    e_HP_d[f1] = e_HP_std_2 - (2 - theta_ex_d_Ave_d[f1]) / 9 * (e_HP_std_2 - e_HP_std_m7)

    # 2) 2 <= theta_ex_d_Ave_d < 7
    f2 = np.logical_and(2 <= theta_ex_d_Ave_d, theta_ex_d_Ave_d < 7)
    e_HP_d[f2] = e_HP_std_7 - (7 - theta_ex_d_Ave_d[f2]) / 5 * (e_HP_std_7 - e_HP_std_2)

    # 3) 7 <= theta_ex_d_Ave_d < 25
    f3 = np.logical_and(7 <= theta_ex_d_Ave_d, theta_ex_d_Ave_d < 25)
    e_HP_d[f3] = e_HP_std_25 - (25 - theta_ex_d_Ave_d[f3]) / 18 * (e_HP_std_25 - e_HP_std_7)

    # 4) 25 <= theta_ex_d_Ave_d
    f4 = 25 <= theta_ex_d_Ave_d
    e_HP_d[f4] = e_HP_std_25

    return e_HP_d


# ============================================================================
# G.3.8 給湯熱負荷
# ============================================================================

# バックアップボイラーが分担する給湯熱負荷

# (15a)
def get_L_BB_k_d_t(L_BB_k_d, L_dashdash_k_d_t):
    """

    Args:
      L_BB_k_d: param L_dashdash_k_d_t:
      L_dashdash_k_d_t: 

    Returns:

    """
    L_BB_k_d_t = np.zeros(24 * 365)

    L_BB_k_d = np.repeat(L_BB_k_d, 24)
    L_dashdash_k_d = np.repeat(get_L_dashdash_k_d(L_dashdash_k_d_t), 24)

    f = L_dashdash_k_d > 0
    L_BB_k_d_t[f] = L_BB_k_d[f] * L_dashdash_k_d_t[f] / L_dashdash_k_d[f]

    return L_BB_k_d_t


# (15b)
def get_L_BB_s_d_t(L_BB_s_d, L_dashdash_s_d_t):
    """

    Args:
      L_BB_s_d: param L_dashdash_s_d_t:
      L_dashdash_s_d_t: 

    Returns:

    """
    L_BB_s_d_t = np.zeros(24 * 365)

    L_BB_s_d = np.repeat(L_BB_s_d, 24)
    L_dashdash_s_d = np.repeat(get_L_dashdash_s_d(L_dashdash_s_d_t), 24)

    f = L_dashdash_s_d > 0
    L_BB_s_d_t[f] = L_BB_s_d[f] * L_dashdash_s_d_t[f] / L_dashdash_s_d[f]

    return L_BB_s_d_t


# (15c)
def get_L_BB_w_d_t(L_BB_w_d, L_dashdash_w_d_t):
    """

    Args:
      L_BB_w_d: param L_dashdash_w_d_t:
      L_dashdash_w_d_t: 

    Returns:

    """
    L_BB_w_d_t = np.zeros(24 * 365)

    L_BB_w_d = np.repeat(L_BB_w_d, 24)
    L_dashdash_w_d = np.repeat(get_L_dashdash_w_d(L_dashdash_w_d_t), 24)

    f = L_dashdash_w_d > 0
    L_BB_w_d_t[f] = L_BB_w_d[f] * L_dashdash_w_d_t[f] / L_dashdash_w_d[f]

    return L_BB_w_d_t


# (15d)
def get_L_BB_b1_d_t(L_BB_b1_d, L_dashdash_b1_d_t):
    """

    Args:
      L_BB_b1_d: param L_dashdash_b1_d_t:
      L_dashdash_b1_d_t: 

    Returns:

    """
    L_BB_b1_d_t = np.zeros(24 * 365)

    L_BB_b1_d = np.repeat(L_BB_b1_d, 24)
    L_dashdash_b1_d = np.repeat(get_L_dashdash_b1_d(L_dashdash_b1_d_t), 24)

    f = L_dashdash_b1_d > 0
    L_BB_b1_d_t[f] = L_BB_b1_d[f] * L_dashdash_b1_d_t[f] / L_dashdash_b1_d[f]

    return L_BB_b1_d_t


# (15e)
def get_L_BB_b2_d_t(L_BB_b2_d, L_dashdash_b2_d_t):
    """

    Args:
      L_BB_b2_d: param L_dashdash_b2_d_t:
      L_dashdash_b2_d_t: 

    Returns:

    """
    L_BB_b2_d_t = np.zeros(24 * 365)

    L_BB_b2_d = np.repeat(L_BB_b2_d, 24)
    L_dashdash_b2_d = np.repeat(get_L_dashdash_b2_d(L_dashdash_b2_d_t), 24)

    f = L_dashdash_b2_d > 0
    L_BB_b2_d_t[f] = L_BB_b2_d[f] * L_dashdash_b2_d_t[f] / L_dashdash_b2_d[f]

    return L_BB_b2_d_t


# (15f)
def get_L_BB_ba1_d_t(L_BB_ba1_d, L_dashdash_ba1_d_t):
    """

    Args:
      L_BB_ba1_d: param L_dashdash_ba1_d_t:
      L_dashdash_ba1_d_t: 

    Returns:

    """
    L_BB_ba1_d_t = np.zeros(24 * 365)

    L_BB_ba1_d = np.repeat(L_BB_ba1_d, 24)
    L_dashdash_ba1_d = np.repeat(get_L_dashdash_ba1_d(L_dashdash_ba1_d_t), 24)

    f = L_dashdash_ba1_d > 0
    L_BB_ba1_d_t[f] = L_BB_ba1_d[f] * L_dashdash_ba1_d_t[f] / L_dashdash_ba1_d[f]

    return L_BB_ba1_d_t


# (15g)
def get_L_BB_ba2_d_t(L_dashdash_ba2_d_t):
    """

    Args:
      L_dashdash_ba2_d_t: 

    Returns:

    """
    return L_dashdash_ba2_d_t


# (16a)
def get_L_BB_k_d(L_HP_d, L_dashdash_d, L_dashdash_k_d):
    """

    Args:
      L_HP_d: param L_dashdash_d:
      L_dashdash_k_d: 
      L_dashdash_d: 

    Returns:

    """
    return L_dashdash_k_d - L_HP_d * (L_dashdash_k_d / L_dashdash_d)


# (16b)
def get_L_BB_s_d(L_HP_d, L_dashdash_d, L_dashdash_s_d):
    """

    Args:
      L_HP_d: param L_dashdash_d:
      L_dashdash_s_d: 
      L_dashdash_d: 

    Returns:

    """
    return L_dashdash_s_d - L_HP_d * (L_dashdash_s_d / L_dashdash_d)


# (16c)
def get_L_BB_w_d(L_HP_d, L_dashdash_d, L_dashdash_w_d):
    """

    Args:
      L_HP_d: param L_dashdash_d:
      L_dashdash_w_d: 
      L_dashdash_d: 

    Returns:

    """
    return L_dashdash_w_d - L_HP_d * (L_dashdash_w_d / L_dashdash_d)


# (16d)
def get_L_BB_b1_d(L_HP_d, L_dashdash_d, L_dashdash_b1_d):
    """

    Args:
      L_HP_d: param L_dashdash_d:
      L_dashdash_b1_d: 
      L_dashdash_d: 

    Returns:

    """
    return L_dashdash_b1_d - L_HP_d * (L_dashdash_b1_d / L_dashdash_d)


# (16e)
def get_L_BB_b2_d(L_HP_d, L_dashdash_d, L_dashdash_b2_d):
    """

    Args:
      L_HP_d: param L_dashdash_d:
      L_dashdash_b2_d: 
      L_dashdash_d: 

    Returns:

    """
    return L_dashdash_b2_d - L_HP_d * (L_dashdash_b2_d / L_dashdash_d)


# (16f)
def get_L_BB_ba1_d(L_HP_d, L_dashdash_d, L_dashdash_ba1_d):
    """

    Args:
      L_HP_d: param L_dashdash_d:
      L_dashdash_ba1_d: 
      L_dashdash_d: 

    Returns:

    """
    return L_dashdash_ba1_d - L_HP_d * (L_dashdash_ba1_d / L_dashdash_d)


# (16g)
def get_L_BB_ba2_d(L_dashdash_ba2_d):
    """

    Args:
      L_dashdash_ba2_d: 

    Returns:

    """
    return L_dashdash_ba2_d


# ============================================================================
# G.4 1日当たり／1時間当たりの太陽熱補正給湯熱負荷
# ============================================================================


# 1日当たりの電気ヒートポンプが分担する給湯熱負荷 (17)
def get_L_HP_d(Theta_ex_min_HP, a_HP, b_HP, etr_loss_TU, Q_HP_max, L_dashdash_d, theta_ex_d_Ave_d):
    """

    Args:
      Theta_ex_min_HP: param a_HP:
      b_HP: param etr_loss_TU:
      Q_HP_max: param L_dashdash_d:
      theta_ex_d_Ave_d: 
      a_HP: 
      etr_loss_TU: 
      L_dashdash_d: 

    Returns:

    """
    L_HP_d = np.zeros(365)

    # 1. theta_ex_d_Ave_d >= Theta_ex_min_HP (17a)
    f1 = (theta_ex_d_Ave_d >= Theta_ex_min_HP)
    L_HP_d[f1] = np.clip(
        (a_HP * L_dashdash_d[f1] + b_HP) * (1 - etr_loss_TU),
        None,
        np.clip(L_dashdash_d[f1], None, Q_HP_max * (1 - etr_loss_TU))
    )

    # 2. theta_ex_d_Ave_d < Theta_ex_min_HP (17b)
    f2 = (theta_ex_d_Ave_d < Theta_ex_min_HP)
    L_HP_d[f2] = 0

    return L_HP_d


# 1日当たりの太陽熱補正給湯熱負荷 (MJ/d) (18)
def get_L_dashdash_d(L_dashdash_d_t):
    """

    Args:
      L_dashdash_d_t: 1時間当たりの太陽熱補正給湯熱負荷 (MJ/h)

    Returns:
      1日当たりの太陽熱補正給湯熱負荷 (MJ/d)

    """
    return np.sum(L_dashdash_d_t.reshape(365, 24), axis=1)


# 1時間当たりの太陽熱補正給湯熱負荷 (MJ/h) (19)
def get_L_dashdash_d_t(L_dashdash_k_d_t, L_dashdash_s_d_t, L_dashdash_w_d_t, L_dashdash_b1_d_t, L_dashdash_b2_d_t,
                       L_dashdash_ba1_d_t):
    """

    Args:
      L_dashdash_k_d_t: 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)
      L_dashdash_s_d_t: 1時間当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_w_d_t: 1時間当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_b2_d_t: 1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h)
      L_dashdash_ba1_d_t: 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      1時間当たりの太陽熱補正給湯熱負荷 (MJ/h)

    """
    return L_dashdash_k_d_t \
           + L_dashdash_s_d_t \
           + L_dashdash_w_d_t \
           + L_dashdash_b1_d_t \
           + L_dashdash_b2_d_t \
           + L_dashdash_ba1_d_t


# 1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)
def get_L_dashdash_k_d(L_dashdash_k_d_t):
    """

    Args:
      L_dashdash_k_d_t: 1時間当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/h)

    Returns:
      1日当たりの台所水栓における太陽熱補正給湯熱負荷 (MJ/d)

    """
    return np.sum(L_dashdash_k_d_t.reshape((365, 24)), axis=1)


# 1日当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/d)
def get_L_dashdash_s_d(L_dashdash_s_d_t):
    """

    Args:
      L_dashdash_s_d_t: 1時間当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      1日当たりの浴室シャワー水栓における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_s_d_t.reshape((365, 24)), axis=1)


# 1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)
def get_L_dashdash_w_d(L_dashdash_w_d_t):
    """

    Args:
      L_dashdash_w_d_t: 1時間当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      1日当たりの洗面水栓における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_w_d_t.reshape((365, 24)), axis=1)


# 1日当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/d)
def get_L_dashdash_b1_d(L_dashdash_b1_d_t):
    """

    Args:
      L_dashdash_b1_d_t: 1時間当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      1日当たりの浴槽水栓湯はり時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_b1_d_t.reshape((365, 24)), axis=1)


# 1日当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/d)
def get_L_dashdash_b2_d(L_dashdash_b2_d_t):
    """

    Args:
      L_dashdash_b2_d_t: 1時間当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      1日当たりの浴槽自動湯はり時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_b2_d_t.reshape((365, 24)), axis=1)


# 1日当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/d)
def get_L_dashdash_ba1_d(L_dashdash_ba1_d_t):
    """

    Args:
      L_dashdash_ba1_d_t: 1時間当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      1日当たりの浴槽水栓さし湯時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_ba1_d_t.reshape((365, 24)), axis=1)


# 1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)
def get_L_dashdash_ba2_d(L_dashdash_ba2_d_t):
    """

    Args:
      L_dashdash_ba2_d_t: 1時間当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/h)

    Returns:
      1日当たりの浴槽追焚時における太陽熱補正給湯負荷 (MJ/d)

    """
    return np.sum(L_dashdash_ba2_d_t.reshape((365, 24)), axis=1)
