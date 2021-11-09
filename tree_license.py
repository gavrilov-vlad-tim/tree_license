import click
import os
import subprocess


def render_license(license_path, file_name='', project_path='', year='',
                   org_name=''):
    render_command = ' '.join(('./render', f'--filename={file_name}',
                               f'--root_folder={project_path}', f'--year={year}',
                               f'--org_name={org_name}', license_path))
    license_text = subprocess.check_output(render_command, shell=True).decode('utf-8')
    _, ext = os.path.splitext(file_name)
    ext_comment = {'sh': '#', 'py': '#', 'css': ('/*', '*/'),
                   'html': ('<!--', '-->')}
    comment_str = ext_comment[ext]
    if isinstance(comment_str, tuple):
        start_comment, end_comment = comment_str
        license_text = f'{start_comment}{license_text}{end_comment}'
    else:
        license_text = '\n'.join(
            f'{comment_str}{line}' for line in license_text.split('\n')
        )
    return license_text


def process_file(file_path, license_path, log_path, project_path):
    with open(file_path) as f:
        file_name = os.path.basename(file_path)
        file_text = f.read()

        license_signs = (f'File: {file_name}', f'Project: {project_path}')
        if all(sign in file_text for sign in license_signs):
            return

@click.command()
@click.argument('project_path', required=True, type=click.Path(exists=True))
@click.option('-f', default=None, type=click.Path(exists=True))
@click.option('-l', default=None, type=click.Path(exists=True))
def process_project(f, l, project_path):

    license_path = f if f else os.getenv('LICENSE_FILE_PATH')
    if not license_path:
        raise Exception('Missing path to license file')

    log_path = l
    if not l:
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'license.log')

    for _, __, files in os.walk(project_path):
        for file in files:
            process_file(file, license_path, log_path, project_path)


if __name__ == '__main__':
    process_project()
