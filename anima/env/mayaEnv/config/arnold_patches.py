# -*- coding: utf-8 -*-
# Copyright (c) 2012-2017, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause


def createArnoldTextureSettings():
    """The patched version of the original file
    """
    import pymel.core as pm
    import maya.cmds as cmds
    import pymel.versions as versions
    from mtoa.ui.globals import settings

    pm.setUITemplate('attributeEditorTemplate', pushTemplate=True)
    pm.columnLayout(adjustableColumn=True)

    pm.attrControlGrp(
        'autotx',
        cc=settings.updateAutoTxSettings,
        label="Auto-convert Textures to TX (Disabled in Anima)",
        attribute='defaultArnoldRenderOptions.autotx',
        enable=False
    )

    pm.attrControlGrp('use_existing_tiled_textures',
                      label="Use Existing TX Textures",
                      attribute='defaultArnoldRenderOptions.use_existing_tiled_textures')

    # disable autotx
    pm.setAttr('defaultArnoldRenderOptions.autotx', 0)
    settings.updateAutoTxSettings()
    cmds.separator()

    # don't create texture_automip for 2017 as autoTx is ON by default
    maya_version = versions.shortName()
    if int(float(maya_version)) < 2017:
        pm.attrControlGrp('texture_automip',
                          label="Auto-mipmap",
                          attribute='defaultArnoldRenderOptions.textureAutomip')

    pm.attrControlGrp('texture_accept_unmipped',
                      label="Accept Unmipped",
                      attribute='defaultArnoldRenderOptions.textureAcceptUnmipped')

    cmds.separator()

    pm.checkBoxGrp('ts_autotile',
                   cc=settings.updateAutotileSettings,
                   label='',
                   label1='Auto-tile')

    pm.connectControl('ts_autotile', 'defaultArnoldRenderOptions.autotile',
                      index=2)

    pm.intSliderGrp('ts_texture_autotile',
                    label="Tile Size",
                    minValue=16,
                    maxValue=64,
                    fieldMinValue=16,
                    fieldMaxValue=1024
                    )

    pm.connectControl('ts_texture_autotile',
                      'defaultArnoldRenderOptions.textureAutotile', index=1)
    pm.connectControl('ts_texture_autotile',
                      'defaultArnoldRenderOptions.textureAutotile', index=2)
    pm.connectControl('ts_texture_autotile',
                      'defaultArnoldRenderOptions.textureAutotile', index=3)

    '''pm.attrControlGrp('texture_autotile',
                        label="Auto-tile Size",
                        attribute='defaultArnoldRenderOptions.textureAutotile')'''

    pm.attrControlGrp('texture_accept_untiled',
                      label="Accept Untiled",
                      attribute='defaultArnoldRenderOptions.textureAcceptUntiled')

    pm.attrControlGrp('texture_max_memory_MB',
                      label="Max Cache Size (MB)",
                      attribute='defaultArnoldRenderOptions.textureMaxMemoryMB')

    pm.attrControlGrp('texture_max_open_files',
                      label="Max Open Files",
                      attribute='defaultArnoldRenderOptions.textureMaxOpenFiles')

    cmds.separator()

    cmds.attrControlGrp('texture_diffuse_blur',
                        label="Diffuse Blur",
                        attribute='defaultArnoldRenderOptions.textureDiffuseBlur')

    # cmds.attrControlGrp('texture_glossy_blur',
    #                     label="Glossy Blur",
    #                     attribute='defaultArnoldRenderOptions.textureGlossyBlur')

    pm.setParent('..')

    pm.setUITemplate(popTemplate=True)
