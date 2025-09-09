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
from gi.repository import Gtk, Gdk, GLib
from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbutton import ToolButton
from gettext import gettext as _
import os
import json
import time
from sugar3.graphics.palette import Palette
from sugar3.graphics import style
from collabwrapper import CollabWrapper
from game import Game

class OddScoring(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        
        
        self._loaded_from_journal = False
        self._read_file_called = False
        
        # Create toolbar
        self._create_toolbar()
        
        # Create game instance
        try:
            self.game = Game()
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
        except Exception as e:
            print(f"ERROR: Failed to create CollabWrapper: {e}")
            self._collab = None
        
        if self._collab:
            self.game.set_collab_wrapper(self._collab)
        
        try:
            game_widget = self.game.get_widget()
            self.set_canvas(game_widget)
            
            game_widget.show_all()
        except Exception as e:
            print(f"ERROR: Failed to set canvas: {e}")
            import traceback
            traceback.print_exc()
        
        if self._collab:
            GLib.timeout_add(500, self._setup_collab)
        
        GLib.timeout_add(200, self._check_and_show_menu)
        
    
    def _setup_collab(self):
        """Setup collaboration after everything is initialized"""
        try:
            if self._collab:
                self._collab.setup()
        except Exception as e:
            print(f"ERROR: Failed to setup collaboration: {e}")
        return False
    
    def _check_and_show_menu(self):
        """Show menu only if we haven't loaded from journal"""
        try:
            if not self._read_file_called:
                self.game.show_menu()
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
        self.help_button = ToolButton("toolbar-help")
        self.help_button.set_tooltip("Help")
        self.help_button.connect("clicked", self._show_help)
        toolbar_box.toolbar.insert(self.help_button, -1)
        self.help_button.show()
        
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
    
    def _show_help(self, button):
        """Show the help dialog when help button is clicked."""
        help_message = """About the Odd Scoring Game:
The Odd Scoring Game is a strategic mathematical puzzle that combines position-based movement with parity theory (even/odd numbers). Players must think several moves ahead to control whether the total number of steps taken will be even or odd.

Game Objective:
Move your character from the starting position to cell 0 (the finish line). The twist: your victory depends on whether the total number of steps taken throughout the game is even or odd!

How to Play:
1. Your character starts at the highest numbered cell on the board
2. On each turn, choose to move 1, 2, or 3 spaces toward position 0
3. You can only move toward 0 - no moving backwards or staying in place
4. The game ends when any player reaches cell 0
5. Victory is determined by the total step count being even or odd

Winning Conditions:
• If the total number of steps is EVEN → You win!
• If the total number of steps is ODD → Your opponent wins!

Game Modes:
• Single Player: Practice against an AI opponent
• Two Player: Challenge a friend on the same device
• Collaborative: Share the game with other Sugar users over the network
"""
        
        self._show_dialog("Odd Scoring Game Help", help_message)

    def _show_dialog(self, title, message):
        """Show custom help dialog with Sugar styling"""
        try:
            from sugar3.graphics import style
            parent_window = self.get_toplevel()
            
            dialog = Gtk.Window()
            dialog.set_title(title)
            dialog.set_modal(True)
            dialog.set_decorated(False)
            dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
            dialog.set_border_width(style.LINE_WIDTH)
            dialog.set_transient_for(parent_window)
            
            dialog_width = min(700, max(500, self.get_allocated_width() * 3 // 4))
            dialog_height = min(600, max(400, self.get_allocated_height() * 3 // 4))
            dialog.set_size_request(dialog_width, dialog_height)
            
            main_vbox = Gtk.VBox()
            main_vbox.set_border_width(style.DEFAULT_SPACING)
            dialog.add(main_vbox)
            
            header_box = Gtk.HBox()
            header_box.set_spacing(style.DEFAULT_SPACING)
            
            title_label = Gtk.Label()
            title_label.set_markup(f'<span size="large" weight="bold">{title}</span>')
            header_box.pack_start(title_label, True, True, 0)
            
            close_button = Gtk.Button()
            close_button.set_relief(Gtk.ReliefStyle.NONE)
            close_button.set_size_request(40, 40)
            
            try:
                from sugar3.graphics.icon import Icon
                close_icon = Icon(icon_name='dialog-cancel', pixel_size=24)
                close_button.add(close_icon)
            except:
                close_label = Gtk.Label()
                close_label.set_markup('<span size="x-large" weight="bold">✕</span>')
                close_button.add(close_label)
            
            close_button.connect('clicked', lambda b: dialog.destroy())
            header_box.pack_end(close_button, False, False, 0)
            
            main_vbox.pack_start(header_box, False, False, 0)
            
            separator = Gtk.HSeparator()
            main_vbox.pack_start(separator, False, False, style.DEFAULT_SPACING)
            
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled.set_hexpand(True)
            scrolled.set_vexpand(True)
            
            content_label = Gtk.Label()
            content_label.set_text(message)
            content_label.set_halign(Gtk.Align.START)
            content_label.set_valign(Gtk.Align.START)
            content_label.set_line_wrap(True)
            content_label.set_max_width_chars(90)
            content_label.set_selectable(True)
            content_label.set_margin_left(15)
            content_label.set_margin_right(15)
            content_label.set_margin_top(15)
            content_label.set_margin_bottom(15)
            
            scrolled.add(content_label)
            main_vbox.pack_start(scrolled, True, True, 0)
            
            try:
                css_provider = Gtk.CssProvider()
                css_data = """
                window {
                    background-color: #ffffff;
                    border: 3px solid #4A90E2;
                    border-radius: 12px;
                }
                label {
                    color: #333333;
                }
                button {
                    border-radius: 20px;
                }
                button:hover {
                    background-color: rgba(74, 144, 226, 0.1);
                }
                scrolledwindow {
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                }
                """.encode('utf-8')
                
                css_provider.load_from_data(css_data)
                style_context = dialog.get_style_context()
                style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            except Exception as css_error:
                print(f"CSS styling failed: {css_error}")
            
            dialog.show_all()
            
            dialog.connect('key-press-event', 
                        lambda d, e: d.destroy() if Gdk.keyval_name(e.keyval) == 'Escape' else False)
            
        except Exception as e:
            print(f"Error showing help dialog: {e}")
            self._show_simple_help_fallback()

    def _show_simple_help_fallback(self):
        """Simple fallback help dialog if custom dialog fails"""
        dialog = Gtk.MessageDialog(
            parent=self.get_toplevel(),
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=_("Odd Scoring Game Help"),
        )
        dialog.format_secondary_text(
            _("Move from the starting position to cell 0. Victory depends on "
              "whether the total steps taken is even or odd! Use Move 1, 2, or 3 buttons.")
        )
        dialog.run()
        dialog.destroy()
    
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
    
    def read_file(self, file_path):
        """Load game state from Journal"""
        
        self._read_file_called = True
        
        if not os.path.exists(file_path):
            print(f"ERROR: File does not exist: {file_path}")
            GLib.timeout_add(100, lambda: self.game.show_menu())
            return
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
                try:
                    data = json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"ERROR: JSON parsing failed: {e}")
                    GLib.timeout_add(100, lambda: self.game.show_menu())
                    return
            
            game_state = data.get('game_state', {})
            if game_state:
                
                if hasattr(self.game, 'load_state'):
                    if self.game.load_state(game_state):
                        self._loaded_from_journal = True
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
                game_state = self.game.save_state()
                data['game_state'] = game_state
            else:
                print("ERROR: game object doesn't have save_state method")
            
            json_string = json.dumps(data, indent=2)
            
            with open(file_path, 'w') as f:
                f.write(json_string)
                f.flush()
                os.fsync(f.fileno())
                
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
        if self.game:
            self.game.on_collaboration_joined()

    def __buddy_joined_cb(self, collab, buddy):
        """Called when another user joins"""
        if self.game:
            self.game.on_buddy_joined(buddy)

    def __buddy_left_cb(self, collab, buddy):
        """Called when another user leaves"""
        if self.game:
            self.game.on_buddy_left(buddy)

    def __message_cb(self, collab, buddy, message):
        """Called when we receive a message"""
        if self.game:
            self.game.on_message_received(buddy, message)
        else:
            print("ERROR: No game object to handle message")
    
    def get_data(self):
        """Called by CollabWrapper when someone joins to get current state"""
        if hasattr(self.game, 'get_game_state_for_sync'):
            data = self.game.get_game_state_for_sync()
            return data
        return {}

    def set_data(self, data):
        """Called by CollabWrapper when joining to receive current state"""
        if data and hasattr(self.game, 'set_game_state_from_sync'):
            self.game.set_game_state_from_sync(data)