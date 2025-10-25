"""
Basic tests for the Kingdom-77 Discord bot.
These tests verify the bot's core functionality and configuration.
"""
import pytest
import sys
import os

# Add parent directory to path to import main module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_supported_languages():
    """Test that SUPPORTED languages dictionary is properly configured."""
    from main import SUPPORTED
    
    assert isinstance(SUPPORTED, dict)
    assert len(SUPPORTED) > 0
    assert 'ar' in SUPPORTED
    assert 'en' in SUPPORTED
    assert SUPPORTED['ar'] == 'Arabic'
    assert SUPPORTED['en'] == 'English'


def test_channels_file_path():
    """Test that CHANNELS_FILE path is properly set."""
    from main import CHANNELS_FILE
    
    assert CHANNELS_FILE is not None
    assert isinstance(CHANNELS_FILE, str)
    assert CHANNELS_FILE.endswith('channels.json')


def test_load_channels_function():
    """Test that load_channels function works correctly."""
    from main import load_channels
    
    channels = load_channels()
    assert isinstance(channels, dict)


def test_color_choosing_logic():
    """Test latency color selection logic."""
    from main import _choose_latency_color
    import discord
    
    # Green for fast latency
    color_fast = _choose_latency_color(50)
    assert color_fast == discord.Color.green()
    
    # Gold for medium latency
    color_medium = _choose_latency_color(150)
    assert color_medium == discord.Color.gold()
    
    # Red for slow latency
    color_slow = _choose_latency_color(300)
    assert color_slow == discord.Color.red()


def test_make_embed_function():
    """Test embed creation function."""
    from main import make_embed
    import discord
    
    embed = make_embed(title="Test", description="Test Description")
    assert isinstance(embed, discord.Embed)
    assert embed.title == "Test"
    assert embed.description == "Test Description"


def test_bot_instance():
    """Test that bot instance is created properly."""
    from main import bot
    from discord.ext import commands
    
    assert bot is not None
    assert isinstance(bot, commands.Bot)
    assert bot.command_prefix == '!'


def test_intents_configuration():
    """Test that bot intents are properly configured."""
    from main import intents
    import discord
    
    assert isinstance(intents, discord.Intents)
    assert intents.message_content is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
