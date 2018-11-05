# -*- coding: utf-8 -*-
# Copyright (c) 2012-2018, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
import os
import subprocess
import tempfile
import threading
from anima.env import nukeEnv
import nuke


from anima import logger
from anima.utils import do_db_setup


def update_outputs():
    """updates outputs in the current script
    """
    do_db_setup()
    nEnv = nukeEnv.Nuke()
    version = nEnv.get_current_version()
    if version:
        nEnv.create_main_write_node(version)


def output_to_h264(write_node=None):
    """an after render function which converts the input to h264
    """
    # get the file name
    if not write_node:
        write_node = nuke.thisNode()

    file_full_path = nuke.filename(write_node)

    # add the _h264 extension to the filename
    file_name = os.path.basename(file_full_path)
    path = file_full_path[:-len(file_name)]
    file_name_wo_ext, ext = os.path.splitext(file_name)

    # split any '.' (ex: a.%04d -> [a, %04d])
    file_name_wo_ext = file_name_wo_ext.split('.')[0]
    # add _h264
    output_file_name = file_name_wo_ext + '_h264.mov'
    output_full_path = os.path.join(path, output_file_name)

    # TODO: if it is a sequence of images rename them by creating temp soft
    #       links to each frame and then use the sequence format in ffmpeg

    # run ffmpeg in a seperate thread
    t = threading.Timer(
        1.0,
        convert_to_h264,
        args=[file_full_path, output_full_path]
    )
    t.start()


def convert_to_h264(input_path, output_path):
    """converts the given input to h264
    """
    ffmpeg(**{
        'i': input_path,
        'vcodec': 'libx264',
        'b:v': '4096k',
        'o': output_path
    })


def convert_to_animated_gif(input_path, output_path):
    """converts the given input to animated gif

    :param input_path: A string of path, can have wild card characters
    :param output_path: The output path
    :return:
    """
    ffmpeg(**{
        'i': input_path,
        'vcodec': 'libx264',
        'b:v': '4096k',
        'o': output_path
    })


def ffmpeg(**kwargs):
    """a simple python wrapper for ffmpeg command
    """

    # there is only one special keyword called 'o'

    # this will raise KeyError if there is no 'o' key which is good to prevent
    # the rest to execute
    output = kwargs['o']
    kwargs.pop('o')

    # generate args
    args = ['ffmpeg']
    for key in kwargs:
        # append the flag
        args.append('-' + key)
        # append the value
        args.append(kwargs[key])
        # overwrite output
    args.append('-y')
    # append the output
    args.append(output)

    logger.debug('calling real ffmpeg with args: %s' % args)

    process = subprocess.Popen(args, stderr=subprocess.PIPE)

    # loop until process finishes and capture stderr output
    stderr_buffer = []
    while True:
        stderr = process.stderr.readline()

        if stderr == '' and process.poll() is not None:
            break

        if stderr != '':
            stderr_buffer.append(stderr)

    if process.returncode:
        # there is an error
        raise RuntimeError(stderr_buffer)

    logger.debug(stderr_buffer)
    logger.debug('process completed!')


def open_in_file_browser(path):
    """opens the file browser with the given path
    """
    import platform

    system = platform.system()

    if system == 'Windows':
        subprocess.Popen(['explorer', '/select,', path.replace('/', '\\')])
    elif system == 'Darwin':
        subprocess.Popen([
            'open', '-a', '/System/Library/CoreServices/Finder.app', path
        ])
    elif system == 'Linux':
        subprocess.Popen(['nautilus', path])


def open_node_in_file_browser(node):
    """opens the node path in filebrowser
    """
    file_full_path = nuke.filename(node)
    # get the path
    file_name = os.path.basename(file_full_path)
    path = file_full_path[:-len(file_name)]
    open_in_file_browser(path)


def open_selected_nodes_in_file_browser():
    """opens selected node in filebrowser
    """
    nodes = nuke.selectedNodes()
    for node in nodes:
        open_node_in_file_browser(node)


def create_auto_crop_writer():
    """creates a write node for every selected node, and sets the autocrop flag
    to auto crop the output for fast reading
    """
    # get selected nodes and deselect them
    nodes = nuke.selectedNodes()
    [node.setSelected(False) for node in nodes]

    write_nodes = []

    for node in nodes:
        write_node = nuke.createNode('Write')
        file_path = node['file'].value()
        filename_with_number_seq, ext = os.path.splitext(file_path)
        filename, number_seq = os.path.splitext(filename_with_number_seq)

        write_node['file'].setValue(
            filename + '_auto_cropped' + number_seq + ext
        )
        write_node['channels'].setValue('all')
        write_node['autocrop'].setValue(True)
        write_node.setXpos(node.xpos() + 100)
        write_node.setYpos(node.ypos())

        # connect it to the original node
        write_node.setInput(0, node)
        write_node.setSelected(False)

        # store the write node
        write_nodes.append(write_node)

    # connect the write nodes to afanasy if afanasy exists
    try:
        afanasy = nuke.createNode('afanasy')
        for i, node in enumerate(write_nodes):
            afanasy.setInput(i, node)
    except RuntimeError:
        pass
