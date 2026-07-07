import gunicorn

gunicorn.SERVER = "InfraBox"

# Single worker keeps the in-memory JSON store consistent.
# Scale horizontally with a load balancer + shared data volume if needed later.
workers = 1
bind = "0.0.0.0:5000"
timeout = 120
