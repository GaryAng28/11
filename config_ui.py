from log import logger, fileHandler, new_file_handler

logger.name = "config_ui"
logger.removeHandler(fileHandler)
logger.addHandler(new_file_handler())

import typing
import shutil
import subprocess
from PyQt5.QtWidgets import (QApplication, QFormLayout, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox,
                             QWidget, QTabWidget, QComboBox, QStyleFactory, QDoubleSpinBox, QSpinBox, QFrame, QMessageBox, QPushButton, QInputDialog, QScrollArea, QLayout)
from PyQt5.QtGui import QValidator, QIcon

from config import *
from setting import *
from version import now_version
from game_info import name_2_mobile_game_info_map


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class BiDict():
    def __init__(self, original_dict: dict):
        self.key_to_val = dict({k: v for k, v in original_dict.items()})
        self.val_to_key = dict({v: k for k, v in original_dict.items()})


def create_pushbutton(text, color="") -> QPushButton:
    btn = QPushButton(text)
    btn.setStyleSheet(f"background-color: {color}; font-weight: bold; font-family: Microsoft YaHei")

    return btn


def create_checkbox(val=False, name="") -> QCheckBox:
    checkbox = QCheckBox(name)

    checkbox.setChecked(val)

    return checkbox


def create_spin_box(value: int, maximum: int = 99999, minimum: int = 0) -> QSpinBox:
    spinbox = QSpinBox()

    spinbox.setValue(value)
    spinbox.setMaximum(maximum)
    spinbox.setMinimum(minimum)

    return spinbox


def create_double_spin_box(value: float, maximum: float = 1.0, minimum: float = 0.0) -> QDoubleSpinBox:
    spinbox = QDoubleSpinBox()

    spinbox.setValue(value)
    spinbox.setMaximum(maximum)
    spinbox.setMinimum(minimum)

    return spinbox


def create_combobox(current_val: str, values: List[str] = None) -> QComboBox:
    combobox = QComboBox()

    if values is not None:
        combobox.addItems(values)
    combobox.setCurrentText(current_val)

    return combobox


def create_lineedit(current_text: str, placeholder_text="") -> QLineEdit:
    lineedit = QLineEdit(current_text)

    lineedit.setPlaceholderText(placeholder_text)

    return lineedit


def add_form_seperator(form_layout: QFormLayout, title: str):
    form_layout.addRow(f"=== {title} ===", QHLine())


def make_scroll_layout(inner_layout: QLayout):
    widget = QWidget()
    widget.setLayout(inner_layout)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(widget)

    scroll_layout = QVBoxLayout()
    scroll_layout.addWidget(scroll)

    return scroll_layout


def list_to_str(vlist: List[str]):
    return ','.join(str(v) for v in vlist)


def str_to_list(str_list: str):
    str_list = str_list.strip(" ,")
    if str_list == "":
        return []

    return [s.strip() for s in str_list.split(',')]


class QQListValidator(QValidator):
    def validate(self, text: str, pos: int) -> typing.Tuple['QValidator.State', str, int]:
        sl = str_to_list(text)

        for qq in sl:
            if not qq.isnumeric():
                return (QValidator.Invalid, text, pos)

        return (QValidator.Acceptable, text, pos)


def show_message(title, text):
    logger.info(f"{title} {text}")

    message_box = QMessageBox()
    message_box.setWindowTitle(title)
    message_box.setText(text)
    message_box.exec_()


class ConfigUi(QFrame):
    def __init__(self, parent=None):
        super(ConfigUi, self).__init__(parent)

        self.resize(1080, 720)
        self.setWindowTitle("简易配置工具（如需要更细化配置，请使用文本编辑器编辑config.toml）")

        self.setStyleSheet(f"font-family: Microsoft YaHei")
        self.setWindowIcon(QIcon("icons/config_ui.ico"))

        self.setWhatsThis("简易配置工具")

        self.load()

        logger.info(f"配置工具启动成功，版本号为v{now_version}")

    def load(self):
        self.from_config(self.load_config())

        logger.info("已读取成功，请按需调整配置，调整完记得点下保存~")

    def notify_reopen(self, checked=False):
        show_message("请重新打开", "目前因为不知道如何清除pyqt的已有组件然后再添加新的组件，暂时没有实现重新读取配置的功能，请直接右上角关掉重新打开-。-")

    def save(self, checked=False, show_message_box=True):
        self.save_config(self.to_config())
        if show_message_box:
            show_message("保存成功", "已保存成功\nconfig.toml已不再有注释信息，如有需要，可去config.toml.example查看注释")

    def load_config(self) -> Config:
        load_config(local_config_path="")
        return config()

    def save_config(self, cfg: Config):
        save_config(cfg)

    def from_config(self, cfg: Config):
        # 根据配置初始化ui
        top_layout = QVBoxLayout()

        self.create_buttons(top_layout)
        self.create_tabs(cfg, top_layout)

        self.setLayout(top_layout)

    def create_buttons(self, top_layout: QVBoxLayout):
        btn_load = create_pushbutton("读取配置", "DeepSkyBlue")
        btn_save = create_pushbutton("保存配置", "Aquamarine")

        btn_load.clicked.connect(self.notify_reopen)
        btn_save.clicked.connect(self.save)

        layout = QHBoxLayout()
        layout.addWidget(btn_load)
        layout.addWidget(btn_save)
        top_layout.addLayout(layout)
        top_layout.addWidget(QHLine())

        btn_add_account = create_pushbutton("添加账号", "lightgreen")
        btn_del_account = create_pushbutton("删除账号", "hotpink")
        btn_clear_login_status = create_pushbutton("清除登录状态", "DarkCyan")

        btn_add_account.clicked.connect(self.add_account)
        btn_del_account.clicked.connect(self.del_account)
        btn_clear_login_status.clicked.connect(self.clear_login_status)

        layout = QHBoxLayout()
        layout.addWidget(btn_add_account)
        layout.addWidget(btn_del_account)
        layout.addWidget(btn_clear_login_status)
        top_layout.addLayout(layout)
        top_layout.addWidget(QHLine())

        btn_run_djc_helper = create_pushbutton("运行小助手", "cyan")
        btn_run_djc_helper.clicked.connect(self.run_djc_helper)
        top_layout.addWidget(btn_run_djc_helper)
        top_layout.addWidget(QHLine())

    def run_djc_helper(self):
        logger.info("运行小助手前自动保存配置")
        self.save(show_message_box=False)

        exe_path = "DNF蚊子腿小助手.exe"
        if run_from_src():
            exe_path = "main.py"
        subprocess.Popen([
            os.path.realpath(exe_path),
        ], cwd=".", shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        logger.info(f"{exe_path} 已经启动~请等待其完成操作")

    def clear_login_status(self):
        shutil.rmtree(cached_dir, ignore_errors=True)
        os.mkdir(cached_dir)

        show_message("清除完毕", "登录状态已经清除完毕，可使用新账号重新运行~")

    def add_account(self, checked=False):
        account_name, ok = QInputDialog.getText(self, "添加账号", "要添加的账号名称", QLineEdit.Normal, "")
        if ok:
            logger.info(f"尝试添加账号 {account_name} ...")

            for account in self.accounts:
                if account.lineedit_name.text() == account_name:
                    show_message("添加失败", f"已存在名称为 {account_name} 的账号，请重新操作~")
                    return

            account_config = AccountConfig()
            account_config.name = account_name
            account_ui = AccountConfigUi(account_config)
            self.accounts.append(account_ui)
            self.tabs.addTab(account_ui, account_name)

            show_message("添加成功", "请继续进行其他操作~ 全部操作完成后记得保存~")

    def del_account(self, checked=False):
        account_name, ok = QInputDialog.getText(self, "删除账号", "要删除的账号名称", QLineEdit.Normal, "")
        if ok:
            logger.info(f"尝试删除账号 {account_name} ...")

            account_to_delete = None
            for account in self.accounts:
                if account.lineedit_name.text() == account_name:
                    account_to_delete = account
                    break

            if account_to_delete is None:
                show_message("删除失败", f"未找到名称为 {account_name} 的账号，请重新操作~")
                return

            self.accounts.remove(account_to_delete)
            self.tabs.removeTab(self.tabs.indexOf(account_to_delete))
            show_message("删除成功", "请继续进行其他操作~ 全部操作完成后记得保存~")

    def create_tabs(self, cfg: Config, top_layout: QVBoxLayout):
        self.tabs = QTabWidget()
        self.create_common_tab(cfg)
        self.create_account_tabs(cfg)
        top_layout.addWidget(self.tabs)

    def create_common_tab(self, cfg: Config):
        self.common = CommonConfigUi(cfg.common)
        self.tabs.addTab(self.common, "公共配置")

    def create_account_tabs(self, cfg: Config):
        self.accounts = []  # type: List[AccountConfigUi]
        for account in cfg.account_configs:
            account_ui = AccountConfigUi(account)
            self.accounts.append(account_ui)
            self.tabs.addTab(account_ui, account.name)

    def to_config(self) -> Config:
        cfg = self.load_config()

        self.common.update_config(cfg.common)

        account_configs = []
        for idx, account in enumerate(self.accounts):
            # 以在账号中的次序作为唯一定位key，从而获取当前配置中该账号的配置，以便能保留一些配置工具中未涉及的配置，可以与文本编辑器改动兼容
            if idx < len(cfg.account_configs):
                account_config = cfg.account_configs[idx]
            else:
                account_config = AccountConfig()

            account.update_config(account_config)
            account_configs.append(account_config)

        cfg.account_configs = account_configs

        return cfg


class CommonConfigUi(QFrame):
    def __init__(self, cfg: CommonConfig, parent=None):
        super(CommonConfigUi, self).__init__(parent)

        self.from_config(cfg)

    def from_config(self, cfg: CommonConfig):
        form_layout = QFormLayout()

        self.checkbox_check_update_on_start = create_checkbox(cfg.check_update_on_start)
        form_layout.addRow("检查更新", self.checkbox_check_update_on_start)

        self.checkbox_auto_update_on_start = create_checkbox(cfg.auto_update_on_start)
        form_layout.addRow("自动更新（需要购买DLC才可生效）", self.checkbox_auto_update_on_start)

        self.checkbox_force_use_portable_chrome = create_checkbox(cfg.force_use_portable_chrome)
        form_layout.addRow("强制使用便携版chrome", self.checkbox_force_use_portable_chrome)

        self.checkbox_run_in_headless_mode = create_checkbox(cfg.run_in_headless_mode)
        form_layout.addRow("自动登录模式不显示浏览器界面", self.checkbox_run_in_headless_mode)

        self.checkbox_try_auto_bind_new_activity = create_checkbox(cfg.try_auto_bind_new_activity)
        form_layout.addRow("尝试自动绑定新活动", self.checkbox_try_auto_bind_new_activity)

        self.lineedit_majieluo_send_card_target_qq = create_lineedit(cfg.majieluo_send_card_target_qq, "填写qq号")
        form_layout.addRow("马杰洛新春版本赠送卡片目标QQ", self.lineedit_majieluo_send_card_target_qq)

        self.lineedit_auto_send_card_target_qqs = create_lineedit(list_to_str(cfg.auto_send_card_target_qqs), "填写qq号列表，使用英文逗号分开，示例：123, 456, 789")
        self.lineedit_auto_send_card_target_qqs.setValidator(QQListValidator())
        form_layout.addRow("自动赠送卡片的目标QQ数组", self.lineedit_auto_send_card_target_qqs)

        self.xinyue = XinYueConfigUi(form_layout, cfg.xinyue)
        self.fixed_teams = []
        for team in cfg.fixed_teams:
            self.fixed_teams.append(FixedTeamConfigUi(form_layout, team))

        add_form_seperator(form_layout, "其他")

        self.combobox_log_level = create_combobox(cfg.log_level, [
            "debug",
            "info",
            "warning",
            "error",
            "critical",
        ])
        form_layout.addRow("日志级别", self.combobox_log_level)

        self.spinbox_http_timeout = create_spin_box(cfg.http_timeout)
        form_layout.addRow("HTTP超时（秒）", self.spinbox_http_timeout)

        self.login = LoginConfigUi(form_layout, cfg.login)
        self.retry = RetryConfigUi(form_layout, cfg.retry)

        self.setLayout(make_scroll_layout(form_layout))

    def update_config(self, cfg: CommonConfig):
        cfg.force_use_portable_chrome = self.checkbox_force_use_portable_chrome.isChecked()
        cfg.run_in_headless_mode = self.checkbox_run_in_headless_mode.isChecked()
        cfg.check_update_on_start = self.checkbox_check_update_on_start.isChecked()
        cfg.auto_update_on_start = self.checkbox_auto_update_on_start.isChecked()
        cfg.try_auto_bind_new_activity = self.checkbox_try_auto_bind_new_activity.isChecked()

        cfg.http_timeout = self.spinbox_http_timeout.value()
        cfg.log_level = self.combobox_log_level.currentText()
        cfg.majieluo_send_card_target_qq = self.lineedit_majieluo_send_card_target_qq.text()
        cfg.auto_send_card_target_qqs = str_to_list(self.lineedit_auto_send_card_target_qqs.text())

        self.login.update_config(cfg.login)
        self.retry.update_config(cfg.retry)
        self.xinyue.update_config(cfg.xinyue)
        for idx, team in enumerate(self.fixed_teams):
            team.update_config(cfg.fixed_teams[idx])


class LoginConfigUi(QWidget):
    def __init__(self, form_layout: QFormLayout, cfg: LoginConfig, parent=None):
        super(LoginConfigUi, self).__init__(parent)

        self.from_config(form_layout, cfg)

    def from_config(self, form_layout: QFormLayout, cfg: LoginConfig):
        add_form_seperator(form_layout, "登录阶段超时(秒)")

        self.spinbox_max_retry_count = create_spin_box(cfg.max_retry_count)
        form_layout.addRow("重试次数", self.spinbox_max_retry_count)

        self.spinbox_retry_wait_time = create_spin_box(cfg.retry_wait_time)
        form_layout.addRow("重试间隔时间", self.spinbox_retry_wait_time)

        self.spinbox_open_url_wait_time = create_spin_box(cfg.open_url_wait_time)
        form_layout.addRow("打开网页后等待时长", self.spinbox_open_url_wait_time)

        self.spinbox_load_page_timeout = create_spin_box(cfg.load_page_timeout)
        form_layout.addRow("加载页面的超时时间", self.spinbox_load_page_timeout)

        self.spinbox_load_login_iframe_timeout = create_spin_box(cfg.load_login_iframe_timeout)
        form_layout.addRow("点击登录按钮后的超时时间", self.spinbox_load_login_iframe_timeout)

        self.spinbox_login_timeout = create_spin_box(cfg.login_timeout)
        form_layout.addRow("登录的超时时间", self.spinbox_login_timeout)

        self.spinbox_login_finished_timeout = create_spin_box(cfg.login_finished_timeout)
        form_layout.addRow("等待登录完成的超时时间", self.spinbox_login_finished_timeout)

        add_form_seperator(form_layout, "自动处理滑动验证码")

        self.checkbox_auto_resolve_captcha = create_checkbox(cfg.auto_resolve_captcha)
        form_layout.addRow("启用", self.checkbox_auto_resolve_captcha)

        self.doublespinbox_move_captcha_delta_width_rate = create_double_spin_box(cfg.move_captcha_delta_width_rate)
        self.doublespinbox_move_captcha_delta_width_rate.setSingleStep(0.01)
        form_layout.addRow("每次尝试滑动验证码多少倍滑块宽度的偏移值", self.doublespinbox_move_captcha_delta_width_rate)

    def update_config(self, cfg: LoginConfig):
        cfg.max_retry_count = self.spinbox_max_retry_count.value()
        cfg.retry_wait_time = self.spinbox_retry_wait_time.value()
        cfg.open_url_wait_time = self.spinbox_open_url_wait_time.value()
        cfg.load_page_timeout = self.spinbox_load_page_timeout.value()
        cfg.load_login_iframe_timeout = self.spinbox_load_login_iframe_timeout.value()
        cfg.login_timeout = self.spinbox_login_timeout.value()
        cfg.login_finished_timeout = self.spinbox_login_finished_timeout.value()
        cfg.auto_resolve_captcha = self.checkbox_auto_resolve_captcha.isChecked()
        cfg.move_captcha_delta_width_rate = self.doublespinbox_move_captcha_delta_width_rate.value()


class RetryConfigUi(QWidget):
    def __init__(self, form_layout: QFormLayout, cfg: RetryConfig, parent=None):
        super(RetryConfigUi, self).__init__(parent)

        self.from_config(form_layout, cfg)

    def from_config(self, form_layout: QFormLayout, cfg: RetryConfig):
        add_form_seperator(form_layout, "通用重试配置")

        self.spinbox_request_wait_time = create_spin_box(cfg.request_wait_time)
        form_layout.addRow("请求间隔时间", self.spinbox_request_wait_time)

        self.spinbox_max_retry_count = create_spin_box(cfg.max_retry_count)
        form_layout.addRow("最大重试次数", self.spinbox_max_retry_count)

        self.spinbox_retry_wait_time = create_spin_box(cfg.retry_wait_time)
        form_layout.addRow("重试间隔时间", self.spinbox_retry_wait_time)

    def update_config(self, cfg: RetryConfig):
        cfg.request_wait_time = self.spinbox_request_wait_time.value()
        cfg.max_retry_count = self.spinbox_max_retry_count.value()
        cfg.retry_wait_time = self.spinbox_retry_wait_time.value()


class XinYueConfigUi(QWidget):
    def __init__(self, form_layout: QFormLayout, cfg: XinYueConfig, parent=None):
        super(XinYueConfigUi, self).__init__(parent)

        self.from_config(form_layout, cfg)

    def from_config(self, form_layout: QFormLayout, cfg: XinYueConfig):
        add_form_seperator(form_layout, "心悦相关配置")

        self.combobox_submit_task_after = create_combobox(str(cfg.submit_task_after), [str(hour) for hour in range(24)])
        form_layout.addRow("心悦操作最早处理时间", self.combobox_submit_task_after)

    def update_config(self, cfg: XinYueConfig):
        cfg.submit_task_after = int(self.combobox_submit_task_after.currentText())


class FixedTeamConfigUi(QWidget):
    def __init__(self, form_layout: QFormLayout, cfg: FixedTeamConfig, parent=None):
        super(FixedTeamConfigUi, self).__init__(parent)

        self.from_config(form_layout, cfg)

    def from_config(self, form_layout: QFormLayout, cfg: FixedTeamConfig):
        add_form_seperator(form_layout, f"心悦战场固定队 - {cfg.id}")

        self.checkbox_enable = create_checkbox(cfg.enable)
        form_layout.addRow("启用", self.checkbox_enable)

        self.lineedit_id = create_lineedit(cfg.id, "固定队伍id，仅用于本地区分用")
        form_layout.addRow("队伍id", self.lineedit_id)

        self.lineedit_members = create_lineedit(list_to_str(cfg.members), "固定队成员，必须是三个，则必须都配置在本地的账号列表中了，否则将报错，不生效")
        self.lineedit_members.setValidator(QQListValidator())
        form_layout.addRow("成员", self.lineedit_members)

    def update_config(self, cfg: FixedTeamConfig):
        cfg.enable = self.checkbox_enable.isChecked()
        cfg.id = self.lineedit_id.text()
        cfg.members = str_to_list(self.lineedit_members.text())


class AccountConfigUi(QWidget):
    login_mode_bidict = BiDict({
        "手动登录": "by_hand",
        "扫码/点击头像登录": "qr_login",
        "账号密码自动登录": "auto_login",
    })

    def __init__(self, cfg: AccountConfig, parent=None):
        super(AccountConfigUi, self).__init__(parent)

        self.from_config(cfg)

    def from_config(self, cfg: AccountConfig):
        form_layout = QFormLayout()

        self.checkbox_enable = create_checkbox(cfg.enable)
        form_layout.addRow("启用该账号", self.checkbox_enable)

        self.lineedit_name = create_lineedit(cfg.name, "账号名称，仅用于区分不同账号，请确保不同账号名称不一样")
        form_layout.addRow("账号名称", self.lineedit_name)

        self.checkbox_cannot_bind_dnf = create_checkbox(cfg.cannot_bind_dnf)
        form_layout.addRow("无法在道聚城绑定dnf", self.checkbox_cannot_bind_dnf)

        self.combobox_login_mode = create_combobox(self.login_mode_bidict.val_to_key.get(cfg.login_mode, "扫码/点击头像登录"), list(self.login_mode_bidict.key_to_val.keys()))
        form_layout.addRow("登录模式", self.combobox_login_mode)

        self.account_info = AccountInfoConfigUi(form_layout, cfg.account_info)

        self.combobox_login_mode.currentTextChanged.connect(self.on_login_mode_change)
        self.on_login_mode_change(self.combobox_login_mode.currentText())

        self.mobile_game_role_info = MobileGameRoleInfoConfigUi(form_layout, cfg.mobile_game_role_info)
        self.exchange_items = []
        for exchange_item in cfg.exchange_items:
            self.exchange_items.append(ExchangeItemConfigUi(form_layout, exchange_item))
        self.ark_lottery = ArkLotteryConfigUi(form_layout, cfg.ark_lottery)
        self.vip_mentor = VipMentorConfigUi(form_layout, cfg.vip_mentor)
        self.dnf_helper_info = DnfHelperInfoConfigUi(form_layout, cfg.dnf_helper_info)
        self.hello_voice = HelloVoiceInfoConfigUi(form_layout, cfg.hello_voice)
        self.firecrackers = FirecrackersConfigUi(form_layout, cfg.firecrackers)

        add_form_seperator(form_layout, "其他")

        self.lineedit_drift_send_qq_list = create_lineedit(list_to_str(cfg.drift_send_qq_list), "填写qq号列表，使用英文逗号分开，示例：123, 456, 789")
        self.lineedit_drift_send_qq_list.setValidator(QQListValidator())
        form_layout.addRow("漂流瓶每日邀请列表（不会实际发消息）", self.lineedit_drift_send_qq_list)

        self.lineedit_spring_fudai_receiver_qq_list = create_lineedit(list_to_str(cfg.spring_fudai_receiver_qq_list), "填写qq号列表，使用英文逗号分开，示例：123, 456, 789")
        self.lineedit_spring_fudai_receiver_qq_list.setValidator(QQListValidator())
        form_layout.addRow("新春福袋大作战邀请列表（会实际发消息）", self.lineedit_spring_fudai_receiver_qq_list)

        self.checkbox_enable_firecrackers_invite_friend = create_checkbox(cfg.enable_firecrackers_invite_friend)
        form_layout.addRow("燃放爆竹活动是否尝试邀请好友（不会实际发消息）", self.checkbox_enable_firecrackers_invite_friend)

        self.checkbox_enable_majieluo_invite_friend = create_checkbox(cfg.enable_majieluo_invite_friend)
        form_layout.addRow("马杰洛活动是否尝试黑钻送好友（不会实际发消息）", self.checkbox_enable_majieluo_invite_friend)

        self.lineedit_dnf_bbs_formhash = create_lineedit(cfg.dnf_bbs_formhash, "形如：8df1d678")
        form_layout.addRow("dnf论坛签到formhash", self.lineedit_dnf_bbs_formhash)

        self.lineedit_dnf_bbs_cookie = create_lineedit(cfg.dnf_bbs_cookie, "请填写论坛请求的完整cookie串")
        form_layout.addRow("dnf论坛cookie", self.lineedit_dnf_bbs_cookie)

        self.function_switches = FunctionSwitchesConfigUi(form_layout, cfg.function_switches)

        self.setLayout(make_scroll_layout(form_layout))

    def update_config(self, cfg: AccountConfig):
        cfg.enable = self.checkbox_enable.isChecked()
        cfg.name = self.lineedit_name.text()
        cfg.login_mode = self.login_mode_bidict.key_to_val[self.combobox_login_mode.currentText()]
        cfg.cannot_bind_dnf = self.checkbox_cannot_bind_dnf.isChecked()

        cfg.drift_send_qq_list = str_to_list(self.lineedit_drift_send_qq_list.text())
        cfg.spring_fudai_receiver_qq_list = str_to_list(self.lineedit_spring_fudai_receiver_qq_list.text())
        cfg.enable_firecrackers_invite_friend = self.checkbox_enable_firecrackers_invite_friend.isChecked()
        cfg.enable_majieluo_invite_friend = self.checkbox_enable_majieluo_invite_friend.isChecked()

        cfg.dnf_bbs_formhash = self.lineedit_dnf_bbs_formhash.text()
        cfg.dnf_bbs_cookie = self.lineedit_dnf_bbs_cookie.text()

        self.account_info.update_config(cfg.account_info)
        self.function_switches.update_config(cfg.function_switches)
        self.mobile_game_role_info.update_config(cfg.mobile_game_role_info)
        for idx, exchange_item in enumerate(self.exchange_items):
            exchange_item.update_config(cfg.exchange_items[idx])
        self.ark_lottery.update_config(cfg.ark_lottery)
        self.vip_mentor.update_config(cfg.vip_mentor)
        self.dnf_helper_info.update_config(cfg.dnf_helper_info)
        self.hello_voice.update_config(cfg.hello_voice)
        self.firecrackers.update_config(cfg.firecrackers)

        # 这些是动态生成的，不需要保存到配置表中
        delattr(cfg, "sDjcSign")

    def on_login_mode_change(self, text):
        self.account_info.setDisabled(text != self.login_mode_bidict.val_to_key['auto_login'])


class AccountInfoConfigUi(QWidget):
    def __init__(self, form_layout: QFormLayout, cfg: AccountInfoConfig, parent=None):
        super(AccountInfoConfigUi, self).__init__(parent)

        self.from_config(form_layout, cfg)

    def from_config(self, form_layout: QFormLayout, cfg: AccountInfoConfig):
        add_form_seperator(form_layout, f"若使用账号密码自动登录，请配置下列信息")

        self.lineedit_account = create_lineedit(cfg.account)
        form_layout.addRow("QQ账号", self.lineedit_account)

        self.lineedit_password = create_lineedit(cfg.password, "使用账号密码自动登录有风险_请理解这个功能到底如何使用你的账号密码后再决定是否使用")
        self.lineedit_password.setEchoMode(QLineEdit.Password)

        btn_show_password = QPushButton("按住显示密码")
        btn_show_password.pressed.connect(self.show_password)
        btn_show_password.released.connect(self.hide_password)

        layout = QHBoxLayout()
        layout.addWidget(self.lineedit_password)
        layout.addWidget(btn_show_password)
        form_layout.addRow("QQ密码", layout)

    def show_password(self):
        self.lineedit_password.setEchoMode(QLineEdit.Normal)

    def hide_password(self):
        self.lineedit_password.setEchoMode(QLineEdit.Password)

    def update_config(self, cfg: AccountInfoConfig):
        cfg.account = self.lineedit_account.text()
        cfg.password = self.lineedit_password.text()

    def setDisabled(self, disabled: bool) -> None:
        super().setDisabled(disabled)

        self.lineedit_account.setDisabled(disabled)
        self.lineedit_password.setDisabled(disabled)


class FunctionSwitchesConfigUi(QWidget):
    def __init__(self, form_layout: QFormLayout, cfg: FunctionSwitchesConfig, parent=None):
        super(FunctionSwitchesConfigUi, self).__init__(parent)

        self.from_config(form_layout, cfg)

    def from_config(self, form_layout: QFormLayout, cfg: FunctionSwitchesConfig):
        add_form_seperator(form_layout, f"各功能开关")

        self.checkbox_disable_most_activities = create_checkbox(cfg.disable_most_activities)
        form_layout.addRow("禁用绝大部分活动", self.checkbox_disable_most_activities)

        # ----------------------------------------------------------
        add_form_seperator(form_layout, "普通skey")

        self.checkbox_get_djc = create_checkbox(cfg.get_djc)
        form_layout.addRow("领取道聚城", self.checkbox_get_djc)

        self.checkbox_make_wish = create_checkbox(cfg.make_wish)
        form_layout.addRow("道聚城许愿", self.checkbox_make_wish)

        self.checkbox_get_xinyue = create_checkbox(cfg.get_xinyue)
        form_layout.addRow("心悦特权专区", self.checkbox_get_xinyue)

        self.checkbox_get_credit_xinyue_gift = create_checkbox(cfg.get_credit_xinyue_gift)
        form_layout.addRow("腾讯游戏信用相关礼包", self.checkbox_get_credit_xinyue_gift)

        self.checkbox_get_heizuan_gift = create_checkbox(cfg.get_heizuan_gift)
        form_layout.addRow("每月黑钻等级礼包", self.checkbox_get_heizuan_gift)

        self.checkbox_get_dnf_shanguang = create_checkbox(cfg.get_dnf_shanguang)
        form_layout.addRow("DNF闪光杯第三期", self.checkbox_get_dnf_shanguang)

        self.checkbox_get_qq_video = create_checkbox(cfg.get_qq_video)
        form_layout.addRow("qq视频活动", self.checkbox_get_qq_video)

        self.checkbox_get_youfei = create_checkbox(cfg.get_youfei)
        form_layout.addRow("qq视频-看江湖有翡", self.checkbox_get_youfei)

        self.checkbox_get_dnf_helper_chronicle = create_checkbox(cfg.get_dnf_helper_chronicle)
        form_layout.addRow("dnf助手编年史（需配置助手userId）", self.checkbox_get_dnf_helper_chronicle)

        self.checkbox_get_dnf_helper = create_checkbox(cfg.get_dnf_helper)
        form_layout.addRow("dnf助手活动（需配置助手userId和token）", self.checkbox_get_dnf_helper)

        self.checkbox_get_hello_voice = create_checkbox(cfg.get_hello_voice)
        form_layout.addRow("hello语音奖励兑换（需配置hello语音的用户ID）", self.checkbox_get_hello_voice)

        self.checkbox_get_dnf_welfare = create_checkbox(cfg.get_dnf_welfare)
        form_layout.addRow("DNF福利中心兑换", self.checkbox_get_dnf_welfare)

        self.checkbox_get_majieluo = create_checkbox(cfg.get_majieluo)
        form_layout.addRow("DNF马杰洛的规划第三期", self.checkbox_get_majieluo)

        self.checkbox_get_dnf_bbs_signin = create_checkbox(cfg.get_dnf_bbs_signin)
        form_layout.addRow("dnf论坛签到", self.checkbox_get_dnf_bbs_signin)

        self.checkbox_get_dnf_spring = create_checkbox(cfg.get_dnf_spring)
        form_layout.addRow("DNF新春夺宝大作战", self.checkbox_get_dnf_spring)

        self.checkbox_get_wegame_spring = create_checkbox(cfg.get_wegame_spring)
        form_layout.addRow("新春献豪礼 首次盲盒限时领", self.checkbox_get_wegame_spring)

        self.checkbox_get_spring_fudai = create_checkbox(cfg.get_spring_fudai)
        form_layout.addRow("新春福袋大作战", self.checkbox_get_spring_fudai)

        self.checkbox_get_spring_collection = create_checkbox(cfg.get_spring_collection)
        form_layout.addRow("DNF新春福利集合站", self.checkbox_get_spring_collection)

        self.checkbox_get_firecrackers = create_checkbox(cfg.get_firecrackers)
        form_layout.addRow("燃放爆竹", self.checkbox_get_firecrackers)

        # ----------------------------------------------------------
        add_form_seperator(form_layout, "QQ空间pskey")

        self.checkbox_get_ark_lottery = create_checkbox(cfg.get_ark_lottery)
        form_layout.addRow("集卡", self.checkbox_get_ark_lottery)

        self.checkbox_get_vip_mentor = create_checkbox(cfg.get_vip_mentor)
        form_layout.addRow("会员关怀", self.checkbox_get_vip_mentor)

        # ----------------------------------------------------------
        add_form_seperator(form_layout, "安全管家pskey")

        self.checkbox_get_guanjia = create_checkbox(cfg.get_guanjia)
        form_layout.addRow("管家蚊子腿", self.checkbox_get_guanjia)

    def update_config(self, cfg: FunctionSwitchesConfig):
        cfg.disable_most_activities = self.checkbox_disable_most_activities.isChecked()

        cfg.get_djc = self.checkbox_get_djc.isChecked()
        cfg.make_wish = self.checkbox_make_wish.isChecked()
        cfg.get_xinyue = self.checkbox_get_xinyue.isChecked()
        cfg.get_credit_xinyue_gift = self.checkbox_get_credit_xinyue_gift.isChecked()
        cfg.get_heizuan_gift = self.checkbox_get_heizuan_gift.isChecked()
        cfg.get_dnf_shanguang = self.checkbox_get_dnf_shanguang.isChecked()
        cfg.get_qq_video = self.checkbox_get_qq_video.isChecked()
        cfg.get_youfei = self.checkbox_get_youfei.isChecked()
        cfg.get_dnf_helper_chronicle = self.checkbox_get_dnf_helper_chronicle.isChecked()
        cfg.get_dnf_helper = self.checkbox_get_dnf_helper.isChecked()
        cfg.get_hello_voice = self.checkbox_get_hello_voice.isChecked()
        cfg.get_dnf_welfare = self.checkbox_get_dnf_welfare.isChecked()
        cfg.get_majieluo = self.checkbox_get_majieluo.isChecked()
        cfg.get_dnf_bbs_signin = self.checkbox_get_dnf_bbs_signin.isChecked()
        cfg.get_dnf_spring = self.checkbox_get_dnf_spring.isChecked()
        cfg.get_wegame_spring = self.checkbox_get_wegame_spring.isChecked()
        cfg.get_spring_fudai = self.checkbox_get_spring_fudai.isChecked()
        cfg.get_spring_collection = self.checkbox_get_spring_collection.isChecked()
        cfg.get_firecrackers = self.checkbox_get_firecrackers.isChecked()

        cfg.get_ark_lottery = self.checkbox_get_ark_lottery.isChecked()
        cfg.get_vip_mentor = self.checkbox_get_vip_mentor.isChecked()

        cfg.get_guanjia = self.checkbox_get_guanjia.isChecked()


class MobileGameRoleInfoConfigUi(QWidget):
    def __init__(self, form_layout: QFormLayout, cfg: MobileGameRoleInfoConfig, parent=None):
        super(MobileGameRoleInfoConfigUi, self).__init__(parent)

        self.from_config(form_layout, cfg)

    def from_config(self, form_layout: QFormLayout, cfg: MobileGameRoleInfoConfig):
        add_form_seperator(form_layout, f"完成《礼包达人》任务所需的手游的名称信息")

        self.combobox_game_name = create_combobox(cfg.game_name, ['无', '任意手游', *sorted(name_2_mobile_game_info_map.keys())])
        form_layout.addRow("手游名称", self.combobox_game_name)

    def update_config(self, cfg: MobileGameRoleInfoConfig):
        cfg.game_name = self.combobox_game_name.currentText()


class ExchangeItemConfigUi(QWidget):
    def __init__(self, form_layout: QFormLayout, cfg: ExchangeItemConfig, parent=None):
        super(ExchangeItemConfigUi, self).__init__(parent)

        self.from_config(form_layout, cfg)

    def from_config(self, form_layout: QFormLayout, cfg: ExchangeItemConfig):
        add_form_seperator(form_layout, f"道聚城兑换道具 - {cfg.sGoodsName}")

        self.spinbox_count = create_spin_box(cfg.count, 10)
        form_layout.addRow("兑换数目/次数（0表示不兑换）", self.spinbox_count)

    def update_config(self, cfg: ExchangeItemConfig):
        cfg.count = self.spinbox_count.value()


class ArkLotteryConfigUi(QWidget):
    def __init__(self, form_layout: QFormLayout, cfg: ArkLotteryConfig, parent=None):
        super(ArkLotteryConfigUi, self).__init__(parent)

        self.from_config(form_layout, cfg)

    def from_config(self, form_layout: QFormLayout, cfg: ArkLotteryConfig):
        add_form_seperator(form_layout, f"集卡")

        self.combobox_lucky_dnf_server_name = create_combobox(dnf_server_id_to_name(cfg.lucky_dnf_server_id), dnf_server_name_list())
        form_layout.addRow("幸运勇士区服名称", self.combobox_lucky_dnf_server_name)

        self.lineedit_lucky_dnf_role_id = create_lineedit(cfg.lucky_dnf_role_id, "角色ID，形如 1282822，不知道时可以选择区服名称，该数值留空，这样处理到抽卡的时候会用黄色字体打印出来信息")
        form_layout.addRow("幸运勇士角色ID", self.lineedit_lucky_dnf_role_id)

        self.checkbox_need_take_awards = create_checkbox(cfg.need_take_awards)
        form_layout.addRow("领取礼包", self.checkbox_need_take_awards)

        cost_all_cards_and_do_lottery = cfg.act_id_to_cost_all_cards_and_do_lottery.get(zzconfig().actid, False)
        self.checkbox_cost_all_cards_and_do_lottery = create_checkbox(cost_all_cards_and_do_lottery)
        form_layout.addRow("是否消耗所有卡牌来抽奖", self.checkbox_cost_all_cards_and_do_lottery)

    def update_config(self, cfg: ArkLotteryConfig):
        cfg.lucky_dnf_server_id = dnf_server_name_to_id(self.combobox_lucky_dnf_server_name.currentText())
        cfg.lucky_dnf_role_id = self.lineedit_lucky_dnf_role_id.text()

        cfg.need_take_awards = self.checkbox_need_take_awards.isChecked()

        cfg.act_id_to_cost_all_cards_and_do_lottery[zzconfig().actid] = self.checkbox_cost_all_cards_and_do_lottery.isChecked()


class VipMentorConfigUi(QWidget):
    def __init__(self, form_layout: QFormLayout, cfg: VipMentorConfig, parent=None):
        super(VipMentorConfigUi, self).__init__(parent)

        self.from_config(form_layout, cfg)

    def from_config(self, form_layout: QFormLayout, cfg: VipMentorConfig):
        add_form_seperator(form_layout, f"会员关怀")

        self.spinbox_take_index = create_spin_box(cfg.take_index, 3, 1)
        form_layout.addRow("兑换数目", self.spinbox_take_index)

        self.combobox_guanhuai_dnf_server_name = create_combobox(dnf_server_id_to_name(cfg.guanhuai_dnf_server_id), dnf_server_name_list())
        form_layout.addRow("关怀礼包角色区服名称", self.combobox_guanhuai_dnf_server_name)

        self.lineedit_guanhuai_dnf_role_id = create_lineedit(cfg.guanhuai_dnf_role_id, "角色ID，形如 1282822，不知道时可以选择区服名称，该数值留空，这样处理到抽卡的时候会用黄色字体打印出来信息")
        form_layout.addRow("关怀礼包角色角色ID", self.lineedit_guanhuai_dnf_role_id)

    def update_config(self, cfg: VipMentorConfig):
        cfg.take_index = self.spinbox_take_index.value()

        cfg.guanhuai_dnf_server_id = dnf_server_name_to_id(self.combobox_guanhuai_dnf_server_name.currentText())
        cfg.guanhuai_dnf_role_id = self.lineedit_guanhuai_dnf_role_id.text()


class DnfHelperInfoConfigUi(QWidget):
    def __init__(self, form_layout: QFormLayout, cfg: DnfHelperInfoConfig, parent=None):
        super(DnfHelperInfoConfigUi, self).__init__(parent)

        self.from_config(form_layout, cfg)

    def from_config(self, form_layout: QFormLayout, cfg: DnfHelperInfoConfig):
        add_form_seperator(form_layout, f"dnf助手信息")

        self.lineedit_userId = create_lineedit(cfg.userId, "dnf助手->我的->编辑->社区ID")
        form_layout.addRow("社区ID", self.lineedit_userId)

        self.lineedit_nickName = create_lineedit(cfg.nickName, "dnf助手->我的->编辑->昵称")
        form_layout.addRow("昵称", self.lineedit_nickName)

        self.lineedit_token = create_lineedit(cfg.token, "形如 sSfsEtDH , 可通过助手分享出的活动链接或抓包得到的活动链接中找到token参数")
        form_layout.addRow("登陆票据", self.lineedit_token)

        self.checkbox_chronicle_lottery = create_checkbox(cfg.chronicle_lottery)
        form_layout.addRow("编年史开启抽奖", self.checkbox_chronicle_lottery)

    def update_config(self, cfg: DnfHelperInfoConfig):
        cfg.userId = self.lineedit_userId.text()
        cfg.nickName = self.lineedit_nickName.text()
        cfg.token = self.lineedit_token.text()

        cfg.chronicle_lottery = self.checkbox_chronicle_lottery.isChecked()


class HelloVoiceInfoConfigUi(QWidget):
    def __init__(self, form_layout: QFormLayout, cfg: HelloVoiceInfoConfig, parent=None):
        super(HelloVoiceInfoConfigUi, self).__init__(parent)

        self.from_config(form_layout, cfg)

    def from_config(self, form_layout: QFormLayout, cfg: HelloVoiceInfoConfig):
        add_form_seperator(form_layout, f"hello语音相关信息")

        self.lineedit_hello_id = create_lineedit(cfg.hello_id, "hello语音->我的->头像右侧，昵称下方的【ID：XXXXXX】中的XXX那部分")
        form_layout.addRow("hello语音的用户ID", self.lineedit_hello_id)

    def update_config(self, cfg: HelloVoiceInfoConfig):
        cfg.hello_id = self.lineedit_hello_id.text()


class FirecrackersConfigUi(QWidget):
    def __init__(self, form_layout: QFormLayout, cfg: FirecrackersConfig, parent=None):
        super(FirecrackersConfigUi, self).__init__(parent)

        self.from_config(form_layout, cfg)

    def from_config(self, form_layout: QFormLayout, cfg: FirecrackersConfig):
        add_form_seperator(form_layout, f"燃放爆竹")

        self.checkbox_enable_lottery = create_checkbox(cfg.enable_lottery)
        form_layout.addRow("开启抽奖", self.checkbox_enable_lottery)

    def update_config(self, cfg: FirecrackersConfig):
        cfg.enable_lottery = self.checkbox_enable_lottery.isChecked()


def main():
    app = QApplication([])

    app.setStyle(QStyleFactory.create("fusion"))

    ui = ConfigUi()
    ui.show()

    app.exec()


if __name__ == '__main__':
    main()