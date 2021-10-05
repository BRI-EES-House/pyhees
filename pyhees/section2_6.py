# ============================================================================
# 第二章 単位住戸の一次エネルギー消費量
# 第六節 長屋又は共同住宅の一次エネルギー消費量
# Ver.01（エネルギー消費性能計算プログラム（住宅版）Ver.02.08～）
# ============================================================================
import math
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING, ROUND_FLOOR

def get_U_A_total(UA_list, building_floors, N_u):
    """住棟単位外皮平均熱貫流率（W/m2 K）…………式(1)

    Args:
      UA_list(list: list: list(Decimal)): UA_list[f][i]---階層fにおける単位住戸iの外皮平均熱貫流率(W/m2K)
      building_floors(int): 建物の階数（階）…………入力1.2(1)3
      N_u(list(int)): N_u[f]---階層fにおける単位住戸iの総数（-）

    Returns:
      Decimal: 住棟単位外皮平均熱貫流率（W/m2 K）

    """

    UA_sum = sum([sum(UA_list[f][:N_u[f]]) for f in range(1, building_floors+1)])
    N_u_sum = sum(N_u[1:building_floors+1])

    UA_total =  UA_sum / N_u_sum
    # 小数点以下二位未満の端数を切り上げ
    UA_total = Decimal(UA_total).quantize(Decimal('0.01'), rounding=ROUND_CEILING)

    return UA_total


def get_eta_A_C_total(eta_AC_list, building_floors, N_u):
    """住棟単位冷房期平均日射熱取得率 (%) …………式(2)

    Args:
      eta_AC_list(list: list: list(Decimal)): eta_AC_list[f][i]---階層fにおける単位住戸iの冷房期の平均日射熱取得率 (W/m2)/(W/m2) (%)
      building_floors(int): 建物の階数（階）…………入力1.2(1)3
      N_u(list(int)): N_u[f]---階層fにおける単位住戸iの総数（-）

    Returns:
      Decimal: 住棟単位冷房期平均日射熱取得率 (%)

    """

    eta_AC_sum = sum([sum(eta_AC_list[f][:N_u[f]]) for f in range(1, building_floors+1)])
    N_u_sum = sum(N_u[1:building_floors+1])

    etaAC_total = eta_AC_sum / N_u_sum
    # 小数点以下一位未満の端数を切り上げ
    etaAC_total = Decimal(etaAC_total).quantize(Decimal('0.1'), rounding=ROUND_CEILING)

    return etaAC_total


def get_U_A_f_i(q_f_i, A_env_f_i):
    """階層fにおける単位住戸iの外皮平均熱貫流率（W/m2K）…………式(3)

    Args:
      q_f_i(float): 階層fにおける単位住戸iの単位温度差当たりの熱損失量…………式(4)/get_q_f_i
      A_env_f_i(Decimal): 階層fにおける単位住戸iの外皮の部位の面積の合計…………式(7)/get_A_env_f_i

    Returns:
      Decimal: 階層fにおける単位住戸iの外皮平均熱貫流率（W/m2K）

    """

    # Decimalの有効桁数を小数点以下10桁とする
    U_A_f_i = Decimal(q_f_i / float(A_env_f_i)).quantize(Decimal(str(10**(-10))), rounding=ROUND_HALF_UP)

    # 小数点以下二位未満の端数を切り上げ
    U_A_f_i = Decimal(U_A_f_i).quantize(Decimal('0.01'), rounding=ROUND_CEILING)

    return U_A_f_i


def get_q_f_i(A_roof_f_i, A_ceiling_f_i, A_ofloor_f_i, A_ufloor_f_i, A_ifloor_f_i, 
                A_owall_0_f_i, A_owall_90_f_i, A_owall_180_f_i, A_owall_270_f_i, 
                A_iwall_0_f_i, A_iwall_90_f_i, A_iwall_180_f_i, A_iwall_270_f_i, 
                A_window_0_f_i, A_window_90_f_i, A_window_180_f_i, A_window_270_f_i, 
                A_door_0_f_i, A_door_90_f_i, A_door_180_f_i, A_door_270_f_i,
                ceiling_heat_trans_ratio, U_ceiling, owall_heat_trans_ratio, iwall_heat_trans_ratio, window_heat_trans_ratio, U_door, ifloor_heat_trans_ratio, lowermost_floor_heat_trans_ratio, ofloor_heat_trans_ratio,
                H_OS, H_MS, H_IS, H_180, 
                L_HB_roof_owall_top_0_oc_f_i, L_HB_roof_owall_top_90_oc_f_i, L_HB_roof_owall_top_180_oc_f_i, L_HB_roof_owall_top_270_oc_f_i,
                L_HB_roof_owall_top_0_ic_t_f_i, L_HB_roof_owall_top_0_ic_b_f_i, L_HB_roof_iwall_top_90_f_i, L_HB_roof_iwall_top_270_f_i,
                L_dash_HB_roof_iwall_top_90_f_i, L_dash_HB_roof_iwall_top_0_f_i, 
                L_HB_owall_owall_0_90_f_i, L_HB_owall_owall_90_180_f_i, L_HB_owall_owall_180_270_f_i, L_HB_owall_owall_270_0_f_i,
                L_HB_owall_iwall_0_90_f_i, L_HB_owall_iwall_0_270_f_i, L_HB_owall_iwall_180_90_f_i, L_HB_owall_iwall_180_270_f_i,
                L_dash_HB_owall_iwall_0_90_f_i, L_dash_HB_owall_iwall_90_0_f_i, L_dash_HB_owall_iwall_180_90_f_i, L_dash_HB_owall_iwall_270_0_f_i,
                L_HB_owall_ifloor_0_bottom_t_f_i, L_HB_owall_ifloor_0_bottom_b_f_i, L_HB_owall_ifloor_90_bottom_t_f_i, L_HB_owall_ifloor_90_bottom_b_f_i,
                L_HB_owall_ifloor_180_bottom_t_f_i, L_HB_owall_ifloor_180_bottom_b_f_i, L_HB_owall_ifloor_270_bottom_t_f_i, L_HB_owall_ifloor_270_bottom_b_f_i,
                L_HB_owall_ofloor_0_bottom_oc_f_i, L_HB_owall_ofloor_90_bottom_oc_f_i, L_HB_owall_ofloor_180_bottom_oc_f_i, L_HB_owall_ofloor_270_bottom_oc_f_i,
                L_HB_owall_ofloor_0_bottom_ic_t_f_i, L_HB_owall_ofloor_0_bottom_ic_b_f_i, 
                L_HB_owall_ufloor_0_bottom_f_i, L_HB_owall_ufloor_90_bottom_f_i, L_HB_owall_ufloor_180_bottom_f_i, L_HB_owall_ufloor_270_bottom_f_i,
                L_HB_iwall_ofloor_90_bottom_f_i, L_HB_iwall_ufloor_90_bottom_f_i, L_HB_iwall_ufloor_270_bottom_f_i,
                L_dash_HB_iwall_ufloor_90_bottom_f_i, L_dash_HB_iwall_ufloor_0_bottom_f_i, L_HB_iwall_ofloor_270_bottom_f_i, L_dash_HB_iwall_ofloor_90_bottom_f_i, L_dash_HB_iwall_ofloor_0_bottom_f_i,
                roof_owall_oc_psi, roof_owall_ic_psi, roof_iwall_psi, owall_owall_psi, owall_iwall_psi, owall_ifloor_psi, owall_ufloor_psi,
                owall_ofloor_oc_psi, owall_ofloor_ic_psi, iwall_ufloor_psi, iwall_ofloor_psi):
    """階層fにおける単位住戸iの単位温度差当たりの熱損失量…………式(4)

    Args:
      A_roof_f_i(float): 階層fにおける単位住戸iの屋根面積（m2）…………式(8)/get_A_roof_f_i
      A_ceiling_f_i(float): 階層fにおける単位住戸iの上階側界床面積（m2）…………式(9)/get_A_ceiling_f_i
      A_ofloor_f_i(float): 階層fにおける単位住戸iの外気に接する床面積（m2）…………式(16)/get_A_ofloor_f_i
      A_ufloor_f_i(float): 階層fにおける単位住戸iの外気に通じる床裏に接する床面積（m2）…………式(15)/get_A_ufloor_f_i
      A_ifloor_f_i(float): 階層fにおける単位住戸iの界床面積（m2）…………式(14)/get_A_ifloor_f_i
      A_owall_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の外壁面積（m2）…………式(10a)/get_A_owall_0_f_i
      A_owall_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の外壁面積（m2）…………式(10b)/get_A_owall_90_f_i
      A_owall_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の外壁面積（m2）…………式(10c)/get_A_owall_180_f_i
      A_owall_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の外壁面積（m2）…………式(10d)/get_A_owall_270_f_i
      A_iwall_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の界壁面積（m2）…………式(11a)/get_A_iwall_0_f_i
      A_iwall_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の界壁面積（m2）…………式(11b)/get_A_iwall_90_f_i
      A_iwall_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の界壁面積（m2）…………式(11c)/get_A_iwall_180_f_i
      A_iwall_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の界壁面積（m2）…………式(11d)/get_A_iwall_270_f_i
      A_window_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の窓面積（m2）…………式(12a)/get_A_window_0_f_i
      A_window_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の窓面積（m2）…………式(12b)/get_A_window_90_f_i
      A_window_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の窓面積（m2）…………式(12c)/get_A_window_180_f_i
      A_window_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の窓面積（m2）…………式(12d)/get_A_window_270_f_i
      A_door_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の玄関ドアの面積（m2）…………式(13a)/get_A_door_0_f_i
      A_door_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の玄関ドアの面積（m2）…………式(13b)/get_A_door_90_f_i
      A_door_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の玄関ドアの面積（m2）…………式(13c)/get_A_door_180_f_i
      A_door_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の玄関ドアの面積（m2）…………式(13d)/get_A_door_270_f_i
      ceiling_heat_trans_ratio(float): 屋根（又は天井、以下同様）の熱貫流率（W/m2K）………… A.11.1 屋根の熱貫流率
      U_ceiling(float): 上階側界床の熱貫流率（W/m2K）………… A.11.2 上階側界床の熱貫流率
      owall_heat_trans_ratio(float): 外壁の熱貫流率（W/m2K）………… A.11.3 外壁の熱貫流率
      iwall_heat_trans_ratio(float): 界壁の熱貫流率（W/m2K）………… A.11.4 界壁の熱貫流率
      window_heat_trans_ratio(float): 窓の熱貫流率（W/m2K）………… A.11.5 窓の熱貫流率
      U_door(float): 玄関ドアの熱貫流率（W/m2K）………… A.11.6 玄関ドアの熱貫流率
      ifloor_heat_trans_ratio(float): 界床の熱貫流率（W/m2K）………… A.11.7 界床の熱貫流率
      lowermost_floor_heat_trans_ratio(float): 外気に通じる床裏に接する床の熱貫流率（W/m2K）………… A.11.8 外気に通じる床裏に接する床の熱貫流率
      ofloor_heat_trans_ratio(float): 外気に接する床の熱貫流率（W/m2K）………… A.11.9 外気に接する床の熱貫流率
      H_OS(float): 外気の温度差係数（-）………… A.9 外皮の部分及び熱橋の温度差係数
      H_MS(float): 外気に通じる床裏の温度差係数（-）………… A.9 外皮の部分及び熱橋の温度差係数
      H_IS(float): 住戸と同様の熱的環境の空間の温度差係数（-）………… A.9 外皮の部分及び熱橋の温度差係数
      H_180(float): 主開口方位から時計回りに 180°の方向に面した部位の隣接空間の温度差係数（-）………… A.9 外皮の部分及び熱橋の温度差係数
      L_HB_roof_owall_top_0_oc_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19a)/get_L_HB_roof_owall_top_0_oc_f_i
      L_HB_roof_owall_top_90_oc_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19b)/get_L_HB_roof_owall_top_90_oc_f_i
      L_HB_roof_owall_top_180_oc_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに180°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19c)/get_L_HB_roof_owall_top_180_oc_f_i
      L_HB_roof_owall_top_270_oc_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに270°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19d)/get_L_HB_roof_owall_top_270_oc_f_i
      L_HB_roof_owall_top_0_ic_t_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の上部の入隅部による熱橋の長さ（m）…………式(20a)/get_L_HB_roof_owall_top_0_ic_t_f_i
      L_HB_roof_owall_top_0_ic_b_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の下部の入隅部による熱橋の長さ（m）…………式(20b-1,2)get_L_HB_roof_owall_top_0_ic_b_f_i
      L_HB_roof_iwall_top_90_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した界壁による熱橋の長さ（m）…………式(21a-1,2)/get_L_HB_roof_iwall_top_90_f_i
      L_HB_roof_iwall_top_270_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに270°の方向に面した界壁による熱橋の長さ（m）…………式(21b-1,2)/get_L_HB_roof_iwall_top_270_f_i
      L_dash_HB_roof_iwall_top_90_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した室内壁による熱橋の加算長さ（m）…………式(21c)/get_L_dash_HB_roof_iwall_top_90_f_i
      L_dash_HB_roof_iwall_top_0_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した室内壁による熱橋の加算長さ（m）…………式(21d)/get_L_dash_HB_roof_iwall_top_0_f_i
      L_HB_owall_owall_0_90_f_i(float): 階層fにおける単位住戸iの主開口部方位から時計回りに0°及び90°の方位に面した外壁同士の熱橋の長さ（m）…………式(22a)/get_L_HB_owall_owall_0_90_f_i
      L_HB_owall_owall_90_180_f_i(float): 階層fにおける単位住戸iの主開口部方位から時計回りに90°及び180°の方位に面した外壁同士の熱橋の長さ（m）…………式(22b)/get_L_HB_owall_owall_90_180_f_i
      L_HB_owall_owall_180_270_f_i(float): 階層fにおける単位住戸iの主開口部方位から時計回りに180°及び270°の方位に面した外壁同士の熱橋の長さ（m）…………式(22c)/get_L_HB_owall_owall_180_270_f_i
      L_HB_owall_owall_270_0_f_i(float): 階層fにおける単位住戸iの主開口部方位から時計回りに270°及び0°の方位に面した外壁同士の熱橋の長さ（m）…………式(22d)/get_L_HB_owall_owall_270_0_f_i
      L_HB_owall_iwall_0_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と90°の方向に面した界壁による熱橋の長さ（m）…………式(23a-1,2)/get_L_HB_owall_iwall_0_90_f_i
      L_HB_owall_iwall_0_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と270°の方向に面した界壁による熱橋の長さ（m）…………式(23b-1,2)/get_L_HB_owall_iwall_0_270_f_i
      L_HB_owall_iwall_180_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と90°の方向に面した界壁による熱橋の長さ（m）…………式(23c-1,2)/get_L_HB_owall_iwall_180_90_f_i
      L_HB_owall_iwall_180_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と270°の方向に面した界壁による熱橋の長さ（m）…………式(23d-1,2)/get_L_HB_owall_iwall_180_270_f_i
      L_dash_HB_owall_iwall_0_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と90°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23e)/get_L_dash_HB_owall_iwall_0_90_f_i
      L_dash_HB_owall_iwall_90_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と0°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23f)/get_L_dash_HB_owall_iwall_90_0_f_i
      L_dash_HB_owall_iwall_180_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と90°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23g)/get_L_dash_HB_owall_iwall_180_90_f_i
      L_dash_HB_owall_iwall_270_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と0°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23h)/get_L_dash_HB_owall_iwall_270_0_f_i
      L_HB_owall_ifloor_0_bottom_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24a-1,2,3)/get_L_HB_owall_ifloor_0_bottom_t_f_i
      L_HB_owall_ifloor_0_bottom_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24b-1,2)/get_L_HB_owall_ifloor_0_bottom_b_f_i
      L_HB_owall_ifloor_90_bottom_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24c-1,2)/get_L_HB_owall_ifloor_90_bottom_t_f_i
      L_HB_owall_ifloor_90_bottom_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24d-1,2)/get_L_HB_owall_ifloor_90_bottom_b_f_i
      L_HB_owall_ifloor_180_bottom_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24e)/get_L_HB_owall_ifloor_180_bottom_t_f_i
      L_HB_owall_ifloor_180_bottom_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24f)/get_L_HB_owall_ifloor_180_bottom_b_f_i
      L_HB_owall_ifloor_270_bottom_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24g-1,2)/get_L_HB_owall_ifloor_270_bottom_t_f_i
      L_HB_owall_ifloor_270_bottom_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24h-1,2)/get_L_HB_owall_ifloor_270_bottom_b_f_i
      L_HB_owall_ofloor_0_bottom_oc_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26a)/get_L_HB_owall_ofloor_0_bottom_oc_f_i
      L_HB_owall_ofloor_90_bottom_oc_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26b)/get_L_HB_owall_ofloor_90_bottom_oc_f_i
      L_HB_owall_ofloor_180_bottom_oc_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26c)/get_L_HB_owall_ofloor_180_bottom_oc_f_i
      L_HB_owall_ofloor_270_bottom_oc_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26d)/get_L_HB_owall_ofloor_270_bottom_oc_f_i
      L_HB_owall_ofloor_0_bottom_ic_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の上部と外気に接する床の入隅部による熱橋の長さ（m）…………式(27a-1,2)/get_L_HB_owall_ofloor_0_bottom_ic_t_f_i
      L_HB_owall_ofloor_0_bottom_ic_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の下部と外気に接する床の入隅部による熱橋の長さ（m）…………式(27b)/get_L_HB_owall_ofloor_0_bottom_ic_b_f_i
      L_HB_owall_ufloor_0_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25a)/get_L_HB_owall_ufloor_0_bottom_f_i
      L_HB_owall_ufloor_90_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25b-1,2)/get_L_HB_owall_ufloor_90_bottom_f_i
      L_HB_owall_ufloor_180_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25c)/get_L_HB_owall_ufloor_180_bottom_f_i
      L_HB_owall_ufloor_270_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25d-1,2)/get_L_HB_owall_ufloor_270_bottom_f_i
      L_HB_iwall_ofloor_90_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した界壁と外気に接する床による熱橋の長さ（m）…………式(29a-1,2)/get_L_HB_iwall_ofloor_90_bottom_f_i
      L_HB_iwall_ufloor_90_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した界壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(28a-1,2)/get_L_HB_iwall_ufloor_90_bottom_f_i
      L_HB_iwall_ufloor_270_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した界壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(28b-1,2)/get_L_HB_iwall_ufloor_270_bottom_f_i
      L_dash_HB_iwall_ufloor_90_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した室内壁と外気に通じる床裏に接する床による熱橋の加算長さ（m）…………式(28c)/get_L_dash_HB_iwall_ufloor_90_bottom_f_i
      L_dash_HB_iwall_ufloor_0_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した室内壁と外気に通じる床裏に接する床による熱橋の加算長さ（m）…………式(28d)/get_L_dash_HB_iwall_ufloor_0_bottom_f_i
      L_HB_iwall_ofloor_270_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した界壁と外気に接する床による熱橋の長さ（m）…………式(29b-1,2)/get_L_HB_iwall_ofloor_270_bottom_f_i
      L_dash_HB_iwall_ofloor_90_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した室内壁と外気に接する床による熱橋の加算長さ（m）…………式(29c)/get_L_dash_HB_iwall_ofloor_90_bottom_f_i
      L_dash_HB_iwall_ofloor_0_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した室内壁と外気に接する床による熱橋の加算長さ（m）…………式(29d)/get_L_dash_HB_iwall_ofloor_0_bottom_f_i
      roof_owall_oc_psi(float): 屋根と外壁による出隅部の熱橋の線熱貫流率（W/mK）………… A.12.1 屋根と外壁による出隅部の熱橋の線熱貫流率(get_roof_owall_oc_psi)
      roof_owall_ic_psi(float): 屋根と外壁による入隅部の熱橋の線熱貫流率（W/mK）………… A.12.2 屋根と外壁による入隅部の熱橋の線熱貫流率(get_roof_owall_ic_psi)
      roof_iwall_psi(float): 屋根と界壁又は室内壁による熱橋の線熱貫流率（W/mK）………… A.12.3 屋根と界壁又は室内壁による熱橋の線熱貫流率(get_roof_iwall_psi)
      owall_owall_psi(float): 外壁同士による熱橋の線熱貫流率（W/mK）………… A.12.4 外壁同士による熱橋の線熱貫流率(get_owall_owall_psi)
      owall_iwall_psi(float): 外壁と界壁又は室内壁による熱橋の線熱貫流率（W/mK）………… A.12.5 外壁と界壁又は室内壁による熱橋の線熱貫流率(get_owall_iwall_psi)
      owall_ifloor_psi(float): 外壁と界床による熱橋の線熱貫流率（W/mK）………… A.12.6 外壁と界床による熱橋の線熱貫流率(get_owall_ifloor_psi)
      owall_ufloor_psi(float): 外壁と外気に通じる床裏に接する床による熱橋の線熱貫流率（W/mK）………… A.12.7 外壁と外気に通じる床裏に接する床による熱橋の線熱貫流率(get_owall_ufloor_psi)
      owall_ofloor_oc_psi(float): 外壁と外気に接する床による出隅部の熱橋の線熱貫流率（W/mK）………… A.12.8 外壁と外気に接する床の出隅部による熱橋の線熱貫流率(get_owall_ofloor_oc_psi)
      owall_ofloor_ic_psi(float): 外壁と外気に接する床による入隅部の熱橋の線熱貫流率（W/mK）………… A.12.9 外壁と外気に接する床の入隅部による熱橋の線熱貫流率(get_owall_ofloor_ic_psi)
      iwall_ufloor_psi(float): 界壁又は室内壁と外気に通じる床裏に接する床による熱橋の線熱貫流率（W/mK）………… A.12.10 界壁又は室内壁と外気に通じる床裏に接する床による熱橋の線熱貫流率(get_iwall_ufloor_psi)
      iwall_ofloor_psi(float): 界壁又は室内壁と外気に接する床と熱橋の線熱貫流率（W/mK）………… A.12.11 界壁又は室内壁と外気に接する床による熱橋の線熱貫流率(get_iwall_ofloor_psi)

    Returns:
      float: 階層fにおける単位住戸iの単位温度差当たりの熱損失量

    """

    # 右辺第1項/屋根における単位温度差あたりの熱損失量
    q_roof = A_roof_f_i * H_OS * ceiling_heat_trans_ratio
    # 右辺第2項/上階側界床における単位温度差あたりの熱損失量
    q_ceiling = A_ceiling_f_i * H_IS * U_ceiling
    # 右辺第3項/外壁における単位温度差あたりの熱損失量
    q_owall = ((A_owall_0_f_i + A_owall_90_f_i + A_owall_270_f_i) * H_OS + A_owall_180_f_i * H_180) * owall_heat_trans_ratio
    # 右辺第4項/界壁における単位温度差あたりの熱損失量
    q_iwall = (A_iwall_0_f_i + A_iwall_90_f_i + A_iwall_180_f_i + A_iwall_270_f_i) * H_IS * iwall_heat_trans_ratio
    # 右辺第5項/窓における単位温度差あたりの熱損失量
    q_window = ((A_window_0_f_i + A_window_90_f_i + A_window_270_f_i) * H_OS + A_window_180_f_i * H_180) * window_heat_trans_ratio
    # 右辺第6項/玄関ドアにおける単位温度差あたりの熱損失量
    q_door = ((A_door_0_f_i + A_door_90_f_i + A_door_270_f_i) * H_OS + A_door_180_f_i * H_180) * U_door
    # 右辺第7項/界床における単位温度差あたりの熱損失量
    q_ifloor = A_ifloor_f_i * H_IS * ifloor_heat_trans_ratio 
    # 右辺第8項/外気に通じる床裏に接する床における単位温度差あたりの熱損失量
    q_ufloor = A_ufloor_f_i * H_MS * lowermost_floor_heat_trans_ratio
    # 右辺第9項/外気に接する床における単位温度差あたりの熱損失量
    q_ofloor = A_ofloor_f_i * H_OS * ofloor_heat_trans_ratio
    # 右辺第10項/屋根と外壁による出隅部の熱橋における単位温度差あたりの熱損失量
    q_roof_owall_oc = (L_HB_roof_owall_top_0_oc_f_i + L_HB_roof_owall_top_90_oc_f_i + L_HB_roof_owall_top_180_oc_f_i + L_HB_roof_owall_top_270_oc_f_i) * H_OS * roof_owall_oc_psi
    # 右辺第11項/屋根と外壁による入隅部の熱橋における単位温度差あたりの熱損失量
    q_roof_owall_ic = (L_HB_roof_owall_top_0_ic_t_f_i + L_HB_roof_owall_top_0_ic_b_f_i) * H_OS * roof_owall_ic_psi / 2
    # 右辺第12項,13項/屋根と界壁又は室内壁による熱橋における単位温度差あたりの熱損失量
    q_roof_iwall = (L_HB_roof_iwall_top_90_f_i + L_HB_roof_iwall_top_270_f_i) * H_OS * roof_iwall_psi / 2 \
        +(L_dash_HB_roof_iwall_top_90_f_i + L_dash_HB_roof_iwall_top_0_f_i) * H_OS * roof_iwall_psi
    # 右辺第14項/外壁同士による熱橋における単位温度差あたりの熱損失量
    q_owall_owall = ((L_HB_owall_owall_0_90_f_i + L_HB_owall_owall_270_0_f_i) * H_OS \
            + L_HB_owall_owall_90_180_f_i * (H_OS / 2 + H_180 / 2) \
            + L_HB_owall_owall_180_270_f_i * (H_180 / 2 + H_OS / 2)) * owall_owall_psi
    # 右辺第15項,16項/外壁と界壁又は室内壁による熱橋
    q_owall_iwall = ((L_HB_owall_iwall_0_90_f_i + L_HB_owall_iwall_0_270_f_i) * H_OS \
            + (L_HB_owall_iwall_180_90_f_i + L_HB_owall_iwall_180_270_f_i) * H_180) * owall_iwall_psi / 2 \
            + ((L_dash_HB_owall_iwall_0_90_f_i + L_dash_HB_owall_iwall_90_0_f_i + L_dash_HB_owall_iwall_270_0_f_i) * H_OS \
            + L_dash_HB_owall_iwall_180_90_f_i * H_180) * owall_iwall_psi
    # 右辺第17項/外壁と界床による熱橋における単位温度差あたりの熱損失量
    q_owall_ifloor = ((L_HB_owall_ifloor_0_bottom_t_f_i + L_HB_owall_ifloor_0_bottom_b_f_i + L_HB_owall_ifloor_90_bottom_t_f_i \
            + L_HB_owall_ifloor_90_bottom_b_f_i + L_HB_owall_ifloor_270_bottom_t_f_i \
            + L_HB_owall_ifloor_270_bottom_b_f_i) * H_OS \
            +(L_HB_owall_ifloor_180_bottom_t_f_i \
            + L_HB_owall_ifloor_180_bottom_b_f_i) * H_180) * owall_ifloor_psi / 2
    # 右辺第18項/外壁と外気に通じる床裏に接する床による熱橋における単位温度差あたりの熱損失量
    q_owall_ufloor = ((L_HB_owall_ufloor_0_bottom_f_i + L_HB_owall_ufloor_90_bottom_f_i \
            + L_HB_owall_ufloor_270_bottom_f_i) * H_OS \
            + L_HB_owall_ufloor_180_bottom_f_i * H_180) *owall_ufloor_psi
    # 右辺第19項/外壁と外気に接する床の出隅部による熱橋における単位温度差あたりの熱損失量
    q_owall_ofloor_oc = (L_HB_owall_ofloor_0_bottom_oc_f_i + L_HB_owall_ofloor_90_bottom_oc_f_i \
            + L_HB_owall_ofloor_180_bottom_oc_f_i \
            + L_HB_owall_ofloor_270_bottom_oc_f_i) * H_OS * owall_ofloor_oc_psi
    # 右辺第20項/外壁と外気に接する床の入隅部による熱橋における単位温度差あたりの熱損失量
    q_owall_ofloor_ic = (L_HB_owall_ofloor_0_bottom_ic_t_f_i + L_HB_owall_ofloor_0_bottom_ic_b_f_i) * H_OS * owall_ofloor_ic_psi / 2 
    # 右辺第21項,22項/界壁又は室内壁と外気に通じる床裏に接する床による熱橋における単位温度差あたりの熱損失量
    q_iwall_ufloor = (L_HB_iwall_ufloor_90_bottom_f_i + L_HB_iwall_ufloor_270_bottom_f_i) * H_MS * iwall_ufloor_psi / 2 \
            +(L_dash_HB_iwall_ufloor_90_bottom_f_i + L_dash_HB_iwall_ufloor_0_bottom_f_i) * H_MS * iwall_ufloor_psi
    # 右辺第23項,24項/界壁又は室内壁と外気に接する床による熱橋における単位温度差あたりの熱損失量
    q_iwall_ofloor = (L_HB_iwall_ofloor_90_bottom_f_i + L_HB_iwall_ofloor_270_bottom_f_i) * H_OS * iwall_ofloor_psi /2 \
            +(L_dash_HB_iwall_ofloor_90_bottom_f_i + L_dash_HB_iwall_ofloor_0_bottom_f_i) * H_OS * iwall_ofloor_psi

    # テスト用
    q_part_f_i = {
        'q_roof': q_roof,
        'q_ceiling': q_ceiling,
        'q_owall': q_owall,
        'q_iwall': q_iwall,
        'q_window': q_window,
        'q_door': q_door,
        'q_ifloor': q_ifloor,
        'q_ufloor': q_ufloor,
        'q_ofloor': q_ofloor,
        'q_roof_owall_oc': q_roof_owall_oc,
        'q_roof_owall_ic': q_roof_owall_ic,
        'q_roof_iwall': q_roof_iwall,
        'q_owall_owall': q_owall_owall,
        'q_owall_iwall': q_owall_iwall,
        'q_owall_ifloor': q_owall_ifloor,
        'q_owall_ufloor': q_owall_ufloor,
        'q_owall_ofloor_oc': q_owall_ofloor_oc,
        'q_owall_ofloor_ic': q_owall_ofloor_ic,
        'q_iwall_ufloor': q_iwall_ufloor,
        'q_iwall_ofloor': q_iwall_ofloor
        }

    return q_roof + q_ceiling \
        + q_owall \
        + q_iwall \
        + q_window \
        + q_door \
        + q_ifloor + q_ufloor + q_ofloor \
        + q_roof_owall_oc \
        + q_roof_owall_ic \
        + q_roof_iwall \
        + q_owall_owall \
        + q_owall_iwall \
        + q_owall_ifloor \
        + q_owall_ufloor \
        + q_owall_ofloor_oc \
        + q_owall_ofloor_ic \
        + q_iwall_ufloor \
        + q_iwall_ofloor, \
        q_part_f_i


def get_eta_A_H_f_i(m_H_f_i, A_env_f_i):
    """階層fにおける単位住戸iの暖房期の平均日射熱取得率（(W/m)/(W/m2)）(%) …………式(5a)

    Args:
      m_H_f_i(float): 階層fにおける単位住戸iの単位日射強度当たりの暖房期の日射熱取得量（W/(W/m2)）…………式(5b)/get_m_H_f_i
      A_env_f_i(Decimal): 階層fにおける単位住戸iの外皮の部位の面積の合計…………式(7)/get_A_env_f_i

    Returns:
      Decimal: 階層fにおける単位住戸iの暖房期の平均日射熱取得率（(W/m)/(W/m2)）

    """

    # Decimalの有効桁数を小数点以下10桁とする
    eta_A_H_f_i = Decimal((m_H_f_i / float(A_env_f_i)) * 100).quantize(Decimal(str(10**(-10))), rounding=ROUND_HALF_UP)
    # 小数点以下一位未満の端数を切り下げ
    eta_A_H_f_i = eta_A_H_f_i.quantize(Decimal('0.1'), rounding=ROUND_FLOOR)

    return eta_A_H_f_i


def get_m_H_f_i(A_roof_f_i, A_owall_0_f_i, A_owall_90_f_i, A_owall_180_f_i, A_owall_270_f_i, 
                A_window_0_f_i, A_window_90_f_i, A_window_180_f_i, A_window_270_f_i, 
                A_door_0_f_i, A_door_90_f_i, A_door_180_f_i, A_door_270_f_i, A_ofloor_f_i,
                L_HB_roof_owall_top_0_oc_f_i, L_HB_roof_owall_top_90_oc_f_i, L_HB_roof_owall_top_180_oc_f_i, L_HB_roof_owall_top_270_oc_f_i,
                L_HB_roof_owall_top_0_ic_t_f_i, L_HB_roof_owall_top_0_ic_b_f_i, L_HB_roof_iwall_top_90_f_i, L_HB_roof_iwall_top_270_f_i,
                L_dash_HB_roof_iwall_top_90_f_i, L_dash_HB_roof_iwall_top_0_f_i, L_HB_owall_owall_0_90_f_i, L_HB_owall_owall_90_180_f_i, L_HB_owall_owall_180_270_f_i, L_HB_owall_owall_270_0_f_i,
                L_HB_owall_iwall_0_90_f_i, L_HB_owall_iwall_0_270_f_i, L_HB_owall_iwall_180_90_f_i, L_HB_owall_iwall_180_270_f_i,
                L_dash_HB_owall_iwall_0_90_f_i, L_dash_HB_owall_iwall_90_0_f_i, L_dash_HB_owall_iwall_180_90_f_i, L_dash_HB_owall_iwall_270_0_f_i,
                L_HB_owall_ifloor_0_bottom_t_f_i, L_HB_owall_ifloor_0_bottom_b_f_i, L_HB_owall_ifloor_90_bottom_t_f_i, L_HB_owall_ifloor_90_bottom_b_f_i, 
                L_HB_owall_ifloor_180_bottom_t_f_i, L_HB_owall_ifloor_180_bottom_b_f_i, L_HB_owall_ifloor_270_bottom_t_f_i, L_HB_owall_ifloor_270_bottom_b_f_i,
                L_HB_owall_ufloor_0_bottom_f_i, L_HB_owall_ufloor_90_bottom_f_i, L_HB_owall_ufloor_180_bottom_f_i, L_HB_owall_ufloor_270_bottom_f_i,
                L_HB_owall_ofloor_0_bottom_oc_f_i, L_HB_owall_ofloor_90_bottom_oc_f_i, L_HB_owall_ofloor_180_bottom_oc_f_i, L_HB_owall_ofloor_270_bottom_oc_f_i, 
                L_HB_owall_ofloor_0_bottom_ic_t_f_i, L_HB_owall_ofloor_0_bottom_ic_b_f_i, L_HB_iwall_ofloor_90_bottom_f_i, L_HB_iwall_ofloor_270_bottom_f_i,
                L_dash_HB_iwall_ofloor_90_bottom_f_i, L_dash_HB_iwall_ofloor_0_bottom_f_i,
                nu_H_top, nu_H_bottom, nu_H_0, nu_H_90, nu_H_180, nu_H_270,
                eta_H_roof, eta_H_owall, eta_H_window_0, eta_H_window_90, eta_H_window_180, eta_H_window_270, eta_H_door, eta_H_ofloor,
                eta_dash_H_HB_roof_owall_oc, eta_dash_H_HB_roof_owall_ic, eta_dash_H_HB_roof_iwall, eta_dash_H_HB_owall_owall, eta_dash_H_HB_owall_iwall, eta_dash_H_HB_owall_ifloor, eta_dash_H_HB_owall_ufloor, 
                eta_dash_H_HB_owall_ofloor_oc, eta_dash_H_HB_owall_ofloor_ic, eta_dash_H_HB_iwall_ofloor):
    """階層fにおける単位住戸iの単位日射強度当たりの暖房期の日射熱取得量（W/(W/m2)）…………式(5b)

    Args:
      A_roof_f_i(float): 階層fにおける単位住戸iの屋根面積（m2）…………式(8)/get_A_roof_f_i
      A_owall_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の外壁面積（m2）…………式(10a)/get_A_owall_0_f_i
      A_owall_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の外壁面積（m2）…………式(10b)/get_A_owall_90_f_i
      A_owall_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の外壁面積（m2）…………式(10c)/get_A_owall_180_f_i
      A_owall_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の外壁面積（m2）…………式(10d)/get_A_owall_270_f_i
      A_window_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の窓面積（m2）…………式(12a)/get_A_window_0_f_i
      A_window_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の窓面積（m2）…………式(12b)/get_A_window_90_f_i
      A_window_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の窓面積（m2）…………式(12c)/get_A_window_180_f_i
      A_window_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の窓面積（m2）…………式(12d)/get_A_window_270_f_i
      A_door_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の玄関ドアの面積（m2）…………式(13a)/get_A_door_0_f_i
      A_door_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の玄関ドアの面積（m2）…………式(13b)/get_A_door_90_f_i
      A_door_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の玄関ドアの面積（m2）…………式(13c)/get_A_door_180_f_i
      A_door_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の玄関ドアの面積（m2）…………式(13d)/get_A_door_270_f_i
      A_ofloor_f_i(float): 階層fにおける単位住戸iの外気に接する床面積（m2）…………式(16)/get_A_ofloor_f_i
      L_HB_roof_owall_top_0_oc_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19a)/get_L_HB_roof_owall_top_0_oc_f_i
      L_HB_roof_owall_top_90_oc_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19b)/get_L_HB_roof_owall_top_90_oc_f_i
      L_HB_roof_owall_top_180_oc_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに180°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19c)/get_L_HB_roof_owall_top_180_oc_f_i
      L_HB_roof_owall_top_270_oc_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに270°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19d)/get_L_HB_roof_owall_top_270_oc_f_i
      L_HB_roof_owall_top_0_ic_t_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の上部の入隅部による熱橋の長さ（m）…………式(20a)/get_L_HB_roof_owall_top_0_ic_t_f_i
      L_HB_roof_owall_top_0_ic_b_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の下部の入隅部による熱橋の長さ（m）…………式(20b-1,2)get_L_HB_roof_owall_top_0_ic_b_f_i
      L_HB_roof_iwall_top_90_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した界壁による熱橋の長さ（m）…………式(21a-1,2)/get_L_HB_roof_iwall_top_90_f_i
      L_HB_roof_iwall_top_270_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに270°の方向に面した界壁による熱橋の長さ（m）…………式(21b-1,2)/get_L_HB_roof_iwall_top_270_f_i
      L_dash_HB_roof_iwall_top_90_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した室内壁による熱橋の加算長さ（m）…………式(21c)/get_L_dash_HB_roof_iwall_top_90_f_i
      L_dash_HB_roof_iwall_top_0_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した室内壁による熱橋の加算長さ（m）…………式(21d)/get_L_dash_HB_roof_iwall_top_0_f_i
      L_HB_owall_owall_0_90_f_i(float): 階層fにおける単位住戸iの主開口部方位から時計回りに0°及び90°の方位に面した外壁同士の熱橋の長さ（m）…………式(22a)/get_L_HB_owall_owall_0_90_f_i
      L_HB_owall_owall_90_180_f_i(float): 階層fにおける単位住戸iの主開口部方位から時計回りに90°及び180°の方位に面した外壁同士の熱橋の長さ（m）…………式(22b)/get_L_HB_owall_owall_90_180_f_i
      L_HB_owall_owall_180_270_f_i(float): 階層fにおける単位住戸iの主開口部方位から時計回りに180°及び270°の方位に面した外壁同士の熱橋の長さ（m）…………式(22c)/get_L_HB_owall_owall_180_270_f_i
      L_HB_owall_owall_270_0_f_i(float): 階層fにおける単位住戸iの主開口部方位から時計回りに270°及び0°の方位に面した外壁同士の熱橋の長さ（m）…………式(22d)/get_L_HB_owall_owall_270_0_f_i
      L_HB_owall_iwall_0_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と90°の方向に面した界壁による熱橋の長さ（m）…………式(23a-1,2)/get_L_HB_owall_iwall_0_90_f_i
      L_HB_owall_iwall_0_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と270°の方向に面した界壁による熱橋の長さ（m）…………式(23b-1,2)/get_L_HB_owall_iwall_0_270_f_i
      L_HB_owall_iwall_180_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と90°の方向に面した界壁による熱橋の長さ（m）…………式(23c-1,2)/get_L_HB_owall_iwall_180_90_f_i
      L_HB_owall_iwall_180_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と270°の方向に面した界壁による熱橋の長さ（m）…………式(23d-1,2)/get_L_HB_owall_iwall_180_270_f_i
      L_dash_HB_owall_iwall_0_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と90°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23e)/get_L_dash_HB_owall_iwall_0_90_f_i
      L_dash_HB_owall_iwall_90_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と0°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23f)/get_L_dash_HB_owall_iwall_90_0_f_i
      L_dash_HB_owall_iwall_180_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と90°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23g)/get_L_dash_HB_owall_iwall_180_90_f_i
      L_dash_HB_owall_iwall_270_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と0°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23h)/get_L_dash_HB_owall_iwall_270_0_f_i
      L_HB_owall_ifloor_0_bottom_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24a-1,2,3)/get_L_HB_owall_ifloor_0_bottom_t_f_i
      L_HB_owall_ifloor_0_bottom_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24b-1,2)/get_L_HB_owall_ifloor_0_bottom_b_f_i
      L_HB_owall_ifloor_90_bottom_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24c-1,2)/get_L_HB_owall_ifloor_90_bottom_t_f_i
      L_HB_owall_ifloor_90_bottom_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24d-1,2)/get_L_HB_owall_ifloor_90_bottom_b_f_i
      L_HB_owall_ifloor_180_bottom_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24e)/get_L_HB_owall_ifloor_180_bottom_t_f_i
      L_HB_owall_ifloor_180_bottom_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24f)/get_L_HB_owall_ifloor_180_bottom_b_f_i
      L_HB_owall_ifloor_270_bottom_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24g-1,2)/get_L_HB_owall_ifloor_270_bottom_t_f_i
      L_HB_owall_ifloor_270_bottom_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24h-1,2)/get_L_HB_owall_ifloor_270_bottom_b_f_i
      L_HB_owall_ufloor_0_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25a)/get_L_HB_owall_ufloor_0_bottom_f_i
      L_HB_owall_ufloor_90_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25b-1,2)/get_L_HB_owall_ufloor_90_bottom_f_i
      L_HB_owall_ufloor_180_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25c)/get_L_HB_owall_ufloor_180_bottom_f_i
      L_HB_owall_ufloor_270_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25d-1,2)/get_L_HB_owall_ufloor_270_bottom_f_i
      L_HB_owall_ofloor_0_bottom_oc_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26a)/get_L_HB_owall_ofloor_0_bottom_oc_f_i
      L_HB_owall_ofloor_90_bottom_oc_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26b)/get_L_HB_owall_ofloor_90_bottom_oc_f_i
      L_HB_owall_ofloor_180_bottom_oc_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26c)/get_L_HB_owall_ofloor_180_bottom_oc_f_i
      L_HB_owall_ofloor_270_bottom_oc_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26d)/get_L_HB_owall_ofloor_270_bottom_oc_f_i
      L_HB_owall_ofloor_0_bottom_ic_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の上部と外気に接する床の入隅部による熱橋の長さ（m）…………式(27a-1,2)/get_L_HB_owall_ofloor_0_bottom_ic_t_f_i
      L_HB_owall_ofloor_0_bottom_ic_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の下部と外気に接する床の入隅部による熱橋の長さ（m）…………式(27b)/get_L_HB_owall_ofloor_0_bottom_ic_b_f_i
      L_HB_iwall_ofloor_90_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した界壁と外気に接する床による熱橋の長さ（m）…………式(29a-1,2)/get_L_HB_iwall_ofloor_90_bottom_f_i
      L_HB_iwall_ofloor_270_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した界壁と外気に接する床による熱橋の長さ（m）…………式(29b-1,2)/get_L_HB_iwall_ofloor_270_bottom_f_i
      L_dash_HB_iwall_ofloor_90_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した室内壁と外気に接する床による熱橋の加算長さ（m）…………式(29c)/get_L_dash_HB_iwall_ofloor_90_bottom_f_i
      L_dash_HB_iwall_ofloor_0_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した室内壁と外気に接する床による熱橋の加算長さ（m）…………式(29d)/get_L_dash_HB_iwall_ofloor_0_bottom_f_i
      nu_H_top(float): 上面に面した外皮の部位の暖房期の方位係数…………A.10 外皮の部位の方位係数
      nu_H_bottom(float): 下面に面した外皮の部位の暖房期の方位係数…………A.10 外皮の部位の方位係数
      nu_H_0(float): 主開口方位から時計回りに0°の方向に面した外皮の部位の暖房期の方位係数…………A.10 外皮の部位の方位係数
      nu_H_90(float): 主開口方位から時計回りに90°の方向に面した外皮の部位の暖房期の方位係数…………A.10 外皮の部位の方位係数
      nu_H_180(float): 主開口方位から時計回りに180°の方向に面した外皮の部位の暖房期の方位係数…………A.10 外皮の部位の方位係数
      nu_H_270(float): 主開口方位から時計回りに270°の方向に面した外皮の部位の暖房期の方位係数…………A.10 外皮の部位の方位係数
      eta_H_roof(float): 屋根の暖房期の日射熱取得率((W/m2)/(W/m2))…………A.13.1屋根の日射熱取得率
      eta_H_owall(float): 外壁の暖房期の日射熱取得率((W/m2)/(W/m2)) …………A.13.2 外壁の日射熱取得率
      eta_H_window_0(float): 主開口方位から時計回りに0°の方向に面した窓の暖房期の日射熱取得率((W/m2)/(W/m2))…………A.13.3 窓の日射熱取得率 ② 窓の暖房期の日射熱取得率
      eta_H_window_90(float): 主開口方位から時計回りに90°の方向に面した窓の暖房期の日射熱取得率((W/m2)/(W/m2))…………A.13.3 窓の日射熱取得率 ② 窓の暖房期の日射熱取得率
      eta_H_window_180(float): 主開口方位から時計回りに180°の方向に面した窓の暖房期の日射熱取得率((W/m2)/(W/m2))…………A.13.3 窓の日射熱取得率 ② 窓の暖房期の日射熱取得率
      eta_H_window_270(float): 主開口方位から時計回りに270°の方向に面した窓の暖房期の日射熱取得率((W/m2)/(W/m2))…………A.13.3 窓の日射熱取得率 ② 窓の暖房期の日射熱取得率
      eta_H_door(float): ドアの暖房期の日射熱取得率((W/m2)/(W/m2)) …………A.13.4 玄関ドアの日射熱取得率
      eta_H_ofloor(float): 外気に接する床の暖房期の日射熱取得率((W/m2)/(W/m2))…………A.13.5 外気に接する床の日射熱取得率
      eta_dash_H_HB_roof_owall_oc(float): 屋根と外壁の出隅部における熱橋の暖房期の日射熱取得率((W/m)/(W/m2))…………A.13.6 屋根と外壁における出隅部の熱橋の日射熱取得率
      eta_dash_H_HB_roof_owall_ic(float): 屋根と外壁の入隅部における熱橋の暖房期の日射熱取得率((W/m)/(W/m2)) …………A.13.7 屋根と外壁における入隅部の熱橋の日射熱取得率
      eta_dash_H_HB_roof_iwall(float): 屋根と界壁及び室内壁における熱橋の暖房期の日射熱取得率((W/m)/(W/m2)) …………A.13.8 屋根と界壁又は室内壁における熱橋の日射熱取得率
      eta_dash_H_HB_owall_owall(float): 外壁と外壁における熱橋の暖房期の日射熱取得率((W/m)/(W/m2)) …………A.13.9 外壁と外壁における熱橋の日射熱取得率
      eta_dash_H_HB_owall_iwall(float): 外壁と界壁及び室内壁における熱橋の暖房期の日射熱取得率((W/m)/(W/m2))…………A.13.10 外壁と界壁又は室内壁における熱橋の日射熱取得率
      eta_dash_H_HB_owall_ifloor(float): 外壁と界床における熱橋の暖房期の日射熱取得率((W/m)/(W/m2))…………A.13.11 外壁と界床における熱橋の日射熱取得率
      eta_dash_H_HB_owall_ufloor(float): 外壁と外気に通じる床裏に接する床における熱橋の暖房期の日射熱取得率((W/m)/(W/m2))…………A.13.12 外壁と外気に通じる床裏に接する床における熱橋の日射熱取得率
      eta_dash_H_HB_owall_ofloor_oc(float): 外壁と外気に接する床の出隅部における熱橋の暖房期の日射熱取得率((W/m)/(W/m2)) …………A.13.13 外壁と外気に接する床の出隅部における熱橋の日射熱取得率
      eta_dash_H_HB_owall_ofloor_ic(float): 外壁と外気に接する床の入隅部における熱橋の暖房期の日射熱取得率((W/m)/(W/m2))…………A.13.14 外壁と外気に接する床の入隅部における熱橋の日射熱取得率
      eta_dash_H_HB_iwall_ofloor(float): 界壁及び室内壁と外気に接する床における熱橋の暖房期の日射熱取得率((W/m)/(W/m2))…………A.13.15 界壁又は室内壁と外気に接する床における熱橋の日射熱取得率

    Returns:
      float: 階層fにおける単位住戸iの単位日射強度当たりの暖房期の日射熱取得量（W/(W/m2)）

    """

    # 右辺第1項/屋根における暖房期の日射熱取得量
    m_H_roof = A_roof_f_i * nu_H_top * eta_H_roof
    # 右辺第2項/外壁における暖房期の日射熱取得量
    m_H_owall = (A_owall_0_f_i * nu_H_0 + A_owall_90_f_i * nu_H_90 + A_owall_180_f_i * nu_H_180 + A_owall_270_f_i * nu_H_270) \
            * eta_H_owall
    # 右辺第3項~第6項/窓における暖房期の日射熱取得量
    m_H_window = A_window_0_f_i * nu_H_0 * eta_H_window_0 + A_window_90_f_i * nu_H_90 * eta_H_window_90 \
            + A_window_180_f_i * nu_H_180 * eta_H_window_180 + A_window_270_f_i * nu_H_270 * eta_H_window_270
    # 右辺第7項/玄関ドアにおける暖房期の日射熱取得量
    m_H_door = (A_door_0_f_i * nu_H_0 + A_door_90_f_i * nu_H_90 + A_door_180_f_i * nu_H_180 + A_door_270_f_i * nu_H_270) \
            * eta_H_door
    # 右辺第8項/外気に接する床における暖房期の日射熱取得量
    m_H_ofloor = A_ofloor_f_i * nu_H_bottom * eta_H_ofloor
    # 右辺第9項/屋根と外壁による出隅部の熱橋における暖房期の日射熱取得量
    m_H_roof_owall_oc = (L_HB_roof_owall_top_0_oc_f_i * (nu_H_top + nu_H_0) / 2 + L_HB_roof_owall_top_90_oc_f_i * (nu_H_top + nu_H_90) / 2 \
            + L_HB_roof_owall_top_180_oc_f_i * (nu_H_top + nu_H_180) / 2 \
            + L_HB_roof_owall_top_270_oc_f_i * (nu_H_top + nu_H_270) / 2) * eta_dash_H_HB_roof_owall_oc
    # 右辺第10項/屋根と外壁による入隅部の熱橋における暖房期の日射熱取得量
    m_H_roof_owall_ic = (L_HB_roof_owall_top_0_ic_t_f_i * (nu_H_top + nu_H_0) / 2 + L_HB_roof_owall_top_0_ic_b_f_i * (nu_H_top + nu_H_0) / 2) \
            * eta_dash_H_HB_roof_owall_ic / 2
    # 右辺第11項,第12項/屋根と界壁又は室内壁による熱橋における暖房期の日射熱取得量
    m_H_roof_iwall = (L_HB_roof_iwall_top_90_f_i + L_HB_roof_iwall_top_270_f_i) * nu_H_top * eta_dash_H_HB_roof_iwall / 2 \
        + (L_dash_HB_roof_iwall_top_90_f_i + L_dash_HB_roof_iwall_top_0_f_i) * nu_H_top * eta_dash_H_HB_roof_iwall
    # 右辺第13項/外壁同士による熱橋における暖房期の日射熱取得量
    m_H_owall_owall = (L_HB_owall_owall_0_90_f_i * (nu_H_0 + nu_H_90) / 2 + L_HB_owall_owall_270_0_f_i * (nu_H_270 + nu_H_0) / 2\
            + L_HB_owall_owall_90_180_f_i * (nu_H_90 + nu_H_180) / 2 \
            + L_HB_owall_owall_180_270_f_i * (nu_H_180 + nu_H_270) / 2) * eta_dash_H_HB_owall_owall
    # 右辺第14項,第15項/外壁と界壁又は室内壁による熱橋における暖房期の日射熱取得量
    m_H_owall_iwall = ((L_HB_owall_iwall_0_90_f_i + L_HB_owall_iwall_0_270_f_i) * nu_H_0 \
            + (L_HB_owall_iwall_180_90_f_i + L_HB_owall_iwall_180_270_f_i) * nu_H_180) \
            * eta_dash_H_HB_owall_iwall / 2 \
        + (L_dash_HB_owall_iwall_0_90_f_i * nu_H_0 + L_dash_HB_owall_iwall_90_0_f_i * nu_H_90 \
            + L_dash_HB_owall_iwall_180_90_f_i * nu_H_180 + L_dash_HB_owall_iwall_270_0_f_i * nu_H_270) \
            * eta_dash_H_HB_owall_iwall
    # 右辺第16項/外壁と界床による熱橋による熱橋における暖房期の日射熱取得量
    m_H_owall_ifloor = ((L_HB_owall_ifloor_0_bottom_t_f_i + L_HB_owall_ifloor_0_bottom_b_f_i) * nu_H_0 \
            + (L_HB_owall_ifloor_90_bottom_t_f_i + L_HB_owall_ifloor_90_bottom_b_f_i) * nu_H_90 \
            + (L_HB_owall_ifloor_180_bottom_t_f_i + L_HB_owall_ifloor_180_bottom_b_f_i) * nu_H_180 \
            + (L_HB_owall_ifloor_270_bottom_t_f_i + L_HB_owall_ifloor_270_bottom_b_f_i) * nu_H_270) \
            * eta_dash_H_HB_owall_ifloor / 2
    # 右辺第17項/外壁と外気に通じる床裏に接する床による熱橋における暖房期の日射熱取得量 
    m_H_owall_ufloor = (L_HB_owall_ufloor_0_bottom_f_i * nu_H_0 / 2 + L_HB_owall_ufloor_90_bottom_f_i * nu_H_90 / 2 \
            + L_HB_owall_ufloor_180_bottom_f_i * nu_H_180 / 2 + L_HB_owall_ufloor_270_bottom_f_i * nu_H_270 / 2) \
            * eta_dash_H_HB_owall_ufloor
    # 右辺第18項/外壁と外気に接する床の出隅部による熱橋における暖房期の日射熱取得量
    m_H_owall_ofloor_oc = (L_HB_owall_ofloor_0_bottom_oc_f_i * (nu_H_0 + nu_H_bottom) / 2 \
            + L_HB_owall_ofloor_90_bottom_oc_f_i * (nu_H_90 + nu_H_bottom) / 2 \
            + L_HB_owall_ofloor_180_bottom_oc_f_i * (nu_H_180 + nu_H_bottom) / 2 \
            + L_HB_owall_ofloor_270_bottom_oc_f_i * (nu_H_270 + nu_H_bottom) / 2 ) * eta_dash_H_HB_owall_ofloor_oc
    # 右辺第19項/外壁と外気に接する床の入隅部による熱橋における暖房期の日射熱取得量
    m_H_owall_ofloor_ic = (L_HB_owall_ofloor_0_bottom_ic_t_f_i + L_HB_owall_ofloor_0_bottom_ic_b_f_i) * ( nu_H_0 + nu_H_bottom) / 2 \
            * eta_dash_H_HB_owall_ofloor_ic / 2
    # 右辺第20項/界壁又は室内壁と外気に接する床による熱橋における暖房期の日射熱取得量
    m_H_iwall_ofloor = (L_HB_iwall_ofloor_90_bottom_f_i + L_HB_iwall_ofloor_270_bottom_f_i) * nu_H_bottom * eta_dash_H_HB_iwall_ofloor / 2 \
            + (L_dash_HB_iwall_ofloor_90_bottom_f_i + L_dash_HB_iwall_ofloor_0_bottom_f_i) * nu_H_bottom \
            * eta_dash_H_HB_iwall_ofloor
    
    # テスト用
    m_H_part_f_i = {
        'm_H_roof': m_H_roof,
        'm_H_owall': m_H_owall,
        'm_H_window': m_H_window,
        'm_H_door': m_H_door,
        'm_H_ofloor': m_H_ofloor,
        'm_H_roof_owall_oc': m_H_roof_owall_oc,
        'm_H_roof_owall_ic': m_H_roof_owall_ic,
        'm_H_roof_iwall': m_H_roof_iwall,
        'm_H_owall_owall': m_H_owall_owall,
        'm_H_owall_iwall': m_H_owall_iwall,
        'm_H_owall_ifloor': m_H_owall_ifloor,
        'm_H_owall_ufloor': m_H_owall_ufloor,
        'm_H_owall_ofloor_oc': m_H_owall_ofloor_oc,
        'm_H_owall_ofloor_ic': m_H_owall_ofloor_ic,
        'm_H_iwall_ofloor': m_H_iwall_ofloor
    }

    return m_H_roof \
        + m_H_owall \
        + m_H_window \
        + m_H_door \
        + m_H_ofloor \
        + m_H_roof_owall_oc \
        + m_H_roof_owall_ic \
        + m_H_roof_iwall \
        + m_H_owall_owall \
        + m_H_owall_iwall \
        + m_H_owall_ifloor \
        + m_H_owall_ufloor \
        + m_H_owall_ofloor_oc \
        + m_H_owall_ofloor_ic \
        + m_H_iwall_ofloor, \
        m_H_part_f_i


def get_eta_A_C_f_i(m_C_f_i, A_env_f_i):
    """階層fにおける単位住戸iの冷房期の平均日射熱取得率（(W/m)/(W/m2) (%) …………式(6a)

    Args:
      m_C_f_i(float): 階層fにおける単位住戸iの単位日射強度当たりの冷房期の日射熱取得量（W/(W/m2)）…………式(6b)/get_m_C_f_i
      A_env_f_i(Decimal): 階層fにおける単位住戸iの外皮の部位の面積の合計…………式(7)/get_A_env_f_i

    Returns:
      Decimal: 階層fにおける単位住戸iの冷房期の平均日射熱取得率（(W/m)/(W/m2)）

    """

    # Decimalの有効桁数を小数点以下10桁とする
    eta_A_C_f_i = Decimal((m_C_f_i / float(A_env_f_i)) * 100).quantize(Decimal(str(10**(-10))), rounding=ROUND_HALF_UP)
    # 小数点以下一位未満の端数を切り上げ
    eta_A_C_f_i = eta_A_C_f_i.quantize(Decimal('0.1'), rounding=ROUND_CEILING)

    return eta_A_C_f_i


def get_m_C_f_i(A_roof_f_i, A_owall_0_f_i, A_owall_90_f_i, A_owall_180_f_i, A_owall_270_f_i, 
                A_window_0_f_i, A_window_90_f_i, A_window_180_f_i, A_window_270_f_i, 
                A_door_0_f_i, A_door_90_f_i, A_door_180_f_i, A_door_270_f_i, A_ofloor_f_i,
                L_HB_roof_owall_top_0_oc_f_i, L_HB_roof_owall_top_90_oc_f_i, L_HB_roof_owall_top_180_oc_f_i, L_HB_roof_owall_top_270_oc_f_i,
                L_HB_roof_owall_top_0_ic_t_f_i, L_HB_roof_owall_top_0_ic_b_f_i, L_HB_roof_iwall_top_90_f_i, L_HB_roof_iwall_top_270_f_i,
                L_dash_HB_roof_iwall_top_90_f_i, L_dash_HB_roof_iwall_top_0_f_i, L_HB_owall_owall_0_90_f_i, L_HB_owall_owall_90_180_f_i, L_HB_owall_owall_180_270_f_i, L_HB_owall_owall_270_0_f_i,
                L_HB_owall_iwall_0_90_f_i, L_HB_owall_iwall_0_270_f_i, L_HB_owall_iwall_180_90_f_i, L_HB_owall_iwall_180_270_f_i,
                L_dash_HB_owall_iwall_0_90_f_i, L_dash_HB_owall_iwall_90_0_f_i, L_dash_HB_owall_iwall_180_90_f_i, L_dash_HB_owall_iwall_270_0_f_i,
                L_HB_owall_ifloor_0_bottom_t_f_i, L_HB_owall_ifloor_0_bottom_b_f_i, L_HB_owall_ifloor_90_bottom_t_f_i, L_HB_owall_ifloor_90_bottom_b_f_i, 
                L_HB_owall_ifloor_180_bottom_t_f_i, L_HB_owall_ifloor_180_bottom_b_f_i, L_HB_owall_ifloor_270_bottom_t_f_i, L_HB_owall_ifloor_270_bottom_b_f_i,
                L_HB_owall_ufloor_0_bottom_f_i, L_HB_owall_ufloor_90_bottom_f_i, L_HB_owall_ufloor_180_bottom_f_i, L_HB_owall_ufloor_270_bottom_f_i,
                L_HB_owall_ofloor_0_bottom_oc_f_i, L_HB_owall_ofloor_90_bottom_oc_f_i, L_HB_owall_ofloor_180_bottom_oc_f_i, L_HB_owall_ofloor_270_bottom_oc_f_i, 
                L_HB_owall_ofloor_0_bottom_ic_t_f_i, L_HB_owall_ofloor_0_bottom_ic_b_f_i, L_HB_iwall_ofloor_90_bottom_f_i, L_HB_iwall_ofloor_270_bottom_f_i,
                L_dash_HB_iwall_ofloor_90_bottom_f_i, L_dash_HB_iwall_ofloor_0_bottom_f_i,
                nu_C_top, nu_C_bottom, nu_C_0, nu_C_90, nu_C_180, nu_C_270,
                eta_C_roof, eta_C_owall, eta_C_window_0, eta_C_window_90, eta_C_window_180, eta_C_window_270, eta_C_door, eta_C_ofloor,
                eta_dash_C_HB_roof_owall_oc, eta_dash_C_HB_roof_owall_ic, eta_dash_C_HB_roof_iwall, eta_dash_C_HB_owall_owall, eta_dash_C_HB_owall_iwall, eta_dash_C_HB_owall_ifloor, eta_dash_C_HB_owall_ufloor, 
                eta_dash_C_HB_owall_ofloor_oc, eta_dash_C_HB_owall_ofloor_ic, eta_dash_C_HB_iwall_ofloor):
    """階層fにおける単位住戸iの単位日射強度当たりの冷房期の日射熱取得量（W/(W/m2)）…………式(6b)

    Args:
      A_roof_f_i(float): 階層fにおける単位住戸iの屋根面積（m2）…………式(8)/get_A_roof_f_i
      A_owall_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の外壁面積（m2）…………式(10a)/get_A_owall_0_f_i
      A_owall_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の外壁面積（m2）…………式(10b)/get_A_owall_90_f_i
      A_owall_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の外壁面積（m2）…………式(10c)/get_A_owall_180_f_i
      A_owall_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の外壁面積（m2）…………式(10d)/get_A_owall_270_f_i
      A_window_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の窓面積（m2）…………式(12a)/get_A_window_0_f_i
      A_window_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の窓面積（m2）…………式(12b)/get_A_window_90_f_i
      A_window_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の窓面積（m2）…………式(12c)/get_A_window_180_f_i
      A_window_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の窓面積（m2）…………式(12d)/get_A_window_270_f_i
      A_door_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の玄関ドアの面積（m2）…………式(13a)/get_A_door_0_f_i
      A_door_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の玄関ドアの面積（m2）…………式(13b)/get_A_door_90_f_i
      A_door_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の玄関ドアの面積（m2）…………式(13c)/get_A_door_180_f_i
      A_door_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の玄関ドアの面積（m2）…………式(13d)/get_A_door_270_f_i
      A_ofloor_f_i(float): 階層fにおける単位住戸iの外気に接する床面積（m2）…………式(16)/get_A_ofloor_f_i
      L_HB_roof_owall_top_0_oc_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19a)/get_L_HB_roof_owall_top_0_oc_f_i
      L_HB_roof_owall_top_90_oc_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19b)/get_L_HB_roof_owall_top_90_oc_f_i
      L_HB_roof_owall_top_180_oc_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに180°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19c)/get_L_HB_roof_owall_top_180_oc_f_i
      L_HB_roof_owall_top_270_oc_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに270°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19d)/get_L_HB_roof_owall_top_270_oc_f_i
      L_HB_roof_owall_top_0_ic_t_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の上部の入隅部による熱橋の長さ（m）…………式(20a)/get_L_HB_roof_owall_top_0_ic_t_f_i
      L_HB_roof_owall_top_0_ic_b_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の下部の入隅部による熱橋の長さ（m）…………式(20b-1,2)get_L_HB_roof_owall_top_0_ic_b_f_i
      L_HB_roof_iwall_top_90_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した界壁による熱橋の長さ（m）…………式(21a-1,2)/get_L_HB_roof_iwall_top_90_f_i
      L_HB_roof_iwall_top_270_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに270°の方向に面した界壁による熱橋の長さ（m）…………式(21b-1,2)/get_L_HB_roof_iwall_top_270_f_i
      L_dash_HB_roof_iwall_top_90_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した室内壁による熱橋の加算長さ（m）…………式(21c)/get_L_dash_HB_roof_iwall_top_90_f_i
      L_dash_HB_roof_iwall_top_0_f_i(float): 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した室内壁による熱橋の加算長さ（m）…………式(21d)/get_L_dash_HB_roof_iwall_top_0_f_i
      L_HB_owall_owall_0_90_f_i(float): 階層fにおける単位住戸iの主開口部方位から時計回りに0°及び90°の方位に面した外壁同士の熱橋の長さ（m）…………式(22a)/get_L_HB_owall_owall_0_90_f_i
      L_HB_owall_owall_90_180_f_i(float): 階層fにおける単位住戸iの主開口部方位から時計回りに90°及び180°の方位に面した外壁同士の熱橋の長さ（m）…………式(22b)/get_L_HB_owall_owall_90_180_f_i
      L_HB_owall_owall_180_270_f_i(float): 階層fにおける単位住戸iの主開口部方位から時計回りに180°及び270°の方位に面した外壁同士の熱橋の長さ（m）…………式(22c)/get_L_HB_owall_owall_180_270_f_i
      L_HB_owall_owall_270_0_f_i(float): 階層fにおける単位住戸iの主開口部方位から時計回りに270°及び0°の方位に面した外壁同士の熱橋の長さ（m）…………式(22d)/get_L_HB_owall_owall_270_0_f_i
      L_HB_owall_iwall_0_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と90°の方向に面した界壁による熱橋の長さ（m）…………式(23a-1,2)/get_L_HB_owall_iwall_0_90_f_i
      L_HB_owall_iwall_0_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と270°の方向に面した界壁による熱橋の長さ（m）…………式(23b-1,2)/get_L_HB_owall_iwall_0_270_f_i
      L_HB_owall_iwall_180_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と90°の方向に面した界壁による熱橋の長さ（m）…………式(23c-1,2)/get_L_HB_owall_iwall_180_90_f_i
      L_HB_owall_iwall_180_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と270°の方向に面した界壁による熱橋の長さ（m）…………式(23d-1,2)/get_L_HB_owall_iwall_180_270_f_i
      L_dash_HB_owall_iwall_0_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と90°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23e)/get_L_dash_HB_owall_iwall_0_90_f_i
      L_dash_HB_owall_iwall_90_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と0°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23f)/get_L_dash_HB_owall_iwall_90_0_f_i
      L_dash_HB_owall_iwall_180_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と90°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23g)/get_L_dash_HB_owall_iwall_180_90_f_i
      L_dash_HB_owall_iwall_270_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と0°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23h)/get_L_dash_HB_owall_iwall_270_0_f_i
      L_HB_owall_ifloor_0_bottom_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24a-1,2,3)/get_L_HB_owall_ifloor_0_bottom_t_f_i
      L_HB_owall_ifloor_0_bottom_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24b-1,2)/get_L_HB_owall_ifloor_0_bottom_b_f_i
      L_HB_owall_ifloor_90_bottom_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24c-1,2)/get_L_HB_owall_ifloor_90_bottom_t_f_i
      L_HB_owall_ifloor_90_bottom_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24d-1,2)/get_L_HB_owall_ifloor_90_bottom_b_f_i
      L_HB_owall_ifloor_180_bottom_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24e)/get_L_HB_owall_ifloor_180_bottom_t_f_i
      L_HB_owall_ifloor_180_bottom_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24f)/get_L_HB_owall_ifloor_180_bottom_b_f_i
      L_HB_owall_ifloor_270_bottom_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24g-1,2)/get_L_HB_owall_ifloor_270_bottom_t_f_i
      L_HB_owall_ifloor_270_bottom_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24h-1,2)/get_L_HB_owall_ifloor_270_bottom_b_f_i
      L_HB_owall_ufloor_0_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25a)/get_L_HB_owall_ufloor_0_bottom_f_i
      L_HB_owall_ufloor_90_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25b-1,2)/get_L_HB_owall_ufloor_90_bottom_f_i
      L_HB_owall_ufloor_180_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25c)/get_L_HB_owall_ufloor_180_bottom_f_i
      L_HB_owall_ufloor_270_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25d-1,2)/get_L_HB_owall_ufloor_270_bottom_f_i
      L_HB_owall_ofloor_0_bottom_oc_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26a)/get_L_HB_owall_ofloor_0_bottom_oc_f_i
      L_HB_owall_ofloor_90_bottom_oc_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26b)/get_L_HB_owall_ofloor_90_bottom_oc_f_i
      L_HB_owall_ofloor_180_bottom_oc_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26c)/get_L_HB_owall_ofloor_180_bottom_oc_f_i
      L_HB_owall_ofloor_270_bottom_oc_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26d)/get_L_HB_owall_ofloor_270_bottom_oc_f_i
      L_HB_owall_ofloor_0_bottom_ic_t_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の上部と外気に接する床の入隅部による熱橋の長さ（m）…………式(27a-1,2)/get_L_HB_owall_ofloor_0_bottom_ic_t_f_i
      L_HB_owall_ofloor_0_bottom_ic_b_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の下部と外気に接する床の入隅部による熱橋の長さ（m）…………式(27b)/get_L_HB_owall_ofloor_0_bottom_ic_b_f_i
      L_HB_iwall_ofloor_90_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した界壁と外気に接する床による熱橋の長さ（m）…………式(29a-1,2)/get_L_HB_iwall_ofloor_90_bottom_f_i
      L_HB_iwall_ofloor_270_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した界壁と外気に接する床による熱橋の長さ（m）…………式(29b-1,2)/get_L_HB_iwall_ofloor_270_bottom_f_i
      L_dash_HB_iwall_ofloor_90_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した室内壁と外気に接する床による熱橋の加算長さ（m）…………式(29c)/get_L_dash_HB_iwall_ofloor_90_bottom_f_i
      L_dash_HB_iwall_ofloor_0_bottom_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した室内壁と外気に接する床による熱橋の加算長さ（m）…………式(29d)/get_L_dash_HB_iwall_ofloor_0_bottom_f_i
      nu_C_top(float): 上面に面した外皮の部位の冷房期の方位係数…………A.10 外皮の部位の方位係数
      nu_C_bottom(float): 下面に面した外皮の部位の冷房期の方位係数…………A.10 外皮の部位の方位係数
      nu_C_0(float): 主開口方位から時計回りに0°の方向に面した外皮の部位の冷房期の方位係数…………A.10 外皮の部位の方位係数
      nu_C_90(float): 主開口方位から時計回りに90°の方向に面した外皮の部位の冷房期の方位係数…………A.10 外皮の部位の方位係数
      nu_C_180(float): 主開口方位から時計回りに180°の方向に面した外皮の部位の冷房期の方位係数…………A.10 外皮の部位の方位係数
      nu_C_270(float): 主開口方位から時計回りに270°の方向に面した外皮の部位の冷房期の方位係数…………A.10 外皮の部位の方位係数
      eta_C_roof(float): 屋根の冷房期の日射熱取得率((W/m2)/(W/m2))…………A.13.1屋根の日射熱取得率
      eta_C_owall(float): 外壁の冷房期の日射熱取得率((W/m2)/(W/m2)) …………A.13.2 外壁の日射熱取得率
      eta_C_window_0(float): 主開口方位から時計回りに0°の方向に面した窓の冷房期の日射熱取得率((W/m2)/(W/m2))…………A.13.3 窓の日射熱取得率 ② 窓の冷房期の日射熱取得率
      eta_C_window_90(float): 主開口方位から時計回りに90°の方向に面した窓の冷房期の日射熱取得率((W/m2)/(W/m2))…………A.13.3 窓の日射熱取得率 ② 窓の冷房期の日射熱取得率
      eta_C_window_180(float): 主開口方位から時計回りに180°の方向に面した窓の冷房期の日射熱取得率((W/m2)/(W/m2))…………A.13.3 窓の日射熱取得率 ② 窓の冷房期の日射熱取得率
      eta_C_window_270(float): 主開口方位から時計回りに270°の方向に面した窓の冷房期の日射熱取得率((W/m2)/(W/m2))…………A.13.3 窓の日射熱取得率 ② 窓の冷房期の日射熱取得率
      eta_C_door(float): ドアの冷房期の日射熱取得率((W/m2)/(W/m2)) …………A.13.4 玄関ドアの日射熱取得率
      eta_C_ofloor(float): 外気に接する床の冷房期の日射熱取得率((W/m2)/(W/m2))…………A.13.5 外気に接する床の日射熱取得率
      eta_dash_C_HB_roof_owall_oc(float): 屋根と外壁の出隅部における熱橋の冷房期の日射熱取得率((W/m)/(W/m2))…………A.13.6 屋根と外壁における出隅部の熱橋の日射熱取得率
      eta_dash_C_HB_roof_owall_ic(float): 屋根と外壁の入隅部における熱橋の冷房期の日射熱取得率((W/m)/(W/m2)) …………A.13.7 屋根と外壁における入隅部の熱橋の日射熱取得率
      eta_dash_C_HB_roof_iwall(float): 屋根と界壁及び室内壁における熱橋の冷房期の日射熱取得率((W/m)/(W/m2)) …………A.13.8 屋根と界壁又は室内壁における熱橋の日射熱取得率
      eta_dash_C_HB_owall_owall(float): 外壁と外壁における熱橋の冷房期の日射熱取得率((W/m)/(W/m2)) …………A.13.9 外壁と外壁における熱橋の日射熱取得率
      eta_dash_C_HB_owall_iwall(float): 外壁と界壁及び室内壁における熱橋の冷房期の日射熱取得率((W/m)/(W/m2))…………A.13.10 外壁と界壁又は室内壁における熱橋の日射熱取得率
      eta_dash_C_HB_owall_ifloor(float): 外壁と界床における熱橋の冷房期の日射熱取得率((W/m)/(W/m2))…………A.13.11 外壁と界床における熱橋の日射熱取得率
      eta_dash_C_HB_owall_ufloor(float): 外壁と外気に通じる床裏に接する床における熱橋の冷房期の日射熱取得率((W/m)/(W/m2))…………A.13.12 外壁と外気に通じる床裏に接する床における熱橋の日射熱取得率
      eta_dash_C_HB_owall_ofloor_oc(float): 外壁と外気に接する床の出隅部における熱橋の冷房期の日射熱取得率((W/m)/(W/m2)) …………A.13.13 外壁と外気に接する床の出隅部における熱橋の日射熱取得率
      eta_dash_C_HB_owall_ofloor_ic(float): 外壁と外気に接する床の入隅部における熱橋の冷房期の日射熱取得率((W/m)/(W/m2))…………A.13.14 外壁と外気に接する床の入隅部における熱橋の日射熱取得率
      eta_dash_C_HB_iwall_ofloor(float): 界壁及び室内壁と外気に接する床における熱橋の冷房期の日射熱取得率((W/m)/(W/m2))…………A.13.15 界壁又は室内壁と外気に接する床における熱橋の日射熱取得率

    Returns:
      float: 階層fにおける単位住戸iの単位日射強度当たりの冷房期の日射熱取得量（W/(W/m2)）

    """

    # 右辺第1項/屋根における冷房期の日射熱取得量
    m_C_roof = A_roof_f_i * nu_C_top * eta_C_roof
    # 右辺第2項/外壁における冷房期の日射熱取得量
    m_C_owall = (A_owall_0_f_i * nu_C_0 + A_owall_90_f_i * nu_C_90 + A_owall_180_f_i * nu_C_180 + A_owall_270_f_i * nu_C_270) \
            * eta_C_owall
    # 右辺第3項~第6項/窓における冷房期の日射熱取得量
    m_C_window = A_window_0_f_i * nu_C_0 * eta_C_window_0 + A_window_90_f_i * nu_C_90 * eta_C_window_90 \
            + A_window_180_f_i * nu_C_180 * eta_C_window_180 + A_window_270_f_i * nu_C_270 * eta_C_window_270
    # 右辺第7項/玄関ドアにおける冷房期の日射熱取得量
    m_C_door = (A_door_0_f_i * nu_C_0 + A_door_90_f_i * nu_C_90 + A_door_180_f_i * nu_C_180 + A_door_270_f_i * nu_C_270) \
            * eta_C_door
    # 右辺第8項/外気に接する床における冷房期の日射熱取得量
    m_C_ofloor = A_ofloor_f_i * nu_C_bottom * eta_C_ofloor
    # 右辺第9項/屋根と外壁による出隅部の熱橋における冷房期の日射熱取得量
    m_C_roof_owall_oc = (L_HB_roof_owall_top_0_oc_f_i * (nu_C_top + nu_C_0) / 2 + L_HB_roof_owall_top_90_oc_f_i * (nu_C_top + nu_C_90) / 2 \
            + L_HB_roof_owall_top_180_oc_f_i * (nu_C_top + nu_C_180) / 2 \
            + L_HB_roof_owall_top_270_oc_f_i * (nu_C_top + nu_C_270) / 2) * eta_dash_C_HB_roof_owall_oc
    # 右辺第10項/屋根と外壁による入隅部の熱橋における冷房期の日射熱取得量
    m_C_roof_owall_ic = (L_HB_roof_owall_top_0_ic_t_f_i * (nu_C_top + nu_C_0) / 2 + L_HB_roof_owall_top_0_ic_b_f_i * (nu_C_top + nu_C_0) / 2) \
            * eta_dash_C_HB_roof_owall_ic / 2
    # 右辺第11項,第12項/屋根と界壁又は室内壁による熱橋における冷房期の日射熱取得量
    m_C_roof_iwall = (L_HB_roof_iwall_top_90_f_i + L_HB_roof_iwall_top_270_f_i) * nu_C_top * eta_dash_C_HB_roof_iwall / 2 \
        + (L_dash_HB_roof_iwall_top_90_f_i + L_dash_HB_roof_iwall_top_0_f_i) * nu_C_top * eta_dash_C_HB_roof_iwall
    # 右辺第13項/外壁同士による熱橋における冷房期の日射熱取得量
    m_C_owall_owall = (L_HB_owall_owall_0_90_f_i * (nu_C_0 + nu_C_90) / 2 + L_HB_owall_owall_270_0_f_i * (nu_C_270 + nu_C_0) / 2\
            + L_HB_owall_owall_90_180_f_i * (nu_C_90 + nu_C_180) / 2 \
            + L_HB_owall_owall_180_270_f_i * (nu_C_180 + nu_C_270) / 2) * eta_dash_C_HB_owall_owall
    # 右辺第14項,第15項/外壁と界壁又は室内壁による熱橋における冷房期の日射熱取得量
    m_C_owall_iwall = ((L_HB_owall_iwall_0_90_f_i + L_HB_owall_iwall_0_270_f_i) * nu_C_0 \
            + (L_HB_owall_iwall_180_90_f_i + L_HB_owall_iwall_180_270_f_i) * nu_C_180) \
            * eta_dash_C_HB_owall_iwall / 2 \
        + (L_dash_HB_owall_iwall_0_90_f_i * nu_C_0 + L_dash_HB_owall_iwall_90_0_f_i * nu_C_90 \
            + L_dash_HB_owall_iwall_180_90_f_i * nu_C_180 + L_dash_HB_owall_iwall_270_0_f_i * nu_C_270) \
            * eta_dash_C_HB_owall_iwall
    # 右辺第16項/外壁と界床による熱橋による熱橋における冷房期の日射熱取得量
    m_C_owall_ifloor = ((L_HB_owall_ifloor_0_bottom_t_f_i + L_HB_owall_ifloor_0_bottom_b_f_i) * nu_C_0 \
            + (L_HB_owall_ifloor_90_bottom_t_f_i + L_HB_owall_ifloor_90_bottom_b_f_i) * nu_C_90 \
            + (L_HB_owall_ifloor_180_bottom_t_f_i + L_HB_owall_ifloor_180_bottom_b_f_i) * nu_C_180 \
            + (L_HB_owall_ifloor_270_bottom_t_f_i + L_HB_owall_ifloor_270_bottom_b_f_i) * nu_C_270) \
            * eta_dash_C_HB_owall_ifloor / 2
    # 右辺第17項/外壁と外気に通じる床裏に接する床による熱橋における冷房期の日射熱取得量
    m_C_owall_ufloor = (L_HB_owall_ufloor_0_bottom_f_i * nu_C_0 / 2 + L_HB_owall_ufloor_90_bottom_f_i * nu_C_90 / 2 \
            + L_HB_owall_ufloor_180_bottom_f_i * nu_C_180 / 2 + L_HB_owall_ufloor_270_bottom_f_i * nu_C_270 / 2) \
            * eta_dash_C_HB_owall_ufloor
    # 右辺第18項/外壁と外気に接する床の出隅部による熱橋における冷房期の日射熱取得量
    m_C_owall_ofloor_oc = (L_HB_owall_ofloor_0_bottom_oc_f_i * (nu_C_0 + nu_C_bottom) / 2 \
            + L_HB_owall_ofloor_90_bottom_oc_f_i * (nu_C_90 + nu_C_bottom) / 2 \
            + L_HB_owall_ofloor_180_bottom_oc_f_i * (nu_C_180 + nu_C_bottom) / 2 \
            + L_HB_owall_ofloor_270_bottom_oc_f_i * (nu_C_270 + nu_C_bottom) / 2 ) * eta_dash_C_HB_owall_ofloor_oc
    # 右辺第19項/外壁と外気に接する床の入隅部による熱橋における冷房期の日射熱取得量
    m_C_owall_ofloor_ic = (L_HB_owall_ofloor_0_bottom_ic_t_f_i + L_HB_owall_ofloor_0_bottom_ic_b_f_i) * ( nu_C_0 + nu_C_bottom) / 2 \
            * eta_dash_C_HB_owall_ofloor_ic / 2
    # 右辺第20項/界壁又は室内壁と外気に接する床による熱橋における冷房期の日射熱取得量
    m_C_iwall_ofloor = (L_HB_iwall_ofloor_90_bottom_f_i + L_HB_iwall_ofloor_270_bottom_f_i) * nu_C_bottom * eta_dash_C_HB_iwall_ofloor / 2 \
            + (L_dash_HB_iwall_ofloor_90_bottom_f_i + L_dash_HB_iwall_ofloor_0_bottom_f_i) * nu_C_bottom \
            * eta_dash_C_HB_iwall_ofloor

    # テスト用
    m_C_part_f_i = {
        'm_C_roof': m_C_roof,
        'm_C_owall': m_C_owall,
        'm_C_window': m_C_window,
        'm_C_door': m_C_door,
        'm_C_ofloor': m_C_ofloor,
        'm_C_roof_owall_oc': m_C_roof_owall_oc,
        'm_C_roof_owall_ic': m_C_roof_owall_ic,
        'm_C_roof_iwall': m_C_roof_iwall,
        'm_C_owall_owall': m_C_owall_owall,
        'm_C_owall_iwall': m_C_owall_iwall,
        'm_C_owall_ifloor': m_C_owall_ifloor,
        'm_C_owall_ufloor': m_C_owall_ufloor,
        'm_C_owall_ofloor_oc': m_C_owall_ofloor_oc,
        'm_C_owall_ofloor_ic': m_C_owall_ofloor_ic,
        'm_C_iwall_ofloor': m_C_iwall_ofloor,
    }

    return m_C_roof \
        + m_C_owall \
        + m_C_window \
        + m_C_door \
        + m_C_ofloor \
        + m_C_roof_owall_oc \
        + m_C_roof_owall_ic \
        + m_C_roof_iwall \
        + m_C_owall_owall \
        + m_C_owall_iwall \
        + m_C_owall_ifloor \
        + m_C_owall_ufloor \
        + m_C_owall_ofloor_oc \
        + m_C_owall_ofloor_ic \
        + m_C_iwall_ofloor, \
        m_C_part_f_i

    
def get_A_env_f_i(A_roof_f_i, A_ceiling_f_i, A_owall_0_f_i, A_owall_90_f_i, A_owall_180_f_i, A_owall_270_f_i, 
                    A_iwall_0_f_i, A_iwall_90_f_i, A_iwall_180_f_i, A_iwall_270_f_i, 
                    A_window_0_f_i, A_window_90_f_i, A_window_180_f_i, A_window_270_f_i,
                    A_door_0_f_i, A_door_90_f_i, A_door_180_f_i, A_door_270_f_i, A_ifloor_f_i, A_ufloor_f_i, A_ofloor_f_i):
    """階層fにおける単位住戸iの外皮の部位の面積の合計…………式(7)

    Args:
      A_roof_f_i(float): 階層fにおける単位住戸iの屋根面積（m2）…………式(8)/get_A_roof_f_i
      A_ceiling_f_i(float): 階層fにおける単位住戸iの上階側界床面積（m2）…………式(9)/get_A_ceiling_f_i
      A_owall_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の外壁面積（m2）…………式(10a)/get_A_owall_0_f_i
      A_owall_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の外壁面積（m2）…………式(10b)/get_A_owall_90_f_i
      A_owall_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の外壁面積（m2）…………式(10c)/get_A_owall_180_f_i
      A_owall_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の外壁面積（m2）…………式(10d)/get_A_owall_270_f_i
      A_iwall_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の界壁面積（m2）…………式(11a)/get_A_iwall_0_f_i
      A_iwall_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の界壁面積（m2）…………式(11b)/get_A_iwall_90_f_i
      A_iwall_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の界壁面積（m2）…………式(11c)/get_A_iwall_180_f_i
      A_iwall_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の界壁面積（m2）…………式(11d)/get_A_iwall_270_f_i
      A_window_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の窓面積（m2）…………式(12a)/get_A_window_0_f_i
      A_window_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の窓面積（m2）…………式(12b)/get_A_window_90_f_i
      A_window_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の窓面積（m2）…………式(12c)/get_A_window_180_f_i
      A_window_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の窓面積（m2）…………式(12d)/get_A_window_270_f_i
      A_door_0_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の玄関ドアの面積（m2）…………式(13a)/get_A_door_0_f_i
      A_door_90_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の玄関ドアの面積（m2）…………式(13b)/get_A_door_90_f_i
      A_door_180_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の玄関ドアの面積（m2）…………式(13c)/get_A_door_180_f_i
      A_door_270_f_i(float): 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の玄関ドアの面積（m2）…………式(13d)/get_A_door_270_f_i
      A_ifloor_f_i(float): 階層fにおける単位住戸iの界床面積（m2）…………式(14)/get_A_ifloor_f_i
      A_ufloor_f_i(float): 階層fにおける単位住戸iの外気に通じる床裏に接する床面積（m2）…………式(15)/get_A_ufloor_f_i
      A_ofloor_f_i(float): 階層fにおける単位住戸iの外気に接する床面積（m2）…………式(16)/get_A_ofloor_f_i

    Returns:
      Decimal: 階層fにおける単位住戸iの外皮の部位の面積の合計（m2）

    """

    A_env_f_i = A_roof_f_i + A_ceiling_f_i + A_owall_0_f_i + A_owall_90_f_i + A_owall_180_f_i + A_owall_270_f_i + \
        A_iwall_0_f_i + A_iwall_90_f_i + A_iwall_180_f_i + A_iwall_270_f_i + \
        A_window_0_f_i + A_window_90_f_i + A_window_180_f_i + A_window_270_f_i + \
        A_door_0_f_i + A_door_90_f_i + A_door_180_f_i + \
        A_door_270_f_i + A_ifloor_f_i + A_ufloor_f_i + A_ofloor_f_i

    # Decimalの有効桁数を小数点以下10桁とする
    A_env_f_i = Decimal(str(A_env_f_i)).quantize(Decimal(str(10**(-10))), rounding=ROUND_HALF_UP)
    return A_env_f_i.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def get_A_roof_f_i(total_roof_area, dwelling_units):
    """階層fにおける単位住戸iの屋根面積…………式(8)

    Args:
      total_roof_area(float): 階層fにおける単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの屋根面積（m2）

    """

    return total_roof_area / dwelling_units


def get_A_ceiling_f_i(total_floor_area, total_roof_area, f, building_floors, dwelling_units):
    """階層fにおける単位住戸iの上階側界床面積…………式(9)

    Args:
      total_floor_area(float): 階層fにおける単位住戸の床面積の合計（m2）…………入力1.2(2)6
      total_roof_area(float): 階層fにおける単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area
      f(int): 階層（-）
      building_floors(int): 建物の階数（階）…………入力1.2(1)3
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの上階側界床面積（m2）

    """

    if f == building_floors:
        return 0.0
    elif f <= building_floors-1:
        return (total_floor_area - total_roof_area) / dwelling_units
    else:
        raise ValueError("invalid value in f or building_floors")


def get_A_owall_0_f_i(l_frnt_total_f, H_f, A_window_0_total_f, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の外壁面積（m2）…………式(10a)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      A_window_0_total_f(float): 階層fにおける単位住戸の主開口方位から時計回りに0°の方向に面した部位の窓面積の合計（m2）…………式(33a)/get_A_window_0_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の外壁面積

    """

    return (l_frnt_total_f * H_f - A_window_0_total_f) / dwelling_units


def get_A_owall_90_f_i(l_dpth_total_f, H_f, A_window_90_total_f, i):
    """階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の外壁面積（m2）…………式(10b)

    Args:
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      A_window_90_total_f(float): 階層fにおける単位住戸の主開口方位から時計回りに90°の方向に面した部位の窓面積の合計（m2）…………式(33b)/get_A_window_90_total_f
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の外壁面積

    """
    
    if i == 0:
        return l_dpth_total_f * H_f - A_window_90_total_f
    else:
        return 0.0


def get_A_owall_180_f_i(l_frnt_total_f, H_f, A_window_180_total_f, A_door_180_f_i, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の外壁面積（m2）…………式(10c)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      A_window_180_total_f(float): 階層fにおける単位住戸の主開口方位から時計回りに180°の方向に面した部位の窓面積の合計（m2）…………式(33c)/get_A_window_180_total_f
      A_door_180_f_i(float): 階層fにおける単位住戸の主開口方位から時計回りに180°の方向に面した部位の窓面積の合計（m2）…………式(13c)
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の外壁面積

    """

    return (l_frnt_total_f * H_f - A_window_180_total_f) / dwelling_units - A_door_180_f_i


def get_A_owall_270_f_i(l_dpth_total_f, H_f, A_window_270_total_f, i, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の外壁面積（m2）…………式(10d)

    Args:
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      A_window_270_total_f(float): 階層fにおける単位住戸の主開口方位から時計回りに270°の方向に面した部位の窓面積の合計（m2）…………式(33d)/get_A_window_270_total_f
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の外壁面積

    """

    if i == dwelling_units - 1:
        return l_dpth_total_f * H_f - A_window_270_total_f
    else:
        return 0.0


def get_A_iwall_0_f_i():
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した界壁面積（m2）…………式(11a)

    Args:

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した界壁面積

    """

    return 0.0


def get_A_iwall_90_f_i(l_dpth_total_f, H_f, i):
    """階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した界壁面積（m2）…………式(11b)

    Args:
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した界壁面積

    """

    if i == 0:
        return 0.0
    else:
        return l_dpth_total_f * H_f
    
    
def get_A_iwall_180_f_i():
    """階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した界壁面積（m2）…………式(11c)

    Args:

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した界壁面積

    """

    return 0.0


def get_A_iwall_270_f_i(l_dpth_total_f, H_f, i, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した界壁面積（m2）…………式(11d)

    Args:
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した界壁面積

    """

    if i == dwelling_units - 1:
        return 0.0
    else:
        return l_dpth_total_f * H_f


def get_A_window_0_f_i(A_window_0_total_f, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の窓面積…………式(12a)

    Args:
      A_window_0_total_f(float): 階層fにおける単位住戸の主開口方位から時計回りに0°の方向に面した部位の窓面積の合計（m2）…………式(33a)/get_A_window_0_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した部位の窓面積

    """

    return A_window_0_total_f / dwelling_units


def get_A_window_90_f_i(A_window_90_total_f, i):
    """階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の窓面積…………式(12b)

    Args:
      A_window_90_total_f(float): 階層fにおける単位住戸の主開口方位から時計回りに90°の方向に面した部位の窓面積の合計（m2）…………式(33b)/get_A_window_90_total_f
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した部位の窓面積

    """

    if i == 0:
        return A_window_90_total_f
    else:
        return 0.0


def get_A_window_180_f_i(A_window_180_total_f, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の窓面積…………式(12c)

    Args:
      A_window_180_total_f(float): 階層fにおける単位住戸の主開口方位から時計回りに180°の方向に面した部位の窓面積の合計（m2）…………式(33c)/get_A_window_180_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した部位の窓面積

    """

    return A_window_180_total_f / dwelling_units


def get_A_window_270_f_i(A_window_270_total_f, i, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の窓面積…………式(12d)

    Args:
      A_window_270_total_f(float): 階層fにおける単位住戸の主開口方位から時計回りに270°の方向に面した部位の窓面積の合計（m2）…………式(33d)/get_A_window_270_total_f
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した部位の窓面積

    """

    if i == dwelling_units - 1:
        return A_window_270_total_f
    else:
        return 0.0


def get_A_door_0_f_i():
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した玄関ドア面積…………式(13a)

    Args:

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した玄関ドア面積（m2）

    """

    return 0.0


def get_A_door_90_f_i():
    """階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した玄関ドア面積…………式(13b)

    Args:

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した玄関ドア面積（m2）

    """

    return 0.0


def get_A_door_180_f_i():
    """階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した玄関ドア面積…………式(13c)

    Args:

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した玄関ドア面積（m2）

    """

    return 1.6


def get_A_door_270_f_i():
    """階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した玄関ドア面積…………式(13d)

    Args:

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した玄関ドア面積（m2）

    """

    return 0.0


def get_A_ifloor_f_i(A_ifloor_total_f, dwelling_units):
    """階層fにおける単位住戸iの界床面積（m2）…………式(14)

    Args:
      A_ifloor_total_f(float): 階層fにおける単位住戸の界床面積の合計（m2）…………式(34)/get_A_ifloor_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの界床面積（m2）

    """

    return A_ifloor_total_f / dwelling_units


def get_A_ufloor_f_i(A_ufloor_total_f, dwelling_units):
    """階層fにおける単位住戸iの外気に通じる床裏に接する床面積（m2）…………式(15)

    Args:
      A_ufloor_total_f(float): 階層fにおける単位住戸の外気に通じる床裏に接する床面積の合計（m2）…………式(35)/get_A_ufloor_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの外気に通じる床裏に接する床面積（m2）

    """

    return A_ufloor_total_f / dwelling_units


def get_A_ofloor_f_i(total_ofloor_area, dwelling_units):
    """階層fにおける単位住戸iの外気に接する床面積…………式(16)

    Args:
      total_ofloor_area(float): 階層fにおける単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの外気に接する床面積（m2）

    """

    return total_ofloor_area / dwelling_units


def get_A_floor_f_i(total_floor_area, dwelling_units):
    """階層fにおける単位住戸iの床面積…………式(17)

    Args:
      total_floor_area(float): 階層fにおける単位住戸の床面積の合計（m2）…………入力1.2(2)6
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      Decimal: 階層fにおける単位住戸iの床面積（m2）

    """
    A_floor_f_i = total_floor_area / dwelling_units
    # Decimalの有効桁数を小数点以下10桁とする
    A_floor_f_i = Decimal(A_floor_f_i).quantize(Decimal(str(10**(-10))), rounding=ROUND_HALF_UP)
    return A_floor_f_i.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def get_A_MR_f_i(A_floor_f_i, has_other_room):
    """階層fにおける単位住戸iの主たる居室の床面積…………式(18a)

    Args:
      A_floor_f_i(Decimal): 階層fにおける単位住戸iの床面積（m2）…………式(17)/get_A_floor_f_i
      has_other_room(str): その他の居室の有無

    Returns:
      Decimal: 階層fにおける単位住戸iの主たる居室の床面積（m2）

    """

    if has_other_room == '有り':
        A_MR_f_i = float(A_floor_f_i) * 0.346
    elif has_other_room == '無し':
        A_MR_f_i = float(A_floor_f_i) * 0.771
    else:
        raise ValueError("invalid value in has_other_room")

    # Decimalの有効桁数を小数点以下10桁とする
    A_MR_f_i = Decimal(A_MR_f_i).quantize(Decimal(str(10**(-10))), rounding=ROUND_HALF_UP)
    return A_MR_f_i.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def get_A_OR_f_i(A_floor_f_i, has_other_room):
    """階層fにおける単位住戸iのその他の居室の床面積…………式(18b)

    Args:
      A_floor_f_i(Decimal): 階層fにおける単位住戸iの床面積（m2）…………式(17)/get_A_floor_f_i
      has_other_room(str): その他の居室の有無

    Returns:
      Decimal: 階層fにおける単位住戸iのその他の居室の床面積（m2）

    """

    if has_other_room == '有り':
        A_OR_f_i = float(A_floor_f_i) * 0.425
        # Decimalの有効桁数を小数点以下10桁とする
        A_OR_f_i = Decimal(A_OR_f_i).quantize(Decimal(str(10**(-10))), rounding=ROUND_HALF_UP)
        return A_OR_f_i.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    elif has_other_room == '無し':
        return 0.0
    else:
        raise ValueError("invalid value in has_other_room")


def get_L_HB_roof_owall_top_0_oc_f_i(l_frnt_total_f, dwelling_units, total_roof_area):
    """階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19a)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      total_roof_area(float): 階層fにおける単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area

    Returns:
      float: 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の出隅部による熱橋の長さ（m）

    """

    if total_roof_area == 0:
        return 0.0
    else:
        return l_frnt_total_f / dwelling_units


def get_L_HB_roof_owall_top_90_oc_f_i(total_roof_area, l_frnt_total_f, i):
    """階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19b)

    Args:
      total_roof_area(float): 階層fにおける単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した外壁の出隅部による熱橋の長さ（m）

    """

    if i == 0:
        return total_roof_area / l_frnt_total_f
    else:
        return 0.0


def get_L_HB_roof_owall_top_180_oc_f_i(l_frnt_total_f, dwelling_units, f, building_floors):
    """階層fにおける単位住戸iの屋根と主開口方位から時計回りに180°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19c)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      f(int): 階層（-）
      building_floors(int): 建物の階数（階）…………入力1.2(1)3

    Returns:
      float: 階層fにおける単位住戸iの屋根と主開口方位から時計回りに180°の方向に面した外壁の出隅部による熱橋の長さ（m）

    """

    if f == building_floors:
        return l_frnt_total_f / dwelling_units
    else:
        return 0.0


def get_L_HB_roof_owall_top_270_oc_f_i(total_roof_area, l_frnt_total_f, i, dwelling_units):
    """階層fにおける単位住戸iの屋根と主開口方位から時計回りに270°の方向に面した外壁の出隅部による熱橋の長さ（m）…………式(19d)

    Args:
      total_roof_area(float): 階層fにおける単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの屋根と主開口方位から時計回りに270°の方向に面した外壁の出隅部による熱橋の長さ（m）

    """

    if i == dwelling_units - 1:
        return total_roof_area / l_frnt_total_f
    else:
        return 0.0


def get_L_HB_roof_owall_top_0_ic_t_f_i(l_frnt_total_f, dwelling_units, total_roof_area, f, building_floors):
    """階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の上部の入隅部による熱橋の長さ（m）…………式(20a)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      total_roof_area(float): 階層fにおける単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area
      f(int): 階層（-）
      building_floors(int): 建物の階数（階）…………入力1.2(1)3

    Returns:
      float: 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の上部の入隅部による熱橋の長さ（m）

    """

    if total_roof_area != 0 and f != building_floors:
        return l_frnt_total_f / dwelling_units
    # total_roof_area == 0 or f == building_floors に同じ(ドモルガン)
    else:
        return 0.0


def get_L_HB_roof_owall_top_0_ic_b_f_i(l_frnt_total_f, dwelling_units, dwelling_units_minus_1, total_roof_area_minus_1, f):
    """階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の下部の入隅部による熱橋の長さ（m）…………式(20b-1,2)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      dwelling_units_minus_1(float): 階層f-1における単位住戸iの総数（-）…………入力1.2(2)11
      total_roof_area_minus_1(float): 階層f-1における単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area
      f(int): 階層（-）

    Returns:
      float: 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した外壁の下部の入隅部による熱橋の長さ（m）

    """

    # 式(20b-1)
    if dwelling_units_minus_1 != 0:
        if total_roof_area_minus_1 != 0 and f != 1:
            return l_frnt_total_f / dwelling_units
        # total_roof_area-1 == 0 or f == 1 に同じ(ドモルガン)
        else:
            return 0.0
    # 式(20b-2)
    else:
        return 0.0


def get_L_HB_roof_iwall_top_90_f_i(total_roof_area, l_frnt_total_f, i, dwelling_units):
    """階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した界壁による熱橋の長さ（m）…………式(21a-1,2)

    Args:
      total_roof_area(float): 階層fにおける単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した界壁による熱橋の長さ（m）

    """

    # 式(21a-1) 
    if dwelling_units == 1:
        return 0.0
    # 式(21a-2)
    else:
        if i == dwelling_units - 1:
            return total_roof_area / l_frnt_total_f
        elif i == 0:
            return 0.0
        # i != 0 and i != dwelling_units - 1 
        else:
            return total_roof_area / l_frnt_total_f


def get_L_HB_roof_iwall_top_270_f_i(total_roof_area, l_frnt_total_f, i, dwelling_units):
    """階層fにおける単位住戸iの屋根と主開口方位から時計回りに270°の方向に面した界壁による熱橋の長さ（m）…………式(21b-1,2)

    Args:
      total_roof_area(float): 階層fにおける単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの屋根と主開口方位から時計回りに270°の方向に面した界壁による熱橋の長さ（m）

    """

    # 式(21b-1) 
    if dwelling_units == 1:
        return 0.0
    # 式(21b-2)
    else:
        if i == dwelling_units - 1:
            return 0.0
        elif i == 0:
            return total_roof_area / l_frnt_total_f
        # i != 0 and i != dwelling_units - 1 
        else:
            return total_roof_area / l_frnt_total_f


def get_L_dash_HB_roof_iwall_top_90_f_i(total_roof_area, l_frnt_total_f, dwelling_units):
    """階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した室内壁による熱橋の加算長さ（m）…………式(21c)

    Args:
      total_roof_area(float): 階層fにおける単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの屋根と主開口方位から時計回りに90°の方向に面した室内壁による熱橋の加算長さ（m）

    """

    return (total_roof_area / l_frnt_total_f) * (l_frnt_total_f / (20 * dwelling_units))


def get_L_dash_HB_roof_iwall_top_0_f_i(total_roof_area, l_frnt_total_f, dwelling_units):
    """階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した室内壁による熱橋の加算長さ（m）…………式(21d)

    Args:
      total_roof_area(float): 階層fにおける単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの屋根と主開口方位から時計回りに0°の方向に面した室内壁による熱橋の加算長さ（m）

    """

    return (l_frnt_total_f / dwelling_units) * (total_roof_area / (20 * l_frnt_total_f))


def get_L_HB_owall_owall_0_90_f_i(H_f, i):
    """階層fにおける単位住戸iの主開口部方位から時計回りに0°及び90°の方位に面した外壁同士の熱橋の長さ（m）…………式(22a)

    Args:
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口部方位から時計回りに0°及び90°の方位に面した外壁同士の熱橋の長さ（m）

    """

    if i == 0:
        return H_f
    else:
        return 0.0


def get_L_HB_owall_owall_90_180_f_i(H_f, i):
    """階層fにおける単位住戸iの主開口部方位から時計回りに90°及び180°の方位に面した外壁同士の熱橋の長さ（m）…………式(22b)

    Args:
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口部方位から時計回りに90°及び180°の方位に面した外壁同士の熱橋の長さ（m）

    """

    if i == 0:
        return H_f
    else:
        return 0.0


def get_L_HB_owall_owall_180_270_f_i(H_f, i, dwelling_units):
    """階層fにおける単位住戸iの主開口部方位から時計回りに180°及び270°の方位に面した外壁同士の熱橋の長さ（m）…………式(22c)

    Args:
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口部方位から時計回りに180°及び270°の方位に面した外壁同士の熱橋の長さ（m）

    """

    if i == dwelling_units  - 1:
        return H_f
    else:
        return 0.0


def get_L_HB_owall_owall_270_0_f_i(H_f, i, dwelling_units):
    """階層fにおける単位住戸iの主開口部方位から時計回りに270°及び0°の方位に面した外壁同士の熱橋の長さ（m）…………式(22d)

    Args:
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口部方位から時計回りに270°及び0°の方位に面した外壁同士の熱橋の長さ（m）

    """

    if i == dwelling_units  - 1:
        return H_f
    else:
        return 0.0     


def get_L_HB_owall_iwall_0_90_f_i(H_f, i, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と90°の方向に面した界壁による熱橋の長さ（m）…………式(23a-1,2)

    Args:
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と90°の方向に面した界壁による熱橋の長さ（m）

    """

    # 式(23a-1)
    if dwelling_units == 1:
        return 0.0
    # 式(23a-2)
    else:
        if i == dwelling_units - 1:
            return H_f
        elif i == 0:
            return 0.0
        # i != 0 and i != dwelling_units - 1
        else:
            return H_f

    
def get_L_HB_owall_iwall_0_270_f_i(H_f, i, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と270°の方向に面した界壁による熱橋の長さ（m）…………式(23b-1,2)

    Args:
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と270°の方向に面した界壁による熱橋の長さ（m）

    """

    # 式(23b-1)
    if dwelling_units == 1:
        return 0.0
    # 式(23b-2)
    else:
        if i == dwelling_units - 1:
            return 0.0
        elif i == 0:
            return H_f
        # i != 0 and i != dwelling_units - 1
        else:
            return H_f    


def get_L_HB_owall_iwall_180_90_f_i(H_f, i, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と90°の方向に面した界壁による熱橋の長さ（m）…………式(23c-1,2)

    Args:
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と90°の方向に面した界壁による熱橋の長さ（m）

    """

    # 式(23c-1)
    if dwelling_units == 1:
        return 0.0
    # 式(23c-2)
    else:
        if i == dwelling_units - 1:
            return H_f
        elif i == 0:
            return 0.0
        # i != 0 and i != dwelling_units - 1
        else:
            return H_f   


def get_L_HB_owall_iwall_180_270_f_i(H_f, i, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と270°の方向に面した界壁による熱橋の長さ（m）…………式(23d-1,2)

    Args:
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と270°の方向に面した界壁による熱橋の長さ（m）

    """

    # 式(23d-1)
    if dwelling_units == 1:
        return 0.0
    # 式(23d-2)
    else:
        if i == dwelling_units - 1:
            return 0.0
        elif i == 0:
            return H_f
        # i != 0 and i != dwelling_units - 1
        else:
            return H_f   


def get_L_dash_HB_owall_iwall_0_90_f_i(H_f, l_frnt_total_f, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と90°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23e)

    Args:
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と90°の方向に面した室内壁による熱橋の加算長さ（m）

    """

    return H_f * (l_frnt_total_f / (20 * dwelling_units))


def get_L_dash_HB_owall_iwall_90_0_f_i(H_f, l_dpth_total_f, i):
    """階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と0°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23f)

    Args:
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と0°の方向に面した室内壁による熱橋の加算長さ（m）

    """

    if i == 0:
        return H_f * (l_dpth_total_f / 20)
    else:
        return 0.0


def get_L_dash_HB_owall_iwall_180_90_f_i(H_f, l_frnt_total_f, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と90°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23g)

    Args:
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と90°の方向に面した室内壁による熱橋の加算長さ（m）

    """

    return H_f * (l_frnt_total_f / (20 * dwelling_units))


def get_L_dash_HB_owall_iwall_270_0_f_i(H_f, l_dpth_total_f, dwelling_units, i):
    """階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と0°の方向に面した室内壁による熱橋の加算長さ（m）…………式(23h)

    Args:
      H_f(float): 階層fにおける階高（m）…………式(30)/get_H_f
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と0°の方向に面した室内壁による熱橋の加算長さ（m）

    """

    if i == dwelling_units -1:
        return H_f * (l_dpth_total_f / 20)
    else:
        return 0.0  


def get_L_HB_owall_ifloor_0_bottom_t_f_i(l_frnt_total_f, dwelling_units, dwelling_units_plus_1, A_roof_f_i, total_ofloor_area_plus_1, f, building_floors):
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24a-1,2,3)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      dwelling_units_plus_1(float): 階層f+1における単位住戸iの総数（-）…………入力1.2(2)11
      A_roof_f_i(float): 階層fにおける単位住戸iの屋根面積（m2）…………式(8)/get_A_roof_f_i
      total_ofloor_area_plus_1(float): 階層fにおける単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9
      f(int): 階層（-）
      building_floors(int): 建物の階数（階）…………入力1.2(1)3

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の上部と界床による熱橋の長さ（m）

    """

    # 式(24a-1)
    if f == building_floors:
        return 0.0
    # 式(24a-2)
    elif f != building_floors and dwelling_units_plus_1 != 0:
        if A_roof_f_i == 0 and total_ofloor_area_plus_1 == 0:
            return l_frnt_total_f / dwelling_units
        # A_roof_f_i != 0 or total_ofloor_area_plus_1 != 0
        else:
            return 0.0
    # 式(24a-3)
    # f != building_floors and dwelling_units_plus_1 == 0:
    else:
        return 0.0

    
def get_L_HB_owall_ifloor_0_bottom_b_f_i(l_frnt_total_f, dwelling_units, dwelling_units_minus_1, A_ofloor_f_i, total_roof_area_minus_1, f):
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24b-1,2)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      dwelling_units_minus_1(float): 階層f-1における単位住戸iの総数（-）…………入力1.2(2)11
      A_ofloor_f_i(float): 階層fにおける単位住戸iの外気に接する床面積（m2）…………式(16)/get_A_ofloor_f_i
      total_roof_area_minus_1(float): 階層f-1における単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area
      f(int): 階層（-）

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の下部と界床による熱橋の長さ（m）

    """

    # 式(24b-1)
    if f == 1 or dwelling_units_minus_1 == 0:
        return 0.0
    # 式(24b-2)
    # f != 1 and dwelling_units_minus_1 != 0
    else:
        if A_ofloor_f_i == 0 and total_roof_area_minus_1 == 0:
            return l_frnt_total_f / dwelling_units
        # A_ofloor_f_i != 0 or total_roof_area_minus_1 != 0
        else:
            return 0.0

def get_L_HB_owall_ifloor_90_bottom_t_f_i(l_dpth_total_f, total_roof_area, l_frnt_total_f, f, building_floors, i):
    """階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24c-1,2)

    Args:
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      total_roof_area(float): 階層fにおける単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      i(int): 単位住戸
      f(int): 階層（-）
      building_floors(int): 建物の階数（階）…………入力1.2(1)3

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁の上部と界床による熱橋の長さ（m）

    """

    # 式(24c-1)
    if f == building_floors:
        return 0.0
    # 式(24c-2)
    else:
        if i == 0:
            return l_dpth_total_f - (total_roof_area / l_frnt_total_f)
        else:
            return 0.0


def get_L_HB_owall_ifloor_90_bottom_b_f_i(l_dpth_total_f, total_ofloor_area, l_frnt_total_f, f, i):
    """階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24d-1,2)

    Args:
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      total_ofloor_area(float): 階層fにおける単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      f(int): 階層（-）
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁の下部と界床による熱橋の長さ（m）

    """

    # 式(24d-1)
    if f == 1:
        return 0.0
    # 式(24d-2)
    else:
        if i == 0:
            return l_dpth_total_f - (total_ofloor_area / l_frnt_total_f)
        else:
            return 0.0


def get_L_HB_owall_ifloor_180_bottom_t_f_i(l_frnt_total_f, dwelling_units, f, building_floors):
    """階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24e)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      f(int): 階層（-）
      building_floors(int): 建物の階数（階）…………入力1.2(1)3

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁の上部と界床による熱橋の長さ（m）

    """

    if f == building_floors:
        return 0.0
    else:
        return l_frnt_total_f / dwelling_units


def get_L_HB_owall_ifloor_180_bottom_b_f_i(l_frnt_total_f, dwelling_units, f):
    """階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24f)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      f(int): 階層（-）

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁の下部と界床による熱橋の長さ（m）

    """

    if f == 1:
        return 0.0
    else:
        return l_frnt_total_f / dwelling_units


def get_L_HB_owall_ifloor_270_bottom_t_f_i(l_dpth_total_f, total_roof_area, l_frnt_total_f, f, building_floors, i, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁の上部と界床による熱橋の長さ（m）…………式(24g-1,2)

    Args:
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      total_roof_area(float): 階層fにおける単位住戸の屋根面積の合計（m2）…………式(32)/get_total_roof_area
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      f(int): 階層（-）
      building_floors(int): 建物の階数（階）…………入力1.2(1)3
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁の上部と界床による熱橋の長さ（m）

    """

    # 式(24g-1)
    if f == building_floors:
        return 0.0
    # 式(24g-2)
    else:
        if i == dwelling_units - 1:
            return l_dpth_total_f - (total_roof_area / l_frnt_total_f)
        else:
            return 0.0


def get_L_HB_owall_ifloor_270_bottom_b_f_i(l_dpth_total_f, total_ofloor_area, l_frnt_total_f, f, i, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁の下部と界床による熱橋の長さ（m）…………式(24h-1,2)

    Args:
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      total_ofloor_area(float): 階層fにおける単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      f(int): 階層（-）
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁の下部と界床による熱橋の長さ（m）

    """

    # 式(24h-1)
    if f == 1:
        return 0.0
    # 式(24h-2)
    else:
        if i == dwelling_units - 1:
            return l_dpth_total_f - (total_ofloor_area / l_frnt_total_f)
        else:
            return 0.0


def get_L_HB_owall_ufloor_0_bottom_f_i(l_frnt_total_f, dwelling_units, f):
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25a)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      f(int): 階層（-）

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）

    """

    if f == 1:
        return l_frnt_total_f / dwelling_units
    else:
        return 0.0


def get_L_HB_owall_ufloor_90_bottom_f_i(l_dpth_total_f, f, i):
    """階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25b-1,2)

    Args:
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      f(int): 階層（-）
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）

    """

    # 式(25b-1)
    if f == 1:
        if i == 0:
            return l_dpth_total_f
        else:
            return 0.0
    # 式(25b-2)
    else:
        return 0.0


def get_L_HB_owall_ufloor_180_bottom_f_i(l_frnt_total_f, dwelling_units, f):
    """階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25c)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      f(int): 階層（-）

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）

    """

    if f == 1:
        return l_frnt_total_f / dwelling_units
    else:
        return 0.0


def get_L_HB_owall_ufloor_270_bottom_f_i(l_dpth_total_f, f, i, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(25d-1,2)

    Args:
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      f(int): 階層（-）
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と外気に通じる床裏に接する床による熱橋の長さ（m）

    """
    
    # 式(25d-1)
    if f == 1:
        if i == dwelling_units - 1:
            return l_dpth_total_f
        else:
            return 0.0
    # 式(25d-2)
    else:
        return 0.0

 
def get_L_HB_owall_ofloor_0_bottom_oc_f_i(l_frnt_total_f, dwelling_units, total_ofloor_area):
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26a)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      total_ofloor_area(float): 階層fにおける単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）

    """

    if total_ofloor_area != 0:
        return l_frnt_total_f / dwelling_units
    else:
        return 0.0

 
def get_L_HB_owall_ofloor_90_bottom_oc_f_i(total_ofloor_area, l_frnt_total_f, i):
    """階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26b)

    Args:
      total_ofloor_area(float): 階層fにおける単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）

    """

    if i == 0:
        return total_ofloor_area / l_frnt_total_f
    else:
        return 0.0


def get_L_HB_owall_ofloor_180_bottom_oc_f_i():
    """階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26c)

    Args:

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに180°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）

    """

    return 0.0

  
def get_L_HB_owall_ofloor_270_bottom_oc_f_i(total_ofloor_area, l_frnt_total_f, i, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）…………式(26d)

    Args:
      total_ofloor_area(float): 階層fにおける単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      i(int): 単位住戸
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した外壁と外気に接する床の出隅部による熱橋の長さ（m）

    """

    if i == dwelling_units - 1:
        return total_ofloor_area / l_frnt_total_f
    else:
        return 0.0


def get_L_HB_owall_ofloor_0_bottom_ic_t_f_i(l_frnt_total_f, dwelling_units, dwelling_units_plus_1, total_ofloor_area_plus_1, f, building_floors):
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の上部と外気に接する床の入隅部による熱橋の長さ（m）…………式(27a-1,2)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      dwelling_units_plus_1(float): 階層f+1における単位住戸iの総数（-）…………入力1.2(2)11
      total_ofloor_area_plus_1(float): 階層f+1における単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9
      f(int): 階層（-）
      building_floors(int): 建物の階数（階）…………入力1.2(1)3

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の上部と外気に接する床の入隅部による熱橋の長さ（m）

    """

    # 式(27a-1)
    if dwelling_units_plus_1 != 0:
        if total_ofloor_area_plus_1 != 0 and f != building_floors:
            return l_frnt_total_f / dwelling_units
        # total_ofloor_area_plus_1 == 0 or f == building_floors
        else:
            return 0.0
    # 式(27a-2)
    else:
        return 0.0


def get_L_HB_owall_ofloor_0_bottom_ic_b_f_i(l_frnt_total_f, dwelling_units, total_ofloor_area):
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の下部と外気に接する床の入隅部による熱橋の長さ（m）…………式(27b)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      total_ofloor_area(float): 階層f+1における単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した外壁の下部と外気に接する床の入隅部による熱橋の長さ（m）

    """

    if total_ofloor_area != 0:
        return l_frnt_total_f / dwelling_units
    else:
        return 0.0


def get_L_HB_iwall_ufloor_90_bottom_f_i(l_dpth_total_f, dwelling_units, f, i):
    """階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した界壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(28a-1,2)

    Args:
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      f(int): 階層（-）
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した界壁と外気に通じる床裏に接する床による熱橋の長さ（m）

    """

    # 式(28a-1)
    if dwelling_units == 1 or f != 1:
        return 0
    # 式(28a-2)
    # dwelling_units != 1 and f == 1
    else:
        if i == dwelling_units - 1:
            return l_dpth_total_f
        elif i == 0:
            return 0.0
        # i != 0 and i != dwelling_units - 1
        else:
            return l_dpth_total_f


def get_L_HB_iwall_ufloor_270_bottom_f_i(l_dpth_total_f, dwelling_units, f, i):
    """階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した界壁と外気に通じる床裏に接する床による熱橋の長さ（m）…………式(28b-1,2)

    Args:
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      f(int): 階層（-）
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した界壁と外気に通じる床裏に接する床による熱橋の長さ（m）

    """

    # 式(28b-1)
    if dwelling_units == 1 or f != 1:
        return 0
    # 式(28b-2)
    # dwelling_units != 1 and f == 1
    else:
        if i == 0:
            return l_dpth_total_f
        elif i == dwelling_units - 1:
            return 0.0
        # i != 0 and i != dwelling_units - 1
        else:
            return l_dpth_total_f


def get_L_dash_HB_iwall_ufloor_90_bottom_f_i(l_dpth_total_f, l_frnt_total_f, dwelling_units, f):
    """階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した室内壁と外気に通じる床裏に接する床による熱橋の加算長さ（m）…………式(28c)

    Args:
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      f(int): 階層（-）

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した室内壁と外気に通じる床裏に接する床による熱橋の加算長さ（m）

    """

    if f == 1:
        return l_dpth_total_f * (l_frnt_total_f / (20 * dwelling_units))
    else:
        return 0.0    


def get_L_dash_HB_iwall_ufloor_0_bottom_f_i(l_frnt_total_f, l_dpth_total_f, dwelling_units, f):
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した室内壁と外気に通じる床裏に接する床による熱橋の加算長さ（m）…………式(28d)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      l_dpth_total_f(float): 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)/get_l_dpth_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      f(int): 階層（-）

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した室内壁と外気に通じる床裏に接する床による熱橋の加算長さ（m）

    """

    if f == 1:
        return l_frnt_total_f * (l_dpth_total_f / (20 * dwelling_units))
    else:
        return 0.0 


def get_L_HB_iwall_ofloor_90_bottom_f_i(total_ofloor_area, l_frnt_total_f, dwelling_units, i):
    """階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した界壁と外気に接する床による熱橋の長さ（m）…………式(29a-1,2)

    Args:
      total_ofloor_area(float): 階層fにおける単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した界壁と外気に接する床による熱橋の長さ（m）

    """

    # 式(29a-1)
    if dwelling_units == 1:
        return 0.0
    # 式(29a-2)
    else:
        if i == dwelling_units - 1:
            return total_ofloor_area / l_frnt_total_f
        elif i == 0:
            return 0.0
        # i != 0 and i != dwelling_units - 1
        else:
            return total_ofloor_area / l_frnt_total_f


def get_L_HB_iwall_ofloor_270_bottom_f_i(total_ofloor_area, l_frnt_total_f, dwelling_units, i):
    """階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した界壁と外気に接する床による熱橋の長さ（m）…………式(29b-1,2)

    Args:
      total_ofloor_area(float): 階層fにおける単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      i(int): 単位住戸

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに270°の方向に面した界壁と外気に接する床による熱橋の長さ（m）

    """

    # 式(29b-1)
    if dwelling_units == 1:
        return 0.0
    # 式(29b-2)
    else:
        if i == 0:
            return total_ofloor_area / l_frnt_total_f
        elif i == dwelling_units - 1:
            return 0.0
        # i != 0 and i != dwelling_units - 1
        else:
            return total_ofloor_area / l_frnt_total_f


def get_L_dash_HB_iwall_ofloor_90_bottom_f_i(total_ofloor_area, l_frnt_total_f, dwelling_units):
    """階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した室内壁と外気に接する床による熱橋の加算長さ（m）…………式(29c)

    Args:
      total_ofloor_area(float): 階層fにおける単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに90°の方向に面した室内壁と外気に接する床による熱橋の加算長さ（m）

    """

    return (total_ofloor_area / l_frnt_total_f) * (l_frnt_total_f / (20 * dwelling_units))


def get_L_dash_HB_iwall_ofloor_0_bottom_f_i(l_frnt_total_f, dwelling_units, total_ofloor_area):
    """階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した室内壁と外気に接する床による熱橋の加算長さ（m）…………式(29d)

    Args:
      l_frnt_total_f(float): 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)/get_l_frnt_total_f
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11
      total_ofloor_area(float): 階層fにおける単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9

    Returns:
      float: 階層fにおける単位住戸iの主開口方位から時計回りに0°の方向に面した室内壁と外気に接する床による熱橋の加算長さ（m）

    """

    return (l_frnt_total_f / dwelling_units) * (total_ofloor_area / (20 * l_frnt_total_f))


def get_H_f(building_height, building_floors):
    """階層fにおける階高（m）…………式(30)

    Args:
      building_height(float): 建物の高さ（m）…………入力1.2(1)2
      building_floors(int): 建物の階数（階）…………入力1.2(1)3

    Returns:
      float: 階層fにおける階高（m）

    """

    return building_height / building_floors


def get_l_frnt_total_f(peripheral_length, total_floor_area):
    """階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31a)

    Args:
      peripheral_length(float): 階層fにおける住戸部分全体の外周長（m）…………入力1.2(2)7
      total_floor_area(float): 階層fにおける単位住戸の床面積の合計（m2）…………入力1.2(2)6

    Returns:
      float: 階層fにおける住棟の間口方向に面した住戸部分全体の外周の辺の長さ（m）

    """

    return (peripheral_length + pow((pow(peripheral_length, 2) - 16 * total_floor_area), 0.5)) / 4


def get_l_dpth_total_f(peripheral_length, total_floor_area):
    """階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）…………式(31b)

    Args:
      peripheral_length(float): 階層fにおける住戸部分全体の外周長（m）…………入力1.2(2)7
      total_floor_area(float): 階層fにおける単位住戸の床面積の合計（m2）…………入力1.2(2)6

    Returns:
      float: 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）

    """

    return (peripheral_length - pow((pow(peripheral_length, 2) - 16 * total_floor_area), 0.5)) / 4


def get_total_roof_area(total_floor_area, total_roof_area, f, building_floors):
    """階層fにおける単位住戸の屋根面積の合計（m2）…………式(32)

    Args:
      total_floor_area(float): 階層fにおける単位住戸の床面積の合計（m2）…………入力1.2(2)6
      total_roof_area(float): 階層fにおける単位住戸の屋根面積の合計（m2）…………入力1.2(2)10
      f(int): 階層（-）
      building_floors(int): 建物の階数（階）…………入力1.2(1)3

    Returns:
      float: 階層fにおける住棟の奥行き方向に面した住戸部分全体の外周の辺の長さ（m）

    """

    if f == building_floors:
        return total_floor_area
    else:
        return total_roof_area


def get_A_window_0_total_f(total_window_area, dwelling_units):
    """階層fにおける単位住戸の主開口方位から時計回りに0°の方向に面した部位の窓面積の合計（m2）…………式(33a)

    Args:
      total_window_area(float): 階層fにおける単位住戸の主開口方位から時計回りに0°の方向に面した部位の窓面積の合計（m2）…………入力1.2(2)8
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸の主開口方位から時計回りに0°の方向に面した部位の窓面積の合計（m2）

    """

    return total_window_area * (1 - 0.24 / dwelling_units) * 0.64


def get_A_window_90_total_f(total_window_area, dwelling_units):
    """階層fにおける単位住戸の主開口方位から時計回りに90°の方向に面した部位の窓面積の合計（m2）…………式(33b)

    Args:
      total_window_area(float): 階層fにおける単位住戸の主開口方位から時計回りに90°の方向に面した部位の窓面積の合計（m2）…………入力1.2(2)8
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸の主開口方位から時計回りに90°の方向に面した部位の窓面積の合計（m2）

    """

    return total_window_area * (0.12 / dwelling_units)


def get_A_window_180_total_f(total_window_area, dwelling_units):
    """階層fにおける単位住戸の主開口方位から時計回りに180°の方向に面した部位の窓面積の合計（m2）…………式(33c)

    Args:
      total_window_area(float): 階層fにおける単位住戸の主開口方位から時計回りに180°の方向に面した部位の窓面積の合計（m2）…………入力1.2(2)8
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸の主開口方位から時計回りに180°の方向に面した部位の窓面積の合計（m2）

    """

    return total_window_area * (1 - 0.24 / dwelling_units) * 0.36


def get_A_window_270_total_f(total_window_area, dwelling_units):
    """階層fにおける単位住戸の主開口方位から時計回りに270°の方向に面した部位の窓面積の合計（m2）…………式(33d)

    Args:
      total_window_area(float): 階層fにおける単位住戸の主開口方位から時計回りに270°の方向に面した部位の窓面積の合計（m2）…………入力1.2(2)8
      dwelling_units(float): 階層fにおける単位住戸iの総数（-）…………入力1.2(2)11

    Returns:
      float: 階層fにおける単位住戸の主開口方位から時計回りに270°の方向に面した部位の窓面積の合計（m2）

    """

    return total_window_area * (0.12 / dwelling_units)


# 表記ゆれの可能性あり　ofloor→floor_outかも
def get_A_ifloor_total_f(total_floor_area, total_ofloor_area, f):
    """階層fにおける単位住戸の界床面積の合計（m2）…………式(34)

    Args:
      total_floor_area(float): 階層fにおける単位住戸の床面積の合計（m2）…………入力1.2(2)6
      total_ofloor_area(float): 階層fにおける単位住戸の外気に接する床面積の合計（m2）…………入力1.2(2)9
      f(int): 階層（-）

    Returns:
      float: 階層fにおける単位住戸の界床面積の合計（m2）

    """

    if f == 1:
        return 0
    # f >= 2
    else: 
        return total_floor_area - total_ofloor_area


def get_A_ufloor_total_f(total_floor_area, f):   
    """階層fにおける単位住戸の外気に通じる床裏に接する床面積の合計（m2）…………式(35)

    Args:
      total_floor_area(float): 階層fにおける単位住戸の床面積の合計（m2）…………入力1.2(2)6
      f(int): 階層（-）

    Returns:
      float: 階層fにおける単位住戸の外気に通じる床裏に接する床面積の合計（m2）

    """

    if f == 1:
        return total_floor_area
    # f >= 2
    else:
        return 0


def get_H_180_type(corridor_type):       
    """H_180(主開口方位から時計回りに180°の方向に面した部位の隣接空間の温度差係数)を求める際の温度差係数の種類…………表3

    Args:
      corridor_type(str): 共用廊下の種類…………入力1.2(1)4

    Returns:
      str: 温度差係数の種類

    """

    H_type_dict = {
        '外廊下' : '外気',
        '空調しない中廊下' : '外気に通じていない空間',
        '空調する中廊下' : '住戸と同様の熱的環境の空間'
    }

    return H_type_dict[corridor_type]


def get_roof_owall_oc_psi(building_structure, owall_insulation_part, ceiling_insulation_part):
    """屋根と外壁による出隅部の熱橋の線熱貫流率…………表4

    Args:
      building_structure(structure: structure: str): 当該共同住宅の構造…………入力1.2(1)1
      owall_insulation_part(str): 断熱位置（外壁）…………入力1.3 10
      ceiling_insulation_part(str): 断熱位置（屋根）…………入力1.3 11

    Returns:
      float: 屋根と外壁による出隅部の熱橋の線熱貫流率

    """

    # Key: 断熱位置（屋根）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が無断熱のときの線熱貫流率
    No_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.00,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00
    }

    # Key: 断熱位置（屋根）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が内断熱のときの線熱貫流率
    Internal_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.00,
        '外断熱' : 2.10,
        '外内両面断熱' : 0.00
    }

    # Key: 断熱位置（屋根）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が外断熱のときの線熱貫流率
    External_dict = {
        '無断熱' : 0.00,
        '内断熱' : 2.10,
        '外断熱' : 1.20,
        '外内両面断熱' : 0.00
    }

    # Key: 断熱位置（屋根）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が外内両面断熱のときの線熱貫流率
    Both_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.00,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00
    }

    if building_structure == '鉄筋コンクリート造':
        try:
            if owall_insulation_part == '無断熱':
                return No_dict[ceiling_insulation_part]
            elif owall_insulation_part == '内断熱':
                return Internal_dict[ceiling_insulation_part]
            elif owall_insulation_part == '外断熱':
                return External_dict[ceiling_insulation_part]
            elif owall_insulation_part == '外内両面断熱':
                return Both_dict[ceiling_insulation_part]
            else:
                raise ValueError("invalid value in owall_insulation_part")
        except KeyError:
            raise ValueError("invalid value in ceiling_insulation_part")
    elif building_structure == '鉄骨造':
        return 1.00
        # ↓テスト用の値
        # return 2.10
    elif building_structure == '木造（CLTパネル工法以外）':
        return 0.00
    elif building_structure == '木造（CLTパネル工法）':
        return 0.36
    else:
        raise ValueError("invalid value in building_structure")


def get_roof_owall_ic_psi(building_structure, owall_insulation_part, ceiling_insulation_part):
    """屋根と外壁による入隅部の熱橋の線熱貫流率…………表5

    Args:
      building_structure(structure: structure: str): 当該共同住宅の構造…………入力1.2(1)1
      owall_insulation_part(str): 断熱位置（外壁）…………入力1.3 10
      ceiling_insulation_part(str): 断熱位置（屋根）…………入力1.3 11

    Returns:
      float: 屋根と外壁による入隅部の熱橋の線熱貫流率

    """

    # Key: 断熱位置（屋根）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が無断熱のときの線熱貫流率
    No_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.00,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00
    }

    # Key: 断熱位置（屋根）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が内断熱のときの線熱貫流率
    Internal_dict = {
        '無断熱' : 0.00,
        '内断熱' : 3.35,
        '外断熱' : 0.90,
        '外内両面断熱' : 0.00
    }

    # Key: 断熱位置（屋根）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が外断熱のときの線熱貫流率
    External_dict = {
        '無断熱' : 0.00,
        '内断熱' : 2.50,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00
    }

    # Key: 断熱位置（屋根）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が外内両面断熱のときの線熱貫流率
    Both_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.00,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00
    }

    if building_structure == '鉄筋コンクリート造':
        try:
            if owall_insulation_part == '無断熱':
                return No_dict[ceiling_insulation_part]
            elif owall_insulation_part == '内断熱':
                return Internal_dict[ceiling_insulation_part]
            elif owall_insulation_part == '外断熱':
                return External_dict[ceiling_insulation_part]
            elif owall_insulation_part == '外内両面断熱':
                return Both_dict[ceiling_insulation_part]
            else:
                raise ValueError("invalid value in owall_insulation_part")
        except KeyError:
            raise ValueError("invalid value in ceiling_insulation_part")
    elif building_structure == '鉄骨造':
        return 1.00
        # ↓テスト用の値
        # return 2.50
    elif building_structure == '木造（CLTパネル工法以外）':
        return 0.00
    elif building_structure == '木造（CLTパネル工法）':
        return 0.36
    else:
        raise ValueError("invalid value in building_structure")


def get_roof_iwall_psi(building_structure, ceiling_insulation_part, has_iwall_insulation_reinforcement):
    """屋根と界壁又は室内壁による熱橋の線熱貫流率…………表6

    Args:
      building_structure(structure: structure: str): 当該共同住宅の構造…………入力1.2(1)1
      ceiling_insulation_part(str): 断熱位置（屋根）…………入力1.3 11
      has_iwall_insulation_reinforcement(str): 断熱位置（界壁）…………入力1.3 14

    Returns:
      float: 屋根と界壁又は室内壁による熱橋の線熱貫流率

    """

    ###
    # HEESAPART-17(2020/08/06)の時点で、
    # 対象部位がない場合（＝界壁がない建物の場合）の線熱貫流率は定義されていない 
    # → とりあえず線熱貫流率を0とすることにする
    ###
    # Key: 断熱位置（界壁）
    # Value: 鉄筋コンクリート造かつ断熱位置（屋根）が無断熱のときの線熱貫流率
    No_dict = {
        '無し' : 0.00,
        '有り' : 0.00,
        '対象部位なし' : 0.00
    }

    # Key: 断熱位置（界壁）
    # Value: 鉄筋コンクリート造かつ断熱位置（屋根）が内断熱のときの線熱貫流率
    Internal_dict = {
        '無し' : 3.05,
        '有り' : 2.15,
        '対象部位なし' : 0.00
    }

    # Key: 断熱位置（界壁）
    # Value: 鉄筋コンクリート造かつ断熱位置（屋根）が外断熱のときの線熱貫流率
    External_dict = {
        '無し' : 0.00,
        '有り' : 0.00,
        '対象部位なし' : 0.00
    }

    # Key: 断熱位置（界壁）
    # Value: 鉄筋コンクリート造かつ断熱位置（屋根）が外内両面断熱のときの線熱貫流率
    Both_dict = {
        '無し' : 0.00,
        '有り' : 0.00,
        '対象部位なし' : 0.00
    }

    if building_structure == '鉄筋コンクリート造':
        try:
            if ceiling_insulation_part == '無断熱':
                return No_dict[has_iwall_insulation_reinforcement]
            elif ceiling_insulation_part == '内断熱':
                return Internal_dict[has_iwall_insulation_reinforcement]
            elif ceiling_insulation_part == '外断熱':
                return External_dict[has_iwall_insulation_reinforcement]
            elif ceiling_insulation_part == '外内両面断熱':
                return Both_dict[has_iwall_insulation_reinforcement]
            else:
                raise ValueError("invalid value in ceiling_insulation_part")
        except KeyError:
            raise ValueError("invalid value in has_iwall_insulation_reinforcement")
    elif building_structure == '鉄骨造':
        return 1.00
        # ↓テスト用の値
        # return 2.15
    elif building_structure == '木造（CLTパネル工法以外）':
        return 0.00
    elif building_structure == '木造（CLTパネル工法）':
        return 0.36
    else:
        raise ValueError("invalid value in building_structure")


def get_owall_owall_psi(building_structure, owall_insulation_part):
    """外壁同士による熱橋の線熱貫流率…………表7

    Args:
      building_structure(structure: structure: str): 当該共同住宅の構造…………入力1.2(1)1
      owall_insulation_part(str): 断熱位置（外壁）…………入力1.3 10

    Returns:
      float: 外壁同士による熱橋の線熱貫流率

    """

    if building_structure == '鉄筋コンクリート造':
        if owall_insulation_part == '無断熱':
            return 0.00
        elif owall_insulation_part == '内断熱':
            return 0.00
        elif owall_insulation_part == '外断熱':
            return 0.00
        elif owall_insulation_part == '外内両面断熱':
            return 0.00
        else:
            raise ValueError("invalid value in owall_insulation_part")
    elif building_structure == '鉄骨造':
        return 0.60
        # ↓テスト用の値
        # return 0.60
    elif building_structure == '木造（CLTパネル工法以外）':
        return 0.00
    elif building_structure == '木造（CLTパネル工法）':
        return 0.00
    else:
        raise ValueError("invalid value in building_structure")


def get_owall_iwall_psi(building_structure, owall_insulation_part, has_iwall_insulation_reinforcement):
    """外壁と界壁又は室内壁による熱橋の線熱貫流率…………表8

    Args:
      building_structure(structure: structure: str): 当該共同住宅の構造…………入力1.2(1)1
      owall_insulation_part(str): 断熱位置（外壁）…………入力1.3 10
      has_iwall_insulation_reinforcement(str): 断熱位置（界壁）…………入力1.3 14

    Returns:
      float: 外壁と界壁又は室内壁による熱橋の線熱貫流率

    """

    ###
    # HEESAPART-17(2020/08/06)の時点で、
    # 対象部位がない場合（＝界壁がない建物の場合）の線熱貫流率は定義されていない 
    # → とりあえず線熱貫流率を0とすることにする
    ###
    # Key: 断熱位置（界壁）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が無断熱のときの線熱貫流率
    No_dict = {
        '無し' : 0.00,
        '有り' : 0.00,
        '対象部位なし' : 0.00 
    }

    # Key: 断熱位置（界壁）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が内断熱のときの線熱貫流率
    Internal_dict = {
        '無し' : 3.05,
        '有り' : 2.15,
        '対象部位なし' : 0.00
    }

    # Key: 断熱位置（界壁）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が外断熱のときの線熱貫流率
    External_dict = {
        '無し' : 0.00,
        '有り' : 0.00,
        '対象部位なし' : 0.00
    }

    # Key: 断熱位置（界壁）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が外内両面断熱のときの線熱貫流率
    Both_dict = {
        '無し' : 0.00,
        '有り' : 0.00,
        '対象部位なし' : 0.00
    }

    if building_structure == '鉄筋コンクリート造':
        try:
            if owall_insulation_part == '無断熱':
                return No_dict[has_iwall_insulation_reinforcement]
            elif owall_insulation_part == '内断熱':
                return Internal_dict[has_iwall_insulation_reinforcement]
            elif owall_insulation_part == '外断熱':
                return External_dict[has_iwall_insulation_reinforcement]
            elif owall_insulation_part == '外内両面断熱':
                return Both_dict[has_iwall_insulation_reinforcement]
            else:
                raise ValueError("invalid value in owall_insulation_part")
        except KeyError:
            raise ValueError("invalid value in has_iwall_insulation_reinforcement")
    elif building_structure == '鉄骨造':
        return 0.60
        # ↓テスト用の値
        # return 3.05
    elif building_structure == '木造（CLTパネル工法以外）':
        return 0.00
    elif building_structure == '木造（CLTパネル工法）':
        return 0.36
    else:
        raise ValueError("invalid value in building_structure")


def get_owall_ifloor_psi(building_structure, owall_insulation_part, has_ifloor_insulation_reinforcement):
    """外壁と界床による熱橋の線熱貫流率…………表9

    Args:
      building_structure(structure: structure: str): 当該共同住宅の構造…………入力1.2(1)1
      owall_insulation_part(str): 断熱位置（外壁）…………入力1.3 10
      has_ifloor_insulation_reinforcement(str): 断熱位置（界床）…………入力1.3 15

    Returns:
      float: 外壁と界床による熱橋の線熱貫流率

    """

    ###
    # HEESAPART-17(2020/08/06)の時点で、
    # 対象部位がない場合（＝界床がない建物の場合）の線熱貫流率は定義されていない 
    # → とりあえず線熱貫流率を0とすることにする
    ###
    # Key: 断熱位置（界床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が無断熱のときの線熱貫流率
    No_dict = {
        '無し' : 0.00,
        '有り' : 0.00,
        '対象部位なし' : 0.00,
    }

    # Key: 断熱位置（界床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が内断熱のときの線熱貫流率
    Internal_dict = {
        '無し' : 3.05,
        '有り' : 2.15,
        '対象部位なし' : 0.00,
    }

    # Key: 断熱位置（界床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が外断熱のときの線熱貫流率
    External_dict = {
        '無し' : 0.00,
        '有り' : 0.00,
        '対象部位なし' : 0.00,
    }

    # Key: 断熱位置（界床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が外内両面断熱のときの線熱貫流率
    Both_dict = {
        '無し' : 0.00,
        '有り' : 0.00,
        '対象部位なし' : 0.00,
    }

    if building_structure == '鉄筋コンクリート造':
        try:
            if owall_insulation_part == '無断熱':
                return No_dict[has_ifloor_insulation_reinforcement]
            elif owall_insulation_part == '内断熱':
                return Internal_dict[has_ifloor_insulation_reinforcement]
            elif owall_insulation_part == '外断熱':
                return External_dict[has_ifloor_insulation_reinforcement]
            elif owall_insulation_part == '外内両面断熱':
                return Both_dict[has_ifloor_insulation_reinforcement]
            else:
                raise ValueError("invalid value in owall_insulation_part")
        except KeyError:
            raise ValueError("invalid value in has_ifloor_insulation_reinforcement")
    elif building_structure == '鉄骨造':
        return 1.00
        # ↓テスト用の値
        # return 0.36
    elif building_structure == '木造（CLTパネル工法以外）':
        return 0.00
    elif building_structure == '木造（CLTパネル工法）':
        return 0.36
    else:
        raise ValueError("invalid value in building_structure")


def get_owall_ufloor_psi(building_structure, owall_insulation_part, lowermost_floor_insulation_part):
    """外壁と外気に通じる床裏に接する床による熱橋の線熱貫流率…………表10

    Args:
      building_structure(structure: structure: str): 当該共同住宅の構造…………入力1.2(1)1
      owall_insulation_part(str): 断熱位置（外壁）…………入力1.3 10
      lowermost_floor_insulation_part(str): 断熱位置（外気に通じる床裏に接する床）…………入力1.3 12

    Returns:
      float: 外壁と外気に通じる床裏に接する床による熱橋の線熱貫流率

    """

    ###
    # HEESAPART-17(2020/08/06)の時点で、
    # 対象部位がない場合（＝外気に通じる床裏に接する床がない建物の場合）の線熱貫流率は定義されていない 
    # → とりあえず線熱貫流率を0とすることにする
    ###
    # Key: 断熱位置（外気に通じる床裏に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が無断熱のときの線熱貫流率
    No_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.00,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00,
        '対象部位なし': 0.00
    }

    # Key: 断熱位置（外気に通じる床裏に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が内断熱のときの線熱貫流率
    Internal_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.00,
        '外断熱' : 2.00,
        '外内両面断熱' : 0.00,
        '対象部位なし': 0.00
    }

    # Key: 断熱位置（外気に通じる床裏に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が外断熱のときの線熱貫流率
    External_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.80,
        '外断熱' : 2.10,
        '外内両面断熱' : 0.00,
        '対象部位なし': 0.00
    }

    # Key: 断熱位置（外気に通じる床裏に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が外内両面断熱のときの線熱貫流率
    Both_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.00,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00,
        '対象部位なし': 0.00
    }

    if building_structure == '鉄筋コンクリート造':
        try:
            if owall_insulation_part == '無断熱':
                return No_dict[lowermost_floor_insulation_part]
            elif owall_insulation_part == '内断熱':
                return Internal_dict[lowermost_floor_insulation_part]
            elif owall_insulation_part == '外断熱':
                return External_dict[lowermost_floor_insulation_part]
            elif owall_insulation_part == '外内両面断熱':
                return Both_dict[lowermost_floor_insulation_part]
            else:
                raise ValueError("invalid value in owall_insulation_part")
        except KeyError:
            raise ValueError("invalid value in lowermost_floor_insulation_part")
    elif building_structure == '鉄骨造':
        return 1.00
        # ↓テスト用の値
        # return 2.00
    elif building_structure == '木造（CLTパネル工法以外）':
        return 0.00
    elif building_structure == '木造（CLTパネル工法）':
        return 0.36
    else:
        raise ValueError("invalid value in building_structure")


# 「断熱位置（外壁（下部））」＝「断熱位置（外壁）」
def get_owall_ofloor_oc_psi(building_structure, owall_insulation_part, ofloor_insulation_part):
    """外壁と外気に接する床の出隅部による熱橋の線熱貫流率…………表11

    Args:
      building_structure(structure: structure: str): 当該共同住宅の構造…………入力1.2(1)1
      owall_insulation_part(str): 断熱位置（外壁（下部））…………　＝断熱位置（外壁）
      ofloor_insulation_part(str): 断熱位置（外気に接する床）…………入力1.3 13

    Returns:
      float: 外壁と外気に接する床の出隅部による熱橋の線熱貫流率

    """

    ###
    # HEESAPART-17(2020/08/06)の時点で、
    # 対象部位がない場合（＝外気に接する床がない建物の場合）の線熱貫流率は定義されていない 
    # → とりあえず線熱貫流率を0とすることにする
    ###
    # Key: 断熱位置（外気に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁（下部））が無断熱のときの線熱貫流率
    No_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.00,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00,
        '対象部位なし' : 0.00,
    }

    # Key: 断熱位置（外気に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁（下部））が内断熱のときの線熱貫流率
    Internal_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.00,
        '外断熱' : 2.00,
        '外内両面断熱' : 0.00,
        '対象部位なし' : 0.00,
    }

    # Key: 断熱位置（外気に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁（下部））が外断熱のときの線熱貫流率
    External_dict = {
        '無断熱' : 0.00,
        '内断熱' : 2.00,
        '外断熱' : 1.20,
        '外内両面断熱' : 0.00,
        '対象部位なし' : 0.00,
    }

    # Key: 断熱位置（外気に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁（下部））が外内両面断熱のときの線熱貫流率
    Both_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.00,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00,
        '対象部位なし' : 0.00,
    }

    if building_structure == '鉄筋コンクリート造':
        try:
            if owall_insulation_part == '無断熱':
                return No_dict[ofloor_insulation_part]
            elif owall_insulation_part == '内断熱':
                return Internal_dict[ofloor_insulation_part]
            elif owall_insulation_part == '外断熱':
                return External_dict[ofloor_insulation_part]
            elif owall_insulation_part == '外内両面断熱':
                return Both_dict[ofloor_insulation_part]
            else:
                raise ValueError("invalid value in owall_insulation_part")
        except KeyError:
            raise ValueError("invalid value in ofloor_insulation_part")
    elif building_structure == '鉄骨造':
        return 1.00
        # ↓テスト用の値
        # return 0.80
    elif building_structure == '木造（CLTパネル工法以外）':
        return 0.00
    elif building_structure == '木造（CLTパネル工法）':
        return 0.36
    else:
        raise ValueError("invalid value in building_structure")


def get_owall_ofloor_ic_psi(building_structure, owall_insulation_part, ofloor_insulation_part):
    """外壁と外気に接する床の入隅部による熱橋の線熱貫流率…………表12

    Args:
      building_structure(structure: structure: str): 当該共同住宅の構造…………入力1.2(1)1
      owall_insulation_part(str): 断熱位置（外壁）…………入力項目にない（断熱位置（外壁）の表記ゆれの可能性）
      ofloor_insulation_part(str): 断熱位置（外気に接する床）…………入力1.3 13

    Returns:
      float: 外壁と外気に接する床の入隅部による熱橋の線熱貫流率

    """

    ###
    # HEESAPART-17(2020/08/06)の時点で、
    # 対象部位がない場合（＝外気に接する床がない建物の場合）の線熱貫流率は定義されていない 
    # → とりあえず線熱貫流率を0とすることにする
    ###
    # Key: 断熱位置（外気に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が無断熱のときの線熱貫流率
    No_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.00,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00,
        '対象部位なし' : 0.00
    }

    # Key: 断熱位置（外気に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が内断熱のときの線熱貫流率
    Internal_dict = {
        '無断熱' : 0.00,
        '内断熱' : 3.35,
        '外断熱' : 1.70,
        '外内両面断熱' : 0.00,
        '対象部位なし' : 0.00
    }

    # Key: 断熱位置（外気に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が外断熱のときの線熱貫流率
    External_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.90,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00,
        '対象部位なし' : 0.00
    }

    # Key: 断熱位置（外気に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（外壁）が外内両面断熱のときの線熱貫流率
    Both_dict = {
        '無断熱' : 0.00,
        '内断熱' : 0.00,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00,
        '対象部位なし' : 0.00
    }

    if building_structure == '鉄筋コンクリート造':
        try:
            if owall_insulation_part == '無断熱':
                return No_dict[ofloor_insulation_part]
            elif owall_insulation_part == '内断熱':
                return Internal_dict[ofloor_insulation_part]
            elif owall_insulation_part == '外断熱':
                return External_dict[ofloor_insulation_part]
            elif owall_insulation_part == '外内両面断熱':
                return Both_dict[ofloor_insulation_part]
            else:
                raise ValueError("invalid value in owall_insulation_part")
        except KeyError:
            raise ValueError("invalid value in ofloor_insulation_part")
    elif building_structure == '鉄骨造':
        return 1.00
        # ↓テスト用の値
        # return 1.55
    elif building_structure == '木造（CLTパネル工法以外）':
        return 0.00
    elif building_structure == '木造（CLTパネル工法）':
        return 0.36
    else:
        raise ValueError("invalid value in building_structure")

 
def get_iwall_ufloor_psi(building_structure, has_iwall_insulation_reinforcement, lowermost_floor_insulation_part):
    """界壁又は室内壁と外気に通じる床裏に接する床による熱橋の線熱貫流率…………表13

    Args:
      building_structure(structure: structure: str): 当該共同住宅の構造…………入力1.2(1)1
      has_iwall_insulation_reinforcement(str): 断熱位置（界壁）…………入力1.3 14
      lowermost_floor_insulation_part(str): 断熱位置（外気に通じる床裏に接する床）…………入力1.3 12

    Returns:
      float: 界壁又は室内壁と外気に通じる床裏に接する床による熱橋の線熱貫流率

    """

    ###
    # HEESAPART-17(2020/08/06)の時点で、
    # 対象部位がない場合（＝外気に通じる床裏に接する床がない建物の場合）の線熱貫流率は定義されていない 
    # → とりあえず線熱貫流率を0とすることにする
    ###
    # Key: 断熱位置（外気に通じる床裏に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（界壁）が無しのときの線熱貫流率
    No_dict = {
        '無断熱' : 0.00,
        '内断熱' : 3.05,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00,
        '対象部位なし': 0.00
    }

    # Key: 断熱位置（外気に通じる床裏に接する床）
    # Value: 鉄筋コンクリート造かつ断熱位置（界壁）が有りのときの線熱貫流率
    Yes_dict = {
        '無断熱' : 0.00,
        '内断熱' : 2.18,
        '外断熱' : 0.00,
        '外内両面断熱' : 0.00,
        '対象部位なし': 0.00
    }

    ###
    # HEESAPART-17(2020/08/06)の時点で、
    # 対象部位がない場合（＝界壁がない建物の場合）の線熱貫流率は定義されていない 
    # → とりあえず線熱貫流率を0とすることにする
    ###
    if building_structure == '鉄筋コンクリート造':
        try:
            if has_iwall_insulation_reinforcement == '無し':
                return No_dict[lowermost_floor_insulation_part]
            elif has_iwall_insulation_reinforcement == '有り':
                return Yes_dict[lowermost_floor_insulation_part]
            elif has_iwall_insulation_reinforcement == '対象部位なし':
                return 0.00
            else:
                raise ValueError("invalid value in has_iwall_insulation_reinforcement")
        except KeyError:
            raise ValueError("invalid value in lowermost_floor_insulation_part")
    elif building_structure == '鉄骨造':
        return 1.00
        # ↓テスト用の値
        # return 1.00
    elif building_structure == '木造（CLTパネル工法以外）':
        return 0.00
    elif building_structure == '木造（CLTパネル工法）':
        return 0.36
    else:
        raise ValueError("invalid value in building_structure")                   

 
def get_iwall_ofloor_psi(building_structure, ofloor_insulation_part, has_iwall_insulation_reinforcement):
    """界壁又は室内壁と外気に接する床による熱橋の線熱貫流率…………表14

    Args:
      building_structure(structure: structure: str): 当該共同住宅の構造…………入力1.2(1)1
      ofloor_insulation_part(str): 断熱位置（外気に接する床）…………入力1.3 13
      has_iwall_insulation_reinforcement(str): 断熱位置（界壁）…………入力1.3 14

    Returns:
      float: 界壁又は室内壁と外気に接する床による熱橋の線熱貫流率

    """

    ###
    # HEESAPART-17(2020/08/06)の時点で、
    # 対象部位がない場合（＝界壁がない建物の場合）の線熱貫流率は定義されていない 
    # → とりあえず線熱貫流率を0とすることにする
    ###
    # Key: 断熱位置（界壁）
    # Value: 鉄筋コンクリート造かつ断熱位置（外気に接する床）が無断熱のときの線熱貫流率
    No_dict = {
        '無し' : 0.00,
        '有り' : 0.00,
        '対象部位なし' : 0.00
    }

    # Key: 断熱位置（界壁）
    # Value: 鉄筋コンクリート造かつ断熱位置（外気に接する床）が内断熱のときの線熱貫流率
    Internal_dict = {
        '無し' : 3.05,
        '有り' : 2.15,
        '対象部位なし' : 0.00
    }

    # Key: 断熱位置（界壁）
    # Value: 鉄筋コンクリート造かつ断熱位置（外気に接する床）が外断熱のときの線熱貫流率
    External_dict = {
        '無し' : 0.00,
        '有り' : 0.00,
        '対象部位なし' : 0.00
    }

    # Key: 断熱位置（界壁）
    # Value: 鉄筋コンクリート造かつ断熱位置（外気に接する床）が外内両面断熱のときの線熱貫流率
    Both_dict = {
        '無し' : 0.00,
        '有り' : 0.00,
        '対象部位なし' : 0.00
    }

    ###
    # HEESAPART-17(2020/08/06)の時点で、
    # 対象部位がない場合（＝外気に接する床がない建物の場合）の線熱貫流率は定義されていない 
    # → とりあえず線熱貫流率を0とすることにする
    ###
    if building_structure == '鉄筋コンクリート造':
        try:
            if ofloor_insulation_part == '無断熱':
                return No_dict[has_iwall_insulation_reinforcement]
            elif ofloor_insulation_part == '内断熱':
                return Internal_dict[has_iwall_insulation_reinforcement]
            elif ofloor_insulation_part == '外断熱':
                return External_dict[has_iwall_insulation_reinforcement]
            elif ofloor_insulation_part == '外内両面断熱':
                return Both_dict[has_iwall_insulation_reinforcement]
            elif ofloor_insulation_part == '対象部位なし':
                return 0.00
            else:
                raise ValueError("invalid value in ofloor_insulation_part")
        except KeyError:
            raise ValueError("invalid value in has_iwall_insulation_reinforcement")
    elif building_structure == '鉄骨造':
        return 1.00
        # ↓テスト用の値
        # return 1.05
    elif building_structure == '木造（CLTパネル工法以外）':
        return 0.00
    elif building_structure == '木造（CLTパネル工法）':
        return 0.36
    else:
        raise ValueError("invalid value in building_structure")