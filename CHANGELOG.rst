=======
Changes
=======

0.3.0
=====

* [Max] Added 3ds Max support. It is now possible to fully use UIs like Version
  Creator through 3ds Max.

0.2.1
=====

* **Update:** Rearranged the UI modules to better organize the system.

* **Update:** ``anima.ui.models.task.TaskTreeModel`` is now loading task
  hierarchies considerably faster.

* **New:** Added item icons to ``TaskTreeView`` context menu.

* **New:** Added code that will allow the system to draw font based icons for
  ``TaskItem``\ s, but it is not working for now.

* **New:** Added preliminary support for parsing and replicating XSens Network
  Protocol.

* **New:** Added option for power users to delete versions in version_creator
  UI.

* **New:** Added ``config.py`` and ``Config`` class that expands
  ``stalker.defaults``. So no need to use ``stalker.defaults`` anymore. All the
  configuration variables are moved to ``Config`` class and can be reached with
  ``anima.defaults`` instance:

  .. code-block::

      from anima import defaults
      # Access to stalker.defaults
      print(defaults.database_engine_settings)

      # Access anima config variables and functions
      print(defaults.status_colors)

* **Update:** ``anima`` now loads considerably faster, which speeds up Maya's
  initialization process.

* **Fix:** Fixed ``time_log_dialog`` to properly fix both task statuses and
  schedule info of the given task (with the code coming from Stalker Pyramid).

* **Fix:** Fixed all ``stalker.db.session.DBSession`` imports to make the
  system compatible with ``Stalker v0.2.20+``.

* **Fix:** Fixed ``cutOut_spinBox`` maximum value to be settable bigger than
  99.


0.2.0
=====

* **Update:** Added support for Maya 2017.
* **Update:** Updated the system to work with Qt5 and PySide2.
* **New:** ``LoginDialog`` now creates a ``AuthenticationLog`` instance upon
  user login.

0.1.13.dev
==========

* **New:** Representations in Maya now also have the same pivot points of the
  objects at the base representation.

* **New:** Added option to choose which representation to reference in
  Version Creator UI.

* **Update:** Updated the implementation of the RecentFileManager to use JSON
  instead of Pickle to speed things up and do not struggle with future errors
  of handling binary data.

0.1.12
======

* **New:** Added Representations. In supporting environments (like Maya)
  Representations are accompanying versions to the original one holding
  representational data or in another word the same data in another
  representation.

  For example, a Maya scene may contain a very complex high res polygonal
  object, which can not be easily drawn in view port. It is now possible to
  create a Representation (may called GPU) that holds the same data in a
  gpuCache node. The current implementation for Maya automatically generates a
  BoudingBox representation (BBOX) a GPU (GPU) representation and an Arnold
  Stand In representation (ASS) for certain types of versions during
  publishing.

* **New:** There are now two types of publishers, one called "Pre Publisher"
  and the other called "Post Publisher". The Pre Publishers are run before
  publishing the file and the Post Publishers are run after a successful
  publish operation.

0.1.11
======

* **New:** Added **Archiver** class to help flattening a maya scene to a
  default maya project folder structure without importing the scene references.

0.1.10
======

* **New:** Added a new helper function called ``anima.env.discover_env_vars()``
  which will help loading environment variables from a file called ``env.json``
  which is placed to a path defined with ``$ANIMAPATH``.

0.1.9
=====

* **New:** Added a new helper function to ``anima.env.create_repo_vars()``
  which will create environment variables for all of the ``Repository``
  instances in the current database.

* **New:** Added a new helper function called
  ``anima.env.to_os_independent_path()`` to convert a path to a OS independent
  path, which returns a path which is using environment variables.

* **New:** Added full support to ``Representations`` for Maya.

* **New:** It is now possible to choose one of the supported representations
  for the current environment in ``version_creator`` UI and open the given
  ``version`` with the desired representation.

0.1.8
=====

* **Update:** Using the forked library of the unmaintained ``PyTimeCode``
  called ``timecode`` instead of it.

0.1.7
=====

* **New:** Implemented **Shallow Reference Update** which only updates the
  current scene without generating any new versions.

0.1.6
=====

* **New:** Organized the library structure. There is no ``pipeline`` module
  anymore, all the content of ``pipeline`` is moved to the ``anima`` (base)
  module.

0.1.5
=====

* **Extension:**

  * **New:** This is a new module, which will hold all the extensions to the
    environment classes. Its main tool is the ``anima.extension.extends``
    decorator, which makes it very easy to patch extend any classes defined
    outside of ``anima`` library.

* **Pipeline:**

  * **Env:**

    * **Update:** Renamed all ``XEnv`` classes in environment to ``X`` (MayaEnv
      to Maya ie).

    * **Maya:**

      * **New:** Added Maya.fix_reference_namespaces() tool method, which
        deeply updates reference namespaces from old format (which uses version
        number) to new format (which uses the version.nice_name). This method
        also does a deep update while doing the namespace fix. It can handle
        very complex situations. For now it seems stable.

* **Previs:**

  * **New:** Added three new classes called ``SequenceManagerExtension``,
    ``SequencerExtension`` and ``ShotExtension``. These classes are mainly for
    extending functionality of original PyMel classes by using the
    ``anima.extension.extends`` decorator.

0.1.4
=====

* **Pipeline:**

  * **New:** maya.Maya.update_versions() updates all the references no
    matter how deeply they have been referenced to the current scene. It will
    create new Versions if necessary and return them as a list of Version
    instances.

  * **Update:** ``open_()`` method in ``base.EnvironmentBase`` class renamed to
    ``open()``, thus updated all the inherited classes (Maya, Nuke, Photoshop,
    Fusion, Houdini).

  * **Update:** ``update_references_list`` in maya.Maya class is renamed to
    ``update_version_inputs`` to make it clear what it does.

  * **Update:** maya.Maya.reference() now updates the inputs of the related
    Version instance of the newly created reference. This last update greatly
    reduces cycle issues in Version.inputs attribute, which can happen if the
    reference is created with Maya class but then removed by hand and then the
    file is saved manually, in this situation the Version.inputs will not be
    updated. So with this update, when this file is referenced to another
    Version (or simply to an empty maya scene) the referenced Versions inputs
    attribute is updated.

  * **New:** Replaced Maya.check_references() with Maya.deep_reference_check(),
    now the default action is to do a deep reference check.

  * **Update:** Maya.check_references() now returns a dictionary (Reference
    Resolution Dictionary) with three keys: ['leave', 'update', 'create'] with
    a list of Version instances in each one of them (or an empty list). This
    dictionary can be modified and then passed to Maya.update_versions(), which
    in return will update or create new versions as desired.

  * **Update:** Removed EnvironmentBase.post_open() method as it was getting
    useless, also reflected this change in all the derived classes.

0.1.3.2
=======

* **Render:**

  * **Arnold:**

    * **New:** H2A now includes world space motion vector information to the
      file. Although it is not usable in current form, further work needs to be
      done to convert the world space data to camera space data.

* **Pipeline:**

 * **Fix:** Fixed the 'already maximum connection' error by closing the
   database session when the UI is closed.
 * **New:** Added a new class called RecentFilesManager to manage recent files
   in an environment internally.

0.1.3.1
=======

* **Pipeline:**

  * **Env:**

    * **Update:** The external paths are not replaced with relative paths
      anymore. Also the output file name format is following the new naming
      convention.

0.1.3
=====

* **Pipeline:**

  * **Env:**

    * **New:** Moved ``stalker.models.env.EnvironmentBase`` to
      ``anima.pipeline.env.base.EnvironmentBase``.
    * **New:** Added ``stalker.models.env.photoshop.Photoshop`` class for
      Photoshop.

  * **UI:**
  
    * **Version Creator:**

      * **Update:** Version Creator now use ``version.nice_name`` attribute to
        name the new versions.

0.1.2
=====

* **Pipeline:**

 * **UI:**

   * **General:**

     * **New:** Added icons for ZBrush, Photoshop and MudBox.

   * **Version Creator:**

     * **New:** Version creator now supports External environments through
       environmentless mode and added presets for ZBrush, Photoshop and
       Mudbox.

 * **Env:**

   * **External:**

     * **New:** Added ExternalEnv and ExternalEnvFactory classes to handle
       external environments (which doesn't support python by default). For
       now there are three external environments: Photoshop, ZBrush and
       Mudbox.

0.1.1
=====

* **Pipeline:**

  * **UI:**

    * **Version Creator:**

      * **New:** Added "Use Namespace" option to allow importing/referencing to
        root namespace especially important for maya and alembic caches.

      * **Update:** It is not possible to save a version to a container task
        any more.

0.1.0
=====

* **Pipeline:**

  * **Env:**

    * **Maya:**

      * **New:** Maya now uses the significant name for playblast file name
        and render output filename.
      * **Update:** Maya now will leave the reference load state in the same
        state as it was saved.

0.1.0.a6
========

* **Render:**

  * **Arnold:**

    * **Base85:**

        * **New:** This is a new module which is doing Arnold compatible Base85
          encoding and decoding along with the Standard and RFC1924 formats. It
          is mainly used in producing Binary data for *.ass files.

    * **H2A:**

      * **New:** This is a new module which contains necessary code to be used
        in "Houdini To Arnold" Python SOP which exports fur data (for now) to
        arnold compatible *.ass file for Houdini.

* **Pipeline:**

  * **Env:**

    * **Maya:**

      * **Fix:** Fixed Maya.export(), it is now committing the data to the
        database.

0.1.0.a5
========

* **Pipeline:**

  * **UI:**

    * **Version Creator:**

      * **New:** Version Creator now tries to allow the user to cancel login,
        but it is not completely working for now.
      * **New:** Version Creator UI is now using QTreeView to display tasks on
        demand.
      * **New:** Version Creator UI is now able to restore the ui for a deeper
        task hierarchy with not yet loaded task items in the tasks_treeView.
      * **New:** Removed the statuses_comboBox from Version Creator UI.
      * **New:** Added a new context menu to the items in the tasks_treeView
        where the user is able to go to the dependent or dependee tasks of the
        clicked item in Version Creator UI.
      * **Fix:** 'my_tasks_only_checkBox' is back with the functionality.
      * **New:** Added a new and simple search field for the tasks_treeView. It
        needs to be greatly enhanced.
      * **Fix:** The default take name is now inserted at the top of the takes
        list.
      * **New:** It is now possible to use CamelCase in take names.
      * **New:** Added a disabled 'No Dependencies' menu action for tasks with
        no dependencies or dependees.

    * **Version Updater:**

      * **Fix:** Fixed check state checking for PySide by using
        QtCore.Qt.CheckState.

  * **Env:**

    * **Maya:**

      * **New:** External files are now moved to the
        version.absolute_path/external_files folder
      * **Fix:** Fixed a bug where the references where reloaded over and over
        again when saving a new version.
      * **New:** Added support for Arnold Renderer.

    * **Nuke:**

      * **Fix:** Fixed a typo
      * **New:** Now also in Nuke, the current version is set as the parent of
        the newly created version.

    * **Houdini:**

      * **New:** Now also in Nuke, the current version is set as the parent of
        the newly created version.
      * **Fix:** The file is not saved twice to store environment variables.

0.1.0.a4
========

* **Pipeline:**

  * **UI:**

    * **Fix:** Version Creator UI now sets the statuses_comboBox to the status
      of the last version in the previous_version_tableWidget.
    * **New:** Version Creator UI now uses a QSplitter for tasks_groupBox,
      new_version_groupBox and previous_versions_groupBox which allows sizing
      of the columns.
    * **New:** Version Creator UI now shows the dependent task list in a new
      column in tasks_treeWidget.
    * **New:** Version Creator UI can now display task thumbnails through
      Stalker Pyramid server.
    * **Update:** In Version Creator UI, Version notes are now saved in
      **Version.description** attribute instead of creating a new **Note**
      instance.
    * **Utils:**

      * **New:** Added a new class called **UIFile** to manage ui files.
      * **New:** UICompiler now checks the *.ui* files against their stored md5
        checksum values to prevent unnecessary compiles of unchanged files.

  * **Utils:**

    * **New:** utils.open_browser_in_location() now selects the file if a file
      path is given.
    * **New:** Added **StalkerThumbnailCache** class, which can read thumbnails
      from Stalker Pyramid server through ``urllib2`` and cache them locally.

  * **Env:**

    * **Fix:** Houdini env is working now.
    * **Fix:** Nuke env is working now.
    * **New:** Maya env is now storing the parent version info upon save and
      updates inputs (references) of the current version properly.

0.1.0.a3
========

* **Pipeline:**

  * **UI:**

    * **Fix:** Reorganized and fixed the code that chooses between ``PySide``
      or ``PyQt4``. To choose one of the libraries, let say to choose
      ``PySide`` as the library in UI::

        # first import the code that sets the system to pyside
        from anima.pipeline.ui import SET_PYSIDE
        SET_PYSIDE()

        # then import QtCore and QtGui as follows
        from anima.pipeline.ui.lib import QtCore, QtGui

      The default library is PyQt4.
    * **Update:** **version_creator.fill_tasks_treeWidget()** now works much
      faster.
    * **Update:** **version_creator.previous_versions_tableWidget** now
      displays the icon of the created environment.

  * **Environments:**

    * **Maya:**

      * **Update:** Maya now uses the folder that the current version is saved
        as the project folder.
      * **Update:** Maya sets the fps and resolution even if it is not the
        first version in its series.

0.1.0.a2
========

* **Pipeline:**

  * **Update:** login_dialog is now working.
  * **New:** created a new UI called version_creator for creating new Versions
    from within environments
  * **New:** A new field is added to the **version_creator** UI which lets the
    user to restore the previous version from the given path.
  * **New:** Created environment class for **Fusion**.
  * **New:** Created environment class for **Maya**.

0.1.0.a1
========

* Update: Organized the folder structure
* Update: Moved all rigging scripts to ``rig`` package.
* New: Created a new package called ``pipeline``.
* Update: Converted the uiCompiler.py to a standalone script which runs with
  system python (where it is much easier to install PySide and PyQt4 with
  system package managers).
