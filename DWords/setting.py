from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt
from .version import VERSION
from . import utils, real_path

class Setting(QDialog):

    def __init__(self):
        super().__init__()
        self._data = {}

        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowTitle("DWords - Setting")
        self.setWindowIcon(QIcon(real_path("img/logo.svg")))
        self.setMinimumWidth(330)
        self.setAttribute(Qt.WA_DeleteOnClose)

        body = QVBoxLayout()
        self.setLayout(body)

        setting = QTabWidget()
        body.addWidget(setting)

        self._account_setting = QWidget()
        self._danmuku_setting = QWidget()
        self._about = QWidget()

        self.initAccountSetting()
        self.initDanmukuSetting()
        self.initAbout()

        setting.addTab(self._account_setting, "Account Setting")
        setting.addTab(self._danmuku_setting, "Danmuku Setting")
        setting.addTab(self._about, "About")

        btns = QHBoxLayout()
        ok = QPushButton("OK")
        ok.clicked.connect(self.clickOK)
        apply = QPushButton("Apply")
        apply.clicked.connect(self.clickApply)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.clickCancel)
        btns.addStretch(1)
        btns.addWidget(ok)
        btns.addWidget(apply)
        btns.addWidget(cancel)

        body.addLayout(btns)

    def initAccountSetting(self):
        widget = self._account_setting
        layout = QVBoxLayout()
        widget.setLayout(layout)

        label_email = QLabel("Email: ")
        edit_email = QLineEdit(utils.get_setting("email"))
        edit_email.key = "email"
        edit_email.textChanged.connect(self.accountSettingChanged)

        label_password = QLabel("Password: ")
        edit_password = QLineEdit(utils.get_setting("password"))
        edit_password.key = "password"
        edit_password.setEchoMode(QLineEdit.Password)
        edit_password.textChanged.connect(self.accountSettingChanged)

        label_smtp = QLabel("SMTP server: ")
        edit_smtp = QLineEdit(utils.get_setting("smtp_server"))
        edit_smtp.key = "smtp_server"
        edit_smtp.textChanged.connect(self.accountSettingChanged)

        label_pop3 = QLabel("POP3 server: ")
        edit_pop3 = QLineEdit(utils.get_setting("pop3_server"))
        edit_pop3.key = "pop3_server"
        edit_pop3.textChanged.connect(self.accountSettingChanged)

        layout.addWidget(label_email)
        layout.addWidget(edit_email)
        layout.addWidget(label_password)
        layout.addWidget(edit_password)
        layout.addWidget(label_smtp)
        layout.addWidget(edit_smtp)
        layout.addWidget(label_pop3)
        layout.addWidget(edit_pop3)

    def accountSettingChanged(self, value):
        self._data[self.sender().key] = value

    def initDanmukuSetting(self):
        widget = self._danmuku_setting
        layout = QVBoxLayout()
        widget.setLayout(layout)

        speed = utils.get_setting("danmuku_speed")
        label_speed = QLabel("Speed: %.2f" % (speed * 100))
        layout.addWidget(label_speed)
        self._label_speed = label_speed

        slider_speed = QSlider(Qt.Horizontal)
        slider_speed.setValue(99 - utils.value2progress("danmuku_speed", speed))
        slider_speed.valueChanged.connect(self.speedChanged)
        layout.addWidget(slider_speed)

        frequency = utils.get_setting("danmuku_frequency")
        label_frequency = QLabel("Frequency: per %.2fs" % (frequency / 1000))
        layout.addWidget(label_frequency)
        self._label_frequency = label_frequency

        slider_frequency = QSlider(Qt.Horizontal)
        slider_frequency.setValue(utils.value2progress("danmuku_frequency", frequency))
        slider_frequency.valueChanged.connect(self.frequencyChanged)
        layout.addWidget(slider_frequency)

        default_color = utils.get_setting("danmuku_default_color")
        label_color = QLabel("Default Color")
        layout.addWidget(label_color)
        colors = QHBoxLayout()
        for name, (color, _) in utils.COLORS.items():
            rbtn = QRadioButton(None)
            qss = f"""
            QRadioButton::indicator {{ width:13px; height:13px; background-color:rgb({color}); border: 2px solid rgb({color}); }}
            QRadioButton::indicator:checked {{ border: 2px solid black; }}
            """
            rbtn.setStyleSheet(qss)
            rbtn.setChecked(name == default_color)
            rbtn.toggled.connect(self.clickColor)
            rbtn.color = name

            colors.addWidget(rbtn)

        layout.addLayout(colors)

        transparency = utils.get_setting("danmuku_transparency")
        label_transparency = QLabel(f"Transparency: {int(transparency * 100)}%")
        layout.addWidget(label_transparency)
        self._label_transparency = label_transparency

        slider_transparency = QSlider(Qt.Horizontal)
        slider_transparency.setValue(utils.value2progress("danmuku_transparency", transparency))
        slider_transparency.valueChanged.connect(self.transparencyChanged)
        layout.addWidget(slider_transparency)

        default_show_paraphrase = utils.get_setting("danmuku_default_show_paraphrase")
        check_show_paraphrase = QCheckBox("Default show paraphrase")
        check_show_paraphrase.setChecked(default_show_paraphrase)
        check_show_paraphrase.toggled.connect(self.clickShowParaphrase)
        layout.addWidget(check_show_paraphrase)

    def speedChanged(self, progress):
        progress = 99 - progress
        value = utils.progress2value("danmuku_speed", progress)
        self._label_speed.setText("Speed: %.2f" % (value * 100))
        self._data["danmuku_speed"] = value

    def frequencyChanged(self, progress):
        value = utils.progress2value("danmuku_frequency", progress)
        self._label_frequency.setText("Frequency: per %.2fs" % (value / 1000))
        self._data["danmuku_frequency"] = value

    def clickColor(self, e):
        if e:
            sender = self.sender()
            self._data["danmuku_default_color"] = sender.color

    def transparencyChanged(self, progress):
        value = utils.progress2value("danmuku_transparency", progress)
        self._label_transparency.setText(f"Transparency: {int(value * 100)}%")
        self._data["danmuku_transparency"] = value

    def clickShowParaphrase(self, e):
        self._data["danmuku_default_show_paraphrase"] = e

    def initAbout(self):
        widget = self._about
        layout = QVBoxLayout()
        widget.setLayout(layout)

        def add_line(widget):
            line = QHBoxLayout()
            line.addStretch(1)
            line.addWidget(widget)
            line.addStretch(1)
            layout.addLayout(line)

        label_icon = QLabel()
        label_icon.setPixmap(
            QPixmap(real_path("img/logo.svg"))
            .scaled(60, 60, transformMode=Qt.SmoothTransformation)
        )
        add_line(label_icon)

        label_title = QLabel("DWords")
        label_title.setFont(QFont("Consolas", 18))
        add_line(label_title)

        label_version = QLabel("<a href='https://github.com/luyuhuang/DWords'>Homepage</a> | Version: " + VERSION)
        label_version.setOpenExternalLinks(True)
        add_line(label_version)
        add_line(QLabel("Licence: GPLv3"))

        label_author = QLabel("Author: <a href='https://luyuhuang.github.io'>Luyu Huang</a>")
        label_author.setOpenExternalLinks(True)
        add_line(label_author)

        layout.addStretch(1)

    def apply(self):
        for key, value in self._data.items():
            utils.set_setting(key, value)

    def clickOK(self):
        self.apply()
        self.close()

    def clickCancel(self):
        self.close()

    def clickApply(self):
        self.apply()
