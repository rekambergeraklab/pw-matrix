#!/usr/bin/env python3
import sys
import os
import json
import subprocess
import argparse
import math
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QScrollArea, QGridLayout,
                             QLabel)
from PyQt6.QtGui import QPainter, QColor, QFontMetrics, QFont, QPen
from PyQt6.QtCore import Qt, QSize

CONFIG_FILE = os.path.expanduser("~/.config/pw_matrix_routing.json")

DEVICE_COLORS = [
    "#2C3E50", "#1E8449", "#76448A", "#A93226",
    "#2874A6", "#B9770E", "#117864", "#5B2C6F", "#2E4053"
]

class VerticalLabel(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor("#a0a0a0"))

        font = painter.font()
        font.setBold(True)
        font.setPointSize(14)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
        painter.setFont(font)

        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(-90)

        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(self.text)
        text_height = fm.height()

        painter.drawText(int(-text_width / 2), int(text_height / 3), self.text)
        painter.end()

    def sizeHint(self):
        font = self.font()
        font.setPointSize(14)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
        fm = QFontMetrics(font)
        return QSize(fm.height() + 20, fm.horizontalAdvance(self.text) + 20)

class RotatedLabel(QWidget):
    def __init__(self, text, tooltip="", parent=None):
        super().__init__(parent)
        self.text = text
        self.setToolTip(tooltip if tooltip else text)
        self.angle = -45
        self.highlighted = False

    def set_highlight(self, state):
        self.highlighted = state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = painter.font()

        if self.highlighted:
            painter.setPen(QColor("#FF9800"))
            font.setBold(True)
        else:
            painter.setPen(QColor("#eeeeee"))
            font.setBold(False)

        painter.setFont(font)
        painter.translate(self.width() / 2 - 8, self.height() - 6)
        painter.rotate(self.angle)
        painter.drawText(0, 0, self.text)
        painter.end()

    def sizeHint(self):
        fm = QFontMetrics(self.font())
        width = fm.horizontalAdvance(self.text)
        height = fm.height()
        rad = math.radians(abs(self.angle))
        new_width = int(width * math.cos(rad) + height * math.sin(rad))
        new_height = int(width * math.sin(rad) + height * math.cos(rad))
        return QSize(max(20, new_width), new_height + 15)

    def minimumSizeHint(self):
        return self.sizeHint()

class LeftPortLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.base_style = "background-color: #3a3a3a; color: #eeeeee; font-size: 11px; padding: 4px; font-weight: normal;"
        self.high_style = "background-color: #252525; color: #FF9800; font-size: 11px; padding: 4px; font-weight: bold; border-right: 2px solid #FF9800;"
        self.setStyleSheet(self.base_style)
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def set_highlight(self, state):
        self.setStyleSheet(self.high_style if state else self.base_style)


class PipeWireBackend:
    alsa_out_counter = 1
    alsa_in_counter = 1
    v4l2_in_counter = 1
    node_aliases = {}

    @staticmethod
    def get_outputs():
        try:
            res = subprocess.run(['pw-link', '-o'], capture_output=True, text=True)
            return [line.strip() for line in res.stdout.split('\n') if line.strip()]
        except Exception: return []

    @staticmethod
    def get_inputs():
        try:
            res = subprocess.run(['pw-link', '-i'], capture_output=True, text=True)
            return [line.strip() for line in res.stdout.split('\n') if line.strip()]
        except Exception: return []

    @staticmethod
    def get_links():
        links = set()
        try:
            res = subprocess.run(['pw-link', '-l'], capture_output=True, text=True)
            lines = res.stdout.split('\n')
            current_port = None
            for line in lines:
                if line.startswith(' ') and '|->' in line:
                    linked = line.split('|->')[1].strip()
                    links.add((current_port, linked))
                elif line.strip() and not line.startswith(' '):
                    current_port = line.strip()
            return links
        except Exception: return links

    @staticmethod
    def group_ports(ports):
        groups = {}
        for p in ports:
            if ':' in p:
                node, port = p.split(':', 1)
            else:
                node, port = 'Misc', p

            if 'midi' in node.lower() or 'midi' in port.lower():
                continue

            if node not in groups: groups[node] = []
            groups[node].append(port)

        def sort_key(item):
            return item[0].lower()

        return dict(sorted(groups.items(), key=sort_key))

    @classmethod
    def get_node_alias(cls, node_name):
        if node_name in cls.node_aliases:
            return cls.node_aliases[node_name]

        if node_name.startswith('alsa_output'):
            alias = f"alsa_out{cls.alsa_out_counter}"
            cls.alsa_out_counter += 1
            cls.node_aliases[node_name] = alias
            return alias

        elif node_name.startswith('alsa_input'):
            alias = f"alsa_in{cls.alsa_in_counter}"
            cls.alsa_in_counter += 1
            cls.node_aliases[node_name] = alias
            return alias

        elif 'v4l2' in node_name.lower():
            alias = f"v4l2_in{cls.v4l2_in_counter}"
            cls.v4l2_in_counter += 1
            cls.node_aliases[node_name] = alias
            return alias

        return node_name

    @staticmethod
    def simplify_port_name(port_name):
        port_lower = port_name.lower()

        mapping = {
            'playback_fl': 'L', 'playback_fr': 'R', 'playback_fc': 'C',
            'capture_fl': 'L', 'capture_fr': 'R', 'capture_fc': 'C',
            'monitor_fl': 'L', 'monitor_fr': 'R'
        }
        if port_lower in mapping:
            return mapping[port_lower]

        if 'monitor' in port_lower and 'aux' in port_lower:
            match = re.search(r'\d+', port_lower)
            return f"d.out-{int(match.group()) + 1}" if match else "d.out"

        if 'aux' in port_lower:
            match = re.search(r'\d+', port_lower)
            num_suffix = f"-{int(match.group()) + 1}" if match else ""
            return f"tx{num_suffix}"

        return port_name.replace('playback_', '').replace('capture_', '')

class LineOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.start_pos = None
        self.end_pos = None
        self.color = QColor(76, 175, 80, 200)

    def paintEvent(self, event):
        if self.start_pos and self.end_pos:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(self.color, 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(self.start_pos, self.end_pos)

class MatrixContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drawing = False
        self.start_grid = None
        self.draw_button = None

        self.btn_map = {}
        self.row_labels = {}
        self.col_labels = {}

        self.overlay = LineOverlay(self)

    def resizeEvent(self, event):
        self.overlay.resize(self.size())
        super().resizeEvent(event)

    def eventFilter(self, obj, event):
        if isinstance(obj, QPushButton):

            if event.type() == event.Type.Enter:
                grid_pos = self.get_grid_pos(obj)
                if grid_pos:
                    r, c = grid_pos
                    if r in self.row_labels: self.row_labels[r].set_highlight(True)
                    if c in self.col_labels: self.col_labels[c].set_highlight(True)
                return False

            elif event.type() == event.Type.Leave:
                grid_pos = self.get_grid_pos(obj)
                if grid_pos:
                    r, c = grid_pos
                    if r in self.row_labels: self.row_labels[r].set_highlight(False)
                    if c in self.col_labels: self.col_labels[c].set_highlight(False)
                return False

            elif event.type() == event.Type.MouseButtonPress:
                if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
                    self.overlay.start_pos = self.mapFromGlobal(event.globalPosition().toPoint())
                    self.overlay.end_pos = self.overlay.start_pos
                    self.overlay.color = QColor(76, 175, 80, 200) if event.button() == Qt.MouseButton.LeftButton else QColor(244, 67, 54, 200)

                    self.drawing = True
                    self.start_grid = self.get_grid_pos(obj)
                    self.draw_button = event.button()
                    self.overlay.update()
                    return False

            elif event.type() == event.Type.MouseMove and self.drawing:
                self.overlay.end_pos = self.mapFromGlobal(event.globalPosition().toPoint())
                self.overlay.update()
                return True

            elif event.type() == event.Type.MouseButtonRelease:
                if self.drawing and event.button() == self.draw_button:
                    final_pos = self.mapFromGlobal(event.globalPosition().toPoint())

                    self.drawing = False
                    self.overlay.start_pos = None
                    self.overlay.end_pos = None
                    self.overlay.update()

                    end_grid = self.get_grid_pos_from_pixel(final_pos)
                    if self.start_grid and end_grid and self.start_grid != end_grid:
                        connect = (self.draw_button == Qt.MouseButton.LeftButton)
                        self.apply_diagonal_patch(self.start_grid, end_grid, connect)
                        return True

        return super().eventFilter(obj, event)

    def get_grid_pos(self, btn):
        for pos, mapped_btn in self.btn_map.items():
            if mapped_btn == btn: return pos
        return None

    def get_grid_pos_from_pixel(self, pos):
        global_pos = self.mapToGlobal(pos)
        for grid_pos, btn in self.btn_map.items():
            local_pos = btn.mapFromGlobal(global_pos)
            if btn.rect().contains(local_pos): return grid_pos
        return None

    def apply_diagonal_patch(self, start, end, connect=True):
        r1, c1 = start
        r2, c2 = end

        r_step = 1 if r2 > r1 else -1 if r2 < r1 else 0
        c_step = 1 if c2 > c1 else -1 if c2 < c1 else 0
        steps = max(abs(r2 - r1), abs(c2 - c1))

        for i in range(steps + 1):
            r = r1 + (i * r_step if r_step != 0 else 0)
            c = c1 + (i * c_step if c_step != 0 else 0)

            if (r, c) in self.btn_map:
                btn = self.btn_map[(r, c)]
                if connect and not btn.isChecked():
                    btn.setChecked(True)
                elif not connect and btn.isChecked():
                    btn.setChecked(False)


class PwMatrixApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # WINDOW NAME UPDATED HERE
        self.setWindowTitle("pw-matrix")
        self.resize(1150, 850)
        self.saved_links = self.load_state()
        self.device_color_map = {}

        self.setStyleSheet("""
            QMainWindow, QScrollArea { background-color: #404040; }
            QWidget#MainWidget { background-color: #404040; }
            QWidget#MatrixContainer { background-color: #252525; }
            QPushButton#RefreshBtn {
                background-color: #555555; color: white; border: 1px solid #777;
                padding: 6px 12px; border-radius: 4px; font-weight: bold;
            }
            QPushButton#RefreshBtn:hover { background-color: #666666; }
        """)

        self.main_widget = QWidget()
        self.main_widget.setObjectName("MainWidget")
        self.setCentralWidget(self.main_widget)

        self.master_layout = QVBoxLayout(self.main_widget)

        # --- TOOLBAR & CREDITS SETUP ---
        self.toolbar = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Matrix")
        self.btn_refresh.setObjectName("RefreshBtn")
        self.btn_refresh.clicked.connect(self.refresh_matrix)
        self.toolbar.addWidget(self.btn_refresh)

        self.toolbar.addStretch()

        self.header_info_layout = QVBoxLayout()
        self.header_info_layout.setSpacing(2)

        self.lbl_slogan = QLabel("Bahwa sesungguhnya kemerdekaan itu ialah hak segala bangsa.")
        self.lbl_slogan.setStyleSheet("color: #cccccc; font-size: 14px; font-style: italic;")
        self.lbl_slogan.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.lbl_credit = QLabel("developed by rekambergeraklab Yogyakarta-Indonesia v1.0.0")
        self.lbl_credit.setStyleSheet("color: #aaaaaa; font-size: 11px; font-weight: bold;")
        self.lbl_credit.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.header_info_layout.addWidget(self.lbl_slogan)
        self.header_info_layout.addWidget(self.lbl_credit)

        self.toolbar.addLayout(self.header_info_layout)
        self.master_layout.addLayout(self.toolbar)

        # --- MAIN WORK AREA ---
        self.work_area_layout = QHBoxLayout()
        self.master_layout.addLayout(self.work_area_layout)

        self.lbl_source = VerticalLabel("S O U R C E")
        self.work_area_layout.addWidget(self.lbl_source)

        self.right_side_layout = QVBoxLayout()
        self.work_area_layout.addLayout(self.right_side_layout)

        self.lbl_dest = QLabel("D E S T I N A T I O N")
        self.lbl_dest.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_dest.setStyleSheet("color: #a0a0a0; font-weight: bold; font-size: 14pt; letter-spacing: 4px; padding-bottom: 5px;")
        self.right_side_layout.addWidget(self.lbl_dest)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.matrix_widget = MatrixContainer()
        self.matrix_widget.setObjectName("MatrixContainer")
        self.grid = QGridLayout(self.matrix_widget)
        self.grid.setSpacing(1)
        self.scroll.setWidget(self.matrix_widget)

        self.right_side_layout.addWidget(self.scroll)

        self.is_updating_ui = False
        self.apply_saved_routing()
        self.refresh_matrix()

    def get_device_color(self, node_name):
        if node_name not in self.device_color_map:
            color_index = len(self.device_color_map) % len(DEVICE_COLORS)
            self.device_color_map[node_name] = DEVICE_COLORS[color_index]
        return self.device_color_map[node_name]

    def load_state(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception: pass
        return []

    def save_state(self):
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.saved_links, f, indent=4)
        except Exception as e: print(f"Failed to save state: {e}")

    def apply_saved_routing(self):
        for out_port, in_port in self.saved_links:
            subprocess.run(['pw-link', out_port, in_port], capture_output=True)

    def refresh_matrix(self):
        self.is_updating_ui = True
        self.matrix_widget.btn_map.clear()
        self.matrix_widget.row_labels.clear()
        self.matrix_widget.col_labels.clear()

        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget is not None: widget.setParent(None)

        out_groups = PipeWireBackend.group_ports(PipeWireBackend.get_outputs())
        in_groups = PipeWireBackend.group_ports(PipeWireBackend.get_inputs())
        current_links = PipeWireBackend.get_links()

        port_style = "background-color: #3a3a3a; color: #eeeeee; font-size: 11px; padding: 4px;"

        current_col = 2
        col_mapping = []

        for raw_node, ports in in_groups.items():
            node_color = self.get_device_color(raw_node)
            display_name = PipeWireBackend.get_node_alias(raw_node)

            lbl_node = QLabel(display_name)
            lbl_node.setStyleSheet(f"background-color: {node_color}; color: #ffffff; font-weight: bold; padding: 4px;")
            lbl_node.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_node.setToolTip(raw_node)
            self.grid.addWidget(lbl_node, 0, current_col, 1, len(ports))

            for port in ports:
                display_port = PipeWireBackend.simplify_port_name(port)

                lbl_port = RotatedLabel(display_port, tooltip=f"{raw_node}:{port}")
                self.matrix_widget.col_labels[current_col] = lbl_port

                container = QWidget()
                container.setStyleSheet("background-color: #3a3a3a;")
                container.setMinimumHeight(lbl_port.sizeHint().height())

                vbox = QVBoxLayout(container)
                vbox.setContentsMargins(0, 0, 0, 0)
                vbox.addWidget(lbl_port, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)

                self.grid.addWidget(container, 1, current_col)
                col_mapping.append((current_col, f"{raw_node}:{port}"))
                current_col += 1

        current_row = 2
        for raw_node, ports in out_groups.items():
            node_color = self.get_device_color(raw_node)
            display_name = PipeWireBackend.get_node_alias(raw_node)

            lbl_node = QLabel(display_name)
            lbl_node.setStyleSheet(f"background-color: {node_color}; color: #ffffff; font-weight: bold; padding: 4px;")
            lbl_node.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_node.setToolTip(raw_node)
            self.grid.addWidget(lbl_node, current_row, 0, len(ports), 1)

            for port in ports:
                display_port = PipeWireBackend.simplify_port_name(port)

                lbl_port = LeftPortLabel(display_port)
                lbl_port.setToolTip(f"Source: {raw_node}:{port}")
                self.matrix_widget.row_labels[current_row] = lbl_port

                self.grid.addWidget(lbl_port, current_row, 1)

                out_port_full = f"{raw_node}:{port}"

                for col_idx, in_port_full in col_mapping:
                    btn = QPushButton()
                    btn.setFixedSize(20, 20)
                    btn.setCheckable(True)
                    btn.setCursor(Qt.CursorShape.PointingHandCursor)

                    btn.setToolTip(f"{out_port_full}\n➔\n{in_port_full}")

                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #333333;
                            border: 1px solid #222222;
                            border-radius: 2px;
                        }
                        QPushButton:hover { background-color: #555555; }
                        QPushButton:checked {
                            background-color: #4CAF50;
                            border: 1px solid #2E7D32;
                        }
                        QPushButton:checked:hover { background-color: #66BB6A; }
                    """)

                    if (out_port_full, in_port_full) in current_links: btn.setChecked(True)
                    btn.toggled.connect(lambda checked, o=out_port_full, i=in_port_full: self.toggle_link(o, i, checked))

                    self.matrix_widget.btn_map[(current_row, col_idx)] = btn
                    btn.installEventFilter(self.matrix_widget)

                    container = QWidget()
                    container.setStyleSheet("background-color: #303030;")
                    cb_layout = QHBoxLayout(container)
                    cb_layout.addWidget(btn)
                    cb_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    cb_layout.setContentsMargins(0, 0, 0, 0)
                    self.grid.addWidget(container, current_row, col_idx)

                current_row += 1

        self.matrix_widget.overlay.raise_()
        self.is_updating_ui = False

    def toggle_link(self, out_port, in_port, checked):
        if self.is_updating_ui: return
        pair = [out_port, in_port]
        if checked:
            res = subprocess.run(['pw-link', out_port, in_port], capture_output=True)
            if res.returncode == 0 and pair not in self.saved_links:
                self.saved_links.append(pair)
        else:
            subprocess.run(['pw-link', '-d', out_port, in_port], capture_output=True)
            if pair in self.saved_links:
                self.saved_links.remove(pair)
        self.save_state()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="pw-matrix")
    parser.add_argument('--apply-only', action='store_true', help="Apply saved routing and exit")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    if args.apply_only:
        PwMatrixApp().apply_saved_routing()
        sys.exit(0)
    else:
        window = PwMatrixApp()
        window.show()
        sys.exit(app.exec())
