# Dreem project — backend
This is my Dreem application's work. It's working, although all the optional tasks are not fulfilled.
Please see the [Progress](#Progress) section for details. I chose to focus on having this project running
almost out-of-the-box rather than polishing non-viable code.

> Shipping beats perfection.

You will need __Docker__ and __Docker Compose__ to use it. I developped on __Ubuntu 16.04 LTS__ and I have
Docker `18.03.1-ce` and Docker Compose `1.16.1` installed.

## Progress
| Task | Progression |
| --- | --- |
| **Access API** | ✓ |
| **Signal access endpoint** | ✓ |
| **Scheduled task** | ✓ |
| **User permission layer** | ✓ |
| Minimum frontend | |
| Route filters | |
| Unit tests | ✓ |
| Asynchronous task pipeline monitor | |
| Dockerfile | ✓ |

I selected a small number of fields to save into the database. There is no doubt that the records
contain many more. Here are the selected fields:
~~~RAW
start_time, sleep_start_time, sleep_stop_time, stop_time, sleep_score, number_of_stimulations, 
number_of_wake, user, device, dreempy_version, reporting's dreemnogram
~~~

## Architecture choices
There are three actors in this project. The first one is a **MySQL database**, which stores the 
records' data, users and devices. Then comes the **REST API**, which provides an access to
the latters. Finally is the **Collector**, which collects and processes the nightly records.

To save time, I chose to keep the **Django embedded development webserver** to serve the API, and to
have the Collector making **polling** on the disk to discover the new records.

### Tools
I used Docker and Docker Compose. See the [Docker section](#docker-whale) for details.

### Authentication and permissions
I used Django default authentication and permissions layer. Here are the permissions I gave:

| Access level | permissions |
| --- | --- |
| Anonymous | Nothing |
| User | Read access to everything but users. |
| Administrator | Read access to everything. |

### Database
I chose MySQL because it's the one I know the best that fits the needs.

### H5 files
I did not know about this file format, after a few searches I used the Python [h5py](http://docs.h5py.org/en/latest/index.html) library.

## Remaining work
:clock730: It would be nice to have in the future:
* a production-capable webserver, such as **Apache** or **Nginx**;
* a dedicated DB account for the backend application, with appropriate rights;
* a configuration file to share credentials.

:alarm_clock: If I had more time, I would have:
* turned off debugging (and performed related tests);
* parsed all the remaining fields from the h5 record files;
* improved the hypnogram storage format so it can be queried right from the database;
* created archives to move the processed records;
* improved the collector's script so it can work concurrently to other instances of itself;
* added a rotating logging feature;
* added a full set of API integration tests.

## Docker :whale:
The architecture works with **three Docker images**.

First comes the database image, which is a regular MySQL image (`mysql:5.7`). It is configured
directly from the `docker-compose.yml` file, using environment variables.
Then comes the API image, which is a custom image made from an Alpine base with Python
(`python:3.6.3-alpine3.7`). Alpine distribution is light and builds fast. It is a good choice to
build sharp and efficient Docker images. Is it extended with Django and Django Framework.
Finally comes the Collector's image, which is based on the previous one. The Collector uses the Django
shell, so it requires the same dependencies as the API. The image is extended with the H5PY
library, for H5 file management.

### MySQL database
Nothing distinctive. All the configuration is made in `docker-compose.yml`. To keep things simple
MySQL is configured with the only `root` user. A Docker named volume is used to save its data between
two `make up` commands.

### API
The API is running on the Django development web server. Its container shares the port `8000` with
the host to allow the use a of browser on [http://localhost:8000](http://localhost:8000).

### Collector
The collector's job is to collect, extract and store the records' data. The one I made is pretty
simple. It runs within Django, but on a dedicated server (with a shared volume).
It is constantly **polling** the host's `dropzone/` folder, a custom directory where the client has
to **put its records**.

Once a record is detected, it is read, extracted and then its data is stored inside the MySQL database.
Finally the record is removed from the drop zone.

To watch the Collector's activity, you can watch the Docker logs during execution:
~~~SHELL
docker-compose logs -f collector
~~~

### A note on Docker Compose start
All the containers are not starting at the same speed. Usually the `api` and the `collector` are
running within a second, while `db` takes extra time to get ready. Unfortunately `db` is required
by the two other containers. In order for them to wait for the database's readiness, I used the script
called `wait-for.sh`. It makes the containers wait for the database to listen on port `3306` before
running the regular commands.

## Setup
I chose to use a _Makefile_, to ease the setup and the validation. First clone the repository,
then from a terminal run the following command:
~~~
make build && make up
~~~

The `build` target builds the Docker images (the Collector's build takes time because of `h5py`).
Then it makes the database migration scripts and runs them.

The `up` target stops and recreates the containers, in detached mode. The **database is not erased**
on `make up`. To have it reset, run `make clean` before. To get all the logs run `make logs`.

The API is available on [http://localhost:8000](http://localhost:8000).

### Tests
Tests can be run with the following command. See `DreemProject/api/tests.py` for details.
~~~SHELL
make test
~~~

Also, Pylint can be run for syntax checking. I did not get rid of the following warnings: `fixme`
(my TODOs), `too-few-public-methods`, `no-member`, `too-many-ancestors`, `import-error`.
I miss practice to solve the last three ones.

~~~SHELL
docker-compose exec api sh
pylint collector.py api/*.py
~~~

### Playing with the project
#### API
The API container have `httpie` installed, which permits to play with the API. Run the following
commands from the inside of the container (`docker-compose exec api sh`).

For the moment the database is empty, and there are no users, so every request gets rejected:
~~~SHELL
http :8000/records/
#> HTTP/1.1 403 Forbidden
~~~

You may create an admin through `manage.py`, then regular users through the API:
~~~SHELL
python manage.py createsuperuser --username admin --email admin@dreem.com
# You'll be prompted for a password.
#> Superuser created successfully.

http -a admin:[yourpassword] :8000/users/ username=user1
#> HTTP/1.1 201 Created
http -a admin:[yourpassword] :8000/users/ username=user2
#> HTTP/1.1 201 Created
http -a admin:[yourpassword] :8000/users/ username=user3
#> HTTP/1.1 201 Created
…
~~~

Now we can fetch the list of users, or only one's details:
~~~SHELL
http -a admin:[yourpassword] :8000/users/
http -a admin:[yourpassword] :8000/users/2/
~~~

See `DreemProject/api/tests.py` for details about the signal access endpoint.

#### Collector
To insert records, simply **drop** one or more H5 files into the `dropzone/` folder on your computer.
The Collector will see it within **5 seconds**, and process it.

:bulb: Note that **unregistered devices** are **inserted** by the collector into the database.

You can know query for records and devices:
~~~SHELL
http -a admin:[yourpassword] :8000/records/
http -a admin:[yourpassword] :8000/records/1/
http -a admin:[yourpassword] :8000/devices/
http -a admin:[yourpassword] :8000/devices/1/
~~~

#### MySQL
You can also dive into the database to inspect schemas and tables:

~~~SHELL
docker-compose exec db mysql -uroot -proot dreem-project
~~~

Here are the commands to list the tables, get their schema, and finally list their rows:
~~~SQL
SHOW TABLES;

DESCRIBE api_record;
DESCRIBE api_device;
-- and so on…

SELECT * FROM api_record;
-- …
~~~

Finally, to clean your computer just as if nothing happened, run `make proper` :sparkles:, then
delete the project's folder.
