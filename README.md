# Fitness Tracker Analytics

Streamlit dashboard for the fitness data analytics case study (Python EDA -> SQL analytics -> this app).
Covers three pillars: user activity, sleep patterns, body metrics, for 33 Fitbit users over a one-month window.

## Repo structure

```
.
├── app.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
└── data/
    ├── activity_clean.csv
    ├── sleep_clean.csv
    └── weight_clean.csv
```

## Run locally

```
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this folder's contents to a new GitHub repo (keep the structure above, `app.py` at repo root).
2. Go to share.streamlit.io, sign in with GitHub, click "New app".
3. Select the repo, branch, and set the main file path to `app.py`.
4. Deploy. `requirements.txt` is picked up automatically; no secrets or extra config needed since all
   data is bundled in `data/`.
