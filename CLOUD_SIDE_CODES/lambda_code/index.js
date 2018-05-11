console.log("Loading function");
var AWS = require("aws-sdk");

exports.handler = function(event, context) {
    var eventText = JSON.stringify(event, null, 2);
    var myMessage = "Hi "+event.deviceId.toString()+"\n";
    if(event.light >= 20 & event.light<=100){
        return;      
    } else if(event.light < 20){
        myMessage = myMessage+"You are in low light area which might be harmful to your eyes. Light measure is "+event.light.toString() + " LUX.\n";
    } else if(event.light > 100){
        myMessage = myMessage+"Light around you is too bright which might be harmful to your eyes. Light measure is "+event.light.toString() + " LUX.\n";
    }
    if(event.audio > 120){
        myMessage += "You are in a noisy area which might affect your ears. Noise measure is "+event.audio.toString()+" DB";
    }
    var myTarget = event.id;
    var sns = new AWS.SNS();
    var params = {
        Message: myMessage, 
        Subject: "Alert",
        //TopicArn: "arn:aws:sns:us-east-1:582363083840:IOTTopic"
        TargetArn: myTarget
    };

    console.log(sns.listSubscriptionsByTopic("arn:aws:sns:us-east-1:582363083840:IOTTopic"))
    sns.publish(params, context.done);
};