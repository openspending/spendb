import requests
import json
import sys
import os


def grab_source(url, output):
    """
    Grab a source from a url and store it in an output file

    This creates uses requests as a dependency because I'm lazy.
    It probably would have taken me less time to just write it with
    urllib than writing this docstring
    """

    # We use stream because these files might be huge
    response = requests.get(url, stream=True)

    # We don't do anything if there's something wrong with the url
    # This is basically what made urllib.urlretrieve a hassle
    if not response.ok:
        return

    with open(output, 'w') as output_file:
        for block in response.iter_content(1024):
            output_file.write(block)


def archive(directory):
    """
    Archive a OpenSpending dataset export directory
    """

    # If we accidentally pass in something that's not a directory
    # we don't do anything
    if not os.path.isdir(directory):
        return

    # Check if the directory contains a dataset.json file
    dataset = os.path.join(directory, 'dataset.json')
    if not os.path.isfile(dataset):
        return

    # Open the dataset.json file and grab the sources listed in it
    with open(dataset) as descriptor:
        data = json.load(descriptor)
        if len(data['sources']):
            # Create an archive directory because there are some
            # sources we want to grab
            archive_directory = os.path.join(directory, 'archive')
            if not os.path.exists(archive_directory):
                os.makedirs(archive_directory)            

            # Loop through sources, grab them and store in an output file
            # called <source_id>.csv
            for source in data['sources']:
                filename = '{0}.csv'.format(source['id'])
                archive_file = os.path.join(archive_directory, filename)
                grab_source(source['url'], output=archive_file)

            # If the archive directory is empty which will happen if
            # grabbing the sources failed for some reason
            if not os.listdir(archive_directory):
                os.rmdir(archive_directory)


if __name__ == "__main__":
    # Loop through each of the arguments and archive them
    for directory in sys.argv[1:]:
        archive(directory)
