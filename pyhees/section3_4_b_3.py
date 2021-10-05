# B.3 地域の区分、方位及び日除けの形状（オーバーハング型）に応じて簡易的に算出する方法

def get_f_H_i(region, direction, y1, y2, z):
    """ 開口部iの暖房期の取得日射熱補正係数

    :param region: 省エネルギー地域区分
    :type region: int
    :param direction: 外皮の部位の方位
    :type direction: str
    :param y1: 日除け下端から窓上端までの垂直方向の距離 (mm)
    :type y1: float
    :param y2: 窓の開口高さ寸法 (mm)
    :type y2: float
    :param z: 壁面からの日除けの張り出し寸法（ひさし等のオーバーハング型日除けの出寸法は壁表面から先端までの寸法とする）(mm)
    :type z: float
    :return: 開口部iの暖房期の取得日射熱補正係数
    :rtype: float
    """

    # 暖房期における1地域から7地域までの南東面・南面・南西面 --- 式(1a)
    if (region in [1,2,3,4,5,6,7] and direction in ['南東', '南', '南西']):
        return min(0.01 * (5 + 20 * ((3*y1 + y2) / z)), 0.72)
    # 暖房期における1地域から7地域までの南東面・南面・南西面以外 --- 式(1b)
    elif (region in [1,2,3,4,5,6,7] and not(direction in ['南東', '南', '南西'])):
        return min(0.01 * (10 + 15 * ((2*y1 + y2) / z)), 0.72)
    else:
        ValueError("invalid value in region or direction")


def get_f_C_i(region, direction, y1, y2, z):
    """ 開口部iの冷房期の取得日射熱補正係数

    :param region: 省エネルギー地域区分
    :type region: int
    :param direction: 外皮の部位の方位
    :type direction: str
    :param y1: 日除け下端から窓上端までの垂直方向の距離 (mm)
    :type y1: float
    :param y2: 窓の開口高さ寸法 (mm)
    :type y2: float
    :param z: 壁面からの日除けの張り出し寸法（ひさし等のオーバーハング型日除けの出寸法は壁表面から先端までの寸法とする）(mm)
    :type z: float
    :return: 開口部iの冷房期の取得日射熱補正係数
    :rtype: float
    """

    Direction_dict = {'Top':'上面', 'N':'北', 'NE':'北東', 'E':'東', 'SE':'南東', 
                    'S':'南', 'SW':'南西', 'W':'西', 'NW':'北西', 'Bottom':'下面'}
    
    # 冷房期における1地域から7地域までの南面 --- 式(2a)
    if (region in [1,2,3,4,5,6,7] and Direction_dict[direction] in ['南']):
        return min(0.01 * (24 + 9 * ((3*y1 + y2) / z)), 0.93)
    # 冷房期における1地域から7地域までの南面以外及び8地域の南東面・南面・南西面以外 --- 式(2b)
    elif ((region in [1,2,3,4,5,6,7] and not(Direction_dict[direction] in ['南'])) or (region == 8 and not(Direction_dict[direction] in ['南東', '南', '南西']))):
        return min(0.01 * (16 + 24 * ((2*y1 + y2) / z)), 0.93)
    # 冷房期における8地域の南東面・南面・南西面 --- 式(2c)
    elif (region == 8 and Direction_dict[direction] in ['南東', '南', '南西']):
        return min(0.01 * (16 + 19 * ((2*y1 + y2) / z)), 0.93)
    else:
        ValueError("invalid value in region or direction")