# =====================================================================
# PDF出力 & AI推論機能モジュール
# =====================================================================

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# 日本語フォント設定（IPAフォントを使用）
# 注: 実際の運用では、フォントファイルのパスを指定する必要があります

def create_pdf_report(analysis_results, family_info):
    """
    わかりやすいPDFレポートを生成
    
    Parameters:
    - analysis_results: 分析結果（父・母・本人のHDデータ）
    - family_info: 家族情報（生年月日など）
    
    Returns:
    - PDFのバイナリデータ
    """
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           topMargin=2*cm, bottomMargin=2*cm,
                           leftMargin=2*cm, rightMargin=2*cm)
    
    story = []
    styles = getSampleStyleSheet()
    
    # カスタムスタイル
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#00BFFF'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14
    )
    
    # タイトル
    story.append(Paragraph("親子の心の仕組み分析レポート", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 日付
    from datetime import datetime
    story.append(Paragraph(f"作成日: {datetime.now().strftime('%Y年%m月%d日')}", body_style))
    story.append(Spacer(1, 1*cm))
    
    # 1. はじめに
    story.append(Paragraph("はじめに", heading_style))
    intro_text = """
    このレポートは、あなたとご両親の「生まれつきの心の仕組み」を分析し、
    幼少期に受けた影響を明らかにするものです。
    
    ここでわかることは、「誰が悪い」ではなく、「なぜそうなったのか」です。
    理解することで、あなたは自由になれます。
    """
    story.append(Paragraph(intro_text, body_style))
    story.append(Spacer(1, 1*cm))
    
    # 2. 家族の基本情報
    story.append(Paragraph("1. ご家族の基本的な性質", heading_style))
    
    father = analysis_results['father']
    mother = analysis_results['mother']
    child = analysis_results['child']
    
    # わかりやすい表現に変換
    def translate_type(t):
        trans = {
            'Generator': '働き続ける人',
            'Manifesting Generator': '同時進行が得意な人',
            'Projector': '全体を見渡す人',
            'Manifestor': '新しく始める人',
            'Reflector': '周りを映す鏡のような人'
        }
        return trans.get(t, t)
    
    def translate_authority(a):
        trans = {
            'Sacral': '体の感覚で決める',
            'Emotional': '時間をかけて決める',
            'Splenic': '一瞬の直感で決める',
            'Ego': '自分の意志で決める',
            'G': '環境の声を聞いて決める',
            'Mental': '人と話して決める',
            'Lunar': '月の周期で決める'
        }
        return trans.get(a, a)
    
    family_data = [
        ['', 'お父さん', 'お母さん', 'あなた'],
        ['基本タイプ', translate_type(father['type']), translate_type(mother['type']), translate_type(child['type'])],
        ['決め方', translate_authority(father['authority']), translate_authority(mother['authority']), translate_authority(child['authority'])]
    ]
    
    family_table = Table(family_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    family_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00BFFF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(family_table)
    story.append(Spacer(1, 1*cm))
    
    # 3. あなたが受けた影響
    story.append(Paragraph("2. あなたが幼少期に受けた影響", heading_style))
    
    if not child['undefined_centers']:
        story.append(Paragraph("""
        あなたは全ての部分が完成した状態で生まれてきました。
        これは非常に珍しいことです。
        
        ご両親や周りの人からの影響を、自分のペースで取り入れることができたでしょう。
        ただし、多くの人は「未完成な部分」を持っているため、
        その人たちの気持ちを理解しにくい面があるかもしれません。
        """, body_style))
    else:
        story.append(Paragraph(f"""
        あなたには「周りの影響を受けやすい部分」が{len(child['undefined_centers'])}箇所あります。
        これらの部分で、ご両親からの影響を強く受けてきました。
        """, body_style))
        
        story.append(Spacer(1, 0.5*cm))
        
        # 各センターの詳細（わかりやすく）
        center_translations = {
            '頭脳': '考え・疑問',
            '思考': '思考の仕方',
            '表現': '話すこと',
            '自己': '自分らしさ',
            '意志': '意志・約束',
            '生命力': 'エネルギー',
            '直感': '直感',
            '感情': '感情',
            '活力': '活力'
        }
        
        for center in child['undefined_centers']:
            story.append(PageBreak())
            
            center_name = center_translations.get(center, center)
            story.append(Paragraph(f"【{center_name}について】", heading_style))
            
            # 両親のパターン判定
            f_def = center in father['defined_centers']
            m_def = center in mother['defined_centers']
            
            if f_def and m_def:
                pattern_desc = "ご両親とも、この部分がしっかりしていました。"
                impact = f"そのため、「{center_name}はこうあるべき」という強いメッセージを受け取ってきたでしょう。"
            elif not f_def and not m_def:
                pattern_desc = "ご両親とも、この部分が柔軟でした。"
                impact = f"そのため、家庭全体がこの部分で不安定で、「{center_name}」について明確な答えがない環境でした。"
            else:
                pattern_desc = "ご両親の片方はしっかり、片方は柔軟でした。"
                impact = f"そのため、{center_name}について、矛盾するメッセージを受け取ってきたでしょう。"
            
            story.append(Paragraph(pattern_desc, body_style))
            story.append(Paragraph(impact, body_style))
            story.append(Spacer(1, 0.5*cm))
            
            # 解放のアドバイス
            liberation_text = f"""
            ✨ これからの生き方のヒント:
            
            あなたの{center_name}は、「周りの影響を受け取るアンテナ」です。
            これは弱さではなく、特別な感度です。
            
            他人の{center_name}を自分のものだと思い込まず、
            「これは誰かから受け取ったものだ」と気づくだけで、
            あなたは自由になれます。
            """
            story.append(Paragraph(liberation_text, body_style))
            story.append(Spacer(1, 0.5*cm))
    
    # PDF生成
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- AI推論機能 ---
async def generate_ai_insight(person_hd, parents_hd=None):
    """
    Claude APIを使用して、個人のHDから深い洞察を生成
    
    Parameters:
    - person_hd: 個人のHD分析結果
    - parents_hd: 両親のHD分析結果（オプション）
    
    Returns:
    - AI生成の洞察テキスト
    """
    
    # プロンプト構築
    prompt = f"""
あなたはヒューマンデザインの専門家です。以下の情報から、この人への深い洞察を3-5文で生成してください。

# 基本情報
- タイプ: {person_hd['type']}
- プロファイル: {person_hd['profile']}
- 定義型: {person_hd['definition']}
- 権威: {person_hd['authority']}

# 定義されたセンター
{', '.join(person_hd['defined_centers'])}

# 未定義センター
{', '.join(person_hd['undefined_centers']) if person_hd['undefined_centers'] else '全センター定義'}

# インカネーションクロス
- 太陽（パーソナリティ）: ゲート{person_hd['incarnation_cross']['P_Sun']}
- 地球（パーソナリティ）: ゲート{person_hd['incarnation_cross']['P_Earth']}
- 太陽（デザイン）: ゲート{person_hd['incarnation_cross']['D_Sun']}
- 地球（デザイン）: ゲート{person_hd['incarnation_cross']['D_Earth']}

# 指示
この人の人生のテーマ、強み、気をつけるべき点を、専門用語を避けて、わかりやすく3-5文で伝えてください。
"""
    
    try:
        # Claude API呼び出し
        import anthropic
        
        client = anthropic.Anthropic()
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    
    except Exception as e:
        # APIが使えない場合はデフォルトメッセージ
        return f"""
        あなたは{person_hd['type']}として、独自の道を歩む人です。
        {person_hd['authority']}で決断することが、あなたにとって最も自然です。
        """

# テスト用
if __name__ == "__main__":
    # サンプルデータでテスト
    sample_hd = {
        'type': 'Generator',
        'profile': '5/1',
        'definition': 'Single',
        'authority': 'Sacral',
        'defined_centers': ['生命力', '自己', '表現'],
        'undefined_centers': ['頭脳', '思考', '意志', '直感', '感情', '活力'],
        'incarnation_cross': {
            'P_Sun': 38,
            'P_Earth': 39,
            'D_Sun': 48,
            'D_Earth': 21
        }
    }
    
    family_info = {
        'father': '1950年1月1日',
        'mother': '1952年1月1日',
        'child': '1980年1月1日'
    }
    
    analysis = {
        'father': sample_hd,
        'mother': sample_hd,
        'child': sample_hd
    }
    
    pdf_buffer = create_pdf_report(analysis, family_info)
    
    with open('/home/claude/test_report.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print("✅ テストPDF生成完了: /home/claude/test_report.pdf")
