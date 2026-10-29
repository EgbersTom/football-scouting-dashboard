import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns

st.set_page_config(page_title="Leverkusen Scouting Dashboard 2023/24", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        min-width: 380px !important;
        max-width: 450px !important;
    }
    div[data-baseweb="select"] * {
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER & TROLL/DATENBASIS-HINWEIS ---
st.title("⚽ Bayer 04 Leverkusen – Scouting Dashboard")
st.caption("Bundesliga Saison 2023/24 | Data Analytics & Event-Analyse")

st.info(
    "ℹ️ **Datenbasis:** Dieser Datensatz umfasst die **34 Bundesliga-Spiele von Bayer 04 Leverkusen** "
    "aus der Ungeschlagen-Saison 2023/24 (StatsBomb Open Data). Leistungsdaten von Gegenspielern "
    "(z. B. Harry Kane, Dani Olmo) beziehen sich ausschließlich auf deren Direktduelle gegen Leverkusen."
)

@st.cache_resource
def get_db_engine():
    return create_engine("sqlite:///football_scouting.db")

engine = get_db_engine()

# --- DATENBANK-ABFRAGEN ---
@st.cache_data
def load_matches():
    query = "SELECT match_id, match_date, home_team, away_team, home_score, away_score FROM matches ORDER BY match_date ASC;"
    return pd.read_sql(query, engine)

@st.cache_data
def load_pass_data():
    query = """
    SELECT match_id, player, team, location_x, location_y, under_pressure, pass_outcome
    FROM events 
    WHERE type = 'Pass' AND location_x IS NOT NULL AND location_y IS NOT NULL;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def load_shot_data():
    query = """
    SELECT match_id, player, team, location_x, location_y, under_pressure, shot_statsbomb_xg, shot_outcome
    FROM events 
    WHERE type = 'Shot' AND location_x IS NOT NULL AND location_y IS NOT NULL;
    """
    return pd.read_sql(query, engine)

matches_df = load_matches()
df_passes = load_pass_data()
df_shots = load_shot_data()

# --- SIDEBAR FILTER ---
st.sidebar.header("Navigation & Filter")

match_options = ["Alle 34 Leverkusen-Spiele (Gesamte Saison)"] + [
    f"{row['home_team']} vs. {row['away_team']} ({row['home_score']}:{row['away_score']}) | {row['match_date']}"
    for _, row in matches_df.iterrows()
]
selected_match_option = st.sidebar.selectbox("Spielauswahl", match_options)

# Spiel-Filter anwenden
if selected_match_option != "Alle 34 Leverkusen-Spiele (Gesamte Saison)":
    selected_idx = match_options.index(selected_match_option) - 1
    selected_match_id = matches_df.iloc[selected_idx]['match_id']
    df_passes = df_passes[df_passes['match_id'] == selected_match_id]
    df_shots = df_shots[df_shots['match_id'] == selected_match_id]

# --- HAUPT-TABS DEFINIEREN ---
tab_pass, tab_shot = st.tabs(["📊 Pass-Analysen", "🎯 Schuss- & xG-Analyse"])


# ==========================================
# TAB 1: PASS-ANALYSEN
# ==========================================
with tab_pass:
    mode = st.sidebar.radio("Modus (Pässe)", ["Einzelspieler", "Spieler-Vergleich (Side-by-Side)"], key="pass_mode")
    pressure_filter = st.sidebar.radio("Gegnerdruck (Pässe)", ["Alle Pässe", "Nur unter Druck", "Ohne Druck"], key="pass_pressure")
    view_mode = st.sidebar.selectbox("Visualisierung (Pässe)", ["Pass-Punkte", "Pass-Heatmap (Dichte)"], key="pass_view")

    # Druck-Filter
    if pressure_filter == "Nur unter Druck":
        df_passes_filtered = df_passes[df_passes['under_pressure'] == 1].copy()
    elif pressure_filter == "Ohne Druck":
        df_passes_filtered = df_passes[df_passes['under_pressure'] != 1].copy()
    else:
        df_passes_filtered = df_passes.copy()

    df_passes_filtered['success'] = df_passes_filtered['pass_outcome'].isna()
    pass_players = sorted(df_passes['player'].dropna().unique())

    def draw_pass_pitch(player_df, view_mode):
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#1e1e1e')
        ax.set_facecolor('#1e1e1e')

        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e1e1e', line_color='#c7c7c7', linewidth=1.5)
        pitch.draw(ax=ax)

        if view_mode == "Pass-Punkte":
            successful = player_df[player_df['success'] == True]
            unsuccessful = player_df[player_df['success'] == False]
            
            pitch.scatter(successful['location_x'], successful['location_y'], ax=ax, c='#2ecc71', edgecolors='black', s=60, label='Angekommen', alpha=0.7)
            pitch.scatter(unsuccessful['location_x'], unsuccessful['location_y'], ax=ax, c='#e74c3c', edgecolors='black', s=60, label='Fehlpass', alpha=0.7, marker='X')
            ax.legend(facecolor='#1e1e1e', labelcolor='white', loc='upper left', fontsize='small')

        elif view_mode == "Pass-Heatmap (Dichte)":
            if len(player_df) >= 3:
                sns.kdeplot(x=player_df['location_x'], y=player_df['location_y'], fill=True, cmap='magma', alpha=0.6, thresh=0.05, ax=ax, cbar=True, cbar_kws={'shrink': 0.75})
                if len(ax.collections) > 0 and hasattr(ax.collections[0], 'colorbar'):
                    cbar = ax.collections[0].colorbar
                    if cbar:
                        cbar.ax.yaxis.label.set_color('white')
                        cbar.ax.tick_params(colors='white')
                        vmin, vmax = cbar.mappable.get_clim()
                        cbar.set_ticks([vmin + 0.15 * (vmax - vmin), vmax - 0.15 * (vmax - vmin)])
                        cbar.set_ticklabels(['Wenig Aktivität', 'Hohe Aktivität'])
            else:
                ax.text(60, 40, "Zu wenige Datenpunkte", color="white", ha="center", va="center")

        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    if not pass_players:
        st.warning("Keine Passdaten für die aktuelle Auswahl vorhanden.")
    elif mode == "Einzelspieler":
        default_idx = pass_players.index("Florian Wirtz") if "Florian Wirtz" in pass_players else 0
        selected_player = st.selectbox("Spieler wählen (Pässe)", pass_players, index=default_idx)
        
        p_data = df_passes_filtered[df_passes_filtered['player'] == selected_player]
        total = len(p_data)
        success_cnt = p_data['success'].sum() if total > 0 else 0
        quote = round((success_cnt / total * 100), 1) if total > 0 else 0.0

        c1, c2, c3 = st.columns(3)
        c1.metric("Pässe Gespielt", total)
        c2.metric("Angekommen", success_cnt)
        c3.metric("Passquote", f"{quote} %")

        draw_pass_pitch(p_data, view_mode)
    else:
        p1_idx = pass_players.index("Florian Wirtz") if "Florian Wirtz" in pass_players else 0
        p2_idx = pass_players.index("Granit Xhaka") if "Granit Xhaka" in pass_players else (1 if len(pass_players) > 1 else 0)

        col1, col2 = st.columns(2)
        with col1:
            player1 = st.selectbox("Spieler 1", pass_players, index=p1_idx, key="p1_pass")
            p1_data = df_passes_filtered[df_passes_filtered['player'] == player1]
            p1_total = len(p1_data)
            p1_success = p1_data['success'].sum() if p1_total > 0 else 0
            p1_quote = round((p1_success / p1_total * 100), 1) if p1_total > 0 else 0.0
            st.markdown(f"**Gespielt:** {p1_total} | **Angekommen:** {p1_success} | **Quote:** `{p1_quote} %`")
            draw_pass_pitch(p1_data, view_mode)

        with col2:
            player2 = st.selectbox("Spieler 2", pass_players, index=p2_idx, key="p2_pass")
            p2_data = df_passes_filtered[df_passes_filtered['player'] == player2]
            p2_total = len(p2_data)
            p2_success = p2_data['success'].sum() if p2_total > 0 else 0
            p2_quote = round((p2_success / p2_total * 100), 1) if p2_total > 0 else 0.0
            st.markdown(f"**Gespielt:** {p2_total} | **Angekommen:** {p2_success} | **Quote:** `{p2_quote} %`")
            draw_pass_pitch(p2_data, view_mode)


# ==========================================
# TAB 2: SCHUSS- & xG-ANALYSE
# ==========================================
with tab_shot:
    st.subheader("🎯 Shot-Map & Expected Goals (xG) Analyse")
    
    shot_players = sorted(df_shots['player'].dropna().unique())
    selected_shooter = st.selectbox("Spieler für Schuss-Analyse wählen (oder 'Alle Spieler')", ["Alle Spieler"] + shot_players)

    # Daten filtern
    if selected_shooter != "Alle Spieler":
        shooter_df = df_shots[df_shots['player'] == selected_shooter].copy()
        match_count = shooter_df['match_id'].nunique()
        st.caption(f"📊 **Spiele im Datensatz:** {selected_shooter} wurde in **{match_count} Spiel(en)** erfasst.")
    else:
        shooter_df = df_shots.copy()

    # Torkennzahlen
    total_shots = len(shooter_df)
    goals = len(shooter_df[shooter_df['shot_outcome'] == 'Goal'])
    total_xg = round(pd.to_numeric(shooter_df['shot_statsbomb_xg'], errors='coerce').sum(), 2)
    xg_per_shot = round(total_xg / total_shots, 2) if total_shots > 0 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Schüsse Gesamt", total_shots)
    m2.metric("Tore Erzielt", goals)
    m3.metric("Expected Goals (xG)", total_xg)
    m4.metric("xG pro Schuss", xg_per_shot)

    # SHOT MAP ZEICHNEN (Halbfeld-Ansicht)
    def draw_shot_pitch(shot_df):
        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor('#1e1e1e')
        ax.set_facecolor('#1e1e1e')

        # Half-Pitch Fokus auf das gegnerische Tor
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e1e1e', line_color='#c7c7c7', linewidth=1.5, half=True)
        pitch.draw(ax=ax)

        if len(shot_df) > 0:
            shot_df['shot_statsbomb_xg'] = pd.to_numeric(shot_df['shot_statsbomb_xg'], errors='coerce').fillna(0.02)
            
            goals_df = shot_df[shot_df['shot_outcome'] == 'Goal']
            no_goals_df = shot_df[shot_df['shot_outcome'] != 'Goal']

            size_no_goals = no_goals_df['shot_statsbomb_xg'] * 700 + 50
            size_goals = goals_df['shot_statsbomb_xg'] * 700 + 50

            # Fehlschüsse / Pariert (Rot / Kreise)
            pitch.scatter(
                no_goals_df['location_x'], no_goals_df['location_y'],
                ax=ax, c='#e74c3c', edgecolors='black', s=size_no_goals, label='Kein Tor', alpha=0.6
            )

            # Tore (Grüne Sterne)
            pitch.scatter(
                goals_df['location_x'], goals_df['location_y'],
                ax=ax, c='#2ecc71', edgecolors='black', s=size_goals, label='Tor ⚽', alpha=0.9, marker='*'
            )

            ax.legend(facecolor='#1e1e1e', labelcolor='white', loc='upper left', fontsize='medium')
        else:
            ax.text(90, 40, "Keine Schussdaten vorhanden", color="white", ha="center", va="center")

        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    col_map, col_table = st.columns([1.2, 1])

    with col_map:
        st.markdown("**Shot-Map (Punktgröße = xG-Wert)**")
        draw_shot_pitch(shooter_df)

    with col_table:
        st.markdown("**Top-Chancen & Torgefahr (Leaderboard)**")
        if len(df_shots) > 0:
            df_shots['shot_statsbomb_xg_num'] = pd.to_numeric(df_shots['shot_statsbomb_xg'], errors='coerce').fillna(0.0)
            
            leaderboard = df_shots.groupby(['player', 'team']).agg(
                Spiele=('match_id', 'nunique'),
                Schüsse=('shot_statsbomb_xg_num', 'count'),
                Tore=('shot_outcome', lambda x: (x == 'Goal').sum()),
                xG_Gesamt=('shot_statsbomb_xg_num', 'sum')
            ).reset_index()
            
            leaderboard['xG_Gesamt'] = leaderboard['xG_Gesamt'].round(2)
            leaderboard = leaderboard.rename(columns={'player': 'Spieler', 'team': 'Team'})
            leaderboard = leaderboard.sort_values(by='xG_Gesamt', ascending=False)
            
            st.dataframe(leaderboard, use_container_width=True, hide_index=True)