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

import os, sys, yaml, re
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
def kt():
    """
    Work on production environment
    """
    env_ubuntu()
    env.settings = 'kt'
    server_credential(env.settings)
    env.hosts = ['kt.mbi.nus.edu.sg']
    env.path = os.path.join(env.server.doc, env.project_name)
    env.wp.db_name = env.project_name
    env.wp.url = env.hosts[0] + '/'


@task
def prod():
    """
    Work on production environment
    """
    env_ubuntu()
    env.settings = 'prod'
    server_credential(env.settings)
    env.hosts = ['107.167.183.230']
    env.path = '/var/www/html'
    env.wp.db_name = env.project_name
    env.wp.url = env.hosts[0] + '/'


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
    env.path = os.path.join(env.server.doc, env.project_name)
    env.wp.url = env.hosts[0] + '/'


@task
def dev():
    """
    Development environment
    """
    env_mac()
    env.settings = 'dev'
    env.hosts = ['localhost']
    env.path = '/Users/mbikyaw/PycharmProjects/mbinfo/wordpress'
    server_credential('dev')
    env.wp.url = 'http://localhost:8083/'


@task
def download_database(use_wp=True):
    """
    Dump production database and restore into local.
    Remote and local login user must set MYSQL_USER and MYSQL_PASS properly.
    Local must already create database openfreezer;
    :return: the download file name in local.
    """
    prod()
    fn = '%(db_name)s.sql.gz' % env.wp
    if use_wp:
        with(cd(env.path)):
            print("Running export")
            run("wp db export %s.sql" % env.wp.db_name)
            run("gzip -9 %s" % env.wp.db_name)
            get(fn, fn)
            run("rm %s" % fn)
    else:
        run("mysqldump -q --user=%s --password=%s %s | gzip -9 > %s.sql.gz" %
            (env.server.mysql_root, env.server.mysql_root_pass, env.wp.db_name, env.wp.db_name))
        get(fn, fn)
        run("rm %s" % fn)
    return fn


@task
def publish_mbinfo_figure():
    """
    Zip mbinfo-figure plugin for distribution
    :return:
    """
    local('cd wordpress/wp-content/plugins; zip -q -x .git -r mbinfo-figure.zip mbinfo-figure')
    local('mv wordpress/wp-content/plugins/mbinfo-figure.zip ./')


@task
def publish_mbinfo_pinfo():
    """
    Zip mbinfo-figure plugin for distribution
    :return:
    """
    local('cd wordpress/wp-content/plugins; zip -q -X -x .git -r mbinfo-pinfo.zip mbinfo-pinfo')
    local('mv wordpress/wp-content/plugins/mbinfo-pinfo.zip ./')


@task
def publish_mbinfo_widgets():
    """
    Zip mbinfo-figure plugin for distribution
    :return:
    """
    local('cd wordpress/wp-content/plugins; zip -q -X -x .git -r mbinfo-widgets.zip mbinfo-widgets')
    local('mv wordpress/wp-content/plugins/mbinfo-widgets.zip ./')

@task
def publish_mbinfo_video():
    """
    Zip mbinfo-video plugin for distribution
    :return:
    """
    local('cd wordpress/wp-content/plugins; zip -q -X -x .git -r mbinfo-video.zip mbinfo-video')
    local('mv wordpress/wp-content/plugins/mbinfo-video.zip ./')


@task
def publish_mbinfo_frontend():
    """
    Zip mbinfo-figure plugin for distribution
    :return:
    """
    local('cd wordpress/wp-content/plugins; zip -q -x .git -r mbinfo-frontend-editor.zip mbinfo-frontend-editor')
    local('mv wordpress/wp-content/plugins/mbinfo-frontend-editor.zip ./')


@task
def install_mbinfo_figure():
    """
    Install mbinfo-figure plugin
    :return:
    """
    require('settings', provided_by=[prod, staging, dev])
    with cd(env.path):
        put('mbinfo-figure.zip', 'mbinfo-figure.zip')
        run('wp plugin install mbinfo-figure.zip --force --activate')


@task
def install_mbinfo_pinfo():
    """
    Install mbinfo-figure plugin
    :return:
    """
    require('settings', provided_by=[prod, staging, dev])
    with cd(env.path):
        put('mbinfo-pinfo.zip', 'mbinfo-pinfo.zip')
        run('wp plugin install mbinfo-pinfo.zip --force --activate')


@task
def install_mbinfo_video():
    """
    Install mbinfo-figure plugin
    :return:
    """
    require('settings', provided_by=[prod, staging, dev])
    with cd(env.path):
        put('mbinfo-video.zip', 'mbinfo-video.zip')
        run('wp plugin install mbinfo-video.zip --force --activate')


@task
def install_mbinfo_frontend():
    """
    Install mbinfo-figure plugin
    :return:
    """
    require('settings', provided_by=[prod, staging, dev])
    with cd(env.path):
        put('mbinfo-frontend-editor.zip', 'mbinfo-frontend-editor.zip')
        run('wp plugin install mbinfo-frontend-editor.zip --force --activate')


@task
def install_mbinfo_widgets():
    """
    Install mbinfo-figure plugin
    :return:
    """
    require('settings', provided_by=[prod, staging, dev])
    with cd(env.path):
        put('mbinfo-widgets.zip', 'mbinfo-widgets.zip')
        run('wp plugin install mbinfo-widgets.zip --force --activate')


@task
def deploy():
    """
    Deploy source code.
    :return:
    """
    require('settings', provided_by=[prod, staging])
    fns = ['wp-content/plugins/better-anchor-links/css/mwm-aal.css',
           'wp-content/themes/Zephyr/framework/templates/widgets/search.php',
           'wp-content/themes/Zephyr-child/functions.php',
           'wp-content/themes/Zephyr-child/page-home.php',
           'wp-content/themes/Zephyr-child/page-topic-home.php',
           'wp-content/themes/Zephyr-child/page-figure-list.php',
           'wp-content/themes/Zephyr-child/page-protein.php',
           'wp-content/themes/Zephyr-child/single-figure.php']
    for fn in fns:
        put(os.path.join('wordpress', fn), os.path.join(env.path, fn))


@task
def backup_database(fresh_download=False):
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


@task
def restore_database():
    """
    Restore database from backup
    Check out available database backups:
    gsutil ls gs://mbinfo-backup/mbinfo/db/
    :return:
    """
    download_database()
    fn = "%(db_name)s.sql" % env.wp
    local('gzip -d %s.gz' % fn)
    dev()
    with(cd(env.path)):
        run("wp db drop --yes")
        run("wp db create")
        local('mysql -q --user=%s --password=%s %s < %s' %
              (env.server.mysql_root, env.server.mysql_root_pass, env.wp.db_name, fn))
        run("wp search-replace 'http://107.167.183.230' 'http://%s' --skip-columns=guid" %
            re.sub(r"/$", '', env.wp.url))
    local('rm -f %s' % fn)


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
        apply_zephyr()
        run('wp plugin install kcite')
        run('wp plugin activate kcite')
    print('Wordpress installed.')


@task
def apply_zephyr():
    """
    Install wordpress
    :return:
    """
    require('settings', provided_by=[prod, staging, dev])
    put('./Zephyr.zip', os.path.join(env.path, 'wp-content/themes/'))
    put('./Zephyr-child.zip', os.path.join(env.path, 'wp-content/themes/'))
    with cd(env.path):
        with cd('wp-content/themes'):
            run('wp theme install Zephyr.zip')
            run('rm Zephyr.zip')
            run('wp theme install Zephyr-child.zip')
            run('rm Zephyr-child.zip')
            with cd('Zephyr/vendor/plugins/'):
                run('wp plugin install js_composer.zip')
                run('wp plugin install revslider.zip')
        run('wp theme activate Zephyr-child')
        run('wp plugin activate revslider')
    print('Zephyr theme applied.')


@task
def update_zephyr():
    """
    Install wordpress
    :return:
    """
    require('settings', provided_by=[prod, staging, dev])
    put('./Zephyr.zip', os.path.join(env.path, 'wp-content/themes/'))
    with cd(env.path):
        with cd('wp-content/themes'):
            run('wp theme install Zephyr.zip --force')
            run('rm Zephyr.zip')
    print('Zephyr theme updated.')


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


def download_source():
    """
    Download production code to local.
    :return:
    """
    require('settings', provided_by=[staging, dev])
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
      scp mbinfo.mbi.nus.edu.sg:/tmp/wordpress.sql.gz ./
    :return:
    """
    require('settings', provided_by=[prod, staging, dev])
    put('mbinfo_wordpress.zip', '%(project_name)s.zip' % env)
    run('unzip -q -o %(project_name)s.zip' % env)
    run('mv ./wordpress %(path)s' % env)
    sudo('chown -R %s:%s %s' % (env.server.user, env.server.group, env.path))
    put('wordpress.sql.gz', os.path.join(env.path,'wordpress.sql.gz'))
    with cd(env.path):
        run('chmod -R g+w wp-content/uploads/')
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
        run('wp core update')
        run('wp theme update --all')
        run('wp plugin update --all')
        if not 'mbinfo' == env.project_name:
            run("wp search-replace 'http://mbinfo.mbi.nus.edu.sg' 'http://%s.mbi.nus.edu.sg' --skip-columns=guid" %
                env.project_name)


