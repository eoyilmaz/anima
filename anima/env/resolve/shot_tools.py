# -*- coding: utf-8 -*-
"""Shot related tools
"""

from anima.ui.lib import QtCore, QtWidgets


class Clip(object):
    """
    """
    pass


class PlateInjector(object):
    """Renders plates for the given clip

    Generates render jobs that renders the VFX related clips in the current
    timeline to their respective shot folder.
    """

    def __init__(self):
        self.project = None
        self.sequence = None
        self.clip = None

    def create_render_job(self):
        """creates render job for the clip
        """
        # create a new render output for each clip
        from anima.env import blackmagic
        resolve = blackmagic.get_resolve()

        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        timeline = proj.GetCurrentTimeline()

        shot_code = self.get_shot_code()

        # get the shot
        from stalker import Task, Shot, Type
        shot = Shot.query.filter(Shot.project==self.project).filter(Shot.code==shot_code).first()
        if not shot:
            raise RuntimeError("No shot with code: %s" % shot_code)

        # get plate task
        plate_type = Type.query.filter(Type.name=='Plate').first()
        if not plate_type:
            raise RuntimeError("No plate type!!!")

        plate_task = Task.query.filter(Task.parent==shot).filter(Task.type==plate_type).first()
        if not plate_task:
            raise RuntimeError("No plate task in shot: %s" % shot_code)

        proj.SetCurrentRenderFormatAndCodec('exr', 'RGBHalfZIP')

        proj.SetRenderSettings({
            'MarkIn': self.clip.GetStart(),
            'MarkOut': self.clip.GetEnd()-1,
            'CustomName': '%s_Main_v001' % shot_code,
            'TargetDir': '%s/Outputs/Main/v001/exr' % plate_task.absolute_path
        })
        proj.AddRenderJob()

    def get_shot_code(self):
        """Returns the shot code of the given clip

        :param clip:
        :return:
        """
        markers = self.clip.GetMarkers()
        print('markers: %s' % markers)
        if markers:
            keys = markers.keys()
            print('keys: %s' % keys)
            frame_id = list(keys)[0]
            marker = markers[frame_id]
            print("marker: %s" % marker)
            shot_code = marker['note']
            print("shot_code: %s" % shot_code)
            return shot_code

    def set_shot_code(self, shot_code):
        """Sets the shot code of the given clip

        :param clip:
        :return:
        """
        print("#############################")
        print("set_shot_code")
        print('clip     : %s' % self.clip)
        print('clip name: %s' % self.clip.GetName())
        print('shot_code (Input): %s' % shot_code)
        markers = self.clip.GetMarkers()
        print("markers: %s" % markers)
        if markers:
            print("Updating first marker")
            # get the first marker
            keys = markers.keys()
            print('keys: %s' % keys)
            frame_id = list(keys)[0]
            print('frame_id: %s' % frame_id)
            print("type(frame_id): %s" % type(frame_id))
            marker = markers[frame_id]

            result = self.clip.UpdateMarkerCustomData('%s' % frame_id, customData={0: shot_code})
            print("result: %s" % result)
            # marker['note'] = shot_code
        else:
            print('Adding new marker')
            result = self.clip.AddMarker(
                frameId=0,
                color='Blue',
                name='Marker 1',
                note=shot_code,
                duration=1,
            )
            print("result: %s" % result)


class PlateInjectorUI(QtWidgets.QDialog):
    """The UI for the PlateInjector
    """

    def __init__(self):
        self.setup_ui()

    def setup_ui(self):
        """sets the ui up
        """
        self.main_layout = QtWidgets.QVBoxLayout(self)
