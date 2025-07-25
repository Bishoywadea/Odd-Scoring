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

class Game:
    def __init__(self):
        # Help panel state
        self.show_help = False
        
        # Game state
        self.N = random.randint(8, 20)
        self.current_position = self.N - 1
        
        # Create main content
        self._create_main_content()
        
        # Create help overlay (initially hidden)
        self._create_help_overlay()
        
        # Create overlay container
        self.overlay = Gtk.Overlay()
        self.overlay.add(self.main_box)
        self.overlay.add_overlay(self.help_overlay)
        
        # Initially hide help
        self.help_overlay.hide()
    
    def get_widget(self):
        """Return the main widget to be used in the activity"""
        return self.overlay
    
    def _create_main_content(self):
        # Create main container
        self.main_box = Gtk.VBox(spacing=20)
        self.main_box.set_margin_left(50)
        self.main_box.set_margin_right(50)
        self.main_box.set_margin_top(50)
        self.main_box.set_margin_bottom(50)
        
        # Game title
        title = Gtk.Label()
        title.set_markup("<span size='x-large' weight='bold'>Magic Moving Game</span>")
        title.set_halign(Gtk.Align.CENTER)
        self.main_box.pack_start(title, False, False, 0)
        
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
            cell.set_markup(f"<span size='large' weight='bold'>{i}</span>")
            cell.set_size_request(60, 60)
            cell.set_halign(Gtk.Align.CENTER)
            cell.set_valign(Gtk.Align.CENTER)
            
            # Style the cell
            if i == self.current_position:
                # Character position
                cell.set_markup(f"<span size='large' weight='bold' color='red'>🚶\n{i}</span>")
            elif i == 0:
                # Finish line
                cell.set_markup(f"<span size='large' weight='bold' color='green'>🏁\n{i}</span>")
            
            # Add border
            cell_frame = Gtk.Frame()
            cell_frame.add(cell)
            cell_frame.set_shadow_type(Gtk.ShadowType.OUT)
            
            cells_row.pack_start(cell_frame, False, False, 0)
            self.cell_labels.append(cell)
        
        grid_container.pack_start(cells_row, False, False, 0)
        
        # Add grid to main box
        self.main_box.pack_start(grid_container, True, True, 0)
        
        # Game info
        info_label = Gtk.Label()
        info_label.set_markup(f"<span size='medium'>Grid Size: {self.N} cells | Current Position: {self.current_position}</span>")
        info_label.set_halign(Gtk.Align.CENTER)
        self.main_box.pack_start(info_label, False, False, 0)
    
    def _load_help_content(self):
        """Load help content from help.txt file"""
        help_file_path = os.path.join(os.path.dirname(__file__), 'help.txt')
        
        try:
            with open(help_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Default help content if file doesn't exist
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
        
        # Set background color with transparency (like pygame version)
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        .help-overlay {
            background-color: rgba(255, 255, 255, 0.85);
        }
        .help-panel {
            background-color: white;
            border: 3px solid black;
            border-radius: 10px;
            padding: 30px;
        }
        .help-title {
            font-size: 24px;
            font-weight: bold;
            color: black;
            margin-bottom: 15px;
        }
        .help-content {
            font-size: 14px;
            color: black;
        }
        """)
        
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
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
        
        # Title only (no close button) - fixed markup
        help_title = Gtk.Label()
        help_title.set_markup("<span size='24000' weight='bold'>HELP</span>")
        help_title.set_halign(Gtk.Align.CENTER)
        
        help_panel.pack_start(help_title, False, False, 0)
        
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