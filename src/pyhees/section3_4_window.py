# 6 大部分がガラスで構成されている窓等の開口部

# 6.1 日射熱取得率
from pyhees.section3_3_5 import calc_Opening_U_i
import pyhees.section3_4_b_1 as f
import pyhees.section3_4_c as eater_d


def get_eta_H_i(f_H_i, etr_d_i):
    """開口部の暖房期の日射熱取得率 (-) …………式(3)

    Args:
      f_H_i(float): 開口部の暖房期の取得日射熱補正係数 (-)
      etr_d_i(float): 開口部の垂直面日射熱出得率((W/m2)/(W/m2))

    Returns:
      float: 開口部の暖房期の日射熱取得率((W/m2)/(W/m2))

    """
    return f_H_i * etr_d_i


def calc_eta_H_i_byDict(Region, Direction, window_part):
    """WindowPart形式の辞書から窓・窓部分(ドアや窓が同一枠内で併設される場合)の暖房期の日射熱取得率を求める

    Args:
      region(int): 省エネルギー地域区分
      Direction(str): 方位
      window_part(dict(WindowPart)): 窓
      Region: returns: 開口部の暖房期の日射熱取得率

    Returns:
      float: 開口部の暖房期の日射熱取得率

    """

    
    # 取得日射熱補正係数
    # 1) 外壁に設置される開口部の場合、方法イ）、ロ）及びハ）を用いることができる
    if Direction in ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE', 'Bottom']:
        # イ)地域の区分、方位及び日除けの形状に依らず定められた値を用いる方法
        if window_part['FcMethod'] == 'No':
            f_H_i = f.const.get_f_H_i()
        # ロ)地域の区分、方位及び日除けの形状（オーバーハング型）に応じて簡易的に算出する方法
        elif window_part['FcMethod'] == 'Simple':
            has_over_hang = {
                'Yes': True,
                'No':  False,
            }[window_part['HasShade']]
            y1 = window_part.get('WindowTopToEaveHeight')
            y2 = window_part.get('WindowHeight')
            z  = window_part.get('EaveDepth')
            f_H_i = f.simple.get_f_H_i(Region, Direction, has_over_hang, y1, y2, z)
        # ハ)地域の区分、方位及び日除けの形状に応じて算出した日除け効果係数と斜入射特性を用いる方法
        elif window_part['FcMethod'] == 'Accurate':
            f_ang_H = f.detail.get_table_b_1(Region, window_part['GlassSpecForCategory'], 'H', Direction)
            f_H_i = f.detail.get_f_H_i(f_ang_H, window_part['GammaH'], Direction)
        else:
            raise ValueError(window_part['FcMethod'])
    # 2) 屋根又は屋根の直下の天井に設置されている開口部の場合、方法イ）及びハ）を用いることができる
    elif Direction == 'Top':
        # イ)地域の区分、方位及び日除けの形状に依らず定められた値を用いる方法
        if window_part['FcMethod'] == 'No':
            f_H_i = f.const.get_f_H_i()
        # ハ)地域の区分、方位及び日除けの形状に応じて算出した日除け効果係数と斜入射特性を用いる方法
        elif window_part['FcMethod'] == 'Accurate':
            f_ang_H = f.detail.get_table_b_1(Region, window_part['GlassSpecForCategory'], 'H', Direction)
            f_H_i = f.detail.get_f_H_i(f_ang_H, window_part['GammaH'], Direction)
        else:
            raise ValueError(window_part['FcMethod'])
    else:
        raise ValueError(Direction)

    # 垂直面日射熱取得率
    # 二重窓
    if window_part['IsSetWindow'] == 'Yes':
        if 'SolarHeatGainCoefficient' in window_part:
            etr_g1_i = window_part['SolarHeatGainCoefficient']
        else:
            # 付属部材
            # 和障子の場合は室内側の窓の垂直面日射熱取得率に含める
            if window_part['Attachment'] == 'Shoji':
                etr_g1_i = calc_etr_g_byKey(window_part['GlassType'], 'No')
            # 外付けブラインドの場合は外気側の窓の垂直面日射熱取得率に含める
            elif window_part['Attachment'] == 'ExteriorBlind':
                etr_g1_i = calc_etr_g_byKey(window_part['GlassType'], 'ExteriorBlind')
            else:
                etr_g1_i = calc_etr_g_byKey(window_part['GlassType'], 'No')

        if 'SolarHeatGainCoefficientForInnerWindow' in window_part:
            etr_g2_i = window_part['SolarHeatGainCoefficientForInnerWindow']
        else:
            # 付属部材
            # 和障子の場合は室内側の窓の垂直面日射熱取得率に含める
            if window_part['Attachment'] == 'Shoji':
                etr_g2_i = calc_etr_g_byKey(window_part['GlassTypeForInnerWindow'], 'Shoji')
            # 外付けブラインドの場合は外気側の窓の垂直面日射熱取得率に含める
            elif window_part['Attachment'] == 'ExteriorBlind':
                etr_g2_i = calc_etr_g_byKey(window_part['GlassTypeForInnerWindow'], 'No')
            else:
                etr_g2_i = calc_etr_g_byKey(window_part['GlassTypeForInnerWindow'], 'No')

        # 枠の影響を考慮しない場合
        if window_part['FrameRef'] == 'No':
            etr_d1_i = eater_d.get_etr_d_i(etr_g1_i, '影響がない')
            etr_d2_i = eater_d.get_etr_d_i(etr_g2_i, '影響がない')
        # 枠の影響を考慮する場合
        else:
            # 外窓
            # 木製建具又は樹脂製建具
            if window_part['SashSpec'] == 'WoodenOrResin':
                etr_d1_i = eater_d.get_etr_d_i(etr_g1_i, '木製建具又は樹脂製建具')
            # 木と金属の複合材料製建具、樹脂と金属の複合材料製建具、金属製熱遮断構造建具又は金属製建具
            else:
                etr_d1_i = eater_d.get_etr_d_i(etr_g1_i, '木と金属の複合材料製建具、樹脂と金属の複合材料製建具、金属製熱遮断構造建具又は金属製建具')
            
            # 内窓
            # 木製建具又は樹脂製建具
            if window_part['SashSpecForInnerWindow'] == 'WoodenOrResin':
                etr_d2_i = eater_d.get_etr_d_i(etr_g2_i, '木製建具又は樹脂製建具')
            # 木と金属の複合材料製建具、樹脂と金属の複合材料製建具、金属製熱遮断構造建具又は金属製建具
            else:
                etr_d2_i = eater_d.get_etr_d_i(etr_g2_i, '木と金属の複合材料製建具、樹脂と金属の複合材料製建具、金属製熱遮断構造建具又は金属製建具')

        if window_part['SashSpec'] == 'WoodenOrResin' and window_part['SashSpecForInnerWindow'] == 'WoodenOrResin':
            r_f = get_r_f('室内側の窓及び外気側の窓の両方の枠が木製建具又は樹脂製建具')
        else:
            r_f = get_r_f('それ以外')
        
        etr_d_i = get_eta_d_i(etr_d1_i, etr_d2_i, r_f)

    # 二重窓でない
    else:
        if 'SolarHeatGainCoefficient' in window_part:
            etr_g_i = window_part['SolarHeatGainCoefficient']
        else:
            etr_g_i = calc_etr_g_byKey(window_part['GlassType'], window_part['Attachment'])
        # 枠の影響を考慮しない場合
        if window_part['FrameRef'] == 'No':
            etr_d_i = eater_d.get_etr_d_i(etr_g_i, '影響がない')
        # 枠の影響を考慮する場合
        else:
            # 木製建具又は樹脂製建具
            if window_part['SashSpec'] == 'WoodenOrResin':
                etr_d_i = eater_d.get_etr_d_i(etr_g_i, '木製建具又は樹脂製建具')
            # 木と金属の複合材料製建具、樹脂と金属の複合材料製建具、金属製熱遮断構造建具又は金属製建具
            else:
                etr_d_i = eater_d.get_etr_d_i(etr_g_i, '木と金属の複合材料製建具、樹脂と金属の複合材料製建具、金属製熱遮断構造建具又は金属製建具')
    
    return get_eta_H_i(f_H_i, etr_d_i)



def get_eta_C_i(f_C_i, etr_d_i):
    """開口部の冷房期の日射熱取得率 (-)…………式(4)

    Args:
      f_C_i(float): 開口部の冷房期の取得日射熱補正係数 (-)
      etr_d_i(float): 開口部の垂直面日射熱出得率 ((W/m2)/(W/m2))

    Returns:
      開口部の冷房期の日射熱取得率((W/m2)/(W/m2))

    """
    return f_C_i * etr_d_i


def calc_eta_C_i_byDict(Region, Direction, window_part):
    """Window形式の辞書から窓・窓部分(ドアや窓が同一枠内で併設される場合)の冷房期の日射熱取得率を求める

    Args:
      region(int): 省エネルギー地域区分
      Direction(str): 方位
      window_part(dict(WindowPart)): 窓
      Region: returns: 開口部の冷房期の日射熱取得率

    Returns:
      float: 開口部の冷房期の日射熱取得率

    """
    
    # 取得日射熱補正係数
    # 1) 外壁に設置される開口部の場合、方法イ）、ロ）及びハ）を用いることができる
    if Direction in ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE', 'Bottom']:
        # イ)地域の区分、方位及び日除けの形状に依らず定められた値を用いる方法
        if window_part['FcMethod'] == 'No':
            f_C_i = f.const.get_f_C_i()
        # ロ)地域の区分、方位及び日除けの形状（オーバーハング型）に応じて簡易的に算出する方法
        elif window_part['FcMethod'] == 'Simple':
            has_over_hang = {
                'Yes': True,
                'No':  False,
            }[window_part['HasShade']]
            y1 = window_part.get('WindowTopToEaveHeight')
            y2 = window_part.get('WindowHeight')
            z  = window_part.get('EaveDepth')
            f_C_i = f.simple.get_f_C_i(Region, Direction, has_over_hang, y1, y2, z)
        # ハ)地域の区分、方位及び日除けの形状に応じて算出した日除け効果係数と斜入射特性を用いる方法
        elif window_part['FcMethod'] == 'Accurate':
            f_ang_C = f.detail.get_table_b_1(Region, window_part['GlassSpecForCategory'], 'C', Direction)
            f_C_i = f.detail.get_f_C_i(f_ang_C, window_part['GammaC'], Direction)
        else:
            raise ValueError(window_part['FcMethod'])
    # 2) 屋根又は屋根の直下の天井に設置されている開口部の場合、方法イ）及びハ）を用いることができる
    elif Direction == 'Top':
        # イ)地域の区分、方位及び日除けの形状に依らず定められた値を用いる方法
        if window_part['FcMethod'] == 'No':
            f_C_i = f.const.get_f_C_i()
        # ハ)地域の区分、方位及び日除けの形状に応じて算出した日除け効果係数と斜入射特性を用いる方法
        elif window_part['FcMethod'] == 'Accurate':
            f_ang_C = f.detail.get_table_b_1(Region, window_part['GlassSpecForCategory'], 'C', Direction)
            f_C_i = f.detail.get_f_C_i(f_ang_C, window_part['GammaC'], Direction)
    else:
        raise ValueError(Direction)

    # 垂直面日射熱取得率
    # 二重窓
    if window_part['IsSetWindow'] == 'Yes':
        if 'SolarHeatGainCoefficient' in window_part:
            etr_g1_i = window_part['SolarHeatGainCoefficient']
        else:
            # 付属部材
            # 和障子の場合は室内側の窓の垂直面日射熱取得率に含める
            if window_part['Attachment'] == 'Shoji':
                etr_g1_i = calc_etr_g_byKey(window_part['GlassType'], 'No')
            # 外付けブラインドの場合は外気側の窓の垂直面日射熱取得率に含める
            elif window_part['Attachment'] == 'ExteriorBlind':
                etr_g1_i = calc_etr_g_byKey(window_part['GlassType'], 'ExteriorBlind')
            else:
                etr_g1_i = calc_etr_g_byKey(window_part['GlassType'], 'No')

        if 'SolarHeatGainCoefficientForInnerWindow' in window_part:
            etr_g2_i = window_part['SolarHeatGainCoefficientForInnerWindow']
        else:
            # 付属部材
            # 和障子の場合は室内側の窓の垂直面日射熱取得率に含める
            if window_part['Attachment'] == 'Shoji':
                etr_g2_i = calc_etr_g_byKey(window_part['GlassTypeForInnerWindow'], 'Shoji')
            # 外付けブラインドの場合は外気側の窓の垂直面日射熱取得率に含める
            elif window_part['Attachment'] == 'ExteriorBlind':
                etr_g2_i = calc_etr_g_byKey(window_part['GlassTypeForInnerWindow'], 'No')
            else:
                etr_g2_i = calc_etr_g_byKey(window_part['GlassTypeForInnerWindow'], 'No')


        # 枠の影響を考慮しない場合
        if window_part['FrameRef'] == 'No':
            etr_d1_i = eater_d.get_etr_d_i(etr_g1_i, '影響がない')
            etr_d2_i = eater_d.get_etr_d_i(etr_g2_i, '影響がない')
        # 枠の影響を考慮する場合
        else:
            # 外窓
            # 木製建具又は樹脂製建具
            if window_part['SashSpec'] == 'WoodenOrResin':
                etr_d1_i = eater_d.get_etr_d_i(etr_g1_i, '木製建具又は樹脂製建具')
            # 木と金属の複合材料製建具、樹脂と金属の複合材料製建具、金属製熱遮断構造建具又は金属製建具
            else:
                etr_d1_i = eater_d.get_etr_d_i(etr_g1_i, '木と金属の複合材料製建具、樹脂と金属の複合材料製建具、金属製熱遮断構造建具又は金属製建具')
            
            # 内窓
            # 木製建具又は樹脂製建具
            if window_part['SashSpecForInnerWindow'] == 'WoodenOrResin':
                etr_d2_i = eater_d.get_etr_d_i(etr_g2_i, '木製建具又は樹脂製建具')
            # 木と金属の複合材料製建具、樹脂と金属の複合材料製建具、金属製熱遮断構造建具又は金属製建具
            else:
                etr_d2_i = eater_d.get_etr_d_i(etr_g2_i, '木と金属の複合材料製建具、樹脂と金属の複合材料製建具、金属製熱遮断構造建具又は金属製建具')

        if window_part['SashSpec'] == 'WoodenOrResin' and window_part['SashSpecForInnerWindow'] == 'WoodenOrResin':
            r_f = get_r_f('室内側の窓及び外気側の窓の両方の枠が木製建具又は樹脂製建具')
        else:
            r_f = get_r_f('それ以外')
        
        etr_d_i = get_eta_d_i(etr_d1_i, etr_d2_i, r_f)

    # 二重窓でない
    else:
        if 'SolarHeatGainCoefficient' in window_part:
            etr_g_i = window_part['SolarHeatGainCoefficient']
        else:
            etr_g_i = calc_etr_g_byKey(window_part['GlassType'], window_part['Attachment'])
        # 枠の影響を考慮しない場合
        if window_part['FrameRef'] == 'No':
            etr_d_i = eater_d.get_etr_d_i(etr_g_i, '影響がない')
        # 枠の影響を考慮する場合
        else:
            # 木製建具又は樹脂製建具
            if window_part['SashSpec'] == 'WoodenOrResin':
                etr_d_i = eater_d.get_etr_d_i(etr_g_i, '木製建具又は樹脂製建具')
            # 木と金属の複合材料製建具、樹脂と金属の複合材料製建具、金属製熱遮断構造建具又は金属製建具
            else:
                etr_d_i = eater_d.get_etr_d_i(etr_g_i, '木と金属の複合材料製建具、樹脂と金属の複合材料製建具、金属製熱遮断構造建具又は金属製建具')
    
    return get_eta_C_i(f_C_i, etr_d_i)


# 6.2 垂直面日射熱取得率

def get_eta_d_i(etr_d1_i, etr_d2_i, r_f):
    """二重窓等の複数の開口部が組み合わさった開口部の垂直面日射熱取得率 (-) (5)

    Args:
      etr_d1_i(float): 開口部の外気側の窓の垂直面日射熱取得率 (-)
      etr_d2_i(float): 開口部の室内側の窓の垂直面日射熱取得率 (-)
      r_f(float): 開口部の全体の面積に対するガラス部分の面積の比 (-)

    Returns:
      float: 二重窓等の複数の開口部が組み合わさった開口部の垂直面日射熱取得率

    """
    return etr_d1_i * etr_d2_i * 1.06 / r_f


def get_r_f(frame_type):
    """開口部の全体の面積に対するガラス部分の面積の比 (-)

    Args:
      frame_type(str): 枠の種類

    Returns:
      float: 開口部の全体の面積に対するガラス部分の面積の比

    """
    if frame_type == '室内側の窓及び外気側の窓の両方の枠が木製建具又は樹脂製建具':
        return 0.72
    elif frame_type == 'それ以外':
        return 0.8
    else:
        raise ValueError(frame_type)


def calc_etr_g_byKey(glass_type, attachment):
    """ノードの値から垂直面日射熱取得率を取得（C 表1）

    Args:
      glass_type(String): ガラス仕様の区分
      attachment(String): 付属品部材

    Returns:
      float: 垂直面日射熱取得率

    """

    # ノードの値と関数get_etr_g内のガラス仕様の区分を対応づける
    type_dict = {
        '3PairDoubleLowEG':'2枚以上のガラス表面にLow-E膜を使用したLow-E三層複層ガラス(日射取得型)',
        '3PairDoubleLowES':'2枚以上のガラス表面にLow-E膜を使用したLow-E三層複層ガラス(日射遮蔽型)',
        '3PairLowEG':'Low-E三層複層ガラス(日射取得型)',
        '3PairLowES':'Low-E三層複層ガラス(日射遮蔽型)',
        '3PairClear':'三層複層ガラス',
        '2PairLowEG':'Low-E二層複層ガラス(日射取得型)',
        '2PairLowES':'Low-E二層複層ガラス(日射遮蔽型)',
        '2PairClear':'二層複層ガラス',
        '2PairSingleClear':'単板ガラス2枚を組み合わせたもの',
        'SingleClear':'単板ガラス'
    }

    attachment_dict = {
        'No':'付属部材なし',
        'Shoji':'和障子',
        'ExteriorBlind':'外付けブラインド'
    }

    return eater_d.get_etr_g(type_dict[glass_type], attachment_dict[attachment])
