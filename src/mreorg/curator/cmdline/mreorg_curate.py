#! /usr/bin/python
import argparse
import sys,os
from django.core.management import execute_from_command_line



if not 'MREORG_CONFIG' in os.environ:
    os.environ['MREORG_CONFIG'] = ''


# django internally will call this file, when files on the disk change.
# To allow this; we set a flag as an environmental variable, and
# check to see if we are 're-entering' when running the webserver:
if 'CURATION_REENTRYFLAG' in os.environ['MREORG_CONFIG']:
    print 'Rentry'
    execute_from_command_line(sys.argv)




def ensure_MREORG_REENTRY_flag_set():
    # Make sure that the 'CURATION_REENTRYFLAG' is in the list of flags:
    mreorg_config_str = os.environ.get('MREORG_CONFIG','') 
    if not 'CURATION_REENTRYFLAG' in mreorg_config_str:
        mreorg_config_str += ';CURATION_REENTRYFLAG'
    os.environ['MREORG_CONFIG'] = mreorg_config_str

def cmd_runserver(params):
    os.environ['DJANGO_SETTINGS_MODULE']='mreorg.curator.settings'

    # Make sure that the 'CURATION_REENTRYFLAG' is in the list of flags:
    ensure_MREORG_REENTRY_flag_set()

    # OK....
    #cmd = 'runserver' if not params.profile else 'runprofileserver'
    if params.profile:
        print 'Building args'
        sys.argv = [ __file__,  'runprofileserver', '%d'%params.port, ' --kcachegrind', ' --prof-path=/tmp/my-profile-data' ]
    else:
        sys.argv = [ __file__,  'runserver', '%d'%params.port]
    print sys.argv
    execute_from_command_line(sys.argv)





def cmd_runbackend(params):
    import mreorg.curator.backend_sim.simmgr_backend
    mreorg.curator.backend_sim.simmgr_backend.run_backend()


def cmd_builddb(params):
    print 'Rebuild-db'
    import mreorg
    db_filename = mreorg.MReOrgConfig.get_simulation_sqllite_filename()

    # Make sure that the 'CURATION_REENTRYFLAG' is in the list of flags:
    ensure_MREORG_REENTRY_flag_set()
    if params.rebuild:
        os.unlink(db_filename)
    if os.path.exists(db_filename):
        raise ValueError("The database already exists. Either delete it manually or use the --rebuild flag to delete the existing data")
    
    os.environ['DJANGO_SETTINGS_MODULE']='mreorg.curator.settings'
    sys.argv = [ __file__,  'syncdb']
    execute_from_command_line(sys.argv)



def cmd_backup(*args, **kwargs):
    print 'backup', args, kwargs
    assert False, 'Not Implemented yet'



def cmd_reloadconfig(params):
    os.environ['DJANGO_SETTINGS_MODULE']='mreorg.curator.settings'

    from mreorg.curator.frontend.dbdata_from_config import update_db_from_config
    update_db_from_config()




def build_parser():
    description = "mreorg.curate is tool for managing large numbers of simulations"
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_reloadconfig = subparsers.add_parser('reconfig', help='Reload the configuration from the configuration file' )
    parser_reloadconfig.set_defaults(func=cmd_reloadconfig)

    parser_runserver = subparsers.add_parser('runserver', help='run the django backend' )
    parser_runserver.add_argument('-p', '--port', type=int, default=8000, help='the port to run django on')
    parser_runserver.add_argument('--profile', action='store_true', help='profile the server using django-extensions')
    parser_runserver.set_defaults(func=cmd_runserver)


    parser_runbackend = subparsers.add_parser('runbackend', help="launch a 'backend-worker")
    parser_runbackend.set_defaults(func=cmd_runbackend)

    parser_builddb = subparsers.add_parser('builddb', help='create the database')
    parser_builddb.add_argument('-r', '--rebuild',action='store_true',  help='delete an existing database before starting')
    parser_builddb.set_defaults(func=cmd_builddb)

    parser_backup = subparsers.add_parser('backup', help='backup the existing database')
    parser_backup.set_defaults(func=cmd_backup)
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
