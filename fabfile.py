# Fabfile for managing MBInfo WordPress web site
#
# Fab use SSH Agent forwarding for remote login. SSH login is required for all clients including local host.
#
# Require shell environment are described in shell_env_example.sh.
#
#
# To get started, type:
#
#   fab production hello
#

import os, sys
import time
from fabric.api import *
from utils import AttributeDict

env.hosts = ['localhost']

env.project_name = 'mbinfo'
env.path = os.getcwd()

env.db_host = 'localhost'
env.db_name = env.project_name
env.server = AttributeDict({
    'doc': '/var/www/httpdocs/',
    'user': 'www-data',
    'group': 'www-data'
})
env.wp = AttributeDict({
    'url': 'http://localhost',
    'title': 'MBInfo',
    'admin_email': 'admin@example.com',
    'dbname': env.project_name,
    'dbprefix': 'wp_'
})

env.wp_tarball = "https://wordpress.org/latest.tar.gz"

env.backup_bucket = 'mbinfo-backup'


@task
def hello():
    """
    Hello to login test.
    :return:
    """
    run("hostname")


"""
Environments
"""


def env_mac():
    """
    Set OS X environment
    :return:
    """
    env.server.doc = '/Library/WebServer/Documents'
    env.server.user = 'mbikyaw'
    env.server.group = 'wheel'


@task
def production():
    """
    Work on production environment
    """
    env_mac()
    env.settings = 'production'
    env.hosts = ['mbinfo.mbi.nus.edu.sg']
    env.path = os.path.join(env.server.doc, env.project_name)
    env.wp.admin_password = 'kyaw@mechanobio.info'
    env.wp.admin_email = 'kyaw@mechanobio.info'


@task
def staging():
    """
    Work on staging environment
    """
    env.settings = 'staging'
    env.hosts = ['staging.example.com']


@task
def dev():
    """
    Development environment
    """
    env_mac()
    env.settings = 'dev'
    env.hosts = ['localhost']


@task
def download_database():
    """
    Dump production database and restore into local.
    Remote and local login user must set MYSQL_USER and MYSQL_PASS properly.
    Local must already create database openfreezer;
    :return:
    """
    run("mysqldump  --user=${MYSQL_ROOT} --password=${MYSQL_ROOT_PASS} %(db_name)s | gzip -9 > "
        "/tmp/%(db_name)s.sql.gz" % env)
    get("/tmp/%(db_name)s.sql.gz" % env, './%(db_name)s.sql.gz' % env)


@task
def backup_database(fresh_download=True):
    """
    Backup production database
    Require Google gcloud command line auth setup.
    :return:
    """
    if not fresh_download:
        download_database()
    local("gsutil cp %s.sql.gz gs://%s/%s/db/%s.sql.gz" % (env.db_name, env.backup_bucket, env.project_name,
                                                           time.strftime("%Y%m%d")))


def restore_database():
    """
    Restore database from backup
    Local must already create database;
    :return:
    """
    download_database()
    local('gzip -d %(db_name)s.sql.gz' % env)
    local('mysql --user=${MYSQL_ROOT} --password=${MYSQL_ROOT_PASS} %(db_name)s < %(db_name)s.sql' % env)
    local('rm -f %(db_name)s.sql' % env)


def download_source():
    """
    Download removte source code to local.
     Local must not have any source code in 'src' folder.
    :return:
    """
    run('cd /srv/www/htdocs; zip -r /tmp/openfreezer.zip openfreezer')
    get('/tmp/openfreezer.zip', './openfreezer.zip')
    run('rm -f /tmp/openfreezer.zip')
    local('unzip ./openfreezer.zip')
    local('rm -f ./openfreezer.zip')
    local('mv openfreezer src')



"""
Utilities
"""


def wp_cli():
    """
    Install WP-CLI, if necesary
    :param host:
    :return:
    """
    wp = run('which wp')
    if wp is None:
        print('Installing WP-CLI not Implemented')
        return 1
    else:
        print('WP-CLI ' + wp)


@task
def install_wordpress():
    """
    Install wordpress
    :return:
    """
    require('settings', provided_by=[production, staging, dev])
    run("mkdir -p %(path)s" % env)
    with cd(env.path):
        run('wp core download --locale=en_GB')
        run('wp core config --dbname=%(dbname)s --dbuser=$MYSQL_USER --dbpass=$MYSQL_USER_PASS '
            '--dbprefix=%(dbprefix)s' % env.wp)
        run('wp db create')
        run("wp core install --url=%(url)s --title=%(title)s --admin_user=$WP_ADMIN "
            "--admin_password=$WP_ADMIN_PASS --admin_email=%(admin_email)s" % env.wp)
    print('Wordpress installed.')


@task
def shiva_wordpress():
    """
    Destroy wordpress install
    :return:
    """
    require('settings', provided_by=[production, staging, dev])
    run('wp db drop')
    run("rm -rf %(path)s" % env)


def get_wordpress():
    """
    Download wordpress
    :return:
    """
    require('settings', provided_by=[production, staging, dev])
    print("Downloading and installing Wordpress...")
    sudo("mkdir -p %(path)s" % env)
    with cd(env.path):
        run("curl -s %(wp_tarball)s | tar xzf -" % env)
        run('mv wordpress/* .')
        run('rmdir wordpress')
    print("Done.")


def install_plugin(name, version='latest'):
    try:
        from lxml.html import parse
        from lxml.cssselect import CSSSelector
    except ImportError:
        print("I need lxml to do this")
        exit()

    print("Looking for %s..." % name)

    url = "http://wordpress.org/extend/plugins/%s/" % name
    p = parse("%sdownload/" % url)
    sel = CSSSelector('.block-content .unmarked-list a')
    dload_elems = sel(p)

    if not dload_elems:
        print("Can't find plugin %s" % name)
        exit()

    #first is latest
    if version == 'latest':
        plugin_zip = dload_elems[0].attrib['href']
        version = dload_elems[0].text
    else:
        plugin_zip = None
        for e in dload_elems:
            if e.text == 'version':
                plugin_zip = e.attrib['href']
                break

    if not plugin_zip:
        print("Can't find plugin %s" % name)
        exit()
    else:
        print("Found version %s of %s, installing..." % (version, name) )
        with cd(env.path + "/wp-content/plugins"):
            env.run('curl -s %s -o %s.%s.zip' % (plugin_zip, name, version) )
            env.run('unzip -n %s.%s.zip' % (name, version) )

        if raw_input("Read instructions for %s? [Y|n]" % name) in ("","Y"):
            subprocess.call(['open', url])
