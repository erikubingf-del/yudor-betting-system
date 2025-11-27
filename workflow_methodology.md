# Yudor Betting System: Phase 2 Methodology & Workflow

## 1. Scientific Philosophy
The core objective of the Yudor System is to calculate the **True Probability** of a match outcome more accurately than the market (Bookmakers).

*   **The Edge**: `Edge = (Market Odds / True Odds) - 1`
*   **The Goal**: Identify bets where `Edge > 5%` (Positive Expected Value).
*   **Asian Handicap (AH)**: We focus on AH lines because they reduce the outcome to a binary (Win/Loss) or near-binary state, eliminating the "Draw" complexity in terms of payout structure.
    *   *Example*: If we calculate the "True Line" is -0.75 but the market offers -0.25, we have a massive edge on the favorite.

## 2. The Phase 2 Pipeline (Automated Analysis)
The system operates "blindly" to generate unbiased predictions based on data triangulation.

### A. Data Triangulation (The "Three Pillars")
1.  **Hard Stats (Quantitative)**:
    *   **FBref**: Granular match data (xG, Possession, Passes).
    *   **FootyStats**: Season-long trends (Form, BTTS %, Season xG).
    *   **API-Football**: Validator for fixtures, injuries, and predictions.
2.  **Soft Context (Qualitative)**:
    *   **News Scrapers**: BBC (UK), GloboEsporte (Brazil), Serper (Global).
    *   **Sentiment Analysis**: LLM/Keyword analysis of news to detect "Crisis", "Motivation", or "Injuries".
3.  **Lineups**:
    *   **FotMob/API-Football**: Confirmed or predicted lineups to adjust for key player absence.

### B. Modeling Engine
Currently, we use a **Poisson Distribution Model** adjusted by **Q-Scores** (Quality Scores derived from the data).
*   **Base**: Poisson distribution using Season Goals For/Against.
*   **Adjustment**: Q-Scores (Form, Motivation, Injuries) shift the expected goal counts (lambda).
*   **Future State**: As we collect data, this will be replaced by a **Logistic Regression / Gradient Boosting Model** trained on our specific Q-Scores.

## 3. The Scientific Workflow (The Loop)

### Step 1: Batch Analysis (Automated)
*   **Input**: A list of upcoming matches (`matches_batch.txt`).
*   **Process**: The `Phase2Orchestrator` runs overnight or on-demand.
*   **Output**: `phase2_results.json` containing:
    *   Calculated "True Odds".
    *   Identified "Value Bets" (where Edge > Threshold).
    *   Confidence Score (Data quality check).

### Step 2: Manual Review (Human Filter)
*   **Role**: You (The User) act as the final "Portfolio Manager".
*   **Action**: Review the "Value Bets" identified by the system.
*   **Decision**:
    *   *Approve*: The stats make sense, context is solid. -> **BET**.
    *   *Reject*: The model missed a key factor (e.g., "Manager just sacked"). -> **SKIP**.

### Step 3: Ledger Entry (Data Logging)
*   **Tool**: `ledger_manager.py` (or Airtable).
*   **Record**:
    *   Match ID
    *   System Prediction (e.g., AH -0.5)
    *   System Confidence
    *   Market Odds
    *   Stake
    *   **Status**: `Pending`

### Step 4: Result & Post-Mortem (Learning)
*   **Activation**: After matches conclude.
*   **Process**:
    1.  Update Ledger with Scores.
    2.  Calculate P/L (Profit/Loss).
    3.  **The "Why" Analysis**:
        *   *Win*: Did we win for the right reasons? (Model validated).
        *   *Loss*: Why? Variance? Or Systemic Error?
            *   *Example*: "Model consistently overestimates Home teams in Brazil Serie B".
*   **Feedback**:
    *   If a systemic error is found (statistically significant, n > 20 matches), we tweak the **Q-Score Weights** or **Model Parameters**.

## 4. Long-Term Evolution (Machine Learning)
We are building a dataset for the future.
*   **Inputs (X)**: Q-Scores, Sentiment, xG Diff, Elo Diff.
*   **Target (y)**: Match Result (Home/Draw/Away) and AH Outcome (Win/Loss).
*   **Trigger**: Once we have **100+ logged matches**, we switch from "Poisson + Heuristics" to "Trained ML Model".
    *   The system will "learn" which Q-Scores actually predict winners.

### Data Organization (The "Brain")
To facilitate this learning, every match analyzed is saved as a structured JSON file:
*   **Path**: `data/matches/{League}/{Season}/{Date}_{Home}_vs_{Away}.json`
*   **Content**: Contains ALL "Three Pillars" data (News, Stats, Lineups) + The System's Prediction.
*   **Purpose**: This is the "Training Set". The `post_mortem_analyst.py` script reads the Ledger (Result) and links it back to these JSONs (Input) to train the model.

## 5. Directory Structure
*   `scripts/Phase2/`
    *   `phase2_orchestrator.py`: The Brain.
    *   `ledger_manager.py`: The Accountant.
    *   `post_mortem_analyst.py`: The Teacher (Reviews results).
    *   `ah_value_finder.py`: The Mathematician.
    *   `*_collector.py`: The Researchers.
    *   `matches_batch.txt`: The To-Do List.
*   `data/matches/`: The Memory (Historical Data).
