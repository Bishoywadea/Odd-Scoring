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

import pygame as pg
import sys
import gi
import random
from enum import Enum
import time
import math
from gettext import gettext as _
from config import Theme

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

WIDTH, HEIGHT = 1200, 800
FPS = 60

class GameMode(Enum):
    VS_BOT = 1
    LOCAL_MULTIPLAYER = 2

class Game(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.show_help = False

    def set_canvas(self, canvas):
        self.canvas = canvas
        if self.screen:
            pg.display.set_caption(_("Odd Scoring"))

    def toggle_help(self):
        self.show_help = not self.show_help

    def run(self):
        pg.init()
        pg.font.init()
        
        self.clock = pg.time.Clock()
        
        self.screen = pg.display.get_surface()
        
        if self.screen:
            self.screen_width = self.screen.get_width()
            self.screen_height = self.screen.get_height()
        else:
            self.screen_width = WIDTH
            self.screen_height = HEIGHT
            self.screen = pg.display.set_mode((WIDTH, HEIGHT))
            pg.display.set_caption("Euclid's Game")
        
        self.font_small = pg.font.Font(None, 24)
        self.font = pg.font.Font(None, 36)
        self.font_large = pg.font.Font(None, 48)
        self.title_font = pg.font.Font(None, 72)
        
        self.bot_avatar = self.create_enhanced_bot_avatar()
        
        self.setup_squares()

        while self.running:
            while Gtk.events_pending():
                Gtk.main_iteration()

            self.handle_events()
            
            current_time = time.time()
            dt = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            self.update(dt)
            self.draw()
            self.clock.tick(FPS)

        pg.quit()
        sys.exit(0)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.handle_click(event.pos)

    def handle_click(self, mouse_pos):
        if self.show_help:
            self.show_help = False
            return

    def draw(self):
        if self.show_help:
            self.draw_enhanced_help(self.screen)

        pg.display.flip()

    def draw_enhanced_help(self, screen):
        colors = self.theme
        
        overlay = pg.Surface((self.screen_width, self.screen_height), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        help_width = 800
        help_height = 600
        help_x = (self.screen_width - help_width) // 2
        help_y = (self.screen_height - help_height) // 2
        
        self.draw_glassmorphism_panel(screen, pg.Rect(help_x, help_y, help_width, help_height))
        
        title_text = self.title_font.render(_("How to Play"), True, colors['TEXT'])
        title_rect = title_text.get_rect(center=(self.screen_width // 2, help_y + 50))
        screen.blit(title_text, title_rect)
        
        help_lines = [
            _("Odd Scoring Game Rules:"),
        ]
        
        y_offset = help_y + 100
        for line in help_lines:
            if line.strip():
                if line.endswith(":"):
                    text = self.font_large.render(line, True, colors['PRIMARY'])
                else:
                    text = self.font.render(line, True, colors['TEXT'])
                screen.blit(text, (help_x + 40, y_offset))
            y_offset += 35
        
    def quit(self):
        self.running = False

# Main execution
if __name__ == "__main__":
    game = Game()
    game.run()