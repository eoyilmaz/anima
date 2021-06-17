# -*- coding: utf-8 -*-

__version__ = "1.1.0"


class NetflixReporter(object):
    """Creates Netflix compliant reports of Episodes/Sequences
    """
    csv_header = "Episode;Shot Name;VFX Shot Status;Key Shot;Shot Methodologies;Scope of Work;Vendors;" \
                 "VFX Turnover to Vendor Date;VFX Next Studio Review Date;VFX Final Delivery Date;VFX Final Version;" \
                 "Shot Cost;Currency;Report Date;Report Note"
    csv_format = "{episode_number};{shot.code};{status};{key_shot};{shot_methodologies};{scope_of_work};{vendors};" \
                 "{vfx_turnover_to_vendor_date};{vfx_next_studio_review_date};{vfx_final_delivery_date};" \
                 "{vfx_final_version};{shot_cost};{currency};{report_date};{report_note}"

    status_lut = {
        'WFD': 'Waiting To Start',
        'RTS': 'Waiting To Start',
        'WIP': 'In Progress',
        'PREV': 'Pending Netflix Review',
        'HREV': 'In Progress',
        'DREV': 'In Progress',
        'CMPL': 'Approved',
        'STOP': 'Omit',
        'OH': 'On Hold',
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
        if 'comp' in child_task_type_names:
            shot_methodologies.append("2D Comp")

        # Cleanup -> "2D Paint"
        if 'cleanup' in child_task_type_names:
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
            animation_tasks = filter(lambda x: x.type and x.type.name.lower().startswith("anim"), child_tasks)
            for animation_task in animation_tasks:
                for dep in animation_task.depends:
                    if dep.type and dep.type.name.lower() == 'rig':
                        # check if this is a rig for a character
                        parent_asset = dep.parent
                        if parent_asset.type and parent_asset.type.name.lower().starts_widht("char"):
                            shot_methodologies.append("3D Character")
                            break

        # MattePaint -> "2D DMP"
        if "matte" in child_task_type_names or "mattepaint" in child_task_type_names:
            shot_methodologies.append("2D DMP")

        # FX -> "Dynamic Sim"
        if "fx" in child_task_type_names:
            shot_methodologies.append("Dynamic Sim")

        return shot_methodologies

    def report(self, seq, csv_output_path, vfx_turnover_to_vendor_date, vfx_next_studio_review_date, vendors,
               hourly_cost, currency):
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

        scene_type = Type.query.filter(Type.name == 'Scene').first()
        scenes = Task.query.filter(Task.type == scene_type).filter(Task.parent == ep).order_by(Task.name).all()

        for scene in scenes:
            shots_task = Task.query.filter(Task.name == 'Shots').filter(Task.parent == scene).first()
            for shot in Shot.query.filter(Shot.parent == shots_task).order_by(Shot.code).all():

                comp_or_cleanup_task = Task.query.filter(Task.parent == shot).filter(Task.name == 'Comp').first()
                if not comp_or_cleanup_task:
                    comp_or_cleanup_task = Task.query.filter(Task.parent == shot).filter(Task.name == 'Cleanup').first()

                vfx_final_version = ''
                if comp_or_cleanup_task and comp_or_cleanup_task.status and comp_or_cleanup_task.status.code == 'CMPL':
                    version = Version.query.filter(Version.task == comp_or_cleanup_task).first()
                    if version:
                        latest_version = version.latest_version
                        vfx_final_version = 'v%03i' % latest_version.version_number

                # {shot_cost};{currency};{report_date};{report_note}
                total_bid_seconds = 0
                for child in shot.children:
                    if child.schedule_model == 'duration':
                        # skip ``duration`` based tasks
                        continue

                    total_bid_seconds += shot.to_seconds(child.bid_timing, child.bid_unit, child.schedule_model)

                shot.update_schedule_info()
                rendered_data = self.csv_format.format(
                    episode_number=ep.name[2:],
                    episode=ep,
                    scene=scene,
                    scene_number=scene.name[4:],
                    shot=shot,
                    task=comp_or_cleanup_task,
                    status=self.map_status_code(comp_or_cleanup_task.status),
                    key_shot='',
                    shot_methodologies=', '.join(self.generate_shot_methodologies(shot)),
                    scope_of_work=shot.description,
                    vendors=', '.join(vendors),
                    vfx_turnover_to_vendor_date=vfx_turnover_to_vendor_date.strftime(self.date_time_format),
                    vfx_next_studio_review_date=vfx_next_studio_review_date if comp_or_cleanup_task.status.code == 'CMPL' else '',
                    vfx_final_delivery_date=shot.end.strftime(self.date_time_format),
                    vfx_final_version=vfx_final_version,
                    shot_cost='%0.2f' % (total_bid_seconds / 3600 * hourly_cost),
                    currency=currency,
                    report_date=utc_now.strftime(self.date_time_format),
                    report_note=''
                )

                data.append(rendered_data)

        # we may have updated the schedule info
        DBSession.commit()

        with open(csv_output_path, 'w') as f:
            f.write('\n'.join(data))
