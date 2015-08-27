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

import os, sys, yaml
import time
from fabric.api import *
from fabric.contrib import files
from utils import AttributeDict

env.hosts = ['localhost']

env.project_name = 'mbinfo'
env.path = os.getcwd()
env.servers = yaml.load(file(os.path.expanduser('~/.servers.yaml'), 'r'))

env.server = AttributeDict({
    'doc': '/var/www/html/',
    'user': 'www-data',
    'group': 'www-data',
    'db_host': 'localhost',
    'mysql_root': '',
    'mysql_root_pass': '',
    'mysql_user': '',
    'mysql_user_pass': ''
})
env.wp = AttributeDict({
    'url': 'http://localhost',
    'title': 'MBInfo',
    'admin_email': 'kyaw@mechanobio.info',
    'db_name': env.project_name,
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


def env_ubuntu():
    """
    Set OS X environment
    :return:
    """
    env.server.doc = '/var/www/html'
    env.server.user = 'mbikyaw'
    env.server.group = 'www-data'


def apply_def_setup():
    """
    Apply default WordPress settings base on base configuration.
    :return:
    """
    env.path = os.path.join(env.server.doc, env.project_name)
    env.wp.url = env.hosts[0] + '/' + env.project_name + '/'


def server_credential(ev='prod'):
    """
    Set MYSQL credential
    :param env:
    :return:
    """
    env.server.mysql_root = env.servers[ev]['mysql_root']
    env.server.mysql_root_pass = env.servers[ev]['mysql_root_pass']
    env.server.mysql_user = env.servers[ev]['mysql_user']
    env.server.mysql_user_pass = env.servers[ev]['mysql_user_pass']
    env.wp.wp_admin = env.servers[ev]['wp_admin']
    env.wp.wp_admin_pass = env.servers[ev]['wp_admin_pass']


@task
def prod():
    """
    Work on production environment
    """
    env_mac()
    env.settings = 'prod'
    server_credential(env.settings)
    env.hosts = ['mbinfo.mbi.nus.edu.sg']
    env.path = os.path.join(env.server.doc, env.project_name)
    env.wp.db_name = 'wordpress'
    apply_def_setup()

@task
def staging(name='kt-w1'):
    """
    Work on staging environment
    :param name subdomain name
    """
    env.settings = 'staging'
    env.project_name = name
    env.hosts = ['kt.mbi.nus.edu.sg']
    server_credential(env.settings)
    env_ubuntu()
    env.wp.db_name = env.project_name
    apply_def_setup()


@task
def dev():
    """
    Development environment
    """
    env_mac()
    env.settings = 'dev'
    env.hosts = ['localhost']
    server_credential('dev')


@task
def download_database():
    """
    Dump production database and restore into local.
    Remote and local login user must set MYSQL_USER and MYSQL_PASS properly.
    Local must already create database openfreezer;
    :return: the download file name in local.
    """
    prod()
    run("mysqldump  --user=%s --password=%s %s | gzip -9 > /tmp/%s.sql.gz" %
        (env.server.mysql_root, env.server.mysql_root_pass, env.wp.db_name, env.wp.db_name))
    fn = '%(db_name)s.sql.gz' % env.wp
    get("/tmp/%(db_name)s.sql.gz" % env.wp, fn)
    run("rm /tmp/%(db_name)s.sql.gz" % env.wp)
    return fn


@task
def backup_database(fresh_download=True):
    """
    Backup production database
    Require Google gcloud command line auth setup.
    :return:
    """
    if not fresh_download:
        download_database()
    local("gsutil cp %s.sql.gz gs://%s/%s/db/%s-%s.sql.gz" % (env.wp.db_name, env.backup_bucket, env.project_name,
                                                              env.wp.db_name, time.strftime("%Y%m%d")))
    run("rm %(db_name)s.sql.gz" % env.wp)


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


@task
def clone_production_to_staging():
    """
    Clone production web site to local
    """
    prod()
    download_source()
    prev_pn = env.project_name
    staging()
    local("mv %s.zip %s.zip" %(prev_pn, env.project_name))
    restore_source()


@task
def setup_virtual_host(name):
    """
    Setup virtual host
    :param name: name of virtual host
    """
    require('settings', provided_by=[prod, staging, dev])
    doc = os.path.join(env.server.doc, name)
    context = {
        'port': 80,
        'server_name': name + '.mbi.nus.edu.sg',
        'document_root': doc
    }
    conf_fn = name + '.conf'
    files.upload_template('vhost.conf.template', '/etc/apache2/sites-available/' + conf_fn, context, use_sudo=True)
    run('mkdir -p %s' % doc)
    sudo("a2ensite %s" % conf_fn)
    sudo('service apache2 restart')

"""
Utilities
"""


def wp_cli():
    """
    Install WP-CLI, if necessary
    :param host:
    :return:
    """
    wp = run('which wp')
    if wp is None:
        print('Installing WP-CLI...')
        with cd('/tmp/'):
            run('curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar')
            run('chmod +x wp-cli.phar')
            sudo('mv wp-cli.phar /usr/local/bin/wp')
        print('Installed.')


@task
def install_wordpress():
    """
    Install wordpress
    :return:
    """
    require('settings', provided_by=[prod, staging, dev])
    wp_cli()
    run("mkdir -p %(path)s" % env)
    with cd(env.path):
        run('wp core download --locale=en_GB')
        run('wp core config --dbname=%s --dbuser=%s --dbpass=%s --dbprefix=%s'
            % (env.wp.db_name, env.server.mysql_user, env.server.mysql_user_pass, env.wp.dbprefix))
        run('wp db create')
        run("wp core install --url=%(url)s --title=%(title)s --admin_user=%(wp_admin)s "
            "--admin_password=%(wp_admin_pass)s --admin_email=%(admin_email)s" % env.wp)
        with cd('wp-content/themes'):
            put('Zephyr.zip', './')
            run('wp theme install Zephyr.zip')
            run('rm Zephyr.zip')
            put('Zephyr-child.zip', './')
            run('wp theme install Zephyr-child.zip')
            run('rm Zephyr-child.zip')
            with cd('Zephyr/vendor/plugins/'):
                run('wp plugin install js_composer.zip')
                run('wp plugin install revslider.zip')
        run('wp theme activate Zephyr-child')
        run('wp plugin activate revslider')
        run('wp plugin install kcite')
        run('wp plugin activate kcite')
    print('Wordpress installed.')


@task
def shiva_wordpress():
    """
    Destroy wordpress install
    :return:
    """
    require('settings', provided_by=[prod, staging, dev])
    with cd(env.path):
        if files.exists('wp-config.php'):
            run('wp db drop')
    run("rm -rf %(path)s" % env)


@task
def download_source():
    """
    Download remote source code to local.
    :return:
    """
    require('settings', provided_by=[prod, staging, dev])
    run("rm -f /tmp/%(project_name)s.zip && zip -r /tmp/%(project_name)s.zip %(path)s" % env)
    with cd(env.path):
        run()
    get("/tmp/%(project_name)s.zip" % env, "./%(project_name)s.zip" % env)
    run('rm -f /tmp/%(project_name)s.zip' % env)


@task
def restore_source():
    """
    Deploy prebuild source code to server.
    :return:
    """
    require('settings', provided_by=[prod, staging, dev])
    put('%(project_name)s.zip' % env, '%(path)s/%(project_name)s.zip', env)
    with cd(env.path):
        run('unzip -o ./%(project_name)s.zip' % env)


@task
def deploy_mbinfo_from_mac():
    """
    Deploy prebuild source code to server.

    Download source:
      cd ~/Sites
      zip -r /tmp/mbinfo_wordpress.zip wordpress
      mysqldump  --user=root --password=wordpressmbi wordpress | gzip -9 > /tmp/wordpress.sql.gz
      scp wordpress@mbinfo.mbi.nus.edu.sg:/tmp/mbinfo_wordpress.zip ./
      cp mbinfo.mbi.nus.edu.sg:/tmp/wordpress.sql.gz ./
    :return:
    """
    require('settings', provided_by=[prod, staging, dev])
    put('mbinfo_wordpress.zip', '%(project_name)s.zip' % env)
    run('unzip -q -o %(project_name)s.zip' % env)
    run('mv wordpress %(path)s' % env)
    put('wordpress.sql.gz', os.path.join(env.path,'wordpress.sql.gz'))
    with cd(env.path):
        # change db name
        run('sed -i "s/%s/%s/" wp-config.php' % ("'DB_NAME', 'wordpress", "'DB_NAME', '" + env.wp.db_name))
        run('sed -i "s/%s/%s/" wp-config.php' % ("'DB_USER', 'wordpress", "'DB_USER', '" + env.server.mysql_user))
        run('sed -i "s/%s/%s/" wp-config.php' % ("'DB_PASSWORD', 'wordpressmbi",
                                                 "'DB_PASSWORD', '" + env.server.mysql_user_pass))
        run('gzip -d wordpress.sql.gz')
        run('wp db create')
        run('wp db import wordpress.sql')
        run('rm wordpress.sql')
        run('wp option set siteurl %s' % env.wp.url)
        run('wp option set home %s' % env.wp.url)
        run("wp search-replace 'http://mbinfo.mbi.nus.edu.sg' 'http://%s.mbi.nus.edu.sg' --skip-columns=guid" %
            env.project_name)


