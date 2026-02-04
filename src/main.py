"""
Meme Video Generator - Main Entry Point

A professional tool for generating and uploading meme videos to multiple platforms.
"""

import argparse
import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import (
    bold, cyan, green, header, red, yellow,
    init_config, setup_logger
)
from src.core.niche_manager import NicheManager


def print_banner():
    """Print application banner."""
    print()
    print(header("═" * 60))
    print(header("           MEME VIDEO GENERATOR v1.0.0"))
    print(header("═" * 60))
    print()


def print_menu():
    """Print main menu."""
    print(bold("What would you like to do?"))
    print(f"    1. {cyan('Generate Memes')}")
    print(f"    2. {cyan('Upload to YouTube')}")
    print(f"    3. {cyan('Upload to TikTok')}")
    print(f"    4. {cyan('Upload to All Platforms')}")
    print(f"    5. {cyan('View Niche Statistics')}")
    print(f"    6. {cyan('List All Niches')}")
    print(f"    7. {red('Exit')}")
    print()


def handle_generate(niche_path: str, count: int = 1):
    """
    Handle meme generation.
    
    Args:
        niche_path: Path to niche directory
        count: Number of memes to generate
    """
    print(yellow(f"\nGenerating {count} meme(s)..."))
    print(red("\n⚠️  Note: Full video generation module is being migrated."))
    print("This is a placeholder. The actual implementation will be in src/core/generator.py")
    print()
    

def handle_upload(niche_path: str, platform: str):
    """
    Handle video upload.
    
    Args:
        niche_path: Path to niche directory
        platform: Platform to upload to ('youtube', 'tiktok', 'all')
    """
    print(yellow(f"\nUploading to {platform}..."))
    print(red("\n⚠️  Note: Upload module is being migrated."))
    print("This is a placeholder. The actual implementation will be in src/core/uploader.py")
    print()


def handle_stats(niche_path: str):
    """
    Handle statistics display.
    
    Args:
        niche_path: Path to niche directory
    """
    niche_mgr = NicheManager()
    niche_mgr.get_niche_summary(niche_path)


def handle_list_niches():
    """List all available niches."""
    niche_mgr = NicheManager()
    niches = niche_mgr.list_niches()
    
    if not niches:
        print(red("\nNo niches found."))
        print("Please create a niche in data/niches/ or run the migration script.")
        print()
        return
    
    print(bold("\nAvailable niches:"))
    for niche in niches:
        display_name = niche[1:] if niche.startswith('!') else niche
        print(f"  • {cyan(display_name)}")
    print()


def interactive_mode():
    """Run in interactive mode with menu."""
    print_banner()
    
    niche_mgr = NicheManager()
    
    while True:
        print_menu()
        
        try:
            choice = input(bold("> ")).strip()
            
            if choice == '1':
                # Generate memes
                niche_path = niche_mgr.select_niche()
                if niche_path:
                    try:
                        count = int(input("\nHow many memes to generate? ").strip() or "1")
                        handle_generate(niche_path, count)
                    except ValueError:
                        print(red("Invalid number."))
            
            elif choice == '2':
                # Upload to YouTube
                niche_path = niche_mgr.select_niche()
                if niche_path:
                    handle_upload(niche_path, 'youtube')
            
            elif choice == '3':
                # Upload to TikTok
                niche_path = niche_mgr.select_niche()
                if niche_path:
                    handle_upload(niche_path, 'tiktok')
            
            elif choice == '4':
                # Upload to all platforms
                niche_path = niche_mgr.select_niche()
                if niche_path:
                    handle_upload(niche_path, 'all')
            
            elif choice == '5':
                # View statistics
                niche_path = niche_mgr.select_niche()
                if niche_path:
                    handle_stats(niche_path)
            
            elif choice == '6':
                # List niches
                handle_list_niches()
            
            elif choice == '7':
                print(green("\nGoodbye! 👋\n"))
                break
            
            else:
                print(red("Invalid choice. Please select 1-7."))
        
        except KeyboardInterrupt:
            print(green("\n\nGoodbye! 👋\n"))
            break
        except Exception as e:
            print(red(f"\nError: {e}"))
            print("Please try again.\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Meme Video Generator - Generate and upload meme videos'
    )
    
    # Commands
    parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate meme videos'
    )
    parser.add_argument(
        '--upload',
        choices=['youtube', 'tiktok', 'all'],
        help='Upload videos to platform'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show niche statistics'
    )
    parser.add_argument(
        '--list-niches',
        action='store_true',
        help='List all available niches'
    )
    
    # Options
    parser.add_argument(
        '--niche',
        help='Niche name to work with'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=1,
        help='Number of videos to generate/upload'
    )
    parser.add_argument(
        '--config',
        default='config',
        help='Configuration directory'
    )
    
    args = parser.parse_args()
    
    # Initialize configuration
    try:
        config_dir = args.config
        init_config(config_dir)
    except FileNotFoundError as e:
        print(red(f"\n❌ Configuration Error: {e}"))
        print(yellow("\n💡 Tip: Make sure you have copied config.example.yaml to config.yaml"))
        print(f"   Run: cp {config_dir}/config.example.yaml {config_dir}/config.yaml\n")
        sys.exit(1)
    except Exception as e:
        print(red(f"\n❌ Error loading configuration: {e}\n"))
        sys.exit(1)
    
    # Set up logging
    logs_dir = 'logs'
    Path(logs_dir).mkdir(exist_ok=True)
    logger = setup_logger(
        'main',
        log_file=f'{logs_dir}/app.log',
        level='INFO'
    )
    
    # Handle commands
    if args.list_niches:
        handle_list_niches()
        return
    
    # Get niche path if niche specified
    niche_path = None
    if args.niche:
        niche_mgr = NicheManager()
        niches_base = niche_mgr.niches_base_path
        niche_path = os.path.join(niches_base, args.niche)
        
        if not os.path.exists(niche_path):
            # Try with ! prefix (legacy)
            niche_path = os.path.join(niches_base, f"!{args.niche.capitalize()}")
        
        if not os.path.exists(niche_path):
            print(red(f"\n❌ Niche not found: {args.niche}"))
            print("Available niches:")
            handle_list_niches()
            sys.exit(1)
    
    # Execute commands
    if args.generate:
        if not niche_path:
            print(red("❌ Please specify a niche with --niche"))
            sys.exit(1)
        handle_generate(niche_path, args.count)
    
    elif args.upload:
        if not niche_path:
            print(red("❌ Please specify a niche with --niche"))
            sys.exit(1)
        handle_upload(niche_path, args.upload)
    
    elif args.stats:
        if not niche_path:
            print(red("❌ Please specify a niche with --niche"))
            sys.exit(1)
        handle_stats(niche_path)
    
    else:
        # No command specified, run interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
