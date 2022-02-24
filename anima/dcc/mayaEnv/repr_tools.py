# -*- coding: utf-8 -*-

import os
import re
import shutil
import subprocess
import tempfile
import uuid

import pymel.core as pm
from stalker import LocalSession, Repository

from anima.representation import Representation
from anima.dcc.mayaEnv import auxiliary
from anima import logger


#
# Stores shading nodes that is commonly used
# This is used in publish scripts and in representation generation
#
RENDER_RELATED_NODE_TYPES = [

    # generic
    'shadingEngine',
    'displacementShader',

    # materials
    'anisotropic',
    'blinn',
    'lambert',
    'layeredShader',
    'oceanShader',
    'phong',
    'phongE',
    'rampShader',
    'shadingMap',
    'surfaceShader',
    'useBackground',

    # volumetricMaterials
    'envFog',
    'fluidShape',
    'lightFog',
    'particleCloud',
    'volumeFog',
    'volumeShader',

    # 2DTextures
    'bulge',            # +
    'checker',          # +
    'cloth',            # +
    'file',             # +
    'fluidTexture2D',   # +
    'fractal',          # +
    'grid',             # +
    'mandelbrot',       # +
    'mountain',         # +
    'movie',            # +
    'noise',            # +
    'ocean',            # +
    'psdFileTex',       # +
    'ramp',             # +
    'water',            # +
    'layeredTexture',   # + this is not a 2d texture but will be listed here
    'imagePlane',       # +

    # 3DTextures
    'brownian',         # +
    'cloud',            # +
    'crater',           # +
    'fluidTexture3D',   # +
    'granite',          # +
    'leather',          # +
    'mandelbrot3D',     # +
    'marble',           # +
    'rock',             # +
    'snow',             # +
    'solidFractal',     # +
    'stucco',           # +
    'volumeNoise',      # +
    'wood',             # +

    # environmentTextures
    'envBall',
    'envChrome',
    'envCube',
    'envSky',
    'envSphere',

    # generalUtilities
    'arrayMapper',
    'bump2d',            # +
    'bump3d',            # +
    'composeMatrix',
    'condition',
    'decomposeMatrix',
    'distanceBetween',
    'eulerToQuat',
    'heightField',
    'inverseMatrix',
    'lightInfo',
    'multiplyDivide',
    'place2dTexture',    # +
    'place3dTexture',    # +
    'plusMinusAverage',  # +
    'projection',        # +
    'quatAdd',
    'quatConjugate',
    'quatInvert',
    'quatNegate',
    'quatNormalize',
    'quatProd',
    'quatSub',
    'quatToEuler',
    'reverse',
    'samplerInfo',       # +
    'setRange',
    'stencil',           # +
    'transposeMatrix',
    'uvChooser',         # +
    'vectorProduct',

    # scalarUtilities
    'addDoubleLinear',
    'addMatrix',
    'angleBetween',
    'blendTwoAttr',
    'choice',
    'chooser',
    'curveInfo',
    'fourByFourMatrix',
    'frameCache',
    'multDoubleLinear',
    'multMatrix',
    'surfaceInfo',       # +
    'unitConversion',
    'wtAddMatrix',

    # switchUtilities
    'doubleShadingSwitch',
    'quadShadingSwitch',
    'singleShadingSwitch',
    'tripleShadingSwitch',

    # colorUtilities
    'blendColors',      # +
    'clamp',            # +
    'colorProfile',
    'contrast',         # +
    'gammaCorrect',     # +
    #'grade_tm',
    'hsvToRgb',         # +
    'luminance',        # +
    'remapColor',       # +
    'remapHsv',         # +
    'remapValue',       # +
    'rgbToHsv',         # +
    'surfaceLuminance', # +

    # particleUtilities
    'particleSamplerInfo',

    # glow
    'opticalFX',

    # arnoldTexture
    'aiImage',       # +
    'aiNoise',       # +

    # arnoldShaderSurface
    'aiAmbientOcclusion',
    'aiHair',
    'aiRaySwitch',
    'aiShadowCatcher',
    'aiSkin',
    'aiStandard',
    'aiStandardSurface',
    'aiUtility',
    'aiWireframe',

    # arnoldShaderUtility
    'aiBump2d',
    'aiBump3d',
    'aiMotionVector',
    'aiUserDataBool',
    'aiUserDataColor',
    'aiUserDataFloat',
    'aiUserDataInt',
    'aiUserDataPnt2',
    'aiUserDataString',
    'aiUserDataVector',
    'aiVolumeCollector',
    'aiWriteColor',
    'aiWriteFloat',

    # arnoldShaderVolume
    'aiDensity',
    'aiFog',
    'aiVolumeScattering',

    # arnoldTextureEnvironment
    'aiPhysicalSky',
    'aiSky',

    # Redshift Materials
    'RedshiftAmbientOcclusion',
    'RedshiftArchitectural',
    'RedshiftAttributeLookup',
    'RedshiftBokeh',
    'RedshiftBumpBlender',
    'RedshiftBumpMap',
    'RedshiftCameraMap',
    'RedshiftCarPaint',
    'RedshiftCurvature',
    'RedshiftDisplacement',
    'RedshiftDisplacementBlender',
    'RedshiftDomeLight',
    'RedshiftEnvironment',
    'RedshiftFresnel',
    'RedshiftLightGobo',
    'RedshiftIESLight',
    'RedshiftIncandescent',
    'RedshiftLensDistortion',
    'RedshiftMaterial',
    'RedshiftMaterialBlender',
    'RedshiftNormalMap',
    'RedshiftHair',
    'RedshiftHairPosition',
    'RedshiftHairRandomColor',
    'RedshiftMatteShadowCatcher',
    'RedshiftPhotographicExposure',
    'RedshiftPhysicalLight',
    'RedshiftPhysicalSky',
    'RedshiftPhysicalSun',
    'RedshiftPortalLight',
    'RedshiftRaySwitch',
    'RedshiftRoundCorners',
    'RedshiftShaderSwitch',
    'RedshiftSkin',
    'RedshiftSprite',
    'RedshiftState',
    'RedshiftSubSurfaceScatter',
    'RedshiftUserDataColor',
    'RedshiftUserDataInteger',
    'RedshiftUserDataVector',
    'RedshiftUserDataScalar',
    'RedshiftVertexColor',
    'RedshiftVolume',
    'RedshiftVolumeScattering',
    'RedshiftWireFrame',
]

READ_ONLY_NODE_NAMES = [
    'lambert1',
    'particleCloud1',
    'shaderGlow1',
    'initialParticleSE',
    'initialShadingGroup'
]


class RepresentationGenerator(object):
    """Generates different representations of the current scene
    """

    def __init__(self, version=None):
        local_session = LocalSession()
        self.logged_in_user = local_session.logged_in_user

        if not self.logged_in_user:
            raise RuntimeError('Please login first!')

        from anima.dcc.mayaEnv import Maya
        self.maya_env = Maya()

        self.base_take_name = None
        self.version = version

    @classmethod
    def get_local_root_nodes(cls):
        """returns the root nodes that are not referenced
        """
        return [node for node in auxiliary.get_root_nodes()
                if node.referenceFile() is None]

    def get_latest_repr_version(self, take_name):
        """returns the latest published version or creates a new version

        :param str take_name: The take_name
        :return:
        """
        from stalker import Version

        # filter to get the latest published version
        v = Version.query\
            .filter(Version.task == self.version.task)\
            .filter(Version.take_name == take_name)\
            .filter(Version.is_published == True)\
            .order_by(Version.version_number.desc())\
            .first()

        if v is None:
            # create a new version
            v = Version(
                created_by=self.logged_in_user,
                task=self.version.task,
                take_name=take_name
            )
            v.is_published = True
        else:
            # change updated by
            v.updated_by = self.logged_in_user

        return v

    @classmethod
    def is_model_task(cls, task):
        """checks if the given task is a model task

        :param task: A Stalker Task instance
        """
        task_type = task.type
        if task_type:
            # check the task type name
            if task_type.name.lower() in ['model']:
                return True
        else:
            # check the task name
            if task.name.lower() in ['model']:
                return True

        # if we came here it must not be a model task
        return False

    @classmethod
    def is_look_dev_task(cls, task):
        """checks if the given task is a look development task

        :param task: A Stalker Task instance
        """
        task_type = task.type
        if task_type:
            # check the task type name
            if task_type.name.lower() in ['look development']:
                return True
        else:
            # check the task name
            if task.name.lower() in ['look_dev', 'lookdev', 'look dev']:
                return True

        # if we came here it must not be a look dev task task
        return False

    @classmethod
    def is_scene_assembly_task(cls, task):
        """checks if the given task is a scene assembly task

        :param task: A Stalker Task instance
        """
        task_type = task.type
        if task_type:
            # check the task type name
            if task_type.name.lower() in ['scene assembly']:
                return True
        else:
            # check the task name
            if task.name.lower() in ['scene assembly']:
                return True

        # if we came here it must not be a scene assembly task task
        return False

    @classmethod
    def is_vegetation_task(cls, task):
        """checks if the given task is a vegetation task

        :param task: A Stalker Task instance
        """
        task_type = task.type
        if task_type:
            # check the task type name
            if task_type.name.lower() in ['vegetation']:
                return True
        else:
            # check the task name
            if task.name.lower() in ['vegetation']:
                return True

        # if we came here it must not be a vegetation task task
        return False

    @classmethod
    def is_exterior_or_interior_task(cls, task):
        """checks if the given task is the first Layout task of an
        Exterior or Interior task.

        :param task: a stalker.task
        :return:
        """

        if task.type and task.type.name.lower() == 'layout':
            parent = task.parent
            if task.name.lower() == 'hires':
                if parent and parent.parent and parent.parent.type \
                   and parent.parent.type.name.lower() in ['exterior', 'interior']:
                    return True
            elif task.name.lower() == 'layout':
                if parent and parent.type \
                   and parent.type.name.lower() in ['exterior', 'interior']:
                    return True

        return False

    def _validate_version(self, version):
        """validates the given version value

        :param version: A stalker.model.version.Version instance
        :return:
        """
        if not version:
            raise RuntimeError(
                'Please supply a valid Stalker Version object!'
            )

        from stalker import Version
        if not isinstance(version, Version):
            raise TypeError(
                'version should be a stalker.models.version.Version instance'
            )

        r = Representation(version=version)

        self.base_take_name = r.get_base_take_name(version)
        if not r.is_base():
            raise RuntimeError(
                'This is not a Base take for this representation series, '
                'please open the base (%s) take!!!' % self.base_take_name
            )

        return version

    def open_version(self, version=None):
        """Opens the given version

        :param version: A stalker.models.version.Version instance
        :return:
        """
        current_v = self.maya_env.get_current_version()
        if current_v is not version:
            self.maya_env.open(version, force=True,
                               skip_update_check=True,
                               reference_depth=3)

    @classmethod
    def make_unique(cls, filename, force=True):
        """Generates a unique filename if the file already exists

        :param filename:
        :param force:
        :return:
        """
        import uuid

        def generate_filename():
            random_part = uuid.uuid4().hex[-4:]
            data = os.path.splitext(filename)
            return '%s_%s%s' % (data[0], random_part, data[1])

        if not force:
            if os.path.exists(filename):
                new_filename = generate_filename()
                while os.path.exists(new_filename):
                    new_filename = generate_filename()
                return new_filename
            else:
                return filename
        else:
            return generate_filename()

    def generate_all(self):
        """generates all representations at once
        """
        # self.generate_gpu()
        # self.generate_ass()
        self.generate_rs()

    def generate_bbox(self):
        """generates the BBox representation of the current scene
        """
        # validate the version first
        self.version = self._validate_version(self.version)

        if not os.path.exists(self.version.absolute_full_path):
            raise RuntimeError(
                "Path doesn't exists: %s" % self.version.absolute_full_path
            )
        self.open_version(self.version)

        task = self.version.task

        # check if all references have an BBOX repr first
        refs_with_no_bbox_repr = []
        for ref in pm.listReferences():
            if ref.version and not ref.has_repr('BBOX'):
                refs_with_no_bbox_repr.append(ref)

        if len(refs_with_no_bbox_repr):
            raise RuntimeError(
                'Please generate the BBOX Representation of the references '
                'first!!!\n%s' %
                '\n'.join(map(lambda x: str(x.path), refs_with_no_bbox_repr))
            )

        # do different things for Vegetation tasks
        if self.is_vegetation_task(task):
            # load all references back
            for ref in pm.listReferences():
                ref.load()

            # find the _pfxPolygons node
            pfx_polygons_node = pm.PyNode('kks___vegetation_pfxPolygons')

            all_children = []
            for node in pfx_polygons_node.getChildren():
                for child_node in node.getChildren():
                    all_children.append(child_node)

            auxiliary.replace_with_bbox(all_children)

            # clean up other nodes
            pm.delete('kks___vegetation_pfxStrokes')
            pm.delete('kks___vegetation_paintableGeos')
        elif self.is_scene_assembly_task(task):
            # reload all references
            # replace all root references with their BBOX representation
            for ref in pm.listReferences():
                ref.to_repr('BBOX')
        else:
            # find all non referenced root nodes
            root_nodes = self.get_local_root_nodes()

            if len(root_nodes):
                all_children = []
                for root_node in root_nodes:
                    for child in root_node.getChildren():
                        all_children.append(child)

                auxiliary.replace_with_bbox(all_children)

            # reload all references
            # replace all root references with their BBOX representation
            for ref in pm.listReferences():
                ref.to_repr('BBOX')

        # if this is an Exterior/Interior -> Layout -> Hires task flatten it
        if self.is_exterior_or_interior_task(task):
            # and import all of the references
            all_refs = pm.listReferences()
            while len(all_refs) != 0:
                for ref in all_refs:
                    if not ref.isLoaded():
                        ref.load()
                    ref.importContents()
                all_refs = pm.listReferences()

        # save the scene as {{original_take}}@BBOX
        # use maya
        take_name = '%s%s%s' % (
            self.base_take_name, Representation.repr_separator, 'BBOX'
        )
        v = self.get_latest_repr_version(take_name)

        self.maya_env.save_as(v)

        # reopen the original version
        pm.newFile(force=True)

    def generate_proxy(self):
        """generates the Proxy representation of the current scene
        """
        pass

    def generate_gpu(self):
        """generates the GPU representation of the current scene
        """
        # validate the version first
        self.version = self._validate_version(self.version)

        if not os.path.exists(self.version.absolute_full_path):
            raise RuntimeError("Path doesn't exists: %s" % self.version.absolute_full_path)
        self.open_version(self.version)

        # load necessary plugins
        pm.loadPlugin('gpuCache')
        pm.loadPlugin('AbcExport')
        pm.loadPlugin('AbcImport')

        # check if all references have an GPU repr first
        refs_with_no_gpu_repr = []
        for ref in pm.listReferences():
            if ref.version and not ref.has_repr('GPU'):
                refs_with_no_gpu_repr.append(ref)

        if len(refs_with_no_gpu_repr):
            raise RuntimeError(
                'Please generate the GPU Representation of the references '
                'first!!!\n%s' %
                '\n'.join(map(lambda x: str(x.path), refs_with_no_gpu_repr))
            )

        # unload all references
        for ref in pm.listReferences():
            ref.unload()

        # for local models generate an ABC file
        output_path = os.path.join(
            self.version.absolute_path,
            'Outputs/alembic/'
        ).replace('\\', '/')

        gpu_command = \
            'gpuCache -startTime %(start_frame)s -endTime %(end_frame)s '\
            '-optimize -optimizationThreshold 40000 '\
            '-writeMaterials ' \
            '-dataFormat ogawa '\
            '-directory "%(path)s" '\
            '-fileName "%(filename)s" ' \
            '%(node)s;'

        # do not use the -dataFormat flag if it is earlier than Maya2014 Ext1
        if pm.versions.current() < 201450:
            gpu_command = \
                'gpuCache -startTime %(start_frame)s ' \
                '-endTime %(end_frame)s ' \
                '-optimize -optimizationThreshold 40000 ' \
                '-writeMaterials ' \
                '-directory "%(path)s" ' \
                '-fileName "%(filename)s" ' \
                '%(node)s;'

        start_frame = end_frame = int(pm.currentTime(q=1))

        if not self.is_scene_assembly_task(self.version.task):

            if self.is_vegetation_task(self.version.task):
                # in vegetation files, we export the GPU files directly from
                # the Base version, also we use the geometry under
                # "pfxPolygons" and parent the resulting Stand-In nodes to the
                # pfxPolygons
                # load all references
                for ref in pm.listReferences():
                    ref.load()

                # find the _pfxPolygons node
                try:
                    pfx_polygons_node = \
                        pm.PyNode('kks___vegetation_pfxPolygons')
                except pm.MayaNodeError:
                    pfx_polygons_node = None

                try:
                    pfx_polygons_node = \
                        pm.PyNode('kks___vegetation_pfxPolygons')
                    pfx_polygons_node_children = \
                        pfx_polygons_node.getChildren()
                except pm.MayaNodeError:
                    pfx_polygons_node_children = []

                for node in pfx_polygons_node_children:
                    for child_node in node.getChildren():
                        child_node_name = \
                            child_node.name().split('___')[-1]
                        child_node_shape = child_node.getShape()
                        child_node_shape_name = None

                        if child_node_shape:
                            child_node_shape_name = child_node_shape.name()

                        pm.select(child_node)
                        temp_output_fullpath = \
                            tempfile.mktemp().replace('\\', '/')
                        temp_output_path, temp_output_filename = \
                            os.path.split(temp_output_fullpath)

                        output_filename = '%s_%s' % (
                            self.version.nice_name,
                            child_node_name.split(':')[-1]
                            .replace(':', '_')
                            .replace('|', '_')
                        )

                        # run the mel command
                        # check if file exists
                        pm.mel.eval(
                            gpu_command % {
                                'start_frame': start_frame,
                                'end_frame': start_frame,  # end_frame,
                                'node': child_node.fullPath(),
                                'path': temp_output_path,
                                'filename': temp_output_filename
                            }
                        )

                        cache_file_full_path = \
                            os.path\
                            .join(output_path, output_filename + '.abc')\
                            .replace('\\', '/')

                        # create the intermediate directories
                        try:
                            os.makedirs(
                                os.path.dirname(cache_file_full_path)
                            )
                        except OSError:
                            # directory exists
                            pass

                        # now move in to its place
                        shutil.move(
                            temp_output_fullpath + '.abc',
                            cache_file_full_path
                        )

                        # set rotate and scale pivots
                        rp = pm.xform(child_node, q=1, ws=1, rp=1)
                        sp = pm.xform(child_node, q=1, ws=1, sp=1)
                        # child_node.setRotatePivotTranslation([0, 0, 0])

                        # delete the child and add a GPU node instead
                        pm.delete(child_node)

                        # check if file exists and create nodes
                        if os.path.exists(cache_file_full_path):
                            gpu_node = pm.createNode('gpuCache')
                            gpu_node_tra = gpu_node.getParent()

                            pm.parent(gpu_node_tra, node)
                            gpu_node_tra.rename(child_node_name)

                            if child_node_shape_name is not None:
                                gpu_node.rename(child_node_shape_name)

                            pm.xform(gpu_node_tra, ws=1, rp=rp)
                            pm.xform(gpu_node_tra, ws=1, sp=sp)

                            gpu_node.setAttr(
                                'cacheFileName',
                                cache_file_full_path,
                                type="string"
                            )
                        else:
                            print(
                                'File not found!: %s' %
                                cache_file_full_path
                            )

                # clean up other nodes
                try:
                    pm.delete('kks___vegetation_pfxStrokes')
                except pm.MayaNodeError:
                    pass

                try:
                    pm.delete('kks___vegetation_paintableGeos')
                except pm.MayaNodeError:
                    pass

                # Check RedshiftProxyMesh nodes in the scene
                rs_proxy_lut = {}
                rs_proxy_meshes = pm.ls(type='RedshiftProxyMesh')
                for rs_proxy_mesh in rs_proxy_meshes:
                    # this scene is not a regular Vegetation task
                    # it is the new Proxy file type that is converted from
                    # Houdini.
                    #
                    # So generate the alembic files by first converting the
                    # rsProxyMesh'es in to preview nodes

                    # for the same rsproxy use the same gpuproxy
                    rs_proxy_mesh_file_path = rs_proxy_mesh.fileName.get()
                    rs_proxy_mesh_file_name = \
                        os.path.basename(rs_proxy_mesh_file_path)
                    cache_file_full_path = None
                    if rs_proxy_mesh_file_path in rs_proxy_lut:
                        cache_file_full_path = \
                            rs_proxy_lut[rs_proxy_mesh_file_path]

                    child_node = \
                        rs_proxy_mesh.outputs(type='mesh')[0]
                    child_shape = \
                        child_node.getShape()
                    root_node = child_node.getParent()
                    child_name = child_node.name()
                    child_shape_name = None
                    if child_shape:
                        child_shape_name = child_shape.name()

                    # store local position
                    tra = child_node.t.get()
                    rot = child_node.r.get()
                    sca = child_node.s.get()

                    # do not generate the cache_file_path if it exists
                    if cache_file_full_path is None:
                        temp_output_fullpath = \
                            tempfile.mktemp().replace('\\', '/')
                        temp_output_path, temp_output_filename = \
                            os.path.split(temp_output_fullpath)

                        output_filename = '%s.abc' % \
                            os.path.splitext(
                                os.path.basename(
                                    rs_proxy_mesh_file_name
                                )
                            )[0]

                        # generate at origin
                        pm.parent(child_node, world=1)
                        child_node.t.set(0, 0, 0)
                        child_node.r.set(0, 0, 0)
                        child_node.s.set(1, 1, 1)

                        # set proxy mesh display to preview
                        rs_proxy_mesh.displayMode.set(1)

                        # run the mel command
                        # check if file exists
                        pm.mel.eval(
                            gpu_command % {
                                'start_frame': start_frame,
                                'end_frame': end_frame,
                                'node': child_node.fullPath(),
                                'path': temp_output_path,
                                'filename': temp_output_filename
                            }
                        )

                        # restore local position
                        pm.parent(child_node, root_node)
                        child_node.t.set(tra)
                        child_node.r.set(rot)
                        child_node.s.set(sca)

                        cache_file_full_path = \
                            os.path.join(
                                output_path,
                                output_filename
                            ).replace('\\', '/')

                        # store the cache_file_full_path
                        rs_proxy_lut[rs_proxy_mesh_file_path] = \
                            cache_file_full_path

                        # create the intermediate directories
                        try:
                            os.makedirs(
                                os.path.dirname(cache_file_full_path)
                            )
                        except OSError:
                            # directory exists
                            pass

                        # now move in to its place
                        shutil.move(
                            temp_output_fullpath + '.abc',
                            cache_file_full_path
                        )

                    # delete the child and add a GPU node instead
                    pm.delete(child_node)

                    # check if file exists
                    if os.path.exists(cache_file_full_path):
                        gpu_node = pm.createNode('gpuCache')
                        gpu_node_tra = gpu_node.getParent()

                        pm.parent(gpu_node_tra, root_node)
                        gpu_node_tra.rename(child_name)

                        if child_shape_name is not None:
                            gpu_node.rename(child_shape_name)

                        # restore local transform
                        gpu_node_tra.t.set(tra)
                        gpu_node_tra.r.set(rot)
                        gpu_node_tra.s.set(sca)

                        gpu_node.setAttr(
                            'cacheFileName',
                            cache_file_full_path,
                            type="string"
                        )
            else:
                root_nodes = self.get_local_root_nodes()
                if len(root_nodes):
                    for root_node in root_nodes:
                        # export each child of each root as separate nodes
                        for child_node in root_node.getChildren():

                            # check if it is a transform node
                            if not isinstance(child_node, pm.nt.Transform):
                                continue

                            if not auxiliary.has_shape(child_node):
                                continue

                            child_name = child_node.name()
                            child_shape = child_node.getShape()
                            child_shape_name = None
                            if child_shape:
                                child_shape_name = child_shape.name()

                            child_full_path = \
                                child_node.fullPath()[1:].replace('|', '_')

                            temp_output_fullpath = \
                                tempfile.mktemp().replace('\\', '/')
                            temp_output_path, temp_output_filename = \
                                os.path.split(temp_output_fullpath)

                            output_filename =\
                                '%s_%s' % (
                                    self.version.nice_name,
                                    child_full_path
                                )

                            # before doing anything smooth any polygon objects
                            # under this node if aiSubdivType is not 0
                            for node in child_node.listRelatives(ad=1, type='mesh'):
                                if node.getAttr('aiSubdivType') != 0:
                                    node.displaySmoothMesh.set(2)
                                    # set it equal to aiSubdivIterations
                                    node.smoothLevel.set(
                                        node.aiSubdivIterations.get()
                                    )

                            # run the mel command
                            # check if file exists
                            pm.mel.eval(
                                gpu_command % {
                                    'start_frame': start_frame,
                                    'end_frame': end_frame,
                                    'node': child_node.fullPath(),
                                    'path': temp_output_path,
                                    'filename': temp_output_filename
                                }
                            )

                            cache_file_full_path = \
                                os.path\
                                .join(
                                    output_path,
                                    '%s.abc' % (
                                        output_filename
                                    )
                                )\
                                .replace('\\', '/')

                            # create the intermediate directories
                            try:
                                os.makedirs(
                                    os.path.dirname(cache_file_full_path)
                                )
                            except OSError:
                                # directory exists
                                pass

                            # now move in to its place
                            shutil.move(
                                temp_output_fullpath + '.abc',
                                cache_file_full_path
                            )

                            # set rotate and scale pivots
                            rp = pm.xform(child_node, q=1, ws=1, rp=1)
                            sp = pm.xform(child_node, q=1, ws=1, sp=1)
                            # rpt = child_node.getRotatePivotTranslation()

                            # delete the child and add a GPU node instead
                            pm.delete(child_node)

                            # check if file exists
                            if os.path.exists(cache_file_full_path):
                                gpu_node = pm.createNode('gpuCache')
                                gpu_node_tra = gpu_node.getParent()

                                pm.parent(gpu_node_tra, root_node)
                                gpu_node_tra.rename(child_name)

                                if child_shape_name is not None:
                                    gpu_node.rename(child_shape_name)

                                pm.xform(gpu_node_tra, ws=1, rp=rp)
                                pm.xform(gpu_node_tra, ws=1, sp=sp)
                                # child_node.setRotatePivotTranslation(rpt)

                                gpu_node.setAttr(
                                    'cacheFileName',
                                    cache_file_full_path,
                                    type="string"
                                )

        # load all references again
        # convert all references to GPU
        logger.debug('converting all references to GPU')
        for ref in pm.listReferences():
            # check if this is a Model reference
            ref.to_repr('GPU')
            ref.load()

        # if this is an Exterior/Interior -> Layout -> Hires task flatten it
        task = self.version.task

        is_exterior_or_interior_task = self.is_exterior_or_interior_task(task)
        if is_exterior_or_interior_task:
            logger.debug('importing all references')
            # and import all of the references
            all_refs = pm.listReferences()
            while len(all_refs) != 0:
                for ref in all_refs:
                    if not ref.isLoaded():
                        ref.load()
                    ref.importContents()
                all_refs = pm.listReferences()

            # assign lambert1 to all GPU nodes
            pm.sets('initialShadingGroup', e=1, fe=auxiliary.get_root_nodes())

            # clean up
            self.clean_up()

        # 6. save the scene as {{original_take}}@GPU
        # use maya
        take_name = '%s%s%s' % (
            self.base_take_name, Representation.repr_separator, 'GPU'
        )
        v = self.get_latest_repr_version(take_name)
        self.maya_env.save_as(v)

        # export the root nodes under the same file
        if is_exterior_or_interior_task:
            logger.debug('exporting root nodes')
            pm.select(auxiliary.get_root_nodes())
            pm.exportSelected(
                v.absolute_full_path,
                type='mayaAscii',
                force=True
            )

        logger.debug('renewing scene')
        # clear scene
        pm.newFile(force=True)

    def make_tx(self, texture_path):
        """converts the given texture to TX
        """
        # check if it is tiled
        tile_path = texture_path
        orig_path_as_tx = ''.join([os.path.splitext(texture_path)[0], '.tx'])

        if '<' in tile_path:
            # replace any <U> and <V> with an *
            tile_path = tile_path.replace('<U>', '*')
            tile_path = tile_path.replace('<V>', '*')
            tile_path = tile_path.replace('<UDIM>', '*')

        import glob
        files_to_process = glob.glob(tile_path)

        for tile_path in files_to_process:
            tx_path = ''.join([os.path.splitext(tile_path)[0], '.tx'])
            # generate if not exists
            if not os.path.exists(tx_path):
                # TODO: Consider Color Management
                cmd = 'maketx -o "%s" -u --oiio %s' % (tx_path, tile_path)

                if os.name == 'nt':
                    proc = subprocess.Popen(
                        cmd,
                        creationflags=subprocess.SW_HIDE,
                        shell=True
                    )
                else:
                    proc = subprocess.Popen(
                        cmd,
                        shell=True
                    )
    
                proc.wait()

        return orig_path_as_tx

    @classmethod
    def clean_up(self):
        """cleans up the scene
        """
        num_of_items_deleted = pm.mel.eval('MLdeleteUnused')

        logger.debug('deleting unknown references')
        delete_nodes_types = ['reference', 'unknown']
        for node in pm.ls(type=delete_nodes_types):
            node.unlock()

        logger.debug('deleting "delete_nodes_types"')
        try:
            pm.delete(pm.ls(type=delete_nodes_types))
        except RuntimeError:
            pass

    def generate_ass(self):
        """generates the ASS representation of the current scene

        For Model Tasks the ASS is generated over the LookDev Task because it
        is not possible to assign a material to an object inside an ASS file.
        """
        # before doing anything, check if this is a look dev task
        # and export the objects from the referenced files with their current
        # shadings, then replace all of the references to ASS repr and than
        # add Stand-in nodes and parent them under the referenced models

        # load necessary plugins
        pm.loadPlugin('mtoa')

        # disable "show plugin shapes"
        active_panel = auxiliary.Playblaster.get_active_panel()
        show_plugin_shapes = pm.modelEditor(active_panel, q=1, pluginShapes=1)
        pm.modelEditor(active_panel, e=1, pluginShapes=False)

        # validate the version first
        self.version = self._validate_version(self.version)

        if not os.path.exists(self.version.absolute_full_path):
            raise RuntimeError("Path doesn't exists: %s" % self.version.absolute_full_path)
        self.open_version(self.version)

        task = self.version.task

        # export_command = 'arnoldExportAss -f "%(path)s" -s -mask 24 ' \
        #                  '-lightLinks 0 -compressed -boundingBox ' \
        #                  '-shadowLinks 0 -cam perspShape;'

        export_command = 'arnoldExportAss -f "%(path)s" -s -mask 60' \
                         '-lightLinks 1 -compressed -boundingBox ' \
                         '-shadowLinks 1 -cam perspShape;'

        # calculate output path
        output_path = \
            os.path.join(self.version.absolute_path, 'Outputs/ass/')\
            .replace('\\', '/')

        # check if all references have an ASS repr first
        refs_with_no_ass_repr = []
        for ref in pm.listReferences():
            if ref.version and not ref.has_repr('ASS'):
                refs_with_no_ass_repr.append(ref)

        if len(refs_with_no_ass_repr):
            raise RuntimeError(
                'Please generate the ASS Representation of the references '
                'first!!!\n%s' %
                '\n'.join(map(lambda x: str(x.path), refs_with_no_ass_repr))
            )

        if self.is_look_dev_task(task):
            # in look dev files, we export the ASS files directly from the Base
            # version and parent the resulting Stand-In node to the parent of
            # the child node

            # load only Model references
            for ref in pm.listReferences():
                v = ref.version
                load_ref = False
                if v:
                    ref_task = v.task
                    if self.is_model_task(ref_task):
                        load_ref = True

                if load_ref:
                    ref.load()
                    ref.importContents()

            # Make all texture paths relative
            # replace all "$REPO#" from all texture paths first
            #
            # This is needed to properly render textures with any OS
            maya_version = int(pm.about(v=1))
            if maya_version == 2014:
                types_and_attrs = {
                    'aiImage': 'filename',
                    'file': 'fileTextureName',
                    'imagePlane': 'imageName'
                }
            else:
                types_and_attrs = {
                    'aiImage': 'filename',
                    'file': ('computedFileTextureNamePattern',
                             'fileTextureName'),
                    'imagePlane': 'imageName'
                }

            for node_type in types_and_attrs.keys():
                attr_name = types_and_attrs[node_type]
                set_attr_name = attr_name
                if isinstance(attr_name, tuple):
                    set_attr_name = attr_name[1]
                    attr_name = attr_name[0]

                for node in pm.ls(type=node_type):
                    orig_path = node.getAttr(attr_name).replace("\\", "/")
                    path = re.sub(
                        r'(\$REPO[0-9/]+)',
                        '',
                        orig_path
                    )
                    tx_path = self.make_tx(path)
                    inputs = node.attr(set_attr_name).inputs(p=1)

                    if len(inputs):
                        # set the input attribute
                        for input_node_attr in inputs:
                            input_node_attr.set(tx_path)
                    else:
                        node.setAttr(set_attr_name, tx_path)

            # randomize all render node names
            # This is needed to prevent clashing of materials in a bigger scene
            all_render_related_nodes = [
                node for node in pm.ls()
                if node.type() in RENDER_RELATED_NODE_TYPES
            ]
            for node in all_render_related_nodes:
                if node.referenceFile() is None and \
                   node.name() not in READ_ONLY_NODE_NAMES:
                    node.rename('%s_%s' % (node.name(), uuid.uuid4().hex))

            nodes_to_ass_files = {}

            # export all root ass files as they are
            for root_node in auxiliary.get_root_nodes():
                for child_node in root_node.getChildren():
                    # check if it is a transform node
                    if not isinstance(child_node, pm.nt.Transform):
                        continue

                    if not auxiliary.has_shape(child_node):
                        continue

                    # randomize child node name
                    # TODO: This is not working as intended, node names are like |NS:node1|NS:node2
                    #       resulting a child_node_name as "node2"
                    child_node_name = child_node\
                        .fullPath()\
                        .replace('|', '_')\
                        .split(':')[-1]

                    child_node_full_path = child_node.fullPath()

                    pm.select(child_node)
                    child_node.rename(
                        '%s_%s' % (child_node.name(), uuid.uuid4().hex)
                    )

                    output_filename =\
                        '%s_%s.ass' % (
                            self.version.nice_name,
                            child_node_name
                        )

                    output_full_path = \
                        os.path.join(output_path, output_filename)

                    # run the mel command
                    pm.mel.eval(
                        export_command % {
                            'path': output_full_path.replace('\\', '/')
                        }
                    )
                    nodes_to_ass_files[child_node_full_path] = \
                        '%s.gz' % output_full_path
                    # print('%s -> %s' % (
                    #     child_node_full_path,
                    #     output_full_path)
                    # )

            # reload the scene
            pm.newFile(force=True)
            self.open_version(self.version)

            # convert all references to ASS
            # we are doing it a little bit early here, but we need to
            for ref in pm.listReferences():
                ref.to_repr('ASS')

            all_stand_ins = pm.ls(type='aiStandIn')
            for ass_node in all_stand_ins:
                ass_tra = ass_node.getParent()
                full_path = ass_tra.fullPath()
                if full_path in nodes_to_ass_files:
                    ass_file_path = \
                        Repository.to_os_independent_path(
                            nodes_to_ass_files[full_path]
                        )
                    ass_node.setAttr('dso', ass_file_path)

        elif self.is_vegetation_task(task):
            # in vegetation files, we export the ASS files directly from the
            # Base version, also we use the geometry under "pfxPolygons"
            # and parent the resulting Stand-In nodes to the
            # pfxPolygons
            # load all references
            for ref in pm.listReferences():
                ref.load()

            # Make all texture paths relative
            # replace all "$REPO#" from all texture paths first
            #
            # This is needed to properly render textures with any OS
            maya_version = int(pm.about(v=1))
            if maya_version == 2014:
                types_and_attrs = {
                    'aiImage': 'filename',
                    'file': 'fileTextureName',
                    'imagePlane': 'imageName'
                }
            else:
                types_and_attrs = {
                    'aiImage': 'filename',
                    'file': ('computedFileTextureNamePattern',
                             'fileTextureName'),
                    'imagePlane': 'imageName'
                }

            for node_type in types_and_attrs.keys():
                attr_name = types_and_attrs[node_type]
                set_attr_name = attr_name
                if isinstance(attr_name, tuple):
                    set_attr_name = attr_name[1]
                    attr_name = attr_name[0]

                for node in pm.ls(type=node_type):
                    orig_path = node.getAttr(attr_name).replace("\\", "/")
                    path = re.sub(
                        r'(\$REPO[0-9/]+)',
                        '',
                        orig_path
                    )
                    tx_path = self.make_tx(path)
                    inputs = node.attr(set_attr_name).inputs(p=1)

                    if len(inputs):
                        # set the input attribute
                        for input_node_attr in inputs:
                            input_node_attr.set(tx_path)
                    else:
                        node.setAttr(set_attr_name, tx_path)

            # import shaders that are referenced to this scene
            # there is only one reference in the vegetation task and this is
            # the shader scene
            for ref in pm.listReferences():
                ref.importContents()

            # randomize all render node names
            # This is needed to prevent clashing of materials in a bigger scene
            all_render_related_nodes = [
                node for node in pm.ls()
                if node.type() in RENDER_RELATED_NODE_TYPES
            ]
            for node in all_render_related_nodes:
                if node.referenceFile() is None and \
                   node.name() not in READ_ONLY_NODE_NAMES:
                    node.rename('%s_%s' % (node.name(), uuid.uuid4().hex))

            # find the _pfxPolygons node
            pfx_polygons_node = pm.PyNode('kks___vegetation_pfxPolygons')

            for node in pfx_polygons_node.getChildren():
                for child_node in node.getChildren():
                    #print('processing %s' % child_node.name())
                    child_node_name = child_node.name().split('___')[-1]

                    pm.select(child_node)
                    output_filename =\
                        '%s_%s.ass' % (
                            self.version.nice_name,
                            child_node_name.replace(':', '_').replace('|', '_')
                        )

                    output_full_path = \
                        os.path.join(output_path, output_filename)

                    # run the mel command
                    pm.mel.eval(
                        export_command % {
                            'path': output_full_path.replace('\\', '/')
                        }
                    )

                    # generate an aiStandIn node and set the path
                    ass_node = auxiliary.create_arnold_stand_in(
                        path='%s.gz' % output_full_path
                    )
                    ass_tra = ass_node.getParent()

                    # parent the ass node under the current node
                    # under pfx_polygons_node
                    pm.parent(ass_tra, node)

                    # set pivots
                    rp = pm.xform(child_node, q=1, ws=1, rp=1)
                    sp = pm.xform(child_node, q=1, ws=1, sp=1)
                    # rpt = child_node.getRotatePivotTranslation()

                    pm.xform(ass_tra, ws=1, rp=rp)
                    pm.xform(ass_tra, ws=1, sp=sp)
                    # ass_tra.setRotatePivotTranslation(rpt)

                    # delete the child_node
                    pm.delete(child_node)

                    # give it the same name with the original
                    ass_tra.rename('%s' % child_node_name)

            # clean up other nodes
            pm.delete('kks___vegetation_pfxStrokes')
            pm.delete('kks___vegetation_paintableGeos')

        elif self.is_model_task(task):
            # convert all children of the root node
            # to an empty aiStandIn node
            # and save it as it is
            root_nodes = self.get_local_root_nodes()

            for root_node in root_nodes:
                for child_node in root_node.getChildren(type=pm.nt.Transform):
                    child_node_name = child_node.name()

                    rp = pm.xform(child_node, q=1, ws=1, rp=1)
                    sp = pm.xform(child_node, q=1, ws=1, sp=1)

                    pm.delete(child_node)

                    ass_node = auxiliary.create_arnold_stand_in(path='')
                    ass_tra = ass_node.getParent()
                    pm.parent(ass_tra, root_node)
                    ass_tra.rename(child_node_name)

                    # set pivots
                    pm.xform(ass_tra, ws=1, rp=rp)
                    pm.xform(ass_tra, ws=1, sp=sp)

                    # because there will be possible material assignments
                    # in look dev disable overrideShaders
                    ass_node.setAttr('overrideShaders', False)

                    # we definitely do not use light linking in our studio,
                    # which seems to create more problems then it solves.
                    ass_node.setAttr('overrideLightLinking', False)

        # convert all references to ASS
        for ref in pm.listReferences():
            ref.to_repr('ASS')
            ref.load()

        # fix an arnold bug
        for node_name in ['initialShadingGroup', 'initialParticleSE']:
            node = pm.PyNode(node_name)
            node.setAttr("ai_surface_shader", (0, 0, 0), type="float3")
            node.setAttr("ai_volume_shader", (0, 0, 0), type="float3")

        # if this is an Exterior/Interior -> Layout -> Hires task flatten it
        is_exterior_or_interior_task = self.is_exterior_or_interior_task(task)
        if is_exterior_or_interior_task:
            # and import all of the references
            all_refs = pm.listReferences()
            while len(all_refs) != 0:
                for ref in all_refs:
                    if not ref.isLoaded():
                        ref.load()
                    ref.importContents()
                all_refs = pm.listReferences()

            # assign lambert1 to all GPU nodes
            pm.sets('initialShadingGroup', e=1, fe=auxiliary.get_root_nodes())

            # now remove them from the group
            pm.sets('initialShadingGroup', e=1, rm=pm.ls())

            # and to make sure that no override is enabled
            [node.setAttr('overrideLightLinking', False)
             for node in pm.ls(type='aiStandIn')]

            # make sure motion blur is disabled
            [node.setAttr('motionBlur', False)
             for node in pm.ls(type='aiStandIn')]

            # clean up
            self.clean_up()

        # check if all aiStandIn nodes are included in
        # ArnoldStandInDefaultLightSet set
        try:
            arnold_stand_in_default_light_set = \
                pm.PyNode('ArnoldStandInDefaultLightSet')
        except pm.MayaNodeError:
            # just create it
            arnold_stand_in_default_light_set = \
                pm.createNode(
                    'objectSet',
                    name='ArnoldStandInDefaultLightSet'
                )

        pm.select(None)
        pm.sets(
            arnold_stand_in_default_light_set,
            fe=pm.ls(type='aiStandIn')
        )

        # save the scene as {{original_take}}@ASS
        # use maya
        take_name = '%s%s%s' % (
            self.base_take_name, Representation.repr_separator, 'ASS'
        )
        v = self.get_latest_repr_version(take_name)
        self.maya_env.save_as(v)

        # export the root nodes under the same file
        if is_exterior_or_interior_task:
            pm.select(auxiliary.get_root_nodes())
            pm.exportSelected(
                v.absolute_full_path,
                type='mayaAscii',
                force=True
            )

        # new scene
        pm.newFile(force=True)

        # reset show plugin shapes option
        active_panel = auxiliary.Playblaster.get_active_panel()
        pm.modelEditor(active_panel, e=1, pluginShapes=show_plugin_shapes)

    def generate_rs(self):
        """generates the RS representation of the current scene

        For Model Tasks the RS is generated over the LookDev Task because it
        is not possible to assign a material to an object inside an RS file.
        """
        # before doing anything, check if this is a look dev task
        # and export the objects from the referenced files with their current
        # shadings, then replace all of the references to RS repr and than
        # add Stand-in nodes and parent them under the referenced models

        # load necessary plugins
        try:
            pm.loadPlugin('redshift4maya')
        except RuntimeError:
            # Redshift For maya is not installed
            return

        # somehow the above check is not raising a normal Python error
        # trying different measures
        try:
            pm.pluginInfo('redshift4maya', query=True, vendor=True)
        except RuntimeError:
            # now we are sure that the plugin is not loaded
            return

        # # disable "show plugin shapes"
        # active_panel = auxiliary.Playblaster.get_active_panel()
        # show_plugin_shapes = pm.modelEditor(active_panel, q=1, pluginShapes=1)
        # pm.modelEditor(active_panel, e=1, pluginShapes=False)

        # validate the version first
        self.version = self._validate_version(self.version)

        if not os.path.exists(self.version.absolute_full_path):
            raise RuntimeError(
                "Path doesn't exists: %s" % self.version.absolute_full_path
            )
        self.open_version(self.version)

        task = self.version.task

        export_command = 'rsProxy -fp "%(path)s" -c -z -sl;'

        # calculate output path
        output_path = \
            os.path.join(self.version.absolute_path, 'Outputs/rs/')\
            .replace('\\', '/')

        # check if all references have an ASS repr first
        refs_with_no_ass_repr = []
        for ref in pm.listReferences():
            if ref.version and not ref.has_repr('RS'):
                refs_with_no_ass_repr.append(ref)

        if len(refs_with_no_ass_repr):
            raise RuntimeError(
                'Please generate the RS Representation of the references '
                'first!!!\n%s' %
                '\n'.join(map(lambda x: str(x.path), refs_with_no_ass_repr))
            )

        # from anima.dcc.mayaEnv.redshift import RedShiftTextureProcessor
        if self.is_look_dev_task(task):
            # in look dev files, we export the RS files directly from the Base
            # version and parent the resulting RS node to the parent of
            # the child node

            # load only Model references
            for ref in pm.listReferences():
                v = ref.version
                load_ref = False
                if v:
                    ref_task = v.task
                    if self.is_model_task(ref_task):
                        load_ref = True

                if load_ref:
                    ref.load()
                    ref.importContents()

            # Make all texture paths relative
            # replace all "$REPO#" from all texture paths first
            #
            # This is needed to properly render textures with any OS
            types_and_attrs = {
                'aiImage': 'filename',
                'file': 'computedFileTextureNamePattern',
                'imagePlane': 'imageName'
            }

            for node_type in types_and_attrs.keys():
                attr_name = types_and_attrs[node_type]
                for node in pm.ls(type=node_type):
                    orig_path = node.getAttr(attr_name).replace("\\", "/")
                    path = re.sub(
                        r'(\$REPO[0-9/]+)',
                        '',
                        orig_path
                    )
                    # RedShiftTextureProcessor(path).convert()

            # randomize all render node names
            # This is needed to prevent clashing of materials in a bigger scene
            # for node in pm.ls(type=RENDER_RELATED_NODE_TYPES):
            #     if node.referenceFile() is None and \
            #        node.name() not in READ_ONLY_NODE_NAMES:
            #         node.rename('%s_%s' % (node.name(), uuid.uuid4().hex))

            nodes_to_rs_files = {}

            # export all root rs files as they are
            for root_node in auxiliary.get_root_nodes():
                for child_node in root_node.getChildren():
                    # check if it is a transform node
                    if not isinstance(child_node, pm.nt.Transform):
                        continue

                    if not auxiliary.has_shape(child_node):
                        continue

                    # randomize child node name
                    child_node_name = child_node\
                        .fullPath()\
                        .replace('|', '_')\
                        .split(':')[-1]

                    child_node_full_path = child_node.fullPath()

                    pm.select(child_node)
                    child_node.rename(
                        '%s_%s' % (child_node.name(), uuid.uuid4().hex)
                    )

                    output_filename =\
                        '%s_%s.rs' % (
                            self.version.nice_name,
                            child_node_name
                        )

                    output_full_path = \
                        os.path.join(output_path, output_filename)

                    temp_full_path = \
                        tempfile.mktemp(suffix='.rs')

                    # create path
                    try:
                        os.makedirs(output_path)
                    except OSError:
                        # dir exists
                        pass

                    # run the mel command with temp file path
                    try:
                        pm.mel.eval(
                            export_command % {
                                'path': temp_full_path.replace('\\', '/')
                            }
                        )
                        # then move it to the original place
                        try:
                            shutil.move(temp_full_path, output_full_path)
                        except OSError as e:
                            # some Linux flavors don't allow move to overwrite
                            # if source and target files are under different
                            # file systems. So simply remove the target
                            # and move the source again
                            if os.name == 'posix':
                                # remove the target
                                os.remove(output_full_path)
                                # then move the file again
                                shutil.move(temp_full_path, output_full_path)

                        nodes_to_rs_files[child_node_full_path] = \
                            output_full_path
                    except pm.MelError:
                        # not exportable group
                        pass

            # reload the scene
            pm.newFile(force=True)
            self.open_version(self.version)

            # convert all references to RS
            # we are doing it a little bit early here, but we need to
            for ref in pm.listReferences():
                ref.to_repr('RS')

            all_proxies = pm.ls(type='RedshiftProxyMesh')
            for rs_proxy_node in all_proxies:
                # somehow the output of the RedshiftProxyNode is the Transform
                # node
                rs_proxy_tra = rs_proxy_node.outMesh.outputs()[0]
                full_path = rs_proxy_tra.fullPath()
                if full_path in nodes_to_rs_files:
                    proxy_file_path = nodes_to_rs_files[full_path]
                    # Repository.to_os_independent_path(
                    #     nodes_to_rs_files[full_path]
                    # )
                    rs_proxy_node.setAttr('fileName', proxy_file_path)

        elif self.is_vegetation_task(task):
            # in vegetation files, we export the RS files directly from the
            # Base version, also we use the geometry under "pfxPolygons"
            # and parent the resulting Proxy nodes to the
            # pfxPolygons
            # load all references
            for ref in pm.listReferences():
                ref.load()

            # Make all texture paths relative
            # replace all "$REPO#" from all texture paths first
            #
            # This is needed to properly render textures with any OS
            types_and_attrs = {
                'aiImage': 'filename',
                'file': 'computedFileTextureNamePattern',
                'imagePlane': 'imageName'
            }

            for node_type in types_and_attrs.keys():
                attr_name = types_and_attrs[node_type]
                for node in pm.ls(type=node_type):
                    orig_path = node.getAttr(attr_name).replace("\\", "/")
                    path = re.sub(
                        r'(\$REPO[0-9/]+)',
                        '',
                        orig_path
                    )
                    # RedShiftTextureProcessor(path).convert()

            # import shaders that are referenced to this scene
            # there is only one reference in the vegetation task and this is
            # the shader scene
            for ref in pm.listReferences():
                ref.importContents()

            # randomize all render node names
            # This is needed to prevent clashing of materials in a bigger scene
            # all_render_related_nodes = [
            #     node for node in pm.ls()
            #     if node.type() in RENDER_RELATED_NODE_TYPES
            # ]
            # for node in all_render_related_nodes:
            #     if node.referenceFile() is None and \
            #        node.name() not in READ_ONLY_NODE_NAMES:
            #         node.rename('%s_%s' % (node.name(), uuid.uuid4().hex))

            # find the _pfxPolygons node
            try:
                pfx_polygons_node = pm.PyNode('kks___vegetation_pfxPolygons')
                pfx_polygons_node_children = pfx_polygons_node.getChildren()
            except pm.MayaNodeError:
                pfx_polygons_node_children = []

            for node in pfx_polygons_node_children:
                for child_node in node.getChildren():
                    # print('processing %s' % child_node.name())
                    child_node_name = child_node.name().split('___')[-1]

                    pm.select(child_node)
                    output_filename =\
                        '%s_%s.rs' % (
                            self.version.nice_name,
                            child_node_name.replace(':', '_').replace('|', '_')
                        )

                    output_full_path = \
                        os.path.join(output_path, output_filename)

                    # create path
                    try:
                        os.makedirs(os.path.dirname(output_full_path))
                    except OSError:
                        # dir exists
                        pass

                    # run the mel command
                    pm.mel.eval(
                        export_command % {
                            'path': output_full_path.replace('\\', '/')
                        }
                    )

                    # generate an aiStandIn node and set the path
                    rs_proxy_mesh_node, rs_proxy_mesh_shape = \
                        auxiliary.create_rs_proxy_node(path=output_full_path)
                    rs_proxy_tra = rs_proxy_mesh_shape.getParent()

                    # parent the rs_proxy_mesh_shape under the current node
                    # under pfx_polygons_node
                    pm.parent(rs_proxy_tra, node)

                    # set pivots
                    rp = pm.xform(child_node, q=1, ws=1, rp=1)
                    sp = pm.xform(child_node, q=1, ws=1, sp=1)
                    # rpt = child_node.getRotatePivotTranslation()

                    pm.xform(rs_proxy_tra, ws=1, rp=rp)
                    pm.xform(rs_proxy_tra, ws=1, sp=sp)
                    # rs_proxy_node.setRotatePivotTranslation(rpt)

                    # delete the child_node
                    pm.delete(child_node)

                    # give it the same name with the original
                    rs_proxy_tra.rename('%s' % child_node_name)

                    # set the drawing overrides
                    rs_proxy_tra.overrideEnabled.set(1)
                    rs_proxy_tra.overrideShading.set(0)

            # clean up other nodes
            try:
                pm.delete('kks___vegetation_pfxStrokes')
            except pm.MayaNodeError:
                pass

            try:
                pm.delete('kks___vegetation_paintableGeos')
            except pm.MayaNodeError:
                pass

        elif self.is_model_task(task):
            # convert all children of the root node
            # to an empty rs node
            # and save it as it is
            root_nodes = self.get_local_root_nodes()

            for root_node in root_nodes:
                for child_node in root_node.getChildren(type=pm.nt.Transform):
                    child_node_name = child_node.name()

                    rp = pm.xform(child_node, q=1, ws=1, rp=1)
                    sp = pm.xform(child_node, q=1, ws=1, sp=1)

                    pm.delete(child_node)

                    rs_proxy_node, rs_proxy_mesh = \
                        auxiliary.create_rs_proxy_node(path='')
                    rs_proxy_tra = rs_proxy_mesh.getParent()
                    pm.parent(rs_proxy_tra, root_node)
                    rs_proxy_tra.rename(child_node_name)

                    # set pivots
                    pm.xform(rs_proxy_tra, ws=1, rp=rp)
                    pm.xform(rs_proxy_tra, ws=1, sp=sp)

                    # set the drawing overrides
                    rs_proxy_tra.overrideEnabled.set(1)
                    rs_proxy_tra.overrideShading.set(0)

        # convert all references to RS
        for ref in pm.listReferences():
            ref.to_repr('RS')
            ref.load()

        # if this is an Exterior/Interior -> Layout -> Hires task flatten it
        is_exterior_or_interior_task = self.is_exterior_or_interior_task(task)
        if is_exterior_or_interior_task:
            # and import all of the references
            all_refs = pm.listReferences()
            while len(all_refs) != 0:
                for ref in all_refs:
                    if not ref.isLoaded():
                        ref.load()
                    ref.importContents()
                all_refs = pm.listReferences()

            # assign lambert1 to all RS nodes
            pm.sets('initialShadingGroup', e=1, fe=auxiliary.get_root_nodes())

            # # now remove them from the group
            # pm.sets('initialShadingGroup', e=1, rm=pm.ls())

            # clean up
            self.clean_up()

        # save the scene as {{original_take}}@ASS
        # use maya
        take_name = '%s%s%s' % (
            self.base_take_name, Representation.repr_separator, 'RS'
        )
        v = self.get_latest_repr_version(take_name)
        self.maya_env.save_as(v)

        # export the root nodes under the same file
        if is_exterior_or_interior_task:
            pm.select(auxiliary.get_root_nodes())
            pm.exportSelected(
                v.absolute_full_path,
                type='mayaAscii',
                force=True
            )

        # new scene
        pm.newFile(force=True)
