import click
import os
import subprocess


def process_file(file_path, license_path, log_path):
    shebang_str = '#!'
    with open(file_path) as f:
        filename = os.path.splitext(os.path.basename(file_path))
        file_text = f.read()


@click.command()
@click.argument('project_path', required=True, type=click.Path(exists=True))
@click.option('-f', default=None, type=click.Path(exists=True))
@click.option('-l', default=None, type=click.Path(exists=True))
def process_project(f, l, project_path):

    license_path = f if f else os.getenv('LICENSE_FILE_PATH')
    if not license_path:
        raise Exception('Missing path to license file')

    log_path = l if l else os.path.join(__file__, 'license.log')
    for _, __, files in os.walk(project_path):
        for file in files:
            process_file(file, license_path, log_path)


if __name__ == '__main__':
    process_project()
