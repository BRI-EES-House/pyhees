# 付録 E 外気側表⾯の日射吸収率に応じた係数
#
def get_f_alpha_i(alpha):
    """一般部位、大部分が不透明材料で構成されている開口部𝑖（ドア等）及び熱橋における外気側表面の日射吸収率に応じた係数の計算

    Args:
      alpha(float): 外気側表⾯の日射吸収率 (-)

    Returns:
      float: 外気側表⾯の日射吸収率に応じた係数 (-)

    """
    # 外気側表⾯の日射吸収率に応じた係数を1とする場合
    if (alpha is None):
      return 1
    else:
      # 式(1)
      return alpha / 0.8
