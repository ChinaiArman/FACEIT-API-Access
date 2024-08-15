# FACEIT API Access

## What is this script for?

This script is used to get the match results from a Faceit tournament and save them in a CSV file.

## How to use this script.

### Prerequisites:

1. Python 3.6 or higher
2. A Faceit API key. You can get one [here](https://developers.faceit.com/start/intro)

### Steps:

1. Install the dependencies with `pip install -r requirements.txt`
2. Create a file named `.env` in the root directory of the project and add the following line:

```shell
API_KEY="YOUR_API_KEY"
```

3. Create a new terminal in the root directory of the project and run the script with the following command:

```shell
python main.py "TOURNAMENT_ID"
```

## How to get the tournament ID.

1. Go to the tournament page
2. Copy the ID from the URL

Example: `https://www.faceit.com/en/championship/ae421537-8e52-4d5f-bbeb-327d82760fd9/Mini-Poke%20Showdown%20-%202v2%20-%20NA/teams?group=1` → `ae421537-8e52-4d5f-bbeb-327d82760fd9`

## Questions?

DM: ow2Cookie on Discord
