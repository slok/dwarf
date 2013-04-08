$(document).ready(function() {
  
  //In the template set the userId and websocketUrl

  if (userId != null){
      // push notifications stuff------------------------------------
      //connect to the socket
      var socket = io.connect(websocketUrl);
      $("#messages").append('<li>Connecting...</li>');
      

      //Redis notification receiver
      socket.on('notification', function (channel, notification) {

        notification = JSON.parse(notification);

        var options = {
          title: notification.title,
          message: notification.description,
          icon: notification.image,
          sticky: true
        };
        $.meow(options);
      });

      //Connection confirmation
      socket.on('connected', function () {
        // Send the user ID
        socket.emit('join', userId);
      });
      // End push notifications stuff---------------------------------
  }

});