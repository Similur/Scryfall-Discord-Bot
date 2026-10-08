# Scryfall Discord bot

Look up Magic: The Gathering cards in Discord with `/search`. The bot uses Scryfall to show a card image, rules text, prices, and other printings.

## Set up the bot

1. Create an application in the [Discord Developer Portal](https://discord.com/developers/applications).
2. Open its **Bot** page and generate a bot token.
3. In **Installation**, enable **Guild Install**. Add the `bot` and `applications.commands` scopes, with **View Channels**, **Send Messages**, and **Embed Links** permissions.
4. Use the installation link to add the bot to your server.

See [Discord's setup guide](https://docs.discord.com/developers/quick-start/getting-started) for details. This bot connects through Discord's gateway; it does not need an Interactions Endpoint URL or Message Content intent.

## Run locally

Install [Miniforge](https://github.com/conda-forge/miniforge) or another Conda distribution, then open a terminal in this project folder:

```powershell
conda env create -f environment.yml
conda activate scryfall-bot
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder with your bot token:

```dotenv
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

Start the bot:

```powershell
python Scryfall.py
```

Keep the terminal running while you use the bot. Press `Ctrl+C` to stop it. On macOS or Linux, use `cp .env.example .env` for the copy step.

The bot reads `.env` from the folder containing `Scryfall.py`. An existing `DISCORD_BOT_TOKEN` environment variable takes priority over the file.

`requirements.txt` lists the same Python dependencies for environments that use a requirements file. The Conda setup above is enough to run this project.

## Search for a card

In your server, type `/search` and fill in the options:

```text
/search card_name:Lightning Bolt
/search card_name:Lightning Bolt set_name:m11
```

`card_name` is required. `set_name` is optional and accepts a set name or code. The bot shows the newest matching printing returned by the search, plus up to 12 other printings from the first page of results. Prices can be missing when Scryfall has no listed price.

## Upload to GitHub

1. Create an empty repository on GitHub.
2. Choose **Add file → Upload files**.
3. Upload this folder's contents, including `.env.example` and `.gitignore`, and commit them. If you downloaded the ZIP, extract it first.

Check that the dotfiles appear in the upload list. Do not upload your local `.env`: `.gitignore` protects Git-based commits, but browser uploads require you to choose the files yourself. See [GitHub's file upload guide](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository).

Uploading the code to GitHub does not run the bot. Run it on your computer or a host with a persistent Python process.

## Troubleshooting

- **Missing token:** Check that `.env` is beside `Scryfall.py` and contains `DISCORD_BOT_TOKEN`.
- **Invalid token:** Generate a new token on the application's Bot page and update `.env`.
- **No `/search` command:** Confirm the bot was installed with `applications.commands`. Commands are synced at startup and may take time to appear.
- **No reply or embed:** Check the bot's channel permissions and the terminal for errors.
- **Card lookup failed:** Check the card name, optional set filter, and your internet connection. Scryfall error details are included in the reply.

Card data and images come from [Scryfall](https://scryfall.com). This project is not affiliated with Scryfall or Wizards of the Coast.
