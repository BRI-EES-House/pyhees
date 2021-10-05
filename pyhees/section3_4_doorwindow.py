# 8 欄間付きドアや袖付きドア等のドアや窓が同一枠内で併設される場合の開口部

# ドアや窓が同一枠内で併設される場合の開口部の暖房期の日射熱取得率 ((W/m)/(W/m2))　(8)
def get_eta_H_i(eta_d_W_H_i, eta_d_D_H_i, A_d_W, A_d_D):
    """ ドアや窓が同一枠内で併設される場合の開口部iの暖房期の日射熱取得率 ((W/m)/(W/m2)) (8)

    :param eta_d_W_H_i: ドアや窓が同一枠内で併設される場合の開口部iの窓部分の暖房期の日射熱取得率((W/m2)/(W/m2))
    :type eta_d_W_H_i: float
    :param eta_d_D_H_i: ドアや窓が同一枠内で併設される場合の開口部iのドア部分の暖房期の日射熱取得率((W/m2)/(W/m2))
    :type eta_d_D_H_i: float
    :param A_d_W: ドアや窓が同一枠内で併設される場合の開口部（窓又はドア）の窓部分の面積(m2)
    :type A_d_W: float
    :param A_d_D: ドアや窓が同一枠内で併設される場合の開口部（窓又はドア）のドア部分の面積(m2)
    :type A_d_D: float
    :return: 開口部iの暖房期の日射熱取得率
    :rtype: float
    """
    return (A_d_W * eta_d_W_H_i + A_d_D * eta_d_D_H_i) / (A_d_W + A_d_D)


# ドアや窓が同一枠内で併設される場合の開口部の冷房期の日射熱取得率 ((W/m)/(W/m2))　(9)
def get_eta_C_i(eta_d_W_C_i, eta_d_D_C_i, A_d_W, A_d_D):
    """ ドアや窓が同一枠内で併設される場合の開口部iの冷房期の日射熱取得率 ((W/m)/(W/m2)) (9)

    :param eta_d_W_C_i: ドアや窓が同一枠内で併設される場合の開口部iの窓部分の冷房期の日射熱取得率((W/m2)/(W/m2))
    :type eta_d_W_C_i: float
    :param eta_d_D_C_i: ドアや窓が同一枠内で併設される場合の開口部iのドア部分の冷房期の日射熱取得率((W/m2)/(W/m2))
    :type eta_d_D_C_i: float
    :param A_d_W: ドアや窓が同一枠内で併設される場合の開口部（窓又はドア）の窓部分の面積(m2)
    :type A_d_W: float
    :param A_d_D: ドアや窓が同一枠内で併設される場合の開口部（窓又はドア）のドア部分の面積(m2)
    :type A_d_D: float
    :return: 開口部iの冷房期の日射熱取得率
    :rtype: float
    """
    return (A_d_W * eta_d_W_C_i + A_d_D * eta_d_D_C_i) / (A_d_W + A_d_D)
