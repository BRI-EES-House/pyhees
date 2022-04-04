# ============================================================================
# 第三章 暖冷房負荷と外皮性能
# 第三節 熱貫流率及び線熱貫流率
# Ver.17（住宅・住戸の外皮性能の計算プログラム Ver.3.0.0～）
# ============================================================================

## 外皮の詳細計算
### 1 概要
"""
主に、
3章2節8.1 外皮平均熱貫流率(section3_2_8.py>calc_U_A)……①
3章2節8.2 暖房期の平均日射熱取得率(section3_2_8.py>calc_eta_A_H)……②
3章2節8.3 冷房期の外皮平均熱貫流率(section3_2_8.py>calc_eta_A_C)……③
を求めたい。
部位ごとの熱貫流率・熱橋の線熱貫流率の値(①の計算に必要)は3章3節、
日射熱取得率の値(②③の計算に必要)は3章4節を参照して計算する。
"""
### 2 入力
"""
入力XML(共有：XML定義表20200901.XLSM参照)から辞書を作成し、①～③の計算を行う関数に引数として渡す。
辞書作成の基本方針は、
A. XMLの属性は、ノード名をKey、値をValueとして辞書に入れる
B. XMLの子要素は、ノード名をKey、子要素をA・Bのルールに則って辞書にしたものをValueとして辞書にいれる。
   同じノード名の子要素が 繰り返される場合、同様に辞書化したもののリストをValueとする。
とする。
従って、辞書は下記の 4データ構造 に示す階層構造を持つ。
"""
#### 2.1 XML→辞書変換例
""" 
XML
<Envelope>
    <Region>○○</Region>
    <Wall Name="部位1" Area="○○" ... >
        <GeneralPart Type="○○" Area="○○" ... >
            <SolidLayer Thickness="○○" ... />
            <SolidLayer Thickness="○○" ... />
            <AirLayer Type="○○" ... />
        </GeneralPart>
        <GeneralPart ... >
        </GeneralPart>
    </Wall>
    <Wall Name="部位2" Area="○○" ...>
        <GeneralPart Type="○○" Area="○○" ... >
            ...
        </GeneralPart>
        ...
    </Wall>
</Envelope>
　
　↓↓↓

Python
{
'Region':○○,   ← 属性のノード名をKey、値をValueとする
'Wall':[   ← 子要素のノード名をKeyとする・繰り返しがあるためValueはリスト
    {
    'Name':'部位1', 'Area':○○, ... ,
    'GeneralPart':[
        {
        'Type':'○○',
        'Area':'○○',
        'SolidLayer':[
            {'Thickness':'○○', ... },
            {'Thickness':'○○', ... }
            ],
        'AirLayer':[
            {'Type':'○○', ... }
            ],
        },
        { 
        ...
        }
        ]  ← GeneralPart終わり
    ...
    },  ← 部位1終わり
    {
    'Name':'部位2','Area':○○, ... ,
    'GeneralPart':[ { ... } ],
    ...
    }
    ]  ← Wall終わり
}
"""
#### 2.2 繰り返しのある要素について
"""
繰り返しのある要素(部分や層)の要素数上限は暫定で設定した。
部分に含まれる層のリストは先頭要素を一番外側(外気側)とみなしている。
"""
#### 2.3 未入力項目の扱いについて
"""
本プログラムでは基本的に、未入力項目はKey/Valueペアがないとみなす。(⇒XML定義表中の全ての項目が辞書のKeyになっている必要はない。)
一部、未入力はValueがNoneになるという前提で処理する(section3_3_5.py>calc_R_i_k_l等)例外もあり。
"""
### 3 出力
"""
①～③の計算を行う関数は、入力XMLを辞書化したものに計算結果を付加したものを返す。
計算結果の階層構造内での位置は下記の 4データ構造 に示す。

例
{
'Region':○○,
'Wall':[ 
    { 'Name':'部位1', 'Area':○○, ... , }
    ] 
}

↓↓ 計算後 ↓↓

{
'Region':○○,
'Wall':[ 
    { 'Name':'部位1', 'Area':○○, ... , 
      'GeneralPart_output':[...], ← 付加された計算結果
      'U_i': ○○, ← 付加された計算結果
    }
    ] 
}
"""
#### 3.1 出力する計算結果
"""
仕様が決まっていないため、旧バージョンのXML定義表に載っていたものを参考に暫定的に設定した。
部位ごとの熱貫流率・線熱貫流率の他、窓を除く外皮等の熱貫流率の計算では、部分や層ごとの熱貫流率や熱抵抗の計算結果も含めた。
想定外の計算結果(途中でエラー、計算対象外など)は空欄や'ERROR'・'NaN'など現時点では統一できていない。
"""
### 4 データ構造     #### XML定義表20200901より作成 ####
"""
''で囲われていないもの(Envelope/Wall_direct/Wall_accurate等)は
辞書の形式(必要最小限のkey・valueペアの集合に名前を付けたもの・情報の整理が目的)を表す。
実際に動作させる際は、XML定義表中の全ての要素が含まれる入力データを関数に渡す。
"""
#### 4.1 辞書のKey名について
"""
XML定義表のノード名由来のもの(Name,Window,GammaC等)は大文字始まり、
プログラム中での処理の都合で追加したもの(part_Name,layer_name等)は小文字始まりとしている。
"""
######## 全体 ########
"""
Envelope---Envelope要素のノード名をkey、値をvalueとして持つ辞書
|
|--'Name': 建物名称
|       
|--'Description': 所在地
|
|--'Version': バージョン
|
|--'Region': 地域区分
|
|--'Wall': 窓を除く外皮等のリスト
|           形式: Wall_direct Wall_accurate Wall_simple Wall_rc Wall_steel 
|
|--'Window': 窓のリスト
|          
|--'Door': ドアのリスト
|
|--'Foundation': 基礎等のリスト
|
|--'LinearHeatBridge': 熱橋のリスト
                        形式: LinearHeatBridge_wood LinearHeatBridge_rc LinearHeatBridge_steel
"""
## 出力
"""
|--'U_A': 外皮平均熱貫流率
|--'eta_A_H': 暖房期の平均日射熱取得率
|--'eta_A_C': 冷房期の平均日射熱取得率
"""

######## 窓を除く外皮等 ########
###### 木造 ######
#### 直接指定 ####
"""
Wall_direct---Wall要素のノード名をkey、値をvalueとして持つ辞書
|
|--'Name': 名前
|--'Area': 面積
|--'Method': 計算方法 'Direct' 
|--'Adjacent': 隣接空間等の種類別
|       'Open'(外気) または 'Connected'(外気に通じる空間) または 'Close'(外気に通じていない空間又は外気に通じる床裏) または
|       'Separator'(住戸、住戸と同様の熱的環境の空間又は外気に通じていない床裏)
|--'SolarGain': 日射取得率
|       'Yes'(日射熱取得が発生する部位) または 'No'(日射熱取得が発生しない部分)
|--'Direction': 方位
|       'Top'(屋根上面) または 'N'(北) または 'NE'(北東) または 'E'(東) または 'SE'(南東) または 
|       'S'(南) または 'SW'(南西) または 'W'(西) または 'NW'(北西) または 'Bottom'(下面)
|--'GammaH': 暖房期の日除けの効果係数
|--'GammaC': 冷房期の日除けの効果係数
|--'UValue': 熱貫流率
|--'UValueInfo': 熱貫流率の入力根拠
"""
## 出力
"""
|--'U_i': 熱貫流率
"""

#### 詳細計算法 ####
"""
Wall_accurate---Wall要素のノード名をkey、値をvalueとして持つ辞書
|
|--'Name': 名前
|--'Area': 面積
|--'Method': 計算方法 'Accurate' 
|--'Adjacent': 隣接空間等の種類別
|       'Open'(外気) または 'Connected'(外気に通じる空間) または 'Close'(外気に通じていない空間又は外気に通じる床裏) または
|       'Separator'(住戸、住戸と同様の熱的環境の空間又は外気に通じていない床裏)
|--'Direction': 方位
|       'Top'(屋根上面) または 'N'(北) または 'NE'(北東) または 'E'(東) または 'SE'(南東) または 
|       'S'(南) または 'SW'(南西) または 'W'(西) または 'NW'(北西) または 'Bottom'(下面)
|--'SolarGain': 日射取得率
|       'Yes'(日射熱取得が発生する部位) または 'No'(日射熱取得が発生しない部分)
|--'Type': 部位の種類
|       'Roof'(屋根) または 'Ceiling'(天井) または 'ExternalWall'(外壁) または 'Floor'(床) または 
|       'BoundaryWall'(界壁) または 'BoundaryCeiling'(上階側界床) または 'BoundaryFloor'(下階側界床)
|--'Outside': 室外側は外気か？
|       'Yes'(外気) または 'No'(外気以外（通気層、小屋裏、床裏等）)
|--'GammaH': 暖房期の日除けの効果係数
|--'GammaC': 冷房期の日除けの効果係数
|--'GeneralPart': 含まれる一般部分のリスト＝GeneralPart_accurateの形式を持つ辞書のリスト
    |   例：'GeneralPart':[GeneralPart1,GeneralPart2,...,GeneralPart5]
    |
    |
    GeneralPart_accurate---GeneralPart要素のノード名をkey、値をvalueとして持つ辞書
    |
    |--'part_Name':'GeneralPart'
    |--'Area': 面積
    |--'layer': 含まれる層のリスト＝SolidLayer_accurateまたはAirLayer_accurateの形式を持つ辞書のリスト
        |   [layer1,layer2,...]　先頭要素が一番外側(外気側)とする　※変更の可能性あり　
        |
        SolidLayer_accurate---SolidLayer要素のノード名をkey、値をvalueとして持つ辞書
        |
        |--'layer_Name': 'SolidLayer'
        |--'LambdaValue' : 熱伝導率
        |--'Thickness': 厚さ
        |--'Material': 素材名
        |--'MaterialInfo': 熱伝導率の根拠
        |--'ExternalReduction': 外張断熱の熱抵抗の低減
        |       'Yes'(外張断熱で１層張りの下地併用) または 'No'(外張断熱で１層張りの下地併用ではない) 
        |
        |
        AirLayer_accurate--AirLayer要素のノード名をkey、値をvalueとして持つ辞書
        |
        |--'layer_Name': 'AirLayer'
        |--'Type': 空気層の種類
                'AirTight'(面材で密閉された空気層) または 'OnSiteNonConnected'(他の空間と連通していない空気層) または
                'OnSiteConnected'(他の空間と連通している空気層)
"""
## 出力
"""
|
|--'GeneralPart_output': 含まれる一般部分の計算結果リスト＝GeneralPart_accurate_outputの形式を持つ辞書のリスト
|   |   [GeneralPart1,GeneralPart2,...,GeneralPart5]
|   |
|   |
|   GeneralPart_accurate_output--暫定の形式
|   |
|   |--'R1': 層1の熱抵抗
|   |--'R2': 層2の熱抵抗
|   |--'R3': 層3の熱抵抗
|   |--'R5': 層4の熱抵抗
|   |--'R6': 層5の熱抵抗
|   |--'R7': 層6の熱抵抗
|   |--'Rse': 外気側表面熱伝達抵抗
|   |--'Rsi': 室内側表面熱伝達抵抗
|   |--'Ru_n': 部分の熱抵抗の合計
|   |--'Un': 部分の熱貫流率
|   |--'a': 面積比率
|
|--'U_i': 熱貫流率
"""


#### 簡略計算法 ####
"""
Wall_simple---Wall要素のノード名をkey、値をvalueとして持つ辞書
|
|--'Name': 名前
|--'Area': 面積
|--'Method': 計算方法 'Simple' 
|--'Adjacent': 隣接空間等の種類別
|       'Open'(外気) または 'Connected'(外気に通じる空間) または 'Close'(外気に通じていない空間又は外気に通じる床裏) または
|       'Separator'(住戸、住戸と同様の熱的環境の空間又は外気に通じていない床裏)
|--'Direction': 方位
|       'Top'(屋根上面) または 'N'(北) または 'NE'(北東) または 'E'(東) または 'SE'(南東) または 
|       'S'(南) または 'SW'(南西) または 'W'(西) または 'NW'(北西) または 'Bottom'(下面)
|--'SolarGain': 日射取得率
|       'Yes'(日射熱取得が発生する部位) または 'No'(日射熱取得が発生しない部分)
|--'Type': 部位の種類
|       'Roof'(屋根) または 'Ceiling'(天井) または 'ExternalWall'(外壁) または 'Floor'(床) または 
|       'BoundaryWall'(界壁) または 'BoundaryCeiling'(上階側界床) または 'BoundaryFloor'(下階側界床)
|--'ConstructionMethod': 工法の種類
|       'FrameFloorBeam'(軸組構法（床梁工法）) または 
|       'FrameSleeper'(軸組構法（束立大引工法）) または
|       'FrameRigidFloor'(軸組構法（剛床工法）) または
|       'FrameSameLevel'(軸組構法（床梁土台同面工法）) または
|       'FrameWall'(軸組構法（外壁）) または
|       'FrameCeiling'(軸組構法（天井）) または
|       'FrameRoof'(軸組構法（屋根）) または
|       'WallFloor'(枠組構法（床）) または
|       'WallWall'(枠組構法（外壁）) または
|       'WallRoof'(枠組構法（屋根）)
|--'InsulationPlace': 断熱箇所
|       'FloorJoistInterval'(根太間) または 'FloorBeamInterval'(大引間) または
|       'FloorJoistBeamInterval'(根太間＋大引間) または 'PillarInterval'(柱・間柱間) または
|       'StudInterval'(たて枠間) または
|       'RoofBeamInterval'(桁・梁間) または 'RafterInterval'(たるき間)または
|--'Outside': 室外側は外気か？
|       'Yes'(外気) または 'No'(外気以外（通気層、小屋裏、床裏等）)
|--'GammaH': 暖房期の日除けの効果係数
|--'GammaC': 冷房期の日除けの効果係数
|--'GeneralPart': 含まれる一般部分のリスト＝GeneralPart_simpleの形式を持つ辞書のリスト
|   |   例：'GeneralPart':[GeneralPart1] (要素数は1を想定)要素数が2以上の場合でも一番先頭要素のみを計算に使用する
|   |
|   |
|   GeneralPart_simple---GeneralPart要素のノード名をkey、値をvalueとして持つ辞書
|   |
|   |--'part_Name':'GeneralPart'
|   |--'layer': 含まれる層のリスト＝SolidLayer_simpleまたはAirLayer_simpleの形式を持つ辞書のリスト
|       |   [layer1,layer2,...]　先頭要素が一番外側(外気側)とする　※変更の可能性あり　
|       |
|       SolidLayer_simple---SolidLayer要素のノード名をkey、値をvalueとして持つ辞書
|       |
|       |--'layer_Name': 'SolidLayer'
|       |--'LambdaValue' : 熱伝導率
|       |--'Thickness': 厚さ
|       |--'Material': 素材名
|       |--'MaterialInfo': 熱伝導率の根拠
|       |--'ExternalReduction': 外張断熱の熱抵抗の低減
|       |       'Yes'(外張断熱で１層張りの下地併用) または 'No'(外張断熱で１層張りの下地併用ではない) 
|       |
|       |
|       AirLayer_simple--AirLayer要素のノード名をkey、値をvalueとして持つ辞書
|       |
|       |--'layer_Name': 'AirLayer'
|       |--'Type': 空気層の種類
|               'AirTight'(面材で密閉された空気層) または 'OnSiteNonConnected'(他の空間と連通していない空気層) または
|               'OnSiteConnected'(他の空間と連通している空気層)
|
|
|--'MixPart': 含まれる断熱部＋熱橋部のリスト＝MixPart_simpleの形式を持つ辞書のリスト
|   |           ※該当する部分がない場合は空リスト
|   |   例：'MixPart':[]/[MixPart1]/[MixPart1, MixPart2] (要素数は0or1or2を想定)
|   |           要素が3つ以上ある場合は先頭から順に計算に使用する
|   |           要素数は3章3節5.1.1(2)の表3-6における断熱部＋熱橋部の面積比率のとり方で決まる
|   |           例えば、軸組構法の束立大引工法において根太間及び大引間に断熱する場合の床
|   |           (つまり、'Type':'Floor','ConstructionMethod':'FrameSleeper','InsulationPlace':'FloorJoistBeamInterval' の場合)
|   |           の場合、表3-2が参照されるため要素数は2。
|   |       
|   |
|   MixPart_simple--MixPart要素のノード名をkey、値をvalueとして持つ辞書
|   |
|   |--'part_Name':'MixPart'
|   |--'Type': 種類
|   |       'JoistIntervalAndBeam'(根太間断熱材＋大引材等)
|   |       'JoistAndBeamInterval'(根太材＋大引間断熱材)
|   |--'layer': 含まれる層のリスト＝SolidLayer_simpleまたはAirLayer_simpleの形式を持つ辞書のリスト
|       |   [layer1,layer2,...]　先頭要素が一番外側(外気側)とする　※変更の可能性あり　
|       |
|       SolidLayer_simple---SolidLayer要素のノード名をkey、値をvalueとして持つ辞書
|       |
|       |--'layer_Name': 'SolidLayer'
|       |--'LambdaValue' : 熱伝導率
|       |--'Thickness': 厚さ
|       |--'Material': 素材名
|       |--'MaterialInfo': 熱伝導率の根拠
|       |--'ExternalReduction': 外張断熱の熱抵抗の低減
|       |       'Yes'(外張断熱で１層張りの下地併用) または 'No'(外張断熱で１層張りの下地併用ではない) 
|       |
|       |
|       AirLayer_simple--AirLayer要素のノード名をkey、値をvalueとして持つ辞書
|       |
|       |--'layer_Name': 'AirLayer'
|       |--'Type': 空気層の種類
|               'AirTight'(面材で密閉された空気層) または 'OnSiteNonConnected'(他の空間と連通していない空気層) または
|               'OnSiteConnected'(他の空間と連通している空気層) 
|
|
|--'HeatBridge': 含まれる熱橋部分（軸組部分）のリスト＝HeatBridge_simpleの形式を持つ辞書のリスト
    |   例：'HeatBridge':[HeatBridge1] (要素数は1を想定)要素数が2以上の場合でも一番先頭要素のみを計算に使用する
    |
    |
    HeatBridge_simple--HeatBridge要素のノード名をkey、値をvalueとして持つ辞書
    |
    |--'part_Name':'HeatBridge'
    |--'Type': 種類
    |       'Joist-Beam'(根太材＋大引材等)
    |       'Pillar-HeatBridge'(構造部材等＋付加断熱層内熱橋部)
    |       'Lintel-HeatBridge'(まぐさ＋付加断熱層内熱橋部)
    |--'layer': 含まれる層のリスト＝SolidLayer_simpleまたはAirLayer_simpleの形式を持つ辞書のリスト
        |   [layer1,layer2,...]　先頭要素が一番外側(外気側)とする　※変更の可能性あり　
        |
        SolidLayer_simple---SolidLayer要素のノード名をkey、値をvalueとして持つ辞書
        |
        |--'layer_Name': 'SolidLayer'
        |--'LambdaValue' : 熱伝導率
        |--'Thickness': 厚さ
        |--'Material': 素材名
        |--'MaterialInfo': 熱伝導率の根拠
        |--'ExternalReduction': 外張断熱の熱抵抗の低減
        |       'Yes'(外張断熱で１層張りの下地併用) または 'No'(外張断熱で１層張りの下地併用ではない) 
        |
        |
        AirLayer_simple--AirLayer要素のノード名をkey、値をvalueとして持つ辞書
        |
        |--'layer_Name': 'AirLayer'
        |--'Type': 空気層の種類
                'AirTight'(面材で密閉された空気層) または 'OnSiteNonConnected'(他の空間と連通していない空気層) または
                'OnSiteConnected'(他の空間と連通している空気層)  
"""
## 出力
"""
|
|--'Rse': 外気側表面熱伝達抵抗　
|--'Rsi': 室内側表面熱伝達抵抗
|--'GeneralPart_output': 含まれる一般部分の計算結果＝GeneralPart_simple_outputの形式を持つ辞書
|   |
|   |
|   GeneralPart_simple_output--暫定の形式
|   |
|   |--'R1': 層1の熱抵抗
|   |--'R2': 層2の熱抵抗
|   |--'R3': 層3の熱抵抗
|   |--'R4': 層4の熱抵抗 ※層数変更可能性あり
|   |--'Ru_n': 部分の熱抵抗の合計
|   |--'Un': 部分の熱貫流率
|   |--'a': 面積比率
|
|--'MixPart1_output': 含まれる一般部分+熱橋部分1の計算結果＝MixPart_simple_outputの形式を持つ辞書
|   |
|   |
|   MixPart_simple_output--暫定の形式
|   |
|   |--'R1': 層1の熱抵抗
|   |--'R2': 層2の熱抵抗
|   |--'R3': 層3の熱抵抗
|   |--'R4': 層4の熱抵抗 ※層数変更可能性あり
|   |--'Ru_n': 部分の熱抵抗の合計
|   |--'Un': 部分の熱貫流率
|   |--'a': 面積比率
|
|--'MixPart2_output': 含まれる一般部分+熱橋部分2の計算結果＝MixPart_simple_outputの形式を持つ辞書
|   |
|   |
|   MixPart_simple_output--暫定の形式
|   |
|   |--'R1': 層1の熱抵抗
|   |--'R2': 層2の熱抵抗
|   |--'R3': 層3の熱抵抗
|   |--'R4': 層4の熱抵抗 ※層数変更可能性あり
|   |--'Ru_n': 部分の熱抵抗の合計
|   |--'Un': 部分の熱貫流率
|   |--'a': 面積比率
|
|--'HeatBridge_output': 含まれる熱橋部分の計算結果＝HeatBridge_simple_outputの形式を持つ辞書
|   |
|   |
|   HeatBridge_simple_output--暫定の形式
|   |
|   |--'R1': 層1の熱抵抗
|   |--'R2': 層2の熱抵抗
|   |--'R3': 層3の熱抵抗
|   |--'R4': 層4の熱抵抗 ※層数変更可能性あり
|   |--'Ru_n': 部分の熱抵抗の合計
|   |--'Un': 部分の熱貫流率
|   |--'a': 面積比率
|
|--'U_i': 熱貫流率
"""


###### 鉄筋コンクリート造等 ######
"""
Wall_rc---Wall要素のノード名をkey、値をvalueとして持つ辞書
|
|--'Name': 名前
|--'Area': 面積
|--'Method': 計算方法 'RC' 
|--'Adjacent': 隣接空間等の種類別
|       'Open'(外気) または 'Connected'(外気に通じる空間) または 'Close'(外気に通じていない空間又は外気に通じる床裏) または
|       'Separator'(住戸、住戸と同様の熱的環境の空間又は外気に通じていない床裏)
|--'Direction': 方位
|       'Top'(屋根上面) または 'N'(北) または 'NE'(北東) または 'E'(東) または 'SE'(南東) または 
|       'S'(南) または 'SW'(南西) または 'W'(西) または 'NW'(北西) または 'Bottom'(下面)
|--'SolarGain': 日射取得率
|       'Yes'(日射熱取得が発生する部位) または 'No'(日射熱取得が発生しない部分)
|--'Type': 部位の種類
|       'Roof'(屋根) または 'Ceiling'(天井) または 'ExternalWall'(外壁) または 'Floor'(床) または 
|       'BoundaryWall'(界壁) または 'BoundaryCeiling'(上階側界床) または 'BoundaryFloor'(下階側界床)
|--'Outside': 室外側は外気か？
|       'Yes'(外気) または 'No'(外気以外（通気層、小屋裏、床裏等）)
|--'GammaH': 暖房期の日除けの効果係数
|--'GammaC': 冷房期の日除けの効果係数
|--'GeneralPart': 含まれる一般部分のリスト＝GeneralPart_rcの形式を持つ辞書のリスト
    |   例：'GeneralPart':[GeneralPart1] (要素数は1を想定)要素数が2以上の場合でも一番先頭要素のみを計算に使用する
    |
    |
    GeneralPart_rc---一般部分についてのパラメータ名をキー、パラメータの値を値として持つ辞書
    |
    |--'part_Name':'GeneralPart'
    |--'layer': 含まれる層のリスト＝SolidLayer_rcまたはAirLayer_rcの形式を持つ辞書のリスト
        |   [layer1,layer2,...]　先頭要素が一番外側(外気側)とする　※変更の可能性あり　
        |
        SolidLayer_rc---SolidLayer要素のノード名をkey、値をvalueとして持つ辞書
        |
        |--'layer_Name': 'SolidLayer'
        |--'LambdaValue' : 熱伝導率
        |--'Thickness': 厚さ
        |--'Material': 素材名
        |--'MaterialInfo': 熱伝導率の根拠
        |--'ExternalReduction': 'No'(木造以外はデフォルトでNo) 
        |
        |
        AirLayer_rc--空気層についてのパラメータ名をキー、パラメータの値を値として持つ辞書
        |
        |--'layer_Name': 'AirLayer'
        |--'Type': 空気層の種類
                'AirTight'(面材で密閉された空気層) または 'OnSiteNonConnected'(他の空間と連通していない空気層) または
                'OnSiteConnected'(他の空間と連通している空気層)
"""
## 出力
"""
|
|--'GeneralPart_output': 含まれる一般部分の計算結果＝GeneralPart_rc_outputの形式を持つ辞書
|   |
|   |
|   GeneralPart_rc_output--暫定の形式
|   |
|   |--'R1': 層1の熱抵抗
|   |--'R2': 層2の熱抵抗
|   |--'R3': 層3の熱抵抗
|   |--'R5': 層4の熱抵抗
|   |--'R6': 層5の熱抵抗
|   |--'R7': 層6の熱抵抗
|   |--'Rse': 外気側表面熱伝達抵抗
|   |--'Rsi': 室内側表面熱伝達抵抗
|   |--'R_u': 一般部の熱抵抗の合計
|   |--'U_g_i': 一般部の熱貫流率
|
|--'U_i': 熱貫流率 ※一般部の熱貫流率と同じ？
"""


###### 鉄骨造 ######
"""
Wall_steel---Wall要素のノード名をkey、値をvalueとして持つ辞書
|
|--'Name': 名前
|--'Area': 面積
|--'Method': 計算方法 'Steel' 
|--'Adjacent': 隣接空間等の種類別
|       'Open'(外気) または 'Connected'(外気に通じる空間) または 'Close'(外気に通じていない空間又は外気に通じる床裏) または
|       'Separator'(住戸、住戸と同様の熱的環境の空間又は外気に通じていない床裏)
|--'Direction': 方位
|       'Top'(屋根上面) または 'N'(北) または 'NE'(北東) または 'E'(東) または 'SE'(南東) または 
|       'S'(南) または 'SW'(南西) または 'W'(西) または 'NW'(北西) または 'Bottom'(下面)
|--'SolarGain': 日射取得率
|       'Yes'(日射熱取得が発生する部位) または 'No'(日射熱取得が発生しない部分)
|--'Type': 部位の種類
|       'Roof'(屋根) または 'Ceiling'(天井) または 'ExternalWall'(外壁) または 'Floor'(床) または 
|       'BoundaryWall'(界壁) または 'BoundaryCeiling'(上階側界床) または 'BoundaryFloor'(下階側界床)
|--'Outside': 室外側は外気か？
|       'Yes'(外気) または 'No'(外気以外（通気層、小屋裏、床裏等）)
|--'ExteriorThermalResistance': 外装材＋断熱補強材の熱抵抗
|       'Over1.7'(1.7以上) または 'Under1.7'(1.7未満1.5以上) または 
|       'Under1.5'(1.5未満1.3以上) または 'Under1.3'(1.3未満1.1以上) または 
|       'Under1.1'(1.1未満0.9以上) または 'Under0.9'(0.9未満0.7以上) または 
|       'Under0.7'(0.7未満0.5以上) または 'Under0.5'(0.5未満0.3以上) または 
|       'Under0.3'(0.3未満0.1以上) または 'Under0.1'(0.1未満)
|--'GammaH': 暖房期の日除けの効果係数
|--'GammaC': 冷房期の日除けの効果係数
|--'GeneralPart': 含まれる一般部分のリスト＝GeneralPart_steelの形式を持つ辞書のリスト
    |   例：'GeneralPart':[GeneralPart1] (要素数は1を想定)要素数が2以上の場合でも一番先頭要素のみを計算に使用する
    |
    |
    GeneralPart_steel---一般部分についてのパラメータ名をキー、パラメータの値を値として持つ辞書
    |
    |--'part_Name':'GeneralPart'
    |--'layer': 含まれる層のリスト＝SolidLayer_steelまたはAirLayer_steelの形式を持つ辞書のリスト
        |   [layer1,layer2,...]　先頭要素が一番外側(外気側)とする　※変更の可能性あり　
        |
        SolidLayer_steel---SolidLayer要素のノード名をkey、値をvalueとして持つ辞書
        |
        |--'layer_Name': 'SolidLayer'
        |--'LambdaValue' : 熱伝導率
        |--'Thickness': 厚さ
        |--'Material': 素材名
        |--'MaterialInfo': 熱伝導率の根拠
        |--'ExternalReduction': 'No'(木造以外はデフォルトでNo) 
        |
        |
        AirLayer_steel--空気層についてのパラメータ名をキー、パラメータの値を値として持つ辞書
        |
        |--'layer_Name': 'AirLayer'
        |--'Type': 空気層の種類
                'AirTight'(面材で密閉された空気層) または 'OnSiteNonConnected'(他の空間と連通していない空気層) または
                'OnSiteConnected'(他の空間と連通している空気層)
"""
## 出力
"""
|
|--'GeneralPart_output': 含まれる一般部分の計算結果＝GeneralPart_steel_outputの形式を持つ辞書
|   |
|   |
|   GeneralPart_steel_output--暫定の形式
|   |
|   |--'R1': 層1の熱抵抗
|   |--'R2': 層2の熱抵抗
|   |--'R3': 層3の熱抵抗
|   |--'R5': 層4の熱抵抗
|   |--'R6': 層5の熱抵抗
|   |--'R7': 層6の熱抵抗
|   |--'Rse': 外気側表面熱伝達抵抗
|   |--'Rsi': 室内側表面熱伝達抵抗
|   |--'R_u': 一般部の熱抵抗の合計
|   |--'U_g_i': 一般部の熱貫流率 
|   |--'U_r_s': 補正熱貫流率
|
|--'U_i': 熱貫流率
"""


###### 土間床等の外周部 ######
"""
Foundation---Foundation要素のノード名をkey、値をvalueとして持つ辞書
|
|--'Name': 名前
|--'Area': 土間床等の面積
|--'OuterLength': 外周の長さ
|--'PsiF': 線熱貫流率
|--'Adjacent': 隣接空間等の種類別
|       'Open'(外気) または 'Connected'(外気に通じる空間) または 'Close'(外気に通じていない空間又は外気に通じる床裏) または
|       'Separator'(住戸、住戸と同様の熱的環境の空間又は外気に通じていない床裏)
"""
## 出力
"""
|
|--'U_F': 線熱貫流率
"""


###### 窓 ######
"""
Window---Window要素のノード名をkey、値をvalueとして持つ辞書
|
|--'Method': 'Window' ※内部処理のため追加
|--'Name': 名前
|--'Direction': 方位
|       'Top'(屋根上面) または 'N'(北) または 'NE'(北東) または 'E'(東) または 'SE'(南東) または 
|       'S'(南) または 'SW'(南西) または 'W'(西) または 'NW'(北西) または 'Bottom'(下面)
|--'SolarGain': 日射取得率
|       'Yes'(日射熱取得が発生する部位) または 'No'(日射熱取得が発生しない部分)
|--'Adjacent': 隣接空間等の種類別
|       'Open'(外気) または 'Connected'(外気に通じる空間) または 'Close'(外気に通じていない空間又は外気に通じる床裏) または
|       'Separator'(住戸、住戸と同様の熱的環境の空間又は外気に通じていない床裏)
|--'WindowPart': 窓部分(WindowPart形式をもつ辞書)
    |
    |
    WindowPart---窓部分についてのパラメータ名をキー、パラメータの値を値として持つ辞書
    |
    |--'IsSetWindow': 二重窓の入力
    |       'Yes'(二重窓の入力あり) または 'No'(二重窓の入力なし)
    |--'Area': 面積
    |--'OuterHeatTransferOpeningArea': 二重窓における外気側窓の伝熱開口面積
    |--'InternalHeatTransferOpeningArea': 二重窓における室内側窓の伝熱開口面積
    |--'HasShade': 日除けの有無
    |       'Yes'(あり) または 'No'(なし)
    |--'SashSpec': 建具仕様
    |       'WoodenOrResin'(木製建具又は樹脂製建具) または 'Mix'(木と金属の複合材料製建具又は樹脂と金属の複合材料製建具) または 
    |       'MetallicInsulated'(金属製熱遮断構造建具) または 'Metalic'(金属製建具) 
    |--'SashSpecForInnerWindow': 建具仕様(内窓)
    |       'WoodenOrResin'(木製建具又は樹脂製建具) または 'Mix'(木と金属の複合材料製建具又は樹脂と金属の複合材料製建具) または 
    |       'MetallicInsulated'(金属製熱遮断構造建具) または 'Metalic'(金属製建具) 
    |--'GlassSpecForCategory': ガラス仕様（区分）
    |       'Single'(単層) または '2Pair'(二層複層) または '3Pair'(三層以上の複層)
    |--'Attachment': 付属品部材
    |       'No'(なし) または 'Shutter'(シャッター) または 'Shoji'(障子) または 'WindbreakSpace'(風除室) または 'ExteriorBlind'(外付けブラインド)     
    |--'UValue': 熱貫流率
    |--'UValueInfo': 熱貫流率の入力根拠
    |--'UValueForInnerWindow': 熱貫流率（内窓）
    |--'UValueInfoForInnerWindow': 熱貫流率の入力根拠（内窓）
    |--'SolarHeatGainCoefficient': ガラスの垂直面日射熱取得率
    |--'SolarHeatGainCoefficientInfo': ガラスの垂直面日射熱取得率の入力根拠
    |--'GlassType': ガラス仕様の区分
    |       '3PairDoubleLowEG'(2枚以上のガラス表面にLow-E膜を使用したLow-E三層複層ガラス　日射取得型) または
    |       '3PairDoubleLowES'(2枚以上のガラス表面にLow-E膜を使用したLow-E三層複層ガラス　日射遮蔽型) または
    |       '3PairLowEG'(Low-E三層複層ガラス　日射取得型) または
    |       '3PairLowES'(Low-E三層複層ガラス　日射遮蔽型) または
    |       '3PairClear'(三層複層ガラス) または
    |       '2PairLowEG'(Low-E二層複層ガラス　日射取得型) または
    |       '2PairLowES'(Low-E二層複層ガラス　日射遮蔽型) または
    |       '2PairClear'(二層複層ガラス) または
    |       '2PairSingleClear'(単板ガラス2枚を組み合わせたもの) または
    |       'SingleClear'(単板ガラス) 
    |--'SolarHeatGainCoefficientForInnerWindow': ガラスの垂直面日射熱取得率（内窓）
    |--'SolarHeatGainCoefficientInfoForInnerWindow': ガラスの垂直面日射熱取得率の入力根拠（内窓）
    |--'GlassTypeForInnerWindow': ガラス仕様の区分（内窓）
    |       '3PairDoubleLowEG'(2枚以上のガラス表面にLow-E膜を使用したLow-E三層複層ガラス　日射取得型) または
    |       '3PairDoubleLowES'(2枚以上のガラス表面にLow-E膜を使用したLow-E三層複層ガラス　日射遮蔽型) または
    |       '3PairLowEG'(Low-E三層複層ガラス　日射取得型) または
    |       '3PairLowES'(Low-E三層複層ガラス　日射遮蔽型) または
    |       '3PairClear'(三層複層ガラス) または
    |       '2PairLowEG'(Low-E二層複層ガラス　日射取得型) または
    |       '2PairLowES'(Low-E二層複層ガラス　日射遮蔽型) または
    |       '2PairClear'(二層複層ガラス) または
    |       '2PairSingleClear'(単板ガラス2枚を組み合わせたもの) または
    |       'SingleClear'(単板ガラス) 
    |--'FcMethod': 窓の日射熱取得の計算方法
    |       'No'(計算しない) または 'Simple'(簡易法) または 'Accurate'(詳細法)
    |--'FrameRef': 枠の影響の有無
    |       'Yes'(枠の影響がある場合) または 'No'(枠の影響がない場合)
    |--'WindowTopToEaveHeight': 日除け下端から窓上端までの垂直方向の距離
    |--'WindowHeigt': 窓の開口高さ寸法
    |--'EaveDepth': 窓面からの日除けの張り出し寸法
    |--'GammaH': 暖房期の日除けの効果係数
    |--'GammaC': 冷房期の日除けの効果係数
"""
## 出力
"""
|--'U_i': 熱貫流率
"""


###### ドア ######
"""
Door---Door要素のノード名をkey、値をvalueとして持つ辞書
|
|--'Method': 'Door' ※内部処理のため追加
|--'Name': 名前
|--'Direction': 方位
|       'Top'(屋根上面) または 'N'(北) または 'NE'(北東) または 'E'(東) または 'SE'(南東) または 
|       'S'(南) または 'SW'(南西) または 'W'(西) または 'NW'(北西) または 'Bottom'(下面)
|--'SolarGain': 日射取得率
|       'Yes'(日射熱取得が発生する部位) または 'No'(日射熱取得が発生しない部分)
|--'Adjacent': 隣接空間等の種類別
|       'Open'(外気) または 'Connected'(外気に通じる空間) または 'Close'(外気に通じていない空間又は外気に通じる床裏) または
|       'Separator'(住戸、住戸と同様の熱的環境の空間又は外気に通じていない床裏)
|--'DoorPart': ドア部分(DoorPart形式をもつ辞書)
    |
    |
    DoorPart---ドア部分についてのパラメータ名をキー、パラメータの値を値として持つ辞書
    |
    |--'Area': 面積
    |--'HasShade': 日除けの有無
    |       'Yes'(あり) または 'No'(なし)
    |--'GammaH': 暖房期の日除けの効果係数
    |--'GammaC': 冷房期の日除けの効果係数
    |--'UValue': 熱貫流率
    |--'UValueInfo': 熱貫流率の入力根拠
    |--'Attachment': 付属品部材
            'No'(なし) または 'Shutter'(シャッター) または 'Shoji'(障子) または 'WindbreakSpace'(風除室)
"""
## 出力
"""
|--'U_i': 熱貫流率
"""


######## 熱橋 ########
###### 木造 ######
"""
LinearHeatBridge_wood--LinearHeatBridge要素のノード名をkey、値をvalueとして持つ辞書
|
|--'part_Name':'LinearHeatBridge'
|--'SolarGain': 日射取得率
|       'Yes'(有) または 'No'(無)
|--'StructureType': 構造の種別 'Wood'
|--'ComponentNames': 接する部位の名前のリスト
|--'Length':長さ
|--'LinearThermalTransmittance':線熱貫流率
|--'GammaH': 暖房期の日除けの効果係数
|--'GammaC': 冷房期の日除けの効果係数
"""
## 出力
"""
|--'Psi': 線熱貫流率
"""

###### 鉄筋コンクリート造等 ######
"""
LinearHeatBridge_rc--LinearHeatBridge要素のノード名をkey、値をvalueとして持つ辞書
|
|--'part_Name':'LinearHeatBridge'
|--'SolarGain': 日射取得率
|       'Yes'(有) または 'No'(無)
|--'StructureType': 構造の種別 'RC'
|--'ComponentNames': 接する部位の名前のリスト
|--'Length':長さ
|--'LinearThermalTransmittance':線熱貫流率　※付録Cの表を見て入力する
|--'GammaH': 暖房期の日除けの効果係数
|--'GammaC': 冷房期の日除けの効果係数
"""
## 出力
"""
|--'Psi': 線熱貫流率
"""


###### 鉄骨造 ######
"""
LinearHeatBridge_steel--LinearHeatBridge要素のノード名をkey、値をvalueとして持つ辞書
|
|--'part_Name':'LinearHeatBridge'
|--'SolarGain': 日射取得率
|       'Yes'(有) または 'No'(無)
|--'StructureType': 構造の種別 'Steel'
|--'ComponentNames': 接する部位の名前(配列)
|--'Length':長さ
|--'ExteriorThermalResistance': 外装材＋断熱補強材の熱抵抗
|       'Over1.7'(1.7以上) または 'Under1.7'(1.7未満1.5以上) または 
|       'Under1.5'(1.5未満1.3以上) または 'Under1.3'(1.3未満1.1以上) または 
|       'Under1.1'(1.1未満0.9以上) または 'Under0.9'(0.9未満0.7以上) または 
|       'Under0.7'(0.7未満0.5以上) または 'Under0.5'(0.5未満0.3以上) または 
|       'Under0.3'(0.3未満0.1以上) または 'Under0.1'(0.1未満)
|--'Type':部位
|       'Column'(柱) または 'Beam'(梁)
|--'ColumnInterval': 柱見付寸法
|       'Over300'(300以上) または 'Under300'(300未満200以上) または
|       'Under200'(200未満100以上) または 'Under100'(100未満)
|--'BeamInterval': 梁見付寸法
|       'Over400'(400以上) または 'Under400'(400未満200以上) または 'Under200'(200未満)
|--'GammaH': 暖房期の日除けの効果係数
|--'GammaC': 冷房期の日除けの効果係数
"""
## 出力
"""
|--'Psi': 線熱貫流率
"""
