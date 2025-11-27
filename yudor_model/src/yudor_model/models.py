
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np
from scipy.stats import poisson

def train_poisson_model(df: pd.DataFrame):
    """
    Trains a Poisson regression model to predict match outcomes.
    
    The model is based on the Dixon-Coles model, with modifications.
    We fit two separate models for home and away goals.
    
    log(home_goals) ~ home_team + away_team + home_advantage
    log(away_goals) ~ home_team + away_team
    
    Returns:
        A dictionary containing the trained home and away models.
    """
    
    # Drop rows with missing data in key columns
    df_clean = df.dropna(subset=['home_goals', 'away_goals', 'home_team_name', 'away_team_name'])
    
    if len(df_clean) == 0:
        print("Not enough data to train the model.")
        return None

    # Prepare the data for modeling
    goal_model_data = pd.concat([
        df_clean[['home_team_name', 'away_team_name', 'home_goals']].assign(home=1).rename(
            columns={'home_team_name': 'team', 'away_team_name': 'opponent', 'home_goals': 'goals'}
        ),
        df_clean[['away_team_name', 'home_team_name', 'away_goals']].assign(home=0).rename(
            columns={'away_team_name': 'team', 'home_team_name': 'opponent', 'away_goals': 'goals'}
        )
    ])

    # Fit the Poisson regression model using statsmodels
    # We use team as an attacking parameter and opponent as a defensive parameter
    poisson_model = smf.glm(
        formula="goals ~ home + team + opponent",
        data=goal_model_data,
        family=sm.families.Poisson()
    ).fit()
    
    print(poisson_model.summary())

    return poisson_model


def predict_match_outcome(poisson_model, home_team, away_team):
    """
    Predicts the outcome probabilities of a match using the trained Poisson model.

    Args:
        poisson_model: The trained Poisson model from `train_poisson_model`.
        home_team: The name of the home team.
        away_team: The name of the away team.

    Returns:
        A dictionary with the probabilities for home win, draw, and away win.
    """
    if poisson_model is None:
        return {"home_win": 0, "draw": 0, "away_win": 0}

    # Predict expected goals for home and away teams
    home_exp_goals = poisson_model.predict(pd.DataFrame(data={'team': home_team, 'opponent': away_team, 'home': 1}, index=[1]))
    away_exp_goals = poisson_model.predict(pd.DataFrame(data={'team': away_team, 'opponent': home_team, 'home': 0}, index=[1]))

    # Calculate probabilities for different scorelines
    # We'll consider up to 10 goals for each team
    max_goals = 10
    
    home_probs = [poisson.pmf(i, home_exp_goals) for i in range(max_goals + 1)]
    away_probs = [poisson.pmf(i, away_exp_goals) for i in range(max_goals + 1)]
    
    # Create a matrix of scoreline probabilities
    score_matrix = np.outer(home_probs, away_probs)
    
    # Calculate probabilities for home win, draw, and away win
    home_win_prob = np.sum(np.tril(score_matrix, -1))
    draw_prob = np.sum(np.diag(score_matrix))
    away_win_prob = np.sum(np.triu(score_matrix, 1))

    return {
        "home_win": home_win_prob,
        "draw": draw_prob,
        "away_win": away_win_prob,
        "predicted_home_goals": home_exp_goals.iloc[0],
        "predicted_away_goals": away_exp_goals.iloc[0]
    }
