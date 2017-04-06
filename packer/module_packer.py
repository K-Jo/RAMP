import os
import sys
import json
import zipfile
import argparse
import module_metadata
from commands_discovery import discover_modules_commands

INTRO_MSG = """
 _____       _ _     __        _          _____       _     _         
| __  |___ _| |_|___|  |   ___| |_ ___   |     |___ _| |_ _| |___ ___ 
|    -| -_| . | |_ -|  |__| .'| . |_ -|  | | | | . | . | | | | -_|_ -|
|__|__|___|___|_|___|_____|__,|___|___|  |_|_|_|___|___|___|_|___|___|

This utility will walk you through creating a Redis module package file.
It only covers the most common items, and tries to guess sensible defaults.

See `module_packer help json` for definitive documentation on these fields
and exactly what they do.

Press ^C at any time to quit."""

def setup_arg_parser():
    """
    Initialize cmd args parser
    """
    arg_parser = argparse.ArgumentParser(description='Create a new module package')
    arg_parser.add_argument('-a','--author', dest='author', default=module_metadata.AUTHOR, help='module author')
    arg_parser.add_argument('-e','--email', dest='email', default=module_metadata.EMAIL, help='author\'s email')
    arg_parser.add_argument('-ar','--architecture', dest='architecture', default=module_metadata.ARCHITECTURE, help='module compiled on 32/64 bits arch')
    arg_parser.add_argument('-d','--description', dest='description', default=module_metadata.DESCRIPTION, help='short description')
    arg_parser.add_argument('-ho','--homepage', dest='homepage', default=module_metadata.HOMEPAGE, help='module homepage')
    arg_parser.add_argument('-l','--license', dest='license', default=module_metadata.LICENSE, help='license')
    arg_parser.add_argument('-ex','--extras', dest='extra_files', default=module_metadata.EXTRA_FILES, help='extra files')
    arg_parser.add_argument('-c','--cmdargs', dest='command_line_args', default=module_metadata.COMMAND_LINE_ARGS, help='module command line arguments')
    arg_parser.add_argument('-r', '--redis-min-version', dest='redis_min_version', default=module_metadata.MIN_REDIS_VERSION, help='redis minimum version')
    arg_parser.add_argument('-rl', '--rlec-min-version', dest='rlec_min_version', default=module_metadata.MIN_RLEC_VERSION, help='rlec minimum version')
    # TODO: add param (-o) to specify package location.
    return arg_parser

def set_defaults(module_path):
    """
    Creates a module metadata using default values
    """
    metadata = module_metadata.create_default_metadata(module_path)
    return metadata

def update_metadata_module_info(metadata, module):
    """
    Sets metadata with module internal attributes
    """
    metadata["module_name"] = module.name
    metadata["version"] = module.version
    metadata["commands"] = [cmd.to_dict() for cmd in module.commands]

def interactive_mode(metadata):
    """
    Creates module metadata from user provided input
    """
    print INTRO_MSG
    user_input = raw_input("Architecture:{} ".format(module_metadata.ARCHITECTURE))
    if user_input is not "":
        metadata["architecture"] = int(user_input)

    user_input = raw_input("Author: ")
    if user_input is not "":
        metadata["author"] = user_input

    user_input = raw_input("Email: ")
    if user_input is not "":
        metadata["email"] = user_input

    user_input = raw_input("Description:{} ".format(module_metadata.DESCRIPTION))
    if user_input is not "":
        metadata["description"] = user_input

    user_input = raw_input("Homepage:{} ".format(module_metadata.HOMEPAGE))
    if user_input is not "":
        metadata["homepage"] = user_input

    user_input = raw_input("License:{} ".format(module_metadata.LICENSE))
    if user_input is not "":
        metadata["license"] = user_input

    user_input = raw_input("Extra files:{} ".format(module_metadata.EXTRA_FILES))
    if user_input is not "":
        metadata["extra_files"] = user_input

    user_input = raw_input("Command line args:{} ".format(module_metadata.COMMAND_LINE_ARGS))
    if user_input is not "":
        metadata["command_line_args"] = user_input

    user_input = raw_input("Min redis version:{} ".format(module_metadata.MIN_REDIS_VERSION))
    if user_input is not "":
        metadata["min_redis_version"] = user_input

    user_input = raw_input("Min rlec version:{} ".format(module_metadata.MIN_RLEC_VERSION))
    if user_input is not "":
        metadata["min_rlec_version"] = user_input

def cmd_mode(metadata, argv):
    """
    Create module metadata from command line arguments
    """
    arg_parser = setup_arg_parser()
    args = arg_parser.parse_args(argv)

    metadata["architecture"] = int(args.architecture)
    metadata["author"] = args.author
    metadata["email"] = args.email
    metadata["description"] = args.description
    metadata["homepage"] = args.homepage
    metadata["license"] = args.license
    metadata["extra_files"] = args.extra_files
    metadata["command_line_args"] = args.command_line_args
    metadata["min_redis_version"] = args.redis_min_version
    metadata["min_rlec_version"] = args.rlec_min_version

def archive(module_path, metadata):
    """
    Archives both module and module metadata.
    """
    with open('module.json', 'w') as outfile:
        json.dump(metadata, outfile, indent=4, sort_keys=True)

    archive_file = zipfile.ZipFile('module.zip', 'w', zipfile.ZIP_DEFLATED)
    try:
        archive_file.write(module_path, metadata["module_file"])
        archive_file.write('module.json')
        print "module.zip generated."
    finally:
        archive_file.close()
        os.remove("module.json")

def usage():
    """
    Prints usage
    """
    print "usage: module_packer.py <PATH_TO_MODULE>"

def main(argv):
    if len(argv) is 1:
        usage()
        return 1

    module_path = argv[1]
    metadata = set_defaults(module_path)

    if len(argv) is 2:
        interactive_mode(metadata)
    else:
        cmd_mode(metadata, argv[2:])

    # Load module into redis and discover its commands
    module = discover_modules_commands(module_path, metadata["command_line_args"])
    update_metadata_module_info(metadata, module)

    archive(module_path, metadata)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))