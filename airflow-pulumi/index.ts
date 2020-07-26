// Copyright 2016-2019, Pulumi Corporation.  All rights reserved.

import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config("airflow");
const dbPassword = config.require("dbPassword");

const vpc = awsx.ec2.Vpc.getDefault();

// Create a basic cluster and autoscaling group
const cluster = new awsx.ecs.Cluster("airflow", { vpc });
const autoScalingGroup = cluster.createAutoScalingGroup("airflow", {
    subnetIds: vpc.publicSubnetIds,
    templateParameters: {
        minSize: 1
    },
    launchConfigurationArgs: {
        instanceType: "t2.medium",
        keyName: "kaizen-mbp"
    }
});

const securityGroupIds = cluster.securityGroups.map(g => g.id);

const dbSubnets = new aws.rds.SubnetGroup("dbsubnets", {
    subnetIds: vpc.publicSubnetIds
});

const db = new aws.rds.Instance("airflow-postgresdb", {
    engine: "postgres",

    instanceClass: "db.t2.micro",
    allocatedStorage: 20,

    dbSubnetGroupName: dbSubnets.id,
    vpcSecurityGroupIds: securityGroupIds,

    name: "airflow",
    username: "airflow",
    password: dbPassword,

    skipFinalSnapshot: true
});

// const cacheSubnets = new aws.elasticache.SubnetGroup("cachesubnets", {
//     subnetIds: vpc.publicSubnetIds
// });

// const cacheCluster = new aws.elasticache.Cluster("cachecluster", {
//     engine: "redis",

//     nodeType: "cache.t2.micro",
//     numCacheNodes: 1,

//     subnetGroupName: cacheSubnets.id,
//     securityGroupIds: securityGroupIds
// });

const hosts = pulumi.all([db.endpoint.apply(e => e.split(":")[0])]);
const environment = hosts.apply(([postgresHost]) => [
    { name: "POSTGRES_HOST", value: postgresHost },
    { name: "POSTGRES_PASSWORD", value: dbPassword },
    { name: "EXECUTOR", value: "Sequential" }
]);

const airflowControllerListener = new awsx.elasticloadbalancingv2.ApplicationListener(
    "airflowcontroller",
    {
        external: true,
        port: 8080,
        protocol: "HTTP",
        targetGroup: {
            name: "airflow-tg",
            port: 8080,
            protocol: "HTTP",
            healthCheck: {
                path: "/health"
            }
        }
    }
);

const airflowController = new awsx.ecs.EC2Service("airflowcontroller", {
    cluster,
    desiredCount: 1,
    taskDefinitionArgs: {
        containers: {
            webserver: {
                image: awsx.ecs.Image.fromPath(
                    "webserver",
                    "./airflow-container"
                ),
                portMappings: [airflowControllerListener],
                environment: environment,
                command: ["webserver"],
                memory: 1024
            }
        }
    }
});

export let airflowEndpoint = airflowControllerListener.endpoint.hostname;
