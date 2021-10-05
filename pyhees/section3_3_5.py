import pyhees.section3_3_a as thermophysical
from pyhees.section3_3_b import calc_U_bySpec

# ============================================================================
# 5. 部位の熱貫流率
# ============================================================================

# ============================================================================
# 5.1 一般部位
# ============================================================================

def get_Wood_Direct_U_i(portion_i):
    """ 熱貫流率が直接指定される場合

    :param portion_i: 一般部位𝑖
    :type portion_i: dict(Wall_direct)
    :return: 一般部位𝑖の熱貫流率, その他の計算結果
    :rtype: float, dict
    """

    # 数値チェック
    if range_correct(0.00, 999.999, portion_i['UValue']):
        U_i = portion_i['UValue']
    # 範囲が不正ならエラー
    else:
        U_i = 'ERROR'

    portion_i['U_i'] = U_i

    return U_i, portion_i


# ============================================================================
# 5.1.1 木造
# ============================================================================

def calc_Wood_Accurate_U_i(portion_i):
    """ 詳細計算法　一般部位𝑖の熱貫流率　(1)

    :param portion_i: 一般部位𝑖
    :type portion_i: dict(Wall_accurate)
    :return: 一般部位𝑖の熱貫流率, その他の計算結果
    :rtype: float, dict
    """

    U_i = 0.0
    #一般部位iを構成する部分のリスト
    part_list = portion_i['GeneralPart']

    # 結果部分
    portion_i['GeneralPart_output']=[{},{},{},{},{}]

    R_se_i, R_si_i = thermophysical.calc_R_si_R_se(portion_i['Type'], portion_i['Outside'])

    k_num = len(part_list)  # 一般部位iを構成する部分の数
    for k in range(k_num):
        part_k = part_list[k]
        # 面積が未入力(None)の場合はエラー
        if part_k['Area'] == None:
            U_i_k = 'ERROR'
            R_list = ['ERROR'] * len(part_k['layer'])
            sum_R_i_k_l = 'ERROR'
            a_i_k = 'ERROR'
        # 数値チェック　範囲が正しければ計算
        elif range_correct(0.00, 9999.99, part_k['Area']):
            U_i_k, R_list, sum_R_i_k_l = calc_U_i_k(portion_i['Type'], portion_i['Outside'], part_k)
            a_i_k = get_Wood_Accurate_a_i_k(part_list, k)
        # 範囲が不正ならエラー
        else:
            U_i_k = 'ERROR'
            R_list = ['ERROR'] * len(part_k['layer'])
            sum_R_i_k_l = 'ERROR'
            a_i_k = 'ERROR'

        # 出力-層の熱抵抗
        for i, node in enumerate(['R1', 'R2', 'R3', 'R5', 'R6', 'R7']):
            if i < len(R_list):
                portion_i['GeneralPart_output'][k][node] = R_list[i]

        portion_i['GeneralPart_output'][k]['Rse'] = R_se_i
        portion_i['GeneralPart_output'][k]['Rsi'] = R_si_i
        portion_i['GeneralPart_output'][k]['Ru_n'] = sum_R_i_k_l
        portion_i['GeneralPart_output'][k]['Un'] = U_i_k
        portion_i['GeneralPart_output'][k]['a'] = a_i_k
        U_i += a_i_k*U_i_k

    portion_i['U_i'] = U_i
    return U_i, portion_i


def get_Wood_Accurate_a_i_k(part_list, k):
    """ 一般部位𝑖の部分𝑘の面積比率a_i_k　(2)

    :param part_list: 一般部位iを構成する部分のリスト
    :type part_list: dict(GeneralPart_accurate)
    :param k: 面積比率を求める部分の番号
    :type k: int
    :return: 一般部位𝑖の部分𝑘の面積比率a_i_k
    :rtype: float
    """

    sum_S_i_k = 0.0
    k_num = len(part_list)  # 一般部位iを構成する部分の数
    for k_ in range(k_num):
        if part_list[k_]['Area'] != None:
            sum_S_i_k += part_list[k_]['Area']

    return part_list[k]['Area'] / sum_S_i_k 


def calc_Wood_Simple_U_i(portion_i):
    """ 
    面積比率法（充填断熱する場合又は充填断熱し付加断熱する場合）（簡略計算方法）

    :param portion_i: 一般部位𝑖
    :type portion_i: dict(Wall_simple1)
    :return: 一般部位𝑖の熱貫流率, その他の計算結果
    :rtype: float, dict
    """

    # (1)と同じ
    U_i = 0.0
    part_list = []  # 一般部位iを構成する部分のリスト
    part_list.append(portion_i['GeneralPart'][0]) #一般部分を追加
    if 'HeatBridge' in portion_i:
        part_list.append(portion_i['HeatBridge'][0]) #熱橋部分を追加
    
    # 軸組構法の束立大引工法において根太間及び大引間に断熱する場合の床の場合のみ断熱部＋熱橋部を追加
    if (portion_i['Type']=='Floor' and portion_i['ConstructionMethod']=='FrameSleeper' and portion_i['InsulationPlace']=='FloorJoistBeamInterval'):
        part_list.append(portion_i['MixPart'][0])
        part_list.append(portion_i['MixPart'][1])

    R_se_i, R_si_i = thermophysical.calc_R_si_R_se(portion_i['Type'], portion_i['Outside'])
    portion_i['Rse'] = R_se_i
    portion_i['Rsi'] = R_si_i

    # 結果部分
    portion_i['GeneralPart_output']={}
    portion_i['HeatBridge_output']={}
    portion_i['MixPart1_output']={}
    portion_i['MixPart2_output']={}

    k_num = len(part_list)  # k_num=4(断熱部＋熱橋部がある場合)または2
    for k in range(k_num):
        U_i_k, R_list, sum_R_i_k_l = calc_U_i_k(portion_i['Type'],
                        portion_i['Outside'], part_list[k])
        a_i_k = calc_Wood_Simple1_a_i_k(portion_i, part_list[k])

        if k == 0:
            output_part = 'GeneralPart_output'
        elif k == 1:
            output_part = 'HeatBridge_output'
        elif k == 2:
            output_part = 'MixPart1_output'
        else:
            output_part = 'MixPart2_output'

        for r, R_item in enumerate(R_list):
            portion_i[output_part]['R{}'.format(r + 1)] = R_item

        portion_i[output_part]['Ru_n'] = sum_R_i_k_l
        portion_i[output_part]['Un'] = U_i_k        
        portion_i[output_part]['a'] = a_i_k
        U_i += a_i_k*U_i_k
    
    portion_i['U_i'] = U_i
    return U_i, portion_i


def calc_Wood_Simple1_a_i_k(portion_i, part_k):
    """
    面積比率法において一般部位𝑖の部分𝑘の面積比率a_i_kを求める

    :param portion_i: 一般部位i
    :type portion_i: dict (Wall)
    :param part_k: 面積比率を求める対象の部分
    :type part_k: dict(GeneralPart_simple1/MixPart_simple1/HeatBridge_simple1)
    :return: 一般部位𝑖の部分𝑘の面積比率a_i_k
    :rtype: float
    """

    portion_Type = portion_i['Type']
    # 床
    if portion_Type == 'Floor':
        return get_table_3_1(portion_i['ConstructionMethod'], portion_i['InsulationPlace'], part_k)
    # 外壁
    elif portion_Type == 'ExternalWall':
        return get_table_4(portion_i['ConstructionMethod'], portion_i['InsulationPlace'], part_k)
    # 天井
    elif portion_Type == 'Ceiling':
        return get_table_5(part_k, portion_i['InsulationPlace'])
    # 屋根
    elif portion_Type == 'Roof':
        return get_table_6(portion_i['InsulationPlace'], part_k)
    else:
        raise ValueError("invalid value in ['Type']")


def get_table_3_1(ConstructionMethod, InsulationPlace, part_k):
    """ 表3-1 木造における床の面積比率

    :param ConstructionMethod: 'FrameFloorBeam'(軸組構法（床梁工法）)または
                                'FrameSleeper'(軸組構法（束立大引工法）)または
                                'FrameRigidFloor'(軸組構法（剛床工法）)または
                                'FrameSameLevel'(軸組構法（床梁土台同面工法）)または
                                'WallFloor'(枠組構法（床）)
    :type ConstructionMethod: str
    :param InsulationPlace: 'FloorJoistInterval'(根太間)または
                            'FloorBeamInterval'(大引間)または
                            'FloorJoistBeamInterval'(根太間＋大引間)
    :type InsulationPlace: str
    :param part_k: 面積比率を求める対象の部分k
    :type part_k: GeneralPart_simple1またはMixPart_simple1またはHeatBridge_simple1形式の辞書
    :return: 木造における床の面積比率
    :rtype: float
    """

    # 'GeneralPart'(断熱部分（一般部分）)または'MixPart'(断熱部＋熱橋部)または'HeatBridge'(熱橋部分（軸組部分）)
    part_type = part_k['part_Name']

    # 軸組構法（床梁工法）
    if ConstructionMethod == 'FrameFloorBeam':
        # 根太間に断熱する
        if InsulationPlace == 'FloorJoistInterval':
            a_i_k_dict = {'HeatBridge':0.20,'GeneralPart':0.80}
            return a_i_k_dict[part_type]
        else:
            raise ValueError("invalid value in ['InsulationPlace']")
    # 軸組構法（束立大引工法）
    elif ConstructionMethod == 'FrameSleeper':
        # 根太間に断熱する
        if InsulationPlace == 'FloorJoistInterval':
            a_i_k_dict = {'HeatBridge':0.20,'GeneralPart':0.80}
            return a_i_k_dict[part_type]
        # 大引間に断熱する
        elif InsulationPlace == 'FloorBeamInterval':
            a_i_k_dict = {'HeatBridge':0.15,'GeneralPart':0.85}
            return a_i_k_dict[part_type]
        # 根太間及び大引間に断熱する場合 -> 表3-2参照
        elif InsulationPlace == 'FloorJoistBeamInterval':
            return get_table_3_2(part_k)
        else:
            raise ValueError("invalid value in ['InsulationPlace']")
    # 軸組構法（剛床工法）
    elif ConstructionMethod == 'FrameRigidFloor':
        a_i_k_dict = {'HeatBridge':0.15,'GeneralPart':0.85}
        return a_i_k_dict[part_type]
    # 軸組構法（床梁土台同面工法）
    elif ConstructionMethod == 'FrameSameLevel':
        # 根太間に断熱する
        if InsulationPlace == 'FloorJoistInterval':
            a_i_k_dict = {'HeatBridge':0.30,'GeneralPart':0.70}
            return a_i_k_dict[part_type]
        else:
            raise ValueError("invalid value in ['InsulationPlace']")
    # 枠組構法（床）
    elif ConstructionMethod == 'WallFloor':
        # 根太間に断熱する
        if InsulationPlace == 'FloorJoistInterval':
            a_i_k_dict = {'HeatBridge':0.13,'GeneralPart':0.87}
            return a_i_k_dict[part_type]
        else:
            raise ValueError("invalid value in ['InsulationPlace']")
    else:
        raise ValueError("invalid value in ['ConstructionMethod']")



def get_table_3_2(part_k):
    """ 表3-2 軸組構法の束立大引工法において根太間及び大引間に断熱する場合の床の面積比率

    :param part_k: 面積比率を求める対象の部分k
    :type part_k: GeneralPart_simpleまたはMixPart_simpleまたはHeatBridge_simple形式の辞書
    :return: 軸組構法の束立大引工法において根太間及び大引間に断熱する場合の床の面積比率
    :rtype: float
    """

    # 'GeneralPart'(断熱部分（一般部分）)または'MixPart'(断熱部＋熱橋部)または'HeatBridge'(熱橋部分（軸組部分）)
    part_type = part_k['part_Name']

    # 断熱部分 ⇒　根太間断熱材＋大引間断熱材
    if part_type == 'GeneralPart':
        return 0.72
    # 断熱部分＋熱橋部分
    elif part_type == 'MixPart':
        # 根太間断熱材＋大引材等 根太材＋大引間断熱材
        a_i_k_dict = {'JoistIntervalAndBeam':0.12, 'JoistAndBeamInterval':0.13}
        return a_i_k_dict[part_k['Type']]
    # 熱橋部分　⇒　根太材＋大引材等
    elif part_type == 'HeatBridge':
        return 0.03
    else:
        raise ValueError("invalid value in ['part_Name']")


def get_table_4(ConstructionMethod, InsulationPlace, part_k):
    """ 表4 木造における外壁（界壁）の面積比率

    :param ConstructionMethod: 'FrameWall'(軸組構法（外壁）)または
                                'WallWall'(枠組構法（外壁）)
    :type ConstructionMethod: str
    :param InsulationPlace: 'PillarInterval'(柱・間柱間)または
                            'StudInterval'(たて枠間)または
    :type InsulationPlace: str
    :param part_k: 面積比率を求める対象の部分k
    :type part_k: GeneralPart_simple1またはMixPart_simple1またはHeatBridge_simple1形式の辞書
    :return: 木造における外壁（界壁）の面積比率
    :rtype: float
    """

    # 'GeneralPart'(断熱部分（一般部分）)または'MixPart'(断熱部＋熱橋部)または'HeatBridge'(熱橋部分（軸組部分）)
    part_type = part_k['part_Name']

    # 軸組構法
    if ConstructionMethod == 'FrameWall':
        # 柱・間柱間に断熱する場合
        if InsulationPlace == 'PillarInterval':
            a_i_k_dict = {'HeatBridge':0.17, 'GeneralPart':0.83}
            return a_i_k_dict[part_type]
        else:
            raise ValueError("invalid value in ['InsulationPlace']")
    # 枠組壁工法
    elif ConstructionMethod == 'WallWall':
        # たて枠間に断熱する場合
        if InsulationPlace == 'StudInterval':
            a_i_k_dict = {'HeatBridge':0.23, 'GeneralPart':0.77}
            return a_i_k_dict[part_type]
        else:
            raise ValueError("invalid value in ['InsulationPlace']")
    else:
        raise ValueError("invalid value in ['ConstructionMethod']")




def get_table_5(part_k, InsulationPlace):
    """ 表5 木造における天井の面積比率

    :param part_k: 面積比率を求める対象の部分k
    :type part_k: GeneralPart_simpleまたはMixPart_simpleまたはHeatBridge_simple形式の辞書
    :return: 木造における天井の面積比率
    :rtype: float
    """

    if InsulationPlace == 'RoofBeamInterval':
        # 'GeneralPart'(断熱部分（一般部分）)または'HeatBridge'(熱橋部分（軸組部分）)
        part_type = part_k['part_Name']
        # 熱橋部分, 断熱部分
        a_i_k_dict = {'HeatBridge':0.13, 'GeneralPart':0.87}
        return a_i_k_dict[part_type]
    else:
        raise ValueError("invalid value in ['InsulationPlace']")

def get_table_6(InsulationPlace, part_k):
    """ 表6 木造における屋根の面積比率

    :param InsulationPlace: 'RafterInterval'(たるき間)
    :type InsulationPlace: str
    :param part_k: 面積比率を求める対象の部分k
    :type part_k: GeneralPart_simple1またはMixPart_simple1またはHeatBridge_simple1形式の辞書
    :return: 木造における屋根の面積比率
    :rtype: float
    """

    # 'GeneralPart'(断熱部分（一般部分）)または'HeatBridge'(熱橋部分（軸組部分）)
    part_type = part_k['part_Name']
    # たるき間に断熱する場合
    if InsulationPlace == 'RafterInterval':
        # 熱橋部分, 断熱部分
        a_i_k_dict = {'HeatBridge':0.14, 'GeneralPart':0.86}
        return a_i_k_dict[part_type]
    else:
        raise ValueError("invalid value in ['InsulationPlace']")


def get_layer_list(part_k):
    """ 部分kを構成する層のリストを出力する

    :param part_k: 部分k  
    :type part_k: dict(GeneralPart_accurate/GeneralPart_simple1/MixPart_simple1/HeatBridge_simple1/GeneralPart_simple2/GeneralPart_rc/GeneralPart_steel/GeneralPart_foundation)
    :returm: 部分kを構成する層のリスト
    :rtype: 
    """
    layer_list = []  # 部分kを構成する層のリスト
    layer_list.extend(part_k['SolidLayer'])
    layer_list.extend(part_k['AirLayer'])
    return layer_list


# ============================================================================
# 5.1.2 鉄筋コンクリート造等
# ============================================================================

def calc_RC_U_i(portion_i):
    """ 鉄筋コンクリート造等の一般部位𝑖の熱貫流率𝑈𝑖

    :param portion_i: 一般部位i
    :type portion_i: dict(Wall_rc)
    :return: 一般部位iの熱貫流率U_i, その他の計算結果
    :rtype: float, dict
    """

    # 結果用
    portion_i['GeneralPart_output'] = {}

    # 一般部位𝑖の熱貫流率𝑈𝑖は、一般部位𝑖の部分𝑘の熱貫流率𝑈𝑖,𝑘に等しいとする。
    # 部分kはportion_i['GeneralPart'][0]を採用する
    U_i, R_list, sum_R_i_k_l = calc_U_i_k(portion_i['Type'], portion_i['Outside'], portion_i['GeneralPart'][0])
    
    # 層ごとの熱抵抗(層数は変更の可能性あり)
    for i in range(len(R_list),6):
        R_list.append('')
    portion_i['GeneralPart_output']['R1'] = R_list[0]
    portion_i['GeneralPart_output']['R2'] = R_list[1]
    portion_i['GeneralPart_output']['R3'] = R_list[2]
    portion_i['GeneralPart_output']['R5'] = R_list[3]
    portion_i['GeneralPart_output']['R6'] = R_list[4]
    portion_i['GeneralPart_output']['R7'] = R_list[5]
    
    R_se_i, R_si_i = thermophysical.calc_R_si_R_se(portion_i['Type'], portion_i['Outside'])
    portion_i['GeneralPart_output']['Rse'] = R_se_i
    portion_i['GeneralPart_output']['Rsi'] = R_si_i

    portion_i['GeneralPart_output']['R_u'] = sum_R_i_k_l
    portion_i['GeneralPart_output']['U_g_i'] = U_i
    portion_i['U_i'] = U_i

    return U_i, portion_i


# ============================================================================
# 5.1.3 鉄骨造
# ============================================================================

def calc_Steel_U_i(portion_i):
    """ 鉄骨造における一般部位kの熱貫流率U_i (3)

    :param portion_i: 一般部位i
    :type portion_i: dict(Wall_steel)
    :return: 鉄骨造における一般部位kの熱貫流率U_i, その他の計算結果
    :rtype: float, dict
    """

    # 結果用
    portion_i['GeneralPart_output'] = {}

    # 一般部位iの断熱部分の熱貫流率U_g_iは、一般部位iの部分kの熱貫流率U_i_kに等しいとする
    # 部分kはportion_i['GeneralPart'][0]を採用する
    U_g_i, R_list, sum_R_i_k_l = calc_U_i_k(portion_i['Type'],
                       portion_i['Outside'], portion_i['GeneralPart'][0])
    U_r_i = get_table_7(portion_i['ExteriorThermalResistance'])
    
    # 層ごとの熱抵抗(層数は変更の可能性あり)
    for i in range(len(R_list),6):
        R_list.append('')
    portion_i['GeneralPart_output']['R1'] = R_list[0]
    portion_i['GeneralPart_output']['R2'] = R_list[1]
    portion_i['GeneralPart_output']['R3'] = R_list[2]
    portion_i['GeneralPart_output']['R5'] = R_list[3]
    portion_i['GeneralPart_output']['R6'] = R_list[4]
    portion_i['GeneralPart_output']['R7'] = R_list[5]

    R_se_i, R_si_i = thermophysical.calc_R_si_R_se(portion_i['Type'], portion_i['Outside'])
    portion_i['GeneralPart_output']['Rse'] = R_se_i
    portion_i['GeneralPart_output']['Rsi'] = R_si_i

    portion_i['GeneralPart_output']['R_u'] = sum_R_i_k_l
    portion_i['GeneralPart_output']['U_g_i'] = U_g_i
    portion_i['GeneralPart_output']['U_r_s'] = U_r_i

    U_i = U_g_i + U_r_i
    portion_i['U_i'] = U_i

    return U_i, portion_i


def get_table_7(ExteriorThermalResistance):
    """ 表7 鉄骨造における一般部位の熱橋部分（柱及び梁以外）の仕様に応じた補正熱貫流率

    :param ExteriorThermalResistance: 外装材＋断熱補強材の熱抵抗
                                        'Over17'(1.7以上)または'Under17'(1.7未満1.5以上)または
                                        'Under15'(1.5未満1.3以上)または'Under13'(1.3未満1.1以上)または
                                        'Under11'(1.1未満0.9以上)または'Under09'(0.9未満0.7以上)または
                                        'Under07'(0.7未満0.5以上)または'Under05'(0.5未満0.3以上)または
                                        'Under03'(0.3未満0.1以上)または'Under01'(0.1未満)
    :type ExteriorThermalResistance: str
    :return: 鉄骨造における一般部位の熱橋部分（柱及び梁以外）の仕様に応じた補正熱貫流率(U_r)
    :rtype: float
    """

    U_r_dict = {'Over1.7': 0.00, 'Under1.7': 0.10, 'Under1.5': 0.13, 'Under1.3': 0.14, 'Under1.1': 0.18,
                'Under0.9': 0.22, 'Under0.7': 0.40, 'Under0.5': 0.45, 'Under0.3': 0.60, 'Under0.1': 0.70}

    return U_r_dict[ExteriorThermalResistance]


# ============================================================================
# 5.1.4 一般部位の断面構成が同一である部分の熱貫流率
# ============================================================================

def calc_U_i_k(portion_type, portion_outside, part_k):
    """ 一般部位iの部分kの熱貫流率U_i_k (4)

    :param portion_type: 部位iの種類
                'Floor'(床)または'ExternalWall'(外壁)または'Ceiling'(天井)または'Roof'(屋根)
    :type portion_type: str
    :param portion_outside: 部位iの室外側は外気か？
                'Yes'または'No'
    :type portion_outside: str
    :param part_k: 面積比率を求める対象の部分k
    :type part_k: GeneralPart_○○またはMixPart_○○またはHeatBridge_○○形式の辞書
    :return: 一般部位iの部分kの熱貫流率,
             層ごとの熱抵抗の値をR1,R2,...,R7の順に入れたリスト,
             部分の熱抵抗の合計
    :rtype: float,
            list,
            float
    """

    R_se_i, R_si_i = thermophysical.calc_R_si_R_se(
        portion_type, portion_outside)

    # 部分kを構成する層のリスト・先頭要素が一番外側(外気側)
    layer_list = part_k['layer']

    sum_R_i_k_l, R_list = calc_R_i_k(layer_list)
    
    U_i_k = 1.0 / (R_se_i + R_si_i + sum_R_i_k_l)
    return  U_i_k, R_list, sum_R_i_k_l

def calc_R_i_k(layer_list):
    """ 一般部位iの部分kの熱抵抗　(4)の分母の3項目Σl_R_i_k_l
    
    :param layer_list: 部分kを構成する層のリスト・先頭要素が一番外側(外気側)
    :type layer_list: 
    :return: 一般部位iの部分kの熱抵抗　Σl_R_i_k_l,
             層ごとの熱抵抗の値をR1,R2,...,R7の順に入れたリスト
    :rtype: float,
            list
    """
    sum_R_i_k_l = 0.0
    l_num = len(layer_list)  # 一般部位iの部分kの層の数
    R_list = [0] * l_num # 層ごとの熱抵抗の値をR1,R2,...,R7の順に入れる
    for l in range(l_num):
        layer_l = layer_list[l]
        R_list[l] = calc_R_i_k_l(layer_l)
        
        # 入力数値の範囲が不正である場合は「ERROR」を返す
        if R_list[l] != 'ERROR':
            sum_R_i_k_l += R_list[l]
            # 空気層の種類が「他の空間と連通している空気層」の場合、空気層よりも室内側の建材の熱抵抗値の加算は不可
            # =これ以降の層の熱抵抗の値は計算しない
            if layer_l['layer_Name'] == 'AirLayer' and layer_l['Type'] == 'OnSiteConnected':
                break
    return sum_R_i_k_l, R_list


def calc_R_i_k_l(layer_l):
    """ 一般部位iの部分kの層lの熱抵抗 (5)

    :param layer_l: 層l
    :type: dict(SolidLayer_accurate/AirLayer_accurate/SolidLayer_simple1/AirLayer_simple1/SolidLayer_simple2/AirLayer_simple2/SolidLayer_rc/AirLayer_rc/SolidLayer_steel/AirLayer_steel/SolidLayer_foundation/AirLayer_foundation/)
    :return: 層lの熱抵抗
    :rtype: float
    """

    # 層lが固体の場合(6)
    if layer_l['layer_Name'] == 'SolidLayer':

        # 数値・素材名どちらも未入力の場合は「ERROR」
        if 'Material' not in layer_l and 'LambdaValue' not in layer_l:
            return 'ERROR'
        # 数値・素材名どちらも入力されている場合は素材名を優先する
        # 素材名を選択する場合、付録Aの表1/表2の値を熱伝導率に使う
        elif 'Material' in layer_l:
            lambda_i_k_l = thermophysical.calc_lambda(layer_l['Material'])
        # 素材名が空欄の場合は数値を利用する
        else:
            # 範囲チェック　範囲が正しければ計算に使う
            if range_correct(0.001, 999.999, layer_l['LambdaValue']):
                lambda_i_k_l = layer_l['LambdaValue']
            # 範囲が不正の場合は「ERROR」
            else:
                return 'ERROR'

        # 範囲チェック
        if range_correct(0.00, 1.00, layer_l['Thickness']):
            # 木造における外張断熱又は付加断熱の場合で、下地材などにより、断熱材を貫通する熱橋部
            # を有する場合は、外張断熱又は付加断熱の断熱材の熱抵抗に0.9を乗じて計算する。
            if 'ExternalReduction' in layer_l:
                if layer_l['ExternalReduction'] == 'Yes':
                    return layer_l['Thickness'] / lambda_i_k_l * 0.9
                    
            return layer_l['Thickness'] / lambda_i_k_l
        # 範囲が不正の場合は「ERROR」
        else:
            return 'ERROR'
            

    # 層lが空気の場合
    else:
        # 未入力の場合は「ERROR」
        if layer_l['Type'] == None:
            return 'ERROR'
        else:
            return thermophysical.get_table_4(layer_l['Type'])


# ============================================================================
# 5.2 開口部
# ============================================================================

def calc_Opening_U_i(opening_i):
    """ 開口部𝑖の熱貫流率

    :param opening_i: 開口部i
    :type opening_i: dict(Window/Door/WindowDoor)
    :return: 開口部𝑖の熱貫流率, 入力に計算結果を付加したデータ
    :rtype: float, dict
    """

    #### 熱貫流率計算(2020.09.10 HEESENV-74 時点) ####
    #### ○データ構造
    #### Window>WindowPart>Attachment Door>DoorPart>Attachment
    #### DoorWindow>WindowPart>Attachment
    ####           >DoorPart>Attachment
    #### 　⇒欄間付きドアの場合Attachmentは窓部分・ドア部分それぞれに付く
    #### ①窓・ドア
    #### 窓・ドアの熱貫流率を求め(5.2.4)、付属部材(5.2.1~3)の有無に応じて付属部材込みの熱貫流率を求める
    #### ②欄間付きドア
    #### ドア部分と窓部分についてそれぞれ①の方法で計算し、5.2.4式(10)より全体の熱貫流率を求める


    # 窓
    if opening_i['Method'] == 'Window':
        U_i = calc_OpeningPart_U_i(opening_i['WindowPart'], 'Window')
        opening_i['U_i'] = U_i
        return U_i, opening_i
    # ドア
    elif opening_i['Method'] == 'Door':
        U_i = calc_OpeningPart_U_i(opening_i['DoorPart'], 'Door')
        opening_i['U_i'] = U_i
        return U_i, opening_i
    # 欄間付きドア
    elif opening_i['Method'] == 'DoorWindow':
        # 窓部分の面積
        A_d_W = opening_i['WindowPart']['Area']
        # 窓部分の熱貫流率
        U_d_W = calc_OpeningPart_U_i(opening_i['WindowPart'], 'Window')
        # ドア部分の面積
        A_d_D = opening_i['DoorPart']['Area']
        # ドア部分の熱貫流率
        U_d_D = calc_OpeningPart_U_i(opening_i['DoorPart'], 'Door')
        U_i = get_U_d_windowdoor(U_d_W, U_d_D, A_d_W, A_d_D)
        opening_i['U_i'] = U_i
        return U_i, opening_i


def calc_OpeningPart_U_i(opening_part, opening_type):
    """ 開口部𝑖の窓(窓部分)・ドア(ドア部分)の熱貫流率

    :param opening_part: 開口部i
    :type opening_part: dict(WindowPart/DoorPart)
    :param opening_type: 開口部の種類
    :type opening_type: str(Window/Door)
    :return: 開口部𝑖の熱貫流率
    :rtype: float
    """

    # 付属部材が付与されずかつ風除室に面しない場合
    if 'Attachment' not in opening_part or opening_part['Attachment'] == 'No':
        return calc_No_Attachment_U_i(opening_part, opening_type)
    # 風除室に面する場合
    elif opening_part['Attachment'] == 'WindbreakSpace':
        return calc_Windbreak_U_i(opening_part, opening_type)
    # 付属部材が付与される場合
    else:
        return calc_Attachment_U_i(opening_part, opening_type)


# ============================================================================
# 5.2.1 付属部材が付与されずかつ風除室に面しない場合
# ============================================================================

def calc_No_Attachment_U_i(opening_part, opening_type):
    """ 付属部材が付与されずかつ風除室に面しない場合の開口部𝑖の熱貫流率

    :param opening_part: 開口部i
    :type opening_part: dict(WindowPart/DoorPart)
    :param opening_type: 開口部の種類
    :type opening_type: str(Window/Door)
    :return: 開口部𝑖の熱貫流率
    :rtype: float
    """

    try:
        return calc_U_d(opening_part, opening_type)
    # ノードの値に不正値が含まれている場合ValueErrorが発生
    # 計算結果は「ERROR」とする
    except ValueError:
        return 'ERROR'

# ============================================================================
# 5.2.2 付属部材が付与される場合
# ============================================================================


def calc_Attachment_U_i(opening_part, opening_type):
    """ 付属部材が付与される場合の開口部𝑖の熱貫流率 (6)

    :param opening_part: 開口部i
    :type opening_part: dict(WindowPart/DoorPart)
    :param opening_type: 開口部の種類
    :type opening_type: str(Window/Door)
    :return: 開口部𝑖の熱貫流率
    :rtype: float
    """

    try: 
        U_d_i = calc_U_d(opening_part, opening_type)
    # ノードの値に不正値が含まれている場合ValueErrorが発生
    # 計算結果は「ERROR」とする
    except ValueError:
        return 'ERROR'
        
    U_d_r_i = calc_Attachment_U_d_r_i(opening_part['Attachment'], U_d_i)

    return get_Attachment_U_i(U_d_i, U_d_r_i)


def get_Attachment_U_i(U_d_i, U_d_r_i):
    """ 付属部材が付与される場合の開口部𝑖の熱貫流率…………式(6)

    :param U_d_i: 窓又はドアiの熱貫流率
    :type U_d_i: float
    :param U_d_r_i: 付属部材が付与された窓又はドアiの熱貫流率（W/m2 K）
    :type U_d_r_i: float
    :return: 付属部材が付与される場合の開口部𝑖の熱貫流率
    :rtype: float
    """

    return 0.5 * U_d_i + 0.5 * U_d_r_i


def calc_Attachment_U_d_r_i(attachment, U_d_i):
    """ 付属部材が付与された窓又はドア𝑖の熱貫流率 (7)

    :param attachment: 付属部材 
    :type attachment: str
    :param U_d_i: 又はドアiの熱貫流率
    :type U_d_i: float
    :return: 開口部𝑖の熱貫流率
    :rtype: float
    """

    delta_R_arc = get_table_8(attachment)
    return 1.0 / ((1.0 / U_d_i) + delta_R_arc)


def get_table_8(Attachment):
    """ 表8 付属部材の熱抵抗

    :param Attachment: 付属部材
                        'Shutter'(シャッター又は雨戸)または'Shoji'(障子)
    :type Attachment: dict
    :return: 付属部の熱抵抗
    :rtype: float
    """

    # シャッター又は雨戸
    if Attachment == 'Shutter':
        return 0.10
    # 障子
    elif Attachment == 'Shoji':
        return 0.18


# ============================================================================
# 5.2.3 風除室に面する場合
# ============================================================================


def calc_Windbreak_U_i(opening_part, opening_type):
    """ 風除室に面する場合の開口部𝑖の熱貫流率 (8)

    :param opening_part: 開口部i
    :type opening_part: dict(WindowPart/DoorPart)
    :param opening_type: 開口部の種類
    :type opening_type: str(Window/Door)
    :return: 開口部𝑖の熱貫流率
    :rtype: float
    """

    try:
        U_d_i = calc_U_d(opening_part, opening_type)
    # ノードの値に不正値が含まれている場合ValueErrorが発生
    # 計算結果は「ERROR」とする
    except ValueError:
        return 'ERROR'
    return get_Windbreak_U_i(U_d_i)


def get_Windbreak_U_i(U_d_i):
    """ 風除室に面する場合の開口部𝑖の熱貫流率…………式(8)

    :param U_d_i: 窓又はドアiの熱貫流率…………calc_U_d
    :type U_d_i: float
    :return: 風除室に面する場合の開口部𝑖の熱貫流率
    :rtype: float
    """

    return 1.0 / ((1.0 / U_d_i) + 0.1)


# ============================================================================
# 5.2.4 窓又はドアの熱貫流率
# ============================================================================

def calc_U_d(opening_part, opening_type):
    """ 窓又はドアの熱貫流率

    :param opening_part: 開口部i
    :type opening_part: dict(WindowPart/DoorPart)
    :param opening_type: 開口部の種類
    :type opening_type: str(Window/Door)
    :return: 窓又はドアの熱貫流率
    :rtype: float
    """

    if opening_type == 'Window':
        return calc_U_d_window(opening_part)
    elif opening_type == 'Door':
        return calc_U_d_door(opening_part)
    else:
        raise ValueError("invalid value in type")


def calc_U_d_door(door_part):
    """ ドアの熱貫流率

    :param door: ドア
    :type door: dict(DoorPart)
    :return: ドアの熱貫流率
    :rtype: float
    """

    U_d = door_part['UValue']

    return U_d


def calc_U_d_window(window_part):
    """ 窓の熱貫流率

    :param window_part: 窓
    :type window_part: dict(WindowPart)
    :return: 窓の熱貫流率
    :rtype: float
    """

    # 二重窓の場合の熱貫流率…………式(9)
    if window_part['IsSetWindow'] == 'Yes':
        # 外気側窓の熱貫流率
        U_d_ex = window_part['UValue']
        # 室内側窓の熱貫流率
        U_d_in = window_part['UValueForInnerWindow']
        # 二重窓における外気側窓の伝熱開口面積
        A_ex = window_part['OuterHeatTransferOpeningArea']
        # 二重窓における室内側窓の伝熱開口面積
        A_in = window_part['InternalHeatTransferOpeningArea']
        # 二重窓における外気側と室内側の表面熱伝達抵抗の和
        R_s = 0.17
        # 二重窓における二重窓中空層の熱抵抗
        delta_R_a = 0.173
        U_d = get_U_d_setwindow(U_d_ex, U_d_in, A_ex, A_in, R_s, delta_R_a)
    else:
        U_d = window_part['UValue']

    return U_d


def get_U_d_setwindow(U_d_ex, U_d_in, A_ex, A_in, R_s, delta_R_a):
    """ 二重窓の場合の窓の熱貫流率U_d…………式(9)

    :param U_d_ex: 二重窓における外気側窓の熱貫流率…………入力(WindowPart>Uvalue)
    :type U_d_ex: float
    :param U_d_in: 二重窓における室内側窓の熱貫流率…………入力(WindowPart>UvalueForInnerWindow)
    :type U_d_in: float
    :param A_ex: 二重窓における外気側窓の伝熱開口面積…………入力(WindowPart>OuterHeatTransferOpeningArea)
    :type A_ex: float
    :param A_in: 二重窓における室内側窓の伝熱開口面積…………入力(WindowPart>InternalHeatTransferOpeningArea)
    :type A_in: float
    :param R_s: 二重窓における外気側と室内側の表面熱伝達抵抗の和…………0.17
    :type R_s: float
    :param delta_R_a: 二重窓における二重窓中空層の熱抵抗…………0.173
    :type delta_R_a: float
    :return: 窓の熱貫流率
    :rtype: float
    """

    return 1.0/( (1.0/U_d_ex) + (A_ex / (A_in*U_d_in) ) - R_s + delta_R_a )


def get_U_d_windowdoor(U_d_W, U_d_D, A_d_W, A_d_D):
    """ 欄間付きドア、袖付きドア等のドアや窓が同一枠内で併設される場合の開口部（窓又はドア）の熱貫流率U_d…………式(10)

    :param U_d_W: ドアや窓が同一枠内で併設される場合の開口部（窓又はドア）の窓部分の熱貫流率
    :type U_d_W: float
    :param U_d_D: ドアや窓が同一枠内で併設される場合の開口部（窓又はドア）のドア部分の熱貫流率
    :type U_d_D: float
    :param A_d_W: ドアや窓が同一枠内で併設される場合の開口部（窓又はドア）の窓部分の面積…………入力(WindowPart>Area)
    :type A_d_W: float
    :param A_d_D: ドアや窓が同一枠内で併設される場合の開口部（窓又はドア）のドア部分の面積…………入力(DoorPart>Area)
    :type A_d_D: float
    :return: 欄間付きドア、袖付きドア等のドアや窓が同一枠内で併設される場合の開口部（窓又はドア）の熱貫流率U_d
    :rtype: float
    """

    return (A_d_W * U_d_W + A_d_D * U_d_D) / (A_d_W + A_d_D)


def range_correct(min, max, num):
    """ 入力数値の範囲チェック

    :param min: 最小
    :type min: float
    :param max: 最大値
    :type max: float
    :param num: チェックする対象の値
    :type num: float
    :return: 範囲が正しいかどうか
    :rtype: bool(True:正しい,False:不正)
    """

    if min <= num and max >= num:
        return True
    else:
        return False

