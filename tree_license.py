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


def insert_license(file_text, ext, license_text):
    if ext == 'css':
        return f'{license_text}{file_text}'

    file_text = file_text.split('\n')
    if ext in ('sh', 'py'):
        insert_line = 0
        for line, text in enumerate(file_text):
            if '#!' in text:
                insert_line = line + 1
                file_text = '\n'.join(file_text[:insert_line]
                                      .append(license_text).extend(file_text))
                return file_text

    if ext == 'html':
        for line, text in enumerate(file_text):
            head_tag = '<head>'
            head_pos = text.find(head_tag)
            if head_pos >= 0:
                insert_pos = head_pos + len(head_tag)
                text = f'{text[:insert_pos]}{license_text}{text[insert_pos:]}'
                file_text[line] = text
                return '\n'.join(file_text)


def process_file(file_path, license_path, log_path, project_path):
    with open(file_path, 'rw') as f:
        file_name = os.path.basename(file_path)
        file_text = f.read()

        license_signs = (f'File: {file_name}', f'Project: {project_path}')
        if all(sign in file_text for sign in license_signs):
            return 0
        _, ext = os.path.splitext(file_name)
        license_text = render_license(license_path, file_name, project_path)
        file_text = insert_license(file_text, ext, license_text)
        f.write(file_text)
        with open(log_path, 'a+') as log:
            log.write(file_path)
        return 1


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
    updated_files = 0
    for _, __, files in os.walk(project_path):
        for file in files:
            updated_files += process_file(file, license_path, log_path, project_path)

    print(f'Total files updated: {updated_files}')
    with open(log_path, 'r') as log:
        print('Updated files:')
        print(log.read())

if __name__ == '__main__':
    process_project()
