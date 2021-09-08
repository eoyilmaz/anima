# -*- coding: utf-8 -*-

#
# RESOLVE_TEMPLATE_VARS should always be deep copied
#
# import copy
# my_template_vars = copy.copy(RESOLVE_TEMPLATE_VARS)
#
RESOLVE_TEMPLATE_VAR_NAMES = [
    'Angle', 'Asp Ratio Notes', 'Associated Mattes', 'Asst Director', 'Asst Producer', 'Audio Bit Depth',
    'Audio Channels', 'Audio Dur TC', 'Audio End TC', 'Audio File Type', 'Audio FPS', 'Audio Media', 'Audio Notes',
    'Audio Offset', 'Audio Recorder', 'Audio Sample Rate', 'Audio Start TC', 'Audio TC Type', 'Aux 1', 'Aux 2', 'BG',
    'Bit Depth', 'Bit Rate', 'Cam #', 'Cam Aperture', 'Cam Asst', 'Cam Firmware', 'Cam Format', 'Cam FPS', 'Cam ID',
    'Cam Notes', 'Cam Operator', 'Cam Serial #', 'Cam TC Type', 'Cam Type', 'Camera Aperture Type',
    'Camera Manufacturer', 'CDL SAT', 'CDL SOP', 'Clip #', 'Clip Directory', 'Clip Name', 'Clip Type', 'Codec Bitrate',
    'Collaborative Update', 'Color Chart', 'Color Space Notes', 'Colorist Asst', 'Colorist Notes', 'Colorist Reviewed',
    'Colorist', 'Comments', 'Continuity Reviewed', 'Continuity', 'Convergence Adj', 'Crew Comments', 'CV',
    'Dailies Colorist', 'Data Level', 'Data Wrangler', 'Date Modified', 'Date Recorded', 'Day / Night', 'Deck Firmware',
    'Deck Serial #', 'Description', 'Dialog Duration', 'Dialog Notes', 'Dialog Starts As', 'Different Frame Rate',
    'Digital Tech', 'Director Reviewed', 'Director', 'Distance', 'DOP Reviewed', 'DOP', 'Drop Frame', 'Duration TC',
    'Edit Sizing', 'Editing Asst', 'Editor', 'EDL Clip Name', 'EDL Event Number', 'EDL Tape Number', 'Embedded Audio',
    'End Dialog TC', 'End Frame', 'End TC', 'Environment', 'Episode #', 'Episode Name', 'Eye', 'FG', 'File Name',
    'File Path', 'Filter', 'Focal Point (mm)', 'Focus Puller', 'Focus Reviewed', 'Format', 'Frame Rate', 'Frames',
    'Framing Chart', 'FSD', 'Fusion Composition', 'Gamma Notes', 'Genre', 'Good Take', 'Graded', 'Grey Chart', 'Group',
    'H-Flip', 'Has Keyframes', 'IA', 'IDT', 'Input Color Space', 'Input LUT', 'Input Sizing Preset', 'Input Sizing',
    'In', 'ISO', 'Key Grip', 'KeyKode', 'Keywords', 'Lab Roll #', 'Lens #', 'Lens Chart', 'Lens Notes', 'Lens Type',
    'Line Producer', 'Location', 'LUT 1', 'LUT 2', 'LUT 3', 'LUT Used On Set', 'LUT Used', 'Marker Keywords',
    'Marker Name', 'Marker Notes', 'Matte Nodes', 'Media Type', 'Modified', 'Mon Color Space', 'Monitor LUT', 'Move',
    'ND Filter', 'Noise Reduction', 'Out', 'PAR Notes', 'PAR', 'People', 'Post Producer', 'Producer', 'Production Asst',
    'Production Co', 'Production Name', 'Program Name', 'Project Name', 'RAW', 'Reel Name', 'Reel Number',
    'Render Codec', 'Render Resolution', 'Resolution', 'Reviewers Notes', 'Rig Inverted', 'Roll Card #', 'S3D Eye',
    'S3D Notes', 'S3D Shot', 'S3D Sync', 'Safe Area', 'Sample Rate (KHz)', 'Scene', 'Script Suprvisr', 'Send to Studio',
    'Send to', 'Sensor Area Captured', 'Sensor', 'Series #', 'Setup', 'Shared Nodes', 'Shoot Day', 'Shot During Ep',
    'Shot Type', 'Shot', 'Shutter Type', 'Shutter', 'Slate TC', 'Sound Mixer', 'Sound Reviewed', 'Sound Roll #',
    'Source Name', 'Start Dialog TC', 'Start Frame', 'Start TC', 'Subclip', 'Take', 'Time-lapse Interval',
    'Timeline Index', 'Timeline Name', 'Tone', 'Track 1', 'Track 2', 'Track 3', 'Track 4', 'Track 5', 'Track 6',
    'Track 7', 'Track 8', 'Track 9', 'Track 10', 'Track 11', 'Track 12', 'Track 13', 'Track 14', 'Track 15', 'Track 16',
    'Track 17', 'Track 18', 'Track 19', 'Track 20', 'Track Name', 'Track Number', 'Tracked', 'Unit Manager',
    'Unit Name', 'Unrendered', 'Usage', 'V-Flip', 'Version', 'VFX Grey Ball', 'VFX Markers', 'VFX Mirror Ball',
    'VFX Notes', 'VFX Shot #', 'VFX Svsr Reviewed', 'Video Codec', 'Wardrobe Reviewed', 'White Balance Tint',
    'White Point',
]
RESOLVE_TEMPLATE_VARS = dict((var, ("${%s}" % var).replace("$", "%")) for var in RESOLVE_TEMPLATE_VAR_NAMES)


def format_resolve_template(template_in, format_variables):
    """Renders the given Resolve template with the given Python dict. The
    result is always Resolve safe. Meaning that variables like "%{Clip Type}"
    will be preserved if the given ``format_variables`` doesn't alter it.

    :param str template_in: A string
    :param dict format_variables:
    :return:
    """
    return template_in.replace("{", "(").replace("}", ")s") % format_variables
