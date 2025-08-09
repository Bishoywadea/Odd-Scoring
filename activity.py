# This file is part of the Odd Scoring Game.
# Copyright (C) 2025 Bishoy Wadea
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbutton import ToolButton
from gettext import gettext as _
import os
import json
import time
from collabwrapper import CollabWrapper
from game import Game

class OddScoring(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        
        print("DEBUG: OddScoring activity starting...")
        
        self._loaded_from_journal = False
        self._read_file_called = False
        
        # Create toolbar
        self._create_toolbar()
        print("DEBUG: Toolbar created")
        
        # Create game instance
        try:
            self.game = Game()
            print("DEBUG: Game instance created")
        except Exception as e:
            print(f"ERROR: Failed to create game: {e}")
            import traceback
            traceback.print_exc()
            return
        
        try:
            self._collab = CollabWrapper(self)
            self._collab.connect('joined', self.__joined_cb)
            self._collab.connect('buddy_joined', self.__buddy_joined_cb)
            self._collab.connect('buddy_left', self.__buddy_left_cb)
            self._collab.connect('message', self.__message_cb)
            print("DEBUG: CollabWrapper created")
        except Exception as e:
            print(f"ERROR: Failed to create CollabWrapper: {e}")
            self._collab = None
        
        if self._collab:
            self.game.set_collab_wrapper(self._collab)
            print("DEBUG: Game connected to collaboration")
        
        try:
            game_widget = self.game.get_widget()
            print(f"DEBUG: Got game widget: {game_widget}")
            self.set_canvas(game_widget)
            print("DEBUG: Canvas set")
            
            game_widget.show_all()
            print("DEBUG: Game widget shown")
        except Exception as e:
            print(f"ERROR: Failed to set canvas: {e}")
            import traceback
            traceback.print_exc()
        
        if self._collab:
            GLib.timeout_add(500, self._setup_collab)
        
        GLib.timeout_add(200, self._check_and_show_menu)
        
        print("DEBUG: OddScoring activity initialization complete")
    
    def _setup_collab(self):
        """Setup collaboration after everything is initialized"""
        print("DEBUG: Setting up collaboration")
        try:
            if self._collab:
                self._collab.setup()
        except Exception as e:
            print(f"ERROR: Failed to setup collaboration: {e}")
        return False
    
    def _check_and_show_menu(self):
        """Show menu only if we haven't loaded from journal"""
        print(f"DEBUG: _check_and_show_menu called, _read_file_called={self._read_file_called}")
        try:
            if not self._read_file_called:
                print("DEBUG: No journal file to load, showing menu")
                self.game.show_menu()
            else:
                print("DEBUG: Journal file is being loaded, not showing menu")
        except Exception as e:
            print(f"ERROR: Failed to show menu: {e}")
            import traceback
            traceback.print_exc()
        return False
    
    def _create_toolbar(self):
        toolbar_box = ToolbarBox()
        
        # Activity button
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)
        activity_button.show()

        # Main menu button
        menu_button = ToolButton('go-home')
        menu_button.set_tooltip(_('Main Menu'))
        menu_button.connect("clicked", self._on_menu_clicked)
        toolbar_box.toolbar.insert(menu_button, -1)

        # Reset button
        reset_button = ToolButton("view-refresh")
        reset_button.set_tooltip("New Game")
        reset_button.connect("clicked", self._reset_game)
        toolbar_box.toolbar.insert(reset_button, -1)
        reset_button.show()
        
        # Theme button
        theme_button = ToolButton("camera")
        theme_button.set_tooltip("Toggle Theme")
        theme_button.connect("clicked", self._toggle_theme)
        toolbar_box.toolbar.insert(theme_button, -1)
        theme_button.show()
        
        # Help button
        help_button = ToolButton("toolbar-help")
        help_button.set_tooltip("Show/Hide Help")
        help_button.connect("clicked", self._show_help)
        toolbar_box.toolbar.insert(help_button, -1)
        help_button.show()
        
        # Separator
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        
        # Stop button
        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()
        
        self.set_toolbar_box(toolbar_box)
        toolbar_box.show_all()
    
    def _toggle_theme(self, button):
        """Toggle theme"""
        try:
            self.game.toggle_theme()
        except Exception as e:
            print(f"ERROR: Failed to toggle theme: {e}")

    def _reset_game(self, button):
        """Reset the game"""
        try:
            self.game.reset_game()
        except Exception as e:
            print(f"ERROR: Failed to reset game: {e}")
    
    def _on_menu_clicked(self, button):
        try:
            self.game.show_menu()
        except Exception as e:
            print(f"ERROR: Failed to show menu: {e}")
    
    def _show_help(self, button):
        """Toggle help panel"""
        try:
            self.game.toggle_help()
        except Exception as e:
            print(f"ERROR: Failed to toggle help: {e}")
    
    def read_file(self, file_path):
        """Load game state from Journal"""
        print(f"DEBUG: read_file called with path: {file_path}")
        
        self._read_file_called = True
        
        if not os.path.exists(file_path):
            print(f"ERROR: File does not exist: {file_path}")
            GLib.timeout_add(100, lambda: self.game.show_menu())
            return
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                print(f"DEBUG: Read {len(content)} characters from file")
                
                try:
                    data = json.loads(content)
                    print(f"DEBUG: Successfully parsed JSON")
                except json.JSONDecodeError as e:
                    print(f"ERROR: JSON parsing failed: {e}")
                    GLib.timeout_add(100, lambda: self.game.show_menu())
                    return
            
            game_state = data.get('game_state', {})
            if game_state:
                print(f"DEBUG: Game state found with keys: {list(game_state.keys())}")
                
                if hasattr(self.game, 'load_state'):
                    print("DEBUG: Loading game state")
                    if self.game.load_state(game_state):
                        self._loaded_from_journal = True
                        print("DEBUG: Game state loaded successfully")
                    else:
                        print("ERROR: game.load_state() returned False")
                        GLib.timeout_add(100, lambda: self.game.show_menu())
                else:
                    print("ERROR: game object doesn't have load_state method")
                    GLib.timeout_add(100, lambda: self.game.show_menu())
            else:
                print("WARNING: No game_state in loaded data")
                GLib.timeout_add(100, lambda: self.game.show_menu())
                
        except Exception as e:
            print(f"ERROR: Unexpected error reading file: {e}")
            GLib.timeout_add(100, lambda: self.game.show_menu())

    def write_file(self, file_path):
        """Save game state to Journal"""
        print(f"DEBUG: write_file called with path: {file_path}")
        
        try:
            data = {
                'metadata': {
                    'activity': 'org.sugarlabs.OddScoring',
                    'activity_version': 1,
                    'mime_type': 'application/x-odd-scoring-game',
                    'timestamp': time.time()
                },
                'game_state': {}
            }
            
            if hasattr(self.game, 'save_state'):
                print("DEBUG: Calling game.save_state()")
                game_state = self.game.save_state()
                print(f"DEBUG: Got game state with keys: {list(game_state.keys()) if game_state else 'None'}")
                data['game_state'] = game_state
            else:
                print("ERROR: game object doesn't have save_state method")
            
            json_string = json.dumps(data, indent=2)
            print(f"DEBUG: JSON serialization successful, length: {len(json_string)}")
            
            with open(file_path, 'w') as f:
                f.write(json_string)
                f.flush()
                os.fsync(f.fileno())
                
            print(f"DEBUG: File written successfully")
                
        except Exception as e:
            print(f"ERROR: Writing file failed: {e}")

    def can_close(self):
        """Called when the activity is about to close"""
        return True

    def close(self):
        """Clean shutdown"""
        super(OddScoring, self).close()
    
    def __joined_cb(self, collab):
        """Called when we join a shared activity"""
        print("DEBUG: Joined shared activity")
        if self.game:
            self.game.on_collaboration_joined()

    def __buddy_joined_cb(self, collab, buddy):
        """Called when another user joins"""
        print(f"DEBUG: Buddy joined: {buddy.props.nick}")
        if self.game:
            self.game.on_buddy_joined(buddy)

    def __buddy_left_cb(self, collab, buddy):
        """Called when another user leaves"""
        print(f"DEBUG: Buddy left: {buddy.props.nick}")
        if self.game:
            self.game.on_buddy_left(buddy)

    def __message_cb(self, collab, buddy, message):
        """Called when we receive a message"""
        print(f"DEBUG: __message_cb called")
        print(f"DEBUG: From buddy: {buddy.props.nick}")
        print(f"DEBUG: Message content: {message}")
        
        if self.game:
            self.game.on_message_received(buddy, message)
        else:
            print("ERROR: No game object to handle message")
    
    def get_data(self):
        """Called by CollabWrapper when someone joins to get current state"""
        print("DEBUG: get_data called")
        if hasattr(self.game, 'get_game_state_for_sync'):
            data = self.game.get_game_state_for_sync()
            print(f"DEBUG: Returning game state: {data}")
            return data
        return {}

    def set_data(self, data):
        """Called by CollabWrapper when joining to receive current state"""
        print(f"DEBUG: set_data called with: {data}")
        if data and hasattr(self.game, 'set_game_state_from_sync'):
            self.game.set_game_state_from_sync(data)