import os
from pathlib import Path
import aiohttp
import discord
from discord import app_commands
from dotenv import load_dotenv


# Look for .env next to this file, regardless of where the bot starts.
# Keep any values already set in the environment.
load_dotenv(Path(__file__).resolve().with_name(".env"))


SCRYFALL_API = "https://api.scryfall.com"
HEADERS = {
	"User-Agent": "CardLookupBot/1.0",
	"Accept": "application/json",
}


class CardBot(discord.Client):
	def __init__(self):
		super().__init__(intents=discord.Intents.default())
		self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
		# Register the slash commands when the bot starts.
		await self.tree.sync()


bot = CardBot()


async def scryfall_get(path, params=None):
	# Stop waiting after 15 seconds if Scryfall does not respond.
	timeout = aiohttp.ClientTimeout(total=15)
	async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
		async with session.get(f"{SCRYFALL_API}{path}", params=params) as response:
			data = await response.json()
			if response.status >= 400:
				raise RuntimeError(data.get("details", "Scryfall request failed."))
			return data


def card_image(card):
	images = card.get("image_uris")
	# For cards with a separate image on each face, show the front.
	if not images and card.get("card_faces"):
		images = card["card_faces"][0].get("image_uris")
	return images.get("normal") if images else None


def price_text(card):
	prices = card.get("prices", {})
	values = []
	# Skip prices Scryfall has not listed.
	for key, label in (("usd", "USD"), ("usd_foil", "foil"), ("eur", "EUR")):
		if prices.get(key):
			values.append(f"{label}: ${prices[key]}" if label != "EUR" else f"EUR: €{prices[key]}")
	return " · ".join(values) or "No listed price"


@bot.tree.command(name="search", description="Look up a Magic card and its printings")
@app_commands.describe(card_name="Card name", set_name="Optional set name or set code")
async def search(interaction: discord.Interaction, card_name: str, set_name: str = None):
	# Acknowledge the command while we wait for Scryfall.
	await interaction.response.defer(thinking=True)
	name_query = card_name.replace('"', "").strip()
	query = f'name:"{name_query}"'
	if set_name and set_name.strip():
		query += f' set:"{set_name.replace(chr(34), "").strip()}"'

	try:
		result = await scryfall_get("/cards/search", {"q": query, "order": "released", "dir": "desc"})
		cards = result.get("data", [])
		if not cards:
			await interaction.followup.send("No matching card found.")
			return

		# Show the newest printing from the search results.
		card = cards[0]
		embed = discord.Embed(
			title=card.get("name", "Unknown card"),
			url=card.get("scryfall_uri"),
			color=discord.Color.dark_green(),
		)
		embed.add_field(name="Type", value=card.get("type_line", "Unknown"), inline=False)
		if card.get("mana_cost"):
			embed.add_field(name="Mana cost", value=card["mana_cost"], inline=True)
		if card.get("oracle_text"):
			embed.add_field(name="Card text", value=card["oracle_text"][:1024], inline=False)
		embed.add_field(
			name=f"Selected printing · {card.get('set_name', 'Unknown set')} ({card.get('set', '').upper()})",
			value=price_text(card),
			inline=False,
		)
		embed.set_image(url=card_image(card)) if card_image(card) else None

		# Use the oracle ID to find other printings of this card.
		oracle_id = card.get("oracle_id")
		if oracle_id:
			prints = await scryfall_get(
				"/cards/search",
				{"q": f"oracleid:{oracle_id}", "unique": "prints", "order": "released", "dir": "desc"},
			)
			others = [printing for printing in prints.get("data", []) if printing.get("id") != card.get("id")]
			lines = [
				f"**{printing.get('set_name', 'Unknown set')} ({printing.get('set', '').upper()})** — {price_text(printing)}"
				for printing in others[:12]
			]
			if len(others) > 12:
				lines.append(f"…and {len(others) - 12} more printings")
			embed.add_field(name="Other printings and prices", value="\n".join(lines) or "No other printings found.", inline=False)

		await interaction.followup.send(embed=embed)
	except (aiohttp.ClientError, RuntimeError, ValueError) as error:
		await interaction.followup.send(f"Card lookup failed: {str(error)[:300]}")


token = os.getenv("DISCORD_BOT_TOKEN")
if not token:
	raise RuntimeError("DISCORD_BOT_TOKEN is missing. Add it to the .env file next to this script or set it in your environment.")
bot.run(token)
