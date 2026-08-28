"""Visual theme for the approved V1 desktop shell."""

APP_STYLESHEET = """
QMainWindow, QWidget {
    background: #11161d;
    color: #d9e1ea;
    font-family: "Segoe UI";
    font-size: 10pt;
}
QToolBar {
    background: #171d25;
    border: 0;
    border-bottom: 1px solid #2a3440;
    spacing: 4px;
    padding: 6px 8px;
}
QToolButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    color: #dce5ef;
    padding: 7px 10px;
}
QToolButton:hover:enabled {
    background: #202a35;
    border-color: #334354;
}
QToolButton:disabled {
    color: #697584;
}
QSplitter::handle {
    background: #26313d;
}
QFrame#section_panel, QFrame#viewport_host {
    background: #151b23;
    border: 1px solid #293542;
    border-radius: 4px;
}
QLabel#section_title {
    color: #eef4fa;
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 0.5px;
}
QLabel#muted_label {
    color: #7f8c99;
}
QLabel#model_status {
    background: #202933;
    border: 1px solid #465260;
    border-radius: 4px;
    color: #c8d1db;
    font-weight: 700;
    padding: 7px 12px;
}
QTreeWidget, QTableWidget {
    background: #121820;
    alternate-background-color: #151d26;
    border: 0;
    color: #cbd5df;
    gridline-color: #27323e;
    selection-background-color: #243b52;
    selection-color: #ffffff;
}
QHeaderView::section {
    background: #1b232d;
    color: #aeb9c4;
    border: 0;
    border-right: 1px solid #2b3642;
    border-bottom: 1px solid #2b3642;
    padding: 6px;
    font-weight: 600;
}
QPushButton {
    min-height: 28px;
    background: #1d2630;
    color: #d7e0e9;
    border: 1px solid #344252;
    border-radius: 4px;
    padding: 4px 10px;
}
QPushButton:hover:enabled {
    background: #263441;
}
QPushButton:disabled {
    color: #65717e;
    border-color: #2a333d;
}
QStatusBar {
    background: #0d1218;
    border-top: 1px solid #28323d;
    color: #98a5b2;
}
"""
