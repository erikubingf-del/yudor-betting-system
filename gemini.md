# Gemini AI Agent: Project Yudor Betting System Enhancement

## 1. Project Objective

The primary objective of this project is to evolve the Yudor Betting System into a highly advanced, automated, and mathematically rigorous platform for identifying value in sports betting markets. The system will leverage artificial intelligence, statistical modeling, and a robust data pipeline to generate fair odds with high consistency and accuracy. It will feature self-learning capabilities to continuously improve its predictive power.

## 2. Current State Analysis

### Strengths:
*   **Comprehensive Data Collection:** The project has a significant amount of historical data and a process for scraping new data.
*   **Existing Infrastructure:** There's a set of scripts for analysis, data consolidation, and integration with Airtable, which provides a foundation to build upon.
*   **Clear Vision:** The user has a clear vision for an advanced, AI-driven system.

### Areas for Improvement:
*   **Mathematical Rigor:** The current methodology for calculating "fair odds" is not explicitly defined in the provided files. It seems to rely on a "YUDOR_MASTER_PROMPT", which suggests a qualitative or heuristic-based approach rather than a transparent, auditable mathematical model.
*   **Code Organization and Modularity:** The scripts in the `scripts` directory appear to have grown organically. There's an opportunity to refactor them into a more modular, object-oriented, and maintainable codebase.
*   **Scalability and Robustness:** The reliance on individual scripts makes the system fragile. A more robust, orchestrated pipeline is needed.
*   **Model Validation and Backtesting:** There is a `test_fair_odds_calculation.py` but it's not clear how systematic backtesting is performed to evaluate the model's performance over time.
*   **Auto-learning:** The current system lacks a clear mechanism for "auto-learning" or model updating based on new results.

## 3. Proposed Architecture: A Mathematically-Grounded, Self-Learning System

I propose a new architecture based on modern data science and machine learning principles, inspired by the work of mathematicians and statisticians who have revolutionized prediction and decision-making under uncertainty.

The new architecture will be composed of the following key components:

*   **1. Data Core:** A centralized and structured data store for all raw and processed data. This will be the single source of truth for the entire system. I'll propose a clear schema.
*   **2. Feature Engineering Engine:** A dedicated module to transform raw data into meaningful features for the predictive model. This will include statistical features, team/player ratings (e.g., Elo or Glicko systems), and other relevant predictors.
*   **3. Predictive Model(s):** The core of the system will be a probabilistic model that outputs the probability of different match outcomes (e.g., home win, draw, away win). I will start with a well-established model like a **Bayesian Hierarchical Model** or a **Poisson-based model** (like the Dixon-Coles model), which are standards in soccer prediction. This provides a strong mathematical foundation.
*   **4. Value Identification Module:** This module will compare the model's predicted probabilities with the market odds to identify value bets.
*   **5. Performance Monitoring and Model Retraining Pipeline:** An automated pipeline to monitor the model's performance on new matches, and to retrain and update the model periodically to ensure it adapts to new patterns in the data.
*   **6. Orchestrator:** A central script to orchestrate the entire pipeline, from data ingestion to value identification and performance monitoring.

## 4. Development Roadmap

Here is the step-by-step plan to build the new system in parallel with the existing one.

1.  **Project Setup & Scaffolding:** Create the directory structure for the new Python project.
2.  **Data Ingestion and Schema Definition:** Analyze the existing data and define a clear, unified schema. Write scripts to transform and load existing data into the new `Data Core`.
3.  **Feature Engineering:** Develop the Feature Engineering Engine.
4.  **Initial Model Implementation:** Implement the first version of the predictive model (e.g., a Poisson-based model).
5.  **Backtesting Engine:** Build a robust backtesting engine to evaluate the model's historical performance.
6.  **Value Identification:** Implement the value identification module.
7.  **Orchestration and Automation:** Create the orchestrator script to run the end-to-end pipeline.
8.  **Integration and A/B Testing:** Integrate the new system with the existing data sources and set up a framework for A/B testing the new model against the legacy system.
9.  **Advanced Model Development:** Explore and implement more advanced models, such as Bayesian Hierarchical Models or Machine Learning models (e.g., Gradient Boosting).
10. **Documentation:** Document the new system's architecture, data schema, and how to use it.

## 5. Key Technologies & Methodologies

*   **Programming Language:** Python
*   **Libraries:**
    *   `pandas` for data manipulation.
    *   `scikit-learn` for machine learning models and utilities.
    *   `pymc` or `stan` for Bayesian modeling.
    *   `mlflow` for model tracking and experiment management.
    *   `prefect` or `airflow` for orchestration (or a custom orchestrator script to begin with).
*   **Methodologies:**
    *   **Bayesian Statistics:** To quantify uncertainty and update beliefs as more data becomes available.
    *   **Poisson Distribution:** For modeling goal-scoring events.
    *   **Elo/Glicko Rating Systems:** To model team strength dynamically.
    *   **Cross-validation and Backtesting:** To rigorously evaluate model performance.
    *   **Modular Programming:** To create a maintainable and extensible codebase.
