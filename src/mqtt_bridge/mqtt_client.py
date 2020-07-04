# -*- coding: utf-8 -*-
import ssl
import rospy
import rospkg
import boto3
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import urllib
import string
import random

rospack = rospkg.RosPack()


def random_client_id(size=6, chars=string.ascii_uppercase + string.digits):
    """Create a random client ID used by the AWS MQTT client.
    :param size: Size of the ID.
    :param chars: Characters to use in the client ID.
    :returns: Client ID
    """
    return "".join(random.choice(chars) for x in range(size))


def default_mqtt_client_factory(aws_params):
    """MQTT Client factory.

    :param dict param: configuration parameters
    :return mqtt.Client: MQTT Client
    """
    # create client:
#    mqtt_client = params.get("aws", {})
#    aws_params = params.get("aws", {})
#    rospy.logwarn(params)#mqtt_client)
#    rospy.logwarn(aws_params)
    endpoint = aws_params.pop("endpoint")
    greengrass_root = aws_params.pop("greengrass_root")
    vehicle_name = aws_params.pop("vehicle_name")
    aws_acc_key_id = aws_params.pop("aws_acc_key_id")
    aws_sec_acc_key = aws_params.pop("aws_sec_acc_key")
    cert = greengrass_root + "certs/root.ca.pem"
    rospy.logwarn(endpoint)
    rospy.logwarn(greengrass_root)
    rospy.logwarn(vehicle_name)
    rospy.logwarn(aws_acc_key_id)
    rospy.logwarn(aws_sec_acc_key)
    rospy.logwarn(cert)

    client = AWSIoTMQTTClient(random_client_id(), useWebsocket=True)
    #        mqtt_client.pop("id", "default_client"), useWebsocket=False
    #    )

    rospy.loginfo(cert)
    rospy.loginfo(
        greengrass_root
        + "certs/"
        + vehicle_name
        + ".private.key"
    )
    rospy.loginfo(
        greengrass_root + "certs/" + vehicle_name + ".cert.pem"
    )
    client.configureIAMCredentials(
        aws_acc_key_id, aws_sec_acc_key
    )
    client.configureCredentials(
        CAFilePath=cert,
        KeyPath=greengrass_root
        + "certs/"
        + vehicle_name
        + ".private.key",
        CertificatePath=greengrass_root
        + "certs/"
        + vehicle_name
        + ".cert.pem",
    )

    rospy.loginfo(endpoint)
    client.configureEndpoint(endpoint, 443)  # aws_iot_params.pop("port", 443))
    client.configureOfflinePublishQueueing(-1) # Infinite offline Publish queueing
    client.configureDrainingFrequency(aws_params.pop("draining_frequency", 260))  # Draining: 2 Hz
    client.configureConnectDisconnectTimeout(aws_params.pop("connect_timeout_in_s", 30))  # 10 sec
    client.configureMQTTOperationTimeout(aws_params.pop("operation_timeout_in_s", 5))  # 5 sec
    return client


def create_private_path_extractor(mqtt_private_path):
    def extractor(topic_path):
        if topic_path.startswith("~/"):
            return "{}/{}".format(mqtt_private_path, topic_path[2:])
        return topic_path

    return extractor


__all__ = ["default_mqtt_client_factory", "create_private_path_extractor"]
