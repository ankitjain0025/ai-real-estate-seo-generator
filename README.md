# AI Real Estate SEO Generator

Production-ready Streamlit application that generates premium SEO and social launch content for Indian real estate developers and marketing teams using xAI Grok API.

## Features

- AI-generated launch content suite from one project form
- SEO Title, Meta Description, Keywords, Google Snippet
- Instagram Caption, LinkedIn Caption
- 25 SEO hashtags and 10 blog topic ideas
- Short and long-form project descriptions
- Content quality score and SEO strength indicator
- Meta description character counter
- Session-state persistence for generated output
- Download output as TXT and Markdown
- Retry logic and robust API error handling
- Premium custom UI/UX with responsive layout

## Tech Stack

- Python
- Streamlit
- xAI Grok API (`grok-3-beta`) via OpenAI-compatible SDK
- dotenv for environment configuration

## Project Structure

```text
AI-SEO-Generator/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── assets/
│   └── logo.png
└── utils/
    ├── __init__.py
    ├── ai_generator.py
    ├── config.py
    ├── prompts.py
    ├── schema.py
    ├── parsing.py
    ├── validation.py
    ├── scoring.py
    ├── formatting.py
    ├── helpers.py
    └── styling.py
```

**Live repository:** https://github.com/ankitjain0025/ai-real-estate-seo-generator

## Installation

1. Clone repository:

```bash
git clone https://github.com/ankitjain0025/ai-real-estate-seo-generator.git
cd ai-real-estate-seo-generator
```

2. Create virtual environment:

```bash
python -m venv .venv
```

3. Activate environment:

- Windows (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

- macOS/Linux:

```bash
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create `.env` in project root:

```env
XAI_API_KEY=your_actual_xai_api_key
```

The app uses:

- `XAI_API_KEY` for xAI authentication
- Base URL: `https://api.x.ai/v1`
- Model: `grok-3-beta` (free/legacy-friendly default; override with `XAI_MODEL`)

## Run Locally

```bash
streamlit run app.py
```

Open the local URL shown in terminal (typically `http://localhost:8501`).

## Streamlit Cloud Deployment

[![Deploy on Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/cloud)

1. Open [Streamlit Community Cloud](https://streamlit.io/cloud) and sign in with GitHub.
2. Click **Create app** and select repository:
   `ankitjain0025/ai-real-estate-seo-generator`
3. Set **Main file path** to `app.py`.
4. In **Advanced settings → Secrets**, paste exactly (TOML format):

```toml
XAI_API_KEY = "your_actual_xai_api_key"
XAI_MODEL = "grok-3-beta"
```

5. Deploy, then open **Manage app → Reboot app** after saving secrets.
6. Confirm sidebar shows **Connected**.

Reference template: `.streamlit/secrets.toml.example`

## GitHub Repository

Remote is already configured:

```bash
git remote -v
git push origin main
```

## Troubleshooting

- **API not connected on Streamlit Cloud**: add `XAI_API_KEY` in App settings → Secrets (TOML), then **Reboot app**. Do not use JSON format in secrets.
- **API not connected locally**: verify `.env` exists and contains valid `XAI_API_KEY`.
- **HTTP 400 / Model not found**: use `XAI_MODEL = "grok-3-beta"` or `grok-3-mini-beta` (do not use retired slugs like `grok-2-1212`).
- **Insufficient credits**: add credits at [console.x.ai Billing](https://console.x.ai); beta aliases still consume API credits.
- **401 errors**: key is invalid or expired; regenerate xAI API key.
- **Timeout/network errors**: retry; app includes built-in retry logic.
- **Empty output**: refine USP, micro-market, and landmarks for better context.
- **Dependency issues**: upgrade pip and reinstall requirements.

## Future Roadmap

- Multi-language output for regional campaigns
- CSV bulk generation for multiple project launches
- Campaign templates by city/micro-market segment
- Built-in competitor SERP positioning hints
- Direct publishing integrations (CMS/social tools)
