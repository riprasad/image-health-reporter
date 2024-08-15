from typing import Any, Dict, List
import logger
import requests
import util


LOGGER = logger.getLogger(__name__)

# https://catalog.redhat.com/api/containers/v1/ui/
SERVER_URL = "https://catalog.redhat.com/api/containers/v1"
REGISTRY = "registry.access.redhat.com"



def get_repositories_and_supported_streams(product_listing_id: str) -> Dict[str, Any]:
    """
    Retrieves information about all repositories and their supported stream tags
    for a given product listing ID.
    
    The request includes the following parameters:
    - `include`: Comma-separated list of fields to include in the response.
    - `page_size`: Size of the page that should be returned.
    - `page`: Page number to return.
    """
    endpoint = f"product-listings/id/{product_listing_id}/repositories"
    url = util.construct_url(SERVER_URL, endpoint)

    headers = {"accept": "application/json"}
    
    params = {
        'include': 'data.repository,data.content_stream_tags',
        'page_size': 100,
        'page': 0
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    # Parses the JSON response from the API into a Python dictionary
    data_dict = response.json()
    
    return data_dict
    


def get_image_grades(repository: str) -> List[Dict[str, str]]:
    """
    Fetches and returns the health grade information for all images in the specified repository.
    
    The request includes the following parameters:
    - `include`: Comma-separated list of fields to include in the response.
    """
    endpoint = f"repositories/registry/{REGISTRY}/repository/{repository}/grades"
    url = util.construct_url(SERVER_URL, endpoint)

    headers = {"accept": "application/json"}
    
    params = {
        'include': 'tag,current_grade,next_drop_date'
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    # Parses the JSON response from the API into a Python List
    repository_images_grade = response.json()
    
    return repository_images_grade



def filter_supported_image_grades(image_grades: List[Dict[str, str]], supported_stream_tags: List[str]) -> List[Dict[str, str]]:
    """
    Filters and returns the image grades of supported versions.
    """
    # Create a set from content_stream_tags for efficient lookup
    tag_set = set(supported_stream_tags)
    
    # Filter image_grades based on whether the tag is in the tag_set
    supported_stream_grades = [grade for grade in image_grades if grade['tag'] in tag_set]

    return supported_stream_grades



def main():
    # TODO - Make it COnfigurable
    product_listing_id = "63b85b573112fe5a95ee9a3a"
        
    
    
    product_listing_data = get_repositories_and_supported_streams(product_listing_id)
    LOGGER.debug(f"Repository Data: {product_listing_data}")
    
    if product_listing_data.get("data"):
        
        # Retrieve the value associated with the key "data" from the dictionary.
        # The value is expected to be a list of dictionaries
        repository_data_list = product_listing_data.get("data")
        
        for grades in repository_data_list:
            repository = grades.get("repository")
            supported_stream_tags = grades.get("content_stream_tags")
            print(f"Repository: {repository}")
            print(f"Supported Stream Tags: {supported_stream_tags}")
            print()
            
            all_image_grades = get_image_grades(repository)
            LOGGER.debug(f"Health Grades For All Images In The Repository '{repository}': {all_image_grades}")
            if all_image_grades:
                supported_image_grades = filter_supported_image_grades(all_image_grades, supported_stream_tags)
                LOGGER.debug(f"Supported Image Grades For Repository '{repository}': {supported_image_grades}")
                for grades in supported_image_grades:
                    LOGGER.info(grades)
            else:
                 LOGGER.error("An error occured while fetching the health grade of the images in repository '{repository}'.")
                 raise Exception()
            
    else:
        LOGGER.error("An error occured while fetching the data for product listing id '{product_listing_id}'.")
        raise Exception()
    
    
    
    
    
if __name__ == '__main__':
    main()