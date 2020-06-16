var clientId = "XXX";
var client;
var speed;
var loginFlag = 0;
var options = {
    onSuccess: onConnect,
    onFailure: doFail,
    userName: "XXX",
    password: "XXX"
};

// connect the client
function login(){
    if(loginFlag == 0) {
        options = {
            onSuccess: onConnect,
            onFailure: doFail,
            userName: "XXX",
            password: "XXX"
        };
        try {
            // Create a client instance
            clientId = "XXX";
            client = new Paho.MQTT.Client("broker's ip", 9001, clientId);
                        
            // set callback handlers
            client.onConnectionLost = onConnectionLost;
            client.onMessageArrived = onMessageArrived;
            client.connect(options);
        }
        finally {
            console.log(loginFlag);
        }
    }
}

// called when the client connects
function onConnect() {
    // Once a connection has been made, make a subscription and send a message.
    console.log("onConnect");
    message = new Paho.MQTT.Message("Connect from " + clientId);
    client.subscribe("login");
    client.subscribe("same_topic_of_publisher");
    message = new Paho.MQTT.Message("Connect from " + clientId);
    message.destinationName = "login";
    client.send(message);
    loginFlag = 1;
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log("onConnectionLost:"+responseObject.errorMessage);
    }
}

// called when a message arrives
function onMessageArrived(message) {
    try{
        console.log("pass");
        if (message.destinationName == "pattern/position") {
            putCircle(message.payloadString.split(",")[1], message.payloadString.split(",")[0])
        }
    }
    catch(err){
        document.getElementById("out_messages").innerHTML=err.message + "<br>";
    }

    console.log("onMessageArrived:"+message.payloadString);
}

function doFail(e) {
    console.log(e);
    document.getElementById("out_messages").innerHTML=e.errorMessage + "<br>";
    loginFlag = 0;
}




function putCircle(topPercentInput, leftPercentInput) {
    console.log("Put circle.");
    
    var circle = document.querySelector("#wholePage");
    var topPercent = topPercentInput * 100 - 10;
    var leftPercent = leftPercentInput * 100 - 10;
    console.log(topPercent);
    console.log(leftPercent);
    circle.innerHTML = "<img class=\"circled\" src=\"circle.png\">" + circle.innerHTML;
    posCircle = document.querySelector("img");
    posCircle.style.top = topPercent + "%";
    posCircle.style.left = leftPercent + "%";
}