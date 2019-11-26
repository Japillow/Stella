def read_websites(file_path):
    """Returns a list of [url, check_interval] for each website."""
    with open(file_path, 'r') as file_handle:
        return [site_url.strip('\n').split(' ') for site_url in file_handle.readlines()]
