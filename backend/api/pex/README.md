Each folder in /backend/api is a folder for a core component of this project.

Pex as an example, has a file for all pex_tasks that are to be run and scheduled.

It also contains pex_mongo.py that handles all special mongo operations for Pex.

In the api/pex folder, each api endpoint has it's own endpoint file like
/backend/api/pex/register.py. In this case the Pex protocol needs a function to
call that endpoint on other nodes, se we map these endpoints to functions stored
in pex_tasks to keep things simple.

