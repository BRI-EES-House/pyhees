# ============================================================================
# 第三章 暖冷房負荷と外皮性能
# 第三節 熱貫流率及び線熱貫流率
# Ver.17（住宅・住戸の外皮性能の計算プログラム Ver.3.0.0～）
# ============================================================================


# ============================================================================
# 付録A 住宅の平均熱貫流率算出に用いる建材等の熱物性値等
# ============================================================================

def calc_lambda(material):
    """表1と表2より材質の熱伝導率を得る

    Args:
      material(str): 建材等名称

    Returns:
      float: 熱伝導率λ(W/mK)

    """
    if material != None:
        try:
            return get_table_1(material)
        except KeyError:
            try:
                return get_table_2(material)
            except KeyError:
                raise ValueError(material)


def get_table_1(material):
    """表1 建材等の熱物性値

    Args:
      material(str): 建材等名称

    Returns:
      float: 熱伝導率λ(W/mK)

    """

    material_dict = {}

    # 金属：鋼 アルミニウム 銅 ステンレス鋼
    metal_dict = {'Steel': 55, 'Aluminum': 210,
                  'Copper': 370, 'StainlessSteel': 15}
    material_dict.update(metal_dict)

    # 岩石・土壌：岩石 土壌
    rock_mud_dict = {'Rock': 3.1, 'Mud': 1.0}
    material_dict.update(rock_mud_dict)

    # コンクリート系材料：コンクリート 軽量コンクリート(軽量1種) 軽量コンクリート(軽量2種)
    #           コンクリートブロック(重量) コンクリートブロック(軽量) セメント・モルタル 押出成型セメント板
    concrete_dict = {'Concrete': 1.6, 'LC1': 0.8, 'LC2': 0.5,
                     'CBheavy': 1.1, 'CBlight': 0.53, 'Mortar': 1.5, 'ECP': 0.40}
    material_dict.update(concrete_dict)

    # 非木質系壁材・下地材：せっこうプラスター しっくい 土壁 ガラス
    #           タイル れんが かわら ロックウール化粧吸音板 火山性ガラス質複層板
    notwoood_dict = {'GypsumPlaster': 0.60, 'CementPlaster': 0.74, 'MudWall': 0.69, 'Glass': 1.0,
                     'Tile': 1.3, 'Brick': 0.64, 'RoofTile': 1.0, 'DressedRockwoolBoard': 0.064, 'Vsboard': 0.13}
    material_dict.update(notwoood_dict)

    # 木質系壁材・下地材：天然木材 合板 木毛セメント板 木片セメント板
    #           ハードファイバーボード(ハードボード) ミディアムデンシティファイバーボード(MDF) 直交集成板(CLTパネル)
    wood_dict = {'Wood': 0.12, 'PlywoodBoard': 0.16, 'CementWoodWool': 0.13, 'CementWoodFlake': 0.15,
                 'HardFiberBoard': 0.17, 'MDF': 0.12, 'CLT': 0.12}
    material_dict.update(wood_dict)

    # 床材：ビニル系床材 FRP
    #           アスファルト類 畳 カーペット類
    floor_dict = {'VinylFloor': 0.19, 'FRP': 0.26,
                  'Asphart': 0.11, 'Tatami': 0.083, 'Carpet': 0.08}
    material_dict.update(floor_dict)

    # グラスウール断熱材：グラスウール断熱材10K相当 グラスウール断熱材16K相当 グラスウール断熱材20K相当
    #           グラスウール断熱材24K相当 グラスウール断熱材32K相当
    #           高性能グラスウール断熱材16K相当 高性能グラスウール断熱材24K相当 高性能グラスウール断熱材32K相当
    #           高性能グラスウール断熱材40K相当 高性能グラスウール断熱材48K相当
    #           吹込み用グラスウール13K相当 吹込み用グラスウール18K相当 吹込み用グラスウール30K相当 吹込み用グラスウール35K相当
    gw_dict = {'GW10K': 0.050, 'GW16K': 0.045, 'GW20K': 0.042,
               'GW24K': 0.038, 'GW32K': 0.036,
               'HGW16K': 0.038, 'HGW24K': 0.036, 'HGW32K': 0.035,
               'HGW40K': 0.034, 'HGW48K': 0.033,
               'BlowingGW13K': 0.052, 'BlowingGW18K': 0.052, 'BlowingGW30K': 0.040, 'BlowingGW35K': 0.040}
    material_dict.update(gw_dict)

    # ロックウール断熱材：吹付けロックウール ロックウール断熱材(マット) ロックウール断熱材(フェルト) ロックウール断熱材(ボード)
    #           吹込み用ロックウール25K相当 吹込み用ロックウール65K相当
    rock_wool_dict = {'SprayedRockWool': 0.064, 'RockWoolMat': 0.038, 'RockWoolFelt': 0.038, 'RockWoolBoard': 0.036,
                      'BlowingRockWool25K': 0.047, 'BlowingRockWool65K': 0.039}
    material_dict.update(rock_wool_dict)

    # セルローズファイバー断熱材：吹込み用セルローズファイバー25K
    #           吹込み用セルローズファイバー45K吹込み用セルローズファイバー55K
    cellulose_dict = {'BlowingCelluloseFiber25K': 0.040,
                      'BlowingCelluloseFiber45K': 0.040, 'BlowingCelluloseFiber55K': 0.040}
    material_dict.update(cellulose_dict)

    # ポリスチレンフォーム断熱材：押出法ポリスチレンフォーム保温板1種 押出法ポリスチレンフォーム保温板2種 押出法ポリスチレンフォーム保温板3種
    #           A種ポリエチレンフォーム保温板1種2号 A種ポリエチレンフォーム保温板2種 ビーズ法ポリスチレンフォーム保温板特号
    #           ビーズ法ポリスチレンフォーム保温板1号 ビーズ法ポリスチレンフォーム保温板2号
    #           ビーズ法ポリスチレンフォーム保温板3号 ビーズ法ポリスチレンフォーム保温板4号
    polyethylene_dict = {'XPSPlate1': 0.040, 'XPSPlate2': 0.034, 'XPSPlate3': 0.028,
                         'PolyethyleneFoam1': 0.042, 'PolyethyleneFoam2': 0.038, 'EPSPlateSP': 0.034,
                         'EPSPlate1': 0.036, 'EPSPlate2': 0.037,
                         'EPSPlate3': 0.040, 'EPSPlate4': 0.043}
    material_dict.update(polyethylene_dict)

    # ウレタンフォーム断熱材：硬質ウレタンフォーム保温板2種1号 硬質ウレタンフォーム保温板2種2号
    urethane_dict = {'PUFPlate1': 0.023, 'PUFPlate2': 0.024}
    material_dict.update(urethane_dict)

    # フェノールフォーム断熱材：フェノールフォーム保温板1種1号 フェノールフォーム保温板1種2号
    phenolic_dict = {'PhenolicFoamPlate1': 0.022, 'PhenolicFoamPlate2': 0.022}
    material_dict.update(phenolic_dict)

    return material_dict[material]


def get_table_2(material):
    """表2 JISで熱物性値の定めのある建材等の熱物性値

    Args:
      material(str): 建材名称

    Returns:
      float: 熱伝導率λ(W/mK)

    """

    material_dict = {}

    # コンクリート系材料：軽量気泡コンクリートパネル(ALCパネル)
    concrete_dict = {'ALC': 0.19}
    material_dict.update(concrete_dict)

    # 非木質系壁材・下地材：せっこうボード/GB-R/GB-D/GB-L/GB-NC, せっこうボード/GB-S/GB-F, せっこうボード/GB-R-H/GB-S-H/GB-D-H,
    #           0.8ケイ酸カルシウム板, 1.0ケイ酸カルシウム板
    notwoood_dict = {'GB_R_D_L_NC': 0.221, 'GB_S_F': 0.241, 'GB_RH_SH_DH': 0.366,
                     'CalciumSilicateBoard08': 0.18, 'CalciumSilicateBoard10': 0.24}

    # 木質系壁材・下地材：タタミボード, A級インシュレーションボード,
    #           シージングボード, パーティクルボード
    wood_dict = {'TatamiBoard': 0.056, 'InsulationBoardA': 0.058,
                 'GypsumSheathingBoard': 0.067, 'ParticleBoard': 0.167}
    material_dict.update(wood_dict)

    # 床材：稲わら畳床, ポリスチレンフォームサンドイッチ稲わら畳床, タタミボードサンドイッチ稲わら畳床,
    #           建材畳床(Ⅰ形), 建材畳床(Ⅱ形), 建材畳床(Ⅲ形), 建材畳床(K、N形)
    floor_dict = {'RiceStrawTatamiFloor': 0.07, 'PFSRiceStrawTatamiFloor': 0.054, 'TBSRiceStrawTatamiFloor': 0.063,
                  'TatamiFloor1': 0.062, 'TatamiFloor2': 0.053, 'TatamiFloor3': 0.052, 'TatamiFloorKN': 0.050}
    material_dict.update(floor_dict)

    # グラスウール断熱材：通常品10-50, 通常品10-49, 通常品10-48, 通常品12-45, 通常品12-44,
    #           通常品16-45, 通常品16-44, 通常品20-42, 通常品20-41, 通常品20-40,
    #           通常品24-38, 通常品32-36, 通常品40-36, 通常品48-35, 通常品64-35, 通常品80-33, 通常品96-33,
    #           高性能品HG10-47, 高性能品HG10-46, 高性能品HG10-45, 高性能品HG10-44, 高性能品HG10-43,
    #           高性能品HG12-43, 高性能品HG12-42, 高性能品HG12-41, 高性能品HG14-38, 高性能品HG14-37,
    #           高性能品HG16-38, 高性能品HG16-37, 高性能品HG16-36,
    #           高性能品HG20-38, 高性能品HG20-37, 高性能品HG20-36, 高性能品HG20-35, 高性能品HG20-34,
    #           高性能品HG24-36, 高性能品HG24-35, 高性能品HG24-34, 高性能品HG24-33,
    #           高性能品HG28-35, 高性能品HG28-34, 高性能品HG28-33,
    #           高性能品HG32-35, 高性能品HG32-34, 高性能品HG32-33,
    #           高性能品HG36-34, 高性能品HG36-33, 高性能品HG36-32, 高性能品HG36-31,
    #           高性能品HG38-34, 高性能品HG38-33, 高性能品HG38-32, 高性能品HG38-31,
    #           高性能品HG40-34, 高性能品HG40-33, 高性能品HG40-32, 高性能品HG48-33, 高性能品HG48-32, 高性能品HG48-31
    gw_dict = {'GW10_50': 0.05, 'GW10_49': 0.049, 'GW10_48': 0.048, 'GW12_45': 0.045, 'GW12_44': 0.044,
               'GW16_45': 0.045, 'GW16_44': 0.044, 'GW20_42': 0.042, 'GW20_41': 0.041, 'GW20_40': 0.04,
               'GW24_38': 0.038, 'GW32_36': 0.036, 'GW40_36': 0.036, 'GW48_35': 0.035, 'GW64_35': 0.035, 'GW80_33': 0.033, 'GW96_33': 0.033,
               'HGW10_47': 0.047, 'HGW10_46': 0.046, 'HGW10_45': 0.045, 'HGW10_44': 0.044, 'HGW10_43': 0.043,
               'HGW12_43': 0.043, 'HGW12_42': 0.042, 'HGW12_41': 0.041, 'HGW14_38': 0.038, 'HGW14_37': 0.037,
               'HGW16_38': 0.038, 'HGW16_37': 0.037, 'HGW16_36': 0.036,
               'HGW20_38': 0.038, 'HGW20_37': 0.037, 'HGW20_36': 0.036, 'HGW20_35': 0.035, 'HGW20_34': 0.034,
               'HGW24_36': 0.036, 'HGW24_35': 0.035, 'HGW24_34': 0.034, 'HGW24_33': 0.033,
               'HGW28_35': 0.035, 'HGW28_34': 0.034, 'HGW28_33': 0.033,
               'HGW32_35': 0.035, 'HGW32_34': 0.034, 'HGW32_33': 0.033,
               'HGW36_34': 0.034, 'HGW36_33': 0.033, 'HGW36_32': 0.032, 'HGW36_31': 0.031,
               'HGW38_34': 0.034, 'HGW38_33': 0.033, 'HGW38_32': 0.032, 'HGW38_31': 0.031,
               'HGW40_34': 0.034, 'HGW40_33': 0.033, 'HGW40_32': 0.032, 'HGW48_33': 0.033, 'HGW48_32': 0.032, 'HGW48_31': 0.031}
    material_dict.update(gw_dict)

    # ロックウール断熱材：LA, LB, LC, LD,
    #           MA, MB, MC,
    #           HA, HB, HC,
    rock_wool_dict = {'RockWoolLA': 0.045, 'RockWoolLB': 0.043, 'RockWoolLC': 0.041, 'RockWoolLD': 0.039,
                      'RockWoolMA': 0.038, 'RockWoolMB': 0.037, 'RockWoolMC': 0.036,
                      'RockWoolHA': 0.036, 'RockWoolHB': 0.035, 'RockWoolHC': 0.034}
    material_dict.update(rock_wool_dict)

    # インシュレーションファイバー断熱材ファイバーマット
    material_dict.update({'InsulationFiberMat': 0.040})

    # インシュレーションファイバー断熱材ファイバーボード
    material_dict.update({'InsulationFiberBoard': 0.052})

    # ビーズ法ポリスチレンフォーム断熱材：1号, 2号, 3号, 4号
    eps_dict = {'EPS1': 0.034, 'EPS2': 0.036, 'EPS3': 0.038, 'EPS4': 0.041}
    material_dict.update(eps_dict)

    # 押出法ポリスチレンフォーム断熱材：1種bA, 1種bB, 1種bC, 2種bA, 2種bB, 2種bC,
    #           3種aA, 3種aB, 3種aC, 3種aD,
    #           3種bA, 3種bB, 3種bC, 3種bD
    xps_dict = {'XPS1bA': 0.04, 'XPS1bB': 0.038, 'XPS1bC': 0.036, 'XPS2bA': 0.034, 'XPS2bB': 0.032, 'XPS2bC': 0.03,
                'XPS3aA': 0.028, 'XPS3aB': 0.026, 'XPS3aC': 0.024, 'XPS3aD': 0.022,
                'XPS3bA': 0.028, 'XPS3bB': 0.026, 'XPS3bC': 0.024, 'XPS3bD': 0.022}
    material_dict.update(xps_dict)

    # 硬質ウレタンフォーム断熱材：1種, 2種1号,
    #           2種2号, 2種3号, 2種4号
    puf_dict = {'PUF1': 0.029, 'PUF2_1': 0.023,
                'PUF2_2': 0.024, 'PUF2_3': 0.027, 'PUF2_4': 0.028}
    material_dict.update(puf_dict)

    # 吹付け硬質ウレタンフォーム：A種1,
    #           A種1H, A種3
    spuf_dict = {'SprayedPUFA1': 0.034,
                 'SprayedPUFA1H': 0.026, 'SprayedPUFA3': 0.04}
    material_dict.update(spuf_dict)

    # ポリエチレンフォーム断熱材：1種1号, 1種2号,
    #           2種, 3種
    polyethylene_dict = {'PolyethyleneFoam1_1': 0.042, 'PolyethyleneFoam1_2': 0.042,
                         'PolyethyleneFoam2': 0.038, 'PolyethyleneFoam3': 0.034}
    material_dict.update(polyethylene_dict)

    # フェノールフォーム断熱材：1種1号AⅠAⅡ, 1種1号BⅠBⅡ, 1種1号CⅠCⅡ, 1種1号DⅠDⅡ, 1種1号EⅠEⅡ,
    #           1種2号AⅠAⅡ, 1種2号BⅠBⅡ, 1種2号CⅠCⅡ, 1種2号DⅠDⅡ, 1種2号EⅠEⅡ,
    #           1種3号AⅠAⅡ, 1種3号BⅠBⅡ, 1種3号CⅠCⅡ, 1種3号DⅠDⅡ, 1種3号EⅠEⅡ,
    #           2種1号AⅠAⅡ, 2種2号AⅠAⅡ, 2種3号AⅠAⅡ, 3種1号AⅠAⅡ
    phenolic_dict = {'PhenolicFoam11_A1_A2': 0.022, 'PhenolicFoam11_B1_B2': 0.021, 'PhenolicFoam11_C1_C2': 0.02, 'PhenolicFoam11_D1_D2': 0.019, 'PhenolicFoam11_E1_E2': 0.018,
                     'PhenolicFoam12_A1_A2': 0.022, 'PhenolicFoam12_B1_B2': 0.021, 'PhenolicFoam12_C1_C2': 0.02, 'PhenolicFoam12_D1_D2': 0.019, 'PhenolicFoam12_E1_E2': 0.018,
                     'PhenolicFoam13_A1_A2': 0.022, 'PhenolicFoam13_B1_B2': 0.021, 'PhenolicFoam13_C1_C2': 0.02, 'PhenolicFoam13_D1_D2': 0.019, 'PhenolicFoam13_E1_E2': 0.018,
                     'PhenolicFoam21_A1_A2': 0.036, 'PhenolicFoam22_A1_A2': 0.034, 'PhenolicFoam23_A1_A2': 0.028, 'PhenolicFoam31_A1_A2': 0.035}
    material_dict.update(phenolic_dict)

    try:
        return material_dict[material]
    except KeyError:
        raise ValueError(material)


def calc_R_si_R_se(part, Outside):
    """表3.1と3.2から表面熱伝達抵抗を求める

    Args:
      part(str): Roof'(屋根)または'Ceiling'(天井)または'ExternalWall'(外壁)または'Floor'(床)または
    'BoundaryWall'(界壁)または'BoundaryCeiling'(上階側界床)または'BoundaryFloor'(下階側界床)
      Outside(str): 室外側は外気かどうか
    'Yes'または'No'

    Returns:
      tuple: 熱的境界内側の表面熱伝達抵抗（m2K/W）, 熱的境界外側の表面熱伝達抵抗（m2K/W）

    """

    if part == 'Roof' or part == 'Ceiling' or part == 'ExternalWall' or part == 'Floor':
        return get_table_3_1(part, Outside)
    elif part == 'BoundaryWall' or part == 'BoundaryCeiling' or part == 'BoundaryFloor':
        return get_table_3_2(part)
    else:
        raise ValueError(part)


def get_table_3_1(part, Outside):
    """表3.1 表面熱伝達抵抗

    Args:
      part(str): Roof'(屋根)または'Ceiling'(天井)または'ExternalWall'(外壁)または'Floor'(床)
      Outside(str): 室外側は外気かどうか
    'Yes'または'No'

    Returns:
      tuple: 熱的境界内側（室内側）の表面熱伝達抵抗（m2K/W）, 熱的境界外側（外気側）の表面熱伝達抵抗（m2K/W）

    """

    # 熱的境界内側  屋根　天井
    #               外壁　床
    R_si_dict = {'Roof': 0.09, 'Ceiling': 0.09,
                 'ExternalWall': 0.11, 'Floor': 0.15}

    # 熱的境界外側  屋根　天井
    #               外壁　床
    R_se_dict = {'Roof': {'Yes': 0.04, 'No': 0.09}, 'Ceiling': {'Yes': 0.00, 'No': 0.09},  # 天井が外気に直接接することはない？表中の'-'とは
                 'ExternalWall': {'Yes': 0.04, 'No': 0.11}, 'Floor': {'Yes': 0.04, 'No': 0.15}}

    try:
        R_si = R_si_dict[part]
        R_se_out = R_se_dict[part]
        try:
            R_se = R_se_out[Outside]
            return R_si, R_se
        except KeyError:
            raise ValueError(Outside)
    except KeyError:
        raise ValueError(part)


def get_table_3_2(part):
    """表3.2 表面熱伝達抵抗（界壁・界床の場合）

    Args:
      part(str): BoundaryWall'(界壁)または'BoundaryCeiling'(上階側界床)または'BoundaryFloor'(下階側界床)

    Returns:
      tuple: 対象住戸の室内側表面熱伝達抵抗（m2K/W）, 隣接住戸の室内側表面熱伝達抵抗（m2K/W）

    """

    # 熱的境界外側＝隣接住戸の室内側表面熱伝達抵抗・熱的境界内側＝対象住戸の室内側表面熱伝達抵抗？？？

    # 対象住戸の室内側表面熱伝達抵抗
    #           界壁
    #           上階側界床 下階側界床
    R_si_dict = {'BoundaryWall': 0.11,
                 'BoundaryCeiling': 0.09, 'BoundaryFloor': 0.15}

    # 隣接住戸の室内側表面熱伝達抵抗
    #           界壁
    #           上階側界床 下階側界床
    R_se_dict = {'BoundaryWall': 0.11,
                 'BoundaryCeiling': 0.09, 'BoundaryFloor': 0.15}

    try:
        return R_si_dict[part], R_se_dict[part]
    except KeyError:
        raise ValueError(part)


def get_table_4(air_type):
    """表4 外皮の内側にある空気層の熱抵抗

    Args:
      air_type(str): 空気層の種類
    'AirTight'(面材で密閉された空気層)または'OnSiteNonConnected'(他の空間と連通していない空気層)または
    'OnSiteConnected'(他の空間と連通している空気層)

    Returns:
      float: 外皮の内側にある空気層の熱抵抗

    """

    R_dict = {'AirTight': 0.09, 'OnSiteNonConnected': 0, 'OnSiteConnected': 0}

    try:
        return R_dict[air_type]
    except KeyError:
        raise ValueError(air_type)
