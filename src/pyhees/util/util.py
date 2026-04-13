# ============================================================================
# ユーティリティ
# ============================================================================

import math

EPSILON = 1e-09

def is_equal(a, b):
  """aとbが等しいかどうかを確認する (a == b)

  Args:
    a(float): a
    b(float): b

  Returns:
    bool: aとbが等しいかどうかの値
  """
  return math.isclose(a, b)


def ceil(val, digit):
  """小数点以下切り上げ

  Args:
    val(float): 切り上げる数値
    digit(int): 小数点以下の桁数

  Returns:
    float: 小数点以下切り上げした値
  """
  p = 10**digit
  return math.ceil((val - EPSILON) * p) / p



def convert_to_gj(mj_val):
  """MJ単位をGJ単位に変換する

  Args:
    mjval(float): MJ単位の値

  Returns:
    float: GJ単位の値
  """
  gj_raw = mj_val / 1000

  return ceil(gj_raw, 1)
