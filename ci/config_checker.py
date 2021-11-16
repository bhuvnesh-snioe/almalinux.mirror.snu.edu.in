#!/usr/bin/env python3.9
import argparse
import logging
from typing import Optional

import yaml
import jsonschema
import json


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
)


class YamlFileType(argparse.FileType):

    def __call__(self, string):
        file_stream = super(YamlFileType, self).__call__(string)
        try:
            return {
                'config_path': file_stream.name,
                'config_data': yaml.safe_load(file_stream),
            }
        except yaml.YAMLError as err:
            raise argparse.ArgumentTypeError(
                f'The YAML file by path "{file_stream.name}" '
                f'is invalid because "{err}"'
            )


class JsonFileType(argparse.FileType):

    def __call__(self, string):
        file_stream = super(JsonFileType, self).__call__(string)
        try:
            return json.load(file_stream)
        except json.JSONDecodeError as err:
            raise argparse.ArgumentTypeError(
                f'The JSON file by path "{file_stream.name}" '
                f'is invalid because "{err}"'
            )


def create_parser():
    parser = argparse.ArgumentParser(
        description='The script checks validity of config (mirror or service) '
                    'schema. It checks a mirror config if you pass both '
                    'params, otherwise it checks only a service config.',
    )
    parser.add_argument(
        '-sc',
        '--service-config',
        default='config.yml',
        dest='service_config',
        help='Path to a service yaml config. Default path is ./config.yml.',
        required=True,
        type=YamlFileType('r'),
    )
    parser.add_argument(
        '-ss',
        '--service-config-json-schema',
        dest='service_config_json_schema',
        help='Path to a JSON schema of service config.',
        required=True,
        type=JsonFileType('r'),
    )
    parser.add_argument(
        '-mc',
        '--mirror-configs',
        dest='mirror_configs',
        help='A list of paths to a checked mirror config',
        default=[],
        nargs='+',
        type=YamlFileType('r'),
    )
    parser.add_argument(
        '-ms',
        '--mirror-config-json-schema',
        dest='mirror_config_json_schema',
        help='Path to a JSON schema of mirror config.',
        type=JsonFileType('r'),
    )
    return parser


def config_validation(
        config_data: dict,
        json_schema: dict,
) -> tuple[bool, Optional[str]]:
    try:
        jsonschema.validate(
            instance=config_data,
            schema=json_schema,
        )
        return True, None
    except jsonschema.ValidationError as err:
        return False, str(err)


def main(args) -> int:
    is_validity, err = config_validation(
        config_data=arguments.service_config['config_data'],
        json_schema=arguments.service_config_json_schema,
    )
    if not is_validity:
        logger.error(
            'Main config "%s" is invalid because "%s"',
            arguments.service_config['config_path'],
            err,
        )
        exit(1)
    exit_code = 0
    for mirror_config in arguments.mirror_configs:
        is_validity, err = config_validation(
            config_data=arguments.service_config['config_data'],
            json_schema=arguments.service_config_json_schema,
        )
        if not is_validity:
            logger.error(
                'The mirror config "%s" is invalid because "%s"',
                mirror_config['config_path'],
                err,
            )
            exit_code = 1
    if not exit_code:
        logger.info('All configs are valid')
    exit(exit_code)


if __name__ == '__main__':
    arguments = create_parser().parse_args()
    main(arguments)