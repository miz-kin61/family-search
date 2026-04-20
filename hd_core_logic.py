# =====================================================================
# HD ゲート・チャネル・センター定義判定ロジック
# =====================================================================

import pandas as pd

# --- ゲートとセンターの対応表 ---
GATE_TO_CENTER = {
    # 頭脳（Head）
    64: '頭脳', 61: '頭脳', 63: '頭脳',
    
    # 思考（Ajna）
    47: '思考', 24: '思考', 4: '思考', 17: '思考', 43: '思考', 11: '思考',
    
    # 表現（Throat）
    62: '表現', 23: '表現', 56: '表現', 35: '表現', 12: '表現', 45: '表現',
    31: '表現', 8: '表現', 33: '表現', 16: '表現', 20: '表現',
    
    # 自己（G）
    7: '自己', 1: '自己', 13: '自己', 10: '自己', 15: '自己', 46: '自己',
    25: '自己', 2: '自己',
    
    # 意志（Heart/Ego）
    21: '意志', 51: '意志', 40: '意志', 26: '意志',
    
    # 生命力（Sacral）
    5: '生命力', 14: '生命力', 29: '生命力', 59: '生命力', 9: '生命力',
    3: '生命力', 42: '生命力', 27: '生命力', 34: '生命力',
    
    # 直感（Spleen）
    48: '直感', 57: '直感', 44: '直感', 50: '直感', 32: '直感',
    28: '直感', 18: '直感',
    
    # 感情（Solar Plexus）
    6: '感情', 37: '感情', 22: '感情', 36: '感情', 30: '感情',
    55: '感情', 49: '感情',
    
    # 活力（Root）
    53: '活力', 60: '活力', 52: '活力', 19: '活力', 39: '活力',
    41: '活力', 58: '活力', 38: '活力', 54: '活力'
}

# --- チャネル定義（ゲートペア） ---
CHANNELS = [
    # 頭脳 ↔ 思考
    (64, 47, '頭脳', '思考', '64-47'),
    (61, 24, '頭脳', '思考', '61-24'),
    (63, 4, '頭脳', '思考', '63-4'),
    
    # 思考 ↔ 表現
    (17, 62, '思考', '表現', '17-62'),
    (43, 23, '思考', '表現', '43-23'),
    (11, 56, '思考', '表現', '11-56'),
    
    # 表現 ↔ 自己
    (31, 7, '表現', '自己', '31-7'),
    (8, 1, '表現', '自己', '8-1'),
    (33, 13, '表現', '自己', '33-13'),
    (20, 10, '表現', '自己', '20-10'),
    
    # 表現 ↔ 意志
    (45, 21, '表現', '意志', '45-21'),
    
    # 表現 ↔ 感情
    (35, 36, '表現', '感情', '35-36'),
    (12, 22, '表現', '感情', '12-22'),
    
    # 表現 ↔ 直感
    (16, 48, '表現', '直感', '16-48'),
    (20, 57, '表現', '直感', '20-57'),
    
    # 表現 ↔ 生命力
    (20, 34, '表現', '生命力', '20-34'),
    
    # 自己 ↔ 意志
    (25, 51, '自己', '意志', '25-51'),
    
    # 自己 ↔ 生命力
    (5, 15, '自己', '生命力', '5-15'),
    (2, 14, '自己', '生命力', '2-14'),
    (46, 29, '自己', '生命力', '46-29'),
    (10, 34, '自己', '生命力', '10-34'),
    
    # 自己 ↔ 直感
    (10, 57, '自己', '直感', '10-57'),
    
    # 意志 ↔ 感情
    (40, 37, '意志', '感情', '40-37'),
    
    # 意志 ↔ 直感
    (26, 44, '意志', '直感', '26-44'),
    
    # 生命力 ↔ 感情
    (6, 59, '生命力', '感情', '6-59'),
    
    # 生命力 ↔ 直感
    (27, 50, '生命力', '直感', '27-50'),
    (34, 57, '生命力', '直感', '34-57'),
    
    # 生命力 ↔ 活力
    (53, 42, '生命力', '活力', '53-42'),
    (3, 60, '生命力', '活力', '3-60'),
    (9, 52, '生命力', '活力', '9-52'),
    
    # 感情 ↔ 活力
    (19, 49, '感情', '活力', '19-49'),
    (39, 55, '感情', '活力', '39-55'),
    (41, 30, '感情', '活力', '41-30'),
    
    # 直感 ↔ 活力
    (18, 58, '直感', '活力', '18-58'),
    (28, 38, '直感', '活力', '28-38'),
    (32, 54, '直感', '活力', '32-54')
]

# --- インカネーションクロス（重要チャネル）---
# 太陽・地球・ノード（北・南）の4つのゲートで構成される
# これは個人の人生のテーマを示す最重要要素

def extract_gates_from_row(row):
    """行データから全ゲートを抽出（ゲート番号のみ）
    
    Parameters:
        row: dict or pd.Series
    """
    gates = set()
    
    # パーソナリティ（P_）とデザイン（D_）の全天体
    planet_cols = [
        'P_Sun', 'P_Earth', 'P_Moon', 'P_NorthNode', 'P_SouthNode',
        'P_Mercury', 'P_Venus', 'P_Mars', 'P_Jupiter', 'P_Saturn',
        'P_Uranus', 'P_Neptune', 'P_Pluto', 'P_Chiron',
        'D_Sun', 'D_Earth', 'D_Moon', 'D_NorthNode', 'D_SouthNode',
        'D_Mercury', 'D_Venus', 'D_Mars', 'D_Jupiter', 'D_Saturn',
        'D_Uranus', 'D_Neptune', 'D_Pluto', 'D_Chiron'
    ]
    
    for col in planet_cols:
        try:
            # dictとSeriesの両方に対応
            if isinstance(row, dict):
                value = row.get(col)
            else:
                # Pandas Series
                value = row.get(col) if hasattr(row, 'get') else row[col] if col in row.index else None
            
            if value is not None and pd.notna(value):
                gate_str = str(value)
                # "38.1" → 38
                gate_num = int(float(gate_str.split('.')[0]))
                gates.add(gate_num)
        except (KeyError, ValueError, AttributeError):
            # カラムが存在しないか、変換できない場合はスキップ
            continue
    
    return gates

def find_active_channels(gates):
    """アクティブなゲートセットからチャネルを判定"""
    active_channels = []
    
    for gate1, gate2, center1, center2, channel_id in CHANNELS:
        if gate1 in gates and gate2 in gates:
            active_channels.append({
                'channel_id': channel_id,
                'gates': (gate1, gate2),
                'centers': (center1, center2)
            })
    
    return active_channels

def determine_defined_centers(active_channels):
    """アクティブなチャネルから定義されたセンターを判定"""
    defined_centers = set()
    
    for channel in active_channels:
        defined_centers.add(channel['centers'][0])
        defined_centers.add(channel['centers'][1])
    
    return defined_centers

def get_incarnation_cross(row):
    """インカネーションクロス（太陽・地球・ノードのゲート）を取得
    
    Parameters:
        row: dict or pd.Series
    """
    def safe_get(row, key):
        """dictとSeriesの両方から安全に値を取得"""
        try:
            if isinstance(row, dict):
                value = row.get(key)
            else:
                value = row.get(key) if hasattr(row, 'get') else row[key] if key in row.index else None
            
            if value is not None and pd.notna(value):
                return int(float(str(value).split('.')[0]))
            return None
        except (KeyError, ValueError, AttributeError):
            return None
    
    cross = {
        'P_Sun': safe_get(row, 'P_Sun'),
        'P_Earth': safe_get(row, 'P_Earth'),
        'P_NorthNode': safe_get(row, 'P_NorthNode'),
        'P_SouthNode': safe_get(row, 'P_SouthNode'),
        'D_Sun': safe_get(row, 'D_Sun'),
        'D_Earth': safe_get(row, 'D_Earth')
    }
    return cross

def analyze_person_hd(row):
    """1行のデータから個人のHD分析を実行
    
    Parameters:
        row: dict or pd.Series
    """
    def safe_get(row, key, default='不明'):
        """dictとSeriesの両方から安全に値を取得"""
        try:
            if isinstance(row, dict):
                return row.get(key, default)
            else:
                return row.get(key, default) if hasattr(row, 'get') else row[key] if key in row.index else default
        except (KeyError, AttributeError):
            return default
    
    # ゲート抽出
    gates = extract_gates_from_row(row)
    
    # チャネル判定
    active_channels = find_active_channels(gates)
    
    # センター定義判定
    defined_centers = determine_defined_centers(active_channels)
    
    # 未定義センター
    all_centers = ['頭脳', '思考', '表現', '自己', '意志', '生命力', '直感', '感情', '活力']
    undefined_centers = [c for c in all_centers if c not in defined_centers]
    
    # インカネーションクロス
    incarnation_cross = get_incarnation_cross(row)
    
    return {
        'gates': gates,
        'active_channels': active_channels,
        'defined_centers': list(defined_centers),
        'undefined_centers': undefined_centers,
        'incarnation_cross': incarnation_cross,
        'type': safe_get(row, 'Type', '不明'),
        'profile': safe_get(row, 'Profile', '不明'),
        'definition': safe_get(row, 'Definition_Type', '不明'),
        'authority': safe_get(row, 'Authority', '不明')
    }

# テスト用
if __name__ == "__main__":
    import pandas as pd
    
    # サンプルデータ
    sample_row = {
        'JST_Time': '1900-01-01 00:00:00',
        'Type': 'Manifesting Generator',
        'Profile': '1/3',
        'Definition_Type': 'Single',
        'Authority': 'Sacral',
        'P_Sun': 38.1,
        'P_Earth': 39.1,
        'P_Moon': 11.5,
        'P_NorthNode': 26.4,
        'P_SouthNode': 45.4,
        'D_Sun': 48.3,
        'D_Earth': 21.3,
        'D_Moon': 57.2,
        'D_NorthNode': 11.1,
        'D_SouthNode': 12.1
    }
    
    result = analyze_person_hd(sample_row)
    print("=== HD分析結果 ===")
    print(f"タイプ: {result['type']}")
    print(f"プロファイル: {result['profile']}")
    print(f"定義型: {result['definition']}")
    print(f"権威: {result['authority']}")
    print(f"\n定義されたセンター: {result['defined_centers']}")
    print(f"未定義センター: {result['undefined_centers']}")
    print(f"\nアクティブなチャネル数: {len(result['active_channels'])}")
    print(f"インカネーションクロス: {result['incarnation_cross']}")
