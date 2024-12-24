from typing import Literal, TypedDict, Any

T_Direction = Literal["Top","N", "NE", "E", "SE","S","SW", "W", "NW", "Bottom" ]
"""方位"""


T_Adjacent = Literal["Outside","Open","Connected","Close","Separator","SeparatorZero"]
"""隣接空間の種類"""

T_StructureType = Literal["Wood","RC","Steel"]
"""構造の種別"""

class HeatBridgeData(TypedDict, total=False):
    """ calc に渡される熱橋データ
    """
    Name : str #名前 任意
    StructureType : T_StructureType #構造の種別 必須 
    Adjacent : T_Adjacent #隣接空間の種類 必須
    Direction: str #方位 AdjacentがOutsideの場合に必須 'N,W'のような文字列
    Length : float #長さ 必須
    ExteriorThermalResistance : float # 熱抵抗 StructureTypeがWood,RCのとき必須
    LinearThermalTransmittance : float #線熱還流率 鉄骨造以外の場合に入力

    Type : Any #部位 StructureTypeがSteelのとき必須
    ColumnInterval : Any #柱見付寸法[鉄骨造] Type=Columnの場合は必須。
    BeamInterval : Any #梁見付寸法[鉄骨造] Type=Beamの場合は必須。
    
    GammaH : float #日よけ効果係数（段房期）Adjacent=Outsideの場合は必須
    GammaC: float #日よけ効果係数（冷房機）Adjacent=Outsideの場合は必須
    SolarAbsorptance : float # 外気側表面の日射吸収率 



class EnvelopeData(TypedDict):
    """ converterが出力し、calc に渡される辞書
    """
    Version : str
    Name : str
    Region : str
    Description : str
    Wall : list[Any]
    Window : list[Any]
    Door : list[Any]
    LinearHeatBridge : list[HeatBridgeData]
    Foundation : list[Any]
    