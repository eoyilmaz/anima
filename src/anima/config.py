# -*- coding: utf-8 -*-

from stalker.config import Config as ConfigBase


class Config(ConfigBase):
    """configurator"""

    extra_config_values = dict(
        # stalker_server_internal_address=
        # defaults.stalker_server_internal_address
        # if 'stalker_server_internal_address' in defaults else None,
        # stalker_server_external_address=
        # defaults.stalker_server_external_address
        # if 'stalker_server_external_address' in defaults else None,
        stalker_dummy_user_login="anima",
        stalker_dummy_user_pass="anima",
        local_cache_folder="~/.cache/anima/",
        recent_file_name="recent_files",
        avid_media_file_path_storage="avid_media_file_path",
        enable_ldap_authentication=False,
        enable_ldap_authorization=False,
        ldap_server_address="",
        ldap_base_dn="",
        ldap_user_group_map={},
        normal_users_group_names=["Normal Users"],
        power_users_group_names=["Power Users", "admins"],
        # environment variable template for repositories
        repo_env_template="REPO%(id)s",
        anima_env_var="ANIMAPATH",
        env_var_file_name="env.json",
        # some media
        ffmpeg_command_path="ffmpeg",
        ffprobe_command_path="ffprobe",
        max_recent_files=50,
        status_colors={
            "wfd": [171, 186, 195],
            "rts": [209, 91, 71],
            "wip": [255, 198, 87],
            "prev": [111, 179, 224],
            "hrev": [126, 110, 176],
            "drev": [126, 110, 176],
            "cmpl": [130, 175, 111],
            "oh": [213, 63, 64],
            "stop": [78, 89, 98],
        },
        _status_colors_by_id={},
        _user_names_lut={},  # a table for fast user name look up,
        cut_in=1001,
        cut_out=1100,
    )

    def __init__(self):
        super(Config, self).__init__()
        self.config_values.update(self.extra_config_values.copy())
        self.user_config = {}

        # the priority order is
        # stalker.config
        # config.py under .stalker_rc directory
        # config.py under $STALKER_PATH

    @property
    def status_colors_by_id(self):
        """fills the _status_colors_by_id dictionary"""
        if not self._status_colors_by_id:
            from anima.utils import do_db_setup

            do_db_setup()
            from stalker import StatusList

            task_status_list = StatusList.query.filter(
                StatusList.target_entity_type == "Task"
            ).first()

            for status in task_status_list.statuses:
                self._status_colors_by_id[status.id] = self.status_colors[
                    status.code.lower()
                ]
        return self._status_colors_by_id

    @property
    def user_names_lut(self):
        """fills the _user_names_lut"""
        if not self._user_names_lut:
            from anima.utils import do_db_setup

            do_db_setup()
            from stalker import User
            from stalker.db.session import DBSession

            for result in DBSession.query(User.id, User.name).all():
                self._user_names_lut.__setitem__(result.id, result.name)
        return self._user_names_lut

    def is_power_user(self, user):
        """A predicate that returns if the user is a power user"""
        if not user:
            return False

        from stalker import Group

        power_users_groups = Group.query.filter(
            Group.name.in_(self.power_users_group_names)
        ).all()
        if power_users_groups:
            for group in power_users_groups:
                if group in user.groups:
                    return True
        return False
