Anima
=====

Anima is a VFX & Animation pipeline library designed for and used in
[Anima Istanbul](http://www.animaistanbul.com) and written purely in Python.

It is also an example of how to use
[Stalker](https://github.com/eoyilmaz/stalker) and build a pipeline on top of
it.

Anima, supplies PyQt4/PySide/PySide2 UI's for Maya, Houdini, Max, Nuke, Fusion,
Blender, Motion Builder and Photoshop and the UIs can be used in standalone
mode where users can upload their files to server and automatically version
them.


How To Install
--------------

First of all, Anima uses [Stalker](https://github.com/eoyilmaz/stalker). So you
need to have a running PostgreSQL database. Stalker can work with other
databases too but the preferred database is PostgreSQL and it is developed and
tested against a PostgreSQL database.

To manage your database settings from one place, you need to create a
`config.py` file in a location that all of workstations and farm computers are
able to read from. The bad side of it is that it exposes your database user and
password. But because it is going to be seen only by the studio workers (and
only by the tech savvy ones) it should be safe.

In this `config.py` file you need to enter the following configuration
variables:

```python
database_engine_settings={
    "sqlalchemy.url": "postgresql://user:password@address/db_name",
    "sqlalchemy.echo": False
}
```

Then you need to create an environment variable called ``STALKER_PATH`` in
every computer that you want to use stalker and then set it to that path
(directory) that contains the `config.py` file. Or you can create a script per
applicationn that first sets the ``STALKER_PATH`` and other custom stuff you
might need in your studio then runs the application.

For Windows, it is a good idea to create another folder in a network storage,
copy `anima` and all of its dependencies to that folder. Then install a local
copy of the `pyscopg2` library and copy the installed `pyscopg2` files (under
python/Lib/site-packages) to that network drive again. So you do not need to
install all of the libraries for every single computer in your studio. And
update your ``PYTHONPATH`` environment variable to point to that folder.

With these steps you will be able to use:

```python
from stalker import db
db.setup()
```

instead of:

```python
from stalker import db
db.setup({"sqlalchemy.url": "....."})
```

So all of your computers will now be able to reach the database without having
too much information about the database. After that, setting up `anima` should
be pretty straight forward:

Clone `anima` to a network share so everyone can see it. Setup the `PYTHONPATH`
environment variable to include the path that contains the `anima` library.
Then you should be able to run the following inside Maya for example:

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
from stalker import db, Studio
our_studio = Studio(
    name='Studio Name',
    daily_working_hours=8,
    timing_resolution=datetime.timedelta(hours=1)  # needed for task schedules
                                                   # if you plan using
                                                   # stalker as a project
                                                   # management tool
)

db.DBSession.add(our_studio)
db.DBSession.commit()
```

You should create users:

```python
from stalker import db, User
user1 = User(
    name='User1',
    login='user1',
    password='secret',
    email='user1@users.com'
)
db.DBSession.add(user1)
db.DBSession.commit()
```

And then you need to create `Projects` and `Tasks` etc. but lets do them later
after you successfully come to this stage.

These should be enough to kick start your pipeline.
