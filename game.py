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
from gi.repository import Gtk, Gdk
import os
import random
from config import Theme

class Game:
    def __init__(self):
        # Help panel state
        self.show_help = False
        
        # Theme state
        self.current_theme = 'LIGHT'
        
        # Game state
        self.N = random.randint(8, 20)  # Random grid size
        self.current_position = self.N - 1  # Start at rightmost cell
        
        # Create main content
        self._create_main_content()
        
        # Create help overlay (initially hidden)
        self._create_help_overlay()
        
        # Create overlay container
        self.overlay = Gtk.Overlay()
        self.overlay.add_overlay(self.help_overlay)
        self.overlay.add(self.main_box)
        
        # Apply initial theme
        self._apply_theme()
        self._update_main_content_colors()
        
        # Initially hide help
        self.main_box.show_all()
    
    def get_widget(self):
        """Return the main widget to be used in the activity"""
        return self.overlay
    
    def _rgb_to_css(self, color):
        """Convert RGB tuple to CSS color string"""
        if len(color) == 3:
            return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        elif len(color) == 4:
            return f"rgba({color[0]}, {color[1]}, {color[2]}, {color[3]/255})"
        return "#000000"

    def _rgb_to_gdk(self, color):
        """Convert RGB tuple to Gdk.RGBA"""
        if len(color) >= 3:
            return Gdk.RGBA(color[0]/255, color[1]/255, color[2]/255, 1.0)
        return Gdk.RGBA(0, 0, 0, 1.0)
    
    def _apply_theme(self):
        """Apply current theme colors to UI"""
        theme_colors = Theme.LIGHT if self.current_theme == 'LIGHT' else Theme.DARK
        
        # Update main background
        self.main_box.override_background_color(
            Gtk.StateFlags.NORMAL, 
            self._rgb_to_gdk(theme_colors['BG'])
        )
        
        # Update CSS for help overlay
        self._update_help_theme()
    
    def _update_help_theme(self):
        """Update help overlay theme"""
        theme_colors = Theme.LIGHT if self.current_theme == 'LIGHT' else Theme.DARK
        
        css_provider = Gtk.CssProvider()
        help_bg_color = f"rgba({theme_colors['BG'][0]}, {theme_colors['BG'][1]}, {theme_colors['BG'][2]}, 0.85)"
        card_bg_color = self._rgb_to_css(theme_colors['CARD_BG'])
        text_color = self._rgb_to_css(theme_colors['TEXT'])
        
        css_data = f"""
        .help-overlay {{
            background-color: {help_bg_color};
        }}
        .help-panel {{
            background-color: {card_bg_color};
            border: 3px solid {self._rgb_to_css(theme_colors['GRAY_DARK'])};
            border-radius: 10px;
            padding: 30px;
        }}
        .help-content {{
            font-size: 14px;
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
        """Toggle between light and dark theme"""
        self.current_theme = 'DARK' if self.current_theme == 'LIGHT' else 'LIGHT'
        self._apply_theme()
        self._update_main_content_colors()
    
    def _update_main_content_colors(self):
        """Update main content colors based on current theme"""
        theme_colors = Theme.LIGHT if self.current_theme == 'LIGHT' else Theme.DARK
        text_color = self._rgb_to_css(theme_colors['TEXT'])
        
        # Update cell colors
        for i, cell in enumerate(self.cell_labels):
            if i == self.current_position:
                cell.set_markup(f"<span size='large' weight='bold' color='{self._rgb_to_css(theme_colors['ERROR'])}'>🚶\n{i}</span>")
            elif i == 0:
                cell.set_markup(f"<span size='large' weight='bold' color='{self._rgb_to_css(theme_colors['SUCCESS'])}'>🏁\n{i}</span>")
            else:
                cell.set_markup(f"<span size='large' weight='bold' color='{text_color}'>{i}</span>")
    
    def _create_main_content(self):
        # Create main container
        self.main_box = Gtk.VBox(spacing=20)
        self.main_box.set_margin_left(0)
        self.main_box.set_margin_right(0)
        self.main_box.set_margin_top(0)
        self.main_box.set_margin_bottom(0)

        # Create grid container
        grid_container = Gtk.VBox(spacing=10)
        grid_container.set_halign(Gtk.Align.CENTER)
        grid_container.set_valign(Gtk.Align.CENTER)
        
        # Create row of cells
        cells_row = Gtk.HBox(spacing=5)
        cells_row.set_halign(Gtk.Align.CENTER)
        
        self.cell_labels = []
        
        for i in range(self.N):
            # Create cell
            cell = Gtk.Label()
            cell.set_size_request(60, 60)
            cell.set_halign(Gtk.Align.CENTER)
            cell.set_valign(Gtk.Align.CENTER)
            
            # Add border
            cell_frame = Gtk.Frame()
            cell_frame.add(cell)
            cell_frame.set_shadow_type(Gtk.ShadowType.OUT)
            
            cells_row.pack_start(cell_frame, False, False, 0)
            self.cell_labels.append(cell)
        
        grid_container.pack_start(cells_row, False, False, 0)
        
        # Add grid to main box
        self.main_box.pack_start(grid_container, True, True, 0)
        
    
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
        # Create semi-transparent background
        self.help_overlay = Gtk.EventBox()
        self.help_overlay.set_halign(Gtk.Align.FILL)
        self.help_overlay.set_valign(Gtk.Align.FILL)
        
        self.help_overlay.get_style_context().add_class("help-overlay")
        
        # Create help panel container
        help_container = Gtk.VBox()
        help_container.set_halign(Gtk.Align.CENTER)
        help_container.set_valign(Gtk.Align.CENTER)
        help_container.set_size_request(600, 400)
        
        # Create help panel
        help_panel = Gtk.VBox(spacing=15)
        help_panel.get_style_context().add_class("help-panel")
        help_panel.set_margin_left(30)
        help_panel.set_margin_right(30)
        help_panel.set_margin_top(30)
        help_panel.set_margin_bottom(30)
        
        # Help content
        help_content = Gtk.Label()
        help_text = self._load_help_content()
        help_content.set_text(help_text)
        help_content.get_style_context().add_class("help-content")
        help_content.set_halign(Gtk.Align.START)
        help_content.set_valign(Gtk.Align.START)
        help_content.set_line_wrap(True)
        help_content.set_max_width_chars(60)
        
        # Create scrolled window for help content
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(help_content)
        scrolled.set_size_request(540, 320)
        
        help_panel.pack_start(scrolled, True, True, 0)
        
        help_container.pack_start(help_panel, False, False, 0)
        self.help_overlay.add(help_container)
        
        # Connect click events to close help when clicking outside
        self.help_overlay.connect("button-press-event", self._on_help_overlay_click)
        
        # Connect key events for ESC key
        self.help_overlay.set_can_focus(True)
        self.help_overlay.connect("key-press-event", self._on_key_press)
    
    def toggle_help(self):
        """Toggle help panel visibility"""
        self.show_help = not self.show_help
        if self.show_help:
            self.help_overlay.show()
            self.help_overlay.grab_focus()
        else:
            self.help_overlay.hide()
    
    def hide_help(self):
        """Hide help panel"""
        self.show_help = False
        self.help_overlay.hide()
    
    def _on_help_overlay_click(self, widget, event):
        """Close help when clicking outside the help panel"""
        # Get the help panel widget
        allocation = widget.get_child().get_allocation()
        if (event.x < allocation.x or 
            event.x > allocation.x + allocation.width or
            event.y < allocation.y or 
            event.y > allocation.y + allocation.height):
            self.hide_help()
        return False
    
    def _on_key_press(self, widget, event):
        """Handle key press events"""
        if event.keyval == Gdk.KEY_Escape:
            self.hide_help()
            return True
        return False
    
    def reset_game(self):
        """Reset the game with a new random N"""
        self.N = random.randint(8, 20)
        self.current_position = self.N - 1

        if hasattr(self, 'main_box'):
            self.overlay.remove(self.main_box)
            self.main_box.destroy()

        self._create_main_content()

        self.overlay.add(self.main_box)
        
        self._apply_theme()
        self._update_main_content_colors()

        self.main_box.show_all()
        
