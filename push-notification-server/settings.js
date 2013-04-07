var config = {};

config.redis = {};
config.web = {};
config.notifications = {};
config.socketio = {};

// this is for the push notifications
config.redis.host = '127.0.0.1';
config.redis.port = 6379;
config.redis.db = 0;

// this is for the persistance
config.redis.counter = {};
config.redis.counter.host = '127.0.0.1';
config.redis.counter.port = 6379;
config.redis.counter.db = 0;

config.web.port = process.env.WEB_PORT || 8001;

config.notifications.subscribeKey = "Push:notifications:";
config.notifications.counterKey = "Connected:clients";

config.socketio.domain = "/notifications";


module.exports = config;