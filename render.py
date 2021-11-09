import click


@click.command()
@click.argument('license_path', required=True, type=click.Path(exists=True))
@click.option('--filename', default='')
@click.option('--root_folder', default='')
@click.option('--year', default='')
@click.option('--org_name', default='')
def render(**kwargs):
    license_path = kwargs.pop('license_path')
    with open(license_path) as lic_file:
        lic_text = lic_file.read()

    for field, value in kwargs.items():
        lic_text = lic_text.replace(f'${{{field}}}', value)
    print(lic_text)


if __name__ == '__main__':
    render()
