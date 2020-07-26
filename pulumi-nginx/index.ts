// Copyright 2016-2019, Pulumi Corporation.  All rights reserved.

import * as awsx from "@pulumi/awsx";
import * as pulumi from "@pulumi/pulumi";

const vpc = awsx.ec2.Vpc.getDefault();

// Create a basic cluster and autoscaling group
const cluster = new awsx.ecs.Cluster("nginx", { vpc });
const autoScalingGroup = cluster.createAutoScalingGroup("nginx", {
    subnetIds: vpc.publicSubnetIds,
    templateParameters: {
        minSize: 1
    },
    launchConfigurationArgs: {
        instanceType: "t2.medium",
        keyName: "kaizen-mbp"
    }
});

const listener = new awsx.elasticloadbalancingv2.ApplicationListener("nginx", {
    external: true,
    port: 80,
    protocol: "HTTP",
    targetGroup: {
        healthCheck: {
            path: "/"
        },
        name: "nginx-tg",
        port: 80,
        protocol: "HTTP"
    }
});

const airflowController = new awsx.ecs.EC2Service("nginx", {
    cluster,
    desiredCount: 1,
    taskDefinitionArgs: {
        containers: {
            webserver: {
                image: awsx.ecs.Image.fromPath("nginx", "./app"),
                portMappings: [listener],
                memory: 256
            }
        }
    }
});

export let frontendURL = pulumi.interpolate`http://${listener.endpoint.hostname}/`;
