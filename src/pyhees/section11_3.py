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

    Args:

    Returns:
      DateFrame: スケジュール

    """
    path = os.path.join(os.path.dirname(__file__), 'data', 'schedule.csv')
    return pd.read_csv(path)


def get_schedule_ac(df):
    """暖冷房スケジュール

    Args:
      df(DateFrame): スケジュール

    Returns:
      ndarray: 暖冷房スケジュール

    """
    return df['暖冷房'].values


def get_schedule_v(df):
    """換気スケジュール

    Args:
      df(DateFrame): スケジュール

    Returns:
      ndarray: 換気スケジュール

    """
    return df['換気'].values


def get_schedule_hw(df):
    """給湯スケジュール

    Args:
      df(DateFrame): スケジュール

    Returns:
      ndarray: 給湯スケジュール

    """
    return df['給湯'].values


def get_schedule_l(df):
    """照明スケジュール

    Args:
      df(DateFrame): スケジュール

    Returns:
      ndarray: 照明スケジュール

    """
    return df['照明'].values


def get_schedule_app(df):
    """家電スケジュール

    Args:
      df(DateFrame): スケジュール

    Returns:
      ndarray: 家電スケジュール

    """
    return df['家電'].values


def get_schedule_cc(df):
    """調理スケジュール

    Args:
      df(DateFrame): スケジュール

    Returns:
      ndarray: 調理スケジュール

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
