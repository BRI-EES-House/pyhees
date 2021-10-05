# ============================================================================
# 付録 A R410A におけるヒートポンプサイクルの理論効率の計算方法
# ============================================================================

# ============================================================================
# A.4 ヒートポンプサイクルの理論効率
# ============================================================================


# ヒートポンプサイクルの理論暖房効率 (1)
def calc_e_ref_H_th(Theta_ref_evp, Theta_ref_cnd, Theta_ref_SC, Theta_ref_SH):
    """ヒートポンプサイクルの理論暖房効率 (1)

    Args:
      Theta_ref_evp(float): 蒸発圧力 (MPa)
      Theta_ref_cnd(float): ヒートポンプサイクルの凝縮温度 (℃)
      Theta_ref_SC(float): ヒートポンプサイクルの過冷温度 (℃)
      Theta_ref_SH(float): ヒートポンプサイクルの過熱度 (℃)

    Returns:
      float: ヒートポンプサイクルの理論暖房効率 (-)

    """
    # 使用されていない変数
    # :param Theta_ref_cnd_out: ヒートポンプサイクルの凝縮温度 (℃)

    # **  A.6 凝縮圧力および蒸発圧力 **

    # 蒸発圧力 (12)
    P_ref_evp = calc_P_ref_evp(Theta_ref_evp)

    # 凝縮圧力 (11)
    P_ref_cnd = calc_P_ref_cnd(Theta_ref_cnd)

    # **  A.6 凝縮器出口エンタルピー **

    # 凝縮器出力温度 (10)
    Theta_ref_cnd_out = get_Theta_ref_cnd_out(Theta_ref_cnd, Theta_ref_SC)

    # 凝縮器出口比エンタルピー (9)
    h_ref_cnd_out = calc_h_ref_cnd_out(P_ref_cnd, Theta_ref_cnd_out)

    # ** A.5 圧縮機吐出及び吸入比エンタルピー **

    # 圧縮機吸込温度 (8)
    Theta_ref_comp_in = get_Theta_ref_comp_in(Theta_ref_evp, Theta_ref_SH)

    # 圧縮機吸込圧力 (7)
    P_ref_comp_in = get_P_ref_comp_in(P_ref_evp)

    # 圧縮機吸込エンタルピー (6)
    h_ref_comp_in = calc_h_ref_comp_in(P_ref_comp_in, Theta_ref_comp_in)

    # 圧縮機吐出比エンタルピー (2)
    h_ref_comp_out = calc_h_ref_comp_out(Theta_ref_evp, Theta_ref_SH, Theta_ref_cnd)

    # ヒートポンプサイクルの理論暖房効率 (1)
    e_ref_H_th = (h_ref_comp_out - h_ref_cnd_out) / (h_ref_comp_out - h_ref_comp_in)

    return e_ref_H_th


# ============================================================================
# A.5 圧縮機吐出及び吸込比エンタルピー
# ============================================================================

# 圧縮機吐出比エンタルピー (2)
def calc_h_ref_comp_out(Theta_ref_evp, Theta_ref_SH, Theta_ref_cnd):
    """圧縮機吐出比エンタルピー (2)

    Args:
      Theta_ref_evp(float): 蒸発圧力 (MPa)
      Theta_ref_SH(float): ヒートポンプサイクルの過熱度 (℃)
      Theta_ref_cnd(float): ヒートポンプサイクルの凝縮温度 (℃)

    Returns:
      float: 圧縮機吐出比エンタルピー (kJ/kg)

    """
    # 凝縮圧力 (11)
    P_ref_cnd = calc_P_ref_cnd(Theta_ref_cnd)

    # 圧縮機吐出圧力 (3)
    P_ref_comp_out = get_P_ref_comp_out(P_ref_cnd)

    # 蒸発圧力 (12)
    P_ref_evp = calc_P_ref_evp(Theta_ref_evp)

    # 圧縮機吸込温度 (8)
    Theta_ref_comp_in = get_Theta_ref_comp_in(Theta_ref_evp, Theta_ref_SH)

    # 圧縮機吸込圧力 (7)
    P_ref_comp_in = get_P_ref_comp_in(P_ref_evp)

    # 圧縮機吸込エンタルピー (6)
    h_ref_comp_in = calc_h_ref_comp_in(P_ref_comp_in, Theta_ref_comp_in)

    # 圧縮機吸込比エントロピー (5)
    S_ref_comp_in = calc_S_ref_comp_in(P_ref_comp_in, h_ref_comp_in)

    # 圧縮機吐出比エントロピー (4)
    S_ref_comp_out = get_S_ref_comp_out(S_ref_comp_in)

    # 圧縮機吐出比エンタルピー (2)
    h_ref_comp_out = get_f_H_gas_comp_out(P_ref_comp_out, S_ref_comp_out)

    return h_ref_comp_out


# 圧縮機吐出圧力 (3)
def get_P_ref_comp_out(P_ref_cnd):
    """圧縮機吐出圧力 (3)
    圧縮機吐出圧力は凝縮圧力と等しいとする。

    Args:
      P_ref_cnd(float): 凝縮圧力 (MPa)

    Returns:
      float: 圧縮機吐出圧力 (MPa)

    """
    return P_ref_cnd


# 圧縮機吐出比エントロピー (4)
def get_S_ref_comp_out(S_ref_comp_in):
    """圧縮機吐出比エントロピー (4)
    圧縮機吐出比エントロピーは圧縮機吸入比エントロピーに等しいとする。

    Args:
      S_ref_comp_in(float): 圧縮機吸入比エントロピー (kJ/kg・K)

    Returns:
      float: 圧縮機吐出比エントロピー (kJ/kg・K)

    """
    return S_ref_comp_in


# 圧縮機吸込比エントロピー (5)
def calc_S_ref_comp_in(P_ref_comp_in, h_ref_comp_in):
    """圧縮機吸込比エントロピー (5)

    Args:
      P_ref_comp_in(float): 圧縮機吸込圧力 (MPa)
      h_ref_comp_in(float): 圧縮機吸込エンタルピー (kJ/kg)

    Returns:
      float: 圧縮機吸込比エントロピー (kJ/kg・K)

    """
    return get_f_S_gas(P_ref_comp_in, h_ref_comp_in)


# 圧縮機吸込エンタルピー (6)
def calc_h_ref_comp_in(P_ref_comp_in, Theta_ref_comp_in):
    """圧縮機吸込エンタルピー (6)

    Args:
      P_ref_comp_in(float): 圧縮機吸込圧力 (℃)
      Theta_ref_comp_in(float): 圧縮機吸込温度 (℃)

    Returns:
      float: 圧縮機吸込エンタルピー (kJ/kg)

    """
    return get_f_H_gas_comp_in(P=P_ref_comp_in, Theta=Theta_ref_comp_in)


# 
def get_P_ref_comp_in(P_ref_evp):
    """圧縮機吸込圧力 (7)
    圧縮機吸込圧力は蒸発圧力に等しいとする。

    Args:
      P_ref_evp(float): 蒸発圧力 (MPa)

    Returns:
      float: 圧縮機吸入圧力 (MPa)

    """
    return P_ref_evp


# 圧縮機吸込温度 (8)
def get_Theta_ref_comp_in(Theta_ref_evp, Theta_ref_SH):
    """圧縮機吸込温度 (8)

    Args:
      Theta_ref_evp(float): ヒートポンプサイクルの蒸発温度 (℃)
      Theta_ref_SH(float): ヒートポンプサイクルの過熱度 (℃)

    Returns:
      float: 圧縮機吸込温度 (℃)

    """
    return Theta_ref_evp + Theta_ref_SH


# ============================================================================
# A.6 凝縮器出口比エンタルピー
# ============================================================================

# 凝縮器出口比エンタルピー (9)
def calc_h_ref_cnd_out(P_ref_cnd, Theta_ref_cnd_out):
    """凝縮器出口比エンタルピー (9)

    Args:
      P_ref_cnd(float): 凝縮圧力 (MPa)
      Theta_ref_cnd_out(float): ヒートポンプサイクルの凝縮温度 (℃)

    Returns:
      float: 凝縮器出口比エンタルピー (kJ/kg)

    """
    return get_f_H_liq(P=P_ref_cnd, Theta=Theta_ref_cnd_out)


# 凝縮器出力温度 (10)
def get_Theta_ref_cnd_out(Theta_ref_cnd, Theta_ref_SC):
    """凝縮器出力温度 (10)

    Args:
      Theta_ref_cnd(float): ヒートポンプサイクルの凝縮温度 (℃)
      Theta_ref_SC(float): ヒートポンプサイクルの過冷温度 (℃)

    Returns:
      float: 凝縮器出力温度 (℃)

    """
    return Theta_ref_cnd - Theta_ref_SC


# A.7 凝縮圧力および蒸発圧力

# 凝縮圧力 (11)
def calc_P_ref_cnd(Theta_ref_cnd):
    """凝縮圧力 (11)

    Args:
      Theta_ref_cnd(float): ヒートポンプサイクルの凝縮温度 (℃)

    Returns:
      float: 凝縮圧力 (MPa)

    """
    return get_f_p_sgas(Theta=Theta_ref_cnd)


# 蒸発圧力 (12)
def calc_P_ref_evp(Theta_ref_evp):
    """蒸発圧力 (12)

    Args:
      Theta_ref_evp(float): ヒートポンプサイクルの蒸発温度 (℃)

    Returns:
      float: 蒸発圧力 (MPa)

    """
    return get_f_p_sgas(Theta=Theta_ref_evp)


# ============================================================================
# A.8 冷媒に関する関数
# ============================================================================

# ============================================================================
# A.8.1 飽和蒸気に関する関数
# ============================================================================

# 飽和蒸気の温度から圧力を求める関数 (13)
def get_f_p_sgas(Theta):
    """飽和蒸気の温度から圧力を求める関数 (13)

    Args:
      Theta(float): 飽和蒸気の温度 (℃)

    Returns:
      float: 飽和蒸気の圧力 (MPa)

    """
    return 2.75857926950901 * 10 ** (-17) * Theta ** 8 \
           + 1.49382057911753 * 10 ** (-15) * Theta ** 7 \
           + 6.52001687267015 * 10 ** (-14) * Theta ** 6 \
           + 9.14153034999975 * 10 ** (-12) * Theta ** 5 \
           + 3.18314616500361 * 10 ** (-9) * Theta ** 4 \
           + 1.60703566663019 * 10 ** (-6) * Theta ** 3 \
           + 3.06278984019513 * 10 ** (-4) * Theta ** 2 \
           + 2.54461992992037 * 10 ** (-2) * Theta \
           + 7.98086455154775 * 10 ** (-1)


# ============================================================================
# A.8.2 過熱蒸気に関する関数
# ============================================================================


# 圧縮機吸引領域において過熱蒸気の圧力と温度から比エンタルピーを求める関数 (14)
def get_f_H_gas_comp_in(P, Theta):
    """圧縮機吸引領域において過熱蒸気の圧力と温度から比エンタルピーを求める関数 (14)

    Args:
      P(float): 過熱蒸気の圧力 (MPa)
      Theta(dloat): 過熱蒸気の温度 (℃)

    Returns:
      float: 過熱蒸気の比エンタルピー (kJ/kg)

    """
    K = Theta + 273.15
    K2=K*K
    K3=K2*K
    P2=P*P
    P3=P2*P
    P4=P2*P2
    return -1.00110355 * 10 ** (-1) * P3 \
           - 1.184450639 * 10 * P2 \
           - 2.052740252 * 10 ** 2 * P \
           + 3.20391 * 10 ** (-6) * K3 \
           - 2.24685 * 10 ** (-3) * K2 \
           + 1.279436909 * K \
           + 3.1271238 * 10 ** (-2) * P2 * K \
           - 1.415359 * 10 ** (-3) * P * K2 \
           + 1.05553912 * P * K \
           + 1.949505039 * 10 ** 2


# 圧縮機吐出領域において過熱蒸気の圧力と比エントロピーから比エンタルピーを求める関数 (15)
def get_f_H_gas_comp_out(P, S):
    """圧縮機吐出領域において過熱蒸気の圧力と比エントロピーから比エンタルピーを求める関数 (15)

    Args:
      P(float): 過熱蒸気の圧力 (MPa)
      S(float): 過熱蒸気の比エントロピー (kJ/kg・K)

    Returns:
      float: 過熱蒸気の比エンタルピー (kJ/kg)

    """
    P2 = P * P
    P3 = P2 * P
    P4 = P2 * P2
    S2 = S * S
    S3 = S2 * S
    S4 = S2 * S2
    return -1.869892835947070 * 10 ** (-1) * P4 \
           + 8.223224182177200 * 10 ** (-1) * P3 \
           + 4.124595239531860 * P2 \
           - 8.346302788803210 * 10 * P \
           - 1.016388214044490 * 10 ** 2 * S4 \
           + 8.652428629143880 * 10 ** 2 * S3 \
           - 2.574830800631310 * 10 ** 3 * S2 \
           + 3.462049327009730 * 10 ** 3 * S \
           + 9.209837906396910 * 10 ** (-1) * P3 * S \
           - 5.163305566700450 * 10 ** (-1) * P2 * S2 \
           + 4.076727767130210 * P * S3 \
           - 8.967168786520070 * P2 * S \
           - 2.062021416757910 * 10 * P * S2 \
           + 9.510257675728610 * 10 * P * S \
           - 1.476914346214130 * 10 ** 3


#  過熱蒸気の圧力と比エンタルピーから比エントロピーを求める関数 (16)
def get_f_S_gas(P, h):
    """過熱蒸気の圧力と比エンタルピーから比エントロピーを求める関数 (16)

    Args:
      P(float): 過熱蒸気の圧力 (MPa)
      h(float): 過熱蒸気の比エンタルピー (kJ/kg)

    Returns:
      float: 過熱蒸気の比エントロピー (kJ/kg・K)

    """

    P2 = P * P
    P3 = P2 * P
    P4 = P2 * P2

    h2 = h * h
    h3 = h2 * h
    h4 = h2 * h2

    return 5.823109493752840 * 10 ** (-2) * P4 \
           - 3.309666523931270 * 10 ** (-1) * P3 \
           + 7.700179914440890 * 10 ** (-1) * P2 \
           - 1.311726004718660 * P \
           + 1.521486605815750 * 10 ** (-9) * h4 \
           - 2.703698863404160 * 10 ** (-6) * h3 \
           + 1.793443775071770 * 10 ** (-3) * h2 \
           - 5.227303746767450 * 10 ** (-1) * h \
           + 1.100368875131490 * 10 ** (-4) * P ** 3 * h \
           + 5.076769807083600 * 10 ** (-7) * P ** 2 * h2 \
           + 1.202580329499520 * 10 ** (-8) * P * h3 \
           - 7.278049214744230 * 10 ** (-4) * P ** 2 * h \
           - 1.449198550965620 * 10 ** (-5) * P * h2 \
           + 5.716086851760640 * 10 ** (-3) * P * h \
           + 5.818448621582900 * 10


# ============================================================================
# A.8.3 過冷却液に関する関数
# ============================================================================

# 過冷却液の圧力と温度から比エンタルピーを求める関数 (17)
def get_f_H_liq(P, Theta):
    """過冷却液の圧力と温度から比エンタルピーを求める関数 (17)

    Args:
      P(float): 過冷却液の圧力 (MPa)
      Theta(float): 過冷却液の温度 (℃)

    Returns:
      float: 過冷却液のエンタルピー (kJ/kg)

    """
    K = Theta + 273.15
    K2 = K * K
    K3 = K2 * K

    P2 = P * P
    P3 = P2 * P

    return 1.7902915 * 10 ** (-2) * P3 \
           + 7.96830322 * 10 ** (-1) * P2 \
           + 5.985874958 * 10 * P \
           + 0 * K3 \
           + 9.86677 * 10 ** (-4) * K2 \
           + 9.8051677 * 10 ** (-1) * K \
           - 3.58645 * 10 ** (-3) * P ** 2 * K \
           + 8.23122 * 10 ** (-4) * P * K2 \
           - 4.42639115 * 10 ** (-1) * P * K \
           - 1.415490404 * 10 ** 2
