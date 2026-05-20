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
├── assets/
│   └── logo.png
└── utils/
    ├── ai_generator.py
    ├── prompts.py
    ├── helpers.py
    └── styling.py
```

## Installation

1. Clone repository:

```bash
git clone <your-repo-url>
cd AI-SEO-Generator
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
- Model: `grok-3-beta`

## Run Locally

```bash
streamlit run app.py
```

Open the local URL shown in terminal (typically `http://localhost:8501`).

## Streamlit Cloud Deployment

1. Push project to GitHub.
2. Open [Streamlit Community Cloud](https://streamlit.io/cloud).
3. Create new app from your repository.
4. Set main file path to `app.py`.
5. In app settings, add secret:
   - `XAI_API_KEY = your_actual_xai_api_key`
6. Deploy.

## GitHub Deployment Workflow

1. Initialize repository if needed:

```bash
git init
git add .
git commit -m "feat: add production-ready AI real estate SEO generator"
```

2. Create remote repository and push:

```bash
git remote add origin <your-repo-url>
git branch -M main
git push -u origin main
```

## Troubleshooting

- **API not connected**: verify `.env` exists and contains valid `XAI_API_KEY`.
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
