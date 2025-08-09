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

class Game:
    def __init__(self):
        self.current_theme = 'LIGHT'
        self.game_mode = None
        self.show_help = False

        self.N = 0
        self.current_position = 0
        self.total_steps = 0
        self.game_over = False
        self.current_player = 1
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
    
    def _create_cell_content(self, cell_index):
        """Create the content for a cell (image + number)"""
        vbox = Gtk.VBox(spacing=2, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        
        image_container = Gtk.VBox(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        image_container.set_size_request(32, 32)
        
        number_label = Gtk.Label()
        
        vbox.pack_start(image_container, False, False, 0)
        vbox.pack_start(number_label, False, False, 0)
        
        return vbox, image_container, number_label

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
        btn_bot.connect("clicked", self._start_game, 'VS_BOT')
        button_box.pack_start(btn_bot, False, False, 0)

        btn_player = Gtk.Button(label="Play vs. Player")
        btn_player.get_style_context().add_class("menu-button")
        btn_player.connect("clicked", self._start_game, 'VS_PLAYER')
        button_box.pack_start(btn_player, False, False, 0)
        
        menu_panel.pack_start(button_box, False, False, 0)
        centering_box.pack_start(menu_panel, False, False, 0)
        main_container.pack_start(centering_box, True, True, 0)
        
        main_container.show_all()
        self.menu_page_container = main_container
        return main_container
        
    def _start_game(self, widget, mode):
        self.game_mode = mode
        self.reset_game()
        self.stack.set_visible_child_name("game_page")
    
    def _create_game_page(self):
        self._create_main_content()
        self._create_help_overlay()

        self.overlay = Gtk.Overlay()
        self.overlay.add(self.main_box)
        self.overlay.add_overlay(self.help_overlay)
        
        self.overlay.show()
        return self.overlay
        
    def _create_main_content(self):
        main_container = Gtk.VBox(halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
        main_container.set_hexpand(True)
        main_container.set_vexpand(True)
        
        content_container = Gtk.VBox(spacing=15, margin=20)
        content_container.set_halign(Gtk.Align.CENTER)
        content_container.set_valign(Gtk.Align.CENTER)
        content_container.set_hexpand(False)
        content_container.set_vexpand(False)

        top_bar = Gtk.HBox(spacing=10)

        label_vbox = Gtk.VBox(halign=Gtk.Align.CENTER, hexpand=True)
        self.title_label = Gtk.Label()
        self.info_label = Gtk.Label()
        label_vbox.pack_start(self.title_label, False, False, 0)
        label_vbox.pack_start(self.info_label, False, False, 0)
        top_bar.pack_start(label_vbox, True, True, 0)
        
        content_container.pack_start(top_bar, False, False, 5)
        
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

    def _on_menu_clicked(self, button):
        self.stack.set_visible_child_name("menu_page")
    
    def _player_move(self, widget, steps):
        if self.game_over: return
        self.current_position -= steps
        self.total_steps += steps
        if self._check_game_over(): return
        if self.game_mode == 'VS_BOT':
            self.current_player = 2
            self._update_ui_state()
            GLib.timeout_add(1000, self._computer_move)
        else:
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
            self._update_ui_state()
            return True
        return False
    
    def _update_ui_state(self):
        theme_colors = Theme.LIGHT if self.current_theme == 'LIGHT' else Theme.DARK
        text_color = self._rgb_to_css(theme_colors['TEXT'])
        error_color = self._rgb_to_css(theme_colors['ERROR'])
        success_color = self._rgb_to_css(theme_colors['SUCCESS'])
        
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
        
        self.grid_container.show_all()
        
        if self.game_over:
            is_total_even = self.total_steps % 2 == 0
            winner = ("You" if is_total_even else "Computer") if self.game_mode == 'VS_BOT' else ("Player 1" if is_total_even else "Player 2")
            result_color = self._rgb_to_css(theme_colors['SUCCESS'])
            self.title_label.set_markup(f"<span size='x-large' weight='bold' color='{result_color}'>{winner.upper()} WINS!</span>")
            self.info_label.set_markup(f"<span color='{text_color}'>Game Over! Total steps: {self.total_steps}.</span>")
        else:
            turn_text = ("Your Turn" if self.current_player == 1 else "Computer's Turn") if self.game_mode == 'VS_BOT' else f"Player {self.current_player}'s Turn"
            mode_text = "vs. Computer" if self.game_mode == 'VS_BOT' else "Player vs. Player"
            self.title_label.set_markup(f"<span size='x-large' weight='bold' color='{text_color}'>{mode_text}</span>")
            self.info_label.set_markup(f"<span color='{text_color}'>Grid: {self.N} | Steps: {self.total_steps} | <span weight='bold'>{turn_text}</span></span>")
        
        is_human_turn = (self.game_mode == 'VS_PLAYER') or (self.game_mode == 'VS_BOT' and self.current_player == 1)
        for i, button in enumerate(self.move_buttons):
            can_move = self.current_position - (i + 1) >= 0
            button.set_sensitive(is_human_turn and not self.game_over and can_move)
    
    def reset_game(self):
        self.N = random.randint(8, 20)
        self.current_position = self.N - 1
        self.total_steps = 0
        self.game_over = False
        self.current_player = 1
        
        for child in self.grid_container.get_children():
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
        
        self.cell_labels = []
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
        if self.show_help: 
            self.hide_help()
            
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
        text_color_css = self._rgb_to_css(theme_colors['TEXT'])

        self.menu_page_container.override_background_color(Gtk.StateFlags.NORMAL, bg_color)
        self.main_box.override_background_color(Gtk.StateFlags.NORMAL, bg_color)
        
        self.menu_title.set_markup("<b>Odd Scoring Game</b>")
        self.menu_subtitle.set_markup("Choose your opponent:")

        self._update_css_theme()

        if self.game_mode:
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

        /* Menu Buttons (Play vs Bot, etc.) */
        .menu-button {{
            font-size: 16px;
            padding: 15px;
            background-color: {btn_primary_bg};
            color: {text_light_color};
        }}
        .menu-button:hover {{
            opacity: 0.9;
        }}

        /* Move Buttons (1, 2, 3) */
        .move-button {{
            font-size: 16px;
            padding: 10px 20px;
            background-color: {btn_move_bg};
            color: {text_color};
        }}

        /* Secondary buttons (like 'Back to Menu') */
        .secondary-button {{
            font-size: 14px;
            padding: 8px 16px;
            background-color: {btn_secondary_bg};
            color: {text_light_color};
        }}
        
        /* Help Panel */
        .help-overlay {{ 
            background-color: {help_bg_rgba}; 
        }}
        .help-panel {{
            background-color: {card_bg};
            border: 2px solid {border_color};
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
        """.encode('utf-8')
        
        css_provider.load_from_data(css_data)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def toggle_theme(self):
        self.current_theme = 'DARK' if self.current_theme == 'LIGHT' else 'LIGHT'
        self._apply_theme()

    def _load_help_content(self):
        return """HOW TO PLAY:
    • Character starts at the highest numbered cell
    • Take turns moving toward cell 0 by 1, 2, or 3 spaces
    • Game ends when character reaches the finish line (cell 0)

    WINNING:
    • If total steps taken is EVEN → You win!
    • If total is ODD → The opponent wins!

    GAME LAYOUT:
    • Numbers represent positions from highest to 0
    • Character moves from higher numbers toward 0
    • Multi-row layout preserves number sequence automatically

    CONTROLS:
    • Click "1", "2", or "3" buttons to move that many spaces
    • Use toolbar buttons to restart, change theme, or return to menu"""
    
    def _create_help_overlay(self):
        self.help_overlay = Gtk.EventBox(halign=Gtk.Align.FILL, valign=Gtk.Align.FILL)
        self.help_overlay.get_style_context().add_class("help-overlay")
        
        centering_box = Gtk.VBox(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        centering_box.set_hexpand(True)
        centering_box.set_vexpand(True)
        
        help_panel = Gtk.VBox(spacing=15)
        
        help_width = min(600, self.screen_width - 100)
        help_height = min(480, self.screen_height - 100)
        help_panel.set_size_request(help_width, help_height)
        
        help_panel.get_style_context().add_class("help-panel")
        
        help_title = Gtk.Label()
        help_title.get_style_context().add_class("help-title")
        help_title.set_markup("<b>HOW TO PLAY</b>")
        help_panel.pack_start(help_title, False, False, 0)
        
        help_content = Gtk.Label()
        help_content.set_text(self._load_help_content())
        help_content.set_halign(Gtk.Align.START)
        help_content.set_valign(Gtk.Align.START)
        help_content.set_line_wrap(True)
        help_content.set_max_width_chars(60)
        help_content.get_style_context().add_class("help-content")
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(help_content)
        help_panel.pack_start(scrolled, True, True, 0)
        
        centering_box.pack_start(help_panel, False, False, 0)
        self.help_overlay.add(centering_box)
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
        centering_box = widget.get_child()
        if not centering_box:
            return False
        help_panel = centering_box.get_children()[0] if centering_box.get_children() else None
        if not help_panel:
            return False
        
        allocation = help_panel.get_allocation()
        parent_allocation = centering_box.get_allocation()
        
        panel_x = parent_allocation.x + allocation.x
        panel_y = parent_allocation.y + allocation.y
        
        if (event.x < panel_x or event.x > panel_x + allocation.width or
            event.y < panel_y or event.y > panel_y + allocation.height):
            self.hide_help()
        return False
    
    def _on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.hide_help()
            return True
        return False