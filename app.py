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
        "data_lang": "Data Language (Keywords)",
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
        "legal_header": "Legal & Privacy Policy",
        "imprint_body": """### Imprint

**Information pursuant to § 5 DDG:**
Benjamin Wingerter
SEOux Indianer
Email: mytools.gscrankingchanges@mindblowmedia.com
Website: seouxindianer.de

**Disclaimer:**
The contents of this app were created with the utmost care. However, we cannot guarantee the correctness, completeness, or topicality of the content.""",
        "privacy_body": """### Privacy Policy

**1. General Information**
This privacy policy informs you about the nature, scope, and purpose of the processing of personal data within this web application.

**2. Data Controller**
Benjamin Wingerter
Email: mytools.gscrankingchanges@mindblowmedia.com

**3. Hosting (Streamlit Cloud)**
This app is hosted on Streamlit Community Cloud, a service provided by Snowflake Inc. (106 East Babcock Street, Suite 3A, Bozeman, MT 59715, USA). To serve the app securely, Snowflake processes connection logs and IP addresses of visitors. This processing is based on our legitimate interest in a secure and efficient operation of the application (Art. 6 (1) (f) GDPR). For more details, please refer to the Snowflake Privacy Policy.

**4. Processing of Uploaded Files (CSV)**
When you upload a Google Search Console export file (Queries.csv):
- The file is processed **exclusively in the transient memory (RAM)** of the server to generate dashboards.
- The uploaded data is **never stored permanently on any storage drive or database**.
- As soon as you terminate your session (e.g., by closing the browser tab, reloading the page, or replacing the file), all processed data is completely erased.
- The legal basis for this processing is Art. 6 (1) (f) GDPR (our legitimate interest in providing you with this analysis tool).

**5. Your Rights**
You have the right to access, rectify, erase, or restrict the processing of your personal data, as well as the right to data portability and objection.""",
    },
    "DE": {
        "title": "GSC Ranking Changes Analyzer",
        "subtitle": "Laden Sie Ihren Google Search Console Vergleichsexport (Queries.csv) hoch und analysieren Sie reale Klick-Verluste und Quick-Wins.",
        "sidebar_data": "1. Daten & Einstellungen",
        "upload_label": "GSC Queries.csv Upload",
        "cluster_settings": "Clustering-Einstellungen",
        "data_lang": "Daten-Sprache (Keywords)",
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
        "legal_header": "Rechtliches / Impressum",
        "imprint_body": """### Impressum

**Angaben gemäß § 5 DDG:**
Benjamin Wingerter
SEOux Indianer
E-Mail: mytools.gscrankingchanges@mindblowmedia.com
Website: seouxindianer.de

**Haftungsausschluss (Disclaimer):**
Die Inhalte dieser App wurden mit größter Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte können wir jedoch keine Gewähr übernehmen.""",
        "privacy_body": """### Datenschutzerklärung

**1. Allgemeine Hinweise**
Diese Datenschutzerklärung klärt Sie über die Art, den Umfang und Zweck der Verarbeitung von personenbezogenen Daten innerhalb dieser Webanwendung (App) auf.

**2. Verantwortlicher**
Benjamin Wingerter
E-Mail: mytools.gscrankingchanges@mindblowmedia.com

**3. Hosting (Streamlit Cloud)**
Diese App wird auf der Streamlit Community Cloud gehostet, einem Dienst von Snowflake Inc. (106 East Babcock Street, Suite 3A, Bozeman, MT 59715, USA). Zur Bereitstellung und zum sicheren Betrieb der App verarbeitet Snowflake Verbindungsdaten und IP-Adressen der Besucher. Die Übermittlung erfolgt auf Grundlage unserer berechtigten Interessen an einem sicheren und effizienten Betrieb des Dienstes (Art. 6 Abs. 1 lit. f DSGVO). Weitere Details finden Sie in der Datenschutzerklärung von Snowflake.

**4. Verarbeitung von hochgeladenen Dateien (CSV)**
Wenn Sie eine Google Search Console Exportdatei (Queries.csv) hochladen:
- Die Datei wird **ausschließlich im Arbeitsspeicher (RAM)** des Servers verarbeitet, um die Auswertungen zu berechnen.
- Die hochgeladenen Daten werden **zu keinem Zeitpunkt dauerhaft auf Datenträgern oder in einer DBA gespeichert**.
- Sobald Sie Ihre Sitzung beenden (z. B. durch Schließen des Browsers, Neuladen der Seite oder Ändern der Upload-Datei), werden die verarbeiteten Daten vollständig gelöscht.
- Die Rechtsgrundlage für diese Verarbeitung ist Art. 6 Abs. 1 lit. f DSGVO (unser berechtigtes Interesse, Ihnen diese Analysefunktionalität anzubieten).

**5. Ihre Rechte**
Sie haben das Recht auf Auskunft, Berichtigung, Löschung und Einschränkung der Verarbeitung Ihrer personenbezogenen Daten sowie das Recht auf Datenübertragbarkeit und Widerspruch.""",
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
data_lang_choice = st.sidebar.selectbox(t.get("data_lang", "Data Language"), options=["Deutsch", "English", "Español", "Français", "Italiano", "Other"], index=0)
brand_input = st.sidebar.text_input(t["brand_input"], value="", help=t["brand_help"])
num_clusters = st.sidebar.slider(t["cluster_count"], min_value=5, max_value=50, value=20, step=5)

if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False

if uploaded_file is not None:
    if st.sidebar.button(t["btn_analyze"], type="primary"):
        st.session_state['analyzed'] = True

# Sidebar - Legal Disclosures
st.sidebar.markdown("---")
with st.sidebar.expander(t["legal_header"]):
    st.markdown(t["imprint_body"])
    st.markdown("---")
    st.markdown(t["privacy_body"])

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
    
    def is_brand(kw):
        kw_lower = str(kw).lower()
        for b in brand_terms:
            if b and b in kw_lower:
                return True
        return False

    temp_losers = df[df['Clicks Loss'] > 0]
    non_brand_kws = temp_losers[~temp_losers['Keyword'].apply(is_brand)]['Keyword'].dropna().tolist()
    
    word_counts = Counter()
    for kw in non_brand_kws:
        words = re.findall(r'\b\w+\b', str(kw).lower())
        for w in words:
            if w not in stopwords and len(w) > 2 and not w.isnumeric():
                word_counts[w] += 1
                
    top_head_terms = [word for word, count in word_counts.most_common(num_clusters)]
    
    def get_cluster(kw):
        kw_lower = str(kw).lower()
        for b in brand_terms:
            if b and b in kw_lower:
                return "Brand"
        for term in top_head_terms:
            if re.search(rf'\b{re.escape(term)}\b', kw_lower):
                return term.capitalize()
        return "undefined"
        
    def get_intent(kw):
        kw_lower = str(kw).lower()
        intents = []
        if data_lang_choice == "Deutsch":
            # User Intent: KNOW
            if re.search(r'((.*\s|^)w(er|em|en|essen|ie|ann|o|elche|as|obei|omit|oran|orin|ohin|obei|eshalb|arum|ieso|orauf|orum|ovor|ogegen|odurch|oher|eswegen|oraus)\s.*)|((.*\s|^)anleitung|anweisung|beschreibung|bestimmung|bin ich|definition|erklärung|forum|frage|gesetz|guide|(.*\s|^)hilfe|how to|muss|kann(\s.*|$)|(.*\s|^)darf|methode|quora|rechtlich|regeln|tipps|tutorial|brauche|vor was|walkthrough|diy|yahoo clever|gute frage)(\s.*|$)', kw_lower):
                intents.append("KNOW")
                
            # User Intent: DO (Transactional)
            if re.search(r'.*aktionen.*|.*am billigsten.*|.*anfordern.*|.*angebot.*|.*anmeldung.*|.*auf lager.*|.*bestellbar.*|.*bestellen.*|.*billig.*|.*coupon.*|.*discount.*|.*download.*|.*free.*|.*garantie.*|.*gebraucht.*|.*gewinnen.*|.*gewinnspiel.*|.*gratis.*|.*günstig.*|.*günstige.*|.*günstiges.*|.*günstigste.*|.*günstigste.*|.*gutschein.*|.*gutscheincode.*|.*im angebot.*|.*in stock.*|.*kaufen.*|.*kaufen.*|.*käuflich.*|.*kontakt.*|.*kostenlos.*|.*leihen.*|.*mieten.*|.*mit kreditkarte.*|.*mit paypal.*|.*ohne schufa.*|.*online kaufen.*|.*onlineshop.*|.*pdf.*|.*preis.*|.*preisausschreiben.*|.*preisvergleich.*|.*preiswert.*|.*rabatt.*|.*shop.*|.*special.*|.*template.*|.*überbestände.*|.*umsonst.*|.*verkauf.*|.*vorlage.*|.*vorrätig.*|.*werbung.*|.*wo kauf.*|.*zu verkaufen.*', kw_lower):
                intents.append("DO (Transactional)")

            # User Intent: regional:CITY
            if re.search(r'.*aach.*|.*aalen.*|.*abenberg.*|.*abensberg.*|.*achern.*|.*achim.*|.*adelsheim.*|.*adenau.*|.*adorf.*|.*ahaus.*|.*ahlen.*|.*ahrensburg.*|.*aichach.*|.*aichtal.*|.*aken.*|.*albstadt.*|.*alfeld.*|.*allendorf.*|.*allstedt.*|.*alpirsbach.*|.*alsdorf.*|.*alsfeld.*|.*alsleben.*|.*altdorf.*|.*altena.*|.*altenau.*|.*altenberg.*|.*altenburg.*|.*altenkirchen.*|.*altensteig.*|.*altentreptow.*|.*altlandsberg.*|.*altötting.*|.*alzenau.*|.*alzey.*|.*amberg.*|.*amöneburg.*|.*amorbach.*|.*andernach.*|.*angermünde.*|.*anklam.*|.*annaberg.*|.*annaberg-buchholz.*|.*annaburg.*|.*annweiler.*|.*ansbach.*|.*apolda.*|.*arendsee.*|.*arneburg.*|.*arnis.*|.*arnsberg.*|.*arnstadt.*|.*arnstein.*|.*artern.*|.*unstrut.*|.*arzberg.*|.*aschaffenburg.*|.*aschersleben.*|.*asperg.*|.*aßlar.*|.*attendorn.*|.*aub.*|.*aue.*|.*auerbach.*|.*augsburg.*|.*augustusburg.*|.*aulendorf.*|.*aurich.*|.*babenhausen.*|.*bacharach.*|.*backnang.*|.*bad aibling.*|.*bad arolsen.*|.*bad bentheim.*|.*bad bergzabern.*|.*bad berka.*|.*bad berleburg.*|.*bad berneck.*|.*bad bevensen.*|.*bad bibra.*|.*bad blankenburg.*|.*bad bramstedt.*|.*bad breisig.*|.*bad brückenau.*|.*bad buchau.*|.*bad camberg.*|.*bad colberg.*|.*bad colberg heldburg.*|.*colberg.*|.*heldburg.*|.*doberan.*|.*bad driburg.*|.*bad düben.*|.*bad dürkheim.*|.*bad dürrenberg.*|.*bad dürrheim.*|.*bad elster.*|.*bad ems.*|.*bad fallingbostel.*|.*bad frankenhausen.*|.*frankenhausen.*|.*kyffhäuser.*|.*bad freienwalde.*|.*bad friedrichshall.*|.*bad gandersheim.*|.*bad gottleuba.*|.*bad gottleuba-berggießhübel.*|.*bad griesbach.*|.*griesbach.*|.*bad grund.*|.*bad harzburg.*|.*bad herrenalb.*|.*bad hersfeld.*|.*bad homburg.*|.*bad homburg vor der höhe.*|.*bad honnef.*|.*bad hönningen.*|.*bad iburg.*|.*bad karlshafen.*|.*kissingen.*|.*bad könig.*|.*königshofen.*|.*bad kösen.*|.*köstritz.*|.*kötzting.*|.*bad kreuznach.*|.*bad krozingen.*|.*bad laasphe.*|.*bad langensalza.*|.*bad lauchstädt.*|.*bad lausick.*|.*bad lauterberg.*|.*bad lauterberg im harz.*|.*bad liebenstein.*|.*bad liebenwerda.*|.*bad liebenzell.*|.*bad lippspringe.*|.*bad lobenstein.*|.*bad marienberg.*|.*bad mergentheim.*|.*bad münder am deister.*|.*bad münster.*|.*bad münster am stein-ebernburg.*|.*bad münstereifel.*|.*bad muskau.*|.*bad nauheim.*|.*bad nenndorf.*|.*bad neuenahr.*|.*bad neuenahr-ahrweiler.*|.*bad neustadt.*|.*bad neustadt an der saale.*|.*bad oeynhausen.*|.*bad oldesloe.*|.*bad orb.*|.*bad pyrmont.*|.*bad rappenau.*|.*bad reichenhall.*|.*bad rodach.*|.*bad sachsa.*|.*bad säckingen.*|.*bad salzdetfurth.*|.*bad salzuflen.*|.*bad salzungen.*|.*bad saulgau.*|.*bad schandau.*|.*bad schmiedeberg.*|.*bad schussenried.*|.*bad schwalbach.*|.*bad schwartau.*|.*bad segeberg.*|.*bad sobernheim.*|.*bad soden.*|.*bad soden am taunus.*|.*bad soden-salmünster.*|.*bad sooden.*|.*bad sooden-allendorf.*|.*staffelstein.*|.*bad sulza.*|.*bad sülze.*|.*teinach.*|.*zavelstein.*|.*tennstedt.*|.*tölz.*|.*bad urach.*|.*vilbel.*|.*bad waldsee.*|.*bad wildbad.*|.*bad wildungen.*|.*bad wilsnack.*|.*bad wimpfen.*|.*bad windsheim.*|.*bad wörishofen.*|.*bad wünnenberg.*|.*bad wurzach.*|.*baden-baden.*|.*baesweiler.*|.*baiersdorf.*|.*balingen.*|.*ballenstedt.*|.*balve.*|.*bamberg.*|.*barby.*|.*bargteheide.*|.*barmstedt.*|.*bärnau.*|.*barntrup.*|.*barsinghausen.*|.*barth.*|.*baruth.*|.*baruth.*|.*bassum.*|.*battenberg.*|.*baumholder.*|.*baunach.*|.*baunatal.*|.*bautzen.*|.*bayreuth.*|.*bebra.*|.*beckum.*|.*bedburg.*|.*beelitz.*|.*beerfelden.*|.*beeskow.*|.*beilngries.*|.*beilstein.*|.*belgern.*|.*belzig.*|.*bendorf.*|.*benneckenstein.*|.*bensheim.*|.*berching.*|.*berga elster.*|.*bergen.*|.*bergheim.*|.*bergisch gladbach.*|.*bergkamen.*|.*bergneustadt.*|.*berka.*|.*berka werra.*|.*werra.*|.*berlin.*|.*bernau bei berlin.*|.*bernburg.*|.*bernkastel-kues.*|.*bernsdorf.*|.*bernstadt a. d. eigen.*|.*bersenbrück.*|.*besigheim.*|.*betzdorf.*|.*betzenstein.*|.*beverungen.*|.*bexbach.*|.*biberach an der riß.*|.*biedenkopf.*|.*bielefeld.*|.*biesenthal.*|.*bietigheim-bissingen.*|.*billerbeck.*|.*bingen am rhein.*|.*birkenfeld.*|.*bischofsheim an der rhön.*|.*bischofswerda.*|.*bismark.*|.*bitburg.*|.*bitterfeld.*|.*blankenburg.*|.*blankenhain.*|.*blaubeuren.*|.*bleckede.*|.*bleicherode.*|.*blieskastel.*|.*blomberg.*|.*blumberg.*|.*bobingen.*|.*böblingen.*|.*bocholt.*|.*bochum.*|.*bockenem.*|.*bodenwerder.*|.*bogen.*|.*böhlen.*|.*boizenburg.*|.*bonn.*|.*bonndorf im schwarzwald.*|.*bönnigheim.*|.*bopfingen.*|.*boppard.*|.*borgentreich.*|.*borgholzhausen.*|.*borken.*|.*borken.*|.*borkum.*|.*borna.*|.*bornheim.*|.*bottrop.*|.*boxberg.*|.*brackenheim.*|.*brake.*|.*brakel.*|.*bramsche.*|.*brand-erbisdorf.*|.*brandenburg an der havel.*|.*brandis.*|.*braubach.*|.*braunfels.*|.*braunlage.*|.*bräunlingen.*|.*braunsbedra.*|.*braunschweig.*|.*breckerfeld.*|.*bredstedt.*|.*brehna.*|.*breisach am rhein.*|.*bremen.*|.*bremerhaven.*|.*bremervörde.*|.*bretten.*|.*breuberg.*|.*brilon.*|.*brotterode.*|.*bruchköbel.*|.*bruchsal.*|.*brück.*|.*brüel.*|.*brühl.*|.*brunsbüttel.*|.*brüssow.*|.*buchen.*|.*buchholz.*|.*buchholz in der nordheide.*|.*buchloe.*|.*bückeburg.*|.*buckow.*|.*büdelsdorf.*|.*büdingen.*|.*bühl.*|.*bünde.*|.*büren.*|.*burg.*|.*burg stargard.*|.*burgau.*|.*burgbernheim.*|.*burgdorf.*|.*bürgel.*|.*burghausen.*|.*burgkunstadt.*|.*burglengenfeld.*|.*burgstädt.*|.*burgwedel.*|.*burladingen.*|.*burscheid.*|.*bürstadt.*|.*buttelstedt.*|.*buttstädt.*|.*butzbach.*|.*bützow.*|.*buxtehude.*|.*calau.*|.*calbe.*|.*calw.*|.*camburg.*|.*castrop-rauxel.*|.*celle.*|.*cham.*|.*chemnitz.*|.*clausthal-zellerfeld.*|.*clingen.*|.*cloppenburg.*|.*coburg.*|.*cochem.*|.*coesfeld.*|.*colditz.*|.*coswig.*|.*coswig.*|.*cottbus.*|.*crailsheim.*|.*creglingen.*|.*creußen.*|.*creuzburg.*|.*crimmitschau.*|.*crivitz.*|.*cuxhaven.*|.*dachau.*|.*dahlen.*|.*dahme.*|.*dahn.*|.*damme.*|.*dannenberg.*|.*dargun.*|.*darmstadt.*|.*dassel.*|.*dassow.*|.*datteln.*|.*daun.*|.*deggendorf.*|.*deidesheim.*|.*delbrück.*|.*delitzsch.*|.*delmenhorst.*|.*demmin.*|.*derenburg.*|.*dessau.*|.*detmold.*|.*dettelbach.*|.*dieburg.*|.*diemelstadt.*|.*diepholz.*|.*dierdorf.*|.*dietenheim.*|.*dietfurt an der altmühl.*|.*dietzenbach.*|.*diez.*|.*dillenburg.*|.*donau.*|.*dillingen.*|.*dingelstädt.*|.*dingolfing.*|.*dinkelsbühl.*|.*dinklage.*|.*dinslaken.*|.*dippoldiswalde.*|.*dissen am teutoburger wald.*|.*ditzingen.*|.*döbeln.*|.*doberlug-kirchhain.*|.*döbern.*|.*dohna.*|.*dömitz.*|.*dommitzsch.*|.*donaueschingen.*|.*donauwörth.*|.*donzdorf.*|.*dorfen.*|.*dormagen.*|.*dornburg.*|.*dornhan.*|.*dornstetten.*|.*dorsten.*|.*dortmund.*|.*dransfeld.*|.*drebkau.*|.*dreieich.*|.*drensteinfurt.*|.*dresden.*|.*drolshagen.*|.*duderstadt.*|.*duisburg.*|.*dülmen.*|.*düren.*|.*düsseldorf.*|.*ebeleben.*|.*eberbach.*|.*ebermannstadt.*|.*ebern.*|.*ebersbach.*|.*ebersbach an der fils.*|.*ebersberg.*|.*eberswalde.*|.*eckartsberga.*|.*eckernförde.*|.*edenkoben.*|.*egeln.*|.*eggenfelden.*|.*eggesin.*|.*ehingen.*|.*ehrenfriedersdorf.*|.*eibelstadt.*|.*eibenstock.*|.*eichstätt.*|.*eilenburg.*|.*einbeck.*|.*eisenach.*|.*eisenberg.*|.*eisenberg.*|.*eisenhüttenstadt.*|.*eisfeld.*|.*eisleben.*|.*eislingen.*|.*elbingerode.*|.*ellingen.*|.*ellrich.*|.*ellwangen.*|.*elmshorn.*|.*elsfleth.*|.*elsterberg.*|.*elsterwerda.*|.*elstra.*|.*elterlein.*|.*eltmann.*|.*eltville am rhein.*|.*elzach.*|.*elze.*|.*emden.*|.*emmendingen.*|.*emmerich am rhein.*|.*emsdetten.*|.*endingen am kaiserstuhl.*|.*engen.*|.*enger.*|.*ennepetal.*|.*ennigerloh.*|.*eppelheim.*|.*eppingen.*|.*eppstein.*|.*erbach.*|.*erbach.*|.*erbendorf.*|.*erding.*|.*erftstadt.*|.*erfurt.*|.*erkelenz.*|.*erkner.*|.*erkrath.*|.*erlangen.*|.*erlenbach am main.*|.*erwitte.*|.*eschborn.*|.*eschenbach in der oberpfalz.*|.*eschershausen.*|.*eschwege.*|.*eschweiler.*|.*espelkamp.*|.*essen.*|.*esslingen.*|.*ettenheim.*|.*ettlingen.*|.*euskirchen.*|.*eutin.*|.*falkenberg.*|.*falkensee.*|.*falkenstein.*|.*fehmarn.*|.*fellbach.*|.*felsberg.*|.*feuchtwangen.*|.*filderstadt.*|.*finsterwalde.*|.*fladungen.*|.*flensburg.*|.*flöha.*|.*flörsheim.*|.*forchheim.*|.*forchtenberg.*|.*frankenau.*|.*frankenberg.*|.*frankenberg.*|.*frankenthal.*|.*frankfurt.*|.*frankfurt am main.*|.*franzburg.*|.*frauenstein.*|.*frechen.*|.*freiberg.*|.*freiberg am neckar.*|.*freiburg im breisgau.*|.*freilassing.*|.*freinsheim.*|.*freising.*|.*freital.*|.*freren.*|.*freudenberg.*|.*freudenberg.*|.*freudenstadt.*|.*freyburg.*|.*freystadt.*|.*freyung.*|.*fridingen an der donau.*|.*friedberg.*|.*friedberg.*|.*friedland.*|.*friedland.*|.*friedrichroda.*|.*friedrichsdorf.*|.*friedrichshafen.*|.*friedrichstadt.*|.*friedrichsthal.*|.*friesack.*|.*friesoythe.*|.*fritzlar.*|.*frohburg.*|.*fröndenberg.*|.*fulda.*|.*fürstenau.*|.*fürstenberg.*|.*fürstenfeldbruck.*|.*fürstenwalde.*|.*fürth.*|.*furth im wald.*|.*furtwangen im schwarzwald.*|.*füssen.*|.*gadebusch.*|.*gaggenau.*|.*gaildorf.*|.*gammertingen.*|.*garbsen.*|.*garching bei münchen.*|.*gardelegen.*|.*garding.*|.*gartz.*|.*garz.*|.*algesheim.*|.*gebesee.*|.*gedern.*|.*geesthacht.*|.*gefell.*|.*gefrees.*|.*gehrden.*|.*geilenkirchen.*|.*geisa.*|.*geiselhöring.*|.*geisenfeld.*|.*geisenheim.*|.*geising.*|.*geisingen.*|.*geislingen.*|.*geislingen an der steige.*|.*geithain.*|.*geldern.*|.*gelnhausen.*|.*gelsenkirchen.*|.*gemünden.*|.*gemünden am main.*|.*gengenbach.*|.*genthin.*|.*georgsmarienhütte.*|.*gera.*|.*gerabronn.*|.*gerbstedt.*|.*geretsried.*|.*geringswalde.*|.*gerlingen.*|.*germering.*|.*germersheim.*|.*gernrode.*|.*gernsbach.*|.*gernsheim.*|.*gerolstein.*|.*gerolzhofen.*|.*gersfeld.*|.*gersthofen.*|.*gescher.*|.*geseke.*|.*gevelsberg.*|.*geyer.*|.*giengen.*|.*gießen.*|.*gifhorn.*|.*gladbeck.*|.*gladenbach.*|.*glashütte.*|.*glauchau.*|.*glinde.*|.*glücksburg.*|.*glückstadt.*|.*gnoien.*|.*goch.*|.*goldberg.*|.*goldkronach.*|.*golßen.*|.*gommern.*|.*göppingen.*|.*görlitz.*|.*goslar.*|.*gößnitz.*|.*gotha.*|.*göttingen.*|.*grabow.*|.*grafenau.*|.*gräfenberg.*|.*gräfenhainichen.*|.*gräfenthal.*|.*grafenwöhr.*|.*grafing.*|.*gransee.*|.*grebenau.*|.*grebenstein.*|.*greding.*|.*greifswald.*|.*greiz.*|.*greußen.*|.*greven.*|.*grevenbroich.*|.*grevesmühlen.*|.*griesheim.*|.*grimma.*|.*grimmen.*|.*gröbzig.*|.*gröditz.*|.*groitzsch.*|.*gronau.*|.*gronau.*|.*gröningen.*|.*groß bieberau.*|.*groß gerau.*|.*groß-umstadt.*|.*großalmerode.*|.*großbottwar.*|.*großbreitenbach.*|.*großenehrich.*|.*großenhain.*|.*großräschen.*|.*großröhrsdorf.*|.*großschirma.*|.*grünberg.*|.*grünhain-beierfeld.*|.*grünsfeld.*|.*grünstadt.*|.*guben.*|.*gudensberg.*|.*güglingen.*|.*gummersbach.*|.*gundelfingen an der donau.*|.*gundelsheim.*|.*güntersberge.*|.*günzburg.*|.*gunzenhausen.*|.*güsten.*|.*güstrow.*|.*gütersloh.*|.*gützkow.*|.*haan.*|.*hachenburg.*|.*hadamar.*|.*hadmersleben.*|.*hagen.*|.*hagenbach.*|.*hagenow.*|.*haiger.*|.*haigerloch.*|.*hainichen.*|.*haiterbach.*|.*halberstadt.*|.*haldensleben.*|.*halle.*|.*halle.*|.*hallenberg.*|.*hallstadt.*|.*haltern am see.*|.*halver.*|.*hamburg.*|.*hameln.*|.*hamm.*|.*hammelburg.*|.*hamminkeln.*|.*hanau.*|.*hann. münden.*|.*hannover.*|.*harburg.*|.*hardegsen.*|.*haren.*|.*harsewinkel.*|.*hartenstein.*|.*hartha.*|.*harzgerode.*|.*haselünne.*|.*haslach im kinzigtal.*|.*hasselfelde.*|.*haßfurt.*|.*hattersheim am main.*|.*hattingen.*|.*hatzfeld.*|.*hausach.*|.*hauzenberg.*|.*havelberg.*|.*havelsee.*|.*hayingen.*|.*hechingen.*|.*hecklingen.*|.*heideck.*|.*heidelberg.*|.*heidenau.*|.*heidenheim an der brenz.*|.*heilbad heiligenstadt.*|.*heilbronn.*|.*heiligenhafen.*|.*heiligenhaus.*|.*heilsbronn.*|.*heimbach.*|.*heimsheim.*|.*heinsberg.*|.*heitersheim.*|.*heldrungen.*|.*helmbrechts.*|.*helmstedt.*|.*hemau.*|.*hemer.*|.*hemmingen.*|.*hemmoor.*|.*hemsbach.*|.*hennef.*|.*hennigsdorf.*|.*heppenheim.*|.*herbolzheim.*|.*herborn.*|.*herbrechtingen.*|.*herbstein.*|.*herdecke.*|.*herdorf.*|.*herford.*|.*heringen.*|.*heringen.*|.*hermeskeil.*|.*hermsdorf.*|.*herne.*|.*herrenberg.*|.*herrieden.*|.*herrnhut.*|.*hersbruck.*|.*herten.*|.*herzberg.*|.*herzberg am harz.*|.*herzogenaurach.*|.*herzogenrath.*|.*hessisch lichtenau.*|.*hessisch oldendorf.*|.*hettingen.*|.*hettstedt.*|.*heubach.*|.*heusenstamm.*|.*hilchenbach.*|.*hildburghausen.*|.*hilden.*|.*hildesheim.*|.*hillesheim.*|.*hilpoltstein.*|.*hirschau.*|.*hirschberg.*|.*hirschhorn.*|.*hitzacker.*|.*hochheim am main.*|.*höchstadt an der aisch.*|.*höchstädt an der donau.*|.*hockenheim.*|.*hofgeismar.*|.*hofheim.*|.*hohen neuendorf.*|.*hohenberg.*|.*hohenleuben.*|.*hohenmölsen.*|.*hohenstein-ernstthal.*|.*hohnstein.*|.*höhr-grenzhausen.*|.*hollfeld.*|.*holzgerlingen.*|.*holzminden.*|.*homberg.*|.*homberg.*|.*homburg.*|.*horb am neckar.*|.*meinberg.*|.*hornbach.*|.*hornberg.*|.*hornburg.*|.*hörstel.*|.*horstmar.*|.*höxter.*|.*hoya.*|.*hoyerswerda.*|.*hoym.*|.*hückelhoven.*|.*hückeswagen.*|.*hüfingen.*|.*hünfeld.*|.*hungen.*|.*hürth.*|.*husum.*|.*ibbenbüren.*|.*ichenhausen.*|.*idar-oberstein.*|.*idstein.*|.*illertissen.*|.*ilmenau.*|.*ilsenburg.*|.*ilshofen.*|.*immenhausen.*|.*immenstadt im allgäu.*|.*ingelfingen.*|.*ingelheim am rhein.*|.*ingolstadt.*|.*iphofen.*|.*iserlohn.*|.*isny im allgäu.*|.*isselburg.*|.*itzehoe.*|.*jarmen.*|.*jena.*|.*jerichow.*|.*jessen.*|.*jeßnitz.*|.*jever.*|.*joachimsthal.*|.*johanngeorgenstadt.*|.*jöhstadt.*|.*jülich.*|.*jüterbog.*|.*kaarst.*|.*kahla.*|.*kaisersesch.*|.*kaiserslautern.*|.*kalbe.*|.*kalkar.*|.*kaltenkirchen.*|.*kaltennordheim.*|.*kamen.*|.*kamenz.*|.*kamp-lintfort.*|.*kandel.*|.*kandern.*|.*kappeln.*|.*karben.*|.*karlsruhe.*|.*karlstadt.*|.*kassel.*|.*kastellaun.*|.*katzenelnbogen.*|.*kaub.*|.*kaufbeuren.*|.*kehl.*|.*kelbra.*|.*kelheim.*|.*kelkheim.*|.*kellinghusen.*|.*kelsterbach.*|.*kemberg.*|.*kemnath.*|.*kempen.*|.*kempten.*|.*kenzingen.*|.*kerpen.*|.*ketzin.*|.*kevelaer.*|.*kiel.*|.*kierspe.*|.*kindelbrück.*|.*kirchberg.*|.*kirchberg.*|.*kirchberg an der jagst.*|.*kirchen.*|.*kirchenlamitz.*|.*kirchhain.*|.*kirchheim unter teck.*|.*kirchheimbolanden.*|.*kirn.*|.*kirtorf.*|.*kitzingen.*|.*kitzscher.*|.*kleve.*|.*klingenberg.*|.*klingenthal.*|.*klötze.*|.*klütz.*|.*knittlingen.*|.*koblenz.*|.*kohren-sahlis.*|.*kolbermoor.*|.*kölleda.*|.*köln.*|.*königs wusterhausen.*|.*königsberg in bayern.*|.*königsbrück.*|.*königsbrunn.*|.*königsee.*|.*königslutter.*|.*königstein.*|.*königstein im taunus.*|.*königswinter.*|.*könnern.*|.*konstanz.*|.*konz.*|.*korbach.*|.*korntal-münchingen.*|.*kornwestheim.*|.*korschenbroich.*|.*köthen.*|.*kraichtal.*|.*krakow am see.*|.*kranichfeld.*|.*krautheim.*|.*krefeld.*|.*kremmen.*|.*krempe.*|.*kreuztal.*|.*kronach.*|.*kronberg im taunus.*|.*kröpelin.*|.*kroppenstedt.*|.*krumbach.*|.*kühlungsborn.*|.*kulmbach.*|.*külsheim.*|.*künzelsau.*|.*kupferberg.*|.*kuppenheim.*|.*kusel.*|.*kyllburg.*|.*kyritz.*|.*laage.*|.*laatzen.*|.*ladenburg.*|.*lahnstein.*|.*lahr.*|.*schwarzwald.*|.*laichingen.*|.*lambrecht.*|.*lampertheim.*|.*landau an der isar.*|.*landau in der pfalz.*|.*landsberg.*|.*landsberg am lech.*|.*landshut.*|.*landstuhl.*|.*langelsheim.*|^langen.*|.*langenau.*|.*langenburg.*|.*langenfeld.*|.*langenhagen.*|.*langenselbold.*|.*langenzenn.*|.*langewiesen.*|.*lassan.*|.*laubach.*|.*laucha an der unstrut.*|.*lauchhammer.*|.*lauchheim.*|.*lauda-königshofen.*|.*lauenburg.*|.*lauf an der pegnitz.*|.*laufen.*|.*laufenburg.*|.*lauffen am neckar.*|.*lauingen.*|.*laupheim.*|.*lauscha.*|.*lauta.*|.*lauter.*|.*lebach.*|.*lebus.*|.*leer.*|.*lehesten.*|.*lehrte.*|.*leichlingen.*|.*leimen.*|.*leinefelde-worbis.*|.*leinfelden-echterdingen.*|.*leipheim.*|.*leipzig.*|.*leisnig.*|.*lemgo.*|.*lengefeld.*|.*lengenfeld.*|.*lengerich.*|.*stadt.*|.*lenzen.*|.*leonberg.*|.*leun.*|.*leuna.*|.*leutenberg.*|.*leutershausen.*|.*leutkirch im allgäu.*|.*leverkusen.*|.*lichtenau.*|.*lichtenberg.*|.*lichtenfels.*|.*lichtenstein.*|.*liebenau.*|.*liebenwalde.*|.*lieberose.*|.*limbach-oberfrohna.*|.*limburg an der lahn.*|.*lindau.*|.*lindau.*|.*linden.*|.*lindenberg.*|.*lindenfels.*|.*lindow.*|.*linnich.*|.*linz am rhein.*|.*löbau.*|.*löbejün.*|.*loburg.*|.*löffingen.*|.*lohmar.*|.*lohne.*|.*löhne.*|.*lohr am main.*|.*loitz.*|.*lollar.*|.*lommatzsch.*|.*löningen.*|.*lorch.*|.*lorch.*|.*lörrach.*|.*lorsch.*|.*lößnitz.*|.*löwenstein.*|.*lübbecke.*|.*lübben.*|.*lübbenau.*|.*spreewald.*|.*lübeck.*|.*lübtheen.*|.*lübz.*|.*lüchow.*|.*lucka.*|.*luckau.*|.*luckenwalde.*|.*lüdenscheid.*|.*lüdinghausen.*|.*ludwigsburg.*|.*ludwigsfelde.*|.*ludwigshafen am rhein.*|.*ludwigslust.*|.*lugau.*|.*lügde.*|.*lüneburg.*|.*lünen.*|.*lunzenau.*|.*lütjenburg.*|.*lützen.*|.*lychen.*|.*magdala.*|.*magdeburg.*|.*mahlberg.*|.*mainbernheim.*|.*mainburg.*|.*maintal.*|.*mainz.*|.*malchin.*|.*malchow.*|.*manderscheid.*|.*mannheim.*|.*mansfeld.*|.*marbach am neckar.*|.*marburg.*|.*marienberg.*|.*marienmünster.*|.*markdorf.*|.*markgröningen.*|.*märkisch buchholz.*|.*markkleeberg.*|.*markneukirchen.*|.*markranstädt.*|.*marktbreit.*|.*marktheidenfeld.*|.*marktleuthen.*|.*marktoberdorf.*|.*marktredwitz.*|.*marktsteft.*|.*marlow.*|.*marne$|^marne.*|.*marsberg.*|.*maulbronn.*|.*maxhütte-haidhof.*|.*mayen.*|.*mechernich.*|.*meckenheim.*|.*medebach.*|.*meerane.*|.*meerbusch.*|.*meersburg.*|.*meinerzhagen.*|.*meiningen.*|.*meisenheim.*|.*meißen.*|.*meldorf.*|.*melle.*|.*melsungen.*|.*memmingen.*|.*menden.*|.*mendig.*|.*mengen.*|.*meppen.*|.*merkendorf.*|.*merseburg.*|.*merzig.*|.*meschede.*|.*meßkirch.*|.*meßstetten.*|.*mettmann.*|.*metzingen.*|.*meuselwitz.*|.*meyenburg.*|.*miesbach.*|.*miltenberg.*|.*mindelheim.*|.*minden.*|.*mirow.*|.*mittenwalde.*|.*mitterteich.*|.*mittweida.*|.*möckern.*|.*möckmühl.*|.*moers.*|.*mölln.*|.*mönchengladbach.*|.*monheim.*|.*monheim am rhein.*|.*monschau.*|.*montabaur.*|.*moosburg an der isar.*|.*mörfelden-walldorf.*|.*moringen.*|.*mosbach.*|.*mössingen.*|.*mücheln.*|.*mügeln.*|.*mühlacker.*|.*mühlberg.*|.*mühldorf.*|.*mühlhausen.*|.*mühlheim.*|.*mühltroff.*|.*mülheim.*|.*müllheim.*|.*müllrose.*|.*münchberg.*|.*müncheberg.*|.*münchen.*|.*münchenbernsdorf.*|.*munderkingen.*|.*münsingen.*|.*munster.*|.*münster.*|.*münstermaifeld.*|.*münzenberg.*|.*murrhardt.*|.*mutzschen.*|.*mylau.*|.*nabburg.*|.*nagold.*|.*naila.*|.*nassau.*|.*nastätten.*|.*nauen.*|.*naumburg.*|.*naumburg.*|.*naunhof.*|.*nebra.*|.*neckarbischofsheim.*|.*neckargemünd.*|.*neckarsteinach.*|.*neckarsulm.*|.*nerchau.*|.*neresheim.*|.*netphen.*|.*nettetal.*|.*netzschkau.*|.*neu-isenburg.*|.*neu ulm.*|.*neubrandenburg.*|.*neubukow.*|.*neubulach.*|.*neuburg.*|.*neudenau.*|.*neuenbürg.*|.*neuenburg am rhein.*|.*neuenhaus.*|.*neuenrade.*|.*neuenstein.*|.*neuerburg.*|.*neuffen.*|.*neugersdorf.*|.*neuhaus am rennweg.*|.*neukalen.*|.*neukirchen.*|.*neukirchen-vluyn.*|.*neukloster.*|.*neumark.*|.*neumünster.*|.*neunburg.*|.*neunkirchen.*|.*neuötting.*|.*neuruppin.*|.*neusalza-spremberg.*|.*neusäß.*|.*neuss.*|.*neustrelitz.*|.*neutraubling.*|.*neuwied.*|.*nidda.*|.*niddatal.*|.*nidderau.*|.*nideggen.*|.*niebüll.*|.*niedenstein.*|.*niederkassel.*|.*niedernhall.*|.*niederstetten.*|.*niederstotzingen.*|.*nieheim.*|.*niemegk.*|.*nienburg.*|.*nienburg.*|.*niesky.*|.*nittenau.*|.*norden.*|.*nordenham.*|.*norderney.*|.*norderstedt.*|.*nordhausen.*|.*nordhorn.*|.*nördlingen.*|.*northeim.*|.*nortorf.*|.*nossen.*|.*nürnberg.*|.*nürtingen.*|.*ober-ramstadt.*|.*oberasbach.*|.*oberhausen.*|.*oberhof.*|.*oberkirch.*|.*oberkochen.*|.*oberlungwitz.*|.*obermoschel.*|.*obernburg am main.*|.*oberndorf am neckar.*|.*obernkirchen.*|.*oberriexingen.*|.*obertshausen.*|.*oberursel.*|.*oberviechtach.*|.*oberweißbach.*|.*oberwesel.*|.*oberwiesenthal.*|.*ochsenfurt.*|.*ochsenhausen.*|.*ochtrup.*|.*oderberg.*|.*oebisfelde.*|.*oederan.*|.*oelde.*|.*oelsnitz.*|.*erzgebirge.*|.*erkenschwick.*|.*oerlinghausen.*|.*oestrich-winkel.*|.*oettingen in bayern.*|.*offenbach am main.*|.*offenburg.*|.*ohrdruf.*|.*öhringen.*|.*olbernhau.*|.*oldenburg.*|.*oldenburg in holstein.*|.*olfen.*|.*olpe.*|.*olsberg.*|.*oppenau.*|.*oppenheim.*|.*oranienbaum.*|.*oranienburg.*|.*orlamünde.*|.*ornbau.*|.*ortenberg.*|.*ortrand.*|.*oschatz.*|.*oschersleben.*|.*osnabrück.*|.*osterburg.*|.*osterburken.*|.*osterfeld.*|.*osterhofen.*|.*osterholz-scharmbeck.*|.*osterode am harz.*|.*osterwieck.*|.*ostfildern.*|.*ostheim vor der rhön.*|.*osthofen.*|.*östringen.*|.*ostritz.*|.*otterberg.*|.*otterndorf.*|.*ottweiler.*|.*overath.*|.*owen.*|.*paderborn.*|.*papenburg.*|.*pappenheim.*|.*parchim.*|.*parsberg.*|.*pasewalk.*|.*passau.*|.*pattensen.*|.*pausa.*|.*vogtland.*|.*pegau.*|.*pegnitz.*|.*peine.*|.*peitz.*|.*penig.*|.*penkun.*|.*penzberg.*|.*penzlin.*|.*perleberg.*|.*petershagen.*|.*pfaffenhofen an der ilm.*|.*pfarrkirchen.*|.*pforzheim.*|.*pfreimd.*|.*pfullendorf.*|.*pfullingen.*|.*philippsburg.*|.*pinneberg.*|.*pirmasens.*|.*pirna.*|.*plattling.*|.*plau am see.*|.*plaue.*|.*plauen.*|.*plettenberg.*|.*pleystein.*|.*plochingen.*|.*plön.*|.*pocking.*|.*pohlheim.*|.*polch.*|.*porta westfalica.*|.*pößneck.*|.*potsdam.*|.*pottenstein.*|.*preetz.*|.*premnitz.*|.*prenzlau.*|.*pressath.*|.*prettin.*|.*pretzsch.*|.*preußisch oldendorf.*|.*pritzwalk.*|.*prüm.*|.*pulheim.*|.*pulsnitz.*|.*putbus.*|.*putlitz.*|.*püttlingen.*|.*quakenbrück.*|.*quedlinburg.*|.*querfurt.*|.*quickborn.*|.*rabenau.*|.*radeberg.*|.*radebeul.*|.*radeburg.*|.*radegast.*|.*radevormwald.*|.*radolfzell am bodensee.*|.*raguhn.*|.*rahden.*|.*rain.*|.*ramstein-miesenbach.*|.*ranis.*|.*ransbach.*|.*baumbach.*|.*rastatt.*|.*rastenberg.*|.*rathenow.*|.*ratingen.*|.*ratzeburg.*|.*rauenberg.*|.*raunheim.*|.*rauschenberg.*|.*ravensburg.*|.*ravenstein.*|.*recklinghausen.*|.*rees.*|.*regen.*|.*regensburg.*|.*regis breitingen.*|.*rehau.*|.*rehburg-loccum.*|.*rehna.*|.*reichelsheim.*|.*reichenbach.*|.*reinbek.*|.*reinfeld.*|.*reinheim.*|.*remagen.*|.*remda-teichel.*|.*remscheid.*|.*remseck am neckar.*|.*renchen.*|.*rendsburg.*|.*rennerod.*|.*renningen.*|.*rerik.*|.*rethem.*|.*reutlingen.*|.*rheda-wiedenbrück.*|.*rhede.*|.*rheinau.*|.*rheinbach.*|.*rheinberg.*|.*rheine.*|.*rheinfelden.*|.*rheinsberg.*|.*rheinstetten.*|.*rhens.*|.*rhinow.*|.*ribnitz-damgarten.*|.*richtenberg.*|.*riedenburg.*|.*riedlingen.*|.*rieneck.*|.*riesa.*|.*rietberg.*|.*rinteln.*|.*röbel.*|.*müritz.*|.*rochlitz.*|.*rockenhausen.*|.*rodalben.*|.*rodenberg.*|.*rödental.*|.*rödermark.*|.*rodewisch.*|.*rodgau.*|.*roding.*|.*römhild.*|.*romrod.*|.*ronneburg.*|.*ronnenberg.*|.*rosbach.*|.*rosenfeld.*|.*rosenheim.*|.*rosenthal.*|.*rösrath.*|.*roßlau.*|.*roßleben.*|.*roßwein.*|.*rostock.*|.*rotenburg.*|.*rotenburg an der fulda.*|.*roth.*|.*rötha.*|.*röthenbach.*|.*rothenburg.*|.*rothenfels.*|.*rottenburg.*|.*rottenburg am neckar.*|.*röttingen.*|.*rottweil.*|.*rötz.*|.*rüdesheim.*|.*ruhla.*|.*ruhland.*|.*runkel.*|.*rüsselsheim.*|.*rüthen.*|.*saalburg.*|.*ebersdorf.*|.*saalfeld.*|.*saale.*|.*saarbrücken.*|.*saarburg.*|.*saarlouis.*|.*sachsenhagen.*|.*sachsenheim.*|.*salzgitter.*|.*salzkotten.*|.*salzwedel.*|.*sandau.*|.*sandersleben.*|.*sangerhausen.*|.*sankt andreasberg.*|.*sankt augustin.*|.*sankt goar.*|.*sankt goarshausen.*|.*sarstedt.*|.*sassenberg.*|.*sassnitz.*|.*sayda.*|.*schafstädt.*|.*schalkau.*|.*schauenstein.*|.*scheer.*|.*scheibenberg.*|.*scheinfeld.*|.*schelklingen.*|.*schenefeld.*|.*scheßlitz.*|.*schieder-schwalenberg.*|.*schildau.*|.*schillingsfürst.*|.*schiltach.*|.*schirgiswalde.*|.*schkeuditz.*|.*schkölen.*|.*schleiden.*|.*schleiz.*|.*schleswig.*|.*schlettau.*|.*schleusingen.*|.*schlieben.*|.*schlitz.*|.*schloß holte-stukenbrock.*|.*schlotheim.*|.*schlüchtern.*|.*schlüsselfeld.*|.*schmalkalden.*|.*schmallenberg.*|.*schmölln.*|.*schnackenburg.*|.*schnaittenbach.*|.*schneeberg.*|.*schneverdingen.*|.*schömberg.*|.*schönau.*|.*schönau im schwarzwald.*|.*schönberg.*|.*schönebeck.*|.*schöneck.*|.*schönewalde.*|.*schongau.*|.*schöningen.*|.*schönsee.*|.*schönwald.*|.*schopfheim.*|.*schöppenstedt.*|.*schorndorf.*|.*schortens.*|.*schotten.*|.*schramberg.*|.*schraplau.*|.*schriesheim.*|.*schrobenhausen.*|.*schrozberg.*|.*schüttorf.*|.*schwaan.*|.*schwabach.*|.*schwäbisch gmünd.*|.*schwäbisch hall.*|.*schwabmünchen.*|.*schwaigern.*|.*schwalbach am taunus.*|.*schwandorf.*|.*schwanebeck.*|.*schwarzenbach.*|.*schwarzenbek.*|.*schwarzenberg.*|.*schwarzenborn.*|.*schwarzheide.*|.*schwedt.*|.*schweich.*|.*schweinfurt.*|.*schwelm.*|.*schwerin.*|.*schwerte.*|.*schwetzingen.*|.*sebnitz.*|.*seehausen.*|.*seehausen.*|.*seelow.*|.*seelze.*|.*seesen.*|.*sehnde.*|.*seifhennersdorf.*|.*selb.*|.*selbitz.*|.*selm.*|.*selters.*|.*senden.*|.*sendenhorst.*|.*senftenberg.*|.*seßlach.*|.*siegburg.*|.*siegen.*|.*sigmaringen.*|.*simbach am inn.*|.*simmern.*|.*hunsrück.*|.*sindelfingen.*|.*singen.*|.*sinsheim.*|.*sinzig.*|.*soest.*|.*solingen.*|.*solms.*|.*soltau.*|.*sömmerda.*|.*sondershausen.*|.*sonneberg.*|.*sonnewalde.*|.*sonthofen.*|.*sontra.*|.*spaichingen.*|.*spalt.*|.*spangenberg.*|.*spenge.*|.*speyer.*|.*spremberg.*|.*sprockhövel.*|.*blasien.*|.*georgen.*|.*ingbert.*|.*st. wendel.*|.*stade.*|.*starnberg.*|.*staßfurt.*|.*staufen im breisgau.*|.*staufenberg.*|.*stavenhagen.*|.*steinach.*|.*steinau.*|.*steinbach.*|.*steinfurt.*|.*steinheim.*|.*stendal.*|.*sternberg.*|.*stockach.*|.*stolberg.*|.*stollberg.*|.*stolpen.*|.*storkow.*|.*stößen.*|.*straelen.*|.*stralsund.*|.*strasburg.*|.*straubing.*|.*strausberg.*|.*strehla.*|.*stromberg.*|.*stühlingen.*|.*stutensee.*|.*stuttgart.*|.*suhl.*|.*sulingen.*|.*sulz am neckar.*|.*sulzbach-rosenberg.*|.*sulzbach.*|.*sulzburg.*|.*sundern (sauerland).*|.*süßen.*|.*syke.*|.*tambach.*|.*dietharz.*|.*tangerhütte.*|.*tangermünde.*|.*tann.*|.*tanna.*|.*tauberbischofsheim.*|.*taucha.*|.*taunusstein.*|.*tecklenburg.*|.*tegernsee.*|.*telgte.*|.*teltow.*|.*templin.*|.*tengen.*|.*tessin.*|.*teterow.*|.*tettnang.*|.*teublitz.*|.*teuchern.*|.*teupitz.*|.*teuschnitz.*|.*thale.*|.*thalheim.*|.*thannhausen.*|.*tharandt.*|.*themar.*|.*thum.*|.*tirschenreuth.*|.*titisee.*|.*tittmoning.*|.*todtnau.*|.*töging.*|.*tönisvorst.*|.*tönning.*|.*torgau.*|.*torgelow.*|.*tornesch.*|.*traben-trarbach.*|.*traunreut.*|.*traunstein.*|.*trebbin.*|.*trebsen.*|.*treffurt.*|.*trendelburg.*|.*treuchtlingen.*|.*treuen.*|.*treuenbrietzen.*|.*triberg im schwarzwald.*|.*tribsees.*|.*trier.*|.*triptis.*|.*trochtelfingen.*|.*troisdorf.*|.*trossingen.*|.*trostberg.*|.*tübingen.*|.*tuttlingen.*|.*twistringen.*|.*übach-palenberg.*|.*überlingen.*|.*uebigau-wahrenbrück.*|.*ueckermünde.*|.*uelzen.*|.*uetersen.*|.*uffenheim.*|.*uhingen.*|.*ulm.*|.*ulrichstein.*|.*unna.*|.*unstrut.*|.*schleißheim.*|.*usedom.*|.*usingen.*|.*uslar.*|.*vacha.*|.*vaihingen an der enz.*|.*vallendar.*|.*varel.*|.*vechta.*|.*velbert.*|.*velburg.*|.*velden.*|.*vellberg.*|.*vellmar.*|.*velten.*|.*verden.*|.*versmold.*|.*vetschau.*|.*viechtach.*|.*vienenburg.*|.*viernheim.*|.*viersen.*|.*villingen-schwenningen.*|.*vilsbiburg.*|.*vilseck.*|.*vilshofen an der donau.*|.*visselhövede.*|.*vlotho.*|.*voerde.*|.*vogtsburg.*|.*kaiserstuhl.*|.*vohburg.*|.*vohenstrauß.*|.*vöhrenbach.*|.*vöhringen.*|.*volkach.*|.*völklingen.*|.*volkmarsen.*|.*vreden.*|.*wachenheim an der weinstraße.*|.*wächtersbach.*|^wadern.*|.* wadern.*|.*waghäusel.*|.*wahlstedt.*|.*waiblingen.*|.*waischenfeld.*|.*waldbröl.*|.*waldeck.*|.*waldenbuch.*|.*waldenburg.*|.*waldenburg.*|.*waldershof.*|.*waldheim.*|.*waldkappel.*|.*waldkirch.*|.*waldkirchen.*|.*waldkraiburg.*|.*waldmünchen.*|.*waldsassen.*|.*waldshut-tiengen.*|.*walldorf.*|.*walldürn.*|.*wallenfels.*|.*walsrode.*|.*waltershausen.*|.*waltrop.*|.*wanfried.*|.*wangen im allgäu.*|.*wanzleben.*|.*warburg.*|.*waren.*|.*warendorf.*|.*warin.*|.*warstein.*|.*wassenberg.*|.*wasserburg am inn.*|.*wassertrüdingen.*|.*wasungen.*|.*wedel.*|.*weener.*|.*wegberg.*|.*wegeleben.*|.*weida.*|.*weiden in der oberpfalz.*|.*weikersheim.*|.*weil am rhein.*|.*weilburg.*|.*weilheim.*|.*weimar.*|.*weinheim.*|.*weinsberg.*|.*weismain.*|.*weißenberg.*|.*weißenburg.*|.*weißenfels.*|.*weißenhorn.*|.*weißensee.*|.*weißenthurm.*|.*weißwasser.*|.*weiterstadt.*|.*welzheim.*|.*welzow.*|.*wemding.*|.*wendlingen.*|.*werben.*|.*werdau.*|.*werder.*|.*werdohl.*|.*werl.*|.*wermelskirchen.*|.*wernau.*|.*werne.*|.*werneuchen.*|.*wernigerode.*|.*werra.*|.*wertheim.*|.*werther.*|.*wertingen.*|.*wesel.*|.*wesenberg.*|.*wesselburen.*|.*wesseling.*|.*westerburg.*|.*westerland.*|.*westerstede.*|.*wetter.*|.*wetter.*|.*wettin.*|.*wetzlar.*|.*widdern.*|.*wiehe.*|.*wiehl.*|.*wiesbaden.*|.*wiesensteig.*|.*wiesloch.*|.*wiesmoor.*|.*wildberg.*|.*wildemann.*|.*wildenfels.*|.*wildeshausen.*|.*wilhelmshaven.*|.*wilkau-haßlau.*|.*willebadessen.*|.*willich.*|.*wilsdruff.*|.*wilster.*|.*wilthen.*|.*windischeschenbach.*|.*windsbach.*|.*winnenden.*|.*winsen.*|.*winterberg.*|.*wipperfürth.*|.*wirges.*|.*wismar.*|.*wissen.*|.*witten.*|.*wittenberg.*|.*wittenberge.*|.*wittenburg.*|.*wittichenau.*|.*wittingen.*|.*wittlich.*|.*wittmund.*|.*wittstock.*|.*dosse.*|.*witzenhausen.*|.*woldegk.*|.*wolfach.*|.*wolfen.*|.*wolfenbüttel.*|.*wolfhagen.*|.*wolframs-eschenbach.*|.*wolfratshausen.*|.*wolfsburg.*|.*wolfstein.*|.*wolgast.*|.*wolkenstein.*|.*wolmirstedt.*|.*wörlitz.*|.*worms.*|.*wörth.*|.*wriezen.*|.*wülfrath.*|.*wunsiedel.*|.*wunstorf.*|.*wuppertal.*|.*würselen.*|.*wurzbach.*|.*würzburg.*|.*wurzen.*|.*wustrow.*|.*wyk auf föhr.*|.*xanten.*|.*zahna.*|.*zarrentin am schaalsee.*|.*zehdenick.*|.*zeil am main.*|.*zeitz.*|.*zell am.*|.*zell im.*|.*mehlis.*|.*zerbst.*|.*zeulenroda.*|.*zeven.*|.*ziegenrück.*|.*zierenberg.*|.*ziesar.*|.*zirndorf.*|.*zittau.*|.*zöblitz.*|.*zörbig.*|.*zossen.*|.*zschopau.*|.*zülpich.*|.*zweibrücken.*|.*zwenkau.*|.*zwickau.*|.*zwiesel.*|.*zwingenberg.*|.*zwönitz.*', kw_lower):
                intents.append("regional:CITY")

            # User Intent: regional:COUNTRY
            if re.search(r'.*belgien.*|.*bulgarien.*|.*dänemark.*|.*deutschland.*|.*estland.*|.*finnland.*|.*frankreich.*|.*griechenland.*|.*irland.*|.*italien.*|.*kroatien.*|.*lettland.*|.*litauen.*|.*luxemburg.*|.*malta.*|.*niederlande.*|.*österreich.*|.*polen.*|.*portugal.*|.*rumänien.*', kw_lower):
                intents.append("regional:COUNTRY")
                
        return ", ".join(intents) if intents else "undefined"

    df['Cluster'] = df['Keyword'].apply(get_cluster)
    df['Search Intent'] = df['Keyword'].apply(get_intent)

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
    
    # Calculate percentage change for the delta of Net Click Change
    total_clicks_old = df['Clicks_Old'].sum()
    pct_change = (net_clicks / total_clicks_old * 100) if total_clicks_old > 0 else 0.0
    pct_sign = " %" if lang == "DE" else "%"
    if net_clicks > 0:
        pct_change_formatted = f"+{format_num(pct_change, decimal_places=1)}{pct_sign}"
    elif net_clicks < 0:
        pct_change_formatted = f"{format_num(pct_change, decimal_places=1)}{pct_sign}"
    else:
        pct_change_formatted = f"{format_num(0.0, decimal_places=1)}{pct_sign}"
        
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t["kpi_lost_total"], f"-{format_num(total_clicks_lost)}")
    with col2:
        st.metric(t["kpi_net_change"], f"+{format_num(net_clicks)}" if net_clicks > 0 else format_num(net_clicks), delta=pct_change_formatted)
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
            
            best_val = best_cluster['Clicks Change']
            best_delta = f"+{format_num(best_val)} {t['clicks']}" if best_val > 0 else f"{format_num(best_val)} {t['clicks']}"
            
            worst_val = worst_cluster['Clicks Change']
            worst_delta = f"+{format_num(worst_val)} {t['clicks']}" if worst_val > 0 else f"{format_num(worst_val)} {t['clicks']}"
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric(t["kpi_best_cluster"], best_cluster['Cluster'], best_delta)
            with c2:
                st.metric(t["kpi_worst_cluster"], worst_cluster['Cluster'], worst_delta)
                
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
            losers_exploded = df[df['Clicks Loss'] > 0].copy()
            cluster_vol = losers_exploded.groupby('Cluster').agg(
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
                cluster_df = losers[losers['Cluster'].apply(lambda x: isinstance(x, list) and any(c in selected_clusters for c in x))]
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
            display_winners = winners[
                (winners['Position Change'] > 0) &
                (~((winners['Position_New'] > 11) & (winners['Position Change'] < 9)))
            ]
            
            if not display_winners.empty:
                display_styled_dataframe(display_winners[['Keyword', 'Position Change', 'Position_Old', 'Position_New', 'Clicks Gain', 'Clicks_Old', 'Clicks_New']], sort_col='Clicks Gain')
                
                fig_win = px.scatter(
                    display_winners, x="Clicks Gain", y="Position_New", 
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
        else:
            st.info(t["win_empty"])

    with tab6:
        st.subheader(t["ad_sub"])
        all_cols = ['Cluster', 'Search Intent', 'Keyword', 'Change', 'Position Change', 'Clicks Change', 'Position_Old', 'Position_New', 'Impressions_Old', 'Impressions_New', 'Clicks_Old', 'Clicks_New']
        
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            all_clusters = sorted(df['Cluster'].dropna().unique().tolist())
            sel_cluster = st.multiselect(t["ad_filter_cluster"], options=all_clusters)
        with col_f2:
            # Gather unique intents from strings that might be comma-separated
            # However, since Intent is a string e.g. 'KNOW, DO', we should extract individual
            all_intents = set()
            for i in df['Search Intent'].dropna():
                for piece in i.split(', '):
                    all_intents.add(piece)
            all_intents = sorted(list(all_intents))
            sel_intent = st.multiselect("Search Intent", options=all_intents)
        with col_f3:
            all_changes = sorted(df['Change'].dropna().unique().tolist())
            sel_change = st.multiselect(t["ad_filter_change"], options=all_changes)
        with col_f4:
            search_kw = st.text_input(t["ad_filter_kw"], key="ad_kw")
            
        f_df = df[all_cols].copy()
        if sel_cluster:
            f_df = f_df[f_df['Cluster'].isin(sel_cluster)]
        if sel_intent:
            f_df = f_df[f_df['Search Intent'].apply(lambda x: any(c in x for c in sel_intent))]
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
