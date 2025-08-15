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
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import os
import random
from config import Theme

from enum import Enum

from sugar3.graphics.toolbutton import ToolButton  
from sugar3.graphics.icon import Icon
from sugar3.graphics.xocolor import XoColor
from sugar3.graphics import style
from sugar3.graphics.palettemenu import PaletteMenuBox
from sugar3.graphics.palettemenu import PaletteMenuItem
from gettext import gettext as _

class GameMode(Enum):
    VS_BOT = 1
    VS_PLAYER = 2
    NETWORK_MULTIPLAYER = 3

class Game:
    def __init__(self):
        self.current_theme = 'LIGHT'
        self.game_mode = None

        self.N = 0
        self.current_position = 0
        self.total_steps = 0
        self.game_over = False
        self.current_player = 1
        self.network_button = None
        self.buddy_available = False

        self._collab = None
        self.is_host = False
        self.network_players = []
        self.my_player_number = None
        self.opponent_buddy = None
        self.game_started = False

        self.screen = Gdk.Screen.get_default()
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        
        self._load_images()

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)

        self.menu_page = self._create_menu_page()
        game_page = self._create_game_page()

        self.stack.add_named(self.menu_page, "menu_page")
        self.stack.add_named(game_page, "game_page")

        self._apply_theme()
        
    def get_widget(self):
        return self.stack

    def _load_images(self):
        """Load PNG images for player and finish line"""
        self.player_pixbuf = None
        self.finish_pixbuf = None
        
        try:
            player_path = os.path.join(os.path.dirname(__file__), 'running.png')
            if os.path.exists(player_path):
                self.player_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    player_path, 32, 32, True
                )
        except Exception as e:
            print(f"Could not load player image: {e}")
        
        try:
            finish_path = os.path.join(os.path.dirname(__file__), 'finish-line.png')
            if os.path.exists(finish_path):
                self.finish_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    finish_path, 32, 32, True
                )
        except Exception as e:
            print(f"Could not load finish image: {e}")

    def _create_menu_page(self):
        """Creates the main menu screen with a styled central panel."""
        main_container = Gtk.VBox(halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
        main_container.set_hexpand(True)
        main_container.set_vexpand(True)
        
        centering_box = Gtk.VBox(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        centering_box.set_hexpand(True)
        centering_box.set_vexpand(True)
        
        menu_panel = Gtk.VBox(spacing=15)
        menu_panel.set_hexpand(False)
        menu_panel.set_vexpand(False)
        
        menu_width = min(450, max(350, self.screen_width // 3))
        menu_panel.set_size_request(menu_width, -1)
        
        menu_panel.get_style_context().add_class("menu-panel")
        
        self.menu_title = Gtk.Label()
        self.menu_title.get_style_context().add_class("menu-panel-title")

        self.menu_subtitle = Gtk.Label()
        self.menu_subtitle.get_style_context().add_class("menu-panel-subtitle")
        
        menu_panel.pack_start(self.menu_title, False, False, 0)
        menu_panel.pack_start(self.menu_subtitle, False, False, 0)
        
        button_box = Gtk.VBox(spacing=15, margin_top=20)
        
        btn_bot = Gtk.Button(label="Play vs. Computer")
        btn_bot.get_style_context().add_class("menu-button")
        btn_bot.connect("clicked", self._start_game, GameMode.VS_BOT)
        button_box.pack_start(btn_bot, False, False, 0)

        btn_player = Gtk.Button(label="Play vs. Player (Local)")
        btn_player.get_style_context().add_class("menu-button")
        btn_player.connect("clicked", self._start_game, GameMode.VS_PLAYER)
        button_box.pack_start(btn_player, False, False, 0)

        self.network_button = Gtk.Button(label="Play vs. Player (Network)")
        self.network_button.get_style_context().add_class("menu-button")
        self.network_button.set_sensitive(False)
        self.network_button.connect("clicked", self._start_network_game_direct)
        button_box.pack_start(self.network_button, False, False, 0)
        
        menu_panel.pack_start(button_box, False, False, 0)
        centering_box.pack_start(menu_panel, False, False, 0)
        main_container.pack_start(centering_box, True, True, 0)
        
        main_container.show_all()
        self.menu_page_container = main_container
        return main_container

    def _start_network_game_direct(self, widget):
        """Start network game directly without lobby"""
        if not self.buddy_available or not self.opponent_buddy:
            print("ERROR: No buddy available for network game")
            return
        
        try:
            print("Starting direct network game...")
            self._reset_for_network_game()
            self.game_mode = GameMode.NETWORK_MULTIPLAYER
            self.is_host = True
            self.my_player_number = 1
            self.game_started = True
            
            N = random.randint(8, 20)
            self.N = N
            
            initial_state = {
                'action': 'game_start',
                'N': N,
                'current_player': 1,
                'host_player': 1,
                'guest_player': 2
            }
            print(f"Host starting new game with N={N}")
            
            if self._collab:
                self._collab.post(initial_state)
                print(f"Sent game_start message: {initial_state}")
            
            self._init_network_game(initial_state)
            
            self.stack.set_visible_child_name("game_page")
            
        except Exception as e:
            print(f"ERROR: Failed to start network game: {e}")
            import traceback
            traceback.print_exc()

    def show_menu(self):
        """Show the main menu"""
        self.game_mode = None
        self.stack.set_visible_child_name("menu_page")
        
    def _start_game(self, widget, mode):
        try:
            if mode == GameMode.VS_BOT or mode == GameMode.VS_PLAYER:
                self.game_mode = mode
                self.reset_game()
                self.stack.set_visible_child_name("game_page")
            else:
                print(f"ERROR: Unsupported game mode in _start_game: {mode}")
        except Exception as e:
            print(f"ERROR: Failed to start game: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_game_page(self):
        try:
            self._create_main_content()
            self.overlay = Gtk.Overlay()
            self.overlay.add(self.main_box)
            self.overlay.show()
            return self.overlay
        except Exception as e:
            print(f"ERROR: Failed to create game page: {e}")
            import traceback
            traceback.print_exc()
            return Gtk.VBox()

    def _reset_for_network_game(self):
        """Reset game state when preparing for network multiplayer"""
        
        self.N = 0
        self.current_position = 0
        self.total_steps = 0
        self.game_over = False
        self.current_player = 1
        
        if hasattr(self, 'cell_contents'):
            self.cell_contents = []
        
        if hasattr(self, 'grid_container'):
            for child in self.grid_container.get_children():
                self.grid_container.remove(child)
                child.destroy()
        
        self.game_started = False

    def _get_my_nick(self):
        """Get our own nickname for display"""
        try:
            from sugar3.profile import get_nick_name
            return get_nick_name()
        except:
            return "Player"
        
    def _create_main_content(self):
        main_container = Gtk.VBox(halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
        main_container.set_hexpand(True)
        main_container.set_vexpand(True)
        
        content_container = Gtk.VBox(spacing=15, margin=20)
        content_container.set_halign(Gtk.Align.CENTER)
        content_container.set_valign(Gtk.Align.CENTER)
        content_container.set_hexpand(False)
        content_container.set_vexpand(False)

        header_box = Gtk.HBox(spacing=10)
        
        back_button = Gtk.Button(label="← Menu")
        back_button.get_style_context().add_class("secondary-button")
        back_button.connect("clicked", self._on_menu_clicked)
        header_box.pack_start(back_button, False, False, 0)

        label_vbox = Gtk.VBox(halign=Gtk.Align.CENTER, hexpand=True)
        self.title_label = Gtk.Label()
        self.info_label = Gtk.Label()
        label_vbox.pack_start(self.title_label, False, False, 0)
        label_vbox.pack_start(self.info_label, False, False, 0)
        header_box.pack_start(label_vbox, True, True, 0)

        self.connection_status = Gtk.Label()
        self.connection_status.set_markup("<span color='green'>● Connected</span>")
        header_box.pack_end(self.connection_status, False, False, 0)
        
        content_container.pack_start(header_box, False, False, 5)
        
        self.grid_container = Gtk.VBox(spacing=10, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        content_container.pack_start(self.grid_container, False, False, 10)

        button_box = Gtk.HBox(spacing=10, halign=Gtk.Align.CENTER)
        self.move_buttons = []
        for i in range(1, 4):
            button = Gtk.Button(label=f"Move {i}")
            button.get_style_context().add_class("move-button")
            button.connect("clicked", self._player_move, i)
            self.move_buttons.append(button)
            button_box.pack_start(button, False, False, 0)
        content_container.pack_start(button_box, False, False, 10)
        
        main_container.pack_start(content_container, True, True, 0)
        self.main_box = main_container

    def _on_menu_clicked(self, button=None):
        if self.game_mode == GameMode.NETWORK_MULTIPLAYER:
            self.game_started = False
        self.show_menu()
    
    def _player_move(self, widget, steps):
        if self.game_over: 
            return
            
        if (self.game_mode == GameMode.NETWORK_MULTIPLAYER and 
            self.current_player != self.my_player_number):
            return
        
        if self.current_player == 2 and self.game_mode == GameMode.VS_BOT:
            return 
        
        self.current_position -= steps
        self.total_steps += steps
        
        if self.game_mode == GameMode.NETWORK_MULTIPLAYER and self._collab:
            move_message = {
                'action': 'move',
                'player': self.current_player,
                'steps': steps,
                'new_position': self.current_position,
                'total_steps': self.total_steps
            }
            try:
                self._collab.post(move_message)
            except Exception as e:
                print(f"ERROR: Failed to send move: {e}")
        
        if self._check_game_over(): 
            return
            
        if self.game_mode == GameMode.VS_BOT:
            self.current_player = 2
            self._update_ui_state()
            GLib.timeout_add(1000, self._computer_move)
        elif self.game_mode == GameMode.VS_PLAYER:
            self.current_player = 2 if self.current_player == 1 else 1
            self._update_ui_state()
        elif self.game_mode == GameMode.NETWORK_MULTIPLAYER:
            self.current_player = 2 if self.current_player == 1 else 1
            self._update_ui_state()

    def _computer_move(self):
        if self.game_over: return False
        ideal_move = self.current_position % 4
        steps = ideal_move if ideal_move != 0 else random.randint(1, 3)
        steps = min(steps, self.current_position, 3)
        if steps == 0: steps = 1
        self.current_position -= steps
        self.total_steps += steps
        if not self._check_game_over():
            self.current_player = 1
            self._update_ui_state()
        return False

    def _check_game_over(self):
        if self.current_position <= 0:
            self.current_position = 0
            self.game_over = True
            
            if self.game_mode == GameMode.NETWORK_MULTIPLAYER and self._collab:
                is_total_even = self.total_steps % 2 == 0
                winner = 1 if is_total_even else 2
                
                game_over_message = {
                    'action': 'game_over',
                    'total_steps': self.total_steps,
                    'winner': winner,
                    'final_position': self.current_position
                }
                try:
                    self._collab.post(game_over_message)
                except Exception as e:
                    print(f"ERROR: Failed to send game over: {e}")
            
            self._update_ui_state()
            self._show_game_over_dialog()
            return True
        return False

    def _show_game_over_dialog(self):
        """Show game over dialog with winner information"""
        is_total_even = self.total_steps % 2 == 0
        
        if self.game_mode == GameMode.VS_BOT:
            winner_text = "You win!" if is_total_even else "Computer wins!"
        elif self.game_mode == GameMode.VS_PLAYER:
            winner_text = f"Player {1 if is_total_even else 2} wins!"
        elif self.game_mode == GameMode.NETWORK_MULTIPLAYER:
            if is_total_even:
                winner_text = "You win!" if self.my_player_number == 1 else f"{self.opponent_buddy.props.nick} wins!"
            else:
                winner_text = "You win!" if self.my_player_number == 2 else f"{self.opponent_buddy.props.nick} wins!"
        
        GLib.timeout_add(1000, lambda: self._delayed_game_over_dialog(winner_text))

    def _delayed_game_over_dialog(self, winner_text):
        """Show Sugar-style game over dialog with winner information"""
        is_total_even = self.total_steps % 2 == 0
        
        if self.game_mode == GameMode.VS_BOT:
            winner_icon = "emblem-favorite" if is_total_even else "computer"
        elif self.game_mode == GameMode.VS_PLAYER:
            winner_icon = "emblem-favorite"
        elif self.game_mode == GameMode.NETWORK_MULTIPLAYER:
            if "You win" in winner_text:
                winner_icon = "emblem-favorite"
            else:
                winner_icon = "avatar-user"
        
        try:
            parent_window = None
            widget = self.stack
            while widget:
                if isinstance(widget, Gtk.Window):
                    parent_window = widget
                    break
                widget = widget.get_parent()
            
            dialog = Gtk.Window()
            dialog.set_title("Game Over")
            dialog.set_modal(True)
            dialog.set_decorated(False)
            dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
            dialog.set_border_width(style.LINE_WIDTH)
            dialog.set_has_resize_grip(False)
            dialog.set_type_hint(Gdk.WindowTypeHint.DIALOG)
            
            if parent_window:
                dialog.set_transient_for(parent_window)
            
            dialog_width = min(500, max(400, self.screen_width // 3))
            dialog_height = min(350, max(250, self.screen_height // 4))
            dialog.set_size_request(dialog_width, dialog_height)
            
            main_vbox = Gtk.VBox()
            main_vbox.set_border_width(style.DEFAULT_SPACING)
            dialog.add(main_vbox)
            
            header_box = Gtk.HBox()
            header_box.set_spacing(style.DEFAULT_SPACING)
            
            title_label = Gtk.Label()
            title_label.set_markup('<span size="x-large" weight="bold">Game Over!</span>')
            title_label.set_halign(Gtk.Align.START)
            header_box.pack_start(title_label, True, True, 0)
            
            close_button = Gtk.Button()
            close_button.set_relief(Gtk.ReliefStyle.NONE)
            close_button.set_tooltip_text('Close')
            close_button.set_size_request(32, 32)
            
            try:
                close_icon = Icon(icon_name='dialog-cancel', pixel_size=20)
                close_button.add(close_icon)
            except Exception as e:
                close_label = Gtk.Label()
                close_label.set_markup('<span size="large" weight="bold">✕</span>')
                close_button.add(close_label)
            
            close_button.connect('clicked', self._on_close_dialog_clicked, dialog)
            header_box.pack_end(close_button, False, False, 0)
            
            main_vbox.pack_start(header_box, False, False, 0)
            
            separator = Gtk.HSeparator()
            main_vbox.pack_start(separator, False, False, style.DEFAULT_SPACING)
            
            content_box = Gtk.VBox(spacing=style.DEFAULT_SPACING)
            content_box.set_halign(Gtk.Align.CENTER)
            content_box.set_valign(Gtk.Align.CENTER)
            content_box.set_hexpand(True)
            content_box.set_vexpand(True)
            
            winner_icon_widget = Icon(
                icon_name=winner_icon,
                pixel_size=style.XLARGE_ICON_SIZE,
                xo_color=XoColor('#00FF00,#008000') if "You win" in winner_text else XoColor()
            )
            content_box.pack_start(winner_icon_widget, False, False, 0)
            
            winner_label = Gtk.Label()
            winner_color = '#4CAF50' if "You win" in winner_text else '#2196F3'
            winner_label.set_markup(f'<span size="xx-large" weight="bold" color="{winner_color}">{winner_text}</span>')
            winner_label.set_halign(Gtk.Align.CENTER)
            content_box.pack_start(winner_label, False, False, style.DEFAULT_SPACING)
            
            stats_box = Gtk.VBox(spacing=5)
            stats_box.set_halign(Gtk.Align.CENTER)
            
            steps_label = Gtk.Label()
            steps_label.set_markup(f'<span size="large">Total Steps: <b>{self.total_steps}</b></span>')
            stats_box.pack_start(steps_label, False, False, 0)
            
            steps_type = "Even" if is_total_even else "Odd"
            steps_color = '#4CAF50' if is_total_even else '#FF9800'
            type_label = Gtk.Label()
            type_label.set_markup(f'<span size="medium" color="{steps_color}">({steps_type} number)</span>')
            stats_box.pack_start(type_label, False, False, 0)
            
            grid_label = Gtk.Label()
            grid_label.set_markup(f'<span size="medium">Grid Size: {self.N}</span>')
            stats_box.pack_start(grid_label, False, False, 0)
            
            content_box.pack_start(stats_box, False, False, style.DEFAULT_SPACING)
            
            main_vbox.pack_start(content_box, True, True, 0)
            
            self._apply_dialog_styling(dialog)
            
            dialog.show_all()
            
            dialog.connect('key-press-event', self._on_dialog_key_press)
            
        except Exception as e:
            print(f"ERROR: Could not show Sugar-style dialog: {e}")
            import traceback
            traceback.print_exc()
            self._show_simple_game_over_fallback(winner_text)
        
        return False
    
    def _apply_dialog_styling(self, dialog):
        """Apply Sugar-style theming to the dialog"""
        try:
            theme_colors = Theme.LIGHT if self.current_theme == 'LIGHT' else Theme.DARK
            bg_color = self._rgb_to_gdk(theme_colors['BG'])
            
            dialog.override_background_color(Gtk.StateFlags.NORMAL, bg_color)
            
            css_provider = Gtk.CssProvider()
            dialog_bg = self._rgb_to_css(theme_colors['CARD_BG'])
            text_color = self._rgb_to_css(theme_colors['TEXT'])
            border_color = self._rgb_to_css(theme_colors['GRAY_DARK'])
            
            css_data = f"""
            window {{
                background-color: {dialog_bg};
                border: 2px solid {border_color};
                border-radius: 8px;
            }}
            
            label {{
                color: {text_color};
            }}
            
            button {{
                border-radius: 6px;
                padding: 8px 16px;
                border: 1px solid {border_color};
            }}
            
            /* Style for the close button to be always visible */
            button:not(:hover) {{
                background-color: transparent;
                border: none;
            }}
            
            button:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }}
            
            separator {{
                color: {border_color};
            }}
            """.encode('utf-8')
            
            css_provider.load_from_data(css_data)
            
            style_context = dialog.get_style_context()
            style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            
        except Exception as e:
            print(f"ERROR: Failed to apply dialog styling: {e}")

    def _on_dialog_key_press(self, dialog, event):
        """Handle keyboard events in the dialog"""
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Escape' or keyname == 'Return':
            dialog.destroy()
            self.show_menu()
        return False

    def _on_close_dialog_clicked(self, button, dialog):
        """Handle close button click - return to menu"""
        dialog.destroy()
        self.show_menu()

    def _show_simple_game_over_fallback(self, winner_text):
        """Fallback to simple dialog if Sugar-style dialog fails"""
        try:
            parent = None
            widget = self.stack
            while widget:
                if isinstance(widget, Gtk.Window):
                    parent = widget
                    break
                widget = widget.get_parent()
            
            dialog = Gtk.MessageDialog(
                parent=parent,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Game Over!"
            )
            
            message = f"{winner_text}\n\nTotal steps: {self.total_steps}"
            dialog.format_secondary_text(message)
            
            def on_response(dialog, response):
                dialog.destroy()
                self.show_menu()
            
            dialog.connect('response', on_response)
            dialog.show()
            
        except Exception as e:
            print(f"ERROR: Even fallback dialog failed: {e}")
            GLib.timeout_add(2000, lambda: self.show_menu())
    
    def _create_cell_content(self, cell_index):
        """Create the content for a cell (image + number)"""
        vbox = Gtk.VBox(spacing=2, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        
        image_container = Gtk.VBox(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        image_container.set_size_request(32, 32)
        
        number_label = Gtk.Label()
        
        vbox.pack_start(image_container, False, False, 0)
        vbox.pack_start(number_label, False, False, 0)
        
        return vbox, image_container, number_label
    
    def _update_ui_state(self):
        theme_colors = Theme.LIGHT if self.current_theme == 'LIGHT' else Theme.DARK
        text_color = self._rgb_to_css(theme_colors['TEXT'])
        error_color = self._rgb_to_css(theme_colors['ERROR'])
        success_color = self._rgb_to_css(theme_colors['SUCCESS'])
        
        if hasattr(self, 'connection_status'):
            if self.game_mode == GameMode.NETWORK_MULTIPLAYER:
                self.connection_status.show()
            else:
                self.connection_status.hide()
        
        for cell_data in self.cell_contents:
            cell_index = cell_data['index']
            image_container = cell_data['image']
            number_label = cell_data['label']
            
            for child in image_container.get_children():
                child.destroy()
            
            if cell_index == self.current_position:
                if self.player_pixbuf:
                    image = Gtk.Image.new_from_pixbuf(self.player_pixbuf)
                    image_container.pack_start(image, True, True, 0)
                else:
                    fallback_label = Gtk.Label()
                    fallback_label.set_markup(f"<span color='{error_color}'>P</span>")
                    image_container.pack_start(fallback_label, True, True, 0)
                
                number_label.set_markup(f"<span size='small' weight='bold' color='{error_color}'>{cell_index}</span>")
                
            elif cell_index == 0:
                if self.finish_pixbuf:
                    image = Gtk.Image.new_from_pixbuf(self.finish_pixbuf)
                    image_container.pack_start(image, True, True, 0)
                else:
                    fallback_label = Gtk.Label()
                    fallback_label.set_markup(f"<span color='{success_color}'>F</span>")
                    image_container.pack_start(fallback_label, True, True, 0)
                
                number_label.set_markup(f"<span size='small' weight='bold' color='{success_color}'>{cell_index}</span>")
                
            else:
                number_label.set_markup(f"<span size='small' weight='bold' color='{text_color}'>{cell_index}</span>")
        
        if hasattr(self, 'grid_container'):
            self.grid_container.show_all()
        
        if self.game_over:
            is_total_even = self.total_steps % 2 == 0
            if self.game_mode == GameMode.VS_BOT:
                winner = "You" if is_total_even else "Computer"
            elif self.game_mode == GameMode.VS_PLAYER:
                winner = "Player 1" if is_total_even else "Player 2"
            elif self.game_mode == GameMode.NETWORK_MULTIPLAYER:
                if is_total_even:
                    winner = "You" if self.my_player_number == 1 else (self.opponent_buddy.props.nick if self.opponent_buddy else "Player 1")
                else:
                    winner = "You" if self.my_player_number == 2 else (self.opponent_buddy.props.nick if self.opponent_buddy else "Player 2")
            
            result_color = self._rgb_to_css(theme_colors['SUCCESS'])
            self.title_label.set_markup(f"<span size='x-large' weight='bold' color='{result_color}'>{winner.upper()} WINS!</span>")
            self.info_label.set_markup(f"<span color='{text_color}'>Game Over! Total steps: {self.total_steps}.</span>")
        else:
            if self.game_mode == GameMode.VS_BOT:
                turn_text = "Your Turn" if self.current_player == 1 else "Computer's Turn"
                mode_text = "vs. Computer"
            elif self.game_mode == GameMode.VS_PLAYER:
                turn_text = f"Player {self.current_player}'s Turn"
                mode_text = "Player vs. Player"
            elif self.game_mode == GameMode.NETWORK_MULTIPLAYER:
                if self.current_player == self.my_player_number:
                    turn_text = "Your Turn"
                else:
                    opponent_name = self.opponent_buddy.props.nick if self.opponent_buddy else "Opponent"
                    turn_text = f"{opponent_name}'s Turn"
                mode_text = "Network Game"
            
            self.title_label.set_markup(f"<span size='x-large' weight='bold' color='{text_color}'>{mode_text}</span>")
            self.info_label.set_markup(f"<span color='{text_color}'>Grid: {self.N} | Steps: {self.total_steps} | <span weight='bold'>{turn_text}</span></span>")
        
        is_human_turn = True
        if self.game_mode == GameMode.VS_BOT:
            is_human_turn = (self.current_player == 1)
        elif self.game_mode == GameMode.NETWORK_MULTIPLAYER:
            is_human_turn = (self.current_player == self.my_player_number)
        
        for i, button in enumerate(self.move_buttons):
            can_move = self.current_position - (i + 1) >= 0
            button.set_sensitive(is_human_turn and not self.game_over and can_move)
    
    def reset_game(self):
        """Reset the game for all modes"""
        if self.game_mode != GameMode.NETWORK_MULTIPLAYER:
            self.N = random.randint(8, 20)
        self.current_position = self.N - 1
        self.total_steps = 0
        self.game_over = False
        self.current_player = 1
        
        if hasattr(self, 'grid_container'):
            for child in self.grid_container.get_children():
                child.destroy()
        self._create_game_grid()
        
    def _create_game_grid(self):
        """Create game grid for all game modes"""
        if not hasattr(self, 'grid_container'):
            print("ERROR: grid_container not found!")
            return

        for child in self.grid_container.get_children():
            self.grid_container.remove(child)
            child.destroy()
        
        cell_width = 60
        cell_spacing = 5
        margin = 40
        available_width = self.screen_width - (2 * margin)
        
        cells_per_row = max(1, available_width // (cell_width + cell_spacing))
        
        if self.N <= cells_per_row:
            rows = 1
            cells_in_rows = [self.N]
        elif self.N <= cells_per_row * 2:
            rows = 2
            cells_first_row = (self.N + 1) // 2
            cells_in_rows = [cells_first_row, self.N - cells_first_row]
        else:
            rows = 3
            cells_per_full_row = self.N // 3
            extra_cells = self.N % 3
            cells_in_rows = []
            for i in range(3):
                cells_in_this_row = cells_per_full_row + (1 if i < extra_cells else 0)
                cells_in_rows.append(cells_in_this_row)
        
        self.cell_contents = []
        cell_index = self.N - 1
        
        grid_box = Gtk.VBox(spacing=5, halign=Gtk.Align.CENTER)
        
        for row in range(rows):
            row_box = Gtk.HBox(spacing=5, halign=Gtk.Align.CENTER)
            
            for col in range(cells_in_rows[row]):
                cell_content, image_container, number_label = self._create_cell_content(cell_index)
                cell_frame = Gtk.Frame(shadow_type=Gtk.ShadowType.OUT)
                cell_frame.set_size_request(cell_width, 60)
                cell_frame.add(cell_content)
                
                row_box.pack_start(cell_frame, False, False, 0)
                
                self.cell_contents.insert(0, {
                    'container': cell_content,
                    'image': image_container,
                    'label': number_label,
                    'index': cell_index
                })
                
                cell_index -= 1
        
            grid_box.pack_start(row_box, False, False, 0)
        
        self.grid_container.pack_start(grid_box, False, False, 0)
        self.grid_container.show_all()
        
        self._apply_theme()
        self._update_ui_state()
            
    def _rgb_to_css(self, color):
        if len(color) == 3: return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        elif len(color) == 4: return f"rgba({color[0]}, {color[1]}, {color[2]}, {color[3]/255})"
        return "#000000"

    def _rgb_to_gdk(self, color):
        if len(color) >= 3: return Gdk.RGBA(color[0]/255, color[1]/255, color[2]/255, 1.0)
        return Gdk.RGBA(0, 0, 0, 1.0)
    
    def _apply_theme(self):
        theme_colors = Theme.LIGHT if self.current_theme == 'LIGHT' else Theme.DARK
        bg_color = self._rgb_to_gdk(theme_colors['BG'])

        self.menu_page_container.override_background_color(Gtk.StateFlags.NORMAL, bg_color)
        if hasattr(self, 'main_box'):
            self.main_box.override_background_color(Gtk.StateFlags.NORMAL, bg_color)
        
        if hasattr(self, 'lobby_box'):
            lobby_parent = self.lobby_box.get_parent()
            if lobby_parent is not None:
                lobby_parent.override_background_color(Gtk.StateFlags.NORMAL, bg_color)
        
        self.menu_title.set_markup("<b>Odd Scoring Game</b>")
        self.menu_subtitle.set_markup("Choose your game mode:")

        self._update_css_theme()

        if self.game_mode and hasattr(self, 'cell_contents'):
            self._update_ui_state()

    def _update_css_theme(self):
        theme_colors = Theme.LIGHT if self.current_theme == 'LIGHT' else Theme.DARK
        css_provider = Gtk.CssProvider()
        
        help_bg_rgba = f"rgba({theme_colors['BG'][0]}, {theme_colors['BG'][1]}, {theme_colors['BG'][2]}, 0.85)"
        card_bg = self._rgb_to_css(theme_colors['CARD_BG'])
        text_color = self._rgb_to_css(theme_colors['TEXT'])
        text_light_color = self._rgb_to_css(Theme.LIGHT['TEXT'])
        btn_primary_bg = self._rgb_to_css(theme_colors['SUCCESS'])
        btn_secondary_bg = self._rgb_to_css(theme_colors['GRAY_DARK'])
        btn_move_bg = self._rgb_to_css(theme_colors['GRAY_LIGHT'])
        border_color = self._rgb_to_css(theme_colors['GRAY_DARK'])

        css_data = f"""
        /* The main card on the menu screen */
        .menu-panel {{
            background-color: {card_bg};
            padding: 40px;
            border-radius: 12px;
            border: 1px solid {border_color};
            min-width: 350px;
        }}
        .menu-panel-title {{
            font-size: 24px;
            font-weight: bold;
            color: {text_color};
            margin-bottom: 5px;
        }}
        .menu-panel-subtitle {{
            font-size: 15px;
            color: {text_color};
            margin-bottom: 20px;
            opacity: 0.8;
        }}

        /* General button styling */
        button {{
            border-radius: 8px;
            border: none;
            font-weight: bold;
        }}

        /* Menu Buttons */
        .menu-button {{
            font-size: 16px;
            padding: 15px;
            background-color: {btn_primary_bg};
            color: {text_light_color};
        }}
        .menu-button:hover {{
            opacity: 0.9;
        }}

        /* Move Buttons */
        .move-button {{
            font-size: 16px;
            padding: 10px 20px;
            background-color: {btn_move_bg};
            color: {text_color};
        }}

        /* Secondary buttons */
        .secondary-button {{
            font-size: 14px;
            padding: 8px 16px;
            background-color: {btn_secondary_bg};
            color: {text_light_color};
        }}

        /* Disabled network button */
        .menu-button:disabled {{
            background-color: {self._rgb_to_css(theme_colors['GRAY_LIGHT'])};
            color: {self._rgb_to_css(theme_colors['GRAY_DARK'])};
            opacity: 0.5;
        }}

        """.encode('utf-8')
        
        css_provider.load_from_data(css_data)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def toggle_theme(self):
        self.current_theme = 'DARK' if self.current_theme == 'LIGHT' else 'LIGHT'
        self._apply_theme()

    def set_collab_wrapper(self, collab):
        """Set the collaboration wrapper reference"""
        self._collab = collab
        self.is_host = False
        self.network_players = []

    def on_collaboration_joined(self):
        """Called when we successfully join a shared activity"""
        print("Successfully joined shared activity")
        self.buddy_available = False
        self.opponent_buddy = None
        self.game_started = False

    def on_buddy_joined(self, buddy):
        """Called when another player joins"""
        print(f"Buddy joined: {buddy.props.nick}")
        self.buddy_available = True
        self.opponent_buddy = buddy
        
        if hasattr(self, 'network_button') and self.network_button is not None:
            try:
                self.network_button.set_sensitive(True)
                self.network_button.set_label(f"Play vs. {buddy.props.nick}")
                print(f"Network button enabled for {buddy.props.nick}")
            except Exception as e:
                print(f"ERROR: Failed to update network button: {e}")
        else:
            print("WARNING: network_button not available yet")

    def on_buddy_left(self, buddy):
        """Called when a player leaves"""
        print(f"Buddy left: {buddy.props.nick}")
        
        if buddy == self.opponent_buddy:
            self.buddy_available = False
            self.opponent_buddy = None
            
            if hasattr(self, 'network_button') and self.network_button is not None:
                try:
                    self.network_button.set_sensitive(False)
                    self.network_button.set_label("Play vs. Player (Network)")
                    print("Network button disabled")
                except Exception as e:
                    print(f"ERROR: Failed to update network button: {e}")
            else:
                print("WARNING: network_button not available")
    def on_message_received(self, buddy, message):
        """Handle incoming collaboration messages"""
        if not isinstance(message, dict):
            print(f"ERROR: Message is not a dict, it's {type(message)}")
            return
            
        action = message.get('action')
        print(f"Received message: {action} from {buddy.props.nick}")
        
        if action == 'game_start':
            self._reset_for_network_game()
            self.game_mode = GameMode.NETWORK_MULTIPLAYER
            self.is_host = False
            self.my_player_number = 2
            self.game_started = True
            self.opponent_buddy = buddy
            print(f"Guest joining game: N={message.get('N')}")
            self._init_network_game(message)
        
        elif action == 'move':
            if (self.game_mode == GameMode.NETWORK_MULTIPLAYER and 
                hasattr(self, 'game_started') and self.game_started):
                self._handle_opponent_move(message)
        
        elif action == 'game_over':
            if self.game_mode == GameMode.NETWORK_MULTIPLAYER:
                self._handle_opponent_game_over(message)
        
    def _handle_opponent_move(self, move_data):
        """Process a move received from the opponent"""
        player = move_data.get('player')
        steps = move_data.get('steps')
        new_position = move_data.get('new_position')
        total_steps = move_data.get('total_steps')
        
        print(f"Processing opponent move: Player {player} moved {steps} steps")
        
        if player != self.current_player:
            print(f"ERROR: Received move for player {player} but current player is {self.current_player}")
            return
        
        if player == self.my_player_number:
            print("ERROR: Received move from opponent but it's marked as our move")
            return
        
        self.current_position = new_position
        self.total_steps = total_steps
        
        if self.current_position <= 0:
            self.current_position = 0
            self.game_over = True
            self._update_ui_state()
            self._show_game_over_dialog()
        else:
            self.current_player = 2 if self.current_player == 1 else 1
            self._update_ui_state()
            
            if self.current_player == self.my_player_number:
                self._notify_your_turn()

    def _handle_opponent_game_over(self, data):
        """Handle game over message from opponent"""
        winner = data.get('winner')
        total_steps = data.get('total_steps')
        final_position = data.get('final_position', 0)
        
        print(f"Received game over: winner={winner}, steps={total_steps}")
        
        self.total_steps = total_steps
        self.current_position = final_position
        self.game_over = True
        
        self._update_ui_state()
        self._show_game_over_dialog()

    def _notify_your_turn(self):
        """Notify player it's their turn with visual feedback"""
        if not hasattr(self, 'title_label'):
            return
            
        original_markup = self.title_label.get_markup()
        
        def flash_on():
            self.title_label.set_markup("<span background='#4CAF50' foreground='white'><b>  YOUR TURN!  </b></span>")
            GLib.timeout_add(500, flash_off)
            return False
        
        def flash_off():
            self.title_label.set_markup(original_markup)
            return False
        
        GLib.timeout_add(100, flash_on)

    def _init_network_game(self, initial_state):
        """Initialize the network game with given state"""
        print(f"Initializing network game with state: {initial_state}")
        
        try:
            self.game_mode = GameMode.NETWORK_MULTIPLAYER
            
            self.N = initial_state['N']
            self.current_position = self.N - 1
            self.total_steps = 0
            self.current_player = initial_state['current_player']
            self.game_over = False
            print(f"Game initialized: N={self.N}, start_pos={self.current_position}")
            
            self.stack.set_visible_child_name("game_page")
            
            self._create_game_grid()
        except Exception as e:
            print(f"ERROR: Failed to initialize network game: {e}")
            import traceback
            traceback.print_exc()

    def get_game_state_for_sync(self):
        """Get current game state for syncing with joining player"""
        if self.game_mode != GameMode.NETWORK_MULTIPLAYER or not self.game_started:
            return {}
        
        return {
            'game_in_progress': True,
            'N': self.N,
            'current_position': self.current_position,
            'total_steps': self.total_steps,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'host_player': 1,
            'guest_player': 2
        }

    def set_game_state_from_sync(self, data):
        """Set game state when joining a game in progress"""
        if data.get('game_in_progress'):
            print("Joining game in progress...")
            self.game_mode = GameMode.NETWORK_MULTIPLAYER 
            self.is_host = False
            self.my_player_number = 2
            self.game_started = True
            
            self.N = data.get('N', 10)
            self.current_position = data.get('current_position', self.N - 1)
            self.total_steps = data.get('total_steps', 0)
            self.current_player = data.get('current_player', 1)
            self.game_over = data.get('game_over', False)
            
            self.stack.set_visible_child_name("game_page")
            self.reset_game()

    def save_state(self):
        """Return the current game state as a dictionary for Journal saving"""
        import json
        
        state = {}
        
        try:
            state['game_mode'] = self.game_mode.value if self.game_mode else 1
            state['current_theme'] = self.current_theme
            state['N'] = self.N
            state['current_position'] = self.current_position
            state['total_steps'] = self.total_steps
            state['game_over'] = self.game_over
            state['current_player'] = self.current_player
            
            state['is_host'] = self.is_host
            state['my_player_number'] = self.my_player_number
            state['game_started'] = self.game_started
            
            if self.game_mode and self.N > 0:
                state['game_in_progress'] = True
            else:
                state['game_in_progress'] = False
            
            json.dumps(state)
            
        except Exception as e:
            print(f"ERROR: Failed to create save state: {e}")
            return {
                'game_mode': 1,
                'current_theme': 'LIGHT', 
                'game_in_progress': False
            }
        
        return state

    def load_state(self, state):
        """Load game state from a dictionary"""
        try:
            try:
                game_mode_value = state.get('game_mode', 1)
                self.game_mode = GameMode(game_mode_value)
            except Exception as e:
                print(f"ERROR: Failed to load game_mode: {e}")
                self.game_mode = GameMode.VS_BOT
            
            self.current_theme = state.get('current_theme', 'LIGHT')
            
            self.N = state.get('N', 0)
            self.current_position = state.get('current_position', 0)
            self.total_steps = state.get('total_steps', 0)
            self.game_over = state.get('game_over', False)
            self.current_player = state.get('current_player', 1)
            
            self.is_host = state.get('is_host', False)
            self.my_player_number = state.get('my_player_number', None)
            self.game_started = state.get('game_started', False)
            
            game_in_progress = state.get('game_in_progress', False)
            
            if game_in_progress and self.N > 0:
                
                self.stack.set_visible_child_name("game_page")
                self.reset_game()
                
                self._apply_theme()
                
            else:
                self.show_menu()
            
            return True
            
        except Exception as e:
            print(f"ERROR: Fatal error in load_state: {e}")
            import traceback
            traceback.print_exc()
            self.show_menu()
            return False