#!/usr/bin/env python
import server.ospath as Path

#MONGODB CONFIG
host = "mongodb://localhost"
port = 27017
db = "cdut"

#Redis CONFIG
redis_host = "localhost"
redis_port = 6379

#LOG CONFIG
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

#PATH
RootPath = Path.getRootPath()