import redis
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

pool = redis.ConnectionPool(host='localhost', port=6379, db=0, decode_responses=True)


class RedisDB:
    def __init__(self):
        self.client = redis.Redis(connection_pool=pool)
        
        
    def add_message(self, user_id, session_id, message):
        key = f"chat:{user_id}:{session_id}"
        try:
            message = json.dumps(message)
            self.client.rpush(key, message)
            self.client.ltrim(key,-10,-1)
            self.client.expire(key, 86400)
        except Exception as err:
            logger.error(err)
            return False
        return True
        
    def get_history(self, user_id, session_id):
        key = f"chat:{user_id}:{session_id}"
        try:
            history = self.client.lrange(key,0,-1)
            history = [json.loads(msg) for msg in history]
        except Exception as err:
            logger.error(err)
            return False
        return history
    
    def create_session(self, user_id, collection_name, session_id):
        key = f"session:{session_id}"
        try:
            self.client.hset(key, 
                             mapping={'user_id':user_id, 'collection_name': collection_name,
                                      'created_at': datetime.now().isoformat()})
            self.client.expire(key,86400)
        except Exception as err:
            logger.error(err)
            return False
        return True
    
    def get_session(self,session_id):
        key = f"session:{session_id}"
        try:
            data = self.client.hgetall(key)
        except Exception as err:
            logger.error(err)
            return False
        return data
    
    def check_rate_limit(self,user_id):
        try:
            date = datetime.now().date()
            key = f'ratelimit:{user_id}:{date}'
            count = self.client.incr(key)
            expire_at= datetime.now().replace(hour=23, minute=59,second=59)
            self.client.expireat(key , expire_at)
            return True if count > 5 else False
        
        except Exception as err:
            logger.error(err)
            return False  
        
            