# -*- coding: utf-8 -*-

__version__ = "1.1.0"

import os


class NetflixReporter(object):
    """Creates Netflix compliant reports of Episodes/Sequences"""

    csv_header = (
        "Episode;Shot Name;VFX Shot Status;Shot Methodologies;Scope of Work;Vendors;"
        "VFX Turnover to Vendor Date;VFX Next Studio Review Date;VFX Final Delivery Date;VFX Final Version;"
        "Shot Cost;Currency;Report Date;Report Note"
    )
    csv_format = (
        "{episode_number};{shot.code};{status};{shot_methodologies};{scope_of_work};{vendors};"
        "{vfx_turnover_to_vendor_date};{vfx_next_studio_review_date};{vfx_final_delivery_date};"
        "{vfx_final_version};{shot_cost};{currency};{report_date};{report_note}"
    )

    status_lut = {
        "WFD": "Waiting To Start",
        "RTS": "Waiting To Start",
        "WIP": "In Progress",
        "PREV": "Pending Netflix Review",
        "HREV": "In Progress",
        "DREV": "In Progress",
        "CMPL": "Approved",
        "STOP": "Omit",
        "OH": "On Hold",
    }

    date_time_format = "%Y-%m-%d"

    def __init__(self):
        pass

    def map_status_code(self, status_code):
        """Maps the given status to Netflix statuses

        :param status_code: A Stalker Status instance or Status.name or Status.code
        :return:
        """
        from stalker import Status

        if isinstance(status_code, Status):
            status_code = status_code.code

        return self.status_lut[status_code]

    @classmethod
    def get_shot_status(cls, shot):
        """calculates the shot status

        :param shot:
        :return:
        """
        # The problem here is that, because of the Plate task, all the shots seem to be WIP at the beginning
        # also we can not use the Comp or Cleanup task status, because they may be WFD but the Camera or Lighting
        # task could be CMPL
        # so we need to calculate the shot status from scratch

        from stalker.db.session import DBSession

        with DBSession.no_autoflush:
            wfd = shot.status_list["WFD"]
            rts = shot.status_list["RTS"]
            wip = shot.status_list["WIP"]
            cmpl = shot.status_list["CMPL"]

        parent_statuses_lut = [wfd, rts, wip, cmpl]

        #   +--------- WFD
        #   |+-------- RTS
        #   ||+------- WIP
        #   |||+------ PREV
        #   ||||+----- HREV
        #   |||||+---- DREV
        #   ||||||+--- OH
        #   |||||||+-- STOP
        #   ||||||||+- CMPL
        #   |||||||||
        # 0b000000000

        binary_status_codes = {
            "WFD": 256,
            "RTS": 128,
            "WIP": 64,
            "PREV": 32,
            "HREV": 16,
            "DREV": 8,
            "OH": 4,
            "STOP": 2,
            "CMPL": 1,
        }

        # use Python
        # logger.debug('using pure Python to query children statuses')
        binary_status = 0
        children_statuses = []
        for child in shot.children:
            # skip Plate task
            if child.type and child.type.name == "Plate":
                continue

            # consider every status only once
            if child.status not in children_statuses:
                children_statuses.append(child.status)
                binary_status += binary_status_codes[child.status.code]

        #
        # I know that the following list seems cryptic but the it shows the
        # final status index in parent_statuses_lut[] list.
        #
        # So by using the cumulative statuses of children we got an index from
        # the following table, and use the found element (integer) as the index
        # for the parent_statuses_lut[] list, and we find the desired status
        #
        # We are doing it in this way for a couple of reasons:
        #
        #   1. We shouldn't hold the statuses in the following list,
        #   2. Using a dictionary is another alternative, where the keys are
        #      the cumulative binary status codes, but at the end the result of
        #      this cumulative thing is a number between 0-511 so no need to
        #      use a dictionary with integer keys
        #
        children_to_parent_statuses_lut = [
            0,
            3,
            3,
            3,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            1,
            2,
            1,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            0,
            2,
            0,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            1,
            2,
            1,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
        ]

        status_index = children_to_parent_statuses_lut[binary_status]
        status = parent_statuses_lut[status_index]

        # logger.debug("binary statuses value : {}".format(binary_status))
        # logger.debug("setting status to : {}".format(status.code))

        return status

    @classmethod
    def generate_shot_methodologies(cls, shot):
        """Generates Netflix complaint shot methodologies field value by looking at the task related information

        :param shot: A Stalker Shot instance.
        :return: Returns a list of string containing the shot methodologies
        """
        shot_methodologies = []
        child_tasks = shot.children
        child_task_type_names = []
        for child_task in child_tasks:
            if child_task.type:
                child_task_type_names.append(child_task.type.name.lower())

        # Comp -> "2D Comp"
        if "comp" in child_task_type_names:
            shot_methodologies.append("2D Comp")

        # Cleanup -> "2D Paint"
        if "cleanup" in child_task_type_names:
            shot_methodologies.append("2D Paint")

        # Lighting.dependency to Layout -> "3D Set Extension"
        if "lighting" in child_task_type_names:
            from stalker import Task

            # get the lighting task first
            lighting_tasks = filter(lambda x: x.name == "Lighting", child_tasks)
            for lighting_task in lighting_tasks:
                assert isinstance(lighting_task, Task)
                deps = lighting_task.depends
                for dep in deps:
                    assert isinstance(dep, Task)
                    if dep.type:
                        dep_type_name = dep.type.name
                        if dep_type_name == "Layout":
                            shot_methodologies.append("3D Set Extension")
                            break

        # Animation -> "3D Animated Object"
        # Animation.dependency -> Character.Rig -> "3D Character"
        if "animation" in child_task_type_names:
            shot_methodologies.append("3D Animated Object")
            # also check if there are any dependencies to a character rig
            animation_tasks = filter(
                lambda x: x.type and x.type.name.lower().startswith("anim"), child_tasks
            )
            for animation_task in animation_tasks:
                for dep in animation_task.depends:
                    if dep.type and dep.type.name.lower() == "rig":
                        # check if this is a rig for a character
                        parent_asset = dep.parent
                        if (
                            parent_asset.type
                            and parent_asset.type.name.lower().starts_widht("char")
                        ):
                            shot_methodologies.append("3D Character")
                            break

        # MattePaint -> "2D DMP"
        if "matte" in child_task_type_names or "mattepaint" in child_task_type_names:
            shot_methodologies.append("2D DMP")

        # FX -> "Dynamic Sim"
        if "fx" in child_task_type_names:
            shot_methodologies.append("Dynamic Sim")

        return shot_methodologies

    def report(
        self,
        seq,
        csv_output_path,
        vfx_turnover_to_vendor_date,
        vfx_next_studio_review_date,
        vendors,
        hourly_cost,
        currency,
    ):
        """Generates the report

        :param seq: The Sequence to generate the report of
        :param csv_output_path: The output path of the resultant CSV file
        :param vfx_turnover_to_vendor_date: The date that the picture lock has been received.
        :param vfx_next_studio_review_date: The date that Netflix can review the CMPL shots
        :param list vendors: A list of vendor names
        :param hourly_cost: The hourly cost for the budget field.
        :param currency: The currency of the hourly cost.
        """
        import datetime
        import pytz
        from stalker import Task, Shot, Version, Type
        from stalker.db.session import DBSession
        from anima.utils import do_db_setup

        do_db_setup()

        utc_now = datetime.datetime.now(pytz.utc)
        ep = seq

        data = [self.csv_header]

        scene_type = Type.query.filter(Type.name == "Scene").first()
        scenes = (
            Task.query.filter(Task.type == scene_type)
            .filter(Task.parent == ep)
            .order_by(Task.name)
            .all()
        )

        for scene in scenes:
            shots_task = (
                Task.query.filter(Task.name == "Shots")
                .filter(Task.parent == scene)
                .first()
            )
            for shot in (
                Shot.query.filter(Shot.parent == shots_task).order_by(Shot.code).all()
            ):

                comp_or_cleanup_task = (
                    Task.query.filter(Task.parent == shot)
                    .filter(Task.name == "Comp")
                    .first()
                )
                if not comp_or_cleanup_task:
                    comp_or_cleanup_task = (
                        Task.query.filter(Task.parent == shot)
                        .filter(Task.name == "Cleanup")
                        .first()
                    )
                if not comp_or_cleanup_task:
                    # no comp or cleanup task, something wrong
                    print("No Comp or CleanUp task in: %s" % shot.name)
                    continue

                vfx_final_version = ""
                if (
                    comp_or_cleanup_task
                    and comp_or_cleanup_task.status
                    and comp_or_cleanup_task.status.code == "CMPL"
                ):
                    version = Version.query.filter(
                        Version.task == comp_or_cleanup_task
                    ).first()
                    if version:
                        latest_version = version.latest_version
                        vfx_final_version = "v%03i" % latest_version.version_number

                # {shot_cost};{currency};{report_date};{report_note}
                total_bid_seconds = 0
                for child in shot.children:
                    if child.schedule_model == "duration":
                        # skip ``duration`` based tasks
                        continue

                    total_bid_seconds += shot.to_seconds(
                        child.bid_timing, child.bid_unit, child.schedule_model
                    )

                shot.update_schedule_info()
                rendered_data = self.csv_format.format(
                    episode_number=ep.name[2:],
                    episode=ep,
                    scene=scene,
                    scene_number=scene.name[4:],
                    shot=shot,
                    task=comp_or_cleanup_task,
                    status=self.map_status_code(
                        self.get_shot_status(shot).code
                        if comp_or_cleanup_task.status.code != "PREV"
                        else "PREV"
                    ),
                    shot_methodologies=", ".join(
                        self.generate_shot_methodologies(shot)
                    ),
                    scope_of_work=shot.description,
                    vendors=", ".join(vendors),
                    vfx_turnover_to_vendor_date=vfx_turnover_to_vendor_date.strftime(
                        self.date_time_format
                    ),
                    vfx_next_studio_review_date=vfx_next_studio_review_date.strftime(
                        self.date_time_format
                    )
                    if comp_or_cleanup_task.status.code in ["CMPL", "PREV"]
                    else "",
                    vfx_final_delivery_date=shot.end.strftime(self.date_time_format),
                    vfx_final_version=vfx_final_version,
                    shot_cost="%0.2f" % (total_bid_seconds / 3600 * hourly_cost),
                    currency=currency,
                    report_date=utc_now.strftime(self.date_time_format),
                    report_note="",
                )

                data.append(rendered_data)

        # we may have updated the schedule info
        DBSession.commit()

        # make dirs
        os.makedirs(os.path.dirname(csv_output_path), exist_ok=True)

        with open(csv_output_path, "w") as f:
            f.write("\n".join(data))


class NetflixReview(object):
    """Generates data for Netflix review process.

    Generally it is used to generate CSVs suitable to upload to Netflix review process.
    """

    def __init__(self):
        self.outputs = []

    @classmethod
    def get_version_from_output(cls, output_path):
        """Returns the related Stalker Version from the given output path

        :param str output_path:
        :return:
        """
        import os

        basename = os.path.basename(output_path)
        version_name = basename.split(".")[0]
        from anima.utils import do_db_setup

        do_db_setup()

        from stalker import Version

        return (
            Version.query.filter(Version.full_path.contains(version_name))
            .order_by(Version.full_path)
            .first()
        )

    def generate_csv(
        self, output_path="", vendor="", submission_note="", submitting_for=""
    ):
        """outputs a CSV suitable to upload to Netflix review process

        :param output_path: The output path.
        :param vendor: The vendor name.
        :param submission_note: The submission note.
        :param submitting_for: "FINAL" or "WIP". The default value comes from the related task, if the task status is
          CMPL then it is set to "FINAL" else "WIP". If this argument is not empty then the value will be used directly.
        """
        from anima.utils import do_db_setup

        do_db_setup()
        import os

        data = [
            "Version Name,Link,Scope Of Work,Vendor,Submitting For,Submission Note",
        ]
        for output in self.outputs:
            version_data = list()
            output_base_name = os.path.basename(output)
            version = self.get_version_from_output(output)
            if not version:
                continue

            # Version Name
            version_data.append(output_base_name)

            # Link
            # Link the related shot
            shot = version.task.parent
            version_data.append(shot.name)

            # Scope Of Work
            version_data.append('"%s"' % shot.description)

            # Vendor
            version_data.append(vendor)

            # Submitting For
            if submitting_for == "":
                submitting_for = "FINAL" if shot.status.name == "CMPL" else "WIP"
            version_data.append(submitting_for)

            # Submission Note
            version_data.append(submission_note)

            data.append(",".join(version_data))

        print(data)

        with open(output_path, "w+") as f:
            f.write("\n".join(data))
