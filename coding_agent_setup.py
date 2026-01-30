#!/usr/bin/env python3
"""
Coding Agent Setup Tool
Interactive CLI to manage orchestrator system prompt
"""
import subprocess
import shutil
from pathlib import Path

PROMPT_FILE = '/opt/coding-agent/system_prompts/orchestrator_prompt.txt'
BACKUP_FILE = '/opt/coding-agent/system_prompts/orchestrator_prompt_default.txt'

def view_prompt():
    """View the current prompt with line numbers"""
    try:
        with open(PROMPT_FILE, 'r') as f:
            lines = f.readlines()
        
        print('\n' + '='*60)
        print(f'CURRENT PROMPT ({len(lines)} lines)')
        print('='*60)
        
        for i, line in enumerate(lines, 1):
            print(f'{i:3d} | {line}', end='')
        
        print('='*60)
        input('\nPress ENTER to return to menu...')
        
    except FileNotFoundError:
        print(f'Error: Prompt file not found at {PROMPT_FILE}')
        input('Press ENTER to continue...')
    except Exception as e:
        print(f'Error viewing prompt: {e}')
        input('Press ENTER to continue...')

def main():
    while True:
        print('\n' + '='*60)
        print('CODING AGENT SETUP')
        print('='*60)
        print('[1] View current prompt')
        print('[2] Edit prompt (opens nano)')
        print('[3] Reset to default')
        print('[4] Create backup')
        print('[5] Show file locations')
        print('[6] Exit')
        print('='*60)
        
        choice = input('Select option: ').strip()
        
        if choice == '1':
            view_prompt()
                
        elif choice == '2':
            try:
                subprocess.run(['nano', PROMPT_FILE])
                print('✓ Prompt saved.')
                input('Press ENTER to continue...')
            except Exception as e:
                print(f'Error editing prompt: {e}')
                input('Press ENTER to continue...')
                
        elif choice == '3':
            try:
                if not Path(BACKUP_FILE).exists():
                    print(f'\nError: Backup file not found at {BACKUP_FILE}')
                    print('Create a backup first with option [4]')
                else:
                    confirm = input(f'\nThis will overwrite the current prompt. Continue? (y/n): ')
                    if confirm.lower() == 'y':
                        shutil.copy(BACKUP_FILE, PROMPT_FILE)
                        print('✓ Successfully reset to default prompt')
                    else:
                        print('Cancelled.')
                input('Press ENTER to continue...')
            except Exception as e:
                print(f'Error resetting prompt: {e}')
                input('Press ENTER to continue...')
                
        elif choice == '4':
            try:
                confirm = input(f'\nThis will overwrite the backup file. Continue? (y/n): ')
                if confirm.lower() == 'y':
                    shutil.copy(PROMPT_FILE, BACKUP_FILE)
                    print(f'✓ Successfully created backup at {BACKUP_FILE}')
                else:
                    print('Cancelled.')
                input('Press ENTER to continue...')
            except Exception as e:
                print(f'Error creating backup: {e}')
                input('Press ENTER to continue...')
        
        elif choice == '5':
            print('\n' + '='*60)
            print('FILE LOCATIONS')
            print('='*60)
            print(f'Prompt file:  {PROMPT_FILE}')
            print(f'  Exists: {Path(PROMPT_FILE).exists()}')
            print(f'Backup file:  {BACKUP_FILE}')
            print(f'  Exists: {Path(BACKUP_FILE).exists()}')
            print('='*60)
            input('Press ENTER to continue...')
                
        elif choice == '6':
            print('\nGoodbye!')
            break
            
        else:
            print('Invalid option. Please select 1-6.')
            input('Press ENTER to continue...')

if __name__ == '__main__':
    main()
