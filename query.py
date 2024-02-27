import os
import requests
import json

LEANIX_API_TOKEN = 'MGj85GksrhvaD5YtWLdxbGcpRf9828rfaX8kKk4L'
LEANIX_SUBDOMAIN = 'https://demo-eu.leanix.net'
LEANIX_GRAPHQL_URL = f'https://demo-eu.leanix.net/services/pathfinder/v1/graphql'
LEANIX_OAUTH2_URL = f'https://demo-eu.leanix.net/services/mtm/v1/oauth2/token'


def _obtain_access_token() -> str:
    """Obtains a LeanIX Access token using the Technical User generated
    API secret.

    Returns:
        str: The LeanIX Access Token
    """
    if not LEANIX_API_TOKEN:
        raise Exception('A valid token is required')
    response = requests.post(
        LEANIX_OAUTH2_URL,
        auth=("apitoken", LEANIX_API_TOKEN),
        data={"grant_type": "client_credentials"},
    )
    response.raise_for_status()
    return response.json().get('access_token')


def main():
    """Executes a query against the LeanIX GraphQL API and prints
    the output.
    """
    access_token = _obtain_access_token()
    graphql_query = """

    {
        allFactSheets(factSheetType: ITComponent) {
            totalCount
            edges {
                node {
                    name
                }
            }
        }
    }
    relITComponentToApplications {
            edges {
              node {
                factSheet {
                  name
                  cost
                }
              }
            }
          }


    """

    data = {'query': graphql_query}
    auth_header = f'Bearer {access_token}'

    response = requests.post(
        url=LEANIX_GRAPHQL_URL,
        headers={'Authorization': auth_header},
        data=json.dumps(data)
    )
    response.raise_for_status()
    print(response.json())


if __name__ == '__main__':
    main()