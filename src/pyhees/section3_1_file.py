# ============================================================================
# 【暖冷房負荷ファイルの内容】
# ============================================================================

import pandas as pd
import os
from functools import lru_cache


def get_filename(hc, region, mode, NVl, j, k, TSl, hex):
    """負荷ファイル名の取得

    Args:
      hc(str): 暖房であれば'H', 冷房であれば'C'
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      NVl(int): 通風レベル 1-3
      j(int): 断熱性能の区分
      k(int): 日射遮蔽レベル 1-3
      TSl(int): 蓄熱の利用の程度の区分 1-2
      hex(bool): 熱交換換気の有無

    Returns:
      str: ファイル名

    """

    # 3.運転モード
    if mode == 'い' or mode == '全館連続' or mode == '全館連続':
        mode_s = 11
    elif mode == 'は' or mode == '居室間歇':
        mode_s = 12
    elif mode == 'ろ' or mode == '居室連続':
        mode_s = 13
    else:
        raise ValueError(mode)

    # 4.断熱水準・熱交換換気の有無
    if j == 1:
        j_s = 2
    elif j == 2:
        j_s = 3 if not hex else 4
    elif j == 3:
        j_s = 5 if not hex else 7
    elif j == 4:
        j_s = 9 if not hex else 11
    else:
        raise ValueError(j)

    # 5.日射遮蔽
    if k == 1:
        k_s = 3
    elif k == 2:
        k_s = 2
    elif k == 3:
        k_s = 1
    else:
        raise ValueError(k)

    # 6.通風設定
    if NVl == 1:
        NVl_s = 1
    elif NVl == 2:
        NVl_s = 3
    elif NVl == 3:
        NVl_s = 5
    else:
        raise ValueError(NVl)

    filename = "I{hc}{region}x_{mode:02d}_{j:02d}_{k}{NVl}2_{TSl}SS.csv" \
        .format(hc=hc, region=region, mode=mode_s, NVl=NVl_s, j=j_s, k=k_s, TSl=TSl)

    return filename


# ※何度も同じファイルを読まないようにキャッシュ
@lru_cache()
def read_csv(hc, filename):
    """負荷ファイルを読み込む

    Args:
      hc(str): 暖房であれば'H', 冷房であれば'C'
      filename(str): ファイル名

    Returns:
      DataFrame: ファイルの内容

    """
    path = os.path.join(os.path.dirname(__file__), 'data', '3-1_HukaData_151019_unifyLDK', filename)
    if hc == 'H':
        df = pd.read_csv(path, skiprows=4, nrows=24 * 365, names=(
            'date', 'hour', 'holiday', 'temp', 'humid', '1_HS', '1_HL', '2_HS', '2_HL', '3_HS', '3_HL', '4_HS', '4_HL',
            '5_HS', '5_HL', '6_HS', '6_HL', '7_HS', '7_HL', '8_HS', '8_HL', '9_HS', '9_HL', '10_HS', '10_HL', '11_HS',
            '11_HL', '12_HS', '12_HL'), encoding='shift_jis')
    elif hc == 'C':
        df = pd.read_csv(path, skiprows=4, nrows=24 * 365, names=(
            'date', 'hour', 'holiday', 'temp', 'humid', '1_CS', '1_CL', '2_CS', '2_CL', '3_CS', '3_CL', '4_CS', '4_CL',
            '5_CS', '5_CL', '6_CS', '6_CL', '7_CS', '7_CL', '8_CS', '8_CL', '9_CS', '9_CL', '10_CS', '10_CL', '11_CS',
            '11_CL', '12_CS', '12_CL'), encoding='shift_jis')
    else:
        raise NotImplementedError()
    return df


def get_L_dash_H_R_TSl_Qj_muH_j_k_d_t_i(region, mode, l, j, k, hex, i):
    """按分しない暖房負荷を取得

    Args:
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      l(int): 蓄熱の利用の程度の区分
      j(int): 断熱性能の区分
      k(int): 日射遮蔽レベル 1-3
      hex(bool): 熱交換換気の有無
      i(int): 暖冷房区画の番号

    Returns:
      ndarray: 按分しない暖房負荷を取得

    """
    filename = get_filename('H', region, mode, 1, j, k, l, False)
    df = read_csv('H', filename)
    return df['%d_HS' % i].values / 1000


def get_L_dash_CS_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, k, i):
    """按分しない冷房顕熱負荷を取得

    Args:
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      l(int): 蓄熱の利用の程度の区分
      j(int): 断熱性能の区分
      k(int): 日射遮蔽レベル 1-3
      i(int): 暖冷房区画の番号

    Returns:
      ndarray: 按分しない冷房顕熱負荷を取得

    """
    filename = get_filename('C', region, mode, l, j, k, 1, False)
    df = read_csv('C', filename)
    L_dash_CS_R_NVl_Qj_muH_j_k_d_t_i = df['%d_CS' % i].values * -1.0 / 1000
    return L_dash_CS_R_NVl_Qj_muH_j_k_d_t_i


def get_L_dash_CL_R_NVl_Qj_muH_j_k_d_t_i(region, mode, l, j, k, i):
    """按分しない冷房潜熱負荷を取得

    Args:
      region(int): 省エネルギー地域区分
      mode(str): 運転モード 'い', 'ろ', 'は'
      l(int): 蓄熱の利用の程度の区分
      j(int): 断熱性能の区分
      k(int): 日射遮蔽レベル 1-3
      i(int): 暖冷房区画の番号

    Returns:
      ndarray: 按分しない冷房潜熱負荷を取得

    """
    filename = get_filename('C', region, mode, l, j, k, 1, False)
    df = read_csv('C', filename)
    L_dash_CL_R_NVl_Qj_muH_j_k_d_t_i = df['%d_CL' % i].values * -1.0 / 1000
    return L_dash_CL_R_NVl_Qj_muH_j_k_d_t_i
