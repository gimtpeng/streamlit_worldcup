# Specification: Streamlit Football Dashboard & Playable World Cup Game

## 1. Project Overview
A Streamlit-based web application providing real-time FIFA World Cup data, dynamic squad visualizations, and an **interactive, playable 2D football mini-game** embedded directly into the 48-team World Cup Mode.

---

## 2. Key Architecture & Features

### Feature 1: Live FIFA Rankings with Auto-Refresh
*   **Data Display:** Show current FIFA world rankings in an interactive table.
*   **Auto-Refresh:** Automatically refresh the page every 1 hour using `st_autorefresh` for live data sync.

### Feature 2: Interactive Pitch Visualizer (Korean)
*   **Trigger:** Clicking a specific nation in the FIFA ranking list triggers the pitch visualizer.
*   **Content:** Overlay the selected team's Manager (감독), Starting Lineup (선발 명단), and Substitutes (교체 명단) in **Korean** over a football field graphic.

### Feature 3: Directly Playable 2D Football Mini-Game (No Simulation)
*   **Implementation:** Embed an HTML5 Canvas + JavaScript game via `st.components.v1.html`.
*   **Controls:** 
    *   **Movement:** Arrow keys or WASD to control the selected player character.
    *   **Action:** Spacebar to shoot/pass toward the AI goal.
*   **Gameplay:** 
    *   The user controls a player representing their chosen nation.
    *   AI characters act as defenders and a goalkeeper, trying to block or steal the ball.
    *   Score goals within a limited time to win the match. Match stats (Score, Time) are synced back to Streamlit using `window.parent.postMessage` or Streamlit component bi-directional communication.

### Feature 4: 2026 Format World Cup Mode (48 Teams with Playable Matches)
*   **Tournament Scale:** 48 Nations split into 12 groups (Groups A to L).
*   **Interactive Group Draw:** Seed teams based on FIFA rankings and perform a random group draw upon clicking `[조 추첨 시작]`.
*   **Group Stage & 3rd-Place Wildcard Logic:**
    *   The user plays their country's matches directly via the 2D mini-game. Other group matches can be quick-resolved.
    *   Top 2 teams from each group advance automatically (24 teams).
    *   **Wildcard Tracker:** Evaluate all 12 third-placed teams (Points -> Goal Difference -> Goals). The **top 8 third-place teams** advance.
*   **Round of 32 Knockout Bracket:** A single-elimination tournament leading to the Finals, where the user must play and win each round to progress.

---

## 3. Technical Requirements & Session State Mapping
*   **Framework:** Streamlit (`python-dotenv`, `pandas`, `plotly`, `st-autorefresh`).
*   **Frontend Engine:** HTML5 Canvas, JS EventListeners (keydown, keyup) for smooth player movement, requestAnimationFrame for game loops.
*   **State Management:** Use `st.session_state` to strictly persist tournament groups, bracket progressions, and user match results.
*   **Language:** The entire user interface and game text must render natively in **Korean**.