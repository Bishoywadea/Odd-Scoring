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
from gi.repository import Gtk
from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbutton import ToolButton
from gettext import gettext as _
from game import Game  # Import the Game class

class OddScoring(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        
        # Create toolbar
        self._create_toolbar()
        
        # Create game instance
        self.game = Game()
        
        # Set the game widget as the canvas
        self.set_canvas(self.game.get_widget())
        self.game.get_widget().show_all()
    
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
        self.game.toggle_theme()

    def _reset_game(self, button):
        """Reset the game"""
        self.game.reset_game()
    
    def _on_menu_clicked(self, button):
        self.game._on_menu_clicked(button)
    
    def _show_help(self, button):
        """Toggle help panel"""
        self.game.toggle_help()
    
    def read_file(self, file_path):
        """Handle file reading if needed"""
        pass
    
    def write_file(self, file_path):
        """Handle file writing if needed"""
        pass