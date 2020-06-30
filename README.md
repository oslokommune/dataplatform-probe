# dataplatform-probe
Monitoring service for dataplatform services and events

## Running
Running this app requires these environment variables to be set:

| Name                   | Description                                                 |
| ---------------------- | ----------------------------------------------------------- |
| AUTHORIZER_API         | URL to Authorizer Api                                       |
| KEYCLOAK_SERVER        | URL to the keycloak server to use                           |
| WEBSOCKET_URL          | URL to the websocket to listen to                           |
| WEBHOOK_TOKEN          | Token to use to authenticate with websocket                 |
| ORIGO_CLIENT_SECRET    | Client Secret of the keycloak client to use                 |
| ORIGO_CLIENT_ID        | Client ID of the keycloak client to use                     |
| ORIGO_ENVIRONMENT      | Which environment to run on(dev/prod)                       |
| KEYCLOAK_REALM         | Name of the keycloak realm to use                           |
| AWS_XRAY_SDK_ENABLED   | Whether to use AWS XRAY SDK (true/false)                    |
| EVENT_INTERVAL_SECONDS | Number of seconds to wait before sending an event           |

Once these environment variables are set you can
run the app with [Pipenv](https://github.com/pypa/pipenv):
1. `pipenv install`
2. `pipenv run app`

Alternatively, you can use the [run.sh](run.sh) script and simply add
in the client secrets yourself:
1. `pipenv install`
2. `pipenv run script`