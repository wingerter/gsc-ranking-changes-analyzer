import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import re
from collections import Counter

st.set_page_config(
    page_title="GSC Ranking Changes Analyzer",
    page_icon="assets/logo-head-clear.png",
    layout="wide"
)

# --- Load Brand Styles ---
try:
    with open("brand_style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Konnte brand_style.css nicht laden: {e}")

# --- i18n Language Setup ---
st.sidebar.image("assets/logo-horizontal.png", use_container_width=True)
st.sidebar.markdown("### Language / Sprache")
lang_choice = st.sidebar.radio("Select Language", options=["EN", "DE"], label_visibility="collapsed")
lang = "EN" if "EN" in lang_choice else "DE"

translations = {
    "EN": {
        "title": "GSC Ranking Changes Analyzer",
        "subtitle": "Upload your Google Search Console comparison export (Queries.csv) and analyze real click losses and quick wins.",
        "sidebar_data": "1. Data & Settings",
        "upload_label": "GSC Queries.csv Upload",
        "cluster_settings": "Clustering Settings",
        "brand_input": "Brand Keywords (comma-separated)",
        "brand_help": "Keywords containing these terms will be grouped into a separate 'Brand' cluster.",
        "cluster_count": "Number of Topic Clusters",
        "btn_analyze": "Analyze",
        "err_format": "Could not recognize the GSC format. Please upload a standard Queries.csv from a GSC date comparison (exactly 9 columns expected).",
        "err_read": "Error reading CSV: ",
        "succ_load": "GSC file successfully loaded and columns recognized!",
        "info_upload": "Please upload a GSC Queries.csv file and click 'Analyze'.",
        
        "kpi_header": "Overview: Real GSC Clicks",
        "kpi_lost_total": "Lost Clicks (Total)",
        "kpi_top10_drops": "Top 10 Drops",
        "kpi_gained_total": "Gained Clicks (Total)",
        "kpi_net_change": "Net Click Change",
        "clicks": "Clicks",
        
        "tab_cluster": "Topic Clusters",
        "tab_drops": "Ranking Drops",
        "tab_losses": "Click Losses (Detail)",
        "tab_lhf": "Low Hanging Fruits",
        "tab_winners": "Winners",
        
        "cl_sub": "Click Loss by Topic Clusters",
        "cl_desc": "Automatic grouping of losing keywords by their most frequent terms (head terms).",
        "cl_chart_title": "Which topic clusters lost the most clicks?",
        "cl_chart_label_c": "Topic Cluster",
        "cl_chart_label_v": "Lost Clicks",
        "cl_detail": "#### Detail Data per Cluster",
        "cl_select": "Select one or more clusters for detail insights:",
        "cl_sum": "Total lost clicks in selected clusters:",
        "cl_empty": "No click losses found.",
        "cl_other": "Other",
        
        "rd_sub": "Ranking Drops Overview",
        "rd_filter": "Filter by keyword (optional):",
        "rd_t3_title": "#### 1. Top 3 Drops (Fell out of Top 3)",
        "rd_t3_empty": "No Top 3 Drops found.",
        "rd_t10_title": "#### 2. Top 10 Drops (Fell out of Top 10)",
        "rd_t10_empty": "No Top 10 Drops found.",
        "rd_p2_title": "#### 3. Page 2 Drops (Dropped from Page 2 further back)",
        "rd_p2_empty": "No Page 2 Drops found.",
        "rd_100_title": "#### 4. Complete Losses (Fell out of Top 100)",
        "rd_100_empty": "No keywords fell out of Top 100.",
        "rd_sum": "Total lost clicks:",
        
        "cd_sub": "Biggest absolute click losses (All)",
        
        "lhf_sub": "Low Hanging Fruits (Position 11 - 15)",
        "lhf_desc": "These keywords currently rank on the top half of page 2 (Position 11-15) and already generate the real impressions shown above. With tiny on-page optimizations, you can push these over the threshold to page 1 and turn those impressions into massive traffic.",
        "lhf_empty": "No keywords found in range 11-15.",
        
        "win_sub": "Winners (Click Gains)",
        "win_empty": "No click winners found.",
        "win_chart_title": "Winner Keywords",
        "win_chart_label_pos": "New Position",
        "win_chart_label_gain": "Gained Clicks",
        "tab_all": "All Data",
        "ad_sub": "All Data (Complete Export)",
        "ad_filter_cluster": "Filter by Cluster",
        "ad_filter_change": "Filter by Change Type",
        "ad_filter_kw": "Search Keyword",
        "kpi_cluster_title": "Topic Cluster Performance",
        "kpi_best_cluster": "Best Cluster",
        "kpi_worst_cluster": "Worst Cluster",
        "kpi_top3_drops": "Top 3 Drops",
        "kpi_lhf": "Low Hanging Fruits",
        "kpi_lhf_link": "See tab below",
        "kpi_lhf_help": "Actual impressions generated in the current timeframe by keywords ranking on positions 11-15. High impressions here mean great potential if pushed to page 1.",
        "kpi_top3_title": "Top 3 Drops (Worst 5)",
        "footer": "MIT License &copy; 2026 Benjamin &quot;SEOux Indianer&quot; Wingerter | Created in Munich & Bangkok with ❤️ | <a href='https://seouxindianer.de' target='_blank' style='color: #2ea3f2; text-decoration: underline;'>seouxindianer.de</a>",
    },
    "DE": {
        "title": "GSC Ranking Changes Analyzer",
        "subtitle": "Laden Sie Ihren Google Search Console Vergleichsexport (Queries.csv) hoch und analysieren Sie reale Klick-Verluste und Quick-Wins.",
        "sidebar_data": "1. Daten & Einstellungen",
        "upload_label": "GSC Queries.csv Upload",
        "cluster_settings": "Clustering-Einstellungen",
        "brand_input": "Brand-Keywords (kommagetrennt)",
        "brand_help": "Keywords, die diese Begriffe enthalten, werden in einem eigenen 'Brand' Cluster gesammelt.",
        "cluster_count": "Anzahl der Themen-Cluster",
        "btn_analyze": "Analysieren",
        "err_format": "Das GSC-Format konnte nicht erkannt werden. Bitte laden Sie eine standardmäßige Queries.csv aus einem GSC-Zeitraumvergleich hoch (genau 9 Spalten erwartet).",
        "err_read": "Fehler beim Lesen der CSV: ",
        "succ_load": "GSC-Datei erfolgreich geladen und Spalten erkannt!",
        "info_upload": "Bitte laden Sie eine GSC Queries.csv Datei hoch und klicken Sie auf 'Analysieren'.",
        
        "kpi_header": "Überblick: Echte GSC-Klicks",
        "kpi_lost_total": "Verlorene Klicks (Gesamt)",
        "kpi_top10_drops": "Top 10 Abstürze",
        "kpi_gained_total": "Gewonnene Klicks (Gesamt)",
        "kpi_net_change": "Netto Klick-Veränderung",
        "clicks": "Klicks",
        
        "tab_cluster": "Themen-Cluster",
        "tab_drops": "Ranking Drops",
        "tab_losses": "Klick-Verluste (Detail)",
        "tab_lhf": "Low Hanging Fruits",
        "tab_winners": "Gewinner",
        
        "cl_sub": "Klick-Verlust nach Themen-Clustern",
        "cl_desc": "Automatische Bündelung der Verlierer-Keywords nach den häufigsten Begriffen (Head-Terms).",
        "cl_chart_title": "Welche Themen-Cluster haben am meisten Klicks verloren?",
        "cl_chart_label_c": "Themen-Cluster",
        "cl_chart_label_v": "Verlorene Klicks",
        "cl_detail": "#### Detail-Daten pro Cluster",
        "cl_select": "Wählen Sie ein oder mehrere Cluster für Detail-Insights:",
        "cl_sum": "Gesamte verlorene Klicks in den gewählten Clustern:",
        "cl_empty": "Keine Klick-Verluste vorhanden.",
        "cl_other": "Sonstiges",
        
        "rd_sub": "Ranking Drops Übersicht",
        "rd_filter": "Nach Keyword filtern (optional):",
        "rd_t3_title": "#### 1. Top 3 Drops (Aus Top 3 gerutscht)",
        "rd_t3_empty": "Keine Top 3 Drops gefunden.",
        "rd_t10_title": "#### 2. Top 10 Drops (Aus Top 10 gerutscht)",
        "rd_t10_empty": "Keine Top 10 Drops gefunden.",
        "rd_p2_title": "#### 3. Seite 2 Drops (Von Seite 2 weiter nach hinten)",
        "rd_p2_empty": "Keine Seite 2 Drops gefunden.",
        "rd_100_title": "#### 4. Komplette Verluste (Aus Top 100 gefallen)",
        "rd_100_empty": "Keine Keywords aus den Top 100 gefallen.",
        "rd_sum": "Verlorene Klicks gesamt:",
        
        "cd_sub": "Größte absolute Klick-Verluste (Alle)",
        
        "lhf_sub": "Low Hanging Fruits (Position 11 - 15)",
        "lhf_desc": "Diese sogenannten **Schwellen-Keywords** ranken aktuell auf der oberen Hälfte von Seite 2 (Position 11-15) und generieren dort bereits die gezeigten, echten Impressionen. Das bedeutet: Das Suchvolumen ist vorhanden. Mit geringen On-Page-Optimierungen können Sie diese Keywords über die Schwelle auf Seite 1 schieben und die Impressionen in signifikanten Traffic verwandeln.",
        "lhf_empty": "Keine Keywords im Bereich 11-15 gefunden.",
        
        "win_sub": "Gewinner (Klick-Zuwachs)",
        "win_empty": "Keine Klick-Gewinner gefunden.",
        "win_chart_title": "Gewinner-Keywords",
        "win_chart_label_pos": "Neue Position",
        "win_chart_label_gain": "Gewonnene Klicks",
        "tab_all": "Alle Daten",
        "ad_sub": "Alle Daten (Gesamter Export)",
        "ad_filter_cluster": "Nach Cluster filtern",
        "ad_filter_change": "Nach Change-Typ filtern",
        "ad_filter_kw": "Keyword suchen",
        "kpi_cluster_title": "Themen-Cluster Performance",
        "kpi_best_cluster": "Bestes Cluster",
        "kpi_worst_cluster": "Schlechtestes Cluster",
        "kpi_top3_drops": "Top 3 Abstürze",
        "kpi_lhf": "Low Hanging Fruits",
        "kpi_lhf_link": "Siehe Reiter unten",
        "kpi_lhf_help": "Echte Impressionen, die diese Keywords im aktuellen Zeitraum auf den Positionen 11-15 gesammelt haben. Viele Impressionen hier bedeuten hohes Potenzial für Seite 1.",
        "kpi_top3_title": "Top 3 Abstürze (Die 5 schlimmsten)",
        "footer": "MIT License &copy; 2026 Benjamin &quot;SEOux Indianer&quot; Wingerter | Erstellt in München & Bangkok mit ❤️ | <a href='https://seouxindianer.de' target='_blank' style='color: #2ea3f2; text-decoration: underline;'>seouxindianer.de</a>",
    }
}

t = translations[lang]

# Helper to format numbers based on selected language (DE: 1.234.567,89 / EN: 1,234,567.89)
def format_num(val, decimal_places=0):
    if pd.isnull(val):
        return ""
    formatted_str = f"{val:,.{decimal_places}f}"
    if lang == "DE":
        placeholder = "|||"
        temp = formatted_str.replace(",", placeholder)
        temp = temp.replace(".", ",")
        formatted_str = temp.replace(placeholder, ".")
    return formatted_str

# Helper to style Plotly figures according to Corporate Design
def style_plotly_fig(fig):
    title_text = ""
    if fig.layout.title is not None:
        if isinstance(fig.layout.title, str):
            title_text = fig.layout.title
        elif hasattr(fig.layout.title, 'text') and fig.layout.title.text is not None:
            title_text = fig.layout.title.text

    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font_family="Raleway",
        font_color="#232323",
        margin=dict(l=60, r=40, t=45, b=45),  # Safe default margins to avoid clipping
        title=dict(
            text=title_text,
            font=dict(family="Raleway", color="#232323", size=15)
        ),
        xaxis=dict(
            title=dict(text=""),  # Suppress default x-axis title to avoid "undefined" text
            gridcolor="#dfdfdf",
            zerolinecolor="#dfdfdf",
            linecolor="#dfdfdf",
            tickfont=dict(family="Open Sans", color="#535353")
        ),
        yaxis=dict(
            title=dict(text=""),  # Suppress default y-axis title to avoid "undefined" text
            gridcolor="#dfdfdf",
            zerolinecolor="#dfdfdf",
            linecolor="#dfdfdf",
            tickfont=dict(family="Open Sans", color="#535353")
        )
    )
    return fig

st.title(t["title"])
st.markdown(t["subtitle"])

# Sidebar - Settings
st.sidebar.header(t["sidebar_data"])
uploaded_file = st.sidebar.file_uploader(t["upload_label"], type=["csv"])

st.sidebar.subheader(t["cluster_settings"])
brand_input = st.sidebar.text_input(t["brand_input"], value="", help=t["brand_help"])
num_clusters = st.sidebar.slider(t["cluster_count"], min_value=5, max_value=50, value=20, step=5)

if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False

if uploaded_file is not None:
    if st.sidebar.button(t["btn_analyze"], type="primary"):
        st.session_state['analyzed'] = True

if uploaded_file is not None and st.session_state['analyzed']:
    try:
        content = uploaded_file.getvalue()
        df = None
        
        for enc in ['utf-8', 'utf-16', 'latin1', 'utf-8-sig']:
            for sep in [',', ';', '\t']:
                try:
                    temp_df = pd.read_csv(io.BytesIO(content), encoding=enc, sep=sep)
                    if len(temp_df.columns) == 9:
                        df = temp_df
                        break
                except Exception:
                    continue
            if df is not None:
                break
                
        if df is None:
            raise Exception(t["err_format"])
            
        df.columns = [
            "Keyword",
            "Clicks_New", "Clicks_Old",
            "Impressions_New", "Impressions_Old",
            "CTR_New", "CTR_Old",
            "Position_New", "Position_Old"
        ]
             
    except Exception as e:
        st.error(f"{t['err_read']}{e}")
        st.stop()
        
    st.success(t["succ_load"])
    
    # --- Data Cleaning ---
    df = df.dropna(subset=['Keyword'])
    df = df[df['Keyword'].astype(str).str.strip() != ""]
    
    for col in df.columns[1:]:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace('%', '', regex=False).str.replace(',', '.', regex=False)
            df[col] = df[col].str.extract(r'([0-9.]+)')[0]
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['Position_New'] = df['Position_New'].replace(0, 101)
    df['Position_Old'] = df['Position_Old'].replace(0, 101)

    # --- Advanced Analytics Logic ---
    df['Clicks Loss'] = df['Clicks_Old'] - df['Clicks_New']
    df['Clicks Gain'] = df['Clicks_New'] - df['Clicks_Old']
    df['Impressions Loss'] = df['Impressions_Old'] - df['Impressions_New']
    df['Position Change'] = df['Position_Old'] - df['Position_New']
    
    df['Clicks Change'] = df['Clicks_New'] - df['Clicks_Old']
    def get_change_type(row):
        po = row['Position_Old']
        pn = row['Position_New']
        if po == 101 and pn != 101: return "New"
        elif po <= 3 and pn > 3: return "OoTop3"
        elif po <= 10 and pn > 10: return "OoTop10"
        elif 10 < po <= 20 and pn > 20: return "OoSERP2"
        elif po <= 100 and pn > 100: return "OoTop100"
        elif po > 10 and pn <= 10: return "IntoTop10"
        elif abs(po - pn) < 1.0: return "None"
        else: return "Changed"
    df['Change'] = df.apply(get_change_type, axis=1)
    
    # --- Clustering Logic ---
    stopwords_de = set([
        "und", "oder", "kaufen", "test", "erfahrung", "erfahrungen", "günstig", "online", "shop", 
        "mit", "für", "von", "in", "der", "die", "das", "den", "dem", "des", "ein", "eine", "einer", 
        "eines", "auf", "im", "am", "zu", "ist", "sind", "wie", "was", "wo", "wer", "warum", "als", "an",
        "bei", "aus", "nach", "um", "bis", "über", "unter", "vor", "zwischen", "aber", "nur", "auch",
        "dass", "dann", "wenn", "so", "sich", "nicht", "noch", "mehr", "durch", "zum", "zur"
    ])
    
    stopwords_en = set([
        "and", "or", "buy", "test", "experience", "cheap", "online", "shop", "with", "for", "of", "in",
        "the", "a", "an", "on", "at", "to", "is", "are", "how", "what", "where", "who", "why", "as",
        "from", "after", "about", "under", "before", "between", "but", "only", "also", "that", "then",
        "if", "so", "not", "more", "by"
    ])
    
    stopwords = stopwords_en if lang == "EN" else stopwords_de
    
    brand_terms = [b.strip().lower() for b in brand_input.split(',')] if brand_input.strip() else []
    
    def get_cluster(kw):
        kw_lower = str(kw).lower()
        for b in brand_terms:
            if b and b in kw_lower:
                return "Brand"
        return None

    temp_losers = df[df['Clicks Loss'] > 0]
    temp_cluster = temp_losers['Keyword'].apply(get_cluster)
    non_brand_kws = temp_losers[temp_cluster.isnull()]['Keyword'].dropna().tolist()
    
    word_counts = Counter()
    for kw in non_brand_kws:
        words = re.findall(r'\b\w+\b', str(kw).lower())
        for w in words:
            if w not in stopwords and len(w) > 2 and not w.isnumeric():
                word_counts[w] += 1
                
    top_head_terms = [word for word, count in word_counts.most_common(num_clusters)]
    
    def assign_head_term(kw):
        kw_lower = str(kw).lower()
        for term in top_head_terms:
            if re.search(rf'\b{re.escape(term)}\b', kw_lower):
                return term.capitalize()
        return "undefined"
        
    df['Cluster'] = df['Keyword'].apply(get_cluster)
    df.loc[df['Cluster'].isnull(), 'Cluster'] = df[df['Cluster'].isnull()]['Keyword'].apply(assign_head_term)

    st.markdown("<hr class='hr--grey'>", unsafe_allow_html=True)
    
    # Segments
    losers = df[df['Clicks Loss'] > 0].copy()
    top3_drops = df[(df['Position_Old'] <= 3) & (df['Position_New'] > 3) & (df['Clicks Loss'] > 0)]
    top10_drops = df[(df['Position_Old'] <= 10) & (df['Position_New'] > 10) & (df['Clicks Loss'] > 0)]
    page2_drops = df[(df['Position_Old'] > 10) & (df['Position_Old'] <= 20) & (df['Position_New'] > 20) & (df['Clicks Loss'] > 0)]
    total_loss = df[(df['Position_Old'] <= 100) & (df['Position_New'] > 100) & (df['Clicks Loss'] > 0)]
    low_hanging = df[(df['Position_New'] >= 11) & (df['Position_New'] <= 15)]
    winners = df[df['Clicks Gain'] > 0].copy()
    
    # --- KPIs ---
    st.header(t["kpi_header"])
    
    total_clicks_lost = int(losers['Clicks Loss'].sum())
    total_clicks_gained = int(winners['Clicks Gain'].sum())
    net_clicks = total_clicks_gained - total_clicks_lost
    lhf_impressions = int(low_hanging['Impressions_New'].sum())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t["kpi_lost_total"], f"-{format_num(total_clicks_lost)}")
    with col2:
        st.metric(t["kpi_net_change"], f"+{format_num(net_clicks)}" if net_clicks > 0 else format_num(net_clicks), delta=net_clicks)
    with col3:
        st.metric(t["kpi_gained_total"], f"+{format_num(total_clicks_gained)}")
        
    st.write("")
    
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(t["kpi_top3_drops"], len(top3_drops), delta=f"-{format_num(int(top3_drops['Clicks Loss'].sum()))} {t['clicks']}", delta_color="normal")
    with col5:
        st.metric(t["kpi_top10_drops"], len(top10_drops), delta=f"-{format_num(int(top10_drops['Clicks Loss'].sum()))} {t['clicks']}", delta_color="normal")
    with col6:
        st.metric(t["kpi_lhf"], len(low_hanging), delta=f"{format_num(lhf_impressions)} Imp.", delta_color="off", help=t["kpi_lhf_help"])
        st.markdown(f"<div style='font-size: 14px; color: gray;'>{t.get('kpi_lhf_link', 'Siehe Reiter unten')}</div>", unsafe_allow_html=True)
        
    st.markdown("<hr class='hr--grey'>", unsafe_allow_html=True)
    
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        st.markdown("#### " + t["kpi_cluster_title"])
        cluster_net = df.groupby('Cluster')['Clicks Change'].sum().reset_index()
        cluster_net = cluster_net[cluster_net['Cluster'] != "undefined"]
        
        if not cluster_net.empty:
            best_cluster = cluster_net.loc[cluster_net['Clicks Change'].idxmax()]
            worst_cluster = cluster_net.loc[cluster_net['Clicks Change'].idxmin()]
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric(t["kpi_best_cluster"], best_cluster['Cluster'], f"{format_num(best_cluster['Clicks Change'])} {t['clicks']}")
            with c2:
                st.metric(t["kpi_worst_cluster"], worst_cluster['Cluster'], f"{format_num(worst_cluster['Clicks Change'])} {t['clicks']}")
                
            top_bottom = pd.concat([cluster_net.nlargest(3, 'Clicks Change'), cluster_net.nsmallest(3, 'Clicks Change')]).drop_duplicates()
            top_bottom = top_bottom.sort_values('Clicks Change')
            fig_net = px.bar(
                top_bottom, x='Clicks Change', y='Cluster', orientation='h',
                color='Clicks Change', color_continuous_scale=[[0.0, '#d28063'], [0.5, '#ffed00'], [1.0, '#90c274']],
                height=200
            )
            style_plotly_fig(fig_net)
            fig_net.update_layout(margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(fig_net, use_container_width=True)

    with viz_col2:
        st.markdown("#### " + t.get("kpi_top3_title", "Top 3 Drops (Worst 5)"))
        if not top3_drops.empty:
            worst_top3 = top3_drops.nlargest(5, 'Clicks Loss').sort_values('Clicks Loss', ascending=True)
            fig_t3 = px.bar(
                worst_top3, x='Clicks Loss', y='Keyword', orientation='h',
                color_discrete_sequence=['#d28063'], height=270
            )
            style_plotly_fig(fig_t3)
            fig_t3.update_layout(margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(fig_t3, use_container_width=True)
        else:
            st.info(t["rd_t3_empty"])
            
    st.markdown("<hr class='hr--grey'>", unsafe_allow_html=True)

    def display_styled_dataframe(df_to_show, sort_col, ascending=False):
        loss_cols = [c for c in ['Clicks Loss'] if c in df_to_show.columns]
        gain_cols = [c for c in ['Clicks Gain'] if c in df_to_show.columns]
        
        styler = df_to_show.sort_values(sort_col, ascending=ascending).style
        format_dict = {}
        
        if loss_cols:
            styler = styler.map(lambda x: 'color: #d28063; font-weight: bold;' if pd.notnull(x) and x > 0 else '', subset=loss_cols)
            for c in loss_cols:
                format_dict[c] = lambda x: f"▼ -{format_num(x)}" if pd.notnull(x) and x > 0 else ("0" if pd.notnull(x) else "")
                
        if gain_cols:
            styler = styler.map(lambda x: 'color: #90c274; font-weight: bold;' if pd.notnull(x) and x > 0 else '', subset=gain_cols)
            for c in gain_cols:
                format_dict[c] = lambda x: f"▲ +{format_num(x)}" if pd.notnull(x) and x > 0 else ("0" if pd.notnull(x) else "")
                
        for c in ['Clicks_New', 'Clicks_Old', 'Impressions_New', 'Impressions_Old']:
            if c in df_to_show.columns:
                format_dict[c] = lambda x: format_num(x) if pd.notnull(x) else ""
                
        for c in ['Position_New', 'Position_Old']:
            if c in df_to_show.columns:
                format_dict[c] = lambda x: format_num(x, decimal_places=2) if pd.notnull(x) and x != 101 else ("-" if x == 101 else "")
                
        if 'Position Change' in df_to_show.columns:
            def style_pos_change(x):
                if pd.isnull(x) or abs(x) > 90: return ''
                if x > 0: return 'color: #90c274; font-weight: bold;'
                if x < 0: return 'color: #d28063; font-weight: bold;'
                return ''
            styler = styler.map(style_pos_change, subset=['Position Change'])
            
            def format_pos_change(x):
                if pd.isnull(x) or abs(x) > 90: return "-"
                val = format_num(abs(x), decimal_places=2)
                if x > 0: val = f"▲ +{val}"
                elif x < 0: val = f"▼ -{val}"
                return val
                
            format_dict['Position Change'] = format_pos_change
            
        if 'Clicks Change' in df_to_show.columns:
            def style_clicks_change(x):
                if pd.isnull(x) or x == 0: return ''
                if x > 0: return 'color: #90c274; font-weight: bold;'
                if x < 0: return 'color: #d28063; font-weight: bold;'
                return ''
            styler = styler.map(style_clicks_change, subset=['Clicks Change'])
            
            def format_clicks_change(x):
                if pd.isnull(x) or x == 0: return "0"
                val = format_num(abs(x))
                if x > 0: val = f"▲ +{val}"
                elif x < 0: val = f"▼ -{val}"
                return val
                
            format_dict['Clicks Change'] = format_clicks_change
            
        styler = styler.format(format_dict)
        st.dataframe(styler, use_container_width=True)

    # --- Visualizations & Tabs ---
    st.header("Details" if lang == "DE" else "Details")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        t["tab_cluster"],
        t["tab_drops"],
        t["tab_losses"], 
        t["tab_lhf"], 
        t["tab_winners"],
        t["tab_all"]
    ])
    
    with tab1:
        st.subheader(t["cl_sub"])
        st.write(t["cl_desc"])
        
        if not losers.empty:
            cluster_vol = losers.groupby('Cluster').agg(
                Clicks_Loss=('Clicks Loss', 'sum'),
                Keyword_Count=('Keyword', 'count')
            ).reset_index()
            cluster_vol = cluster_vol[cluster_vol['Clicks_Loss'] > 0].sort_values('Clicks_Loss', ascending=False)
            
            fig_cluster = px.bar(cluster_vol, x='Cluster', y='Clicks_Loss', 
                         title=t["cl_chart_title"],
                         labels={'Cluster': t["cl_chart_label_c"], 'Clicks_Loss': t["cl_chart_label_v"]},
                         hover_data=['Keyword_Count'],
                         color='Clicks_Loss', color_continuous_scale=[[0.0, '#dfdfdf'], [1.0, '#d28063']])
            style_plotly_fig(fig_cluster)
            st.plotly_chart(fig_cluster, use_container_width=True)
            
            st.markdown(t["cl_detail"])
            selected_clusters = st.multiselect(t["cl_select"], options=cluster_vol['Cluster'].tolist(), default=[cluster_vol['Cluster'].iloc[0]])
            if selected_clusters:
                cluster_df = losers[losers['Cluster'].isin(selected_clusters)]
                st.write(f"{t['cl_sum']} **{format_num(cluster_df['Clicks Loss'].sum())}**")
                display_styled_dataframe(cluster_df[['Keyword', 'Cluster', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Loss', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Loss')
        else:
            st.info(t["cl_empty"])

    with tab2:
        st.subheader(t["rd_sub"])
        kw_filter = st.text_input(t["rd_filter"], key="drops_kw_filter").strip().lower()
        
        f_top3 = top3_drops[top3_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else top3_drops
        f_top10 = top10_drops[top10_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else top10_drops
        f_page2 = page2_drops[page2_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else page2_drops
        f_total = total_loss[total_loss['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else total_loss
        
        st.markdown(t["rd_t3_title"])
        if not f_top3.empty:
            st.write(f"{t['rd_sum']} **{format_num(f_top3['Clicks Loss'].sum())}**")
            display_styled_dataframe(f_top3[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Loss', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Loss')
        else:
            st.info(t["rd_t3_empty"])
            
        st.markdown(t["rd_t10_title"])
        if not f_top10.empty:
            st.write(f"{t['rd_sum']} **{format_num(f_top10['Clicks Loss'].sum())}**")
            display_styled_dataframe(f_top10[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Loss', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Loss')
        else:
            st.info(t["rd_t10_empty"])
            
        st.markdown(t["rd_p2_title"])
        if not f_page2.empty:
            st.write(f"{t['rd_sum']} **{format_num(f_page2['Clicks Loss'].sum())}**")
            display_styled_dataframe(f_page2[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Loss', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Loss')
        else:
            st.info(t["rd_p2_empty"])
            
        st.markdown(t["rd_100_title"])
        if not f_total.empty:
            st.write(f"{t['rd_sum']} **{format_num(f_total['Clicks Loss'].sum())}**")
            display_styled_dataframe(f_total[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Loss', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Loss')
        else:
            st.info(t["rd_100_empty"])

    with tab3:
        st.subheader(t["cd_sub"])
        display_styled_dataframe(losers[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Loss', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Loss')

    with tab4:
        st.subheader(t["lhf_sub"], anchor="low-hanging-fruits")
        st.markdown(t["lhf_desc"])
        if not low_hanging.empty:
            display_styled_dataframe(low_hanging[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Impressions_New', 'Clicks_New']], sort_col='Impressions_New')
        else:
            st.info(t["lhf_empty"])
            
    with tab5:
        st.subheader(t["win_sub"])
        if not winners.empty:
            display_styled_dataframe(winners[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Gain', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Gain')
            
            fig_win = px.scatter(
                winners, x="Clicks Gain", y="Position_New", 
                size="Clicks_New", color="Position Change",
                hover_name="Keyword", title=t["win_chart_title"],
                labels={'Position_New': t["win_chart_label_pos"], 'Clicks Gain': t["win_chart_label_gain"]},
                color_continuous_scale=[[0.0, '#dfdfdf'], [1.0, '#90c274']]
            )
            fig_win.update_yaxes(autorange="reversed")
            style_plotly_fig(fig_win)
            st.plotly_chart(fig_win, use_container_width=True)
        else:
            st.info(t["win_empty"])

    with tab6:
        st.subheader(t["ad_sub"])
        all_cols = ['Cluster', 'Keyword', 'Change', 'Position Change', 'Clicks Change', 'Position_Old', 'Position_New', 'Impressions_Old', 'Impressions_New', 'Clicks_Old', 'Clicks_New']
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            all_clusters = sorted(df['Cluster'].dropna().unique().tolist())
            sel_cluster = st.multiselect(t["ad_filter_cluster"], options=all_clusters)
        with col_f2:
            all_changes = sorted(df['Change'].dropna().unique().tolist())
            sel_change = st.multiselect(t["ad_filter_change"], options=all_changes)
        with col_f3:
            search_kw = st.text_input(t["ad_filter_kw"], key="ad_kw")
            
        f_df = df[all_cols].copy()
        if sel_cluster:
            f_df = f_df[f_df['Cluster'].isin(sel_cluster)]
        if sel_change:
            f_df = f_df[f_df['Change'].isin(sel_change)]
        if search_kw:
            f_df = f_df[f_df['Keyword'].astype(str).str.lower().str.contains(search_kw.lower(), na=False)]
            
        display_styled_dataframe(f_df, sort_col='Clicks Change', ascending=False)

else:
    st.info(translations[lang]["info_upload"])

# Footer
st.markdown("<hr class='hr--grey'>", unsafe_allow_html=True)
st.markdown(
    f"<div style='text-align: center; color: #797979; font-size: 0.9em;'>{t['footer']}</div>", 
    unsafe_allow_html=True
)
