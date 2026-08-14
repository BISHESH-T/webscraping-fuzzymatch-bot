# Stackie — Web Scraping & Fuzzy Matching Discord Bot

A feature-rich Discord bot built with Python that combines **Automated Web Scraping** (via BeautifulSoup) and **Fuzzy String Matching** to track active developer quests, campaigns, and answer user queries with an interactive self-learning knowledge base.

---

## Key Features

* **Automated Web Scraping:** Scrapes `earn.stackup.dev` to extract real-time data on ongoing and upcoming quests and campaigns.
* **Fuzzy-Matching Knowledge Base:** Utilizes sequence-matching distance algorithms (`difflib`) with a confidence threshold (`cutoff=0.7`) to process natural language questions, handling typos and approximate phrasing (`a!ask`).
* **Interactive Self-Learning FAQ:** If a query isn't found in the knowledge base, the bot prompts the user for the answer and dynamically saves new Q&A pairs to JSON in real time.
* **Automated Event Notifications:** Periodically polls for new updates and alerts designated Discord channels about newly launched campaigns or quests.
* **Custom Status & Presence:** Automatically cycles bot status indicators every 20 seconds.

---

## Tech Stack & Concepts

* **Language:** Python 3.8+
* **Framework:** `discord.py` (Commands & Cogs)
* **Web Scraping:** `BeautifulSoup4`, `requests`
* **Information Retrieval / NLP:** Fuzzy String Matching (`difflib` Ratcliff/Obershelp algorithm)
* **Data Storage:** JSON-backed dynamic stores

---

## Prerequisites

* **Python 3.8** or higher installed.
* A Discord Bot Token (created via the [Discord Developer Portal](https://discord.com/developers/applications)).

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/BISHESH-T/webscraping-fuzzymatch-bot.git
cd webscraping-fuzzymatch-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory of the project to store your secret keys securely:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

### 4. Run the Bot
```bash
python stackie.py
```

---

## Bot Commands

| Command | Description |
| :--- | :--- |
| `a!ongoing` | Fetches and displays currently active campaigns/quests. |
| `a!upcoming` | Displays all upcoming campaigns and quests from StackUp. |
| `a!quest` | Retrieves details and direct links for specific quests. |
| `a!ask <query>` | Queries the knowledge base using fuzzy matching to find answers to FAQs. |
| `a!add_channel <id>` | Configures the target channel where notification alerts should be sent. |

---

## Feature Demos

* **Commands Demo (`a!ongoing`, `a!upcoming`, `a!quest`):** Demonstration of command syntax and expected output formatting. — [Watch Demo](https://youtu.be/BpV9LN_CXpo)
* **Knowledge Base Demo (`a!ask`):** Demonstration of query matching, handling misspelled inputs, and self-learning workflow. — [Watch Demo](https://youtu.be/6dBOeDUX9yk)
* **New Campaign Alerting:** Real-time push notification triggering upon detecting new web scraped content. — [Watch Demo](https://youtu.be/ViEyArdfx_Q)

> ⚠️ **Note:** Remember to run `a!add_channel <channel_id>` first so the bot knows where to dispatch push notifications!

---

## 🔗 Add Bot to Your Server

[**Click here to invite Stackie to your Discord Server**](https://discord.com/oauth2/authorize?client_id=982330325910814720&permissions=8&integration_type=0&scope=bot)