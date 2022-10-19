from pyhees.section2_2 import calc_E_T 

if __name__ == '__main__':
    spec = {"region": 6, "type": "一般住宅", "reference": {"reference_year": None
        }, "tatekata": "戸建住宅", "sol_region": None, "A_A": 120.08, "A_MR": 29.81, "A_OR": 51.34, "NV_MR": 0, "NV_OR": 0, "TS": False, "r_A_ufvnt": None, "underfloor_insulation": None, "mode_H": "居室のみを暖房する方式でかつ主たる居室とその他の居室ともに温水暖房を設置する場合に該当しない場合", "mode_C": "居室のみを冷房する方式", "H_A": None, "H_MR": {"type": "ルームエアコンディショナー", "e_class": None, "dualcompressor": False
        }, "H_OR": {"type": "ルームエアコンディショナー", "e_class": None, "dualcompressor": False
        }, "H_HS": None, "C_A": None, "C_MR": {"type": "ルームエアコンディショナー", "e_class": None, "dualcompressor": False
        }, "C_OR": {"type": "ルームエアコンディショナー", "e_class": None, "dualcompressor": False
        }, "HW": {"has_bath": True, "hw_type": "ガス従来型給湯機", "hybrid_category": None, "e_rtd": None, "e_dash_rtd": None, "kitchen_watersaving_A": False, "kitchen_watersaving_C": False, "shower_watersaving_A": False, "shower_watersaving_B": False, "washbowl_watersaving_C": False, "bath_insulation": False, "bath_function": "ふろ給湯機(追焚あり)", "pipe_diameter": "上記以外"
        }, "V": {"type": "ダクト式第二種換気設備又はダクト式第三種換気設備", "input": "評価しない", "N": 0.5
        }, "HEX": None, "L": {"has_OR": True, "has_NO": True, "A_OR": 51.34, "MR_installed": "設置しない", "OR_installed": "設置しない", "NO_installed": "設置しない"
        }, "SHC": None, "PV": None, "CG": None, "ENV": {"method": "当該住宅の外皮面積の合計を用いて評価する", "A_env": 307.51, "A_A": 120.08, "U_A": 0.87, "eta_A_H": 4.3, "eta_A_C": 2.8
        }
    }
    
    labels = ["E_T", "E_H", "E_C", "E_V", "E_L", "E_W", "E_S", "E_M", "UPL", "E_gen", "E_E_gen", "E_E_PV_h_d_t", "E_E", "E_G", "E_K"]
    results = calc_E_T(spec)
    print("1年当たりの各消費量 E_T, E_H, E_C, E_V, E_L, E_W, E_S, E_M, UPL, E_gen, E_E_gen, E_E_PV_h_d_t, E_E, E_G, E_K")
    for (label, value) in zip(labels, results):
        print(label + " : " + str(value))
