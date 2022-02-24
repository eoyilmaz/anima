# -*- coding: utf-8 -*-


def export_data(node, path):
    """exports data to the given path

    :param node: current node (may be it is not necessary)
    :param str path: Output path
    """
    geo = node.geometry()
    point_positions = geo.pointFloatAttribValues("P")
    point_colors = geo.pointFloatAttribValues("Cd")

    all_data = []
    for i in range(int(len(point_positions) / 3)):
        raw_data = "%s \t%s \t%s \t%s \t%s \t%s\n" % (
            point_positions[i * 3], point_positions[i * 3 + 1], point_positions[i * 3 + 2],
            point_colors[i * 3] * 256, point_colors[i * 3 + 1] * 256, point_colors[i * 3 + 2] * 256
        )
        all_data.append(raw_data)

    with open(path, "w") as f:
        f.writelines(all_data)


def main():
    import hou

    node = hou.node(".")
    path = node.parm("path").eval()
    if not path:
        raise hou.Error("Please supply a path")

    export_data(node, path)
