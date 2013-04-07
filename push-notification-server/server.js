var config = require('./settings');
var io = require('socket.io').listen(config.web.port);
var redis = require("redis");

var redisCounterClient = redis.createClient(config.redis.counter.port,
                                            config.redis.counter.host);

io.of(config.socketio.domain).
on('connection', function (socket) {

    // new connection!
    console.log("New connection: " + socket.id);

    //Increment the connections
    redisCounterClient.select(config.redis.counter.db, function(err, res){
      redisCounterClient.incr(config.notifications.counterKey);
    });

    // Send the message of connection for receiving the user ID
    socket.emit('connected');

    // Receive the ID
    socket.on('join', function(userId){

      var channel = config.notifications.subscribeKey + userId;
      console.log("Connecting to redis: " + channel);

      // store in the socket our connection
      socket.redisClient = redis.createClient(config.redis.port,
                                              config.redis.host);

      socket.redisClient.select(config.redis.db, function(err, res){
        socket.redisClient.subscribe(channel);

        // subscribe to our channel (We don't need to check because we have a
        // connection per channel/user)
        socket.redisClient.on("message", function(channel, message) {
          console.log(channel + ': ' + message);
          // Send notification to the client
          socket.emit('notification', channel, message);
        });

      });

    });

    // Disconnection of the user
    socket.on('disconnect',function() {
      console.log('Client Disconnected');

      //Decrement the connections
      redisCounterClient.select(config.redis.counter.db, function(err, res){
        redisCounterClient.decr(config.notifications.counterKey);
      });

    });
});
