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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import pygame
from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.palette import Palette
from gettext import gettext as _

import sugargame.canvas
from game import Game

class OddScoring(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        
        # Create toolbar
        self._create_toolbar()
        
        # Create a simple label
        self.game = Game()

        # Sugar Pygame canvas
        self._pygamecanvas = sugargame.canvas.PygameCanvas(
            self, main=self.game.run, modules=[pygame.display, pygame.font]
        )
        self.game.set_canvas(self._pygamecanvas)

        self.set_canvas(self._pygamecanvas)
        self._pygamecanvas.grab_focus()
    
    def _create_toolbar(self):
        toolbar_box = ToolbarBox()
        self.set_toolbar_box(toolbar_box)

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)

        help_button = ToolButton("toolbar-help")
        help_button.set_tooltip("Help")
        help_button.connect("clicked", self._show_help)
        toolbar_box.toolbar.insert(help_button, -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)

        toolbar_box.show_all()

    def _show_help(self, button):
        self.game.toggle_help()

    def _reset_game(self, button):
        self.game.handle_game_over_click()

    def _toggle_theme(self, button):
        self.game.toggle_theme()

    def read_file(self, file_path):
        self.game.read_file(file_path)

    def write_file(self, file_path):
        self.game.write_file(file_path)

    def close(self):
        self.game.quit()