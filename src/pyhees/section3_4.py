# ============================================================================
# 第三章 暖冷房負荷と外皮性能
# 第四節 日射熱取得率
# Ver.12（住宅・住戸の外皮性能の計算プログラム Ver.03～2021.4）
# ============================================================================

# 5 一般部位
import pyhees.section3_4_common as common

# 6 大部分がガラスで構成されている窓等の開口部
import pyhees.section3_4_window as window

# 7 大部分がガラスで構成されていないドア等の開口部
import pyhees.section3_4_door as door

# 9 熱橋
import pyhees.section3_4_heatbridge as heatbridge

# 10 土間床等の外周部
import pyhees.section3_4_earthfloor as earthfloor


# 付録A 一般部位及び大部分がガラスで構成されていないドア等の開口部における日除けの効果係数
import pyhees.section3_4_a as gamma

# 付録B 大部分がガラスで構成されている窓等の開口部における取得日射熱補正係数
import pyhees.section3_4_b as f

# 付録C 大部分がガラスで構成される窓等の開口部の垂直面日射熱取得率
import pyhees.section3_4_c as eater_d

