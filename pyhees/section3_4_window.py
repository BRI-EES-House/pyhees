# 6 大部分がガラスで構成されている窓等の開口部

# 6.1 日射熱取得率
import pyhees.section3_4_a as gamma
from pyhees.section3_3_5 import calc_Opening_U_i
import pyhees.section3_4_b_1 as f
import pyhees.section3_4_c as eater_d


def get_eta_H_i(f_H_i, etr_d_i):
    """ 開口部の暖房期の日射熱取得率 (-) …………式(3)

    :param f_H_i: 開口部の暖房期の取得日射熱補正係数 (-)
    :type f_H_i: float
    :param etr_d_i: 開口部の垂直面日射熱出得率((W/m2)/(W/m2))
    :type etr_d_i: float
    :return: 開口部の暖房期の日射熱取得率((W/m2)/(W/m2))
    :rtype: float
    """
    return f_H_i * etr_d_i


def calc_eta_H_i_byDict(Region, Direction, window_part):
    """ WindowPart形式の辞書から窓・窓部分(ドアや窓が同一枠内で併設される場合)の暖房期の日射熱取得率を求める

    :param region: 省エネルギー地域区分
    :type region: int
    :param Direction: 方位
    :type Direction: str
    :param window_part: 窓
    :type window_part: dict(WindowPart)
    :return: 開口部の暖房期の日射熱取得率
    :rtype: float
    """

    
    # 取得日射熱補正係数
    # 日除けが設置されている場合
    if window_part['HasShade'] == 'Yes':
        # イ)地域の区分、方位及び日除けの形状に依らず定められた値を用いる方法
        if window_part['FcMethod'] == 'No':
            f_H_i = f.const.get_f_H_i()
        # ロ)地域の区分、方位及び日除けの形状（オーバーハング型）に応じて簡易的に算出する方法
        elif window_part['FcMethod'] == 'Simple':
            f_H_i = f.simple.get_f_H_i(Region, Direction, window_part['WindowTopToEaveHeight'], window_part['WindowHeight'], window_part['EaveDepth'])
        # ハ)地域の区分、方位及び日除けの形状に応じて算出した日除け効果係数と斜入射特性を用いる方法
        elif window_part['FcMethod'] == 'Accurate':
            f_ang_H = f.detail.get_table_b_1(Region, window_part['GlassSpecForCategory'], 'H', Direction)
            f_H_i = f.detail.get_f_H_i(f_ang_H, window_part['GammaH'])
    # 日除けが設置されていない場合/屋根又は屋根の直下の天井に設置されている開口部の場合
    elif window_part['HasShade'] == 'No' or Direction == 'Top':
        # イ)地域の区分、方位及び日除けの形状に依らず定められた値を用いる方法
        if window_part['FcMethod'] == 'No':
            f_H_i = f.const.get_f_H_i()
        # ハ)地域の区分、方位及び日除けの形状に応じて算出した日除け効果係数と斜入射特性を用いる方法
        elif window_part['FcMethod'] == 'Accurate':
            f_ang_H = f.detail.get_table_b_1(Region, window_part['GlassSpecForCategory'], 'H', Direction)
            # 日除け効果係数は1.0とする
            f_H_i = f.detail.get_f_H_i(f_ang_H, 1.0)
        else:
            raise ValueError(window_part['FcMethod'])

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
    """ 開口部の冷房期の日射熱取得率 (-)…………式(4)

    :param f_C_i: 開口部の冷房期の取得日射熱補正係数 (-)
    :type f_C_i: float
    :param etr_d_i: 開口部の垂直面日射熱出得率 ((W/m2)/(W/m2))
    :type etr_d_i: float
    :return: 開口部の冷房期の日射熱取得率((W/m2)/(W/m2))
    :rtype:
    """
    return f_C_i * etr_d_i


def calc_eta_C_i_byDict(Region, Direction, window_part):
    """ Window形式の辞書から窓・窓部分(ドアや窓が同一枠内で併設される場合)の冷房期の日射熱取得率を求める

    :param region: 省エネルギー地域区分
    :type region: int
    :param Direction: 方位
    :type Direction: str
    :param window_part: 窓
    :type window_part: dict(WindowPart)
    :return: 開口部の冷房期の日射熱取得率
    :rtype: float
    """
    
    # 取得日射熱補正係数
    # 日除けが設置されている場合
    if window_part['HasShade'] == 'Yes':
        # イ)地域の区分、方位及び日除けの形状に依らず定められた値を用いる方法
        if window_part['FcMethod'] == 'No':
            f_C_i = f.const.get_f_C_i()
        # ロ)地域の区分、方位及び日除けの形状（オーバーハング型）に応じて簡易的に算出する方法
        elif window_part['FcMethod'] == 'Simple':
            f_C_i = f.simple.get_f_C_i(Region, Direction, window_part['WindowTopToEaveHeight'], window_part['WindowHeight'], window_part['EaveDepth'])
        # ハ)地域の区分、方位及び日除けの形状に応じて算出した日除け効果係数と斜入射特性を用いる方法
        elif window_part['FcMethod'] == 'Accurate':
            f_ang_C = f.detail.get_table_b_1(Region, window_part['GlassSpecForCategory'], 'C', Direction)
            f_C_i = f.detail.get_f_C_i(f_ang_C, window_part['GammaC'])
    # 日除けが設置されていない場合/屋根又は屋根の直下の天井に設置されている開口部の場合
    elif window_part['HasShade'] == 'No' or Direction == 'Top':
        # イ)地域の区分、方位及び日除けの形状に依らず定められた値を用いる方法
        if window_part['FcMethod'] == 'No':
            f_C_i = f.const.get_f_C_i()
        # ハ)地域の区分、方位及び日除けの形状に応じて算出した日除け効果係数と斜入射特性を用いる方法
        elif window_part['FcMethod'] == 'Accurate':
            f_ang_C = f.detail.get_table_b_1(Region, window_part['GlassSpecForCategory'], 'C', Direction)
            # 日除け効果係数は1.0とする
            f_C_i = f.detail.get_f_C_i(f_ang_C, 1.0)


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
    """ 二重窓等の複数の開口部が組み合わさった開口部の垂直面日射熱取得率 (-) (5)

    :param etr_d1_i: 開口部の外気側の窓の垂直面日射熱取得率 (-)
    :type etr_d1_i: float
    :param  etr_d2_i: 開口部の室内側の窓の垂直面日射熱取得率 (-)
    :type etr_d2_i: float
    :param r_f: 開口部の全体の面積に対するガラス部分の面積の比 (-)
    :type r_f: float
    :return: 二重窓等の複数の開口部が組み合わさった開口部の垂直面日射熱取得率
    :rtype: float
    """
    return etr_d1_i * etr_d2_i * 1.06 / r_f


def get_r_f(frame_type):
    """ 開口部の全体の面積に対するガラス部分の面積の比 (-)

    :param frame_type: 枠の種類
    :type frame_type: str
    :return: 開口部の全体の面積に対するガラス部分の面積の比
    :rtype: float
    """
    if frame_type == '室内側の窓及び外気側の窓の両方の枠が木製建具又は樹脂製建具':
        return 0.72
    elif frame_type == 'それ以外':
        return 0.8
    else:
        raise ValueError(frame_type)


def calc_etr_g_byKey(glass_type, attachment):
    """ ノードの値から垂直面日射熱取得率を取得（C 表1）

    :param glass_type : ガラス仕様の区分
    :type glass_type : String
    :param attachment : 付属品部材
    :type attachment : String
    :return: 垂直面日射熱取得率
    :rtype: float
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



### HEESENV-66(2020/08/27)
# 簡易計算では仕様変更前の計算方法を用いるため、仕様変更前のものを残す
# 以下、仕様変更前
###


# 6 大部分がガラスで構成されている窓等の開口部

# 6.1 日射熱取得率
from pyhees.section3_4_b_2 import get_glass_spec_category
from pyhees.section3_4_b_1_1 import *
import pyhees.section3_4_b as f

def get_eta_H_i(f_H_i, etr_d_i):
    """ 開口部の暖房期の日射熱取得率 (-) (3)

    :param f_H_i: 開口部の暖房期の取得日射熱補正係数 (-)
    :type f_H_i: float
    :param etr_d_i: 開口部の垂直面日射熱出得率((W/m2)/(W/m2))
    :type etr_d_i: float
    :return: 開口部の暖房期の日射熱取得率((W/m2)/(W/m2))
    :rtype: float
    """
    return f_H_i * etr_d_i


def get_eta_C_i(f_C_i, etr_d_i):
    """ 開口部の冷房期の日射熱取得率 (-) (4)

    :param f_C_i: 開口部の冷房期の取得日射熱補正係数 (-)
    :type f_C_i: float
    :param etr_d_i: 開口部の垂直面日射熱出得率 ((W/m2)/(W/m2))
    :type etr_d_i: float
    :return: 開口部の冷房期の日射熱取得率((W/m2)/(W/m2))
    :rtype:
    """
    return f_C_i * etr_d_i


# 6.2 垂直面日射熱取得率

def get_eta_d_i(etr_d1_i, etr_d2_i, r_f):
    """ 二重窓等の複数の開口部が組み合わさった開口部の垂直面日射熱取得率 (-) (5)

    :param etr_d1_i: 開口部の外気側の窓の垂直面日射熱取得率 (-)
    :type etr_d1_i: float
    :param  etr_d2_i: 開口部の室内側の窓の垂直面日射熱取得率 (-)
    :type etr_d2_i: float
    :param r_f: 開口部の全体の面積に対するガラス部分の面積の比 (-)
    :type r_f: float
    :return: 二重窓等の複数の開口部が組み合わさった開口部の垂直面日射熱取得率
    :rtype: float
    """
    return etr_d1_i * etr_d2_i * 1.06 / r_f


def get_r_f(frame_type):
    """ 開口部の全体の面積に対するガラス部分の面積の比 (-)

    :param frame_type: 枠の種類
    :type frame_type: str
    :return: 開口部の全体の面積に対するガラス部分の面積の比
    :rtype: float
    """
    if frame_type == '室内側の窓及び外気側の窓の両方の枠が木製建具又は樹脂製建具':
        return 0.72
    elif frame_type == 'それ以外':
        return 0.8
    else:
        raise ValueError(frame_type)