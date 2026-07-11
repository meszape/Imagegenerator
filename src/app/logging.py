import json, logging, sys
class JsonFormatter(logging.Formatter):
    def format(self, record):
        data={'level':record.levelname,'logger':record.name,'message':record.getMessage()}
        for k in ('session_id','turn_id','provider','model','safety_profile','latency_ms','result_status'):
            if hasattr(record,k): data[k]=getattr(record,k)
        return json.dumps(data, default=str)
def configure_logging(level:str='INFO')->None:
    handler=logging.StreamHandler(sys.stdout); handler.setFormatter(JsonFormatter())
    root=logging.getLogger(); root.handlers.clear(); root.addHandler(handler); root.setLevel(level)
def get_logger(name:str): return logging.getLogger(name)
