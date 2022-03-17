import argparse
from . import name as package_name
from .service import ServiceManager
from pathlib import Path
from socket import gethostname


def _handle_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host',
                        help='Set the appropriate listening host name or address value (NOTE: must match SSL cert)',
                        dest='host',
                        default=gethostname())
    parser.add_argument('--port',
                        help='Set the appropriate listening port value',
                        dest='port',
                        default='3012')
    parser.add_argument('--ssl-dir',
                        help='Change the base directory when using SSL certificate and key files with default names',
                        dest='ssl_dir',
                        default=None)
    parser.add_argument('--cert',
                        help='Specify path for a particular SSL certificate file to use',
                        dest='cert_path',
                        default=None)
    parser.add_argument('--key',
                        help='Specify path for a particular SSL private key file to use',
                        dest='key_path',
                        default=None)
    parser.add_argument('--object-store-host',
                        help='Set hostname for connection to object store',
                        dest='obj_store_host',
                        default='minio_proxy')
    parser.add_argument('--object-store-user-secret-name',
                        help='Set name of the Docker secret containing the object store user access key',
                        dest='obj_store_access_key',
                        default=None)
    parser.add_argument('--object-store-passwd-secret-name',
                        help='Set name of the Docker secret containing the object store user secret key',
                        dest='obj_store_secret_key',
                        default=None)
    parser.add_argument('--no-object-store',
                        help='Disable object store functionality and do not try to connect to one',
                        dest='no_obj_store',
                        action='store_true',
                        default=False)
    parser.add_argument('--pycharm-remote-debug',
                        help='Activate Pycharm remote debugging support',
                        dest='pycharm_debug',
                        action='store_true')
    parser.add_argument('--pycharm-remote-debug-egg',
                        help='Set path to .egg file for Python remote debugger util',
                        dest='remote_debug_egg_path',
                        default='/pydevd-pycharm.egg')
    parser.add_argument('--remote-debug-host',
                        help='Set remote debug host to connect back to debugger',
                        dest='remote_debug_host',
                        default='host.docker.internal')
    parser.add_argument('--remote-debug-port',
                        help='Set remote debug port to connect back to debugger',
                        dest='remote_debug_port',
                        type=int,
                        default=55871)

    parser.prog = package_name
    return parser.parse_args()


def main():
    args = _handle_args()

    # Flip this here to be less confusing
    use_obj_store = not args.no_obj_store

    # Initiate a service manager WebsocketHandler implementation for primary messaging and async task loops
    service_manager = ServiceManager(listen_host=args.host, port=args.port, ssl_dir=Path(args.ssl_dir))

    # If we are set to use the object store ...
    if use_obj_store:
        # TODO: (later) manage secret handling a little better
        secrets_dir = Path('/run/secrets')
        access_key_file = None if args.obj_store_access_key is None else secrets_dir.joinpath(args.obj_store_access_key)
        secret_key_file = None if args.obj_store_secret_key is None else secrets_dir.joinpath(args.obj_store_secret_key)
        service_manager.init_object_store_dataset_manager(obj_store_host=args.obj_store_host,
                                                          access_key=access_key_file.read_text(),
                                                          secret_key=secret_key_file.read_text())

    # Setup other required async tasks
    service_manager.add_async_task(service_manager.manage_required_data_checks)

    service_manager.run()


if __name__ == '__main__':
    main()
