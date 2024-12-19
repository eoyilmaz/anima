Anima
=====

Anima is a VFX & Animation Studio Pipeline library.

And a really good example of how to utilize
[Stalker](https://github.com/eoyilmaz/stalker) to build a pipeline on top of
it.

Anima, supplies a suit of pipeline tools for Maya, Houdini, Max, Nuke, Fusion,
Blender, DaVinci Resolve, 3DEqualizer, Motion Builder and Photoshop along side
stand alone tools.

A complete set of
[Rez packages](https://github.com/eoyilmaz/anima/tree/46-update-to-stalker-1x/src/anima/rez_packages)
are also supplied with the library so it is very easy to set the pipeline up
and running.

How To Install
--------------

The best way of utilizing Anima is to use
[Rez](https://github.com/AcademySoftwareFoundation/rez). So, set up Rez for
your workstations first and then build all the required packages under
[anima/rez_packages](https://github.com/eoyilmaz/anima/tree/46-update-to-stalker-1x/src/anima/rez_packages)
that is suitable for your studio.

Some packages like [Stalker](https://github.com/eoyilmaz/stalker) are handled
as `pip` packages with `rez-pip`. To install them in to your rez packages run
the following:

```shell
for python_version in "3.8" "3.9" "3.10" "3.11" "3.12" "3.13" ;
do
    for package in "stalker" "exifread" "qtawesome" "qtpy" ;
    do
        rez-pip --install --python-version $python_version $package
    done
done
```

Update the list of Python versions according to your needs.

As Anima uses [Stalker](https://github.com/eoyilmaz/stalker) under the hood, a
PostgreSQL database, ideally running in a database server, is needed. Stalker
can work with other databases too but the preferred database is PostgreSQL and
it is developed and tested against a PostgreSQL database.

After the database setup is done, it is better to manage your database settings
from one place by creating a `config.py` file in a location that all the
workstations and farm computers are able to read from. Currently the Rez
package for anima uses the `$HOME/Stalker_Config` as the default path for
`config.py`. You can either modify the
`rez_packages/anima/package.py` according to your needs or create a symlink at
`$HOME/Stalker_Config` to another common location that contains the
`config.py` file.

In the `config.py` file you need to enter the following configuration
variables:

```python
database_engine_settings={
    "sqlalchemy.url": "postgresql://user:password@address/db_name",
    "sqlalchemy.echo": False
}
```

After that, it is easy to utilize `anima`, for example to launch Maya with
everything is set up properly:

```shell
rez-env anima maya -- maya
```

This should launch the latest version of Maya with everything set up properly.
To run Maya with Redshift and ACES (or AgX) you can do something like this:

```shell
rez-env anima redshift aces maya -- maya
```

Then inside Maya you can start using the pipeline scripts:

```python
from anima.dcc import mayaEnv
m = mayaEnv.Maya()
```

or better:

```python
from anima.ui.scripts import maya
maya.version_dialog()
```

It is a good idea to create a `Studio` instance in your database, with all the
details needed (ex. working hours, the studio name), you can run it in Maya for
example or in anywhere that has a Python consoles:

```python
import datetime
from stalker import Studio
from stalker.db.session import DBSession
our_studio = Studio(
    name='Studio Name',
    daily_working_hours=8,
    timing_resolution=datetime.timedelta(hours=1)
)

DBSession.add(our_studio)
DBSession.commit()
```

The `daily_working_hours` and `timing_resolution` argument is needed for task
schedules if you plan using stalker as a project management tool.

You should create users:

```python
from stalker import User
user1 = User(
    name='Erkan Ozgur Yilmaz',
    login='eoyilmaz',
    password='my_secret_password',
    email='eoyilmaz@my_studio.com'
)
DBSession.add(user1)
DBSession.commit()
```

And then you need to create `Projects` and `Tasks` etc. but lets do them later
after you successfully come to this stage.

These should be enough to kick start your pipeline.
