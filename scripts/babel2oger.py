# Convert Babel output into OGER term lists.
import json
import logging
import os.path

import click

# Set up logger.
logging.basicConfig(level=logging.INFO)


def convert_compendium(path, dirname, output):
    logging.info(f"convert_compendium({path})")

    with open(path, 'r') as f:
        for line in f:
            cluster = json.loads(line)
            identifiers = cluster['identifiers']

            # Write out the primary identifier
            primary_identifier = identifiers[0]
            output.write(
                f"{dirname}\t{os.path.basename(path)}\t{primary_identifier['i']}\t" +
                f"{primary_identifier.get('l')}\t{primary_identifier.get('l')}\t{cluster['type']}\n"
            )

            secondary_identifiers = identifiers[1:]
            for identifier in secondary_identifiers:
                output.write(
                    f"{dirname}\t{os.path.basename(path)}\t{primary_identifier['i']}\t" +
                    f"{identifier.get('l')}\t{primary_identifier.get('l')}\t{cluster['type']}\n"
                )


@click.command()
@click.option('--output', '-o', type=click.File(
    mode='w'
), default='-')
@click.option('--skip', type=str, multiple=True, default=[])
@click.argument('input', type=click.Path(
    exists=True,
    file_okay=True,
    dir_okay=True,
    allow_dash=True
))
def babel2oger(input, output, skip):
    input_path = click.format_filename(input)

    if os.path.isdir(input_path):
        # If the input path is the Babel output, then we should go down into the compendium directory.
        dirname = input_path
        compendia_dir = os.path.join(input_path, 'babel_outputs', 'compendia')
        if os.path.isdir(compendia_dir):
            input_path = compendia_dir
        iterator = os.walk(input_path, onerror=lambda err: logging.error(f'Error reading file: {err}'), followlinks=True)
        for root, dirs, files in iterator:
            for filename in files:
                if not filename.endswith('.txt'):
                    logging.debug(f"Skipping {filename}, not a .txt file.")

                flag_skip = False
                for s in skip:
                    if filename.startswith(s):
                        flag_skip = True
                        break
                if flag_skip:
                    logging.warning(f"Skipping {filename} as per `--skip` instruction")
                else:
                    convert_compendium(os.path.join(root, filename), os.path.basename(dirname), output)
    elif os.path.isfile(input_path):
        convert_compendium(input_path)
    else:
        logging.error(f"Could not open input path: {input_path}")

if __name__ == '__main__':
    babel2oger()