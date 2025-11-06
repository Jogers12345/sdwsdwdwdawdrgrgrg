#!/usr/bin/env python3
"""
Windows-specific setup and configuration for BSEE.
"""

import os
import sys
import json
from pathlib import Path
import winreg
import subprocess


class WindowsSetup:
    """Windows-specific setup and configuration."""

    def __init__(self):
        """Initialize Windows setup."""
        self.install_dir = Path.cwd()
        self.appdata_dir = Path(os.environ['APPDATA']) / 'BSEE'
        self.desktop_dir = Path(os.environ['USERPROFILE']) / 'Desktop'
        self.start_menu_dir = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'

    def setup_directories(self):
        """Create Windows-specific directory structure."""
        print("Creating directory structure...")

        # Create standard BSEE directories in AppData
        directories = [
            self.appdata_dir / 'inputs',
            self.appdata_dir / 'results',
            self.appdata_dir / 'presets',
            self.appdata_dir / 'history',
            self.appdata_dir / 'logs',
            self.appdata_dir / 'temp'
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {directory}")

        # Create local directories if they don't exist
        local_dirs = ['inputs', 'results', 'presets', 'logs']
        for dir_name in local_dirs:
            (self.install_dir / dir_name).mkdir(exist_ok=True)

        print("Directory structure created successfully!")

    def register_file_associations(self):
        """Register .bin file association with BSEE."""
        print("Registering file associations...")

        try:
            # Create file association for .bin files
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, '.bin') as key:
                winreg.SetValue(key, None, winreg.REG_SZ, 'BSEE.BinaryFile')

            # Create ProgID for BSEE binary files
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 'BSEE.BinaryFile') as key:
                winreg.SetValue(key, None, winreg.REG_SZ, 'BSEE Binary File')
                winreg.SetValueEx(key, 'FriendlyTypeName', 0, winreg.REG_SZ, 'BSEE Binary File')

            with winreg.CreateKey(key, 'shell') as shell_key:
                with winreg.CreateKey(shell_key, 'open') as open_key:
                    with winreg.CreateKey(open_key, 'command') as cmd_key:
                        command = f'"{sys.executable}" "{self.install_dir}\\gui_main.py" "%1"'
                        winreg.SetValue(cmd_key, None, winreg.REG_SZ, command)

                with winreg.CreateKey(shell_key, 'analyze') as analyze_key:
                    winreg.SetValue(analyze_key, None, winreg.REG_SZ, 'Analyze with BSEE')
                    with winreg.CreateKey(analyze_key, 'command') as cmd_key:
                        command = f'"{sys.executable}" "{self.install_dir}\\gui_main.py" "%1"'
                        winreg.SetValue(cmd_key, None, winreg.REG_SZ, command)

            print("  Registered .bin file association")
            print("File associations registered successfully!")

        except PermissionError:
            print("  Warning: Administrator privileges required for file associations")
        except Exception as e:
            print(f"  Error registering file associations: {e}")

    def create_desktop_shortcuts(self):
        """Create desktop shortcuts."""
        print("Creating desktop shortcuts...")

        try:
            # Create desktop shortcut for BSEE GUI
            self._create_shortcut(
                target=str(self.install_dir / 'gui_main.py'),
                shortcut_path=self.desktop_dir / 'BSEE GUI.lnk',
                description='BSEE - Binary Structure Exploration Engine',
                icon=str(self.install_dir / 'bsee.ico') if (self.install_dir / 'bsee.ico').exists() else None
            )

            # Create desktop shortcut for BSEE CLI
            self._create_shortcut(
                target=f'cmd.exe /k "cd /d {self.install_dir} && python main.py --help"',
                shortcut_path=self.desktop_dir / 'BSEE CLI.lnk',
                description='BSEE Command Line Interface'
            )

            print("Desktop shortcuts created successfully!")

        except Exception as e:
            print(f"  Error creating desktop shortcuts: {e}")

    def create_start_menu_shortcuts(self):
        """Create Start Menu shortcuts."""
        print("Creating Start Menu shortcuts...")

        try:
            bsee_menu_dir = self.start_menu_dir / 'BSEE'
            bsee_menu_dir.mkdir(exist_ok=True)

            # Create Start Menu shortcut for BSEE GUI
            self._create_shortcut(
                target=str(self.install_dir / 'gui_main.py'),
                shortcut_path=bsee_menu_dir / 'BSEE GUI.lnk',
                description='BSEE - Binary Structure Exploration Engine',
                icon=str(self.install_dir / 'bsee.ico') if (self.install_dir / 'bsee.ico').exists() else None
            )

            # Create shortcut to inputs folder
            self._create_shortcut(
                target=str(self.appdata_dir / 'inputs'),
                shortcut_path=bsee_menu_dir / 'Input Files.lnk',
                description='BSEE Input Files Folder'
            )

            # Create shortcut to results folder
            self._create_shortcut(
                target=str(self.appdata_dir / 'results'),
                shortcut_path=bsee_menu_dir / 'Results.lnk',
                description='BSEE Results Folder'
            )

            print("Start Menu shortcuts created successfully!")

        except Exception as e:
            print(f"  Error creating Start Menu shortcuts: {e}")

    def _create_shortcut(self, target: str, shortcut_path: Path, description: str, icon: str = None):
        """Create a Windows shortcut."""
        try:
            import winshell
            from win32com.client import Dispatch

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = 'python.exe' if target.endswith('.py') else target
            shortcut.Arguments = f'"{target}"' if target.endswith('.py') else ''
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.Description = description

            if icon and Path(icon).exists():
                shortcut.IconLocation = icon
            else:
                # Try to use python icon as default
                shortcut.IconLocation = sys.executable + ', 0'

            shortcut.save()

        except ImportError:
            # Fallback method using Windows API
            self._create_shortcut_fallback(target, shortcut_path, description, icon)

    def _create_shortcut_fallback(self, target: str, shortcut_path: Path, description: str, icon: str = None):
        """Fallback shortcut creation method."""
        try:
            # Create a simple batch file as shortcut alternative
            if target.endswith('.py'):
                batch_content = f'''@echo off
cd /d "{self.install_dir}"
python "{target}"
pause
'''
                batch_file = shortcut_path.with_suffix('.bat')
                with open(batch_file, 'w') as f:
                    f.write(batch_content)
            else:
                # For non-Python targets, create a simple batch file
                batch_content = f'''@echo off
{target}
pause
'''
                batch_file = shortcut_path.with_suffix('.bat')
                with open(batch_file, 'w') as f:
                    f.write(batch_content)

        except Exception as e:
            print(f"    Could not create shortcut fallback: {e}")

    def setup_environment_variables(self):
        """Setup environment variables."""
        print("Setting up environment variables...")

        try:
            # Add BSEE to PATH if not already present
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
                try:
                    current_path = winreg.QueryValueEx(key, 'PATH')[0]
                except FileNotFoundError:
                    current_path = ''

                if str(self.install_dir) not in current_path:
                    new_path = f"{current_path};{self.install_dir}"
                    winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                    print(f"  Added {self.install_dir} to PATH")

            # Set BSEE_HOME environment variable
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
                winreg.SetValueEx(key, 'BSEE_HOME', 0, winreg.REG_SZ, str(self.install_dir))
                print(f"  Set BSEE_HOME to {self.install_dir}")

            print("Environment variables configured successfully!")

        except PermissionError:
            print("  Warning: Administrator privileges may be required for environment variables")
        except Exception as e:
            print(f"  Error setting environment variables: {e}")

    def create_windows_service(self):
        """Create Windows service (optional)."""
        print("Windows service creation is not implemented yet.")
        print("  This would require administrative privileges and additional setup.")

    def verify_installation(self):
        """Verify the installation."""
        print("Verifying installation...")

        checks = [
            ("Installation directory", self.install_dir.exists()),
            ("GUI main file", (self.install_dir / 'gui_main.py').exists()),
            ("CLI main file", (self.install_dir / 'main.py').exists()),
            ("AppData directories", self.appdata_dir.exists()),
            ("Requirements file", (self.install_dir / 'requirements.txt').exists()),
        ]

        all_passed = True
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False

        if all_passed:
            print("Installation verification passed!")
        else:
            print("Some installation checks failed. Please review the errors above.")

        return all_passed

    def run_setup(self):
        """Run complete Windows setup."""
        print("BSEE Windows Setup")
        print("=" * 50)

        try:
            self.setup_directories()
            self.register_file_associations()
            self.create_desktop_shortcuts()
            self.create_start_menu_shortcuts()
            self.setup_environment_variables()
            self.verify_installation()

            print("\nWindows setup completed successfully!")
            print("You can now:")
            print("  1. Double-click 'BSEE GUI' on your desktop to start the GUI")
            print("  2. Right-click .bin files and select 'Analyze with BSEE'")
            print("  3. Use the Start Menu shortcuts")
            print("  4. Run BSEE from command line using the enhanced PATH")

        except KeyboardInterrupt:
            print("\nSetup interrupted by user")
        except Exception as e:
            print(f"\nSetup failed: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main setup entry point."""
    if sys.platform != 'win32':
        print("This setup script is only for Windows systems.")
        sys.exit(1)

    setup = WindowsSetup()
    setup.run_setup()


if __name__ == "__main__":
    main()