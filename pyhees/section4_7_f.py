# ============================================================================
# 付録 F ヒートポンプ・ガス瞬間式併用型給湯温水暖房機
#       （給湯熱源：ヒートポンプ・ガス瞬間式併用、暖房熱源：ガス瞬間式）
# ============================================================================


# 付録 B ガス温水暖房機及び給湯温水暖房機に記される計算方法によるものとする。
# ※定格効率は、ガス潜熱回収型熱源機として0.87(87.0%)とする。


import pyhees.section4_7_b as gas


def calc_E_E_hs(r_WS_hs, E_G_hs):
    """ 1時間当たりの消費電力量

    :param r_WS_hs: 1時間平均の温水暖房用熱源機の温水供給運転率
    :type r_WS_hs: ndarray
    :param E_G_hs: 1時間当たりの温水暖房用熱源機のガス消費量（MJ/h）
    :type E_G_hs: ndarray
    :return: 1時間当たりの消費電力量
    :rtype: ndarray
    """
    return gas.calc_E_E_hs(
        r_WS_hs=r_WS_hs,
        E_G_hs=E_G_hs
    )


def calc_E_G_hs(q_rtd_hs, Q_out_H_hs, P_hs):
    """ 1時間当たりの温水床暖房用熱源機のガス消費量 (MJ/h)

    :param q_rtd_hs: 温水暖房用熱源機の定格能力 (W)
    :type q_rtd_hs: float
    :param Q_out_H_hs: 1時間当たりの温水暖房用熱源機の暖房出力 (MJ/h)
    :type Q_out_H_hs: ndarray
    :param P_hs: 送水温度の区分
    :type P_hs: int
    :return: 1時間当たりの温水床暖房用熱源機のガス消費量 (MJ/h)
    :rtype: ndarray
    """
    return gas.calc_E_G_hs(
        e_rtd=0.87,
        q_rtd_hs=q_rtd_hs,
        Q_out_H_hs=Q_out_H_hs,
        hs_type="ガス潜熱回収型給湯温水暖房機",
        P_hs=P_hs
    )


def calc_E_K_hs():
    """ 灯油消費量

    :return: 灯油消費量
    :rtype: ndarray
    """
    return gas.get_E_K_hs()


def calc_E_M_hs():
    """ その他の一次エネルギー消費量

    :return: その他の一次エネルギー消費量
    :rtype: ndarray
    """
    return gas.get_E_M_hs()
