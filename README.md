# Children's Services Nearest Neighbours & Clustering Explorer

A DAP (Data Analytics Principles) artefact: an interactive Streamlit app that clusters
local authorities and finds nearest-neighbour comparators for a Children's Services
directorate, extending the ONS statistical nearest neighbours methodology with ten
indicators specific to children's services demand (child poverty, dependency ratio,
population density, no qualifications, weekly pay, CLA rate, CP plan rate, CIN rate,
SEN/EHCP rate, UASC rate).

Live model: K-means clustering + Euclidean nearest neighbours, with elbow and
silhouette diagnostics, run entirely in-app so indicators can be added/removed and
everything recalculates live.

## Folder structure

```
.
├── app.py                     # the Streamlit app (single file)
├── requirements.txt
├── data/
│   └── subnational_indicators.csv   # long-format indicator data
└── README.md
```

## Adding this to your existing fork

Your fork already contains `clustering_and_nearest_neighbours/` from the ONS repo.
Add this app **alongside** it, not inside it, so the two stay clearly separated:

```
Subnational-Statistics-and-Analysis/
├── clustering_and_nearest_neighbours/     # ONS's original code (your Colab work)
└── streamlit_app/                         # <- put these files here
    ├── app.py
    ├── requirements.txt
    ├── data/subnational_indicators.csv
    └── README.md
```

1. In your local clone: `mkdir streamlit_app` (and `mkdir streamlit_app/data`)
2. Copy `app.py`, `requirements.txt`, `README.md` into `streamlit_app/`
3. Copy `subnational_indicators.csv` into `streamlit_app/data/`
4. `git add streamlit_app && git commit -m "Add Streamlit nearest neighbours app" && git push`

## Running locally

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

## Deploying (Streamlit Community Cloud)

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. "New app" → select your repo → set **Main file path** to `streamlit_app/app.py`.
3. Since your repo is private, you'll be prompted to authorise Streamlit's GitHub App
   for that repo specifically — this doesn't make the repo public.
4. Deploy. Any future `git push` to `main` will auto-redeploy.

## Data caveats (see also Tab 1 in the app)

- Indicators span different reference periods (FYE 2023 – April 2025 provisional);
  see the in-app data table for the exact period per indicator.
- The model is scoped to **single-tier authorities** (unitaries, London boroughs,
  metropolitan boroughs, and single-tier councils in Wales/Scotland/NI) because
  children's services indicators are published at upper-tier level while some
  contextual indicators are published at district (lower-tier) level for England's
  shire counties — merging the two needs population-weighted aggregation this
  dataset doesn't include.
- Scotland is excluded from CIN rate (no direct equivalent); Northern Ireland is
  excluded from SEN/EHCP rate and UASC rate (not published by district).
- This is a **bespoke extension** of ONS's method, not a reproduction of an ONS
  model — ONS's own published clustering model does not include any children's
  social care indicators.

## Methodology reference

ONS, *Clustering similar local authorities and statistical nearest neighbours in the
UK: methodology* —
https://www.ons.gov.uk/peoplepopulationandcommunity/wellbeing/methodologies/clusteringsimilarlocalauthoritiesandstatisticalnearestneighboursintheukmethodology
