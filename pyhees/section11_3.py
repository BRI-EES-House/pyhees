# ============================================================================
# 第十一章 その他
# 第三節 生活スケジュール
# Ver.04（エネルギー消費性能計算プログラム（住宅版）Ver.02～）
# ============================================================================

import os
import pandas as pd
from functools import lru_cache


@lru_cache()
def load_schedule():
    """スケジュール読み込み

    :return: スケジュール
    :rtype: DateFrame
    """
    path = os.path.join(os.path.dirname(__file__), 'data', 'schedule.csv')
    return pd.read_csv(path)


def get_schedule_ac(df):
    """暖冷房スケジュール

    :param df: スケジュール
    :type df: DateFrame
    :return: 暖冷房スケジュール
    :rtype: ndarray
    """
    return df['暖冷房'].values


def get_schedule_v(df):
    """換気スケジュール

    :param df: スケジュール
    :type df: DateFrame
    :return: 換気スケジュール
    :rtype: ndarray
    """
    return df['換気'].values


def get_schedule_hw(df):
    """給湯スケジュール

    :param df: スケジュール
    :type df: DateFrame
    :return: 給湯スケジュール
    :rtype: ndarray
    """
    return df['給湯'].values


def get_schedule_l(df):
    """照明スケジュール

    :param df: スケジュール
    :type df: DateFrame
    :return: 照明スケジュール
    :rtype: ndarray
    """
    return df['照明'].values


def get_schedule_app(df):
    """家電スケジュール

    :param df: スケジュール
    :type df: DateFrame
    :return: 家電スケジュール
    :rtype: ndarray
    """
    return df['家電'].values


def get_schedule_cc(df):
    """調理スケジュール

    :param df: スケジュール
    :type df: DateFrame
    :return: 調理スケジュール
    :rtype: ndarray
    """
    return df['調理'].values


if __name__ == '__main__':
    df = load_schedule()
    print(get_schedule_ac(df))
    print(get_schedule_v(df))
    print(get_schedule_hw(df))
    print(get_schedule_l(df))
    print(get_schedule_app(df))
    print(get_schedule_cc(df))
