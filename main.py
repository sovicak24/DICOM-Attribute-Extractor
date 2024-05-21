#! /usr/bin/env python3
# Author: MUDr. Slavomira Senkova
# Description: DICOM attribute exporter
# Licence: TOOD


import pydicom
import os
import json
import logging
import click
import tqdm
from datetime import datetime
from typing import DefaultDict
from functools import update_wrapper
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger("DAE")

log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class HexParamType(click.ParamType):
    name = "hexadecimal"

    def convert(self, value, param, ctx):
        try:
            return int(value, 16)
        except ValueError:
            self.fail(f"{value} is not a valid hexadecimal number", param, ctx)


HEX_TYPE = HexParamType()


def log_decorator(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        log.setLevel(log_levels[ctx.params["log_level"]])
        log.info("Starting DICOM attribute exporter")
        r = ctx.invoke(f, *args, **kwargs)
        log.info("Finishing")
        return r

    return update_wrapper(new_func, f)


def get_filenames(folder):
    """Get the filenames from the input_data folder

    Args:
        folder (str): The folder containing the DICOM files

    Returns:
        list: A list of filenames
    """
    filenames = list()
    for filename in os.listdir(folder):
        if filename.endswith(".dcm"):
            filenames.append("/".join([folder, filename]))
    return filenames


def find_attributes(filenames: list, attributes: list) -> dict:
    """Find the attributes in the DICOM images
    Args:
        filenames (list): A list of filenames
        attributes (list): A list of attributes to extract

    Returns:
        dict: A dictionary containing the attributes

    Example:
        filenames = ['filename']
        attributes = [attr1, attr2]

        output = {
            'filename' : {
                'attr1' : value1,
                'attr2' : value2
            }
        }
    """
    output = DefaultDict(DefaultDict)

    for filename in tqdm.tqdm(filenames):
        # Load the DICOM file
        ds = pydicom.dcmread(filename)

        def get_item(address) -> str:
            try:
                tag = ds.get_item(address)
            except AttributeError:
                print(f"Error: {filename} does not contain the required attributes")
            else:
                return tag.value.decode("utf-8")

        for attribute in attributes:
            output[filename][hex(attribute)] = get_item(hex(attribute))

    return output


@click.command()
@click.option(
    "-i",
    "--input-folder",
    help="Input folder which contains images to extract the attribute from.",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    show_default=True,
    default="./input_data",
)
@click.option(
    "-l",
    "--log-level",
    help="Set logging level.",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    show_default=True,
    default="INFO",
    envvar="LOG_LEVEL",
)
@click.option(
    "-o",
    "--output-file",
    help="Output file name",
    show_default=True,
    default="results-" + (datetime.today()).strftime("%Y-%m-%d_%H-%M-%S") + ".json",
)
@click.option(
    "-a",
    "--attribute",
    help="Which attributes to extract from DICOM images",
    type=HEX_TYPE,
    show_default=True,
    multiple=True,
    required=True,
)
@log_decorator
def main(input_folder, log_level, output_file, attribute) -> None:
    # Get filenames from input_data folder
    filenames = get_filenames(input_folder)
    attribute = tuple(set(attribute))  # Remove duplicates

    log.debug(f"Found {len(filenames)} files in {input_folder}")
    log.debug(f"Extracting attributes: {attribute}")

    # Find attributes in images
    output = find_attributes(filenames, attribute)
    log.debug(f"Found {len(output)} attributes")
    log.debug(f"Saving output to {output_file}")
    # Save JSON output
    with open(output_file, "w") as f:
        json.dump(output, f, indent=4)


if __name__ == "__main__":
    main()
