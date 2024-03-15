# entrypoint.sh

#!/bin/bash

# Espere até que o banco de dados esteja pronto
wait-for-it.sh db:5432 -t 0

# Inicie o serviço web
exec "$@"
