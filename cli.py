#!/usr/bin/env python3
"""
Twitter Auto-Post Bot CLI
A command-line interface for managing automated Twitter posts.
"""

import click
import sys
import os
import schedule
import time
import random

sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import keys
from src.functions import generate_response, initialize_tweepy, get_formatted_date


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Twitter Auto-Post Bot - Automate your Twitter presence."""
    pass


@cli.command()
@click.option('--ai', is_flag=True, help='Generate tweet using AI')
@click.option('--file', 'from_file', is_flag=True, help='Post random tweet from file')
@click.option('--text', help='Post custom text')
@click.option('--prompt', default='Create a short tweet about Motorbikes.', help='Custom prompt for AI (only with --ai)')
def post(ai, from_file, text, prompt):
    """Post a tweet instantly."""

    if sum([ai, from_file, bool(text)]) != 1:
        click.echo(click.style('Error: Please specify exactly one option: --ai, --file, or --text', fg='red'))
        sys.exit(1)

    try:
        client, _ = initialize_tweepy()

        if ai:
            click.echo(click.style(f'Generating tweet with AI...', fg='yellow'))
            click.echo(click.style(f'Prompt: {prompt}', fg='cyan'))
            response = generate_response(prompt)
            tweet_text = response
            click.echo(click.style(f'\nGenerated tweet: {tweet_text}', fg='green'))

        elif from_file:
            tweets_file = os.path.join(os.path.dirname(__file__), 'data', 'tweets.txt')
            if not os.path.exists(tweets_file):
                click.echo(click.style(f'Error: tweets.txt not found at {tweets_file}', fg='red'))
                sys.exit(1)

            with open(tweets_file, 'r') as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]

            if not lines:
                click.echo(click.style('Error: tweets.txt is empty', fg='red'))
                sys.exit(1)

            tweet_text = random.choice(lines)
            click.echo(click.style(f'Selected tweet: {tweet_text}', fg='green'))

        else:
            tweet_text = text
            click.echo(click.style(f'Posting: {tweet_text}', fg='green'))

        client.create_tweet(text=tweet_text)
        click.echo(click.style('Tweet posted successfully!', fg='green', bold=True))

    except Exception as e:
        click.echo(click.style(f'Error posting tweet: {str(e)}', fg='red'))
        sys.exit(1)


@cli.command()
@click.option('--ai', is_flag=True, help='Schedule AI-generated tweets')
@click.option('--file', 'from_file', is_flag=True, help='Schedule tweets from file')
@click.option('--interval', 'interval_min', default=30, type=int, help='Interval in minutes (default: 30)')
@click.option('--refill', is_flag=True, help='Auto-generate new tweets to replenish the pool')
@click.option('--prompt', default='Create a short tweet about Motorbikes.', help='Custom prompt for AI (only with --ai)')
def schedule_posts(ai, from_file, interval_min, refill, prompt):
    """Schedule tweets at a regular interval (default every 30 min)."""

    if not ai and not from_file:
        click.echo(click.style('Error: Please specify either --ai or --file', fg='red'))
        sys.exit(1)

    if ai and from_file:
        click.echo(click.style('Error: Please specify only one option: --ai or --file', fg='red'))
        sys.exit(1)

    tweets_file = os.path.join(os.path.dirname(__file__), 'data', 'tweets.txt')

    try:
        client, _ = initialize_tweepy()
        interval_min = max(1, interval_min)

        if ai:
            def send_ai_post():
                try:
                    click.echo(click.style(f'\nGenerating and posting tweet...', fg='yellow'))
                    response = generate_response(prompt)
                    client.create_tweet(text=response)
                    click.echo(click.style(f'Tweet posted: {response}', fg='green'))
                    click.echo(click.style(f'Next post in {interval_min} minutes', fg='cyan'))
                except Exception as e:
                    click.echo(click.style(f'Error posting tweet: {str(e)}', fg='red'))

            schedule.every(interval_min).minutes.do(send_ai_post)
            click.echo(click.style(f'Scheduled AI tweets every {interval_min} minutes', fg='green', bold=True))
            click.echo(click.style(f'Prompt: {prompt}', fg='cyan'))

        else:
            if not os.path.exists(tweets_file):
                click.echo(click.style(f'Error: tweets.txt not found at {tweets_file}', fg='red'))
                sys.exit(1)

            def send_file_post():
                try:
                    with open(tweets_file, 'r', encoding='utf-8') as file:
                        lines = [line.strip() for line in file.readlines() if line.strip() and not line.startswith('#') and not line.startswith('---')]

                    if not lines:
                        click.echo(click.style('Error: tweets.txt is empty', fg='red'))
                        return

                    tweet_text = random.choice(lines)
                    client.create_tweet(text=tweet_text)
                    click.echo(click.style(f'\nTweet posted: {tweet_text}', fg='green'))

                    if refill:
                        try:
                            response = generate_response(prompt)
                            with open(tweets_file, 'a', encoding='utf-8') as f:
                                f.write(response + '\n')
                            click.echo(click.style(f'Generated new tweet to refill pool: {response}', fg='cyan'))
                        except Exception as refill_err:
                            click.echo(click.style(f'Could not generate refill tweet: {refill_err}', fg='yellow'))

                    click.echo(click.style(f'Next post in {interval_min} minutes', fg='cyan'))
                except Exception as e:
                    click.echo(click.style(f'Error posting tweet: {str(e)}', fg='red'))

            schedule.every(interval_min).minutes.do(send_file_post)
            click.echo(click.style(f'Scheduled tweets from file every {interval_min} minutes', fg='green', bold=True))
            if refill:
                click.echo(click.style(f'Auto-refill mode ON – new tweets will be generated to replenish pool', fg='cyan'))

        click.echo(click.style('\nPress Ctrl+C to stop the scheduler', fg='yellow'))
        if ai:
            send_ai_post()
        else:
            send_file_post()

        while True:
            schedule.run_pending()
            time.sleep(interval_min * 60 if interval_min > 1 else 30)

    except KeyboardInterrupt:
        click.echo(click.style('\n\nScheduler stopped.', fg='yellow'))
    except Exception as e:
        click.echo(click.style(f'Error: {str(e)}', fg='red'))
        sys.exit(1)


@cli.command()
def test():
    """Test Twitter API credentials."""
    try:
        click.echo(click.style('Testing Twitter API credentials...', fg='yellow'))
        client, api = initialize_tweepy()

        user = api.verify_credentials()
        click.echo(click.style('\nCredentials verified successfully!', fg='green', bold=True))
        click.echo(click.style(f'Authenticated as: @{user.screen_name}', fg='cyan'))
        click.echo(click.style(f'Name: {user.name}', fg='cyan'))
        click.echo(click.style(f'Followers: {user.followers_count}', fg='cyan'))
        click.echo(click.style(f'Following: {user.friends_count}', fg='cyan'))

    except Exception as e:
        click.echo(click.style(f'\nCredentials test failed: {str(e)}', fg='red'))
        click.echo(click.style('\nPlease check your credentials in config/keys.py', fg='yellow'))
        sys.exit(1)


@cli.command()
def list_tweets():
    """List all tweets from the tweets.txt file."""
    tweets_file = os.path.join(os.path.dirname(__file__), 'data', 'tweets.txt')

    if not os.path.exists(tweets_file):
        click.echo(click.style(f'Error: tweets.txt not found at {tweets_file}', fg='red'))
        sys.exit(1)

    try:
        with open(tweets_file, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines()
                     if line.strip() and not line.startswith('#') and not line.startswith('---')]

        if not lines:
            click.echo(click.style('tweets.txt is empty. Add some tweets first!', fg='yellow'))
            return

        click.echo(click.style(f'\nFound {len(lines)} tweet(s) in file:', fg='green', bold=True))
        click.echo()

        for i, tweet in enumerate(lines, 1):
            safe = tweet.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
            click.echo(click.style(f'{i}. ', fg='cyan') + safe)

    except Exception as e:
        click.echo(click.style(f'Error reading tweets file: {str(e)}', fg='red'))
        sys.exit(1)


@cli.command()
def add_tweet():
    """Add a new tweet to the tweets.txt file interactively."""
    tweets_file = os.path.join(os.path.dirname(__file__), 'data', 'tweets.txt')

    os.makedirs(os.path.dirname(tweets_file), exist_ok=True)

    tweet = click.prompt(click.style('Enter your tweet', fg='cyan'))

    if len(tweet) > 280:
        click.echo(click.style(f'Warning: Tweet is {len(tweet)} characters (Twitter limit is 280)', fg='yellow'))
        if not click.confirm(click.style('Do you want to add it anyway?', fg='yellow')):
            click.echo(click.style('Tweet not added.', fg='red'))
            return

    try:
        with open(tweets_file, 'a') as file:
            file.write(tweet + '\n')

        click.echo(click.style('\nTweet added successfully!', fg='green', bold=True))

    except Exception as e:
        click.echo(click.style(f'Error adding tweet: {str(e)}', fg='red'))
        sys.exit(1)


@cli.command()
@click.option('--count', default=5, type=int, help='Number of tweets to generate (default: 5)')
@click.option('--prompt', default='Create a short tweet about Motorbikes.', help='Custom prompt for AI generation')
def generate(count, prompt):
    """Generate new tweets via AI and add them to the pool."""
    tweets_file = os.path.join(os.path.dirname(__file__), 'data', 'tweets.txt')
    os.makedirs(os.path.dirname(tweets_file), exist_ok=True)

    if not keys.openai_key or keys.openai_key == "your_openai_key_here":
        click.echo(click.style('Error: OpenAI API key not set. Add OPENAI_API_KEY to .env', fg='red'))
        sys.exit(1)

    try:
        click.echo(click.style(f'Generating {count} tweets...', fg='yellow', bold=True))
        added = 0

        for i in range(count):
            click.echo(click.style(f'\n[{i+1}/{count}] Generating...', fg='cyan'))
            response = generate_response(prompt)

            if len(response) > 280:
                response = response[:277] + '...'

            with open(tweets_file, 'a', encoding='utf-8') as f:
                f.write(response + '\n')

            click.echo(click.style(f'   ✓ {response}', fg='green'))
            added += 1
            time.sleep(1)

        click.echo(click.style(f'\nDone! {added} tweet(s) added to {tweets_file}', fg='green', bold=True))

    except Exception as e:
        click.echo(click.style(f'Error generating tweets: {str(e)}', fg='red'))
        sys.exit(1)


@cli.command()
@click.option('--count', default=5, type=int, help='Number of tweets to generate (default: 5)')
@click.option('--prompt', default='Create a short tweet about Motorbikes.', help='Custom prompt for AI generation')
def topup(count, prompt):
    """Alias for generate – add fresh tweets to the pool."""
    generate.callback(count=count, prompt=prompt)


if __name__ == '__main__':
    cli()
