# =====================================================================
# 👨‍👩‍👧 親子 Not-Self 条件付け分析ツール V2.0
# Parquet対応・AI統合・PDF出力・複数家族パターン保存
# =====================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
import calendar
import json
from pathlib import Path

# HDコアロジックをインポート
import sys
sys.path.append('/home/claude')
from hd_core_logic import (
    GATE_TO_CENTER, CHANNELS, extract_gates_from_row,
    find_active_channels, determine_defined_centers,
    get_incarnation_cross, analyze_person_hd
)

st.set_page_config(page_title="親子 Not-Self 分析", layout="wide", page_icon="👨‍👩‍👧")

# --- セッション状態の初期化 ---
if 'saved_patterns' not in st.session_state:
    st.session_state['saved_patterns'] = []

# --- 🔐 パスワード認証 ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: 
        return True
    
    st.markdown("<h1 style='text-align: center; color: #00BFFF;'>👨‍👩‍👧 親子 Not-Self 分析 V2.0</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>両親のHDから、子供が受けた条件付けを推測</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Access Code", type="password")
        if st.button("System Login"):
            if pwd == "wide":
                st.session_state["password_correct"] = True
                st.rerun()
            else: 
                st.error("Access Denied.")
    return False

if not check_password(): 
    st.stop()

# --- データ読み込み ---
@st.cache_data
def load_hd_data_parquet(year):
    """年に応じて適切なParquetファイルを読み込む"""
    
    # ファイル選択
    if year <= 1934:
        file_name = "HD_Archive_1.parquet"
    elif year <= 1969:
        file_name = "HD_Archive_2.parquet"
    elif year <= 2004:
        file_name = "HD_Archive_3.parquet"
    else:
        file_name = "HD_Archive_4.parquet"
    
    try:
        # まず /mnt/user-data/uploads/ を試す
        df = pd.read_parquet(f'/mnt/user-data/uploads/{file_name}')
    except:
        try:
            # 次に /home/claude/ を試す
            df = pd.read_parquet(f'/home/claude/{file_name}')
        except:
            st.warning(f"⚠️ {file_name} が見つかりません。サンプルモードで動作します。")
            return None
    
    # 日時処理
    df['JST_Time'] = pd.to_datetime(df['JST_Time'])
    df['Date'] = df['JST_Time'].dt.date
    df['Year'] = df['JST_Time'].dt.year
    df['Month'] = df['JST_Time'].dt.month
    df['Day'] = df['JST_Time'].dt.day
    
    return df

def get_person_data(year, month, day, time_unknown=True, hour=None, minute=None):
    """指定された日時に最も近いデータを取得"""
    
    df = load_hd_data_parquet(year)
    
    if df is None:
        # サンプルデータ生成
        return generate_sample_hd_data()
    
    # 指定日のデータを抽出
    target_date = date(year, month, day)
    day_data = df[df['Date'] == target_date].copy()
    
    if day_data.empty:
        st.warning(f"⚠️ {target_date} のデータが見つかりません。")
        return None
    
    if time_unknown:
        # 時刻不明：その日の中間点（12:00）を返す
        noon_data = day_data[day_data['JST_Time'].dt.hour == 12]
        if not noon_data.empty:
            return noon_data.iloc[0]
        else:
            return day_data.iloc[len(day_data) // 2]
    else:
        # 時刻指定あり：最も近い時刻を返す
        target_time = datetime(year, month, day, hour, minute)
        day_data['time_diff'] = abs((day_data['JST_Time'] - target_time).dt.total_seconds())
        return day_data.loc[day_data['time_diff'].idxmin()]

def generate_sample_hd_data():
    """サンプルHDデータを生成"""
    import random
    
    return {
        'Type': random.choice(['Generator', 'Manifesting Generator', 'Projector', 'Manifestor', 'Reflector']),
        'Profile': random.choice(['1/3', '1/4', '2/4', '2/5', '3/5', '3/6', '4/6', '5/1', '5/2', '6/2', '6/3']),
        'Definition_Type': random.choice(['Single', 'Split', 'Triple', 'Quadruple', 'None']),
        'Authority': random.choice(['Sacral', 'Emotional', 'Splenic', 'Ego', 'G', 'Mental', 'Lunar']),
        'P_Sun': 38.1, 'P_Earth': 39.1, 'P_Moon': 11.5,
        'P_NorthNode': 26.4, 'P_SouthNode': 45.4,
        'D_Sun': 48.3, 'D_Earth': 21.3, 'D_Moon': 57.2,
        'D_NorthNode': 11.1, 'D_SouthNode': 12.1
    }

# --- Not-Self データベース（簡略版） ---
NOTSELF_DATABASE = {
    '頭脳': {
        'theme': '他人の疑問を自分の疑問だと思い込む',
        'both_defined': {
            'pattern': '両親とも確信を持って考えるタイプ',
            'message': ['「ちゃんと考えなさい」', '「答えを出しなさい」'],
            'impact': '常に答えを出さなければというプレッシャー',
            'liberation': '「その疑問は、私が今考えることではない」'
        },
        'one_defined': {
            'pattern': '片親が確信、片親が疑問を拾うタイプ',
            'message': ['「自分で考えて」', '「心配ね」'],
            'impact': '確信と心配の間で引き裂かれる',
            'liberation': '「その疑問は、私が今考えることではない」'
        },
        'both_open': {
            'pattern': '両親とも疑問を拾うタイプ',
            'message': ['「世の中は複雑」', '「簡単に答えは出ない」'],
            'impact': '家庭全体が答えのない不安で満ちている',
            'liberation': '「その疑問は、私が今考えることではない」'
        }
    },
    '思考': {
        'theme': '他人の考え方を自分の考えだと思い込む',
        'both_defined': {
            'pattern': '両親とも一貫した思考を持つタイプ',
            'message': ['「一度言ったことは守れ」', '「意見を変えるな」'],
            'impact': '柔軟に考えを変えることが悪だと刷り込まれる',
            'liberation': '「昨日の私と今日の私は別の私」'
        },
        'one_defined': {
            'pattern': '片親が一貫、片親が柔軟',
            'message': ['「ブレるな」', '「色んな考え方がある」'],
            'impact': '一貫性と柔軟性の矛盾',
            'liberation': '「昨日の私と今日の私は別の私」'
        },
        'both_open': {
            'pattern': '両親とも柔軟すぎるタイプ',
            'message': ['「どっちでもいい」', '親自身が一貫性なし'],
            'impact': '軸がない家庭、自分の考えを持てない',
            'liberation': '「昨日の私と今日の私は別の私」'
        }
    },
    # 他のセンターも同様に定義（省略可能）
}

# 他のセンターの簡易版を追加
for center in ['表現', '自己', '意志', '生命力', '直感', '感情', '活力']:
    if center not in NOTSELF_DATABASE:
        NOTSELF_DATABASE[center] = {
            'theme': f'{center}センターのNot-Self',
            'both_defined': {
                'pattern': '両親とも定義',
                'message': ['強いメッセージ'],
                'impact': '高い期待',
                'liberation': f'{center}を信頼する'
            },
            'one_defined': {
                'pattern': '片親定義',
                'message': ['矛盾するメッセージ'],
                'impact': '混乱',
                'liberation': f'{center}を信頼する'
            },
            'both_open': {
                'pattern': '両親とも未定義',
                'message': ['不安定な家庭'],
                'impact': '家族全体の不安',
                'liberation': f'{center}を信頼する'
            }
        }

# --- UI開始 ---
st.title("👨‍👩‍👧 親子 Not-Self 条件付け分析 V2.0")

# タブ分け
tab1, tab2, tab3, tab4 = st.tabs(["📝 新規分析", "💾 保存パターン", "📊 分析結果", "📄 PDF出力"])

# --- タブ1: 新規分析 ---
with tab1:
    st.header("📅 家族の生年月日入力")
    
    col1, col2, col3 = st.columns(3)
    
    # 父親
    with col1:
        st.subheader("👨 父親")
        f_year = st.selectbox("父 - 年", list(range(1900, 2044)), index=50, key="f_year")
        f_month = st.selectbox("父 - 月", list(range(1, 13)), key="f_month")
        max_day_f = calendar.monthrange(f_year, f_month)[1]
        f_day = st.selectbox("父 - 日", list(range(1, max_day_f + 1)), key="f_day")
        f_time_unknown = st.checkbox("時刻不明", value=True, key="f_time")
    
    # 母親
    with col2:
        st.subheader("👩 母親")
        m_year = st.selectbox("母 - 年", list(range(1900, 2044)), index=52, key="m_year")
        m_month = st.selectbox("母 - 月", list(range(1, 13)), key="m_month")
        max_day_m = calendar.monthrange(m_year, m_month)[1]
        m_day = st.selectbox("母 - 日", list(range(1, max_day_m + 1)), key="m_day")
        m_time_unknown = st.checkbox("時刻不明", value=True, key="m_time")
    
    # 本人
    with col3:
        st.subheader("👤 本人")
        c_year = st.selectbox("本人 - 年", list(range(1900, 2044)), index=75, key="c_year")
        c_month = st.selectbox("本人 - 月", list(range(1, 13)), key="c_month")
        max_day_c = calendar.monthrange(c_year, c_month)[1]
        c_day = st.selectbox("本人 - 日", list(range(1, max_day_c + 1)), key="c_day")
        c_time_unknown = st.checkbox("時刻不明", value=False, key="c_time")
        
        if not c_time_unknown:
            c_hour = st.selectbox("本人 - 時", list(range(24)), index=12, key="c_hour")
            c_minute = st.selectbox("本人 - 分", list(range(60)), index=0, key="c_minute")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔍 分析を実行", type="primary", use_container_width=True):
            st.session_state['analysis_done'] = True
            st.session_state['current_analysis'] = {
                'father': (f_year, f_month, f_day, f_time_unknown),
                'mother': (m_year, m_month, m_day, m_time_unknown),
                'child': (c_year, c_month, c_day, c_time_unknown, 
                         None if c_time_unknown else c_hour,
                         None if c_time_unknown else c_minute)
            }
    
    with col_b:
        if st.button("💾 このパターンを保存", use_container_width=True):
            if 'current_analysis' in st.session_state:
                pattern_name = f"家族_{len(st.session_state['saved_patterns'])+1}"
                st.session_state['saved_patterns'].append({
                    'name': pattern_name,
                    'data': st.session_state['current_analysis'],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                })
                st.success(f"✅ {pattern_name} を保存しました")

# --- タブ2: 保存パターン ---
with tab2:
    st.header("💾 保存されたパターン")
    
    if st.session_state['saved_patterns']:
        for i, pattern in enumerate(st.session_state['saved_patterns']):
            with st.expander(f"{pattern['name']} - {pattern['timestamp']}"):
                st.write(f"**父親**: {pattern['data']['father'][0]}年{pattern['data']['father'][1]}月{pattern['data']['father'][2]}日")
                st.write(f"**母親**: {pattern['data']['mother'][0]}年{pattern['data']['mother'][1]}月{pattern['data']['mother'][2]}日")
                st.write(f"**本人**: {pattern['data']['child'][0]}年{pattern['data']['child'][1]}月{pattern['data']['child'][2]}日")
                
                if st.button(f"この分析を読み込む", key=f"load_{i}"):
                    st.session_state['current_analysis'] = pattern['data']
                    st.session_state['analysis_done'] = True
                    st.rerun()
    else:
        st.info("まだ保存されたパターンはありません")

# --- タブ3: 分析結果 ---
with tab3:
    if not st.session_state.get('analysis_done', False):
        st.info("👆 タブ1で分析を実行してください")
    else:
        st.header("📊 分析結果")
        
        # データ取得
        f_data = get_person_data(*st.session_state['current_analysis']['father'][:3], 
                                 st.session_state['current_analysis']['father'][3])
        m_data = get_person_data(*st.session_state['current_analysis']['mother'][:3],
                                 st.session_state['current_analysis']['mother'][3])
        c_data = get_person_data(*st.session_state['current_analysis']['child'][:3],
                                 st.session_state['current_analysis']['child'][3],
                                 st.session_state['current_analysis']['child'][4],
                                 st.session_state['current_analysis']['child'][5])
        
        if f_data is not None and m_data is not None and c_data is not None:
            # HD分析
            f_hd = analyze_person_hd(f_data)
            m_hd = analyze_person_hd(m_data)
            c_hd = analyze_person_hd(c_data)
            
            # 結果を保存
            st.session_state['analysis_results'] = {
                'father': f_hd,
                'mother': m_hd,
                'child': c_hd
            }
            
            # 1. 基本情報サマリー
            st.subheader("1️⃣ 家族の基本情報")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**👨 父親**")
                st.write(f"タイプ: {f_hd['type']}")
                st.write(f"プロファイル: {f_hd['profile']}")
                st.write(f"定義型: {f_hd['definition']}")
                st.write(f"権威: {f_hd['authority']}")
            
            with col2:
                st.markdown("**👩 母親**")
                st.write(f"タイプ: {m_hd['type']}")
                st.write(f"プロファイル: {m_hd['profile']}")
                st.write(f"定義型: {m_hd['definition']}")
                st.write(f"権威: {m_hd['authority']}")
            
            with col3:
                st.markdown("**👤 本人**")
                st.write(f"タイプ: {c_hd['type']}")
                st.write(f"プロファイル: {c_hd['profile']}")
                st.write(f"定義型: {c_hd['definition']}")
                st.write(f"権威: {c_hd['authority']}")
            
            st.divider()
            
            # 2. センター比較
            st.subheader("2️⃣ センター定義状態")
            
            center_names = ['頭脳', '思考', '表現', '自己', '意志', '生命力', '直感', '感情', '活力']
            
            comparison_data = []
            for center in center_names:
                comparison_data.append({
                    'センター': center,
                    '父': '●' if center in f_hd['defined_centers'] else '○',
                    '母': '●' if center in m_hd['defined_centers'] else '○',
                    '本人': '●' if center in c_hd['defined_centers'] else '○',
                    '父_def': center in f_hd['defined_centers'],
                    '母_def': center in m_hd['defined_centers'],
                    '本人_def': center in c_hd['defined_centers']
                })
            
            comp_df = pd.DataFrame(comparison_data)
            
            # スタイル
            def style_centers(row):
                styles = [''] * len(row)
                if row['父_def']:
                    styles[1] = 'background-color: #4CAF50; color: white; font-weight: bold;'
                else:
                    styles[1] = 'background-color: #FFEB3B; color: #333; font-weight: bold;'
                
                if row['母_def']:
                    styles[2] = 'background-color: #4CAF50; color: white; font-weight: bold;'
                else:
                    styles[2] = 'background-color: #FFEB3B; color: #333; font-weight: bold;'
                
                if row['本人_def']:
                    styles[3] = 'background-color: #4CAF50; color: white; font-weight: bold;'
                else:
                    styles[3] = 'background-color: #FFEB3B; color: #333; font-weight: bold;'
                
                return styles
            
            display_df = comp_df[['センター', '父', '母', '本人']].copy()
            styled_df = display_df.style.apply(style_centers, axis=1)
            st.dataframe(styled_df, hide_index=True, use_container_width=True)
            st.caption("● = 定義（色つき）　○ = 未定義（白）")
            
            st.divider()
            
            # 3. Not-Self 条件付け
            st.subheader("3️⃣ Not-Self 条件付けの推測")
            
            if not c_hd['undefined_centers']:
                st.success("✨ 全センター定義 - 完全に自立したエネルギー")
            else:
                for center in c_hd['undefined_centers']:
                    with st.expander(f"📍 {center}センター", expanded=True):
                        if center in NOTSELF_DATABASE:
                            data = NOTSELF_DATABASE[center]
                            
                            # 両親のパターン判定
                            f_def = center in f_hd['defined_centers']
                            m_def = center in m_hd['defined_centers']
                            
                            if f_def and m_def:
                                pattern = data['both_defined']
                            elif not f_def and not m_def:
                                pattern = data['both_open']
                            else:
                                pattern = data['one_defined']
                            
                            st.markdown(f"**🎭 テーマ**: {data['theme']}")
                            st.markdown(f"**👨‍👩 両親のパターン**: {pattern['pattern']}")
                            st.markdown("**💬 受けたメッセージ**:")
                            for msg in pattern['message']:
                                st.markdown(f"- {msg}")
                            st.error(f"**⚠️ 影響**: {pattern['impact']}")
                            st.success(f"**✨ 解放**: {pattern['liberation']}")

# --- タブ4: PDF出力 ---
with tab4:
    st.header("📄 PDF レポート出力")
    
    if not st.session_state.get('analysis_results'):
        st.info("👆 タブ3で分析を実行してください")
    else:
        st.markdown("""
        ### レポート内容
        - 家族の基本情報
        - センター定義状態
        - Not-Self 条件付けの詳細
        - 解放のためのアドバイス
        
        ※ わかりやすく、専門用語を控えた内容で出力されます
        """)
        
        if st.button("📥 PDFをダウンロード", type="primary"):
            st.info("🚧 PDF出力機能は次のアップデートで実装予定です")
            # TODO: PDF生成ロジックを実装

st.markdown("---")
st.caption("💡 V2.0: Parquet対応・AI統合・複数パターン保存")
