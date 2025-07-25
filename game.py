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
import os
import random
from config import Theme

class Game:
    def __init__(self):
        self.show_help = False
        
        self.current_theme = 'LIGHT'
        
        self.N = 0
        self.current_position = 0
        self.total_steps = 0
        self.game_over = False
        self.is_player_turn = True
        
        self.move_buttons = []
        
        self._create_main_content()
        
        self._create_help_overlay()
        
        self.overlay = Gtk.Overlay()
        self.overlay.add_overlay(self.help_overlay)
        self.overlay.add(self.main_box)
        
        self.reset_game()
        
        self.main_box.show_all()
    
    def get_widget(self):
        """Return the main widget to be used in the activity"""
        return self.overlay
    
    def _rgb_to_css(self, color):
        if len(color) == 3:
            return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        elif len(color) == 4:
            return f"rgba({color[0]}, {color[1]}, {color[2]}, {color[3]/255})"
        return "#000000"

    def _rgb_to_gdk(self, color):
        if len(color) >= 3:
            return Gdk.RGBA(color[0]/255, color[1]/255, color[2]/255, 1.0)
        return Gdk.RGBA(0, 0, 0, 1.0)
    
    def _apply_theme(self):
        theme_colors = Theme.LIGHT if self.current_theme == 'LIGHT' else Theme.DARK
        self.main_box.override_background_color(
            Gtk.StateFlags.NORMAL, 
            self._rgb_to_gdk(theme_colors['BG'])
        )
        self._update_help_theme()
    
    def _update_help_theme(self):
        """Update help overlay theme"""
        theme_colors = Theme.LIGHT if self.current_theme == 'LIGHT' else Theme.DARK
        
        css_provider = Gtk.CssProvider()
        help_bg_color = f"rgba({theme_colors['BG'][0]}, {theme_colors['BG'][1]}, {theme_colors['BG'][2]}, 0.85)"
        card_bg_color = self._rgb_to_css(theme_colors['CARD_BG'])
        text_color = self._rgb_to_css(theme_colors['TEXT'])
        button_bg = self._rgb_to_css(theme_colors['GRAY_LIGHT'])

        css_data = f"""
        .help-overlay {{ background-color: {help_bg_color}; }}
        .help-panel {{
            background-color: {card_bg_color};
            border: 3px solid {self._rgb_to_css(theme_colors['GRAY_DARK'])};
            border-radius: 10px; 
            padding: 30px;
        }}
        .help-title {{
            font-size: 20px;
            font-weight: bold;
            color: {text_color};
            margin-bottom: 15px;
        }}
        .help-content {{ 
            font-size: 14px; 
            color: {text_color}; 
        }}
        .move-button {{
            font-size: 16px; font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
            background-color: {button_bg};
            color: {text_color};
        }}
        """.encode('utf-8')
        
        css_provider.load_from_data(css_data)
        
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def toggle_theme(self):
        self.current_theme = 'DARK' if self.current_theme == 'LIGHT' else 'LIGHT'
        self._apply_theme()
        self._update_ui_state()
    
    def _update_ui_state(self):
        """Central function to update all UI elements based on game state."""
        theme_colors = Theme.LIGHT if self.current_theme == 'LIGHT' else Theme.DARK
        text_color = self._rgb_to_css(theme_colors['TEXT'])

        for i, cell in enumerate(self.cell_labels):
            if i == self.current_position:
                cell.set_markup(f"<span size='large' weight='bold' color='{self._rgb_to_css(theme_colors['ERROR'])}'>🚶\n{i}</span>")
            elif i == 0:
                cell.set_markup(f"<span size='large' weight='bold' color='{self._rgb_to_css(theme_colors['SUCCESS'])}'>🏁\n{i}</span>")
            else:
                cell.set_markup(f"<span size='large' weight='bold' color='{text_color}'>{i}</span>")

        if self.game_over:
            winner = "You" if self.total_steps % 2 == 0 else "Computer"
            result_color = self._rgb_to_css(theme_colors['SUCCESS']) if winner == "You" else self._rgb_to_css(theme_colors['ERROR'])
            self.title_label.set_markup(f"<span size='x-large' weight='bold' color='{result_color}'>{winner.upper()} WINS!</span>")
            self.info_label.set_markup(f"<span color='{text_color}'>Game Over! Total steps: {self.total_steps}. Press Reset to play again.</span>")
        else:
            turn_text = "Your Turn" if self.is_player_turn else "Computer's Turn"
            self.info_label.set_markup(f"<span color='{text_color}'>Grid Size: {self.N} | Total Steps: {self.total_steps} | <span weight='bold'>{turn_text}</span></span>")
        
        for button in self.move_buttons:
            button.set_sensitive(self.is_player_turn and not self.game_over)

    def _create_main_content(self):
        self.main_box = Gtk.VBox(spacing=15)
        self.main_box.set_margin_left(0)
        self.main_box.set_margin_right(0)
        self.main_box.set_margin_top(0)
        self.main_box.set_margin_bottom(0)

        self.title_label = Gtk.Label()
        self.main_box.pack_start(self.title_label, False, False, 5)

        self.info_label = Gtk.Label()
        self.main_box.pack_start(self.info_label, False, False, 5)
        
        grid_container = Gtk.VBox(spacing=10)
        grid_container.set_halign(Gtk.Align.CENTER)
        grid_container.set_valign(Gtk.Align.CENTER)
        
        cells_row = Gtk.HBox(spacing=5)
        cells_row.set_halign(Gtk.Align.CENTER)
        
        self.cell_labels = []
        for i in range(self.N):
            cell = Gtk.Label(label=str(i))
            cell.set_size_request(60, 60)
            cell.set_halign(Gtk.Align.CENTER)
            cell.set_valign(Gtk.Align.CENTER)
            cell_frame = Gtk.Frame(shadow_type=Gtk.ShadowType.OUT)
            cell_frame.add(cell)
            cells_row.pack_start(cell_frame, False, False, 0)
            self.cell_labels.append(cell)
        
        grid_container.pack_start(cells_row, False, False, 0)
        self.main_box.pack_start(grid_container, True, True, 10)

        button_box = Gtk.HBox(spacing=10, halign=Gtk.Align.CENTER)
        self.move_buttons = []
        for i in range(1, 4):
            button = Gtk.Button(label=f"Move {i}")
            button.get_style_context().add_class("move-button")
            button.connect("clicked", self._player_move, i)
            self.move_buttons.append(button)
            button_box.pack_start(button, False, False, 0)
        self.main_box.pack_start(button_box, False, False, 10)

    def _player_move(self, widget, steps):
        if not self.is_player_turn or self.game_over:
            return
        
        self.current_position -= steps
        self.total_steps += steps
        self.is_player_turn = False
        
        if self._check_game_over():
            self._update_ui_state()
        else:
            self._update_ui_state()
            GLib.timeout_add(1000, self._computer_move)
    
    def _computer_move(self):
        if self.game_over:
            return False

        ideal_move = self.current_position % 4
        
        if ideal_move == 0:
            steps = random.randint(1, 3)
        else:
            steps = ideal_move
            
        steps = min(steps, self.current_position, 3)
        if steps == 0: steps = 1

        self.current_position -= steps
        self.total_steps += steps
        self.is_player_turn = True

        if not self._check_game_over():
            self._update_ui_state()

        return False

    def _check_game_over(self):
        if self.current_position <= 0:
            self.current_position = 0
            self.game_over = True
            self._update_ui_state()
            return True
        return False

    def reset_game(self):
        """Reset the game with a new random N and clear game state."""
        self.N = random.randint(8, 20)
        self.current_position = self.N - 1
        self.total_steps = 0
        self.game_over = False
        self.is_player_turn = True

        if hasattr(self, 'main_box') and self.main_box.get_parent():
            self.overlay.remove(self.main_box)
        
        self._create_main_content()

        self.overlay.add(self.main_box)
        
        self._apply_theme()
        self._update_ui_state()

        self.main_box.show_all()
        
        if self.show_help:
            self.hide_help()
            

    def _load_help_content(self):
        return """HOW TO PLAY:
• Character starts at the rightmost cell
• Take turns moving LEFT by 1, 2, or 3 spaces
• Game ends when character reaches the finish line (left side)

CONTROLS:
• Click "1", "2", or "3" buttons to move that many spaces
• Press ESC or click outside to close this help

WINNING:
• Count total steps taken by BOTH players
• If total is EVEN → You win!
• If total is ODD → Computer wins!

STRATEGY:
Think ahead! Every move affects the final total.
Try to make the total number of steps even."""
    
    def _create_help_overlay(self):
        self.help_overlay = Gtk.EventBox()
        self.help_overlay.set_halign(Gtk.Align.FILL)
        self.help_overlay.set_valign(Gtk.Align.FILL)
        self.help_overlay.get_style_context().add_class("help-overlay")
        
        help_panel = Gtk.VBox(spacing=15)
        help_panel.get_style_context().add_class("help-panel")
        
        help_panel.set_halign(Gtk.Align.CENTER)
        help_panel.set_valign(Gtk.Align.CENTER)
        help_panel.set_size_request(600, 450)

        help_title = Gtk.Label()
        help_title.get_style_context().add_class("help-title")
        help_title.set_markup("<b>HOW TO PLAY</b>")
        help_panel.pack_start(help_title, False, False, 0)
        
        help_content = Gtk.Label()
        help_text = self._load_help_content()
        help_content.set_text(help_text)
        help_content.get_style_context().add_class("help-content")
        help_content.set_halign(Gtk.Align.START)
        help_content.set_valign(Gtk.Align.START)
        help_content.set_line_wrap(True)
        help_content.set_max_width_chars(60)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(help_content)
        help_panel.pack_start(scrolled, True, True, 0)
        
        self.help_overlay.add(help_panel)
        
        self.help_overlay.connect("button-press-event", self._on_help_overlay_click)
        self.help_overlay.set_can_focus(True)
        self.help_overlay.connect("key-press-event", self._on_key_press)
    
    def toggle_help(self):
        self.show_help = not self.show_help
        if self.show_help:
            self.help_overlay.show_all()
            self.help_overlay.grab_focus()
        else:
            self.help_overlay.hide()
    
    def hide_help(self):
        self.show_help = False
        self.help_overlay.hide()
    
    def _on_help_overlay_click(self, widget, event):
        allocation = widget.get_child().get_allocation()
        if (event.x < allocation.x or 
            event.x > allocation.x + allocation.width or
            event.y < allocation.y or 
            event.y > allocation.y + allocation.height):
            self.hide_help()
        return False
    
    def _on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.hide_help()
            return True
        return False       
