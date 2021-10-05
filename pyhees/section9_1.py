# ============================================================================
# 第九章 自然エネルギー利用設備
# 第一節 太陽光発電設備
# Ver.06（エネルギー消費性能計算プログラム（住宅版）Ver.02.04～）
# ============================================================================


import numpy as np

from pyhees.section11_2 import \
    get_Theta_ex, \
    calc_I_s_d_t


# ============================================================================
# 5. 太陽光発電設備による発電量
# ============================================================================


def calc_E_E_PV_d_t(pv_list, df):
    """太陽光発電設備の発電量 (1)

    :param pv_list: 太陽光発電設備のリスト
    :type pv_list: list
    :param df: load_solrad の返り値
    :type df: DateFrame
    :return: 日付dの時tにおける 1 時間当たりの太陽光発電設備による発電量（kWh/h）
    :rtype: ndarray
    """

    if pv_list is not None:
        return np.sum([calc_E_p_i_d_t(**pv, df=df) for pv in pv_list], axis = 0)
    else:
        return np.zeros(24 * 365)


# ============================================================================
# 6. 太陽電池アレイによる発電量
# ============================================================================


def calc_E_p_i_d_t(P_p_i, P_alpha, P_beta, df, pv_type, pv_setup, etr_IN_r):
    """太陽電池アレイの発電量 (2)

    :param P_p_i: 太陽電池アレイiのシステム容量（kW）
    :type P_p_i: float
    :param P_alpha: 方位角 (°)
    :type P_alpha: float
    :param P_beta: 傾斜角 (°)
    :type P_beta: float
    :param df: load_solrad の返り値
    :type df: DateFrame
    :param pv_type: 太陽電池アレイの種類
    :type pv_type: str
    :param pv_setup: 太陽電池アレイ設置方式
    :type pv_setup: str
    :param etr_IN_r: パワーコンディショナの定格負荷効率
    :type etr_IN_r: float
    :return: 日付dの時刻tにおける 1 時間当たりの太陽電池アレイiの発電量
    :rtype: ndarray
    """

    # 基準状態の日射強度
    alpha_p = get_alpha_p()

    # 設置面の単位面積当たりの日射量
    I_s_i_d_t = calc_I_s_d_t(P_alpha, P_beta, df)

    # 外気温度
    Theta_A_d_t = get_Theta_A_d_t(df)

    # 総合設計係数
    K_p_i_d_t = calc_K_p_i_d_t(pv_type, pv_setup, etr_IN_r, Theta_A_d_t, I_s_i_d_t)

    return P_p_i * (1/alpha_p) * I_s_i_d_t * K_p_i_d_t * 10**(-3)


# ============================================================================
# 7. 太陽電池アレイのシステム容量
# ============================================================================


# ============================================================================
# 8. 基準状態の日射強度
# ============================================================================


def get_alpha_p():
    """基準状態の日射強度

    :return: 基準状態の日射強度
    :rtype: float
    """
    return 1.0


# ============================================================================
# 9. 太陽電池アレイの総合設計係数
# ============================================================================


def calc_K_p_i_d_t(pv_type, pv_setup, etr_IN_R, Theta_A_d_t, I_s_i_d_t):
    """太陽電池アレイの総合設計係数 (3)

    :param pv_type: 太陽電池アレイの種類
    :type pv_type: str
    :param pv_setup: 太陽電池アレイ設置方式
    :type pv_setup: str
    :param etr_IN_R: パワーコンディショナの定格負荷効率
    :type etr_IN_R: float
    :param Theta_A_d_t: 日付dの時刻tにおける外気温度（℃）
    :type Theta_A_d_t: ndarray
    :param I_s_i_d_t: 日付dの時刻tにおける太陽電池アレイiの設置面の単位面積当たりの日射量（W/m2）
    :type I_s_i_d_t: ndarray
    :return: 太陽電池アレイの総合設計係数
    :rtype: ndarray
    """

    # 日陰補正係数, 啓示変化補正係数, アレイ負荷整合補正係数, アレイ回路補正係数
    if pv_type == '結晶シリコン系':
        K_HS_i = get_table_4()[0][0]
        K_PD_i = get_table_4()[1][0]
        K_PA_i = get_table_4()[2][0]
        K_PM_i = get_table_4()[3][0]
    elif pv_type == '結晶シリコン系以外':
        K_HS_i = get_table_4()[0][1]
        K_PD_i = get_table_4()[1][1]
        K_PA_i = get_table_4()[2][1]
        K_PM_i = get_table_4()[3][1]
    else:
        raise NotImplementedError()

    # 太陽電池アレイの温度補正係数
    K_PT_i_d_t = calc_K_PT_i_d_t(pv_type, pv_setup, Theta_A_d_t, I_s_i_d_t)
    
    # インバータ回路補正係数
    K_IN = get_K_IN(etr_IN_R)

    return K_HS_i * K_PD_i * K_PT_i_d_t * K_PA_i * K_PM_i * K_IN


def get_table_4():
    """表 4 太陽電池アレイの補正係数の値

    :return: 表 4 太陽電池アレイの補正係数の値
    :rtype: list
    """
    table_4 = [
        (1.0, 1.0),
        (0.96, 0.99),
        (0.94, 0.94),
        (0.97, 0.97)
    ]
    return table_4

def get_K_IN(etr_IN_R):
    """インバータ回路補正係数 (4)

    :param etr_IN_R: パワーコンディショナの定格負荷効率
    :type etr_IN_R: float
    :return: インバータ回路補正係数
    :rtype: float
    """
    return etr_IN_R * 0.97


def calc_K_PT_i_d_t(pv_type, pv_setup, Theta_A_d_t, I_s_i_d_t):
    """太陽電池アレイの温度補正係数 (5)

    :param pv_type: 太陽電池アレイの種類
    :type pv_type: str
    :param pv_setup: 太陽電池アレイ設置方式
    :type pv_setup: str
    :param Theta_A_d_t: 日付dの時刻tにおける外気温度（℃）
    :type Theta_A_d_t: ndarray
    :param I_s_i_d_t: 日付dの時刻tにおける太陽電池アレイiの設置面の単位面積当たりの日射量（W/m2）
    :type I_s_i_d_t: ndarray
    :return: 日付dの時刻tにおける太陽電池アレイiの温度補正係数
    :rtype: ndarray
    """

    #最大出力温度係数
    if pv_type == '結晶シリコン系':
        alpha_p_max_i = get_table_5()[0][0]
    elif pv_type == '結晶シリコン系以外':
        alpha_p_max_i = get_table_5()[0][1]
    else:
        raise NotImplementedError()

    #加重平均太陽電池モジュール温度
    Theta_CR_i_d_t = get_Theta_CR_i_d_t(pv_setup, Theta_A_d_t, I_s_i_d_t)

    return 1 + alpha_p_max_i * (Theta_CR_i_d_t - 25)


def get_table_5():
    """表 5 太陽電池アレイの最大出力温度係数

    :return: 表 5 太陽電池アレイの最大出力温度係数
    :rtype: list
    """
    table_5 = [
        (-0.0041, -0.0020)
    ]

    return table_5

def get_Theta_CR_i_d_t(pv_setup, Theta_A_d_t, I_s_i_d_t):
    """加重平均太陽電池モジュール温度 (6)

    :param pv_setup: 太陽電池アレイ設置方式
    :type pv_setup: str
    :param Theta_A_d_t: 日付dの時刻tにおける外気温度（℃）
    :type Theta_A_d_t: ndarray
    :param I_s_i_d_t: 日付dの時刻tにおける太陽電池アレイiの設置面の単位面積当たりの日射量（W/m2）
    :type I_s_i_d_t: ndarray
    :return: 日付dの時刻tにおける太陽電池アレイiの加重平均太陽電池モジュール温度
    :rtype: ndarray
    """

    # 係数 f_A, f_B
    if pv_setup == '架台設置型':
        f_A_i = get_table_6()[0][0]
        f_B_i = get_table_6()[0][1]
    elif pv_setup == '屋根置き型':
        f_A_i = get_table_6()[1][0]
        f_B_i = get_table_6()[1][1]
    elif pv_setup == 'その他':
        f_A_i = get_table_6()[2][0]
        f_B_i = get_table_6()[2][1]
    else:
        raise NotImplementedError()

    # 太陽電池アレイの接地面における風速
    V_i_d_t = get_V_i_d_t()

    return Theta_A_d_t + (f_A_i/(f_B_i * V_i_d_t**0.8 + 1)+2) * I_s_i_d_t * 10**(-3) - 2

def get_Theta_A_d_t(df):
    """外気温度

    :param df: load_solrad の返り値
    :type df: DateFrame
    :return: 外気温度
    :rtype: ndarray
    """
    return get_Theta_ex(df)


def get_V_i_d_t():
    """太陽電池アレイの接地面における風速

    :return: 太陽電池アレイの接地面における風速
    :rtype: ndarray
    """
    return 1.5


def get_table_6():
    """表6 係数f_A及びf_Bの値

    :return: 表6 係数f_A及びf_Bの値
    :rtype: list
    """
    table_6 = [
        (46, 0.41),
        (50, 0.38),
        (57, 0.33)
    ]
    return  table_6

if __name__ == "__main__":
    from section11_2 import load_solrad
    from math import pi

    def convert(case):

        spec = {
            #省エネルギー基準地域区分
            'region': case['env_chiki'],

            #年間の日射地域区分
            'sol_region': case['bsc_solarlv'],
        }

        #定格負荷効率
        if case['pv_pcs_koritsu'] in [2, '2']:
            etr_IN_r = float(case['pv_pcs_koritsu_e']) / 100
        else:
            etr_IN_r = 0.927

        panel_list = []
        n = int(case['pv_panelsuu'])
        for i in range(1,n+1):
            panel = {
                'P_p_i': float(case['pv_panel{}_youryo'.format(i)]),
                'etr_IN_r': etr_IN_r
            }

            # 太陽電池アレイの種類
            if case['pv_panel{}_shurui'.format(i)] in [1,'1']:
                panel['pv_type'] = '結晶シリコン系'
            elif case['pv_panel{}_shurui'.format(i)] in [2,'2']:
                panel['pv_type'] = '結晶シリコン系以外'
            else:
                raise ValueError(case['pv_panel{}_shurui'.format(i)])
            
            # 太陽電池アレイ設置方式
            if case['pv_panel{}_setti'.format(i)] in [1,'1']:
                panel['pv_setup'] = '架台設置型'
            elif case['pv_panel{}_setti'.format(i)] in [2,'2']:
                panel['pv_setup'] = '屋根置き型'
            elif case['pv_panel{}_setti'.format(i)] in [3,'3']:
                panel['pv_setup'] = 'その他'
            else:
                raise ValueError(case['pv_panel{}_setti'.format(i)])

            # パネル設置方位（方位角）
            Pa = int(case['pv_panel{}_houi'.format(i)])
            if Pa == 0:
                panel['P_alpha'] = 0.0
            else:
                panel['P_alpha'] = (float(13-Pa) * 30) * pi / 180

            # パネル設置角度（傾斜角
            panel['P_beta'] = ((float(case['pv_panel{}_keisha'.format(i)])-1) * 10) * pi / 180

            panel_list.append(panel)
        
        spec['panel_list'] = panel_list
        
        return spec

    import pandas as pd

    records = pd.read_csv('PV_A.txt', encoding='Shift_JIS').to_dict(orient='records')
    for record in records:
        if record['内部識別子'].startswith('#') == False and record['E_E_gen'] != 'ERR' and record['E_E_gen'] != 'err':
            spec = convert(record)

            solrad = load_solrad(spec['region'], spec['sol_region'])

            E_E_gen = np.sum(calc_E_E_PV_d_t(spec['panel_list'], solrad))

            print('{} E_E_gen: {} [KWh/年], 正解との差分: {} [KWh/年]'.format(record['内部識別子'], E_E_gen, E_E_gen - float(record['E_E_gen'])))
        else:
            print('{} err'.format(record['内部識別子']))



