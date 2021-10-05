# ============================================================================
# 付録B 
# ============================================================================

def calc_U_bySpec(SashFrameDoorSpec,GlassSpec):
	"""表3または8から熱貫流率を求める

    Args:
      SashFrameDoorSpec(str): 建具の仕様
      GlassSpec(str): ガラスの仕様

    Returns:
      float: 熱貫流率 W/m2K

    """

	try:
		return get_table_3(SashFrameDoorSpec,GlassSpec)
	except KeyError:
		return get_table_8(SashFrameDoorSpec,GlassSpec)


def get_table_3(SashSpec,GlassSpec):
    """表3 窓の熱貫流率

    Args:
      SashSpec(str): 建具の仕様
      GlassSpec(str): ガラスの仕様

    Returns:
      float: 熱貫流率 W/m2K

    """

    # 木製建具又は樹脂製建具
    WoodenOrResin_dict = {
                        '3PairDoubleLowEG7': 1.60, #2枚以上のガラス表面にLow-E膜を使用したLow-E三層複層ガラス・されている・7mm以上
                        '3PairLowEG6':1.70, #Low-E三層複層ガラス・されている・6mm以上
                        '3PairLowEA9':1.70, #Low-E三層複層ガラス・されていない・9mm以上
                        '2PairLowEG12':1.90, #Low-E複層ガラス・されている・12mm以上
                        '2PairLowEG0812':2.33, #Low-E複層ガラス・されている・8mm以上12mm未満
                        '2PairLowEG0408':2.91, #Low-E複層ガラス・されている・4mm以上8mm未満
                        '2PairLowEA10':2.33, #Low-E複層ガラス・されていない・10mm以上
                        '2PairLowEA0510':2.91, #Low-E複層ガラス・されていない・5mm以上10mm未満
                        '2PairClearA10':2.91, #遮熱複層ガラス／複層ガラス・10mm以上
                        '2PairClearA0610':3.49, #遮熱複層ガラス／複層ガラス・6mm以上10mm未満
                        'SingleClear':6.51, #単板ガラス
                        }
    # 木と金属の複合材料製建具又は樹脂と金属の複合材料製建具
    Mix_dict = {
                        '2PairLowEG16':2.15, #Low-E複層ガラス・されている・16mm以上
                        '2PairLowEG0816':2.33, #Low-E複層ガラス・されている・8mm以上
                        '2PairLowEG0408':3.49, #Low-E複層ガラス・されている・4mm以上8mm未満
                        '2PairLowEA10':2.33, #Low-E複層ガラス・されていない・10mm以上
                        '2PairLowEA0510':3.49, #Low-E複層ガラス・されていない・5mm以上10mm未満
                        '2PairClearA10':3.49, #遮熱複層ガラス／複層ガラス・10mm以上
                        '2PairClearA0610':4.07, #遮熱複層ガラス／複層ガラス・6mm以上10mm未満
                        }
    # 金属製熱遮断構造建具
    MetallicInsulated_dict = {
                        '2PairLowEG8':2.91, #Low-E複層ガラス・されている・8mm以上
                        '2PairLowEG0408':3.49, #Low-E複層ガラス・されている・4mm以上8mm未満
                        '2PairLowEA10':2.91, #Low-E複層ガラス・されていない・10mm以上
                        '2PairLowEA0610':3.49, #Low-E複層ガラス・されていない・6mm以上10mm未満
                        '2PairClearA10':3.49, #遮熱複層ガラス／複層ガラス・10mm以上
                        '2PairClearA0610':4.07, #遮熱複層ガラス／複層ガラス・6mm以上10mm未満
                        }
    # 金属製建具
    Metalic_dict = {
                        '2PairLowEG8':3.49, #Low-E複層ガラス・されている・8mm以上
                        '2PairLowEG0408':4.07, #Low-E複層ガラス・されている・4mm以上8mm未満
                        '2PairLowEA10':3.49, #Low-E複層ガラス・されていない・10mm以上
                        '2PairLowEA0510':4.07, #Low-E複層ガラス・されていない・5mm以上10mm未満
                        '2PairClearA10':4.07, #遮熱複層ガラス／複層ガラス・10mm以上
                        '2PairClearA0410':4.65, #遮熱複層ガラス／複層ガラス・4mm以上10mm未満
                        'SingleSingleClearA12':4.07, #単板ガラス2枚を組み合わせたもの・12mm以上
                        'SingleSingleClearA0612': 4.65, #単板ガラス2枚を組み合わせたもの・6mm以上12mm未満
                        'SingleClear':6.51, #単板ガラス
                        }

    U_dict = {
            'WoodenOrResin':WoodenOrResin_dict, 
            'Mix':Mix_dict,
            'MetallicInsulated':MetallicInsulated_dict,
            'Metalic':Metalic_dict,
            }
    
    return U_dict[SashSpec][GlassSpec]



def get_table_8(FrameDoorSpec,GlassSpec):
    """表8 ドアの熱貫流率

    Args:
      FrameDoorSpec(str): 枠と戸の仕様
      GlassSpec(str): ガラスの仕様

    Returns:
      float: 熱貫流率 W/m2K

    """

    # 枠：木製・戸：木製断熱積層構造
    Wooden_WoodenInsulation_dict = {
            '3PairClearA12': 2.33, #三層複層ガラス・12mm以上
            '2PairLowEA10': 2.33, #Low-E複層ガラス・10mm以上
            '2PairLowEA6': 2.91, #Low-E複層ガラス・6mm以上10mm未満
            '2PairClearA10': 2.91, #複層ガラス・10mm以上
            'None': 2.33, #ガラスのないもの
    }

    # 枠：金属製熱遮断構造・戸：金属製高断熱フラッシュ構造
    MetalicInsulation_MetalicHighInsulationFlash_dict = {
            '2PairLowEG12':1.75, #Low-E複層ガラス・されている・12mm以上
            'None': 1.75, #ガラスのないもの
    }
    
    # 枠：金属製熱遮断構造、木と金属との複合材料製又は樹脂と金属との複合材料製・戸：金属製断熱フラッシュ構造
    MetalicInsulationOrMix_MetalicInsulationFlash_dict = {
            '2PairLowEA10': 2.33, #Low-E複層ガラス・10mm以上
            '2PairLowEA6': 2.91, #Low-E複層ガラス・6mm以上10mm未満
            '2PairClearA10': 2.91, #複層ガラス・10mm以上
            'None': 2.33, #ガラスのないもの
    }

    # 枠：金属製熱遮断構造・戸：金属製フラッシュ構造
    MetalicInsulation_MetalicFlash_dict = {
            '2PairLowEA10': 3.49, #Low-E複層ガラス・10mm以上
            '2PairClearA10': 3.49, #複層ガラス・10mm以上
            'None': 3.49, #ガラスのないもの
    }

    # 枠：指定しない・戸：木製
    Unspecified_Wooden_dict = {
            '2PairClearA4': 4.65, #複層ガラス・4mm以上
            'None': 4.65, #ガラスのないもの
    }

    # 枠：指定しない・戸：金属製フラッシュ構造
    Unspecified_MetalicFlash_dict = {
            '2PairClearA4': 4.07, #複層ガラス・4mm以上
            'None': 4.07, #ガラスのないもの
    }

    # 枠：指定しない・戸：金属製ハニカムフラッシュ構造
    Unspecified_MetalicHoneycombFlash_dict = {
            '2PairClearA4': 4.65, #複層ガラス・4mm以上
            'None': 4.65, #ガラスのないもの
    }
   

    U_dict = {
            'Wooden_WoodenInsulation':Wooden_WoodenInsulation_dict, 
            'MetalicInsulation_MetalicHighInsulationFlash':MetalicInsulation_MetalicHighInsulationFlash_dict,
            'MetalicInsulationOrMix_MetalicInsulationFlash':MetalicInsulationOrMix_MetalicInsulationFlash_dict,
            'MetalicInsulation_MetalicFlash':MetalicInsulation_MetalicFlash_dict,
            'Unspecified_Wooden':Unspecified_Wooden_dict,
			'Unspecified_MetalicFlash':Unspecified_MetalicFlash_dict,
			'Unspecified_MetalicHoneycombFlash':Unspecified_MetalicHoneycombFlash_dict
			}
    
    return U_dict[FrameDoorSpec][GlassSpec]